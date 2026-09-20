"""Diagnostic-only val probes. All interventions are process-local; no training."""
from pathlib import Path
import subprocess

root=Path('/root/sj-tmp/evidence/baseline800_diagnosis_20260915')
if (root/'runner.pid').exists():
    raise RuntimeError('Diagnostic run already deployed; do not overwrite')
root.mkdir(parents=True,exist_ok=True)
CHILD=r'''import json,sys,os,time,types,hashlib,inspect
from pathlib import Path
name,size,mode,root=sys.argv[1:]
size=int(size)
root=Path(root)
out=root/name
out.mkdir(parents=True,exist_ok=True)
code='/root/sj-tmp/lrs-v2/code'
os.chdir(code)
sys.path.insert(0,code)
import torch
from ultralytics import RTDETR
from ultralytics.models.rtdetr.val import RTDETRValidator
from ultralytics.utils import ops
from src.bpdd_formal_evaluation import summarize_native_box_metrics
from src.lpr_protocol import CATEGORY_NAMES

checkpoint='/root/sj-tmp/checkpoints/fdr-formal-d97e1eb7/fdr-formal-seed0-control-d97e1eb7-epoch-0100.pt'
if name.startswith('G_'):
    checkpoint='/root/sj-tmp/runs/visdrone-v2-existing-state-20260907/formal-seed0-lrs_fdr_feasible-v2/weights/best.pt'
model=RTDETR(checkpoint)
head=model.model.model[-1]
original_generator=head._generate_anchors
if mode=='fresh_anchors':
    head.dynamic=True
elif mode=='no_fuse':
    model.model.fuse=types.MethodType(lambda self,*a,**kw:self,model.model)
elif mode=='anchor_wh_0p8':
    def anchor_probe(self,shapes,grid_size=0.05,dtype=torch.float32,device='cpu',eps=1e-2):
        return original_generator(shapes,grid_size=grid_size*0.8,dtype=dtype,device=device,eps=eps)
    head._generate_anchors=types.MethodType(anchor_probe,head)
    head.dynamic=True
elif mode not in {'native','output_wh_0p8'}:
    raise ValueError(mode)

def tensor_info(x):
    if not isinstance(x,torch.Tensor): return x
    return {'shape':list(x.shape),'dtype':str(x.dtype),'device':str(x.device)}
def head_state():
    state={k:tensor_info(getattr(head,k,None)) for k in ['shapes','anchors','valid_mask','dynamic']}
    state['class']=str(type(head))
    state['eval_idx']=int(head.decoder.eval_idx)
    shapes=getattr(head,'shapes',None)
    anchors=getattr(head,'anchors',None)
    if shapes is not None and isinstance(anchors,torch.Tensor):
        expected,mask=head._generate_anchors(shapes,dtype=anchors.dtype,device=anchors.device)
        finite=torch.isfinite(expected)&torch.isfinite(anchors)
        state['anchors_vs_regenerated_maxabs']=float((expected[finite]-anchors[finite]).abs().max())
        state['anchor_finite_mask_equal']=bool(torch.equal(torch.isfinite(expected),torch.isfinite(anchors)))
        state['valid_mask_equal']=bool(torch.equal(mask,head.valid_mask))
        state['anchor_wh_first']=anchors.sigmoid()[0,0,2:].detach().cpu().tolist()
    return state

class DiagnosticValidator(RTDETRValidator):
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw)
        self.records=[]
        self.shapes=set()
        self.mapping_error=0.0
        self.first_state=None
        self.enc=None
    def preprocess(self,batch):
        batch=super().preprocess(batch)
        self.shapes.add(tuple(batch['img'].shape))
        assert batch['img'].dtype==torch.float32
        assert float(batch['img'].min())>=0 and float(batch['img'].max())<=1
        return batch
    def postprocess(self,preds):
        self.enc=None
        if isinstance(preds,(tuple,list)) and len(preds)>1 and isinstance(preds[1],(tuple,list)):
            raw=preds[1]
            if len(raw)>=4:
                self.enc=(raw[2].detach(),raw[3].detach().sigmoid())
        y=preds[0] if isinstance(preds,(tuple,list)) else preds
        if mode=='output_wh_0p8':
            y=y.clone()
            y[...,2:4]*=0.8
            preds=y
        post=super().postprocess(preds)
        for original,pred in zip(y,post):
            keep=original[:,4]>self.args.conf
            expected=ops.xywh2xyxy(original[keep,:4])*size
            if len(expected):
                self.mapping_error=max(self.mapping_error,float((expected-pred['bboxes']).abs().max()))
        if self.first_state is None:
            self.first_state=head_state()
        return post
    def update_metrics(self,preds,batch):
        for i,pred in enumerate(preds):
            gt=self._prepare_batch(i,batch)
            record={'file':gt['im_file'],'original_shape':gt['ori_shape'],
                'ratio_pad':gt['ratio_pad'],
                'gt_boxes':gt['bboxes'].detach().cpu()/size,
                'gt_cls':gt['cls'].detach().cpu(),
                'boxes':pred['bboxes'].detach().cpu()/size,
                'scores':pred['conf'].detach().cpu(),
                'cls':pred['cls'].detach().cpu()}
            if self.enc is not None:
                boxes,scores=self.enc
                conf,classes=scores[i].max(-1)
                record.update(enc_boxes=ops.xywh2xyxy(boxes[i]).cpu(),enc_scores=conf.cpu(),enc_cls=classes.cpu())
            self.records.append(record)
        return super().update_metrics(preds,batch)

args={'model':checkpoint,'data':'/root/sj-tmp/evidence/visdrone_test_authority_20260915.yaml',
    'task':'detect','mode':'val','split':'val','imgsz':size,'batch':8,'workers':8,
    'conf':0.001,'max_det':300,'nms':False,'device':'0','cache':False,'half':False,
    'rect':False,'plots':False,'save_json':False,'save_txt':False,'verbose':False}
validator=DiagnosticValidator(save_dir=out/'validator',args=dict(args))
start=time.monotonic()
validator(model=model.model)
assert len(validator.records)==548
assert validator.mapping_error==0
torch.save(validator.records,out/'predictions.pt')
report={'name':name,'mode':mode,'diagnostic_only':mode!='native','protocol':args,
    'image_count':len(validator.records),'input_shapes':list(validator.shapes),
    'raw_to_validator_box_maxabs_px':validator.mapping_error,
    'head_after_first_data_batch':validator.first_state,'wall_seconds':time.monotonic()-start,
    **summarize_native_box_metrics(validator.metrics.box,CATEGORY_NAMES)}
(out/'summary.json').write_text(json.dumps(report,indent=2,default=str)+'\n')
print('DIAG_COMPLETE',name,json.dumps(report['metrics']),flush=True)
'''
RUNNER=r'''import subprocess,json,traceback
from pathlib import Path
root=Path(__file__).resolve().parent
tasks=[('B_native640',640,'native'),('B_native800',800,'native'),
    ('B_fresh800',800,'fresh_anchors'),('B_nofuse800',800,'no_fuse'),
    ('B_anchor800',800,'anchor_wh_0p8'),('B_boxwh800',800,'output_wh_0p8'),
    ('G_native640',640,'native'),('G_native800',800,'native')]
records=[]
for name,size,mode in tasks:
    (root/'CURRENT.json').write_text(json.dumps({'name':name,'status':'running'})+'\n')
    record={'name':name}
    try:
        subprocess.run(['/root/miniconda3/envs/lrs-v2/bin/python','-u',str(root/'diagnose.py'),name,str(size),mode,str(root)],check=True,timeout=300)
        record['status']='complete'
    except Exception as e:
        record.update(status='failed',error=repr(e))
        traceback.print_exc()
    records.append(record)
    (root/'STATUS.json').write_text(json.dumps(records,indent=2)+'\n')
(root/'COMPLETE.json').write_text(json.dumps(records,indent=2)+'\n')
'''
compile(CHILD,'diagnose.py','exec')
compile(RUNNER,'runner.py','exec')
(root/'diagnose.py').write_text(CHILD)
(root/'runner.py').write_text(RUNNER)
with (root/'runner.log').open('w') as log:
    p=subprocess.Popen(['/root/miniconda3/envs/lrs-v2/bin/python','-u',str(root/'runner.py')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
(root/'runner.pid').write_text(str(p.pid)+'\n')
print('DIAGNOSTIC_STARTED',p.pid,str(root))

"""Process-only cache precision controls; never edits production source."""
from pathlib import Path
import subprocess

root=Path('/root/sj-tmp/evidence/baseline800_diagnosis_20260915')
assert (root/'COMPLETE.json').exists()
assert not (root/'precision_runner.pid').exists(), 'Already deployed'
source=(root/'diagnose.py').read_text()
old="elif mode=='no_fuse':"
new="""elif mode=='fp16_anchor_generation':
    def precision_probe(self,shapes,grid_size=0.05,dtype=torch.float32,device='cpu',eps=1e-2):
        anchors,mask=original_generator(shapes,grid_size=grid_size,dtype=torch.float16,device=device,eps=eps)
        return anchors.to(dtype),mask
    head._generate_anchors=types.MethodType(precision_probe,head)
    head.dynamic=True
elif mode=='no_fuse':"""
assert source.count(old)==1
source=source.replace(old,new)
old="state['anchor_wh_first']=anchors.sigmoid()[0,0,2:].detach().cpu().tolist()"
new="state['valid_anchor_wh_unique']=anchors.sigmoid()[head.valid_mask.squeeze(-1)][:,2:].unique(dim=0).detach().cpu().tolist()"
assert source.count(old)==1
source=source.replace(old,new)
compile(source,'diagnose_precision.py','exec')
(root/'diagnose_precision.py').write_text(source)
runner=r'''import subprocess,json
from pathlib import Path
root=Path(__file__).resolve().parent
tasks=[('B_fresh640',640,'fresh_anchors'),('B_fp16anchors800',800,'fp16_anchor_generation')]
records=[]
for name,size,mode in tasks:
    p=subprocess.run(['/root/miniconda3/envs/lrs-v2/bin/python','-u',str(root/'diagnose_precision.py'),name,str(size),mode,str(root)],timeout=300)
    records.append({'name':name,'exit_code':p.returncode})
    (root/'PRECISION_STATUS.json').write_text(json.dumps(records,indent=2)+'\n')
(root/'PRECISION_COMPLETE.json').write_text(json.dumps(records,indent=2)+'\n')
'''
(root/'precision_runner.py').write_text(runner)
with (root/'precision_runner.log').open('w') as log:
    p=subprocess.Popen(['/root/miniconda3/envs/lrs-v2/bin/python','-u',str(root/'precision_runner.py')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
(root/'precision_runner.pid').write_text(str(p.pid)+'\n')
print('PRECISION_CONTROLS_STARTED',p.pid)

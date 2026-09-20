import subprocess

SOURCE=r'''import json,sys
from pathlib import Path
import numpy as np
import torch
from ultralytics.utils.metrics import box_iou
torch.set_num_threads(4)
root=Path('/root/sj-tmp/evidence/baseline800_diagnosis_20260915')
reports={}
predictions={}
for p in sorted(root.glob('*/predictions.pt')):
    name=p.parent.name
    predictions[name]=torch.load(p,map_location='cpu',weights_only=False)
    reports[name]=json.loads((p.parent/'summary.json').read_text())
assert 'B_native640' in predictions and 'B_native800' in predictions

ref=predictions['B_native640']
gt_checks={}
analyses={}
per_gt={}
for name,records in predictions.items():
    maxerr=0
    assert len(records)==len(ref)==548
    for a,b in zip(ref,records):
        assert a['file']==b['file'] and torch.equal(a['gt_cls'],b['gt_cls'])
        if a['gt_boxes'].numel(): maxerr=max(maxerr,float((a['gt_boxes']-b['gt_boxes']).abs().max()))
    gt_checks[name]={'same_images_and_classes':True,'normalized_gt_maxabs':maxerr}
    assert maxerr<1e-6
    analyses[name]={}
    per_gt[name]={}
    for stage in ['final','encoder']:
        prefix='' if stage=='final' else 'enc_'
        if prefix+'boxes' not in records[0]: continue
        ious=[]; labels=[]; widths=[]; heights=[]; center_x=[]; center_y=[]; pred_count=0
        conf_values=[]
        for r in records:
            gt=r['gt_boxes']; gtcls=r['gt_cls']
            boxes=r[prefix+'boxes']; scores=r[prefix+'scores']; classes=r[prefix+'cls']
            keep=scores>=0.1
            boxes,scores,classes=boxes[keep],scores[keep],classes[keep]
            pred_count+=len(boxes)
            conf_values.extend(scores.tolist())
            labels.extend(gtcls.tolist())
            if len(boxes)==0:
                ious.extend([0.0]*len(gt)); widths.extend([float('nan')]*len(gt)); heights.extend([float('nan')]*len(gt))
                center_x.extend([float('nan')]*len(gt)); center_y.extend([float('nan')]*len(gt)); continue
            overlap=box_iou(gt,boxes)
            overlap[gtcls[:,None]!=classes[None,:]]=0
            best,index=overlap.max(1)
            matched=boxes[index]
            gtwh=(gt[:,2:]-gt[:,:2]).clamp_min(1e-9)
            predwh=matched[:,2:]-matched[:,:2]
            center=((matched[:,:2]+matched[:,2:])-(gt[:,:2]+gt[:,2:]))/2/gtwh
            ious.extend(best.tolist())
            widths.extend((predwh[:,0]/gtwh[:,0]).tolist())
            heights.extend((predwh[:,1]/gtwh[:,1]).tolist())
            center_x.extend(center[:,0].tolist()); center_y.extend(center[:,1].tolist())
        values={k:np.asarray(v) for k,v in dict(iou=ious,cls=labels,width=widths,height=heights,cx=center_x,cy=center_y).items()}
        per_gt[name][stage]=values
        valid=values['iou']>=.25
        summary={'gt_count':len(ious),'predictions_conf_ge_0p1':pred_count,
            'coverage':{str(t):float((values['iou']>=t).mean()) for t in [.25,.5,.75,.9]},
            'mean_best_same_class_iou':float(values['iou'].mean()),
            'geometry_on_gt_iou_ge_0p25':{k:float(np.nanmedian(values[k][valid])) for k in ['width','height','cx','cy']},
            'per_class_coverage50':{str(c):float((values['iou'][values['cls']==c]>=.5).mean()) for c in range(10)}}
        analyses[name][stage]=summary
paired={}
for name,stages in per_gt.items():
    if name=='B_native640':continue
    a=per_gt['B_native640']['final']; b=stages['final']
    valid=(a['iou']>=.5)&(b['iou']>=.25)
    paired[name]={'common_gt_count':int(valid.sum()),
        'baseline640':{k:float(np.nanmedian(a[k][valid])) for k in ['iou','width','height','cx','cy']},
        'candidate':{k:float(np.nanmedian(b[k][valid])) for k in ['iou','width','height','cx','cy']}}

equivalence={}
for candidate in ['B_fresh800','B_nofuse800','B_fp16anchors800']:
    if candidate not in predictions:continue
    maxbox=0.; maxscore=0.; nclass=0; different_count=0
    for a,b in zip(predictions['B_native800'],predictions[candidate]):
        if a['boxes'].shape!=b['boxes'].shape:
            different_count+=1; continue
        if a['boxes'].numel():
            maxbox=max(maxbox,float((a['boxes']-b['boxes']).abs().max()))
            maxscore=max(maxscore,float((a['scores']-b['scores']).abs().max()))
            nclass+=int((a['cls']!=b['cls']).sum())
    equivalence[candidate]={'max_normalized_box_diff_rank_aligned':maxbox,'max_score_diff_rank_aligned':maxscore,'class_disagreements_rank_aligned':nclass,'different_prediction_count_images':different_count}
anchor_isolation={'same_images':True,'encoder_max_score_diff':0.0,'encoder_class_disagreements':0,'encoder_max_center_diff':0.0}
for a,b in zip(predictions['B_native800'],predictions['B_anchor800']):
    assert a['file']==b['file']
    anchor_isolation['encoder_max_score_diff']=max(anchor_isolation['encoder_max_score_diff'],float((a['enc_scores']-b['enc_scores']).abs().max()))
    anchor_isolation['encoder_class_disagreements']+=int((a['enc_cls']!=b['enc_cls']).sum())
    ac=(a['enc_boxes'][:,:2]+a['enc_boxes'][:,2:])/2
    bc=(b['enc_boxes'][:,:2]+b['enc_boxes'][:,2:])/2
    anchor_isolation['encoder_max_center_diff']=max(anchor_isolation['encoder_max_center_diff'],float((ac-bc).abs().max()))
assert anchor_isolation['encoder_max_score_diff']==0
assert anchor_isolation['encoder_class_disagreements']==0
assert anchor_isolation['encoder_max_center_diff']<1e-6
checkpoint_hashes={}
checkpoint_training_args={}
import hashlib,inspect
sys.path.insert(0,'/root/sj-tmp/lrs-v2/code')
from ultralytics import RTDETR
from ultralytics.nn.modules.transformer import DeformableTransformerDecoder,MSDeformAttn
sources={}
for ckpt in [reports['B_native640']['protocol']['model'],reports['G_native640']['protocol']['model']]:
    with open(ckpt,'rb') as f: checksum=hashlib.file_digest(f,'sha256').hexdigest() if hasattr(hashlib,'file_digest') else hashlib.sha256(f.read()).hexdigest()
    checkpoint_hashes[ckpt]=checksum
    model=RTDETR(ckpt)
    train_args=model.ckpt.get('train_args',{})
    if not isinstance(train_args,dict): train_args=vars(train_args)
    checkpoint_training_args[ckpt]={k:train_args.get(k) for k in ['imgsz','epochs','batch','multi_scale','rect','amp','optimizer','pretrained','data','seed','deterministic','fraction','scale','mosaic','mixup','copy_paste']}
    head=model.model.model[-1]
    sources[str(type(head))+'.forward']=inspect.getsource(head.forward)
    sources[str(type(head.decoder))+'.forward']=inspect.getsource(head.decoder.forward)
sources['MSDeformAttn.forward']=inspect.getsource(MSDeformAttn.forward)
(root/'decoder_sources.json').write_text(json.dumps(sources,indent=2)+'\n')
result={'kind':'diagnostic_only_val_geometry_analysis','confidence_cutoff':.1,
    'coverage_note':'Per-GT best same-class overlap; not one-to-one matching and not official recall.',
    'gt_checks':gt_checks,'analyses':analyses,'paired_geometry':paired,'equivalence':equivalence,
    'metrics':{k:v['metrics'] for k,v in reports.items()},'anchor_intervention_isolation':anchor_isolation,'checkpoint_sha256_after_diagnostics':checkpoint_hashes,'checkpoint_training_args':checkpoint_training_args}
(root/'ANALYSIS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
for name,report in reports.items():print(name,report['metrics'])
for name in ['B_native640','B_native800','B_anchor800','G_native640','G_native800']:
    if name in analyses:print('GEOMETRY',name,json.dumps(analyses[name]))
print('PAIRED',json.dumps(paired))
print('EQUIVALENCE',json.dumps(equivalence))
print('ANCHOR_ISOLATION',json.dumps(anchor_isolation))
'''
subprocess.run(['/root/miniconda3/envs/lrs-v2/bin/python','-c',SOURCE],check=True)

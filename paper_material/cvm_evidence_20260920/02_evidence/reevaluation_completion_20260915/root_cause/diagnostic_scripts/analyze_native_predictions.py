import sys, json
from pathlib import Path
from collections import Counter
import numpy as np
import torch
from PIL import Image
sys.path.insert(0,'/root/sj-tmp/lrs-v2/bpdd-capacity-v2-fia-code')
from src.bpdd_formal_evaluation import _match_predictions
from ultralytics.utils.metrics import ap_per_class, box_iou
torch.set_num_threads(2)
root=Path('/root/sj-tmp/evidence/native_root_cause_20260915')
names=['pedestrian','people','bicycle','car','van','truck','tricycle','awning-tricycle','bus','motor']
results={}
for arm in ['G','GF','GB','Full']:
 for split in ['val','test']:
  dest=root/arm/split
  if not (dest/'predictions.pt').exists():continue
  cache=torch.load(dest/'predictions.pt',map_location='cpu',weights_only=False)
  records=[]; errors={}
  for index,(p,t,file) in enumerate(zip(cache['predictions'],cache['targets'],cache['files'])):
   with Image.open(file) as im:w,h=im.size
   tp=_match_predictions(p['bboxes'],p['cls'],t['bboxes'],t['cls'])
   records.append(dict(tp=tp,conf=p['conf'].numpy(),pred_cls=p['cls'].numpy(),target_cls=t['cls'].numpy(),aspect=w/h,scene=Path(file).stem.split('_')[0]))
   iou=box_iou(t['bboxes'],p['bboxes']).numpy()
   for cls in [0,1,4,5,9]:
    gi=np.flatnonzero(t['cls'].numpy()==cls)
    for threshold in [.001,.1]:
     key=f'{names[cls]}_conf{threshold}'
     s=errors.setdefault(key,Counter())
     s['gt']+=len(gi)
     eligible=p['conf'].numpy()>=threshold
     correct=(p['cls'].numpy()==cls)&eligible
     wrong=(p['cls'].numpy()!=cls)&eligible
     sizes=(t['bboxes'][gi,2:]-t['bboxes'][gi,:2]).prod(dim=1).sqrt().numpy()
     for row,size in zip(gi,sizes):
      same=float(iou[row,correct].max()) if correct.any() else 0.
      any_iou=float(iou[row,eligible].max()) if eligible.any() else 0.
      s['same_iou50']+=int(same>=.5);s['same_iou75']+=int(same>=.75)
      if same<.5:
       if any_iou>=.5:
        s['wrong_class_overlap50']+=1
        ids=np.flatnonzero(eligible & (iou[row]>=.5))
        winner=ids[np.argmax(p['conf'].numpy()[ids])]
        s['confused_as_'+names[int(p['cls'][winner])]]+=1
       elif same>=.1:s['localization_10_50']+=1
       else:s['no_same_class_overlap10']+=1
      s['tiny_gt']+=int(size<16);s['tiny_same_iou50']+=int(size<16 and same>=.5)
  groups={'all':list(range(len(records))), 'aspect_16_9':[i for i,r in enumerate(records) if abs(r['aspect']-16/9)<.02], 'aspect_4_3':[i for i,r in enumerate(records) if abs(r['aspect']-4/3)<.02]}
  summaries={}
  for group,indices in groups.items():
   if not indices:continue
   merged={key:np.concatenate([records[i][key] for i in indices],axis=0) for key in ['tp','conf','pred_cls','target_cls']}
   raw=ap_per_class(**merged,plot=False)
   ap=raw[5];classes=raw[6]
   summaries[group]=dict(images=len(indices),map=float(ap.mean()),per_class={names[int(c)]:float(row.mean()) for c,row in zip(classes,ap)},gt={names[k]:int((merged['target_cls']==k).sum()) for k in range(10)})
  reference=json.loads((dest/'summary.json').read_text())
  assert abs(summaries['all']['map']-reference['metrics']['map'])<1e-10, (arm,split,summaries['all']['map'],reference['metrics']['map'])
  results[f'{arm}/{split}']=dict(groups=summaries,errors={k:dict(v) for k,v in errors.items()})
  print('ANALYZED',arm,split,flush=True)
(root/'error_analysis.json').write_text(json.dumps(results,indent=2))
print('ERROR_ANALYSIS_COMPLETE',flush=True)

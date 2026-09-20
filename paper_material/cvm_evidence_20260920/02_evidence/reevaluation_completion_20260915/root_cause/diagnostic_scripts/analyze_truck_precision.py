import sys,json,zipfile
from pathlib import Path
import numpy as np
import torch
from PIL import Image
sys.path.insert(0,'/root/sj-tmp/lrs-v2/bpdd-capacity-v2-fia-code')
from src.bpdd_formal_evaluation import _match_predictions
from ultralytics.utils.metrics import box_iou
torch.set_num_threads(2)
root=Path('/root/sj-tmp/evidence/native_root_cause_20260915')
results={}
for arm in ['G','GF','GB','Full']:
 for split in ['val','test']:
  cache=torch.load(root/arm/split/'predictions.pt',map_location='cpu',weights_only=False)
  out={str(c):{'pred':0,'tp50':0,'tp75':0,'fp50':0,'duplicate_or_competing_match':0,'wrong_class_overlap50':0,'same_class_localization':0,'background_or_other':0} for c in [4,5,8]}
  for p,t in zip(cache['predictions'],cache['targets']):
   tp=_match_predictions(p['bboxes'],p['cls'],t['bboxes'],t['cls'])
   iou=box_iou(t['bboxes'],p['bboxes']).numpy()
   for c in [4,5,8]:
    ids=np.flatnonzero((p['cls'].numpy()==c)&(p['conf'].numpy()>=.1))
    s=out[str(c)];s['pred']+=len(ids);s['tp50']+=int(tp[ids,0].sum());s['tp75']+=int(tp[ids,5].sum());s['fp50']+=int((~tp[ids,0]).sum())
    for j in ids[~tp[ids,0]]:
     correct=t['cls'].numpy()==c
     same=float(iou[correct,j].max()) if correct.any() else 0.
     wrong=float(iou[~correct,j].max()) if (~correct).any() else 0.
     if same>=.5:s['duplicate_or_competing_match']+=1
     elif wrong>=.5:s['wrong_class_overlap50']+=1
     elif same>=.1:s['same_class_localization']+=1
     else:s['background_or_other']+=1
  results[f'{arm}/{split}']=out
(root/'precision_error_analysis.json').write_text(json.dumps(results,indent=2))
for key,data in results.items():print('PRECISION_ERRORS',key,json.dumps(data))

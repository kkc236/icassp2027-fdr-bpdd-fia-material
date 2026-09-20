import sys,json
from pathlib import Path
import numpy as np
import torch
sys.path.insert(0,'/root/sj-tmp/lrs-v2/bpdd-capacity-v2-fia-code')
from src.bpdd_formal_evaluation import _match_predictions
torch.set_num_threads(2)
root=Path('/root/sj-tmp/evidence/native_root_cause_20260915')
results={}
for arm in ['G','Full']:
 for split in ['val','test']:
  cache=torch.load(root/arm/split/'predictions.pt',map_location='cpu',weights_only=False)
  scores=[];correct=[]
  for p,t in zip(cache['predictions'],cache['targets']):
   mask=p['cls'].numpy()==5
   if not mask.any():continue
   tp=_match_predictions(p['bboxes'],p['cls'],t['bboxes'],t['cls'])
   scores.append(p['conf'].numpy()[mask]);correct.append(tp[mask])
  scores=np.concatenate(scores);correct=np.concatenate(correct);order=np.argsort(-scores)
  correct=correct[order];scores=scores[order]
  out={str(k):{'detections':min(k,len(scores)),'tp50':int(correct[:k,0].sum()),'tp75':int(correct[:k,5].sum()),'tp90':int(correct[:k,8].sum()),'score_cutoff':float(scores[min(k,len(scores))-1])} for k in [100,500,1000,2000,5000]}
  results[f'{arm}/{split}']=out
(root/'truck_ranking.json').write_text(json.dumps(results,indent=2))
print('TRUCK_RANKING',json.dumps(results))

import sys,json,hashlib,subprocess
from pathlib import Path
import numpy as np
import torch
torch.set_num_threads(2)
root=Path('/root/sj-tmp/evidence/native_root_cause_20260915')
result={}
for split in ['val','test']:
 p=root/'G'/split/'predictions.pt'
 cache=torch.load(p,map_location='cpu',weights_only=False)
 bad=[];maxerr=0.;count=0
 for target,file in zip(cache['targets'],cache['files']):
  lp=Path(file.replace('/images/','/labels/')).with_suffix('.txt')
  arr=np.array([list(map(float,line.split())) for line in lp.read_text().splitlines() if line.strip()],dtype=np.float32).reshape(-1,5)
  boxes=np.concatenate((arr[:,1:3]-arr[:,3:5]/2,arr[:,1:3]+arr[:,3:5]/2),axis=1)*640
  actual=target['bboxes'].numpy()
  count+=len(arr)
  if boxes.shape!=actual.shape or not np.array_equal(arr[:,0],target['cls'].numpy()):bad.append(str(lp));continue
  err=float(np.abs(boxes-actual).max()) if len(arr) else 0.
  maxerr=max(err,maxerr)
  if err>.001:bad.append(str(lp))
 result[split]=dict(images=len(cache['files']),labels=count,actual_target_mismatches=bad,max_abs_input_pixel_error=maxerr,npy_files=len(list(Path('/root/sj-tmp/datasets/VisDrone/images',split).glob('*.npy'))))
print('ACTUAL_TARGET_AUDIT',json.dumps(result))
(root/'actual_target_audit.json').write_text(json.dumps(result,indent=2))
for code in ['/root/sj-tmp/lrs-v2/code','/root/sj-tmp/lrs-v2/bpdd-capacity-v2-fia-code']:
 print('CODE',code)
 for f in ['src/fdr_head.py','src/rtdetr_lrs_system.py']:
  p=Path(code)/f
  print('FILE',f,hashlib.sha256(p.read_bytes()).hexdigest())
print('ORIGINAL_GEOMETRY')
code='/root/sj-tmp/lrs-v2/code'
r=subprocess.run(['git','-C',code,'show','c1ac0b25e534f6dc5ba85ade418046a30a51a011:src/fdr_head.py'],capture_output=True,text=True)
print('STATUS',r.returncode)
ls=r.stdout.splitlines()
for i,line in enumerate(ls):
 if 'decode_feasible_fdr_boxes(' in line:print('\n'.join(ls[max(0,i-3):i+10]))

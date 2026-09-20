import sys, json, subprocess
from pathlib import Path
root=Path('/root/sj-tmp/evidence/native_root_cause_20260915')
source=r'''import sys,json
from pathlib import Path
sys.path.insert(0,sys.argv[1])
import torch
from ultralytics import RTDETR
m=RTDETR(sys.argv[2]).model
data={'type':str(type(m)),'scalar_parameters':{},'runtime_flags':{}}
for name,p in m.named_parameters():
 if p.numel()==1:data['scalar_parameters'][name]=float(p.detach())
for name,module in m.named_modules():
 for key in ['feasible_geometry','local_expert_preserve_base','local_expert_enabled','eval_idx','reg_scale','expert_scale']:
  val=getattr(module,key,None)
  if isinstance(val,(bool,float,int,str)):data['runtime_flags'][name+'.'+key]=val
print(json.dumps(data))
'''
result={}
for name,code in [('G','code'),('GF','code'),('GB','bpdd-capacity-v2-fia-code'),('Full','bpdd-capacity-v2-fia-code')]:
 d=json.loads((root/name/'val'/'summary.json').read_text())
 r=subprocess.run(['/root/miniconda3/envs/lrs-v2/bin/python','-c',source,'/root/sj-tmp/lrs-v2/'+code,d['protocol']['model']],capture_output=True,text=True,timeout=25,check=True)
 result[name]=json.loads(r.stdout.splitlines()[-1])
(root/'module_runtime.json').write_text(json.dumps(result,indent=2))
print('MODULE_RUNTIME',json.dumps(result))

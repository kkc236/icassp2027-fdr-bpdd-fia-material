from pathlib import Path
import json,hashlib,sys,subprocess
roots=[Path(p) for p in sys.argv[1:]]
seen=set(); hits=[]; counts=0
metric_keys={'map','map50-95','map50_95','ap','bbox_map','bbox_ap','map_50_95','metrics/map50-95(b)'}
excluded={'classes','class_details','per_class','perclass','scales','scale_details','speed','latency','timing'}
def walk(value,trail=()):
 if isinstance(value,dict):
  for key,item in value.items():
   if key.lower() in excluded:continue
   if key.lower() in metric_keys and isinstance(item,(int,float)) and (.245<=item<=.265 or 24.5<=item<=26.5):yield '.'.join(trail+(key,)),item
   if isinstance(item,(dict,list)):yield from walk(item,trail+(key,))
 elif isinstance(value,list):
  for i,item in enumerate(value):yield from walk(item,trail+(str(i),))
for root in roots:
 for p in root.rglob('*.json'):
  if any(part in {'node_modules','.git','.venv','site-packages','labels','annotations'} for part in p.parts):continue
  try:
   if p.stat().st_size>2_000_000:continue
   raw=p.read_bytes(); sha=hashlib.sha256(raw).hexdigest()
   if sha in seen:continue
   seen.add(sha);d=json.loads(raw);counts+=1
   found=list(walk(d))
   if found:
    row=dict(file=str(p),metrics=found,sha256=sha)
    hits.append(row);print('CANDIDATE',json.dumps(row),flush=True)
  except (OSError,ValueError,UnicodeError):continue
print('SCAN_DONE',counts,'unique JSON files;',len(hits),'candidate files',flush=True)

import sys, io, json, zipfile, hashlib, subprocess
from pathlib import Path
from collections import Counter
from PIL import Image
import numpy as np
root=Path('/root/sj-tmp/datasets/VisDrone')
result={}
for split,zipname in [('val','VisDrone2019-DET-val.zip'),('test','VisDrone2019-DET-test-dev.zip')]:
 mismatches=[]; img_bad=[]; ignored=Counter(); classes=Counter(); areas={k:[] for k in range(10)}; dims=Counter()
 with zipfile.ZipFile(root/zipname) as z:
  anns=sorted(n for n in z.namelist() if '/annotations/' in n and n.endswith('.txt'))
  for n in anns:
   stem=Path(n).stem
   ip=root/'images'/split/(stem+'.jpg')
   with Image.open(ip) as im: w,h=im.size
   dims[(w,h)]+=1
   original=z.read(n.replace('/annotations/','/images/').replace('.txt','.jpg'))
   if hashlib.sha256(original).digest()!=hashlib.sha256(ip.read_bytes()).digest():img_bad.append(stem)
   expected=[]
   for line in z.read(n).decode('utf-8-sig').splitlines():
    a=line.split(','); x,y,bw,bh=map(float,a[:4]); score=int(a[4]); cls=int(a[5])-1
    if score==0 or cls not in range(10): ignored[cls]+=1;continue
    if bw<=0 or bh<=0:continue
    expected.append([cls,(x+bw/2)/w,(y+bh/2)/h,bw/w,bh/h]);classes[cls]+=1;areas[cls].append((bw/w*bh/h)**.5*640)
   actual=[list(map(float,l.split())) for l in (root/'labels'/split/(stem+'.txt')).read_text().splitlines() if l.strip()]
   if len(expected)!=len(actual) or (expected and not np.allclose(expected,actual,atol=5.1e-7,rtol=0)):mismatches.append(stem)
 result[split]={'images':len(anns),'image_byte_mismatches':img_bad,'label_semantic_mismatches':mismatches,'class_counts':dict(classes),'ignored_counts':dict(ignored),'dimensions':dims.most_common(8),'median_target_side_at640':{k:float(np.median(v)) for k,v in areas.items()}}
print('DATA_AUDIT',json.dumps(result))
Path('/root/sj-tmp/evidence/native_root_cause_20260915/original_archive_audit.json').write_text(json.dumps(result,indent=2))
for name in ['lrs_gfdr_fia_20260909.log','formal-seed0-capacity-v3-safe-fia-lrsv2.log','formal-seed0-capacity-v3-safe-bpdd-lrsv2.log']:
 p=Path('/root/sj-tmp/logs')/name
 lines=p.read_text(errors='replace').splitlines()
 print('ENV_LOG',name,[l for l in lines if 'Ultralytics ' in l][:2])
for root_run in ['visdrone-v2-existing-state-20260907','visdrone-v2-lrs-gfdr-fia-20260909']:
 for p in (Path('/root/sj-tmp/runs')/root_run/'authority').glob('*.json'):
  print('AUTH',str(p),p.read_text()[:7000])

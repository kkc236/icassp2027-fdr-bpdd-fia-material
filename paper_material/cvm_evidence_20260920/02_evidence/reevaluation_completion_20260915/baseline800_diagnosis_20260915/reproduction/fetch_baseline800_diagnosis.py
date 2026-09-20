import base64,hashlib,json,time,zlib
from pathlib import Path

root=Path('/root/sj-tmp/evidence/baseline800_diagnosis_20260915')
assert (root/'ANALYSIS.json').exists()
assert (root/'PRECISION_COMPLETE.json').exists()
files={}
large=[]
for p in sorted(root.rglob('*')):
    if not p.is_file(): continue
    if p.suffix=='.pt':
        content=p.read_bytes()
        large.append({'remote_path':str(p),'sha256':hashlib.sha256(content).hexdigest(),'bytes':len(content)})
    elif p.suffix in {'.json','.py','.txt','.log'}:
        content=p.read_bytes()
        files[str(p.relative_to(root))]={'remote_path':str(p),'sha256':hashlib.sha256(content).hexdigest(),'base64':base64.b64encode(content).decode()}
bundle=json.dumps({'files':files,'raw_prediction_artifacts':large},separators=(',',':')).encode()
print('BUNDLE_SHA256',hashlib.sha256(bundle).hexdigest())
encoded=base64.b64encode(zlib.compress(bundle,9)).decode()
for i in range(0,len(encoded),512):
    print('BUNDLE_CHUNK',encoded[i:i+512],flush=True)
    time.sleep(.08)
print('BUNDLE_END')

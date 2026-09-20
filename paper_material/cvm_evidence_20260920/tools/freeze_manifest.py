"""Regenerate the inventory after intentional edits; verification remains separate."""
from pathlib import Path
import hashlib,json,os
ROOT=Path(__file__).resolve().parents[1]
if os.name=='nt' and not str(ROOT).startswith('\\\\?\\'):
    ROOT=Path('\\\\?\\'+str(ROOT))
EXCLUDED={'MANIFEST.json','SHA256SUMS.txt','00_index/verification.json'}
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
files=[]
for p in sorted(ROOT.rglob('*')):
    if not p.is_file() or '__pycache__' in p.parts:continue
    name=p.relative_to(ROOT).as_posix()
    if name in EXCLUDED:continue
    files.append({'path':name,'bytes':p.stat().st_size,'sha256':sha(p)})
data={'format_version':1,'date':'2026-09-20','branch':'codex/cvm-evidence-20260920',
      'hash_semantics':'SHA-256 of literal file bytes; archive .gitattributes disables newline conversion',
      'exclusions':sorted(EXCLUDED),'file_count':len(files),'total_bytes':sum(f['bytes'] for f in files),'files':files}
(ROOT/'MANIFEST.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'SHA256SUMS.txt').write_text(''.join(f"{f['sha256']}  {f['path']}\n" for f in files),encoding='utf-8')
print(json.dumps({'files':len(files),'bytes':data['total_bytes']}))

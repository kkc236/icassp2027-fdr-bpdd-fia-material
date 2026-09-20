"""Read-only integrity and key-result checks for the frozen evidence bundle.

Uses only Python's standard library. Does not import archived model or server code.
"""
from pathlib import Path
from decimal import Decimal
import csv, hashlib, json, os, statistics, sys

ROOT=Path(__file__).resolve().parents[1]
if os.name=='nt' and not str(ROOT).startswith('\\\\?\\'):
    ROOT=Path('\\\\?\\'+str(ROOT))
EXCLUDED={'MANIFEST.json','SHA256SUMS.txt','00_index/verification.json'}
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def read(relative):return json.loads((ROOT/relative).read_text(encoding='utf-8'))

manifest=read('MANIFEST.json')
paths=set()
for rec in manifest['files']:
    p=(ROOT/rec['path']).resolve()
    assert p.is_relative_to(ROOT.resolve()),rec['path']
    assert p.is_file() and p.stat().st_size==rec['bytes'],rec['path']
    assert sha(p)==rec['sha256'],rec['path']
    assert rec['path'] not in paths
    paths.add(rec['path'])
actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
assert actual-EXCLUDED==paths,{'unlisted':sorted(actual-EXCLUDED-paths),'missing':sorted(paths-actual)}

origins=read('00_index/source_origins.json')['copied_files']
for rec in origins:
    assert sha(ROOT/rec['path'])==rec['sha256'],rec['path']

release=read('01_manuscript/RELEASE_METADATA.json')
assert release['pdf_sha256']==sha(ROOT/'01_manuscript/MANUSCRIPT_CVM.pdf')
assert release['main_tex_sha256']==sha(ROOT/'01_manuscript/main.tex')
assert (release['pages'],release['tables'],release['figures'],release['references'])==(13,6,4,25)

claims=read('00_index/claim_evidence.json')
entries=claims if isinstance(claims,list) else claims.get('claims',claims.get('entries',[]))
assert entries, 'Missing claim index'
link_count=0
for entry in entries:
    for ref in entry['evidence']:
        rel=ref if isinstance(ref,str) else ref['path']
        assert (ROOT/rel).exists(),(entry['id'],rel)
        link_count+=1

references=read('00_index/reference_index.json')
refs=references if isinstance(references,list) else references.get('references',references.get('entries',[]))
assert len(refs)==25
for ref in refs:
    if ref.get('archive_path'):
        p=ROOT/ref['archive_path']
        assert p.is_file(),ref['key']
        assert sha(p)==ref['local_fulltext_sha256'],ref['key']
    for relative in ref.get('supplement_archive_paths',[]):
        assert (ROOT/relative).is_file(),relative

baseline=read('02_evidence/baseline_strict_val/fdr-vs-control-strict-final-paper-metrics.json')['baseline']
assert f"{baseline['overall']['map']*100:.3f}"=='21.911'
with (ROOT/'02_evidence/visdrone_g_f_training_20260909/results.csv').open(encoding='utf-8') as f:
    training=list(csv.DictReader(f))
assert len(training)==100
best=max(training,key=lambda r:float(r['metrics/mAP50-95(B)']))
assert int(best['epoch'])==97 and f"{float(best['metrics/mAP50-95(B)'])*100:.3f}"=='29.773'

timing=[]
for name in ['Baseline','G','G_F','G_B','Full']:
    row=read('02_evidence/batch8_efficiency_20260916/v1/'+name+'.json')
    samples=row['latency_samples_ms']
    assert len(samples)==row['sample_count']==300
    median=statistics.median(samples)
    assert abs(median-row['batch_median_ms'])<1e-9
    assert abs(8000/median-row['images_per_second_from_median'])<1e-9
    assert row['sha256_before'].lower()==row['sha256_after'].lower()
    timing.append({'arm':name,'samples':len(samples),'batch_median_ms':median})

base='02_evidence/reevaluation_completion_20260915/baseline_best_800_20260915/'
native=[]
for path,expected in [('files/test/imgsz640/summary.json','17.743'),
                     ('comparisons/FULL_CAPACITY_B_F/test/imgsz640/summary.json','23.604')]:
    rec=read(base+path)
    def find_ap(obj):
        if isinstance(obj,dict):
            for k,v in obj.items():
                if k in ('map','mAP50_95','metrics/mAP50-95(B)') and isinstance(v,(int,float)): yield v
                yield from find_ap(v)
        elif isinstance(obj,list):
            for item in obj:yield from find_ap(item)
    assert any(f'{v*100:.3f}'==expected for v in find_ap(rec)),path
    native.append(expected)

uavdt=[]
for name in ['baseline-exp','exp']:
    raw=(ROOT/'01_manuscript/inputs/uavdt'/name/'paper_data.txt').read_text(encoding='utf-8')
    line=next(s for s in raw.splitlines() if s.startswith('all('))
    uavdt.append(Decimal(line.split()[-1])*100)
assert uavdt==[Decimal('14.12'),Decimal('16.96')]
assert uavdt[1]-uavdt[0]==Decimal('2.84')
confirmation=read('01_manuscript/inputs/uavdt/author_confirmation.json')
assert confirmation['status']=='author_confirmed_full' and confirmation['checkpoint_verified'] is False

result={'status':'passed','files_hashed':len(paths),'original_copies_checked':len(origins),
        'claim_entries':len(entries),'claim_paths_checked':link_count,'reference_entries':len(refs),
        'manuscript':{'pages':13,'tables':6,'figures':4,'references':25,'unchanged_from_release':True},
        'native_test_AP':native,'uavdt_AP':[str(v) for v in uavdt],
        'baseline_strict_val_AP':'21.911','G_F_best_logged_val':{'epoch':97,'AP':'29.773'},
        'timing_samples_checked':sum(r['samples'] for r in timing),'timing':timing,
        'new_training':False,'new_model_inference':False,
        'scope':'Byte integrity, source mapping, recorded metric arithmetic; not a fresh scientific replication'}
print(json.dumps(result,ensure_ascii=False,indent=2))

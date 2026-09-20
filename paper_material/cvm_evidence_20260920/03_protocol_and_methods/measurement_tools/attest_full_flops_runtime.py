"""Read-only post-measurement source/checkpoint integrity and environment receipt."""
import hashlib,importlib.util,json,subprocess
from pathlib import Path
base=Path('/root/sj-tmp/evidence/full-flops-inventory-20260915-v2')
code=Path('/root/sj-tmp/lrs-v2/bpdd-capacity-v2-fia-code')
spec=importlib.util.spec_from_file_location('prior_measure','/root/sj-tmp/evidence/audit-remediation-efficiency-20260915-v3/measure.py')
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
previous=json.loads(Path('/root/sj-tmp/evidence/audit-remediation-efficiency-20260915-v3/efficiency.json').read_text())
sources={p:helper.sha256(code/p) for p in previous['source_sha256']}
assert sources==previous['source_sha256']
weights={name:helper.sha256(path) for name,(path,_) in helper.CHECKPOINTS.items()}
assert all(weights[name]==expected for name,(_,expected) in helper.CHECKPOINTS.items())
record={'status':'pass','completed_inventory':json.loads((base/'COMPLETE.json').read_text()),
 'source_sha256':sources,'checkpoint_sha256_after':weights,'environment':previous['environment'],
 'trace_script_sha256':helper.sha256(base/'trace.py'),
 'gpu_compute_processes':subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip(),
 'training_started':False,'checkpoint_files_written':False,'uavdt_in_scope':False}
payload=json.dumps(record,indent=2).encode()
receipt=base/'integrity_receipt.json'
if receipt.exists():assert receipt.read_bytes()==payload
else:receipt.write_bytes(payload)
print('RECEIPT',json.dumps(record),flush=True)

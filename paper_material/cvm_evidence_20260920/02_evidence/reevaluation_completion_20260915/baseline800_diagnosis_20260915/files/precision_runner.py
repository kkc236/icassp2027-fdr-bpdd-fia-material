import subprocess,json
from pathlib import Path
root=Path(__file__).resolve().parent
tasks=[('B_fresh640',640,'fresh_anchors'),('B_fp16anchors800',800,'fp16_anchor_generation')]
records=[]
for name,size,mode in tasks:
    p=subprocess.run(['/root/miniconda3/envs/lrs-v2/bin/python','-u',str(root/'diagnose_precision.py'),name,str(size),mode,str(root)],timeout=300)
    records.append({'name':name,'exit_code':p.returncode})
    (root/'PRECISION_STATUS.json').write_text(json.dumps(records,indent=2)+'\n')
(root/'PRECISION_COMPLETE.json').write_text(json.dumps(records,indent=2)+'\n')

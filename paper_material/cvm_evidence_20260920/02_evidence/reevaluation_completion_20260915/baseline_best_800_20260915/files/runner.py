import json
import subprocess
import traceback
from pathlib import Path
root=Path(__file__).resolve().parent
records=[]
for split, size in [('test',800),('test',640),('val',640),('val',800)]:
    record={'split':split,'imgsz':size,'status':'running'}
    (root/'CURRENT.json').write_text(json.dumps(record)+'\n')
    try:
        subprocess.run(['/root/miniconda3/envs/lrs-v2/bin/python','-u',str(root/'evaluate.py'),split,str(size),str(root)],check=True,timeout=600)
        record['status']='complete'
    except Exception as exc:
        record['status']='failed'
        record['error']=repr(exc)
        traceback.print_exc()
    records.append(record)
    (root/'RUN_STATUS.json').write_text(json.dumps(records,indent=2)+'\n')
    if record['status']=='failed':
        break
(root/'RUN_COMPLETE.json').write_text(json.dumps({'records':records},indent=2)+'\n')

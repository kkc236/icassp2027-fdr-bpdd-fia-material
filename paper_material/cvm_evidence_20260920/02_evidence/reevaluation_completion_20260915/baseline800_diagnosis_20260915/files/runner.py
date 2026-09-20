import subprocess,json,traceback
from pathlib import Path
root=Path(__file__).resolve().parent
tasks=[('B_native640',640,'native'),('B_native800',800,'native'),
    ('B_fresh800',800,'fresh_anchors'),('B_nofuse800',800,'no_fuse'),
    ('B_anchor800',800,'anchor_wh_0p8'),('B_boxwh800',800,'output_wh_0p8'),
    ('G_native640',640,'native'),('G_native800',800,'native')]
records=[]
for name,size,mode in tasks:
    (root/'CURRENT.json').write_text(json.dumps({'name':name,'status':'running'})+'\n')
    record={'name':name}
    try:
        subprocess.run(['/root/miniconda3/envs/lrs-v2/bin/python','-u',str(root/'diagnose.py'),name,str(size),mode,str(root)],check=True,timeout=300)
        record['status']='complete'
    except Exception as e:
        record.update(status='failed',error=repr(e))
        traceback.print_exc()
    records.append(record)
    (root/'STATUS.json').write_text(json.dumps(records,indent=2)+'\n')
(root/'COMPLETE.json').write_text(json.dumps(records,indent=2)+'\n')

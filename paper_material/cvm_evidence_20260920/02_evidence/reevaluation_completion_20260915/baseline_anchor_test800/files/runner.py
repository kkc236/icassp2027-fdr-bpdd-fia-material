import json,subprocess,traceback
from pathlib import Path
root=Path(__file__).resolve().parent
code=Path('/root/sj-tmp/lrs-v2/code')
command=['/root/miniconda3/envs/lrs-v2/bin/python','-u',str(code/'scripts/eval_baseline_anchor_scale.py'),
    '--checkpoint','/root/sj-tmp/checkpoints/fdr-formal-d97e1eb7/fdr-formal-seed0-control-d97e1eb7-epoch-0100.pt',
    '--data-yaml','/root/sj-tmp/evidence/visdrone_test_authority_20260915.yaml',
    '--output-dir',str(root/'test800'),'--split','test','--imgsz','800','--batch','8','--workers','8',
    '--device','0','--expected-images','1610','--anchor-scale-reference','640']
status={'status':'running','command':command,'fixed_scale':0.8,'test_parameter_search':False}
(root/'CURRENT.json').write_text(json.dumps(status,indent=2)+'\n')
try:
    with (root/'evaluation.log').open('w') as log:
        subprocess.run(command,cwd=code,stdout=log,stderr=subprocess.STDOUT,timeout=600,check=True)
    report=json.loads((root/'test800/summary.json').read_text())
    assert report['processed_images']==1610 and report['protocol']['split']=='test'
    assert report['protocol']['imgsz']==800 and report['actual_input_dtypes']==['torch.float32']
    assert report['anchor_correction']['applied'] and report['anchor_correction']['scale']==.8
    assert report['hashes_after']==report['hashes_before']
    assert report['hashes_after']['checkpoint']=='9C242711F44B7E68B360AF904AB7C44F64505C7136B7E7F90481092AE3308AF7'
    assert report['hashes_after']['data_yaml']=='3CCAF145213879DF0544CBB924A9F5EF8C2D9EB01D964FC18883E18D1197FE63'
    assert report['loaded_ema']
    status.update(status='complete',metrics=report['metrics'],processed_images=report['processed_images'])
    (root/'COMPLETE.json').write_text(json.dumps(status,indent=2)+'\n')
except Exception as error:
    status.update(status='failed',error=repr(error))
    (root/'FAILED.json').write_text(json.dumps(status,indent=2)+'\n')
    traceback.print_exc()
    raise
finally:
    (root/'CURRENT.json').write_text(json.dumps(status,indent=2)+'\n')

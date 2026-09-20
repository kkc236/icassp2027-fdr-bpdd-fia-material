import json,subprocess,traceback,hashlib
from pathlib import Path
root=Path(__file__).resolve().parent
code=Path('/root/sj-tmp/lrs-v2/code')
python='/root/miniconda3/envs/lrs-v2/bin/python'
checkpoint=Path('/root/sj-tmp/checkpoints/fdr-formal-d97e1eb7/fdr-formal-seed0-control-d97e1eb7-epoch-0100.pt')
data=Path('/root/sj-tmp/evidence/visdrone_test_authority_20260915.yaml')
expected_ckpt='9C242711F44B7E68B360AF904AB7C44F64505C7136B7E7F90481092AE3308AF7'
expected_data='3CCAF145213879DF0544CBB924A9F5EF8C2D9EB01D964FC18883E18D1197FE63'
records=[]
try:
    assert hashlib.sha256(checkpoint.read_bytes()).hexdigest().upper()==expected_ckpt
    assert hashlib.sha256(data.read_bytes()).hexdigest().upper()==expected_data
    test_command=[python,'-m','pytest','tests/test_inference_anchor_scale.py','tests/test_baseline_anchor_scale_cli.py','-q','--junitxml='+str(root/'server_tests.xml')]
    with (root/'server_tests.log').open('w') as log:
        subprocess.run(test_command,cwd=code,stdout=log,stderr=subprocess.STDOUT,timeout=180,check=True)
    (root/'SERVER_TESTS_PASSED.json').write_text(json.dumps({'command':test_command,'exit_code':0})+'\n')
    for size,expected in [(640,.21917411394055758),(800,.1910801258687437)]:
        name=f'val_calibrated_{size}'
        command=[python,'-u',str(code/'scripts/eval_baseline_anchor_scale.py'),
            '--checkpoint',str(checkpoint),'--data-yaml',str(data),'--output-dir',str(root/name),
            '--split','val','--imgsz',str(size),'--batch','8','--workers','8','--device','0',
            '--expected-images','548','--anchor-scale-reference','640']
        (root/'CURRENT.json').write_text(json.dumps({'name':name,'command':command,'status':'running'})+'\n')
        with (root/(name+'.log')).open('w') as log:
            subprocess.run(command,cwd=code,stdout=log,stderr=subprocess.STDOUT,timeout=300,check=True)
        report=json.loads((root/name/'summary.json').read_text())
        assert report['processed_images']==548
        assert report['hashes_after']=={'checkpoint':expected_ckpt,'data_yaml':expected_data}
        assert report['loaded_ema']
        assert abs(report['metrics']['map']-expected)<1e-9, (size,report['metrics']['map'],expected)
        assert report['anchor_correction']['applied']==(size==800)
        records.append({'name':name,'status':'complete','expected_map':expected,'actual_map':report['metrics']['map']})
        (root/'STATUS.json').write_text(json.dumps(records,indent=2)+'\n')
    (root/'COMPLETE.json').write_text(json.dumps({'status':'complete','records':records},indent=2)+'\n')
except Exception as error:
    (root/'FAILED.json').write_text(json.dumps({'status':'failed','error':repr(error),'records':records},indent=2)+'\n')
    traceback.print_exc()
    raise

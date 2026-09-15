"""Two-image CPU integration check; never competes with training for CUDA RAM."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    package=Path(__file__).resolve().parent
    root=Path(tempfile.mkdtemp(prefix='export-smoke-',dir=package))
    images=root/'images'
    images.mkdir()
    original=json.loads(Path('/root/sj-tmp/datasets/VisDrone-coco/annotations/instances_val.json').read_text())
    picked=original['images'][:2]
    ids={x['id'] for x in picked}
    for item in picked:
        (images/item['file_name']).symlink_to(Path('/root/sj-tmp/datasets/VisDrone/images/val')/item['file_name'])
    original['images']=picked
    original['annotations']=[x for x in original['annotations'] if x['image_id'] in ids]
    gt=root/'gt.json'
    gt.write_text(json.dumps(original))
    trainroot=Path('/root/sj-tmp/dfine-runs/dfine-l-visdrone-bs4-scratch-cross-20260914')
    jointroot=Path('/root/sj-tmp/runs/formal-safe-capacity-fia-20260912-lrsv2/formal-seed0-capacity-v3-safe-fia')
    import csv
    records=list(csv.DictReader((jointroot/'results.csv').open()))
    assert int(float(records[-1]['epoch']))==100, 'Joint final epoch is not 100'
    code='/root/sj-tmp/eval/uav-detection-baselines-fb0a6a16'
    common=['--images',str(images),'--device','cpu','--score-threshold','0.001']
    commands={
      'joint':[str(package/'export_joint_common.py'),'--code-root',code,
               '--checkpoint',str(jointroot/'weights/best.pt'),'--model-yaml',code+'/configs/rtdetr-l-lrs-gfdr-capacity-v3-safe-bpdd-fia.yaml'],
      'dfine':[str(package/'export_dfine_predictions.py'),'--dfine-root','/root/sj-tmp/dfine-bs4-official',
               '--config','/root/sj-tmp/dfine-bs4-official/configs/dfine/dfine_hgnetv2_l_visdrone_bs4_scratch.yml',
               '--checkpoint',str(trainroot/'global_best.pth')],
    }
    env={**os.environ,'OMP_NUM_THREADS':'2','MKL_NUM_THREADS':'2'}
    for model,args in commands.items():
        subprocess.run([sys.executable,*args,*common,'--output',str(root/f'{model}.jsonl')],check=True,env=env,timeout=300)
        subprocess.run([sys.executable,str(package/'evaluate_common.py'),'--predictions',str(root/f'{model}.jsonl'),
                        '--annotations',str(gt),'--coco-output',str(root/f'{model}.coco.json'),
                        '--report',str(root/f'{model}.metrics.json'),'--max-det','300'],check=True,env=env,timeout=120)
    report={'status':'passed','scope':'two real validation images, CPU export + ID mapping + common COCO evaluation; not final accuracy',
            'joint_completion_epoch':100,'output':str(root)}
    (package/'export-smoke-result.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report),flush=True)


if __name__=='__main__':
    main()

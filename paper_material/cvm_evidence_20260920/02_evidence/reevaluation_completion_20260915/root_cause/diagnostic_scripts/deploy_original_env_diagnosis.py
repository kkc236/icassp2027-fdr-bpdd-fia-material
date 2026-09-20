from pathlib import Path
import subprocess, json

root = Path('/root/sj-tmp/evidence/native_root_cause_20260915')
root.mkdir(exist_ok=True, parents=True)
child = r'''import sys, os, json, hashlib, inspect, platform
from pathlib import Path
name, code, checkpoint, out = sys.argv[1:]
os.chdir(code)
sys.path.insert(0, code)
import torch, ultralytics
from ultralytics import RTDETR
from ultralytics.models.rtdetr.val import RTDETRValidator
from src.bpdd_formal_evaluation import CachedScaleRTDETRValidator, summarize_native_box_metrics
from src.lpr_protocol import CATEGORY_NAMES

class Capture(CachedScaleRTDETRValidator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.files = []
    def update_metrics(self, preds, batch):
        self.files.extend(batch['im_file'])
        super().update_metrics(preds, batch)

out = Path(out)
environment = dict(python=platform.python_version(), executable=sys.executable, torch=torch.__version__, ultralytics=ultralytics.__version__, package=ultralytics.__file__)
environment['validator_sha256'] = hashlib.sha256(inspect.getsource(RTDETRValidator).encode()).hexdigest()
environment['cuda'] = torch.version.cuda
for split in ['val', 'test']:
    model = RTDETR(checkpoint)
    protocol = dict(data='/root/sj-tmp/evidence/visdrone_test_authority_20260915.yaml', model=checkpoint, task='detect', mode='val', imgsz=640, batch=8, workers=8, conf=0.001, max_det=300, nms=False, device='0', cache=False, half=False, rect=False, plots=False, save_json=False, save_txt=False, verbose=True, split=split)
    val = Capture(save_dir=out/name/split, args=protocol)
    val(model=model.model)
    expected = 548 if split == 'val' else 1610
    assert len(val.files) == len(val.scale_predictions) == expected
    report = dict(arm=name, split=split, environment=environment, protocol=protocol, checkpoint_sha256=hashlib.sha256(Path(checkpoint).read_bytes()).hexdigest(), processed=expected, **summarize_native_box_metrics(val.metrics.box, CATEGORY_NAMES))
    report['class_precision'] = val.metrics.box.p.tolist()
    report['class_recall'] = val.metrics.box.r.tolist()
    dest=out/name/split
    dest.mkdir(exist_ok=True, parents=True)
    (dest/'summary.json').write_text(json.dumps(report, indent=2))
    torch.save(dict(predictions=val.scale_predictions, targets=val.scale_targets, files=val.files), dest/'predictions.pt')
    print('COMPLETE', name, split, report['metrics'], flush=True)
    del val, model
    torch.cuda.empty_cache()
'''
arms = [
 ('G', '/root/sj-tmp/lrs-v2/code', '/root/sj-tmp/runs/visdrone-v2-existing-state-20260907/formal-seed0-lrs_fdr_feasible-v2/weights/best.pt'),
 ('GF', '/root/sj-tmp/lrs-v2/code', '/root/sj-tmp/runs/visdrone-v2-lrs-gfdr-fia-20260909/formal-seed0-lrs_gfdr_fia-v1/weights/best.pt'),
 ('GB', '/root/sj-tmp/lrs-v2/bpdd-capacity-v2-fia-code', '/root/sj-tmp/runs/formal-safe-capacity-bpdd-20260913-lrsv2/formal-seed0-capacity-v3-safe-bpdd/weights/best.pt'),
 ('Full', '/root/sj-tmp/lrs-v2/bpdd-capacity-v2-fia-code', '/root/sj-tmp/runs/formal-safe-capacity-fia-20260912-lrsv2/formal-seed0-capacity-v3-safe-fia/weights/best.pt')]
compile(child, 'diagnose.py', 'exec')
(root/'diagnose.py').write_text(child)
runner = 'import subprocess,json\nfrom pathlib import Path\n'
runner += f'root=Path({str(root)!r})\n'
runner += f'arms={arms!r}\n'
runner += "for name,code,ck in arms:\n    subprocess.run(['/root/miniconda3/envs/lrs-v2/bin/python','-u',str(root/'diagnose.py'),name,code,ck,str(root)],check=True)\n"
runner += "(root/'COMPLETE.json').write_text(json.dumps({'completed':True,'arms':4,'splits':2}))\n"
compile(runner, 'runner.py', 'exec')
(root/'runner.py').write_text(runner)
assert not (root/'runner.pid').exists(), 'Existing diagnostic runner: inspect before starting duplicate'
with (root/'runner.log').open('w') as stream:
    proc = subprocess.Popen(['/root/miniconda3/envs/lrs-v2/bin/python','-u',str(root/'runner.py')],stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
(root/'runner.pid').write_text(str(proc.pid))
print('STARTED',proc.pid,str(root))

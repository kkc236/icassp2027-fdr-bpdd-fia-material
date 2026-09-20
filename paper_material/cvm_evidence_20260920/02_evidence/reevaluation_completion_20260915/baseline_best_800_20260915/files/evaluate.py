import hashlib
import inspect
import json
import os
import platform
import sys
import time
from pathlib import Path

split, size, root = sys.argv[1:]
size = int(size)
root = Path(root)
code_root = '/root/sj-tmp/lrs-v2/code'
os.chdir(code_root)
sys.path.insert(0, code_root)
import torch
import ultralytics
from ultralytics import RTDETR
from ultralytics.models.rtdetr.val import RTDETRValidator
from ultralytics.engine.trainer import BaseTrainer
from src.bpdd_formal_evaluation import summarize_native_box_metrics
from src.lpr_protocol import CATEGORY_NAMES

checkpoint = Path('/root/sj-tmp/checkpoints/fdr-formal-d97e1eb7/fdr-formal-seed0-control-d97e1eb7-epoch-0100.pt')
data = Path('/root/sj-tmp/evidence/visdrone_test_authority_20260915.yaml')
expected_images = {'test':1610, 'val':548}[split]
out = root / split / f'imgsz{size}'
out.mkdir(parents=True, exist_ok=True)

def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8*1024*1024), b''):
            h.update(block)
    return h.hexdigest().upper()

checkpoint_sha = sha256(checkpoint)
data_sha = sha256(data)
assert checkpoint_sha == '9C242711F44B7E68B360AF904AB7C44F64505C7136B7E7F90481092AE3308AF7'
assert data_sha == '3CCAF145213879DF0544CBB924A9F5EF8C2D9EB01D964FC18883E18D1197FE63'
ckpt = torch.load(checkpoint, map_location='cpu', weights_only=False)
curve = {k.strip(): v for k, v in ckpt['train_results'].items()}
epochs = curve['epoch']
maps = curve['metrics/mAP50-95(B)']
best_epochs = [int(e) for e,m in zip(epochs,maps) if m == max(maps)]
assert [int(e) for e in epochs] == list(range(1,101))
assert best_epochs == [100] and int(ckpt['epoch'])+1 == 100
assert abs(float(ckpt['best_fitness']) - float(ckpt['train_metrics']['fitness'])) < 1e-9
assert abs(float(ckpt['best_fitness']) - max(maps)) < 1e-9
assert ckpt['ema'] is not None
identity = {
    'baseline_authority':'fdr-formal-d97e1eb7-seed0-control',
    'archive_path':str(checkpoint), 'archive_sha256':checkpoint_sha,
    'completed_epoch':100, 'unique_best_epochs':best_epochs,
    'selection_metric':'training validation metrics/mAP50-95(B)',
    'best_fitness':ckpt['best_fitness'], 'train_metrics':ckpt['train_metrics'],
    'train_results':curve, 'train_args':ckpt['train_args'],
    'checkpoint_version':ckpt['version'],
    'evaluation_state':'EMA from the archived validation-best epoch (also final epoch)',
    'literal_stripped_best_file_available':False,
    'literal_stripped_best_byte_identity_claimed':False,
    'note':'Best-epoch selection is established by the embedded full 100-epoch curve and matching fitness; no test-driven checkpoint selection.'
}
(out/'BEST_EPOCH_IDENTITY.json').write_text(json.dumps(identity, indent=2, default=str)+'\n')
(out/'save_model_runtime_source.txt').write_text(inspect.getsource(BaseTrainer.save_model))
del ckpt

class CaptureValidator(RTDETRValidator):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.input_shapes=set()
        self.input_dtypes=set()
        self.processed_images=0
    def preprocess(self,batch):
        batch=super().preprocess(batch)
        self.input_shapes.add(tuple(int(x) for x in batch['img'].shape))
        self.input_dtypes.add(str(batch['img'].dtype))
        return batch
    def update_metrics(self,preds,batch):
        self.processed_images+=len(preds)
        return super().update_metrics(preds,batch)

protocol = {
    'model':str(checkpoint),'data':str(data),'task':'detect','mode':'val',
    'split':split,'imgsz':size,'batch':8,'workers':8,'conf':0.001,
    'max_det':300,'nms':False,'device':'0','cache':False,'half':False,
    'rect':False,'plots':False,'save_json':False,'save_txt':False,'verbose':True
}
model=RTDETR(str(checkpoint))
loaded_ema = model.model is model.ckpt.get('ema')
assert loaded_ema, 'Refusing evaluation of a non-EMA checkpoint state'
start=time.monotonic()
validator=CaptureValidator(save_dir=out/'validator',args=dict(protocol))
validator(model=model.model)
elapsed=time.monotonic()-start
assert validator.processed_images == expected_images
assert all(shape[-2:]==(size,size) for shape in validator.input_shapes)
assert validator.input_dtypes == {'torch.float32'}
report={
    'kind':'frozen_baseline_validation_best_epoch_same_validator',
    'arm':'BASELINE_STRICT_CONTROL_BEST','split':split,
    'checkpoint':{'path':str(checkpoint),'sha256':checkpoint_sha,'completed_epoch':100,'loaded_ema':loaded_ema},
    'best_epoch_identity_file':'BEST_EPOCH_IDENTITY.json',
    'data':{'path':str(data),'sha256':data_sha,'expected_images':expected_images},
    'protocol':protocol,'effective_validator_args':vars(validator.args),
    'environment':{'python':platform.python_version(),'torch':torch.__version__,
        'cuda':torch.version.cuda,'ultralytics':ultralytics.__version__,
        'ultralytics_file':ultralytics.__file__,'executable':sys.executable},
    'actual_input_shapes':[list(x) for x in sorted(validator.input_shapes)],
    'actual_input_dtypes':sorted(validator.input_dtypes),
    'processed_images':validator.processed_images,'wall_seconds':elapsed,
    'parameter_count':sum(p.numel() for p in model.model.parameters()),
    **summarize_native_box_metrics(validator.metrics.box,CATEGORY_NAMES)
}
(out/'summary.json').write_text(json.dumps(report,indent=2,sort_keys=True,default=str)+'\n')
print('BASELINE_BEST_COMPLETE',split,size,json.dumps(report['metrics']),flush=True)

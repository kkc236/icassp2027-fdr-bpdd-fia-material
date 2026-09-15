"""Run official D-FINE with observational provenance and checkpoint capture.

No optimizer, loss, sampling or official stage-control behavior is overridden.
The evaluated model is saved before the official stage manager can restore a
different checkpoint. Epoch refers to chronological loop index, not the restored
solver.last_epoch counter.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path


def write_json(path, payload):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + '\n', encoding='utf-8')
    tmp.replace(path)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--dfine-root', type=Path, required=True)
    p.add_argument('--config', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--preflight-only', action='store_true')
    a = p.parse_args()
    sys.path.insert(0, str(a.dfine_root.resolve()))
    import torch
    from src.core import YAMLConfig
    from src.misc import dist_utils
    from src.solver import TASKS
    import src.solver.det_solver as det_solver

    if a.output.exists() and any(a.output.iterdir()):
        raise RuntimeError(f'Refusing nonempty training output: {a.output}')
    dist_utils.setup_distributed(0, 'builtin', seed=0)
    cfg = YAMLConfig(str(a.config), device='cuda:0', seed=0,
                     output_dir=str(a.output), use_amp=False)
    assert cfg.epochs == 100 and cfg.yaml_cfg['train_dataloader']['total_batch_size'] == 4
    assert not cfg.yaml_cfg['HGNetv2']['pretrained']
    model = cfg.model
    frozen = [n for n, v in model.backbone.named_parameters() if not v.requires_grad]
    if frozen:
        raise RuntimeError(f'Random backbone contains frozen parameters: {frozen[:8]}')
    bn_count = sum(isinstance(m, torch.nn.BatchNorm2d) for m in model.backbone.modules())
    assert bn_count > 0, 'Scratch backbone must have trainable BatchNorm'
    groups = [{'parameters': sum(v.numel() for v in g['params']),
               'lr': g['lr'], 'weight_decay': g['weight_decay']} for g in cfg.optimizer.param_groups]
    record = {'format_version': 2, 'status': 'preflight_passed', 'pid': os.getpid(),
              'started_at': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
              'config': str(a.config), 'config_sha256': sha(a.config),
              'resolved_config': cfg.yaml_cfg, 'parameters': sum(v.numel() for v in model.parameters()),
              'trainable_parameters': sum(v.numel() for v in model.parameters() if v.requires_grad),
              'backbone_frozen_parameters': frozen, 'backbone_batchnorm_layers': bn_count,
              'optimizer_groups': groups, 'torch': torch.__version__, 'cuda': torch.version.cuda,
              'gpu': torch.cuda.get_device_name(0), 'accumulation_steps': 1,
              'source_files': {str(f.relative_to(a.dfine_root)): sha(f)
                               for f in sorted((a.dfine_root / 'src').rglob('*.py'))},
              'selection': 'native validation AP50:95 global best over chronological epochs 0..99; final snapshot also retained',
              'training_protocol': 'scratch-adapted official D-FINE; FP32, batch4; official stage resets retained',
              'comparison_type': 'cross_training_protocol_common_evaluation'}
    print(json.dumps({k:v for k,v in record.items() if k not in ('resolved_config','source_files')}, default=str), flush=True)
    if a.preflight_only:
        return
    a.output.mkdir(parents=True, exist_ok=False)
    write_json(a.output / 'run-authority.json', record)
    solver = TASKS[cfg.yaml_cfg['task']](cfg)
    original_evaluate = det_solver.evaluate
    best = -float('inf')
    started = time.monotonic()

    def snapshot(module, name, epoch, ap):
        path = a.output / name
        temporary = path.with_suffix('.pth.tmp')
        torch.save({'model': module.state_dict(), 'epoch': epoch,
                    'native_val_ap': ap, 'inference_only': True,
                    'config_sha256': record['config_sha256']}, temporary)
        temporary.replace(path)

    def evaluate_recorded(*args, **kwargs):
        nonlocal best
        result = original_evaluate(*args, **kwargs)
        epoch = int(args[6] if len(args) > 6 else kwargs['epoch'])
        ap = float(result[0]['coco_eval_bbox'][0])
        if not 0 <= ap <= 1:
            raise RuntimeError(f'Invalid validation AP: {ap}')
        row = {'epoch_zero_based': epoch, 'epoch_completed': epoch + 1,
               'native_val_ap': ap, 'elapsed_seconds': time.monotonic() - started,
               'max_cuda_allocated_bytes': torch.cuda.max_memory_allocated(),
               'max_cuda_reserved_bytes': torch.cuda.max_memory_reserved()}
        if ap > best:
            snapshot(args[0], 'global_best.pth', epoch, ap)
            best = ap
            write_json(a.output / 'global-best.json', row)
        snapshot(args[0], 'last_evaluated.pth', epoch, ap)
        with (a.output / 'chronological-validation.jsonl').open('a', encoding='utf-8') as f:
            f.write(json.dumps(row, sort_keys=True) + '\n')
        write_json(a.output / 'progress.json', {'status': 'training', **row, 'best_native_val_ap': best})
        return result

    det_solver.evaluate = evaluate_recorded
    try:
        solver.fit()
        rows = [json.loads(x) for x in (a.output / 'chronological-validation.jsonl').read_text().splitlines()]
        if [x['epoch_zero_based'] for x in rows] != list(range(100)):
            raise RuntimeError('Chronological 100-epoch completion check failed')
        write_json(a.output / 'completion.json', {'status': 'training_complete', 'epochs': 100,
                   'best_native_val_ap': best, 'elapsed_seconds': time.monotonic() - started})
    except BaseException as exc:
        write_json(a.output / 'failure.json', {'status': 'failed', 'type': type(exc).__name__, 'message': str(exc)})
        raise
    finally:
        det_solver.evaluate = original_evaluate
        dist_utils.cleanup()


if __name__ == '__main__':
    main()

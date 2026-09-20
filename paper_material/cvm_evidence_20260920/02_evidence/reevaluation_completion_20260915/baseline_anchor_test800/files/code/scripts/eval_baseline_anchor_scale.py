"""Native VisDrone baseline evaluation with opt-in reference-anchor scaling.

No training, no checkpoint rewriting, and no changes to other evaluation CLIs.
"""
from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import platform
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8*1024*1024), b''):
            digest.update(block)
    return digest.hexdigest().upper()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkpoint', type=Path, required=True)
    parser.add_argument('--data-yaml', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True, help='new directory; never overwrite previous results')
    parser.add_argument('--anchor-scale-reference', type=int, default=None,
                        help='opt in using checkpoint training size, e.g. 640; omitted means native')
    parser.add_argument('--imgsz', type=int, default=800)
    parser.add_argument('--split', choices=['val','test'], default='val')
    parser.add_argument('--batch', type=int, default=8)
    parser.add_argument('--workers', type=int, default=8)
    parser.add_argument('--device', default='0')
    parser.add_argument('--expected-images', type=int, default=None)
    return parser


def validate_options(args: argparse.Namespace) -> None:
    for size in [args.imgsz, args.anchor_scale_reference]:
        if size is not None and (type(size) is not int or size <= 0 or size % 32):
            raise ValueError('image sizes must be positive integers divisible by 32')
    if args.batch <= 0 or args.workers < 0 or (args.expected_images is not None and args.expected_images <= 0):
        raise ValueError('invalid batch/workers/expected-images')


def validate_reference_size(checkpoint: dict, reference: int | None) -> None:
    if reference is None:
        return
    train_args = checkpoint.get('train_args') or {}
    recorded = train_args.get('imgsz') if isinstance(train_args, dict) else getattr(train_args, 'imgsz', None)
    if type(recorded) is not int or recorded != reference:
        raise ValueError(f'anchor reference {reference} does not match checkpoint training imgsz={recorded!r}')


def prepare_eval_model(model, device: str):
    """Use native backend preparation (fusion before device transfer).

    Pre-transferring to GPU changes the fusion arithmetic and slightly changes
    AP even when calibration is a no-op. Let the native backend own the order.
    """
    from ultralytics.nn.autobackend import AutoBackend
    from ultralytics.utils.torch_utils import select_device
    backend = AutoBackend(model=model, device=select_device(device), fp16=False)
    return backend.backend.model.eval()


def run(args: argparse.Namespace) -> dict:
    validate_options(args)
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    try:
        import torch
        import ultralytics
        from ultralytics import RTDETR
        from ultralytics.models.rtdetr.val import RTDETRValidator
        from ultralytics.nn.modules.head import RTDETRDecoder
        from src.inference_anchor_scale import calibrated_rtdetr_anchors
        from src.bpdd_formal_evaluation import summarize_native_box_metrics

        checkpoint, data = args.checkpoint.resolve(), args.data_yaml.resolve()
        before = {'checkpoint': file_sha256(checkpoint), 'data_yaml': file_sha256(data)}
        detector = RTDETR(str(checkpoint))
        validate_reference_size(detector.ckpt, args.anchor_scale_reference)
        heads = [m for m in detector.model.modules() if isinstance(m, RTDETRDecoder)]
        if len(heads) != 1 or type(heads[0]) is not RTDETRDecoder or heads[0].nc != 10:
            raise TypeError('this entry point is validated for the stock 10-class VisDrone baseline only')
        # Finish native fusion/device preparation before opening the scope, so
        # cached-anchor restoration stays on the model's current device.
        detector.model = prepare_eval_model(detector.model, args.device)
        loaded_ema = detector.model is detector.ckpt.get('ema')
        protocol = {
            'model': str(checkpoint), 'data': str(data), 'task': 'detect', 'mode': 'val',
            'split': args.split, 'imgsz': args.imgsz, 'batch': args.batch, 'workers': args.workers,
            'device': args.device, 'conf': .001, 'max_det': 300, 'nms': False, 'half': False,
            'rect': False, 'cache': False, 'plots': False, 'save_json': False, 'save_txt': False,
            'verbose': True,
        }

        class CaptureValidator(RTDETRValidator):
            def __init__(self, *a, **kw):
                super().__init__(*a, **kw)
                self.shapes, self.dtypes, self.images = set(), set(), 0

            def preprocess(self, batch):
                batch = super().preprocess(batch)
                self.shapes.add(tuple(batch['img'].shape))
                self.dtypes.add(str(batch['img'].dtype))
                if tuple(batch['img'].shape[-2:]) != (args.imgsz, args.imgsz) or batch['img'].dtype != torch.float32:
                    raise RuntimeError('unexpected native evaluator input size/dtype')
                return batch

            def update_metrics(self, preds, batch):
                self.images += len(preds)
                return super().update_metrics(preds, batch)

        validator = CaptureValidator(save_dir=out/'validator', args=dict(protocol))
        start = time.monotonic()
        with calibrated_rtdetr_anchors(
            detector.model, reference_imgsz=args.anchor_scale_reference or args.imgsz,
            inference_imgsz=args.imgsz, enabled=args.anchor_scale_reference is not None,
        ) as correction:
            (out/'protocol.json').write_text(json.dumps({'protocol': protocol, 'anchor_correction': correction, 'hashes_before': before}, indent=2)+'\n', encoding='utf-8')
            validator(model=detector.model)
        if args.expected_images is not None and validator.images != args.expected_images:
            raise RuntimeError(f'image count mismatch: expected {args.expected_images}, got {validator.images}')
        if validator.images != len(validator.dataloader.dataset):
            raise RuntimeError('incomplete dataset evaluation')
        after = {'checkpoint': file_sha256(checkpoint), 'data_yaml': file_sha256(data)}
        if before != after:
            raise RuntimeError('checkpoint or dataset YAML changed during evaluation')
        report = {
            'status': 'complete', 'kind': 'frozen-baseline-native-validator-anchor-scale-v1',
            'protocol': protocol, 'anchor_correction': correction,
            'hashes_before': before, 'hashes_after': after, 'loaded_ema': loaded_ema,
            'processed_images': validator.images,
            'actual_input_shapes': sorted(validator.shapes), 'actual_input_dtypes': sorted(validator.dtypes),
            'wall_seconds': time.monotonic()-start,
            'parameter_count': sum(p.numel() for p in detector.model.parameters()),
            'environment': {'python': platform.python_version(), 'torch': torch.__version__,
                            'ultralytics': ultralytics.__version__, 'cuda': torch.version.cuda},
            'implementation_sha256': {str(path): file_sha256(path) for path in [Path(__file__).resolve(), ROOT/'src/inference_anchor_scale.py']},
            'native_anchor_generator_sha256': hashlib.sha256(inspect.getsource(RTDETRDecoder._generate_anchors).encode()).hexdigest(),
            **summarize_native_box_metrics(validator.metrics.box, [detector.names[i] for i in range(10)]),
        }
        temporary = out/'summary.json.tmp'
        temporary.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False)+'\n', encoding='utf-8')
        temporary.replace(out/'summary.json')
        return report
    except Exception as error:
        (out/'FAILED.json').write_text(json.dumps({'status': 'failed', 'error': repr(error)}, indent=2)+'\n', encoding='utf-8')
        raise


if __name__ == '__main__':
    print(json.dumps(run(build_parser().parse_args()), ensure_ascii=False, indent=2))

"""Opt-in stock RT-DETR reference-anchor calibration, with no weight mutation.

This is an inference protocol change, not the project's FDR feasible geometry.
Use a fresh/eval model and do not share it with another thread during the scope.
"""
from contextlib import contextmanager
from types import MethodType

import torch
from torch import nn
from ultralytics.nn.modules.head import RTDETRDecoder


@contextmanager
def calibrated_rtdetr_anchors(
    model: nn.Module, *, reference_imgsz: int, inference_imgsz: int, enabled: bool = True
):
    """Scale anchor w/h by reference/inference; restore all temporary state.

    Square inputs only. Equal sizes or disabled correction do not regenerate
    anchors: this preserves the original checkpoint's cached-anchor precision.
    Custom FDR heads are intentionally not opted in without their own evidence.
    """
    for value in (reference_imgsz, inference_imgsz):
        if type(value) is not int or value <= 0 or value % 32:
            raise ValueError('image sizes must be positive integers divisible by 32')
    heads = [m for m in model.modules() if isinstance(m, RTDETRDecoder)]
    if len(heads) != 1 or type(heads[0]) is not RTDETRDecoder:
        raise TypeError('calibration requires exactly one stock RTDETRDecoder')
    head = heads[0]
    if model.training or head.training:
        raise RuntimeError('anchor calibration is inference-only; call model.eval() first')
    if getattr(head, '_anchor_scale_scope_active', False):
        raise RuntimeError('anchor calibration is already active on this model')
    scale = reference_imgsz / inference_imgsz
    applied = bool(enabled and scale != 1.0)
    metadata = {
        'protocol': 'reference-anchor-wh-scale-v1' if enabled else 'native',
        'requested': bool(enabled), 'applied': applied,
        'reference_imgsz': reference_imgsz, 'inference_imgsz': inference_imgsz,
        'scale': scale if enabled else 1.0,
        'training_changed': False, 'weights_changed': False,
    }
    if not applied:
        yield metadata
        return

    missing = object()
    names = ('_generate_anchors', 'dynamic', 'shapes', 'anchors', 'valid_mask')
    saved = {name: (name in head.__dict__, getattr(head, name, missing)) for name in names}
    original_generator = head._generate_anchors

    def generate(self, shapes, grid_size=0.05, dtype=torch.float32, device='cpu', eps=1e-2):
        if model.training or self.training:
            raise RuntimeError('anchor calibration is inference-only')
        return original_generator(shapes, grid_size=grid_size * scale, dtype=dtype, device=device, eps=eps)

    def check_input(module, args, kwargs):
        if module.training or head.training:
            raise RuntimeError('anchor calibration is inference-only')
        value = args[0] if args else kwargs.get('x')
        if not isinstance(value, torch.Tensor) or value.ndim != 4 or tuple(value.shape[-2:]) != (inference_imgsz, inference_imgsz):
            raise ValueError(f'calibrated input must be a BCHW tensor of size {inference_imgsz}x{inference_imgsz}')

    hook = None
    try:
        head._anchor_scale_scope_active = True
        head._generate_anchors = MethodType(generate, head)
        # Rebuilding prevents a pre-existing native 800 cache from bypassing the
        # wrapper. This matches the validated diagnostic, including its dtype.
        head.dynamic = True
        hook = model.register_forward_pre_hook(check_input, with_kwargs=True)
        yield metadata
    finally:
        if hook is not None:
            hook.remove()
        for name, (was_own, value) in saved.items():
            if was_own:
                setattr(head, name, value)
            elif name in head.__dict__:
                delattr(head, name)
        if '_anchor_scale_scope_active' in head.__dict__:
            delattr(head, '_anchor_scale_scope_active')

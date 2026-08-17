"""Detached distribution-head replay for ACR-BPDD auxiliary supervision.

The helper records the real input of each FDR distribution head through
``forward_pre_hook`` callbacks.  Recorded tensors are detached immediately.
Replaying the same six heads therefore preserves gradients for their private
parameters without creating a second backward path through the shared decoder.
"""

from __future__ import annotations

from collections.abc import Iterable

import torch
from torch import Tensor, nn
from torch.utils.hooks import RemovableHandle


FDR_REPLAY_LAYERS = 6
FDR_DISTRIBUTION_DIM = 132


class ACRBPDDDetachedHeadReplay:
    """Capture detached FDR head inputs and replay one isolated BPDD graph.

    A capture window is explicit and single-use::

        replay.begin_capture()
        detector_forward()
        cumulative_logits = replay.replay()

    ``replay`` consumes the cache.  Callers must begin a fresh window for every
    microbatch.  The helper is intentionally not an ``nn.Module`` so its
    transient cache and hook state cannot enter a model ``state_dict``.
    """

    def __init__(
        self,
        heads: Iterable[nn.Module],
        *,
        expected_layers: int = FDR_REPLAY_LAYERS,
        output_dim: int = FDR_DISTRIBUTION_DIM,
    ) -> None:
        if int(expected_layers) != FDR_REPLAY_LAYERS:
            raise ValueError("ACR-BPDD replay requires exactly six layers")
        if int(output_dim) <= 0:
            raise ValueError("output_dim must be positive")

        self._head_source = heads if isinstance(heads, (list, nn.ModuleList)) else tuple(heads)
        resolved = self._resolve_heads(initial=True)
        identifiers = tuple(id(head) for head in resolved)
        if len(set(identifiers)) != len(identifiers):
            raise ValueError("ACR-BPDD replay heads contain duplicate module identities")

        self._expected_layers = int(expected_layers)
        self._output_dim = int(output_dim)
        self._head_ids = identifiers
        self._capture_enabled = False
        self._replaying = False
        self._removed = False
        self._cached_inputs: list[Tensor | None] = [None] * self._expected_layers
        self._input_shape: tuple[int, ...] | None = None
        self._input_device: torch.device | None = None
        self._handles: list[RemovableHandle] = []

        try:
            for index, head in enumerate(resolved):
                handle = head.register_forward_pre_hook(self._make_capture_hook(index))
                self._handles.append(handle)
        except Exception:
            for handle in self._handles:
                handle.remove()
            self._handles.clear()
            self._removed = True
            raise

    @property
    def capture_enabled(self) -> bool:
        """Return whether the current training forward is being observed."""

        return self._capture_enabled

    @property
    def cached_layer_count(self) -> int:
        """Return the number of decoder-layer inputs in the current window."""

        return sum(value is not None for value in self._cached_inputs)

    @property
    def cached_input_ids(self) -> tuple[int, ...]:
        """Expose detached input identities for lifecycle evidence/tests."""

        return tuple(id(value) for value in self._cached_inputs if value is not None)

    def _resolve_heads(self, *, initial: bool = False) -> tuple[nn.Module, ...]:
        try:
            resolved = tuple(self._head_source)
        except TypeError as error:
            raise TypeError("heads must be an iterable of torch modules") from error
        if len(resolved) != FDR_REPLAY_LAYERS:
            prefix = "ACR-BPDD replay requires" if initial else "ACR-BPDD replay head identity changed: expected"
            raise ValueError(f"{prefix} exactly six heads")
        if not all(isinstance(head, nn.Module) for head in resolved):
            raise TypeError("every ACR-BPDD replay head must be an nn.Module")
        return resolved

    def _validated_heads(self) -> tuple[nn.Module, ...]:
        try:
            heads = self._resolve_heads()
        except Exception:
            self.clear()
            raise
        if tuple(id(head) for head in heads) != self._head_ids:
            self.clear()
            raise RuntimeError("ACR-BPDD replay head identity changed after hook registration")
        return heads

    @staticmethod
    def _head_device(head: nn.Module) -> torch.device | None:
        devices = {
            tensor.device
            for tensor in (*tuple(head.parameters()), *tuple(head.buffers()))
        }
        if len(devices) > 1:
            raise RuntimeError("ACR-BPDD distribution head spans multiple devices")
        return next(iter(devices), None)

    def _make_capture_hook(self, index: int):
        def capture_hook(module: nn.Module, args: tuple[object, ...]) -> None:
            if self._removed or self._replaying or not self._capture_enabled:
                return
            if not module.training:
                self.clear()
                return
            try:
                self._capture_input(index, module, args)
            except Exception:
                self.clear()
                raise

        return capture_hook

    def _capture_input(
        self,
        index: int,
        module: nn.Module,
        args: tuple[object, ...],
    ) -> None:
        if id(module) != self._head_ids[index]:
            raise RuntimeError("ACR-BPDD replay hook observed a changed head identity")
        if self._cached_inputs[index] is not None:
            raise RuntimeError(f"ACR-BPDD replay captured decoder layer {index} more than once")
        if len(args) != 1 or not isinstance(args[0], Tensor):
            raise TypeError("ACR-BPDD distribution heads must receive one tensor input")

        value = args[0]
        if value.ndim != 3:
            raise ValueError("ACR-BPDD captured input shape must be [B,Q,C]")
        shape = tuple(int(dimension) for dimension in value.shape)
        if self._input_shape is None:
            self._input_shape = shape
            self._input_device = value.device
        elif shape != self._input_shape:
            raise ValueError(
                f"ACR-BPDD captured input shape changed from {self._input_shape} to {shape}"
            )
        elif value.device != self._input_device:
            raise RuntimeError("ACR-BPDD captured inputs must stay on one device")

        head_device = self._head_device(module)
        if head_device is not None and head_device != value.device:
            raise RuntimeError("ACR-BPDD head and captured input devices differ")
        if not value.is_floating_point():
            raise TypeError("ACR-BPDD captured inputs must be floating point tensors")
        if not bool(torch.isfinite(value).all().item()):
            raise FloatingPointError("non-finite ACR-BPDD captured head input")

        detached = value.detach()
        if detached.requires_grad or detached.grad_fn is not None:
            raise RuntimeError("ACR-BPDD failed to detach a captured head input")
        self._cached_inputs[index] = detached

    def begin_capture(self) -> bool:
        """Begin one training capture window, returning false in evaluation."""

        if self._removed:
            raise RuntimeError("ACR-BPDD replay hooks were removed")
        self.clear()
        heads = self._validated_heads()
        if not all(head.training for head in heads):
            return False
        self._capture_enabled = True
        return True

    def replay(self, *, cumulative: bool = True) -> Tensor:
        """Replay the six private heads and return ``[L,B,Q,132]`` logits."""

        if self._removed:
            raise RuntimeError("ACR-BPDD replay hooks were removed")
        heads = self._validated_heads()
        if self.cached_layer_count != self._expected_layers:
            self.clear()
            raise RuntimeError("ACR-BPDD replay requires six captured layers")

        captured = tuple(self._cached_inputs)
        if any(value is None for value in captured):
            self.clear()
            raise RuntimeError("ACR-BPDD replay cache is incomplete")

        self._replaying = True
        try:
            deltas: list[Tensor] = []
            for index, (head, value) in enumerate(zip(heads, captured, strict=True)):
                if value is None:  # narrowed above; retained for static type checkers
                    raise RuntimeError("ACR-BPDD replay cache is incomplete")
                delta = head(value)
                expected_shape = (*value.shape[:2], self._output_dim)
                if not isinstance(delta, Tensor) or tuple(delta.shape) != expected_shape:
                    raise ValueError(
                        f"ACR-BPDD layer {index} output shape must be {expected_shape}"
                    )
                if delta.device != value.device:
                    raise RuntimeError("ACR-BPDD replay output changed device")
                deltas.append(delta)

            raw = torch.stack(deltas)
            if not bool(torch.isfinite(raw).all().item()):
                raise FloatingPointError("non-finite ACR-BPDD replay logits")
            if not cumulative:
                return raw

            cumulative_logits: list[Tensor] = []
            running: Tensor | int = 0
            for delta in deltas:
                running = delta + running
                cumulative_logits.append(running)
            return torch.stack(cumulative_logits)
        finally:
            self._replaying = False
            self.clear()

    def clear(self) -> None:
        """Disable capture and discard every transient detached input."""

        self._capture_enabled = False
        self._cached_inputs = [None] * self._expected_layers
        self._input_shape = None
        self._input_device = None

    def remove(self) -> None:
        """Remove all hooks safely; repeated calls are harmless."""

        self.clear()
        if self._removed:
            return
        for handle in self._handles:
            handle.remove()
        self._handles.clear()
        self._removed = True


__all__ = [
    "ACRBPDDDetachedHeadReplay",
    "FDR_DISTRIBUTION_DIM",
    "FDR_REPLAY_LAYERS",
]

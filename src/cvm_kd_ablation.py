"""Full-capacity KD ablations; the original Safe model remains the default."""

from __future__ import annotations

from dataclasses import asdict, replace
import json
from pathlib import Path
from typing import Any

import torch

from src.bpdd_capacity_loss import CapacityBPDDOptions
from src.fdr_protocol import public_state_sha256
from src.lrs_runtime_evidence import RuntimeEvidenceRecorder
from src.rtdetr_bpdd_capacity_fia import CapacityBPDDFIASafeTrainer


KD_MODES = ("no_kd", "edge_only", "mixed")
BASE_COMMIT = "a43056af2a843ec9bae109d3420367c13f3bcef6"


def resolved_options(mode: str) -> CapacityBPDDOptions:
    if mode not in KD_MODES:
        raise ValueError(f"unknown KD mode: {mode}")
    return CapacityBPDDOptions(
        enabled=mode != "no_kd", cls_weight=0.0,
        decay_start=80, decay_end=100, mixed_box_gate=mode != "edge_only",
    )


def apply_kd_mode(model: Any, mode: str) -> None:
    """Change only training KD controls, after the original Safe construction."""
    expected = resolved_options(mode)
    original = model.capacity_options
    # Refuse unrelated models rather than silently changing their recipe.
    invariant = asdict(replace(original, enabled=expected.enabled,
                               mixed_box_gate=expected.mixed_box_gate))
    if invariant != asdict(expected):
        raise ValueError("KD ablation requires the frozen v3-Safe loss recipe")
    model.capacity_options = expected
    model.kd_ablation_mode = mode
    model.capacity_method_revision = f"cvm-kd-ablation-{mode}-20260921"
    if getattr(model, "criterion", None) is not None:
        model.criterion.capacity_options = expected


def validate_resume_model(weights: Any, mode: str) -> None:
    if getattr(weights, "kd_ablation_mode", None) != mode:
        raise ValueError("resume checkpoint KD mode is absent or different")
    if asdict(weights.capacity_options) != asdict(resolved_options(mode)):
        raise ValueError("resume checkpoint effective KD options differ")


class KDAblationTrainer(CapacityBPDDFIASafeTrainer):
    """Same graph/initialization/optimizer as Safe, with explicit resume identity."""

    def __init__(self, *args, kd_mode: str, **kwargs) -> None:
        resolved_options(kd_mode)
        self.kd_mode = kd_mode
        super().__init__(*args, **kwargs)

    def get_model(self, cfg=None, weights=None, verbose=True):
        if weights is not None:
            if not self.resume:
                raise ValueError("KD ablations must start fresh or explicitly resume")
            validate_resume_model(weights, self.kd_mode)
        # Always build the unchanged Safe architecture and private modules.
        model = super().get_model(cfg=cfg, weights=None, verbose=verbose)
        self.fresh_initial_state_sha256 = public_state_sha256(model.state_dict())
        if weights is not None:
            model.load(weights, verbose=False)
        apply_kd_mode(model, self.kd_mode)
        return model


class KDAblationRecorder:
    """Keep full-runtime.jsonl and add unambiguous KD selection diagnostics."""

    count_fields = ("edge_candidates_before_iou", "mixed_rejected_edges",
                    "active_edges", "applied_edges", "selected_weight_sum")
    mean_fields = ("unscaled_localization_loss", "localization_loss", "schedule_scale")

    def __init__(self, mode: str) -> None:
        self.mode = mode
        self.original = RuntimeEvidenceRecorder()
        self.sums: dict[str, float] = {}
        self.observations = 0

    def reset(self, trainer) -> None:
        model = getattr(trainer.model, "module", trainer.model)
        if getattr(model, "kd_ablation_mode", None) != self.mode:
            raise RuntimeError("runtime model has lost its KD mode")
        if asdict(model.capacity_options) != asdict(resolved_options(self.mode)):
            raise RuntimeError("runtime KD options changed")
        self.original.reset(trainer)
        self.sums = {name: 0.0 for name in (*self.count_fields, *self.mean_fields)}
        self.observations = 0

    def capture(self, trainer) -> None:
        self.original.capture(trainer)
        model = getattr(trainer.model, "module", trainer.model)
        stats = model.last_capacity_statistics
        for key in self.sums:
            value = stats[key].detach()
            if not torch.isfinite(value):
                raise FloatingPointError(f"nonfinite KD diagnostic: {key}")
            self.sums[key] += float(value)
        self.observations += 1

    def write(self, trainer) -> None:
        self.original.write(trainer)
        record = {
            "completed_epoch": int(trainer.epoch) + 1,
            "mode": self.mode,
            "effective_options": asdict(resolved_options(self.mode)),
            "observations": self.observations,
            **{key: self.sums[key] for key in self.count_fields},
            **{key + "_mean": self.sums[key] / max(self.observations, 1)
               for key in self.mean_fields},
        }
        path = Path(trainer.save_dir) / "kd-runtime.jsonl"
        with path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, sort_keys=True) + "\n")


__all__ = ["KD_MODES", "BASE_COMMIT", "resolved_options", "apply_kd_mode",
           "validate_resume_model", "KDAblationTrainer", "KDAblationRecorder"]

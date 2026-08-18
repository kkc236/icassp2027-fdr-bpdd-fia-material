"""Active-confidence-renormalized, head-isolated BPDD integration.

ACR-BPDD changes training supervision only.  The stock/FDR forward graph is
left untouched; a temporary hook window records the six real FDR box-head
inputs, detaches them, and replays only those small private heads for BPDD.
Consequently the auxiliary gradient cannot enter the shared decoder.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch
from torch import Tensor
from ultralytics.utils import RANK

from src.acr_bpdd_replay import ACRBPDDDetachedHeadReplay
from src.bpdd_loss import BPDDDetectionLoss, bpdd_distribution_loss
from src.rtdetr_fdr import FDRRTDETRDetectionModel, _load_initial_state
from src.rtdetr_fdr_bpdd import FDRBPDDDetectionModel, FDRBPDDTrainer


ACR_BPDD_MODEL_CFG = (
    Path(__file__).resolve().parents[1]
    / "configs"
    / "rtdetr-l-fdr-acr-bpdd.yaml"
)


class FDRACRBPDDDetectionModel(FDRBPDDDetectionModel):
    """FDR+BPDD with active-confidence scaling and a shared-gradient firewall."""

    supports_common_gradient_firewall = True

    def __init__(
        self,
        cfg: str | Path | dict = ACR_BPDD_MODEL_CFG,
        ch: int = 3,
        nc: int | None = None,
        verbose: bool = True,
        *,
        private_seed: int | None = None,
    ) -> None:
        super().__init__(
            cfg=cfg,
            ch=ch,
            nc=nc,
            verbose=verbose,
            private_seed=private_seed,
        )
        raw_options = self.yaml.get("bpdd_loss")
        if not isinstance(raw_options, dict):
            raise TypeError("ACR-BPDD model YAML requires a bpdd_loss mapping")
        self.common_gradient_firewall = bool(
            raw_options.get("common_gradient_firewall", False)
        )
        if self.bpdd_options.normalization != "reliability_mass":
            raise ValueError("ACR-BPDD requires reliability-mass normalization")
        if not self.common_gradient_firewall:
            raise ValueError("ACR-BPDD requires the common-gradient firewall")
        self.acr_replay = ACRBPDDDetachedHeadReplay(
            self.model[-1].dec_bbox_head,
            query_tail=300,
            strict_checks=False,
        )
        self.last_acr_replay_max_abs_diff: float | None = None
        self.last_acr_replay_tolerance: float | None = None

    def predict(
        self,
        x: Tensor,
        profile: bool = False,
        visualize: bool = False,
        batch: dict[str, Any] | None = None,
        augment: bool = False,
        embed: list[int] | None = None,
    ) -> tuple | Tensor:
        """Capture private head inputs only around one real training forward."""

        capture = self.acr_replay.begin_capture() if self.training else False
        try:
            output = super().predict(
                x,
                profile=profile,
                visualize=visualize,
                batch=batch,
                augment=augment,
                embed=embed,
            )
        except BaseException:
            self.acr_replay.clear()
            raise
        if self.training and not capture:
            self.acr_replay.clear()
            raise RuntimeError("ACR-BPDD training forward did not enable replay capture")
        return output

    def _normal_replayed_corners(self) -> Tensor:
        evidence = self.last_fdr_evidence
        if evidence is None:
            self.acr_replay.clear()
            raise RuntimeError("ACR-BPDD requires retained FDR evidence")
        replayed = self.acr_replay.replay(cumulative=True)
        normal_queries = int(evidence.corner_logits.shape[2])
        if replayed.shape[2] != normal_queries:
            raise RuntimeError("ACR-BPDD replay does not contain exactly 300 normal Queries")
        normal = replayed
        if normal.shape != evidence.corner_logits.shape:
            raise RuntimeError("ACR-BPDD replay/FDR corner shapes differ")
        retained = evidence.corner_logits.detach().float()
        absolute_error = (normal.detach().float() - retained).abs()
        difference = absolute_error.max()
        if normal.dtype in {torch.float16, torch.bfloat16}:
            epsilon = float(torch.finfo(normal.dtype).eps)
            allowed_error = epsilon + epsilon * retained.abs()
        else:
            allowed_error = torch.full_like(absolute_error, 1.0e-6)
        value = float(difference.cpu())
        tolerance = float(allowed_error.max().cpu())
        self.last_acr_replay_max_abs_diff = value
        self.last_acr_replay_tolerance = tolerance
        if (
            not bool(torch.isfinite(absolute_error).all().item())
            or value > tolerance
        ):
            raise RuntimeError(
                "ACR-BPDD replay changed cumulative corner values: "
                f"max_abs={value}, tolerance={tolerance}"
            )
        # Preserve the exact stock/FDR forward values while the zero-valued
        # straight-through residual keeps the BPDD gradient private to the
        # detached distribution-head replay.
        return evidence.corner_logits.detach() + (normal - normal.detach())

    def loss(
        self,
        batch: dict[str, Tensor],
        preds: tuple | None = None,
    ) -> tuple[Tensor, Tensor]:
        """Compute stock+FDR normally and BPDD on detached-head replay logits."""

        if not hasattr(self, "criterion"):
            self.criterion = self.init_criterion()
        if not isinstance(self.criterion, BPDDDetectionLoss):
            raise TypeError("ACR-BPDD model criterion was unexpectedly replaced")
        self.last_acr_replay_max_abs_diff = None
        self.last_acr_replay_tolerance = None
        if not self.training:
            self.acr_replay.clear()
            return super().loss(batch, preds)

        try:
            self.criterion.bpdd_runtime_enabled = False
            total, displayed = FDRRTDETRDetectionModel.loss(self, batch, preds)
            private_corners = self._normal_replayed_corners()
            evidence = self.last_fdr_evidence
            if evidence is None:
                raise RuntimeError("ACR-BPDD FDR evidence disappeared")
            assignments = self.criterion.normal_assignment_snapshot()
            if len(assignments) != private_corners.shape[0] + 1:
                raise RuntimeError("ACR-BPDD stock assignment count changed")
            targets = batch["bboxes"].to(device=private_corners.device)
            matched = self.criterion._matched_bpdd_inputs(
                private_corners,
                evidence.pre_boxes,
                targets,
                assignments[-1],
            )
            result = bpdd_distribution_loss(
                *matched,
                options=self.bpdd_options,
            )
        except BaseException:
            self.acr_replay.clear()
            raise
        finally:
            self.criterion.bpdd_runtime_enabled = True

        self.last_fdr_losses["loss_bpdd"] = result.loss
        self.last_bpdd_statistics = dict(result.statistics)
        self.criterion.last_bpdd_statistics = dict(result.statistics)
        return total + result.loss, displayed


class FDRACRBPDDTrainer(FDRBPDDTrainer):
    """Frozen FDR trainer that constructs only the ACR-BPDD candidate graph."""

    def get_model(
        self,
        cfg: dict | str | None = None,
        weights: str | None = None,
        verbose: bool = True,
    ) -> FDRACRBPDDDetectionModel:
        del cfg
        model = FDRACRBPDDDetectionModel(
            ACR_BPDD_MODEL_CFG,
            nc=self.data["nc"],
            ch=self.data["channels"],
            verbose=verbose and RANK == -1,
            private_seed=10_000 + self.experiment_seed,
        )
        if weights:
            model.load(weights)
        else:
            _load_initial_state(
                model,
                getattr(self, "initial_state_path", None),
                variant="fdr",
            )
        return model


__all__ = [
    "ACR_BPDD_MODEL_CFG",
    "FDRACRBPDDDetectionModel",
    "FDRACRBPDDTrainer",
]

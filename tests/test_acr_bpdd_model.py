from __future__ import annotations

from pathlib import Path
from copy import deepcopy
import io

import pytest
import torch

from src.acr_bpdd_replay import ACRBPDDDetachedHeadReplay
from src.bpdd_loss import BPDDOptions
from src.rtdetr_fdr import FDRRTDETRDetectionModel, FDRTrainer
from src.rtdetr_fdr_acr_bpdd import (
    ACR_BPDD_MODEL_CFG,
    FDRACRBPDDDetectionModel,
    FDRACRBPDDTrainer,
)
from src.rtdetr_fdr_bpdd import FDRBPDDDetectionModel


FDR_CFG = Path(__file__).resolve().parents[1] / "configs" / "rtdetr-l-fdr.yaml"


@pytest.fixture(scope="module")
def paired_models() -> tuple[FDRRTDETRDetectionModel, FDRACRBPDDDetectionModel]:
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(91_701)
        fdr = FDRRTDETRDetectionModel(FDR_CFG, nc=10, verbose=False)
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(91_701)
        acr = FDRACRBPDDDetectionModel(ACR_BPDD_MODEL_CFG, nc=10, verbose=False)
    return fdr, acr


def test_acr_model_is_state_and_parameter_exact_to_fdr(
    paired_models: tuple[FDRRTDETRDetectionModel, FDRACRBPDDDetectionModel],
) -> None:
    fdr, acr = paired_models
    assert acr.state_dict().keys() == fdr.state_dict().keys()
    for name, expected in fdr.state_dict().items():
        torch.testing.assert_close(acr.state_dict()[name], expected, rtol=0, atol=0)
    assert sum(parameter.numel() for parameter in acr.parameters()) == sum(
        parameter.numel() for parameter in fdr.parameters()
    )


def test_acr_model_uses_only_frozen_yaml_controls(
    paired_models: tuple[FDRRTDETRDetectionModel, FDRACRBPDDDetectionModel],
) -> None:
    _fdr, acr = paired_models
    assert acr.bpdd_options == BPDDOptions(
        enabled=True,
        weight=0.5,
        temperature=0.5,
        margin=0.02,
        eps=1e-6,
        normalization="reliability_mass",
        reliability_floor=0.5,
    )
    assert acr.common_gradient_firewall is True
    assert isinstance(acr.acr_replay, ACRBPDDDetachedHeadReplay)
    assert acr.acr_replay.query_tail == 300
    assert acr.acr_replay.strict_checks is False


def test_plain_bpdd_model_rejects_acr_yaml_fail_closed() -> None:
    with pytest.raises(ValueError, match="firewall-capable"):
        FDRBPDDDetectionModel(ACR_BPDD_MODEL_CFG, nc=10, verbose=False)


def test_acr_eval_is_bit_exact_to_plain_fdr(
    paired_models: tuple[FDRRTDETRDetectionModel, FDRACRBPDDDetectionModel],
) -> None:
    fdr, acr = paired_models
    acr.load_state_dict(fdr.state_dict(), strict=True)
    fdr.eval()
    acr.eval()
    image = torch.zeros((1, 3, 128, 128))

    with torch.inference_mode():
        fdr_output, fdr_raw = fdr(image)
        acr_output, acr_raw = acr(image)

    torch.testing.assert_close(acr_output, fdr_output, rtol=0, atol=0)
    for actual, expected in zip(acr_raw[:-1], fdr_raw[:-1], strict=True):
        torch.testing.assert_close(actual, expected, rtol=0, atol=0)
    assert acr_raw[-1] is fdr_raw[-1] is None
    assert acr.acr_replay.cached_layer_count == 0


def test_acr_training_bpdd_graph_reaches_only_distribution_heads(
) -> None:
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(91_702)
        acr = FDRACRBPDDDetectionModel(ACR_BPDD_MODEL_CFG, nc=10, verbose=False)
    acr.train()
    batch = {
        "img": torch.zeros((1, 3, 128, 128)),
        "cls": torch.tensor([[0.0]]),
        "bboxes": torch.tensor([[0.5, 0.5, 0.2, 0.2]]),
        "batch_idx": torch.tensor([0.0]),
    }

    total, displayed = acr.loss(batch)
    bpdd = acr.last_fdr_losses["loss_bpdd"]
    common = next(acr.model[0].parameters())
    private = next(acr.model[-1].dec_bbox_head[0].parameters())
    common_gradient, private_gradient = torch.autograd.grad(
        bpdd,
        (common, private),
        retain_graph=True,
        allow_unused=True,
    )

    assert torch.isfinite(total)
    assert torch.isfinite(displayed).all()
    assert torch.isfinite(bpdd)
    assert common_gradient is None
    assert private_gradient is not None
    assert torch.isfinite(private_gradient).all()
    assert acr.last_fdr_evidence is not None
    assert acr.last_fdr_evidence.dn_corner_logits is not None
    assert acr.last_fdr_evidence.dn_corner_logits.shape[2] > 0
    assert acr.last_fdr_evidence.corner_logits.shape[2] == 300
    assert acr.last_acr_replay_max_abs_diff is not None
    assert acr.last_acr_replay_max_abs_diff <= 1e-6
    assert acr.acr_replay.cached_layer_count == 0


def test_acr_loss_failure_always_clears_transient_hooks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(91_703)
        acr = FDRACRBPDDDetectionModel(ACR_BPDD_MODEL_CFG, nc=10, verbose=False)
    acr.train()
    criterion = acr.init_criterion()
    acr.criterion = criterion

    def fail_after_forward(*_args, **_kwargs):
        raise RuntimeError("injected stock criterion failure")

    monkeypatch.setattr(criterion, "stock_plus_fgl", fail_after_forward)
    batch = {
        "img": torch.zeros((1, 3, 128, 128)),
        "cls": torch.tensor([[0.0]]),
        "bboxes": torch.tensor([[0.5, 0.5, 0.2, 0.2]]),
        "batch_idx": torch.tensor([0.0]),
    }

    with pytest.raises(RuntimeError, match="injected"):
        acr.loss(batch)

    assert acr.acr_replay.capture_enabled is False
    assert acr.acr_replay.cached_layer_count == 0
    assert all(not head._forward_pre_hooks for head in acr.model[-1].dec_bbox_head)
    assert criterion.bpdd_runtime_enabled is True


def test_acr_trainer_keeps_fdr_fixed_protocol_and_model_cfg() -> None:
    assert issubclass(FDRACRBPDDTrainer, FDRTrainer)
    assert FDRACRBPDDTrainer.controlled_amp_scale == 128.0
    trainer = FDRACRBPDDTrainer.__new__(FDRACRBPDDTrainer)
    trainer.data = {"nc": 10, "channels": 3}
    trainer.experiment_seed = 0
    trainer.initial_state_path = None

    model = trainer.get_model(cfg=str(FDR_CFG), weights=None, verbose=False)

    assert isinstance(model, FDRACRBPDDDetectionModel)
    assert model.bpdd_options.normalization == "reliability_mass"


def test_acr_model_deepcopy_and_checkpoint_pickle_are_hook_clean(
    paired_models: tuple[FDRRTDETRDetectionModel, FDRACRBPDDDetectionModel],
) -> None:
    _fdr, acr = paired_models
    assert all(not head._forward_pre_hooks for head in acr.model[-1].dec_bbox_head)

    copied = deepcopy(acr).float()
    buffer = io.BytesIO()
    torch.save(copied, buffer)
    buffer.seek(0)
    restored = torch.load(buffer, map_location="cpu", weights_only=False)

    assert isinstance(restored, FDRACRBPDDDetectionModel)
    assert restored.state_dict().keys() == acr.state_dict().keys()
    assert all(
        not head._forward_pre_hooks for head in restored.model[-1].dec_bbox_head
    )

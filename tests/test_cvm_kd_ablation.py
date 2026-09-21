from __future__ import annotations

from dataclasses import asdict
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest
import torch

import src.bpdd_capacity_loss as loss_module
from src.bpdd_capacity_loss import quality_gated_capacity_distillation
from src.cvm_kd_ablation import (
    BASE_COMMIT, KD_MODES, KDAblationRecorder, KDAblationTrainer,
    apply_kd_mode, resolved_options, validate_resume_model,
)
from src.rtdetr_bpdd_capacity import CapacityBPDDDetectionLoss
from src.rtdetr_bpdd_capacity_fia import CapacityBPDDFIASafeTrainer


@pytest.fixture(autouse=True)
def small_cpu_thread_pool():
    previous = torch.get_num_threads()
    torch.set_num_threads(2)
    yield
    torch.set_num_threads(previous)


def inputs():
    student = torch.zeros(2, 1, 2, 4, 33)
    teacher = torch.zeros(1, 2, 4, 33)
    student[..., 26] = 4
    teacher[..., 16] = 5
    return (
        student.requires_grad_(), torch.zeros(2, 1, 2, 3, requires_grad=True),
        teacher.requires_grad_(), torch.zeros(1, 2, 3, requires_grad=True),
        torch.tensor([0.5, 0.5, 0.2, 0.2]).expand(1, 2, 4),
        torch.tensor([[0.5, 0.5, 0.2, 0.2]]), torch.tensor([1]),
    )


def evaluate(values, options, function=quality_gated_capacity_distillation, epoch=50):
    match = tuple(torch.tensor([0]) for _ in range(3))
    return function(*values, [match, match], match, options, epoch=epoch)


def test_default_mixed_matches_frozen_full_loss_and_gradients():
    root = Path(__file__).resolve().parents[1]
    source = subprocess.check_output(
        ["git", "show", f"{BASE_COMMIT}:src/bpdd_capacity_loss.py"], cwd=root, text=True,
    )
    name = "_frozen_capacity_loss_for_parity"
    module = importlib.util.module_from_spec(importlib.util.spec_from_loader(name, loader=None))
    sys.modules[name] = module
    try:
        exec(compile(source, name, "exec"), module.__dict__)
        old_inputs, new_inputs = inputs(), inputs()
        old = evaluate(old_inputs, module.CapacityBPDDOptions(
            cls_weight=0, decay_start=80, decay_end=100), module.quality_gated_capacity_distillation)
        new = evaluate(new_inputs, resolved_options("mixed"))
        assert new.loss.item() > 0
        torch.testing.assert_close(new.loss, old.loss, rtol=0, atol=0)
        old.loss.backward()
        new.loss.backward()
        torch.testing.assert_close(new_inputs[0].grad, old_inputs[0].grad, rtol=0, atol=0)
        for key in old.statistics:
            torch.testing.assert_close(new.statistics[key], old.statistics[key], rtol=0, atol=0)
    finally:
        sys.modules.pop(name)


def test_edge_only_removes_only_iou_gate_and_keeps_teacher_detached(monkeypatch):
    def reject(source, *args, **kwargs):
        return torch.zeros(source.shape[0], dtype=torch.bool), torch.zeros(source.shape[0])
    monkeypatch.setattr(loss_module, "decoded_teacher_iou_gate", reject)
    mixed = evaluate(inputs(), resolved_options("mixed"))
    values = inputs()
    edge = evaluate(values, resolved_options("edge_only"))
    assert mixed.loss.item() == 0 and edge.loss.item() > 0
    assert edge.statistics["mixed_rejected_edges"] == edge.statistics["active_edges"]
    assert edge.statistics["applied_edges"] > 0
    edge.loss.backward()
    assert values[0].grad.abs().sum() > 0
    assert values[2].grad is None
    monkeypatch.setattr(loss_module, "decoded_teacher_iou_gate", lambda source, *a, **k:
                        (torch.ones(source.shape[0], dtype=torch.bool), torch.zeros(source.shape[0])))
    all_kept = evaluate(inputs(), resolved_options("mixed"))
    torch.testing.assert_close(edge.loss, all_kept.loss, rtol=0, atol=0)


@pytest.mark.parametrize("mode,epoch", [("no_kd", 50), ("mixed", 10), ("edge_only", 100)])
def test_candidates_are_not_reported_as_applied_when_kd_is_zero(mode, epoch):
    result = evaluate(inputs(), resolved_options(mode), epoch=epoch)
    assert result.statistics["edge_candidates_before_iou"] > 0
    assert result.statistics["active_edges"] > 0
    assert result.statistics["applied_edges"] == 0
    assert result.loss.item() == 0


def test_no_kd_keeps_expert_direct_losses_and_gradients():
    criterion = CapacityBPDDDetectionLoss(
        nc=3, use_vfl=True, fgl_weight=.15, supervise_pre_boxes=False,
        supervise_dn_fdr=False, reliability_shrinkage_alpha=.25,
        capacity_options=resolved_options("no_kd"),
    )
    reference = torch.tensor([.5, .5, .2, .2]).expand(1, 2, 4).clone()
    boxes = reference.unsqueeze(0).expand(7, 1, 2, 4).clone().requires_grad_()
    scores = torch.zeros(7, 1, 2, 3, requires_grad=True)
    corners = torch.zeros(6, 1, 2, 132, requires_grad=True)
    expert_boxes = (reference + torch.tensor([.03, .03, .02, .02])).requires_grad_()
    expert_scores = torch.zeros(1, 2, 3, requires_grad=True)
    expert_corners = torch.zeros(1, 2, 132, requires_grad=True)
    batch = {"cls": torch.tensor([1]), "bboxes": reference[0, :1].clone(), "gt_groups": [1]}
    match = [(torch.tensor([0]), torch.tensor([0]))]
    losses = criterion(
        (boxes, scores), batch, corner_logits=corners, pre_boxes=reference,
        normal_match_indices=[match] * 7, expert_boxes=expert_boxes,
        expert_scores=expert_scores, expert_corners=expert_corners,
        student_classes=scores[1:], completed_epoch=50,
    )
    assert losses["loss_bpdd_capacity_loc"].item() == 0
    assert losses["loss_bpdd_capacity_cls"].item() == 0
    direct = [value for name, value in losses.items() if "expert" in name]
    assert len(direct) >= 4 and sum(direct).item() > 0
    sum(direct).backward()
    for tensor in (expert_boxes, expert_scores, expert_corners):
        assert tensor.grad is not None and tensor.grad.abs().sum() > 0


class TinyFull(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.weight = torch.nn.Parameter(torch.zeros(2))
        self.capacity_options = resolved_options("mixed")
        self.criterion = SimpleNamespace(capacity_options=self.capacity_options)

    def load(self, weights, verbose=False):
        self.load_state_dict(weights.state_dict())


@pytest.mark.parametrize("mode", KD_MODES)
def test_trainer_mode_reaches_criterion_and_survives_serialization_resume(mode, monkeypatch):
    monkeypatch.setattr(CapacityBPDDFIASafeTrainer, "get_model", lambda *a, **k: TinyFull())
    trainer = object.__new__(KDAblationTrainer)
    trainer.kd_mode, trainer.resume = mode, False
    fresh = trainer.get_model(verbose=False)
    assert asdict(fresh.criterion.capacity_options) == asdict(resolved_options(mode))
    with torch.no_grad():
        fresh.weight.fill_(3.5)
    buffer = io.BytesIO()
    torch.save(fresh, buffer)
    buffer.seek(0)
    weights = torch.load(buffer, weights_only=False)
    trainer.resume = True
    resumed = trainer.get_model(weights=weights, verbose=False)
    torch.testing.assert_close(resumed.weight, fresh.weight, rtol=0, atol=0)
    assert resumed.kd_ablation_mode == mode
    assert asdict(resumed.criterion.capacity_options) == asdict(resolved_options(mode))
    wrong_mode = "mixed" if mode != "mixed" else "no_kd"
    with pytest.raises(ValueError, match="mode"):
        validate_resume_model(weights, wrong_mode)


def test_mode_switch_does_not_change_model_tensor_state():
    model = TinyFull()
    before = {key: value.clone() for key, value in model.state_dict().items()}
    for mode in KD_MODES:
        apply_kd_mode(model, mode)
        for key, value in model.state_dict().items():
            torch.testing.assert_close(value, before[key], rtol=0, atol=0)


def test_recorder_preserves_candidate_and_applied_distinction(tmp_path):
    mode = "no_kd"
    model = TinyFull()
    apply_kd_mode(model, mode)
    model.last_capacity_statistics = evaluate(inputs(), resolved_options(mode)).statistics
    trainer = SimpleNamespace(model=model, epoch=49, save_dir=tmp_path)
    recorder = KDAblationRecorder(mode)
    recorder.reset(trainer)
    recorder.capture(trainer)
    recorder.write(trainer)
    import json
    record = json.loads((tmp_path / "kd-runtime.jsonl").read_text())
    assert record["active_edges"] > 0 and record["applied_edges"] == 0
    assert (tmp_path / "full-runtime.jsonl").is_file()

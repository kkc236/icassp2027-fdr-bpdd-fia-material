from __future__ import annotations

import math

import pytest
import torch

from src.bpdd_loss import BPDDOptions, bpdd_distribution_loss


EXPECTED_STATISTICS = {
    "active_edge_ratio",
    "mean_reliability",
    "mean_teacher_improvement",
    "mixture_beats_final_ratio",
    "mean_mixture_advantage_over_final",
    "matched_queries",
    "eligible_edges",
    "denominator",
    "reliability_mass",
    "normalization_gain",
}


def _targets(matches: int = 1) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    indices = torch.zeros((matches, 4), dtype=torch.long)
    right = torch.zeros((matches, 4), dtype=torch.float32)
    left = torch.ones((matches, 4), dtype=torch.float32)
    return indices, right, left


def _binary_logits(
    student_target_probability: float,
    teacher_target_probability: float,
    *,
    dtype: torch.dtype = torch.float32,
) -> torch.Tensor:
    probabilities = torch.tensor(
        [
            [student_target_probability, 1.0 - student_target_probability],
            [teacher_target_probability, 1.0 - teacher_target_probability],
        ],
        dtype=torch.float32,
    )
    return probabilities.log().to(dtype).reshape(2, 1, 1, 2).repeat(1, 1, 4, 1)


def _acr_options(**overrides: object) -> BPDDOptions:
    values: dict[str, object] = {
        "normalization": "reliability_mass",
        "reliability_floor": 0.5,
        "margin": 0.0,
    }
    values.update(overrides)
    return BPDDOptions(**values)


def test_options_default_to_v1_and_validate_acr_fields() -> None:
    options = BPDDOptions()

    assert options.normalization == "eligible_edges"
    assert options.reliability_floor == pytest.approx(0.5)

    for normalization in ("", "active_edges", "RELIABILITY_MASS", None):
        with pytest.raises(ValueError, match="normalization"):
            BPDDOptions(normalization=normalization)  # type: ignore[arg-type]

    for reliability_floor in (0.0, -0.1, 1.0001, math.nan, math.inf):
        with pytest.raises(ValueError, match="reliability_floor"):
            BPDDOptions(reliability_floor=reliability_floor)


def test_default_eligible_edge_normalization_preserves_v1_formula() -> None:
    logits = _binary_logits(0.2, 0.3)
    indices, right, left = _targets()
    weight = 0.5
    result = bpdd_distribution_loss(
        logits,
        indices,
        right,
        left,
        options=BPDDOptions(weight=weight, margin=0.0),
    )

    reliability = math.log(0.3 / 0.2) / -math.log(0.2)
    divergence = 0.3 * math.log(0.3 / 0.2) + 0.7 * math.log(0.7 / 0.8)
    expected = weight * reliability * divergence

    assert result.loss.item() == pytest.approx(expected, rel=1e-6, abs=1e-8)
    assert result.statistics["denominator"].item() == pytest.approx(4.0)
    assert result.statistics["normalization_gain"].item() == pytest.approx(1.0)


def test_reliability_mass_uses_exact_mass_when_above_floor() -> None:
    logits = _binary_logits(0.25, 0.75)
    indices, right, left = _targets()
    weight = 0.5
    result = bpdd_distribution_loss(
        logits,
        indices,
        right,
        left,
        options=_acr_options(weight=weight),
    )

    reliability = math.log(0.75 / 0.25) / -math.log(0.25)
    divergence = 0.75 * math.log(0.75 / 0.25) + 0.25 * math.log(0.25 / 0.75)
    reliability_mass = 4.0 * reliability

    assert reliability > 0.5
    assert result.loss.item() == pytest.approx(weight * divergence, rel=1e-6)
    assert result.statistics["reliability_mass"].item() == pytest.approx(
        reliability_mass, rel=1e-6
    )
    assert result.statistics["denominator"].item() == pytest.approx(
        reliability_mass, rel=1e-6
    )
    assert result.statistics["normalization_gain"].item() == pytest.approx(
        4.0 / reliability_mass, rel=1e-6
    )


def test_rho_half_caps_amplification_at_two_times_v1() -> None:
    logits = _binary_logits(0.2, 0.3)
    indices, right, left = _targets()
    v1 = bpdd_distribution_loss(
        logits,
        indices,
        right,
        left,
        options=BPDDOptions(weight=0.5, margin=0.0),
    )
    acr = bpdd_distribution_loss(
        logits,
        indices,
        right,
        left,
        options=_acr_options(weight=0.5),
    )

    assert acr.statistics["reliability_mass"].item() < 2.0
    assert acr.statistics["denominator"].item() == pytest.approx(2.0)
    assert acr.statistics["normalization_gain"].item() == pytest.approx(2.0)
    assert acr.loss.item() == pytest.approx(2.0 * v1.loss.item(), rel=1e-6)


def test_zero_reliability_is_finite_noop_with_floor_denominator() -> None:
    logits = _binary_logits(0.75, 0.25).requires_grad_()
    indices, right, left = _targets()
    result = bpdd_distribution_loss(
        logits, indices, right, left, options=_acr_options()
    )
    result.loss.backward()

    torch.testing.assert_close(result.loss, torch.zeros_like(result.loss))
    assert result.statistics["reliability_mass"].item() == pytest.approx(0.0)
    assert result.statistics["denominator"].item() == pytest.approx(2.0)
    assert result.statistics["normalization_gain"].item() == pytest.approx(2.0)
    assert logits.grad is not None
    assert torch.isfinite(logits.grad).all()
    torch.testing.assert_close(logits.grad, torch.zeros_like(logits.grad))


def test_no_matches_return_complete_detached_zero_statistics() -> None:
    logits = torch.empty((6, 0, 4, 33), requires_grad=True)
    indices, right, left = _targets(matches=0)
    result = bpdd_distribution_loss(
        logits, indices, right, left, options=_acr_options()
    )
    result.loss.backward()

    assert set(result.statistics) == EXPECTED_STATISTICS
    for name in ("denominator", "reliability_mass", "normalization_gain"):
        value = result.statistics[name]
        assert value.item() == pytest.approx(0.0)
        assert not value.requires_grad
    assert logits.grad is not None
    assert torch.isfinite(logits.grad).all()


def test_acr_promotes_fp16_and_produces_finite_gradients() -> None:
    logits = _binary_logits(0.2, 0.3, dtype=torch.float16).requires_grad_()
    indices, right, left = _targets()
    result = bpdd_distribution_loss(
        logits, indices, right, left, options=_acr_options()
    )
    result.loss.backward()

    assert result.loss.dtype == torch.float32
    assert torch.isfinite(result.loss)
    assert logits.grad is not None
    assert logits.grad.dtype == torch.float16
    assert torch.isfinite(logits.grad).all()


def test_denominator_is_detached_from_reliability_gradient() -> None:
    logits = _binary_logits(0.25, 0.75).requires_grad_()
    indices, right, left = _targets()
    options = _acr_options(weight=0.5)
    result = bpdd_distribution_loss(
        logits, indices, right, left, options=options
    )
    actual_gradient = torch.autograd.grad(result.loss, logits)[0]

    manual_logits = logits.detach().clone().requires_grad_()
    log_probabilities = torch.log_softmax(manual_logits.float(), dim=-1)
    teacher = log_probabilities[1].exp().detach()
    student_error = -log_probabilities[0, ..., 0]
    teacher_error = -teacher[..., 0].log()
    reliability = (
        (student_error.detach() - teacher_error - options.margin)
        / student_error.detach().clamp_min(options.eps)
    ).clamp(0.0, 1.0)
    divergence = (
        teacher * (teacher.clamp_min(options.eps).log() - log_probabilities[0])
    ).sum(dim=-1)
    eligible_edges = reliability.numel()
    reliability_mass = reliability.detach().sum()
    floor = reliability_mass.new_tensor(options.reliability_floor * eligible_edges)
    detached_denominator = torch.maximum(reliability_mass, floor).detach()
    manual_loss = (
        options.weight * (reliability.detach() * divergence).sum() / detached_denominator
    )
    expected_gradient = torch.autograd.grad(manual_loss, manual_logits)[0]

    torch.testing.assert_close(actual_gradient, expected_gradient)
    for name in ("denominator", "reliability_mass", "normalization_gain"):
        assert not result.statistics[name].requires_grad

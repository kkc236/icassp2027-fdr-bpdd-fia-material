from __future__ import annotations

import pytest
import torch
from torch import nn

from src.acr_bpdd_replay import ACRBPDDDetachedHeadReplay


def _heads(*, input_dim: int = 4, output_dim: int = 132) -> nn.ModuleList:
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(71_031)
        return nn.ModuleList(
            [nn.Linear(input_dim, output_dim) for _ in range(6)]
        )


def _inputs(*, input_dim: int = 4) -> list[torch.Tensor]:
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(81_031)
        return [
            torch.randn(2, 3, input_dim, requires_grad=True)
            for _ in range(6)
        ]


def _forward_all(
    heads: nn.ModuleList,
    inputs: list[torch.Tensor],
) -> torch.Tensor:
    return torch.stack(
        [head(value) for head, value in zip(heads, inputs, strict=True)]
    )


def _fdr_cumulative(deltas: torch.Tensor) -> torch.Tensor:
    cumulative: list[torch.Tensor] = []
    running: torch.Tensor | int = 0
    for delta in deltas:
        running = delta + running
        cumulative.append(running)
    return torch.stack(cumulative)


def test_replay_cumulative_logits_match_the_original_forward() -> None:
    heads = _heads()
    inputs = _inputs()
    replay = ACRBPDDDetachedHeadReplay(heads)

    assert replay.begin_capture() is True
    original_deltas = _forward_all(heads, inputs)
    original_cumulative = _fdr_cumulative(original_deltas)

    replayed = replay.replay(cumulative=True)

    assert replayed.shape == (6, 2, 3, 132)
    torch.testing.assert_close(replayed, original_cumulative, rtol=1e-6, atol=1e-7)
    assert replay.capture_enabled is False
    assert replay.cached_layer_count == 0


def test_replay_gradients_reach_heads_but_not_captured_decoder_inputs() -> None:
    heads = _heads()
    inputs = _inputs()
    replay = ACRBPDDDetachedHeadReplay(heads)

    replay.begin_capture()
    original_deltas = _forward_all(heads, inputs)
    replayed = replay.replay()
    replayed.square().mean().backward()

    for value in inputs:
        assert value.grad is None
    for head in heads:
        assert head.weight.grad is not None
        assert torch.count_nonzero(head.weight.grad) > 0
    assert original_deltas.grad_fn is not None


def test_six_layers_use_true_cumulative_residuals() -> None:
    heads = _heads(input_dim=1, output_dim=132)
    for index, head in enumerate(heads, start=1):
        with torch.no_grad():
            head.weight.zero_()
            head.bias.fill_(float(index))
    inputs = [torch.ones(1, 2, 1, requires_grad=True) for _ in range(6)]
    replay = ACRBPDDDetachedHeadReplay(heads)

    replay.begin_capture()
    raw = _forward_all(heads, inputs)
    cumulative = replay.replay(cumulative=True)

    expected = torch.tensor([1, 3, 6, 10, 15, 21], dtype=cumulative.dtype)
    expected = expected[:, None, None, None].expand_as(cumulative)
    torch.testing.assert_close(cumulative, expected, rtol=0, atol=0)
    torch.testing.assert_close(raw[:, 0, 0, 0], torch.arange(1, 7, dtype=raw.dtype))


def test_replay_does_not_recursively_overwrite_captured_inputs() -> None:
    heads = _heads()
    inputs = _inputs()
    replay = ACRBPDDDetachedHeadReplay(heads)

    replay.begin_capture()
    _forward_all(heads, inputs)
    captured_ids = replay.cached_input_ids
    replayed = replay.replay()

    assert replayed.shape[0] == 6
    assert len(captured_ids) == 6
    assert replay.cached_layer_count == 0
    assert replay.cached_input_ids == ()


def test_repeated_capture_lifecycles_do_not_mix_batches() -> None:
    heads = _heads()
    replay = ACRBPDDDetachedHeadReplay(heads)
    first_inputs = _inputs()
    second_inputs = [value.detach().clone().mul_(2).requires_grad_() for value in first_inputs]

    replay.begin_capture()
    first_expected = _fdr_cumulative(_forward_all(heads, first_inputs))
    first_actual = replay.replay()

    replay.begin_capture()
    second_expected = _fdr_cumulative(_forward_all(heads, second_inputs))
    second_actual = replay.replay()

    torch.testing.assert_close(first_actual, first_expected)
    torch.testing.assert_close(second_actual, second_expected)
    assert not torch.equal(first_actual, second_actual)


def test_disabled_and_eval_forwards_leave_no_cache() -> None:
    heads = _heads()
    inputs = _inputs()
    replay = ACRBPDDDetachedHeadReplay(heads)

    _forward_all(heads, inputs)
    assert replay.cached_layer_count == 0

    heads.eval()
    assert replay.begin_capture() is False
    _forward_all(heads, inputs)
    assert replay.capture_enabled is False
    assert replay.cached_layer_count == 0


def test_identity_layer_count_and_parameter_source_changes_are_rejected() -> None:
    with pytest.raises(ValueError, match="exactly six"):
        ACRBPDDDetachedHeadReplay(nn.ModuleList(list(_heads())[:5]))

    duplicate = nn.Linear(4, 132)
    with pytest.raises(ValueError, match="duplicate"):
        ACRBPDDDetachedHeadReplay(nn.ModuleList([duplicate] * 6))

    heads = _heads()
    replay = ACRBPDDDetachedHeadReplay(heads)
    heads[0] = nn.Linear(4, 132)
    with pytest.raises(RuntimeError, match="head identity changed"):
        replay.begin_capture()
    assert replay.cached_layer_count == 0
    assert replay.capture_enabled is False


def test_shape_and_nonfinite_capture_errors_clear_the_lifecycle() -> None:
    heads = _heads()
    inputs = _inputs()
    replay = ACRBPDDDetachedHeadReplay(heads)

    replay.begin_capture()
    heads[0](inputs[0])
    with pytest.raises(ValueError, match="shape"):
        heads[1](torch.randn(1, 3, 4))
    assert replay.capture_enabled is False
    assert replay.cached_layer_count == 0

    replay.begin_capture()
    with pytest.raises(FloatingPointError, match="non-finite"):
        heads[0](torch.full((2, 3, 4), float("nan")))
    assert replay.capture_enabled is False
    assert replay.cached_layer_count == 0


def test_incomplete_replay_clears_cache_and_hook_removal_is_idempotent() -> None:
    heads = _heads()
    inputs = _inputs()
    replay = ACRBPDDDetachedHeadReplay(heads)

    replay.begin_capture()
    for index in range(5):
        heads[index](inputs[index])
    with pytest.raises(RuntimeError, match="six captured layers"):
        replay.replay()
    assert replay.capture_enabled is False
    assert replay.cached_layer_count == 0

    replay.remove()
    replay.remove()
    _forward_all(heads, inputs)
    assert replay.cached_layer_count == 0
    with pytest.raises(RuntimeError, match="removed"):
        replay.begin_capture()

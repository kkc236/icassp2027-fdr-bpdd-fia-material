"""Independent arithmetic checks for the paper's stated formulation.

Standard library only. This executes no model, loss implementation, training,
dataset evaluation, inference, or autograd. Rational examples check the ideal
LRS identities; IEEE binary32 examples check the written evaluation order.
"""

from __future__ import annotations

import ast
from fractions import Fraction as Q
import hashlib
from itertools import product
import json
from pathlib import Path
import struct


ROOT = Path(__file__).resolve().parents[1]


def binary32(value: float) -> float:
    """Round a scalar to IEEE 754 binary32, then return its exact Python value."""
    return struct.unpack("!f", struct.pack("!f", value))[0]


def group_operator(values: tuple[Q, ...], alpha: Q) -> tuple[Q, ...]:
    """Apply ((1-alpha) I + alpha/n 11^T) by exact matrix multiplication."""
    n = len(values)
    if n < 2:
        return values
    return tuple(
        sum(((1 - alpha) * int(i == j) + alpha / n) * values[j] for j in range(n))
        for i in range(n)
    )


def scoped_operator(values, image_ids, eligible, alpha):
    result = list(values)
    for image_id in set(image_ids):
        indices = [i for i, ident in enumerate(image_ids) if ident == image_id and eligible[i]]
        transformed = group_operator(tuple(values[i] for i in indices), alpha)
        for i, value in zip(indices, transformed):
            result[i] = value
    return tuple(result)


def fraction_values(values):
    return [str(value) for value in values]


def main() -> None:
    checks = []

    def record(name, condition, details):
        if not condition:
            raise AssertionError(name)
        checks.append({"name": name, "passed": True, "details": details})

    raw, floor = binary32(-1), binary32(0.00025)
    unparenthesized = binary32(binary32(floor + raw) - raw)
    parenthesized = binary32(floor + binary32(raw - raw))
    record(
        "binary32_evaluation_order_counterexample",
        unparenthesized < floor and parenthesized == floor,
        {"raw_extent": raw, "floor": floor,
         "left_associated_expression": unparenthesized,
         "parenthesized_implemented_expression": parenthesized,
         "interpretation": "An algebraically equivalent left-associated expression can fall below the stated forward floor."},
    )

    math_path = ROOT / "inputs" / "frozen_fdr_math.py"
    loss_path = ROOT / "inputs" / "frozen_fdr_loss.py"
    tree = ast.parse(math_path.read_text(encoding="utf-8"))
    decoder = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "decode_feasible_fdr_boxes")
    extent_assignment = next(
        n for n in ast.walk(decoder)
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "extent" for t in n.targets)
    )
    expected = ast.parse("bounded.detach() + (raw_extent - raw_extent.detach())", mode="eval").body
    record(
        "frozen_source_preserves_parenthesized_zero_term",
        ast.dump(extent_assignment.value, include_attributes=False) == ast.dump(expected, include_attributes=False),
        {"source": "inputs/frozen_fdr_math.py", "function": decoder.name,
         "line": extent_assignment.lineno, "expression": ast.unparse(extent_assignment.value),
         "scope": "AST inspection only; production code is not executed."},
    )

    # Exhaustive small rational groups: the check uses a matrix operator and
    # tests invariants, rather than replaying production loops or FP32 repairs.
    grid = tuple(Q(i, 4) for i in range(5))
    group_cases = 0
    for n in (2, 3, 4):
        for values in product(grid, repeat=n):
            mean = sum(values) / n
            old_variance = sum((value - mean) ** 2 for value in values) / n
            for layer in range(6):
                alpha = Q(1, 4) * (1 - Q(layer, 5))
                result = group_operator(values, alpha)
                assert sum(result) == sum(values)
                assert all(min(values) <= value <= max(values) for value in result)
                assert all(value >= alpha * mean for value in result)
                assert all(result[i] - result[j] == (1 - alpha) * (values[i] - values[j]) for i in range(n) for j in range(n))
                variance = sum((value - mean) ** 2 for value in result) / n
                assert variance == (1 - alpha) ** 2 * old_variance
                if layer == 5:
                    assert result == values
                group_cases += 1
    record(
        "exact_lrs_group_identities",
        group_cases == 4650,
        {"rational_group_cases": group_cases, "group_sizes": [2, 3, 4],
         "input_grid": fraction_values(grid), "layers": list(range(6)),
         "properties": ["total weight conservation", "pairwise difference contraction and ordering preservation", "convex-hull bounds", "lower bound alpha times group mean", "variance factor (1-alpha)^2", "unchanged final layer"],
         "arithmetic": "Exact rational arithmetic; does not assert bitwise identities after production FP32 residual corrections."},
    )

    example = (Q(0), Q(1, 4), Q(3, 4))
    expected_example = (Q(1, 12), Q(13, 48), Q(31, 48))
    result = group_operator(example, Q(1, 4))
    record(
        "nonzero_group_supplies_zero_quality_match",
        result == expected_example and result[0] > 0,
        {"input": fraction_values(example), "alpha": "1/4", "output": fraction_values(result), "total_before_and_after": "1"},
    )
    record(
        "all_zero_group_stays_zero",
        all(group_operator((Q(0), Q(0), Q(0)), Q(1, 4) * (1 - Q(layer, 5))) == (Q(0), Q(0), Q(0)) for layer in range(6)),
        {"interpretation": "LRS redistributes existing quality weight; it does not create weight in an all-zero group."},
    )
    record(
        "singleton_and_empty_groups_stay_unchanged",
        group_operator((Q(3, 8),), Q(1, 4)) == (Q(3, 8),) and group_operator((), Q(1, 4)) == (),
        {"singleton": "3/8", "alpha": "1/4"},
    )

    values = (Q(0), Q(1, 2), Q(1), Q(1, 4), Q(3, 4))
    image_ids = (0, 0, 0, 1, 1)
    eligible = (True, True, False, True, True)
    result = scoped_operator(values, image_ids, eligible, Q(1, 4))
    expected_result = (Q(1, 16), Q(7, 16), Q(1), Q(5, 16), Q(11, 16))
    modified_ineligible = (Q(0), Q(1, 2), Q(0), Q(1, 4), Q(3, 4))
    modified_result = scoped_operator(modified_ineligible, image_ids, eligible, Q(1, 4))
    record(
        "image_scope_and_ineligible_exclusion",
        result == expected_result
        and result[2] == values[2]
        and result[:2] == modified_result[:2]
        and result[3:] == modified_result[3:]
        and sum(result[:3]) == sum(values[:3])
        and sum(result[3:]) == sum(values[3:]),
        {"input": fraction_values(values), "image_ids": image_ids, "eligible": eligible,
         "output": fraction_values(result), "interpretation": "Only eligible objects of the same image are pooled; changing an ineligible quality leaves eligible outputs unchanged."},
    )
    changed_second_image = (Q(0), Q(1, 2), Q(1), Q(0), Q(0))
    isolated = scoped_operator(changed_second_image, image_ids, eligible, Q(1, 4))
    record(
        "unrelated_image_cannot_change_first_image",
        isolated[:3] == result[:3],
        {"interpretation": "Separate image groups cannot exchange their supervision budget."},
    )

    manifest = {
        "status": "passed",
        "scope": "Formula arithmetic and source-expression consistency only. No neural model, dataset prediction, training, autograd, or accuracy evaluation was run.",
        "limitations": [
            "Finite rational examples supplement the stated algebraic identities; they are not a general proof by enumeration.",
            "Ideal LRS identities do not imply a measured improvement in AP, gradient variance, convergence, or reliability calibration.",
            "The AST check verifies expression structure, not execution of the PyTorch decoder or its gradients.",
            "The existing archived geometric regressions remain distinct evidence; no new detector experiment is claimed."
        ],
        "dependencies": "Python standard library only",
        "checked_sources": [
            {"path": str(path.relative_to(ROOT)).replace("\\", "/"),
             "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            for path in (math_path, loss_path)
        ],
        "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "check_count": len(checks),
        "checks": checks,
    }
    destination = ROOT / "reviews" / "formulation_checks.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed", "check_count": len(checks), "rational_group_cases": group_cases, "output": str(destination)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

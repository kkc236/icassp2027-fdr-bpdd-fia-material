"""Build publication records from a completed D-FINE matched post-run status."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


METRIC_NAMES = (
    "AP",
    "AP50",
    "AP75",
    "APs",
    "APm",
    "APl",
    "AR1",
    "AR10",
    "AR100",
    "ARs",
    "ARm",
    "ARl",
)

SOURCE_IDS = {
    "treatment": "dfine_s_equal_fia_24c9cb1_seed0_formal132_best_val_test",
    "control": "dfine_s_official7fe2_seed0_formal132_best_val_test",
    "pair": "dfine_s_equal_fia_vs_official7fe2_matched_pair",
}

EXPECTED_ORDER = (
    ("treatment", "val"),
    ("treatment", "test"),
    ("control", "val"),
    ("control", "test"),
)
EXPECTED_PROTOCOL_ID = "dfine-s-vs-dfine-s-equal-fia-visdrone-seed0-20260823"
EXPECTED_SOURCE_COMMITS = {
    "control": "7fe2f8889f0b7b817f20c315b40fc15a4fb64ae6",
    "treatment": "24c9cb1fba1357b5930f483a26f9e2d787a4e7ef",
}
EXPECTED_ATTRIBUTION_BOUNDARY = {
    "claim_unit": "EQuAL+FIA bundle on D-FINE-S",
    "isolated_equal_gain_claim_allowed": False,
    "isolated_fia_gain_claim_allowed": False,
    "component_attribution_requires_dedicated_ablation": True,
    "reason": (
        "The treatment arm changes EQuAL and FIA together; its control delta "
        "can support only a bundle-level claim until dedicated component "
        "ablations are completed."
    ),
}
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROTOCOL_PATH = (
    ROOT
    / "paper_material"
    / "evidence"
    / "dfine_s_equal_fia_matched_20260823"
    / "protocol.json"
)


class MatchedResultError(ValueError):
    """Raised when source evidence is incomplete or internally inconsistent."""


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise MatchedResultError(f"{label} must be an object")
    return value


def _validate_protocol(protocol: Mapping[str, Any]) -> None:
    if protocol.get("protocol_id") != EXPECTED_PROTOCOL_ID:
        raise MatchedResultError(
            f"protocol_id must be the frozen {EXPECTED_PROTOCOL_ID} contract"
        )
    comparison = _require_mapping(
        protocol.get("comparison_contract"), "comparison_contract"
    )
    if comparison.get("strict_paired") is not False:
        raise MatchedResultError("frozen protocol must declare strict_paired=false")
    arms = _require_mapping(protocol.get("arms"), "arms")
    for method, expected_commit in EXPECTED_SOURCE_COMMITS.items():
        arm = _require_mapping(arms.get(method), f"arms.{method}")
        if arm.get("source_commit") != expected_commit:
            raise MatchedResultError(
                f"{method} source commit must match the frozen protocol"
            )
    boundary = _require_mapping(
        protocol.get("bundle_attribution_boundary"),
        "bundle_attribution_boundary",
    )
    if dict(boundary) != EXPECTED_ATTRIBUTION_BOUNDARY:
        raise MatchedResultError(
            "bundle attribution boundary must match the frozen protocol"
        )


def _metric_availability() -> dict[str, dict[str, Any]]:
    return {
        name: {"value": None, "status": "not_reported_by_coco_evaluator"}
        for name in ("precision", "recall", "f1")
    }


def _validated_evaluations(
    postrun_status: Mapping[str, Any],
) -> list[Mapping[str, Any]]:
    if postrun_status.get("format") != "dfine.post_training_evaluations":
        raise MatchedResultError(
            "postrun format must be dfine.post_training_evaluations"
        )
    if postrun_status.get("version") != 1:
        raise MatchedResultError("postrun version must be 1")
    if postrun_status.get("status") != "complete":
        raise MatchedResultError("postrun status must have status=complete")
    evaluations = postrun_status.get("evaluations")
    if not isinstance(evaluations, list):
        raise MatchedResultError("evaluations must be a list in fixed evaluation order")
    try:
        order = tuple((item.get("method"), item.get("split")) for item in evaluations)
    except AttributeError as error:
        raise MatchedResultError("each evaluation must be an object") from error
    if order != EXPECTED_ORDER:
        raise MatchedResultError(
            "fixed evaluation order must be treatment val, treatment test, "
            "control val, control test"
        )

    runs = _require_mapping(postrun_status.get("runs"), "runs")
    checkpoints: dict[str, str] = {}
    for method in ("treatment", "control"):
        run = _require_mapping(runs.get(method), f"runs.{method}")
        best = _require_mapping(run.get("best"), f"runs.{method}.best")
        checkpoint = best.get("checkpoint_path")
        checkpoint_sha256 = best.get("checkpoint_sha256")
        if not isinstance(checkpoint, str) or not checkpoint:
            raise MatchedResultError(
                f"runs.{method}.best checkpoint_path must be a non-empty string"
            )
        if (
            not isinstance(checkpoint_sha256, str)
            or SHA256_PATTERN.fullmatch(checkpoint_sha256) is None
        ):
            raise MatchedResultError(
                f"runs.{method}.best checkpoint SHA-256 must be 64 lowercase hex characters"
            )
        checkpoints[method] = checkpoint

    for item in evaluations:
        method = item["method"]
        split = item["split"]
        if isinstance(item.get("returncode"), bool) or item.get("returncode") != 0:
            raise MatchedResultError(
                f"{method} {split} must have returncode=0"
            )
        if item.get("ema_restored") is not True:
            raise MatchedResultError(
                f"{method} {split} must have ema_restored=true"
            )
        if item.get("checkpoint") != checkpoints[method]:
            raise MatchedResultError(
                f"{method} val/test must use the same checkpoint as runs.{method}.best"
            )
        optional_sha = item.get("checkpoint_sha256")
        expected_sha = runs[method]["best"]["checkpoint_sha256"]
        if optional_sha is not None and optional_sha != expected_sha:
            raise MatchedResultError(
                f"{method} {split} checkpoint SHA-256 disagrees with runs.{method}.best"
            )
        metrics = _require_mapping(item.get("metrics"), f"{method} {split} metrics")
        stats = metrics.get("coco_eval_bbox")
        if not isinstance(stats, list) or len(stats) != len(METRIC_NAMES):
            raise MatchedResultError(
                f"{method} {split} must contain exactly 12 COCO stats"
            )
        if any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            for value in stats
        ):
            raise MatchedResultError(
                f"{method} {split} COCO stats must be finite numeric values"
            )
    return evaluations


def _metric_map(stats: Sequence[float]) -> dict[str, float]:
    return dict(zip(METRIC_NAMES, stats, strict=True))


def _row(
    *,
    row_id: str,
    split: str,
    role: str,
    method: str,
    metrics: Mapping[str, float],
    delta_pp: Mapping[str, float] | None,
) -> dict[str, Any]:
    return {
        "id": row_id,
        "split": split,
        "role": role,
        "method": method,
        "source_id": SOURCE_IDS[role],
        "precision": None,
        "recall": None,
        "f1": None,
        "precision_recall_f1_status": "not_reported_by_coco_evaluator",
        "metrics": dict(metrics),
        "delta_pp": None if delta_pp is None else dict(delta_pp),
    }


def _render_markdown(rows: Sequence[Mapping[str, Any]]) -> str:
    lines = [
        "# D-FINE-S + EQuAL + FIA 协议匹配结果",
        "",
        "P/R/F1 未由本次 COCO evaluator 报告，保持为空且不作反推。",
        "",
    ]
    by_split = {
        split: [row for row in rows if row["split"] == split]
        for split in ("val", "test")
    }
    for split in ("val", "test"):
        lines.extend(
            [
                f"## VisDrone {split}",
                "",
                "| 编号 | 方法 | AP | AP50 | AP75 | APs | APm | APl | ΔAP (pp) |",
                "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in by_split[split]:
            metrics = row["metrics"]
            delta = row["delta_pp"]
            delta_ap = "—" if delta is None else f"{delta['AP']:+.6f}"
            lines.append(
                "| {id} | {method} | {AP:.6f} | {AP50:.6f} | {AP75:.6f} | "
                "{APs:.6f} | {APm:.6f} | {APl:.6f} | {delta_ap} |".format(
                    id=row["id"], method=row["method"], delta_ap=delta_ap, **metrics
                )
            )
        lines.append("")
    lines.extend(
        [
            "`strict_paired=false`：两臂协议匹配，但来自不同 source commit。",
            "差值仅支持 EQuAL+FIA bundle 级归因，不支持拆分为单组件贡献。",
            "",
        ]
    )
    return "\n".join(lines)


def build_matched_results(
    postrun_status: Mapping[str, Any], protocol: Mapping[str, Any]
) -> dict[str, Any]:
    """Return pure pair-summary, paper-result, and Chinese Markdown values."""

    _validate_protocol(protocol)
    validated = _validated_evaluations(postrun_status)
    evaluations = {(item["method"], item["split"]): item for item in validated}
    metric_sets = {
        key: _metric_map(item["metrics"]["coco_eval_bbox"])
        for key, item in evaluations.items()
    }
    comparisons: dict[str, dict[str, Any]] = {}
    rows: list[dict[str, Any]] = []
    for split in ("val", "test"):
        treatment = metric_sets[("treatment", split)]
        control = metric_sets[("control", split)]
        delta_pp = {
            name: (treatment[name] - control[name]) * 100 for name in METRIC_NAMES
        }
        comparisons[split] = {
            "treatment_source_id": SOURCE_IDS["treatment"],
            "control_source_id": SOURCE_IDS["control"],
            "treatment_metrics": dict(treatment),
            "control_metrics": dict(control),
            "delta_pp": delta_pp,
        }
        rows.extend(
            [
                _row(
                    row_id="DF-0",
                    split=split,
                    role="control",
                    method=protocol["arms"]["control"]["method"],
                    metrics=control,
                    delta_pp=None,
                ),
                _row(
                    row_id="DF-1",
                    split=split,
                    role="treatment",
                    method=protocol["arms"]["treatment"]["method"],
                    metrics=treatment,
                    delta_pp=delta_pp,
                ),
            ]
        )

    runs = postrun_status["runs"]
    arms = {
        method: {
            "source_id": SOURCE_IDS[method],
            "method": protocol["arms"][method]["method"],
            "source_commit": protocol["arms"][method]["source_commit"],
            "checkpoint": {
                "path": runs[method]["best"]["checkpoint_path"],
                "sha256": runs[method]["best"]["checkpoint_sha256"],
            },
            "results": {
                split: dict(metric_sets[(method, split)])
                for split in ("val", "test")
            },
        }
        for method in ("treatment", "control")
    }
    pair_summary = {
        "format": "dfine.equal_fia.matched_pair_summary",
        "version": 1,
        "status": "complete",
        "protocol_id": protocol["protocol_id"],
        "source_id": SOURCE_IDS["pair"],
        "source_ids": dict(SOURCE_IDS),
        "strict_paired": False,
        "bundle_attribution_boundary": dict(protocol["bundle_attribution_boundary"]),
        "metric_availability": _metric_availability(),
        "arms": arms,
        "comparisons": comparisons,
    }
    paper_results = {
        "format": "dfine.equal_fia.matched_paper_results",
        "version": 1,
        "protocol_id": protocol["protocol_id"],
        "source_id": SOURCE_IDS["pair"],
        "strict_paired": False,
        "bundle_attribution_boundary": dict(protocol["bundle_attribution_boundary"]),
        "metric_availability": _metric_availability(),
        "rows": rows,
    }
    return {
        "pair_summary": pair_summary,
        "paper_results": paper_results,
        "markdown": _render_markdown(rows),
    }


def _write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    try:
        temporary.write_text(text, encoding="utf-8", newline="\n")
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def write_matched_results(
    documents: Mapping[str, Any], output_root: str | Path
) -> dict[str, str]:
    """Atomically write a generated bundle into a new or empty root only."""

    output_root = Path(output_root).resolve()
    if output_root.exists():
        if not output_root.is_dir() or any(output_root.iterdir()):
            raise MatchedResultError(
                f"output root must be new or empty; refusing to overwrite: {output_root}"
            )
    else:
        output_root.mkdir(parents=True)

    paths = {
        "pair_summary": output_root / "pair_summary.json",
        "paper_results": (
            output_root
            / "paper_material"
            / "results"
            / "dfine_equal_fia_matched_results.json"
        ),
        "markdown": (
            output_root
            / "paper_material"
            / "results"
            / "DFINE_EQUAL_FIA_MATCHED_RESULTS_ZH.md"
        ),
    }
    for key in ("pair_summary", "paper_results"):
        try:
            serialized = json.dumps(
                documents[key],
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
                allow_nan=False,
            )
        except (KeyError, TypeError, ValueError) as error:
            raise MatchedResultError(f"cannot serialize {key}: {error}") from error
        _write_text_atomic(paths[key], serialized + "\n")
    markdown = documents.get("markdown")
    if not isinstance(markdown, str):
        raise MatchedResultError("markdown document must be a string")
    _write_text_atomic(
        paths["markdown"], markdown if markdown.endswith("\n") else markdown + "\n"
    )
    return {key: str(path) for key, path in paths.items()}


def _read_json_object(path: Path, label: str) -> Mapping[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise MatchedResultError(f"cannot read {label} JSON {path}: {error}") from error
    return _require_mapping(value, label)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--postrun-status", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL_PATH)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args(argv)

    try:
        status = _read_json_object(args.postrun_status, "postrun_status")
        protocol = _read_json_object(args.protocol, "protocol")
        documents = build_matched_results(status, protocol)
        files = write_matched_results(documents, args.output_root)
    except MatchedResultError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    print(
        json.dumps(
            {"status": "written", "files": files},
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

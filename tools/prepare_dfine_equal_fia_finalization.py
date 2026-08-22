"""Verify pulled D-FINE evidence and prepare a non-destructive finalization bundle.

This tool never contacts a server, runs an evaluation, edits the material tree, or
uploads to GitHub.  It reuses ``generate_dfine_equal_fia_matched_results`` for
the result calculation and adds local byte-level evidence verification plus
deterministic integration artifacts.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.generate_dfine_equal_fia_matched_results import (  # noqa: E402
    EXPECTED_ORDER,
    MatchedResultError,
    SOURCE_IDS,
    build_matched_results,
)


EVIDENCE_TARGET = (
    "paper_material/evidence/dfine_s_equal_fia_matched_20260823"
)
PAIR_SUMMARY_TARGET = f"{EVIDENCE_TARGET}/pair_summary.json"
RESULT_JSON_TARGET = (
    "paper_material/results/dfine_equal_fia_matched_results.json"
)
RESULT_MD_TARGET = (
    "paper_material/results/DFINE_EQUAL_FIA_MATCHED_RESULTS_ZH.md"
)
SHA256_RE = re.compile(r"[0-9a-f]{64}")
EXPECTED_CONFIGS = {
    ("treatment", "val"): "dfine_hgnetv2_s_visdrone_equal_fia.yml",
    ("treatment", "test"): "dfine_hgnetv2_s_visdrone_equal_fia_test.yml",
    ("control", "val"): "dfine_hgnetv2_s_visdrone.yml",
    ("control", "test"): "dfine_hgnetv2_s_visdrone_test.yml",
}
EXPECTED_DATASET_PROTOCOL = {
    "name": "VisDrone2019-DET",
    "train": {
        "images": 6471,
        "instances": 343204,
        "annotation_sha256": "e21b7109def110cec00c74d9fa95db590995b93e2633cb31abf3bc0b45b5c65c",
    },
    "val": {
        "images": 548,
        "instances": 38759,
        "annotation_sha256": "200d58fffda1ab131548ba1a978b2f59be410d6a95b5adadc4075912cdcca477",
    },
    "test": {
        "images": 1610,
        "instances": 75102,
        "annotation_sha256": "b699bf1b9e1e366fef481bb561b8c79b1dc2e1da81be437b598b0dd6d0fa3fd7",
        "authority": "local_held_out",
        "official_challenge_server": False,
    },
}
EXPECTED_TRAINING_PROTOCOL = {
    "seed": 0,
    "epochs": 132,
    "image_size": 640,
    "total_batch_size": 8,
    "effective_train_workers": 4,
    "effective_val_workers": 4,
    "amp": True,
    "ema": True,
    "pretrained_backbone_sha256": (
        "70a372e8cbc59b34c5da2943261ecb633faf304a58e7e05461a27bd8d8b7f3d1"
    ),
}
EXPECTED_EVALUATION_PROTOCOL = {
    "evaluator": "pycocotools.COCOeval",
    "iou_type": "bbox",
    "max_dets": [1, 10, 100],
    "primary_max_dets": 100,
    "best_checkpoint_selection_split": "val",
    "best_checkpoint_selection_metric": "COCO_AP50_95",
    "test_used_for_model_selection": False,
    "same_evaluator_for_both_arms": True,
}
EXPECTED_METRIC_BOUNDARY = {
    "primary_metrics": ["COCO_AP50_95", "COCO_AP50", "COCO_AP75"],
    "precision_recall_f1_status": "not_emitted_by_this_coco_protocol",
    "cross_evaluator_metric_mixing_allowed": False,
}


class FinalizationError(ValueError):
    """Raised when final evidence is missing, inconsistent, or unsafe to stage."""


def _json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path, label: str) -> Mapping[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise FinalizationError(f"cannot read {label} JSON {path}: {error}") from error
    if not isinstance(value, Mapping):
        raise FinalizationError(f"{label} must be a JSON object")
    return value


def _remote_name(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise FinalizationError(f"{label} must be a non-empty path")
    name = PurePosixPath(value.replace("\\", "/")).name
    if not name or name in {".", ".."}:
        raise FinalizationError(f"{label} has no safe basename")
    return name


def _require_sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise FinalizationError(f"{label} must be 64 lowercase hexadecimal characters")
    return value


def _verify_file(path: Path, record: Mapping[str, Any], label: str) -> dict[str, Any]:
    if not path.is_file():
        raise FinalizationError(f"missing local {label}: {path}")
    expected_bytes = record.get("bytes")
    if (
        isinstance(expected_bytes, bool)
        or not isinstance(expected_bytes, int)
        or expected_bytes <= 0
    ):
        raise FinalizationError(f"{label} bytes must be a positive integer")
    actual_bytes = path.stat().st_size
    if actual_bytes != expected_bytes:
        raise FinalizationError(
            f"{label} byte count mismatch: expected {expected_bytes}, found {actual_bytes}"
        )
    expected_sha = _require_sha(record.get("sha256"), f"{label} sha256")
    actual_sha = _sha256_file(path)
    if actual_sha != expected_sha:
        raise FinalizationError(
            f"{label} SHA-256 mismatch: expected {expected_sha}, found {actual_sha}"
        )
    return {
        "source_path": path,
        "bytes": actual_bytes,
        "sha256": actual_sha,
    }


def _validate_run_evidence(
    status: Mapping[str, Any], evidence_root: Path
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    runs = status.get("runs")
    if not isinstance(runs, Mapping):
        raise FinalizationError("postrun runs must be an object")
    repository_files: list[dict[str, Any]] = []
    release_assets: list[dict[str, Any]] = []
    for method in ("treatment", "control"):
        run = runs.get(method)
        if not isinstance(run, Mapping):
            raise FinalizationError(f"runs.{method} must be an object")
        if run.get("epoch_count") != 132 or run.get("epoch_range") != [0, 131]:
            raise FinalizationError(f"runs.{method} must prove exactly epochs 0..131")
        best = run.get("best")
        if not isinstance(best, Mapping):
            raise FinalizationError(f"runs.{method}.best must be an object")
        best_epoch = best.get("best_epoch")
        if isinstance(best_epoch, bool) or not isinstance(best_epoch, int):
            raise FinalizationError(f"runs.{method}.best_epoch must be an integer")
        if best.get("checkpoint_last_epoch") != best_epoch:
            raise FinalizationError(
                f"runs.{method} best checkpoint epoch does not match selected epoch"
            )
        expected_stage = "best_stg1" if best_epoch < 120 else "best_stg2"
        if best.get("stage") != expected_stage:
            raise FinalizationError(
                f"runs.{method}.best stage must be {expected_stage} for epoch {best_epoch}"
            )
        if best.get("checkpoint_has_ema") is not True:
            raise FinalizationError(f"runs.{method} best checkpoint must contain EMA")
        stats = best.get("stats")
        if (
            not isinstance(stats, list)
            or len(stats) != 12
            or any(
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                for value in stats
            )
        ):
            raise FinalizationError(f"runs.{method}.best.stats must contain 12 finite COCO stats")
        val_ap = best.get("val_ap")
        if (
            isinstance(val_ap, bool)
            or not isinstance(val_ap, (int, float))
            or not math.isfinite(val_ap)
            or val_ap != stats[0]
        ):
            raise FinalizationError(
                f"runs.{method}.best.val_ap must exactly equal best.stats[0]"
            )

        run_root = evidence_root / "runs" / method
        for filename, hash_key, role in (
            ("log.txt", "log_sha256", f"{method}_training_jsonl"),
            ("train.log", "train_log_sha256", f"{method}_training_log"),
        ):
            path = run_root / filename
            record = {
                "bytes": path.stat().st_size if path.is_file() else 0,
                "sha256": run.get(hash_key),
            }
            verified = _verify_file(path, record, role)
            verified.update(
                {
                    "target_path": f"./runs/{method}/{filename}",
                    "role": role,
                }
            )
            repository_files.append(verified)
            release_assets.append(dict(verified))

        checkpoint_name = _remote_name(
            best.get("checkpoint_path"), f"runs.{method}.best.checkpoint_path"
        )
        checkpoint_parent = str(
            PurePosixPath(str(best.get("checkpoint_path")).replace("\\", "/")).parent
        ).rstrip("/")
        run_directory = str(run.get("run_dir", "")).replace("\\", "/").rstrip("/")
        if checkpoint_parent != run_directory:
            raise FinalizationError(
                f"runs.{method} best checkpoint is not bound to its run directory"
            )
        checkpoint = _verify_file(
            run_root / checkpoint_name,
            {
                "bytes": best.get("checkpoint_bytes"),
                "sha256": best.get("checkpoint_sha256"),
            },
            f"{method} best checkpoint",
        )
        checkpoint.update(
            {
                "role": f"{method}_best_checkpoint",
                "recommended_name": f"{method}-{checkpoint_name}",
            }
        )
        release_assets.append(checkpoint)
    return repository_files, release_assets


def _validate_frozen_protocol(protocol: Mapping[str, Any]) -> None:
    training = protocol.get("shared_training_protocol")
    if not isinstance(training, Mapping) or training.get("seed") != 0:
        raise FinalizationError("frozen training protocol must use seed 0")
    checks = (
        ("dataset protocol", protocol.get("dataset"), EXPECTED_DATASET_PROTOCOL),
        (
            "training protocol",
            protocol.get("shared_training_protocol"),
            EXPECTED_TRAINING_PROTOCOL,
        ),
        (
            "evaluation protocol",
            protocol.get("shared_evaluation_protocol"),
            EXPECTED_EVALUATION_PROTOCOL,
        ),
        (
            "metric boundary",
            protocol.get("metric_boundary"),
            EXPECTED_METRIC_BOUNDARY,
        ),
    )
    for label, actual, expected in checks:
        if actual != expected:
            raise FinalizationError(f"frozen {label} does not match the Formal132 contract")


def _flag_value(command: list[Any], flag: str, label: str) -> Any:
    if command.count(flag) != 1:
        raise FinalizationError(f"{label} command must contain {flag} exactly once")
    index = command.index(flag)
    if index + 1 >= len(command):
        raise FinalizationError(f"{label} command has no value after {flag}")
    return command[index + 1]


def _validate_evaluations(
    status: Mapping[str, Any], evidence_root: Path
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    evaluations = status.get("evaluations")
    if not isinstance(evaluations, list) or len(evaluations) != 4:
        raise FinalizationError("postrun must contain exactly four evaluations")
    repository_files: list[dict[str, Any]] = []
    release_assets: list[dict[str, Any]] = []
    runs = status["runs"]
    for expected, item in zip(EXPECTED_ORDER, evaluations, strict=True):
        if not isinstance(item, Mapping):
            raise FinalizationError("each evaluation must be an object")
        method, split = expected
        label = f"{method} {split}"
        if (item.get("method"), item.get("split")) != expected:
            raise FinalizationError("evaluations are not in the frozen four-job order")
        if item.get("returncode") != 0 or isinstance(item.get("returncode"), bool):
            raise FinalizationError(f"{label} returncode must be zero")
        if item.get("ema_restored") is not True:
            raise FinalizationError(f"{label} must prove EMA restoration")
        checkpoint = runs[method]["best"]["checkpoint_path"]
        if item.get("checkpoint") != checkpoint:
            raise FinalizationError(f"{label} does not use the selected best checkpoint")
        if _remote_name(item.get("config"), f"{label} config") != EXPECTED_CONFIGS[expected]:
            raise FinalizationError(f"{label} does not use the frozen evaluation config")

        command = item.get("command")
        if not isinstance(command, list) or not all(isinstance(value, str) for value in command):
            raise FinalizationError(f"{label} command must be a string list")
        if command.count("--use-amp") != 1 or command.count("--test-only") != 1:
            raise FinalizationError(f"{label} command must preserve AMP and test-only mode")
        if _flag_value(command, "--seed", label) != "0":
            raise FinalizationError(f"{label} command must use seed 0")
        if _flag_value(command, "-r", label) != checkpoint:
            raise FinalizationError(f"{label} command checkpoint disagrees with selected best")
        if _flag_value(command, "-c", label) != item.get("config"):
            raise FinalizationError(f"{label} command config disagrees with status")
        if _flag_value(command, "--output-dir", label) != item.get("output_dir"):
            raise FinalizationError(f"{label} command output directory disagrees with status")

        artifacts = item.get("artifacts")
        if not isinstance(artifacts, Mapping):
            raise FinalizationError(f"{label} artifacts must be an object")
        local_dir = evidence_root / "evaluations" / method / split
        verified_by_key: dict[str, dict[str, Any]] = {}
        for key, filename, role_suffix in (
            ("eval_pth", "eval.pth", "eval_pth"),
            ("evaluation_metrics_json", "evaluation_metrics.json", "evaluation_metrics"),
            ("evaluation_log", "evaluation.log", "evaluation_log"),
        ):
            record = artifacts.get(key)
            if not isinstance(record, Mapping):
                raise FinalizationError(f"{label} is missing {key} metadata")
            remote_artifact = record.get("path")
            if _remote_name(remote_artifact, f"{label} {key} path") != filename:
                raise FinalizationError(f"{label} {key} artifact basename is not canonical")
            artifact_parent = str(
                PurePosixPath(str(remote_artifact).replace("\\", "/")).parent
            ).rstrip("/")
            expected_parent = str(item.get("output_dir", "")).replace("\\", "/").rstrip("/")
            if artifact_parent != expected_parent:
                raise FinalizationError(
                    f"{label} {key} is not bound to its evaluation output directory"
                )
            verified = _verify_file(local_dir / filename, record, f"{label} {key}")
            verified.update(
                {
                    "target_path": f"./evaluations/{method}/{split}/{filename}",
                    "role": f"{method}_{split}_{role_suffix}",
                }
            )
            verified_by_key[key] = verified
            release_assets.append(dict(verified))
            if key != "eval_pth":
                repository_files.append(dict(verified))

        metrics_payload = _load_json(
            verified_by_key["evaluation_metrics_json"]["source_path"],
            f"{label} evaluation metrics",
        )
        if metrics_payload != item.get("metrics"):
            raise FinalizationError(f"{label} local metrics do not exactly match postrun status")
        if (
            metrics_payload.get("format")
            != "dfine.coco_bbox.evaluation_metrics"
            or metrics_payload.get("version") != 1
        ):
            raise FinalizationError(f"{label} metrics use an unsupported evaluator schema")

        log_text = verified_by_key["evaluation_log"]["source_path"].read_text(
            encoding="utf-8", errors="replace"
        )
        if "Load ema.state_dict from model.state_dict" in log_text:
            raise FinalizationError(f"{label} synthesized EMA instead of restoring it")
        if "Load ema.state_dict" not in log_text:
            raise FinalizationError(f"{label} local log does not prove EMA restoration")
    return repository_files, release_assets


def _manifest_text(records: list[dict[str, Any]], generated: Mapping[str, bytes]) -> str:
    entries = [(record["target_path"], record["sha256"]) for record in records]
    entries.extend((path, _sha256_bytes(data)) for path, data in generated.items())
    if len({path for path, _ in entries}) != len(entries):
        raise FinalizationError("manifest contains duplicate target paths")
    return "".join(f"{sha256}  {path}\n" for path, sha256 in sorted(entries))


def _replace_or_insert_section(text: str, marker: str, section: str) -> str:
    start = f"<!-- {marker}_START -->"
    end = f"<!-- {marker}_END -->"
    block = f"{start}\n{section.rstrip()}\n{end}\n"
    if start in text or end in text:
        if text.count(start) != 1 or text.count(end) != 1 or text.index(start) > text.index(end):
            raise FinalizationError(f"document has malformed {marker} markers")
        before, remainder = text.split(start, 1)
        _, after = remainder.split(end, 1)
        return before + block + after.lstrip("\r\n")
    lines = text.splitlines(keepends=True)
    if not lines or not lines[0].startswith("# "):
        raise FinalizationError("material document must start with a level-one heading")
    return lines[0].rstrip("\r\n") + "\n\n" + block + "\n" + "".join(lines[1:]).lstrip("\r\n")


def _documentation_patch(
    material_root: Path, pair_summary: Mapping[str, Any]
) -> str:
    comparisons = pair_summary["comparisons"]
    val = comparisons["val"]
    test = comparisons["test"]
    status_section = "\n".join(
        [
            "## D-FINE-S + EQuAL + FIA 协议匹配结果",
            "",
            "Formal132 处理组与官方 D-FINE-S 控制组已完成统一 best-val 选择和 val/test COCO 复评。",
            f"val：处理组 AP={val['treatment_metrics']['AP']:.6f}，"
            f"控制组 AP={val['control_metrics']['AP']:.6f}，"
            f"ΔAP={val['delta_pp']['AP']:+.6f} pp；",
            f"test：处理组 AP={test['treatment_metrics']['AP']:.6f}，"
            f"控制组 AP={test['control_metrics']['AP']:.6f}，"
            f"ΔAP={test['delta_pp']['AP']:+.6f} pp。",
            "该比较为 `strict_paired=false` 的协议匹配比较；test 是 local "
            "held-out，不参与选模，也不是 challenge-server 结果。",
            "差值只支持 EQuAL+FIA bundle 级归因，旧 A–E/main_results 保持历史状态且不被覆盖。",
        ]
    )
    readme_section = "\n".join(
        [
            "## D-FINE 正式匹配结果",
            "",
            "- [D-FINE-S + EQuAL + FIA val/test 协议匹配结果]"
            "(results/DFINE_EQUAL_FIA_MATCHED_RESULTS_ZH.md)",
            "- [对应机器结果](results/dfine_equal_fia_matched_results.json)",
            "- [最终证据清单](evidence/dfine_s_equal_fia_matched_20260823/MANIFEST.sha256)",
        ]
    )
    targets = (
        ("CURRENT_RERUN_STATUS_ZH.md", status_section),
        ("README_ZH.md", readme_section),
    )
    chunks: list[str] = []
    for name, section in targets:
        path = material_root / name
        try:
            old = path.read_text(encoding="utf-8")
        except OSError as error:
            raise FinalizationError(f"cannot read material document {path}: {error}") from error
        new = _replace_or_insert_section(old, "DFINE_EQUAL_FIA_MATCHED_RESULT", section)
        chunks.extend(
            difflib.unified_diff(
                old.splitlines(keepends=True),
                new.splitlines(keepends=True),
                fromfile=f"a/paper_material/{name}",
                tofile=f"b/paper_material/{name}",
            )
        )
    return "".join(chunks)


def _release_manifest(assets: list[dict[str, Any]]) -> dict[str, Any]:
    normalized = []
    for item in sorted(assets, key=lambda value: value["role"]):
        source = Path(item["source_path"])
        normalized.append(
            {
                "role": item["role"],
                "source_path": source.as_posix(),
                "recommended_name": item.get("recommended_name", f"{item['role']}-{source.name}"),
                "bytes": item["bytes"],
                "sha256": item["sha256"],
            }
        )
    return {
        "format": "dfine.equal_fia.github_release_asset_plan",
        "version": 1,
        "suggested_tag": "dfine-s-equal-fia-formal132-20260823",
        "automatic_upload": False,
        "contains_credentials": False,
        "assets": normalized,
    }


def _source_fragment(
    protocol: Mapping[str, Any], pair_bytes: bytes, result_bytes: bytes
) -> dict[str, Any]:
    evidence = f"{EVIDENCE_TARGET}/pair_summary.json"
    result = RESULT_JSON_TARGET
    return {
        "format": "material.source_manifest_merge_fragment",
        "version": 1,
        "merge_target": "paper_material/evidence/source_manifest.json#/sources",
        "conflict_policy": "require_absent_or_byte_equivalent",
        "sources": {
            SOURCE_IDS["treatment"]: {
                "title": "D-FINE-S + EQuAL + FIA Formal132 best-checkpoint val/test",
                "artifact": evidence,
                "sha256": _sha256_bytes(pair_bytes),
                "source_commit": protocol["arms"]["treatment"]["source_commit"],
                "checkpoint_sha256_path": "#/arms/treatment/checkpoint/sha256",
                "splits_available": ["val", "test"],
                "evidence_level": "matched_protocol_best_val_selected_exact_coco_val_test",
            },
            SOURCE_IDS["control"]: {
                "title": "Official D-FINE-S Formal132 best-checkpoint val/test control",
                "artifact": evidence,
                "sha256": _sha256_bytes(pair_bytes),
                "source_commit": protocol["arms"]["control"]["source_commit"],
                "checkpoint_sha256_path": "#/arms/control/checkpoint/sha256",
                "splits_available": ["val", "test"],
                "evidence_level": "matched_protocol_best_val_selected_exact_coco_val_test",
            },
            SOURCE_IDS["pair"]: {
                "title": "D-FINE-S versus D-FINE-S + EQuAL + FIA matched comparison",
                "artifact": result,
                "sha256": _sha256_bytes(result_bytes),
                "pair_summary": evidence,
                "pair_summary_sha256": _sha256_bytes(pair_bytes),
                "strict_paired": False,
                "splits_available": ["val", "test"],
                "evidence_level": "matched_protocol_non_strict_pair_bundle_attribution_only",
            },
        },
    }


def _validate_source_fragment(
    material_root: Path, fragment: Mapping[str, Any]
) -> None:
    manifest = _load_json(
        material_root / "evidence" / "source_manifest.json", "source manifest"
    )
    existing = manifest.get("sources")
    if not isinstance(existing, Mapping):
        raise FinalizationError("source manifest sources must be an object")
    proposed = fragment.get("sources")
    if not isinstance(proposed, Mapping):
        raise FinalizationError("source manifest fragment sources must be an object")
    for source_id, record in proposed.items():
        if source_id in existing and existing[source_id] != record:
            raise FinalizationError(
                f"source manifest conflict for existing source ID {source_id}"
            )


def _internal_audit_status(pair_summary: Mapping[str, Any]) -> dict[str, Any]:
    delta_by_split = {
        split: pair_summary["comparisons"][split]["delta_pp"]["AP"]
        for split in ("val", "test")
    }
    if all(value > 0 for value in delta_by_split.values()):
        outcome = "positive"
    elif all(value < 0 for value in delta_by_split.values()):
        outcome = "negative"
    else:
        outcome = "mixed_or_zero"
    gain_allowed = outcome == "positive"
    return {
        "format": "dfine.equal_fia.internal_audit_status",
        "version": 1,
        "scope": "internal_only_not_formal_result_authority",
        "outcome_policy": "negative_or_positive_by_completed_matched_eval",
        "completed_matched_eval_outcome": outcome,
        "completed_matched_eval_delta_ap_pp": delta_by_split,
        "claim_gate": {
            "formal_bundle_gain_claim_allowed": gain_allowed,
            "formal_bundle_gain_claim_rule": "requires_positive_AP_delta_on_both_val_and_test",
            "isolated_component_gain_claim_allowed": False,
            "isolated_component_reason": "treatment changes EQuAL and FIA together",
            "negative_or_mixed_outcome_requires_plain_reporting": not gain_allowed,
        },
        "early_training_internal_context": {
            "formal_result_use_allowed": False,
            "observation": "treatment_trailing_control",
            "approximate_delta_pp": -8.1,
            "protocol_pretrain_initialization_evaluator_error_found": False,
            "diagnostic_factors": [
                "native_raw_reference_with_preliminary_supervision_disabled_"
                "yielded_exact_zero_pre_box_head",
                "dn_fgl_disabled_was_followed_by_abnormal_ddf_behavior",
            ],
        },
    }


def prepare_bundle(
    *,
    postrun_status_path: Path,
    evidence_root: Path,
    protocol_path: Path,
    material_root: Path,
) -> dict[str, bytes]:
    """Validate every local authority and return all deterministic output bytes."""

    evidence_root = evidence_root.resolve()
    postrun_status_path = postrun_status_path.resolve()
    try:
        postrun_status_path.relative_to(evidence_root)
    except ValueError as error:
        raise FinalizationError("postrun_status must be inside evidence_root") from error
    status = _load_json(postrun_status_path, "postrun_status")
    protocol = _load_json(protocol_path, "protocol")
    _validate_frozen_protocol(protocol)
    try:
        documents = build_matched_results(status, protocol)
    except MatchedResultError as error:
        raise FinalizationError(str(error)) from error

    run_files, run_assets = _validate_run_evidence(status, evidence_root)
    evaluation_files, evaluation_assets = _validate_evaluations(status, evidence_root)
    pair_bytes = _json_bytes(documents["pair_summary"])
    result_bytes = _json_bytes(documents["paper_results"])
    markdown = documents["markdown"]
    markdown_bytes = (markdown if markdown.endswith("\n") else markdown + "\n").encode("utf-8")
    release = _release_manifest(
        [
            {
                "role": "postrun_status",
                "source_path": postrun_status_path,
                "bytes": postrun_status_path.stat().st_size,
                "sha256": _sha256_file(postrun_status_path),
            },
            *run_assets,
            *evaluation_assets,
        ]
    )
    release_bytes = _json_bytes(release)
    evidence_attributes = b"* -text\n"

    protocol_record = {
        "source_path": protocol_path,
        "target_path": "./protocol.json",
        "bytes": protocol_path.stat().st_size,
        "sha256": _sha256_file(protocol_path),
    }
    status_record = {
        "source_path": postrun_status_path,
        "target_path": "./postrun_status.json",
        "bytes": postrun_status_path.stat().st_size,
        "sha256": _sha256_file(postrun_status_path),
    }
    manifest = _manifest_text(
        [protocol_record, status_record, *run_files, *evaluation_files],
        {
            "./.gitattributes": evidence_attributes,
            "./pair_summary.json": pair_bytes,
        },
    ).encode("utf-8")
    fragment = _source_fragment(protocol, pair_bytes, result_bytes)
    _validate_source_fragment(material_root.resolve(), fragment)
    internal_audit = _internal_audit_status(documents["pair_summary"])
    patch = _documentation_patch(material_root.resolve(), documents["pair_summary"])
    repository_evidence_copies = []
    for record in [status_record, *run_files, *evaluation_files]:
        source_path = Path(record["source_path"]).resolve()
        try:
            source_relative = source_path.relative_to(evidence_root).as_posix()
        except ValueError as error:
            raise FinalizationError(
                f"repository evidence source escapes evidence_root: {source_path}"
            ) from error
        target_relative = str(record["target_path"]).removeprefix("./")
        repository_evidence_copies.append(
            {
                "source": source_relative,
                "target": f"{EVIDENCE_TARGET}/{target_relative}",
                "bytes": record["bytes"],
                "sha256": record["sha256"],
            }
        )
    apply_plan = {
        "format": "dfine.equal_fia.material_apply_plan",
        "version": 1,
        "automatic_apply": False,
        "forbidden_targets": [
            "paper_material/results/main_results.json",
            "paper_material/results/MAIN_TABLE_ZH.md",
            "paper_material/results/RESULTS_ZH.md",
        ],
        "generated_targets": [
            PAIR_SUMMARY_TARGET,
            f"{EVIDENCE_TARGET}/.gitattributes",
            RESULT_JSON_TARGET,
            RESULT_MD_TARGET,
            f"{EVIDENCE_TARGET}/MANIFEST.sha256",
        ],
        "repository_evidence_copies": sorted(
            repository_evidence_copies, key=lambda item: item["target"]
        ),
        "merge_fragment": "integration/source_manifest.fragment.json",
        "documentation_patch": "integration/material_docs.patch",
        "release_asset_plan": "integration/github_release_assets.json",
        "internal_audit_status": "integration/internal_audit_status.json",
        "server_actions": [],
        "github_actions": [],
    }
    return {
        PAIR_SUMMARY_TARGET: pair_bytes,
        f"{EVIDENCE_TARGET}/.gitattributes": evidence_attributes,
        RESULT_JSON_TARGET: result_bytes,
        RESULT_MD_TARGET: markdown_bytes,
        f"{EVIDENCE_TARGET}/MANIFEST.sha256": manifest,
        "integration/source_manifest.fragment.json": _json_bytes(fragment),
        "integration/material_docs.patch": patch.encode("utf-8"),
        "integration/github_release_assets.json": release_bytes,
        "integration/material_apply_plan.json": _json_bytes(apply_plan),
        "integration/internal_audit_status.json": _json_bytes(internal_audit),
    }


def write_bundle(files: Mapping[str, bytes], output_root: Path) -> None:
    """Atomically materialize a prepared bundle into a new or empty directory."""

    output_root = output_root.resolve()
    if output_root.exists() and (not output_root.is_dir() or any(output_root.iterdir())):
        raise FinalizationError(f"output root must be new or empty: {output_root}")
    temporary = output_root.with_name(f".{output_root.name}.tmp")
    if temporary.exists():
        raise FinalizationError(f"temporary output already exists: {temporary}")
    temporary.mkdir(parents=True)
    try:
        for relative, data in sorted(files.items()):
            path = temporary / Path(relative)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        if output_root.exists():
            output_root.rmdir()
        os.replace(temporary, output_root)
    finally:
        if temporary.exists():
            for path in sorted(temporary.rglob("*"), reverse=True):
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    path.rmdir()
            temporary.rmdir()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--postrun-status", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--material-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        files = prepare_bundle(
            postrun_status_path=args.postrun_status,
            evidence_root=args.evidence_root,
            protocol_path=args.protocol,
            material_root=args.material_root,
        )
        write_bundle(files, args.output_root)
    except FinalizationError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "status": "prepared",
                "verified_evaluation_count": 4,
                "output_root": str(args.output_root.resolve()),
                "files": sorted(files),
                "server_actions": [],
                "github_actions": [],
            },
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

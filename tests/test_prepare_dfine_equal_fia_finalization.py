from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "prepare_dfine_equal_fia_finalization.py"
PROTOCOL = (
    ROOT
    / "paper_material"
    / "evidence"
    / "dfine_s_equal_fia_matched_20260823"
    / "protocol.json"
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write(path: Path, data: bytes) -> dict[str, object]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return {"bytes": len(data), "sha256": _sha256(data)}


def _make_evidence(root: Path) -> Path:
    stats = {
        ("treatment", "val"): [0.31 + index / 100 for index in range(12)],
        ("treatment", "test"): [0.23 + index / 100 for index in range(12)],
        ("control", "val"): [0.30 + index / 100 for index in range(12)],
        ("control", "test"): [0.20 + index / 100 for index in range(12)],
    }
    config_names = {
        ("treatment", "val"): "dfine_hgnetv2_s_visdrone_equal_fia.yml",
        ("treatment", "test"): "dfine_hgnetv2_s_visdrone_equal_fia_test.yml",
        ("control", "val"): "dfine_hgnetv2_s_visdrone.yml",
        ("control", "test"): "dfine_hgnetv2_s_visdrone_test.yml",
    }

    runs: dict[str, dict] = {}
    checkpoints: dict[str, tuple[str, str]] = {}
    for method, marker in (
        ("treatment", b"treatment-checkpoint"),
        ("control", b"control-checkpoint"),
    ):
        checkpoint_name = f"{method}_best_stg2.pth"
        checkpoint_path = root / "runs" / method / checkpoint_name
        checkpoint_record = _write(checkpoint_path, marker)
        log_record = _write(root / "runs" / method / "log.txt", b'{"epoch": 0}\n')
        train_record = _write(
            root / "runs" / method / "train.log", b"Training time 1:00:00\n"
        )
        remote_checkpoint = f"/server/runs/{method}/{checkpoint_name}"
        checkpoints[method] = (remote_checkpoint, checkpoint_record["sha256"])
        runs[method] = {
            "run_dir": f"/server/runs/{method}",
            "epoch_count": 132,
            "epoch_range": [0, 131],
            "log_sha256": log_record["sha256"],
            "train_log_sha256": train_record["sha256"],
            "best": {
                "best_epoch": 127,
                "val_ap": 0.30,
                "stats": [0.30 + index / 100 for index in range(12)],
                "stage": "best_stg2",
                "checkpoint_path": remote_checkpoint,
                "checkpoint_last_epoch": 127,
                "checkpoint_sha256": checkpoint_record["sha256"],
                "checkpoint_bytes": checkpoint_record["bytes"],
                "checkpoint_has_ema": True,
            },
        }

    evaluations = []
    for method, split in (
        ("treatment", "val"),
        ("treatment", "test"),
        ("control", "val"),
        ("control", "test"),
    ):
        output_dir = f"/server/evaluations/{method}/{split}"
        checkpoint, checkpoint_sha = checkpoints[method]
        local_dir = root / "evaluations" / method / split
        metrics_payload = {
            "format": "dfine.coco_bbox.evaluation_metrics",
            "version": 1,
            "coco_eval_bbox": stats[(method, split)],
            "metrics": {},
        }
        metrics_record = _write(
            local_dir / "evaluation_metrics.json",
            (json.dumps(metrics_payload, sort_keys=True) + "\n").encode(),
        )
        log_record = _write(
            local_dir / "evaluation.log", b"Load ema.state_dict\n"
        )
        eval_record = _write(local_dir / "eval.pth", b"auditable-eval")
        config = f"/server/source/configs/dfine/custom/{config_names[(method, split)]}"
        command = [
            "/venv/bin/python",
            "-u",
            "/server/source/train.py",
            "-c",
            config,
            "--use-amp",
            "--seed",
            "0",
            "--test-only",
            "-r",
            checkpoint,
            "--output-dir",
            output_dir,
        ]
        evaluations.append(
            {
                "method": method,
                "split": split,
                "config": config,
                "checkpoint": checkpoint,
                "output_dir": output_dir,
                "command": command,
                "returncode": 0,
                "metrics": metrics_payload,
                "artifacts": {
                    "eval_pth": {
                        "path": f"{output_dir}/eval.pth",
                        **eval_record,
                    },
                    "evaluation_metrics_json": {
                        "path": f"{output_dir}/evaluation_metrics.json",
                        **metrics_record,
                    },
                    "evaluation_log": {
                        "path": f"{output_dir}/evaluation.log",
                        **log_record,
                    },
                },
                "ema_restored": True,
            }
        )

    status = {
        "format": "dfine.post_training_evaluations",
        "version": 1,
        "status": "complete",
        "inputs": {
            "train_run_dir": "/server/runs/treatment",
            "control_run_dir": "/server/runs/control",
            "source_dir": "/server/source",
            "eval_root": "/server/evaluations",
            "python": "/venv/bin/python",
        },
        "runs": runs,
        "evaluations": evaluations,
    }
    status_path = root / "postrun_status.json"
    status_path.write_text(
        json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return status_path


def test_cli_verifies_local_evidence_and_prepares_non_destructive_bundle(
    tmp_path: Path,
) -> None:
    evidence = tmp_path / "pulled-evidence"
    status = _make_evidence(evidence)
    output = tmp_path / "finalization"

    result = subprocess.run(
        [
            sys.executable,
            str(TOOL),
            "--postrun-status",
            str(status),
            "--evidence-root",
            str(evidence),
            "--protocol",
            str(PROTOCOL),
            "--material-root",
            str(ROOT / "paper_material"),
            "--output-root",
            str(output),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["status"] == "prepared"
    assert report["verified_evaluation_count"] == 4
    assert report["server_actions"] == []
    assert report["github_actions"] == []

    expected = {
        "paper_material/evidence/dfine_s_equal_fia_matched_20260823/pair_summary.json",
        "paper_material/results/dfine_equal_fia_matched_results.json",
        "paper_material/results/DFINE_EQUAL_FIA_MATCHED_RESULTS_ZH.md",
        "paper_material/evidence/dfine_s_equal_fia_matched_20260823/MANIFEST.sha256",
        "paper_material/evidence/dfine_s_equal_fia_matched_20260823/.gitattributes",
        "integration/source_manifest.fragment.json",
        "integration/material_docs.patch",
        "integration/github_release_assets.json",
        "integration/material_apply_plan.json",
        "integration/internal_audit_status.json",
    }
    assert {
        path.relative_to(output).as_posix()
        for path in output.rglob("*")
        if path.is_file()
    } == expected

    manifest = (
        output
        / "paper_material/evidence/dfine_s_equal_fia_matched_20260823/MANIFEST.sha256"
    ).read_text(encoding="utf-8")
    assert "./postrun_status.json" in manifest
    assert "./runs/treatment/treatment_best_stg2.pth" not in manifest
    assert "./evaluations/treatment/val/evaluation_metrics.json" in manifest
    assert "./pair_summary.json" in manifest
    attributes = (
        output
        / "paper_material/evidence/dfine_s_equal_fia_matched_20260823/.gitattributes"
    ).read_bytes()
    assert attributes == b"* -text\n"
    assert f"{_sha256(attributes)}  ./.gitattributes" in manifest

    release = json.loads(
        (output / "integration/github_release_assets.json").read_text("utf-8")
    )
    assert release["automatic_upload"] is False
    assert release["contains_credentials"] is False
    assert {item["role"] for item in release["assets"]} >= {
        "treatment_best_checkpoint",
        "control_best_checkpoint",
        "postrun_status",
        "treatment_val_evaluation_log",
        "control_test_evaluation_metrics",
    }

    fragment = json.loads(
        (output / "integration/source_manifest.fragment.json").read_text("utf-8")
    )
    assert set(fragment["sources"]) == {
        "dfine_s_equal_fia_24c9cb1_seed0_formal132_best_val_test",
        "dfine_s_official7fe2_seed0_formal132_best_val_test",
        "dfine_s_equal_fia_vs_official7fe2_matched_pair",
    }
    for record in fragment["sources"].values():
        artifact = record["artifact"]
        assert (output / artifact).is_file()

    patch = (output / "integration/material_docs.patch").read_text("utf-8")
    assert "CURRENT_RERUN_STATUS_ZH.md" in patch
    assert "README_ZH.md" in patch
    assert "D-FINE-S + EQuAL + FIA 协议匹配结果" in patch
    assert "main_results.json" not in patch
    assert "MAIN_TABLE_ZH.md" not in patch

    apply_plan = json.loads(
        (output / "integration/material_apply_plan.json").read_text("utf-8")
    )
    copy_targets = {
        item["target"] for item in apply_plan["repository_evidence_copies"]
    }
    assert copy_targets >= {
        "paper_material/evidence/dfine_s_equal_fia_matched_20260823/postrun_status.json",
        "paper_material/evidence/dfine_s_equal_fia_matched_20260823/runs/treatment/log.txt",
        "paper_material/evidence/dfine_s_equal_fia_matched_20260823/"
        "evaluations/control/test/evaluation_metrics.json",
    }
    assert all(
        not item["target"].endswith((".pth", ".pt"))
        for item in apply_plan["repository_evidence_copies"]
    )

    audit = json.loads(
        (output / "integration/internal_audit_status.json").read_text("utf-8")
    )
    assert audit["outcome_policy"] == "negative_or_positive_by_completed_matched_eval"
    assert audit["completed_matched_eval_outcome"] == "positive"
    assert audit["claim_gate"]["formal_bundle_gain_claim_allowed"] is True
    assert audit["claim_gate"]["isolated_component_gain_claim_allowed"] is False
    assert audit["early_training_internal_context"] == {
        "formal_result_use_allowed": False,
        "observation": "treatment_trailing_control",
        "approximate_delta_pp": -8.1,
        "protocol_pretrain_initialization_evaluator_error_found": False,
        "diagnostic_factors": [
            "native_raw_reference_with_preliminary_supervision_disabled_"
            "yielded_exact_zero_pre_box_head",
            "dn_fgl_disabled_was_followed_by_abnormal_ddf_behavior",
        ],
    }
    formal_text = (
        output / "paper_material/results/DFINE_EQUAL_FIA_MATCHED_RESULTS_ZH.md"
    ).read_text("utf-8")
    formal_json = (
        output / "paper_material/results/dfine_equal_fia_matched_results.json"
    ).read_text("utf-8")
    for internal_only in ("-8.1", "pre_box", "abnormal_ddf"):
        assert internal_only not in formal_text
        assert internal_only not in formal_json


def test_rejects_a_protocol_that_changes_the_frozen_training_seed(
    tmp_path: Path,
) -> None:
    from tools.prepare_dfine_equal_fia_finalization import (
        FinalizationError,
        prepare_bundle,
    )

    evidence = tmp_path / "pulled-evidence"
    status = _make_evidence(evidence)
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    protocol["shared_training_protocol"]["seed"] = 1
    changed_protocol = tmp_path / "changed-protocol.json"
    changed_protocol.write_text(json.dumps(protocol), encoding="utf-8")

    with pytest.raises(FinalizationError, match="seed"):
        prepare_bundle(
            postrun_status_path=status,
            evidence_root=evidence,
            protocol_path=changed_protocol,
            material_root=ROOT / "paper_material",
        )


@pytest.mark.parametrize(
    ("keys", "replacement", "message"),
    [
        (("shared_training_protocol", "epochs"), 131, "training protocol"),
        (("shared_training_protocol", "image_size"), 800, "training protocol"),
        (
            ("shared_evaluation_protocol", "test_used_for_model_selection"),
            True,
            "evaluation protocol",
        ),
        (
            ("dataset", "test", "annotation_sha256"),
            "c" * 64,
            "dataset protocol",
        ),
        (
            ("metric_boundary", "cross_evaluator_metric_mixing_allowed"),
            True,
            "metric boundary",
        ),
    ],
)
def test_rejects_any_drift_from_the_frozen_matched_protocol(
    tmp_path: Path,
    keys: tuple[str, ...],
    replacement: object,
    message: str,
) -> None:
    from tools.prepare_dfine_equal_fia_finalization import (
        FinalizationError,
        prepare_bundle,
    )

    evidence = tmp_path / "pulled-evidence"
    status = _make_evidence(evidence)
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    cursor = protocol
    for key in keys[:-1]:
        cursor = cursor[key]
    cursor[keys[-1]] = replacement
    changed_protocol = tmp_path / "changed-protocol.json"
    changed_protocol.write_text(json.dumps(protocol), encoding="utf-8")

    with pytest.raises(FinalizationError, match=message):
        prepare_bundle(
            postrun_status_path=status,
            evidence_root=evidence,
            protocol_path=changed_protocol,
            material_root=ROOT / "paper_material",
        )


def test_rejects_artifact_metadata_bound_to_a_different_output_directory(
    tmp_path: Path,
) -> None:
    from tools.prepare_dfine_equal_fia_finalization import (
        FinalizationError,
        prepare_bundle,
    )

    evidence = tmp_path / "pulled-evidence"
    status_path = _make_evidence(evidence)
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status["evaluations"][0]["artifacts"]["eval_pth"]["path"] = (
        "/server/evaluations/control/test/eval.pth"
    )
    status_path.write_text(json.dumps(status), encoding="utf-8")

    with pytest.raises(FinalizationError, match="output directory"):
        prepare_bundle(
            postrun_status_path=status_path,
            evidence_root=evidence,
            protocol_path=PROTOCOL,
            material_root=ROOT / "paper_material",
        )


def test_rejects_a_best_checkpoint_claim_bound_to_another_run_directory(
    tmp_path: Path,
) -> None:
    from tools.prepare_dfine_equal_fia_finalization import (
        FinalizationError,
        prepare_bundle,
    )

    evidence = tmp_path / "pulled-evidence"
    status_path = _make_evidence(evidence)
    status = json.loads(status_path.read_text(encoding="utf-8"))
    wrong = "/server/runs/control/treatment_best_stg2.pth"
    status["runs"]["treatment"]["best"]["checkpoint_path"] = wrong
    for item in status["evaluations"]:
        if item["method"] == "treatment":
            item["checkpoint"] = wrong
            item["command"][item["command"].index("-r") + 1] = wrong
    status_path.write_text(json.dumps(status), encoding="utf-8")

    with pytest.raises(FinalizationError, match="run directory"):
        prepare_bundle(
            postrun_status_path=status_path,
            evidence_root=evidence,
            protocol_path=PROTOCOL,
            material_root=ROOT / "paper_material",
        )


def test_rejects_a_best_record_whose_val_ap_disagrees_with_its_coco_stats(
    tmp_path: Path,
) -> None:
    from tools.prepare_dfine_equal_fia_finalization import (
        FinalizationError,
        prepare_bundle,
    )

    evidence = tmp_path / "pulled-evidence"
    status_path = _make_evidence(evidence)
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status["runs"]["control"]["best"]["val_ap"] = 0.99
    status_path.write_text(json.dumps(status), encoding="utf-8")

    with pytest.raises(FinalizationError, match="val_ap"):
        prepare_bundle(
            postrun_status_path=status_path,
            evidence_root=evidence,
            protocol_path=PROTOCOL,
            material_root=ROOT / "paper_material",
        )


def test_rejects_a_best_record_with_the_wrong_stage_for_its_epoch(
    tmp_path: Path,
) -> None:
    from tools.prepare_dfine_equal_fia_finalization import (
        FinalizationError,
        prepare_bundle,
    )

    evidence = tmp_path / "pulled-evidence"
    status_path = _make_evidence(evidence)
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status["runs"]["control"]["best"]["stage"] = "best_stg1"
    status_path.write_text(json.dumps(status), encoding="utf-8")

    with pytest.raises(FinalizationError, match="stage"):
        prepare_bundle(
            postrun_status_path=status_path,
            evidence_root=evidence,
            protocol_path=PROTOCOL,
            material_root=ROOT / "paper_material",
        )


def test_rejects_a_conflicting_existing_source_manifest_record(
    tmp_path: Path,
) -> None:
    from tools.prepare_dfine_equal_fia_finalization import (
        FinalizationError,
        prepare_bundle,
    )

    evidence = tmp_path / "pulled-evidence"
    status_path = _make_evidence(evidence)
    material = tmp_path / "paper_material"
    (material / "evidence").mkdir(parents=True)
    (material / "CURRENT_RERUN_STATUS_ZH.md").write_text("# status\n", encoding="utf-8")
    (material / "README_ZH.md").write_text("# readme\n", encoding="utf-8")
    (material / "evidence/source_manifest.json").write_text(
        json.dumps(
            {
                "sources": {
                    "dfine_s_equal_fia_24c9cb1_seed0_formal132_best_val_test": {
                        "artifact": "wrong.json"
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(FinalizationError, match="source manifest conflict"):
        prepare_bundle(
            postrun_status_path=status_path,
            evidence_root=evidence,
            protocol_path=PROTOCOL,
            material_root=material,
        )


def test_rejects_a_locally_tampered_best_checkpoint(tmp_path: Path) -> None:
    from tools.prepare_dfine_equal_fia_finalization import (
        FinalizationError,
        prepare_bundle,
    )

    evidence = tmp_path / "pulled-evidence"
    status_path = _make_evidence(evidence)
    checkpoint = evidence / "runs/control/control_best_stg2.pth"
    checkpoint.write_bytes(checkpoint.read_bytes() + b"tampered")

    with pytest.raises(FinalizationError, match="checkpoint byte count mismatch"):
        prepare_bundle(
            postrun_status_path=status_path,
            evidence_root=evidence,
            protocol_path=PROTOCOL,
            material_root=ROOT / "paper_material",
        )


def test_rejects_local_metrics_that_do_not_exactly_match_postrun_status(
    tmp_path: Path,
) -> None:
    from tools.prepare_dfine_equal_fia_finalization import (
        FinalizationError,
        prepare_bundle,
    )

    evidence = tmp_path / "pulled-evidence"
    status_path = _make_evidence(evidence)
    status = json.loads(status_path.read_text(encoding="utf-8"))
    metrics_path = evidence / "evaluations/treatment/val/evaluation_metrics.json"
    payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    payload["coco_eval_bbox"][0] = 0.999
    metrics_record = _write(
        metrics_path, (json.dumps(payload, sort_keys=True) + "\n").encode()
    )
    status["evaluations"][0]["artifacts"]["evaluation_metrics_json"].update(
        metrics_record
    )
    status_path.write_text(json.dumps(status), encoding="utf-8")

    with pytest.raises(FinalizationError, match="exactly match"):
        prepare_bundle(
            postrun_status_path=status_path,
            evidence_root=evidence,
            protocol_path=PROTOCOL,
            material_root=ROOT / "paper_material",
        )


def test_rejects_a_log_that_synthesizes_instead_of_restoring_ema(
    tmp_path: Path,
) -> None:
    from tools.prepare_dfine_equal_fia_finalization import (
        FinalizationError,
        prepare_bundle,
    )

    evidence = tmp_path / "pulled-evidence"
    status_path = _make_evidence(evidence)
    status = json.loads(status_path.read_text(encoding="utf-8"))
    log_path = evidence / "evaluations/control/test/evaluation.log"
    log_record = _write(
        log_path, b"Load ema.state_dict from model.state_dict\n"
    )
    status["evaluations"][3]["artifacts"]["evaluation_log"].update(log_record)
    status_path.write_text(json.dumps(status), encoding="utf-8")

    with pytest.raises(FinalizationError, match="synthesized EMA"):
        prepare_bundle(
            postrun_status_path=status_path,
            evidence_root=evidence,
            protocol_path=PROTOCOL,
            material_root=ROOT / "paper_material",
        )


def test_rejects_an_evaluation_with_fewer_than_twelve_coco_stats(
    tmp_path: Path,
) -> None:
    from tools.prepare_dfine_equal_fia_finalization import (
        FinalizationError,
        prepare_bundle,
    )

    evidence = tmp_path / "pulled-evidence"
    status_path = _make_evidence(evidence)
    status = json.loads(status_path.read_text(encoding="utf-8"))
    item = status["evaluations"][2]
    item["metrics"]["coco_eval_bbox"].pop()
    metrics_path = evidence / "evaluations/control/val/evaluation_metrics.json"
    metrics_record = _write(
        metrics_path, (json.dumps(item["metrics"], sort_keys=True) + "\n").encode()
    )
    item["artifacts"]["evaluation_metrics_json"].update(metrics_record)
    status_path.write_text(json.dumps(status), encoding="utf-8")

    with pytest.raises(FinalizationError, match="exactly 12 COCO stats"):
        prepare_bundle(
            postrun_status_path=status_path,
            evidence_root=evidence,
            protocol_path=PROTOCOL,
            material_root=ROOT / "paper_material",
        )


def test_writer_refuses_nonempty_output_without_touching_it(tmp_path: Path) -> None:
    from tools.prepare_dfine_equal_fia_finalization import (
        FinalizationError,
        prepare_bundle,
        write_bundle,
    )

    evidence = tmp_path / "pulled-evidence"
    status_path = _make_evidence(evidence)
    files = prepare_bundle(
        postrun_status_path=status_path,
        evidence_root=evidence,
        protocol_path=PROTOCOL,
        material_root=ROOT / "paper_material",
    )
    output = tmp_path / "occupied"
    output.mkdir()
    sentinel = output / "keep.txt"
    sentinel.write_text("user-owned", encoding="utf-8")

    with pytest.raises(FinalizationError, match="new or empty"):
        write_bundle(files, output)

    assert sentinel.read_text(encoding="utf-8") == "user-owned"
    assert list(output.iterdir()) == [sentinel]


def test_negative_completed_pair_blocks_a_formal_gain_claim() -> None:
    from tools.prepare_dfine_equal_fia_finalization import _internal_audit_status

    audit = _internal_audit_status(
        {
            "comparisons": {
                "val": {"delta_pp": {"AP": -8.1}},
                "test": {"delta_pp": {"AP": -7.9}},
            }
        }
    )

    assert audit["completed_matched_eval_outcome"] == "negative"
    assert audit["claim_gate"]["formal_bundle_gain_claim_allowed"] is False
    assert audit["claim_gate"]["negative_or_mixed_outcome_requires_plain_reporting"] is True

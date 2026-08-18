from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import torch
import yaml
from torch import nn

from src.acr_bpdd_protocol import (
    ACR_BPDD_PROTOCOL_SHA256,
    FDR_INITIAL_STATE_SHA256,
    build_run_identity,
)
from src.lpr_protocol import CATEGORY_NAMES


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "evaluate_acr_bpdd_formal.py"
SCALE_NAMES = ("tiny", "small", "medium", "large")


def _load_module():
    assert SCRIPT.is_file(), "ACR-BPDD formal evaluation CLI has not been implemented"
    spec = importlib.util.spec_from_file_location("evaluate_acr_bpdd_formal", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _canonical_sha(payload: dict) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest().upper()


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(
            json.dumps(row, sort_keys=True, separators=(",", ":"), allow_nan=False)
            + "\n"
            for row in rows
        ),
        encoding="utf-8",
    )


def _source() -> dict[str, str]:
    return {"git_commit": "a" * 40, "tree_sha256": "B" * 64}


def _identity() -> dict[str, object]:
    return build_run_identity(
        _source(), stage="formal", variant="fdr_acr_bpdd", seed=0
    )


def _dataset_yaml(path: Path, dataset_root: Path) -> Path:
    path.write_text(
        yaml.safe_dump(
            {
                "path": str(dataset_root.resolve()),
                "train": "images/train",
                "val": "images/val",
                "names": list(CATEGORY_NAMES),
                "nc": 10,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return path


def _run_authority(
    tmp_path: Path,
) -> tuple[Path, Path, Path, Path, Path, Path]:
    run = tmp_path / "formal-seed0-fdr_acr_bpdd-v1"
    weights = run / "weights"
    weights.mkdir(parents=True)
    checkpoint = weights / "epoch99.pt"
    checkpoint.write_bytes(b"acr-bpdd-formal-final")
    checkpoint_sha = _sha(checkpoint)
    dataset_root = tmp_path / "VisDrone"
    data_yaml = _dataset_yaml(tmp_path / "formal-data.yaml", dataset_root)
    queue = run / "publication-queue.jsonl"
    epochs = run / "acr-bpdd-epochs.jsonl"
    ledger = tmp_path / "publication-ledger.jsonl"
    identity = _identity()
    manifest = {
        "format_version": 1,
        "protocol_sha256": ACR_BPDD_PROTOCOL_SHA256,
        "fdr_protocol_sha256": identity["fdr_protocol_sha256"],
        "source": _source(),
        "run_identity": identity,
        "initial_state": {
            "path": str((tmp_path / "initial-state.pt").resolve()),
            "sha256": FDR_INITIAL_STATE_SHA256,
        },
        "data": str(data_yaml.resolve()),
        "publication_queue": str(queue.resolve()),
        "comparison": {
            "evidence_level": "preliminary_cross_run",
            "strict_paired": False,
        },
    }
    (run / "acr-bpdd-run.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    epoch_rows = [
        {
            "completed_epoch": epoch,
            "run_id": identity["run_id"],
            "variant": "fdr_acr_bpdd",
            "stage": "formal",
            "gradients_finite": True,
        }
        for epoch in range(1, 101)
    ]
    _write_jsonl(epochs, epoch_rows)
    csv_path = run / "acr-bpdd-epochs.csv"
    csv_path.write_text("completed_epoch\n1\n", encoding="utf-8")
    optimizer_path = run / "optimizer-evidence.jsonl"
    optimizer_path.write_text('{"optimizer_attempt":1}\n', encoding="utf-8")
    declared_artifacts = [
        str(path.resolve())
        for path in (
            epochs,
            csv_path,
            run / "acr-bpdd-run.json",
            optimizer_path,
        )
    ]
    queue_rows = []
    ledger_rows = []
    for epoch in range(1, 101):
        sha256 = checkpoint_sha if epoch == 100 else f"{epoch:064X}"
        row = {
            "run_id": identity["run_id"],
            "variant": "fdr_acr_bpdd",
            "stage": "formal",
            "completed_epoch": epoch,
            "status": "pending",
            "checkpoint": str(
                (weights / f"epoch{epoch - 1}.pt").resolve()
            ),
            "checkpoint_sha256": sha256,
            "artifacts": list(declared_artifacts),
        }
        queue_rows.append(row)
        ledger_rows.append(
            {
                "run_id": identity["run_id"],
                "variant": "fdr_acr_bpdd",
                "stage": "formal",
                "completed_epoch": epoch,
                "queue_record_sha256": _canonical_sha(row),
                "checkpoint": {
                    "name": f"fdr-acr-bpdd-formal-epoch-{epoch:04d}.pt",
                    "sha256": sha256,
                },
                "verified": True,
            }
        )
    _write_jsonl(queue, queue_rows)
    _write_jsonl(ledger, ledger_rows)
    return run, checkpoint, ledger, queue, epochs, dataset_root


def _make_split(dataset_root: Path, split: str, count: int) -> None:
    image_root = dataset_root / "images" / split
    label_root = dataset_root / "labels" / split
    image_root.mkdir(parents=True, exist_ok=True)
    label_root.mkdir(parents=True, exist_ok=True)
    for index in range(count):
        stem = f"frame-{index:04d}"
        (image_root / f"{stem}.jpg").write_bytes(f"image-{index}".encode())
        (label_root / f"{stem}.txt").write_bytes(f"0 0.5 0.5 0.1 {index}\n".encode())


def _validation_payload(map_value: float = 0.31, *, images: int = 2) -> dict:
    return {
        "metrics": {
            "precision": 0.57,
            "recall": 0.50,
            "f1": 0.5327102804,
            "map50": 0.49,
            "map75": 0.30,
            "map": map_value,
        },
        "scales": {name: map_value for name in SCALE_NAMES},
        "scale_details": {
            name: {"gt": 1, "map50": 0.4, "map75": 0.3, "map": map_value}
            for name in SCALE_NAMES
        },
        "classes": {name: map_value for name in CATEGORY_NAMES},
        "class_details": {
            name: {
                "id": index,
                "map50": 0.4,
                "map75": 0.3,
                "map": map_value,
            }
            for index, name in enumerate(CATEGORY_NAMES)
        },
        "processed_images": images,
        "prediction_passes": 1,
    }


def _reference(path: Path, map_value: float) -> Path:
    path.write_text(json.dumps(_validation_payload(map_value)), encoding="utf-8")
    return path


def test_cli_exposes_only_frozen_final_evaluation_controls() -> None:
    formal = _load_module()
    parser = formal.build_parser()
    args = parser.parse_args(
        [
            "--run-dir",
            "run",
            "--checkpoint",
            "epoch99.pt",
            "--publication-ledger",
            "ledger.jsonl",
            "--dataset-root",
            "VisDrone",
            "--split",
            "test",
            "--fdr-evaluation",
            "fdr.json",
            "--bpdd-evaluation",
            "bpdd.json",
            "--output",
            "report.json",
            "--device",
            "cuda:1",
        ]
    )
    assert args.run_dir == Path("run")
    assert args.checkpoint == Path("epoch99.pt")
    assert args.publication_ledger == Path("ledger.jsonl")
    assert args.dataset_root == Path("VisDrone")
    assert args.split == "test"
    assert args.fdr_evaluation == Path("fdr.json")
    assert args.bpdd_evaluation == Path("bpdd.json")
    assert args.output == Path("report.json")
    assert args.device == "cuda:1"
    assert parser.parse_args(
        [
            "--run-dir", "run",
            "--checkpoint", "epoch99.pt",
            "--publication-ledger", "ledger.jsonl",
            "--dataset-root", "VisDrone",
            "--output", "report.json",
        ]
    ).split == "val"
    assert not any(
        option in parser._option_string_actions
        for option in ("--imgsz", "--batch", "--max-det", "--nms", "--warmup", "--runs")
    )


def test_protocols_are_frozen_for_one_prediction_pass_and_fp16_benchmark() -> None:
    formal = _load_module()
    assert formal.EVALUATION_PROTOCOL == {
        "imgsz": 640,
        "batch": 8,
        "workers": 8,
        "conf": 0.001,
        "max_det": 300,
        "nms": False,
    }
    assert formal.BENCHMARK_PROTOCOL == {
        "imgsz": 640,
        "batch": 1,
        "half": True,
        "warmup": 50,
        "runs": 200,
    }


def test_formal_authority_requires_exact_100_epoch_queue_and_verified_ledger(
    tmp_path: Path,
) -> None:
    formal = _load_module()
    run, checkpoint, ledger, queue, epochs, _ = _run_authority(tmp_path)

    authority = formal.validate_formal_authority(
        run, checkpoint=checkpoint, publication_ledger=ledger
    )

    assert authority["identity"] == _identity()
    assert authority["completed_epoch"] == 100
    assert authority["epoch_records"]["completed_epochs"] == [1, 100]
    assert authority["publication_queue"]["completed_epochs"] == [1, 100]
    assert authority["publication_ledger"]["completed_epochs"] == [1, 100]
    assert authority["publication_ledger"]["all_verified"] is True
    assert authority["checkpoint_sha256"] == _sha(checkpoint)
    assert authority["artifacts"]["run_manifest"]["sha256"] == _sha(
        run / "acr-bpdd-run.json"
    )
    assert authority["artifacts"]["epoch_records"]["sha256"] == _sha(epochs)
    assert authority["artifacts"]["publication_queue"]["sha256"] == _sha(queue)
    assert authority["artifacts"]["publication_ledger"]["sha256"] == _sha(ledger)
    assert authority["artifacts"]["acr-bpdd-epochs.csv"] == {
        "path": str((run / "acr-bpdd-epochs.csv").resolve()),
        "bytes": (run / "acr-bpdd-epochs.csv").stat().st_size,
        "sha256": _sha(run / "acr-bpdd-epochs.csv"),
        "declared_first_epoch": 1,
        "declared_last_epoch": 100,
        "declared_epoch_count": 100,
    }
    assert authority["artifacts"]["optimizer-evidence.jsonl"] == {
        "path": str((run / "optimizer-evidence.jsonl").resolve()),
        "bytes": (run / "optimizer-evidence.jsonl").stat().st_size,
        "sha256": _sha(run / "optimizer-evidence.jsonl"),
        "declared_first_epoch": 1,
        "declared_last_epoch": 100,
        "declared_epoch_count": 100,
    }


@pytest.mark.parametrize(
    "mutation",
    ("path_escape", "missing_file"),
)
def test_queue_string_artifacts_reject_escape_and_missing_file(
    tmp_path: Path, mutation: str
) -> None:
    formal = _load_module()
    run, checkpoint, ledger, queue, _, _ = _run_authority(tmp_path)
    queue_rows = [json.loads(line) for line in queue.read_text("utf-8").splitlines()]
    if mutation == "path_escape":
        outside = tmp_path / "outside.jsonl"
        outside.write_text("outside\n", encoding="utf-8")
        queue_rows[0]["artifacts"].append(str(outside))
    else:
        missing = run / "missing.jsonl"
        queue_rows[0]["artifacts"].append(str(missing))
    _write_jsonl(queue, queue_rows)
    ledger_rows = [json.loads(line) for line in ledger.read_text("utf-8").splitlines()]
    ledger_rows[0]["queue_record_sha256"] = _canonical_sha(queue_rows[0])
    _write_jsonl(ledger, ledger_rows)

    expected = "outside run directory" if mutation == "path_escape" else "artifact is missing"
    with pytest.raises((FileNotFoundError, ValueError), match=expected):
        formal.validate_formal_authority(
            run, checkpoint=checkpoint, publication_ledger=ledger
        )


def test_same_epoch_duplicate_exact_string_path_is_deduplicated(tmp_path: Path) -> None:
    formal = _load_module()
    run, checkpoint, ledger, queue, _, _ = _run_authority(tmp_path)
    queue_rows = [json.loads(line) for line in queue.read_text("utf-8").splitlines()]
    queue_rows[0]["artifacts"].append(queue_rows[0]["artifacts"][0])
    _write_jsonl(queue, queue_rows)
    ledger_rows = [json.loads(line) for line in ledger.read_text("utf-8").splitlines()]
    ledger_rows[0]["queue_record_sha256"] = _canonical_sha(queue_rows[0])
    _write_jsonl(ledger, ledger_rows)

    authority = formal.validate_formal_authority(
        run, checkpoint=checkpoint, publication_ledger=ledger
    )

    assert authority["artifacts"]["epoch_records"][
        "declared_epoch_count"
    ] == 100


def test_canonical_alias_with_conflicting_object_semantics_is_rejected(
    tmp_path: Path,
) -> None:
    formal = _load_module()
    run, checkpoint, ledger, queue, _, _ = _run_authority(tmp_path)
    queue_rows = [json.loads(line) for line in queue.read_text("utf-8").splitlines()]
    target = run / "optimizer-evidence.jsonl"
    alias = run / "evidence" / ".." / target.name
    queue_rows[0]["artifacts"].append(
        {
            "name": "different-optimizer-semantics.jsonl",
            "path": str(alias),
            "content_semantics": "cumulative",
        }
    )
    _write_jsonl(queue, queue_rows)
    ledger_rows = [json.loads(line) for line in ledger.read_text("utf-8").splitlines()]
    ledger_rows[0]["queue_record_sha256"] = _canonical_sha(queue_rows[0])
    _write_jsonl(ledger, ledger_rows)

    with pytest.raises(ValueError, match="semantic|conflict|canonical"):
        formal.validate_formal_authority(
            run, checkpoint=checkpoint, publication_ledger=ledger
        )


def test_optional_immutable_object_artifact_validates_declared_sha(tmp_path: Path) -> None:
    formal = _load_module()
    run, checkpoint, ledger, queue, _, _ = _run_authority(tmp_path)
    immutable = run / "frozen-evaluation-authority.json"
    immutable.write_text('{"frozen":true}\n', encoding="utf-8")
    queue_rows = [json.loads(line) for line in queue.read_text("utf-8").splitlines()]
    queue_rows[0]["artifacts"].append(
        {
            "name": immutable.name,
            "path": str(immutable),
            "content_semantics": "immutable",
            "sha256": _sha(immutable),
        }
    )
    _write_jsonl(queue, queue_rows)
    ledger_rows = [json.loads(line) for line in ledger.read_text("utf-8").splitlines()]
    ledger_rows[0]["queue_record_sha256"] = _canonical_sha(queue_rows[0])
    _write_jsonl(ledger, ledger_rows)

    authority = formal.validate_formal_authority(
        run, checkpoint=checkpoint, publication_ledger=ledger
    )

    assert authority["artifacts"][immutable.name] == {
        "path": str(immutable.resolve()),
        "bytes": immutable.stat().st_size,
        "sha256": _sha(immutable),
        "declared_first_epoch": 1,
        "declared_last_epoch": 1,
        "declared_epoch_count": 1,
    }


@pytest.mark.parametrize("mode", ("ambiguous_historical_sha", "immutable_sha_mismatch"))
def test_object_sha_is_only_valid_for_matching_immutable_artifact(
    tmp_path: Path, mode: str
) -> None:
    formal = _load_module()
    run, checkpoint, ledger, queue, _, _ = _run_authority(tmp_path)
    target = run / "optimizer-evidence.jsonl"
    if mode == "immutable_sha_mismatch":
        target = run / "frozen-mismatch.json"
        target.write_text('{"frozen":true}\n', encoding="utf-8")
    declaration = {
        "name": target.name,
        "path": str(target),
        "sha256": "0" * 64,
    }
    if mode == "immutable_sha_mismatch":
        declaration["content_semantics"] = "immutable"
    queue_rows = [json.loads(line) for line in queue.read_text("utf-8").splitlines()]
    queue_rows[0]["artifacts"] = [declaration]
    _write_jsonl(queue, queue_rows)
    ledger_rows = [json.loads(line) for line in ledger.read_text("utf-8").splitlines()]
    ledger_rows[0]["queue_record_sha256"] = _canonical_sha(queue_rows[0])
    _write_jsonl(ledger, ledger_rows)

    expected = (
        "immutable|semantic"
        if mode == "ambiguous_historical_sha"
        else "SHA256 mismatch"
    )
    with pytest.raises(ValueError, match=expected):
        formal.validate_formal_authority(
            run, checkpoint=checkpoint, publication_ledger=ledger
        )


@pytest.mark.parametrize(
    "mutation",
    (
        "manifest_variant",
        "manifest_stage",
        "epoch_gap",
        "queue_gap",
        "ledger_unverified",
        "ledger_queue_sha",
        "ledger_checkpoint_sha",
        "actual_checkpoint_sha",
    ),
)
def test_formal_authority_fails_closed_on_any_chain_drift(
    tmp_path: Path, mutation: str
) -> None:
    formal = _load_module()
    run, checkpoint, ledger, queue, epochs, _ = _run_authority(tmp_path)
    if mutation.startswith("manifest_"):
        path = run / "acr-bpdd-run.json"
        payload = json.loads(path.read_text("utf-8"))
        payload["run_identity"][mutation.removeprefix("manifest_")] = "wrong"
        path.write_text(json.dumps(payload), encoding="utf-8")
    elif mutation == "epoch_gap":
        rows = [json.loads(line) for line in epochs.read_text("utf-8").splitlines()]
        rows.pop(40)
        _write_jsonl(epochs, rows)
    elif mutation == "queue_gap":
        rows = [json.loads(line) for line in queue.read_text("utf-8").splitlines()]
        rows[40]["completed_epoch"] = 42
        _write_jsonl(queue, rows)
    elif mutation == "ledger_unverified":
        rows = [json.loads(line) for line in ledger.read_text("utf-8").splitlines()]
        rows[40]["verified"] = False
        _write_jsonl(ledger, rows)
    elif mutation == "ledger_queue_sha":
        rows = [json.loads(line) for line in ledger.read_text("utf-8").splitlines()]
        rows[40]["queue_record_sha256"] = "0" * 64
        _write_jsonl(ledger, rows)
    elif mutation == "ledger_checkpoint_sha":
        rows = [json.loads(line) for line in ledger.read_text("utf-8").splitlines()]
        rows[40]["checkpoint"]["sha256"] = "0" * 64
        _write_jsonl(ledger, rows)
    else:
        checkpoint.write_bytes(b"changed-final")

    with pytest.raises(ValueError, match="manifest|identity|epoch|queue|ledger|SHA256|checkpoint"):
        formal.validate_formal_authority(
            run, checkpoint=checkpoint, publication_ledger=ledger
        )


def test_formal_authority_rejects_any_checkpoint_name_other_than_epoch99(
    tmp_path: Path,
) -> None:
    formal = _load_module()
    run, _, ledger, _, _, _ = _run_authority(tmp_path)
    checkpoint = run / "weights" / "last.pt"
    checkpoint.write_bytes(b"acr-bpdd-formal-final")
    with pytest.raises(ValueError, match="epoch99"):
        formal.validate_formal_authority(
            run, checkpoint=checkpoint, publication_ledger=ledger
        )


def test_formal_authority_allows_relocated_epoch99_when_sha_chain_matches(
    tmp_path: Path,
) -> None:
    formal = _load_module()
    run, checkpoint, ledger, queue, _, _ = _run_authority(tmp_path)
    relocated = tmp_path / "downloaded" / "epoch99.pt"
    relocated.parent.mkdir()
    relocated.write_bytes(checkpoint.read_bytes())
    queue_rows = [json.loads(line) for line in queue.read_text("utf-8").splitlines()]
    queue_rows[-1]["checkpoint"] = str((tmp_path / "server" / "epoch99.pt").resolve())
    _write_jsonl(queue, queue_rows)
    ledger_rows = [json.loads(line) for line in ledger.read_text("utf-8").splitlines()]
    ledger_rows[-1]["queue_record_sha256"] = _canonical_sha(queue_rows[-1])
    _write_jsonl(ledger, ledger_rows)

    authority = formal.validate_formal_authority(
        run, checkpoint=relocated, publication_ledger=ledger
    )

    assert authority["checkpoint_sha256"] == _sha(relocated)


def test_split_authority_records_every_test_image_and_label_content_sha256(
    tmp_path: Path,
) -> None:
    formal = _load_module()
    dataset_root = tmp_path / "VisDrone"
    _make_split(dataset_root, "test", 2)

    authority = formal.build_split_authority(dataset_root, "test")

    assert authority["split"] == "test"
    assert authority["images"]["count"] == 2
    assert authority["labels"]["count"] == 2
    assert len(authority["images"]["files"]) == 2
    assert len(authority["labels"]["files"]) == 2
    image = dataset_root / "images" / "test" / "frame-0000.jpg"
    assert authority["images"]["files"][0] == {
        "path": "images/test/frame-0000.jpg",
        "bytes": image.stat().st_size,
        "sha256": _sha(image),
    }
    before = authority["labels"]["sha256"]
    (dataset_root / "labels" / "test" / "frame-0000.txt").write_bytes(b"changed")
    assert formal.build_split_authority(dataset_root, "test")["labels"]["sha256"] != before


def test_val_split_requires_exactly_548_images(tmp_path: Path) -> None:
    formal = _load_module()
    dataset_root = tmp_path / "VisDrone"
    _make_split(dataset_root, "val", 548)
    authority = formal.build_split_authority(dataset_root, "val")
    assert authority["images"]["count"] == 548
    (dataset_root / "images" / "val" / "frame-0547.jpg").unlink()
    with pytest.raises(ValueError, match="548"):
        formal.build_split_authority(dataset_root, "val")


def test_complete_metrics_never_fabricate_missing_scale_or_class_values() -> None:
    formal = _load_module()
    complete = _validation_payload()
    assert formal.validate_complete_metrics(complete) is complete
    del complete["class_details"][CATEGORY_NAMES[-1]]["map75"]
    with pytest.raises(ValueError, match="class|AP75|map75"):
        formal.validate_complete_metrics(complete)

    complete = _validation_payload()
    del complete["scales"]["tiny"]
    with pytest.raises(ValueError, match="scale|tiny"):
        formal.validate_complete_metrics(complete)


def test_latency_summary_reports_mean_median_p95_and_mean_fps() -> None:
    formal = _load_module()
    summary = formal.latency_summary([1.0, 2.0, 3.0, 4.0, 10.0])
    assert summary == {
        "mean_ms": 4.0,
        "median_ms": 3.0,
        "p95_ms": pytest.approx(8.8),
        "fps": pytest.approx(250.0),
    }
    with pytest.raises(ValueError, match="finite|positive|empty"):
        formal.latency_summary([])


def test_optional_references_are_always_explicit_cross_run_deltas(
    tmp_path: Path,
) -> None:
    formal = _load_module()
    current = _validation_payload(0.31)
    fdr = _reference(tmp_path / "fdr.json", 0.28)
    bpdd = _reference(tmp_path / "bpdd.json", 0.30)

    comparison = formal.build_cross_run_comparison(
        current, fdr_evaluation=fdr, bpdd_evaluation=bpdd
    )

    assert comparison["comparison_scope"] == "preliminary_cross_run"
    assert comparison["strict_paired"] is False
    assert set(comparison["references"]) == {"fdr", "bpdd"}
    assert comparison["references"]["fdr"]["metrics_delta"]["map"] == pytest.approx(0.03)
    assert comparison["references"]["bpdd"]["scale_delta"]["tiny"] == pytest.approx(0.01)
    assert comparison["references"]["bpdd"]["class_delta"]["car"]["map75"] == pytest.approx(0.0)
    assert comparison["references"]["fdr"]["artifact_sha256"] == _sha(fdr)
    assert not any("strict" in key and key != "strict_paired" for key in comparison)
    assert formal.build_cross_run_comparison(current) == {
        "comparison_scope": "preliminary_cross_run",
        "strict_paired": False,
        "references": {},
    }


class TinyCheckpointState(nn.Module):
    def __init__(self, value: float) -> None:
        super().__init__()
        self.weight = nn.Parameter(torch.tensor([value]))


class TinyInferenceModel(nn.Module):
    def __init__(self, *args, nc: int | None = None, **kwargs) -> None:
        super().__init__()
        assert nc == 10
        self.weight = nn.Parameter(torch.zeros(1))


def test_shared_exact_loader_requires_optimizer_and_hashes_model_tensor_state(
    tmp_path: Path,
) -> None:
    formal = _load_module()
    checkpoint = tmp_path / "epoch99.pt"
    model_state = TinyCheckpointState(2.0)
    torch.save(
        {
            "epoch": 99,
            "optimizer": {"state": {}, "param_groups": []},
            "ema": None,
            "model": model_state,
        },
        checkpoint,
    )
    loaded = formal.load_exact_final_checkpoint(
        checkpoint,
        expected_sha256=_sha(checkpoint),
        model_factory=TinyInferenceModel,
    )
    assert loaded.metadata["source_field"] == "model"
    assert loaded.metadata["sha256"] == _sha(checkpoint)
    assert loaded.metadata["ema_state_sha256"] == formal.state_sha256(
        model_state.state_dict()
    )
    torch.testing.assert_close(loaded.model.weight, torch.tensor([2.0]))

    torch.save({"epoch": 99, "optimizer": None, "ema": model_state}, checkpoint)
    with pytest.raises(ValueError, match="optimizer"):
        formal.load_exact_final_checkpoint(
            checkpoint,
            expected_sha256=_sha(checkpoint),
            model_factory=TinyInferenceModel,
        )


def test_end_to_end_report_binds_authorities_metrics_efficiency_and_inventory(
    tmp_path: Path,
) -> None:
    formal = _load_module()
    run, checkpoint, ledger, queue, epochs, dataset_root = _run_authority(tmp_path)
    _make_split(dataset_root, "test", 2)
    fdr = _reference(tmp_path / "fdr.json", 0.28)
    output = tmp_path / "acr-bpdd-test-evaluation.json"
    validation_model = object()
    efficiency_model = object()
    metadata = {
        "kind": "exact-final-ema",
        "completed_epoch": 100,
        "raw_epoch": 99,
        "sha256": _sha(checkpoint),
        "sha256_verified": True,
        "source_field": "ema",
        "ema_state_sha256": "E" * 64,
        "strict_fdr_inference_graph": True,
    }
    calls: dict[str, object] = {"load": []}

    def loader(path, *, expected_sha256):
        calls["load"].append((Path(path), expected_sha256))
        model = validation_model if len(calls["load"]) == 1 else efficiency_model
        return SimpleNamespace(model=model, metadata=dict(metadata))

    def validate(model, *, dataset_root, split, save_dir, device, expected_images):
        calls["validation"] = (
            model,
            Path(dataset_root),
            split,
            Path(save_dir),
            device,
            expected_images,
        )
        return _validation_payload(images=2)

    def efficiency(model, *, device):
        calls["efficiency"] = (model, device)
        return {
            "parameters": 33_500_000,
            "gflops": 105.2,
            "fp16": {
                "device": device,
                "batch": 1,
                "warmup": 50,
                "runs": 200,
                "mean_ms": 5.1,
                "median_ms": 5.0,
                "p95_ms": 5.5,
                "fps": 1000 / 5.1,
            },
        }

    report = formal.evaluate_formal_checkpoint(
        run_dir=run,
        checkpoint=checkpoint,
        publication_ledger=ledger,
        dataset_root=dataset_root,
        split="test",
        fdr_evaluation=fdr,
        bpdd_evaluation=None,
        output=output,
        device="cuda:0",
        checkpoint_loader=loader,
        validation_runner=validate,
        efficiency_runner=efficiency,
        environment_reader=lambda _device: {
            "gpu": {"name": "mock RTX 4090"},
            "software": {"python": "3.x", "torch": "mock"},
        },
    )

    assert calls["load"] == [
        (checkpoint.resolve(), _sha(checkpoint)),
        (checkpoint.resolve(), _sha(checkpoint)),
    ]
    assert calls["validation"] == (
        validation_model,
        dataset_root.resolve(),
        "test",
        output.parent / "validator",
        "cuda:0",
        2,
    )
    assert calls["efficiency"] == (efficiency_model, "cuda:0")
    assert report["evaluation_identity"] == {
        **_identity(),
        "completed_epoch": 100,
        "split": "test",
        "images": 2,
        "labels": 2,
    }
    assert report["checkpoint"]["ema_state_sha256"] == "E" * 64
    assert report["metrics"]["map"] == pytest.approx(0.31)
    assert len(report["class_details"]) == 10
    assert list(report["scales"]) == list(SCALE_NAMES)
    assert report["efficiency"]["fp16"]["mean_ms"] == 5.1
    assert report["environment"]["gpu"]["name"] == "mock RTX 4090"
    assert report["comparisons"]["comparison_scope"] == "preliminary_cross_run"
    assert report["comparisons"]["strict_paired"] is False
    inventory = report["artifact_sha256_inventory"]
    assert inventory["scope"] == "all_immutable_evaluation_inputs"
    assert inventory["artifacts"]["checkpoint"]["sha256"] == _sha(checkpoint)
    assert inventory["artifacts"]["epoch_records"]["sha256"] == _sha(epochs)
    assert inventory["artifacts"]["publication_queue"]["sha256"] == _sha(queue)
    assert inventory["artifacts"]["publication_ledger"]["sha256"] == _sha(ledger)
    assert inventory["artifacts"]["fdr_evaluation"]["sha256"] == _sha(fdr)
    assert inventory["artifacts"]["acr-bpdd-epochs.csv"]["sha256"] == _sha(
        run / "acr-bpdd-epochs.csv"
    )
    assert inventory["artifacts"]["optimizer-evidence.jsonl"]["sha256"] == _sha(
        run / "optimizer-evidence.jsonl"
    )
    assert inventory["artifacts"]["optimizer-evidence.jsonl"] == {
        "path": str((run / "optimizer-evidence.jsonl").resolve()),
        "bytes": (run / "optimizer-evidence.jsonl").stat().st_size,
        "sha256": _sha(run / "optimizer-evidence.jsonl"),
        "declared_first_epoch": 1,
        "declared_last_epoch": 100,
        "declared_epoch_count": 100,
    }
    assert inventory["tensor_states"] == {
        "checkpoint_ema_or_model": {
            "source_field": "ema",
            "sha256": "E" * 64,
        }
    }
    assert inventory["dataset_split"]["images"]["count"] == 2
    assert inventory["dataset_split"]["labels"]["count"] == 2
    assert json.loads(output.read_text("utf-8")) == report

    before = dict(calls)
    with pytest.raises(FileExistsError):
        formal.evaluate_formal_checkpoint(
            run_dir=run,
            checkpoint=checkpoint,
            publication_ledger=ledger,
            dataset_root=dataset_root,
            split="test",
            output=output,
            checkpoint_loader=loader,
            validation_runner=validate,
            efficiency_runner=efficiency,
            environment_reader=lambda _device: {},
        )
    assert calls == before

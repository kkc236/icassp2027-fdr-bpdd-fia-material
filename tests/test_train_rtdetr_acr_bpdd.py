from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import pytest
import torch

from scripts import train_rtdetr_fdr as fdr_cli


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "train_rtdetr_acr_bpdd.py"
INITIAL_STATE_SHA256 = (
    "51AAB2EB3FB7D123501C69C7B8DC90FF3EA0B9344A108EDEEF2C7D6DCDBB742D"
)


def _load_module():
    assert SCRIPT.is_file(), "ACR-BPDD training CLI has not been implemented"
    spec = importlib.util.spec_from_file_location("train_rtdetr_acr_bpdd", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _args(tmp_path: Path, **changes):
    values = {
        "protocol_manifest": tmp_path / "protocol.json",
        "initial_state": tmp_path / "initial-state.pt",
        "dataset_root": tmp_path / "VisDrone",
        "output_root": tmp_path / "runs",
        "publication_queue": None,
        "resume": None,
        "name": None,
        "dry_run": False,
    }
    values.update(changes)
    return SimpleNamespace(**values)


def _source() -> dict[str, str]:
    return {"git_commit": "a" * 40, "tree_sha256": "A" * 64}


def _rehash(module, manifest: dict) -> dict:
    payload = deepcopy(manifest)
    payload.pop("manifest_sha256", None)
    manifest["manifest_sha256"] = module.public_state_sha256(payload)
    return manifest


def _manifest(module, state: Path) -> dict:
    source = _source()
    identity = module.build_run_identity(
        source, stage="formal", variant="fdr_acr_bpdd", seed=0
    )
    return _rehash(
        module,
        {
            "format_version": 1,
            "source": source,
            "source_sha256": module.public_state_sha256(source),
            "protocol": module.ACR_BPDD_PROTOCOL,
            "protocol_sha256": module.ACR_BPDD_PROTOCOL_SHA256,
            "initial_state": {
                "path": str(state.resolve()),
                "sha256": INITIAL_STATE_SHA256,
            },
            "run_identities": {"fdr_acr_bpdd_formal": identity},
        },
    )


def _write_manifest(module, path: Path, manifest: dict) -> None:
    path.write_bytes(module.canonical_json_bytes(manifest) + b"\n")


def _fake_trainer(run: Path, *, epoch: int = 0):
    model = SimpleNamespace(
        last_fdr_losses={
            "loss_fgl": torch.tensor(0.15),
            "loss_fgl_aux": torch.tensor(0.05),
            "loss_bbox_pre": torch.tensor(0.25),
            "loss_giou_pre": torch.tensor(0.35),
            "loss_bpdd": torch.tensor(0.45),
        },
        last_bpdd_statistics={
            "active_edge_ratio": torch.tensor(0.25),
            "mean_reliability": torch.tensor(0.75),
            "mean_teacher_improvement": torch.tensor(0.125),
            "mixture_beats_final_ratio": torch.tensor(0.50),
            "mean_mixture_advantage_over_final": torch.tensor(0.025),
            "denominator": torch.tensor(4.0),
            "reliability_mass": torch.tensor(3.0),
            "normalization_gain": torch.tensor(2.0),
        },
        last_acr_replay_max_abs_diff=5.0e-7,
    )
    return SimpleNamespace(
        epoch=epoch,
        save_dir=run,
        model=model,
        tloss=torch.tensor([1.0, 2.0, 3.0]),
        metrics={
            "metrics/precision(B)": 0.10,
            "metrics/recall(B)": 0.20,
            "metrics/mAP50(B)": 0.30,
            "metrics/mAP50-95(B)": 0.40,
        },
        validator=SimpleNamespace(
            metrics=SimpleNamespace(box=SimpleNamespace(map75=0.25))
        ),
        last_gradient_norms={
            "gradient_norm": 4.0,
            "fdr_gradient_norm": 5.0,
            "gradients_finite": True,
        },
    )


def test_cli_is_formal100_seed0_single_arm_only() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    for allowed in (
        "--protocol-manifest",
        "--initial-state",
        "--dataset-root",
        "--output-root",
        "--publication-queue",
        "--resume",
        "--name",
        "--dry-run",
    ):
        assert allowed in result.stdout
    for forbidden in (
        "--variant",
        "--stage",
        "--epochs",
        "--seed",
        "--batch",
        "--workers",
        "--imgsz",
        "--optimizer",
        "--bpdd-weight",
        "--normalization",
        "--reliability-floor",
    ):
        assert forbidden not in result.stdout


def test_settings_exactly_reuse_fdr_authority_and_acr_model(tmp_path: Path) -> None:
    module = _load_module()
    args = _args(tmp_path)
    data_yaml = tmp_path / "formal-data.yaml"
    settings = module.build_settings(args, data_yaml)
    expected = {
        **fdr_cli.FROZEN_SETTINGS,
        "model": str(module.ACR_BPDD_MODEL_CFG.resolve()),
        "data": str(data_yaml.resolve()),
        "epochs": 100,
        "seed": 0,
        "project": str(args.output_root.resolve()),
        "name": "formal-seed0-fdr_acr_bpdd-v1",
        "exist_ok": False,
    }
    assert settings == expected


def test_factory_constructs_only_acr_trainer(tmp_path: Path, monkeypatch) -> None:
    module = _load_module()
    calls: list[dict] = []

    class Trainer:
        def __init__(self, **kwargs):
            calls.append(kwargs)

    monkeypatch.setattr(module, "_load_trainer_type", lambda: Trainer)
    state = tmp_path / "initial-state.pt"
    settings = {"epochs": 100}
    module.create_trainer(settings, state)
    assert calls == [
        {
            "overrides": settings,
            "initial_state_path": state.resolve(),
            "experiment_seed": 0,
        }
    ]


def test_manifest_and_checked_out_source_drift_fail_closed(tmp_path: Path, monkeypatch) -> None:
    module = _load_module()
    state = tmp_path / "initial-state.pt"
    manifest = _manifest(module, state)
    path = tmp_path / "protocol.json"
    _write_manifest(module, path, manifest)
    assert module.load_authority(path) == manifest

    changed = deepcopy(manifest)
    changed["protocol"]["acr_bpdd"]["weight"] = 99.0
    _rehash(module, changed)
    _write_manifest(module, path, changed)
    with pytest.raises(ValueError, match="protocol"):
        module.load_authority(path)

    monkeypatch.setattr(module, "current_source_identity", lambda _root=module.ROOT: _source())
    assert module.validate_source_authority(manifest) == _source()
    monkeypatch.setattr(
        module,
        "current_source_identity",
        lambda _root=module.ROOT: {**_source(), "tree_sha256": "B" * 64},
    )
    with pytest.raises(ValueError, match="ACR-BPDD authority"):
        module.validate_source_authority(manifest)


def test_resume_requires_same_formal_identity_flags_queue_and_hash(tmp_path: Path) -> None:
    module = _load_module()
    identity = module.build_run_identity(
        _source(), stage="formal", variant="fdr_acr_bpdd", seed=0
    )
    run = tmp_path / "run"
    weights = run / "weights"
    weights.mkdir(parents=True)
    checkpoint = weights / "epoch9.pt"
    checkpoint.write_bytes(b"epoch-nine")
    queue = run / "publication-queue.jsonl"
    queue.write_text(
        json.dumps(
            {
                "run_id": identity["run_id"],
                "completed_epoch": 10,
                "checkpoint": str(checkpoint.resolve()),
                "checkpoint_sha256": hashlib.sha256(b"epoch-nine").hexdigest().upper(),
            }
        )
        + "\n",
        encoding="utf-8",
    )
    runtime = {
        "run_identity": identity,
        "comparison": {
            "evidence_level": "preliminary_cross_run",
            "strict_paired": False,
        },
        "publication_queue": str(queue.resolve()),
    }
    (run / "acr-bpdd-run.json").write_text(json.dumps(runtime), encoding="utf-8")
    assert module.validate_resume_checkpoint(checkpoint, identity) == checkpoint.resolve()

    runtime["comparison"]["strict_paired"] = True
    (run / "acr-bpdd-run.json").write_text(json.dumps(runtime), encoding="utf-8")
    with pytest.raises(ValueError, match="strict_paired"):
        module.validate_resume_checkpoint(checkpoint, identity)


def test_epoch_evidence_schema_and_append_are_immutable(tmp_path: Path) -> None:
    module = _load_module()
    run = tmp_path / "run"
    trainer = _fake_trainer(run)
    context = {"run_identity": {"run_id": "acr-formal"}}
    first = module.write_epoch_evidence(trainer, context)
    assert module.write_epoch_evidence(trainer, context) == first
    required = {
        "loss_bpdd",
        "bpdd_denominator",
        "bpdd_reliability_mass",
        "bpdd_normalization_gain",
        "acr_replay_max_abs_diff",
        "gradient_norm",
        "fdr_gradient_norm",
        "gradients_finite",
    }
    assert required <= first.keys()
    assert first["variant"] == "fdr_acr_bpdd"
    assert first["stage"] == "formal"
    assert first["bpdd_denominator"] == pytest.approx(4.0)
    assert first["bpdd_reliability_mass"] == pytest.approx(3.0)
    assert first["bpdd_normalization_gain"] == pytest.approx(2.0)
    assert first["acr_replay_max_abs_diff"] == pytest.approx(5.0e-7)
    assert first["gradients_finite"] is True

    trainer.model.last_acr_replay_max_abs_diff = 9.0e-7
    with pytest.raises(ValueError, match="changed ACR-BPDD evidence"):
        module.write_epoch_evidence(trainer, context)

    with (run / "acr-bpdd-epochs.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 1
    assert required <= rows[0].keys()


def test_publication_queue_binds_exact_epoch_checkpoint_and_artifacts(tmp_path: Path) -> None:
    module = _load_module()
    run = tmp_path / "run"
    trainer = _fake_trainer(run)
    weights = run / "weights"
    weights.mkdir(parents=True)
    checkpoint = weights / "epoch0.pt"
    checkpoint.write_bytes(b"epoch-zero")
    (run / "acr-bpdd-epochs.jsonl").write_text("{}\n", encoding="utf-8")
    (run / "acr-bpdd-epochs.csv").write_text("completed_epoch\n", encoding="utf-8")
    (run / "acr-bpdd-run.json").write_text("{}", encoding="utf-8")
    context = {
        "run_identity": {"run_id": "acr-formal"},
        "publication_queue": None,
    }
    record = module.queue_epoch_publication(trainer, context)
    assert module.queue_epoch_publication(trainer, context) == record
    assert record["variant"] == "fdr_acr_bpdd"
    assert record["stage"] == "formal"
    assert record["completed_epoch"] == 1
    assert record["checkpoint"] == str(checkpoint.resolve())
    assert record["checkpoint_sha256"] == hashlib.sha256(b"epoch-zero").hexdigest().upper()
    assert {Path(path).name for path in record["artifacts"]} == {
        "acr-bpdd-epochs.jsonl",
        "acr-bpdd-epochs.csv",
        "acr-bpdd-run.json",
        "optimizer-evidence.jsonl",
    }


def test_runtime_manifest_marks_preliminary_cross_run_and_is_create_only(tmp_path: Path) -> None:
    module = _load_module()
    args = _args(tmp_path)
    trainer = SimpleNamespace(save_dir=tmp_path / "run")
    manifest = _manifest(module, args.initial_state)
    identity = manifest["run_identities"]["fdr_acr_bpdd_formal"]
    data_yaml = tmp_path / "formal-data.yaml"
    module._runtime_manifest(
        trainer,
        args=args,
        manifest=manifest,
        run_identity=identity,
        data_yaml=data_yaml,
    )
    runtime_path = trainer.save_dir / "acr-bpdd-run.json"
    payload = json.loads(runtime_path.read_text(encoding="utf-8"))
    assert payload["comparison"] == {
        "evidence_level": "preliminary_cross_run",
        "strict_paired": False,
    }
    module._runtime_manifest(
        trainer,
        args=args,
        manifest=manifest,
        run_identity=identity,
        data_yaml=data_yaml,
    )
    payload["comparison"]["strict_paired"] = True
    runtime_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="changed ACR-BPDD run authority"):
        module._runtime_manifest(
            trainer,
            args=args,
            manifest=manifest,
            run_identity=identity,
            data_yaml=data_yaml,
        )


def test_dry_run_builds_no_model_and_writes_no_run_directory(tmp_path: Path, monkeypatch) -> None:
    module = _load_module()
    args = _args(tmp_path, dry_run=True)
    manifest = _manifest(module, args.initial_state)
    monkeypatch.setattr(module, "load_authority", lambda _path: manifest)
    monkeypatch.setattr(module, "validate_source_authority", lambda _manifest: _source())
    monkeypatch.setattr(
        module,
        "validate_initial_state_file",
        lambda _path, _manifest: {"status": "valid"},
    )
    monkeypatch.setattr(
        module,
        "create_trainer",
        lambda *_args, **_kwargs: pytest.fail("dry-run constructed a model"),
    )
    monkeypatch.setattr(
        module,
        "prepare_data_yaml",
        lambda *_args, **_kwargs: pytest.fail("dry-run wrote dataset authority"),
    )

    summary = module.execute(args)
    assert summary["status"] == "dry-run-passed"
    assert summary["variant"] == "fdr_acr_bpdd"
    assert summary["stage"] == "formal"
    assert not args.output_root.exists()

from __future__ import annotations

import importlib.util
import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_acr_bpdd_cuda_preflight.py"
STATE_SHA256 = "51AAB2EB3FB7D123501C69C7B8DC90FF3EA0B9344A108EDEEF2C7D6DCDBB742D"
DATASET_SHA256 = "FD92E9FF4B3B58FCDD5A32F7E770FC3398E566B627DB0E188CB5FF9F3B7BBDAB"


def _load_module():
    assert SCRIPT.is_file(), "ACR-BPDD CUDA preflight CLI is missing"
    spec = importlib.util.spec_from_file_location("run_acr_bpdd_cuda_preflight", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _source() -> dict[str, str]:
    return {"git_commit": "a" * 40, "tree_sha256": "B" * 64}


def _manifest(module, state: Path) -> dict:
    source = _source()
    identity = module.build_run_identity(
        source, stage="formal", variant="fdr_acr_bpdd", seed=0
    )
    manifest = {
        "format_version": 1,
        "source": source,
        "source_sha256": module.public_state_sha256(source),
        "protocol": module.ACR_BPDD_PROTOCOL,
        "protocol_sha256": module.ACR_BPDD_PROTOCOL_SHA256,
        "initial_state": {
            "path": str(state.resolve()),
            "sha256": STATE_SHA256,
        },
        "run_identities": {"fdr_acr_bpdd_formal": identity},
    }
    manifest["manifest_sha256"] = module.public_state_sha256(manifest)
    return manifest


def _measurements() -> dict:
    return {
        "loss_total": 12.5,
        "loss_bpdd": 0.125,
        "active_edge_ratio": 0.5,
        "reliability_mass": 7.5,
        "replay_max_abs_diff": 0.0,
        "normal_queries": 300,
        "dn_queries": 80,
        "common_parameter_tensors": 100,
        "common_bpdd_gradient_tensors": 0,
        "bbox_parameter_tensors": 36,
        "bbox_bpdd_nonzero_gradient_tensors": 18,
        "amp_scale_before": 128.0,
        "amp_scale_after_first_step": 128.0,
        "amp_scale_after_resume_step": 128.0,
        "first_parameter_update_max_abs": 1.0e-4,
        "resume_parameter_update_max_abs": 1.0e-4,
        "optimizer_state_reload_exact": True,
        "scaler_state_reload_exact": True,
        "state_reload_exact": True,
        "eval_output_max_abs_diff": 0.0,
    }


def _checks() -> dict[str, bool]:
    return {
        "real_visdrone_batch8": True,
        "loss_bpdd_positive": True,
        "active_edge_ratio_positive": True,
        "reliability_mass_positive": True,
        "common_bpdd_grads_none": True,
        "bbox_bpdd_grad_nonzero": True,
        "bbox_bpdd_grads_finite": True,
        "total_grads_finite": True,
        "replay_max_diff_le_1e_6": True,
        "normal_queries_300": True,
        "dn_nonempty": True,
        "forward": True,
        "backward": True,
        "musgd_step": True,
        "checkpoint_saved": True,
        "strict_state_reload": True,
        "eval_output_exact": True,
        "optimizer_scaler_reload": True,
        "resume_step": True,
    }


def _evidence(module, tmp_path: Path) -> dict:
    import torch

    checkpoint = tmp_path / "acr-bpdd-preflight.pt"
    torch.save(
        {
            "model": {"weight": torch.ones(1)},
            "optimizer": {"state": {}, "param_groups": [{"params": [0]}]},
            "scaler": {"scale": 128.0},
        },
        checkpoint,
    )
    optimizer_evidence = tmp_path / "optimizer-evidence.jsonl"
    optimizer_evidence.write_text(
        '{"optimizer_attempt":1}\n{"optimizer_attempt":2}\n',
        encoding="utf-8",
    )
    return {
        "source": _source(),
        "protocol_sha256": module.ACR_BPDD_PROTOCOL_SHA256,
        "initial_state": {
            "path": str((tmp_path / "initial-state.pt").resolve()),
            "sha256": STATE_SHA256,
        },
        "dataset": {
            **module.ACR_BPDD_PROTOCOL["dataset"],
            "root": str((tmp_path / "VisDrone").resolve()),
        },
        "environment": dict(module.ACR_BPDD_PROTOCOL["environment"]),
        "runtime": {
            "device": "cuda:0",
            "gpu_name": "NVIDIA GeForce RTX 4090",
            "batch": 8,
            "imgsz": 640,
            "amp": True,
            "amp_scale": 128.0,
            "optimizer": "MuSGD",
            "optimizer_groups": 8,
            "queries": 300,
        },
        "checks": _checks(),
        "measurements": _measurements(),
        "artifacts": {
            "checkpoint": str(checkpoint.resolve()),
            "checkpoint_sha256": module.file_sha256(checkpoint),
            "optimizer_evidence": str(optimizer_evidence.resolve()),
            "optimizer_evidence_sha256": module.file_sha256(optimizer_evidence),
        },
    }


def _write_authorities(module, tmp_path: Path) -> tuple[Path, Path, Path, dict]:
    state = tmp_path / "initial-state.pt"
    state.write_bytes(b"state")
    dataset = tmp_path / "VisDrone"
    dataset.mkdir()
    manifest = _manifest(module, state)
    manifest_path = tmp_path / "protocol.json"
    manifest_path.write_bytes(module.canonical_json_bytes(manifest) + b"\n")
    return manifest_path, state, dataset, manifest


def test_build_passed_report_is_self_hashed_and_create_only(tmp_path: Path) -> None:
    module = _load_module()
    _manifest_path, _state, _dataset, manifest = _write_authorities(module, tmp_path)
    report = module.build_passed_report(_evidence(module, tmp_path), manifest=manifest)
    output = tmp_path / "preflight.json"

    module.write_create_only_report(output, report)

    assert report["format_version"] == 1
    assert report["status"] == "passed"
    unhashed = {key: value for key, value in report.items() if key != "report_sha256"}
    assert report["report_sha256"] == module.public_state_sha256(unhashed)
    assert output.read_bytes() == module.canonical_json_bytes(report) + b"\n"
    with pytest.raises(FileExistsError):
        module.write_create_only_report(output, report)


def test_validator_accepts_only_complete_passing_authority(tmp_path: Path) -> None:
    module = _load_module()
    _manifest_path, state, dataset, manifest = _write_authorities(module, tmp_path)
    report = module.build_passed_report(_evidence(module, tmp_path), manifest=manifest)
    output = tmp_path / "preflight.json"
    module.write_create_only_report(output, report)

    accepted = module.validate_preflight_report(
        output,
        manifest=manifest,
        source=_source(),
        initial_state=state,
        dataset_root=dataset,
        file_hasher=lambda path: STATE_SHA256 if path == state.resolve() else module.file_sha256(path),
    )

    assert accepted == report


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda report: report.update(status="engineering_failed"), "status"),
        (lambda report: report["source"].update(tree_sha256="C" * 64), "source"),
        (lambda report: report.update(protocol_sha256="D" * 64), "protocol"),
        (lambda report: report["initial_state"].update(sha256="E" * 64), "initial-state"),
        (lambda report: report["dataset"].update(sha256="F" * 64), "dataset"),
        (lambda report: report["environment"].update(torch="9.9.9"), "environment"),
        (lambda report: report["runtime"].update(gpu_name="NVIDIA A100"), "RTX 4090"),
        (lambda report: report["runtime"].update(batch=4), "batch8"),
        (lambda report: report["runtime"].update(imgsz=512), "imgsz640"),
        (lambda report: report["runtime"].update(device="cuda:1"), "cuda:0"),
        (lambda report: report["runtime"].update(amp_scale=64.0), "AMP128"),
        (lambda report: report["runtime"].update(optimizer="AdamW"), "MuSGD"),
        (lambda report: report["runtime"].update(optimizer_groups=0), "optimizer groups"),
        (lambda report: report["checks"].update(dn_nonempty=False), "check"),
        (lambda report: report["measurements"].update(replay_max_abs_diff=2e-6), "replay"),
        (lambda report: report["measurements"].update(active_edge_ratio=0.0), "active-edge"),
        (lambda report: report["measurements"].update(reliability_mass=0.0), "reliability mass"),
        (lambda report: report["measurements"].update(common_bpdd_gradient_tensors=1), "shared gradient"),
        (lambda report: report["measurements"].update(common_parameter_tensors=0), "common parameter"),
        (lambda report: report["measurements"].update(bbox_bpdd_nonzero_gradient_tensors=0), "box-head gradient"),
        (lambda report: report["measurements"].update(normal_queries=299), "normal Query"),
        (lambda report: report["measurements"].update(dn_queries=0), "DN Query"),
        (lambda report: report["measurements"].update(amp_scale_after_resume_step=64.0), "AMP"),
        (lambda report: report["measurements"].update(first_parameter_update_max_abs=0.0), "MuSGD"),
        (lambda report: report["measurements"].update(optimizer_state_reload_exact=False), "optimizer state"),
        (lambda report: report["measurements"].update(eval_output_max_abs_diff=1e-6), "eval output"),
    ],
)
def test_validator_rejects_tamper_authority_drift_and_false_checks(
    tmp_path: Path, mutate, message: str
) -> None:
    module = _load_module()
    _manifest_path, state, dataset, manifest = _write_authorities(module, tmp_path)
    report = module.build_passed_report(_evidence(module, tmp_path), manifest=manifest)
    mutate(report)
    # Re-hash to prove semantic validation cannot be bypassed by recomputing the hash.
    report["report_sha256"] = module.public_state_sha256(
        {key: value for key, value in report.items() if key != "report_sha256"}
    )
    output = tmp_path / "preflight.json"
    module.write_create_only_report(output, report)

    with pytest.raises(ValueError, match=message):
        module.validate_preflight_report(
            output,
            manifest=manifest,
            source=_source(),
            initial_state=state,
            dataset_root=dataset,
            file_hasher=lambda path: STATE_SHA256 if path == state.resolve() else module.file_sha256(path),
        )


def test_validator_rejects_hash_tamper_and_symlink(tmp_path: Path) -> None:
    module = _load_module()
    _manifest_path, state, dataset, manifest = _write_authorities(module, tmp_path)
    report = module.build_passed_report(_evidence(module, tmp_path), manifest=manifest)
    report["measurements"]["loss_bpdd"] = 99.0
    output = tmp_path / "tampered.json"
    output.write_bytes(module.canonical_json_bytes(report) + b"\n")
    with pytest.raises(ValueError, match="self-hash"):
        module.validate_preflight_report(
            output,
            manifest=manifest,
            source=_source(),
            initial_state=state,
            dataset_root=dataset,
        )

    target = tmp_path / "target.json"
    target.write_bytes(module.canonical_json_bytes(report) + b"\n")
    link = tmp_path / "link.json"
    try:
        link.symlink_to(target)
    except OSError as error:
        pytest.skip(f"symlink creation unavailable: {error}")
    with pytest.raises(ValueError, match="symlink"):
        module.validate_preflight_report(
            link,
            manifest=manifest,
            source=_source(),
            initial_state=state,
            dataset_root=dataset,
        )


def test_execute_writes_no_passed_report_when_cuda_gate_fails(tmp_path: Path) -> None:
    module = _load_module()
    manifest_path, state, dataset, manifest = _write_authorities(module, tmp_path)
    output = tmp_path / "preflight.json"
    context = module.PreflightContext(
        protocol_manifest=manifest_path,
        initial_state=state,
        dataset_root=dataset,
        output=output,
        repository_root=ROOT,
    )

    def fail(_context):
        raise RuntimeError("loss_bpdd was zero")

    with pytest.raises(RuntimeError, match="loss_bpdd"):
        module.execute_preflight(
            context,
            cuda_runner=fail,
            manifest_loader=lambda _path: manifest,
            source_loader=lambda _root: _source(),
            state_hasher=lambda _path: STATE_SHA256,
            dataset_loader=lambda _root: dict(module.ACR_BPDD_PROTOCOL["dataset"]),
        )
    assert not output.exists()


def test_execute_rejects_artifact_path_collision_before_cuda(tmp_path: Path) -> None:
    module = _load_module()
    manifest_path, state, dataset, manifest = _write_authorities(module, tmp_path)
    output = state.with_suffix(".json")
    original = state.read_bytes()
    context = module.PreflightContext(
        protocol_manifest=manifest_path,
        initial_state=state,
        dataset_root=dataset,
        output=output,
        repository_root=ROOT,
    )

    with pytest.raises(ValueError, match="initial-state"):
        module.execute_preflight(
            context,
            cuda_runner=lambda _context: pytest.fail("path collision reached CUDA"),
            manifest_loader=lambda _path: manifest,
            source_loader=lambda _root: _source(),
            state_hasher=lambda _path: STATE_SHA256,
            dataset_loader=lambda _root: dict(module.ACR_BPDD_PROTOCOL["dataset"]),
        )
    assert state.read_bytes() == original
    assert not output.exists()


def test_execute_rejects_foreign_repository_root_before_cuda(tmp_path: Path) -> None:
    module = _load_module()
    manifest_path, state, dataset, manifest = _write_authorities(module, tmp_path)
    context = module.PreflightContext(
        protocol_manifest=manifest_path,
        initial_state=state,
        dataset_root=dataset,
        output=tmp_path / "preflight.json",
        repository_root=tmp_path,
    )

    with pytest.raises(ValueError, match="repository root"):
        module.execute_preflight(
            context,
            cuda_runner=lambda _context: pytest.fail("foreign source reached CUDA"),
            manifest_loader=lambda _path: manifest,
            source_loader=lambda _root: _source(),
            state_hasher=lambda _path: STATE_SHA256,
            dataset_loader=lambda _root: dict(module.ACR_BPDD_PROTOCOL["dataset"]),
        )


def test_execute_detects_initial_state_mutation_during_cuda_gate(tmp_path: Path) -> None:
    module = _load_module()
    manifest_path, state, dataset, manifest = _write_authorities(module, tmp_path)
    output = tmp_path / "preflight.json"
    context = module.PreflightContext(
        protocol_manifest=manifest_path,
        initial_state=state,
        dataset_root=dataset,
        output=output,
        repository_root=ROOT,
    )

    def mutate(_context):
        state.write_bytes(b"mutated")
        return _evidence(module, tmp_path)

    def state_hasher(path: Path) -> str:
        return STATE_SHA256 if path.read_bytes() == b"state" else "0" * 64

    with pytest.raises(ValueError, match="changed during preflight"):
        module.execute_preflight(
            context,
            cuda_runner=mutate,
            manifest_loader=lambda _path: manifest,
            source_loader=lambda _root: _source(),
            state_hasher=state_hasher,
            dataset_loader=lambda _root: dict(module.ACR_BPDD_PROTOCOL["dataset"]),
        )
    assert not output.exists()


def test_validator_rejects_missing_or_changed_checkpoint_artifact(tmp_path: Path) -> None:
    module = _load_module()
    _manifest_path, state, dataset, manifest = _write_authorities(module, tmp_path)
    report = module.build_passed_report(_evidence(module, tmp_path), manifest=manifest)
    output = tmp_path / "preflight.json"
    module.write_create_only_report(output, report)
    checkpoint = Path(report["artifacts"]["checkpoint"])
    checkpoint.write_bytes(b"changed")

    with pytest.raises(ValueError, match="checkpoint SHA256"):
        module.validate_preflight_report(
            output,
            manifest=manifest,
            source=_source(),
            initial_state=state,
            dataset_root=dataset,
            file_hasher=lambda path: (
                STATE_SHA256 if path == state.resolve() else module.file_sha256(path)
            ),
        )


def test_validator_rejects_hashed_non_checkpoint_payload(tmp_path: Path) -> None:
    module = _load_module()
    _manifest_path, state, dataset, manifest = _write_authorities(module, tmp_path)
    evidence = _evidence(module, tmp_path)
    checkpoint = Path(evidence["artifacts"]["checkpoint"])
    checkpoint.write_text("not a torch checkpoint", encoding="utf-8")
    evidence["artifacts"]["checkpoint_sha256"] = module.file_sha256(checkpoint)
    report = module.build_passed_report(evidence, manifest=manifest)
    output = tmp_path / "preflight.json"
    module.write_create_only_report(output, report)

    with pytest.raises(ValueError, match="checkpoint is unreadable"):
        module.validate_preflight_report(
            output,
            manifest=manifest,
            source=_source(),
            initial_state=state,
            dataset_root=dataset,
            file_hasher=lambda path: (
                STATE_SHA256 if path == state.resolve() else module.file_sha256(path)
            ),
        )


def test_execute_injected_cuda_runner_produces_valid_report(tmp_path: Path) -> None:
    module = _load_module()
    manifest_path, state, dataset, manifest = _write_authorities(module, tmp_path)
    output = tmp_path / "preflight.json"
    evidence = _evidence(module, tmp_path)
    context = module.PreflightContext(
        protocol_manifest=manifest_path,
        initial_state=state,
        dataset_root=dataset,
        output=output,
        repository_root=ROOT,
    )

    report = module.execute_preflight(
        context,
        cuda_runner=lambda _context: deepcopy(evidence),
        manifest_loader=lambda _path: manifest,
        source_loader=lambda _root: _source(),
        state_hasher=lambda _path: STATE_SHA256,
        dataset_loader=lambda _root: dict(module.ACR_BPDD_PROTOCOL["dataset"]),
    )

    assert report["status"] == "passed"
    assert json.loads(output.read_text("utf-8")) == report


def test_launch_environment_is_rechecked_from_current_process(tmp_path: Path) -> None:
    module = _load_module()
    expected = dict(module.ACR_BPDD_PROTOCOL["environment"])
    report = {"environment": expected, "runtime": {"gpu_name": expected["gpu"]}}

    assert module.validate_launch_environment(
        report, environment_loader=lambda: dict(expected)
    ) == expected
    drifted = dict(expected)
    drifted["torch"] = "9.9.9"
    with pytest.raises(ValueError, match="current launch environment"):
        module.validate_launch_environment(report, environment_loader=lambda: drifted)


def test_formal_musgd_builder_includes_conv_and_linear_weights() -> None:
    module = _load_module()
    import torch

    model = torch.nn.Sequential(
        torch.nn.Conv2d(3, 4, 3),
        torch.nn.Flatten(),
        torch.nn.Linear(4 * 6 * 6, 2),
    )
    optimizer = module._formal_musgd(model)
    muon_ids = {
        id(parameter)
        for group in optimizer.param_groups
        if group.get("use_muon") is True
        for parameter in group["params"]
    }

    assert id(model[0].weight) in muon_ids
    assert id(model[2].weight) in muon_ids
    assert id(model[0].bias) not in muon_ids


def test_gradient_summary_requires_live_finite_private_gradient() -> None:
    module = _load_module()
    import torch

    live = torch.tensor([0.5])
    zero = torch.tensor([0.0])
    summary = module.summarize_gradients([live, None, zero])
    assert summary == {
        "gradient_tensors": 2,
        "none_tensors": 1,
        "finite": True,
        "nonzero_tensors": 1,
    }


def test_dataset_authority_recomputes_frozen_sha256(tmp_path: Path, monkeypatch) -> None:
    module = _load_module()
    root = tmp_path / "VisDrone"
    (root / "images" / "train").mkdir(parents=True)
    (root / "images" / "val").mkdir(parents=True)
    protocol = deepcopy(module.ACR_BPDD_PROTOCOL)
    protocol["dataset"]["train_images"] = 0
    protocol["dataset"]["val_images"] = 0
    monkeypatch.setattr(module, "ACR_BPDD_PROTOCOL", protocol)
    monkeypatch.setattr(
        module,
        "dataset_signature",
        lambda _root: {"sha256": DATASET_SHA256},
    )

    assert module._dataset_authority(root)["sha256"] == DATASET_SHA256

    monkeypatch.setattr(
        module,
        "dataset_signature",
        lambda _root: {"sha256": "0" * 64},
    )
    with pytest.raises(RuntimeError, match="SHA256"):
        module._dataset_authority(root)

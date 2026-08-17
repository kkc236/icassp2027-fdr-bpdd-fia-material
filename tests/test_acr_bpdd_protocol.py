from __future__ import annotations

import importlib.util
import sys
from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from src.fdr_protocol import FDR_PROTOCOL, FDR_PROTOCOL_SHA256
from src.acr_bpdd_protocol import (
    ACR_BPDD_PROTOCOL,
    ACR_BPDD_PROTOCOL_SHA256,
    FDR_INITIAL_STATE_SHA256,
    build_run_identity,
    canonical_json_bytes,
    public_state_sha256,
    validate_manifest,
    validate_resume_authority,
)


ROOT = Path(__file__).resolve().parents[1]
OLD_YAML = ROOT / "configs" / "rtdetr-l-fdr-bpdd.yaml"
NEW_YAML = ROOT / "configs" / "rtdetr-l-fdr-acr-bpdd.yaml"
PREPARE_SCRIPT = ROOT / "scripts" / "prepare_acr_bpdd_protocol.py"
EXPECTED_FDR_SOURCE_COMMIT = "d97e1eb7f98414752a1c1f38287697db3f2a0679"
EXPECTED_INITIAL_STATE_SHA256 = (
    "51AAB2EB3FB7D123501C69C7B8DC90FF3EA0B9344A108EDEEF2C7D6DCDBB742D"
)


def _source() -> dict[str, str]:
    return {"git_commit": "a" * 40, "tree_sha256": "B" * 64}


def _fingerprints() -> dict[str, str]:
    return {
        "public": "1" * 64,
        "fdr_public": "2" * 64,
        "replaced_control": "3" * 64,
        "private": "4" * 64,
        "control": "5" * 64,
        "fdr": "6" * 64,
    }


def _load_prepare_module():
    assert PREPARE_SCRIPT.is_file(), "ACR-BPDD protocol preparer is missing"
    spec = importlib.util.spec_from_file_location(
        "prepare_acr_bpdd_protocol", PREPARE_SCRIPT
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_acr_yaml_is_an_independent_exact_graph_copy_with_only_bpdd_controls_changed() -> None:
    old = yaml.safe_load(OLD_YAML.read_text(encoding="utf-8"))
    new = yaml.safe_load(NEW_YAML.read_text(encoding="utf-8"))

    old_graph = {key: value for key, value in old.items() if key != "bpdd_loss"}
    new_graph = {key: value for key, value in new.items() if key != "bpdd_loss"}
    assert new_graph == old_graph
    assert old["bpdd_loss"] == {
        "enabled": True,
        "weight": 0.5,
        "temperature": 0.5,
        "margin": 0.02,
        "eps": 1e-6,
        "matched_layer": "final",
        "include_dn": False,
    }
    assert new["bpdd_loss"] == {
        **old["bpdd_loss"],
        "normalization": "reliability_mass",
        "reliability_floor": 0.5,
        "common_gradient_firewall": True,
    }


def test_protocol_inherits_every_frozen_fdr_training_authority() -> None:
    assert ACR_BPDD_PROTOCOL["fdr_authority"] == {
        "protocol_sha256": FDR_PROTOCOL_SHA256,
        "source_commit": EXPECTED_FDR_SOURCE_COMMIT,
        "initial_state_sha256": EXPECTED_INITIAL_STATE_SHA256,
    }
    for key in ("environment", "dataset", "training", "augmentation"):
        assert ACR_BPDD_PROTOCOL[key] == FDR_PROTOCOL[key]
        assert ACR_BPDD_PROTOCOL[key] is not FDR_PROTOCOL[key]
    assert ACR_BPDD_PROTOCOL_SHA256 == public_state_sha256(ACR_BPDD_PROTOCOL)
    assert ACR_BPDD_PROTOCOL_SHA256 != FDR_PROTOCOL_SHA256


def test_protocol_exposes_only_the_fresh_formal100_seed0_acr_arm() -> None:
    assert ACR_BPDD_PROTOCOL["acr_bpdd"] == {
        "weight": 0.5,
        "temperature": 0.5,
        "margin": 0.02,
        "eps": 1e-6,
        "matched_layer": "final",
        "include_dn": False,
        "normalization": "reliability_mass",
        "reliability_floor": 0.5,
        "common_gradient_firewall": True,
    }
    assert ACR_BPDD_PROTOCOL["variants"] == {
        "fdr_acr_bpdd": {
            "model_yaml": "configs/rtdetr-l-fdr-acr-bpdd.yaml",
            "fdr_enabled": True,
            "bpdd_enabled": True,
            "acr_enabled": True,
        }
    }
    assert ACR_BPDD_PROTOCOL["seed"] == 0
    assert ACR_BPDD_PROTOCOL["stages"] == {
        "formal": {"schedule_epochs": 100, "fresh_start": True}
    }
    assert ACR_BPDD_PROTOCOL["comparison"] == {
        "evidence_level": "preliminary_cross_run",
        "strict_paired": False,
    }


def test_run_identity_binds_source_protocol_state_and_only_authorized_run() -> None:
    identity = build_run_identity(
        _source(), stage="formal", variant="fdr_acr_bpdd", seed=0
    )

    assert identity == {
        "source_sha256": public_state_sha256(_source()),
        "protocol_sha256": ACR_BPDD_PROTOCOL_SHA256,
        "fdr_protocol_sha256": FDR_PROTOCOL_SHA256,
        "initial_state_sha256": EXPECTED_INITIAL_STATE_SHA256,
        "run_id": identity["run_id"],
        "stage": "formal",
        "variant": "fdr_acr_bpdd",
        "seed": 0,
    }
    assert identity["run_id"].startswith("fdr_acr_bpdd-formal-seed0-")


@pytest.mark.parametrize(
    ("stage", "variant", "seed", "message"),
    [
        ("screen", "fdr_acr_bpdd", 0, "stage"),
        ("formal", "fdr_bpdd", 0, "variant"),
        ("formal", "fdr_acr_bpdd", 1, "seed0"),
    ],
)
def test_run_identity_rejects_every_non_authorized_run(
    stage: str, variant: str, seed: int, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        build_run_identity(_source(), stage=stage, variant=variant, seed=seed)


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("source_sha256", "A" * 64),
        ("protocol_sha256", "B" * 64),
        ("fdr_protocol_sha256", "C" * 64),
        ("initial_state_sha256", "D" * 64),
        ("run_id", "foreign-run"),
        ("stage", "screen"),
        ("variant", "fdr_bpdd"),
        ("seed", 1),
    ],
)
def test_resume_rejects_every_authority_drift(field: str, replacement: object) -> None:
    expected = build_run_identity(
        _source(), stage="formal", variant="fdr_acr_bpdd", seed=0
    )
    checkpoint = deepcopy(expected)
    checkpoint[field] = replacement

    with pytest.raises(ValueError, match=field):
        validate_resume_authority(checkpoint, expected)


def test_prepare_manifest_is_create_only_and_self_validating(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_prepare_module()
    state = tmp_path / "initial-state.pt"
    state.write_bytes(b"test-state")
    output = tmp_path / "acr-bpdd-protocol.json"
    monkeypatch.setattr(module, "_file_sha256", lambda _path: EXPECTED_INITIAL_STATE_SHA256)
    monkeypatch.setattr(
        module, "_validate_initial_state", lambda _path: {"fingerprints": _fingerprints()}
    )
    monkeypatch.setattr(module, "current_source_identity", lambda _root: _source())
    monkeypatch.setattr(module, "dirty_source_paths", lambda _root: [])

    manifest = module.prepare_manifest(
        source_commit="a" * 40,
        source_tree_sha256="B" * 64,
        initial_state=state,
        output=output,
        repository_root=tmp_path,
    )

    assert manifest["source"] == _source()
    assert manifest["source_sha256"] == public_state_sha256(_source())
    assert manifest["protocol"] == ACR_BPDD_PROTOCOL
    assert manifest["protocol_sha256"] == ACR_BPDD_PROTOCOL_SHA256
    assert manifest["initial_state"] == {
        "path": str(state.resolve()),
        "sha256": EXPECTED_INITIAL_STATE_SHA256,
        "fingerprints": _fingerprints(),
    }
    assert set(manifest["run_identities"]) == {"fdr_acr_bpdd_formal"}
    assert validate_manifest(manifest, expected_source=_source()) is None
    assert output.read_bytes() == canonical_json_bytes(manifest) + b"\n"

    with pytest.raises(FileExistsError):
        module.prepare_manifest(
            source_commit="a" * 40,
            source_tree_sha256="B" * 64,
            initial_state=state,
            output=output,
            repository_root=tmp_path,
        )


def test_prepare_rejects_dirty_source_before_writing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_prepare_module()
    state = tmp_path / "initial-state.pt"
    state.write_bytes(b"state")
    output = tmp_path / "manifest.json"
    monkeypatch.setattr(module, "dirty_source_paths", lambda _root: ["src/drift.py"])

    with pytest.raises(ValueError, match="dirty"):
        module.prepare_manifest(
            source_commit="a" * 40,
            source_tree_sha256="B" * 64,
            initial_state=state,
            output=output,
            repository_root=tmp_path,
        )
    assert not output.exists()


def test_prepare_rejects_commit_or_tree_source_drift(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_prepare_module()
    state = tmp_path / "initial-state.pt"
    state.write_bytes(b"state")
    monkeypatch.setattr(module, "dirty_source_paths", lambda _root: [])
    monkeypatch.setattr(
        module,
        "current_source_identity",
        lambda _root: {"git_commit": "c" * 40, "tree_sha256": "D" * 64},
    )

    with pytest.raises(ValueError, match="source drift"):
        module.prepare_manifest(
            source_commit="a" * 40,
            source_tree_sha256="B" * 64,
            initial_state=state,
            output=tmp_path / "manifest.json",
            repository_root=tmp_path,
        )


def test_manifest_validation_rejects_public_hash_and_identity_drift(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_prepare_module()
    state = tmp_path / "initial-state.pt"
    state.write_bytes(b"state")
    monkeypatch.setattr(module, "_file_sha256", lambda _path: EXPECTED_INITIAL_STATE_SHA256)
    monkeypatch.setattr(
        module, "_validate_initial_state", lambda _path: {"fingerprints": _fingerprints()}
    )
    monkeypatch.setattr(module, "current_source_identity", lambda _root: _source())
    monkeypatch.setattr(module, "dirty_source_paths", lambda _root: [])
    manifest = module.prepare_manifest(
        source_commit="a" * 40,
        source_tree_sha256="B" * 64,
        initial_state=state,
        output=tmp_path / "manifest.json",
        repository_root=tmp_path,
    )

    source_drift = deepcopy(manifest)
    source_drift["source_sha256"] = "F" * 64
    with pytest.raises(ValueError, match="source_sha256"):
        validate_manifest(source_drift, expected_source=_source())

    identity_drift = deepcopy(manifest)
    identity_drift["run_identities"]["fdr_acr_bpdd_formal"]["run_id"] = "foreign"
    with pytest.raises(ValueError, match="run identity"):
        validate_manifest(identity_drift, expected_source=_source())


def test_prepare_cli_exposes_only_explicit_authority_inputs() -> None:
    module = _load_prepare_module()
    actions = {action.dest for action in module.build_parser()._actions}
    assert actions == {
        "help",
        "source_commit",
        "source_tree_sha256",
        "initial_state",
        "output",
        "repository_root",
    }

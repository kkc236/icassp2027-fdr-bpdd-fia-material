"""Immutable single-arm authority for formal FDR + ACR-BPDD training."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from src.fdr_protocol import (
    FDR_PROTOCOL,
    FDR_PROTOCOL_SHA256,
    canonical_json_bytes,
    public_state_sha256,
    write_create_only_manifest,
)


FDR_SOURCE_COMMIT = "d97e1eb7f98414752a1c1f38287697db3f2a0679"
FDR_INITIAL_STATE_SHA256 = (
    "51AAB2EB3FB7D123501C69C7B8DC90FF3EA0B9344A108EDEEF2C7D6DCDBB742D"
)

ACR_BPDD_PROTOCOL: dict[str, Any] = {
    "design": "ultralytics-rtdetr-l-fdr-acr-bpdd-v1",
    "fdr_authority": {
        "protocol_sha256": FDR_PROTOCOL_SHA256,
        "source_commit": FDR_SOURCE_COMMIT,
        "initial_state_sha256": FDR_INITIAL_STATE_SHA256,
    },
    "environment": deepcopy(FDR_PROTOCOL["environment"]),
    "dataset": deepcopy(FDR_PROTOCOL["dataset"]),
    "training": deepcopy(FDR_PROTOCOL["training"]),
    "augmentation": deepcopy(FDR_PROTOCOL["augmentation"]),
    "acr_bpdd": {
        "weight": 0.5,
        "temperature": 0.5,
        "margin": 0.02,
        "eps": 1e-6,
        "matched_layer": "final",
        "include_dn": False,
        "normalization": "reliability_mass",
        "reliability_floor": 0.5,
        "common_gradient_firewall": True,
    },
    "variants": {
        "fdr_acr_bpdd": {
            "model_yaml": "configs/rtdetr-l-fdr-acr-bpdd.yaml",
            "fdr_enabled": True,
            "bpdd_enabled": True,
            "acr_enabled": True,
        }
    },
    "seed": 0,
    "stages": {
        "formal": {"schedule_epochs": 100, "fresh_start": True},
    },
    "comparison": {
        "evidence_level": "preliminary_cross_run",
        "strict_paired": False,
    },
}
ACR_BPDD_PROTOCOL_SHA256 = public_state_sha256(ACR_BPDD_PROTOCOL)


def build_run_identity(
    source_identity: Mapping[str, Any],
    *,
    stage: str,
    variant: str,
    seed: int,
) -> dict[str, Any]:
    """Bind the only authorized run to source, FDR state, and ACR protocol."""

    if stage not in ACR_BPDD_PROTOCOL["stages"]:
        raise ValueError(f"unknown ACR-BPDD stage: {stage}")
    if variant not in ACR_BPDD_PROTOCOL["variants"]:
        raise ValueError(f"unknown ACR-BPDD variant: {variant}")
    if seed != ACR_BPDD_PROTOCOL["seed"]:
        raise ValueError("ACR-BPDD protocol is frozen to seed0")
    source_sha256 = public_state_sha256(source_identity)
    run_id = (
        f"{variant}-{stage}-seed0-{source_sha256[:12].lower()}-"
        f"{ACR_BPDD_PROTOCOL_SHA256[:12].lower()}"
    )
    return {
        "source_sha256": source_sha256,
        "protocol_sha256": ACR_BPDD_PROTOCOL_SHA256,
        "fdr_protocol_sha256": FDR_PROTOCOL_SHA256,
        "initial_state_sha256": FDR_INITIAL_STATE_SHA256,
        "run_id": run_id,
        "stage": stage,
        "variant": variant,
        "seed": seed,
    }


def validate_resume_authority(
    checkpoint_identity: Mapping[str, Any],
    expected_identity: Mapping[str, Any],
) -> None:
    """Reject resume unless every immutable run-identity field matches."""

    required = (
        "source_sha256",
        "protocol_sha256",
        "fdr_protocol_sha256",
        "initial_state_sha256",
        "run_id",
        "stage",
        "variant",
        "seed",
    )
    for field in required:
        if (
            field not in checkpoint_identity
            or checkpoint_identity[field] != expected_identity.get(field)
        ):
            raise ValueError(
                f"resume authority mismatch for {field}: "
                f"expected={expected_identity.get(field)!r}, "
                f"actual={checkpoint_identity.get(field)!r}"
            )


def validate_manifest(
    manifest: Mapping[str, Any],
    *,
    expected_source: Mapping[str, Any] | None = None,
) -> None:
    """Fail closed on source, public-state, protocol, or run-identity drift."""

    source = manifest.get("source")
    if not isinstance(source, Mapping):
        raise ValueError("manifest source authority is missing")
    source_mapping = dict(source)
    if expected_source is not None and source_mapping != dict(expected_source):
        raise ValueError("manifest source authority differs from checked-out source")
    expected_source_sha256 = public_state_sha256(source_mapping)
    if manifest.get("source_sha256") != expected_source_sha256:
        raise ValueError("manifest source_sha256 mismatch")
    if manifest.get("protocol") != ACR_BPDD_PROTOCOL:
        raise ValueError("manifest protocol payload mismatch")
    if manifest.get("protocol_sha256") != ACR_BPDD_PROTOCOL_SHA256:
        raise ValueError("manifest protocol_sha256 mismatch")

    initial_state = manifest.get("initial_state")
    if not isinstance(initial_state, Mapping):
        raise ValueError("manifest initial-state authority is missing")
    if initial_state.get("sha256") != FDR_INITIAL_STATE_SHA256:
        raise ValueError("manifest initial-state SHA256 mismatch")

    expected_identity = build_run_identity(
        source_mapping, stage="formal", variant="fdr_acr_bpdd", seed=0
    )
    identities = manifest.get("run_identities")
    if not isinstance(identities, Mapping) or set(identities) != {
        "fdr_acr_bpdd_formal"
    }:
        raise ValueError("manifest run identity set mismatch")
    if identities["fdr_acr_bpdd_formal"] != expected_identity:
        raise ValueError("manifest run identity mismatch")

    expected_manifest_sha256 = public_state_sha256(
        {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    )
    if manifest.get("manifest_sha256") != expected_manifest_sha256:
        raise ValueError("manifest_sha256 mismatch")


__all__ = [
    "ACR_BPDD_PROTOCOL",
    "ACR_BPDD_PROTOCOL_SHA256",
    "FDR_INITIAL_STATE_SHA256",
    "FDR_SOURCE_COMMIT",
    "build_run_identity",
    "canonical_json_bytes",
    "public_state_sha256",
    "validate_manifest",
    "validate_resume_authority",
    "write_create_only_manifest",
]

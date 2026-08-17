"""Create one immutable FDR + ACR-BPDD formal100 protocol manifest."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

import torch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.acr_bpdd_protocol import (  # noqa: E402
    ACR_BPDD_PROTOCOL,
    ACR_BPDD_PROTOCOL_SHA256,
    FDR_INITIAL_STATE_SHA256,
    build_run_identity,
    public_state_sha256,
    validate_manifest,
    write_create_only_manifest,
)
from src.fdr_protocol import validate_fdr_initial_state  # noqa: E402


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _validate_hex(value: str, *, length: int, name: str) -> str:
    normalized = value.lower()
    if len(normalized) != length or any(
        character not in "0123456789abcdef" for character in normalized
    ):
        raise ValueError(f"{name} must be exactly {length} hexadecimal characters")
    return normalized


def _validate_initial_state(path: Path) -> dict:
    artifact = torch.load(path, map_location="cpu", weights_only=False)
    validate_fdr_initial_state(artifact)
    return artifact


def dirty_source_paths(repository_root: Path) -> list[str]:
    """Return every tracked or untracked source drift path."""

    result = subprocess.run(
        [
            "git",
            "-C",
            str(Path(repository_root).resolve()),
            "status",
            "--porcelain=v1",
            "-z",
            "--untracked-files=all",
        ],
        check=True,
        capture_output=True,
    )
    return [
        entry.decode("utf-8", errors="surrogateescape")
        for entry in result.stdout.split(b"\0")
        if entry
    ]


def current_source_identity(repository_root: Path) -> dict[str, str]:
    """Hash the checked-out commit and all tracked bytes deterministically."""

    root = Path(repository_root).resolve()
    commit = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip().lower()
    tracked = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        check=True,
        capture_output=True,
    ).stdout
    digest = hashlib.sha256()
    for raw in tracked.split(b"\0"):
        if not raw:
            continue
        path = root / raw.decode("utf-8", errors="surrogateescape")
        digest.update(raw + b"\0")
        digest.update(path.read_bytes())
    return {"git_commit": commit, "tree_sha256": digest.hexdigest().upper()}


def prepare_manifest(
    *,
    source_commit: str,
    source_tree_sha256: str,
    initial_state: Path,
    output: Path,
    repository_root: Path = ROOT,
) -> dict:
    """Validate clean source and frozen state, then create the sole-arm manifest."""

    repository_root = Path(repository_root).resolve()
    dirty = dirty_source_paths(repository_root)
    if dirty:
        raise ValueError(f"source repository is dirty: {dirty[:5]}")
    source = {
        "git_commit": _validate_hex(
            source_commit, length=40, name="source_commit"
        ),
        "tree_sha256": _validate_hex(
            source_tree_sha256, length=64, name="source_tree_sha256"
        ).upper(),
    }
    actual_source = current_source_identity(repository_root)
    if actual_source != source:
        raise ValueError(
            "source drift: requested authority differs from checked-out source: "
            f"expected={source}, actual={actual_source}"
        )

    initial_state = Path(initial_state).resolve()
    if not initial_state.is_file() or initial_state.is_symlink():
        raise FileNotFoundError(f"FDR initial state not found: {initial_state}")
    state_sha256 = _file_sha256(initial_state)
    if state_sha256 != FDR_INITIAL_STATE_SHA256:
        raise ValueError(
            "ACR-BPDD initial-state SHA256 mismatch: "
            f"expected={FDR_INITIAL_STATE_SHA256}, actual={state_sha256}"
        )
    artifact = _validate_initial_state(initial_state)
    fingerprints = artifact.get("fingerprints")
    if not isinstance(fingerprints, dict):
        raise ValueError("FDR initial-state fingerprints are missing")

    identity = build_run_identity(
        source, stage="formal", variant="fdr_acr_bpdd", seed=0
    )
    manifest = {
        "format_version": 1,
        "source": source,
        "source_sha256": public_state_sha256(source),
        "protocol": ACR_BPDD_PROTOCOL,
        "protocol_sha256": ACR_BPDD_PROTOCOL_SHA256,
        "initial_state": {
            "path": str(initial_state),
            "sha256": state_sha256,
            "fingerprints": dict(fingerprints),
        },
        "run_identities": {"fdr_acr_bpdd_formal": identity},
    }
    manifest["manifest_sha256"] = public_state_sha256(manifest)
    validate_manifest(manifest, expected_source=source)
    write_create_only_manifest(Path(output).resolve(), manifest)
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--source-tree-sha256", required=True)
    parser.add_argument("--initial-state", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repository-root", type=Path, default=ROOT)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    prepare_manifest(
        source_commit=args.source_commit,
        source_tree_sha256=args.source_tree_sha256,
        initial_state=args.initial_state,
        output=args.output,
        repository_root=args.repository_root,
    )


if __name__ == "__main__":
    main()

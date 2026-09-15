"""Shared, fail-closed provenance manifest for paired checkpoint evaluations."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping


def sha256(path: Path) -> str:
    """Return the upper-case SHA-256 of one regular, existing file."""
    path = path.resolve()
    if not path.is_file() or path.is_symlink():
        raise FileNotFoundError(path)
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def build_manifest(
    *,
    dataset: str,
    data_yaml: Path,
    split: str,
    imgsz: int,
    batch: int,
    workers: int,
    device: str,
    checkpoints: Mapping[str, Path],
) -> dict[str, object]:
    """Build provenance before evaluation; every supplied checkpoint must exist."""
    if len(checkpoints) < 2:
        raise ValueError("a common evaluation requires at least two checkpoints")
    if split not in {"val", "test"}:
        raise ValueError("split must be val or test")
    if imgsz <= 0 or batch <= 0 or workers < 0:
        raise ValueError("imgsz/batch/workers are invalid")
    resolved_data = data_yaml.resolve()
    data_hash = sha256(resolved_data)
    resolved_checkpoints = {
        name: {
            "path": str(Path(path).resolve()),
            "sha256": sha256(Path(path)),
            "bytes": Path(path).resolve().stat().st_size,
        }
        for name, path in sorted(checkpoints.items())
    }
    return {
        "format_version": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": dataset,
        "contract": {
            "data_yaml": str(resolved_data),
            "data_yaml_sha256": data_hash,
            "split": split,
            "imgsz": imgsz,
            "batch": batch,
            "workers": workers,
            "device": device,
            "same_data_yaml_for_every_arm": True,
            "same_process_and_evaluator_required": True,
            "checkpoint_selection": "user-supplied frozen checkpoint",
        },
        "checkpoints": resolved_checkpoints,
    }

"""Authority, dataset, metric, and audit helpers for ACR-BPDD final evaluation."""

from __future__ import annotations

import hashlib
import json
import math
import platform
import re
import statistics
from pathlib import Path
from typing import Any, Mapping, Sequence

import torch
import yaml

from src.acr_bpdd_protocol import (
    ACR_BPDD_PROTOCOL_SHA256,
    FDR_INITIAL_STATE_SHA256,
    build_run_identity,
)
from src.bpdd_formal_evaluation import SCALE_NAMES, file_sha256
from src.lpr_protocol import CATEGORY_NAMES


VARIANT = "fdr_acr_bpdd"
STAGE = "formal"
EXPECTED_EPOCHS = 100
EXPECTED_VAL_IMAGES = 548
IMAGE_SUFFIXES = frozenset({".jpg", ".jpeg", ".png", ".bmp", ".webp"})
CORE_METRICS = ("precision", "recall", "f1", "map50", "map75", "map")
CLASS_METRICS = ("map50", "map75", "map")
SHA256_PATTERN = re.compile(r"[0-9A-F]{64}")


def _read_json(path: str | Path) -> dict[str, Any]:
    source = Path(path).resolve()
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON authority: {source}") from error
    if not isinstance(payload, dict):
        raise ValueError(f"JSON authority is not an object: {source}")
    return payload


def _read_jsonl(path: str | Path, *, label: str) -> list[dict[str, Any]]:
    source = Path(path).resolve()
    if not source.is_file():
        raise FileNotFoundError(f"{label} not found: {source}")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        source.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid {label} JSON at line {line_number}") from error
        if not isinstance(row, dict):
            raise ValueError(f"{label} row {line_number} is not an object")
        rows.append(row)
    return rows


def _canonical_sha256(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest().upper()


def artifact_record(path: str | Path) -> dict[str, Any]:
    source = Path(path).resolve()
    if not source.is_file():
        raise FileNotFoundError(f"evaluation artifact not found: {source}")
    return {
        "path": str(source),
        "bytes": source.stat().st_size,
        "sha256": file_sha256(source),
    }


def _require_exact_epochs(rows: Sequence[Mapping[str, Any]], *, label: str) -> None:
    if len(rows) != EXPECTED_EPOCHS:
        raise ValueError(f"{label} must contain exactly 100 rows")
    epochs = [row.get("completed_epoch") for row in rows]
    if epochs != list(range(1, EXPECTED_EPOCHS + 1)):
        raise ValueError(f"{label} must contain contiguous epochs 1-100")


def _require_identity(
    row: Mapping[str, Any], identity: Mapping[str, Any], *, label: str
) -> None:
    for field in ("run_id", "variant", "stage"):
        if row.get(field) != identity.get(field):
            raise ValueError(f"{label} identity mismatch for {field}")


def _resolve_manifest_path(value: Any, *, run: Path, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError(f"ACR-BPDD run manifest is missing {label}")
    raw = Path(value)
    return (raw if raw.is_absolute() else run / raw).resolve()


def _is_within(path: Path, directory: Path) -> bool:
    try:
        path.relative_to(directory)
    except ValueError:
        return False
    return True


def _validate_queue_artifacts(
    value: Any,
    *,
    run: Path,
    completed_epoch: int,
    inventory: dict[str, dict[str, Any]],
) -> None:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence) or not value:
        raise ValueError(
            f"ACR-BPDD publication queue epoch {completed_epoch} artifacts are invalid"
        )
    for declaration in value:
        if not isinstance(declaration, Mapping):
            raise ValueError(
                f"ACR-BPDD publication queue epoch {completed_epoch} artifact "
                "declaration is not an object"
            )
        raw_path = declaration.get("path")
        if not isinstance(raw_path, str) or not raw_path:
            raise ValueError("ACR-BPDD queue artifact path is missing")
        source = _resolve_manifest_path(raw_path, run=run, label="artifact path")
        if not _is_within(source, run):
            raise ValueError(f"ACR-BPDD queue artifact is outside run directory: {source}")
        if not source.is_file():
            raise FileNotFoundError(f"ACR-BPDD queue artifact is missing: {source}")
        name = declaration.get("name", source.name)
        if (
            not isinstance(name, str)
            or not name
            or Path(name).name != name
            or name in {".", ".."}
        ):
            raise ValueError("ACR-BPDD queue artifact name is invalid")
        declared_sha = str(declaration.get("sha256", "")).upper()
        if SHA256_PATTERN.fullmatch(declared_sha) is None:
            raise ValueError(f"ACR-BPDD queue artifact {name} SHA256 is invalid")
        record = artifact_record(source)
        if record["sha256"] != declared_sha:
            raise ValueError(f"ACR-BPDD queue artifact {name} SHA256 mismatch")
        previous = inventory.get(name)
        if previous is not None and previous != record:
            raise ValueError(f"ACR-BPDD queue artifact duplicate name conflict: {name}")
        inventory[name] = record


def validate_formal_authority(
    run_dir: str | Path,
    *,
    checkpoint: str | Path,
    publication_ledger: str | Path,
) -> dict[str, Any]:
    """Validate the immutable Formal100 run, queue, ledger, and final checkpoint."""

    run = Path(run_dir).resolve()
    checkpoint_path = Path(checkpoint).resolve()
    ledger_path = Path(publication_ledger).resolve()
    if checkpoint_path.name != "epoch99.pt":
        raise ValueError("ACR-BPDD Formal100 only accepts exact epoch99.pt")
    if not checkpoint_path.is_file():
        raise FileNotFoundError(f"ACR-BPDD final checkpoint not found: {checkpoint_path}")

    manifest_path = run / "acr-bpdd-run.json"
    manifest = _read_json(manifest_path)
    source = manifest.get("source")
    identity = manifest.get("run_identity")
    initial_state = manifest.get("initial_state")
    if manifest.get("format_version") != 1:
        raise ValueError("ACR-BPDD run manifest format must be 1")
    if not isinstance(source, Mapping) or not isinstance(identity, Mapping):
        raise ValueError("ACR-BPDD run manifest identity authority is incomplete")
    expected_identity = build_run_identity(
        source, stage=STAGE, variant=VARIANT, seed=0
    )
    if dict(identity) != expected_identity:
        raise ValueError("ACR-BPDD run manifest identity, variant, or stage mismatch")
    if manifest.get("protocol_sha256") != ACR_BPDD_PROTOCOL_SHA256:
        raise ValueError("ACR-BPDD run manifest protocol SHA256 mismatch")
    if manifest.get("fdr_protocol_sha256") != identity.get("fdr_protocol_sha256"):
        raise ValueError("ACR-BPDD run manifest FDR protocol SHA256 mismatch")
    if not isinstance(initial_state, Mapping) or (
        initial_state.get("sha256") != FDR_INITIAL_STATE_SHA256
    ):
        raise ValueError("ACR-BPDD run manifest initial-state authority mismatch")
    if manifest.get("comparison") != {
        "evidence_level": "preliminary_cross_run",
        "strict_paired": False,
    }:
        raise ValueError("ACR-BPDD run manifest comparison authority mismatch")

    epoch_path = run / "acr-bpdd-epochs.jsonl"
    epoch_rows = _read_jsonl(epoch_path, label="ACR-BPDD epoch records")
    _require_exact_epochs(epoch_rows, label="ACR-BPDD epoch records")
    for row in epoch_rows:
        _require_identity(row, identity, label="ACR-BPDD epoch record")
        if row.get("gradients_finite") is not True:
            raise ValueError("ACR-BPDD epoch record contains non-finite gradients")

    queue_path = _resolve_manifest_path(
        manifest.get("publication_queue"), run=run, label="publication_queue"
    )
    queue_rows = _read_jsonl(queue_path, label="ACR-BPDD publication queue")
    _require_exact_epochs(queue_rows, label="ACR-BPDD publication queue")
    queue_hashes: list[str] = []
    queue_artifacts: dict[str, dict[str, Any]] = {}
    for row in queue_rows:
        _require_identity(row, identity, label="ACR-BPDD publication queue")
        if row.get("status") != "pending":
            raise ValueError("ACR-BPDD publication queue row is not pending")
        completed_epoch = int(row["completed_epoch"])
        _validate_queue_artifacts(
            row.get("artifacts"),
            run=run,
            completed_epoch=completed_epoch,
            inventory=queue_artifacts,
        )
        checkpoint_sha = str(row.get("checkpoint_sha256", "")).upper()
        if SHA256_PATTERN.fullmatch(checkpoint_sha) is None:
            raise ValueError("ACR-BPDD publication queue checkpoint SHA256 is invalid")
        queue_hashes.append(_canonical_sha256(row))

    ledger_rows = _read_jsonl(ledger_path, label="ACR-BPDD publication ledger")
    _require_exact_epochs(ledger_rows, label="ACR-BPDD publication ledger")
    for index, (row, queue_row, queue_hash) in enumerate(
        zip(ledger_rows, queue_rows, queue_hashes, strict=True), 1
    ):
        _require_identity(row, identity, label="ACR-BPDD publication ledger")
        if row.get("verified") is not True:
            raise ValueError(f"ACR-BPDD publication ledger epoch {index} is not verified")
        if str(row.get("queue_record_sha256", "")).upper() != queue_hash:
            raise ValueError(
                f"ACR-BPDD publication ledger/queue SHA256 mismatch at epoch {index}"
            )
        ledger_checkpoint = row.get("checkpoint")
        if not isinstance(ledger_checkpoint, Mapping):
            raise ValueError(
                f"ACR-BPDD publication ledger checkpoint missing at epoch {index}"
            )
        if str(ledger_checkpoint.get("sha256", "")).upper() != str(
            queue_row.get("checkpoint_sha256", "")
        ).upper():
            raise ValueError(
                f"ACR-BPDD publication ledger/checkpoint SHA256 mismatch at epoch {index}"
            )

    final_queue_checkpoint = _resolve_manifest_path(
        queue_rows[-1].get("checkpoint"), run=queue_path.parent, label="final checkpoint"
    )
    if final_queue_checkpoint.name != "epoch99.pt":
        raise ValueError("ACR-BPDD final publication queue entry is not epoch99.pt")
    checkpoint_sha = file_sha256(checkpoint_path)
    if checkpoint_sha != str(queue_rows[-1]["checkpoint_sha256"]).upper():
        raise ValueError("ACR-BPDD final checkpoint SHA256 differs from publication queue")

    artifacts = {
        "run_manifest": artifact_record(manifest_path),
        "epoch_records": artifact_record(epoch_path),
        "publication_queue": artifact_record(queue_path),
        "publication_ledger": artifact_record(ledger_path),
        "checkpoint": artifact_record(checkpoint_path),
    }
    data_path = _resolve_manifest_path(manifest.get("data"), run=run, label="data")
    artifacts["data_yaml"] = artifact_record(data_path)
    for name, record in queue_artifacts.items():
        if name in artifacts and artifacts[name] != record:
            raise ValueError(f"ACR-BPDD artifact inventory name conflict: {name}")
        artifacts[name] = record
    return {
        "identity": dict(identity),
        "completed_epoch": EXPECTED_EPOCHS,
        "manifest": manifest,
        "data": str(data_path),
        "checkpoint_sha256": checkpoint_sha,
        "epoch_records": {
            "count": EXPECTED_EPOCHS,
            "completed_epochs": [1, EXPECTED_EPOCHS],
            "all_gradients_finite": True,
        },
        "publication_queue": {
            "count": EXPECTED_EPOCHS,
            "completed_epochs": [1, EXPECTED_EPOCHS],
            "artifacts": sorted(queue_artifacts),
        },
        "publication_ledger": {
            "count": EXPECTED_EPOCHS,
            "completed_epochs": [1, EXPECTED_EPOCHS],
            "all_verified": True,
        },
        "artifacts": artifacts,
    }


def validate_data_yaml(data_yaml: str | Path, dataset_root: str | Path) -> dict[str, Any]:
    yaml_path = Path(data_yaml).resolve()
    payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("ACR-BPDD evaluation data YAML is not a mapping")
    root = Path(dataset_root).resolve()
    raw_root = Path(str(payload.get("path", root)))
    yaml_root = (raw_root if raw_root.is_absolute() else yaml_path.parent / raw_root).resolve()
    if yaml_root != root:
        raise ValueError("ACR-BPDD data YAML dataset root mismatch")
    if int(payload.get("nc", -1)) != 10 or tuple(payload.get("names", ())) != tuple(
        CATEGORY_NAMES
    ):
        raise ValueError("ACR-BPDD data YAML category authority mismatch")
    raw_val = Path(str(payload.get("val", "")))
    val_path = (raw_val if raw_val.is_absolute() else yaml_root / raw_val).resolve()
    if val_path != (root / "images" / "val").resolve():
        raise ValueError("ACR-BPDD data YAML val authority mismatch")
    return artifact_record(yaml_path)


def _file_inventory(files: Sequence[Path], *, dataset_root: Path) -> dict[str, Any]:
    digest = hashlib.sha256()
    records: list[dict[str, Any]] = []
    total_bytes = 0
    for path in sorted(files, key=lambda item: item.relative_to(dataset_root).as_posix()):
        relative = path.relative_to(dataset_root).as_posix()
        sha256 = file_sha256(path)
        size = path.stat().st_size
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(sha256.encode("ascii"))
        digest.update(b"\n")
        records.append({"path": relative, "bytes": size, "sha256": sha256})
        total_bytes += size
    return {
        "count": len(records),
        "bytes": total_bytes,
        "sha256": digest.hexdigest().upper(),
        "files": records,
    }


def build_split_authority(dataset_root: str | Path, split: str) -> dict[str, Any]:
    if split not in {"val", "test"}:
        raise ValueError(f"unsupported ACR-BPDD evaluation split: {split}")
    root = Path(dataset_root).resolve()
    image_root = root / "images" / split
    label_root = root / "labels" / split
    if not image_root.is_dir() or not label_root.is_dir():
        raise FileNotFoundError(f"VisDrone {split} image/label directories are incomplete")
    images = [
        path
        for path in image_root.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    ]
    labels = [
        path for path in label_root.rglob("*") if path.is_file() and path.suffix.lower() == ".txt"
    ]
    if not images:
        raise ValueError(f"VisDrone {split} split contains no images")
    if split == "val" and len(images) != EXPECTED_VAL_IMAGES:
        raise ValueError(
            f"frozen ACR-BPDD val authority requires exactly 548 images, got {len(images)}"
        )
    return {
        "dataset_root": str(root),
        "split": split,
        "images": _file_inventory(images, dataset_root=root),
        "labels": _file_inventory(labels, dataset_root=root),
    }


def _finite(value: Any, *, label: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"non-finite {label}")
    return result


def validate_complete_metrics(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    metrics = payload.get("metrics")
    if not isinstance(metrics, Mapping):
        raise ValueError("evaluation metrics block is missing")
    for name in CORE_METRICS:
        if name not in metrics:
            raise ValueError(f"evaluation metric {name} is missing")
        _finite(metrics[name], label=name)
    scales = payload.get("scales")
    if not isinstance(scales, Mapping):
        raise ValueError("evaluation scale metrics are missing")
    for name in SCALE_NAMES:
        if name not in scales:
            raise ValueError(f"evaluation scale metric {name} is missing")
        _finite(scales[name], label=f"scale {name}")
    classes = payload.get("class_details")
    if not isinstance(classes, Mapping):
        raise ValueError("evaluation class metrics are missing")
    for class_name in CATEGORY_NAMES:
        detail = classes.get(class_name)
        if not isinstance(detail, Mapping):
            raise ValueError(f"evaluation class metric {class_name} is missing")
        for name in CLASS_METRICS:
            if name not in detail:
                raise ValueError(f"evaluation class {class_name} {name}/AP75 is missing")
            _finite(detail[name], label=f"class {class_name} {name}")
    return payload


def _percentile(values: Sequence[float], quantile: float) -> float:
    ordered = sorted(float(value) for value in values)
    position = (len(ordered) - 1) * quantile
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] * (upper - position) + ordered[upper] * (position - lower)


def latency_summary(values: Sequence[float]) -> dict[str, float]:
    samples = [float(value) for value in values]
    if not samples or not all(math.isfinite(value) and value > 0 for value in samples):
        raise ValueError("latency samples must be non-empty, finite, and positive")
    mean = float(statistics.fmean(samples))
    return {
        "mean_ms": mean,
        "median_ms": float(statistics.median(samples)),
        "p95_ms": _percentile(samples, 0.95),
        "fps": 1000.0 / mean,
    }


def _metric_delta(
    current: Mapping[str, Any], reference: Mapping[str, Any], names: Sequence[str]
) -> dict[str, float]:
    return {name: float(current[name]) - float(reference[name]) for name in names}


def _reference_delta(
    current: Mapping[str, Any], path: str | Path
) -> dict[str, Any]:
    reference_path = Path(path).resolve()
    reference = _read_json(reference_path)
    metrics = reference.get("metrics")
    if not isinstance(metrics, Mapping) or any(name not in metrics for name in CORE_METRICS):
        raise ValueError(f"cross-run reference lacks complete core metrics: {reference_path}")
    for name in CORE_METRICS:
        _finite(metrics[name], label=f"reference {name}")
    result: dict[str, Any] = {
        "comparison_type": "cross_run_difference",
        "artifact": str(reference_path),
        "artifact_sha256": file_sha256(reference_path),
        "metrics_delta": _metric_delta(current["metrics"], metrics, CORE_METRICS),
    }
    scales = reference.get("scales")
    if isinstance(scales, Mapping) and all(name in scales for name in SCALE_NAMES):
        result["scale_delta"] = _metric_delta(current["scales"], scales, SCALE_NAMES)
    class_details = reference.get("class_details")
    if isinstance(class_details, Mapping):
        class_delta: dict[str, dict[str, float]] = {}
        for class_name in CATEGORY_NAMES:
            left = current["class_details"].get(class_name)
            right = class_details.get(class_name)
            if isinstance(left, Mapping) and isinstance(right, Mapping) and all(
                name in right for name in CLASS_METRICS
            ):
                class_delta[class_name] = _metric_delta(left, right, CLASS_METRICS)
        if class_delta:
            result["class_delta"] = class_delta
    return result


def build_cross_run_comparison(
    current: Mapping[str, Any],
    *,
    fdr_evaluation: str | Path | None = None,
    bpdd_evaluation: str | Path | None = None,
) -> dict[str, Any]:
    validate_complete_metrics(current)
    references: dict[str, Any] = {}
    if fdr_evaluation is not None:
        references["fdr"] = _reference_delta(current, fdr_evaluation)
    if bpdd_evaluation is not None:
        references["bpdd"] = _reference_delta(current, bpdd_evaluation)
    return {
        "comparison_scope": "preliminary_cross_run",
        "strict_paired": False,
        "references": references,
    }


def execution_environment(device: str) -> dict[str, Any]:
    import torchvision
    import ultralytics

    torch_device = torch.device(device)
    gpu: dict[str, Any] | None = None
    if torch_device.type == "cuda" and torch.cuda.is_available():
        index = torch_device.index
        if index is None:
            index = torch.cuda.current_device()
        properties = torch.cuda.get_device_properties(index)
        gpu = {
            "index": index,
            "name": properties.name,
            "total_memory_bytes": properties.total_memory,
            "compute_capability": list(properties.major_minor)
            if hasattr(properties, "major_minor")
            else [properties.major, properties.minor],
        }
    return {
        "device": str(torch_device),
        "gpu": gpu,
        "software": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "torch": torch.__version__,
            "torchvision": torchvision.__version__,
            "ultralytics": ultralytics.__version__,
            "cuda": torch.version.cuda,
            "cudnn": torch.backends.cudnn.version(),
        },
    }


__all__ = [
    "CORE_METRICS",
    "EXPECTED_EPOCHS",
    "EXPECTED_VAL_IMAGES",
    "STAGE",
    "VARIANT",
    "artifact_record",
    "build_cross_run_comparison",
    "build_split_authority",
    "execution_environment",
    "latency_summary",
    "validate_complete_metrics",
    "validate_data_yaml",
    "validate_formal_authority",
]

"""Measure the frozen four-row paper efficiency table on one CUDA device.

Five checkpoint authorities are measured because the strict FDR control paired
with FDR+BPDD is retained as an auxiliary audit row.  The four paper rows keep
their canonical checkpoint authorities.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import math
import platform
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


BENCHMARK_PROTOCOL = {
    "imgsz": 640,
    "batch": 1,
    "half": False,
    "warmup_iterations": 100,
    "measured_iterations": 300,
    "cuda_synchronize": True,
    "latency_scope": "preprocess_inference_postprocess",
    "latency_statistic": "median_and_p90_end_to_end_ms",
    "fps_definition": "1000 / median_end_to_end_latency_ms",
    "conf": 0.001,
    "max_det": 300,
}

REQUIRED_AUTHORITIES = (
    "baseline",
    "fdr",
    "strict_pair_fdr",
    "fdr_bpdd",
    "fdr_bpdd_fia",
)

PAPER_ROWS = ("baseline", "fdr", "fdr_bpdd", "fdr_bpdd_fia")

METHOD_NAMES = {
    "baseline": "RT-DETR-L Baseline",
    "fdr": "RT-DETR-L + FDR",
    "strict_pair_fdr": "RT-DETR-L + FDR (strict BPDD-pair control)",
    "fdr_bpdd": "RT-DETR-L + FDR + BPDD",
    "fdr_bpdd_fia": "RT-DETR-L + FDR + BPDD + FIA",
}


def _percentile(values: Sequence[float], quantile: float) -> float:
    ordered = sorted(float(value) for value in values)
    position = (len(ordered) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] * (upper - position) + ordered[upper] * (position - lower)


def latency_summary(values: Sequence[float]) -> dict[str, int | float]:
    samples = [float(value) for value in values]
    if not samples or not all(math.isfinite(value) and value > 0 for value in samples):
        raise ValueError("latency samples must be finite and positive")
    median_ms = statistics.median(samples)
    return {
        "sample_count": len(samples),
        "median_ms": median_ms,
        "p90_ms": _percentile(samples, 0.90),
        "fps": 1000.0 / median_ms,
    }


def checkpoint_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def prediction_kwargs(*, image: Any, device_index: int) -> dict[str, Any]:
    """Build an FP32 prediction call without the deprecated ``half`` CLI flag."""

    return {
        "source": image,
        "imgsz": BENCHMARK_PROTOCOL["imgsz"],
        "batch": BENCHMARK_PROTOCOL["batch"],
        "device": device_index,
        "conf": BENCHMARK_PROTOCOL["conf"],
        "max_det": BENCHMARK_PROTOCOL["max_det"],
        "verbose": False,
        "save": False,
        "stream": False,
    }


def build_report(
    records: Mapping[str, Mapping[str, Any]],
    *,
    environment: Mapping[str, Any],
) -> dict[str, Any]:
    missing = [name for name in REQUIRED_AUTHORITIES if name not in records]
    extra = [name for name in records if name not in REQUIRED_AUTHORITIES]
    if missing:
        raise ValueError(f"missing benchmark authorities: {missing}")
    if extra:
        raise ValueError(f"unexpected benchmark authorities: {extra}")
    normalized = {name: dict(records[name]) for name in REQUIRED_AUTHORITIES}
    for name, record in normalized.items():
        if record.get("latency", {}).get("sample_count") != BENCHMARK_PROTOCOL[
            "measured_iterations"
        ]:
            raise ValueError(f"invalid latency sample count for {name}")
    return {
        "format_version": 1,
        "status": "completed_unified_measurement",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "protocol": dict(BENCHMARK_PROTOCOL),
        "environment": dict(environment),
        "paper_rows": [
            {"authority_id": name, **normalized[name]} for name in PAPER_ROWS
        ],
        "strict_bpdd_pair": {
            "fdr_authority_id": "strict_pair_fdr",
            "bpdd_authority_id": "fdr_bpdd",
            "rows": [
                {"authority_id": name, **normalized[name]}
                for name in ("strict_pair_fdr", "fdr_bpdd")
            ],
        },
        "all_authorities": normalized,
    }


def _load_runtime_modules() -> tuple[Any, Any, Any]:
    import numpy as np
    import torch
    from ultralytics import RTDETR
    from ultralytics.utils.torch_utils import get_flops

    # Register custom classes before torch/Ultralytics unpickles old checkpoints.
    for module_name in (
        "src.fia",
        "src.rtdetr_fdr",
        "src.rtdetr_fdr_bpdd",
        "src.rtdetr_fdr_bpdd_fia",
    ):
        try:
            __import__(module_name)
        except ModuleNotFoundError:
            pass
    return np, torch, (RTDETR, get_flops)


def _model_graph_identity(model: Any) -> dict[str, Any]:
    layers = getattr(model, "model", None)
    if layers is None:
        return {"model_class": type(model).__name__}
    identity: dict[str, Any] = {
        "model_class": type(model).__name__,
        "layer_count": len(layers),
    }
    if len(layers) > 23:
        identity.update(
            {
                "layer_22_class": type(layers[22]).__name__,
                "layer_22_from": getattr(layers[22], "f", None),
                "layer_23_from": getattr(layers[23], "f", None),
                "decoder_from": getattr(layers[-1], "f", None),
            }
        )
    return identity


def _benchmark_one(
    authority_id: str,
    checkpoint: Path,
    *,
    device_index: int,
    expected_sha256: str | None,
) -> dict[str, Any]:
    np, torch, runtime = _load_runtime_modules()
    RTDETR, get_flops = runtime
    if not torch.cuda.is_available():
        raise RuntimeError("the frozen unified benchmark requires CUDA")
    actual_sha256 = checkpoint_sha256(checkpoint)
    if expected_sha256 and actual_sha256.lower() != expected_sha256.lower():
        raise ValueError(
            f"checkpoint hash mismatch for {authority_id}: {actual_sha256}"
        )

    device = torch.device(f"cuda:{device_index}")
    rng = np.random.default_rng(20260820)
    image = rng.integers(
        0,
        256,
        size=(BENCHMARK_PROTOCOL["imgsz"], BENCHMARK_PROTOCOL["imgsz"], 3),
        dtype=np.uint8,
    )
    detector = RTDETR(str(checkpoint))
    detector.model.to(device).eval().float()
    if next(detector.model.parameters()).dtype != torch.float32:
        raise RuntimeError(f"{authority_id} did not enter the frozen FP32 mode")
    parameters = sum(parameter.numel() for parameter in detector.model.parameters())
    gflops = float(get_flops(detector.model, imgsz=BENCHMARK_PROTOCOL["imgsz"]))
    predict_kwargs = prediction_kwargs(image=image, device_index=device_index)
    with torch.inference_mode():
        for _ in range(BENCHMARK_PROTOCOL["warmup_iterations"]):
            detector.predict(**predict_kwargs)
        torch.cuda.synchronize(device)
        torch.cuda.reset_peak_memory_stats(device)
        samples: list[float] = []
        for _ in range(BENCHMARK_PROTOCOL["measured_iterations"]):
            torch.cuda.synchronize(device)
            started = time.perf_counter()
            detector.predict(**predict_kwargs)
            torch.cuda.synchronize(device)
            samples.append((time.perf_counter() - started) * 1000.0)
    peak_memory_mib = torch.cuda.max_memory_allocated(device) / (1024.0**2)
    record = {
        "method": METHOD_NAMES[authority_id],
        "checkpoint": {
            "path": str(checkpoint),
            "sha256": actual_sha256,
            "size_bytes": checkpoint.stat().st_size,
        },
        "parameters": parameters,
        "gflops": gflops,
        "peak_memory_mib": peak_memory_mib,
        "latency": latency_summary(samples),
        "latency_samples_ms": samples,
        "graph_identity": _model_graph_identity(detector.model),
    }
    del detector
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.synchronize(device)
    return record


def _environment(torch: Any, *, device_index: int) -> dict[str, Any]:
    import ultralytics

    properties = torch.cuda.get_device_properties(device_index)
    return {
        "hostname": platform.node(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "torch": torch.__version__,
        "cuda_runtime": torch.version.cuda,
        "cudnn": torch.backends.cudnn.version(),
        "ultralytics": ultralytics.__version__,
        "gpu": properties.name,
        "gpu_total_memory_mib": properties.total_memory / (1024.0**2),
        "device_index": device_index,
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    _, torch, _ = _load_runtime_modules()
    output = Path(args.output).resolve()
    if output.exists():
        raise FileExistsError(f"refusing to overwrite benchmark evidence: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    checkpoints = {
        "baseline": Path(args.baseline).resolve(),
        "fdr": Path(args.fdr).resolve(),
        "strict_pair_fdr": Path(args.strict_pair_fdr).resolve(),
        "fdr_bpdd": Path(args.fdr_bpdd).resolve(),
        "fdr_bpdd_fia": Path(args.fdr_bpdd_fia).resolve(),
    }
    expected_hashes = {
        "baseline": args.baseline_sha256,
        "fdr": args.fdr_sha256,
        "strict_pair_fdr": args.strict_pair_fdr_sha256,
        "fdr_bpdd": args.fdr_bpdd_sha256,
        "fdr_bpdd_fia": args.fdr_bpdd_fia_sha256,
    }
    records: dict[str, dict[str, Any]] = {}
    for index, authority_id in enumerate(REQUIRED_AUTHORITIES, start=1):
        print(
            f"[{index}/{len(REQUIRED_AUTHORITIES)}] benchmarking {authority_id}",
            flush=True,
        )
        records[authority_id] = _benchmark_one(
            authority_id,
            checkpoints[authority_id],
            device_index=args.device,
            expected_sha256=expected_hashes[authority_id],
        )
        latency = records[authority_id]["latency"]
        print(
            f"  median={latency['median_ms']:.4f} ms, "
            f"p90={latency['p90_ms']:.4f} ms, fps={latency['fps']:.2f}",
            flush=True,
        )
    report = build_report(
        records,
        environment=_environment(torch, device_index=args.device),
    )
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(output)
    print(f"wrote {output}", flush=True)
    return report


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in REQUIRED_AUTHORITIES:
        option = name.replace("_", "-")
        parser.add_argument(f"--{option}", required=True)
        parser.add_argument(f"--{option}-sha256")
    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("--output", required=True)
    return parser.parse_args(argv)


if __name__ == "__main__":
    run(parse_args())

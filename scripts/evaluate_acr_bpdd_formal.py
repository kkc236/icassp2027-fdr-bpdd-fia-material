"""Independently evaluate an exact ACR-BPDD Formal100 checkpoint."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import torch
from torch import nn
from ultralytics.utils.torch_utils import get_flops

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.acr_bpdd_formal_evaluation import (  # noqa: E402
    artifact_record,
    build_cross_run_comparison,
    build_split_authority,
    execution_environment,
    latency_summary,
    validate_complete_metrics,
    validate_data_yaml,
    validate_formal_authority,
)
from src.bpdd_formal_evaluation import (  # noqa: E402
    CachedScaleRTDETRValidator,
    LoadedFinalCheckpoint,
    SCALE_NAMES,
    load_exact_final_checkpoint,
    state_sha256,
    summarize_native_box_metrics,
    summarize_scale_metrics,
    write_create_only_json,
)
from src.lpr_protocol import CATEGORY_NAMES  # noqa: E402


EVALUATION_PROTOCOL = {
    "imgsz": 640,
    "batch": 8,
    "workers": 8,
    "conf": 0.001,
    "max_det": 300,
    "nms": False,
}
BENCHMARK_PROTOCOL = {
    "imgsz": 640,
    "batch": 1,
    "half": True,
    "warmup": 50,
    "runs": 200,
}


def run_official_validation(
    model: Any,
    *,
    dataset_root: str | Path,
    split: str,
    save_dir: str | Path,
    device: str,
    expected_images: int,
) -> dict[str, Any]:
    """Run one Ultralytics validation pass and reuse its predictions for breakdowns."""

    root = Path(dataset_root).resolve()
    data = {
        "path": str(root),
        "train": str((root / "images" / "train").resolve()),
        "val": str((root / "images" / "val").resolve()),
        "test": str((root / "images" / "test").resolve()),
        "names": list(CATEGORY_NAMES),
        "nc": len(CATEGORY_NAMES),
    }
    with tempfile.TemporaryDirectory(prefix="acr-bpdd-evaluation-") as temporary:
        data_path = Path(temporary) / "data.json"
        data_path.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        validator = CachedScaleRTDETRValidator(
            save_dir=Path(save_dir),
            args={
                "model": str(data_path),
                "data": str(data_path),
                "task": "detect",
                "mode": "val",
                "split": split,
                **EVALUATION_PROTOCOL,
                "device": device,
                "cache": False,
                "half": False,
                "rect": False,
                "plots": False,
                "save_json": False,
                "save_txt": False,
                "verbose": False,
            },
        )
        validator(model=model)
    processed = len(validator.scale_targets)
    if processed != expected_images or len(validator.scale_predictions) != processed:
        raise RuntimeError(
            f"official {split} processed {processed} images instead of {expected_images}"
        )
    result = {
        **summarize_native_box_metrics(validator.metrics.box, CATEGORY_NAMES),
        **summarize_scale_metrics(
            validator.scale_predictions,
            validator.scale_targets,
            class_count=len(CATEGORY_NAMES),
        ),
        "processed_images": processed,
        "prediction_passes": 1,
    }
    validate_complete_metrics(result)
    return result


def _synchronize(device: torch.device) -> None:
    if device.type == "cuda":
        torch.cuda.synchronize(device)


def run_efficiency_audit(model: nn.Module, *, device: str) -> dict[str, Any]:
    torch_device = torch.device(device)
    if torch_device.type != "cuda" or not torch.cuda.is_available():
        raise RuntimeError("ACR-BPDD FP16 latency audit requires CUDA")
    parameters = sum(parameter.numel() for parameter in model.parameters())
    gflops = float(get_flops(model, imgsz=BENCHMARK_PROTOCOL["imgsz"]))
    runtime_model = model.to(torch_device).eval().half()
    image = torch.randn(
        BENCHMARK_PROTOCOL["batch"],
        3,
        BENCHMARK_PROTOCOL["imgsz"],
        BENCHMARK_PROTOCOL["imgsz"],
        device=torch_device,
        dtype=torch.float16,
    )
    torch.cuda.reset_peak_memory_stats(torch_device)
    samples: list[float] = []
    with torch.inference_mode():
        for _ in range(BENCHMARK_PROTOCOL["warmup"]):
            runtime_model.predict(image)
        _synchronize(torch_device)
        for _ in range(BENCHMARK_PROTOCOL["runs"]):
            _synchronize(torch_device)
            started = time.perf_counter()
            runtime_model.predict(image)
            _synchronize(torch_device)
            samples.append((time.perf_counter() - started) * 1000.0)
    return {
        "parameters": int(parameters),
        "gflops": gflops,
        "fp16": {
            "device": str(torch_device),
            "batch": BENCHMARK_PROTOCOL["batch"],
            "warmup": BENCHMARK_PROTOCOL["warmup"],
            "runs": BENCHMARK_PROTOCOL["runs"],
            **latency_summary(samples),
            "peak_memory_mib": torch.cuda.max_memory_allocated(torch_device) / 1024**2,
        },
    }


def _validate_loaded_checkpoint(
    loaded: LoadedFinalCheckpoint,
    *,
    expected_file_sha256: str,
) -> None:
    metadata = loaded.metadata
    if metadata.get("kind") not in {"exact-final-ema", "exact-final-model"}:
        raise ValueError("ACR-BPDD evaluation requires exact-final EMA/model state")
    if metadata.get("completed_epoch") != 100 or metadata.get("raw_epoch") != 99:
        raise ValueError("ACR-BPDD checkpoint is not completed epoch 100/raw epoch99")
    if metadata.get("sha256_verified") is not True or (
        str(metadata.get("sha256", "")).upper() != expected_file_sha256
    ):
        raise ValueError("ACR-BPDD checkpoint file SHA256 was not verified")
    if metadata.get("source_field") not in {"ema", "model"}:
        raise ValueError("ACR-BPDD checkpoint contains neither EMA nor model")
    state_digest = str(metadata.get("ema_state_sha256", "")).upper()
    if len(state_digest) != 64:
        raise ValueError("ACR-BPDD EMA/model tensor-state SHA256 is invalid")
    if metadata.get("strict_fdr_inference_graph") is not True:
        raise ValueError("ACR-BPDD final evaluation must use the ordinary FDR graph")


def evaluate_formal_checkpoint(
    *,
    run_dir: str | Path,
    checkpoint: str | Path,
    publication_ledger: str | Path,
    dataset_root: str | Path,
    split: str = "val",
    fdr_evaluation: str | Path | None = None,
    bpdd_evaluation: str | Path | None = None,
    output: str | Path,
    device: str = "cuda:0",
    checkpoint_loader: Callable[..., LoadedFinalCheckpoint] = load_exact_final_checkpoint,
    validation_runner: Callable[..., dict[str, Any]] = run_official_validation,
    efficiency_runner: Callable[..., dict[str, Any]] = run_efficiency_audit,
    environment_reader: Callable[[str], dict[str, Any]] = execution_environment,
) -> dict[str, Any]:
    output_path = Path(output).resolve()
    if output_path.exists():
        raise FileExistsError(f"refusing to overwrite evaluation: {output_path}")
    checkpoint_path = Path(checkpoint).resolve()
    dataset_path = Path(dataset_root).resolve()
    authority = validate_formal_authority(
        run_dir,
        checkpoint=checkpoint_path,
        publication_ledger=publication_ledger,
    )
    validate_data_yaml(authority["data"], dataset_path)
    split_authority = build_split_authority(dataset_path, split)
    expected_images = int(split_authority["images"]["count"])

    loaded = checkpoint_loader(
        checkpoint_path,
        expected_sha256=authority["checkpoint_sha256"],
    )
    _validate_loaded_checkpoint(
        loaded, expected_file_sha256=authority["checkpoint_sha256"]
    )
    validation = validation_runner(
        loaded.model,
        dataset_root=dataset_path,
        split=split,
        save_dir=output_path.parent / "validator",
        device=device,
        expected_images=expected_images,
    )
    validate_complete_metrics(validation)
    if validation.get("processed_images") != expected_images:
        raise RuntimeError("ACR-BPDD validation processed image count differs from authority")
    if validation.get("prediction_passes") != 1:
        raise RuntimeError("ACR-BPDD validation must use one independent prediction pass")

    efficiency_loaded = checkpoint_loader(
        checkpoint_path,
        expected_sha256=authority["checkpoint_sha256"],
    )
    _validate_loaded_checkpoint(
        efficiency_loaded, expected_file_sha256=authority["checkpoint_sha256"]
    )
    if efficiency_loaded.metadata != loaded.metadata:
        raise ValueError("ACR-BPDD independent efficiency reload differs from evaluation state")
    efficiency = efficiency_runner(efficiency_loaded.model, device=device)
    comparisons = build_cross_run_comparison(
        validation,
        fdr_evaluation=fdr_evaluation,
        bpdd_evaluation=bpdd_evaluation,
    )

    artifacts = dict(authority["artifacts"])
    if fdr_evaluation is not None:
        artifacts["fdr_evaluation"] = artifact_record(fdr_evaluation)
    if bpdd_evaluation is not None:
        artifacts["bpdd_evaluation"] = artifact_record(bpdd_evaluation)
    inventory = {
        "algorithm": "SHA256",
        "scope": "all_immutable_evaluation_inputs",
        "output_self_hash_excluded": True,
        "artifacts": artifacts,
        "tensor_states": {
            "checkpoint_ema_or_model": {
                "source_field": loaded.metadata["source_field"],
                "sha256": loaded.metadata["ema_state_sha256"],
            }
        },
        "dataset_split": split_authority,
    }
    report = {
        "format_version": 1,
        "evaluation_identity": {
            **authority["identity"],
            "completed_epoch": 100,
            "split": split,
            "images": expected_images,
            "labels": int(split_authority["labels"]["count"]),
        },
        "run_authority": {
            "completed_epoch": authority["completed_epoch"],
            "epoch_records": authority["epoch_records"],
            "publication_queue": authority["publication_queue"],
            "publication_ledger": authority["publication_ledger"],
        },
        "checkpoint": dict(loaded.metadata),
        "dataset_authority": split_authority,
        "evaluation_protocol": dict(EVALUATION_PROTOCOL),
        "benchmark_protocol": dict(BENCHMARK_PROTOCOL),
        **validation,
        "efficiency": efficiency,
        "environment": environment_reader(device),
        "comparisons": comparisons,
        "artifact_sha256_inventory": inventory,
    }
    write_create_only_json(output_path, report)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--publication-ledger", type=Path, required=True)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--split", choices=("val", "test"), default="val")
    parser.add_argument("--fdr-evaluation", type=Path)
    parser.add_argument("--bpdd-evaluation", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = evaluate_formal_checkpoint(
        run_dir=args.run_dir,
        checkpoint=args.checkpoint,
        publication_ledger=args.publication_ledger,
        dataset_root=args.dataset_root,
        split=args.split,
        fdr_evaluation=args.fdr_evaluation,
        bpdd_evaluation=args.bpdd_evaluation,
        output=args.output,
        device=args.device,
    )
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Evaluate two or more frozen Ultralytics checkpoints under one exact contract.

The caller supplies an installed source checkout through --code-root.  Importing
the current custom model modules before loading checkpoints lets PyTorch resolve
the project classes without replacing or modifying checkpoint tensors.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from importlib.metadata import version
from pathlib import Path
from typing import Any

try:  # Supports both ``python scripts/...`` and ``import scripts...``.
    from scripts.common_reevaluation import build_manifest, sha256
except ModuleNotFoundError:
    from common_reevaluation import build_manifest, sha256


def parse_checkpoint(value: str) -> tuple[str, Path]:
    name, separator, raw_path = value.partition("=")
    if not separator or not name or not raw_path:
        raise argparse.ArgumentTypeError("checkpoints must use NAME=/absolute/path/to/best.pt")
    if not name.replace("_", "").isalnum():
        raise argparse.ArgumentTypeError("checkpoint names may use letters, digits, and underscores")
    return name, Path(raw_path)


def metric_payload(metrics: Any) -> dict[str, Any]:
    results = getattr(metrics, "results_dict", {})
    if not isinstance(results, dict):
        raise TypeError("Ultralytics validation returned no results dictionary")
    keep = {
        key: float(value)
        for key, value in results.items()
        if isinstance(value, (int, float))
    }
    speed = getattr(metrics, "speed", {})
    if not isinstance(speed, dict):
        speed = {}
    return {"metrics": keep, "speed_ms_per_image": {str(k): float(v) for k, v in speed.items()}}


def load_custom_symbols(code_root: Path) -> None:
    """Register project custom classes only; no weights are loaded here."""
    sys.path.insert(0, str(code_root.resolve()))
    try:
        from src.rtdetr_fdr import register_fdr_module

        register_fdr_module()
    except ModuleNotFoundError as error:
        raise RuntimeError(f"--code-root is not a compatible FDR checkout: {code_root}") from error
    # These imports make checkpoint model classes resolvable when present.  A
    # stock baseline remains valid if a particular optional module is absent.
    for module in ("src.rtdetr_lrs_system", "src.rtdetr_bpdd_capacity_fia"):
        try:
            __import__(module)
        except ModuleNotFoundError:
            continue


def run(args: argparse.Namespace) -> dict[str, Any]:
    names_and_paths = [parse_checkpoint(item) for item in args.checkpoint]
    checkpoints = dict(names_and_paths)
    if len(checkpoints) != len(names_and_paths):
        raise ValueError("checkpoint arm names must be unique")
    manifest = build_manifest(
        dataset=args.dataset,
        data_yaml=args.data_yaml,
        split=args.split,
        imgsz=args.imgsz,
        batch=args.batch,
        workers=args.workers,
        device=args.device,
        checkpoints=checkpoints,
    )
    load_custom_symbols(args.code_root)
    import torch
    from ultralytics import RTDETR

    run_root = args.output_dir.resolve()
    run_root.mkdir(parents=True, exist_ok=False)
    arms: dict[str, Any] = {}
    for arm, checkpoint in names_and_paths:
        frozen_hash = sha256(checkpoint)
        detector = RTDETR(str(checkpoint.resolve()))
        metrics = detector.val(
            data=str(args.data_yaml.resolve()),
            split=args.split,
            imgsz=args.imgsz,
            batch=args.batch,
            workers=args.workers,
            device=args.device,
            conf=args.conf,
            max_det=args.max_det,
            nms=False,
            half=False,
            rect=False,
            cache=False,
            project=str(run_root),
            name=arm,
            exist_ok=False,
            verbose=True,
        )
        if sha256(checkpoint) != frozen_hash:
            raise RuntimeError(f"checkpoint changed while evaluating: {checkpoint}")
        model = detector.model
        arms[arm] = {
            "checkpoint": manifest["checkpoints"][arm],
            "parameters": sum(parameter.numel() for parameter in model.parameters()),
            "metrics": metric_payload(metrics),
        }
        del detector
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    report = {
        **manifest,
        "status": "complete",
        "framework": {
            "python": platform.python_version(),
            "torch": torch.__version__,
            "ultralytics": version("ultralytics"),
            "cuda_available": torch.cuda.is_available(),
            "cuda_device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        },
        "evaluation": {"conf": args.conf, "max_det": args.max_det, "nms": False, "half": False, "rect": False, "cache": False},
        "arms": arms,
    }
    (run_root / "common_evaluation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, choices=("VisDrone", "UAVDT"))
    parser.add_argument("--code-root", type=Path, required=True)
    parser.add_argument("--data-yaml", type=Path, required=True)
    parser.add_argument("--checkpoint", action="append", required=True, help="NAME=/absolute/path/to/checkpoint.pt; repeat")
    parser.add_argument("--output-dir", type=Path, required=True, help="must not already exist")
    parser.add_argument("--split", default="val", choices=("val", "test"))
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--device", default="0")
    parser.add_argument("--conf", type=float, default=0.001)
    parser.add_argument("--max-det", type=int, default=300)
    print(json.dumps(run(parser.parse_args()), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

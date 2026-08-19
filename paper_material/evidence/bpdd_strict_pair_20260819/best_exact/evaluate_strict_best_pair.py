"""Evaluate one strict-pair best checkpoint on one frozen VisDrone split."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


# The later audit checkout adds only the evaluator helper; the model-definition
# files used to deserialize these checkpoints are byte-identical to 848f00cb.
SOURCE = Path("/data/uav/source/uav-detection-baselines-2997705c")
sys.path.insert(0, str(SOURCE))

from ultralytics import RTDETR  # noqa: E402
from src.bpdd_formal_evaluation import (  # noqa: E402
    CachedScaleRTDETRValidator,
    summarize_native_box_metrics,
    summarize_scale_metrics,
)
from src.lpr_protocol import CATEGORY_NAMES  # noqa: E402
from src.rtdetr_fdr import FDRRTDETRDetectionModel  # noqa: E402
from src.rtdetr_fdr_bpdd import FDRBPDDDetectionModel  # noqa: E402


CHECKPOINTS = {
    "fdr": {
        "path": Path(
            "/data/uav/runs/bpdd-formal-848f00cb/"
            "formal-seed0-fdr-bpdd-v1/weights/best.pt"
        ),
        "sha256": "d2b6407bd291bf5d6a0e1651c99894a27bb4d8f293c82cd92e404060d6780d82",
        "expected_type": FDRRTDETRDetectionModel,
        "best_epoch": 97,
    },
    "fdr_bpdd": {
        "path": Path(
            "/data/uav/runs/bpdd-formal-848f00cb/"
            "formal-seed0-fdr_bpdd-bpdd-v1/weights/best.pt"
        ),
        "sha256": "8c7fee3cff1c3f84210f694b1f080115b16948104f6c4bd181652fd4a3667f35",
        "expected_type": FDRBPDDDetectionModel,
        "best_epoch": 93,
    },
}

SPLITS = {
    "val": {
        "data": Path(
            "/data/uav/runs/bpdd-formal-848f00cb/_bpdd-authority/formal-data.yaml"
        ),
        "images": 548,
        "instances": 38759,
    },
    "test": {
        "data": Path("/data/uav/evidence/strict-control-test-d97e1eb7/test-data.yaml"),
        "images": 1610,
        "instances": 75102,
    },
}

PROTOCOL = {
    "imgsz": 640,
    "batch": 8,
    "workers": 8,
    "conf": 0.001,
    "max_det": 300,
    "nms": False,
    "device": "0",
    "cache": False,
    "half": False,
    "rect": False,
    "plots": False,
    "save_json": False,
    "save_txt": False,
    "verbose": True,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=sorted(CHECKPOINTS), required=True)
    parser.add_argument("--split", choices=sorted(SPLITS), required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    checkpoint = CHECKPOINTS[args.variant]
    split = SPLITS[args.split]
    checkpoint_path = checkpoint["path"]
    actual_sha = sha256(checkpoint_path)
    if actual_sha != checkpoint["sha256"]:
        raise RuntimeError(f"checkpoint SHA mismatch: {actual_sha}")

    save_dir = args.output_root / f"{args.variant}_{args.split}" / "validator"
    output = args.output_root / f"{args.variant}_{args.split}.json"
    if output.exists():
        raise FileExistsError(output)

    wrapper = RTDETR(str(checkpoint_path))
    if type(wrapper.model) is not checkpoint["expected_type"]:
        raise TypeError(type(wrapper.model))

    validator = CachedScaleRTDETRValidator(
        save_dir=save_dir,
        args={
            "model": str(checkpoint_path),
            "data": str(split["data"]),
            "task": "detect",
            "mode": "val",
            "split": args.split,
            **PROTOCOL,
        },
    )
    validator(model=wrapper.model)
    processed = len(validator.scale_targets)
    if processed != split["images"] or len(validator.scale_predictions) != processed:
        raise RuntimeError(
            f"processed {processed} images instead of {split['images']}"
        )

    report = {
        "format_version": 1,
        "experiment_id": "bpdd_strict_pair_20260819_best_exact_evaluation",
        "source_commit": "848f00cb7a40907e3884885ecd5bbd474450758a",
        "variant": args.variant,
        "split": args.split,
        "best_epoch": checkpoint["best_epoch"],
        "checkpoint": {
            "path": str(checkpoint_path),
            "sha256": actual_sha,
            "model_type": f"{type(wrapper.model).__module__}.{type(wrapper.model).__name__}",
        },
        "dataset": {
            "data_yaml": str(split["data"]),
            "images": split["images"],
            "instances": split["instances"],
        },
        "evaluation_protocol": {**PROTOCOL, "split": args.split},
        **summarize_native_box_metrics(validator.metrics.box, CATEGORY_NAMES),
        **summarize_scale_metrics(
            validator.scale_predictions,
            validator.scale_targets,
            class_count=len(CATEGORY_NAMES),
        ),
        "processed_images": processed,
        "prediction_passes": 1,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    print("STRICT_BEST_EVAL_COMPLETE")
    print(json.dumps({"variant": args.variant, "split": args.split, "metrics": report["metrics"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

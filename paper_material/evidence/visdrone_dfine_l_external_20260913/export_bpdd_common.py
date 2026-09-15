"""Export a Capacity-BPDD-only checkpoint with the common PIL/FP32 contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Mapping
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from export_dfine_predictions import _sha256, preprocess_image  # noqa: E402
from prediction_contract import stretch_boxes_to_original, validate_row, write_jsonl  # noqa: E402


def checkpoint_state(artifact: Mapping[str, object]) -> dict[str, object]:
    source = artifact.get("ema") or artifact.get("model")
    if source is None:
        raise ValueError("checkpoint has no EMA/model state")
    if hasattr(source, "state_dict"):
        state = source.state_dict()
    elif isinstance(source, Mapping):
        state = source.get("state_dict", source)
    else:
        raise ValueError("checkpoint state is not loadable")
    if not isinstance(state, Mapping) or not state:
        raise ValueError("checkpoint state is empty")
    return dict(state)


def load_bpdd_model(code_root: Path, model_yaml: Path, checkpoint: Path):
    sys.path.insert(0, str(code_root.resolve()))
    import torch
    from src.rtdetr_bpdd_capacity import CapacityBPDDDetectionModel
    from src.rtdetr_fdr import register_fdr_module

    register_fdr_module()
    model = CapacityBPDDDetectionModel(
        cfg=model_yaml, ch=3, nc=10, verbose=False, private_seed=10_000
    )
    artifact = torch.load(checkpoint, map_location="cpu", weights_only=False)
    if not isinstance(artifact, Mapping):
        raise ValueError("checkpoint must be a mapping")
    incompatible = model.load_state_dict(checkpoint_state(artifact), strict=True)
    if incompatible.missing_keys or incompatible.unexpected_keys:
        raise ValueError("strict BPDD checkpoint loading produced incompatible keys")
    model.eval()
    return model, {
        "model_class": type(model).__name__,
        "model_yaml": str(model_yaml.resolve()),
        "model_yaml_sha256": _sha256(model_yaml),
        "checkpoint": str(checkpoint.resolve()),
        "checkpoint_sha256": _sha256(checkpoint),
        "checkpoint_epoch": artifact.get("epoch"),
        "source_field": "ema" if artifact.get("ema") is not None else "model",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--code-root", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--model-yaml", type=Path, required=True)
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--score-threshold", type=float, default=0.001)
    args = parser.parse_args()

    import torch
    from ultralytics.models.rtdetr.val import RTDETRValidator

    initial_sha = _sha256(args.checkpoint)
    model, metadata = load_bpdd_model(args.code_root, args.model_yaml, args.checkpoint)
    model = model.float().to(args.device).eval()
    decoder = RTDETRValidator(
        save_dir=args.output.parent / "decoder",
        args={"imgsz": 640, "conf": args.score_threshold, "max_det": 300, "single_cls": False},
    )
    rows = []
    with torch.inference_mode():
        image_paths = sorted(
            p for p in args.images.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}
        )
        for path in image_paths:
            from PIL import Image

            with Image.open(path) as source:
                image = source.convert("RGB")
            width, height = image.size
            tensor = preprocess_image(image).unsqueeze(0).to(args.device)
            pred = decoder.postprocess(model(tensor))[0]
            boxes = stretch_boxes_to_original(pred["bboxes"], width, height).cpu()
            scores = pred["conf"].detach().cpu()
            classes = pred["cls"].detach().cpu()
            indices = scores.argsort(descending=True)[:300]
            rows.append(
                validate_row(
                    {
                        "image_id": path.stem,
                        "width": width,
                        "height": height,
                        "detections": [
                            {
                                "bbox_xyxy": boxes[i].tolist(),
                                "score": float(scores[i]),
                                "category_id": int(classes[i]),
                            }
                            for i in indices
                            if float(scores[i]) > args.score_threshold
                        ],
                    }
                )
            )
    write_jsonl(args.output, rows)
    if _sha256(args.checkpoint) != initial_sha:
        raise AssertionError("read-only checkpoint changed")
    report = {
        "status": "complete",
        "framework": "Ultralytics",
        "variant": "LRS-GFDR + Capacity-BPDD-v3-Safe (BPDD-only)",
        "processed_images": len(rows),
        "parameters": sum(value.numel() for value in model.parameters()),
        "prediction_sha256": _sha256(args.output),
        "checkpoint": metadata,
        "evaluation": {
            "imgsz": 640,
            "resize": "PIL bilinear stretch_xy",
            "precision": "fp32",
            "conf": args.score_threshold,
            "topk": 300,
            "nms": False,
            "tta": False,
        },
    }
    args.output.with_suffix(".report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

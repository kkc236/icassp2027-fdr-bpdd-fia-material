"""Standalone official D-FINE prediction exporter for VisDrone."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

import torch

from prediction_contract import validate_row, write_jsonl


def dfine_output_to_contract_row(*, labels: torch.Tensor, boxes: torch.Tensor, scores: torch.Tensor,
                                 image_id: str, width: int, height: int) -> dict[str, Any]:
    labels = labels.detach().long().cpu()
    boxes = boxes.detach().float().cpu()
    scores = scores.detach().float().cpu()
    if boxes.ndim != 2 or boxes.shape[-1] != 4 or labels.numel() != boxes.shape[0] or scores.numel() != boxes.shape[0]:
        raise ValueError("D-FINE output tensors have inconsistent shapes")
    return validate_row({
        "image_id": image_id,
        "width": width,
        "height": height,
        "detections": [
            {"bbox_xyxy": [float(value) for value in box], "score": float(score), "category_id": int(label)}
            for label, box, score in zip(labels.tolist(), boxes.tolist(), scores.tolist(), strict=True)
        ],
    })


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _state_from_checkpoint(checkpoint: Mapping[str, Any]) -> dict[str, torch.Tensor]:
    source = checkpoint.get("ema", checkpoint.get("model"))
    if isinstance(source, torch.nn.Module):
        return dict(source.float().state_dict())
    if isinstance(source, Mapping):
        module = source.get("module", source.get("state_dict", source))
        if isinstance(module, Mapping) and all(isinstance(value, torch.Tensor) for value in module.values()):
            return dict(module)
    raise ValueError("D-FINE checkpoint has no loadable tensor state")


class _PadToSize:
    def __init__(self, size: tuple[int, int], fill: int = 114) -> None:
        self.size, self.fill = size, fill

    def __call__(self, image):
        import torchvision.transforms.functional as F
        width, height = F.get_image_size(image)
        return F.pad(image, (0, 0, self.size[0] - width, self.size[1] - height), self.fill)


def export_predictions(*, dfine_root: Path, config: Path, checkpoint: Path, images: Path,
                       output: Path, device: str = "cuda:0", score_threshold: float = 0.0) -> dict[str, Any]:
    sys.path.insert(0, str(dfine_root.resolve()))
    from src.core import YAMLConfig
    import torchvision.transforms as T
    from PIL import Image

    cfg = YAMLConfig(str(config), resume=str(checkpoint), num_classes=10)
    state = _state_from_checkpoint(torch.load(checkpoint, map_location="cpu", weights_only=False))
    cfg.model.load_state_dict(state, strict=True)
    model = cfg.model.deploy().to(device).eval()
    postprocessor = cfg.postprocessor.deploy().to(device).eval()
    transform = T.Compose([
        T.Resize(size=639, max_size=640), _PadToSize((640, 640)), T.ToTensor(),
    ])
    rows: list[dict[str, Any]] = []
    with torch.inference_mode():
        for image_path in sorted(images.glob("*.jpg")):
            image = Image.open(image_path).convert("RGB")
            width, height = image.size
            tensor = transform(image).unsqueeze(0).to(device)
            original_size = torch.tensor([[width, height]], device=device)
            labels, boxes, scores = postprocessor(model(tensor), original_size)
            keep = scores[0] >= score_threshold
            rows.append(dfine_output_to_contract_row(
                labels=labels[0][keep], boxes=boxes[0][keep], scores=scores[0][keep],
                image_id=image_path.stem, width=width, height=height,
            ))
    write_jsonl(output, rows)
    report = {
        "format_version": 1, "status": "complete", "framework": "D-FINE",
        "config": str(config.resolve()), "config_sha256": _sha256(config),
        "checkpoint": str(checkpoint.resolve()), "checkpoint_sha256": _sha256(checkpoint),
        "images": str(images.resolve()), "processed_images": len(rows),
        "prediction_file": str(output.resolve()), "num_classes": 10,
        "postprocess": {"use_focal_loss": True, "num_top_queries": 300, "remap_mscoco_category": False},
    }
    output.with_suffix(".report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dfine-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--score-threshold", type=float, default=0.0)
    args = parser.parse_args()
    print(json.dumps(export_predictions(**vars(args)), indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

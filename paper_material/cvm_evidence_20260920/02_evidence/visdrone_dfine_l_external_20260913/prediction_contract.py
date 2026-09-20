"""Small standalone copy of the cross-framework prediction contract."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping


def stretch_boxes_to_original(boxes, width, height, input_width=640, input_height=640):
    """Invert RT-DETR's independent x/y resize; never apply letterbox offsets."""
    result = boxes.detach().float().clone()
    result[:, [0, 2]] *= float(width) / input_width
    result[:, [1, 3]] *= float(height) / input_height
    return result


def validate_row(row: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(row, Mapping):
        raise ValueError("prediction row must be an object")
    image_id = row.get("image_id")
    if not isinstance(image_id, (str, int)) or isinstance(image_id, bool) or str(image_id) == "":
        raise ValueError("image_id must be non-empty")
    width, height = float(row.get("width")), float(row.get("height"))
    if not math.isfinite(width) or not math.isfinite(height) or width <= 0 or height <= 0:
        raise ValueError("image dimensions must be positive finite numbers")
    detections = row.get("detections")
    if not isinstance(detections, list):
        raise ValueError("detections must be a list")
    normalized = []
    for det in detections:
        if not isinstance(det, Mapping) or not isinstance(det.get("bbox_xyxy"), (list, tuple)):
            raise ValueError("invalid detection")
        box = [float(value) for value in det["bbox_xyxy"]]
        score = float(det["score"])
        category = int(det["category_id"])
        if len(box) != 4 or not all(math.isfinite(value) for value in box):
            raise ValueError("bbox_xyxy must contain four finite values")
        if box[2] < box[0] or box[3] < box[1] or not 0 <= score <= 1 or not 0 <= category < 10:
            raise ValueError("invalid bbox, score, or category_id")
        normalized.append({"bbox_xyxy": box, "score": score, "category_id": category})
    return {"image_id": str(image_id), "width": width, "height": height, "detections": normalized}


def write_jsonl(path: str | Path, rows: Iterable[Mapping[str, Any]]) -> Path:
    destination = Path(path).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    seen: set[str] = set()
    payload: list[str] = []
    for row in rows:
        normalized = validate_row(row)
        if normalized["image_id"] in seen:
            raise ValueError(f"duplicate image_id: {normalized['image_id']}")
        seen.add(normalized["image_id"])
        payload.append(json.dumps(normalized, ensure_ascii=False, sort_keys=True))
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.write_text("\n".join(payload) + ("\n" if payload else ""), encoding="utf-8", newline="\n")
    temporary.replace(destination)
    return destination

"""Deterministically convert the project's VisDrone YOLO labels to COCO."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Iterable

from PIL import Image


CATEGORY_NAMES = (
    "pedestrian",
    "people",
    "bicycle",
    "car",
    "van",
    "truck",
    "tricycle",
    "awning-tricycle",
    "bus",
    "motor",
)
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}
BOUNDARY_EPSILON = 1e-6


def _images_for_split(root: Path, split: str) -> list[Path]:
    image_dir = root / "images" / split
    if not image_dir.is_dir():
        raise FileNotFoundError(f"image split does not exist: {image_dir}")
    images = sorted(
        (path for path in image_dir.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES),
        key=lambda path: path.name,
    )
    if not images:
        raise ValueError(f"image split is empty: {image_dir}")
    return images


def _parse_label_line(line: str, path: Path, line_number: int) -> tuple[int, float, float, float, float]:
    fields = line.split()
    if len(fields) != 5:
        raise ValueError(f"{path}:{line_number}: expected class cx cy w h")
    try:
        category, cx, cy, width, height = int(fields[0]), *(float(value) for value in fields[1:])
    except ValueError as exc:
        raise ValueError(f"{path}:{line_number}: non-numeric label") from exc
    if not 0 <= category < len(CATEGORY_NAMES):
        raise ValueError(f"{path}:{line_number}: class id outside 0..9")
    values = (cx, cy, width, height)
    if not all(math.isfinite(value) for value in values):
        raise ValueError(f"{path}:{line_number}: normalized values must be finite")
    if width <= 0 or height <= 0 or width > 1 or height > 1:
        raise ValueError(f"{path}:{line_number}: normalized width/height outside (0,1]")
    if not 0 <= cx <= 1 or not 0 <= cy <= 1:
        raise ValueError(f"{path}:{line_number}: normalized center outside [0,1]")
    if (
        cx - width / 2 < -BOUNDARY_EPSILON
        or cx + width / 2 > 1 + BOUNDARY_EPSILON
        or cy - height / 2 < -BOUNDARY_EPSILON
        or cy + height / 2 > 1 + BOUNDARY_EPSILON
    ):
        raise ValueError(f"{path}:{line_number}: normalized box extends outside image")
    return category, cx, cy, width, height


def _read_labels(label_path: Path, image_path: Path, image_width: int, image_height: int) -> list[dict[str, Any]]:
    if not label_path.is_file():
        raise FileNotFoundError(f"missing label file for {image_path.name}: {label_path}")
    annotations: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(label_path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line:
            continue
        category, cx, cy, width, height = _parse_label_line(line, label_path, line_number)
        # A few source labels land 5e-7 outside the boundary due to decimal
        # rounding (e.g. ``cy + h/2 == 1.0000005``).  Keep the original YOLO
        # files untouched, but clip only this numerical noise in the COCO
        # projection so D-FINE receives valid pixel boxes.
        x0 = max(0.0, cx - width / 2)
        y0 = max(0.0, cy - height / 2)
        x1 = min(1.0, cx + width / 2)
        y1 = min(1.0, cy + height / 2)
        x, y = x0 * image_width, y0 * image_height
        box_width, box_height = (x1 - x0) * image_width, (y1 - y0) * image_height
        annotations.append({
            "area": box_width * box_height,
            "bbox": [x, y, box_width, box_height],
            "category_id": category,
            "iscrowd": 0,
            "segmentation": [],
        })
    return annotations


def convert_split(root: Path, split: str, output: Path) -> dict[str, Any]:
    """Convert one split and return the exact COCO payload written to ``output``."""

    root, output = Path(root), Path(output)
    images: list[dict[str, Any]] = []
    annotations: list[dict[str, Any]] = []
    for image_id, image_path in enumerate(_images_for_split(root, split), 1):
        with Image.open(image_path) as image:
            width, height = image.size
        images.append({"file_name": image_path.name, "height": height, "id": image_id, "width": width})
        for annotation in _read_labels(root / "labels" / split / f"{image_path.stem}.txt", image_path, width, height):
            annotation["id"] = len(annotations) + 1
            annotation["image_id"] = image_id
            annotations.append(annotation)
    payload = {
        "annotations": annotations,
        "categories": [
            {"id": category_id, "name": name, "supercategory": "object"}
            for category_id, name in enumerate(CATEGORY_NAMES)
        ],
        "images": images,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    temporary.replace(output)
    return payload


def convert_dataset(root: Path, output_dir: Path, splits: Iterable[str] = ("train", "val", "test")) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for split in splits:
        payload = convert_split(root, split, Path(output_dir) / f"instances_{split}.json")
        summary[split] = {"images": len(payload["images"]), "annotations": len(payload["annotations"])}
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--splits", nargs="+", default=["train", "val", "test"])
    args = parser.parse_args()
    summary = convert_dataset(args.dataset_root, args.output_dir, args.splits)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

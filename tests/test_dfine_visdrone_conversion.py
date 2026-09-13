from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
from PIL import Image


MODULE_PATH = (
    Path(__file__).parents[1]
    / "paper_material"
    / "evidence"
    / "visdrone_dfine_l_external_20260913"
    / "convert_visdrone_yolo_to_coco.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("visdrone_converter", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _make_dataset(root: Path) -> None:
    image_dir = root / "images" / "train"
    label_dir = root / "labels" / "train"
    image_dir.mkdir(parents=True)
    label_dir.mkdir(parents=True)
    Image.new("RGB", (100, 50), "white").save(image_dir / "b.jpg")
    Image.new("RGB", (80, 80), "white").save(image_dir / "a.jpg")
    (label_dir / "a.txt").write_text("3 0.5 0.5 0.2 0.4\n", encoding="utf-8")
    (label_dir / "b.txt").write_text("", encoding="utf-8")


def test_convert_split_is_deterministic_and_uses_pixel_xywh(tmp_path: Path) -> None:
    module = _load_module()
    _make_dataset(tmp_path)
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"

    module.convert_split(tmp_path, "train", first)
    module.convert_split(tmp_path, "train", second)

    assert first.read_bytes() == second.read_bytes()
    payload = json.loads(first.read_text(encoding="utf-8"))
    assert [image["file_name"] for image in payload["images"]] == ["a.jpg", "b.jpg"]
    assert payload["categories"][3] == {"id": 3, "name": "car", "supercategory": "object"}
    assert payload["annotations"] == [
        {
            "area": pytest.approx(16 * 32),
            "bbox": [pytest.approx(32.0), pytest.approx(24.0), pytest.approx(16.0), pytest.approx(32.0)],
            "category_id": 3,
            "id": 1,
            "image_id": 1,
            "iscrowd": 0,
            "segmentation": [],
        }
    ]


def test_convert_split_rejects_invalid_class_and_box(tmp_path: Path) -> None:
    module = _load_module()
    _make_dataset(tmp_path)
    (tmp_path / "labels" / "train" / "a.txt").write_text("10 0.5 0.5 0.2 0.4\n", encoding="utf-8")
    with pytest.raises(ValueError, match="class"):
        module.convert_split(tmp_path, "train", tmp_path / "out.json")

    (tmp_path / "labels" / "train" / "a.txt").write_text("3 0.5 0.5 1.2 0.4\n", encoding="utf-8")
    with pytest.raises(ValueError, match="normalized"):
        module.convert_split(tmp_path, "train", tmp_path / "out.json")


def test_convert_split_rejects_missing_label_file(tmp_path: Path) -> None:
    module = _load_module()
    _make_dataset(tmp_path)
    (tmp_path / "labels" / "train" / "a.txt").unlink()
    with pytest.raises(FileNotFoundError, match="a.txt"):
        module.convert_split(tmp_path, "train", tmp_path / "out.json")


def test_convert_split_clips_rounding_noise_at_image_boundary(tmp_path: Path) -> None:
    module = _load_module()
    _make_dataset(tmp_path)
    (tmp_path / "labels" / "train" / "a.txt").write_text(
        "3 0.5 0.98000025 0.2 0.0400005\n", encoding="utf-8"
    )
    module.convert_split(tmp_path, "train", tmp_path / "out.json")
    payload = json.loads((tmp_path / "out.json").read_text(encoding="utf-8"))
    annotation = payload["annotations"][0]
    assert annotation["bbox"][1] == pytest.approx(76.8)
    assert annotation["bbox"][3] == pytest.approx(3.2)

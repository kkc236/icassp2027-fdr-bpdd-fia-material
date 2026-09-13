from __future__ import annotations

import sys
from pathlib import Path

import pytest

PACKAGE = Path(__file__).parents[1] / "paper_material" / "evidence" / "visdrone_dfine_l_external_20260913"
sys.path.insert(0, str(PACKAGE))

from evaluate_common import predictions_to_coco, validate_image_coverage  # noqa: E402


def _row(image_id: str) -> dict:
    return {
        "image_id": image_id,
        "width": 640.0,
        "height": 480.0,
        "detections": [{"bbox_xyxy": [1.0, 2.0, 21.0, 32.0], "score": 0.8, "category_id": 2}],
    }


def test_predictions_to_coco_uses_xywh_and_zero_based_category_mapping() -> None:
    result = predictions_to_coco([_row("7")])
    assert result == [{"image_id": 7, "category_id": 2, "bbox": [1.0, 2.0, 20.0, 30.0], "score": 0.8}]


def test_validate_image_coverage_rejects_missing_and_duplicate_ids() -> None:
    with pytest.raises(ValueError, match="missing"):
        validate_image_coverage([_row("1")], ["1", "2"])
    with pytest.raises(ValueError, match="duplicate"):
        validate_image_coverage([_row("1"), _row("1")], ["1"])

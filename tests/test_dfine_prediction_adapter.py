from __future__ import annotations

import sys
from pathlib import Path

import pytest
import torch

PACKAGE = Path(__file__).parents[1] / "paper_material" / "evidence" / "visdrone_dfine_l_external_20260913"
sys.path.insert(0, str(PACKAGE))

from export_dfine_predictions import dfine_output_to_contract_row, disable_external_pretraining  # noqa: E402


def test_dfine_output_uses_native_pixel_xyxy_and_zero_based_labels() -> None:
    row = dfine_output_to_contract_row(
        labels=torch.tensor([2, 9]),
        boxes=torch.tensor([[1.0, 2.0, 20.0, 30.0], [0.0, 0.0, 10.0, 10.0]]),
        scores=torch.tensor([0.8, 0.2]),
        image_id="000007",
        width=640,
        height=480,
    )
    assert row["image_id"] == "000007"
    assert row["detections"][0]["category_id"] == 2
    assert row["detections"][0]["bbox_xyxy"] == [1.0, 2.0, 20.0, 30.0]


def test_dfine_output_rejects_category_outside_visdrone() -> None:
    with pytest.raises(ValueError, match="category_id"):
        dfine_output_to_contract_row(
            labels=torch.tensor([10]),
            boxes=torch.tensor([[1.0, 2.0, 20.0, 30.0]]),
            scores=torch.tensor([0.8]),
            image_id="000007",
            width=640,
            height=480,
        )


def test_checkpoint_loading_disables_external_hgnet_pretraining() -> None:
    config = {"HGNetv2": {"pretrained": True}}
    disable_external_pretraining(config)
    assert config["HGNetv2"]["pretrained"] is False

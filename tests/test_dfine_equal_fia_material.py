import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATERIAL = ROOT / "paper_material"
EVIDENCE = MATERIAL / "evidence" / "dfine_s_equal_fia_matched_20260823"
PROTOCOL = EVIDENCE / "protocol.json"
CONTROL = EVIDENCE / "control"
EXPERIMENT = MATERIAL / "experiments" / "DFINE_EQUAL_FIA_MATCHED_PROTOCOL_ZH.md"

CONTROL_ARTIFACT_HASHES = {
    "best_checkpoint.json": "a21ce60f4d3decdee7f950e05e29e03649a37c006c4575464ca5d3ca7944caef",
    "protocol_correction.json": "f269da009e701de1b22cf5afdccd87614be625d7d335585853c949ce5675127a",
    "protocol_manifest.json": "33888cd44d369ccaf9797819ea2c5fde85ea7dadaeb0d32e5ea7a749a386b8f5",
    "training_completion.json": "e8f94b44203464cd073e8446754a852132c09791fd412ded068026085a79e193",
    "training_config.yml": "d6276a2801e1bf6972e019116abf8e6450e8b1cc174b445f1a3fe4e71dc102fd",
    "training_log.jsonl": "87f73a4fd7095edb455b293d66611bf3e4dee4b7ff9949998d7bf5d4cd93dd59",
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_text_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def test_matched_protocol_binds_existing_control_evidence() -> None:
    protocol = _load_json(PROTOCOL)

    assert protocol["format_version"] == 1
    assert protocol["protocol_id"] == "dfine-s-vs-dfine-s-equal-fia-visdrone-seed0-20260823"
    assert protocol["dataset"]["name"] == "VisDrone2019-DET"
    assert protocol["dataset"]["train"] == {
        "images": 6471,
        "instances": 343204,
        "annotation_sha256": "e21b7109def110cec00c74d9fa95db590995b93e2633cb31abf3bc0b45b5c65c",
    }
    assert protocol["dataset"]["val"] == {
        "images": 548,
        "instances": 38759,
        "annotation_sha256": "200d58fffda1ab131548ba1a978b2f59be410d6a95b5adadc4075912cdcca477",
    }
    assert protocol["dataset"]["test"] == {
        "images": 1610,
        "instances": 75102,
        "annotation_sha256": "b699bf1b9e1e366fef481bb561b8c79b1dc2e1da81be437b598b0dd6d0fa3fd7",
        "authority": "local_held_out",
        "official_challenge_server": False,
    }

    assert protocol["shared_training_protocol"] == {
        "seed": 0,
        "epochs": 132,
        "image_size": 640,
        "total_batch_size": 8,
        "effective_train_workers": 4,
        "effective_val_workers": 4,
        "amp": True,
        "ema": True,
        "pretrained_backbone_sha256": "70a372e8cbc59b34c5da2943261ecb633faf304a58e7e05461a27bd8d8b7f3d1",
    }
    assert protocol["shared_evaluation_protocol"] == {
        "evaluator": "pycocotools.COCOeval",
        "iou_type": "bbox",
        "max_dets": [1, 10, 100],
        "primary_max_dets": 100,
        "best_checkpoint_selection_split": "val",
        "best_checkpoint_selection_metric": "COCO_AP50_95",
        "test_used_for_model_selection": False,
        "same_evaluator_for_both_arms": True,
    }

    arms = protocol["arms"]
    assert arms["control"]["method"] == "D-FINE-S official"
    assert arms["control"]["source_commit"] == "7fe2f8889f0b7b817f20c315b40fc15a4fb64ae6"
    assert arms["treatment"]["method"] == "D-FINE-S + EQuAL + FIA"
    assert arms["treatment"]["source_commit"] == "24c9cb1fba1357b5930f483a26f9e2d787a4e7ef"

    comparison = protocol["comparison_contract"]
    assert comparison["strict_paired"] is False
    assert comparison["matched_protocol_dimensions"] == [
        "dataset",
        "pretrained_backbone",
        "seed",
        "epochs",
        "image_size",
        "batch_size",
        "effective_workers",
        "amp",
        "ema",
        "evaluator",
    ]
    assert comparison["non_strict_reason"] == "different_source_commits"
    assert comparison["default_off_regression"]["verified"] is True
    assert comparison["default_off_regression"]["does_not_make_strict_pair"] is True

    boundary = protocol["bundle_attribution_boundary"]
    assert boundary["claim_unit"] == "EQuAL+FIA bundle on D-FINE-S"
    assert boundary["isolated_equal_gain_claim_allowed"] is False
    assert boundary["isolated_fia_gain_claim_allowed"] is False
    assert boundary["component_attribution_requires_dedicated_ablation"] is True

    for name, expected_sha256 in CONTROL_ARTIFACT_HASHES.items():
        assert (CONTROL / name).is_file(), name
        assert _git_text_sha256(CONTROL / name) == expected_sha256


def test_matched_protocol_explains_selection_metrics_and_claim_boundaries() -> None:
    text = EXPERIMENT.read_text(encoding="utf-8")

    for required in (
        "val 选择 best",
        "test 不参与选模",
        "统一 COCO evaluator",
        "maxDets=100",
        "P/R/F1",
        "不与 COCO AP 混用",
        "local held-out",
        "不是 VisDrone challenge server",
        "strict_paired=false",
        "不同 source commit",
        "default-off 回归",
        "EQuAL+FIA bundle",
        "不能拆分归因",
    ):
        assert required in text

    assert "最终结果" not in text
    assert "处理臂优于" not in text

import csv
import hashlib
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MATERIAL = ROOT / "paper_material"
EVIDENCE = MATERIAL / "evidence" / "equal_formal100_20260821"

CHECKPOINT_SHA256 = "06c5809af89c9a6b944f8615ac4a92c28322b36db6eb872c73407a58e54c3bca"
SOURCE_COMMIT = "fca7763679b6e10ed68f98971a362a054ecd4853"

EXPECTED = {
    "val": {
        "images": 548,
        "instances": 38_759,
        "precision": 0.5940546227482266,
        "recall": 0.48866551561492555,
        "f1": 0.5362309210717304,
        "map50": 0.49047659360905327,
        "map75": 0.3010264455466055,
        "map": 0.29437802106009,
    },
    "test": {
        "images": 1_610,
        "instances": 75_102,
        "precision": 0.5215760478832335,
        "recall": 0.4288392988126689,
        "f1": 0.47068328058742026,
        "map50": 0.40624635226953254,
        "map75": 0.2353634277327714,
        "map": 0.23460964111033686,
    },
}

AP_FDR_REFERENCE = {
    "val": {
        "source_id": "fdr_val",
        "precision": 0.56911,
        "recall": 0.49278,
        "map50": 0.48468,
        "map75": 0.29253,
        "map": 0.28966,
    },
    "test": {
        "source_id": "fdr_test_exact",
        "precision": 0.5034013232722852,
        "recall": 0.4316771784011883,
        "map50": 0.3983397033621551,
        "map75": 0.2289027217475196,
        "map": 0.2280010020468384,
    },
}

ARTIFACT_HASHES = {
    "args.yaml": "42f22ddf2d4c85a8232f12ed5d71c53b053f4abc76f07e3b142bd46237b8781f",
    "results.csv": "8c9939380832aaf31ae0c0ae8a441d06aa8f2e759208c7c66bc8282e831a531d",
    "completion-manifest.json": "c044ae6a45aec29d809f2c7e22e1c6ff4ac7c85899c14eed9e6c92217e659106",
    "equal_val.json": "3990a5ee856407f5007f044988ec1c1fdc99c9f2783fcf5c0de48e6a8145e7a4",
    "equal_test.json": "5b34545d662255b852a63a8e59104976d7d686c76df20328a379548a99d1452b",
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_equal_raw_evidence_is_present_and_byte_bound() -> None:
    for name, expected_hash in ARTIFACT_HASHES.items():
        path = EVIDENCE / name
        assert path.is_file(), name
        assert _sha256(path) == expected_hash


@pytest.mark.parametrize("split", ["val", "test"])
def test_equal_exact_evaluations_match_the_frozen_best_checkpoint(split: str) -> None:
    record = _load_json(EVIDENCE / f"equal_{split}.json")
    expected = EXPECTED[split]

    assert record["paper_method"] == "equal"
    assert record["raw_runtime_method"] == "ace_fdr"
    assert record["source_commit"] == SOURCE_COMMIT
    assert record["best_epoch"] == 91
    assert record["checkpoint"]["sha256"] == CHECKPOINT_SHA256
    assert record["checkpoint"]["bytes"] == 67_288_254
    assert record["split"] == split
    assert record["dataset"]["images"] == expected["images"]
    assert record["dataset"]["instances"] == expected["instances"]
    assert record["processed_images"] == expected["images"]
    assert record["prediction_passes"] == 1
    assert record["evaluation_protocol"] == {
        "batch": 8,
        "cache": False,
        "conf": 0.001,
        "device": "0",
        "half": False,
        "imgsz": 640,
        "max_det": 300,
        "nms": False,
        "plots": False,
        "rect": False,
        "save_json": False,
        "save_txt": False,
        "split": split,
        "verbose": True,
        "workers": 8,
    }
    for metric in ("precision", "recall", "f1", "map50", "map75", "map"):
        assert record["metrics"][metric] == pytest.approx(expected[metric], abs=1e-15)
    assert len(record["class_details"]) == 10
    assert set(record["scale_details"]) == {"tiny", "small", "medium", "large"}


def test_equal_completion_manifest_binds_the_same_val_and_test() -> None:
    manifest = _load_json(EVIDENCE / "completion-manifest.json")
    assert manifest["status"] == "complete"
    assert manifest["best_epoch"] == 91
    assert manifest["checkpoint_sha256"] == CHECKPOINT_SHA256
    for split in ("val", "test"):
        for metric, value in EXPECTED[split].items():
            if metric not in {"images", "instances"}:
                assert manifest["metrics"][split][metric] == pytest.approx(value, abs=1e-15)


def test_equal_machine_summary_keeps_comparison_and_adoption_boundaries() -> None:
    summary = _load_json(MATERIAL / "results" / "equal_results.json")
    assert summary["paper_method"] == "EQuAL"
    assert summary["expansion"] == "Edge-adaptive Query-Aligned Localization"
    assert summary["raw_runtime_method"] == "ACE-FDR"
    assert summary["source_commit"] == SOURCE_COMMIT
    assert summary["checkpoint_sha256"] == CHECKPOINT_SHA256
    assert summary["best_epoch"] == 91
    assert summary["adoption"]["standalone_gate"] == "pass"
    assert summary["adoption"]["paper_system_status"] == "combination_retraining_pending"
    assert summary["adoption"]["old_ap_fdr_combinations_relabel_allowed"] is False

    for split in ("val", "test"):
        assert summary["exact_metrics"][split] == EXPECTED[split]
        comparison = summary["ap_fdr_registered_comparison"][split]
        assert comparison["reference_source_id"] == AP_FDR_REFERENCE[split]["source_id"]
        assert comparison["strict_paired"] is False
        for metric in ("precision", "recall", "map50", "map75", "map"):
            expected_delta = (EXPECTED[split][metric] - AP_FDR_REFERENCE[split][metric]) * 100
            assert comparison["delta_pp"][metric] == pytest.approx(expected_delta, abs=1e-12)


def test_equal_class_csv_is_a_lossless_projection_of_raw_evidence() -> None:
    csv_path = MATERIAL / "results" / "equal_class_results.csv"
    with csv_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 20
    for split in ("val", "test"):
        raw = _load_json(EVIDENCE / f"equal_{split}.json")
        split_rows = {row["class"]: row for row in rows if row["split"] == split}
        assert set(split_rows) == set(raw["class_details"])
        for class_name, metrics in raw["class_details"].items():
            row = split_rows[class_name]
            assert int(row["class_id"]) == metrics["id"]
            assert float(row["map50"]) == metrics["map50"]
            assert float(row["map75"]) == metrics["map75"]
            assert float(row["map"]) == metrics["map"]


def test_equal_is_linked_from_the_material_entry_and_not_mixed_with_old_combinations() -> None:
    readme = (MATERIAL / "README_ZH.md").read_text(encoding="utf-8")
    method = (MATERIAL / "methods" / "EQUAL_ZH.md").read_text(encoding="utf-8")
    result = (MATERIAL / "results" / "EQUAL_RESULTS_ZH.md").read_text(encoding="utf-8")
    protocol = (MATERIAL / "experiments" / "PROTOCOL_ZH.md").read_text(encoding="utf-8")

    assert "methods/EQUAL_ZH.md" in readme
    assert "results/EQUAL_RESULTS_ZH.md" in readme
    assert "results/equal_results.json" in readme
    assert "0.294378" in result and "0.234610" in result
    assert "0.301026" in result and "0.235363" in result
    assert "EQuAL + BPDD" in result and "待重训" in result
    assert "不能" in result and "改名" in result
    assert "preliminary_box: false" in method
    assert "supervise_dn_fdr: false" in method
    assert "edge_adaptive_fgl: true" in method
    assert "EQuAL" in protocol and "best.pt" in protocol


def test_equal_source_manifest_registers_all_imported_artifacts() -> None:
    manifest = _load_json(MATERIAL / "evidence" / "source_manifest.json")
    source = manifest["sources"]["equal_formal100_best_exact_20260821"]
    assert source["source_commit"] == SOURCE_COMMIT
    assert source["paper_method"] == "EQuAL"
    assert source["raw_runtime_method"] == "ACE-FDR"
    assert source["checkpoint_sha256"] == CHECKPOINT_SHA256
    assert source["evidence_level"] == "best_checkpoint_independent_val_and_test_exact"
    assert source["strict_paired"] is False
    assert source["combination_retraining_required"] is True
    assert {item["path"].rsplit("/", 1)[-1]: item["sha256"] for item in source["artifacts"]} == ARTIFACT_HASHES

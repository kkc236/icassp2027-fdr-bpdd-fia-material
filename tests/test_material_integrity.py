import csv
import hashlib
import json
import math
import re
import statistics
import subprocess
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MATERIAL_ROOT = REPOSITORY_ROOT / "paper_material"

REQUIRED_MATERIAL_FILES = (
    "README_ZH.md",
    "methods/FDR_ZH.md",
    "methods/BPDD_ZH.md",
    "methods/FIA_ZH.md",
    "experiments/PROTOCOL_ZH.md",
    "experiments/BPDD_STRICT_PAIR_PROTOCOL_ZH.md",
    "experiments/FIA_ABLATION_SCAFFOLD_ZH.md",
    "evidence/fia_results_status.json",
    "evidence/fia_existing_best_evaluation.json",
    "evidence/fdr_bpdd_fia_val.txt",
    "evidence/fdr_bpdd_fia_test.txt",
    "results/FIA_RESULTS_STATUS_ZH.md",
    "results/RESULTS_ZH.md",
    "results/main_results.json",
    "results/MAIN_TABLE_ZH.md",
    "results/COMPLEXITY_ZH.md",
    "results/complexity_results.json",
    "evidence/unified_complexity_20260820/README.md",
    "evidence/unified_complexity_20260820/unified_complexity_raw.json",
    "evidence/source_manifest.json",
    "evidence/bpdd_val_exact.json",
    "results/SPLIT_GAIN_COMPARISON_ZH.md",
    "results/split_gain_comparison.json",
    "results/split_overall_results.csv",
    "results/split_scale_results.csv",
    "results/split_class_results.csv",
    "results/fia_existing_best_val_results.csv",
    "results/fia_existing_best_test_results.csv",
    "results/fdr_bpdd_fia_text_report_class_results.csv",
    "results/EXTERNAL_VISDRONE_COMPARISON_ZH.md",
    "results/external_visdrone_comparison.json",
    "results/external_visdrone_comparison.csv",
    "writing/ICASSP2027_OUTLINE_ZH.md",
    "figures/FIGURE_PLAN_ZH.md",
)

EXPECTED_METHODS = (
    "RT-DETR-L",
    "RT-DETR-L+FDR",
    "RT-DETR-L+FDR+BPDD",
)


def _tracked_files():
    completed = subprocess.run(
        ["git", "-C", str(REPOSITORY_ROOT), "ls-files", "-z"],
        check=True,
        capture_output=True,
    )
    for encoded_path in completed.stdout.split(b"\0"):
        if not encoded_path:
            continue
        relative_path = encoded_path.decode("utf-8", errors="ignore")
        path = REPOSITORY_ROOT / relative_path
        if path.is_file():
            yield path, relative_path


def _read_required_text(relative_path):
    path = MATERIAL_ROOT / relative_path
    assert path.is_file(), f"missing required material file: {path.relative_to(REPOSITORY_ROOT)}"
    return path.read_text(encoding="utf-8")


def _load_required_json(relative_path):
    return json.loads(_read_required_text(relative_path))


def test_required_material_files_exist():
    missing = [
        str((MATERIAL_ROOT / relative_path).relative_to(REPOSITORY_ROOT))
        for relative_path in REQUIRED_MATERIAL_FILES
        if not (MATERIAL_ROOT / relative_path).is_file()
    ]

    assert not missing, f"missing required material files: {missing}"


def test_existing_best_fia_evaluations_are_registered():
    evidence = _load_required_json("evidence/fia_existing_best_evaluation.json")
    manifest = _load_required_json("evidence/source_manifest.json")

    assert evidence["format_version"] == 1
    assert evidence["dataset"] == {
        "name": "VisDrone",
        "split": "val",
        "images": 548,
        "instances": 38759,
        "data_yaml_sha256": "6cabb57ba5336c1b8a9e43ef376117f06e90d83f998f1e4fe7d1b8c5b2435a71",
    }
    assert evidence["test_dataset"] == {
        "name": "VisDrone",
        "split": "test",
        "images": 1610,
        "instances": 75102,
        "archive_sha256": "b28a94b06dfd9e36ce77ff8155fb82b9d2c030f198a76105933bd56c6ea6a68d",
        "data_yaml_sha256": "f2bf9d335c3306ecc27e4bf7ca86ef35b56a93555cab4397d585fe2dbcb9e4ae",
    }
    assert evidence["evaluation_protocol"] == {
        "imgsz": 640,
        "batch": 8,
        "workers": 8,
        "conf": 0.001,
        "max_det": 300,
        "nms": False,
        "cache": False,
        "half": False,
        "rect": False,
        "checkpoint_selection": "best.pt",
    }

    arms = {arm["variant"]: arm for arm in evidence["arms"]}
    assert set(arms) == {
        "fia_only_p3",
        "fia_only_cascading_superseded",
        "fdr_fia",
    }
    assert arms["fia_only_p3"]["checkpoint_sha256"] == (
        "c00cae89aaeb722854f8c845d14507c3598f75d509c2b12a3222b35a004157a6"
    )
    assert arms["fia_only_cascading_superseded"]["checkpoint_sha256"] == (
        "cf7203733c6d7f66ba8708dfda3b8aa6ac5cd8564bc31b68cde7e8513cf211d9"
    )
    assert arms["fdr_fia"]["checkpoint_sha256"] == (
        "6f624bbc262e840fa6f416486f3813d8ae1c0d9d8daccfb2997f5da6d427d5f1"
    )
    assert arms["fia_only_p3"]["graph_identity"]["p3_only"] is True
    assert arms["fia_only_p3"]["graph_identity"]["layer_23_from"] == 21
    for arm in arms.values():
        assert arm["graph_identity"]["decoder_from"] == [22, 25, 28]
        assert arm["val"]["evidence_level"] == "best_checkpoint_independent_val_exact"
        assert arm["test"]["evidence_level"] == (
            "best_checkpoint_independent_test_exact"
        )
        if arm["test"]["per_class"] is not None:
            assert len(arm["val"]["per_class"]) == 10
            assert len(arm["test"]["per_class"]) == 10
            assert all(
                class_row["f1"] is not None and class_row["map75"] is not None
                for class_row in arm["test"]["per_class"]
            )
        else:
            assert arm["val"]["per_class_status"] == "not_supplied"
            assert arm["test"]["per_class_status"] == "not_supplied"
        assert arm["source_id"] in manifest["sources"]
        source = manifest["sources"][arm["source_id"]]
        assert source["test_evaluation_protocol"]["split"] == "test"
        assert source["independent_test_metrics"] == arm["test"]["metrics"]

    assert arms["fia_only_p3"]["val"]["metrics"]["map"] == 0.22705639514425527
    assert (
        arms["fia_only_cascading_superseded"]["val"]["metrics"]["map"]
        == 0.21679545343355132
    )
    assert arms["fdr_fia"]["val"]["metrics"]["map"] == 0.29494032070762063
    assert arms["fia_only_p3"]["test"]["metrics"] == {
        "precision": 0.4482592209945812,
        "recall": 0.377636033342981,
        "f1": 0.3954178960043504,
        "map50": 0.33664177054432,
        "map75": 0.18201140298044138,
        "map": 0.18551746406283812,
    }
    assert arms["fdr_fia"]["test"]["metrics"] == {
        "precision": 0.5189669713045484,
        "recall": 0.43165506726917735,
        "f1": 0.46065437704605916,
        "map50": 0.4074392932750549,
        "map75": 0.23587873005461435,
        "map": 0.23464538660213996,
    }
    status = _load_required_json("evidence/fia_results_status.json")
    status_arms = status["updated_standalone_results"]
    status_variants = {"fia_only": "fia_only_p3", "fdr_fia": "fdr_fia"}
    for status_variant, evidence_variant in status_variants.items():
        source = manifest["sources"][arms[evidence_variant]["source_id"]]
        assert status_arms[status_variant]["val_metrics"]["f1"] == (
            arms[evidence_variant]["val"]["metrics"]["f1"]
        )
        assert source["metrics"]["f1"] == arms[evidence_variant]["val"]["metrics"]["f1"]
        assert source["evaluation_protocol"]["f1_definition"] == (
            "mean_per_class_result.box.f1"
        )
    assert arms["fia_only_p3"]["val"]["delta_map_pp"] == (
        arms["fia_only_p3"]["val"]["metrics"]["map"] - 0.21911
    ) * 100
    assert arms["fdr_fia"]["val"]["delta_map_pp"] == (
        arms["fdr_fia"]["val"]["metrics"]["map"] - 0.289659749097641
    ) * 100

    csv_path = MATERIAL_ROOT / "results/fia_existing_best_val_results.csv"
    with csv_path.open(encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    assert len(csv_rows) == 3
    assert {row["source_id"] for row in csv_rows} == {
        "fia_p3_only_best_checkpoint_exact",
        "fia_existing_best_independent_val",
        "fdr_fia_existing_best_independent_val",
    }
    csv_by_source = {row["source_id"]: row for row in csv_rows}
    assert csv_by_source["fia_p3_only_best_checkpoint_exact"]["result_status"] == "current"
    assert csv_by_source["fia_existing_best_independent_val"]["result_status"] == (
        "superseded"
    )


def test_fia_only_p3_exact_evaluation_supersedes_cascading_record():
    evidence = _load_required_json("evidence/fia_existing_best_evaluation.json")
    manifest = _load_required_json("evidence/source_manifest.json")
    status = _load_required_json("evidence/fia_results_status.json")

    arms = {arm["variant"]: arm for arm in evidence["arms"]}
    current = arms["fia_only_p3"]
    superseded = arms["fia_only_cascading_superseded"]

    assert current["source_id"] == "fia_p3_only_best_checkpoint_exact"
    assert current["source_commit"] == "118ad631eff93ad806f85ea47819578e6e00bfc5"
    assert current["checkpoint_sha256"] == (
        "c00cae89aaeb722854f8c845d14507c3598f75d509c2b12a3222b35a004157a6"
    )
    assert current["graph_identity"] == {
        "p3_only": True,
        "fia_layer": 22,
        "fia_layer_from": -1,
        "fia_layer_from_raw": -1,
        "fia_layer_from_effective": 21,
        "layer_23_from": 21,
        "decoder_from": [22, 25, 28],
        "topology_label": "p3_only_standalone",
    }
    assert current["val"]["metrics"] == {
        "precision": 0.4871962209136635,
        "recall": 0.42531734343807504,
        "f1": 0.4509443663180429,
        "map50": 0.39874518726363956,
        "map75": 0.2218076018094571,
        "map": 0.22705639514425527,
    }
    assert current["val"]["delta_map_pp"] == 0.7946395144255269
    assert current["test"]["metrics"] == {
        "precision": 0.4482592209945812,
        "recall": 0.377636033342981,
        "f1": 0.3954178960043504,
        "map50": 0.33664177054432,
        "map75": 0.18201140298044138,
        "map": 0.18551746406283812,
    }
    assert current["test"]["delta_reference_source_id"] == (
        "strict_control_test_exact"
    )
    assert current["test"]["delta_map_pp"] == 0.8101032384120604
    assert current["test"]["delta_strict_paired"] is False

    assert superseded["source_id"] == "fia_existing_best_independent_val"
    assert superseded["result_status"] == "superseded"
    assert superseded["superseded_by"] == current["source_id"]

    source = manifest["sources"][current["source_id"]]
    assert source["source_commit"] == current["source_commit"]
    assert source["checkpoint_sha256"] == current["checkpoint_sha256"]
    assert source["graph_identity"] == current["graph_identity"]
    assert source["metrics"] == current["val"]["metrics"]
    assert source["independent_test_metrics"] == current["test"]["metrics"]
    assert {
        manifest["sources"][source_id]["canonical_local_artifact_sha256"]
        for source_id in (
            "fia_p3_only_best_checkpoint_exact",
            "fia_existing_best_independent_val",
            "fdr_fia_existing_best_independent_val",
        )
    } == {"7d75dcdc6bfe23cc9d57e0e2f495b558eed14bd3fc9c29e1de8c2e1a5e65f882"}

    assert status["canonical_fia_only_source_id"] == current["source_id"]
    assert "fia_existing_best_independent_val" in status["superseded_source_ids"]
    assert status["updated_standalone_results"]["fia_only"]["source_id"] == (
        current["source_id"]
    )
    assert status["superseded_standalone_results"]["fia_only_cascading"][
        "source_id"
    ] == "fia_existing_best_independent_val"


def test_fia_only_p3_raw_artifacts_and_per_class_rows_are_reproducible():
    evidence = _load_required_json("evidence/fia_existing_best_evaluation.json")
    manifest = _load_required_json("evidence/source_manifest.json")
    status = _load_required_json("evidence/fia_results_status.json")
    source = manifest["sources"]["fia_p3_only_best_checkpoint_exact"]
    artifact_root = MATERIAL_ROOT / "evidence/fia_p3_only_20260819"
    expected_hashes = {
        "fia-only-p3-val.json": "5e6c3c0a8935f28f017df6a5e0a4ad4d7ade1ae926c55db44a9721f0bc84a625",
        "fia-only-p3-test.json": "653ab5e9fc84c9d0e9826ce455e468f8cd52d6ec78e4327306f07c322ccbab29",
        "graph-identity-normalization.json": "b80a424b1c7d87d8882ca890132048ac99d6718ea27b244f9155ad412991b68f",
    }

    assert source["release_asset"] == {
        "name": "fia-p3-only-final-20260819.tar.gz",
        "asset_id": 520838108,
        "size_bytes": 62725579,
        "sha256": "e3576cb58342c278f6e0ee7d5c46979f57d7a0bd95f3596acdf161f991af87b5",
        "updated_at": "2026-08-19T12:52:19Z",
        "url": "https://github.com/kkc236/uav-detection-baselines/releases/download/DFR-BDPP-FIA/fia-p3-only-final-20260819.tar.gz",
    }
    assert {
        Path(item["path"]).name: item["sha256"] for item in source["artifacts"]
    } == expected_hashes

    raw = {}
    for filename, expected_sha256 in expected_hashes.items():
        path = artifact_root / filename
        assert path.is_file()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected_sha256
        if filename.endswith(".json") and filename.startswith("fia-only"):
            raw[filename] = json.loads(path.read_text(encoding="utf-8"))

    lean_manifest = artifact_root / "MANIFEST.sha256"
    manifest_lines = lean_manifest.read_text(encoding="utf-8").splitlines()
    assert len(manifest_lines) == 18
    assert all("MANIFEST.sha256" not in line for line in manifest_lines)
    for filename, expected_sha256 in expected_hashes.items():
        assert f"{expected_sha256}  ./evaluation/{filename}" in manifest_lines

    arms = {arm["variant"]: arm for arm in evidence["arms"]}
    current = arms["fia_only_p3"]
    val_classes = raw["fia-only-p3-val.json"]["per_class"]
    test_classes = raw["fia-only-p3-test.json"]["per_class"]
    assert len(val_classes) == len(test_classes) == 10
    assert current["val"]["per_class"] == val_classes
    assert current["test"]["per_class"] == test_classes
    assert source["per_class_status"] == "available_exact"
    assert source["per_class_artifacts"] == {
        "val": "paper_material/evidence/fia_p3_only_20260819/fia-only-p3-val.json#per_class",
        "test": "paper_material/evidence/fia_p3_only_20260819/fia-only-p3-test.json#per_class",
        "class_count": 10,
    }
    status_current = status["updated_standalone_results"]["fia_only"]
    assert status_current["per_class_available"] is True
    assert status_current["per_class_count"] == 10
    assert status_current["per_class_artifacts"] == {
        "val": "paper_material/evidence/fia_p3_only_20260819/fia-only-p3-val.json#per_class",
        "test": "paper_material/evidence/fia_p3_only_20260819/fia-only-p3-test.json#per_class",
    }


def test_existing_best_fia_test_csv_matches_exact_evidence():
    evidence = _load_required_json("evidence/fia_existing_best_evaluation.json")
    evidence_arms = {arm["source_id"]: arm for arm in evidence["arms"]}
    expected_counts = {
        "pedestrian": (1197, 21006),
        "people": (797, 6376),
        "bicycle": (377, 1302),
        "car": (1530, 28074),
        "van": (1168, 5771),
        "truck": (750, 2659),
        "tricycle": (245, 530),
        "awning-tricycle": (233, 599),
        "bus": (838, 2940),
        "motor": (794, 5845),
    }

    csv_path = MATERIAL_ROOT / "results/fia_existing_best_test_results.csv"
    with csv_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    expected_row_count = sum(
        1 + (10 if arm["test"]["per_class"] is not None else 0)
        for arm in evidence_arms.values()
    )
    assert len(rows) == expected_row_count
    assert {row["source_id"] for row in rows} == set(evidence_arms)
    assert all(row["split"] == "test" for row in rows)
    assert all(
        row["evidence_level"] == "best_checkpoint_independent_test_exact"
        for row in rows
    )
    assert all(row["map75"] != "" for row in rows)
    assert all(row["f1"] != "" for row in rows)

    for source_id, arm in evidence_arms.items():
        arm_rows = [row for row in rows if row["source_id"] == source_id]
        overall_rows = [row for row in arm_rows if row["scope"] == "overall"]
        class_rows = [row for row in arm_rows if row["scope"] == "class"]
        assert len(overall_rows) == 1
        expected_per_class = arm["test"]["per_class"]
        assert len(class_rows) == (10 if expected_per_class is not None else 0)

        overall = overall_rows[0]
        assert overall["method"] == arm["method"]
        assert overall["class"] == "all"
        assert int(overall["images"]) == arm["test"]["images"]
        assert int(overall["instances"]) == arm["test"]["instances"]
        for metric in ("precision", "recall", "f1", "map50", "map75", "map"):
            assert float(overall[metric]) == arm["test"]["metrics"][metric]

        evidence_classes = {
            class_row["class"]: class_row
            for class_row in (expected_per_class or [])
        }
        if expected_per_class is not None:
            assert {row["class"] for row in class_rows} == set(expected_counts)
        for row in class_rows:
            class_name = row["class"]
            expected = evidence_classes[class_name]
            assert (int(row["images"]), int(row["instances"])) == expected_counts[
                class_name
            ]
            for metric in ("precision", "recall", "f1", "map50", "map75", "map"):
                assert float(row[metric]) == expected[metric]


def test_legacy_third_method_name_is_absent():
    forbidden = bytes((105, 114, 97))
    forbidden_pattern = re.compile(
        rb"(?<![A-Za-z])" + re.escape(forbidden) + rb"(?![A-Za-z])",
        re.IGNORECASE,
    )
    offenders = set()

    for path, relative_path in _tracked_files():
        encoded_path = relative_path.encode("utf-8")
        redacted_path = forbidden_pattern.sub(b"<legacy>", encoded_path).decode(
            "utf-8", errors="ignore"
        )
        if forbidden_pattern.search(encoded_path):
            offenders.add(f"{redacted_path} (filename)")
        if forbidden_pattern.search(path.read_bytes()):
            offenders.add(f"{redacted_path} (content)")

    assert not offenders, f"legacy third-method token found in: {sorted(offenders)}"


def test_main_results_are_bound_to_manifest():
    results = _load_required_json("results/main_results.json")
    manifest = _load_required_json("evidence/source_manifest.json")

    assert results["format_version"] == 1
    assert manifest["format_version"] == 1
    assert tuple(row["method"] for row in results["rows"]) == EXPECTED_METHODS

    sources = manifest["sources"]
    assert isinstance(sources, dict)
    assert all(row["source_id"] in sources for row in results["rows"])

    rows = {row["method"]: row for row in results["rows"]}
    assert rows["RT-DETR-L"]["map"] == 0.21911
    assert rows["RT-DETR-L+FDR"]["map"] == 0.28966
    assert rows["RT-DETR-L+FDR+BPDD"]["map"] == 0.29225786956881444

    assert all(row["fia"] is False for row in results["rows"])
    assert {
        row["source_id"]
        for row in results["supplementary_updated_fia_observations"]
    } == {
        "fia_p3_only_best_checkpoint_exact",
        "fdr_fia_existing_best_independent_val",
        "fia_updated_three_module_text_val",
        "fia_updated_three_module_text_test",
    }
    assert all(
        row["source_id"] in sources
        for row in results["supplementary_updated_fia_observations"]
    )
    assert {
        row["source_id"] for row in results["superseded_fia_observations"]
    } == {"fia_existing_best_independent_val"}
    assert all(
        row["superseded_by"] == "fia_p3_only_best_checkpoint_exact"
        for row in results["superseded_fia_observations"]
    )
    assert "supplementary_unverified_observations" not in results


def test_repository_contains_no_github_pat():
    marker = ("github" + "_pat_").encode("ascii")
    pat_shaped_value = re.compile(re.escape(marker) + rb"[A-Za-z0-9_]{20,}")
    offenders = []

    for path, relative_path in _tracked_files():
        if pat_shaped_value.search(path.read_bytes()):
            offenders.append(relative_path)

    assert not offenders, f"GitHub PAT-shaped values found in: {sorted(offenders)}"


def test_source_manifest_has_sha256_for_local_artifacts():
    manifest = _load_required_json("evidence/source_manifest.json")
    sources = manifest["sources"]
    assert isinstance(sources, dict)

    missing_or_invalid = []
    for source_id, source in sources.items():
        local_path = next(
            (
                source.get(key)
                for key in ("local_artifact_path", "artifact_path", "path", "artifact")
                if source.get(key)
            ),
            None,
        )
        if local_path is not None and re.fullmatch(r"[0-9a-fA-F]{64}", source.get("sha256", "")) is None:
            missing_or_invalid.append(source_id)

    assert not missing_or_invalid, (
        "manifest sources with local artifacts must have 64-character SHA-256 values: "
        f"{sorted(missing_or_invalid)}"
    )


def test_pre_revision_fia_results_are_scope_limited_and_replaced():
    status = _load_required_json("evidence/fia_results_status.json")
    manifest = _load_required_json("evidence/source_manifest.json")

    assert status["format_version"] == 1
    assert status["status"] == (
        "fia_only_p3_exact_val_test_three_module_four_decimal_val_test_available"
    )
    assert status["valid_fia_result_source_ids"] == [
        "fia_p3_only_best_checkpoint_exact",
        "fdr_fia_existing_best_independent_val",
        "fia_updated_three_module_checkpoint_best_val",
        "fia_updated_three_module_terminal_val",
        "fia_updated_three_module_terminal_test",
        "fia_updated_three_module_text_val",
        "fia_updated_three_module_text_test",
    ]
    assert status["user_reported_updated_result_direction"] == (
        "superseded_by_direct_best_checkpoint_evaluation"
    )
    assert status["user_report_is_formal_numeric_evidence"] is False
    standalone = status["updated_standalone_results"]
    assert standalone["fia_only"]["test_metrics"]["map75"] == (
        0.18201140298044138
    )
    assert standalone["fia_only"]["delta_map_pp"] == 0.7946395144255269
    assert standalone["fia_only"]["test_delta_map_pp"] == 0.8101032384120604
    assert standalone["fdr_fia"]["test_metrics"]["map75"] == (
        0.23587873005461435
    )
    assert all(
        standalone[arm]["test_evidence_level"]
        == "best_checkpoint_independent_test_exact"
        for arm in ("fia_only", "fdr_fia")
    )

    revoked_source_ids = {
        "fia_formal100_val_exact",
        "fia_ablation_release_dfr_bdpp_fia",
        "fia_terminal_val",
    }
    assert revoked_source_ids == set(status["revoked_source_ids"])
    assert revoked_source_ids.isdisjoint(manifest["sources"])
    assert all(
        source_id in manifest["sources"]
        for source_id in status["valid_fia_result_source_ids"]
    )
    assert status["superseded_source_ids"] == [
        "fia_existing_best_independent_val"
    ]
    superseded = status["superseded_standalone_results"]["fia_only_cascading"]
    assert superseded["result_status"] == "superseded"
    assert superseded["superseded_by"] == "fia_p3_only_best_checkpoint_exact"
    assert superseded["test_metrics"]["map75"] == 0.17161307417237592
    updated = status["updated_three_module_observation"]
    source = manifest["sources"]["fia_updated_three_module_checkpoint_best_val"]
    assert updated["graph"]["p3_only"] is True
    assert updated["graph"]["layer_23_from"] == 21
    assert updated["metrics"]["map"] == 0.29618
    assert updated["metrics"]["map75"] is None
    assert updated["delta_from_bpdd_map_pp"] > 0
    assert source["release_asset_sha256"] == (
        "fd972586e2833a28aa02d04ac9e460b0d7c8cfc4e6e8bcb48da273f0e905593c"
    )
    assert source["graph_identity"] == updated["graph"]
    assert source["checkpoint_embedded_best_val"]["map"] == 0.29618
    assert source["formal_main_table_allowed"] is False
    assert all(
        item["id"] != "formal100_three_module_fia_identity_projection"
        for item in manifest.get("normalizations", [])
    )

    web_audit = status["web_release_audit"]
    assert web_audit["release_id"] == 371026410
    assert web_audit["release_tag"] == "DFR-BDPP-FIA"
    assert web_audit["displayed_asset_count"] == 11
    assert web_audit["custom_asset_count"] == 9
    assert web_audit["autogenerated_source_archive_count"] == 2
    assert web_audit["hidden_updated_standalone_assets_found"] is True
    assert web_audit["canonical_p3_only_fia_asset"]["asset_id"] == 520838108
    for arm in ("fia_only", "fdr_fia"):
        candidate = web_audit["standalone_candidates"][arm]
        assert candidate["web_assets_present"] is True
        assert candidate["observed_checkpoint_layer_23_from"] == -1
        assert candidate["required_updated_checkpoint_layer_23_from"] == 21
        assert candidate["numeric_use_allowed"] is True
    assert web_audit["standalone_candidates"]["fia_only"]["decision"] == (
        "superseded_by_fresh_p3_only_exact_evaluation"
    )
    assert web_audit["standalone_candidates"]["fia_only"][
        "numeric_use_scope"
    ] == "historical independent val and test exact only; not canonical revised P3-only evidence"
    assert web_audit["standalone_candidates"]["fdr_fia"]["decision"] == (
        "accepted_as_existing_published_best_not_p3_only"
    )

    removed_paths = (
        "evidence/fdr_bpdd_fia_val_exact.json",
        "evidence/fia_ablation_release_evidence.json",
        "results/FDR_BPDD_FIA_DETAILED_ZH.md",
        "results/fdr_bpdd_fia_val_class_results.csv",
        "results/fdr_bpdd_fia_val_scale_results.csv",
        "results/fia_ablation_release_test_class_results.csv",
        "assets/fia_terminal_validation.jpg",
        "assets/fia_only_test_release.png",
        "assets/fdr_fia_test_release.png",
    )
    assert all(not (MATERIAL_ROOT / path).exists() for path in removed_paths)

    restored_page = _read_required_text("results/FIA_ABLATION_RELEASE_RESULTS_ZH.md")
    for required_text in (
        "P3-only",
        "best_checkpoint_independent_val_exact",
        "best_checkpoint_independent_test_exact",
        "model[23].f=-1",
        "model[23].f=21",
            "0.56996",
            "0.49848",
            "0.48982",
            "0.29618",
            "0.227056",
            "0.185517",
            "0.294940",
            "+0.7946",
            "+0.5280",
            "118ad631eff93ad806f85ea47819578e6e00bfc5",
            "c00cae89aaeb722854f8c845d14507c3598f75d509c2b12a3222b35a004157a6",
            "fd972586e2833a28aa02d04ac9e460b0d7c8cfc4e6e8bcb48da273f0e905593c",
    ):
        assert required_text in restored_page
    for revoked_text in (
        "0.21671",
        "0.29408",
    ):
        assert revoked_text not in restored_page


def test_main_table_mentions_all_methods_and_evidence_levels():
    table = _read_required_text("results/MAIN_TABLE_ZH.md")
    results = _load_required_json("results/main_results.json")

    paper_names = {
        "RT-DETR-L": "RT-DETR-L Baseline",
        "RT-DETR-L+FDR": "RT-DETR-L + FDR",
        "RT-DETR-L+FDR+BPDD": "RT-DETR-L + FDR + BPDD",
    }
    missing_methods = [
        method for method in EXPECTED_METHODS if paper_names[method] not in table
    ]
    evidence_levels = sorted({row["evidence_level"] for row in results["rows"]})
    missing_evidence_levels = [level for level in evidence_levels if level not in table]

    assert not missing_methods, f"main table is missing methods: {missing_methods}"
    assert not missing_evidence_levels, (
        f"main table is missing evidence levels: {missing_evidence_levels}"
    )


def test_main_table_matches_user_standard_a_to_e_display():
    table = _read_required_text("results/MAIN_TABLE_ZH.md")
    expected_rows = (
        "| A | RT-DETR-L Baseline | — | — | — | 0.46761 | 0.41731 | 0.38663 | 0.21302 | 0.21911 | — |",
        "| B | RT-DETR-L + FDR | ✓ | — | — | 0.56911 | 0.49278 | 0.48468 | 0.29253 | 0.28966 | +7.055 pp |",
        "| C | RT-DETR-L + FDR + BPDD | ✓ | ✓ | — | 0.57063 | 0.49446 | 0.48641 | 0.29810 | 0.29226 | +0.260 pp |",
        "| D | RT-DETR-L + FDR + FIA | ✓ | — | ✓ | 0.57752 | 0.49089 | 0.48631 | 0.29972 | 0.29494 | +0.528 pp |",
        "| E | RT-DETR-L + FDR + BPDD + FIA | ✓ | ✓ | ✓ | 0.5693 | 0.4991 | 0.4898 | 0.3042 | 0.2961 | +0.384 pp |",
    )
    for row in expected_rows:
        assert row in table
    assert "PPDD" not in table

    results = _load_required_json("results/main_results.json")
    display = results["standard_ablation_display"]
    assert [row["id"] for row in display] == ["A", "B", "C", "D", "E"]
    assert display[-1]["map_display"] == "0.2961"
    assert display[-1]["delta_display"] == "+0.384 pp"
    assert display[-1]["source_id"] == "fia_updated_three_module_text_val"

    d_row = next(row for row in display if row["id"] == "D")
    assert d_row == {
        "id": "D",
        "model": "RT-DETR-L + FDR + FIA",
        "fdr": True,
        "bpdd": False,
        "fia": True,
        "precision_display": "0.57752",
        "recall_display": "0.49089",
        "map50_display": "0.48631",
        "map75_display": "0.29972",
        "map_display": "0.29494",
        "delta_display": "+0.528 pp",
        "source_id": "fdr_fia_existing_best_independent_val",
    }
    supplementary_d = next(
        row
        for row in results["supplementary_updated_fia_observations"]
        if row["split"] == "VisDrone val"
        and row["method"] == "RT-DETR-L+FDR+FIA"
    )
    assert supplementary_d["precision"] == 0.5775238641748943
    assert supplementary_d["recall"] == 0.4908887926435492
    assert supplementary_d["map50"] == 0.486314064615312
    assert supplementary_d["map75"] == 0.29972392008500426
    assert supplementary_d["map"] == 0.29494032070762063
    assert supplementary_d["delta_map_pp"] == 0.5280571609979634
    assert supplementary_d["delta_strict_paired"] is False
    assert "待整理" not in table
    assert "待整理" not in json.dumps(display, ensure_ascii=False)

    manifest = _load_required_json("evidence/source_manifest.json")
    standard_source = manifest["sources"][display[-1]["source_id"]]
    assert standard_source["metrics"] == {
        "precision": 0.5693,
        "recall": 0.4991,
        "f1": 0.5285,
        "map50": 0.4898,
        "map75": 0.3042,
        "map": 0.2961,
    }
    assert standard_source["evidence_level"] == "user_supplied_text_report_4dp"


def test_bpdd_strict_pair_and_unified_complexity_materials_are_nonfabricated():
    protocol = _read_required_text("experiments/BPDD_STRICT_PAIR_PROTOCOL_ZH.md")
    for required_text in (
        "唯一新增训练实验",
        "同一源码提交",
        "seed=0",
        "FDR",
        "FDR+BPDD",
        "AP75",
        "+0.557 pp",
        "训练期",
        "不增加推理分支",
        "已完成训练",
        "+0.239 pp",
        "+0.283 pp",
        "+0.276 pp",
    ):
        assert required_text in protocol

    page = _read_required_text("results/COMPLEXITY_ZH.md")
    for required_text in (
        "RT-DETR-L Baseline",
        "RT-DETR-L + FDR",
        "RT-DETR-L + FDR + BPDD",
        "RT-DETR-L + FDR + BPDD + FIA",
        "Params",
        "FLOPs",
        "FPS",
        "Latency",
        "AP75",
        "mAP50–95",
        "28.85",
        "25.21",
        "0.861 ms",
        "1,500",
        "不增加推理分支",
    ):
        assert required_text in page

    complexity = _load_required_json("results/complexity_results.json")
    assert complexity["format_version"] == 1
    assert complexity["status"] == "completed_unified_measurement"
    assert complexity["protocol"]["same_hardware_required"] is True
    assert complexity["protocol"]["imgsz"] == 640
    assert complexity["protocol"]["batch"] == 1
    assert complexity["protocol"]["half"] is False
    rows = {row["method"]: row for row in complexity["rows"]}
    assert set(rows) == {
        "RT-DETR-L Baseline",
        "RT-DETR-L + FDR",
        "RT-DETR-L + FDR + BPDD",
        "RT-DETR-L + FDR + BPDD + FIA",
    }
    assert all(
        isinstance(row[key], (int, float)) and row[key] > 0
        for row in rows.values()
        for key in (
            "params",
            "gflops",
            "peak_memory_mib",
            "fps",
            "latency_ms",
            "latency_p90_ms",
        )
    )
    assert rows["RT-DETR-L Baseline"]["ap75"] == 0.21302
    assert rows["RT-DETR-L + FDR"]["map"] == 0.28966
    assert rows["RT-DETR-L + FDR + BPDD"]["ap75"] == 0.29810
    assert rows["RT-DETR-L + FDR + BPDD + FIA"]["map"] == 0.2961
    assert rows["RT-DETR-L Baseline"]["params"] == 32826626
    assert rows["RT-DETR-L + FDR"]["gflops"] == 108.22912
    assert rows["RT-DETR-L + FDR + BPDD"]["inference_contract"] == (
        "same_as_fdr_by_measurement_and_construction"
    )
    assert rows["RT-DETR-L + FDR + BPDD + FIA"]["params"] == 33458090
    pair = complexity["strict_bpdd_pair"]
    assert pair["fdr"]["params"] == pair["fdr_bpdd"]["params"]
    assert pair["fdr"]["gflops"] == pair["fdr_bpdd"]["gflops"]
    assert pair["fdr"]["peak_memory_mib"] == pair["fdr_bpdd"]["peak_memory_mib"]
    assert pair["conclusion"] == (
        "equal_static_cost_and_no_measurable_inference_overhead"
    )

    raw_path = MATERIAL_ROOT / complexity["source"]["raw_artifact"].removeprefix(
        "paper_material/"
    )
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    assert hashlib.sha256(raw_path.read_bytes()).hexdigest() == complexity["source"][
        "raw_artifact_sha256"
    ]
    assert raw["status"] == "completed_unified_measurement"
    assert raw["environment"]["gpu"] == "NVIDIA GeForce RTX 4090"
    assert set(raw["all_authorities"]) == {
        "baseline",
        "fdr",
        "strict_pair_fdr",
        "fdr_bpdd",
        "fdr_bpdd_fia",
    }
    for authority in raw["all_authorities"].values():
        samples = authority["latency_samples_ms"]
        latency = authority["latency"]
        assert len(samples) == 300
        assert all(math.isfinite(value) and value > 0 for value in samples)
        assert statistics.median(samples) == latency["median_ms"]
        ordered = sorted(samples)
        position = (len(ordered) - 1) * 0.9
        lower = math.floor(position)
        upper = math.ceil(position)
        p90 = (
            ordered[lower]
            if lower == upper
            else ordered[lower] * (upper - position)
            + ordered[upper] * (position - lower)
        )
        assert p90 == latency["p90_ms"]
        assert 1000.0 / latency["median_ms"] == latency["fps"]

    manifest = _load_required_json("evidence/source_manifest.json")
    source = manifest["sources"]["generated_unified_complexity_contract"]
    assert source["artifact"] == "paper_material/results/complexity_results.json"
    artifact = REPOSITORY_ROOT / source["artifact"]
    assert hashlib.sha256(artifact.read_bytes()).hexdigest() == source["sha256"]
    raw_source = manifest["sources"]["unified_complexity_20260820"]
    assert raw_source["artifact"] == complexity["source"]["raw_artifact"]
    assert raw_source["sha256"] == complexity["source"]["raw_artifact_sha256"]


def test_completed_bpdd_strict_pair_is_source_bound_and_reported():
    summary = _load_required_json(
        "evidence/bpdd_strict_pair_20260819/strict_pair_summary.json"
    )
    manifest = _load_required_json("evidence/source_manifest.json")
    results = _load_required_json("results/main_results.json")
    page = _read_required_text("results/RESULTS_ZH.md")
    protocol = _read_required_text("experiments/BPDD_STRICT_PAIR_PROTOCOL_ZH.md")

    assert summary["format_version"] == 1
    assert summary["status"] == "best_checkpoint_exact_val_test_complete"
    assert summary["authority"]["source_commit"] == (
        "848f00cb7a40907e3884885ecd5bbd474450758a"
    )
    assert summary["authority"]["evaluator_commit"] == (
        "2997705c8f448cee10339eb87daed818dcef8e1e"
    )
    assert summary["authority"]["seed"] == 0
    assert summary["authority"]["imgsz"] == 640
    assert summary["authority"]["batch"] == 8
    assert summary["authority"]["workers"] == 8
    assert summary["authority"]["conf"] == 0.001
    assert summary["authority"]["max_det"] == 300
    assert summary["authority"]["nms"] is False
    assert summary["authority"]["cache"] is False
    assert summary["authority"]["half"] is False
    assert summary["authority"]["rect"] is False
    assert summary["arms"]["fdr"]["best_epoch"] == 97
    assert summary["arms"]["fdr"]["selection_metrics"] == {
        "precision": 0.5808,
        "recall": 0.47923,
        "map50": 0.48232,
        "map75": None,
        "map": 0.29047,
    }
    assert summary["arms"]["fdr_bpdd"]["best_epoch"] == 93
    assert summary["arms"]["fdr_bpdd"]["selection_metrics"] == {
        "precision": 0.57937,
        "recall": 0.49101,
        "map50": 0.48657,
        "map75": None,
        "map": 0.29278,
    }
    exact = summary["independent_best_evaluation"]
    assert exact["val"]["fdr"]["map75"] == 0.29694111137614726
    assert exact["val"]["fdr_bpdd"]["map75"] == 0.2976607591780332
    assert exact["val"]["deltas_pp"]["map"] == 0.2389750054356654
    assert exact["val"]["deltas_pp"]["map75"] == 0.07196478018859365
    assert exact["test"]["fdr"]["map"] == 0.2311236870257676
    assert exact["test"]["fdr_bpdd"]["map"] == 0.23395865945253597
    assert exact["test"]["deltas_pp"]["map"] == 0.2834972426768362
    assert exact["test"]["deltas_pp"]["map75"] == 0.2758792898446355
    assert summary["inference_graph"]["fdr_params"] == 32334278
    assert summary["inference_graph"]["fdr_bpdd_params"] == 32334278
    assert summary["inference_graph"]["fdr_gflops"] == 103.7
    assert summary["inference_graph"]["fdr_bpdd_gflops"] == 103.7

    for artifact in summary["artifacts"]:
        path = REPOSITORY_ROOT / artifact["artifact"]
        assert path.is_file()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == artifact["sha256"]

    source = manifest["sources"]["bpdd_strict_pair_20260819"]
    assert source["artifact"] == (
        "paper_material/evidence/bpdd_strict_pair_20260819/strict_pair_summary.json"
    )
    summary_path = REPOSITORY_ROOT / source["artifact"]
    assert hashlib.sha256(summary_path.read_bytes()).hexdigest() == source["sha256"]
    assert results["strict_bpdd_pair_20260819"] == summary["paper_result_record"]

    for required_text in (
        "严格配对训练和 `best.pt` 统一 val/test 独立精确复评均已完成",
        "0.290380",
        "0.292770",
        "+0.239 pp",
        "+0.283 pp",
        "+0.276 pp",
    ):
        assert required_text in page
    assert "状态为 **已完成训练及统一 best.pt val/test 复评**" in protocol


def test_split_gain_comparison_covers_every_module_combination_without_fabrication():
    comparison = _load_required_json("results/split_gain_comparison.json")
    manifest = _load_required_json("evidence/source_manifest.json")

    assert comparison["format_version"] == 1
    combinations = {
        (row["fdr"], row["bpdd"], row["fia"]): row
        for row in comparison["combination_matrix"]
    }
    assert len(combinations) == 8
    assert combinations[(False, True, False)]["status"] == "invalid_dependency"
    assert combinations[(False, True, True)]["status"] == "invalid_dependency"
    assert combinations[(False, False, True)]["status"] == (
        "p3_only_best_checkpoint_exact_val_and_test"
    )
    assert combinations[(True, False, True)]["status"] == "existing_best_evaluated"
    assert combinations[(True, True, True)]["status"] == (
        "updated_four_decimal_val_test_available"
    )

    rows = {
        (row["split"], row["method"]): row
        for row in comparison["overall_rows"]
    }
    assert rows[("test", "RT-DETR-L+FDR+BPDD")]["metrics"]["map"] == (
        0.23165906438722952
    )
    assert all("FIA" not in row["method"] for row in comparison["overall_rows"])
    assert "supplementary_observation" not in comparison
    assert "supplementary_release_ablation_rows" not in comparison
    assert all(
        row["source_id"] in manifest["sources"]
        for row in comparison["overall_rows"]
        if row["source_id"] is not None
    )
    assert all(
        row["source_id"] in manifest["sources"]
        for row in comparison["supplementary_updated_fia_observations"]
    )
    supplementary = {
        (row["split"], row["method"]): row
        for row in comparison["supplementary_updated_fia_observations"]
    }
    assert supplementary[("test", "RT-DETR-L+FIA")]["metrics"]["map75"] == (
        0.18201140298044138
    )
    assert supplementary[("val", "RT-DETR-L+FIA")]["metrics"]["map"] == (
        0.22705639514425527
    )
    assert supplementary[("test", "RT-DETR-L+FIA")]["delta_map_pp"] == (
        0.8101032384120604
    )
    assert supplementary[("test", "RT-DETR-L+FDR+FIA")]["metrics"][
        "map75"
    ] == 0.23587873005461435
    assert all(
        supplementary[("test", method)]["evidence_level"]
        == "best_checkpoint_independent_test_exact"
        for method in ("RT-DETR-L+FIA", "RT-DETR-L+FDR+FIA")
    )
    assert {
        row["source_id"] for row in comparison["superseded_fia_observations"]
    } == {"fia_existing_best_independent_val"}


def test_readme_links_split_comparison_outputs():
    readme = _read_required_text("README_ZH.md")
    for relative_path in (
        "results/RESULTS_ZH.md",
        "results/SPLIT_GAIN_COMPARISON_ZH.md",
        "results/split_gain_comparison.json",
        "results/split_overall_results.csv",
        "results/split_scale_results.csv",
        "results/split_class_results.csv",
        "experiments/FIA_ABLATION_SCAFFOLD_ZH.md",
        "results/FIA_ABLATION_RELEASE_RESULTS_ZH.md",
        "results/FIA_RESULTS_STATUS_ZH.md",
        "evidence/fia_results_status.json",
        "evidence/fia_existing_best_evaluation.json",
        "results/fia_existing_best_val_results.csv",
        "results/fia_existing_best_test_results.csv",
        "evidence/fdr_bpdd_fia_val.txt",
        "evidence/fdr_bpdd_fia_test.txt",
        "results/fdr_bpdd_fia_text_report_class_results.csv",
    ):
        assert relative_path in readme


def test_consolidated_results_page_covers_exact_fia_val_test_and_boundaries():
    page = _read_required_text("results/RESULTS_ZH.md")

    for required_text in (
        "RT-DETR-L+FDR+BPDD",
        "0.292258",
        "FIA-only",
        "0.227056",
        "0.185517",
        "FDR+FIA",
        "0.294940",
        "0.234645",
        "0.182011",
        "0.235879",
        "+0.7946 pp",
        "+0.8101 pp",
        "best_checkpoint_independent_test_exact",
        "逐类别 F1 均值",
        "fresh P3-only",
        "P3-only",
        "0.29618",
        "非严格",
        "fia_existing_best_test_results.csv",
    ):
        assert required_text in page

    assert "三模块 test 已完成" not in page


def test_consolidated_results_page_contains_complete_a_to_e_val_and_test_tables():
    page = _read_required_text("results/RESULTS_ZH.md")

    expected_val_rows = (
        "| A | RT-DETR-L Baseline | — | — | — | 0.46761 | 0.41731 | 0.38663 | 0.21302 | 0.21911 | — |",
        "| B | RT-DETR-L + FDR | ✓ | — | — | 0.56911 | 0.49278 | 0.48468 | 0.29253 | 0.28966 | +7.055 pp vs A |",
        "| C | RT-DETR-L + FDR + BPDD | ✓ | ✓ | — | 0.57063 | 0.49446 | 0.48641 | 0.29810 | 0.29226 | +0.260 pp vs B |",
        "| D | RT-DETR-L + FDR + FIA | ✓ | — | ✓ | 0.57752 | 0.49089 | 0.48631 | 0.29972 | 0.29494 | +0.528 pp vs B |",
        "| E | RT-DETR-L + FDR + BPDD + FIA | ✓ | ✓ | ✓ | 0.5693 | 0.4991 | 0.4898 | 0.3042 | 0.2961 | +0.384 pp vs C |",
    )
    expected_test_rows = (
        "| A | RT-DETR-L Baseline | — | — | — | 0.41798 | 0.37301 | 0.32221 | 0.17550 | 0.17742 | — |",
        "| B | RT-DETR-L + FDR | ✓ | — | — | 0.50340 | 0.43168 | 0.39834 | 0.22890 | 0.22800 | +5.058 pp vs A |",
        "| C | RT-DETR-L + FDR + BPDD | ✓ | ✓ | — | 0.52267 | 0.42614 | 0.40369 | 0.23265 | 0.23166 | +0.366 pp vs B |",
        "| D | RT-DETR-L + FDR + FIA | ✓ | — | ✓ | 0.51897 | 0.43166 | 0.40744 | 0.23588 | 0.23465 | +0.664 pp vs B |",
        "| E | RT-DETR-L + FDR + BPDD + FIA | ✓ | ✓ | ✓ | 0.5189 | 0.4361 | 0.4081 | 0.2327 | 0.2337 | +0.204 pp vs C |",
    )

    for expected_row in (*expected_val_rows, *expected_test_rows):
        assert expected_row in page


def test_three_module_text_reports_are_canonical_and_complete():
    status = _load_required_json("evidence/fia_results_status.json")
    manifest = _load_required_json("evidence/source_manifest.json")
    comparison = _load_required_json("results/split_gain_comparison.json")

    expected = {
        "val": {
            "source_id": "fia_updated_three_module_text_val",
            "metrics": {
                "precision": 0.5693,
                "recall": 0.4991,
                "f1": 0.5285,
                "map50": 0.4898,
                "map75": 0.3042,
                "map": 0.2961,
            },
            "artifact": "paper_material/evidence/fdr_bpdd_fia_val.txt",
            "original_sha256": "24b799cb57ef8a12338d7086c699ccf02101cfd529e5785a82e3dc71bf3ac8ef",
        },
        "test": {
            "source_id": "fia_updated_three_module_text_test",
            "metrics": {
                "precision": 0.5189,
                "recall": 0.4361,
                "f1": 0.4634,
                "map50": 0.4081,
                "map75": 0.2327,
                "map": 0.2337,
            },
            "artifact": "paper_material/evidence/fdr_bpdd_fia_test.txt",
            "original_sha256": "e2b81acb63e5ff704ae8635200d595ea24884ccf88a4cab7195010dffbe51480",
        },
    }

    for split, item in expected.items():
        source_id = item["source_id"]
        assert source_id in status["valid_fia_result_source_ids"]
        observation = status[f"updated_three_module_text_{split}_observation"]
        assert observation["source_id"] == source_id
        assert observation["metrics"] == item["metrics"]
        assert observation["evidence_level"] == "user_supplied_text_report_4dp"
        assert observation["delta_from_bpdd_map_pp"] > 0

        source = manifest["sources"][source_id]
        assert source["metrics"] == item["metrics"]
        assert source["artifact"] == item["artifact"]
        assert source["original_artifact"]["sha256"] == item["original_sha256"]
        assert len(source["per_class"]) == 10
        artifact = REPOSITORY_ROOT / source["artifact"]
        assert artifact.is_file()
        assert hashlib.sha256(artifact.read_bytes()).hexdigest() == source["sha256"]

        rows = [
            row
            for row in comparison["supplementary_updated_fia_observations"]
            if row["split"] == split
            and row["method"] == "RT-DETR-L+FDR+BPDD+FIA"
        ]
        assert len(rows) == 1
        assert rows[0]["metrics"] == item["metrics"]
        assert rows[0]["source_id"] == source_id

    csv_path = MATERIAL_ROOT / "results/fdr_bpdd_fia_text_report_class_results.csv"
    with csv_path.open(encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    assert len(csv_rows) == 22
    assert {row["split"] for row in csv_rows} == {"val", "test"}
    assert all(row["f1"] and row["map75"] for row in csv_rows)

    page = _read_required_text("results/RESULTS_ZH.md")
    assert "0.2961" in page
    assert "0.2337" in page
    assert "user_supplied_text_report_4dp" in page


def test_split_detail_csvs_have_expected_exact_coverage():
    expected_counts = {
        "results/split_overall_results.csv": 10,
        "results/split_scale_results.csv": 24,
        "results/split_class_results.csv": 60,
    }

    for relative_path, expected_count in expected_counts.items():
        path = MATERIAL_ROOT / relative_path
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        assert len(rows) == expected_count, relative_path

    for relative_path in expected_counts:
        path = MATERIAL_ROOT / relative_path
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        assert all(row.get("fia", "false") != "true" for row in rows)
        assert all("FIA" not in row["method"] for row in rows)


def test_external_visdrone_comparison_contract_and_source_policy():
    comparison = _load_required_json("results/external_visdrone_comparison.json")
    manifest = _load_required_json("evidence/source_manifest.json")

    assert comparison["format_version"] == 1
    assert comparison["dataset"] == "VisDrone2019-DET"
    assert comparison["policy"]["parameter_count_is_filter"] is False
    assert comparison["policy"]["parameter_count_is_sort_key"] is False
    assert comparison["policy"]["cross_protocol_delta_allowed"] is False
    assert comparison["policy"]["sota_claim_allowed"] is False
    assert comparison["policy"]["venue_scope"] == "ccf_a_b_conference_only"
    assert comparison["policy"]["relative_sort_order"] == [
        "not_higher",
        "higher",
        "not_rankable",
    ]

    rows = comparison["rows"]
    assert len(rows) >= 12
    assert {row["split"] for row in rows} >= {"val", "test", "not_reported"}
    assert {row["family"] for row in rows} == {
        "project",
        "detr",
        "yolo",
        "anchor_based",
        "two_stage",
    }
    assert {
        "UAV-DETR-R18",
        "UAV-DETR-R50",
        "NRQO",
        "HIC-YOLOv5",
        "YOLOv5x + EMA",
        "YOLOv8-M",
        "YOLOv8-L",
        "RT-DETR-R50",
        "ClusDet-R50",
        "QueryDet",
        "TPH-YOLOv5-x + UGS",
        "DM-EFS",
        "UFPMP-Det-R50",
        "DINO-5scale + UGS",
        "VARDet",
        "RAFDE",
        "ResBiDet",
        "YOLOv10-X",
        "RT-DETR-R34",
        "FBRT-YOLO-L",
        "FBRT-YOLO-X",
        "RT-DETR-L + FDR + BPDD + FIA",
    }.issubset({row["method"] for row in rows})
    family_by_method = {row["method"]: row["family"] for row in rows}
    assert family_by_method["QueryDet"] == "anchor_based"
    assert family_by_method["ClusDet-R50"] == "two_stage"
    assert family_by_method["UFPMP-Det-R50"] == "two_stage"

    forbidden_statuses = {
        "preprint",
        "arxiv_only",
        "researchgate_only",
        "unverified",
    }
    assert not ({row["publication_status"] for row in rows} & forbidden_statuses)

    for row in rows:
        assert row["source_url"].startswith("https://")
        assert row["source_table"]
        assert row["evidence_type"] in {
            "our_run",
            "reported_by_original_paper",
            "standard_baseline_rebenchmarked_by_original_paper",
        }
        assert set(row["metrics"]) == {
            "precision",
            "recall",
            "ap50",
            "ap75",
            "map50_95",
        }
        assert row["parameter_count_m"] is None or row["parameter_count_m"] > 0
        assert row["venue_rank"] in {"project", "A", "B"}
        assert row["relative_to_project"] in {
            "reference",
            "project_baseline",
            "not_higher",
            "higher",
            "not_rankable",
        }
        if row["source_id"] is not None:
            assert row["source_id"] in manifest["sources"]

    external_rows = [row for row in rows if row["family"] != "project"]
    allowed_venues = {
        "ICCV 2019",
        "AAAI 2022",
        "CVPR 2022",
        "ICASSP 2023",
        "ICASSP 2026",
        "IJCAI 2025",
        "ICRA 2024",
        "AAAI 2025",
        "ICME 2025",
        "ICCV 2025",
        "IROS 2025",
    }
    allowed_source_ids = {
        "external_clusdet_iccv_2019",
        "external_ufpmp_aaai_2022",
        "external_querydet_cvpr_2022",
        "external_ema_icassp_2023",
        "external_vardet_icassp_2026",
        "external_resbidet_icassp_2026",
        "external_rafde_ijcai_2025",
        "external_hic_yolov5_icra_2024",
        "external_fbrt_yolo_aaai_2025",
        "external_nrqo_icme_2025",
        "external_dm_efs_iccv_2025",
        "external_ugs_iccv_2025",
        "external_uav_detr_iros_2025",
    }
    assert {row["venue"] for row in external_rows} <= allowed_venues
    assert {row["source_id"] for row in external_rows} <= allowed_source_ids
    assert all(
        row["publication_status"] == "peer_reviewed_conference"
        for row in external_rows
    )
    assert {row["venue_rank"] for row in external_rows} == {"A", "B"}

    project_by_split = {
        row["split"]: row["metrics"]["map50_95"]
        for row in rows
        if row["id"] in {"project_val_full", "project_test_full"}
    }
    for row in external_rows:
        score = row["metrics"]["map50_95"]
        if row["split"] not in project_by_split or score is None:
            assert row["relative_to_project"] == "not_rankable"
            continue
        expected = (
            "higher"
            if score > project_by_split[row["split"]]
            else "not_higher"
        )
        assert row["relative_to_project"] == expected

    ranked_val = [row for row in external_rows if row["split"] == "val"]
    lower = [row for row in ranked_val if row["relative_to_project"] == "not_higher"]
    higher = [row for row in ranked_val if row["relative_to_project"] == "higher"]
    assert [row["metrics"]["map50_95"] for row in lower] == sorted(
        (row["metrics"]["map50_95"] for row in lower), reverse=True
    )
    assert [row["metrics"]["map50_95"] for row in higher] == sorted(
        row["metrics"]["map50_95"] for row in higher
    )
    assert rows.index(lower[-1]) < rows.index(higher[0])

    vardet = next(row for row in rows if row["method"] == "VARDet")
    assert vardet["venue"] == "ICASSP 2026"
    assert vardet["venue_rank"] == "B"
    assert vardet["family"] == "detr"
    assert vardet["split"] == "val"
    assert vardet["input_size"] == "1333x800"
    assert vardet["backbone"] == "ResNet-50"
    assert vardet["metrics"] == {
        "precision": None,
        "recall": None,
        "ap50": 0.617,
        "ap75": 0.391,
        "map50_95": 0.365,
    }
    assert vardet["relative_to_project"] == "higher"
    assert vardet["comparison_scope"] == "external_b_venue_reported_val"
    assert "unified reimplementation" in vardet["evaluator"]
    assert "not protocol-matched" in vardet["note"]

    rafde = next(row for row in rows if row["method"] == "RAFDE")
    assert rafde["venue"] == "IJCAI 2025"
    assert rafde["venue_rank"] == "A"
    assert rafde["split"] == "val"
    assert rafde["input_size"] == "640x640"
    assert rafde["backbone"] == "YOLOv11m"
    assert rafde["metrics"] == {
        "precision": None,
        "recall": None,
        "ap50": 0.485,
        "ap75": None,
        "map50_95": 0.3,
    }
    assert rafde["relative_to_project"] == "higher"

    resbidet = next(row for row in rows if row["method"] == "ResBiDet")
    assert resbidet["venue"] == "ICASSP 2026"
    assert resbidet["venue_rank"] == "B"
    assert resbidet["split"] == "not_reported"
    assert resbidet["metrics"]["ap50"] == 0.387
    assert resbidet["metrics"]["map50_95"] is None
    assert resbidet["relative_to_project"] == "not_rankable"

    vardet_source = manifest["sources"]["external_vardet_icassp_2026"]
    assert vardet_source["source_url"] == (
        "https://doi.org/10.1109/ICASSP55912.2026.11463846"
    )
    assert vardet_source["ccf_class"] == "B"
    assert vardet_source["source_tables"] == ["Table 1"]


def test_external_visdrone_csv_matches_json_rows():
    comparison = _load_required_json("results/external_visdrone_comparison.json")
    csv_path = MATERIAL_ROOT / "results/external_visdrone_comparison.csv"
    with csv_path.open(encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))

    assert len(csv_rows) == len(comparison["rows"])
    assert [row["id"] for row in csv_rows] == [
        row["id"] for row in comparison["rows"]
    ]
    for flat, structured in zip(csv_rows, comparison["rows"]):
        assert flat["method"] == structured["method"]
        assert flat["split"] == structured["split"]
        assert flat["source_url"] == structured["source_url"]
        for csv_key, json_key in (
            ("precision", "precision"),
            ("recall", "recall"),
            ("ap50", "ap50"),
            ("ap75", "ap75"),
            ("map50_95", "map50_95"),
        ):
            expected = structured["metrics"][json_key]
            assert flat[csv_key] == ("" if expected is None else str(expected))


def test_external_visdrone_runtime_scope_is_explicit_when_reported():
    comparison = _load_required_json("results/external_visdrone_comparison.json")
    speed_rows = [row for row in comparison["rows"] if row["fps"] is not None]

    assert speed_rows
    for row in speed_rows:
        assert set(row["hardware"]) == {
            "gpu",
            "batch",
            "precision",
            "backend",
            "latency_scope",
        }
        assert all(value is not None for value in row["hardware"].values())
        if row["fps_comparison_allowed"]:
            assert row["hardware"] == comparison["fps_reference_protocol"]


def test_external_visdrone_material_is_linked_and_has_claim_boundaries():
    readme = _read_required_text("README_ZH.md")
    results = _read_required_text("results/RESULTS_ZH.md")
    outline = _read_required_text("writing/ICASSP2027_OUTLINE_ZH.md")
    page = _read_required_text("results/EXTERNAL_VISDRONE_COMPARISON_ZH.md")

    for path in (
        "results/EXTERNAL_VISDRONE_COMPARISON_ZH.md",
        "results/external_visdrone_comparison.json",
        "results/external_visdrone_comparison.csv",
    ):
        assert path in readme
    assert "EXTERNAL_VISDRONE_COMPARISON_ZH.md" in results
    assert "EXTERNAL_VISDRONE_COMPARISON_ZH.md" in outline
    for required_text in (
        "不同 split 不计算涨点",
        "外部论文报告值，不是本项目复跑值",
        "不宣称 SOTA",
        "参数量不是筛选条件",
        "CCF A",
        "CCF B",
        "不高于本文",
        "高于本文",
        "不可排序",
        "CVPR",
        "ICCV",
        "AAAI",
        "ICASSP",
        "ICRA",
        "ICME",
        "IROS",
        "VARDet",
        "RAFDE",
        "ResBiDet",
        "1333×800",
        "非严格可比",
        "not_reported",
    ):
        assert required_text in page
    assert "VARDet" in outline
    assert "ICASSP 2026" in outline
    for forbidden_text in ("Sensors 2024", "Remote Sensing", "Scientific Reports"):
        assert forbidden_text not in page
def test_dfine_inspiration_and_bpdd_originality_framing_contract() -> None:
    readme = _read_required_text("README_ZH.md")
    fdr = _read_required_text("methods/FDR_ZH.md")
    bpdd = _read_required_text("methods/BPDD_ZH.md")
    outline = _read_required_text("writing/ICASSP2027_OUTLINE_ZH.md")
    audit = _read_required_text(
        "writing/NOVELTY_POSITIONING_AND_ADVERSARIAL_AUDIT_ZH.md"
    )

    for text in (readme, fdr, outline, audit):
        assert "受 D-FINE 启发" in text
    for text in (readme, bpdd, outline, audit):
        assert "由本文独立提出并实现的原创算法" in text

    assert "不复用 GO-LSD 的教师构造、DDF 损失或代码实现" in bpdd
    assert "问题启发相关、算法构造独立" in bpdd
    assert "教师来源" in bpdd
    assert "可靠性门控" in bpdd
    assert "匹配合同" in bpdd
    assert "查询范围" in bpdd
    assert "independently formulate and implement BPDD" in audit
    assert "不扩张为未经系统检索证明的“文献史上首次”" in audit


def test_ap_fdr_contribution_first_attribution_contract() -> None:
    spec = (
        REPOSITORY_ROOT
        / "docs/superpowers/specs/2026-08-20-dfine-inspired-originality-framing-design.md"
    ).read_text(encoding="utf-8")
    fdr = _read_required_text("methods/FDR_ZH.md")
    audit = _read_required_text(
        "writing/NOVELTY_POSITIONING_AND_ADVERSARIAL_AUDIT_ZH.md"
    )

    for forbidden in ("1:4", "1/5", "80% 原创", "算法主体 80%"):
        assert forbidden not in spec
        assert forbidden not in fdr
        assert forbidden not in audit

    assert fdr.index("## 本文原创设计") < fdr.index("## 基础构件来源")
    for symbol in (
        "weighting_function",
        "Integral",
        "translate_gt",
        "bbox2distance",
        "distance2bbox",
        "unimodal_distribution_focal_loss",
    ):
        assert symbol in fdr
    assert "不以任何数值比例描述算法原创性" in audit

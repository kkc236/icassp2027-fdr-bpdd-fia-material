import csv
import hashlib
import json
import re
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
    "experiments/FIA_ABLATION_SCAFFOLD_ZH.md",
    "evidence/fia_results_status.json",
    "evidence/fia_existing_best_evaluation.json",
    "evidence/fdr_bpdd_fia_val.txt",
    "evidence/fdr_bpdd_fia_test.txt",
    "results/FIA_RESULTS_STATUS_ZH.md",
    "results/RESULTS_ZH.md",
    "results/main_results.json",
    "results/MAIN_TABLE_ZH.md",
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
    assert set(arms) == {"fia_only", "fdr_fia"}
    assert arms["fia_only"]["checkpoint_sha256"] == (
        "cf7203733c6d7f66ba8708dfda3b8aa6ac5cd8564bc31b68cde7e8513cf211d9"
    )
    assert arms["fdr_fia"]["checkpoint_sha256"] == (
        "6f624bbc262e840fa6f416486f3813d8ae1c0d9d8daccfb2997f5da6d427d5f1"
    )
    for arm in arms.values():
        assert arm["graph_identity"]["p3_only"] is False
        assert arm["graph_identity"]["layer_23_from"] == -1
        assert arm["graph_identity"]["decoder_from"] == [22, 25, 28]
        assert arm["val"]["evidence_level"] == "best_checkpoint_independent_val_exact"
        assert len(arm["val"]["per_class"]) == 10
        assert arm["test"]["evidence_level"] == (
            "best_checkpoint_independent_test_exact"
        )
        assert len(arm["test"]["per_class"]) == 10
        assert all(
            class_row["f1"] is not None and class_row["map75"] is not None
            for class_row in arm["test"]["per_class"]
        )
        assert arm["source_id"] in manifest["sources"]
        source = manifest["sources"][arm["source_id"]]
        assert source["test_evaluation_protocol"]["split"] == "test"
        assert source["independent_test_metrics"] == arm["test"]["metrics"]

    assert arms["fia_only"]["val"]["metrics"]["map"] == 0.21679545343355132
    assert arms["fdr_fia"]["val"]["metrics"]["map"] == 0.29494032070762063
    assert arms["fia_only"]["test"]["metrics"] == {
        "precision": 0.42405399388824083,
        "recall": 0.3696529891467626,
        "f1": 0.38186403219771886,
        "map50": 0.32511085966127234,
        "map75": 0.17161307417237592,
        "map": 0.1771764568469921,
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
    for variant in ("fia_only", "fdr_fia"):
        source = manifest["sources"][arms[variant]["source_id"]]
        assert status_arms[variant]["val_metrics"]["f1"] == (
            arms[variant]["val"]["metrics"]["f1"]
        )
        assert source["metrics"]["f1"] == arms[variant]["val"]["metrics"]["f1"]
        assert source["evaluation_protocol"]["f1_definition"] == (
            "mean_per_class_result.box.f1"
        )
    assert arms["fia_only"]["val"]["delta_map_pp"] == (
        arms["fia_only"]["val"]["metrics"]["map"] - 0.21911
    ) * 100
    assert arms["fdr_fia"]["val"]["delta_map_pp"] == (
        arms["fdr_fia"]["val"]["metrics"]["map"] - 0.289659749097641
    ) * 100

    csv_path = MATERIAL_ROOT / "results/fia_existing_best_val_results.csv"
    with csv_path.open(encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    assert len(csv_rows) == 2
    assert {row["source_id"] for row in csv_rows} == {
        "fia_existing_best_independent_val",
        "fdr_fia_existing_best_independent_val",
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

    assert len(rows) == 22
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
        assert len(class_rows) == 10

        overall = overall_rows[0]
        assert overall["method"] == arm["method"]
        assert overall["class"] == "all"
        assert int(overall["images"]) == arm["test"]["images"]
        assert int(overall["instances"]) == arm["test"]["instances"]
        for metric in ("precision", "recall", "f1", "map50", "map75", "map"):
            assert float(overall[metric]) == arm["test"]["metrics"][metric]

        evidence_classes = {
            class_row["class"]: class_row
            for class_row in arm["test"]["per_class"]
        }
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
        "fia_existing_best_independent_val",
        "fdr_fia_existing_best_independent_val",
        "fia_updated_three_module_text_val",
        "fia_updated_three_module_text_test",
    }
    assert all(
        row["source_id"] in sources
        for row in results["supplementary_updated_fia_observations"]
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
        "standalone_exact_val_test_three_module_four_decimal_val_test_available"
    )
    assert status["valid_fia_result_source_ids"] == [
        "fia_existing_best_independent_val",
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
        0.17161307417237592
    )
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
    assert web_audit["displayed_asset_count"] == 10
    assert web_audit["custom_asset_count"] == 8
    assert web_audit["autogenerated_source_archive_count"] == 2
    assert web_audit["hidden_updated_standalone_assets_found"] is False
    for arm in ("fia_only", "fdr_fia"):
        candidate = web_audit["standalone_candidates"][arm]
        assert candidate["web_assets_present"] is True
        assert candidate["observed_checkpoint_layer_23_from"] == -1
        assert candidate["required_updated_checkpoint_layer_23_from"] == 21
        assert candidate["decision"] == (
            "accepted_as_existing_published_best_not_p3_only"
        )
        assert candidate["numeric_use_allowed"] is True
        assert candidate["numeric_use_scope"] == (
            "independent val and test exact; not revised P3-only evidence"
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
        "0.216795",
        "0.294940",
        "-0.2315",
        "+0.5280",
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
        "| D | RT-DETR-L + FDR + FIA | ✓ | — | ✓ | 待整理 | 待整理 | 待整理 | 待整理 | 待整理 | FIA 独立增量 |",
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
    assert combinations[(False, False, True)]["status"] == "existing_best_evaluated"
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
        0.17161307417237592
    )
    assert supplementary[("test", "RT-DETR-L+FDR+FIA")]["metrics"][
        "map75"
    ] == 0.23587873005461435
    assert all(
        supplementary[("test", method)]["evidence_level"]
        == "best_checkpoint_independent_test_exact"
        for method in ("RT-DETR-L+FIA", "RT-DETR-L+FDR+FIA")
    )


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
        "0.216795",
        "0.177176",
        "FDR+FIA",
        "0.294940",
        "0.234645",
        "0.171613",
        "0.235879",
        "best_checkpoint_independent_test_exact",
        "逐类别 F1 的均值",
        "published cascading",
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
        "results/split_overall_results.csv": 6,
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

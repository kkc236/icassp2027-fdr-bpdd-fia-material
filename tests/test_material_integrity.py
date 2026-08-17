import csv
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
    "results/FIA_RESULTS_STATUS_ZH.md",
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
        assert arm["test"]["evidence_level"] == "best_checkpoint_screenshot_rounded"
        assert arm["test"]["metrics"]["map75"] is None
        assert arm["source_id"] in manifest["sources"]

    assert arms["fia_only"]["val"]["metrics"]["map"] == 0.21679545343355132
    assert arms["fdr_fia"]["val"]["metrics"]["map"] == 0.29494032070762063
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
        "fia_updated_three_module_checkpoint_best_val",
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
        "existing_best_standalone_evaluated_three_module_available"
    )
    assert status["valid_fia_result_source_ids"] == [
        "fia_existing_best_independent_val",
        "fdr_fia_existing_best_independent_val",
        "fia_updated_three_module_checkpoint_best_val"
    ]
    assert status["user_reported_updated_result_direction"] == (
        "superseded_by_direct_best_checkpoint_evaluation"
    )
    assert status["user_report_is_formal_numeric_evidence"] is False

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
        "best_checkpoint_screenshot_rounded",
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

    missing_methods = [
        method
        for method in EXPECTED_METHODS
        if re.search(rf"\|\s*{re.escape(method)}\s*\|", table) is None
    ]
    evidence_levels = sorted({row["evidence_level"] for row in results["rows"]})
    missing_evidence_levels = [level for level in evidence_levels if level not in table]

    assert not missing_methods, f"main table is missing methods: {missing_methods}"
    assert not missing_evidence_levels, (
        f"main table is missing evidence levels: {missing_evidence_levels}"
    )


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
        "updated_checkpoint_best_val_available"
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


def test_readme_links_split_comparison_outputs():
    readme = _read_required_text("README_ZH.md")
    for relative_path in (
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
    ):
        assert relative_path in readme


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

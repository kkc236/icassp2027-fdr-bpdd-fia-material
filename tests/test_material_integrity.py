import hashlib
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
    "results/main_results.json",
    "results/MAIN_TABLE_ZH.md",
    "evidence/source_manifest.json",
    "evidence/bpdd_val_exact.json",
    "evidence/fdr_bpdd_fia_val_exact.json",
    "results/FDR_BPDD_FIA_DETAILED_ZH.md",
    "results/fdr_bpdd_fia_val_class_results.csv",
    "results/fdr_bpdd_fia_val_scale_results.csv",
    "results/SPLIT_GAIN_COMPARISON_ZH.md",
    "results/split_gain_comparison.json",
    "results/split_overall_results.csv",
    "results/split_scale_results.csv",
    "results/split_class_results.csv",
    "writing/ICASSP2027_OUTLINE_ZH.md",
    "figures/FIGURE_PLAN_ZH.md",
    "assets/fia_terminal_validation.jpg",
)

EXPECTED_METHODS = (
    "RT-DETR-L",
    "RT-DETR-L+FDR",
    "RT-DETR-L+FDR+BPDD",
    "RT-DETR-L+FDR+BPDD+FIA",
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

    full_model = rows["RT-DETR-L+FDR+BPDD+FIA"]
    assert full_model["precision"] == 0.5557616181420737
    assert full_model["recall"] == 0.4983437446164801
    assert full_model["map50"] == 0.4812409327058466
    assert full_model["map75"] == 0.295103629855508
    assert full_model["map"] == 0.28995286433682393
    assert full_model["evidence_level"] == "exact_single_arm"
    assert full_model["source_id"] == "fia_formal100_val_exact"


def test_fia_formal100_detailed_evidence_is_complete_and_bound():
    evidence_path = MATERIAL_ROOT / "evidence" / "fdr_bpdd_fia_val_exact.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    manifest = _load_required_json("evidence/source_manifest.json")

    assert evidence["method"] == "RT-DETR-L+FDR+BPDD+FIA"
    assert evidence["split"] == "VisDrone val"
    assert evidence["metrics"]["map"] == 0.28995286433682393
    assert evidence["checkpoint"]["sha256"] == (
        "3EA6CD138C20AD38A35EF652407B6D77C423379A06E669028F771517843E069F"
    )
    assert set(evidence["scale_details"]) == {"tiny", "small", "medium", "large"}
    assert len(evidence["class_details"]) == 10
    assert evidence["provenance"]["source_sha256"] == (
        "5AE8CA9AC71FA49D7C754E69CDFF87934D44B02FE7992754A89AE2151701FC5F"
    )
    assert evidence["provenance"]["third_method_name_normalized_to_fia"] is True

    source = manifest["sources"]["fia_formal100_val_exact"]
    assert source["local_artifact"] == (
        "paper_material/evidence/fdr_bpdd_fia_val_exact.json"
    )
    canonical_bytes = subprocess.run(
        ["git", "-C", str(REPOSITORY_ROOT), "show", f":{source['local_artifact']}"],
        check=True,
        capture_output=True,
    ).stdout
    actual_sha256 = hashlib.sha256(canonical_bytes).hexdigest()
    assert source["canonical_local_artifact_sha256"] == actual_sha256


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


def test_fia_ablation_manifest_records_p3_only_config_normalization():
    manifest = _load_required_json("evidence/source_manifest.json")
    source = manifest["sources"]["fia_ablation_scaffold_1d083140"]
    artifacts = {artifact["path"]: artifact for artifact in source["artifacts"]}

    for relative_path in (
        "configs/rtdetr-l-fia.yaml",
        "configs/rtdetr-l-fdr-fia.yaml",
    ):
        artifact = artifacts[relative_path]
        actual_oid = subprocess.run(
            [
                "git",
                "-C",
                str(REPOSITORY_ROOT),
                "hash-object",
                f"--path={relative_path}",
                relative_path,
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        assert artifact["local_git_blob_oid"] == actual_oid
        assert artifact["local_git_blob_oid"] != artifact["git_blob_oid"]
        assert re.fullmatch(
            r"[0-9a-f]{64}", artifact["local_canonical_sha256"]
        )
        assert artifact["normalization"] == "preserve_p3_only_fia_topology"


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
    assert combinations[(False, False, True)]["status"] == (
        "experiment_scaffold_available"
    )
    assert combinations[(True, False, True)]["status"] == (
        "experiment_scaffold_available"
    )
    assert "fia_ablation_scaffold_1d083140" in manifest["sources"]

    rows = {
        (row["split"], row["method"]): row
        for row in comparison["overall_rows"]
    }
    assert rows[("val", "RT-DETR-L+FDR+BPDD+FIA")]["metrics"]["map"] == (
        0.28995286433682393
    )
    assert rows[("test", "RT-DETR-L+FDR+BPDD")]["metrics"]["map"] == (
        0.23165906438722952
    )
    assert rows[("test", "RT-DETR-L+FDR+BPDD+FIA")]["status"] == (
        "exact_evaluation_pending"
    )
    assert rows[("test", "RT-DETR-L+FDR+BPDD+FIA")]["metrics"] is None
    assert all(
        row["source_id"] in manifest["sources"]
        for row in comparison["overall_rows"]
        if row["source_id"] is not None
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
    ):
        assert relative_path in readme


def test_split_detail_csvs_have_expected_exact_coverage():
    expected_counts = {
        "results/split_overall_results.csv": 8,
        "results/split_scale_results.csv": 28,
        "results/split_class_results.csv": 70,
    }

    for relative_path, expected_count in expected_counts.items():
        path = MATERIAL_ROOT / relative_path
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        assert len(rows) == expected_count, relative_path

    with (MATERIAL_ROOT / "results/split_overall_results.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        overall_rows = list(csv.DictReader(handle))
    pending = next(
        row
        for row in overall_rows
        if row["split"] == "test"
        and row["method"] == "RT-DETR-L+FDR+BPDD+FIA"
    )
    assert pending["map"] == ""
    assert pending["status"] == "exact_evaluation_pending"

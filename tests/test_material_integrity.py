import json
import re
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MATERIAL_ROOT = REPOSITORY_ROOT / "paper_material"
TEXT_SUFFIXES = {".py", ".md", ".json", ".yaml", ".yml", ".csv", ".txt"}

REQUIRED_MATERIAL_FILES = (
    "README_ZH.md",
    "methods/FDR_ZH.md",
    "methods/BPDD_ZH.md",
    "methods/FIA_ZH.md",
    "experiments/PROTOCOL_ZH.md",
    "results/main_results.json",
    "results/MAIN_TABLE_ZH.md",
    "evidence/source_manifest.json",
    "evidence/bpdd_val_exact.json",
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


def _repository_paths():
    for path in REPOSITORY_ROOT.rglob("*"):
        relative_path = path.relative_to(REPOSITORY_ROOT)
        if ".git" not in relative_path.parts:
            yield path, relative_path


def _text_files():
    for path, relative_path in _repository_paths():
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
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
    forbidden = bytes((105, 114, 97)).decode("ascii")
    offenders = set()

    for path, relative_path in _repository_paths():
        display_path = relative_path.as_posix()
        if forbidden in display_path.lower():
            offenders.add(f"{display_path} (filename)")
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            content = path.read_text(encoding="utf-8", errors="ignore")
            if forbidden in content.lower():
                offenders.add(f"{display_path} (content)")

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
    assert full_model["map_display"] == 0.296
    assert full_model["evidence_level"] == "screenshot_rounded"


def test_repository_contains_no_github_pat():
    marker = "github" + "_pat_"
    pat_shaped_value = re.compile(re.escape(marker) + r"[A-Za-z0-9_]{20,}")
    offenders = []

    for path, relative_path in _text_files():
        content = path.read_text(encoding="utf-8", errors="ignore")
        if pat_shaped_value.search(content):
            offenders.append(relative_path.as_posix())

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

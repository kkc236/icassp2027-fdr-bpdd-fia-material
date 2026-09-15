"""Contract tests for the reproducible common-evaluation launchers."""

from pathlib import Path
import subprocess
import sys


def test_common_manifest_binds_two_existing_checkpoints(tmp_path: Path) -> None:
    from scripts.common_reevaluation import build_manifest

    data = tmp_path / "uavdt.yaml"
    data.write_text("path: /data/UAVDT\n", encoding="utf-8")
    baseline = tmp_path / "baseline.pt"
    joint = tmp_path / "joint.pt"
    baseline.write_bytes(b"baseline")
    joint.write_bytes(b"joint")

    manifest = build_manifest(
        dataset="UAVDT",
        data_yaml=data,
        split="val",
        imgsz=640,
        batch=8,
        workers=8,
        device="0",
        checkpoints={"baseline": baseline, "joint": joint},
    )

    assert manifest["contract"]["data_yaml_sha256"]
    assert set(manifest["checkpoints"]) == {"baseline", "joint"}
    assert manifest["contract"]["same_data_yaml_for_every_arm"] is True


def test_common_manifest_rejects_a_missing_checkpoint(tmp_path: Path) -> None:
    from scripts.common_reevaluation import build_manifest

    data = tmp_path / "data.yaml"
    data.write_text("path: /data\n", encoding="utf-8")
    try:
        build_manifest(
            dataset="VisDrone",
            data_yaml=data,
            split="test",
            imgsz=640,
            batch=8,
            workers=8,
            device="0",
            checkpoints={"g": tmp_path / "missing.pt", "g_fia": tmp_path / "also-missing.pt"},
        )
    except FileNotFoundError as error:
        assert "missing.pt" in str(error)
    else:
        raise AssertionError("missing checkpoints must fail closed")


def test_launcher_is_directly_executable_from_repository_root() -> None:
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "scripts/run_common_checkpoint_eval.py", "--help"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "--checkpoint" in result.stdout


def test_selected_markdown_has_one_terminal_newline() -> None:
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        ["node", "scripts/extract_selected_paper_tables.cjs"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    for name in ("SUPPLEMENTARY_TABLES.md", "UAVDT_TABLE_4_DRAFT.md"):
        payload = (root / "paper_material/submission_tables_20260915/selected" / name).read_bytes()
        assert payload.endswith(b"\n")
        assert not payload.endswith(b"\n\n")

import hashlib
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MATERIAL = ROOT / "paper_material"
EVIDENCE = MATERIAL / "evidence" / "lrs_fdr_formal100_20260828"
EVALUATION = EVIDENCE / "independent-evaluation"

ARM_FILES = {
    "original_fdr": "original_fdr.json",
    "clean_fdr": "na_fdr.json",
    "clean_fdr_plus_lrs_fgl": "lrs_fdr.json",
}

EXPECTED_METRICS = {
    "original_fdr": {
        "precision": 0.5702492505408118,
        "recall": 0.49141741757237556,
        "f1": 0.5279065878019488,
        "map50": 0.48470023900552056,
        "map75": 0.2940702122604297,
        "map": 0.2906981464337135,
    },
    "clean_fdr": {
        "precision": 0.5870448657223408,
        "recall": 0.4983385679226654,
        "f1": 0.5390668193782427,
        "map50": 0.49311876600517646,
        "map75": 0.3010611821592428,
        "map": 0.2968554815705331,
    },
    "clean_fdr_plus_lrs_fgl": {
        "precision": 0.5795115237637029,
        "recall": 0.5006064300903195,
        "f1": 0.537176877900053,
        "map50": 0.4918052555530953,
        "map75": 0.3057730327087865,
        "map": 0.2969680381039347,
    },
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def test_lrs_fdr_evidence_manifest_and_source_registry_are_byte_exact() -> None:
    manifest_entries = {}
    for line in (EVIDENCE / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
        digest, relative_path = line.split(maxsplit=1)
        manifest_entries[relative_path] = digest

    assert len(manifest_entries) == 11
    for relative_path, expected_digest in manifest_entries.items():
        artifact = EVIDENCE / relative_path
        assert artifact.is_file(), relative_path
        assert _sha256(artifact) == expected_digest

    source_manifest = _load_json(MATERIAL / "evidence" / "source_manifest.json")
    source = source_manifest["sources"]["lrs_fdr_formal100_best_val_20260828"]
    assert source["source_branch"] == "codex/lrs-fgl"
    assert source["source_commit"] == "9fa9078011d92cc23fc1f0eec06ff34983986ff0"
    assert source["paper_methods"] == {
        "original_fdr": "Original FDR",
        "clean_fdr": "NA-FDR",
        "clean_fdr_plus_lrs_fgl": "LRS-FDR",
    }
    assert source["historical_runtime_aliases_preserved"] is True
    assert source["strict_fresh_concurrent_pair"] is False
    assert source["multi_seed"] is False
    for artifact in source["artifacts"]:
        path = ROOT / artifact["path"]
        assert path.is_file(), artifact["path"]
        assert _sha256(path) == artifact["sha256"]


def test_lrs_fdr_three_arm_evaluations_match_the_frozen_comparison() -> None:
    comparison = _load_json(EVALUATION / "comparison.json")
    assert comparison["verification_status"] == "ANALYZED"
    assert set(comparison["arms"]) == set(ARM_FILES)

    evaluations = {}
    for arm, filename in ARM_FILES.items():
        evaluation = _load_json(EVALUATION / filename)
        evaluations[arm] = evaluation
        assert evaluation["arm"] == arm
        assert evaluation["metrics"] == EXPECTED_METRICS[arm]
        assert evaluation["metrics"] == comparison["arms"][arm]["metrics"]
        assert evaluation["class_details"] == comparison["arms"][arm]["class_details"]
        assert evaluation["scale_details"] == comparison["arms"][arm]["scale_details"]
        assert evaluation["checkpoint"]["sha256"] == comparison["arms"][arm]["checkpoint_sha256"]
        assert evaluation["processed_images"] == 548
        assert evaluation["prediction_passes"] == 1

    comparisons = {
        "clean_vs_original": ("clean_fdr", "original_fdr"),
        "lrs_vs_clean": ("clean_fdr_plus_lrs_fgl", "clean_fdr"),
        "lrs_vs_original": ("clean_fdr_plus_lrs_fgl", "original_fdr"),
    }
    for delta_name, (treatment, control) in comparisons.items():
        for metric in EXPECTED_METRICS[treatment]:
            expected = (
                evaluations[treatment]["metrics"][metric]
                - evaluations[control]["metrics"][metric]
            )
            assert comparison["deltas"][delta_name]["metrics"][metric] == pytest.approx(
                expected, abs=1e-15
            )


def test_lrs_fdr_method_has_one_direct_internal_ablation_and_honest_boundaries() -> None:
    method = (MATERIAL / "methods" / "FDR_ZH.md").read_text(encoding="utf-8")
    results = (MATERIAL / "results" / "LRS_FDR_RESULTS_ZH.md").read_text(
        encoding="utf-8"
    )

    assert "**NA-FDR** 是其原生对齐基础和 `w/o LRS` 内部消融" in method
    assert "### 4.2 唯一直接内部消融" in method
    assert "reliability_shrinkage_alpha: 0.0" in method
    assert "reliability_shrinkage_alpha: 0.25" in method
    assert "模型参数、state dict、decoder 输出" in method
    assert "LRS 相对 NA-FDR 的 mAP 只有 `+0.011 pp`" in method
    assert "Tiny/Small mAP 分别下降 `0.851/0.181 pp`" in method
    assert "seed 0" in method
    assert "### 不能写" in results
    assert "LRS-FGL 显著提高总体 mAP" in results
    assert "seed 0 足以证明跨随机种子稳定性" in results
    assert "第二数据集" in results


def test_paper_facing_material_uses_lrs_fdr_identity_without_rebranding_history() -> None:
    readme = (MATERIAL / "README_ZH.md").read_text(encoding="utf-8")
    current = (MATERIAL / "CURRENT_RERUN_STATUS_ZH.md").read_text(encoding="utf-8")
    outline = (MATERIAL / "writing" / "ICASSP2027_OUTLINE_ZH.md").read_text(
        encoding="utf-8"
    )
    audit = (
        MATERIAL / "writing" / "NOVELTY_POSITIONING_AND_ADVERSARIAL_AUDIT_ZH.md"
    ).read_text(encoding="utf-8")
    figure_plan = (MATERIAL / "figures" / "FIGURE_PLAN_ZH.md").read_text(
        encoding="utf-8"
    )

    for text in (readme, current, outline, audit, figure_plan):
        assert "LRS-FDR" in text
        assert "NA-FDR" in text
    for text in (current, outline, audit, figure_plan):
        assert "Clean FDR" not in text
    assert "历史运行标识 “Clean FDR” 不再作为论文" in readme
    assert "旧 AP-FDR+BPDD/FIA checkpoint" in readme
    assert "LRS-FDR+BPDD+FIA 的同身份完整训练" in audit
    assert "UAVDT 只绑定既有 Baseline 并运行 Full" in audit

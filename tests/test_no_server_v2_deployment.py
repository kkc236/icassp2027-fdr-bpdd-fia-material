from __future__ import annotations

import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "paper_material/evidence/no_server_correctness_v2_20260906"


def test_source_archive_identity_and_checksum():
    authority = json.loads((PACKAGE / "SOURCE_AUTHORITY.json").read_text(encoding="utf-8"))
    archive = PACKAGE / authority["archive"]
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == authority["archive_sha256"]
    with zipfile.ZipFile(archive) as bundle:
        assert bundle.comment.decode() == authority["source_commit"]
        files = [name for name in bundle.namelist() if not name.endswith("/")]
        assert len(files) == authority["tracked_file_count"]
        assert all(name.startswith("uav-detection-baselines/") and ".." not in Path(name).parts for name in files)
        assert "uav-detection-baselines/src/lrs_runtime_evidence.py" in files
        assert "uav-detection-baselines/tests/test_no_server_correctness.py" in files
        assert not any("local-validation/" in name for name in files)


def test_evidence_hashes_and_final_junit_are_bound():
    report = json.loads((PACKAGE / "TEST_REPORT.json").read_text(encoding="utf-8"))
    for name, digest in report["evidence_sha256"].items():
        assert hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest() == digest
    suites = ET.parse(PACKAGE / "regression-final.xml").getroot().findall("testsuite")
    assert sum(int(s.attrib["failures"]) + int(s.attrib["errors"]) for s in suites) == 0
    assert sum(int(s.attrib["tests"]) - int(s.attrib["skipped"]) for s in suites) == report["final_regression"]["passed"]
    assert sum(int(s.attrib["skipped"]) for s in suites) == report["final_regression"]["skipped"]


def test_deployment_does_not_claim_formal_or_cuda_accuracy():
    report = json.loads((PACKAGE / "TEST_REPORT.json").read_text(encoding="utf-8"))
    assert report["method_revision"] == "v2-fp32-extent-logspace-ac-bpdd"
    assert report["cuda_verified"] is False
    assert report["formal100_completed"] is False
    assert report["metrics"] is None
    assert report["cpu_fp16_execution"] == "rejected_explicitly_after_nonfinite_grid_sample_reproduction"
    assert report["full_graph_checks"] == {"arms": ["f", "g", "h", "i"], "precisions": ["fp32", "cpu-bf16"], "count": 8}


def test_current_method_docs_distinguish_anchor_and_bpdd_versions():
    fdr = (ROOT / "paper_material/methods/FDR_ZH.md").read_text(encoding="utf-8")
    bpdd = (ROOT / "paper_material/methods/BPDD_ZH.md").read_text(encoding="utf-8")
    assert r"\operatorname{Decode}(r_0,d_l)" in fdr
    assert "attention 使用的 reference 仍逐层更新" in fdr
    assert "当前 AC-BPDD" in bpdd and "`weight=0.15`" in bpdd
    assert "以下为历史 final-assignment BPDD" in bpdd

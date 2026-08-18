# VisDrone External Comparison Material Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a paper-ready, primary-source-backed VisDrone comparison package limited to CCF B conference papers covering DETR/RT-DETR and YOLO methods, while excluding top conferences, journals, preprints, and unlike-protocol deltas.

**Architecture:** Store one canonical JSON dataset, derive a synchronized flat CSV view, and render a Chinese Markdown comparison page from the same audited values. Link the package from the material index, consolidated results, and paper outline; bind local artifacts and source provenance in the evidence manifest. Parameter count remains descriptive metadata and is not an admission or sorting gate.

**Tech Stack:** Markdown, JSON, CSV, Python/pytest, Git

---

### Task 1: Lock the comparison contract with failing tests

**Files:**
- Modify: `tests/test_material_integrity.py`
- Test: `tests/test_material_integrity.py`

- [x] Add tests requiring the new JSON/CSV/Markdown files and their README/results/outline links.
- [x] Assert formal-publication status, primary-source URL/table provenance, split/input separation, and explicit unavailable values.
- [x] Assert that preprints, arXiv-only, ResearchGate-only, and unverified rows are absent.
- [x] Assert any speed row carries batch, precision, backend, and latency-scope fields; only fully matched rows may enable direct FPS comparison.
- [x] Assert parameter count is metadata only and is not used as a filtering/sorting requirement.
- [x] Run `python -m pytest tests/test_material_integrity.py -q` and confirm failure is caused by the missing comparison package.

### Task 2: Build the canonical machine-readable comparison

**Files:**
- Create: `paper_material/results/external_visdrone_comparison.json`
- Create: `paper_material/results/external_visdrone_comparison.csv`
- Modify: `paper_material/evidence/source_manifest.json`
- Test: `tests/test_material_integrity.py`

- [x] Transcribe only values verified in original formally published papers or the repository's canonical run evidence.
- [x] Group rows by `val`, `test`, or `not_reported`; record input, backbone, pretraining, evaluator, and metric availability without inference.
- [x] Add selected standard YOLO/RT-DETR baselines reported in the formal IROS comparison table and keep speed comparisons non-direct when runtime fields differ or are unreported.
- [x] Flatten the JSON rows to CSV with identical values and provenance identifiers.
- [x] Add local artifact hashes and publication-source metadata to the evidence manifest.
- [x] Run the focused integrity tests and confirm the machine-readable package passes.

### Task 3: Write and integrate the paper-facing comparison

**Files:**
- Create: `paper_material/results/EXTERNAL_VISDRONE_COMPARISON_ZH.md`
- Modify: `paper_material/README_ZH.md`
- Modify: `paper_material/results/RESULTS_ZH.md`
- Modify: `paper_material/writing/ICASSP2027_OUTLINE_ZH.md`
- Test: `tests/test_material_integrity.py`

- [x] Add separate val, test, split-unclear, and runtime-boundary sections.
- [x] State that external numbers are reported values, not reruns; disallow cross-table delta and SOTA claims.
- [x] Explain that parameter count is retained for context but is not a selection criterion.
- [x] Link the comparison package from the material index, consolidated results, and ICASSP writing outline.
- [x] Run focused tests and `git diff --check`.

### Task 4: Verify, commit, and publish

**Files:**
- Verify all files changed above.

- [x] Run `python -m pytest tests/test_material_integrity.py -q`.
- [x] Run JSON parsing, CSV/JSON row-parity, link/path, forbidden-source-status, and SHA-256 checks.
- [x] Review `git diff --stat`, `git diff --check`, and final repository status.
- [x] Commit the implementation and push the updated private material repository.

### Task 5: Extend the comparison to CCF A/B and add relative ordering

**Files:**
- Modify: `tests/test_material_integrity.py`
- Modify: `paper_material/results/external_visdrone_comparison.json`
- Modify: `paper_material/results/external_visdrone_comparison.csv`
- Modify: `paper_material/results/EXTERNAL_VISDRONE_COMPARISON_ZH.md`
- Modify: `paper_material/evidence/source_manifest.json`
- Modify: material index, consolidated results, and paper outline

- [x] Add failing tests for A/B venue labels, required A-venue primary sources, and same-split relative-position groups.
- [x] Add primary-source-backed ICCV/CVPR/AAAI rows and preserve protocol differences.
- [x] Sort explicit val rows into `not_higher` (descending) and `higher` (ascending); keep missing split/input rows `not_rankable`.
- [x] Add the AAAI 2025 RTX 4090 training table while separating its RTX 3080 speed protocol and missing split/input identity.
- [x] Refresh artifact hashes, run focused verification, commit, and push.

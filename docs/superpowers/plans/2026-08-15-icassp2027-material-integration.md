# ICASSP 2027 FDR–BPDD–FIA Material Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and publish one private repository containing the existing runnable FDR, BPDD, and FIA implementation plus normalized, evidence-backed ICASSP writing material.

**Architecture:** Use the current FIA-normalized standalone code tree as the executable base. Import only authoritative FDR/BPDD artifacts from pinned source commits, derive normalized FIA material without changing algorithms, and bind every paper-table value to a machine-readable evidence index. A repository integrity test enforces required files, naming, result consistency, and absence of credentials.

**Tech Stack:** Git, GitHub CLI, Python 3, PyTorch, Ultralytics RT-DETR, PyYAML, pytest, Markdown, JSON, CSV.

---

## File Map

- `tests/test_material_integrity.py`: repository naming, required-file, evidence, and secret guards.
- `paper_material/README_ZH.md`: single entry point for paper writers.
- `paper_material/methods/FDR_ZH.md`: FDR mechanism, integration, and claim boundary.
- `paper_material/methods/BPDD_ZH.md`: BPDD mechanism, dependency, and inference boundary.
- `paper_material/methods/FIA_ZH.md`: FIA mechanism, insertion point, formula, and complexity.
- `paper_material/experiments/PROTOCOL_ZH.md`: frozen dataset, training, and evaluation protocol.
- `paper_material/results/main_results.json`: machine-readable results and evidence levels.
- `paper_material/results/MAIN_TABLE_ZH.md`: human-readable main/ablation table.
- `paper_material/evidence/source_manifest.json`: pinned commits, artifact paths, and checksums.
- `paper_material/writing/ICASSP2027_OUTLINE_ZH.md`: title, problem statement, contributions, and section allocation.
- `paper_material/figures/FIGURE_PLAN_ZH.md`: method and result figure plan grounded in source code.
- `paper_material/assets/fia_terminal_validation.jpg`: user-supplied terminal validation screenshot.
- `docs/FDR_RTDETR_L_STRICT_CONTROL_AND_RESULTS_2026-08-09_ZH.md`: imported FDR report.
- `docs/FDR_YAML_DECLARATIVE_MODULE.md`: imported FDR reproducibility report.
- `research/fdr/`: imported structured FDR authority/evidence.
- `research/bpdd/BPDD_AUTHORITY.md`: imported BPDD claim boundary.
- `research/bpdd/authority.json`: imported BPDD machine authority.
- `evidence/strict-control-test-d97e1eb7/`: imported structured strict test evidence.

### Task 1: Add material integrity tests

**Files:**
- Create: `tests/test_material_integrity.py`

- [ ] **Step 1: Write failing required-file and naming tests**

```python
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "paper_material/README_ZH.md",
    "paper_material/methods/FDR_ZH.md",
    "paper_material/methods/BPDD_ZH.md",
    "paper_material/methods/FIA_ZH.md",
    "paper_material/experiments/PROTOCOL_ZH.md",
    "paper_material/results/main_results.json",
    "paper_material/results/MAIN_TABLE_ZH.md",
    "paper_material/evidence/source_manifest.json",
    "paper_material/writing/ICASSP2027_OUTLINE_ZH.md",
    "paper_material/figures/FIGURE_PLAN_ZH.md",
)


def test_required_material_files_exist() -> None:
    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
    assert missing == []


def test_legacy_third_method_name_is_absent() -> None:
    forbidden = bytes((105, 114, 97)).decode()
    offenders: list[str] = []
    for path in ROOT.rglob("*"):
        if ".git" in path.parts or not path.is_file():
            continue
        if forbidden in path.name.lower():
            offenders.append(str(path.relative_to(ROOT)))
            continue
        if path.suffix.lower() in {".py", ".md", ".json", ".yaml", ".yml", ".csv", ".txt"}:
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
            if forbidden in text:
                offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []
```

- [ ] **Step 2: Write failing evidence consistency and secret tests**

```python
def test_main_results_are_bound_to_manifest() -> None:
    results = json.loads((ROOT / "paper_material/results/main_results.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "paper_material/evidence/source_manifest.json").read_text(encoding="utf-8"))
    source_ids = set(manifest["sources"])
    assert results["format_version"] == 1
    assert [row["method"] for row in results["rows"]] == [
        "RT-DETR-L",
        "RT-DETR-L+FDR",
        "RT-DETR-L+FDR+BPDD",
        "RT-DETR-L+FDR+BPDD+FIA",
    ]
    assert all(row["source_id"] in source_ids for row in results["rows"])
    assert results["rows"][0]["map"] == 0.21911
    assert results["rows"][1]["map"] == 0.28966
    assert results["rows"][2]["map"] == 0.29225786956881444
    assert results["rows"][3]["map_display"] == 0.296
    assert results["rows"][3]["evidence_level"] == "screenshot_rounded"


def test_repository_contains_no_github_pat() -> None:
    marker = "github" + "_pat_"
    offenders = []
    for path in ROOT.rglob("*"):
        if ".git" in path.parts or not path.is_file():
            continue
        if path.suffix.lower() in {".py", ".md", ".json", ".yaml", ".yml", ".csv", ".txt"}:
            if marker in path.read_text(encoding="utf-8", errors="ignore"):
                offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []
```

- [ ] **Step 3: Run tests and verify they fail for missing material**

Run: `python -m pytest tests/test_material_integrity.py -q`

Expected: FAIL listing missing `paper_material/` files.

- [ ] **Step 4: Commit the failing tests**

```powershell
git add tests/test_material_integrity.py
git commit -m "test: define ICASSP material integrity contract"
```

### Task 2: Import pinned FDR and BPDD evidence

**Files:**
- Create: `docs/FDR_RTDETR_L_STRICT_CONTROL_AND_RESULTS_2026-08-09_ZH.md`
- Create: `docs/FDR_YAML_DECLARATIVE_MODULE.md`
- Create: `research/fdr/**`
- Create: `research/bpdd/BPDD_AUTHORITY.md`
- Create: `research/bpdd/authority.json`
- Create: `evidence/strict-control-test-d97e1eb7/**`

- [ ] **Step 1: Fetch pinned source refs without merging histories**

```powershell
git fetch source codex/fdr-yaml-module codex/bpdd-fdr
```

Expected: both refs appear under `source/`.

- [ ] **Step 2: Restore authoritative artifacts from the BPDD tip**

```powershell
git restore --source=source/codex/bpdd-fdr -- `
  docs/FDR_RTDETR_L_STRICT_CONTROL_AND_RESULTS_2026-08-09_ZH.md `
  docs/FDR_YAML_DECLARATIVE_MODULE.md `
  research/fdr `
  research/bpdd `
  evidence/strict-control-test-d97e1eb7
```

Expected: the listed files are added without changing executable source files.

- [ ] **Step 3: Run the naming test**

Run: `python -m pytest tests/test_material_integrity.py::test_legacy_third_method_name_is_absent -q`

Expected: PASS because the selected FDR/BPDD authority set contains no legacy third-method material.

- [ ] **Step 4: Commit imported authority evidence**

```powershell
git add docs research evidence
git commit -m "docs: import pinned FDR and BPDD evidence"
```

### Task 3: Add the machine-readable evidence index and results

**Files:**
- Create: `paper_material/evidence/source_manifest.json`
- Create: `paper_material/results/main_results.json`
- Create: `paper_material/assets/fia_terminal_validation.jpg`

- [ ] **Step 1: Create the source manifest**

The JSON must use these source IDs and pinned commits:

```json
{
  "format_version": 1,
  "sources": {
    "strict_control_val": {
      "commit": "f6fe1365171eceef2ee327e589b14718f3773486",
      "artifact": "docs/FDR_RTDETR_L_STRICT_CONTROL_AND_RESULTS_2026-08-09_ZH.md"
    },
    "fdr_val": {
      "commit": "f6fe1365171eceef2ee327e589b14718f3773486",
      "artifact": "docs/FDR_RTDETR_L_STRICT_CONTROL_AND_RESULTS_2026-08-09_ZH.md"
    },
    "bpdd_val": {
      "commit": "6bec4fece8c9ac49011f0aa64c6d3c1907235d19",
      "artifact": "structured_exact_evaluation"
    },
    "fia_terminal_val": {
      "commit": "7b20c610f9d2ae1a6899e5fc8ed33348dca90d40",
      "artifact": "paper_material/assets/fia_terminal_validation.jpg"
    }
  }
}
```

- [ ] **Step 2: Create the normalized main results JSON**

```json
{
  "format_version": 1,
  "split": "VisDrone val",
  "rows": [
    {"method": "RT-DETR-L", "fdr": false, "bpdd": false, "fia": false, "precision": 0.46761, "recall": 0.41731, "map50": 0.38663, "map75": 0.21302, "map": 0.21911, "evidence_level": "strict", "source_id": "strict_control_val"},
    {"method": "RT-DETR-L+FDR", "fdr": true, "bpdd": false, "fia": false, "precision": 0.56911, "recall": 0.49278, "map50": 0.48468, "map75": 0.29253, "map": 0.28966, "evidence_level": "strict", "source_id": "fdr_val"},
    {"method": "RT-DETR-L+FDR+BPDD", "fdr": true, "bpdd": true, "fia": false, "precision": 0.5706336342276676, "recall": 0.494464137092214, "map50": 0.4864074913692349, "map75": 0.29809564823246976, "map": 0.29225786956881444, "evidence_level": "cross_authority_exact", "source_id": "bpdd_val"},
    {"method": "RT-DETR-L+FDR+BPDD+FIA", "fdr": true, "bpdd": true, "fia": true, "precision_display": 0.569, "recall_display": 0.499, "map50_display": 0.49, "map75": null, "map_display": 0.296, "evidence_level": "screenshot_rounded", "source_id": "fia_terminal_val"}
  ]
}
```

- [ ] **Step 3: Copy the supplied screenshot without modifying its pixels**

Run: `Copy-Item -LiteralPath 'C:\Users\16946\AppData\Local\Temp\codex-clipboard-4702c98a-d8d5-41e5-9833-94a5799a5b71.jpg' -Destination 'paper_material\assets\fia_terminal_validation.jpg'`

Expected: the destination image exists and retains the source SHA-256.

- [ ] **Step 4: Run the evidence consistency tests**

Run: `python -m pytest tests/test_material_integrity.py::test_main_results_are_bound_to_manifest tests/test_material_integrity.py::test_repository_contains_no_github_pat -q`

Expected: `2 passed`.

- [ ] **Step 5: Commit normalized results and evidence index**

```powershell
git add paper_material/evidence paper_material/results paper_material/assets
git commit -m "docs: bind normalized results to source evidence"
```

### Task 4: Write the consolidated method and protocol material

**Files:**
- Create: `paper_material/README_ZH.md`
- Create: `paper_material/methods/FDR_ZH.md`
- Create: `paper_material/methods/BPDD_ZH.md`
- Create: `paper_material/methods/FIA_ZH.md`
- Create: `paper_material/experiments/PROTOCOL_ZH.md`
- Create: `paper_material/results/MAIN_TABLE_ZH.md`

- [ ] **Step 1: Write method pages from executable source**

Each page must include: problem, module position, input/output, mechanism, loss or residual formula, training/inference behavior, source paths, and claim boundary. FIA must document `src/fia.py`, the two local refinement blocks, channel/spatial attention, and `Y=X+alpha(F(X)-X)` with zero-initialized `alpha`.

- [ ] **Step 2: Write the frozen protocol page**

Record VisDrone train 6,471 images, val 548 images, 10 classes, RT-DETR-L, scratch initialization, 640 input, seed 0, 100 epochs, and same-evaluator restrictions. Explicitly prohibit comparing val and test values as deltas.

- [ ] **Step 3: Render the result table from `main_results.json` values**

The Markdown table must contain module checkmarks, Precision, Recall, AP50, AP75, mAP50-95, evidence level, and delta boundaries. The full-model row must display `≈` and leave AP75 unavailable.

- [ ] **Step 4: Write the material entry point**

`README_ZH.md` must link the three methods, protocol, results, evidence manifest, writing outline, and figure plan. It must state that BPDD's minimum valid host is FDR because it consumes FDR boundary distributions.

- [ ] **Step 5: Run material integrity tests**

Run: `python -m pytest tests/test_material_integrity.py -q`

Expected: all tests pass except files scheduled for Task 5.

- [ ] **Step 6: Commit the consolidated core material**

```powershell
git add paper_material
git commit -m "docs: consolidate FDR BPDD FIA paper material"
```

### Task 5: Add ICASSP writing and figure plans

**Files:**
- Create: `paper_material/writing/ICASSP2027_OUTLINE_ZH.md`
- Create: `paper_material/figures/FIGURE_PLAN_ZH.md`

- [ ] **Step 1: Write the evidence-safe ICASSP outline**

The outline must position RT-DETR-L as baseline, FDR as the structured localization foundation adapted from D-FINE, BPDD as training-only distribution distillation, and FIA as high-resolution identity-safe feature enhancement. It must not claim that FDR/FGL/Integral were invented here.

- [ ] **Step 2: Write the figure plan**

Plan exactly four figures: full architecture, BPDD decoder supervision, FIA block, and mAP/AP75 comparison. Each figure entry must name its source code paths and forbidden unsupported labels.

- [ ] **Step 3: Run the full material test**

Run: `python -m pytest tests/test_material_integrity.py -q`

Expected: all tests pass.

- [ ] **Step 4: Commit writing assets**

```powershell
git add paper_material/writing paper_material/figures
git commit -m "docs: add ICASSP writing and figure plans"
```

### Task 6: Verify the executable repository

**Files:**
- Modify only if a verified integration defect is found.

- [ ] **Step 1: Run material integrity tests**

Run: `python -m pytest tests/test_material_integrity.py -q`

Expected: PASS.

- [ ] **Step 2: Run focused FDR/BPDD/FIA tests**

Run: `python -m pytest tests/test_fdr_math.py tests/test_fdr_head.py tests/test_bpdd_loss.py tests/test_fia_module.py tests/test_bpdd_fia_yaml_config.py -q`

Expected: PASS.

- [ ] **Step 3: Run configuration and integration tests**

Run: `python -m pytest tests/test_fdr_yaml_configs.py tests/test_bpdd_fdr_integration.py tests/test_bpdd_fia_integration.py tests/test_bpdd_pr_fia_integration.py -q`

Expected: PASS.

- [ ] **Step 4: Scan tracked files for credentials and naming violations**

Run: `python -m pytest tests/test_material_integrity.py::test_legacy_third_method_name_is_absent tests/test_material_integrity.py::test_repository_contains_no_github_pat -q`

Expected: `2 passed`.

- [ ] **Step 5: Confirm a clean worktree and commit any verification-only repair**

Run: `git status --short`

Expected: no output.

### Task 7: Create and publish the private GitHub repository

**Files:**
- No content changes.

- [ ] **Step 1: Rename the source remote and local branch**

```powershell
git remote rename origin source
git branch -M main
```

- [ ] **Step 2: Create the private repository from the local tree**

Run: `gh repo create kkc236/icassp2027-fdr-bpdd-fia-material --private --source . --remote origin --push`

Expected: GitHub reports repository creation and pushes `main`.

- [ ] **Step 3: Verify visibility and remote**

Run: `gh repo view kkc236/icassp2027-fdr-bpdd-fia-material --json nameWithOwner,visibility,defaultBranchRef,url`

Expected: `visibility` is `PRIVATE` and default branch is `main`.

- [ ] **Step 4: Verify the remote tree and final local status**

```powershell
git fetch origin
git status -sb
git rev-parse HEAD
git rev-parse origin/main
```

Expected: local `main` and `origin/main` SHAs match and the worktree is clean.

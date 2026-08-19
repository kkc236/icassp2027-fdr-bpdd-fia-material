# FIA Release Results Refresh Implementation Plan

> Historical completed plan (superseded): its pending standalone-FIA assumptions are no longer current. The fresh FIA-only P3-only exact val/test status is maintained in `paper_material/results/FIA_RESULTS_STATUS_ZH.md`.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore the established FIA release-results Markdown path with only post-revision FIA evidence and status.

**Architecture:** Keep the machine-readable authority in `fia_results_status.json` and make the restored Markdown page a human-readable projection of that authority. Preserve the current formal-table boundary: only the updated P3-only three-module checkpoint has numeric FIA evidence, while updated standalone arms remain unpopulated pending auditable artifacts.

**Tech Stack:** Markdown, JSON-backed evidence, pytest material-integrity checks.

---

### Task 1: Lock the restored-page contract with a failing test

**Files:**
- Modify: `tests/test_material_integrity.py`
- Test: `tests/test_material_integrity.py`

- [x] **Step 1: Remove only the restored Markdown path from `removed_paths` and add page assertions**

Add assertions requiring `results/FIA_ABLATION_RELEASE_RESULTS_ZH.md` to exist, contain `0.29618`, the checkpoint SHA-256, `P3-only`, and `checkpoint_embedded_best_val`, while rejecting the revoked metrics `0.21671`, `0.29408` and the old run identifiers.

- [x] **Step 2: Run the focused test and verify RED**

Run:

```powershell
python -m pytest tests\test_material_integrity.py::test_pre_revision_fia_results_are_revoked_and_absent -q
```

Expected: FAIL because `paper_material/results/FIA_ABLATION_RELEASE_RESULTS_ZH.md` does not exist.

### Task 2: Restore and overwrite the results page

**Files:**
- Create: `paper_material/results/FIA_ABLATION_RELEASE_RESULTS_ZH.md`
- Modify: `paper_material/README_ZH.md`

- [x] **Step 1: Create the new page from current evidence**

Write a Chinese evidence-status page containing:

```markdown
| FIA-only | 新版方向为正；精确资产待导入 | 不填数 |
| FDR+FIA | 新版方向为正；精确资产待导入 | 不填数 |
| FDR+BPDD+FIA | P3-only checkpoint 已核验 | 0.29618 |
```

Include P `0.56996`, R `0.49848`, AP50 `0.48982`, AP75 unavailable, mAP50–95 `0.29618`, checkpoint SHA-256 `fd972586e2833a28aa02d04ac9e460b0d7c8cfc4e6e8bcb48da273f0e905593c`, and the non-strict arithmetic observation `+0.3922 pp`.

- [x] **Step 2: Restore the README entry**

Add `results/FIA_ABLATION_RELEASE_RESULTS_ZH.md` to the reading order and machine-readable/results navigation without removing the canonical status link.

- [x] **Step 3: Run the focused test and verify GREEN**

Run:

```powershell
python -m pytest tests\test_material_integrity.py::test_pre_revision_fia_results_are_revoked_and_absent tests\test_material_integrity.py::test_readme_links_split_comparison_outputs -q
```

Expected: `2 passed`.

### Task 3: Verify and publish

**Files:**
- Verify all modified files from Tasks 1–2.

- [x] **Step 1: Run the FIA/material regression suite**

Run:

```powershell
python -m pytest tests\test_material_integrity.py tests\test_fia_ablation_entrypoints.py tests\test_fia_module.py tests\test_bpdd_fia_yaml_config.py -q
```

Expected: all runnable tests pass; environment-conditional skips are reported explicitly.

- [x] **Step 2: Run content and Git checks**

Run `git diff --check`, scan the restored page for revoked values/run IDs and high-confidence credentials, and verify all material JSON files parse.

- [x] **Step 3: Commit and push**

```powershell
git add -- paper_material/results/FIA_ABLATION_RELEASE_RESULTS_ZH.md paper_material/README_ZH.md tests/test_material_integrity.py docs/superpowers/plans/2026-08-17-fia-release-results-refresh.md
git commit -m "docs: refresh FIA release results page"
git push origin main
```

- [x] **Step 4: Verify remote synchronization**

Fetch `origin/main`, verify local and remote commit hashes match, confirm repository visibility is `PRIVATE`, and confirm the worktree is clean.

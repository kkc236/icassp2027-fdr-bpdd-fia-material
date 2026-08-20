# ICASSP Writing-Pattern Revision Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite the AP-FDR paper materials using the problem–design–evidence pattern observed in formally published ICASSP method papers, without citing or naming unrelated precedent papers in the manuscript materials.

**Architecture:** Preserve all registered results, provenance boundaries, and method identities. Add one integrity test that prevents unrelated writing exemplars from leaking into manuscript-facing materials, then revise the four core Markdown files so AP-FDR, BPDD, and FIA are introduced through task-specific problems, concrete design actions, and evidence rather than as a list of imported modules.

**Tech Stack:** Markdown, Python 3, pytest, Git.

---

### Task 1: Lock the manuscript boundary

**Files:**
- Modify: `tests/test_material_integrity.py`
- Test: `tests/test_material_integrity.py`

- [ ] **Step 1: Add the failing boundary test**

Add a test that reads `README_ZH.md`, `methods/FDR_ZH.md`, `writing/ICASSP2027_OUTLINE_ZH.md`, and `writing/NOVELTY_POSITIONING_AND_ADVERSARIAL_AUDIT_ZH.md`; assert that the unrelated writing exemplars `YOLO-SAM2`, `SpaRSep`, `Adapting Pitch-Based`, `YOLO-Based Lightweight Object Detection`, and `D2Q-DETR` are absent. Also require the audit and outline to contain `问题—设计—证据`, which is not yet present and therefore makes the test fail before the documentation change.

- [ ] **Step 2: Run the focused test and verify failure**

Run:

```powershell
python -m pytest tests/test_material_integrity.py -k writing_exemplar_boundary -q
```

Expected: one failure because `问题—设计—证据` is absent from the current audit/outline.

- [ ] **Step 3: Commit the test-only change after observing the expected failure**

```powershell
git add tests/test_material_integrity.py
git commit -m "test: lock ICASSP writing exemplar boundary"
```

### Task 2: Rewrite AP-FDR as a problem-driven method

**Files:**
- Modify: `paper_material/methods/FDR_ZH.md`

- [ ] **Step 1: Add the technical problem before the contribution list**

State two precise gaps: stock RT-DETR directly regresses continuous boxes and does not explicitly model per-edge uncertainty; directly replacing the detector with D-FINE would alter classification, query, decoder, and post-processing contracts, preventing a controlled RT-DETR comparison.

- [ ] **Step 2: Convert the four AP-FDR claims into design actions**

Retain the existing four mechanisms and formulas, but connect each mechanism to the preceding gap: localization-only preservation, stock-head preliminary geometry, normal/DN assignment-consistent supervision, and private-RNG initialization.

- [ ] **Step 3: Compress provenance to one bounded transition**

Keep the fixed D-FINE commit, mathematical primitives, and non-original components intact. Present them after the proposed AP-FDR design and explicitly state that the source note defines provenance rather than the paper's contribution.

- [ ] **Step 4: Verify no metric or mechanism drift**

Run:

```powershell
python -m pytest tests/test_material_integrity.py -k "dfine or ap_fdr" -q
```

Expected: all selected tests pass.

### Task 3: Rewrite the paper strategy and outline

**Files:**
- Modify: `paper_material/writing/NOVELTY_POSITIONING_AND_ADVERSARIAL_AUDIT_ZH.md`
- Modify: `paper_material/writing/ICASSP2027_OUTLINE_ZH.md`

- [ ] **Step 1: Add the internal-only exemplar rule**

Record that unrelated ICASSP papers were used only to extract a writing pattern and must not appear in Related Work, comparison tables, or references. Do not name those papers in either manuscript-facing file.

- [ ] **Step 2: Apply the problem–design–evidence pattern**

For AP-FDR, BPDD, and FIA, define the problem sentence, the concrete design sentence, and the evidence sentence. Preserve all existing values and evidence-level qualifiers.

- [ ] **Step 3: Tighten the English draft**

Remove D-FINE from the abstract-level foreground. Keep necessary attribution in Related Work and the method provenance boundary. Describe AP-FDR by its RT-DETR-specific actions, and avoid claims that the established distribution primitives were invented in this work.

- [ ] **Step 4: Keep relevant comparison papers unchanged**

Retain ResBiDet, VARDet, RAFDE, and the existing VisDrone comparison hierarchy because they are task-relevant competitors, not writing exemplars.

### Task 4: Align the material entry page

**Files:**
- Modify: `paper_material/README_ZH.md`

- [ ] **Step 1: Replace module-list framing with responsibility framing**

Describe AP-FDR, BPDD, and FIA as localization representation, cross-layer optimization, and fine-scale representation responses to three concrete UAV-detection problems.

- [ ] **Step 2: Preserve all result and provenance sections byte-for-byte where no wording change is required**

Do not alter val/test values, checkpoint identities, topology labels, strict/non-paired classifications, or complexity numbers.

### Task 5: Verify and publish

**Files:**
- Verify: all files changed in Tasks 1–4

- [ ] **Step 1: Run focused contract tests**

```powershell
python -m pytest tests/test_material_integrity.py -k "writing_exemplar_boundary or dfine_inspiration or ap_fdr_contribution" -q
```

Expected: all selected tests pass.

- [ ] **Step 2: Run the complete integrity suite**

```powershell
python -m pytest tests/test_material_integrity.py -q
```

Expected: all tests pass.

- [ ] **Step 3: Run repository text and whitespace checks**

```powershell
rg -n "YOLO-SAM2|SpaRSep|Adapting Pitch-Based|YOLO-Based Lightweight Object Detection|D2Q-DETR" paper_material/README_ZH.md paper_material/methods/FDR_ZH.md paper_material/writing/ICASSP2027_OUTLINE_ZH.md paper_material/writing/NOVELTY_POSITIONING_AND_ADVERSARIAL_AUDIT_ZH.md
git diff --check
```

Expected: `rg` returns no matches and `git diff --check` returns no errors.

- [ ] **Step 4: Commit and push**

```powershell
git add tests/test_material_integrity.py paper_material/README_ZH.md paper_material/methods/FDR_ZH.md paper_material/writing/ICASSP2027_OUTLINE_ZH.md paper_material/writing/NOVELTY_POSITIONING_AND_ADVERSARIAL_AUDIT_ZH.md
git commit -m "docs: adopt contribution-first ICASSP method writing"
git push origin HEAD:main
```

Expected: the remote `main` branch advances to the new commit and the local worktree is clean.

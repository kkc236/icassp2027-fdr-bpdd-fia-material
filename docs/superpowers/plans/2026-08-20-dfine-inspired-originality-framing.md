# D-FINE-Inspired Originality Framing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make AP-FDR's inspiration boundary and BPDD's independent algorithmic originality explicit and consistent across the paper material repository.

**Architecture:** A small integrity test first defines the required attribution and originality markers. Five canonical Markdown files then receive one consistent claim hierarchy, including a mechanism-level BPDD/GO-LSD comparison and matching Chinese/English contribution language.

**Tech Stack:** Markdown, Python 3.10, pytest, Git.

---

### Task 1: Lock the claim contract

**Files:**
- Modify: `tests/test_material_integrity.py`

- [ ] **Step 1: Add a failing integrity test**

Assert that FDR materials contain `受 D-FINE 启发` and preserve the non-original primitive boundary; assert that BPDD materials contain `由本文独立提出并实现的原创算法`, explicitly deny GO-LSD formula/code reuse, and keep the literature-wide priority limitation.

- [ ] **Step 2: Run the new test and confirm RED**

Run: `python -m pytest tests/test_material_integrity.py -q`

Expected: the new claim-contract assertions fail against the current Markdown.

### Task 2: Rewrite the canonical method and overview pages

**Files:**
- Modify: `paper_material/README_ZH.md`
- Modify: `paper_material/methods/FDR_ZH.md`
- Modify: `paper_material/methods/BPDD_ZH.md`

- [ ] **Step 1: Add AP-FDR inspiration-to-redesign wording**

State that D-FINE motivated the distributional view, while AP-FDR independently reorganizes the stock RT-DETR-L localization branch through localization-only scope, stock-head preliminary geometry, normal/DN assignment consistency, and isolated initialization.

- [ ] **Step 2: Add the BPDD originality statement and comparison table**

State that BPDD is independently formulated and implemented in this work. Compare it with GO-LSD along teacher source, teacher selection, activation gate, assignment, query scope, and objective; explicitly state that BPDD does not reuse GO-LSD teacher construction, DDF loss, or source code.

- [ ] **Step 3: Preserve bounded novelty language**

Clarify that “original” applies to BPDD's concrete mechanism and implementation, not an unverified literature-wide first-ever assertion.

### Task 3: Align the writing blueprint and adversarial audit

**Files:**
- Modify: `paper_material/writing/ICASSP2027_OUTLINE_ZH.md`
- Modify: `paper_material/writing/NOVELTY_POSITIONING_AND_ADVERSARIAL_AUDIT_ZH.md`

- [ ] **Step 1: Rewrite contribution hierarchy**

Use `inspired insight -> AP-FDR redesign -> original BPDD algorithm -> FIA complement` as the paper's narrative order.

- [ ] **Step 2: Add reviewer-facing defenses**

Add direct answers to “AP-FDR is renamed D-FINE” and “BPDD is a GO-LSD variant”, grounded in the two method difference tables and internal ablations.

- [ ] **Step 3: Align English copy**

Use `inspired by` for D-FINE attribution and `independently formulate and implement BPDD` for the BPDD contribution. Avoid `first-ever`, `entirely unrelated`, or `purely novel`.

### Task 4: Verify and publish

**Files:**
- Verify all six modified files and two planning documents.

- [ ] **Step 1: Run the material integrity suite**

Run: `python -m pytest tests/test_material_integrity.py -q`

Expected: all tests pass.

- [ ] **Step 2: Run text safety checks**

Run `git diff --check` and search the five canonical Markdown files for contradictory phrases such as `首次发明 FDR`, `BPDD 与 GO-LSD 完全无关`, and `first-ever`.

- [ ] **Step 3: Commit and push**

Commit the exact scoped files, verify the remote commit, and update `main` only if it is still a fast-forward from the fetched authority.

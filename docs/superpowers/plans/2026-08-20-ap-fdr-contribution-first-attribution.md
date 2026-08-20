# AP-FDR Contribution-First Attribution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the misleading `1:4` narrative ratio with a contribution-first, non-quantified AP-FDR attribution contract and align all current paper materials.

**Architecture:** Treat D-FINE provenance and AP-FDR contribution claims as two separate documentation surfaces. The method page carries the exact implementation provenance; README, outline, abstract guidance, and audit use one concise attribution sentence followed by the RT-DETR-specific original structure and supervision contributions.

**Tech Stack:** Markdown, Python `pytest`, Git.

---

### Task 1: Lock the non-quantified attribution contract

**Files:**
- Modify: `tests/test_material_integrity.py`
- Modify: `docs/superpowers/specs/2026-08-20-dfine-inspired-originality-framing-design.md`

- [ ] **Step 1: Write the failing test**

Append a test that requires the design spec to avoid numeric originality ratios, requires the AP-FDR method page to present original design before provenance, and requires exact D-FINE primitive provenance:

```python
def test_ap_fdr_contribution_first_attribution_contract():
    spec = (REPOSITORY_ROOT / "docs/superpowers/specs/2026-08-20-dfine-inspired-originality-framing-design.md").read_text(encoding="utf-8")
    fdr = _read_required_text("methods/FDR_ZH.md")
    audit = _read_required_text("writing/NOVELTY_POSITIONING_AND_ADVERSARIAL_AUDIT_ZH.md")

    for forbidden in ("1:4", "1/5", "80% 原创", "算法主体 80%"):
        assert forbidden not in spec
        assert forbidden not in fdr
        assert forbidden not in audit

    assert fdr.index("## 本文原创设计") < fdr.index("## 基础构件来源")
    for symbol in (
        "weighting_function",
        "Integral",
        "translate_gt",
        "bbox2distance",
        "distance2bbox",
        "unimodal_distribution_focal_loss",
    ):
        assert symbol in fdr
    assert "不以任何数值比例描述算法原创性" in audit
```

- [ ] **Step 2: Run the focused test to verify it fails**

Run:

```powershell
python -m pytest tests/test_material_integrity.py::test_ap_fdr_contribution_first_attribution_contract -q
```

Expected: `FAIL`, because the current spec contains `1:4` and the method/audit pages do not yet implement the new headings and non-quantification statement.

- [ ] **Step 3: Correct the design specification**

Replace the numeric ratio with this rule:

```markdown
- 不为 D-FINE 基础来源与 AP-FDR 原创设计设置数值比例；篇幅只遵循“来源简述、原创设计详述”。该要求是写作组织原则，不代表代码量、算法构成或原创程度的百分比。
```

Keep the exact primitive list in the specification, but state that function names belong in the method provenance paragraph or supplementary material rather than Abstract/Contributions.

- [ ] **Step 4: Commit the corrected contract and failing test**

```powershell
git add -- tests/test_material_integrity.py docs/superpowers/specs/2026-08-20-dfine-inspired-originality-framing-design.md
git commit -m "test: lock non-quantified AP-FDR attribution"
```

### Task 2: Rewrite AP-FDR materials contribution-first

**Files:**
- Modify: `paper_material/README_ZH.md`
- Modify: `paper_material/methods/FDR_ZH.md`
- Modify: `paper_material/writing/ICASSP2027_OUTLINE_ZH.md`
- Modify: `paper_material/writing/NOVELTY_POSITIONING_AND_ADVERSARIAL_AUDIT_ZH.md`

- [ ] **Step 1: Reorder the AP-FDR method page**

Use `## 本文原创设计` before `## 基础构件来源`. The original-design section must lead with:

```markdown
AP-FDR 的贡献不在于重新命名分布回归基础算子，而在于将其重构为与 stock RT-DETR-L 检测合同兼容的定位系统。
```

Then explain the four independently implemented contributions: localization-only architecture preservation, stock-head-informed preliminary geometry, assignment-consistent normal/DN supervision, and isolated initialization.

The later provenance section uses one compact paragraph plus the six exact symbols. It also states that the 33-bin representation, non-uniform projection, Integral, adjacent-bin FGL, and cumulative distribution refinement are not claimed as original.

- [ ] **Step 2: Shorten README and outline attribution**

Use one sentence of source attribution:

```markdown
AP-FDR 基于 D-FINE 已公开的边界分布基础构件，并面向 stock RT-DETR-L 提出架构保持型定位路径、stock-head-informed preliminary geometry、normal/DN 匹配一致监督与隔离初始化。
```

Do not enumerate code symbols outside the method page.

- [ ] **Step 3: Strengthen the adversarial-audit boundary**

Add the exact statement:

```markdown
不以任何数值比例描述算法原创性；“来源简述、原创设计详述”只是论文组织原则，不代表 D-FINE 与 AP-FDR 的算法占比。
```

Keep the English framing as `builds on established D-FINE primitives` followed immediately by the four AP-FDR contributions. Do not use `80% original`, `mostly original`, or `minor reuse`.

- [ ] **Step 4: Run the focused contract test**

Run:

```powershell
python -m pytest tests/test_material_integrity.py::test_ap_fdr_contribution_first_attribution_contract -q
```

Expected: `1 passed`.

- [ ] **Step 5: Commit the paper-material revision**

```powershell
git add -- paper_material/README_ZH.md paper_material/methods/FDR_ZH.md paper_material/writing/ICASSP2027_OUTLINE_ZH.md paper_material/writing/NOVELTY_POSITIONING_AND_ADVERSARIAL_AUDIT_ZH.md
git commit -m "docs: present AP-FDR contributions before provenance"
```

### Task 3: Verify and publish the material update

**Files:**
- Verify: `tests/test_material_integrity.py`
- Verify: all tracked files changed by Tasks 1-2

- [ ] **Step 1: Run the complete material-integrity suite**

Run:

```powershell
python -m pytest tests/test_material_integrity.py -q
```

Expected: all tests pass.

- [ ] **Step 2: Run whitespace and claim scans**

Run:

```powershell
git diff --check HEAD~2..HEAD
rg -n "1:4|1/5|80% 原创|算法主体 80%|minor reuse|mostly original" docs/superpowers/specs paper_material
```

Expected: `git diff --check` exits 0; the claim scan returns no current affirmative originality-ratio claim.

- [ ] **Step 3: Push without overwriting remote work**

```powershell
git fetch origin main
git merge-base --is-ancestor origin/main HEAD
git push origin HEAD:refs/heads/codex/novelty-framing-20260820
git push origin HEAD:refs/heads/main
```

Expected: both pushes succeed as fast-forwards and `origin/main` resolves to the local `HEAD` commit.


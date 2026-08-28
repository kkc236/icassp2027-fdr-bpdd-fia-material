# NA-FDR / LRS-FDR Main-Material Update Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make NA-FDR the named native-aligned foundation and LRS-FDR the final complete FDR module everywhere in the private material repository, with exact evidence, consistent statistics, and preserved historical identities.

**Architecture:** Treat the frozen design and imported experiment bytes as the two authorities. Add one self-contained evidence package and one canonical result page, then point the current-route, method, outline, novelty, and figure documents to those authorities. Preserve old EQuAL, AP-FDR, DCF, D-FINE-S, checkpoint, and run identifiers as historical records rather than renaming them.

**Tech Stack:** Markdown, JSON, CSV, SHA-256, PowerShell, Git.

---

### Task 1: Import the immutable experiment evidence

**Files:**
- Create: `paper_material/evidence/lrs_fdr_formal100_20260828/README.md`
- Create: `paper_material/evidence/lrs_fdr_formal100_20260828/MANIFEST.sha256`
- Create: `paper_material/evidence/lrs_fdr_formal100_20260828/independent-evaluation/original_fdr.json`
- Create: `paper_material/evidence/lrs_fdr_formal100_20260828/independent-evaluation/na_fdr.json`
- Create: `paper_material/evidence/lrs_fdr_formal100_20260828/independent-evaluation/lrs_fdr.json`
- Create: `paper_material/evidence/lrs_fdr_formal100_20260828/independent-evaluation/comparison.json`
- Create: `paper_material/evidence/lrs_fdr_formal100_20260828/training/original_fdr_results.csv`
- Create: `paper_material/evidence/lrs_fdr_formal100_20260828/training/na_fdr_results.csv`
- Create: `paper_material/evidence/lrs_fdr_formal100_20260828/training/lrs_fdr_results.csv`
- Create: `paper_material/evidence/lrs_fdr_formal100_20260828/authority/lrs_fdr_authority.json`
- Create: `paper_material/evidence/lrs_fdr_formal100_20260828/authority/lrs_fdr_gate0.json`
- Create: `paper_material/evidence/lrs_fdr_formal100_20260828/authority/lrs_fdr_args.yaml`

- [ ] Copy the exact source bytes from `research/fdr/evidence/lrs-fgl-9fa90780` in the completed experiment worktree. Rename only destination filenames; do not change JSON/CSV/YAML contents.
- [ ] Write `README.md` with the canonical-to-historical identity map, frozen evaluator settings, overall/scale tables, evidence limits, source commit `9fa90780`, and checkpoint hashes.
- [ ] Generate `MANIFEST.sha256` from every imported evidence file except the manifest itself, using repository-relative forward-slash paths.
- [ ] Parse all JSON files and assert that the separate-arm overall mAP/AP75 values equal the combined comparison JSON within `1e-12`.
- [ ] Recompute every manifest hash and require exact equality.
- [ ] Commit with `evidence: publish NA-FDR and LRS-FDR validation package`.

### Task 2: Replace the canonical FDR method page

**Files:**
- Modify: `paper_material/methods/FDR_ZH.md`
- Create: `paper_material/results/LRS_FDR_RESULTS_ZH.md`

- [ ] Rewrite `FDR_ZH.md` around one complete innovation: NA-FDR provides native-reference/native-assignment/normal-query alignment; LRS-FDR adds parameter-free layerwise reliability shrinkage inside that aligned formulation.
- [ ] Include the exact canonical configuration:

```yaml
cumulative: true
preliminary_box: false
distribution_feedback: false
fdr_loss:
  fgl_weight: 0.15
  supervise_pre_boxes: false
  supervise_dn_fdr: false
  edge_adaptive_fgl: false
  reliability_shrinkage_alpha: 0.25
```

- [ ] State that `reliability_shrinkage_alpha: 0.0` is NA-FDR (`w/o LRS`) and `0.25` is full LRS-FDR.
- [ ] Attribute 33-bin boundary distributions, non-uniform Integral, cumulative refinement, and basic FGL to D-FINE; claim only the native-aligned organization and exact LRS transform.
- [ ] Write `LRS_FDR_RESULTS_ZH.md` with the frozen overall, delta, scale, class-direction, late-training, and registered-gate results. Keep the single-seed and Tiny/Small regression warnings visible.
- [ ] Add direct relative links from both pages to the evidence package and frozen design.
- [ ] Search both pages and require zero paper-facing uses of `Clean FDR` except inside an explicit `历史运行标识` note.
- [ ] Commit with `docs: define NA-FDR and LRS-FDR as the final FDR method`.

### Task 3: Switch the material entry and current status

**Files:**
- Modify: `paper_material/README_ZH.md`
- Modify: `paper_material/CURRENT_RERUN_STATUS_ZH.md`

- [ ] Replace the D-FINE-S/EQuAL current-route banner with the author-approved RT-DETR-L route: LRS-FDR → BPDD → FIA.
- [ ] Put the FDR method page and LRS-FDR result page first in the reading order; move EQuAL and D-FINE-S to a clearly labeled historical/abandoned-route section.
- [ ] Add the three-arm overall metrics and deltas, using NA-FDR rather than Clean FDR in every paper-facing table.
- [ ] Explain that existing AP-FDR+BPDD/FIA checkpoints remain historical compatibility evidence and cannot be renamed as LRS-FDR combinations.
- [ ] Set the next experiment to the frozen second-dataset matrix: Baseline, Baseline + NA-FDR, and the complete submitted method; do not claim it is completed.
- [ ] Link the evidence package, method page, result page, and frozen design.
- [ ] Commit with `docs: switch the material entry to LRS-FDR`.

### Task 4: Update the paper argument and figure plan

**Files:**
- Modify: `paper_material/writing/ICASSP2027_OUTLINE_ZH.md`
- Modify: `paper_material/writing/NOVELTY_POSITIONING_AND_ADVERSARIAL_AUDIT_ZH.md`
- Modify: `paper_material/figures/FIGURE_PLAN_ZH.md`

- [ ] Replace the first contribution with a unified LRS-FDR contribution containing the NA-FDR foundation and LRS-FGL internal mechanism.
- [ ] Replace the obsolete AP-FDR internal-ablation plan with the completed three-row table: Original FDR / NA-FDR (`w/o LRS`) / LRS-FDR.
- [ ] Bind each claim to its own evidence: NA-FDR vs Original for the native-aligned design; LRS-FDR vs NA-FDR for LRS; LRS-FDR vs Original for the final module.
- [ ] Add the strongest reviewer attacks: “NA-FDR is only component deletion,” “LRS gain is only 0.011 pp mAP,” “Tiny AP falls,” “single seed,” and “second dataset missing,” with evidence-bounded responses.
- [ ] Rewrite the English abstract/contribution/method snippets so they use NA-FDR/LRS-FDR and do not retain stock-head preliminary or DN-FDR claims.
- [ ] Update Figure 1/2/4 to show native decoder reference, representability firewall, layerwise reliability schedule, total-weight conservation, and the three-arm result comparison.
- [ ] Commit with `docs: align the paper narrative with LRS-FDR evidence`.

### Task 5: Run the repository-wide consistency audit

**Files:**
- Verify: all files changed by Tasks 1-4

- [ ] Parse every newly added JSON file with `ConvertFrom-Json`.
- [ ] Recompute `MANIFEST.sha256` and require zero mismatches.
- [ ] Verify every relative Markdown link in the changed Markdown files resolves to an existing repository file, while ignoring HTTP(S) links and anchors.
- [ ] Search current-authority files and require:

```text
NA-FDR present
LRS-FDR present
current route != D-FINE-S
current route != EQuAL
paper-facing Clean FDR occurrences = 0
```

  Historical documents and explicit history/alias notes are excluded from the last three counts.
- [ ] Verify all reported overall and scale numbers against `independent-evaluation/comparison.json` with a deterministic PowerShell check.
- [ ] Run `git diff --check`, inspect `git diff --stat`, and inspect the complete diff for accidental evidence rewrites.
- [ ] Commit any audit corrections with `docs: close LRS-FDR material consistency audit`.

### Task 6: Push and prove remote state

**Files:**
- Verify: Git branch and remote only

- [ ] Push `codex/lrs-fdr-material-freeze` to `private-material` without force.
- [ ] Compare local `git rev-parse HEAD` with `git ls-remote private-material refs/heads/codex/lrs-fdr-material-freeze`; require exact OID equality.
- [ ] Confirm `git status --short --branch` is clean and tracks the pushed material branch.
- [ ] Publish the branch/commit/file links and state explicitly that no old evidence, checkpoints, or historical identifiers were rewritten.

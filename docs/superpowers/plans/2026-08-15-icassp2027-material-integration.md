# ICASSP 2027 FDR–BPDD–FIA Material Integration Plan

> Historical completed plan (superseded for FIA-only status): the pending-evidence assumptions below are retained only as implementation history. Current FIA-only P3-only results are recorded in `paper_material/results/FIA_RESULTS_STATUS_ZH.md`.

## Goal

Keep the private material repository aligned with the modified FIA implementation and prevent any pre-modification FIA experiment from returning to paper tables, plots, or prose.

## Corrected Evidence Policy

- Retain the audited RT-DETR-L, FDR, and FDR+BPDD result rows.
- Revoke all old standalone FIA and old FDR+FIA results, packages, screenshots, hashes, run identities, derived deltas, and conclusions.
- Revoke any old three-module evidence that is not bound to the modified FIA implementation.
- Register the confirmed P3-only modified-FIA three-module checkpoint as provisional evidence only.
- Do not fabricate standalone FIA or FDR+FIA values from the user's report that their reruns are positive.

## Confirmed New Three-Module State

The checkpoint DFR-BDPP-FIA-best.pt has been confirmed as the correct P3-only modified-FIA three-module checkpoint. Its best-validation record is:

- Precision: 0.56996
- Recall: 0.49848
- AP50: 0.48982
- mAP50–95: 0.29618
- Arithmetic observation relative to the current BPDD validation absolute value: +0.3922 percentage points

AP75, test metrics, and frozen-evaluator independent reevaluation remain pending. The record must stay outside the formal exact main table until those items are completed.

## Work Items

### 1. Revoke Old FIA Evidence

- Remove old FIA result rows from machine JSON and CSV files.
- Remove old screenshot and release evidence from the active manifest.
- Remove derived scale, class, and overall FIA deltas.
- Replace tests that require old values or old binary assets.
- Add guards against reintroducing revoked FIA source identities and checkpoint digests.

### 2. Rebind the Modified FIA Implementation

- Identify the exact modified source commit.
- Bind src/fia.py and all FIA-containing YAML files to that commit.
- Verify P3-only graph identity for the confirmed three-module checkpoint.
- Update implementation tests if the modified module contract differs from the current private tree.

### 3. Complete the Three-Module Evaluation

- Verify the checkpoint digest and source/config compatibility.
- Run frozen-evaluator val and test passes.
- Export P, R, AP50, AP75, mAP50–95, four-scale, and ten-class structured outputs.
- Record environment, dataset, command, and evaluator identity.
- Compare only with a compatible FDR+BPDD authority.

### 4. Locate Updated Standalone Assets

- Search GitHub branches, releases, workflow artifacts, and committed evidence for modified FIA-only and FDR+FIA runs.
- Reject assets that cannot be bound to the modified FIA source.
- If no asset is found, keep both rows as pending even though the user reports positive gains.

### 5. Refresh Paper Material

- Use FIA_RESULTS_STATUS_ZH.md as the single FIA evidence status entry.
- Keep the formal table restricted to the three audited non-FIA rows until independent FIA evaluation is complete.
- Show the confirmed three-module best-validation record only in a clearly provisional section.
- Regenerate figures only after the modified module structure and result authority are verified.

### 6. Verify Before Publication

- Scan active Markdown, JSON, CSV, and tests for revoked FIA values and identities.
- Run material integrity, method, configuration, and integration tests.
- Confirm no credential is tracked.
- Confirm the private remote matches the locally verified revision before publication.

## Completion Criteria

The correction is complete only when old FIA evidence cannot be reached through active tables, prose, status links, tests, or manifest entries; the modified three-module checkpoint has a complete independent evaluation; and standalone modified-FIA evidence is either imported with full provenance or explicitly remains pending.

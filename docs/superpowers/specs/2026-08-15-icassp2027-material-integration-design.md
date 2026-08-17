# ICASSP 2027 FDR–BPDD–FIA Material Integration Design

## Objective

Maintain one private repository containing the runnable FDR, BPDD, and modified FIA implementation together with evidence-safe ICASSP writing material. This is a migration, correction, and evidence-binding task rather than an algorithm redesign.

## Repository Scope

- Private repository: kkc236/icassp2027-fdr-bpdd-fia-material.
- Executable configurations for stock RT-DETR-L, FDR, FIA, FDR+BPDD, FDR+FIA, and FDR+BPDD+FIA.
- Training, evaluation, checkpoint, and reproducibility scripts.
- Method descriptions, experiment protocol, tables, evidence mapping, writing outline, and figure plan.

BPDD consumes FDR boundary distributions, so BPDD without FDR is not a valid model arm.

## FIA Evidence Correction

All results produced before the FIA modification are revoked. They must not remain available as historical observations, supplementary trends, approximate evidence, or paper-ready values.

The revoked scope includes old standalone FIA results, old FDR+FIA results, old screenshots, old result packages, and every table or conclusion derived from them.

A correct P3-only modified-FIA three-module checkpoint has been located. Its best-validation record is P=0.56996, R=0.49848, AP50=0.48982, and mAP50–95=0.29618. The arithmetic observation relative to the current BPDD validation absolute value is +0.3922 percentage points. AP75, test results, and a frozen-evaluator independent reevaluation are still unavailable, so this record remains provisional and cannot occupy a formal exact main-table row.

The user reports that the rerun standalone FIA and FDR+FIA experiments are positive, but auditable values have not been obtained and no confirmable updated assets have been found in the currently visible GitHub content.

## Evidence Contract

- Formal numeric tables retain only RT-DETR-L, FDR, and FDR+BPDD until updated FIA evidence is imported.
- Every imported FIA result must bind the modified source commit, model configuration, checkpoint digest, dataset identity, evaluation command, and structured output.
- Validation and test results remain separate.
- Training-log best values do not replace frozen-evaluator independent reevaluation.
- Values from different authorities may be shown only as explicitly labeled arithmetic observations.
- Missing AP75, scale, class, latency, multi-seed, and significance results remain unavailable.

## Documentation Contract

- FIA_RESULTS_STATUS_ZH.md is the single current status page for FIA evidence.
- No active document links to revoked FIA screenshots or result reports as evidence.
- No active paper table reproduces revoked FIA numbers, hashes, or run identities.
- Method and figure descriptions do not freeze FIA internals until the modified implementation is source-bound.

## Verification

The corrected repository is ready when:

1. revoked FIA values and source IDs are absent from active tables and prose;
2. the three non-FIA result rows agree with their evidence;
3. the provisional modified-FIA three-module checkpoint is clearly separated from formal exact results;
4. updated standalone FIA assets, when found, are bound to the modified source;
5. relevant code, configuration, integrity, naming, and credential tests pass;
6. the private remote matches the verified local state.

## Out of Scope

- Fabricating missing exact metrics.
- Treating user-reported positivity as a substitute for artifacts.
- Reusing revoked checkpoints or screenshots.
- Claiming strict paired FIA gains before paired independent evaluation.

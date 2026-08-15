# ICASSP 2027 FDR–BPDD–FIA Material Integration Design

## Objective

Create a new private GitHub repository that consolidates the existing FDR, BPDD, and FIA implementation and all usable paper-writing material. This is a migration and normalization task, not an algorithm redesign.

## Repository

- Proposed repository: `kkc236/icassp2027-fdr-bpdd-fia-material`
- Visibility: private
- Code base: current `fdr-bdpp-fia` tree
- Default branch: `main`
- The existing repository remains unchanged.

## Included Content

1. Runnable FDR, BPDD, and FIA source code.
2. Standalone or minimum-valid method configurations:
   - stock RT-DETR-L;
   - FDR;
   - FIA;
   - FDR + BPDD, because BPDD consumes FDR boundary distributions;
   - FDR + FIA;
   - FDR + BPDD + FIA.
3. Training, evaluation, checkpoint, and reproducibility scripts.
4. Unit and integration tests for each method and the complete model.
5. Authoritative FDR and BPDD experiment evidence.
6. Available FIA validation evidence, including the reported VisDrone validation and test metrics.
7. A `paper_material/` package containing method descriptions, experiment protocol, tables, evidence mapping, claim boundaries, and an ICASSP writing outline.

## Normalized Structure

```text
configs/
src/
scripts/
tests/
third_party/
paper_material/
  README_ZH.md
  methods/
  experiments/
  results/
  evidence/
  writing/
  figures/
```

## Naming Contract

- FIA is the only accepted name for the third method.
- Filenames, directories, Python identifiers, configuration keys, command-line options, result keys, and prose use `FIA` or `fia` consistently.
- Imported historical material is normalized before inclusion.
- A repository-wide test rejects legacy third-method identifiers.

## Evidence Contract

- Every imported result records its source commit SHA and available artifact checksum.
- Strict RT-DETR-L, FDR, and FDR + BPDD values come from committed structured evidence.
- The currently available complete-model terminal result is recorded at its displayed precision and marked as screenshot-level evidence until an exact JSON or CSV is available.
- Values from different dataset splits or evaluation authorities are not subtracted from one another.
- Unsupported AP75, latency, multi-seed, and significance claims remain explicitly unavailable.

## Verification

The repository is ready only when:

1. the naming scan passes;
2. each method entry point imports successfully;
3. all declared YAML configurations parse and build;
4. relevant unit and integration tests pass;
5. paper tables agree with the evidence index;
6. no secret or credential is present;
7. the new GitHub repository is confirmed private after push.

## Out of Scope

- New training runs.
- Algorithm redesign or hyperparameter tuning.
- Fabricating missing exact metrics from rounded terminal output.
- Changing or deleting the existing GitHub repository.

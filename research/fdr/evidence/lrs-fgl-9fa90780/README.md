# LRS-FGL Formal100 Seed-0 Evidence

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: validate
- Origin Date: 2026-08-28
- Verification Status: ANALYZED
- Version Label: lrs_fgl_formal100_validation_v2
- Source Commit: `9fa9078011d92cc23fc1f0eec06ff34983986ff0`
- Scope: VisDrone validation, seed 0, 100 epochs

## Result identity

All three arms contain exactly 100 continuous epoch rows. Each arm is selected
independently by maximum `metrics/mAP50-95(B)`, and Precision, Recall, and mAP50
are reported from that same selected row. This is a fixed-seed paired ablation,
not a multi-seed significance result.

| Arm | Best epoch | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|---:|
| Original FDR | 92 | 0.57064 | 0.49006 | 0.48473 | 0.29078 |
| Clean FDR | 88 | **0.58777** | 0.49849 | **0.49320** | 0.29696 |
| Clean FDR + LRS-FGL | 84 | 0.57860 | **0.50141** | 0.49188 | **0.29703** |

### Final method versus Original FDR

| Metric | Absolute delta | Percentage-point delta |
|---|---:|---:|
| Precision | +0.00796 | +0.796 pp |
| Recall | +0.01135 | +1.135 pp |
| mAP50 | +0.00715 | +0.715 pp |
| mAP50-95 | +0.00625 | +0.625 pp |

The final method is numerically positive over Original FDR in all four headline
metrics. This is the defensible overall-method comparison.

### LRS-FGL internal ablation versus Clean FDR

| Metric | Absolute delta | Percentage-point delta |
|---|---:|---:|
| Precision | -0.00917 | -0.917 pp |
| Recall | +0.00292 | +0.292 pp |
| mAP50 | -0.00132 | -0.132 pp |
| mAP50-95 | +0.00007 | +0.007 pp |

LRS-FGL is Recall-oriented at its selected checkpoint. Its mAP50-95 increment
over Clean FDR is only `0.00007`, so it must not be described as a significant,
stable, broad, or large gain.

## Independent frozen-checkpoint evaluation

The three training-best checkpoints were evaluated again with one frozen,
same-evaluator pass per checkpoint. The evaluation used the VisDrone validation
split (548 images, 38,759 objects), `imgsz=640`, `batch=8`, `conf=0.001`,
`max_det=300`, FP32, and the same native validator implementation for every arm.
This table is the authority for AP75, class-wise AP, and scale-wise AP. Small
differences from the training-log table above are expected because this is an
independent evaluation pass.

| Arm | Precision | Recall | F1 | AP50 | AP75 | mAP50-95 |
|---|---:|---:|---:|---:|---:|---:|
| Original FDR | 0.570249 | 0.491417 | 0.527907 | 0.484700 | 0.294070 | 0.290698 |
| Clean FDR | **0.587045** | 0.498339 | **0.539067** | **0.493119** | 0.301061 | 0.296855 |
| Clean FDR + LRS-FGL | 0.579512 | **0.500606** | 0.537177 | 0.491805 | **0.305773** | **0.296968** |

### Scale-wise mAP50-95

Scale bins are defined in network-input pixels by the square root of box area:
Tiny `<16`, Small `16--32`, Medium `32--96`, and Large `>=96`.

| Arm | Tiny (20,860) | Small (12,420) | Medium (5,349) | Large (130) |
|---|---:|---:|---:|---:|
| Original FDR | 0.147025 | 0.291050 | 0.395473 | 0.380301 |
| Clean FDR | **0.157561** | **0.300759** | 0.400317 | **0.472407** |
| Clean FDR + LRS-FGL | 0.149050 | 0.298944 | **0.400401** | 0.368274 |

Clean FDR improves over Original FDR in every headline metric and every scale
bin in this evaluation. Relative to Clean FDR, LRS-FGL changes Recall by
`+0.002268`, AP75 by `+0.004712`, and mAP50-95 by `+0.000113`, while changing
Precision by `-0.007533`, AP50 by `-0.001314`, Tiny mAP by `-0.008511`, and
Small mAP by `-0.001815`. LRS-FGL is therefore supported only as a targeted
strict-IoU/Recall trade-off, not as a general small-object improvement. The
Large result is descriptive only because that bin contains just 130 objects.

## Late-training stability

| Arm | Epoch 91-100 mean mAP50-95 | Linear slope per epoch |
|---|---:|---:|
| Original FDR | 0.289968 | -0.00003273 |
| Clean FDR | **0.296102** | +0.00004303 |
| Clean FDR + LRS-FGL | 0.295253 | -0.00024321 |

LRS-FGL is `-0.000849` below Clean FDR on the registered last-ten mean and has
a negative late slope. The saved best is therefore a weak point estimate rather
than evidence of a stronger terminal plateau.

## Mechanism and runtime checks

- Gate0 passed on all five shallow decoder layers.
- Representable beneficiary fractions: 33.6%--34.8% of all matches.
- Beneficiary weight-to-count ratios: 0.818--0.830.
- Saturated beneficiary edges: 0.
- Maximum per-image conservation error: `2.98e-8`.
- Optimizer evidence rows: 10,556; skipped AMP steps: 0; non-finite rows: 0.
- LRS FDR-gradient p99: `17.0808`; paired Clean p99: `17.2658`.

The pre-training mechanism and numerical-stability checks pass. The registered
training-time low-IoU next-layer IoU diagnostic was not recorded, so the causal
mechanism gate remains unmeasured.

## Registered decision audit

| Gate | Required | Observed | Status |
|---|---:|---:|---|
| Strong best mAP50-95 | >= 0.29796 | 0.29703 | FAIL |
| Recall at selected row | >= 0.49849 | 0.50141 | PASS |
| Epoch 91-100 mean over Clean | > 0.296102 | 0.295253 | FAIL |
| AP75 regression | <= 0.0005 | +0.004712 | PASS |
| Tiny AP | non-negative | -0.008511 | FAIL |
| Low-IoU next-layer IoU | >= 3 transitions positive | not recorded | UNMEASURED |

**Verdict:** strong paper-level GO is not met. The aggregate final method is a
clear numerical improvement over Original FDR, while LRS-FGL is only a
weak internal-ablation point improvement over Clean FDR. The independent
evaluation supports an AP75/Recall-oriented interpretation, but Tiny AP and
late-training stability do not support a broad-improvement claim. The registered
next-layer mechanism diagnostic remains unmeasured.

## Statistical fallacy scan

- Coverage: 11/11 checked.
- Simpson's paradox, ecological fallacy, Berkson's paradox, collider bias,
  base-rate neglect, survivorship bias, correlation/causation, and reverse
  causality: not applicable to this fixed detector ablation at the available
  aggregation level.
- Regression to the mean: CAUTION because a single best epoch is selected from
  100 noisy validation observations.
- Look-elsewhere effect: CAUTION because the result emphasizes the maximum epoch
  while the registered tail mean is negative versus Clean.
- Garden of forking paths: CAUTION because earlier discarded variants exist;
  the frozen Gate0, unchanged alpha, source commit, and preserved failed evidence
  reduce but do not eliminate this risk.

No p-value, confidence interval, or multi-seed effect estimate is available.
The metric differences are descriptive only.

## Highest-success next step

Do not tune `alpha0` or add another module after observing this validation run.
Use Clean FDR as the robust core result. If LRS-FGL remains in the submitted
method, frame it narrowly as an AP75/Recall-oriented training refinement and
retain Clean FDR as its direct internal control. The highest-value next
experiment is a frozen second-dataset matrix containing Baseline, Baseline +
Clean FDR, and the complete submitted method; duplicating every internal switch
on the second dataset is unnecessary.

## Included artifacts

- `original-fdr/results.csv`
- `clean-fdr/results.csv`
- `lrs-fgl-formal100/results.csv`
- `lrs-fgl-formal100/args.yaml`
- `authority/formal-seed0-lrs-fdr-v1.json`
- `gate0/lrs-fgl-gate0.json`
- `comparison.json`
- `independent-evaluation/original_fdr.json`
- `independent-evaluation/clean_fdr.json`
- `independent-evaluation/clean_fdr_plus_lrs_fgl.json`
- `independent-evaluation/comparison.json`

The 67 MB checkpoints, dataset, logs, caches, and credentials are intentionally
excluded. Checkpoint SHA-256 values are recorded in `comparison.json`.

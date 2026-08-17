# ACR-BPDD Design

## Objective

Improve BPDD on top of the frozen FDR detector without changing the inference graph, detector matching, classification loss, Query selection, decoder topology, or the established FDR mechanism. The candidate is compared with the existing mature FDR authority; a repeated FDR Formal100 is intentionally deferred to the final ablation campaign.

## Evidence and failure mechanism

BPDD v1 produced positive Test-set deltas over FDR (mAP +0.366 pp, AP50 +0.535 pp, AP75 +0.375 pp) but reduced Recall by 0.554 pp. Its signal audit showed that only about 52.17% of eligible layer-edge terms were active. Two implementation properties can therefore limit the benefit:

1. The BPDD sum is divided by every eligible edge, including zero-reliability edges, so useful supervision is diluted as the active ratio falls.
2. The BPDD gradient also enters shared decoder features. This can perturb classification and Query representations even though BPDD is intended to improve only FDR localization distributions, providing a plausible explanation for the Recall loss.

## Candidate: Active-Confidence-Renormalized BPDD

ACR-BPDD makes two isolated training-time changes.

### Active-confidence renormalization

For reliability-weighted KL terms `r_i * KL_i`, use

`L = lambda * sum(r_i * KL_i) / max(sum(stopgrad(r_i)), rho * N)`

where `N` is the number of eligible terms and `rho=0.5`. The floor limits the maximum scale amplification to 2x relative to BPDD v1. The reliability mass is detached and therefore cannot be optimized to manipulate the denominator. Empty or inactive batches remain exactly zero and finite.

### Common-gradient firewall

The forward loss and stock/FDR losses are unchanged. During each accumulation micro-batch, compute the BPDD-only gradient for common model parameters and accumulate it in FP32. Immediately after AMP unscaling and before clipping, subtract this BPDD-only contribution from common parameters. BPDD gradients remain on the FDR distribution box heads. This targets localization while preserving shared decoder/classification learning.

The firewall is training-only and must not add checkpoint parameters or alter the inference graph.

## Compatibility and ablation contract

- Existing BPDD v1 behavior remains selectable.
- ACR normalization and the common-gradient firewall are independent YAML switches.
- FDR authority and hyperparameters remain unchanged.
- Deployment is the same ordinary FDR graph; BPDD/ACR owns no inference parameters.
- The new run starts from the frozen FDR initial state, not from a BPDD or screen checkpoint.

## Adversarial gates before Formal100

1. Mathematical tests: exact denominator, detached reliability, zero-active, no-match, FP16 input, and finite gradients.
2. Gradient tests: stock/FDR total gradient unchanged when BPDD is disabled; with firewall enabled BPDD contribution is absent from common parameters and present on FDR distribution heads.
3. Protocol tests: same dataset, initialization, seed, optimizer, AMP scale, batch, augmentation, Query count, and validation contract.
4. Real CUDA preflight: VisDrone batch 8 forward/backward/optimizer/checkpoint reload under fixed AMP 128.

## Formal run

After all gates pass, run full VisDrone train, seed 0, 100 epochs directly. Publish immutable per-epoch evidence and checkpoints asynchronously. Compare the final independent evaluation with mature FDR100 as `preliminary_cross_run`; reserve `strict_paired` claims for the later complete ablation rerun.


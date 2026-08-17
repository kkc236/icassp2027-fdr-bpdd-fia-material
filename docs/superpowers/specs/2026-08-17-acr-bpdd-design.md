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

### Common-gradient firewall by detached head replay

The stock/FDR forward and losses are unchanged. During the real decoder forward, temporary pre-hooks capture the actual input of each of the six FDR distribution heads and immediately detach it. The hooks are removed before the forward returns. BPDD then replays only the six small distribution MLPs on these detached inputs and reconstructs the same cumulative corner logits.

The replayed values must match the original cumulative logits within `1e-6`. Its graph remains connected to the distribution-head parameters but has no path to Backbone, Encoder, shared Decoder, classification heads, Query selection, or preliminary-box features. This provides the intended firewall without a second shared-network backward pass. The replay is training-only, owns no parameters, leaves no persistent hooks, and cannot alter the inference graph or checkpoint state.

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

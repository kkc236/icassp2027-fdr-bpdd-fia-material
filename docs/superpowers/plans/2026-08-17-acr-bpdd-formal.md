# ACR-BPDD Formal100 Implementation Plan

1. Extend BPDD numerical options with a backward-compatible normalization mode and floor. Add failing unit tests first, then implement the exact ACR formula and evidence fields.
2. Add a YAML-selectable common-gradient firewall using detached replay of the six distribution heads. Test cumulative-logit equivalence, head-only gradients, transient-hook cleanup, deepcopy/checkpoint safety, and disabled/eval equivalence.
3. Add the ACR-BPDD model YAML and training entrypoint while retaining BPDD v1. Freeze the source/protocol identity and validate all experiment parameters against the FDR authority.
4. Run the complete local regression suite, then a real RTX 4090 VisDrone batch-8 CUDA preflight with MuSGD and fixed AMP scale 128. Verify checkpoint save/reload and inference-graph identity.
5. Deploy the commit as an immutable server source directory, start a fresh full-data seed-0 100-epoch run, and start non-blocking per-epoch publication with resume support.
6. At epoch 100, run independent val/test evaluation, scale/category breakdown, parameter/GFLOPs/latency audit, SHA256 inventory, and upload the final report. Mark comparisons to the historical FDR run as preliminary until the final paired ablation rerun.

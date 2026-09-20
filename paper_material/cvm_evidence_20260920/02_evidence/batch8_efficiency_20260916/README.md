# Batch-8 inference benchmark evidence

Inference only, five existing VisDrone checkpoints, 640 square, FP32, batch 8.
Frozen training sources and checkpoints must match the earlier batch-1 measurement.
The experiment records batch latency, amortized per-image cost, throughput and memory.
Amortized time is not a single-request response latency. No training or UAVDT work.

Completed: five arms, 100 warmup batches and 300 measured batches per arm;
1,500 measured batches / 12,000 images in total. All observed model input shapes
were `[8,3,640,640]`, CUDA FP32. Five checkpoint hashes and eight source hashes
matched before/after and matched the earlier batch-1 run.

See [verified report](../../results/CURRENT_BATCH8_EFFICIENCY_ZH.md),
[raw result](v1/efficiency.json), [completion receipt](v1/COMPLETE.json),
[transport manifest](transport_manifest.json), and [verification](verification.json).
No GitHub push was performed in this measurement task.

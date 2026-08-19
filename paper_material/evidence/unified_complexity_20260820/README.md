# Unified complexity benchmark evidence

- Status: completed on 2026-08-20 CST; server intentionally left running at the user's request.
- Raw result: `unified_complexity_raw.json` (SHA-256 `71ecb8f21030d416b3bb5d736cb4cc03a5a53afce98bc05c494e748087c0343c`).
- Runner: `scripts/benchmark_unified_complexity.py` (SHA-256 `e74b22dc626ec335f91b1b01b87c60fe32e8b2d48cbad9a6281b168c55e838e3`).
- Runtime source checkout: `uav-detection-baselines@07d900d32a0c810cce43b8146abe78040e46e677`.
- Environment: NVIDIA GeForce RTX 4090; Python 3.10.12; PyTorch 2.5.1+cu121; CUDA 12.1; cuDNN 90100; Ultralytics 8.4.90.
- Frozen protocol: 640×640, batch 1, FP32, one fixed seeded uint8 RGB image, 100 warm-up calls, 300 measured calls, CUDA synchronization before and after each call, `conf=0.001`, `max_det=300`.
- Latency scope: the public `RTDETR.predict` path, including preprocessing, network inference and postprocessing. FPS is `1000 / median latency (ms)`; P90 and peak allocated CUDA memory are retained.
- Authorities measured: canonical baseline; canonical FDR; strict-pair FDR control; strict-pair FDR+BPDD; canonical P3-only FDR+BPDD+FIA.

The strict-pair FDR and FDR+BPDD rows have identical Params, GFLOPs and peak memory. Their median-latency difference is −0.0848 ms, which is measurement noise rather than an acceleration claim. The first diagnostic run that passed the deprecated `half=False` predictor argument is excluded; this archived raw file is the clean rerun with the model explicitly cast to FP32 and no per-call warning I/O.

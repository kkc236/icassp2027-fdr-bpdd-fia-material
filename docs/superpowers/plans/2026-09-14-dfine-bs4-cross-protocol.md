# D-FINE batch-4 cross-protocol implementation plan

**Goal:** Train one valid scratch D-FINE-L run at batch 4 and compare frozen joint weights under a common evaluator, without retraining the joint model.

**Architecture:** Isolated official D-FINE checkout; a thin runner records initialization, resolved settings, chronological validation and atomic global-best/final snapshots. Standalone exporters map both frameworks to original-pixel boxes. Existing YOLO-derived labels are the common source of ground truth.

**Tech stack:** PyTorch, official D-FINE 267a6da, existing Ultralytics runtime, pycocotools, pytest.

- [x] Verify scratch backbone freeze/LR mismatch; use trainable backbone and BN with AdamW 0.00025, explicitly documented as a scratch adaptation.
- [x] Create a fresh batch-4 FP32 100-epoch config and runner; preserve native augmentation/stage behavior and record it.
- [x] Add tests for filename-to-COCO-ID mapping, missing images, empty predictions, perfect AP at maxDet=300 and nonsquare image coordinates.
- [x] Correct both exporters and common evaluator; use identical geometry, confidence and output cap; preserve original checkpoint bytes.
- [x] Deploy isolated files, run preflight, launch one fresh run; observe real training progress.
- [x] Queue best/last val/test common evaluation automatically; freeze selection rules and record all protocol differences.
- [x] Deliver Chinese protocol, verification results and live run location. Do not label this as matched-training or official VisDrone challenge evaluation.

Verification: 17 targeted local tests passed. Real CPU export and common COCO evaluation on two validation images passed for both model implementations. Joint history reached epoch100. New D-FINE completed its first epoch and entered the second. Full 100-epoch training/evaluation remain pending and are supervised automatically.

User authorized implementation and deployment in the current task; execute inline. No new hyperparameter search or joint-model training is authorized/needed.

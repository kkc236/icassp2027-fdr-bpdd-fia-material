# Ultralytics-D-FINE Evaluation Deployment Implementation Plan

> **For agentic workers:** Implement this plan task-by-task with verification checkpoints. The user's existing Ultralytics checkpoints are read-only inputs; never retrain or overwrite them.

**Goal:** Deploy a reproducible, cross-framework VisDrone evaluation path that loads the existing Ultralytics joint checkpoint correctly, exports a versioned prediction contract, and keeps D-FINE-L in its own official environment.

**Architecture:** The Ultralytics repository owns one exporter that registers the custom FDR modules and loads the exact Capacity-BPDD/FIA graph from its YAML. The D-FINE repository owns its native inference/post-processing. Both write the same per-image prediction JSON schema; a common evaluator consumes those files. No model source files are imported across repositories.

**Tech Stack:** Python 3.11+, PyTorch, Ultralytics 8.4.90, official D-FINE, JSON/JSONL, pytest, SSH/SCP deployment.

---

### Task 1: Define and test the prediction contract

**Files:**
- Create: `tmp-work/bpdd-capacity-v2-fia/src/common_prediction_contract.py`
- Test: `tmp-work/bpdd-capacity-v2-fia/tests/test_common_prediction_contract.py`

- [ ] **Step 1: Write the failing tests.** Test that a prediction row requires `image_id`, `width`, `height`, and a list of `{bbox_xyxy, score, category_id}` detections; reject non-finite values, wrong box length, category outside 0–9, and negative width/height.
- [ ] **Step 2: Run the focused test and confirm it fails because the contract module is missing.**
- [ ] **Step 3: Implement only schema validation and JSONL writing/reading.** The writer must use UTF-8, one row per image, sorted keys, and refuse duplicate `image_id` values.
- [ ] **Step 4: Run the focused test and the existing contract tests.**

### Task 2: Add an Ultralytics joint-checkpoint exporter

**Files:**
- Create: `tmp-work/bpdd-capacity-v2-fia/scripts/export_joint_predictions.py`
- Test: `tmp-work/bpdd-capacity-v2-fia/tests/test_export_joint_predictions.py`

- [ ] **Step 1: Write tests around pure helpers.** Verify checkpoint selection prefers `ema` only when present, refuses a missing state, maps the current custom model output to `xyxy` pixels exactly once, and records the actual model class/config hash.
- [ ] **Step 2: Run tests and confirm the new exporter helpers are absent.**
- [ ] **Step 3: Implement the CLI.** Required inputs: `--checkpoint`, `--model-yaml`, `--data`, `--output`, `--device`; default `--imgsz 640`, `--conf 0.001`, `--max-det 300`, `--half false`. Register FDR modules, instantiate `CapacityBPDDFIASafeDetectionModel` with `nc=10`, load the EMA/model state strictly, and run the existing `RTDETRValidator` dataset once. Export the validator's already-postprocessed `bboxes/conf/cls` after converting input-space coordinates to original pixels. Do not apply a second sigmoid, top-k, or NMS.
- [ ] **Step 4: Run the helper and dry-run tests.** A full validation is allowed only when the checkpoint exists; no training call is made.

### Task 3: Create the D-FINE-side export shim

**Files:**
- Create: `tmp-work/icassp2027-fdr-bpdd-fia-material/paper_material/evidence/visdrone_dfine_l_external_20260913/export_dfine_predictions.py`
- Create: `tmp-work/icassp2027-fdr-bpdd-fia-material/paper_material/evidence/visdrone_dfine_l_external_20260913/dfine_l_visdrone_control.yml`
- Create: `tmp-work/icassp2027-fdr-bpdd-fia-material/paper_material/evidence/visdrone_dfine_l_external_20260913/README.md`

- [ ] **Step 1: Write a fixture test for D-FINE output conversion.** Test normalized cxcywh→pixel xyxy, category IDs 0–9, and the official sigmoid/top-k output shape.
- [ ] **Step 2: Run it red.**
- [ ] **Step 3: Implement a standalone shim that imports only D-FINE, converts its native `labels/boxes/scores` output, and writes the Task 1 JSONL.** Set `remap_mscoco_category=false`; reject missing or non-10-class mappings.
- [ ] **Step 4: Add README commands for environment creation, deterministic YOLO→COCO conversion, validation, and export.** State explicitly that D-FINE training is optional and separate from the existing Ultralytics checkpoint.

### Task 4: Add the common evaluator and replay gate

**Files:**
- Create: `tmp-work/icassp2027-fdr-bpdd-fia-material/paper_material/evidence/visdrone_dfine_l_external_20260913/evaluate_common.py`
- Test: `tmp-work/bpdd-capacity-v2-fia/tests/test_common_evaluator.py`

- [ ] **Step 1: Write tests for same-image matching, AP input validation, and duplicate/missing image detection.**
- [ ] **Step 2: Run red.**
- [ ] **Step 3: Implement a thin adapter to the frozen Ultralytics 8.4.90 detection metric path, with an optional COCOeval report kept in a separate field.** The evaluator must not alter model predictions and must record metric provenance.
- [ ] **Step 4: Run the tests and the existing native validation replay.** The replay must identify the source checkpoint, data signature, and framework version.

### Task 5: Deploy without touching training outputs

**Files/targets:**
- Server source tree `/root/sj-tmp/lrs-v2/bpdd-capacity-v2-fia-code`
- Server evaluation package `/root/sj-tmp/eval/visdrone_dfine_l_external_20260913`

- [ ] **Step 1: Read-only preflight:** verify disk space, source commit, Ultralytics version, dataset counts/signature, and the actual joint checkpoint path.
- [ ] **Step 2: Copy only the new scripts/config/README and do not copy raw data or credentials.**
- [ ] **Step 3: Run syntax/import/dry-run checks on the server.**
- [ ] **Step 4: Run the existing joint checkpoint validation export once.** Save logs and a manifest under a new evaluation directory; never overwrite the archived training evidence.
- [ ] **Step 5: Mark D-FINE-L as `not_started` until an official checkpoint or a separately authorized training run exists.**

### Task 6: Publish auditable metadata

**Files:**
- Create: `paper_material/evidence/visdrone_dfine_l_external_20260913/authority.json`
- Create: `paper_material/evidence/visdrone_dfine_l_external_20260913/result_template.json`

- [ ] **Step 1: Write tests that incomplete runs cannot be marked `complete`.**
- [ ] **Step 2: Generate authority metadata with source commits, config hashes, dataset signature, checkpoint hash, evaluation settings, and status.**
- [ ] **Step 3: Run the full focused test suite and inspect the generated manifest.**
- [ ] **Step 4: Commit only the new deployment/evaluation files to the materials repository; leave unrelated user changes untouched.**


# D-FINE-L queued training and cross-protocol comparison Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** After the running Capacity-BPDD arm finishes, automatically train an official D-FINE-L VisDrone baseline and produce auditable cross-framework comparison artifacts without modifying existing Ultralytics runs.

**Architecture:** A materials-side package provides deterministic YOLO→COCO conversion, an explicit D-FINE-L scratch configuration, a completion-gated server watcher, and a common COCO JSONL/evaluator path. The watcher first validates the completed BPDD run, then runs D-FINE-L in `/root/sj-tmp/dfine-official`, exports both read-only checkpoints, and writes status/manifest files under a new timestamped evaluation directory.

**Tech Stack:** Official D-FINE PyTorch checkout, Python 3.11+, PyTorch/torchvision, pycocotools, Bash, JSON/JSONL, SHA-256, SSH/SCP.

---

### Task 1: Add deterministic VisDrone conversion and D-FINE-L control config

**Files:**
- Create: `paper_material/evidence/visdrone_dfine_l_external_20260913/convert_visdrone_yolo_to_coco.py`
- Modify: `paper_material/evidence/visdrone_dfine_l_external_20260913/dfine_l_visdrone_control.yml`
- Test: `tests/test_dfine_visdrone_conversion.py`

- [ ] **Step 1: Write failing tests** for YOLO normalized boxes, zero-based 10-class IDs, deterministic image ordering, invalid class/box rejection, and expected split counts.
- [ ] **Step 2: Run `pytest tests/test_dfine_visdrone_conversion.py -q` and confirm the converter import is missing.**
- [ ] **Step 3: Implement conversion** that reads `<root>/images/<split>` and `<root>/labels/<split>`, obtains image width/height with PIL, emits COCO `images/annotations/categories`, converts `xywh` normalized boxes to pixel `xywh`, and writes atomically with sorted IDs. The converter must refuse missing labels, class IDs outside 0..9, non-finite values, and out-of-range normalized coordinates.
- [ ] **Step 4: Make the config self-contained for server substitution.** Keep official HGNetv2-B4/D-FINE-L graph, set `num_classes: 10`, `remap_mscoco_category: False`, `HGNetv2.pretrained: False`, `epochs: 100`, `seed: 0`, `eval_spatial_size: [640, 640]`, total batch 8, and explicit train/val `img_folder`/`ann_file` placeholders replaced by the launcher.
- [ ] **Step 5: Run focused conversion tests and `python -m py_compile` on the converter.**

### Task 2: Add queued server launcher and post-training pipeline

**Files:**
- Create: `paper_material/evidence/visdrone_dfine_l_external_20260913/prepare_dfine_l_server.sh`
- Create: `paper_material/evidence/visdrone_dfine_l_external_20260913/run_dfine_l_after_bpdd.sh`
- Create: `paper_material/evidence/visdrone_dfine_l_external_20260913/cross_protocol_pipeline.sh`
- Modify: `paper_material/evidence/visdrone_dfine_l_external_20260913/README.md`

- [ ] **Step 1: Add `prepare_dfine_l_server.sh`** to verify GPU/PyTorch, copy the pinned official source bundle into `/root/sj-tmp/dfine-official` only when absent, create a dedicated environment/output directory, run the converter, and write source/config/data hashes. It must exit nonzero on existing non-empty output or count/class mismatch.
- [ ] **Step 2: Add `run_dfine_l_after_bpdd.sh`** that polls the exact BPDD PID, requires `results.csv` epoch 100 and non-empty `last.pt`/`best.pt`, then calls the prepare script and launches official `train.py` with `--use-amp --seed=0 --device=cuda:0 --output-dir=/root/sj-tmp/dfine-runs/dfine-l-visdrone-20260914`. It must create a status JSON atomically and never use `best_stg2.pth` as a resume checkpoint.
- [ ] **Step 3: Add `cross_protocol_pipeline.sh`** to select D-FINE val best, export D-FINE predictions, export the read-only Ultralytics joint checkpoint, run `evaluate_common.py` on both val/test COCO annotations, and write a manifest that labels the comparison `controlled_external_baseline`.
- [ ] **Step 4: Update README** with exact paths, restart/resume commands, failure states, no-weight/no-raw-data publication rule, and the statement that D-FINE is not imported into Ultralytics.

### Task 3: Validate locally before server deployment

**Files:**
- Test: `tests/test_dfine_queued_pipeline.py`

- [ ] **Step 1: Test that a watcher refuses incomplete BPDD results, duplicate output directories, missing D-FINE source, and missing checkpoint.**
- [ ] **Step 2: Test atomic status transitions `waiting → preparing → training → evaluating → complete` and failure capture.**
- [ ] **Step 3: Run the D-FINE adapter tests, existing materials tests, YAML/JSON parsing, `git diff --check`, and compile checks.**

### Task 4: Deploy and arm the watcher

**Targets:**
- Server source: `/root/sj-tmp/lrs-v2/bpdd-capacity-v2-fia-code`
- Server package: `/root/sj-tmp/eval/visdrone_dfine_l_external_20260913`
- Watcher log: `/root/sj-tmp/eval/dfine_l_after_bpdd_20260914.log`

- [ ] **Step 1: Read-only preflight** disk space, current BPDD PID, source bundle SHA-256, VisDrone split counts, and GPU visibility.
- [ ] **Step 2: Copy only scripts/config/README and the pinned source bundle; do not copy credentials, raw images, labels, or checkpoints to GitHub.**
- [ ] **Step 3: Run server-side syntax/import/converter dry-runs and verify the generated COCO counts before arming.**
- [ ] **Step 4: Start the watcher with `nohup`, record its PID and status file, and verify the current BPDD process remains untouched.**

### Task 5: Verify and publish only auditable metadata

**Files:**
- Modify: `paper_material/evidence/visdrone_dfine_l_external_20260913/authority.json`
- Modify: `paper_material/evidence/visdrone_dfine_l_external_20260913/result_template.json`

- [ ] **Step 1: On completion, download only manifests, logs, metrics JSON/CSV, and SHA-256 records.**
- [ ] **Step 2: Verify D-FINE val/test use the same COCO evaluator settings (`imgsz=640`, `max_det=300`, no TTA/NMS) and that the Ultralytics joint checkpoint is read-only.**
- [ ] **Step 3: Update `authority.json` from `not_started` to `complete` only after checkpoint, prediction, and evaluator manifests pass; otherwise preserve the explicit failure state.**
- [ ] **Step 4: Commit and push only the new metadata and scripts to the materials branch; leave pre-existing untracked user directories untouched.**

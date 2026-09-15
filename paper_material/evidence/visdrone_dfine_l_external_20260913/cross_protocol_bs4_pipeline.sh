#!/usr/bin/env bash
set -euo pipefail
PACKAGE_ROOT="${PACKAGE_ROOT:-/root/sj-tmp/eval/visdrone_dfine_bs4_cross_20260914}"
DATA_ROOT="${DATA_ROOT:-/root/sj-tmp/datasets/VisDrone}"
COCO_ROOT="${COCO_ROOT:-/root/sj-tmp/datasets/VisDrone-coco}"
DFINE_ROOT="${DFINE_ROOT:-/root/sj-tmp/dfine-bs4-official}"
DFINE_OUTPUT="${DFINE_OUTPUT:-/root/sj-tmp/dfine-runs/dfine-l-visdrone-bs4-scratch-cross-20260914}"
DFINE_CONFIG="${DFINE_CONFIG:-$DFINE_ROOT/configs/dfine/dfine_hgnetv2_l_visdrone_bs4_scratch.yml}"
CODE_ROOT="${CODE_ROOT:-/root/sj-tmp/eval/uav-detection-baselines-fb0a6a16}"
JOINT_CHECKPOINT="${JOINT_CHECKPOINT:-/root/sj-tmp/runs/formal-safe-capacity-fia-20260912-lrsv2/formal-seed0-capacity-v3-safe-fia/weights/best.pt}"
JOINT_LAST_CHECKPOINT="${JOINT_LAST_CHECKPOINT:-/root/sj-tmp/runs/formal-safe-capacity-fia-20260912-lrsv2/formal-seed0-capacity-v3-safe-fia/weights/last.pt}"
JOINT_MODEL_YAML="${JOINT_MODEL_YAML:-$CODE_ROOT/configs/rtdetr-l-lrs-gfdr-capacity-v3-safe-bpdd-fia.yaml}"
EVAL_ROOT="${EVAL_ROOT:-/root/sj-tmp/eval/visdrone_dfine_bs4_results_20260914}"
BASE_PYTHON="${BASE_PYTHON:-/root/miniconda3/envs/lrs-v2/bin/python}"
DFINE_PYTHON="${DFINE_PYTHON:-/root/sj-tmp/venvs/dfine-l/bin/python}"
test -s "$DFINE_OUTPUT/completion.json"
test -s "$DFINE_OUTPUT/global_best.pth"
test -s "$DFINE_OUTPUT/last_evaluated.pth"
test -s "$JOINT_CHECKPOINT"
test -s "$JOINT_LAST_CHECKPOINT"
[[ ! -e "$EVAL_ROOT" ]] || { echo "Refusing existing evaluation directory: $EVAL_ROOT" >&2; exit 1; }
mkdir -p "$EVAL_ROOT"
for endpoint in final best; do
  if [[ "$endpoint" == final ]]; then
    dfine_checkpoint="$DFINE_OUTPUT/last_evaluated.pth"
    joint_checkpoint="$JOINT_LAST_CHECKPOINT"
  else
    dfine_checkpoint="$DFINE_OUTPUT/global_best.pth"
    joint_checkpoint="$JOINT_CHECKPOINT"
  fi
  for split in val test; do
    image_dir="$DATA_ROOT/images/$split"
    ann_file="$COCO_ROOT/annotations/instances_${split}.json"
    "$DFINE_PYTHON" "$PACKAGE_ROOT/export_dfine_predictions.py" \
      --dfine-root "$DFINE_ROOT" --config "$DFINE_CONFIG" --checkpoint "$dfine_checkpoint" \
      --images "$image_dir" --output "$EVAL_ROOT/dfine_${endpoint}_${split}.jsonl" \
      --device cuda:0 --score-threshold 0.001
    "$BASE_PYTHON" "$PACKAGE_ROOT/export_joint_common.py" \
      --code-root "$CODE_ROOT" --checkpoint "$joint_checkpoint" --model-yaml "$JOINT_MODEL_YAML" \
      --images "$image_dir" --output "$EVAL_ROOT/joint_${endpoint}_${split}.jsonl" \
      --device cuda:0 --score-threshold 0.001
    for model in dfine joint; do
      for cap in 100 300; do
        "$DFINE_PYTHON" "$PACKAGE_ROOT/evaluate_common.py" \
          --predictions "$EVAL_ROOT/${model}_${endpoint}_${split}.jsonl" --annotations "$ann_file" \
          --coco-output "$EVAL_ROOT/${model}_${endpoint}_${split}.coco.json" \
          --report "$EVAL_ROOT/${model}_${endpoint}_${split}.cap${cap}.json" --max-det "$cap"
      done
    done
  done
done
"$DFINE_PYTHON" "$PACKAGE_ROOT/summarize_cross_protocol.py" --eval-root "$EVAL_ROOT" --dfine-output "$DFINE_OUTPUT"

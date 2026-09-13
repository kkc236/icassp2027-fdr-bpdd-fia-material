#!/usr/bin/env bash
set -euo pipefail

PACKAGE_ROOT="${PACKAGE_ROOT:-/root/sj-tmp/eval/visdrone_dfine_l_external_20260913}"
DATA_ROOT="${DATA_ROOT:-/root/sj-tmp/datasets/VisDrone}"
COCO_ROOT="${COCO_ROOT:-/root/sj-tmp/datasets/VisDrone-coco}"
DFINE_ROOT="${DFINE_ROOT:-/root/sj-tmp/dfine-official}"
DFINE_ENV_ROOT="${DFINE_ENV_ROOT:-/root/sj-tmp/venvs/dfine-l}"
DFINE_OUTPUT="${DFINE_OUTPUT:-/root/sj-tmp/dfine-runs/dfine-l-visdrone-20260914}"
CODE_ROOT="${CODE_ROOT:-/root/sj-tmp/lrs-v2/bpdd-capacity-v2-fia-code}"
JOINT_CHECKPOINT="${JOINT_CHECKPOINT:-/root/sj-tmp/runs/formal-safe-capacity-fia-20260912-lrsv2/formal-seed0-capacity-v3-safe-fia/weights/best.pt}"
JOINT_MODEL_YAML="${JOINT_MODEL_YAML:-$CODE_ROOT/configs/rtdetr-l-lrs-gfdr-capacity-v3-safe-bpdd-fia.yaml}"
EVAL_ROOT="${EVAL_ROOT:-/root/sj-tmp/eval/visdrone_dfine_l_external_20260914}"
BASE_PYTHON="${BASE_PYTHON:-/root/miniconda3/envs/lrs-v2/bin/python}"
DFINE_PYTHON="${DFINE_PYTHON:-$DFINE_ENV_ROOT/bin/python}"

die() { echo "[dfine-cross] ERROR: $*" >&2; exit 1; }
[[ -x "$BASE_PYTHON" ]] || die "missing Ultralytics Python: $BASE_PYTHON"
[[ -x "$DFINE_PYTHON" ]] || die "missing D-FINE Python: $DFINE_PYTHON"
[[ -f "$DFINE_ROOT/train.py" ]] || die "missing D-FINE checkout: $DFINE_ROOT"
[[ -f "$DFINE_OUTPUT/best_stg2.pth" ]] || die "missing D-FINE best_stg2.pth"
[[ -f "$JOINT_CHECKPOINT" && -f "$JOINT_MODEL_YAML" ]] || die "missing read-only Ultralytics joint inputs"
[[ ! -e "$EVAL_ROOT" || -z "$(find "$EVAL_ROOT" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]] || die "evaluation directory is non-empty: $EVAL_ROOT"
mkdir -p "$EVAL_ROOT"

EVAL_CONFIG="$EVAL_ROOT/visdrone_ultralytics_eval.yml"
sed "s|__DATA_ROOT__|$DATA_ROOT|g" "$PACKAGE_ROOT/visdrone_ultralytics_eval.yml" > "$EVAL_CONFIG"

for split in val test; do
  image_dir="$DATA_ROOT/images/$split"
  ann_file="$COCO_ROOT/annotations/instances_${split}.json"
  [[ -d "$image_dir" && -f "$ann_file" ]] || die "missing $split images/annotations"
  "$DFINE_PYTHON" "$PACKAGE_ROOT/export_dfine_predictions.py" \
    --dfine-root "$DFINE_ROOT" \
    --config "$DFINE_ROOT/configs/dfine/dfine_hgnetv2_l_visdrone_control.yml" \
    --checkpoint "$DFINE_OUTPUT/best_stg2.pth" \
    --images "$image_dir" \
    --output "$EVAL_ROOT/dfine_${split}.jsonl" \
    --device cuda:0
  "$DFINE_PYTHON" "$PACKAGE_ROOT/evaluate_common.py" \
    --predictions "$EVAL_ROOT/dfine_${split}.jsonl" \
    --annotations "$ann_file" \
    --coco-output "$EVAL_ROOT/dfine_${split}.coco.json" \
    --report "$EVAL_ROOT/dfine_${split}.report.json" \
    --max-det 300

  "$BASE_PYTHON" "$CODE_ROOT/scripts/export_joint_predictions.py" \
    --checkpoint "$JOINT_CHECKPOINT" \
    --model-yaml "$JOINT_MODEL_YAML" \
    --data "$EVAL_CONFIG" \
    --split "$split" \
    --device 0 \
    --imgsz 640 \
    --conf 0.001 \
    --max-det 300 \
    --output "$EVAL_ROOT/ultralytics_joint_${split}.jsonl"
  "$DFINE_PYTHON" "$PACKAGE_ROOT/evaluate_common.py" \
    --predictions "$EVAL_ROOT/ultralytics_joint_${split}.jsonl" \
    --annotations "$ann_file" \
    --coco-output "$EVAL_ROOT/ultralytics_joint_${split}.coco.json" \
    --report "$EVAL_ROOT/ultralytics_joint_${split}.report.json" \
    --max-det 300
done

"$DFINE_PYTHON" - "$EVAL_ROOT" "$DFINE_OUTPUT" "$JOINT_CHECKPOINT" <<'PY'
import hashlib, json, pathlib, sys
root, dfine_output, joint = map(pathlib.Path, sys.argv[1:])
def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()
manifest = {
    "format_version": 1,
    "status": "complete",
    "comparison_type": "controlled_external_baseline",
    "dfine": {"framework": "D-FINE", "variant": "D-FINE-L", "checkpoint": str(dfine_output / "best_stg2.pth"), "checkpoint_sha256": sha(dfine_output / "best_stg2.pth")},
    "ultralytics_joint": {"framework": "Ultralytics", "variant": "LRS-GFDR + Capacity-BPDD-v3-Safe + FIA", "checkpoint": str(joint), "checkpoint_sha256": sha(joint), "read_only": True},
    "evaluation": {"splits": ["val", "test"], "imgsz": 640, "conf": 0.001, "max_det": 300, "tta": False, "nms": False, "evaluator": "pycocotools.COCOeval"},
    "reports": {split: {name: str(root / f"{name}_{split}.report.json") for name in ("dfine", "ultralytics_joint")} for split in ("val", "test")},
}
(root / "cross-protocol-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(manifest, ensure_ascii=False, sort_keys=True))
PY

echo "[dfine-cross] cross-protocol val/test evaluation complete: $EVAL_ROOT"

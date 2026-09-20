#!/usr/bin/env bash
set -euo pipefail
export PACKAGE_ROOT="${PACKAGE_ROOT:-/root/sj-tmp/eval/visdrone_dfine_bs4_cross_20260914}"
export DFINE_ROOT="${DFINE_ROOT:-/root/sj-tmp/dfine-bs4-official}"
export DFINE_OUTPUT="${DFINE_OUTPUT:-/root/sj-tmp/dfine-runs/dfine-l-visdrone-bs4-scratch-cross-20260914}"
export EVAL_ROOT="${EVAL_ROOT:-/root/sj-tmp/eval/visdrone_dfine_bs4_results_20260914}"
export DATA_ROOT="${DATA_ROOT:-/root/sj-tmp/datasets/VisDrone}"
export COCO_ROOT="${COCO_ROOT:-/root/sj-tmp/datasets/VisDrone-coco}"
export DFINE_PYTHON="${DFINE_PYTHON:-/root/sj-tmp/venvs/dfine-l/bin/python}"
export BASE_PYTHON="${BASE_PYTHON:-/root/miniconda3/envs/lrs-v2/bin/python}"
export CODE_ROOT="${CODE_ROOT:-/root/sj-tmp/eval/uav-detection-baselines-fb0a6a16}"
export JOINT_CHECKPOINT="${JOINT_CHECKPOINT:-/root/sj-tmp/runs/formal-safe-capacity-fia-20260912-lrsv2/formal-seed0-capacity-v3-safe-fia/weights/best.pt}"
export JOINT_LAST_CHECKPOINT="${JOINT_LAST_CHECKPOINT:-/root/sj-tmp/runs/formal-safe-capacity-fia-20260912-lrsv2/formal-seed0-capacity-v3-safe-fia/weights/last.pt}"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export OMP_NUM_THREADS=4
mkdir -p "$PACKAGE_ROOT"
exec 9>"$PACKAGE_ROOT/run.lock"
flock -n 9 || { echo 'This batch-4 job already has a supervisor.' >&2; exit 1; }
trap 'rc=$?; if [ "$rc" -ne 0 ]; then printf "failed exit=%s at=%s\n" "$rc" "$(date -Iseconds)" > "$PACKAGE_ROOT/supervisor-failed.txt"; fi' EXIT
archive=/root/sj-tmp/dfine-source/dfine-source-267a6da.tar.gz
test "$(sha256sum "$archive" | cut -d' ' -f1)" = 543edff31a28658b71bc987cfe689a3de3d920057c232a0520f04f222b35ba7b
if [[ ! -e "$DFINE_ROOT" ]]; then
  mkdir -p "$DFINE_ROOT"
  tar -xzf "$archive" -C "$DFINE_ROOT"
fi
test -f "$DFINE_ROOT/train.py"
test -s "$JOINT_CHECKPOINT"
test -s "$JOINT_LAST_CHECKPOINT"
[[ ! -e "$DFINE_OUTPUT" ]] || { echo "Refusing existing output: $DFINE_OUTPUT" >&2; exit 1; }
export DFINE_CONFIG="$DFINE_ROOT/configs/dfine/dfine_hgnetv2_l_visdrone_bs4_scratch.yml"
"$DFINE_PYTHON" - <<'PY'
import os, json, shutil, hashlib
from pathlib import Path
package, data, coco = (Path(os.environ[k]) for k in ('PACKAGE_ROOT','DATA_ROOT','COCO_ROOT'))
assert shutil.disk_usage('/root/sj-tmp').free > 6 * 1024**3, 'Need at least 6 GiB free'
text = (package / 'dfine_l_visdrone_bs4_scratch.yml').read_text()
replacements = {'__DFINE_OUTPUT_DIR__': os.environ['DFINE_OUTPUT']}
for split in ('train','val'):
    replacements[f'__{split.upper()}_IMG_FOLDER__'] = str(data / 'images' / split)
    replacements[f'__{split.upper()}_ANN_FILE__'] = str(coco / 'annotations' / f'instances_{split}.json')
for k,v in replacements.items():
    text = text.replace(k,v)
Path(os.environ['DFINE_CONFIG']).write_text(text, encoding='utf-8')
counts = {}
for split, n in [('train',6471),('val',548),('test',1610)]:
    ann_path = coco / 'annotations' / f'instances_{split}.json'
    ann = json.loads(ann_path.read_text())
    assert len(ann['images']) == n
    assert [x['id'] for x in ann['categories']] == list(range(10))
    counts[split] = {'images':n,'annotations':len(ann['annotations']), 'sha256':hashlib.sha256(ann_path.read_bytes()).hexdigest()}
(package / 'dataset-preflight.json').write_text(json.dumps(counts, indent=2))
print('Dataset counts and free disk validated', counts, flush=True)
PY
"$DFINE_PYTHON" "$PACKAGE_ROOT/train_dfine_recorded.py" --dfine-root "$DFINE_ROOT" --config "$DFINE_CONFIG" --output "$DFINE_OUTPUT" --preflight-only
timeout --signal=TERM 72h "$DFINE_PYTHON" -u "$PACKAGE_ROOT/train_dfine_recorded.py" \
  --dfine-root "$DFINE_ROOT" --config "$DFINE_CONFIG" --output "$DFINE_OUTPUT" \
  > "$PACKAGE_ROOT/training.log" 2>&1
test -s "$DFINE_OUTPUT/completion.json"
bash "$PACKAGE_ROOT/cross_protocol_bs4_pipeline.sh" > "$PACKAGE_ROOT/evaluation.log" 2>&1
printf 'complete at=%s\n' "$(date -Iseconds)" > "$PACKAGE_ROOT/supervisor-complete.txt"

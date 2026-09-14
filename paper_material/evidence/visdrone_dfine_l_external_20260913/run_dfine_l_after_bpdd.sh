#!/usr/bin/env bash
set -euo pipefail

PACKAGE_ROOT="${PACKAGE_ROOT:-/root/sj-tmp/eval/visdrone_dfine_l_external_20260913}"
BPDD_PID="${BPDD_PID:-39900}"
BPDD_SCRIPT="${BPDD_SCRIPT:-train_lrs_gfdr_capacity_v3_safe_bpdd.py}"
BPDD_RUN_DIR="${BPDD_RUN_DIR:-/root/sj-tmp/runs/formal-safe-capacity-bpdd-20260913-lrsv2/formal-seed0-capacity-v3-safe-bpdd}"
DFINE_ROOT="${DFINE_ROOT:-/root/sj-tmp/dfine-official}"
DFINE_OUTPUT="${DFINE_OUTPUT:-/root/sj-tmp/dfine-runs/dfine-l-visdrone-20260914-fp32}"
DFINE_LOG="${DFINE_LOG:-/root/sj-tmp/eval/dfine_l_train_20260914_fp32.log}"
STATUS_FILE="${STATUS_FILE:-$PACKAGE_ROOT/queued-run-status.json}"
BASE_PYTHON="${BASE_PYTHON:-/root/miniconda3/envs/lrs-v2/bin/python}"

die() { echo "[dfine-queue] ERROR: $*" >&2; write_status failed "$*"; exit 1; }
write_status() {
  local status="$1" message="${2:-}"
  mkdir -p "$(dirname "$STATUS_FILE")"
  printf '{"format_version":1,"status":"%s","message":"%s","updated_at":"%s"}\n' \
    "$status" "$message" "$(date -Iseconds)" > "$STATUS_FILE.tmp"
  mv -f "$STATUS_FILE.tmp" "$STATUS_FILE"
}

write_status waiting "waiting for BPDD PID $BPDD_PID to finish"
while kill -0 "$BPDD_PID" 2>/dev/null; do sleep 60; done
while pgrep -af "[$(printf '%s' "$BPDD_SCRIPT" | cut -c1)]$(printf '%s' "$BPDD_SCRIPT" | cut -c2-)" >/dev/null 2>&1; do sleep 30; done

write_status validating "BPDD process exited; validating 100-epoch completion"
[[ -f "$BPDD_RUN_DIR/results.csv" ]] || die "BPDD results.csv is missing"
[[ -s "$BPDD_RUN_DIR/weights/last.pt" && -s "$BPDD_RUN_DIR/weights/best.pt" ]] || die "BPDD checkpoints are missing"
"$BASE_PYTHON" - "$BPDD_RUN_DIR/results.csv" <<'PY' || die "BPDD results.csv did not reach epoch 100"
import csv, pathlib, sys
rows = list(csv.DictReader(pathlib.Path(sys.argv[1]).open(newline="")))
if not rows or int(float(rows[-1]["epoch"])) < 100:
    raise SystemExit(1)
print("BPDD completion validated", rows[-1]["epoch"])
PY

write_status preparing "deploying official D-FINE-L source, environment, and COCO annotations"
"$PACKAGE_ROOT/prepare_dfine_l_server.sh" || die "D-FINE preparation failed"
DFINE_PYTHON="${DFINE_ENV_ROOT:-/root/sj-tmp/venvs/dfine-l}/bin/python"
CONFIG="$DFINE_ROOT/configs/dfine/dfine_hgnetv2_l_visdrone_control.yml"
[[ -f "$CONFIG" ]] || die "rendered D-FINE config is missing"
[[ ! -e "$DFINE_OUTPUT" || -z "$(find "$DFINE_OUTPUT" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]] || die "D-FINE output directory is non-empty"

write_status training "starting official D-FINE-L scratch training (FP32 stability mode; AMP disabled)"
mkdir -p "$(dirname "$DFINE_LOG")"
"$DFINE_PYTHON" "$DFINE_ROOT/train.py" -c "$CONFIG" --seed 0 --device cuda:0 --output-dir "$DFINE_OUTPUT" >> "$DFINE_LOG" 2>&1 || die "D-FINE-L training failed"
[[ -s "$DFINE_OUTPUT/best_stg2.pth" ]] || die "D-FINE-L best_stg2.pth is missing"

write_status evaluating "exporting both frameworks and running common val/test COCO evaluation"
"$PACKAGE_ROOT/cross_protocol_pipeline.sh" || die "cross-protocol evaluation failed"
write_status complete "D-FINE-L training and cross-protocol evaluation completed"
echo "[dfine-queue] complete"

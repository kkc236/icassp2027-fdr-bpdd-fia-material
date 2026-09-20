#!/usr/bin/env bash
set -euo pipefail

JOINT_PID="${1:?joint trainer PID required}"
JOINT_CSV="/root/sj-tmp/runs/formal-safe-capacity-fia-20260912-lrsv2/formal-seed0-capacity-v3-safe-fia/results.csv"
PROJECT="/root/sj-tmp/lrs-v2/bpdd-capacity-v2-fia-code"
DATASET="/root/sj-tmp/datasets/VisDrone"
INITIAL_STATE="/root/sj-tmp/protocols/lrs-v2-f56b210/initial-state-seed0.pt"
OUTPUT_ROOT="/root/sj-tmp/runs/formal-safe-capacity-bpdd-20260913-lrsv2"
NAME="formal-seed0-capacity-v3-safe-bpdd"
LOG="/root/sj-tmp/logs/formal-seed0-capacity-v3-safe-bpdd-lrsv2.log"

echo "[$(date -Is)] queued behind joint PID=${JOINT_PID}" >> "$LOG"
while kill -0 "$JOINT_PID" 2>/dev/null; do
    sleep 60
done

last_epoch=0
if [[ -f "$JOINT_CSV" ]]; then
    last_epoch="$(awk -F, 'NR>1 && $1 ~ /^[0-9]+$/ {e=$1} END {print e+0}' "$JOINT_CSV")"
fi
if (( last_epoch < 100 )); then
    echo "[$(date -Is)] joint process exited before epoch 100 (last=${last_epoch}); BPDD not started" >> "$LOG"
    exit 2
fi

echo "[$(date -Is)] joint complete at epoch ${last_epoch}; starting BPDD-only" >> "$LOG"
cd "$PROJECT"
exec /root/miniconda3/envs/lrs-v2/bin/python scripts/train_lrs_gfdr_capacity_v3_safe_bpdd.py \
    --dataset-root "$DATASET" \
    --initial-state "$INITIAL_STATE" \
    --output-root "$OUTPUT_ROOT" \
    --name "$NAME" >> "$LOG" 2>&1

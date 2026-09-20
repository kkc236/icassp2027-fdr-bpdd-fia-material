#!/usr/bin/env bash
set -euo pipefail

CODE_ROOT="${CODE_ROOT:?set CODE_ROOT to the checked-out uav-detection-baselines directory}"
DATA_YAML="${DATA_YAML:?set DATA_YAML to the validated UAVDT yaml}"
BASELINE_ARGS="${BASELINE_ARGS:?set BASELINE_ARGS to the completed baseline args.yaml}"
INITIAL_STATE="${INITIAL_STATE:?set INITIAL_STATE to the UAVDT nc=3 FDR initial-state.pt}"
OUTPUT_ROOT="${OUTPUT_ROOT:?set OUTPUT_ROOT to a new output directory}"

cd "$CODE_ROOT"
python scripts/train_uavdt_capacity_v3_safe_fia.py \
  --data-yaml "$DATA_YAML" \
  --baseline-args "$BASELINE_ARGS" \
  --initial-state "$INITIAL_STATE" \
  --output-root "$OUTPUT_ROOT" \
  --dry-run

echo "Review $OUTPUT_ROOT/authority/*.json, then rerun this command without --dry-run."

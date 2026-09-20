#!/usr/bin/env bash
set -euo pipefail

PACKAGE_ROOT="${PACKAGE_ROOT:-/root/sj-tmp/eval/visdrone_dfine_l_external_20260913}"
DATA_ROOT="${DATA_ROOT:-/root/sj-tmp/datasets/VisDrone}"
COCO_ROOT="${COCO_ROOT:-/root/sj-tmp/datasets/VisDrone-coco}"
DFINE_ROOT="${DFINE_ROOT:-/root/sj-tmp/dfine-official}"
SOURCE_TARBALL="${SOURCE_TARBALL:-/root/sj-tmp/dfine-source/dfine-source-267a6da.tar.gz}"
DFINE_ENV_ROOT="${DFINE_ENV_ROOT:-/root/sj-tmp/venvs/dfine-l}"
DFINE_OUTPUT="${DFINE_OUTPUT:-/root/sj-tmp/dfine-runs/dfine-l-visdrone-20260914-fp32-bs4}"
BASE_PYTHON="${BASE_PYTHON:-/root/miniconda3/envs/lrs-v2/bin/python}"
SOURCE_COMMIT="${SOURCE_COMMIT:-267a6da6d04c8ad52e54120692896515b9e55981}"
EXPECTED_SOURCE_SHA256="${EXPECTED_SOURCE_SHA256:-543EDFF31A28658B71BC987CFE689A3DE3D920057C232A0520F04F222B35BA7B}"

die() { echo "[dfine-prepare] ERROR: $*" >&2; exit 1; }
log() { echo "[dfine-prepare] $*"; }

[[ -x "$BASE_PYTHON" ]] || die "missing base Python: $BASE_PYTHON"
[[ -f "$SOURCE_TARBALL" ]] || die "missing source archive: $SOURCE_TARBALL"
[[ -d "$DATA_ROOT/images" && -d "$DATA_ROOT/labels" ]] || die "invalid VisDrone root: $DATA_ROOT"

actual_sha256="$(sha256sum "$SOURCE_TARBALL" | awk '{print toupper($1)}')"
[[ "$actual_sha256" == "$EXPECTED_SOURCE_SHA256" ]] || die "source archive SHA-256 mismatch: $actual_sha256"

if [[ ! -f "$DFINE_ROOT/train.py" ]]; then
  [[ ! -e "$DFINE_ROOT" || -z "$(find "$DFINE_ROOT" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]] || die "D-FINE root exists but is not a recognized checkout: $DFINE_ROOT"
  mkdir -p "$DFINE_ROOT"
  tar -xzf "$SOURCE_TARBALL" -C "$DFINE_ROOT"
fi
[[ -f "$DFINE_ROOT/train.py" && -f "$DFINE_ROOT/configs/dfine/dfine_hgnetv2_l_coco.yml" ]] || die "D-FINE checkout is incomplete: $DFINE_ROOT"

if [[ ! -x "$DFINE_ENV_ROOT/bin/python" ]]; then
  mkdir -p "$(dirname "$DFINE_ENV_ROOT")"
  "$BASE_PYTHON" -m venv --system-site-packages "$DFINE_ENV_ROOT"
fi
DFINE_PYTHON="$DFINE_ENV_ROOT/bin/python"
"$DFINE_PYTHON" - <<'PY'
import torch
assert torch.__version__, "torch is unavailable"
assert torch.cuda.is_available(), "CUDA is unavailable"
print("torch", torch.__version__, "cuda", torch.cuda.get_device_name(0))
PY

if ! "$DFINE_PYTHON" -c 'import faster_coco_eval' >/dev/null 2>&1; then
  "$DFINE_PYTHON" -m pip install --disable-pip-version-check --no-input -i https://pypi.tuna.tsinghua.edu.cn/simple faster-coco-eval
fi
for package in tensorboard calflops transformers loguru pycocotools; do
  if ! "$DFINE_PYTHON" -c "import ${package//-/_}" >/dev/null 2>&1; then
    "$DFINE_PYTHON" -m pip install --disable-pip-version-check --no-input -i https://pypi.tuna.tsinghua.edu.cn/simple "$package"
  fi
done

mkdir -p "$COCO_ROOT/annotations"
"$DFINE_PYTHON" "$PACKAGE_ROOT/convert_visdrone_yolo_to_coco.py" --dataset-root "$DATA_ROOT" --output-dir "$COCO_ROOT/annotations"

"$DFINE_PYTHON" - "$COCO_ROOT/annotations" <<'PY'
import json, pathlib, sys
root = pathlib.Path(sys.argv[1])
expected = {"val": (548, 38759), "test": (1610, 75102)}
for split, expected_counts in expected.items():
    path = root / f"instances_{split}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    actual = (len(payload["images"]), len(payload["annotations"]))
    if actual != expected_counts:
        raise SystemExit(f"{split} count mismatch: expected={expected_counts} actual={actual}")
    if [c["id"] for c in payload["categories"]] != list(range(10)):
        raise SystemExit(f"{split} category IDs are not zero-based 0..9")
print("VisDrone COCO counts validated")
PY

RENDERED_CONFIG="$DFINE_ROOT/configs/dfine/dfine_hgnetv2_l_visdrone_control.yml"
"$DFINE_PYTHON" - "$PACKAGE_ROOT/dfine_l_visdrone_control.yml" "$RENDERED_CONFIG" "$DFINE_OUTPUT" "$DATA_ROOT" "$COCO_ROOT" <<'PY'
from pathlib import Path
import sys
template, output, run_dir, data_root, coco_root = map(Path, sys.argv[1:])
replacements = {
    "__DFINE_OUTPUT_DIR__": str(run_dir),
    "__TRAIN_IMG_FOLDER__": str(data_root / "images" / "train"),
    "__TRAIN_ANN_FILE__": str(coco_root / "annotations" / "instances_train.json"),
    "__VAL_IMG_FOLDER__": str(data_root / "images" / "val"),
    "__VAL_ANN_FILE__": str(coco_root / "annotations" / "instances_val.json"),
}
text = template.read_text(encoding="utf-8")
for token, value in replacements.items():
    text = text.replace(token, value)
if any(token in text for token in replacements):
    raise SystemExit("unresolved config placeholder")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(text, encoding="utf-8", newline="\n")
PY

if [[ -e "$DFINE_OUTPUT" && -n "$(find "$DFINE_OUTPUT" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]]; then
  die "D-FINE output directory is non-empty; refusing to overwrite: $DFINE_OUTPUT"
fi
mkdir -p "$DFINE_OUTPUT"
"$DFINE_PYTHON" - "$PACKAGE_ROOT" "$DFINE_ROOT" "$RENDERED_CONFIG" "$SOURCE_TARBALL" "$COCO_ROOT" "$DFINE_ENV_ROOT" "$SOURCE_COMMIT" <<'PY'
import hashlib, json, pathlib, sys
package, source, config, archive, coco, env, commit = map(pathlib.Path, sys.argv[1:])
def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()
manifest = {
    "format_version": 1,
    "status": "prepared",
    "framework": "D-FINE",
    "variant": "D-FINE-L",
    "source_commit": commit.name,
    "source_archive_sha256": sha(archive),
    "source_root": str(source),
    "config": str(config),
    "config_sha256": sha(config),
    "coco_annotations": {name: {"path": str(path), "sha256": sha(path)} for name, path in (
        ("train", coco / "annotations" / "instances_train.json"),
        ("val", coco / "annotations" / "instances_val.json"),
        ("test", coco / "annotations" / "instances_test.json"),
    )},
    "python": str(env / "bin" / "python"),
    "training": {"epochs": 100, "seed": 0, "imgsz": [640, 640], "total_batch_size": 4, "pretrained": False, "use_amp": False, "stability_note": "FP32 required after FP16 DN-decoder overflow; batch 4 avoids a high-target batch FP32 OOM on the 24GB GPU"},
}
(package / "server-preflight.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(manifest, ensure_ascii=False, sort_keys=True))
PY
log "D-FINE-L environment, source, COCO annotations, and rendered config are ready"

# VisDrone D-FINE-L external evaluation package

This package is an external comparison adapter. The existing Ultralytics
LRS-GFDR + Capacity-BPDD + FIA checkpoint remains read-only and is exported by
`tmp-work/bpdd-capacity-v2-fia/scripts/export_joint_predictions.py`.

The D-FINE side runs in the official D-FINE checkout and environment. It is not
registered as an Ultralytics module. `export_dfine_predictions.py` consumes the
official postprocessor output (`labels`, pixel `xyxy` boxes, sigmoid scores) and
writes one JSONL row per image. Both exporters use zero-based VisDrone class IDs
0..9 and the same 640/300/no-TTA/no-NMS evaluation contract.

The exporter does not train either model. D-FINE-L training is a separate,
explicitly authorized step; until its checkpoint exists, its status is
`not_started`, not a fabricated result.

Example on the server after copying the package and checking paths:

First copy `dfine_l_visdrone_control.yml` into the official checkout's
`configs/dfine/` directory beside `dfine_hgnetv2_l_coco.yml`; its relative
include is intentionally resolved by the D-FINE loader, not by this materials
repository.

```bash
python export_dfine_predictions.py \
  --dfine-root /root/sj-tmp/dfine-official \
  --config /root/sj-tmp/dfine-official/configs/dfine/dfine_hgnetv2_l_coco.yml \
  --checkpoint /root/sj-tmp/dfine-runs/dfine-l-visdrone/best_stg2.pth \
  --images /root/sj-tmp/datasets/VisDrone/images/val \
  --output /root/sj-tmp/eval/visdrone_dfine_l_external_20260913/dfine_val.jsonl
```

Before execution, verify the official D-FINE commit, the 10-class config,
the VisDrone image list, and checkpoint hash. Do not upload raw data or model
weights to the materials repository.

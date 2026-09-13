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

## 自动排队训练（服务器）

本包现在包含三个服务器脚本：

- `prepare_dfine_l_server.sh`：部署固定官方源码包、独立 venv、YOLO→COCO 标注和渲染后的 10 类配置；使用清华 PyPI 镜像补齐依赖。
- `run_dfine_l_after_bpdd.sh`：等待当前 Capacity-BPDD 进程退出，确认 `results.csv` 达到 E100 后才启动 D-FINE-L。
- `cross_protocol_pipeline.sh`：训练完成后导出 D-FINE-L 与只读 Ultralytics 联合 checkpoint，并用同一 COCO evaluator 评测 val/test。

部署包不会包含数据、权重或凭据。服务器上先将固定源码归档复制到
`/root/sj-tmp/dfine-source/dfine-source-267a6da.tar.gz`，再运行：

```bash
chmod +x /root/sj-tmp/eval/visdrone_dfine_l_external_20260913/*.sh
nohup bash /root/sj-tmp/eval/visdrone_dfine_l_external_20260913/run_dfine_l_after_bpdd.sh \
  > /root/sj-tmp/eval/dfine_l_after_bpdd_20260914.log 2>&1 &
echo $! > /root/sj-tmp/eval/dfine_l_after_bpdd_20260914.pid
```

状态文件为 `queued-run-status.json`，状态依次为
`waiting → validating → preparing → training → evaluating → complete`；任何
失败都会记录 `failed` 和原因。重复启动时如果 D-FINE 输出目录非空，脚本会拒绝覆盖。

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

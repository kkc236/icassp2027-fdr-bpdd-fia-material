# VisDrone D-FINE-L external evaluation package

## 2026-09-15：统一评估已完成

训练后的自动评估已于北京时间 08:12 完成。完整结果与复评步骤见
[COMMON_EVALUATION_RESULTS_20260915_ZH.md](COMMON_EVALUATION_RESULTS_20260915_ZH.md)，
原始对比表及 16 份分项报告见 [common_evaluation_20260915/](common_evaluation_20260915/)。
AP50-95@300：末轮对末轮 test 为联合模型 24.1335%、D-FINE 22.5544%；
best 对 best test 为 24.2285%、22.6785%。训练原生验证指标与本表分别保留。

## 2026-09-14 batch=4 跨协议方案

当前新方案见 [CROSS_PROTOCOL_BS4_ZH.md](CROSS_PROTOCOL_BS4_ZH.md)。入口为
`run_bs4_cross.sh`，配置为 `dfine_l_visdrone_bs4_scratch.yml`，自动评测为
`cross_protocol_bs4_pipeline.sh`。这是从头训练适配后的官方 D-FINE-L，
与现有联合模型作统一评测；公开 batch、有效batch、优化器、精度和增强差异。
此前的控制配置和排队脚本保留作历史记录，不是本次新运行入口。
旧导出器/公共评测器已修复非正方形坐标、COCO图像ID映射及AP@300摘要问题；
新方案使用 `export_joint_common.py` 和D-FINE相同的PIL直接拉伸预处理。

This package is an external comparison adapter. The existing Ultralytics
LRS-GFDR + Capacity-BPDD + FIA checkpoint remains read-only and is exported by
`tmp-work/bpdd-capacity-v2-fia/scripts/export_joint_predictions.py`.

The D-FINE side runs in the official D-FINE checkout and environment. It is not
registered as an Ultralytics module. `export_dfine_predictions.py` consumes the
official postprocessor output (`labels`, pixel `xyxy` boxes, sigmoid scores) and
writes one JSONL row per image. Both exporters use zero-based VisDrone class IDs
0..9 and the same 640/300/no-TTA/no-NMS evaluation contract.

The exporter does not train either model. D-FINE-L training is a separate,
explicitly authorized step. The first 2026-09-14 attempt reached epoch 2 and
failed in the official `generalized_box_iou` assertion. Raw COCO validation
showed all boxes finite, positive, and in bounds; a diagnostic replay traced
the invalid geometry to FP16 autocast overflow in a denoising decoder output
under the from-scratch VisDrone run. No checkpoint or metric from that failed
attempt is registered; its status snapshot is `queued-run-status-20260914.json`
and its log remains `/root/sj-tmp/eval/dfine_l_train_20260914.log`.

The repair keeps the official model/loss/data code unchanged and disables
AMP (`use_amp: False`) for this external baseline. A same-checkpoint replay
completed the entire failing epoch (808/808 batches, no invalid-box or
non-finite-parameter event). The formal run additionally uses total batch 4
because a high-target batch can exceed a 24-GB GPU in FP32; this changes only
the memory-safe minibatch size, not the model or evaluation contract. The
formal run uses a new output directory and a fresh provenance record. This is
a numerical-stability correction, not an accuracy intervention.

## 自动排队训练（服务器）

本包现在包含三个服务器脚本：

- `prepare_dfine_l_server.sh`：部署固定官方源码包、独立 venv、YOLO→COCO 标注和渲染后的 10 类配置；使用清华 PyPI 镜像补齐依赖。
- `run_dfine_l_after_bpdd.sh`：等待当前 Capacity-BPDD 进程退出，确认 `results.csv` 达到 E100 后才启动 D-FINE-L（FP32 稳定模式，禁用 AMP，batch=4）。
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
`waiting → validating → preparing → training → evaluating → complete`。历史
失败记录保留在 `queued-run-status-20260914.json` 与 `authority.json`；修复
运行使用新的、明确命名的输出目录，脚本仍会拒绝覆盖非空目录。

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
the VisDrone image list, and checkpoint hash. Do not upload raw data or
credentials. The final cross-protocol package publishes only two evaluation
checkpoints in a dedicated GitHub Release (the validation global-best and the
epoch-100 EMA snapshot); their SHA-256 values and roles are fixed in
`DFINE_L_ASSET_MANIFEST_20260915.json`. The full optimizer-resume `last.pth`
remains omitted because it is not needed for scoring. See
[DFINE_L_FINAL_RESULTS_20260915_ZH.md](DFINE_L_FINAL_RESULTS_20260915_ZH.md)
and the lightweight server evidence under `server_final_20260915/`.

## 2026-09-15 final server evidence

The formal batch=4 run completed 100/100 epochs. The global-best was epoch 93
(AP50-95 28.7726%, AP50 47.1488%); the epoch-100 final snapshot was AP50-95
28.4742%, AP50 46.6781%. These are D-FINE-native validation values and are
reported as an external common-evaluation reference, not a same-protocol
leaderboard result. The release is
`dfine-l-visdrone-bs4-cross-20260914`; the branch copy contains the summary,
manifest, and complete JSONL evidence needed to reproduce the comparison.

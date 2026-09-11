# Capacity-v2 远端最终状态与磁盘清理记录

观测时间：2026-09-11 10:37（Asia/Shanghai）

## 训练状态

- 远端训练任务：`lrs-gfdr-capacity-v2-bpdd`
- 结果目录：`/root/sj-tmp/results/lrs-gfdr-capacity-v2/formal-seed0-lrs_gfdr_capacity_v2_bpdd`
- `results.csv`：100 行，训练已完成；未发现训练进程或 OOM。
- mAP50-95：best `0.29848`（epoch 87），last `0.29511`（epoch 100）
- mAP50：best `0.49648`（epoch 88），last `0.49328`
- Precision：best `0.60928`（epoch 94），last `0.60051`
- Recall：best `0.49844`（epoch 76），last `0.49153`
- `best.pt`、`last.pt` 均存在，约 68 MB/个。

## 磁盘

- 系统盘 `/`：清理前 `6.8/30 GB（23%）`，清理后 `6.1/30 GB（21%）`。
- 数据盘 `/root/sj-tmp`：约 `48/50 GB（95%）`。
- 主要占用：`runs/visdrone-v2-clean-fdr-geometry-20260908` 约 19G，当前 capacity-v2 `results` 约 20G。

## 已执行清理

- 仅清理可重新下载的 `/root/.cache/pip`（110 个文件，约 4.74 GB）。
- 未删除代码、数据集、初始权重、实验结果或任何 epoch checkpoint。

# Baseline best 冻结权重 800 评估（2026-09-15）

已完成 800 test、640 test 控制和两组 val 核对。没有重训，没有改变模型或权重。

## 同口径 test 对比

固定同一 data YAML、原生 RTDETRValidator、batch=8、conf=0.001、max_det=300、无 NMS、非矩形输入；每项 1610 张、75102 个实例。以下均为百分数。

| 模型 | 尺寸 | mAP50-95 | mAP50 | mAP75 | P | R |
|---|---:|---:|---:|---:|---:|---:|
| Baseline best-epoch EMA | 640 | 17.7426 | 32.2539 | 17.5650 | 41.9759 | 37.2449 |
| LRS-GFDR | 640 | 23.6188 | 41.1008 | 23.6445 | 52.6088 | 43.7767 |
| LRS-GFDR + Capacity-BPDD + FIA | 640 | 23.6040 | 41.2409 | 23.5464 | 53.8393 | 43.6336 |
| Baseline best-epoch EMA | 800 | 12.8241 | 27.8854 | 10.3708 | 37.8889 | 33.9059 |
| LRS-GFDR | 800 | 24.0595 | 42.3871 | 24.1524 | 53.9144 | 44.7050 |
| LRS-GFDR + Capacity-BPDD + FIA | 800 | 24.1598 | 42.4634 | 24.2186 | 54.5902 | 44.1799 |

## 验证集核对

| 模型 | 640 val mAP50-95 | 800 val mAP50-95 | 变化（pp） |
|---|---:|---:|---:|
| Baseline best-epoch EMA | 21.9174 | 15.5931 | -6.3244 |
| LRS-GFDR | 29.6164 | 30.0471 | +0.4307 |
| LRS-GFDR + Capacity-BPDD + FIA | 30.1024 | 30.2874 | +0.1850 |

## 结论与边界

- Baseline 的 test 800−640 为 **-4.9185 pp**，并未随尺寸提高而获益。
- 同为 800 时，Full−baseline 为 **+11.3357 pp**；同为 640 时为 **+5.8615 pp**。扩大后的差距不能全部解释成模块新增贡献。
- 800 原先按 G/Full 的 val 选择；baseline 未参与选择。因此保留 640 作为既定主消融口径，800 先列为同尺度敏感性结果，不根据本次 test 分数反向选择主结论。
- 此表保证当前复评口径一致，但不会消除既有训练源码、训练 authority 等潜在差别。
- baseline 下跌原因尚未定位；核对了正确权重、输入尺寸、图数、类别和参数，不能仅凭下降幅度宣称模型缺陷或推理实现错误。

## Best 身份说明（纠正先前文件名误判）

采用 strict-control `fdr-formal-d97e1eb7-seed0-control` 的 epoch-100 归档 EMA。checkpoint 内含完整 1–100 轮验证曲线，唯一最高 mAP50-95 为第 100 轮 0.21916，且当前 fitness 等于 best_fitness。这一训练的 final epoch 同时也是 best epoch；不能因为归档文件名写 epoch-100 而排除其 best 身份。

归档 SHA256：`9C242711F44B7E68B360AF904AB7C44F64505C7136B7E7F90481092AE3308AF7`。本次还验证 RTDETR 实际加载的是该 checkpoint 的 EMA。未声称此文件与缺失的 optimizer-stripped `best.pt` 字节相同。

640 test 本次为 17.7426%，历史 exact-final-EMA 为 17.7416%，差异约 0.0009 pp；归档权重与历史评估指标相符，但未强称逐位相同。

## 证据

- `files/test/imgsz800/summary.json`：本次核心结果。
- `files/*/imgsz*/BEST_EPOCH_IDENTITY.json`：完整100轮曲线、训练参数及 best 身份。
- `files/evaluate.py`、`files/runner.py`、`files/runner.log`：服务器实际执行代码和日志。
- `comparisons/`：G/Full 已有同口径原始摘要（未重新训练或另选 checkpoint）。
- `MANIFEST.json`：传输数据与原文件逐一 SHA256 核验。
- `RESULTS.json`：完整指标和精确差值。

Material Passport：用户已授权冻结评估；本轮新增4次 baseline 评估；无训练、无模型修改；记录了权重身份、协议、形状、FP32及环境；结论范围为本项目转换标注口径。

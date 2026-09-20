# 冻结权重的高分辨率推理核验（2026-09-15）

## 可回答的问题

在**不重训、不改模块、不改 checkpoint、不改数据、不改评估器**的前提下，仅将
VisDrone 推理尺寸从 `640` 调整为更高尺寸，是否能改善项目内的 test 指标？

结论是：可以选择 `imgsz=800`，且在同一验证器的受控对照下，两个固定 checkpoint
的 overall mAP50-95 都上升；`960` 则显著变差。这个结果属于**推理尺度设置的敏感性
结果**，不是 FDR、BPDD 或 FIA 新增的训练增益。

## 预先锁定的选择规则

在读取任何 `test` 结果前，对固定的 G（LRS-GFDR）和 Full
（LRS-GFDR + Capacity-BPDD + FIA）checkpoint 在 VisDrone `val`（548 张）执行：

- 候选：`800`、`960`；
- 规则：选择两臂 val mAP50-95 的非加权均值更高者；
- 固定其余条件：`batch=8`、`workers=8`、请求 `half=False`、`conf=0.001`、`max_det=300`、
  `nms=False`、`rect=False`、`cache=False`；
- 决策：800 的均值为 **30.1673%**，960 为 **27.5473%**，所以在 test 前锁定
  `imgsz=800`。

随后补跑 640 的同验证器控制项；该控制项不参与 800 的选择，专用于排除“历史 640
记录使用了不同评估封装”的疑点。

## 同验证器的总体结果

| Arm | split | 640 mAP50-95 | 800 mAP50-95 | 变化（pp） | 640 → 800 mAP50 | 640 → 800 mAP75 |
|---|---:|---:|---:|---:|---:|---:|
| G：LRS-GFDR | val（548） | 29.6164 | 30.0471 | **+0.4307** | 49.3834 → 50.8456 | 29.9128 → 30.5315 |
| Full：LRS-GFDR + Capacity-BPDD + FIA | val（548） | 30.1024 | 30.2874 | **+0.1850** | 49.8670 → 50.9273 | 30.7237 → 31.1151 |
| G：LRS-GFDR | test（1610） | 23.6188 | 24.0595 | **+0.4407** | 41.1008 → 42.3871 | 23.6445 → 24.1524 |
| Full：LRS-GFDR + Capacity-BPDD + FIA | test（1610） | 23.6040 | 24.1598 | **+0.5558** | 41.2409 → 42.4634 | 23.5464 → 24.2186 |

在 test 的同尺度比较中，Full 相对 G：

- `640`：23.6040 − 23.6188 = **−0.0148 pp**；
- `800`：24.1598 − 24.0595 = **+0.1003 pp**。

两组 640 控制值与此前原生 640 记录（G: 29.6164 / 23.6188，Full: 30.1024 / 23.6040）
逐位一致到所显示精度，确认这里没有改变模型、数据或常规评估路径。

## Baseline-best 补测与身份纠正

项目中确有一个 literal stock `baseline best.pt`：
`/data/uav/runs/fdr-formal-control-d97e1eb7/formal-seed0-control-fdr-v1/weights/best.pt`
（SHA-256 `32f5c09fc2180d39e97a7ab6ea8c86a64c62f4fa7e22dc297181564b04d7ddc0`）。
当前未找到这一 optimizer-stripped 文件，但同一训练的 epoch-100 归档 EMA 可用
（SHA-256 `9C242711F44B7E68B360AF904AB7C44F64505C7136B7E7F90481092AE3308AF7`）。
读取其完整 1–100 轮曲线后确认：**第100轮是唯一验证最佳轮，且当前 fitness 等于
best_fitness（0.21916）**。因此，该训练的 final epoch 同时也是 best epoch。
此前仅凭文件名区分 final 与 best、进而排除该归档权重 best 身份的结论不成立，现予纠正。
这并不声称两个不同序列化文件具有相同字节哈希。

用户随后授权 baseline best 800 冻结评估。采用上述 best-epoch EMA，使用与 G/Full
相同的当前 data YAML 和原生验证器，补测 test 800/640 与 val 800/640。
完整结果、身份依据、传输指纹及执行脚本见
[Baseline best 800 补测报告](../baseline_best_800_20260915/BASELINE_BEST_800_ZH.md)。

Baseline test mAP50-95 从本次640的 **17.7426%** 降至800的 **12.8241%**。
同为800时，Full−baseline 为 **+11.3357 pp**；同为640时为 **+5.8615 pp**。
差距扩大主要伴随 baseline 的尺度退化，不能全部解释为模块新增贡献。
当前复评口径一致，也不自动消除既有训练源码/authority 的差别；仍不应仅据此声称
single-variable strict pair。

## 必须保留的限制

1. `800` 是单独报告的冻结高分辨率推理协议，不是模块新增的训练提升。鉴于 baseline
   在800明显下降，建议保留既定640主要消融表，把800作为同尺度敏感性结果；不得根据
   test 上更大的模型差距反向选择主要口径。
2. 当前项目 test 为有 1610 张图、75102 个实例的项目内 test-dev 转换标注口径；其与
   官方挑战赛完整评测并不等价，仍须沿用仓库既有的口径说明。
3. 这不是针对 `truck` 的修复。Full 的 test truck mAP50-95 从 29.1936% 降至
   28.4497%（−0.7439 pp）；G 也从 30.3878% 降至 28.9319%（−1.4560 pp）。overall
   增长来自其他类别的汇总贡献，不能宣称解决了 UAVDT/VisDrone 的 truck 难题。
4. 800 比 640 更慢、计算量更高；该次验证未把速度/GFLOPs 重测为正式部署指标，论文
   中如采用 800，需单独测量并报告延迟与算力。

## 可使用的表述

> We additionally report a frozen-checkpoint inference-scale sensitivity check. The input scale was selected on validation only, before evaluating the test split. With all weights and evaluation settings fixed, 800-pixel inference consistently improved the overall VisDrone mAP50-95 over the 640-pixel control. We report this as an inference configuration result rather than a training-time module gain.

## 远端原始证据与完整性指纹

每项均使用相同 data YAML SHA-256：
`3CCAF145213879DF0544CBB924A9F5EF8C2D9EB01D964FC18883E18D1197FE63`。

说明：Ultralytics 会在验证后将显式 `half=False` 从持久化的 `protocol` 字典中规范化移除；
调度源码中对全部八次运行均显式传入该开关，其他协议字段则完整保留在每份摘要内。

| 记录 | 远端 `summary.json` SHA-256 |
|---|---|
| G 640 val | `5269792DAE14D63987356A3AC05320CECD09461546374681B762024B4D7B0161` |
| G 800 val | `7C8ED4F7B1D01C4D88B7B2618EE2E5F756A7D10D636A07BE2322CA7271F33B60` |
| Full 640 val | `FB7AEB6ABEA734CB4539D8A18D810F85185AF2E8D6D2D14AEF37EEFA7CA7675D` |
| Full 800 val | `8680BF24FDA742359797425E339B322A1D19D825C66BE6897947E5A9C7CB836D` |
| G 640 test | `570EF7D824BF6A00B6EB24355F841E030013AEA32E752D4BE97E83C611623950` |
| G 800 test | `AC0CA70ED33D12E18F2434F3D7C3306E2A7047522B5CAF5BEF2863FBD1059E11` |
| Full 640 test | `CD629CCA1D7134FF5A3331725B42C199764CA55402AF567E979395CE20A901B5` |
| Full 800 test | `E233166C81C2A83E060AE7E9AD1A9287193B289F26EFA5AEFC91F8AD98619CDC` |
| val 选择决策 | `EEA59B18B3F339FE3AB4352B64CEED29D78A348459DBF53B251E5F532EFF77CFD` |

远端目录：

- `/root/sj-tmp/evidence/visdrone_highres_val_probe_v2_20260915`
- `/root/sj-tmp/evidence/visdrone_highres_test_probe_20260915`
- `/root/sj-tmp/evidence/visdrone_frozen_640_control_20260915`

归档 stock-control **final-EMA（已证实也是该训练 best epoch 的 EMA）** 的历史 test 原始证据：
`evidence/strict-control-test-d97e1eb7/strict-control-test-eval.json`（checkpoint
SHA-256 `9C242711F44B7E68B360AF904AB7C44F64505C7136B7E7F90481092AE3308AF7`）。

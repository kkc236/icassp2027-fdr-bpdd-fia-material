# FIA-only 与 FDR+FIA 消融实验脚手架

## 来源与定位

源码仓库 `uav-detection-baselines` 的 `fdr-bdpp-fia` 分支在提交 `1d0831402e15f6d039510b79eb477b5c34abb42c` 补齐两种缺失消融的配置、训练入口和 test 评估入口。本私密仓库引入该提交，并对两份 YAML 做一次有登记的拓扑规范化。

GitHub Release `DFR-BDPP-FIA` 后续上传了 FIA-only 与 FDR+FIA 的 100 epoch 训练包、日志、checkpoint 和 test 截图，因此这两项已不再是“没有结果”。但 Release target commit 为 `7b20c610`，早于上述配置提交；运行名虽然与后来配置一致，精确 training source commit 仍无法验证。该批结果应登记为历史 Release 证据，而不是当前规范化拓扑的正式消融结果。

## 文件矩阵

| 消融 | 模型配置 | 训练入口 | 评估入口 | 定位解码器 |
|---|---|---|---|---|
| FIA-only | `configs/rtdetr-l-fia.yaml` | `train_fia.py` | `val_fia.py` | stock `RTDETRDecoder` |
| FDR+FIA | `configs/rtdetr-l-fdr-fia.yaml` | `train_fdr_fia.py` | `val_fdr_fia.py` | `FDRRTDETRDecoder` |

两种配置都把 `FIA(256)` 插在 P3 head 路径的第二个 `RepC3` 后。源提交继续用 `-1` 从 FIA 输出重建 P4/P5，这与已验证三模块配置的 P3-only 连接不一致。私密仓库已将两份配置的 P4/P5 重建分支改为显式读取原始 P3（层 21、23/25/26 索引链），decoder 仍读取 FIA 输出层 22；因此 FIA 的拓扑与三模块配置一致，避免消融比较同时改变 P4/P5。

已上传 Release checkpoint 对应的是规范化前的历史 topology：FIA 输出不仅送入 decoder P3，还参与 P4/P5 重建。它与本仓库 P3-only YAML 不是同一计算图，不能改名后作为规范化配置的 checkpoint 使用。

FIA-only 使用 `FDRControlTrainer` 保留 stock decoder；FDR+FIA 使用 `FDRTrainer` 和 FDR loss。两者均不启用 BPDD，从而可分别隔离 FIA 主效应以及 FIA 与 FDR 的交互。源 blob 与规范化后本地 blob 的 OID/SHA-256 均登记在 `source_manifest.json`。

## 提交内默认训练参数

| 参数 | FIA-only | FDR+FIA |
|---|---:|---:|
| epochs | 100 | 100 |
| imgsz | 640 | 640 |
| batch | 8 | 8 |
| workers | 4 | 4 |
| pretrained | False | False |
| optimizer | MuSGD | MuSGD |
| seed / deterministic | 0 / True | 0 / True |
| 默认 device | 0 | 1 |

`configs/VisDrone.yaml` 的根路径已由服务器绝对路径改为仓库相对路径 `VisDrone`。运行环境必须在仓库根下提供该目录或等价映射。

## 与论文冻结协议的差异

两个 `val_*.py` 默认执行 `split="test"`、`imgsz=640`、`batch=4`，但没有显式冻结 `workers=8`、`conf=0.001`、`max_det=300`、`nms=False`、`cache=False`、`half=False` 和 `rect=False`。因此脚本可用于入口验证，不能直接把默认输出与当前 val/test exact 表作严格差值。

正式补实验必须：

1. 两臂使用同一 source commit、initial state、seed、数据顺序、增强随机序列和训练设备合同；
2. val 与 test 分开运行，并显式对齐 `PROTOCOL_ZH.md` 的评估参数；
3. 保存 checkpoint SHA-256、命令、数据集 SHA-256、精确总体/尺度/类别 JSON；
4. FIA-only 只与 stock baseline 配对，FDR+FIA 只与同 authority FDR 配对；不得用三模块行反推 FIA 增益。

## 当前状态

- FIA-only：Release 证据已登记；val 为训练日志 best epoch 的 exact 记录（epoch 88，mAP50–95 `0.21671`），test 为截图舍入值（mAP50–95 `≈0.177`），AP75 缺失；状态为非严格可比。
- FDR+FIA：Release 证据已登记；val 为训练日志 best epoch 的 exact 记录（epoch 97，mAP50–95 `0.29408`），test 为截图舍入值（mAP50–95 `≈0.235`），AP75 缺失；状态为非严格可比。
- 三模块：已有 exact val 单臂结果；exact test 仍待补评。

Release 证据的完整 SHA-256、训练参数与指标边界见 [`../results/FIA_ABLATION_RELEASE_RESULTS_ZH.md`](../results/FIA_ABLATION_RELEASE_RESULTS_ZH.md)。由于历史 topology、未验证的 training source commit 和非冻结 evaluator 合同，主表继续保留四条已有结果，不把 FIA-only 或 FDR+FIA 的 Release 数值并入正式主表；若要证明当前 P3-only FIA，仍需使用规范化 YAML 重新训练并统一复评。

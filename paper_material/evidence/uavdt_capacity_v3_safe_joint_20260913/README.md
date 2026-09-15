# UAVDT：当前 Capacity-BPDD-v3-Safe + FIA 联合模块交接包

## 这是什么

本目录对应当前版本的：

```text
LRS-GFDR + Capacity-BPDD-v3-Safe + FIA
```

UAVDT baseline 已由其他运行完成，本包只准备新的联合臂，不覆盖或替代已有
baseline 结果。

## 不要使用的历史入口

材料仓库根目录的 `train.py` 是旧版 VisDrone 三模块脚本，使用旧的
`FDRBPDDFIATrainer`。`scripts/train_uavdt_full.py` 是旧版 UAVDT
`LRS-FDR+AC-BPDD+FIA` 入口。它们都不是当前 Capacity-BPDD-v3-Safe 联合训练入口。

## 当前代码

代码仓库：

<https://github.com/kkc236/uav-detection-baselines/tree/codex/uavdt-capacity-v3-safe-joint-20260913>

固定 commit：`b9f492320d7be35b846c504de84ea3a85077df76`

当前配置：

`configs/rtdetr-l-lrs-gfdr-capacity-v3-safe-bpdd-fia-uavdt.yaml`

当前入口：

`scripts/train_uavdt_capacity_v3_safe_fia.py`

## 必须由服务器提供的文件

1. UAVDT YOLO 数据集：`images/train`、`images/val`、`labels/train`、`labels/val`；
2. `uavdt.yaml`，类别顺序必须为 `car`、`truck`、`bus`；
3. 已完成 baseline 的 `args.yaml`；
4. 与 UAVDT 三类模型兼容的 FDR `initial-state.pt`。

baseline 的 `best.pt` 只用于最后比较，不作为新联合臂的默认初始化。不能使用
VisDrone 十类 `best.pt` 或 VisDrone 十类 `initial-state.pt` 做严格 UAVDT 训练。

## 环境

建议 Python 3.10、PyTorch 2.5.1+cu121、torchvision 0.20.1+cu121、
Ultralytics 8.4.90。普通依赖优先使用清华镜像，CUDA PyTorch 轮子使用官方 CUDA
索引。完整安装命令见代码仓库的
`docs/UAVDT_CAPACITY_V3_SAFE_JOINT_HANDOFF_ZH.md`。

## 运行

先执行：

```bash
python scripts/train_uavdt_capacity_v3_safe_fia.py \
  --data-yaml /data/UAVDT/uavdt.yaml \
  --baseline-args /data/UAVDT/baseline/args.yaml \
  --initial-state /data/UAVDT/protocols/fdr-initial-state-nc3.pt \
  --output-root /data/UAVDT/runs/current-joint \
  --dry-run
```

检查 authority JSON 后，删除 `--dry-run` 启动正式训练。启动器会从 baseline
继承训练参数，强制 `pretrained=false`、`resume=false`，并只调用当前 v3-Safe
联合 trainer。

## 结果边界

只有在 baseline 和新联合臂的数据、类别映射、输入尺寸、训练预算、增强、seed 和
评估器一致时，才能写成严格对比；否则必须标记为 cross-run。此目录不包含原始
数据集、模型权重、初始状态、密码或服务器凭据。

## 2026-09-15 用户导出结果

用户补充的 `exp/exp` 目录已原样归档到
[`user_export_20260915/`](user_export_20260915/)。其中 `paper_data.txt` 给出当前联合
模型的精确验证汇总：`P=0.4169、R=0.3310、F1=0.3690、AP50=0.2916、AP75=0.1750、
mAP50-95=0.1696`；逐类别结果和复杂度/速度也一并保留。该导出与已有服务器截图的
rounded 数值一致，因此更新的是 H12 的证据精度，不是新增训练实验。由于导出不含
checkpoint、seed、数据清单和原始预测，不能单独重跑评估或宣称 best-to-best 严格对比。

# UAVDT Baseline 实验方案（纯 RT-DETR-L，无 FDR/FIA/BPDD）

> 供他人独立复跑的完整源码与参数说明
> 对照实验目的：在**同一 UAVDT 数据、同一训练协议**下，与「RT-DETR-L + FDR + FIA + BPDD」三模块累加实验（v2）对比，量化三个模块各自的增益。
> 当前三模块实验状态：v2 已跑至约 24/100 轮（giou 平滑下降、无崩塌），完成后再启动 baseline 对比最稳妥。

---

## 1 一句话结论

本实验目前**未跑 baseline**。服务器 runs 目录仅有 v1（崩塌、已废弃）与 v2（三模块、进行中）两个实验，没有任何纯 RT-DETR-L 的对照运行。以下方案与 v2 实验严格同源同参，可直接交给他人执行。

## 2 实验目标

训练**纯 RT-DETR-L（nc=3, 300 queries, 不加载预训练）**，100 轮，seed 0，在官方 UAVDT-Benchmark-M 检测数据上，评估口径与 v2 完全一致（统一 YOLO 格式验证 mAP）。产出指标：epoch100 与 tail-5 的 Precision、Recall、mAP50、mAP50-95、mAP75，以及每轮完整指标 CSV。

## 3 数据准备（关键：与 v2 完全相同的数据划分）

数据源：官方 UAVDT-Benchmark-M 图像 + 官方 DET/MOT toolkit 标注（GT 与 ignore 文件）。

划分规则与 v2 完全一致：

| 项目 | 冻结值 |
|---|---|
| 类别映射 | car=0, truck=1, bus=2 |
| train | 官方 30 个训练序列（M0101, M0201, M0202, M0204, M0206, ...），共 24143 张图 + 314 背景 |
| val | 官方 20 个 DET/MOT 测试序列，共 16592 张图 + 12 背景 |
| 划分单位 | 完整视频序列，禁止随机拆帧，train/val 零交集 |
| 图像存储 | 同文件系统硬链接进入 YOLO 目录 |

服务器上已就绪的 YOLO 格式数据位于 `/home/ubuntu/uavdt-fdr-fia-bpdd/data/UAVDT/`（images/ 与 labels/ 各含 train/、val/ 两级目录）。若在别的机器复跑，需按相同序列划分生成相同目录结构。

数据 yaml（`UAVDT.yaml`）：

```yaml
path: /path/to/UAVDT        # 改为实际数据根目录
train: images/train
val: images/val
names:
  0: car
  1: truck
  2: bus
```

标签格式为 YOLO txt（归一化 xywh），示例：

```
0 0.50537109 0.67592593 0.02050781 0.04814815
0 0.53857422 0.60000000 0.01660156 0.02962963
```

## 4 环境

| 依赖 | 版本（与 v2 一致） |
|---|---|
| Python | 3.10 |
| torch | 2.5.1+cu121 |
| CUDA | 12.1 |
| ultralytics | 8.4.90 |
| GPU | 单卡（RTX 4090 实测 8-10 GB 显存） |

## 5 训练代码

baseline 只需 ultralytics 官方接口，不依赖私有仓库。训练脚本：

```python
# train_uavdt_baseline.py
from ultralytics import RTDETR

settings = dict(
    model="rtdetr-l.yaml",      # ultralytics 内置 stock RT-DETR-L，300 queries
    data="UAVDT.yaml",          # 上文数据 yaml
    epochs=100,
    seed=0,
    imgsz=640,
    batch=8,
    workers=8,
    device="0",
    pretrained=False,           # 关键：不加载预训练权重
    optimizer="MuSGD",
    lr0=0.01,
    lrf=0.01,
    momentum=0.937,
    weight_decay=0.0005,
    warmup_epochs=3.0,
    warmup_momentum=0.8,
    warmup_bias_lr=0.0,
    nbs=64,
    amp=True,                   # AMP scale 固定 128
    deterministic=True,
    mosaic=1.0,                 # 最后 10 轮关闭（见下）
    mixup=0.0,
    scale=0.5,
    translate=0.1,
    fliplr=0.5,
    flipud=0.0,
    shear=0.0,
    perspective=0.0,
    hsv_h=0.015,
    hsv_s=0.7,
    hsv_v=0.4,
    max_det=300,
    save=True,
    save_period=1,
    val=True,
    nms=False,
    cache=False,
    project="runs/baselines",
    name="uavdt-formal100-seed0-rtdetr-baseline",
    exist_ok=False,
)
model = RTDETR("rtdetr-l.yaml")
model.train(**settings)
```

命令行等价形式：

```bash
python -c "
from ultralytics import RTDETR
m = RTDETR('rtdetr-l.yaml')
m.train(model='rtdetr-l.yaml', data='UAVDT.yaml', epochs=100, seed=0, imgsz=640,
        batch=8, workers=8, device='0', pretrained=False, optimizer='MuSGD',
        lr0=0.01, lrf=0.01, momentum=0.937, weight_decay=0.0005,
        warmup_epochs=3.0, warmup_momentum=0.8, warmup_bias_lr=0.0, nbs=64,
        amp=True, deterministic=True, mosaic=1.0, mixup=0.0, scale=0.5,
        translate=0.1, fliplr=0.5, flipud=0.0, shear=0.0, perspective=0.0,
        hsv_h=0.015, hsv_s=0.7, hsv_v=0.4, max_det=300, save=True,
        save_period=1, val=True, nms=False, cache=False,
        project='runs/baselines', name='uavdt-formal100-seed0-rtdetr-baseline')
"
```

## 6 冻结参数汇总

| 类别 | 参数 | 值 |
|---|---|---|
| 训练 | epochs / seed | 100 / 0 |
| 训练 | image size / batch / workers | 640 / 8 / 8 |
| 训练 | GPU | 单卡，不用 DDP |
| 优化器 | optimizer / lr0 / lrf | MuSGD / 0.01 / 0.01 |
| 优化器 | momentum / weight decay | 0.937 / 0.0005 |
| 优化器 | warmup | 3 epochs |
| 精度 | AMP | 开启，scale 固定 128 |
| 确定性 | deterministic | true（CUBLAS_WORKSPACE_CONFIG=:4096:8） |
| 模型 | 结构 | RT-DETR-L，nc=3，300 queries，无预训练 |
| 增强 | mosaic | 1.0（最后 10 轮关闭） |
| 增强 | mixup | 0 |
| 增强 | scale / translate | 0.5 / 0.1 |
| 增强 | fliplr | 0.5 |
| 增强 | flipud / shear / perspective | 0 |
| 增强 | hsv_h / hsv_s / hsv_v | 0.015 / 0.7 / 0.4 |
| 推理 | max_det / nms | 300 / false |

要点：mosaic 最后 10 轮关闭——ultralytics 通过 `close_mosaic` 参数控制（epochs-10 自动生效），若用 `model.train()` 需传 `close_mosaic=10` 或等效设置。上述 settings 建议追加 `close_mosaic=10`。

## 7 与 v2 的一致性检查（复跑后必须核对）

1. epoch 1 参考值：train/giou≈1.36、cls≈0.57、l1≈0.35、mAP50≈0.14（v2 实测，baseline 结构更简单，数值应同量级，不必逐位相同——v2 含 FDR 私有头，参数与损失都更多）；
2. 全程 train/giou 必须为**正值且平滑下降**（v2 到 epoch24 已降至 0.23；若 baseline 出现负 giou 或突变，说明环境/数据/增强不一致，需要排查，参考 v2 的 GIoU 钳制经验）；
3. 产出必须包含：每轮 `results.csv`、`uavdt-run.json` 风格的运行记录、best/last 权重、训练耗时与峰值显存。

## 8 后续对照口径

| 实验 | 组合 | 用途 |
|---|---|---|
| baseline | 纯 RT-DETR-L | 性能下限，模块增益的基准 |
| v2（进行中） | RT-DETR-L + FDR + FIA + BPDD | 三模块累加上限 |
| （可选） | + FDR 单独 / + FDR+FIA | 归因每个模块的独立贡献 |

所有对照必须复用**同一初始状态（seed0）、同一数据划分、同一训练协议**，结论才可比。

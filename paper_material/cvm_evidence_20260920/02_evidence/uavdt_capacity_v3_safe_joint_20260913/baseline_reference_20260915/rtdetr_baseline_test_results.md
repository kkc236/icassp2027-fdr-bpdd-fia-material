# UAVDT RT-DETR Baseline 测试结果

## 实验信息

| 项目 | 内容 |
| --- | --- |
| 实验名称 | uavdt-formal100-seed0-rtdetr-baseline |
| 模型 | RT-DETR-L（Ultralytics） |
| 训练轮数 | 79 epochs（耗时 25.609 小时） |
| 权重文件 | `weights/best.pt` / `weights/last.pt`（各 66.2 MB，已剥离 optimizer） |
| 结果目录 | `/home/ubuntu/uavdt/runs/baselines/uavdt-formal100-seed0-rtdetr-baseline` |

## 运行环境

- Ultralytics 8.4.90
- Python 3.12.8
- PyTorch 2.5.1 + cu124
- GPU：NVIDIA GeForce RTX 4090（24210 MiB）

## 模型概况

- 层数：310
- 参数量：31,989,905
- 计算量：105.3 GFLOPs

## 最终训练验证结果（last.pt 对应）

| Class | Images | Instances | Box(P) | R | mAP50 | mAP50-95 |
| --- | --- | --- | --- | --- | --- | --- |
| all | 17165 | 342686 | 0.492 | 0.294 | 0.265 | 0.135 |

## 最佳权重验证结果（best.pt）

| Class | Images | Instances | Box(P) | R | mAP50 | mAP50-95 |
| --- | --- | --- | --- | --- | --- | --- |
| all | 17165 | 342686 | 0.527 | 0.310 | 0.277 | 0.156 |
| car | 16580 | 322200 | 0.672 | 0.579 | 0.536 | 0.293 |
| truck | 7087 | 15515 | 0.541 | 0.0446 | 0.106 | 0.0621 |
| bus | 3389 | 4971 | 0.367 | 0.307 | 0.189 | 0.112 |

## 推理速度（单张图像）

| 阶段 | 耗时 |
| --- | --- |
| preprocess | 0.1 ms |
| inference | 3.5 ms |
| loss | 0.0 ms |
| postprocess | 0.2 ms |

## 备注

- 验证集约 1073 个 batch，验证耗时约 1 分 47 秒（10.0 it/s）。
- truck 类召回率仅 0.0446，明显偏低，是后续优化的重点方向。

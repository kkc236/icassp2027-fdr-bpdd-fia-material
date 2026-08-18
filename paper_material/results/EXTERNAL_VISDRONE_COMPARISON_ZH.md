# VisDrone 外部方法与效率对比

本页用于 ICASSP 2027 论文的外部方法对比。外部论文报告值，不是本项目复跑值；只有原论文明确给出的数值才登记，缺失项统一写为 `not_reported`，不做反推。

口径先行：不同 split 不计算涨点，不同输入、预训练、评估器或运行环境也不做严格横向差值。本文只说明所提组合在已公开 VisDrone 结果中的相对位置，不宣称 SOTA。参数量不是筛选条件，也不是排序条件，只与 GFLOPs、FPS 一起作为描述字段保留。

## 1. VisDrone val：640×640 优先组

| 方法 | 正式来源 | Backbone | Input | P | R | AP50 | AP75 | mAP50–95 | Params (M) | GFLOPs | 证据 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| RT-DETR-L Baseline | 本项目 | RT-DETR-L | 640 | 0.46761 | 0.41731 | 0.38663 | 0.21302 | 0.21911 | not_reported | not_reported | our_run |
| **RT-DETR-L + FDR + BPDD + FIA** | 本项目 | RT-DETR-L | 640 | 0.5693 | 0.4991 | 0.4898 | 0.3042 | **0.2961** | 32.636 | 109.0 | our_run |
| Drone-DETR | [Sensors 2024, Table 2](https://doi.org/10.3390/s24175496) | RT-DETR-R18 | 640 | not_reported | not_reported | 0.539 | not_reported | 0.339 | 28.7 | not_reported | original paper |
| UAV-DETR-R18 | [IROS 2025, Table I](https://doi.org/10.1109/IROS60139.2025.11246176) | RT-DETR-R18 | 640 | not_reported | not_reported | 0.488 | not_reported | 0.298 | 20.0 | 77.0 | original paper |
| UAV-DETR-R50 | [IROS 2025, Table I](https://doi.org/10.1109/IROS60139.2025.11246176) | RT-DETR-R50 | 640 | not_reported | not_reported | 0.511 | not_reported | 0.315 | 42.0 | 170.0 | original paper |
| VRF-DETR | [Remote Sensing 2025, Table 9](https://doi.org/10.3390/rs17152672) | RT-DETR-derived | 640 | not_reported | not_reported | 0.521 | not_reported | 0.322 | 13.8 | 44.6 | original paper |

本项目行与外部行虽然都使用 640 输入，但 backbone、训练时长、初始化和 evaluator 并不完全一致。因此本表可用于说明结果位置，不能写成“本文相对 Drone-DETR/VRF-DETR 提升或下降多少”。

## 2. VisDrone test：640×640 优先组

| 方法 | 正式来源 | P | R | AP50 | AP75 | mAP50–95 | Params (M) | GFLOPs | 说明 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| RT-DETR-L Baseline | 本项目 | 0.41798 | 0.37301 | 0.32221 | 0.17550 | 0.17742 | not_reported | not_reported | 1,610 images / 75,102 instances |
| **RT-DETR-L + FDR + BPDD + FIA** | 本项目 | **0.5189** | **0.4361** | **0.4081** | **0.2327** | **0.2337** | 32.636 | 109.0 | 四位小数 test 文本记录 |
| Drone-DETR | [Sensors 2024, Table 3](https://doi.org/10.3390/s24175496) | not_reported | not_reported | 0.424 | not_reported | 0.249 | 28.7 | not_reported | 原文明确为 VisDrone2019-test |
| VRF-DETR | [Remote Sensing 2025, Table 10](https://doi.org/10.3390/rs17152672) | not_reported | not_reported | 0.399 | not_reported | 0.233 | 13.8 | 44.6 | test，统一 640 输入 |
| RT-UAV-SOD | [Scientific Reports 2025, Table 2](https://doi.org/10.1038/s41598-025-22855-w) | 0.567 | 0.421 | 0.401 | not_reported | 0.229 | 18.6 | 60.0 | 原文明确为 VisDrone2019-DET test |
| YOLOv13s | [Remote Sensing 2026, Table 1](https://doi.org/10.3390/rs18142404) | 0.428 | 0.318 | 0.296 | not_reported | 0.170 | 9.04 | 20.7 | scratch；RTX 4090 同协议速度基线 |
| WaveUAV-YOLO | [Remote Sensing 2026, Table 1](https://doi.org/10.3390/rs18142404) | 0.467 | 0.352 | 0.335 | not_reported | 0.193 | 11.70 | 30.6 | scratch；RTX 4090 同协议方法行 |

本项目三模块 test mAP50–95=`0.2337`，与 VRF-DETR 的论文报告值 `0.233` 接近，并高于同表列出的 RT-UAV-SOD `0.229` 和 WaveUAV-YOLO `0.193`；但这些只是跨论文绝对值观察，不是严格配对增益。Drone-DETR 的 `0.249` 高于本项目值，同样只作位置参照。

## 3. split 或输入未明确：只作补充观察

| 方法 | 正式来源 | Split | Input | AP50 | AP75 | mAP50–95 | Params (M) | GFLOPs | FPS |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| MCG-RTDETR | [Remote Sensing 2024, Table 3](https://doi.org/10.3390/rs16173169) | not_reported | 640 | 0.582 | 0.263 | 0.297 | 22.64 | 89.7 | 84.1 |
| NRQO | [ICME 2025, Table I](https://doi.org/10.1109/ICME59968.2025.11209405) | not_reported | not_reported | 0.517 | 0.339 | 0.321 | 63.0 | not_reported | not_reported |

MCG-RTDETR 和 NRQO 都已经正式发表，但论文没有把对应表格明确绑定为 val 或 test，因此不能把 `0.297/0.321` 与本项目 `0.2961/0.2337` 直接计算涨点。

## 4. RTX 4090 与 YOLO 效率材料

### 4.1 可直接比较的 4090 成对速度

下表两行来自同一篇正式论文、同一 VisDrone test-dev、同一台 RTX 4090，均为 `640×640`、batch=1、PyTorch 2.2.2，并统计 preprocessing + network inference + NMS 的端到端延迟。论文未明确写推理精度，因此该字段保持 `not_reported`。

| 方法 | AP50 | mAP50–95 | Params (M) | GFLOPs | FPS | GPU | Batch | Precision | Backend | Latency scope |
|---|---:|---:|---:|---:|---:|---|---:|---|---|---|
| YOLOv13s | 0.296 | 0.170 | 9.04 | 20.7 | 52.12 | RTX 4090 | 1 | not_reported | PyTorch 2.2.2 | preprocess + inference + NMS |
| WaveUAV-YOLO | 0.335 | 0.193 | 11.70 | 30.6 | 48.95 | RTX 4090 | 1 | not_reported | PyTorch 2.2.2 | preprocess + inference + NMS |

这两行之间允许直接比较 FPS；它们不能与本项目硬件未绑定的 `81.49 FPS` 直接比较。

### 4.2 4090 训练、3080 测速的统一标准基线

[FBRT-YOLO（AAAI 2025）Table 1](https://doi.org/10.1609/aaai.v39i8.32937) 在同一正式论文中重测了一组标准实时检测器。论文明确说明实验在 RTX 4090 上完成，但 inference speed 例外地在单张 RTX 3080 上测试；论文也没有明确给出 VisDrone split、输入尺寸、推理 batch、精度、backend 和 latency scope。因此这些行可比较 AP/参数量/GFLOPs 的大致位置，FPS 不能与 4090 表或本项目直接比较。

| 标准基线 | AP | AP50 | Params (M) | GFLOPs | FPS | Training GPU | FPS GPU | Split/Input |
|---|---:|---:|---:|---:|---:|---|---|---|
| YOLOv8-M | 0.271 | 0.444 | 25.9 | 78.9 | 83 | RTX 4090 | RTX 3080 | not_reported |
| YOLOv8-L | 0.284 | 0.459 | 43.7 | 165.2 | 61 | RTX 4090 | RTX 3080 | not_reported |
| YOLOv10-L | 0.276 | 0.446 | 24.4 | 120.3 | 64 | RTX 4090 | RTX 3080 | not_reported |
| RT-DETR-R50 | 0.288 | 0.483 | 42.0 | 136.0 | 65 | RTX 4090 | RTX 3080 | not_reported |

这里只使用 AAAI 论文提供的统一标准 baseline 测量，不把 FBRT-YOLO 方法本身作为与 ICASSP 同级的投稿层级对手。

## 5. 相关方法的创新规模与原论文内增量

| 方法 | 主要创新模块 | 原论文内部参照 | mAP50–95 变化 | 数据集/表格覆盖 |
|---|---|---|---:|---|
| Drone-DETR | ESDNet、EDF-FAM、P2 浅层特征融合 | RT-DETR-R18 | val 0.277→0.339（+6.2 pp）；test 0.207→0.249（+4.2 pp） | VisDrone val/test + DOTA；多张对比/消融表 |
| UAV-DETR | MSFF-FE、frequency-focused downsampling、SAC、Inner-SIoU | 对应 RT-DETR-R18/R50 | R18 0.267→0.298（+3.1 pp）；R50 0.284→0.315（+3.1 pp） | VisDrone val + UAVVaste；主表、消融、IoU、效率表 |
| MCG-RTDETR | DualConv/DeConv、CGAM、CGD、P3 head | RT-DETR-R18 | 0.250→0.297（+4.7 pp） | VisDrone + 模块消融/外部方法/AR 表；split 未明确 |
| VRF-DETR | MSRF、AGConv/GMSC、CGF、轻量 backbone | 原文整体消融 baseline | val +3.5 pp | VisDrone val/test + UAVDT；主对比、消融、效率表 |
| NRQO | NT-FPN、PS-RPN | Table III baseline | 0.285→0.321（+3.6 pp） | VisDrone、SODA-D、COCO；多数据集 + 两模块消融 |
| RT-UAV-SOD | CGA-iRMB、GS-Fusion | RT-DETR | test 0.204→0.229（+2.5 pp） | VisDrone test + DOTA + 泛化示例；主表和消融表 |
| WaveUAV-YOLO | WHFD、C2f_AMSB、FFM_Concat、CSFM_Fusion | YOLOv13s Table 1 | test 0.170→0.193（+2.3 pp） | VisDrone test + DIOR/NWPU/HIT-UAV；多数据集、逐类、消融、效率表 |

这组文献说明，B 会或相近体量论文常见做法是 2–4 个互补模块、1 张主对比表、1–3 张消融/效率表，并至少用一个补充数据集或 test split 增强可信度。本项目已有三创新点、完整 A–E val/test 表和逐类 test 结果；外部方法表补齐后，最需要继续谨慎处理的不是“表格数量”，而是跨 authority 的非严格增量和缺少同硬件速度复测。

## 6. 使用边界

- 可以写：本文完整模型在 VisDrone val/test 上分别达到 `0.2961/0.2337` mAP50–95；与正式发表方法的同 split 结果处于可竞争区间。
- 可以写：FDR 提供主要提升，BPDD 和 FIA 在其上形成训练监督与高分辨率表征的互补组合。
- 不可以写：本文优于所有方法、达到 SOTA，或对 split/input/evaluator 不一致的外部行计算百分比提升。
- 不可以把 RTX 3080 FPS 当成 RTX 4090 FPS；也不可以把本项目硬件未绑定的速度与论文速度直接排序。
- 预印本、仅 arXiv、仅 ResearchGate 和无法核实正式出版信息的方法不进入本页、JSON 或 CSV。

机器可读来源：[`external_visdrone_comparison.json`](external_visdrone_comparison.json)；平铺表：[`external_visdrone_comparison.csv`](external_visdrone_comparison.csv)；证据绑定：[`../evidence/source_manifest.json`](../evidence/source_manifest.json)。

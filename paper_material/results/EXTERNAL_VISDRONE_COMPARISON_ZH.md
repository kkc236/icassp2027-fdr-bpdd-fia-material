# VisDrone CCF B 会外部方法对比

本页用于 ICASSP 2027 论文的外部方法对比。外部论文报告值，不是本项目复跑值；只有原论文明确给出的数值才登记，缺失项统一写为 `not_reported`，不做反推。

会议口径固定为 CCF B 类正式会议 full/regular paper。按 CCF 当前目录，本文只采用 ICASSP、ICRA、ICME、IROS 四个会议的已正式发表论文；不再把顶会、期刊或仅预印本来源混入正式外部表。不同 split 不计算涨点，不同输入、预训练、评估器或运行环境也不做严格横向差值；本文不宣称 SOTA。参数量不是筛选条件，也不是排序条件，只作为规模上下文保留。

CCF 目录依据：[图形学与多媒体（ICASSP、ICME）](https://www.ccf.org.cn/Academic_Evaluation/CGAndMT/)；[人工智能（ICRA、IROS）](https://www.ccf.org.cn/Academic_Evaluation/AI/)。

## 1. VisDrone val：640×640 B 会优先组

| 方法 | B 会正式来源 | Backbone | Input | P | R | AP50 | AP75 | mAP50–95 | Params (M) | GFLOPs | 证据 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| RT-DETR-L Baseline | 本项目 | RT-DETR-L | 640 | 0.46761 | 0.41731 | 0.38663 | 0.21302 | 0.21911 | not_reported | not_reported | our_run |
| **RT-DETR-L + FDR + BPDD + FIA** | 本项目 | RT-DETR-L | 640 | 0.5693 | 0.4991 | 0.4898 | 0.3042 | **0.2961** | 32.636 | 109.0 | our_run |
| YOLOv8-M | [IROS 2025, Table I](https://doi.org/10.1109/IROS60139.2025.11246176) | YOLOv8-M | 640 | not_reported | not_reported | 0.407 | not_reported | 0.246 | 25.9 | 78.9 | B 会论文统一表 |
| YOLOv8-L | [IROS 2025, Table I](https://doi.org/10.1109/IROS60139.2025.11246176) | YOLOv8-L | 640 | not_reported | not_reported | 0.427 | not_reported | 0.261 | 43.7 | 165.2 | B 会论文统一表 |
| HIC-YOLOv5 | [ICRA 2024, Table IV](https://doi.org/10.1109/ICRA57147.2024.10610273) | YOLOv5-6.0 | 640 | not_reported | not_reported | 0.4431 | not_reported | 0.2595 | not_reported | not_reported | original paper |
| YOLOv5x + EMA | [ICASSP 2023, Table 2](https://doi.org/10.1109/ICASSP49357.2023.10096516) | YOLOv5x + tiny head | 640 | not_reported | not_reported | 0.4970 | not_reported | 0.3040 | 91.18 | 315.0 | original paper |
| RT-DETR-R18 | [IROS 2025, Table I](https://doi.org/10.1109/IROS60139.2025.11246176) | RT-DETR-R18 | 640 | not_reported | not_reported | 0.446 | not_reported | 0.267 | 20.0 | 60.0 | B 会论文统一表 |
| RT-DETR-R50 | [IROS 2025, Table I](https://doi.org/10.1109/IROS60139.2025.11246176) | RT-DETR-R50 | 640 | not_reported | not_reported | 0.470 | not_reported | 0.284 | 42.0 | 136.0 | B 会论文统一表 |
| UAV-DETR-EV2 | [IROS 2025, Table I](https://doi.org/10.1109/IROS60139.2025.11246176) | EfficientFormerV2 | 640 | not_reported | not_reported | 0.475 | not_reported | 0.287 | 13.0 | 43.0 | original paper |
| UAV-DETR-R18 | [IROS 2025, Table I](https://doi.org/10.1109/IROS60139.2025.11246176) | RT-DETR-R18 | 640 | not_reported | not_reported | 0.488 | not_reported | 0.298 | 20.0 | 77.0 | original paper |
| UAV-DETR-R50 | [IROS 2025, Table I](https://doi.org/10.1109/IROS60139.2025.11246176) | RT-DETR-R50 | 640 | not_reported | not_reported | 0.511 | not_reported | 0.315 | 42.0 | 170.0 | original paper |

同为 640 输入时，本项目 `0.2961` mAP50–95 高于表中的标准 RT-DETR-R50 `0.284`、YOLOv8-L `0.261` 和 HIC-YOLOv5 `0.2595`，接近 UAV-DETR-R18 `0.298` 与 EMA `0.304`，低于 UAV-DETR-R50 `0.315`。这些是 B 会论文绝对值位置，不写成跨论文“提升多少”。

参数规模上，本项目 `32.636M` 介于 YOLOv8-M `25.9M` 与 RT-DETR-R50/UAV-DETR-R50 `42M` 之间；YOLOv8-M 是表中与本项目规模较接近的标准 YOLO 参照。初始化、epoch 和 evaluator 仍不完全一致。

## 2. VisDrone test：B 会正式结果

| 方法 | B 会正式来源 | P | R | AP50 | AP75 | mAP50–95 | Input | 说明 |
|---|---|---:|---:|---:|---:|---:|---:|---|
| RT-DETR-L Baseline | 本项目 | 0.41798 | 0.37301 | 0.32221 | 0.17550 | 0.17742 | 640 | 1,610 images / 75,102 instances |
| **RT-DETR-L + FDR + BPDD + FIA** | 本项目 | **0.5189** | **0.4361** | **0.4081** | **0.2327** | **0.2337** | 640 | 四位小数 test 文本记录 |
| HIC-YOLOv5 | [ICRA 2024, Table IV/VI](https://doi.org/10.1109/ICRA57147.2024.10610273) | 0.4788 | 0.3849 | 0.3695 | not_reported | 0.2085 | 640 | 原文明确标为 Test |

当前能直接绑定 B 会原论文、明确 test 和 640 输入的行不多。本项目三模块 test 的 AP50/mAP50–95 为 `0.4081/0.2337`，HIC-YOLOv5 为 `0.3695/0.2085`；可写“绝对值更高”，但由于训练配置和 evaluator 不同，不计算严格增益。

## 3. split 或输入未明确：只作补充观察

| 方法 | B 会正式来源 | Split | Input | AP50 | AP75 | mAP50–95 | Params (M) |
|---|---|---|---|---:|---:|---:|---:|
| NRQO | [ICME 2025, Table I](https://doi.org/10.1109/ICME59968.2025.11209405) | not_reported | not_reported | 0.517 | 0.339 | 0.321 | 63.0 |

NRQO 已正式发表于 ICME，但原文没有把该 VisDrone 行明确绑定为 val 或 test，输入尺寸也未明确。因此 `0.321` 只能作为同级会议方法位置，不能与本项目 `0.2961/0.2337` 计算涨点。

## 4. B 会论文通常怎么组织实验

| 论文 | 创新模块 | 原论文内部增量 | 定量表数量 | 外部方法表 | 多数据集 | 多种子 |
|---|---|---:|---:|:---:|:---:|:---:|
| EMA（ICASSP 2023） | 1 个跨空间多尺度注意力模块；VisDrone 实验另加 tiny head | YOLOv5x：0.300→0.304，+0.4 pp | 4 | ✓ | ✓（分类与检测共 4 个数据集） | 未报告 |
| HIC-YOLOv5（ICRA 2024） | 小目标检测头、Involution、CBAM，共 3 项 | test 0.1443→0.2085，+6.42 pp | 3 个核心结果/消融表 | ✓ | 否（主实验为 VisDrone） | 未报告 |
| UAV-DETR（IROS 2025） | Inner-SIoU、MSFF-FE、FD、SAC，共 4 项 | R18 0.267→0.298，+3.1 pp；R50 0.284→0.315，+3.1 pp | 5 | ✓ | ✓（VisDrone、UAVVaste） | 未报告 |
| NRQO（ICME 2025） | NT-FPN、PS-RPN，共 2 项 | 0.285→0.321，+3.6 pp | 4 | ✓ | ✓（VisDrone、SODA-D、COCO） | 未报告 |

对 B 会而言，本项目的“三个互补创新点 + val/test 主表 + 模块消融 + 逐类分析 + 外部方法表”在实验结构上够用。现有同级论文也普遍不是多种子设计；所以多种子不是投稿前的硬门槛。更值得补的是把现有表压缩成清晰主线，并确保每个模块的增量、复杂度和失败边界可解释。

## 5. 硬件与速度边界

B 会限定后，没有找到同时满足“VisDrone、正式 CCF B full paper、RTX 4090、完整 batch/precision/backend/latency scope”的可直接速度对比。为避免混入其他层级来源，正式表不再保留 4090 行。

IROS 论文报告 RT-DETR-R18/R50 与 UAV-DETR 的 RTX 3090、PyTorch FP32 FPS，但未完整给出 batch 和 latency scope；本项目 `81.49 FPS` 又未绑定 GPU。因此速度只作背景字段，不排序、不宣称更快。若论文必须给速度对比，应在同一台机器上复测 2–3 个代表模型。

## 6. 使用边界

- 可以写：本文完整模型在 VisDrone val/test 上分别达到 `0.2961/0.2337` mAP50–95，并在 CCF B 会公开结果中处于可竞争区间。
- 可以写：在 640-val 表中，本项目数值接近 UAV-DETR-R18 与 EMA，并高于表中标准 RT-DETR-R50、YOLOv8-L 和 HIC-YOLOv5 的报告值。
- 不可以写：本文优于所有方法、达到 SOTA，或对不同协议外部行计算百分比提升。
- 不可以把 split=`not_reported` 的 NRQO 行并入 val/test 排名。
- 不可以把不同硬件或不完整测速协议的 FPS 直接排序。
- 顶会、期刊、仅预印本、仅聚合页和无法核实正式出版信息的方法不进入本页、JSON 或 CSV。

机器可读来源：[`external_visdrone_comparison.json`](external_visdrone_comparison.json)；平铺表：[`external_visdrone_comparison.csv`](external_visdrone_comparison.csv)；证据绑定：[`../evidence/source_manifest.json`](../evidence/source_manifest.json)。

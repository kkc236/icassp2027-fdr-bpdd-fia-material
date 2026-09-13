# VisDrone CCF A/B 会外部方法对比

本页用于 ICASSP 2027 论文的外部方法对比。外部论文报告值，不是本项目复跑值；只登记正式 full/regular paper 原文可核对的数值，缺失项写为 `not_reported`，不反推。

会议等级按 CCF 当前目录标为 A/B：AAAI、CVPR、ICCV、IJCAI 为 CCF A；ICASSP、ICME、ICRA、IROS 为 CCF B。目录依据：[人工智能](https://www.ccf.org.cn/Academic_Evaluation/AI/)；[图形学与多媒体](https://www.ccf.org.cn/Academic_Evaluation/CGAndMT/)。

排序规则固定为：先列“综合不高于本文”，再列“综合高于本文”，最后列“不可排序”；综合指标仅指同一已报告 split 的 mAP50–95。当前联合主记录的 val 参照是 `0.30109`（E97），test 尚未在同一新 authority 下登记；旧 `0.2961/0.2337` 只作为历史 AP-FDR 三模块参照。组内“不高于”按 mAP 从高到低排列，“高于”按从低到高排列，优先显示最接近本文的结果。这个标签只是绝对值位置，不是严格公平比较：不同输入、预训练、数据处理、训练周期和 evaluator 仍可能不同。不同 split 不计算涨点，跨论文也不写成因果提升；本文不宣称 SOTA。参数量不是筛选条件，只保留为规模上下文。

## 当前联合参照

| 方法 | 状态 | Input | P | R | AP50 | mAP50–95 | 证据 |
|---|---|---:|---:|---:|---:|---:|---|
| **LRS-GFDR + Capacity-BPDD-v3-Safe + FIA** | current joint Formal100, best E97 | 640 | 0.60482 | 0.49693 | 0.49890 | **0.30109** | [`joint-results.csv`](../evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/joint-results.csv) |

下方旧的 `RT-DETR-L + FDR + BPDD + FIA` 外部排序表保留为历史快照，不能与当前联合臂混用。

ResBiDet 与 VARDet 是最直接的同会任务邻居。ResBiDet 发表于 ICASSP 2026，正式摘要报告 VisDrone2019 AP50=`0.387`，低于本文 AP50=`0.4898`；但可访问摘要未给 mAP50–95、split、精确双分辨率输入或完整 evaluator，因此只能作为同会 AP50 位置证据，不能并入 mAP 排名。VARDet 同样发表于 ICASSP 2026，其 Table 1 采用作者统一重实现的 ResNet-50、1333×800、COCO-style 协议；本文采用 RT-DETR-L、640×640 的冻结协议。因此下表登记其绝对结果，但标为非严格可比，不能把 `0.3650−0.2961` 写成方法本身带来的公平差距。

## 1. 历史 AP-FDR 三模块 VisDrone val 参照（已 superseded）

| 方法 | 本文 | Input | P | R | AP50 | AP75 | mAP50–95 | Params (M) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| **RT-DETR-L + FDR + BPDD + FIA** | reference | 640 | 0.5693 | 0.4991 | 0.4898 | 0.3042 | **0.2961** | 33.458 |

### 1.1 综合不高于本文（同为 val，按 mAP 降序）

| 排名 | 方法 | 会议 | 等级 | 家族 | Input/处理 | AP50 | AP75 | mAP50–95 | Params (M) |
|---:|---|---|:---:|---|---|---:|---:|---:|---:|
| 1 | TPH-YOLOv5-x + UGS | [ICCV 2025, Table 2](https://openaccess.thecvf.com/content/ICCV2025/papers/Sun_Uncertainty-Aware_Gradient_Stabilization_for_Small_Object_Detection_ICCV_2025_paper.pdf) | **A** | YOLO | 640 | not_reported | not_reported | **0.2900** | not_reported |
| 2 | UAV-DETR-EV2 | [IROS 2025, Table I](https://doi.org/10.1109/IROS60139.2025.11246176) | **B** | DETR | 640 | 0.4750 | not_reported | **0.2870** | 13.0 |
| 3 | RT-DETR-R50 | [IROS 2025, Table I](https://doi.org/10.1109/IROS60139.2025.11246176) | **B** | DETR | 640 | 0.4700 | not_reported | **0.2840** | 42.0 |
| 4 | QueryDet | [CVPR 2022, Table 2](https://openaccess.thecvf.com/content/CVPR2022/papers/Yang_QueryDet_Cascaded_Sparse_Query_for_Accelerating_High-Resolution_Small_Object_Detection_CVPR_2022_paper.pdf) | **A** | RetinaNet/稀疏查询 | 原图四块非重叠 patch | 0.4814 | 0.2875 | **0.2832** | not_reported |
| 5 | RT-DETR-R18 | [IROS 2025, Table I](https://doi.org/10.1109/IROS60139.2025.11246176) | **B** | DETR | 640 | 0.4460 | not_reported | **0.2670** | 20.0 |
| 6 | ClusDet-R50 | [ICCV 2019, Table 2](https://openaccess.thecvf.com/content_ICCV_2019/papers/Yang_Clustered_Object_Detection_in_Aerial_Images_ICCV_2019_paper.pdf) | **A** | two-stage | 原图 + cluster crops | 0.5060 | 0.2470 | **0.2670** | not_reported |
| 7 | YOLOv8-L | [IROS 2025, Table I](https://doi.org/10.1109/IROS60139.2025.11246176) | **B** | YOLO | 640 | 0.4270 | not_reported | **0.2610** | 43.7 |
| 8 | HIC-YOLOv5 | [ICRA 2024, Table IV](https://doi.org/10.1109/ICRA57147.2024.10610273) | **B** | YOLO | 640 | 0.4431 | not_reported | **0.2595** | not_reported |
| 9 | YOLOv8-M | [IROS 2025, Table I](https://doi.org/10.1109/IROS60139.2025.11246176) | **B** | YOLO | 640 | 0.4070 | not_reported | **0.2460** | 25.9 |

这个组提供了最适合正文的“竞争位置”证据：本文 `0.2961` 高于多项 A/B 会报告值。首选三条主对照是 A 会 ICCV 的 TPH-YOLOv5-x+UGS（`0.2900`），以及 640 输入的 B 会 UAV-DETR-EV2、标准 RT-DETR-R50（`0.2870/0.2840`）。它们与本文数值接近，能说明结果并非只优于早期或弱基线。QueryDet 和 ClusDet 使用切块/聚类裁剪，只作为不同处理路线的背景对照，不写成同协议胜出。

### 1.2 综合高于本文（同为 val，按 mAP 升序）

| 排名 | 方法 | 会议 | 等级 | 家族 | Input/处理 | AP50 | AP75 | mAP50–95 | Params (M) |
|---:|---|---|:---:|---|---|---:|---:|---:|---:|
| 1 | DM-EFS | [ICCV 2025, Table 2](https://openaccess.thecvf.com/content/ICCV2025/papers/Sharma_DM-EFS_Dynamically_Multiplexed_Expanded_Features_Set_Form_for_Robust_and_ICCV_2025_paper.pdf) | **A** | YOLOv7 | 640 | 0.5180 | 0.2930 | **0.2971** | not_reported |
| 2 | UAV-DETR-R18 | [IROS 2025, Table I](https://doi.org/10.1109/IROS60139.2025.11246176) | **B** | DETR | 640 | 0.4880 | not_reported | **0.2980** | 20.0 |
| 3 | RAFDE | [IJCAI 2025, Tables 1–2](https://www.ijcai.org/proceedings/2025/78) | **A** | YOLOv11m | 640；batch=8；150 epochs | 0.4850 | not_reported | **0.3000** | 11.02 |
| 4 | YOLOv5x + EMA | [ICASSP 2023, Table 2](https://doi.org/10.1109/ICASSP49357.2023.10096516) | **B** | YOLO | 640；部分预训练 | 0.4970 | not_reported | **0.3040** | 91.18 |
| 5 | UAV-DETR-R50 | [IROS 2025, Table I](https://doi.org/10.1109/IROS60139.2025.11246176) | **B** | DETR | 640 | 0.5110 | not_reported | **0.3150** | 42.0 |
| 6 | VARDet | [ICASSP 2026, Table 1](https://doi.org/10.1109/ICASSP55912.2026.11463846) | **B** | Transformer detector | 1333×800；R50；统一重实现 | 0.6170 | 0.3910 | **0.3650** | not_reported |
| 7 | UFPMP-Det-R50 | [AAAI 2022, Table 1](https://ojs.aaai.org/index.php/AAAI/article/view/19986/19745) | **A** | two-stage | 1333×800；foreground packing | 0.6240 | 0.3670 | **0.3660** | not_reported |
| 8 | DINO-5scale + UGS | [ICCV 2025, Table 1](https://openaccess.thecvf.com/content/ICCV2025/papers/Sun_Uncertainty-Aware_Gradient_Stabilization_for_Small_Object_Detection_ICCV_2025_paper.pdf) | **A** | DETR | multi-scale；max_det=1500 | 0.6190 | not_reported | **0.3810** | not_reported |

DM-EFS 与本文最接近，仅在绝对 mAP 上高 `0.0010`；UAV-DETR-R18 高 `0.0019`；RAFDE 高 `0.0039`，均不能写成统计显著差异。RAFDE 是最重要的近邻上界：它同为 640 VisDrone val，但采用 YOLOv11m、RAFF+BTRD 和不同训练/evaluator；其完整方法为 AP50=`0.4850`、mAP=`0.3000`，参数量 `11.02M`。本文 AP50=`0.4898` 略高，但 mAP=`0.2961` 略低，适合写成“不同 DETR 路线下达到接近的综合精度”，不适合写成全面优于。VARDet 的 VisDrone val 为 AP50=`0.6170`、AP75=`0.3910`、mAP=`0.3650`；同表 UAVDT val 为 `0.4010/0.3720/0.2480`。VARDet、UFPMP-Det 与 DINO+UGS 使用更高分辨率、切块/多尺度或更宽松的最大预测数，属于强协议参考，不适合直接作为 640 单次推理的公平对照。

## 2. VisDrone test：明确 split 的正式结果

| 相对本文 | 方法 | 会议 | 等级 | P | R | AP50 | AP75 | mAP50–95 | Input |
|---|---|---|:---:|---:|---:|---:|---:|---:|---:|
| reference | **RT-DETR-L + FDR + BPDD + FIA** | 本项目 | — | 0.5189 | 0.4361 | 0.4081 | 0.2327 | **0.2337** | 640 |
| 不高于本文 | HIC-YOLOv5 | [ICRA 2024, Table IV/VI](https://doi.org/10.1109/ICRA57147.2024.10610273) | **B** | 0.4788 | 0.3849 | 0.3695 | not_reported | **0.2085** | 640 |

当前正式 A/B full paper 中，能同时明确 VisDrone test、640 输入和完整 AP 行的结果很少。这里可以写“本文报告值更高”，但训练源和 evaluator 不同，仍不计算严格增益。

## 3. split/input 未明确：不可排序

| 方法 | 会议 | 等级 | Split | Input | AP50 | AP75 | mAP50–95 | Params (M) | GPU 边界 |
|---|---|:---:|---|---|---:|---:|---:|---:|---|
| RT-DETR-R34 | [AAAI 2025, Table 1](https://ojs.aaai.org/index.php/AAAI/article/download/32937/35092) | **A** | not_reported | not_reported | 0.460 | not_reported | 0.272 | 31.0 | train 4090；speed 3080 |
| YOLOv10-X | [AAAI 2025, Table 1](https://ojs.aaai.org/index.php/AAAI/article/download/32937/35092) | **A** | not_reported | not_reported | 0.461 | not_reported | 0.287 | 29.5 | train 4090；speed 3080 |
| FBRT-YOLO-L | [AAAI 2025, Table 1](https://ojs.aaai.org/index.php/AAAI/article/download/32937/35092) | **A** | not_reported | not_reported | 0.477 | not_reported | 0.297 | 14.6 | train 4090；speed 3080 |
| FBRT-YOLO-X | [AAAI 2025, Tables 1–2](https://ojs.aaai.org/index.php/AAAI/article/download/32937/35092) | **A** | not_reported | not_reported | 0.484 | 0.317 | 0.301 | 22.8 | train 4090；speed 3080 |
| NRQO | [ICME 2025, Table I](https://doi.org/10.1109/ICME59968.2025.11209405) | **B** | not_reported | not_reported | 0.517 | 0.339 | 0.321 | 63.0 | train 3090 |
| ResBiDet | [ICASSP 2026, IEEE abstract](https://doi.org/10.1109/ICASSP55912.2026.11464428) | **B** | not_reported | 双分辨率；精确尺寸 not_reported | **0.387** | not_reported | not_reported | not_reported | not_reported |

AAAI 2025 的 FBRT-YOLO 论文确实满足“正式 A 会 + VisDrone + RTX 4090 训练”，也给出参数量相近的 RT-DETR-R34（31.0M）和 YOLOv10-X（29.5M）。但原文没有把 VisDrone 表绑定到 val/test，也没有写 input，因此这些行只能用于模型规模和方法覆盖，不能标为高于或不高于本文。FPS 来自 RTX 3080，不是 4090。ResBiDet 的 IEEE 摘要确认 VisDrone2019 AP50=`0.387`，相对本文 AP50=`0.4898` 低 `10.28 pp`；这一差值只能作为同会、同指标的描述性位置，不能替代缺失的 mAP50–95 或协议信息。

## 4. A/B 会论文的创新与实验组织

| 论文 | 等级 | 主要创新模块 | 原论文内部 VisDrone 增量 | 外部方法表 | 多数据集 | 多种子 |
|---|:---:|---|---:|:---:|:---:|:---:|
| ClusDet（ICCV 2019） | A | CPNet、ScaleNet、专用 DetecNet | R50：0.214→0.267，+5.3 pp | ✓ | ✓（VisDrone、UAVDT、DOTA） | 未报告 |
| QueryDet（CVPR 2022） | A | Query Head、CSQ 稀疏级联查询 | 0.2621→0.2832，+2.11 pp | ✓ | ✓（COCO、VisDrone） | 未报告 |
| UFPMP-Det（AAAI 2022） | A | UFP foreground packing、MP-Det/BoIW | 完整 R50 为 0.366；原文未给一个可独立归因的串行总增量 | ✓ | ✓（VisDrone、UAVDT） | 未报告 |
| FBRT-YOLO（AAAI 2025） | A | redundancy reduction、FCM、MKP | YOLOv8-S：0.236→0.259，+2.3 pp | ✓ | ✓（VisDrone、UAVDT、AI-TOD） | 未报告 |
| DM-EFS（ICCV 2025） | A | 动态复用扩展特征集合 | YOLOv7：0.276→0.2971，+2.11 pp | ✓ | ✓（SODA-D、VisDrone、DarkFace） | 未报告 |
| UGS（ICCV 2025） | A | 离散定位、UM loss、UR refinement | DINO：0.355→0.381，+2.6 pp；TPH-640：0.265→0.290，+2.5 pp | ✓ | ✓（4 个 benchmark） | 未报告 |
| RAFDE（IJCAI 2025） | A | RAFF 区域自适应融合、BTRD 边界过渡区域增强下采样 | YOLOv11m：0.266→0.300，+3.4 pp；RAFF 单独 +2.2 pp，BTRD 追加 +1.2 pp | ✓ | ✓（VisDrone、Drone-vs-Bird） | 未报告 |
| EMA（ICASSP 2023） | B | 跨空间多尺度注意力；VisDrone 加 tiny head | YOLOv5x：0.300→0.304，+0.4 pp | ✓ | ✓ | 未报告 |
| VARDet（ICASSP 2026） | B | visual autoregressive multi-scale prediction、CLIP-guided semantics | 当前证据只绑定 Table 1 绝对值，内部串行增量 not_reported | ✓ | ✓（VisDrone、UAVDT） | 未报告 |
| ResBiDet（ICASSP 2026） | B | 低分辨率全图粗分支引导高分辨率局部精分支 | 可访问摘要仅给绝对 AP50：VisDrone2019 0.387、UAVDT 0.402 | 未从正文核实 | ✓（VisDrone2019、UAVDT） | 未报告 |
| HIC-YOLOv5（ICRA 2024） | B | 小目标头、Involution、CBAM | test：0.1443→0.2085，+6.42 pp | ✓ | 否（主实验 VisDrone） | 未报告 |
| UAV-DETR（IROS 2025） | B | Inner-SIoU、MSFF-FE、FD、SAC | R18/R50 均 +3.1 pp | ✓ | ✓（VisDrone、UAVVaste） | 未报告 |
| NRQO（ICME 2025） | B | NT-FPN、PS-RPN | 0.285→0.321，+3.6 pp | ✓ | ✓（VisDrone、SODA-D、COCO） | 未报告 |

这个样本说明：A/B 会同类工作通常采用 2–4 个相互配合的模块、一个主对比表、一个串行消融表和若干复杂度/泛化分析；多种子并不是这些论文的普遍配置。本项目“三个创新点 + val/test + 组合消融 + 逐类结果 + 外部 A/B 表”的结构达到一般 B 会所需完整度。当前更值得补的是把 BPDD 的作用解释清楚，而不是为了形式强行增加第三数据集。

## 5. 论文写作边界

- 可以写：本文完整模型在 VisDrone val/test 上分别达到 `0.2961/0.2337` mAP50–95，在收录的 CCF A/B 正式论文结果中处于可竞争区间。
- 可以写：在明确 val 的结果里，本文高于 TPH-YOLOv5-x+UGS、UAV-DETR-EV2、标准 RT-DETR-R50、QueryDet、ClusDet 和多项 YOLO 基线的报告值。
- 可以写：本文与 640-val 的 DM-EFS（`0.2971`）和 UAV-DETR-R18（`0.2980`）非常接近。
- 可以写：本文在 640-val 下与 IJCAI 2025 RAFDE（`0.3000`）相差 `0.0039` mAP，展示了 DETR 路线的竞争性；同时本文 AP50=`0.4898`，略高于 RAFDE 的 `0.4850`。
- 可以写：同会 ResBiDet 的正式摘要报告 VisDrone2019 AP50=`0.387`，低于本文 `0.4898`；必须同时说明其 split、精确输入和 mAP50–95 尚未从可访问正文核实。
- 可以写：VARDet 是 ICASSP 2026 的同任务直接竞品，但其 `0.3650` 来自 ResNet-50、1333×800 的统一重实现协议，和本文 640 协议非严格可比。
- 不可以写：本文优于所有 A/B 会方法、达到 SOTA，或把不同协议的绝对差称为模块涨点。
- 不可以把 split=`not_reported` 的 AAAI/ICME 行并入 val/test 排名。
- 不可以把不同硬件或不完整测速协议的 FPS 直接排序。

机器可读来源：[`external_visdrone_comparison.json`](external_visdrone_comparison.json)；平铺表：[`external_visdrone_comparison.csv`](external_visdrone_comparison.csv)；证据绑定：[`../evidence/source_manifest.json`](../evidence/source_manifest.json)。

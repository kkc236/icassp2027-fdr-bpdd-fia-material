# VisDrone 结果汇总（论文写作版）

本页是论文结果的统一入口。正式核心结果、FIA standalone 消融和三模块 P3-only 观察按证据等级分开，val/test 不混写。

## 1. 正式核心结果

论文 A–E 主消融表以 [val 主消融表](MAIN_TABLE_ZH.md) 为准。E 行采用与终端截图对应的四位小数文本记录：`P=0.5693、R=0.4991、AP50=0.4898、AP75=0.3042、mAP=0.2961、+0.384 pp`。checkpoint 的 `0.29618/+0.3922 pp` 是另一条补充正向记录，不用于替换该行 P/R。

### val

| 编号 | 模型 | FDR | BPDD | FIA | Precision | Recall | AP50 | AP75 | mAP50–95 | 模块增量 |
|---|---|:---:|:---:|:---:|---:|---:|---:|---:|---:|---:|
| A | RT-DETR-L Baseline | — | — | — | 0.46761 | 0.41731 | 0.38663 | 0.21302 | 0.21911 | — |
| B | RT-DETR-L + FDR | ✓ | — | — | 0.56911 | 0.49278 | 0.48468 | 0.29253 | 0.28966 | +7.055 pp vs A |
| C | RT-DETR-L + FDR + BPDD | ✓ | ✓ | — | 0.57063 | 0.49446 | 0.48641 | 0.29810 | 0.29226 | +0.260 pp vs B |
| D | RT-DETR-L + FDR + FIA | ✓ | — | ✓ | 0.57752 | 0.49089 | 0.48631 | 0.29972 | 0.29494 | +0.528 pp vs B |
| E | RT-DETR-L + FDR + BPDD + FIA | ✓ | ✓ | ✓ | 0.5693 | 0.4991 | 0.4898 | 0.3042 | 0.2961 | +0.384 pp vs C |

FDR 相对 baseline 的 strict val mAP50–95 提升为 `+7.055 pp`。C、D、E 的增量分别以表中标明的 B、B、C 为参照；它们是已登记结果之间的算术差，不表述为严格配对因果增益。C 行 `RT-DETR-L+FDR+BPDD` 的底层精确 mAP50–95 为 `0.292258`。E 行直接采用四位小数 val 文本记录；checkpoint 内嵌的 `0.29618/+0.3922 pp` 作为另一条补充正向记录保留。

### test

| 编号 | 模型 | FDR | BPDD | FIA | Precision | Recall | AP50 | AP75 | mAP50–95 | 模块增量 |
|---|---|:---:|:---:|:---:|---:|---:|---:|---:|---:|---:|
| A | RT-DETR-L Baseline | — | — | — | 0.41798 | 0.37301 | 0.32221 | 0.17550 | 0.17742 | — |
| B | RT-DETR-L + FDR | ✓ | — | — | 0.50340 | 0.43168 | 0.39834 | 0.22890 | 0.22800 | +5.058 pp vs A |
| C | RT-DETR-L + FDR + BPDD | ✓ | ✓ | — | 0.52267 | 0.42614 | 0.40369 | 0.23265 | 0.23166 | +0.366 pp vs B |
| D | RT-DETR-L + FDR + FIA | ✓ | — | ✓ | 0.51897 | 0.43166 | 0.40744 | 0.23588 | 0.23465 | +0.664 pp vs B |
| E | RT-DETR-L + FDR + BPDD + FIA | ✓ | ✓ | ✓ | 0.5189 | 0.4361 | 0.4081 | 0.2327 | 0.2337 | +0.204 pp vs C |

test 中 A、B、C、D 为已登记 exact 结果；E 来自与截图对应的四位小数文本记录，并已补齐 AP75、F1 和十类明细。E 相对 C 的 `+0.204 pp` 是跨记录算术差，不写成严格配对因果增益。

## 2. FIA standalone 消融

本节直接采用 Release 中 FIA-only 和 FDR+FIA 的 `best.pt`。两份 checkpoint 都是 published cascading 拓扑（`model[23].f=-1`），不是当前三模块采用的 P3-only 拓扑，因此它们是补充兼容性消融，不进入正式核心三行。

### val 独立复评

| 方法 | P | R | F1 | AP50 | AP75 | mAP50–95 | 参照 | ΔmAP |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| FIA-only | 0.479433 | 0.414194 | 0.444432 | 0.385675 | 0.209674 | 0.216795 | baseline | −0.2315 pp |
| FDR+FIA | 0.577524 | 0.490889 | 0.530694 | 0.486314 | 0.299724 | 0.294940 | FDR | +0.5280 pp |

### test 独立复评

test 使用 VisDrone 1,610 images / 75,102 instances，冻结参数为 `imgsz=640`、`batch=8`、`workers=8`、`conf=0.001`、`max_det=300`、`nms/cache/half/rect=False`。

| 方法 | P | R | F1 | AP50 | AP75 | mAP50–95 | 参照 | ΔmAP | 证据 |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|
| FIA-only | 0.424054 | 0.369653 | 0.381864* | 0.325111 | 0.171613 | 0.177176 | baseline | −0.0240 pp | best_checkpoint_independent_test_exact |
| FDR+FIA | 0.518967 | 0.431655 | 0.460654* | 0.407439 | 0.235879 | 0.234645 | FDR | +0.6644 pp | best_checkpoint_independent_test_exact |

星号表示 F1 是 evaluator 输出的逐类别 F1 的均值，不是用总体 P/R 再计算的调和均值。两条 ΔmAP 都是对已登记对照的非严格算术比较。

### test 逐类别结果

| 类别 | FIA-only F1 | FIA-only AP75 | FIA-only mAP | FDR+FIA F1 | FDR+FIA AP75 | FDR+FIA mAP |
|---|---:|---:|---:|---:|---:|---:|
| pedestrian | 0.353405 | 0.046619 | 0.096291 | 0.461861 | 0.100838 | 0.158965 |
| people | 0.262873 | 0.018706 | 0.058687 | 0.377442 | 0.042566 | 0.100748 |
| bicycle | 0.161553 | 0.015816 | 0.036938 | 0.267552 | 0.053241 | 0.081505 |
| car | 0.725355 | 0.488162 | 0.451400 | 0.773051 | 0.569176 | 0.512482 |
| van | 0.398076 | 0.276877 | 0.245607 | 0.461506 | 0.352394 | 0.301729 |
| truck | 0.423384 | 0.247756 | 0.231067 | 0.492812 | 0.331702 | 0.295475 |
| tricycle | 0.258538 | 0.077127 | 0.088664 | 0.338805 | 0.157401 | 0.151794 |
| awning-tricycle | 0.265432 | 0.087845 | 0.095093 | 0.307782 | 0.146100 | 0.131283 |
| bus | 0.578412 | 0.400575 | 0.357926 | 0.622419 | 0.488085 | 0.430524 |
| motor | 0.391613 | 0.056647 | 0.110091 | 0.503315 | 0.117285 | 0.181950 |

精确原始小数及 P/R/AP50 见 [`fia_existing_best_test_results.csv`](fia_existing_best_test_results.csv)。

## 3. 三模块 P3-only 观察

正确 P3-only 的 FDR+BPDD+FIA checkpoint 已确认 `model[23].f=21`。checkpoint 内嵌 best-val 为 P=`0.56996`、R=`0.49848`、AP50=`0.48982`、mAP50–95=`0.29618`；相对当前 FDR+BPDD val 数值为 `+0.3922 pp` 的非严格观察。

用户提供的 val/test 文本记录与旧材料仓归档终端截图逐项对应：

| split | P | R | F1 | AP50 | AP75 | mAP50–95 | ΔmAP vs. FDR+BPDD | 证据 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| val | 0.5693 | 0.4991 | 0.5285 | 0.4898 | 0.3042 | **0.2961** | **+0.384 pp** | user_supplied_text_report_4dp |
| test | 0.5189 | 0.4361 | 0.4634 | 0.4081 | 0.2327 | **0.2337** | **+0.204 pp** | user_supplied_text_report_4dp |

因此三模块在 val/test 上都是正增长。test 覆盖 1,610 images / 75,102 instances；四位小数文本已经补齐 AP75、F1 和十类结果，截图作为三位小数交叉核验。原始文本见 [`../evidence/fdr_bpdd_fia_val.txt`](../evidence/fdr_bpdd_fia_val.txt) 与 [`../evidence/fdr_bpdd_fia_test.txt`](../evidence/fdr_bpdd_fia_test.txt)，结构化明细见 [`fdr_bpdd_fia_text_report_class_results.csv`](fdr_bpdd_fia_text_report_class_results.csv)。

## 4. 论文可用结论

- FDR 是当前最稳定、证据等级最高的主要增益来源。
- BPDD 是论文的主要方法创新，在 FDR 基础上继续提供小幅正向结果，并且只在训练期工作、不增加推理分支。现有 AP75 从 `0.29253` 到 `0.29810`（约 `+0.557 pp`）比总体 mAP 的 `+0.260 pp` 更能提示定位质量改善，但两者仍是跨 authority 算术差，需以唯一新增的严格配对实验升级证据。
- FIA-only 在 val 略低于 baseline，test 基本持平；该负向结果保留在补充消融。FDR+FIA 在 val 和 test 均高于对应 FDR 参照，完整三模块也在两个 split 正增长，因此正文主张限定为“FIA 在 distribution-refined context 下与 FDR 呈正向互补”，不写成“FIA 在任意配置下均稳定提升”。
- 三模块 P3-only 在 val/test 均有正向观察；正文消融使用文本记录 `0.2961（+0.384 pp）` 和 `0.2337（+0.204 pp）`，checkpoint `0.29618` 与终端截图作为互证材料。

完整状态见 [FIA 结果状态](FIA_RESULTS_STATUS_ZH.md)，全部组合和 split 涨点见 [val/test 涨点总对比](SPLIT_GAIN_COMPARISON_ZH.md)，正式主表见 [val 主结果表](MAIN_TABLE_ZH.md)，效率占位与统一测速合同见 [统一复杂度与实时性表](COMPLEXITY_ZH.md)。

## 5. CCF A/B 会 VisDrone 外部位置

已补充 [VisDrone CCF A/B 会外部方法对比](EXTERNAL_VISDRONE_COMPARISON_ZH.md)。正式外部行仅来自 AAAI、CVPR、ICCV、ICASSP、ICRA、ICME、IROS full/regular paper，逐行标出 CCF A/B 等级，并按同 split 的 mAP50–95 分成“综合不高于本文/综合高于本文”；split 或 input 未报告的 AAAI/ICME 行单列为不可排序。期刊和仅预印本来源不进入正式表。

外部数字均为论文报告值，不是本项目复跑值。明确 val 的结果中，本项目三模块 `0.2961` 高于 A 会 TPH-YOLOv5-x+UGS `0.2900`、QueryDet `0.2832`、ClusDet-R50 `0.2670`，也高于 B 会 RT-DETR-R50 `0.2840`、YOLOv8-L `0.2610` 与 HIC-YOLOv5 `0.2595`；它与 A 会 DM-EFS `0.2971`、B 会 UAV-DETR-R18 `0.2980` 最接近。ICASSP 2026 VARDet 报告 `AP50=0.6170、AP75=0.3910、mAP=0.3650`，但使用 ResNet-50、1333×800 的统一重实现协议，与本文 640 协议非严格可比。test 中本项目 `0.2337`，HIC-YOLOv5 为 `0.2085`。这些只用于说明绝对值位置，跨论文不计算严格涨点。AAAI 2025 FBRT-YOLO 论文提供 4090 训练记录和参数相近的 RT-DETR/YOLO 行，但未明确 split/input，因此不进入高低排名，FPS 也不排序。

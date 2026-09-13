# VisDrone 结果汇总（论文写作版）

本页是论文结果的统一入口。正式核心结果、FIA standalone 消融和三模块 P3-only 观察按证据等级分开，val/test 不混写。

## 当前三模块联合主记录（2026-09-12）

原 `RT-DETR-L + FDR + BPDD + FIA` 三模块记录已由新的联合臂替换为：`LRS-GFDR + Capacity-BPDD-v3-Safe + FIA`。该臂完成 VisDrone Formal100（seed0），best 为 epoch 97：P=`0.60482`、R=`0.49693`、AP50=`0.49890`、mAP50–95=`0.30109`；E100 为 P=`0.59526`、R=`0.50472`、AP50=`0.50005`、mAP50–95=`0.30065`。完整曲线、authority、冻结参数和配置见 [`当前联合证据包`](../evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/README.md)。

该新联合臂与历史 AP-FDR A–D 行不构成严格配对，因此不从旧行计算新模块因果增益。旧三模块 val/test 文本、截图和 checkpoint 仅作为 `superseded_history` 保留；论文主结果应优先引用本节和当前联合证据包。

## 0. EQuAL 最新定位方法结果（2026-08-21）

EQuAL seed0 Formal100 已连续完成 100 epochs。使用同一个 best epoch 91 checkpoint（SHA-256 `06c5809af89c9a6b944f8615ac4a92c28322b36db6eb872c73407a58e54c3bca`）完成一次统一 val/test exact 复评：

| split | P | R | F1 | AP50 | AP75 | mAP50–95 | ΔAP75 vs AP-FDR | ΔmAP vs AP-FDR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| val | 0.594055 | 0.488666 | 0.536231 | 0.490477 | **0.301026** | **0.294378** | **+0.850 pp** | **+0.472 pp** |
| test | 0.521576 | 0.428839 | 0.470683 | 0.406246 | **0.235363** | **0.234610** | **+0.646 pp** | **+0.661 pp** |

两个 split 的 AP50、AP75 和 mAP50–95 均正向，EQuAL standalone 采用门槛通过；Recall 略降，不能写成全部指标全面提高。差值以材料仓已登记 AP-FDR authority 为参照，属于同 split、同 evaluator 协议的非严格算术比较，不是 fresh strict pair。

现有 A–E 表及 BPDD/FIA 组合仍属于 AP-FDR 代际，不能改名为 EQuAL 结果。完整系统状态为 `combination_retraining_pending`：先重训 **EQuAL + BPDD**，通过后再重训 **EQuAL + BPDD + FIA**。完整精确数值和逐类结果见 [EQuAL 专页](EQUAL_RESULTS_ZH.md)。

## 1. 正式核心结果

论文 A–E 主消融表以 [val 主消融表](MAIN_TABLE_ZH.md) 为准。E 行采用与终端截图对应的四位小数文本记录：`P=0.5693、R=0.4991、AP50=0.4898、AP75=0.3042、mAP=0.2961、+0.384 pp`。checkpoint 的 `0.29618/+0.3922 pp` 是另一条补充正向记录，不用于替换该行 P/R。

### BPDD 严格配对 best.pt 结果（2026-08-19）

严格配对训练和 `best.pt` 统一 val/test 独立精确复评均已完成。两个实验臂使用同一源码提交 `848f00cb7a40907e3884885ecd5bbd474450758a`、同一 protocol manifest、同一初始状态、`seed=0` 和 100 epochs；复评固定 `imgsz=640`、`batch=8`、`workers=8`、`conf=0.001`、`max_det=300`、`nms/cache/half/rect=False`。

| split / 配置 | best epoch | Precision | Recall | F1 | AP50 | AP75 | mAP50–95 |
|---|---:|---:|---:|---:|---:|---:|---:|
| val FDR | 97 | 0.580168 | 0.480571 | 0.525694 | 0.482261 | 0.296941 | 0.290380 |
| val FDR+BPDD | 93 | 0.578726 | 0.491419 | 0.531511 | 0.486058 | 0.297661 | 0.292770 |
| val BPDD 配对增量 | — | −0.144 pp | **+1.085 pp** | **+0.582 pp** | **+0.380 pp** | **+0.072 pp** | **+0.239 pp** |
| test FDR | 97 | 0.521690 | 0.427194 | 0.469737 | 0.402709 | 0.233129 | 0.231124 |
| test FDR+BPDD | 93 | 0.514256 | 0.433537 | 0.470459 | 0.405614 | 0.235888 | 0.233959 |
| test BPDD 配对增量 | — | −0.743 pp | **+0.634 pp** | **+0.072 pp** | **+0.291 pp** | **+0.276 pp** | **+0.283 pp** |

因此 BPDD 在同 authority、同 seed 的 val 和 test 上均为正增长。尤其 test AP75 提升 `+0.276 pp`，与定位质量改善方向一致。两个 checkpoint 的推理图均为 32,334,278 Params / 103.7 GFLOPs，证明 BPDD 不增加推理参数和 FLOPs。训练 selection 指标 `0.29047/0.29278` 继续作为运行溯源，论文主张使用上述统一 best.pt 精确复评。原始 JSON、完整日志、评估脚本和 SHA-256 已归档在 [`../evidence/bpdd_strict_pair_20260819/best_exact/`](../evidence/bpdd_strict_pair_20260819/best_exact/MANIFEST.sha256)。

下方 A–E 表继续保留用户确认的标准展示口径；其中 C 行是历史 cross-authority 完整指标。严格 BPDD 因果增益只引用本节的新配对表，避免把两套 authority 混成一行。

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

本节采用 fresh P3-only FIA-only `best.pt` 与既有发布版 cascading FDR+FIA `best.pt`。FIA-only 的 raw graph 为：FIA 层 22 `f=-1`（读取上一层 21）、层 23 `f=21`、decoder `[22,25,28]`；checkpoint/source SHA 分别为 `c00cae89aaeb722854f8c845d14507c3598f75d509c2b12a3222b35a004157a6` / `118ad631eff93ad806f85ea47819578e6e00bfc5`。FDR+FIA 的层 23 仍为 `f=-1`，不得标成 P3-only。两条结果都不进入正式核心三行。

### val 独立复评

| 方法 | P | R | F1 | AP50 | AP75 | mAP50–95 | 参照 | ΔmAP |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| FIA-only | 0.487196 | 0.425317 | 0.450944 | 0.398745 | 0.221808 | 0.227056 | canonical baseline `0.21911` | **+0.7946 pp** |
| FDR+FIA | 0.577524 | 0.490889 | 0.530694 | 0.486314 | 0.299724 | 0.294940 | FDR | +0.5280 pp |

### test 独立复评

test 使用 VisDrone 1,610 images / 75,102 instances，冻结参数为 `imgsz=640`、`batch=8`、`workers=8`、`conf=0.001`、`max_det=300`、`nms/cache/half/rect=False`。

| 方法 | P | R | F1 | AP50 | AP75 | mAP50–95 | 参照 | ΔmAP | 证据 |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|
| FIA-only | 0.448259 | 0.377636 | 0.395418 | 0.336642 | 0.182011 | 0.185517 | canonical test baseline `0.177416` | **+0.8101 pp** | best_checkpoint_independent_test_exact |
| FDR+FIA | 0.518967 | 0.431655 | 0.460654 | 0.407439 | 0.235879 | 0.234645 | FDR | +0.6644 pp | best_checkpoint_independent_test_exact |

两行 F1 均为 evaluator 输出的逐类别 F1 均值。fresh FIA-only 的 `+0.8101 pp` 是相对 protocol-comparable canonical test baseline 的同 split 算术差；不得跨 val/test 推导涨点。FDR+FIA 的 ΔmAP 是对已登记 FDR test 的非严格算术比较。

### FIA standalone test 逐类别结果

| 类别 | FIA-only F1 | FIA-only AP75 | FIA-only mAP | FDR+FIA F1 | FDR+FIA AP75 | FDR+FIA mAP |
|---|---:|---:|---:|---:|---:|---:|
| pedestrian | 0.368394 | 0.058334 | 0.108887 | 0.461861 | 0.100838 | 0.158965 |
| people | 0.276630 | 0.024409 | 0.064112 | 0.377442 | 0.042566 | 0.100748 |
| bicycle | 0.180726 | 0.023857 | 0.046437 | 0.267552 | 0.053241 | 0.081505 |
| car | 0.733265 | 0.501363 | 0.460179 | 0.773051 | 0.569176 | 0.512482 |
| van | 0.411359 | 0.290431 | 0.254385 | 0.461506 | 0.352394 | 0.301729 |
| truck | 0.440219 | 0.270827 | 0.245529 | 0.492812 | 0.331702 | 0.295475 |
| tricycle | 0.296539 | 0.084746 | 0.098131 | 0.338805 | 0.157401 | 0.151794 |
| awning-tricycle | 0.257455 | 0.093611 | 0.092398 | 0.307782 | 0.146100 | 0.131283 |
| bus | 0.577443 | 0.408632 | 0.367311 | 0.622419 | 0.488085 | 0.430524 |
| motor | 0.412149 | 0.063903 | 0.117805 | 0.503315 | 0.117285 | 0.181950 |

fresh FIA-only 的逐类数据直接来自本次 [`exact test JSON`](../evidence/fia_p3_only_20260819/fia-only-p3-test.json)，没有复用旧 cascading checkpoint。两臂完整精确小数及 P/R/AP50 见 [`fia_existing_best_test_results.csv`](fia_existing_best_test_results.csv)；使用时必须按 checkpoint SHA 核对。

## 3. 历史三模块 P3-only 观察（已被当前联合替换）

正确 P3-only 的 FDR+BPDD+FIA checkpoint 已确认 `model[23].f=21`。checkpoint 内嵌 best-val 为 P=`0.56996`、R=`0.49848`、AP50=`0.48982`、mAP50–95=`0.29618`；相对当前 FDR+BPDD val 数值为 `+0.3922 pp` 的非严格观察。

用户提供的 val/test 文本记录与旧材料仓归档终端截图逐项对应：

| split | P | R | F1 | AP50 | AP75 | mAP50–95 | ΔmAP vs. FDR+BPDD | 证据 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| val | 0.5693 | 0.4991 | 0.5285 | 0.4898 | 0.3042 | **0.2961** | **+0.384 pp** | user_supplied_text_report_4dp |
| test | 0.5189 | 0.4361 | 0.4634 | 0.4081 | 0.2327 | **0.2337** | **+0.204 pp** | user_supplied_text_report_4dp |

因此三模块在 val/test 上都是正增长。test 覆盖 1,610 images / 75,102 instances；四位小数文本已经补齐 AP75、F1 和十类结果，截图作为三位小数交叉核验。原始文本见 [`../evidence/fdr_bpdd_fia_val.txt`](../evidence/fdr_bpdd_fia_val.txt) 与 [`../evidence/fdr_bpdd_fia_test.txt`](../evidence/fdr_bpdd_fia_test.txt)，结构化明细见 [`fdr_bpdd_fia_text_report_class_results.csv`](fdr_bpdd_fia_text_report_class_results.csv)。

## 4. 统一复杂度与实时性

在同一 NVIDIA GeForce RTX 4090、`imgsz=640`、`batch=1`、FP32 端到端协议下，Baseline、FDR、FDR+BPDD、FDR+BPDD+FIA 分别为 `28.85/25.73/25.77/25.21 FPS`，中位延迟为 `34.66/38.86/38.80/39.66 ms`。

严格配对 FDR 与 FDR+BPDD 的原始架构均为 `33,156,614 Params / 108.229 GFLOPs`，峰值显存同为 `363.98 MiB`；两者中位延迟仅差 `−0.085 ms`，属于测量波动。这给出直接证据：BPDD 不增加推理分支或可测开销。相对 FDR+BPDD，FIA 增加 `301,476 Params（+0.91%）`、`3.419 GFLOPs（+3.16%）` 和 `0.861 ms（+2.22%）` 中位延迟，三模块仍保持 `25.21 FPS`。完整表及 1,500 个原始样本见 [统一复杂度与实时性结果](COMPLEXITY_ZH.md)。

## 5. 论文可用结论

- EQuAL 已在 standalone val/test 的 mAP 与 AP75 上同时超过登记 AP-FDR，成为当前优先定位方案；组合链尚未重训，因此最终论文系统仍保留“待组合验证”状态。
- 原 AP-FDR 仍是现有 BPDD/FIA 组合证据的定位底座，在 EQuAL 组合完成前不能从 A–E 表删除或把旧权重改名。
- AP-FDR 是论文的第一项方法创新，其 localization-only 结构、stock-head-informed preliminary 分支、normal/DN 匹配一致监督和公平初始化合同共同取得相对 baseline 的大幅定位增益。BPDD 是第二项跨层优化创新，在 AP-FDR 上继续提供小幅稳定正增益，并且只在训练期工作、不增加推理分支。严格 best.pt 配对复评确认 val/test mAP50–95 分别 `+0.239/+0.283 pp`，AP75 分别 `+0.072/+0.276 pp`；历史 `+0.260 pp/+0.557 pp` 只保留为 cross-authority 背景观察。
- fresh P3-only FIA-only 在 val mAP50–95 上相对 canonical baseline `0.21911` 提高 `+0.7946 pp`；test mAP50–95=`0.1855174641`，相对 protocol-comparable canonical test baseline `0.1774164317` 为 `+0.8101 pp`。两个差值均限于各自 split。旧 FIA-only cascading 负向结果已 superseded。FDR+FIA 和完整三模块继续作为不同 topology/authority 下的正向兼容性观察。
- 三模块 P3-only 在 val/test 均有正向观察；正文消融使用文本记录 `0.2961（+0.384 pp）` 和 `0.2337（+0.204 pp）`，checkpoint `0.29618` 与终端截图作为互证材料。

完整状态见 [FIA 结果状态](FIA_RESULTS_STATUS_ZH.md)，全部组合和 split 涨点见 [val/test 涨点总对比](SPLIT_GAIN_COMPARISON_ZH.md)，正式主表见 [val 主结果表](MAIN_TABLE_ZH.md)，效率实测结果见 [统一复杂度与实时性表](COMPLEXITY_ZH.md)。

## 6. CCF A/B 会 VisDrone 外部位置

已补充 [VisDrone CCF A/B 会外部方法对比](EXTERNAL_VISDRONE_COMPARISON_ZH.md)。正式外部行仅来自 AAAI、CVPR、ICCV、IJCAI、ICASSP、ICRA、ICME、IROS full/regular paper，逐行标出 CCF A/B 等级，并按同 split 的 mAP50–95 分成“综合不高于本文/综合高于本文”；split、input 或 mAP50–95 未报告的行单列为不可排序。期刊和仅预印本来源不进入正式表。

外部数字均为论文报告值，不是本项目复跑值。明确 val 的结果中，本项目三模块 `0.2961` 高于 A 会 TPH-YOLOv5-x+UGS `0.2900`、QueryDet `0.2832`、ClusDet-R50 `0.2670`，也高于 B 会 UAV-DETR-EV2 `0.2870`、RT-DETR-R50 `0.2840`；它与 A 会 DM-EFS `0.2971`、B 会 UAV-DETR-R18 `0.2980` 和 A 会 RAFDE `0.3000` 构成最接近的上下界。RAFDE 在 640 下报告 AP50=`0.4850`、mAP=`0.3000`；本文 AP50=`0.4898` 略高、mAP 略低。ICASSP 2026 ResBiDet 的 IEEE 摘要报告 VisDrone2019 AP50=`0.387`，低于本文 `0.4898`，但其 split、精确双分辨率输入与 mAP50–95 未公开在可访问摘要中。VARDet 报告 `AP50=0.6170、AP75=0.3910、mAP=0.3650`，但使用 ResNet-50、1333×800 的统一重实现协议，与本文 640 协议非严格可比。test 中本项目 `0.2337`，HIC-YOLOv5 为 `0.2085`。这些只用于说明绝对值位置，跨论文不计算严格涨点。

# FDR、BPDD、FIA 的 val/test 涨点总对比

> 当前三模块联合主记录已切换为 `LRS-GFDR + Capacity-BPDD-v3-Safe + FIA`（VisDrone val best E97 mAP50–95=`0.30109`）。最新 BPDD-only Formal100 已完成（best E80=`0.29277`），固定 test 独立评估 mAP@300=`0.24111`。本页中旧 `FDR+BPDD+FIA` 数值仍作为历史 authority 快照保存，不能替代当前联合记录或与其拼接计算增量。

## 证据状态

正式核心表保留 RT-DETR-L、RT-DETR-L+FDR 和 RT-DETR-L+FDR+BPDD。fresh P3-only FIA-only 与既有 cascading FDR+FIA `best.pt` 均已完成冻结 evaluator 独立 exact val/test。正确 P3-only 三模块已有与终端截图逐项吻合的四位小数文本结果：val mAP50–95=`0.2961`，test mAP50–95=`0.2337`，两者均为正增长；checkpoint 的 val `0.29618` 和终端截图作为交叉印证。

新增 BPDD 严格配对已全部完成：同 authority、同 seed、同 evaluator 的 best.pt 复评中，BPDD 在 val/test 的 mAP50–95 分别提高 **+0.239/+0.283 pp**，AP75 分别提高 **+0.072/+0.276 pp**。下方标准总体表仍保留既有展示口径，严格配对完整结果单列如下。

### 最新 Capacity-BPDD-v3-Safe 训练观测

最新 `LRS-GFDR + Capacity-BPDD-v3-Safe` Formal100 的验证曲线在 E80 达到 mAP50–95=`0.29277`，E100 为 `0.28939`；固定 test 独立评估 mAP50–95@300=`0.24111`、@100=`0.24079`。它仍不升级为新的严格配对增量。原始 CSV、args、权重 SHA-256 和 test 报告见 [`当前联合证据包`](../evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/README.md)。

### 历史 EQuAL standalone 结果

| split | P | R | F1 | AP50 | AP75 | mAP50–95 | ΔmAP vs 登记 AP-FDR |
|---|---:|---:|---:|---:|---:|---:|---:|
| val | 0.594055 | 0.488666 | 0.536231 | 0.490477 | 0.301026 | **0.294378** | **+0.472 pp** |
| test | 0.521576 | 0.428839 | 0.470683 | 0.406246 | 0.235363 | **0.234610** | **+0.661 pp** |

EQuAL 在两个 split 的 AP75 与 mAP 上同向提高，standalone 门槛通过；它现作为历史/外部候选保留，不替换当前 LRS-GFDR/Capacity/FIA 联合主结果。差值为非 fresh-paired 算术比较。

### BPDD 严格配对 best.pt 精确结果

| split / 配置 | P | R | F1 | AP50 | AP75 | mAP50–95 |
|---|---:|---:|---:|---:|---:|---:|
| val FDR | 0.580168 | 0.480571 | 0.525694 | 0.482261 | 0.296941 | 0.290380 |
| val FDR+BPDD | 0.578726 | 0.491419 | 0.531511 | 0.486058 | 0.297661 | 0.292770 |
| val 配对差 | −0.144 pp | +1.085 pp | +0.582 pp | +0.380 pp | **+0.072 pp** | **+0.239 pp** |
| test FDR | 0.521690 | 0.427194 | 0.469737 | 0.402709 | 0.233129 | 0.231124 |
| test FDR+BPDD | 0.514256 | 0.433537 | 0.470459 | 0.405614 | 0.235888 | 0.233959 |
| test 配对差 | −0.743 pp | +0.634 pp | +0.072 pp | +0.291 pp | **+0.276 pp** | **+0.283 pp** |

## 组合覆盖状态

| FDR | BPDD | FIA | 模型 | val | test | 状态 |
|---:|---:|---:|---|---|---|---|
| 0 | 0 | 0 | RT-DETR-L | exact | exact | 已完成 |
| 1 | 0 | 0 | RT-DETR-L+FDR | exact | exact | 已完成 |
| 0 | 1 | 0 | RT-DETR-L+BPDD | — | — | 结构无效：BPDD 必须依赖 FDR |
| 0 | 0 | 1 | RT-DETR-L+FIA | exact best-val | exact best-test | fresh P3-only best；val 相对 canonical baseline `+0.7946 pp` |
| 1 | 1 | 0 | RT-DETR-L+FDR+BPDD | exact | exact | 已完成 |
| 1 | 0 | 1 | RT-DETR-L+FDR+FIA | exact best-val | exact best-test | 现有 best 直接复评；val 正增益 |
| 0 | 1 | 1 | RT-DETR-L+BPDD+FIA | — | — | 结构无效：BPDD 必须依赖 FDR |
| 1 | 1 | 1 | RT-DETR-L+FDR+BPDD+FIA | 四位小数 val 正增长 | 四位小数 test 正增长 | 正确 P3-only；P/R/F1/AP50/AP75/mAP 与十类结果齐全 |

## val 总体结果

| 方法 | P | R | F1 | AP50 | AP75 | mAP50–95 | 相对上一有效行 ΔmAP | 证据 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| RT-DETR-L | 0.467610 | 0.417310 | 0.436570 | 0.386630 | 0.213020 | 0.219110 | — | strict |
| +FDR | 0.569113 | 0.492777 | 0.524840 | 0.484684 | 0.292526 | 0.289660 | +7.055 pp | strict |
| +FDR+BPDD | 0.570634 | 0.494464 | 0.529825* | 0.486407 | 0.298096 | 0.292258 | +0.260 pp | cross_authority_exact |

星号表示 F1 由聚合 P/R 计算。本表 BPDD 相对 FDR 的 `+0.260 pp` 是历史跨 authority 算术差；新的同 authority 配对 val mAP/AP75 增益为 `+0.239/+0.072 pp`，以本页上方严格配对表为准，不与历史行拼接。

| 增量 | ΔP | ΔR | ΔF1 | ΔAP50 | ΔAP75 | ΔmAP50–95 |
|---|---:|---:|---:|---:|---:|---:|
| FDR − Baseline | +10.150 | +7.547 | +8.827 | +9.805 | +7.951 | +7.055 |
| BPDD − FDR | +0.152 | +0.169 | 不跨定义比较 | +0.172 | +0.557 | +0.260 |

## test 总体结果

| 方法 | P | R | F1 | AP50 | AP75 | mAP50–95 | 相对上一有效行 ΔmAP | 证据 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| RT-DETR-L | 0.417978 | 0.373013 | 0.394218 | 0.322208 | 0.175503 | 0.177416 | — | exact |
| +FDR | 0.503401 | 0.431677 | 0.464788 | 0.398340 | 0.228903 | 0.228001 | +5.058 pp | exact |
| +FDR+BPDD | 0.522672 | 0.426137 | 0.469494 | 0.403688 | 0.232647 | 0.231659 | +0.366 pp | exact |

| 增量 | ΔP | ΔR | ΔF1 | ΔAP50 | ΔAP75 | ΔmAP50–95 |
|---|---:|---:|---:|---:|---:|---:|
| FDR − Baseline | +8.542 | +5.866 | +7.057 | +7.613 | +5.340 | +5.058 |
| BPDD − FDR | +1.927 | −0.554 | +0.471 | +0.535 | +0.374 | +0.366 |

## FIA standalone best.pt 消融

### val（独立复评，精确）

| 方法 | P | R | F1 | AP50 | AP75 | mAP50–95 | 参照 | ΔmAP |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| FIA-only | 0.487196 | 0.425317 | 0.450944 | 0.398745 | 0.221808 | 0.227056 | canonical baseline `0.21911` | **+0.7946 pp** |
| FDR+FIA | 0.577524 | 0.490889 | 0.530694 | 0.486314 | 0.299724 | 0.294940 | FDR | +0.528 pp |

### test（best.pt 独立复评，exact evaluator；表内展示到 6 位小数）

| 方法 | P | R | F1 | AP50 | AP75 | mAP50–95 | 参照 | ΔmAP |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| FIA-only | 0.448259 | 0.377636 | 0.395418 | 0.336642 | 0.182011 | 0.185517 | canonical test baseline `0.177416` | **+0.8101 pp** |
| FDR+FIA | 0.518967 | 0.431655 | 0.460654 | 0.407439 | 0.235879 | 0.234645 | FDR | +0.6644 pp |

两行 F1 均为 evaluator 逐类别 F1 均值，fresh FIA-only 逐类结果来自新 checkpoint 的 exact JSON。其 `+0.8101 pp` 是相对 protocol-comparable canonical test baseline 的同 split 算术差；不得跨 val/test 推导涨点。FDR+FIA test 差值是跨既有 authority 的算术观察，不是 strict paired 因果增益。

## 三模块 P3-only 四位小数结果

| 方法 | P | R | F1 | AP50 | AP75 | mAP50–95 | 相对当前 BPDD val | 证据 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| FDR+BPDD+FIA | 0.5693 | 0.4991 | 0.5285 | 0.4898 | 0.3042 | 0.2961 | +0.384 pp | `user_supplied_text_report_4dp` |

| split | P | R | F1 | AP50 | AP75 | mAP50–95 | 相对 FDR+BPDD | 证据 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| test | 0.5189 | 0.4361 | 0.4634 | 0.4081 | 0.2327 | 0.2337 | +0.204 pp | `user_supplied_text_report_4dp` |

三模块 val/test 均为正增长。四位小数文本直接给出 AP75、F1 和十类结果，不再反推；checkpoint 内嵌 best-val `0.29618` 与终端截图的三位小数显示仅作互证。

## FIA 使用边界

- FIA-only 当前行来自 fresh P3-only `best.pt`：层 22 `f=-1`（上一层 21）、层 23 `f=21`、decoder `[22,25,28]`。旧 FIA-only cascading 行已 superseded。
- FDR+FIA 仍来自 Release 既有 cascading `best.pt`，不得标成 P3-only。
- val 与 test 均为统一 evaluator 的精确独立复评，必须按 split 分开报告和比较。
- FIA-only 在 val/test 分别只相对 protocol-comparable canonical baseline 陈述 `+0.7946/+0.8101 pp`，不得跨 split 比较。FDR+FIA 只相对 FDR 陈述，三模块只相对 FDR+BPDD 陈述。
- 三模块可作为四位小数正向消融结果；由于文本未携带完整运行身份，差值按结果间算术比较书写，不扩写为严格配对因果效应。

状态入口：[FIA 结果状态](FIA_RESULTS_STATUS_ZH.md)。既有 [`fia_existing_best_test_results.csv`](fia_existing_best_test_results.csv) 必须按 checkpoint SHA 核对；旧 FIA-only 行仅为历史，不能与 fresh checkpoint 拼接逐类结果。三模块原始记录见 [`val 文本`](../evidence/fdr_bpdd_fia_val.txt)、[`test 文本`](../evidence/fdr_bpdd_fia_test.txt)及其[结构化总体/逐类表](fdr_bpdd_fia_text_report_class_results.csv)。

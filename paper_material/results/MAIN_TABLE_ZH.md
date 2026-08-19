# VisDrone val 主消融表

论文主消融表固定使用以下 A–E 顺序。术语统一为 `BPDD`；E 行采用与标准截图对应的四位小数 val 文本记录，并补齐 F1、AP75 和逐类别证据。

| 编号 | 模型 | FDR | BPDD | FIA | Precision | Recall | AP50 | AP75 | mAP50–95 | 相对上一有效配置 |
|---|---|:---:|:---:|:---:|---:|---:|---:|---:|---:|---|
| A | RT-DETR-L Baseline | — | — | — | 0.46761 | 0.41731 | 0.38663 | 0.21302 | 0.21911 | — |
| B | RT-DETR-L + FDR | ✓ | — | — | 0.56911 | 0.49278 | 0.48468 | 0.29253 | 0.28966 | +7.055 pp |
| C | RT-DETR-L + FDR + BPDD | ✓ | ✓ | — | 0.57063 | 0.49446 | 0.48641 | 0.29810 | 0.29226 | +0.260 pp |
| D | RT-DETR-L + FDR + FIA | ✓ | — | ✓ | 0.57752 | 0.49089 | 0.48631 | 0.29972 | 0.29494 | +0.528 pp |
| E | RT-DETR-L + FDR + BPDD + FIA | ✓ | ✓ | ✓ | 0.5693 | 0.4991 | 0.4898 | 0.3042 | 0.2961 | +0.384 pp |

证据等级：A/B 为 `strict`；C 为 `cross_authority_exact`；D 为 `best_checkpoint_independent_val_exact`；E 为 `user_supplied_text_report_4dp`。D 行及其 `+0.528 pp` 不升级为严格配对；E 行文本记录与归档终端截图逐项吻合，截图只是三位小数显示。checkpoint 内的 `0.29618/+0.3922 pp` 仍作为另一条补充正向记录，不替换本行四位小数结果。

## 新 BPDD 严格配对结果

2026-08-19 已在源码提交 `848f00cb7a40907e3884885ecd5bbd474450758a`、同一 protocol/initial state、`seed=0` 和 100 epochs 下完成 FDR/FDR+BPDD 配对训练，并对两个 `best.pt` 完成统一 val/test 独立精确复评。

| split / 配置 | P | R | F1 | AP50 | AP75 | mAP50–95 |
|---|---:|---:|---:|---:|---:|---:|
| val FDR | 0.580168 | 0.480571 | 0.525694 | 0.482261 | 0.296941 | 0.290380 |
| val FDR+BPDD | 0.578726 | 0.491419 | 0.531511 | 0.486058 | 0.297661 | 0.292770 |
| val 配对差 | −0.144 pp | +1.085 pp | +0.582 pp | +0.380 pp | **+0.072 pp** | **+0.239 pp** |
| test FDR | 0.521690 | 0.427194 | 0.469737 | 0.402709 | 0.233129 | 0.231124 |
| test FDR+BPDD | 0.514256 | 0.433537 | 0.470459 | 0.405614 | 0.235888 | 0.233959 |
| test 配对差 | −0.743 pp | +0.634 pp | +0.072 pp | +0.291 pp | **+0.276 pp** | **+0.283 pp** |

该结果把 BPDD 的正增益升级为同 authority、同 seed、同 evaluator 的完整 val/test 配对证据。A–E 标准表保持用户确认口径，严格 BPDD 数字单独采用上表，不与历史 C 行拼接。原始证据见 [`../evidence/bpdd_strict_pair_20260819/strict_pair_summary.json`](../evidence/bpdd_strict_pair_20260819/strict_pair_summary.json)。

## 差值边界

A–E 标准展示表保持既有口径；+FDR 相对 RT-DETR-L 的严格差值如下，新 BPDD 严格差值见上节：

| 指标 | 绝对差 | 百分点差 |
|---|---:|---:|
| Precision | +0.10150 | +10.150 pp |
| Recall | +0.07547 | +7.547 pp |
| AP50 | +0.09805 | +9.805 pp |
| AP75 | +0.07951 | +7.951 pp |
| mAP50–95 | +0.07055 | +7.055 pp |

+FDR+BPDD 与 +FDR 的已展示数值算术差依次为 Precision +0.0015236342、Recall +0.0016841371、AP50 +0.0017274914、AP75 +0.0055656482、mAP50–95 +0.0025978696。这些只可称“跨 authority 算术差”，不能归因为严格配对的 BPDD 收益。

## FIA 行状态

- FIA-only：采用 fresh P3-only `best.pt` 并完成冻结 evaluator 的独立 exact val/test。raw graph 为层 22 `f=-1`（上一层 21）、层 23 `f=21`、decoder `[22,25,28]`；checkpoint/source SHA 为 `c00cae89aaeb722854f8c845d14507c3598f75d509c2b12a3222b35a004157a6` / `118ad631eff93ad806f85ea47819578e6e00bfc5`。
- FDR+FIA：继续采用 Release 既有 cascading `best.pt`；D 行的 topology 不变，不能称为 P3-only。
- D 行直接登记 FDR+FIA best.pt 的 exact independent val：`P=0.57752、R=0.49089、AP50=0.48631、AP75=0.29972、mAP=0.29494`；相对 B 行的 `+0.528 pp` 是非严格配对算术差。
- FDR+BPDD+FIA：四位小数 val 为 P=0.5693、R=0.4991、F1=0.5285、AP50=0.4898、AP75=0.3042、mAP50–95=0.2961，相对 BPDD val 为 +0.384 pp。
- 同一三模块 test 为 P=0.5189、R=0.4361、F1=0.4634、AP50=0.4081、AP75=0.2327、mAP50–95=0.2337，相对 BPDD test 为 +0.204 pp；val/test 均为正增长。文本记录和截图互证，但差值仍不写成严格配对 FIA 因果增益。

### 现有 best.pt standalone 消融（独立 val）

| 方法 | P | R | AP50 | AP75 | mAP50–95 | 参照 | ΔmAP | 证据 |
|---|---:|---:|---:|---:|---:|---|---:|---|
| RT-DETR-L+FIA | 0.487196 | 0.425317 | 0.398745 | 0.221808 | 0.227056 | canonical RT-DETR-L `0.21911` | **+0.7946 pp** | fresh P3-only best checkpoint independent val exact |
| RT-DETR-L+FDR+FIA | 0.577524 | 0.490889 | 0.486314 | 0.299724 | 0.294940 | RT-DETR-L+FDR | +0.528 pp | best checkpoint independent val exact |

这里的差值是当前登记对照的同 split 算术差，不是严格配对因果增益。fresh P3-only FIA-only 与既有 cascading FDR+FIA 在各自 val 参照下均为正向；两者的 topology/authority 不同，不拼成严格因果序列。

independent exact test 中，fresh FIA-only 的 P/R/F1/AP50/AP75/mAP50–95 为 `0.448259/0.377636/0.395418/0.336642/0.182011/0.185517`，相对 protocol-comparable canonical test baseline `0.177416` 为 `+0.8101 pp`；既有 FDR+FIA 的 test mAP50–95/AP75 为 `0.234645/0.235879`。所有差值限于各自 split，完整 test 表见 [论文结果统一汇总](RESULTS_ZH.md)。

最新状态与导入条件见 [FIA 结果状态](FIA_RESULTS_STATUS_ZH.md)。

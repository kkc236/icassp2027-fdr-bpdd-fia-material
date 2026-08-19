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

2026-08-19 已在源码提交 `848f00cb7a40907e3884885ecd5bbd474450758a`、同一 protocol/initial state、`seed=0` 和 100 epochs 下完成 FDR/FDR+BPDD 配对训练：FDR best epoch 97 的 P/R/AP50/mAP 为 `0.58080/0.47923/0.48232/0.29047`；FDR+BPDD best epoch 93 为 `0.57937/0.49101/0.48657/0.29278`。对应增量为 P `−0.143 pp`、R `+1.178 pp`、AP50 `+0.425 pp`、mAP50–95 `+0.231 pp`。

该结果已经把 BPDD 的 mAP 正增益升级为同 authority、同 seed 配对证据。由于训练 CSV 不含 AP75，当前 A–E 表的 C 行暂不替换；AP75 待 best.pt 独立精确复评后，再一次性刷新 C 行全部指标。原始证据见 [`../evidence/bpdd_strict_pair_20260819/strict_pair_summary.json`](../evidence/bpdd_strict_pair_20260819/strict_pair_summary.json)。

## 差值边界

A–E 标准展示表中，当前完整五指标且可直接写为严格差值的是 +FDR 相对 RT-DETR-L；新 BPDD 配对证据另见上节，其 AP75 尚待补齐：

| 指标 | 绝对差 | 百分点差 |
|---|---:|---:|
| Precision | +0.10150 | +10.150 pp |
| Recall | +0.07547 | +7.547 pp |
| AP50 | +0.09805 | +9.805 pp |
| AP75 | +0.07951 | +7.951 pp |
| mAP50–95 | +0.07055 | +7.055 pp |

+FDR+BPDD 与 +FDR 的已展示数值算术差依次为 Precision +0.0015236342、Recall +0.0016841371、AP50 +0.0017274914、AP75 +0.0055656482、mAP50–95 +0.0025978696。这些只可称“跨 authority 算术差”，不能归因为严格配对的 BPDD 收益。

## FIA 行状态

- FIA-only、FDR+FIA：按当前实验决策直接采用 Release 中各自的 `best.pt`，已在冻结 VisDrone evaluator 下完成独立 exact val/test；两者是已发布 cascading standalone 拓扑，不称为 P3-only。
- D 行直接登记 FDR+FIA best.pt 的 exact independent val：`P=0.57752、R=0.49089、AP50=0.48631、AP75=0.29972、mAP=0.29494`；相对 B 行的 `+0.528 pp` 是非严格配对算术差。
- FDR+BPDD+FIA：四位小数 val 为 P=0.5693、R=0.4991、F1=0.5285、AP50=0.4898、AP75=0.3042、mAP50–95=0.2961，相对 BPDD val 为 +0.384 pp。
- 同一三模块 test 为 P=0.5189、R=0.4361、F1=0.4634、AP50=0.4081、AP75=0.2327、mAP50–95=0.2337，相对 BPDD test 为 +0.204 pp；val/test 均为正增长。文本记录和截图互证，但差值仍不写成严格配对 FIA 因果增益。

### 现有 best.pt standalone 消融（独立 val）

| 方法 | P | R | AP50 | AP75 | mAP50–95 | 参照 | ΔmAP | 证据 |
|---|---:|---:|---:|---:|---:|---|---:|---|
| RT-DETR-L+FIA | 0.479433 | 0.414194 | 0.385675 | 0.209674 | 0.216795 | RT-DETR-L | −0.231 pp | best checkpoint independent val exact |
| RT-DETR-L+FDR+FIA | 0.577524 | 0.490889 | 0.486314 | 0.299724 | 0.294940 | RT-DETR-L+FDR | +0.528 pp | best checkpoint independent val exact |

这里的差值是当前登记对照的算术差，不是严格配对因果增益。结论是：FIA-only 略有负增益，FDR+FIA 呈正增益；论文主线使用 FIA 与 FDR 的兼容组合，不以 FIA-only 作为性能主张。

同一批 `best.pt` 的 independent exact test 已补齐 AP75 和逐类别 F1：FIA-only / FDR+FIA 的 test mAP50–95 分别为 `0.177176` / `0.234645`，AP75 分别为 `0.171613` / `0.235879`。完整 test 表和逐类别明细见 [论文结果统一汇总](RESULTS_ZH.md)。

最新状态与导入条件见 [FIA 结果状态](FIA_RESULTS_STATUS_ZH.md)。

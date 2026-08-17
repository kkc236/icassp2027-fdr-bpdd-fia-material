# VisDrone val 主消融表

论文主消融表固定使用以下 A–E 顺序和展示精度。术语统一为 `BPDD`；E 行保持标准截图的舍入口径，精确 checkpoint 数值放在证据说明中。

| 编号 | 模型 | FDR | BPDD | FIA | Precision | Recall | AP50 | AP75 | mAP50–95 | 相对上一有效配置 |
|---|---|:---:|:---:|:---:|---:|---:|---:|---:|---:|---|
| A | RT-DETR-L Baseline | — | — | — | 0.46761 | 0.41731 | 0.38663 | 0.21302 | 0.21911 | — |
| B | RT-DETR-L + FDR | ✓ | — | — | 0.56911 | 0.49278 | 0.48468 | 0.29253 | 0.28966 | +7.055 pp |
| C | RT-DETR-L + FDR + BPDD | ✓ | ✓ | — | 0.57063 | 0.49446 | 0.48641 | 0.29810 | 0.29226 | +0.260 pp |
| D | RT-DETR-L + FDR + FIA | ✓ | — | ✓ | 待整理 | 待整理 | 待整理 | 待整理 | 待整理 | FIA 独立增量 |
| E | RT-DETR-L + FDR + BPDD + FIA | ✓ | ✓ | ✓ | ≈0.569 | ≈0.499 | ≈0.490 | 待补 | ≈0.296 | 约 +0.37 pp |

证据等级：A/B 为 `strict`；C 为 `cross_authority_exact`。E 行直接绑定归档终端截图的 val 面板，因此 P/R/AP50/mAP 和 `约 +0.37 pp` 都能逐项对上标准表。checkpoint 内的 `0.29618/+0.3922 pp` 是另一条补充正向记录，不作为 E 行 P/R 的“精确展开”。

## 差值边界

唯一可直接写为严格配对差值的是 +FDR 相对 RT-DETR-L：

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
- FDR+BPDD+FIA：已定位正确 P3-only checkpoint；best-val 为 P=0.56996、R=0.49848、AP50=0.48982、mAP50–95=0.29618，相对 BPDD val 为 +0.3922 pp。归档终端 test 为 P≈0.519、R≈0.436、AP50≈0.408、mAP50–95≈0.234，相对 BPDD test 为约 +0.234 pp；val/test 均为正增长。
- 三模块 test 为 `terminal_screenshot_rounded`，仍缺 AP75、F1 和冻结 evaluator 独立 exact 复评，所以只在补充消融区登记，不写成严格配对 FIA 因果增益。

### 现有 best.pt standalone 消融（独立 val）

| 方法 | P | R | AP50 | AP75 | mAP50–95 | 参照 | ΔmAP | 证据 |
|---|---:|---:|---:|---:|---:|---|---:|---|
| RT-DETR-L+FIA | 0.479433 | 0.414194 | 0.385675 | 0.209674 | 0.216795 | RT-DETR-L | −0.231 pp | best checkpoint independent val exact |
| RT-DETR-L+FDR+FIA | 0.577524 | 0.490889 | 0.486314 | 0.299724 | 0.294940 | RT-DETR-L+FDR | +0.528 pp | best checkpoint independent val exact |

这里的差值是当前登记对照的算术差，不是严格配对因果增益。结论是：FIA-only 略有负增益，FDR+FIA 呈正增益；论文主线使用 FIA 与 FDR 的兼容组合，不以 FIA-only 作为性能主张。

同一批 `best.pt` 的 independent exact test 已补齐 AP75 和逐类别 F1：FIA-only / FDR+FIA 的 test mAP50–95 分别为 `0.177176` / `0.234645`，AP75 分别为 `0.171613` / `0.235879`。完整 test 表和逐类别明细见 [论文结果统一汇总](RESULTS_ZH.md)。

最新状态与导入条件见 [FIA 结果状态](FIA_RESULTS_STATUS_ZH.md)。

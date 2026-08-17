# FIA 结果状态

## 当前裁定

按当前论文材料决策，FIA-only 与 FDR+FIA 不再等待 standalone 重训，直接采用 GitHub Release `DFR-BDPP-FIA` 中各自已发布的 `best.pt`。两份 checkpoint 已在冻结 evaluator 下完成独立 val 复评，因此可作为现有 best 的 standalone 消融证据。

这两份 checkpoint 的计算图均为发布版 cascading topology：`model[23].f = -1`，不是后续采用的 P3-only topology。报告时必须明确这一身份，不能把两条 standalone 结果写成 P3-only 结果，也不能与三模块 P3-only checkpoint 混称为同一严格拓扑消融系列。

| 实验臂 | checkpoint 与拓扑 | 当前证据状态 |
|---|---|---|
| FIA-only | 发布版 `best.pt`；cascading，`model[23].f=-1` | 已完成独立 exact val；已有 rounded test 截图 |
| FDR+FIA | 发布版 `best.pt`；cascading，`model[23].f=-1` | 已完成独立 exact val；已有 rounded test 截图 |
| FDR+BPDD+FIA | `DFR-BDPP-FIA-best.pt`；P3-only，`model[23].f=21` | checkpoint 内 best-val 正向观察已登记；独立复评待补 |

## 现有 best 的独立 val 结果

统一复评条件为 VisDrone val（548 images / 38,759 instances）、`imgsz=640`、`batch=8`、`conf=0.001`、`max_det=300`、`nms=False`、`half=False`，checkpoint 选择均为 `best.pt`。

| 实验臂 | P | R | F1 | AP50 | AP75 | mAP50–95 | 参考臂 | mAP 差值 |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| FIA-only | 0.4794334980 | 0.4141938299 | 0.4444322382 | 0.3856754513 | 0.2096736112 | 0.2167954534 | RT-DETR-L | -0.2315 pp |
| FDR+FIA | 0.5775238642 | 0.4908887926 | 0.5306938112 | 0.4863140646 | 0.2997239201 | 0.2949403207 | RT-DETR-L+FDR | +0.5280 pp |

上述差值是跨已有 authority 的算术比较，不是 strict paired 因果增益。可据此表述：现有发布版 FIA-only 在 val mAP50–95 上相对登记 baseline 略低；现有发布版 FDR+FIA 相对登记 FDR 为正向观察。

## 发布截图中的 test 结果

test 截图覆盖 1,610 images / 75,102 instances；截图仅提供舍入后的总体数值，未提供 AP75。

| 实验臂 | P | R | F1 | AP50 | AP75 | mAP50–95 | 证据等级 |
|---|---:|---:|---:|---:|---:|---:|---|
| FIA-only | 0.424 | 0.370 | 0.3946 | 0.325 | — | 0.177 | best-checkpoint screenshot, rounded |
| FDR+FIA | 0.519 | 0.431 | 0.4709 | 0.407 | — | 0.235 | best-checkpoint screenshot, rounded |

这些 test 数值可作为截图观察报告，但不得补造 AP75、增加小数位或冒充冻结 evaluator 的 exact 输出；val 与 test 也不得混合计算涨点。

## 拓扑审计与三模块结果

- FIA-only 与 FDR+FIA：FIA 位于层 22，层 23 继续读取 FIA 输出（`model[23].f=-1`），decoder 输入为 `[22,25,28]`，拓扑标签为 `published_cascading_standalone`。
- FDR+BPDD+FIA：FIA 层 22 读取原始 P3（层 21），层 23 同样读取原始 P3（`model[23].f=21`），decoder 输入为 `[22,25,28]`，属于 P3-only。

三模块 P3-only checkpoint 的嵌入式 best-validation 记录保持不变：P=0.56996、R=0.49848、AP50=0.48982、mAP50–95=0.29618；相对当前 FDR+BPDD val 绝对值为 +0.3922 pp 的非严格配对算术观察。AP75、test 与冻结 evaluator 独立复评仍待补。

## 当前引用规则

- FIA-only 与 FDR+FIA 可引用本页的 exact val 和 rounded test 结果，但必须同时注明发布版 cascading topology。
- FIA-only 的 val 结果应如实报告为轻微负向，不能沿用“standalone 均为正增益”的口述结论。
- FDR+FIA 的 +0.5280 pp 和三模块的 +0.3922 pp 都不是 strict paired 因果增益。
- 三模块仍按 P3-only checkpoint 单独登记，不用 standalone cascading 结果替代。

机器可读证据见 [`../evidence/fia_existing_best_evaluation.json`](../evidence/fia_existing_best_evaluation.json)，汇总 CSV 见 [`fia_existing_best_val_results.csv`](fia_existing_best_val_results.csv)。

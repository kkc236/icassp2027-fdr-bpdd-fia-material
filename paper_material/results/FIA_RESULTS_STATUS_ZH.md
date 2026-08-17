# FIA 结果状态

## 当前裁定

按当前论文材料决策，FIA-only 与 FDR+FIA 不再等待 standalone 重训，直接采用 GitHub Release `DFR-BDPP-FIA` 中各自已发布的 `best.pt`。两份 checkpoint 已在冻结 evaluator 下完成独立 exact val 与 exact test 复评，因此可作为现有 best 的 standalone 消融证据。

这两份 checkpoint 的计算图均为发布版 cascading topology：`model[23].f = -1`，不是后续采用的 P3-only topology。报告时必须明确这一身份，不能把两条 standalone 结果写成 P3-only 结果，也不能与三模块 P3-only checkpoint 混称为同一严格拓扑消融系列。

| 实验臂 | checkpoint 与拓扑 | 当前证据状态 |
|---|---|---|
| FIA-only | 发布版 `best.pt`；cascading，`model[23].f=-1` | 已完成独立 exact val 与 exact test |
| FDR+FIA | 发布版 `best.pt`；cascading，`model[23].f=-1` | 已完成独立 exact val 与 exact test |
| FDR+BPDD+FIA | `DFR-BDPP-FIA-best.pt`；P3-only，`model[23].f=21` | best-val 与归档 test 均为正向；test 为截图舍入，独立 exact 待补 |

## 现有 best 的独立 val 结果

统一复评条件为 VisDrone val（548 images / 38,759 instances）、`imgsz=640`、`batch=8`、`conf=0.001`、`max_det=300`、`nms=False`、`half=False`，checkpoint 选择均为 `best.pt`。

| 实验臂 | P | R | F1 | AP50 | AP75 | mAP50–95 | 参考臂 | mAP 差值 |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| FIA-only | 0.4794334980 | 0.4141938299 | 0.4444322382 | 0.3856754513 | 0.2096736112 | 0.2167954534 | RT-DETR-L | -0.2315 pp |
| FDR+FIA | 0.5775238642 | 0.4908887926 | 0.5306938112 | 0.4863140646 | 0.2997239201 | 0.2949403207 | RT-DETR-L+FDR | +0.5280 pp |

上述差值是跨已有 authority 的算术比较，不是 strict paired 因果增益。可据此表述：现有发布版 FIA-only 在 val mAP50–95 上相对登记 baseline 略低；现有发布版 FDR+FIA 相对登记 FDR 为正向观察。

## 现有 best 的独立 test 结果

两份 Release `best.pt` 已在 VisDrone test（1,610 images / 75,102 instances）完成独立复评。协议为 `split=test`、`imgsz=640`、`batch=8`、`workers=8`、`conf=0.001`、`max_det=300`，且 `nms/cache/half/rect=False`。

| 实验臂 | P | R | F1 | AP50 | AP75 | mAP50–95 | 证据等级 |
|---|---:|---:|---:|---:|---:|---:|---|
| FIA-only | 0.4240539939 | 0.3696529891 | 0.3818640322* | 0.3251108597 | 0.1716130742 | 0.1771764568 | best-checkpoint independent test, exact |
| FDR+FIA | 0.5189669713 | 0.4316550673 | 0.4606543770* | 0.4074392933 | 0.2358787301 | 0.2346453866 | best-checkpoint independent test, exact |

星号表示 F1 为 evaluator 逐类别 F1 的均值，不是由总体 P/R 重新计算的调和均值。val 与 test 必须分开报告；将 test 结果与既有 baseline/FDR 对照做出的算术差同样不是 strict paired 因果增益。

## 拓扑审计与三模块结果

- FIA-only 与 FDR+FIA：FIA 位于层 22，层 23 继续读取 FIA 输出（`model[23].f=-1`），decoder 输入为 `[22,25,28]`，拓扑标签为 `published_cascading_standalone`。
- FDR+BPDD+FIA：FIA 层 22 读取原始 P3（层 21），层 23 同样读取原始 P3（`model[23].f=21`），decoder 输入为 `[22,25,28]`，属于 P3-only。

三模块 P3-only checkpoint 的嵌入式 best-validation 为 P=0.56996、R=0.49848、AP50=0.48982、mAP50–95=0.29618；相对 FDR+BPDD val 为 +0.3922 pp。旧材料仓归档的同组三模块终端面板还包含 VisDrone test（1,610 images / 75,102 instances）：P≈0.519、R≈0.436、AP50≈0.408、mAP50–95≈0.234，相对 FDR+BPDD test `0.231659` 为约 +0.234 pp。由此当前三模块在 val/test 上均为正增长。

test 证据等级为 `terminal_screenshot_rounded`，不是 exact JSON；截图没有显示 AP75 和 F1，因此两项继续留空，冻结 evaluator 的独立 exact 复评仍可作为后续增强证据，但不再把“三模块 test 完全缺失”写入材料。

## 当前引用规则

- FIA-only 与 FDR+FIA 可引用本页的独立 exact val/test 结果，但必须同时注明发布版 cascading topology。
- FIA-only 的 val 结果应如实报告为轻微负向，不能沿用“standalone 均为正增益”的口述结论。
- FDR+FIA 的 +0.5280 pp、三模块 val 的 +0.3922 pp 以及三模块 test 的约 +0.234 pp 都是正向算术观察，不表述为 strict paired 因果增益。
- 三模块仍按 P3-only checkpoint 单独登记，不用 standalone cascading 结果替代。

论文写作统一结果页见 [`RESULTS_ZH.md`](RESULTS_ZH.md)。机器可读证据见 [`../evidence/fia_existing_best_evaluation.json`](../evidence/fia_existing_best_evaluation.json)；独立 val 总体 CSV 见 [`fia_existing_best_val_results.csv`](fia_existing_best_val_results.csv)，独立 exact test 总体与逐类 CSV 见 [`fia_existing_best_test_results.csv`](fia_existing_best_test_results.csv)。

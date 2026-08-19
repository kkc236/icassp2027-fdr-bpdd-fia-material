# FIA 结果状态

## 当前裁定

FIA-only 的 fresh P3-only `best.pt` 已在冻结 evaluator 下完成独立 exact val 与 exact test 复评；不存在 FIA-only 结果 pending。FDR+FIA 继续采用 GitHub Release `DFR-BDPP-FIA` 中的既有 cascading `best.pt`，其已登记 exact val/test 保持不变。

fresh FIA-only 的 raw graph 为正确 P3-only：FIA 层 22 的 `f=-1` 指向上一层 21，层 23 显式 `f=21`，decoder 输入 `[22,25,28]`。这与旧 FIA-only cascading 的层 23 `f=-1` 不同。报告时还须明确既有 FDR+FIA 仍是 cascading，不能把不同 topology/authority 混称为严格配对消融系列。

| 实验臂 | checkpoint 与拓扑 | 当前证据状态 |
|---|---|---|
| FIA-only | fresh `best.pt`；P3-only，层 23 `f=21` | 已完成独立 exact val 与 exact test；当前结果 |
| FDR+FIA | 发布版 `best.pt`；cascading，`model[23].f=-1` | 已完成独立 exact val 与 exact test |
| FDR+BPDD+FIA | `DFR-BDPP-FIA-best.pt`；P3-only，`model[23].f=21` | 四位小数 val/test 文本已补齐，并与 checkpoint/截图互证 |

## 当前 best 的独立 val 结果

统一复评条件为 VisDrone val（548 images / 38,759 instances）、`imgsz=640`、`batch=8`、`workers=8`、`conf=0.001`、`max_det=300`，且 `nms/cache/half/rect=False`；checkpoint 选择均为 `best.pt`。

| 实验臂 | P | R | F1 | AP50 | AP75 | mAP50–95 | 参考臂 | mAP 差值 |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| FIA-only | 0.4871962209136635 | 0.42531734343807504 | 0.4509443663180429 | 0.39874518726363956 | 0.2218076018094571 | 0.22705639514425527 | canonical RT-DETR-L `0.21911` | **+0.7946 pp** |
| FDR+FIA | 0.5775238642 | 0.4908887926 | 0.5306938112 | 0.4863140646 | 0.2997239201 | 0.2949403207 | RT-DETR-L+FDR | +0.5280 pp |

上述差值是各自 val split 内的非严格配对算术比较，不是 strict paired 因果增益。可据此表述：fresh P3-only FIA-only 相对 canonical val baseline 提高 `+0.7946 pp`；既有 FDR+FIA 相对登记 FDR 为正向观察。

## 当前 best 的独立 test 结果

两份当前 `best.pt` 已在 VisDrone test（1,610 images / 75,102 instances）完成独立复评。协议为 `split=test`、`imgsz=640`、`batch=8`、`workers=8`、`conf=0.001`、`max_det=300`，且 `nms/cache/half/rect=False`。

| 实验臂 | P | R | F1 | AP50 | AP75 | mAP50–95 | 证据等级 |
|---|---:|---:|---:|---:|---:|---:|---|
| FIA-only | 0.4482592209945812 | 0.377636033342981 | 0.3954178960043504 | 0.33664177054432 | 0.18201140298044138 | 0.18551746406283812 | best-checkpoint independent test, exact |
| FDR+FIA | 0.5189669713 | 0.4316550673 | 0.4606543770 | 0.4074392933 | 0.2358787301 | 0.2346453866 | best-checkpoint independent test, exact |

两行 F1 均为 evaluator 逐类别 F1 均值，逐类结果已归档。fresh FIA-only 相对 protocol-comparable canonical test baseline `0.1774164316787175` 的同 split 算术差为 `+0.8101 pp`，且不是 strict paired 因果增益。val 与 test 必须分开报告，不从两个 split 之间推导涨点。

## 拓扑审计与三模块结果

- fresh FIA-only：FIA 层 22 的 `f=-1` 读取上一层 21，层 23 读取原始 P3（`f=21`），decoder 输入为 `[22,25,28]`，属于 P3-only。checkpoint SHA-256 为 `c00cae89aaeb722854f8c845d14507c3598f75d509c2b12a3222b35a004157a6`，source SHA 为 `118ad631eff93ad806f85ea47819578e6e00bfc5`。
- 既有 FDR+FIA：层 23 继续读取 FIA 输出（`model[23].f=-1`），属于 published cascading topology。
- FDR+BPDD+FIA：FIA 层 22 读取原始 P3（层 21），层 23 同样读取原始 P3（`model[23].f=21`），decoder 输入为 `[22,25,28]`，属于 P3-only。

三模块 P3-only 的四位小数 val 文本为 P=0.5693、R=0.4991、F1=0.5285、AP50=0.4898、AP75=0.3042、mAP50–95=0.2961；相对 FDR+BPDD val 为 +0.384 pp。对应 VisDrone test（1,610 images / 75,102 instances）为 P=0.5189、R=0.4361、F1=0.4634、AP50=0.4081、AP75=0.2327、mAP50–95=0.2337，相对 FDR+BPDD test `0.231659` 为 +0.204 pp。由此当前三模块在 val/test 上均为正增长。

三模块证据等级为 `user_supplied_text_report_4dp`。两份原始文本均给出总体与十类 P/R/F1/AP50/AP75/mAP；旧终端截图的三位小数结果与文本吻合，作为交叉核验。文本未提供超过四位小数的原始 evaluator JSON，因此不宣称更高数值精度。

## 当前引用规则

- FIA-only 可引用本页 fresh P3-only `best.pt` 的 exact val/test；val 可报告相对 canonical baseline `0.21911` 的 `+0.7946 pp`，test 可报告相对 protocol-comparable canonical test baseline `0.1774164317` 的 `+0.8101 pp`。两者均为 split 内非严格配对算术差。
- FDR+FIA 可引用本页的独立 exact val/test，但必须注明其发布版 cascading topology。
- FDR+FIA 的 +0.5280 pp、三模块 val 的 +0.384 pp 以及三模块 test 的 +0.204 pp 都是正向算术观察，不表述为 strict paired 因果增益。
- 三模块仍按 P3-only checkpoint 单独登记，不用 standalone cascading 结果替代。
- 旧 FIA-only cascading checkpoint 与负向数值已 superseded，只能作为明确标注的历史，不得出现在当前表或当前结论中。

论文写作统一结果页见 [`RESULTS_ZH.md`](RESULTS_ZH.md)。既有 standalone 机器可读证据 [`../evidence/fia_existing_best_evaluation.json`](../evidence/fia_existing_best_evaluation.json) 必须按 checkpoint SHA 核对，旧 FIA-only 记录仅为历史；三模块原始记录见 [`../evidence/fdr_bpdd_fia_val.txt`](../evidence/fdr_bpdd_fia_val.txt) 与 [`../evidence/fdr_bpdd_fia_test.txt`](../evidence/fdr_bpdd_fia_test.txt)，总体与逐类 CSV 见 [`fdr_bpdd_fia_text_report_class_results.csv`](fdr_bpdd_fia_text_report_class_results.csv)。

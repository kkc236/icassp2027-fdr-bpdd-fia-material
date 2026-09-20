# FIA 消融 best.pt 结果

## 采用范围

FIA-only 当前采用 fresh P3-only `best.pt`，FDR+FIA 继续采用 GitHub Release [`DFR-BDPP-FIA`](https://github.com/kkc236/uav-detection-baselines/releases/tag/DFR-BDPP-FIA) 中的既有 `best.pt`。两份 checkpoint 均已完成独立 exact val 与 exact test 复评。

fresh FIA-only 是正确 P3-only：raw graph 中 FIA 层 22 的 `f=-1` 表示读取上一层 21，层 23 显式 `f=21`，decoder 输入为 `[22,25,28]`。既有 FDR+FIA checkpoint 仍是 cascading（层 23 `f=-1`）；三模块 checkpoint 也单独登记为 P3-only。三者不能被描述为同一严格拓扑下的完整因果消融。

## 独立 val 精确结果

| 实验臂 | P | R | F1 | AP50 | AP75 | mAP50–95 | mAP 算术差值 | 配对状态 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| FIA-only | 0.4871962209136635 | 0.42531734343807504 | 0.4509443663180429 | 0.39874518726363956 | 0.2218076018094571 | 0.22705639514425527 | vs. canonical baseline `0.21911`: **+0.7946 pp** | 非严格配对 |
| FDR+FIA | 0.5775238642 | 0.4908887926 | 0.5306938112 | 0.4863140646 | 0.2997239201 | 0.2949403207 | vs. FDR +0.5280 pp | 非严格配对 |

证据等级为 `best_checkpoint_independent_val_exact`。fresh FIA-only 相对 canonical baseline 的 `+0.7946 pp` 与 FDR+FIA 相对登记 FDR 的 `+0.5280 pp` 都是同 split 算术比较，不应写成严格配对的模块因果效应。

## 独立 test 精确结果

test 复评覆盖 1,610 images / 75,102 instances，使用 `split=test`、`imgsz=640`、`batch=8`、`workers=8`、`conf=0.001`、`max_det=300`、`nms/cache/half/rect=False`。

| 实验臂 | P | R | F1 | AP50 | AP75 | mAP50–95 | 证据等级 |
|---|---:|---:|---:|---:|---:|---:|---|
| FIA-only | 0.4482592209945812 | 0.377636033342981 | 0.3954178960043504 | 0.33664177054432 | 0.18201140298044138 | 0.18551746406283812 | `best_checkpoint_independent_test_exact` |
| FDR+FIA | 0.5189669713 | 0.4316550673 | 0.4606543770 | 0.4074392933 | 0.2358787301 | 0.2346453866 | `best_checkpoint_independent_test_exact` |

两行 F1 均为 evaluator 逐类别 F1 均值，逐类精确结果已写入机器 CSV。fresh FIA-only 相对 protocol-comparable canonical test baseline `0.1774164316787175` 的同 split 算术差为 `+0.8101 pp`；test 与 val 分开报告，不从 val/test 之间推导涨点。

## checkpoint 与计算图身份

| 实验臂 | 发布资产 | checkpoint SHA-256 | 计算图身份 |
|---|---|---|---|
| FIA-only | fresh `best.pt`；source SHA `118ad631eff93ad806f85ea47819578e6e00bfc5` | `c00cae89aaeb722854f8c845d14507c3598f75d509c2b12a3222b35a004157a6` | P3-only；层 22 `f=-1`（上一层 21），层 23 `f=21`，decoder `[22,25,28]` |
| FDR+FIA | `fdr-fia-seed0-20260815-211203.zip` / `best.pt` | `6f624bbc262e840fa6f416486f3813d8ae1c0d9d8daccfb2997f5da6d427d5f1` | cascading；`model[23].f=-1`；非 P3-only |
| FDR+BPDD+FIA | `DFR-BDPP-FIA-best.pt` | `fd972586e2833a28aa02d04ac9e460b0d7c8cfc4e6e8bcb48da273f0e905593c` | P3-only；`model[23].f=21` |

## 已 superseded 的 FIA-only 历史

此前发布版 FIA-only checkpoint 的 cascading 图（层 23 `f=-1`）以及由它得到的负向 val/test 数值，已被上表 fresh P3-only checkpoint 取代，不得再作为当前 FIA-only 结果。旧机器表若仍含该 checkpoint，只能按 SHA 识别为历史记录。

## 三模块 P3-only 观察

三模块四位小数文本给出的 val 为 P=0.5693、R=0.4991、F1=0.5285、AP50=0.4898、AP75=0.3042、mAP50–95=0.2961，相对 FDR+BPDD val `0.29225786956881444` 为 +0.384 pp；test 为 P=0.5189、R=0.4361、F1=0.4634、AP50=0.4081、AP75=0.2327、mAP50–95=0.2337，相对 FDR+BPDD test `0.2316590644` 为 +0.204 pp。两项均为正增长，证据等级为 `user_supplied_text_report_4dp`。checkpoint 嵌入式 best-validation P=0.56996、R=0.49848、AP50=0.48982、mAP50–95=0.29618，与四位小数文本及归档终端截图相互印证。

既有机器证据 [`../evidence/fia_existing_best_evaluation.json`](../evidence/fia_existing_best_evaluation.json) 与 [`fia_existing_best_test_results.csv`](fia_existing_best_test_results.csv) 必须按 checkpoint SHA 核对；其中旧 FIA-only 行仅作 superseded history，不能支撑上表 fresh checkpoint。三模块见 [`val 原始文本`](../evidence/fdr_bpdd_fia_val.txt)、[`test 原始文本`](../evidence/fdr_bpdd_fia_test.txt)及[总体/逐类 CSV](fdr_bpdd_fia_text_report_class_results.csv)，统一边界见 [`FIA_RESULTS_STATUS_ZH.md`](FIA_RESULTS_STATUS_ZH.md)。

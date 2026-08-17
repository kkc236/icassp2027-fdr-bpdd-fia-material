# FIA 消融发布版结果

## 采用范围

按当前决策，standalone 消融直接采用 GitHub Release [`DFR-BDPP-FIA`](https://github.com/kkc236/uav-detection-baselines/releases/tag/DFR-BDPP-FIA) 中 FIA-only 与 FDR+FIA 各自已发布的 `best.pt`，不再要求重新训练这两个实验臂。两份 best checkpoint 均已完成独立 exact val 与 exact test 复评。

两份 standalone checkpoint 均为发布版 cascading topology（`model[23].f=-1`），不是 P3-only。后续正确的三模块 checkpoint 则为 P3-only（`model[23].f=21`）；三者不能被描述为同一严格拓扑下的完整因果消融。

## 独立 val 精确结果

| 实验臂 | P | R | F1 | AP50 | AP75 | mAP50–95 | mAP 算术差值 | 配对状态 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| FIA-only | 0.4794334980 | 0.4141938299 | 0.4444322382 | 0.3856754513 | 0.2096736112 | 0.2167954534 | vs. baseline -0.2315 pp | 非严格配对 |
| FDR+FIA | 0.5775238642 | 0.4908887926 | 0.5306938112 | 0.4863140646 | 0.2997239201 | 0.2949403207 | vs. FDR +0.5280 pp | 非严格配对 |

证据等级为 `best_checkpoint_independent_val_exact`。FIA-only 的现有 best 在 val mAP50–95 上略低于登记 baseline；FDR+FIA 的现有 best 相对登记 FDR 呈正向观察。差值来自已有结果的算术比较，不应写成严格配对的模块因果效应。

## 独立 test 精确结果

test 复评覆盖 1,610 images / 75,102 instances，使用 `split=test`、`imgsz=640`、`batch=8`、`workers=8`、`conf=0.001`、`max_det=300`、`nms/cache/half/rect=False`。

| 实验臂 | P | R | F1 | AP50 | AP75 | mAP50–95 | 证据等级 |
|---|---:|---:|---:|---:|---:|---:|---|
| FIA-only | 0.4240539939 | 0.3696529891 | 0.3818640322* | 0.3251108597 | 0.1716130742 | 0.1771764568 | `best_checkpoint_independent_test_exact` |
| FDR+FIA | 0.5189669713 | 0.4316550673 | 0.4606543770* | 0.4074392933 | 0.2358787301 | 0.2346453866 | `best_checkpoint_independent_test_exact` |

星号表示 F1 为 evaluator 逐类别 F1 的均值。test 与 val 分开报告；对现有 baseline/FDR 的 test 算术比较不是严格配对的模块因果效应。

## checkpoint 与计算图身份

| 实验臂 | 发布资产 | checkpoint SHA-256 | 计算图身份 |
|---|---|---|---|
| FIA-only | `fia-seed0-20260815-211156.zip` / `best.pt` | `cf7203733c6d7f66ba8708dfda3b8aa6ac5cd8564bc31b68cde7e8513cf211d9` | cascading；`model[23].f=-1`；非 P3-only |
| FDR+FIA | `fdr-fia-seed0-20260815-211203.zip` / `best.pt` | `6f624bbc262e840fa6f416486f3813d8ae1c0d9d8daccfb2997f5da6d427d5f1` | cascading；`model[23].f=-1`；非 P3-only |
| FDR+BPDD+FIA | `DFR-BDPP-FIA-best.pt` | `fd972586e2833a28aa02d04ac9e460b0d7c8cfc4e6e8bcb48da273f0e905593c` | P3-only；`model[23].f=21` |

## 三模块 P3-only 观察

三模块 checkpoint 的嵌入式 best-validation 记录保持为 P=0.56996、R=0.49848、AP50=0.48982、mAP50–95=0.29618。相对 FDR+BPDD val mAP50–95 `0.29225786956881444` 的算术观察为 +0.3922 pp；严格配对状态为否。该 checkpoint 的 AP75、test 与冻结 evaluator 独立复评仍待补，因此与上表两条已独立复评的 standalone val 结果分开呈现。

完整机器证据见 [`../evidence/fia_existing_best_evaluation.json`](../evidence/fia_existing_best_evaluation.json)，independent exact test 总体与逐类机器表见 [`fia_existing_best_test_results.csv`](fia_existing_best_test_results.csv)，统一边界见 [`FIA_RESULTS_STATUS_ZH.md`](FIA_RESULTS_STATUS_ZH.md)。

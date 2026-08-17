# VisDrone 结果汇总（论文写作版）

本页是论文结果的统一入口。正式核心结果、FIA standalone 消融和三模块 P3-only 观察按证据等级分开，val/test 不混写。

## 1. 正式核心结果

### val

| 方法 | P | R | AP50 | AP75 | mAP50–95 | 证据 |
|---|---:|---:|---:|---:|---:|---|
| RT-DETR-L | 0.467610 | 0.417310 | 0.386630 | 0.213020 | 0.219110 | strict |
| RT-DETR-L+FDR | 0.569113 | 0.492777 | 0.484684 | 0.292526 | 0.289660 | strict |
| RT-DETR-L+FDR+BPDD | 0.570634 | 0.494464 | 0.486407 | 0.298096 | 0.292258 | cross_authority_exact |

FDR 相对 baseline 的 strict val mAP50–95 提升为 `+7.055 pp`。FDR+BPDD 相对 FDR 的数值差为 `+0.260 pp`，但两行来自不同 authority，只能称非严格算术差。

### test

| 方法 | P | R | AP50 | AP75 | mAP50–95 | 相对上一有效行 ΔmAP | 证据 |
|---|---:|---:|---:|---:|---:|---:|---|
| RT-DETR-L | 0.417978 | 0.373013 | 0.322208 | 0.175503 | 0.177416 | — | exact_single_arm |
| RT-DETR-L+FDR | 0.503401 | 0.431677 | 0.398340 | 0.228903 | 0.228001 | +5.058 pp | exact_single_arm |
| RT-DETR-L+FDR+BPDD | 0.522672 | 0.426137 | 0.403688 | 0.232647 | 0.231659 | +0.366 pp | cross_authority_exact |

## 2. FIA standalone 消融

本节直接采用 Release 中 FIA-only 和 FDR+FIA 的 `best.pt`。两份 checkpoint 都是 published cascading 拓扑（`model[23].f=-1`），不是当前三模块采用的 P3-only 拓扑，因此它们是补充兼容性消融，不进入正式核心三行。

### val 独立复评

| 方法 | P | R | F1 | AP50 | AP75 | mAP50–95 | 参照 | ΔmAP |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| FIA-only | 0.479433 | 0.414194 | 0.444432 | 0.385675 | 0.209674 | 0.216795 | baseline | −0.2315 pp |
| FDR+FIA | 0.577524 | 0.490889 | 0.530694 | 0.486314 | 0.299724 | 0.294940 | FDR | +0.5280 pp |

### test 独立复评

test 使用 VisDrone 1,610 images / 75,102 instances，冻结参数为 `imgsz=640`、`batch=8`、`workers=8`、`conf=0.001`、`max_det=300`、`nms/cache/half/rect=False`。

| 方法 | P | R | F1 | AP50 | AP75 | mAP50–95 | 参照 | ΔmAP | 证据 |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|
| FIA-only | 0.424054 | 0.369653 | 0.381864* | 0.325111 | 0.171613 | 0.177176 | baseline | −0.0240 pp | best_checkpoint_independent_test_exact |
| FDR+FIA | 0.518967 | 0.431655 | 0.460654* | 0.407439 | 0.235879 | 0.234645 | FDR | +0.6644 pp | best_checkpoint_independent_test_exact |

星号表示 F1 是 evaluator 输出的逐类别 F1 的均值，不是用总体 P/R 再计算的调和均值。两条 ΔmAP 都是对已登记对照的非严格算术比较。

### test 逐类别结果

| 类别 | FIA-only F1 | FIA-only AP75 | FIA-only mAP | FDR+FIA F1 | FDR+FIA AP75 | FDR+FIA mAP |
|---|---:|---:|---:|---:|---:|---:|
| pedestrian | 0.353405 | 0.046619 | 0.096291 | 0.461861 | 0.100838 | 0.158965 |
| people | 0.262873 | 0.018706 | 0.058687 | 0.377442 | 0.042566 | 0.100748 |
| bicycle | 0.161553 | 0.015816 | 0.036938 | 0.267552 | 0.053241 | 0.081505 |
| car | 0.725355 | 0.488162 | 0.451400 | 0.773051 | 0.569176 | 0.512482 |
| van | 0.398076 | 0.276877 | 0.245607 | 0.461506 | 0.352394 | 0.301729 |
| truck | 0.423384 | 0.247756 | 0.231067 | 0.492812 | 0.331702 | 0.295475 |
| tricycle | 0.258538 | 0.077127 | 0.088664 | 0.338805 | 0.157401 | 0.151794 |
| awning-tricycle | 0.265432 | 0.087845 | 0.095093 | 0.307782 | 0.146100 | 0.131283 |
| bus | 0.578412 | 0.400575 | 0.357926 | 0.622419 | 0.488085 | 0.430524 |
| motor | 0.391613 | 0.056647 | 0.110091 | 0.503315 | 0.117285 | 0.181950 |

精确原始小数及 P/R/AP50 见 [`fia_existing_best_test_results.csv`](fia_existing_best_test_results.csv)。

## 3. 三模块 P3-only 观察

正确 P3-only 的 FDR+BPDD+FIA checkpoint 已确认 `model[23].f=21`。checkpoint 内嵌 best-val 为 P=`0.56996`、R=`0.49848`、AP50=`0.48982`、mAP50–95=`0.29618`；相对当前 FDR+BPDD val 数值为 `+0.3922 pp` 的非严格观察。

该 checkpoint 尚未完成冻结 evaluator 独立 val/test 复评，AP75、test、尺度和类别结果仍为空。因此不能把 standalone test 数值填到三模块，也不能把本行写成严格因果增益。

## 4. 论文可用结论

- FDR 是当前最稳定、证据等级最高的主要增益来源。
- BPDD 在 FDR 基础上继续提供小幅正向结果；正式写作中将其表述为训练期渐进分布蒸馏，并保留跨 authority 边界。
- FIA-only 在 val 略低于 baseline，test 基本持平；FDR+FIA 在 val 和 test 均高于对应 FDR 参照，支持“FIA 与 FDR 兼容并呈正向互补”，不支持“FIA 单独稳定提升”。
- 三模块当前只有 P3-only best-val 正向观察，待独立复评后才能进入完整主表。

完整状态见 [FIA 结果状态](FIA_RESULTS_STATUS_ZH.md)，全部组合和 split 涨点见 [val/test 涨点总对比](SPLIT_GAIN_COMPARISON_ZH.md)，正式主表见 [val 主结果表](MAIN_TABLE_ZH.md)。

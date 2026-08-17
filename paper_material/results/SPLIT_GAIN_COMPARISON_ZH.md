# FDR、BPDD、FIA 的 val/test 涨点总对比

## 证据状态

正式核心表保留 RT-DETR-L、RT-DETR-L+FDR 和 RT-DETR-L+FDR+BPDD。standalone FIA 两个已发布 `best.pt` 已完成冻结 evaluator 独立 exact val/test。正确 P3-only 三模块则单独登记：best-val `0.29618` 和归档 test `≈0.234` 均为正增长，其中 test 是终端截图舍入证据。

## 组合覆盖状态

| FDR | BPDD | FIA | 模型 | val | test | 状态 |
|---:|---:|---:|---|---|---|---|
| 0 | 0 | 0 | RT-DETR-L | exact | exact | 已完成 |
| 1 | 0 | 0 | RT-DETR-L+FDR | exact | exact | 已完成 |
| 0 | 1 | 0 | RT-DETR-L+BPDD | — | — | 结构无效：BPDD 必须依赖 FDR |
| 0 | 0 | 1 | RT-DETR-L+FIA | exact best-val | exact best-test | 现有 best 直接复评；val 略有负增益 |
| 1 | 1 | 0 | RT-DETR-L+FDR+BPDD | exact | exact | 已完成 |
| 1 | 0 | 1 | RT-DETR-L+FDR+FIA | exact best-val | exact best-test | 现有 best 直接复评；val 正增益 |
| 0 | 1 | 1 | RT-DETR-L+BPDD+FIA | — | — | 结构无效：BPDD 必须依赖 FDR |
| 1 | 1 | 1 | RT-DETR-L+FDR+BPDD+FIA | best-val 正增长 | test 约 0.234，正增长 | 正确 P3-only；test 截图舍入，AP75/F1 待 exact |

## val 总体结果

| 方法 | P | R | F1 | AP50 | AP75 | mAP50–95 | 相对上一有效行 ΔmAP | 证据 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| RT-DETR-L | 0.467610 | 0.417310 | 0.436570 | 0.386630 | 0.213020 | 0.219110 | — | strict |
| +FDR | 0.569113 | 0.492777 | 0.524840 | 0.484684 | 0.292526 | 0.289660 | +7.055 pp | strict |
| +FDR+BPDD | 0.570634 | 0.494464 | 0.529825* | 0.486407 | 0.298096 | 0.292258 | +0.260 pp | cross_authority_exact |

星号表示 F1 由聚合 P/R 计算。BPDD 相对 FDR 的数值差是跨 authority 算术差，不是严格配对因果增益。

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
| FIA-only | 0.479433 | 0.414194 | 0.444432 | 0.385675 | 0.209674 | 0.216795 | baseline | −0.231 pp |
| FDR+FIA | 0.577524 | 0.490889 | 0.530694 | 0.486314 | 0.299724 | 0.294940 | FDR | +0.528 pp |

### test（best.pt 独立复评，exact evaluator；表内展示到 6 位小数）

| 方法 | P | R | F1 | AP50 | AP75 | mAP50–95 | 参照 | ΔmAP |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| FIA-only | 0.424054 | 0.369653 | 0.381864* | 0.325111 | 0.171613 | 0.177176 | baseline | −0.0240 pp |
| FDR+FIA | 0.518967 | 0.431655 | 0.460654* | 0.407439 | 0.235879 | 0.234645 | FDR | +0.6644 pp |

星号表示 F1 为 evaluator 逐类别 F1 的均值，不是由总体 P/R 重新计算的调和均值。test 对照差值是跨既有 authority 的算术观察，不是 strict paired 因果增益。

## 新三模块 checkpoint 观察

| 方法 | P | R | AP50 | AP75 | mAP50–95 | 相对当前 BPDD val | 状态 |
|---|---:|---:|---:|---:|---:|---:|---|
| FDR+BPDD+FIA | 0.56996 | 0.49848 | 0.48982 | 待补 | 0.29618 | +0.3922 pp | 正确 P3-only checkpoint 的 best-val；独立复评待补 |

| split | P | R | AP50 | AP75 | mAP50–95 | 相对 FDR+BPDD | 证据 |
|---|---:|---:|---:|---:|---:|---:|---|
| test | ≈0.519 | ≈0.436 | ≈0.408 | 未显示 | ≈0.234 | ≈+0.234 pp | `terminal_screenshot_rounded` |

三模块 val/test 均为正增长。val 来自 checkpoint best 记录；test 来自归档终端面板，不是冻结 evaluator 的 exact JSON，因此 AP75、F1 和精确小数不反推。

## FIA 使用边界

- standalone 行来自 Release 现有 `best.pt`；计算图为 cascading，不得标成 P3-only。
- val 与 test 均为统一 evaluator 对 Release `best.pt` 的精确独立复评，但必须按 split 分开报告和比较。
- FIA-only 只相对 baseline 陈述，FDR+FIA 只相对 FDR 陈述，三模块只相对 FDR+BPDD 陈述。
- 新三模块当前可作为正向补充消融；在源码提交、配置、checkpoint、评估命令和结构化 exact 输出全部绑定后，再升级为正式 exact 总体、尺度和类别表。

状态入口：[FIA 结果状态](FIA_RESULTS_STATUS_ZH.md)。机器 JSON/CSV 已同步登记现有 best.pt 的独立 exact val/test；test 总体与 10 类明细见 [`fia_existing_best_test_results.csv`](fia_existing_best_test_results.csv)。

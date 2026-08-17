# FDR、BPDD、FIA 的 val/test 涨点总对比

## 证据状态

正式核心表保留 RT-DETR-L、RT-DETR-L+FDR 和 RT-DETR-L+FDR+BPDD。按当前决策，standalone FIA 两个已发布 `best.pt` 已直接完成冻结 evaluator 独立 val：FIA-only 略低于 baseline，FDR+FIA 高于 FDR。它们属于 published cascading topology，作为补充消融登记，不称为 P3-only。正确 P3-only 三模块 checkpoint 仍作为单独 best-val 观察。

## 组合覆盖状态

| FDR | BPDD | FIA | 模型 | val | test | 状态 |
|---:|---:|---:|---|---|---|---|
| 0 | 0 | 0 | RT-DETR-L | exact | exact | 已完成 |
| 1 | 0 | 0 | RT-DETR-L+FDR | exact | exact | 已完成 |
| 0 | 1 | 0 | RT-DETR-L+BPDD | — | — | 结构无效：BPDD 必须依赖 FDR |
| 0 | 0 | 1 | RT-DETR-L+FIA | exact best-val | rounded screenshot | 现有 best 直接复评；val 略有负增益 |
| 1 | 1 | 0 | RT-DETR-L+FDR+BPDD | exact | exact | 已完成 |
| 1 | 0 | 1 | RT-DETR-L+FDR+FIA | exact best-val | rounded screenshot | 现有 best 直接复评；val 正增益 |
| 0 | 1 | 1 | RT-DETR-L+BPDD+FIA | — | — | 结构无效：BPDD 必须依赖 FDR |
| 1 | 1 | 1 | RT-DETR-L+FDR+BPDD+FIA | best-val 已定位 | 待独立复评 | 正确 P3-only checkpoint 已确认；AP75/test 待补 |

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

### test（Release 截图舍入）

| 方法 | P | R | F1 | AP50 | AP75 | mAP50–95 | 证据 |
|---|---:|---:|---:|---:|---:|---:|---|
| FIA-only | 0.424 | 0.370 | 0.3946* | 0.325 | — | 0.177 | best checkpoint screenshot rounded |
| FDR+FIA | 0.519 | 0.431 | 0.4709* | 0.407 | — | 0.235 | best checkpoint screenshot rounded |

星号表示 F1 由截图中的 P/R 计算。截图未给 AP75，不能推算；test 数值只按显示精度引用。

## 新三模块 checkpoint 观察

| 方法 | P | R | AP50 | AP75 | mAP50–95 | 相对当前 BPDD val | 状态 |
|---|---:|---:|---:|---:|---:|---:|---|
| FDR+BPDD+FIA | 0.56996 | 0.49848 | 0.48982 | 待补 | 0.29618 | +0.3922 pp | 正确 P3-only checkpoint 的 best-val；独立复评待补 |

该行是修改后 FIA 的正向 checkpoint 观察，不是冻结 evaluator 的正式 exact 行，也不是严格配对因果涨点。test、AP75、尺度和类别结果均待补。

## FIA 使用边界

- standalone 行来自 Release 现有 `best.pt`；计算图为 cascading，不得标成 P3-only。
- val 为统一 evaluator 的精确独立复评；test 为截图舍入观察，不能混作同等级 exact 数据。
- FIA-only 只相对 baseline 陈述，FDR+FIA 只相对 FDR 陈述，三模块只相对 FDR+BPDD 陈述。
- 新三模块在源码提交、配置、checkpoint、数据集身份、评估命令以及结构化 val/test 输出全部绑定后，才进入正式总体、尺度和类别表。

状态入口：[FIA 结果状态](FIA_RESULTS_STATUS_ZH.md)。机器 JSON/CSV 已同步登记现有 best.pt 的独立 val 与截图舍入 test 证据。

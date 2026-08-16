# FDR、BPDD、FIA 的 val/test 涨点总对比

## 组合覆盖状态

三模块共有 8 个开关组合，但 BPDD 依赖 FDR 的逐边分布，因此两种不含 FDR 的 BPDD 组合在结构上无效；FIA 单独和 FDR+FIA 尚无完成的 Formal100 checkpoint。

| FDR | BPDD | FIA | 模型 | val | test | 状态 |
|---:|---:|---:|---|---|---|---|
| 0 | 0 | 0 | RT-DETR-L | exact | exact | 已完成 |
| 1 | 0 | 0 | RT-DETR-L+FDR | exact | exact | 已完成 |
| 0 | 1 | 0 | RT-DETR-L+BPDD | — | — | 结构无效：BPDD 必须依赖 FDR |
| 0 | 0 | 1 | RT-DETR-L+FIA | — | — | 未训练 |
| 1 | 1 | 0 | RT-DETR-L+FDR+BPDD | exact | exact | 已完成 |
| 1 | 0 | 1 | RT-DETR-L+FDR+FIA | — | — | 未训练 |
| 0 | 1 | 1 | RT-DETR-L+BPDD+FIA | — | — | 结构无效：BPDD 必须依赖 FDR |
| 1 | 1 | 1 | RT-DETR-L+FDR+BPDD+FIA | exact | 待 exact 补评 | val 已完成；test 服务器暂不可达 |

## val 总体结果

| 方法 | P | R | F1 | AP50 | AP75 | mAP50–95 | 相对上一行 ΔmAP | 证据 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| RT-DETR-L | 0.467610 | 0.417310 | 0.436570 | 0.386630 | 0.213020 | 0.219110 | — | strict |
| +FDR | 0.569113 | 0.492777 | 0.524840 | 0.484684 | 0.292526 | 0.289660 | **+7.055 pp** | strict |
| +FDR+BPDD | 0.570634 | 0.494464 | 0.529825* | 0.486407 | 0.298096 | 0.292258 | **+0.260 pp** | cross_authority_exact |
| +FDR+BPDD+FIA | 0.555762 | 0.498344 | 0.525489* | 0.481241 | 0.295104 | 0.289953 | **−0.231 pp** | exact_single_arm |

`*` BPDD 与三模块行的 F1 是聚合 P/R 的调和均值；前两行是历史评估器报告值，因此 BPDD 相对 FDR 的 F1 不作为正式涨点。后三行增量不是同一新鲜配对训练，只能写“跨 authority/跨运行算术差”。

val 逐步涨点（百分点）：

| 增量 | ΔP | ΔR | ΔF1 | ΔAP50 | ΔAP75 | ΔmAP50–95 |
|---|---:|---:|---:|---:|---:|---:|
| FDR − Baseline | +10.150 | +7.547 | +8.827 | +9.805 | +7.951 | **+7.055** |
| BPDD − FDR | +0.152 | +0.169 | 不跨定义比较 | +0.172 | +0.557 | **+0.260** |
| FIA 三模块 − FDR+BPDD | −1.487 | +0.388 | −0.434 | −0.517 | −0.299 | **−0.231** |

## test 总体结果

| 方法 | P | R | F1 | AP50 | AP75 | mAP50–95 | 相对上一行 ΔmAP | 证据 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| RT-DETR-L | 0.417978 | 0.373013 | 0.394218 | 0.322208 | 0.175503 | 0.177416 | — | exact |
| +FDR | 0.503401 | 0.431677 | 0.464788 | 0.398340 | 0.228903 | 0.228001 | **+5.058 pp** | exact |
| +FDR+BPDD | 0.522672 | 0.426137 | 0.469494 | 0.403688 | 0.232647 | 0.231659 | **+0.366 pp** | exact |
| +FDR+BPDD+FIA | 待补评 | 待补评 | 待补评 | 待补评 | 待补评 | 待补评 | — | exact_evaluation_pending |

test 逐步涨点（百分点）：

| 增量 | ΔP | ΔR | ΔF1 | ΔAP50 | ΔAP75 | ΔmAP50–95 |
|---|---:|---:|---:|---:|---:|---:|
| FDR − Baseline | +8.542 | +5.866 | +7.057 | +7.613 | +5.340 | **+5.058** |
| BPDD − FDR | +1.927 | −0.554 | +0.471 | +0.535 | +0.374 | **+0.366** |

终端截图曾显示三模块 test 约 `P=0.519`、`R=0.436`、`AP50=0.408`、`mAP=0.234`，但没有 checkpoint、命令与精确运行身份，且 AP75 缺失，因此不填入 exact 表，也不计算正式涨点。

## 分尺度 mAP50–95 涨点

| split | 尺度 | FDR − Baseline | BPDD − FDR | FIA 三模块 − FDR+BPDD |
|---|---|---:|---:|---:|
| val | tiny | +5.796 | −0.016 | +0.168 |
| val | small | +7.214 | +0.778 | −0.421 |
| val | medium | +7.131 | +0.036 | −1.122 |
| val | large | +6.786 | −0.923 | +2.917 |
| test | tiny | +4.000 | −0.029 | 待补评 |
| test | small | +6.071 | +0.473 | 待补评 |
| test | medium | +5.019 | −0.281 | 待补评 |
| test | large | +1.639 | −4.075 | 待补评 |

BPDD 的总体正增益主要由 val 的 small、medium 和 test 的 small 尺度支撑；large 样本很少（val 130、test 306），负波动不能单独用于强结论。三模块 val 的 large、tiny 上升，但 small、medium 下降，与总体 `−0.231 pp` 一致地表明 FIA 尚未形成稳定增益证据。

## 十类别 mAP50–95 涨点

| 类别 | val FDR − Base | val BPDD − FDR | val FIA − BPDD | test FDR − Base | test BPDD − FDR |
|---|---:|---:|---:|---:|---:|
| pedestrian | +9.639 | +0.041 | −0.008 | +5.178 | −0.004 |
| people | +7.884 | +0.280 | −0.266 | +3.791 | +0.369 |
| bicycle | +5.912 | −0.517 | +0.445 | +3.532 | −0.055 |
| car | +6.145 | +0.377 | −0.051 | +5.079 | +0.405 |
| van | +6.514 | −0.649 | +0.937 | +4.638 | +0.914 |
| truck | +5.126 | +1.021 | −1.871 | +6.871 | +1.317 |
| tricycle | +7.759 | +0.293 | −0.215 | +5.174 | −0.825 |
| awning-tricycle | +2.588 | +0.682 | −0.778 | +3.353 | +0.654 |
| bus | +9.341 | +0.988 | −0.601 | +6.928 | +0.519 |
| motor | +9.647 | +0.083 | +0.105 | +6.039 | +0.363 |

FDR 在 val/test 的全部 10 类均为正增益，是当前最稳定主效应。BPDD 在 test 的 `truck`、`van`、`awning-tricycle`、`bus` 上较明显，但 `tricycle` 退化；FIA 三模块在 val 的类别改善与退化并存，不能声称稳定提升。

## 文件入口与写作边界

- 总体机器表：[`split_overall_results.csv`](split_overall_results.csv)
- 全尺度精确值：[`split_scale_results.csv`](split_scale_results.csv)
- 全类别精确值：[`split_class_results.csv`](split_class_results.csv)
- 组合状态与精确总体 JSON：[`split_gain_comparison.json`](split_gain_comparison.json)

论文主表可采用现有 exact 绝对值；只有 strict 配对行可以作因果涨点表述。三模块 test exact 补齐前，不能把截图约 `0.234` 当成最终结果。

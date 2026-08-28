# ICASSP 2027 图表规划：LRS-FDR / BPDD / FIA

> 图中论文名称统一为 NA-FDR / LRS-FDR。历史运行别名、EQuAL、DCF 和官方
> D-FINE-S 替代路线不进入当前主图；需要追踪时只在补充材料的 identity map 中
> 展示。

## 图 1：完整方法依赖图

### 目的

展示三个创新不是任意堆叠：FIA 增强 P3，LRS-FDR 产生逐层四边分布，BPDD 在
训练期消费这些分布并监督早期 decoder 层。

### 固定结构

```text
Image
  -> RT-DETR-L Backbone / Hybrid Encoder
  -> P3 -- FIA --> enhanced P3
  -> P4 / P5 unchanged paths
  -> Decoder queries + native references
  -> LRS-FDR boundary distributions (six layers)
       -> boxes / scores (train and inference)
       -> BPDD future-layer teachers (training only)
```

图中必须：

- 用实线表示推理路径；
- 用虚线表示 LRS weight transform 与 BPDD training-only losses；
- 把 BPDD 标为 removed at inference；
- 不把 LRS-FDR+BPDD+FIA 画成已有结果行，直到新组合训练完成；
- 不沿用旧 AP-FDR 的 preliminary-box 分支或 DN-FDR 分布监督。

## 图 2：NA-FDR 原生对齐

左右对比 Original FDR 与 NA-FDR：

| 元素 | Original FDR | NA-FDR |
|---|---|---|
| Distribution anchor | learned preliminary reference | native decoder reference |
| Preliminary loss | L1/GIoU enabled | absent |
| Normal-query FGL | enabled | enabled, stock assignment reused |
| Extra DN-FDR | enabled | absent; stock DN losses preserved |
| EAW | absent/历史开关 | absent |
| Cumulative 33-bin FDR | enabled | enabled |

主视觉应突出“reference alignment + effective-query supervision”，不要把 NA-FDR
画成只有两个关闭符号的配置截图。

## 图 3：LRS-FGL 机制图

按一次图像、一个浅层 decoder 的 normal matches 展示：

```text
matched boxes + GT
  -> detached IoU q
  -> four-edge target-bin representability check
       ineligible: q unchanged
       eligible: group mean q_bar
                 -> q_tilde = (1-alpha_l) q + alpha_l q_bar
  -> repeat one query weight over four edges
  -> adjacent-bin FGL
```

图中同时标出：

- 六层 alpha：`0.25, 0.20, 0.15, 0.10, 0.05, 0.00`；
- final layer identity；
- per-image/per-layer sum conservation；
- saturated target、DN、unmatched 不参与；
- no parameters / no inference operation。

建议用一组低/中/高 IoU 圆点展示向均值收缩，但不使用未经记录的实际 IoU 数值。

## 图 4：三臂结果与 trade-off

### 4.1 总体子图

只画同一冻结评估器的三组：

| Method | Recall | AP50 | AP75 | mAP |
|---|---:|---:|---:|---:|
| Original FDR | 0.491417 | 0.484700 | 0.294070 | 0.290698 |
| NA-FDR | 0.498339 | **0.493119** | 0.301061 | 0.296855 |
| LRS-FDR | **0.500606** | 0.491805 | **0.305773** | **0.296968** |

推荐分成两组柱：

1. NA-FDR vs Original：表现基础对齐的均衡增益；
2. LRS-FDR vs NA-FDR：表现 AP75/Recall 上升与 AP50/Precision 回落的 trade-off。

不能用截断 y 轴夸大 `+0.011 pp` mAP。

### 4.2 尺度子图

Tiny/Small/Medium mAP 三组并列；Large 单独用浅色或补充表，因为只有 130 个 GT。
图注必须指出 LRS 相对 NA 的 Tiny/Small 为负，不能只画 LRS 相对 Original。

### 4.3 训练稳定性附图

如版面允许，在补充材料画 epoch 91--100 mAP：

- Original mean `0.289968`；
- NA-FDR mean `0.296102`；
- LRS-FDR mean `0.295253`。

该图用于披露 best-point 与 tail 平台差异，不用于宣称 LRS 收敛更稳。

## 表格计划

| Table | 内容 | 当前状态 |
|---|---|---|
| Table 1 | VisDrone 外部会议方法比较 | 旧表可复用，需替换本文最终方法行 |
| Table 2 | Original FDR / NA-FDR / LRS-FDR 总体与内部消融 | 数据完整 |
| Table 3 | 三臂 Tiny/Small/Medium/Large 与类别方向 | 数据完整，建议补充材料 |
| Table 4 | LRS-FDR / +BPDD / +FIA / Full | 新组合未完成，不填数 |
| Table 5 | UAVDT Baseline / Full（两臂） | Baseline authority 待绑定；Full 未运行，不填数 |
| Table 6 | 最终 Params/FLOPs/Latency | LRS 不增量已知；完整新组合待统一实测 |

## 禁止内容

- 把旧 AP-FDR+BPDD/FIA checkpoint 标成 LRS-FDR 组合；
- 把 EQuAL 或 DCF 画成当前最终定位路径；
- 伪造误差条、显著性标记或多 seed 阴影；
- 隐藏 Tiny/Small 相对 NA-FDR 的回落；
- 用 Large 130 GT 的波动支撑总体机制；
- 把 val 与 test 或不同 evaluator 的数字画在同一无标注序列；
- 把历史别名作为论文方法名。

## 数据源

- [LRS-FDR 结果页](../results/LRS_FDR_RESULTS_ZH.md)
- [三臂 comparison JSON](../evidence/lrs_fdr_formal100_20260828/independent-evaluation/comparison.json)
- [LRS-FDR 方法页](../methods/FDR_ZH.md)
- [当前实验状态](../CURRENT_RERUN_STATUS_ZH.md)

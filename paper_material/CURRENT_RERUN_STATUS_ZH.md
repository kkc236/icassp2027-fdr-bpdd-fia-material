# 当前实验与材料状态（2026-08-28）

## 当前唯一论文主线

作者已放弃官方 D-FINE-S 替代 detector 路线，并将论文主线固定回 Ultralytics
RT-DETR-L：

```text
RT-DETR-L -> LRS-FDR -> BPDD -> FIA
```

第一项定位创新的规范身份为：

```text
Original FDR
  -> NA-FDR（原生对齐基础 / w/o LRS）
  -> LRS-FDR（最终完整 FDR 模块）
```

历史运行名称继续保留在原始 JSON、CSV、配置和 checkpoint 中，用于证据追踪；
论文正文、方法图和新结果表统一使用 NA-FDR / LRS-FDR。

## 已完成

### 1. NA-FDR / LRS-FDR Formal100

- Original FDR、NA-FDR、LRS-FDR 均有 100 个连续 epoch 日志；
- 每组按各自 best-val mAP checkpoint 选择，不按 AP75 或 Recall 追选；
- LRS-FDR source commit：`9fa9078011d92cc23fc1f0eec06ff34983986ff0`；
- LRS-FGL Gate0 五个浅层全部通过；
- 三个 checkpoint 已在同一冻结 evaluator 下完成一次总体、十类别、四尺度复评；
- 证据已冻结到 [`lrs_fdr_formal100_20260828`](evidence/lrs_fdr_formal100_20260828/README.md)。

### 2. 当前数值

| 方法 | P | R | AP50 | AP75 | mAP50-95 |
|---|---:|---:|---:|---:|---:|
| Original FDR | 0.570249 | 0.491417 | 0.484700 | 0.294070 | 0.290698 |
| NA-FDR | **0.587045** | 0.498339 | **0.493119** | 0.301061 | 0.296855 |
| LRS-FDR | 0.579512 | **0.500606** | 0.491805 | **0.305773** | **0.296968** |

- NA-FDR 相对 Original FDR：`+0.616 pp` mAP；
- LRS-FDR 相对 NA-FDR：`+0.011 pp` mAP、`+0.471 pp` AP75、`+0.227 pp`
  Recall；
- LRS-FDR 相对 Original FDR：`+0.627 pp` mAP、`+1.170 pp` AP75、
  `+0.919 pp` Recall。

## 尚未完成

### 1. 新 FDR 与 BPDD/FIA 的最终组合

现有 BPDD、FIA 和三模块结果使用旧 AP-FDR checkpoint。代码接口与 LRS-FDR
兼容不等于已经获得新组合结果。以下名称当前不得出现在正式结果表中：

- LRS-FDR + BPDD（未按新 FDR 身份完成正式训练）；
- LRS-FDR + FIA（未按新 FDR 身份完成正式训练）；
- LRS-FDR + BPDD + FIA（未按新 FDR 身份完成正式训练）。

旧结果保留为机制有效性和兼容性历史证据，不直接重命名。

### 2. 第二数据集

当前证据只覆盖 VisDrone、seed 0。第二数据集冻结三组为：

1. Baseline；
2. Baseline + NA-FDR；
3. Baseline + 完整投稿方法。

第二数据集不重复 Original FDR、EQuAL、DCF、NA-FDR/LRS 内部更多开关或全部模块
组合。其职责是泛化验证，VisDrone 负责内部归因。

### 3. 统计稳定性

尚无多 seed 置信区间或显著性检验。现阶段允许单 seed 描述性结果，但不得使用
`significant`、`robust across seeds` 或 `universally generalizable`。

## 已放弃但保留的路线

| 路线 | 状态 | 保留原因 |
|---|---|---|
| EQuAL / EAW | 放弃为当前方法 | standalone 结果和失败边界可审计 |
| DCF-FDR / transient / persistent DCF | 放弃 | Formal100 与后期策略结果可防止重复试错 |
| 官方 D-FINE-S 重跑 | 放弃为投稿 detector | 协议与原始材料仍有历史价值 |
| AP-FDR preliminary + DN-FDR | 历史原始实现 | 是 Original FDR 和旧组合 checkpoint 的真实身份 |

任何历史文档、日志、checkpoint、Release 或 authority JSON 均不删除、不改名、不
覆盖。

## 后续执行顺序

1. 固定 LRS-FDR + BPDD + FIA 的完整 VisDrone 组合配置；
2. 以 Baseline / NA-FDR / 完整方法三组执行第二数据集；
3. 对最终 VisDrone 组合和第二数据集 best checkpoint 使用同一声明协议复评；
4. 更新完整主表、复杂度表和论文英文稿；
5. 若算力允许，再补关键臂多 seed，而不是扩展新的 FDR 机制。

当前阶段不得继续调整 `alpha0=0.25`、新增 EAW/DCF 或根据 val 结果修改 LRS 日程。

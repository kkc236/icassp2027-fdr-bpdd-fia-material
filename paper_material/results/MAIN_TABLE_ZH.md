# VisDrone val 主结果表

下表展示当前正式核心行。FIA 相关结果因 checkpoint 拓扑和配对等级不同，单列在后续消融观察表中，避免与严格主线混排。

| 方法 | FDR | BPDD | FIA | Precision | Recall | AP50 | AP75 | mAP50–95 | 证据等级 | 可安全表述 |
|---|:---:|:---:|:---:|---:|---:|---:|---:|---:|---|---|
| RT-DETR-L | — | — | — | 0.46761 | 0.41731 | 0.38663 | 0.21302 | 0.21911 | strict | 严格基线绝对值 |
| RT-DETR-L+FDR | ✓ | — | — | 0.56911 | 0.49278 | 0.48468 | 0.29253 | 0.28966 | strict | 可与上一行作严格配对差值 |
| RT-DETR-L+FDR+BPDD | ✓ | ✓ | — | 0.5706336342 | 0.4944641371 | 0.4864074914 | 0.2980956482 | 0.2922578696 | cross_authority_exact | 精确绝对值；不得写成严格配对 BPDD 增益 |

## 差值边界

唯一可直接写为严格配对差值的是 +FDR 相对 RT-DETR-L：

| 指标 | 绝对差 | 百分点差 |
|---|---:|---:|
| Precision | +0.10150 | +10.150 pp |
| Recall | +0.07547 | +7.547 pp |
| AP50 | +0.09805 | +9.805 pp |
| AP75 | +0.07951 | +7.951 pp |
| mAP50–95 | +0.07055 | +7.055 pp |

+FDR+BPDD 与 +FDR 的已展示数值算术差依次为 Precision +0.0015236342、Recall +0.0016841371、AP50 +0.0017274914、AP75 +0.0055656482、mAP50–95 +0.0025978696。这些只可称“跨 authority 算术差”，不能归因为严格配对的 BPDD 收益。

## FIA 行状态

- FIA-only、FDR+FIA：按当前实验决策直接采用 Release 中各自的 `best.pt`，已在冻结 VisDrone evaluator 下完成独立 exact val/test；两者是已发布 cascading standalone 拓扑，不称为 P3-only。
- FDR+BPDD+FIA：已定位正确 P3-only 新 checkpoint；best-val 记录为 P=0.56996、R=0.49848、AP50=0.48982、mAP50–95=0.29618，相对当前 BPDD val 绝对值为 +0.3922 pp 的算术观察。
- 新三模块仍缺 AP75、test 和冻结 evaluator 独立复评，所以只在状态区登记，不进入上方正式表，也不写成严格配对 FIA 因果增益。

### 现有 best.pt standalone 消融（独立 val）

| 方法 | P | R | AP50 | AP75 | mAP50–95 | 参照 | ΔmAP | 证据 |
|---|---:|---:|---:|---:|---:|---|---:|---|
| RT-DETR-L+FIA | 0.479433 | 0.414194 | 0.385675 | 0.209674 | 0.216795 | RT-DETR-L | −0.231 pp | best checkpoint independent val exact |
| RT-DETR-L+FDR+FIA | 0.577524 | 0.490889 | 0.486314 | 0.299724 | 0.294940 | RT-DETR-L+FDR | +0.528 pp | best checkpoint independent val exact |

这里的差值是当前登记对照的算术差，不是严格配对因果增益。结论是：FIA-only 略有负增益，FDR+FIA 呈正增益；论文主线使用 FIA 与 FDR 的兼容组合，不以 FIA-only 作为性能主张。

同一批 `best.pt` 的 independent exact test 已补齐 AP75 和逐类别 F1：FIA-only / FDR+FIA 的 test mAP50–95 分别为 `0.177176` / `0.234645`，AP75 分别为 `0.171613` / `0.235879`。完整 test 表和逐类别明细见 [论文结果统一汇总](RESULTS_ZH.md)。

最新状态与导入条件见 [FIA 结果状态](FIA_RESULTS_STATUS_ZH.md)。

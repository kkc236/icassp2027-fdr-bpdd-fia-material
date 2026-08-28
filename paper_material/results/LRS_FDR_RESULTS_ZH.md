# NA-FDR / LRS-FDR Formal100 结果与消融

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent + academic-paper
- Origin Mode: validate / revision
- Origin Date: 2026-08-28
- Verification Status: ANALYZED
- Source Commit: `9fa9078011d92cc23fc1f0eec06ff34983986ff0`
- Evidence: [`lrs_fdr_formal100_20260828`](../evidence/lrs_fdr_formal100_20260828/README.md)
- Scope: VisDrone val、seed 0、100 epochs、独立 best checkpoint 复评

## 1. 实验身份与选择规则

| 论文名称 | 原始证据标识 | Best epoch | 角色 |
|---|---|---:|---|
| Original FDR | `original_fdr` | 92 | 历史 FDR 对照 |
| NA-FDR | `clean_fdr` | 88 | 原生对齐基础、`w/o LRS` |
| LRS-FDR | `clean_fdr_plus_lrs_fgl` / `lrs_fdr` | 84 | 最终完整 FDR 模块 |

每组独立按训练日志中最大的 `metrics/mAP50-95(B)` 选择 best checkpoint；随后在
相同 VisDrone val 和相同冻结评估器下各执行一次 FP32 预测。总体、类别和尺度
统计复用同一预测缓存，不进行 test-set 选模。

评估固定为 548 张图、38,759 个目标、`imgsz=640`、`batch=8`、`workers=8`、
`conf=0.001`、`max_det=300`、`nms=false`、`half=false`、`cache=false`。

## 2. 总体结果

| 方法 | Precision | Recall | F1 | AP50 | AP75 | mAP50-95 |
|---|---:|---:|---:|---:|---:|---:|
| Original FDR | 0.570249 | 0.491417 | 0.527907 | 0.484700 | 0.294070 | 0.290698 |
| NA-FDR | **0.587045** | 0.498339 | **0.539067** | **0.493119** | 0.301061 | 0.296855 |
| LRS-FDR | 0.579512 | **0.500606** | 0.537177 | 0.491805 | **0.305773** | **0.296968** |

### 2.1 分层归因

| 对比 | ΔP | ΔR | ΔF1 | ΔAP50 | ΔAP75 | ΔmAP50-95 |
|---|---:|---:|---:|---:|---:|---:|
| NA-FDR − Original FDR | +1.680 pp | +0.692 pp | +1.116 pp | +0.842 pp | +0.699 pp | +0.616 pp |
| LRS-FDR − NA-FDR | -0.753 pp | +0.227 pp | -0.189 pp | -0.131 pp | +0.471 pp | +0.011 pp |
| LRS-FDR − Original FDR | +0.926 pp | +0.919 pp | +0.927 pp | +0.711 pp | +1.170 pp | +0.627 pp |

正确归因是：

- NA-FDR 贡献主要来自原生 reference、原生 assignment 和正常匹配查询监督的
  统一对齐；它相对 Original FDR 的所有总体指标均为正；
- LRS-FGL 在 NA-FDR 上进一步偏向严格 IoU 定位与 Recall，AP75 和 Recall 上升，
  但 Precision、AP50 和 F1 下降；
- 正文可用 LRS-FDR 相对 Original FDR 的 `+0.627 pp` mAP 和 `+1.170 pp` AP75
  描述最终模块，不得把这两个数全部归因给 LRS-FGL。

## 3. 四尺度完整结果

尺度使用网络输入像素中的 `sqrt(area)`：Tiny `<16`、Small `16--32`、Medium
`32--96`、Large `>=96`。

| Scale | GT | Original AP50 | AP75 | mAP | NA AP50 | AP75 | mAP | LRS AP50 | AP75 | mAP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Tiny | 20,860 | 0.303773 | 0.120423 | 0.147025 | **0.322368** | **0.128494** | **0.157561** | 0.308845 | 0.124744 | 0.149050 |
| Small | 12,420 | 0.462261 | 0.320037 | 0.291050 | **0.476670** | 0.330913 | **0.300759** | 0.470001 | **0.334236** | 0.298944 |
| Medium | 5,349 | 0.546750 | 0.445861 | 0.395473 | **0.548454** | 0.455418 | 0.400317 | 0.544352 | **0.455516** | **0.400401** |
| Large | 130 | 0.441541 | 0.404337 | 0.380301 | **0.562541** | **0.517841** | **0.472407** | 0.417409 | 0.399584 | 0.368274 |

Medium 行的 AP50 最大值实际为 NA-FDR `0.548454`，因此表中该项的强调应归
NA-FDR；Large 只有 130 个 GT，任何排序都只作描述，不形成方法主张。

### 3.1 尺度差值

| Scale | NA − Original ΔmAP | LRS − NA ΔmAP | LRS − Original ΔmAP |
|---|---:|---:|---:|
| Tiny | +1.054 pp | -0.851 pp | +0.203 pp |
| Small | +0.971 pp | -0.181 pp | +0.789 pp |
| Medium | +0.484 pp | +0.008 pp | +0.493 pp |
| Large | +9.211 pp | -10.413 pp | -1.203 pp |

NA-FDR 相对 Original FDR 四尺度 mAP 均为正。LRS-FDR 相对 NA-FDR 的 Tiny 和
Small 下降，因此 LRS 不得表述为小目标全面增强。最终 LRS-FDR 相对 Original
FDR 的 Tiny、Small 和 Medium 为正；Large 结果受极小样本量影响。

## 4. 十类别方向分析

### 4.1 LRS-FDR 相对 NA-FDR

| Class | ΔAP50 | ΔAP75 | ΔmAP |
|---|---:|---:|---:|
| awning-tricycle | -0.1865 pp | +0.9325 pp | +0.3525 pp |
| bicycle | +1.0361 pp | +0.1091 pp | +0.3304 pp |
| bus | -1.7644 pp | +1.9563 pp | -0.9087 pp |
| car | +0.1589 pp | -0.1140 pp | -0.0244 pp |
| motor | -0.4872 pp | -0.6626 pp | -0.3371 pp |
| pedestrian | +0.0720 pp | +0.4130 pp | +0.0944 pp |
| people | -0.5723 pp | -0.0386 pp | -0.0843 pp |
| tricycle | +0.6205 pp | +2.0646 pp | +0.6626 pp |
| truck | -0.4626 pp | -0.2694 pp | -0.3820 pp |
| van | +0.2721 pp | +0.3211 pp | +0.4091 pp |

LRS 相对 NA-FDR：mAP 为正 `5/10` 类，AP75 为正 `6/10` 类，AP50 为正
`5/10` 类。该分布与“严格 IoU/Recall 取向而非全面增益”的解释一致。

### 4.2 LRS-FDR 相对 Original FDR

| Class | ΔAP50 | ΔAP75 | ΔmAP |
|---|---:|---:|---:|
| awning-tricycle | +1.7535 pp | +1.8050 pp | +1.5665 pp |
| bicycle | +1.0612 pp | +0.0792 pp | +0.4095 pp |
| bus | +0.8772 pp | +4.6276 pp | +1.6088 pp |
| car | +0.5188 pp | +0.8409 pp | +0.4763 pp |
| motor | +0.5090 pp | -0.4042 pp | +0.0686 pp |
| pedestrian | +0.1252 pp | +0.7095 pp | +0.3350 pp |
| people | +0.0004 pp | -0.1888 pp | -0.0213 pp |
| tricycle | +0.0681 pp | +2.0217 pp | +0.4076 pp |
| truck | +1.6400 pp | +1.4051 pp | +0.7375 pp |
| van | +0.5517 pp | +0.8068 pp | +0.6814 pp |

最终 LRS-FDR 相对 Original FDR：AP50 为正 `10/10` 类、AP75 为正 `8/10`
类、mAP 为正 `9/10` 类。people 的 mAP 为 `-0.0213 pp`，不得写成十类别全部
提升。

## 5. 训练末段稳定性

| 方法 | Epoch 91--100 mean mAP | Linear slope / epoch |
|---|---:|---:|
| Original FDR | 0.289968 | -0.00003273 |
| NA-FDR | **0.296102** | +0.00004303 |
| LRS-FDR | 0.295253 | -0.00024321 |

LRS-FDR 的 best checkpoint 是正向点估计，但末十轮平均比 NA-FDR 低
`0.0849 pp` 且斜率为负。论文不得据此声称更稳定的终末平台。

## 6. 预注册门检审计

| Gate | Required | Observed | Status |
|---|---:|---:|---|
| Strong best mAP | `>=0.29796` | 0.29703（训练日志） | FAIL |
| Recall at selected row | `>=0.49849` | 0.50141（训练日志） | PASS |
| Epoch 91--100 mean over NA-FDR | `>0.296102` | 0.295253 | FAIL |
| AP75 regression | `<=0.0005` regression | +0.004712 | PASS |
| Tiny AP non-negative vs NA-FDR | `>=0` | -0.008511 | FAIL |
| Low-IoU next-layer IoU | 至少 3 个浅层 transition 为正 | 未记录 | UNMEASURED |

Strong paper-level GO 没有通过。LRS-FGL 可以保留为 LRS-FDR 内部的 AP75/Recall
取向机制，但不能作为“强而全面”的独立涨点。NA-FDR 是更稳的基础贡献。

## 7. 论文可用结论

### 可以写

> NA-FDR 通过原生 reference 与正常匹配分布监督的统一对齐，相对历史 Original
> FDR 在全部总体指标上取得正向变化。建立在 NA-FDR 上的 LRS-FGL 对浅层可表示
> 匹配执行总权重守恒的可靠性收缩，在总体 mAP 基本保持的同时提高 AP75 与
> Recall。完整 LRS-FDR 相对 Original FDR 的 mAP/AP75 分别提高 0.627/1.170
> 个百分点。

### 不能写

- LRS-FGL 显著提高总体 mAP；
- LRS-FDR 在全部尺度、全部类别上提高；
- LRS-FGL 专门增强 Tiny/Small；
- seed 0 足以证明跨随机种子稳定性；
- VisDrone 结果证明跨数据集泛化。

## 8. 下一实验

第二数据集正式名称为 **UAVDT**（不是 UAT），不复制 VisDrone 的内部开关；冻结矩阵
只有两个同域、协议匹配的臂：

1. **Baseline**：作者已确认完成，但 artifact identity 与 metrics 必须先绑定既有
   authority；
2. **Full**：Baseline + 完整投稿方法，尚未完成，不填数。

UAVDT 不运行 NA-FDR、LRS-only、G/H 或其他模块级消融。主数据集负责内部归因，UAVDT
只支持 matched in-domain 的第二数据集 effectiveness / multi-dataset applicability
描述性判断，不支持 zero-shot transfer 或 module-level attribution；单 seed 也不提供
稳定性证明。annotation conversion、split 和 protocol matching 必须随 UAVDT authority
单独登记，不能把 VisDrone 结果当作 UAVDT 结果。

## 9. 机器材料

- [证据包说明](../evidence/lrs_fdr_formal100_20260828/README.md)
- [三组统一 comparison JSON](../evidence/lrs_fdr_formal100_20260828/independent-evaluation/comparison.json)
- [NA-FDR 单臂 JSON](../evidence/lrs_fdr_formal100_20260828/independent-evaluation/na_fdr.json)
- [LRS-FDR 单臂 JSON](../evidence/lrs_fdr_formal100_20260828/independent-evaluation/lrs_fdr.json)
- [SHA-256 清单](../evidence/lrs_fdr_formal100_20260828/MANIFEST.sha256)
- [规范方法页](../methods/FDR_ZH.md)
- [冻结设计](../../docs/superpowers/specs/2026-08-28-lrs-fdr-material-freeze-design.md)

# LRS-FDR / BPDD / FIA 创新定位与对抗性审计

> **作者裁决（2026-08-28）**：LRS-FDR 是当前第一项完整定位创新；NA-FDR 是
> LRS-FDR 的原生对齐基础和内部消融，不作为另一个并列模块。EQuAL、DCF、旧
> AP-FDR 与官方 D-FINE-S 路线只保留为历史材料。

## 1. 最稳中心命题

> 本文面向密集 UAV 小目标提出 LRS-FDR。其 NA-FDR 基础将细粒度分布回归统一
> 对齐到 RT-DETR 原生 decoder reference、stock Hungarian assignment 与 normal
> matched queries；LRS-FGL 进一步在浅层可表示匹配中执行总权重守恒、随层衰减
> 的可靠性收缩，以改善严格 IoU 定位与 Recall。BPDD 从 LRS-FDR 的逐层边界分布
> 构造训练期跨层教师，FIA 从特征侧增强 P3，形成定位、优化与表征的依赖链。

该命题把基础分布算子与本文贡献分开：D-FINE 是 33-bin 边界表示、non-uniform
Integral、累计细化和基础 FGL 的来源；本文主张 NA-FDR 的具体原生对齐组织及
LRS-FGL 的具体可靠性收缩机制。

## 2. 第一创新的正确归因

### 2.1 NA-FDR 不是无贡献对照

NA-FDR 的论文含义是 Native-Aligned FDR：

- 以 RT-DETR native decoder reference 替代 learned preliminary reference；
- 复用 stock Hungarian assignment；
- 额外分布监督只作用于 normal matched queries；
- stock DN 分类、L1 和 GIoU 保留，只取消 DN 上额外 FDR/FGL；
- EAW 关闭，使权重变量保持单一。

其证据是相对 Original FDR 的 Precision/Recall/AP50/AP75/mAP 全部正向，mAP 与
AP75 分别为 `+0.616/+0.699 pp`。因此它可以作为 LRS-FDR 的基础创新设计；但
不能把“删除 preliminary 与 DN-FDR”本身写成创新，必须解释为对几何锚点和有效
查询监督的统一重组，并绑定正向消融。

### 2.2 LRS-FGL 的贡献必须窄而准确

LRS-FGL 对同图像、同浅层、四边目标均可表示的 normal matches，将 detached IoU
权重向该组均值收缩，保持每组总 FGL 权重，并让 alpha 从 `0.25` 衰减到最后层
`0.0`。它没有参数、teacher、matcher、额外 query 或推理分支。

相对 NA-FDR：

- Recall `+0.227 pp`；
- AP75 `+0.471 pp`；
- mAP `+0.011 pp`；
- Precision `-0.753 pp`；
- AP50 `-0.131 pp`；
- Tiny/Small mAP `-0.851/-0.181 pp`。

因此最佳表述是“提高严格 IoU 定位与 Recall，同时基本保持总体 mAP”，而不是
“全面提高检测性能”或“增强小目标”。

### 2.3 最终 LRS-FDR 的总体结果

相对 Original FDR，完整 LRS-FDR 的 Precision、Recall、AP50、AP75、mAP 分别
变化 `+0.926/+0.919/+0.711/+1.170/+0.627 pp`。这组结果支持完整第一创新；
其中 NA-FDR 和 LRS 的贡献必须通过上述两级对照分别解释。

## 3. 三项创新的证据等级

| 贡献 | 设计身份 | 当前证据 | 强度与边界 |
|---|---|---|---|
| LRS-FDR | NA-FDR 原生对齐 + LRS-FGL | 三臂 Formal100、总体/类别/尺度统一复评、Gate0 | 第一创新可用；LRS 仅 AP75/Recall 取向 |
| BPDD | all-future quality teacher + better-only gate | 旧 AP-FDR 上严格 paired val/test、零推理增量 | 机制证据较强；LRS-FDR 新组合待跑 |
| FIA | P3-only residual/attention refinement | fresh standalone val/test、历史组合、复杂度 | standalone 可用；新最终组合待跑 |

当前不能把三项写成已经在同一个新 checkpoint 中共同验证。完成 LRS-FDR+BPDD+FIA
训练前，主张层次应是“第一创新已冻结，第二/第三创新各有既有机制证据，最终新
组合待验证”。

## 4. 对抗性审计

| 审稿人最强攻击 | 风险 | 诚实回应 | 需要展示的证据 |
|---|:---:|---|---|
| NA-FDR 只是关掉两个组件 | 高 | 不把删除写成创新；把贡献限定为 native reference、stock assignment、normal-query supervision 的统一对齐，并用 NA vs Original 的全总体正向结果验证 | 方法差异图、NA−Original 表 |
| LRS 只涨 `0.011 pp` mAP | 高 | 承认 mAP 近似保持；贡献目标是 AP75 `+0.471 pp` 与 Recall `+0.227 pp`，并且最终层目标和总 FGL 权重保持 | LRS−NA 表、alpha 日程、守恒证明 |
| LRS 伤害 Tiny/Small | 高 | 明确 Tiny/Small 相对 NA 下降，不声称小目标全面增强；最终相对 Original 的 Tiny/Small 仍为正 | 四尺度表与 GT 数量 |
| best epoch 是噪声峰值 | 高 | 报告 last-10 mean 和 slope；不声称更高终末平台 | best 与 tail 表 |
| 第一创新大量借用 D-FINE | 高 | Related Work 主动归因基础分布算子；只主张 NA 对齐组织和 LRS 变换 | 来源表、公式差异、代码 commit |
| LRS-FDR 与 BPDD/FIA 未共同重训 | 高 | 旧组合保持历史名称；新组合结果为空，不提前改名或填表 | 当前状态页、最终组合 protocol |
| 单 seed 无统计稳定性 | 中 | 使用 descriptive/fixed-seed wording；若算力允许补关键臂 seed | seed0 authority、限制段 |
| 单数据集无法证明泛化 | 中 | UAVDT 仅采用 matched in-domain Baseline / Full 两臂，不复制内部消融；它支持第二数据集 effectiveness / multi-dataset applicability，不支持 zero-shot transfer 或 module-level attribution | UAVDT 两臂冻结矩阵 |
| Large 波动异常 | 中 | Large 仅 130 GT，不作为主张；重点报告总体和 Tiny/Small/Medium | scale GT count |
| 三模块只是工程堆叠 | 高 | 画出依赖：LRS-FDR 产生分布，BPDD 消费分布，FIA 提供 P3；分别绑定机制证据 | Overall architecture + 分层消融 |

## 5. 审稿通过条件

### 当前已满足

- 最终 FDR 相对 Original FDR 的全部总体指标正向；
- NA-FDR 有独立内部对照，不再依赖“删掉两个开关就算创新”的口头解释；
- LRS 相对 NA-FDR 的 mAP 数值非负，AP75/Recall 为正；
- 公式、alpha 日程、可表示性防火墙、权重守恒和推理边界均已冻结；
- 失败的 EAW/DCF/持久策略证据没有删除或伪装。

### 当前未满足

- LRS-FDR+BPDD+FIA 的同身份完整训练；
- UAVDT Full 与既有 Baseline 的第二数据集验证；
- 多 seed 稳定性；
- LRS 预注册 strong GO；
- low-IoU next-layer mechanism diagnostic。

这些缺口不会否定已有 seed0 描述性结果，但决定正文不能使用“stable、robust、
universal、significant、across datasets”。

## 6. 英文核心文案

### 6.1 Contribution 1

> We propose LRS-FDR, a native-aligned fine-grained distribution refinement
> framework for RT-DETR. Its NA-FDR foundation aligns distribution decoding and
> supervision with native decoder references, stock Hungarian assignments, and
> normally matched queries. Within this aligned formulation, LRS-FGL performs
> representability-aware, layer-decayed reliability shrinkage while preserving
> the total FGL weight of every image-layer group and leaving the final-layer
> objective unchanged.

### 6.2 Method opening

> LRS-FDR reorganizes D-FINE-style boundary-distribution primitives within the
> stock RT-DETR localization path. We first define NA-FDR by anchoring cumulative
> boundary distributions to native decoder references and restricting extra
> distribution supervision to normally matched queries under the stock
> assignments. We then shrink detached shallow-layer IoU reliability weights
> toward an image-local, layer-local mean only when all target edges are
> representable. The shrinkage decays to zero at the final decoder layer and
> conserves the total FGL weight, introducing neither trainable parameters nor
> inference operations.

### 6.3 Results wording

> Under a frozen single-seed VisDrone validation protocol, NA-FDR improves
> mAP50–95 by 0.616 points over Original FDR. Adding LRS-FGL further increases
> AP75 and recall by 0.471 and 0.227 points, respectively, while maintaining
> mAP50–95 (+0.011 points). The complete LRS-FDR improves mAP50–95 and AP75 by
> 0.627 and 1.170 points over Original FDR. These differences are descriptive
> fixed-seed results rather than statistical significance claims.

### 6.4 Related Work attribution

> Fine-grained distribution refinement represents individual box boundaries
> with discrete probability distributions and recovers continuous offsets using
> an integral operator. We adopt the boundary representation, non-uniform
> integral, cumulative refinement, and basic fine-grained localization objective
> studied in D-FINE. Our contribution lies in the native-aligned reference and
> query-supervision organization of NA-FDR and the representability-aware,
> mean-preserving layerwise reliability shrinkage used by LRS-FGL.

### 6.5 暂不使用的完整 Abstract

在 LRS-FDR+BPDD+FIA 新组合与第二数据集完成前，不冻结包含三模块最终精度的完整
英文 Abstract。当前只冻结以上可拼装、证据绑定的小段，避免沿用旧 AP-FDR 三模块
数值冒充 LRS-FDR 系统结果。

## 7. 禁止句式与替代句式

| 不要写 | 改写为 |
|---|---|
| We first invent FDR, Integral, or FGL. | We reorganize established boundary-distribution primitives through native alignment and layerwise reliability shrinkage. |
| LRS-FGL significantly improves mAP. | LRS-FGL improves AP75 and recall while maintaining mAP in the fixed-seed ablation. |
| NA-FDR is just a cleaner baseline. | NA-FDR is the native-aligned foundation and the direct `w/o LRS` control. |
| LRS-FDR improves all object scales. | LRS-FDR is positive over Original FDR on Tiny/Small/Medium mAP, while its direct Tiny/Small comparison with NA-FDR is negative. |
| Our complete three-module model achieves the old AP-FDR score. | The old combination remains historical; the LRS-FDR combination result is pending. |
| Our method generalizes across datasets. | Current conclusions are limited to VisDrone until the frozen second-dataset matrix is completed. |

## 8. 成功率优先的下一步

1. 不再修改 LRS 公式、`alpha0=0.25` 或六层日程；
2. 先完成 LRS-FDR+BPDD+FIA 的 VisDrone 最终组合，确认三个创新能共同工作；
3. UAVDT 只绑定既有 Baseline 并运行 Full；
4. 正文第一创新使用 Original / NA / LRS 三行，详细类别和尺度放补充材料；
5. 时间不足时优先第二数据集而不是全面多 seed 或更多 FDR 开关；
6. 全文用 “descriptive fixed-seed gain”，不使用统计显著措辞。

## 9. 权威材料

- [LRS-FDR 方法页](../methods/FDR_ZH.md)
- [LRS-FDR 结果页](../results/LRS_FDR_RESULTS_ZH.md)
- [三臂证据包](../evidence/lrs_fdr_formal100_20260828/README.md)
- [当前状态](../CURRENT_RERUN_STATUS_ZH.md)
- [冻结设计](../../docs/superpowers/specs/2026-08-28-lrs-fdr-material-freeze-design.md)

# ICASSP 2027 创新定位、核心文案与对抗性审计

> **2026-09-15 当前决策**：论文主系统采用已完成的 Ultralytics `LRS-GFDR + Capacity-BPDD-v3-Safe + FIA` Formal100（best val mAP50–95=`0.30109`）。最新 BPDD-only 已完成 E100（best E80=`0.29277`），并已补齐固定 test 独立评估（mAP@300=`0.24111`）；严格 BPDD 因果结论继续引用同 authority 配对证据。EQuAL standalone 仍保留为历史/外部候选，不把未重训的 EQuAL 组合写入主表。

当前最稳的主张是“架构保持型逐边分布定位 + 训练期跨层边界蒸馏 + P3 高分辨率交互”的协同设计，而不是把基础离散分布算子本身宣称为原创。D-FINE 的四边离散表示、non-uniform Integral 与基础 adjacent-bin FGL 继续明确归因；历史 EQuAL 与 AP-FDR 组合数字按各自 authority 保存，不互相改名。

## 1. 一句话决策

论文不要把卖点写成“三个模块叠加”。AP-FDR 应作为第一项方法创新，先写本文提出的 RT-DETR 专用结构与监督合同，再用一句话说明其边界分布基础构件受 D-FINE 启发；BPDD 则明确作为由本文独立提出并实现的原创算法。最稳的中心命题是：

> 本文提出面向密集 UAV 小目标的架构保持型细粒度分布细化 AP-FDR：在不改变 RT-DETR-L 分类、查询匹配和后处理合同的条件下，以 stock-head-informed preliminary 分支及 normal/DN 匹配一致监督建立逐边分布定位；其基础分布表示受 D-FINE 启发并明确归因。进一步独立提出原创 BPDD，通过目标边条件的未来层教师与 better-only 门控改善早期层，并以轻量 FIA 增强 P3 表征，形成定位、优化与特征协同的完整系统。

这个表述把个人创新分成三个清晰层级：AP-FDR 是架构与监督创新，BPDD 是建立在 AP-FDR 逐层分布上的优化创新，FIA 是轻量表征创新。FDR 的 `+7.055 pp` 支持 AP-FDR 整体有效；在内部单因素消融完成前，不把该增益拆分归因给任一基础算子。

## 2. D-FINE 的处理原则

论文采用“受启发—独立重构—明确归因”的口径。D-FINE 是基础数学来源和研究启发，AP-FDR 才是正文方法主体：

1. 标题不出现 D-FINE，使用 `architecture-preserving distribution refinement` 描述本文方法。
2. Related Work 用一句话说明：逐边离散表示、非均匀 Integral 与 FGL 基础形式参考 D-FINE。
3. Method 直接定义 AP-FDR 的四项个人设计：localization-only、stock-head-informed preliminary、normal/DN assignment consistency、private-RNG initialization contract。
4. 后续正文使用 AP-FDR；结果表因 checkpoint/config 历史标签可继续写 FDR，并在表注说明二者对应同一本文实现。
5. 贡献条目可以写 `We propose AP-FDR`，但不能写 `We first invent FDR/FGL/Integral`。

不以任何数值比例描述算法原创性；“来源简述、原创设计详述”只是论文组织原则，不代表 D-FINE 与 AP-FDR 的算法占比。代码行数、文件数量和文字篇幅也不能代替机制来源判断。

这种安排既保留必要归因，也把审稿焦点从基础算子的出处转向本文为何以新的结构和监督合同重构它们。对于 BPDD，采用“问题启发相关、算法构造独立”的更强口径：GO-LSD 提供跨层定位蒸馏的问题背景，BPDD 的 future-layer mixture、better-only gate、stock assignment contract、normal-only scope 与损失定义均为本文独立设计。

### 写法样本的使用边界

正式 ICASSP 方法论文只用于学习一种稳定的贡献组织方式：先界定目标任务中尚未解决的问题，再给出针对该问题的结构或监督设计，最后用消融、精度和复杂度证据闭合主张。这个内部写作观察不构成本文的技术相关工作，也不进入 Related Work、外部比较表或参考文献。正文只引用与 UAV detection、RT-DETR、分布定位、跨层蒸馏和小目标表征直接相关的工作，不能用“同会存在类似改造论文”替代本文自身的创新论证。

## 3. 推荐标题

首选：

> **Architecture-Preserving Distribution Refinement with Progressive Distillation for Dense UAV Detection**

备选：

> **AP-FDR: Architecture-Preserving Distribution Refinement for Dense UAV Object Detection**

> **Distribution-Refined RT-DETR with Boundary-Progressive Distillation and Fine-Scale Interaction for UAV Detection**

首选标题同时覆盖 AP-FDR 与 BPDD，最利于建立个人方法主线。第二个标题最突出 AP-FDR，但要求正文具备完整内部消融；第三个标题更适合保守投稿版本。

## 4. 问题—设计—证据的三层贡献结构

### 贡献 1：AP-FDR 架构与监督创新

**问题**：stock RT-DETR-L 直接回归连续框，无法显式表达密集小目标每条边的不确定性；整体替换 detector 又会混入分类、Decoder 和查询处理变化。**设计**：提出 AP-FDR，在保留分类、查询选择、Decoder 主体、Hungarian matching 与后处理合同的条件下，将逐边分布定位限制在 localization branch，并构建 stock-head-informed preliminary 分支、normal/DN 共享 stock assignment 的匹配一致监督及隔离初始化。**证据**：严格统一评估中，完整 AP-FDR 相对 baseline 的 val mAP50–95 提高 `+7.055 pp`、AP75 提高 `+7.951 pp`；内部单因素消融完成前，该增益只归于完整 AP-FDR。33-bin 表示、非均匀 Integral 与 FGL 基础形式参考既有工作，不单独计为原创。

### 贡献 2：跨层优化创新 BPDD

**问题**：早期 Decoder 层定位较弱，而固定使用最终层作为教师并不能保证每个目标、每条边都获得更可靠的监督。**设计**：BPDD 是由本文独立提出并实现的原创算法；它从同一次前向的全部未来解码层构造目标边质量加权教师，better-only 门控只在教师优于当前层时施加 KL 监督，并直接复用 stock 最终层匹配。它不复用 GO-LSD 的固定最终层教师、DDF 损失或源代码。**证据**：严格配对 best.pt 复评显示，BPDD 在 val/test 上分别提高 `+0.239/+0.283 pp` mAP50–95，test AP75 提高 `+0.276 pp`；其推理 Params、FLOPs、显存和延迟与 FDR 配对臂相同。

“原创”在这里指 BPDD 的具体 formulation、损失合同与代码实现具有独立来源；不扩张为未经系统检索证明的“文献史上首次”。论文仍应主动引用 GO-LSD，并把六维差异表放在 Method 或 Supplementary，而不是通过弱化相关工作制造原创性。

### 贡献 3：轻量表征互补 FIA

**问题**：640 输入下，密集小目标主要依赖高分辨率 P3，但把增强特征继续级联重建 P4/P5 会扩大干预范围。**设计**：FIA 以 P3-only 拓扑插入，通过双 depth-wise 残差细化、联合通道/空间门控和零初始化残差缩放增强 P3，同时让 P4/P5 继续从原始分支构建。**证据**：fresh P3-only FIA-only 在 val/test 上分别呈现 `+0.7946/+0.8101 pp` 的同 split 算术增益；FIA 只增加 `0.301M` 参数、`3.419G` FLOPs 和 `0.861 ms` 中位延迟，三模块仍达到 `25.21 FPS`。

## 5. 外部论文的使用层级

### 5.1 正文首选：接近但不高于本文

这些结果最适合证明“本文达到近期 A/B 会竞争区间”，放在外部对比表靠前位置：

| 方法 | 会议 | Input | val mAP50–95 | 本文绝对位置 | 正文用途 |
|---|---|---:|---:|---:|---|
| 本文三模块 | ICASSP 2027 投稿 | 640 | **0.2961** | — | 参照 |
| TPH-YOLOv5-x + UGS | ICCV 2025（A） | 640 | 0.2900 | 本文高 0.61 pp | 最近 A 会下界 |
| UAV-DETR-EV2 | IROS 2025（B） | 640 | 0.2870 | 本文高 0.91 pp | 高效 DETR 近邻 |
| RT-DETR-R50 | IROS 2025（B） | 640 | 0.2840 | 本文高 1.21 pp | 同 RT-DETR 家族参照 |

允许写“本文报告值高于这些近期正式论文结果”，但不得写成严格配对提升或统计显著胜出。

### 5.2 近邻上界：证明不是只挑弱对手

| 方法 | 会议 | Input | val mAP50–95 | 与本文差距 | 使用边界 |
|---|---|---:|---:|---:|---|
| DM-EFS | ICCV 2025（A） | 640 | 0.2971 | 本文低 0.10 pp | 近似持平，不声称显著差异 |
| UAV-DETR-R18 | IROS 2025（B） | 640 | 0.2980 | 本文低 0.19 pp | DETR 近邻上界 |
| RAFDE | IJCAI 2025（A） | 640 | 0.3000 | 本文低 0.39 pp | 不同 YOLO/DETR 范式的强近邻 |

RAFDE 由 RAFF 和 BTRD 组成。其 YOLOv11m baseline 为 `0.266` mAP，RAFF 提高到 `0.288`，BTRD 追加后达到 `0.300`，总增益 `+3.4 pp`；完整模型为 `11.02M` Params、`72.0G` FLOPs、AP50=`0.485`。本文综合 mAP 略低，但 AP50=`0.4898` 略高。最稳表述是“本文的 DETR 路线在相同 640 输入下达到接近 IJCAI 2025 RAFDE 的综合精度，同时提供训练期零推理开销的定位蒸馏机制”。

### 5.3 同会直接对照与强协议参考

- **ResBiDet（ICASSP 2026）**：IEEE 正式摘要报告 VisDrone2019 AP50=`0.387`、UAVDT AP50=`0.402`。本文 VisDrone AP50=`0.4898`，绝对高 `10.28 pp`。由于其可访问摘要未给 split、精确双分辨率输入、mAP50–95 与完整 evaluator，只能作为同会 AP50 描述性对照。
- **VARDet（ICASSP 2026）**：VisDrone val mAP=`0.365`，但采用 ResNet-50、1333×800 和统一重实现协议。它用于说明更高分辨率上界，不与本文 640 结果计算公平差值。

外部比较的正文顺序应为：先列三个“接近且不高于本文”的 640 方法，再列三个近邻上界，最后用一句话交代 ResBiDet 和 VARDet 的协议边界。不要让高分辨率结果抢占结果段落中心。

## 6. 对抗性审计

| 审稿人最强攻击 | 风险 | 预先化解方式 | 正文证据 |
|---|:---:|---|---|
| AP-FDR 只是给 D-FINE FDR 换名 | 高 | 逐项区分“参考的基础算子”和“本文提出的结构/监督合同”；用 localization-only、stock-head preliminary、normal/DN assignment consistency 与隔离初始化说明方法差异 | AP-FDR 差异表、内部单因素消融、strict FDR 对照 |
| BPDD 只是 GO-LSD 的改名变体 | 高 | 主动承认问题启发；逐项展示 BPDD 的 all-future softmin teacher、逐边 better-only gate、stock assignment、normal-only scope 与独立损失/代码来源 | BPDD–GO-LSD 六维差异表、`src/bpdd_loss.py`、strict pair |
| 三个模块只是工程堆叠 | 高 | 用依赖关系而非数量组织：FDR 提供分布，BPDD 消费逐层分布，FIA补充 P3 表征 | A–E 消融、FIA-only、严格 BPDD 配对 |
| BPDD 只有约 0.2–0.3 pp，不值得 | 高 | 强调 val/test 同向、test AP75 `+0.276 pp`、零推理开销；不夸大绝对幅度 | strict pair + complexity 表 |
| FIA 与 BPDD 可能互相干扰 | 中 | FIA-only、FDR+FIA 和三模块均为正向；同时如实说明 FDR+FIA 的既有 cascading topology | FIA 状态表与三模块 val/test |
| 单数据集、单 seed 不能证明普适性 | 中 | 结论限定为 VisDrone；不写 universal/generalizable；用完整 test、逐类和效率补足证据深度 | val/test、10 类、复杂度 |
| 外部比较协议不一致 | 高 | 表内逐行标 split/input；近邻 640、强协议、不可排序三层分组；不宣称 SOTA | 外部 VisDrone 对比表 |
| RAFDE 参数更少且 mAP 更高 | 中 | 不回避；强调不同范式、本文 AP50 略高、BPDD 零推理开销和完整 DETR 定位贡献 | RAFDE 原表、本文 complexity |
| ResBiDet 为同会论文，为什么未比较 | 中 | 正文给 AP50 对照并披露公开摘要的缺失字段 | DOI/IEEE abstract |
| 主要涨点来自参考的基础算子，个人创新贡献有限 | 高 | 把 `+7.055 pp` 归给完整 AP-FDR，不拆分冒领；优先用 `w/o preliminary reference` 与 `w/o DN FDR supervision` 验证本文结构/监督组织，其余 no-prebox-loss/no-FGL/no-cumulative 作为后备；BPDD/FIA 再给独立正向证据 | AP-FDR 双消融、strict FDR 对照、BPDD/FIA 结果 |

审稿时最危险的不是出现 D-FINE 引用，而是把完全一致的基础公式改名后声称首次提出。正文应在 Related Work 完成一次明确归因，随后用差异表和消融把注意力锁定在 AP-FDR 的结构、监督合同及其与 BPDD/FIA 的协同上。

## 7. 可直接用于英文稿的核心文案

### 7.1 Abstract draft

Dense UAV imagery poses a coupled challenge of uncertain boundary localization, weak supervision in early decoder layers, and fragile high-resolution representations. We propose architecture-preserving fine-grained distribution refinement (AP-FDR), which introduces per-edge distribution modeling only into the localization branch while retaining the original RT-DETR classification, query assignment, decoder, and post-processing contracts. AP-FDR couples a stock-head-informed preliminary branch with assignment-consistent distribution supervision for both normal and denoising queries. Building on its layer-wise boundary distributions, we independently formulate BPDD, a training-only strategy that constructs target-conditioned teachers from all future decoder layers and activates distillation only when the teacher improves upon the current layer. A lightweight FIA module further enhances the P3 path while preserving the original P4/P5 construction. On VisDrone2019, AP-FDR improves validation mAP50–95 from 21.91% to 28.97%. BPDD provides paired validation/test gains without additional inference parameters or FLOPs, and the complete model reaches 29.61% validation mAP50–95 and 23.37% test mAP50–95 at 25.21 FPS on an RTX 4090.

### 7.2 Introduction 末段

This work studies how fine-grained boundary distributions can be reorganized into an architecture-preserving localization mechanism for dense UAV imagery. AP-FDR confines distribution refinement to the RT-DETR box path, derives its preliminary geometry from the stock regression head, and reuses the original assignments to supervise both normal and denoising queries. Its decoder produces a sequence of boundary distributions, but no single later layer is guaranteed to be the best teacher for every target edge. We therefore independently formulate and implement BPDD to select and distill quality-weighted mixtures of future distributions into earlier layers, and complement it with a lightweight P3 interaction module. The resulting framework couples localization representation, cross-layer optimization, and high-resolution context while retaining the original single-pass detection contract. The relationship between AP-FDR's underlying distribution primitives and D-FINE is stated separately in Related Work and Method.

### 7.3 Contributions

1. We propose AP-FDR, an architecture-preserving distribution refinement method that isolates fine-grained boundary regression in the RT-DETR localization branch, introduces a stock-head-informed preliminary path, and enforces assignment-consistent distribution supervision for normal and denoising queries while preserving the original detection contract.
2. We independently formulate and implement BPDD, an original training-only distillation algorithm that builds target-conditioned softmin teachers from all future decoder layers, suppresses unreliable supervision through a better-only quality gate, and reuses the stock final-layer assignment. Paired experiments confirm consistent validation/test gains without inference overhead.
3. We design a lightweight P3-only FIA module and report a positive standalone observation together with its compatibility with distribution refinement. The complete system provides competitive 640-resolution VisDrone accuracy together with unified latency and complexity measurements.

### 7.4 Related Work 中的 D-FINE 归因段

Fine-grained distribution refinement represents each box boundary with a discrete probability distribution and recovers continuous offsets through an integral operator. Inspired by the boundary representation, non-uniform integral, and fine-grained localization objective studied in D-FINE, we investigate how these primitives can be reorganized for a stock RT-DETR pipeline. AP-FDR contributes an architecture-preserving localization-only path, stock-head-informed preliminary geometry, assignment-consistent normal/denoising supervision, and an isolated initialization contract. D-FINE's GO-LSD also motivates the general question of cross-layer localization transfer; BPDD addresses that question with an independently formulated all-future softmin teacher and target-edge better-only gate rather than the final-layer DDF formulation.

### 7.5 FDR 方法小节开头

We propose AP-FDR to introduce fine-grained boundary distributions without replacing the stock RT-DETR detection pipeline. AP-FDR modifies only the localization branch and preserves the original classification heads, query selection, decoder blocks, Hungarian assignment, and post-processing. A preliminary branch initialized from the stock box head establishes shared geometry, while six isolated distribution heads predict cumulative four-edge logits. The stock per-layer assignments are reused to supervise FGL and preliminary boxes for both normal and denoising queries, avoiding a second matching process. The underlying non-uniform projection, Integral decoding, and adjacent-bin FGL follow established D-FINE primitives; our contribution lies in the architecture-preserving path, stock-head-informed geometry, assignment-consistent supervision, and isolated initialization contract. This distribution sequence further provides the representation consumed by BPDD.

### 7.6 外部结果段

At 640-pixel input resolution, our full model obtains 29.61% mAP50–95 on the VisDrone validation set. This result exceeds the reported values of TPH-YOLOv5-x with UGS (29.00%), UAV-DETR-EV2 (28.70%), and the RT-DETR-R50 reference in UAV-DETR (28.40%). It is also close to DM-EFS (29.71%), UAV-DETR-R18 (29.80%), and RAFDE (30.00%). These values are reported by the corresponding papers under their own training and evaluation settings; we use them to indicate the competitive range rather than to claim a controlled cross-paper improvement. The same-venue ResBiDet paper reports 38.7% AP50 on VisDrone2019, whereas our model reaches 48.98%; its accessible abstract does not expose mAP50–95 or a complete evaluation protocol, so this comparison is descriptive only.

## 8. 禁止句式与替代句式

| 不要写 | 改写为 |
|---|---|
| We first invent fine-grained distribution regression, FGL, or Integral. | We propose AP-FDR, whose architecture-preserving structure and assignment-consistent supervision build on previously studied distribution primitives. |
| AP-FDR is entirely unrelated to D-FINE. | AP-FDR is inspired by D-FINE's distribution primitives but introduces a distinct RT-DETR-specific structure and supervision contract. |
| BPDD is merely a renamed GO-LSD variant. | GO-LSD motivates the cross-layer localization question, whereas BPDD is independently formulated around all-future softmin teachers, better-only gating, stock assignments, and a distinct loss contract. |
| BPDD is the first-ever localization distillation method. | BPDD is an original algorithm independently formulated and implemented in this work; the priority claim is limited to its concrete mechanism and implementation. |
| Our three novel modules all improve performance. | AP-FDR, BPDD, and FIA address localization representation, cross-layer optimization, and high-resolution context, respectively; each claim is tied to its registered evidence level. |
| Our method outperforms state of the art. | Our 640-resolution result lies within the competitive range of recent CCF A/B conference methods. |
| BPDD significantly improves mAP. | BPDD produces consistent paired gains on val/test and improves test AP75 without inference overhead. |
| FIA universally enhances feature extraction. | FIA improves the evaluated P3-only configuration and remains compatible with the distribution-refined system. |
| We outperform ResBiDet by 10.28 pp. | Our reported AP50 is 10.28 points higher; the comparison is descriptive because ResBiDet's accessible abstract does not expose the full protocol. |

## 9. 投稿前最优先动作

1. 以本文件的 Abstract、Introduction 末段和 Contributions 为英文初稿，统一把 AP-FDR、BPDD、FIA 写成定位表示、跨层优化和特征表征三项创新。
2. 主图画清依赖链：FDR produces layer-wise boundary distributions → BPDD trains early layers；FIA 只增强 P3；BPDD 在推理时移除。
3. 正文只保留一张 A–E 消融表、一张外部对比表、一张复杂度表；逐类结果和拓扑审计放补充材料。
4. Results 首先报告 AP-FDR 相对 baseline 的严格结果，再报告 paired BPDD、完整系统和外部位置；AP-FDR 的内部组件只在单因素实验完成后分别归因。
5. Limitation 明确写单数据集、单 seed、基础分布算子的参考来源、尚未完成的 AP-FDR 内部消融以及跨论文协议差异。一般 B 会论文不一定要求多种子，但主动限定结论能明显降低攻击面。

本策略只能最大化证据与叙事的一致性，不能保证录用。真正影响投稿成功率的关键是：AP-FDR 的差异边界和内部消融站得住、BPDD 机制讲清楚、严格配对结果先出现、外部比较不过度、全文不出现互相冲突的数值。

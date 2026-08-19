# ICASSP 2027 创新定位、核心文案与对抗性审计

## 1. 一句话决策

论文不要把卖点写成“三个模块叠加”。FDR 应作为第一项方法创新，但创新对象必须准确落在本文提出的 AP-FDR 结构与监督组织上，而不是声称首次发明离散边界分布。最稳的中心命题是：

> 本文提出面向密集 UAV 小目标的架构保持型细粒度分布细化 AP-FDR：在不改变 RT-DETR-L 分类、查询匹配和后处理合同的条件下，以 stock-head-informed preliminary 分支及 normal/DN 匹配一致监督建立逐边分布定位；进一步提出 BPDD 使后期解码层的高质量边界分布指导早期层，并以轻量 FIA 增强 P3 表征，形成定位、优化与特征协同的完整系统。

这个表述把个人创新分成三个清晰层级：AP-FDR 是架构与监督创新，BPDD 是建立在 AP-FDR 逐层分布上的优化创新，FIA 是轻量表征创新。FDR 的 `+7.055 pp` 支持 AP-FDR 整体有效；在内部单因素消融完成前，不把该增益拆分归因给任一基础算子。

## 2. D-FINE 的处理原则

论文采用“参考并重新组织”的口径。D-FINE 只作为基础数学来源出现，AP-FDR 才是正文方法主体：

1. 标题不出现 D-FINE，使用 `architecture-preserving distribution refinement` 描述本文方法。
2. Related Work 用一句话说明：逐边离散表示、非均匀 Integral 与 FGL 基础形式参考 D-FINE。
3. Method 直接定义 AP-FDR 的四项个人设计：localization-only、stock-head-informed preliminary、normal/DN assignment consistency、private-RNG initialization contract。
4. 后续正文使用 AP-FDR；结果表因 checkpoint/config 历史标签可继续写 FDR，并在表注说明二者对应同一本文实现。
5. 贡献条目可以写 `We propose AP-FDR`，但不能写 `We first invent FDR/FGL/Integral`。

这种安排既保留必要归因，也把审稿焦点从基础算子的出处转向本文为何以新的结构和监督合同重构它们。

## 3. 推荐标题

首选：

> **Architecture-Preserving Distribution Refinement with Progressive Distillation for Dense UAV Detection**

备选：

> **AP-FDR: Architecture-Preserving Distribution Refinement for Dense UAV Object Detection**

> **Distribution-Refined RT-DETR with Boundary-Progressive Distillation and Fine-Scale Interaction for UAV Detection**

首选标题同时覆盖 AP-FDR 与 BPDD，最利于建立个人方法主线。第二个标题最突出 AP-FDR，但要求正文具备完整内部消融；第三个标题更适合保守投稿版本。

## 4. 三层贡献结构

### 贡献 1：AP-FDR 架构与监督创新

提出 AP-FDR，在不改变 RT-DETR-L 分类、查询选择、Decoder 主体、Hungarian matching 与后处理合同的条件下，将逐边分布定位限制在 localization branch。其关键设计包括从 stock 框头获得几何先验的 preliminary 分支、normal/DN 共享 stock assignment 的匹配一致监督，以及不污染公共参数随机状态的新增分布头初始化。33-bin 表示、非均匀 Integral 与 FGL 基础形式参考既有工作，不单独计为原创。

### 贡献 2：跨层优化创新 BPDD

BPDD 不引入额外教师网络，而是从同一次前向的未来解码层构造目标质量加权教师。better-only 门控只在教师优于当前层时施加 KL 监督。严格配对 best.pt 复评显示，BPDD 在 val/test 上分别提高 `+0.239/+0.283 pp` mAP50–95，test AP75 提高 `+0.276 pp`；其推理 Params、FLOPs、显存和延迟与 FDR 配对臂相同。

### 贡献 3：轻量表征互补 FIA

FIA 通过双 depth-wise 残差细化、联合通道/空间门控和零初始化残差缩放增强 P3。fresh P3-only FIA-only 在 val/test 上分别呈现 `+0.7946/+0.8101 pp` 的同 split 算术增益。FIA 只增加 `0.301M` 参数、`3.419G` FLOPs 和 `0.861 ms` 中位延迟；三模块仍达到 `25.21 FPS`。

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

Dense UAV imagery poses a coupled challenge of uncertain boundary localization, weak supervision in early decoder layers, and fragile high-resolution representations. We propose architecture-preserving fine-grained distribution refinement (AP-FDR), which confines distributional boundary regression to the localization branch while retaining the original RT-DETR classification, query assignment, decoder, and post-processing contracts. AP-FDR further couples a stock-head-informed preliminary branch with assignment-consistent distribution supervision for both normal and denoising queries. Building on its layer-wise boundary distributions, we introduce Boundary-Progressive Distribution Distillation (BPDD), a training-only strategy that constructs quality-weighted teachers from future decoder layers and activates distillation only when the teacher improves upon the current layer. A lightweight FIA module further enhances the P3 path while preserving the original P4/P5 construction. On VisDrone2019, AP-FDR improves validation mAP50–95 from 21.91% to 28.97%. BPDD provides paired validation/test gains without additional inference parameters or FLOPs, and the complete model reaches 29.61% validation mAP50–95 and 23.37% test mAP50–95 at 25.21 FPS on an RTX 4090.

### 7.2 Introduction 末段

This work studies how fine-grained boundary distributions can be reorganized into an architecture-preserving localization mechanism for dense UAV imagery. AP-FDR confines distribution refinement to the RT-DETR box path, derives its preliminary geometry from the stock regression head, and reuses the original assignments to supervise both normal and denoising queries. Its decoder produces a sequence of boundary distributions, but early layers remain less reliable than later ones. We therefore introduce BPDD to distill quality-weighted future distributions into earlier layers, and complement it with a lightweight P3 interaction module. The resulting framework couples localization representation, cross-layer optimization, and high-resolution context while retaining the original single-pass detection contract.

### 7.3 Contributions

1. We propose AP-FDR, an architecture-preserving distribution refinement method that isolates fine-grained boundary regression in the RT-DETR localization branch, introduces a stock-head-informed preliminary path, and enforces assignment-consistent distribution supervision for normal and denoising queries while preserving the original detection contract.
2. We propose BPDD, a training-only distillation mechanism that builds softmin-weighted teachers from future decoder layers and suppresses unreliable supervision through a better-only quality gate. Paired experiments confirm consistent validation/test gains without inference overhead.
3. We design a lightweight P3-only FIA module and report a positive standalone observation together with its compatibility with distribution refinement. The complete system provides competitive 640-resolution VisDrone accuracy together with unified latency and complexity measurements.

### 7.4 Related Work 中的 D-FINE 归因段

Fine-grained distribution refinement represents each box boundary with a discrete probability distribution and recovers continuous offsets through an integral operator. Inspired by the boundary representation, non-uniform integral, and fine-grained localization objective studied in D-FINE, we investigate how these primitives can be reorganized for a stock RT-DETR pipeline. Our AP-FDR differs in its architecture-preserving localization-only scope, stock-head-informed preliminary branch, assignment-consistent normal/denoising supervision, and isolated initialization contract. BPDD and FIA subsequently extend AP-FDR from the optimization and high-resolution representation perspectives.

### 7.5 FDR 方法小节开头

We propose AP-FDR to introduce fine-grained boundary distributions without replacing the stock RT-DETR detection pipeline. AP-FDR modifies only the localization branch and preserves the original classification heads, query selection, decoder blocks, Hungarian assignment, and post-processing. A preliminary branch initialized from the stock box head establishes shared geometry, while six isolated distribution heads predict cumulative four-edge logits. The stock per-layer assignments are reused to supervise FGL and preliminary boxes for both normal and denoising queries, avoiding a second matching process. This assignment-consistent distribution sequence further provides the representation consumed by BPDD.

### 7.6 外部结果段

At 640-pixel input resolution, our full model obtains 29.61% mAP50–95 on the VisDrone validation set. This result exceeds the reported values of TPH-YOLOv5-x with UGS (29.00%), UAV-DETR-EV2 (28.70%), and the RT-DETR-R50 reference in UAV-DETR (28.40%). It is also close to DM-EFS (29.71%), UAV-DETR-R18 (29.80%), and RAFDE (30.00%). These values are reported by the corresponding papers under their own training and evaluation settings; we use them to indicate the competitive range rather than to claim a controlled cross-paper improvement. The same-venue ResBiDet paper reports 38.7% AP50 on VisDrone2019, whereas our model reaches 48.98%; its accessible abstract does not expose mAP50–95 or a complete evaluation protocol, so this comparison is descriptive only.

## 8. 禁止句式与替代句式

| 不要写 | 改写为 |
|---|---|
| We first invent fine-grained distribution regression, FGL, or Integral. | We propose AP-FDR, whose architecture-preserving structure and assignment-consistent supervision build on previously studied distribution primitives. |
| AP-FDR is entirely unrelated to D-FINE. | AP-FDR is inspired by D-FINE's distribution primitives but introduces a distinct RT-DETR-specific structure and supervision contract. |
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

# ICASSP 2027 创新定位、核心文案与对抗性审计

## 1. 一句话决策

论文不要把卖点写成“三个模块叠加”，也不要把 FDR 包装成从零发明。最稳的中心命题是：

> 本文构建了一个面向密集 UAV 小目标的 distribution-refined RT-DETR，并提出训练期 BPDD，使后期解码层的高质量边界分布反向指导早期层；FIA 以轻量 P3 增强补充分布定位基础，在几乎不破坏实时性的条件下形成完整系统。

这个表述把个人创新集中在“如何围绕分布定位建立新监督与新表征协同”，而不是争夺 FDR 基础算子的发明权。FDR 的 `+7.055 pp` 是系统成立的强实验证据；BPDD 是主要原创机制；FIA 是轻量互补机制。

## 2. D-FINE 的处理原则

“降低 D-FINE 存在感”只能降低叙事中心度，不能删除归因。安全做法是：

1. 标题不出现 D-FINE，摘要用 `distribution-refined localization` 描述技术基础。
2. Related Work 清楚说明一次：细粒度分布表示、Integral 和 FGL 源自 D-FINE。
3. Method 的 FDR 小节开头再说明一次：本文将该定位形式适配到 Ultralytics RT-DETR-L/VisDrone，并保持 stock matching、DN 与推理合同。
4. 后续正文直接使用 FDR 缩写，不反复讲实现谱系；贡献条目不写“we propose FDR”。
5. 个人贡献写成围绕 FDR 的新机制：BPDD 使用六层累计四边分布构造未来层 softmin 教师，FIA 在高分辨率路径补充分布定位所需表征，完整系统给出统一 val/test 与效率证据。

这样既不会因隐藏来源触发学术诚信质疑，也不会让整篇论文变成 D-FINE 的复现报告。

## 3. 推荐标题

首选：

> **Boundary-Progressive Distribution Distillation for Dense UAV Object Detection**

备选：

> **Distribution-Refined RT-DETR with Boundary-Progressive Distillation and High-Resolution Interaction for UAV Object Detection**

> **BPDD-RTDETR: Progressive Boundary Distribution Learning with Fine-Scale Interaction for UAV Object Detection**

首选标题最利于突出个人创新。第二个标题更完整，但会让审稿人更早追问 distribution refinement 的来源；第三个标题工程感更强，适合正文已经压缩得很紧时使用。

## 4. 三层贡献结构

### 贡献 1：任务化系统贡献

将连续框回归改造成适合密集 UAV 小目标的逐边分布定位路径，并在 RT-DETR-L 中完成 preliminary box、六层累计细化、normal/DN FGL、stock matching 复用与统一推理接口。这里的贡献是可靠适配和任务化系统，不是 FDR/FGL/Integral 的首次提出。

### 贡献 2：主要方法创新 BPDD

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
| FDR 直接来自 D-FINE，论文只是移植 | 高 | 主动归因；把原创中心放在 BPDD 和 FDR-aware FIA；说明适配合同而非冒领基础算子 | FDR 适配边界、BPDD 新公式、FIA 结构 |
| 三个模块只是工程堆叠 | 高 | 用依赖关系而非数量组织：FDR 提供分布，BPDD 消费逐层分布，FIA补充 P3 表征 | A–E 消融、FIA-only、严格 BPDD 配对 |
| BPDD 只有约 0.2–0.3 pp，不值得 | 高 | 强调 val/test 同向、test AP75 `+0.276 pp`、零推理开销；不夸大绝对幅度 | strict pair + complexity 表 |
| FIA 与 BPDD 可能互相干扰 | 中 | FIA-only、FDR+FIA 和三模块均为正向；同时如实说明 FDR+FIA 的既有 cascading topology | FIA 状态表与三模块 val/test |
| 单数据集、单 seed 不能证明普适性 | 中 | 结论限定为 VisDrone；不写 universal/generalizable；用完整 test、逐类和效率补足证据深度 | val/test、10 类、复杂度 |
| 外部比较协议不一致 | 高 | 表内逐行标 split/input；近邻 640、强协议、不可排序三层分组；不宣称 SOTA | 外部 VisDrone 对比表 |
| RAFDE 参数更少且 mAP 更高 | 中 | 不回避；强调不同范式、本文 AP50 略高、BPDD 零推理开销和完整 DETR 定位贡献 | RAFDE 原表、本文 complexity |
| ResBiDet 为同会论文，为什么未比较 | 中 | 正文给 AP50 对照并披露公开摘要的缺失字段 | DOI/IEEE abstract |
| FDR 是主要涨点，BPDD/FIA 增益小 | 高 | 将论文问题定义为“以可靠分布定位为基础，如何继续改善早层监督和高分辨率表征”，而非三个等权模块 | FDR `+7.055 pp`、两个附加模块稳定正向 |

审稿时最危险的不是承认 D-FINE，而是审稿人自己发现来源后认为论文故意模糊。主动用一两句完成归因，反而能把后续讨论锁定在 BPDD、FIA、严格配对与效率证据上。

## 7. 可直接用于英文稿的核心文案

### 7.1 Abstract draft

Dense UAV imagery poses a coupled challenge of uncertain boundary localization, weak supervision in early decoder layers, and fragile high-resolution representations. We develop a distribution-refined RT-DETR framework that addresses these factors without relying on multi-crop inference. Its central contribution is Boundary-Progressive Distribution Distillation (BPDD), a training-only strategy that constructs quality-weighted teachers from future decoder-layer boundary distributions and activates distillation only when the teacher improves upon the current layer. We further introduce a lightweight FIA feature-enhancement module on the P3 path to strengthen small-object features while preserving the original P4/P5 construction. On VisDrone2019, the distribution-refined detector improves validation mAP50–95 from 21.91% to 28.97%. Under a same-source, same-seed paired protocol, BPDD further improves validation and test mAP50–95 by 0.24 and 0.28 points, respectively, with no additional inference parameters or FLOPs. The complete model reaches 29.61% validation mAP50–95 and 23.37% test mAP50–95, while retaining 25.21 FPS in batch-1 FP32 inference on an RTX 4090. These results show that progressive distribution supervision and fine-scale feature interaction provide complementary gains for dense UAV object detection.

### 7.2 Introduction 末段

This work studies how a distribution-refined detector can be specialized for dense UAV imagery beyond a direct replacement of the box regression head. The key observation is that the decoder already produces a sequence of increasingly informative boundary distributions, yet early layers are optimized mainly through conventional layer-wise supervision. We therefore treat later-layer distributions as an internal source of localization knowledge and distill them progressively into earlier layers. This training mechanism is complemented by a lightweight P3 interaction module that improves fine-scale representation before decoding. The resulting design couples localization representation, optimization, and high-resolution context while preserving a compact single-pass inference pipeline.

### 7.3 Contributions

1. We establish a distribution-refined RT-DETR formulation for dense UAV detection, including preliminary-box supervision, cumulative boundary refinement, normal and denoising-query losses, and a unified inference contract.
2. We propose BPDD, a training-only distillation mechanism that builds softmin-weighted teachers from future decoder layers and suppresses unreliable supervision through a better-only quality gate. Paired experiments confirm consistent validation/test gains without inference overhead.
3. We design a lightweight P3-only FIA module and report a positive standalone observation together with its compatibility with distribution refinement. The complete system provides competitive 640-resolution VisDrone accuracy together with unified latency and complexity measurements.

### 7.4 Related Work 中的 D-FINE 归因段

Fine-grained distribution refinement represents each box boundary with a discrete probability distribution and recovers continuous offsets through an integral operator. D-FINE introduced this formulation together with fine-grained localization supervision for DETR-style detection. We adopt this localization basis rather than claiming it as a new component, and focus on two UAV-specific extensions: progressive cross-layer distribution distillation during training and lightweight fine-scale feature interaction before decoding.

### 7.5 FDR 方法小节开头

We first instantiate fine-grained distribution refinement in the Ultralytics RT-DETR-L pipeline. Each decoder layer predicts four 33-bin boundary distributions relative to a shared preliminary box, and cumulative logits are decoded by a non-uniform integral operator. The adaptation preserves the original Hungarian assignment and augments both normal and denoising queries with distribution and preliminary-box supervision. This module serves as the localization substrate for BPDD; the proposed distillation mechanism is described in the next subsection.

### 7.6 外部结果段

At 640-pixel input resolution, our full model obtains 29.61% mAP50–95 on the VisDrone validation set. This result exceeds the reported values of TPH-YOLOv5-x with UGS (29.00%), UAV-DETR-EV2 (28.70%), and the RT-DETR-R50 reference in UAV-DETR (28.40%). It is also close to DM-EFS (29.71%), UAV-DETR-R18 (29.80%), and RAFDE (30.00%). These values are reported by the corresponding papers under their own training and evaluation settings; we use them to indicate the competitive range rather than to claim a controlled cross-paper improvement. The same-venue ResBiDet paper reports 38.7% AP50 on VisDrone2019, whereas our model reaches 48.98%; its accessible abstract does not expose mAP50–95 or a complete evaluation protocol, so this comparison is descriptive only.

## 8. 禁止句式与替代句式

| 不要写 | 改写为 |
|---|---|
| We propose a novel FDR module. | We instantiate a distribution-refined localization basis and build BPDD upon its layer-wise boundary distributions. |
| Our three novel modules all improve performance. | BPDD is the primary new training mechanism; FIA provides a lightweight complementary feature path on the adapted distribution-refined detector. |
| Our method outperforms state of the art. | Our 640-resolution result lies within the competitive range of recent CCF A/B conference methods. |
| BPDD significantly improves mAP. | BPDD produces consistent paired gains on val/test and improves test AP75 without inference overhead. |
| FIA universally enhances feature extraction. | FIA improves the evaluated P3-only configuration and remains compatible with the distribution-refined system. |
| We outperform ResBiDet by 10.28 pp. | Our reported AP50 is 10.28 points higher; the comparison is descriptive because ResBiDet's accessible abstract does not expose the full protocol. |

## 9. 投稿前最优先动作

1. 以本文件的 Abstract、Introduction 末段和 Contributions 为英文初稿，统一全文主语与贡献层级。
2. 主图画清依赖链：FDR produces layer-wise boundary distributions → BPDD trains early layers；FIA 只增强 P3；BPDD 在推理时移除。
3. 正文只保留一张 A–E 消融表、一张外部对比表、一张复杂度表；逐类结果和拓扑审计放补充材料。
4. Results 首先报告 strict paired BPDD，再报告完整系统，最后报告外部位置。不要先用 FDR 的大涨点淹没 BPDD。
5. Limitation 明确写单数据集、单 seed、FDR 继承来源以及跨论文协议差异。一般 B 会论文不一定要求多种子，但主动限定结论能明显降低攻击面。

本策略只能最大化证据与叙事的一致性，不能保证录用。真正影响投稿成功率的关键是：归因无漏洞、BPDD 机制讲清楚、严格配对结果先出现、外部比较不过度、全文不出现互相冲突的数值。

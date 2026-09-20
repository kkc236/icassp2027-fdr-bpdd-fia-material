> 当前章节与证据位置以EVIDENCE_FOCUS_DECISIONS_ZH.md为准；本文件保留相应前版的研究和命名依据。

# 论文命名统一：GCDL 与 LQS

## 1. 先纠正来源判断

本轮查阅 [D-FINE 的 ICLR 2025 正式全文](https://proceedings.iclr.cc/paper_files/paper/2025/file/6cf58a87e3097e7d1f9be3e8693a93de-Paper-Conference.pdf)及[作者官方说明](https://github.com/Peterande/D-FINE/blob/master/README.md)。其两个主要方法名为 FDR（Fine-grained Distribution Refinement）和 GO-LSD（Global Optimal Localization Self-Distillation）。对该正式PDF可检索全文搜索 LRS 未发现匹配。

当前项目旧名 LRS 表示 Layerwise Reliability Shrinkage，是本文对同图同层 IoU 权重向均值收缩的命名。它与 GO-LSD 的跨解码层分布自蒸馏不同。因此，本轮改名的依据是辨识度、术语准确性和层级清晰度，而非确认旧名抄用了 D-FINE 的一个正式模块。

## 2. 采用的命名体系

| 层级 | 原展示名 | 当前展示名 | 含义和边界 |
|---|---|---|---|
| 作者定位设计整体 | LRS-GFDR | **Geometry-Constrained Distributional Localization（GCDL）** | **几何约束分布定位**；包括incoming-reference/监督路径设计、几何可行解码和LQS，不仅是一个修正框尺寸的函数 |
| 训练权重规则 | Layerwise Reliability Shrinkage（LRS） | **Layerwise Quality Shrinkage（LQS）** | **逐层质量权重收缩**；quality具体指detach后的匹配框IoU，收缩对象是FGL权重相对组均值的差异 |
| 几何算子 | GFDR在不同历史材料中被宽泛使用 | **geometry-feasible decoding** | 直接写“几何可行解码”，不再额外造一套缩写 |
| 定位损失描述 | LRS-FGL | **FGL with LQS** | 明确FGL继承自D-FINE，本文改变其eligible权重 |
| 作者路径变体 | Clean-FDR（已在上一轮退出主文） | **Path redesign** | 继续保留，属于作者组内定位变体，不是外部原生FDR基线 |
| 局部视觉扩展 | B/F及历史BPDD/FIA运行名 | **box-conditioned expert / shared P3 refinement** | 正文用直观功能描述，表格与公式保留简短B/F符号，不增加新品牌名 |
| 完整配置 | Full | **Full（G+B+F）** | 与定位核心GCDL区分：G本身29.620 val AP，Full30.109，不能把它们当同一个checkpoint |

新标题：**GCDL: Geometry-Constrained Distributional Localization for UAV Detection**。

注意 distributional 此处指边界位置的概率分布，中文用“分布定位”，不使用容易被理解为分布式计算的“分布式定位”。

## 3. 选择理由

- **总名覆盖定位设计整体。** 旧名把LRS与FDR拼接，容易把作者路径改写、几何规则和训练监督读成一个外围附加项。GCDL用一个总名，首次定义中明确三个组成部分。
- **quality更贴近实际量。** 权重是matched-box IoU，并非经过校准的可靠性或不确定度。LQS保留shrinkage这一准确的数学操作名，同时把quality和loss weights的关系写清。
- **少造缩写。** 核心GCDL、规则LQS足够；几何算子、专家、共享P3用描述名。G/B/F是表格和公式的配置符号，不是另外三种方法品牌。
- **归属不随改名改变。** FDR、FGL和GO-LSD保留D-FINE原名及引用；离散边分布、非均匀支撑、积分、累计细化、固定分布坐标系和基础FGL仍明确归属原工作。

LQS只在同一图像、同一解码层内收缩符合条件的IoU权重；收缩强度随层深减弱。它既不跨层混合权重，也不把所有权重都减小：低于均值者可以增加。新名不改变公式或实验。

## 4. 撞名检索范围

2026-09-17检索了两个英文全称、GCDL与object detection/localization组合，以及LQS与DETR组合。本次未检出上述英文全称的同名DETR方法。GCDL这个缩写已在其他问题中使用，例如[组织病理图像论文的group-convolution模块](https://pmc.ncbi.nlm.nih.gov/articles/PMC12325580/)；不能宣称这四个字母在所有领域唯一。采用完整展开名、任务标题和清楚的首次定义，比追求跨领域缩写独占更实际。本检索不用于主张方法本身的绝对新颖性。

## 5. 已同步范围与追溯

标题及PDF元信息、摘要/引言定义、方法与结论、全部表格、图2/图3标签和图注、README及当前验收信息均同步。

原训练文件、冻结代码、权重、原始CSV/JSON、运行ID和历史审稿记录保持不变。内部文件名lrs.tikz、LaTeX引用标签以及原始证据中的LRS仍用于追溯，不出现在PDF展示名中。映射见 inputs/publication_name_mapping.json。

本次只是论文术语及相应说明调整：没有改变模型、公式、实验协议、AP数值或成本数据。旧版完整工程仍在cvm_experiment_design_20260917目录。

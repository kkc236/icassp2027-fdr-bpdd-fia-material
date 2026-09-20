# 近期检测论文的实验组织：基线身份、消融、负结果与效率

检索与核验日期：2026-09-17。本文是写作与证据组织研究笔记，不是对当前稿件的结果认证，不据此推断论文录用原因。未改稿、未训练、未访问训练服务器。

## 1. 有界检索范围与版本

本次定向检查七篇一手材料：四篇已读 CVM 检测论文，加上与 RT-DETR 直接相关的 D-FINE、DEIM、DEIMv2。这是有目的的比较样本，不是系统综述或全部近期 DETR 工作的排名。CVM 全文复用旧研究目录；新增三篇阅读方法、实验与可得附录，重点复核下表位置，并查看 D-FINE p.9、DEIM p.8 和补充材料 p.1 的原始版面。正文页码均指 **PDF 的物理页码**，DEIM 同时给出论文集页码。

| 材料与核实身份 | 采用版本、官方出处 | 实际重点核对范围 |
|---|---|---|
| FGHDet，CVM 2025 官网收录 | [官方 PDF](https://iccvm.org/2025/papers/s8p2-368-jcst.pdf)，14 页；[2025 官方议程](https://iccvm.org/2025/program.htm) | §5，pp.7–12；Tables 2、4–6；训练输入、验证/测试划分与分步配置 |
| DASSF，CVM 2025 官网收录 | [官方 PDF](https://iccvm.org/2025/papers/lncs/813.pdf)，11 页；同上议程 | §4，pp.5–10；Tables 1–6；全组合消融、跨模型迁移与 FPS |
| LME-DETR，CVM 2026 官网收录 | [官方 PDF](https://iccvm.org/2026/files/papers/265.pdf)，14 页；[2026 官方议程](https://iccvm.org/2026/program.htm)，Poster 2 / P38 | §4，pp.8–12；Tables 1–4；渐进消融、尺寸指标和效率口径 |
| SD-Net，CVM 2026 官网收录 | [官方 PDF](https://iccvm.org/2026/files/papers/691.pdf)，14 页；同上议程，Poster 2 / P37 | §4，pp.8–12；Tables 1–4；P2 底座、局部 strong baseline 与位置实验 |
| D-FINE，ICLR 2025 | [官方论文身份页](https://proceedings.iclr.cc/paper_files/paper/2025/hash/6cf58a87e3097e7d1f9be3e8693a93de-Abstract-Conference.html)、[会议终版 PDF](https://proceedings.iclr.cc/paper_files/paper/2025/file/6cf58a87e3097e7d1f9be3e8693a93de-Paper-Conference.pdf)，17 页 | §§5–6，pp.6–10；Appendix A，pp.14–17；Tables 1、3–7、9 |
| DEIM，CVPR 2025 | [CVF 身份页](https://openaccess.thecvf.com/content/CVPR2025/html/Huang_DEIM_DETR_with_Improved_Matching_for_Fast_Convergence_CVPR_2025_paper.html)、[正式 PDF](https://openaccess.thecvf.com/content/CVPR2025/papers/Huang_DEIM_DETR_with_Improved_Matching_for_Fast_Convergence_CVPR_2025_paper.pdf)，10 页 / pp.15162–15171；[官方补充材料](https://openaccess.thecvf.com/content/CVPR2025/supplemental/Huang_DEIM_DETR_with_CVPR_2025_supplemental.pdf)，3 页 | §4，PDF pp.5–8；Tables 1–8；补充材料全文，尤其 §3 与 Tables 9–13 |
| DEIMv2，预印本 | 正式题名 *Real-Time Object Detection Meets DINOv3*；[arXiv 记录](https://arxiv.org/abs/2509.20787)，初稿 2025-09-25；采用 [v4 PDF](https://arxiv.org/pdf/2509.20787v4)，2026-01-26，7 页 | §§2–3，pp.2–6；Tables 1–4；模型族配置、训练条件、尺寸收益边界 |

身份限制：DEIMv2 的 arXiv、作者项目页/仓库及作者出版记录均纳入身份检索；本次未核实正式会议或期刊身份，因此只能按上述预印本版本引用。作者记录中 TMLR 2026 的 EdgeCrafter 是另一项工作。CVM 议程收录也不等于本文对其每项实验论证的认可。

版本限制：D-FINE 的 arXiv 初稿与会议终版表号不同，以下全部采用会议终版。DEIM 的 CVF HTML 摘要与正式 PDF 有数值差异，本文以正式 PDF 表格为准，不混用网页摘要。

## 2. 八条可直接迁移的写法

### 2.1 把 baseline 写成可恢复的配置身份

**一手依据。** SD-Net Table 3 / §4.4（p.11）从 YOLOv11-s 出发，先增加 P2；Table 4 的 caption 则明确规定其 strong baseline 已含 P2、SC2f 和 S2B。两张表里的“基线”所指不同。DEIM 补充材料 §3（p.1）说明，BN、学习率调度和 decoder 激活的调整构成其新的实验 baseline；还报告这些调整在 L 上无 AP 增益，在 X 上只有小幅增益。[SD-Net](https://iccvm.org/2026/files/papers/691.pdf#page=11)；[DEIM 补充材料](https://openaccess.thecvf.com/content/CVPR2025/supplemental/Huang_DEIM_DETR_with_CVPR_2025_supplemental.pdf#page=1)

**可迁移写法。** 定义三个角色，而不是把三个词当作同义词：

- 原始方法的本地复现：方法名、骨干、配置版本、训练配方和数据划分均可追溯。
- 作者自建 Base：逐项列出相对原始方法的架构及训练修改；不给“原生 RT-DETR”身份。
- 某项局部实验的固定底座：表注完整写出已启用组件；“strong”只是一种相对描述，不是标准认证。

正文首次出现就说明自建 Base。仅在附录深处说明虽然有文献先例，却不适合当前需要消除基线疑问的稿件。没有相应对照时，用“modified base configuration”比暗示已证明更强的命名准确。

### 2.2 分开交代“怎样得到底座”与“新增模块带来什么”

**一手依据。** D-FINE Table 4（p.9）将 RT-DETR-HGNetv2-L 到最终模型的结构、训练及新增方法分步列出，保留 AP 下降的中间步骤。Table 5 / §5.4.2 同页明确不使用那些轻量化修改，专门比较蒸馏方法。因此，两表同名组件的 AP 不同具有已声明的配置原因。[D-FINE 终版](https://proceedings.iclr.cc/paper_files/paper/2025/file/6cf58a87e3097e7d1f9be3e8693a93de-Paper-Conference.pdf#page=9)

**可迁移写法。** 若已有记录足够，用一张配置说明表交代“原始复现→作者 Base”；另一张结果表在固定 Base 上组织新组件。每张表注明共同继承的改动。相同 AP 不能证明两个底座相同，差异 AP 也不能在检查配置前被直接判断为错误。

**适用边界。** 不必为表格形式重新训练。已有原始模型记录不足时，可清楚给出配置差异与证据缺口，但不能把未测的中间行补成结果，也不能把总增益全部归给最后新增的模块。

### 2.3 消融名称要揭示参照点，主张要符合组合覆盖范围

**一手依据。** FGHDet Table 6（p.9）用 `+Tiny+DSIEM+RLH` 显示继承关系；DASSF Table 4（p.8）列出三个组件的全部八种开关组合。LME-DETR Table 4（p.11）caption 明说逐步加入组件，只能观察给定路径上的增量。SD-Net Table 3（p.11）没有覆盖全部二组件组合，因此其“任意两种组合”式概括超出了表内覆盖。[FGHDet](https://iccvm.org/2025/papers/s8p2-368-jcst.pdf#page=9)；[DASSF](https://iccvm.org/2025/papers/lncs/813.pdf#page=8)；[LME-DETR](https://iccvm.org/2026/files/papers/265.pdf#page=11)；[SD-Net](https://iccvm.org/2026/files/papers/691.pdf#page=11)

**可迁移写法。** 保留简洁的组件列，再配稳定配置编号。`Base+A+B` 表示从共同 Base 出发；`Full−A` 表示从完整模型删除 A，二者回答的问题不同。逐步增加组件可写“在该配置上增加 A 后……”，不能写成 A 的无条件独立贡献。没有完整交互对照时，不用“协同已证实”代替“所测组合中最好”。

即使有全组合表，没有重复实验的不确定性估计，也不要把细小差值称作统计显著。

### 2.4 影响核心设计选择的负结果留在主文，扩展扫描可放附录

**一手依据。** SD-Net Table 4（p.11）在主文保留 HCB 扩展到更多尺度后精度回落、成本增加的结果，直接解释部署位置。DEIM Table 4（PDF p.7 / 15168）保留 24 epoch 下 mixup 单独使用不如无增强的行；补充材料 Table 12（p.2）保留目标数量继续增大后 AP 回落的扩展实验。D-FINE 的超参数扫描见 Appendix A.4 / Table 9（p.17），而结构选择路线留在主文。[SD-Net](https://iccvm.org/2026/files/papers/691.pdf#page=11)；[DEIM 主文](https://openaccess.thecvf.com/content/CVPR2025/papers/Huang_DEIM_DETR_with_Improved_Matching_for_Fast_Convergence_CVPR_2025_paper.pdf#page=7)；[DEIM 补充材料](https://openaccess.thecvf.com/content/CVPR2025/supplemental/Huang_DEIM_DETR_with_CVPR_2025_supplemental.pdf#page=2)；[D-FINE 附录](https://proceedings.iclr.cc/paper_files/paper/2025/file/6cf58a87e3097e7d1f9be3e8693a93de-Paper-Conference.pdf#page=17)

**可迁移写法。** 主文保留决定最终架构/配置的反例，以及主要指标和关键尺寸指标的退步；附录承担完整网格、更多规格、次要细节。正文概述“在哪项指标或哪种配置退步”，不必逐个为负结果编造原因。负结果的解释若没有诊断证据，应标为可能原因。

“有论文把某项结果放补充材料”不能成为隐藏直接削弱本文核心主张的依据。若整块消融总收益小或部分配置下降，主文至少保留这一事实与对应入口。

### 2.5 把训练预算与预训练条件当作对照条件

**一手依据。** DEIM Table 6（PDF p.8 / 15169）把 72 epoch 原方法和 36 epoch 增强方法放在一起；Table 7 另列每 epoch 及总 GPU 小时。这个组合主要服务于收敛效率论证。D-FINE Table 1（p.7）将 Objects365 预训练结果另分一组，Appendix Table 6（p.14）具体列训练配方。[DEIM](https://openaccess.thecvf.com/content/CVPR2025/papers/Huang_DEIM_DETR_with_Improved_Matching_for_Fast_Convergence_CVPR_2025_paper.pdf#page=8)；[D-FINE](https://proceedings.iclr.cc/paper_files/paper/2025/file/6cf58a87e3097e7d1f9be3e8693a93de-Paper-Conference.pdf#page=7)

**可迁移写法。** 表注明确固定哪些条件：数据划分、初始化、输入变换、训练周期、训练配方和 checkpoint 选择规则。涉及多种配方时给每种配方独立标记。不同训练预算的比较可以证明实用性能或收敛优势，不能未经说明就当成“唯一变化是模块 A”的消融。

不能只凭 epoch 数推断训练成本相等；缓存、增强、batch、设备和每步工作量都会影响时间。当前若没有可靠训练计时，就报告已有预算信息，不估造 GPU 小时。

### 2.6 效率表必须绑定具体模型配置及计时范围

**一手依据。** D-FINE §5.1 / Fig.1（pp.6、1）说明 T4、TensorRT FP16 和端到端 latency；主表并列参数、GFLOPs 和 latency。DEIMv2 Table 3（p.5）显示，X 规格相对 DEIM-X 的 FLOPs 更少，latency 却更高；§3（pp.4–5）也承认延迟尚未优化。LME-DETR Tables 1、3（pp.9、11）虽列输入、参数、GFLOPs 和 FPS，§4.1 对 FPS 测试过程仍不够完整。[D-FINE](https://proceedings.iclr.cc/paper_files/paper/2025/file/6cf58a87e3097e7d1f9be3e8693a93de-Paper-Conference.pdf#page=6)；[DEIMv2 v4](https://arxiv.org/pdf/2509.20787v4#page=5)；[LME-DETR](https://iccvm.org/2026/files/papers/265.pdf#page=9)

**可迁移写法。** 精度与效率行使用同一明确配置标识；效率表注列输入、batch、硬件、精度、后端，以及是否包括预处理/后处理。统计口径也应说明，例如预热、同步和汇总方式。只报告前向耗时时直称前向耗时；不能借已有“端到端”论文标题扩大自己的计时范围。

参数量、运算量和实测时间是三个不同证据。没有计时证据不能把 FLOPs 下降改写为速度提升，也不能把 batch 吞吐换称单图 latency。这里对完整计时协议的建议是本笔记的可复现性要求；所读论文并非都提供了上述全部细节。尤其 DEIMv2 不能作为省略协议的正面范例。

### 2.7 预先固定主指标，再解释尺寸指标与代价

**一手依据。** DASSF Table 6（p.9）在 DIOR 上的 YOLOv7tiny 迁移出现 AP50 下降、AP50:95 上升；因此不能照搬其“所有指标普遍改善”的概括。DEIMv2 §3 / Table 3（p.5）把主要收益限定在中大目标，小目标收益较弱。SD-Net Table 3（p.11）把精度和参数/FLOPs放在同表，让读者直接看到代价。[DASSF](https://iccvm.org/2025/papers/lncs/813.pdf#page=9)；[DEIMv2 v4](https://arxiv.org/pdf/2509.20787v4#page=5)；[SD-Net](https://iccvm.org/2026/files/papers/691.pdf#page=11)

**可迁移写法。** 总体检测以明确的 AP 定义作主指标；小目标论文紧邻呈现 AP_S，并保留 AP50/AP75 等必要诊断列。正文先说主指标变化，再说尺寸收益是否一致，最后说成本。不要在不同表之间反复换用最有利的指标来定义“最好”。主指标相同而细分指标有差异时，直接说明取舍。

“提升 x 个百分点”与“相对提升 x%”分别计算、标识。GT 在网络输入尺度上的尺寸统计也不能直接替代 evaluator 在原图面积定义下的 AP_S；前者解释任务难点，后者是性能评估，两者承担不同职责。

### 2.8 每张表固定一个问题，并让同一结果跨表可追踪

**一手依据。** FGHDet Tables 5、6（p.9）在 caption 区分 VisDrone validation 和 test，Table 6 同时固定 640 输入；DEIM Tables 1、2、3、8 分别处理实时模型、ResNet 系列、CrowdHuman 和额外预训练。这种分组保留比较条件。[FGHDet](https://iccvm.org/2025/papers/s8p2-368-jcst.pdf#page=9)；[DEIM](https://openaccess.thecvf.com/content/CVPR2025/papers/Huang_DEIM_DETR_with_Improved_Matching_for_Fast_Convergence_CVPR_2025_paper.pdf#page=6)

**可迁移写法。** 主比较表回答最终性能；组件表回答在已定义 Base 上的条件增益；设计选择表回答为什么采用这个实现；效率表回答成本。可共享配置标识，避免每张表重新定义同名模型。数据集、划分和分辨率写在读表时可见的位置，不藏在远处的段落。

这里可学习的是比较边界，不能照搬 FGHDet 的测试集消融去增加当前稿的内部 test。当前无 UAVDT 实验就只写适用范围与未来工作，不能以其他论文的多数据集组织代替自身尚不存在的结果。

## 3. 不应照搬的做法与具体核对点

下列问题是本次表内/表间核对所得，不推断作者动机，也不说明论文整体无效：

| 核对点 | 原文定位 | 本稿应采取的原则 |
|---|---|---|
| 同名基线数值不一致且未在邻近文字充分解释：DASSF 的 YOLOv8n 在 Tables 1/4 与 Table 6 的 VisDrone 行不同 | pp.6、8、9 | 同一运行只建立一份结果记录；若实际配方不同，用不同配置名并解释 |
| LME-DETR 的 baseline AP_M/AP_L 在 Table 2 与 Table 4 不同 | pp.9、11 | 不能仅因为来自已收录论文就接受跨表不一致；必须回到原始记录核验 |
| FGHDet 最终配置参数 43.9M 高于原 baseline 37.2M，局部删头节省不等于最终模型更小 | Tables 5、6，p.9 | 分清“某一步降低成本”和“最终整体成本”；不能扩大局部结论 |
| SD-Net 组件组合覆盖不足以支持“任意两种组合” | §4.4 / Table 3，p.11 | 改成“所测配置中”；没有测过的组合不隐含为已比较 |
| DASSF 部分迁移指标实际下降 | §4.5 / Table 6，p.9 | 不能用总体趋势抹去明确的反例 |
| DEIM 把新 baseline 细节放补充材料；Table 6 的训练周期不同 | 补充 §3 p.1；主文 p.8 | 主文直接披露关键底座差异，区分收敛比较和同预算消融 |
| DEIMv2 主文陈述轻量模型移除部分损失的原因，但未给对应量化消融表；其表格也不是完整的组件因果实验 | §2 p.4，Tables 1–4 | 可以引用为设计观察，不能当作已量化的普遍机制证据；参数/FLOPs减少不代表实测更快 |

上述定位链接分别见第 1 节官方 PDF。D-FINE Table 4 与 Table 5 的差异则属于**已有明确配置解释的不同实验**，与前两项未解释的一致性问题应区别处理。

## 4. 对当前稿件的最小可执行编辑结论

在不重训、不增加内部 test 或逐图可视化的约束下，优先完成以下证据整理即可：

1. 给原始方法复现、自建 Base、完整方法分别定义稳定身份；逐项列明继承关系。
2. 把现有消融重新命名为实际测过的配置，区分逐步增加、从完整模型删除和实现替换。
3. 把已有负结果及成本增长放到解释最终选择的位置；不为未测组合补结论。
4. 在所有主表中固定主指标定义、数据划分与配置身份；每个重复结果都回指同一记录。
5. 把效率结论收敛到现有实测协议能够支持的范围；配置或协议不匹配时明确说明，不能拼成一条“精度—速度”结果。
6. 将多数据集泛化、额外配方控制等尚无证据的主张收窄，UAVDT 保持未来工作身份。

这些是从样本文献中归纳的写作与证据管理建议，不是要求把所有论文的实验数量叠加到当前稿，也不构成“遵循即可录用”的判断。

## 5. 本地材料与复查入口

- 已有四篇 CVM PDF/全文文本复用：`output/cvm_literature_architecture_20260917/research/sources/`。
- LME/SD 的早先全文研究笔记：`output/cvm_literature_architecture_20260917/research/AERIAL_2026_ZH.md`。
- 新增官方 PDF、布局文本和本次重点表格的渲染只用于临时核验，位于系统临时目录 `cvm_experiment_practices_20260917`；可长期引用的准确 URL 与版本已在本文记录。
- 本次没有为身份检索结果中的其他相邻检测论文扩张样本，没有使用博客/排行榜作为技术结论的来源。

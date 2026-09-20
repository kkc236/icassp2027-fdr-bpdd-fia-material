# 独立 CVM 审稿记录

审稿角色：严格 CVM 审稿人。日期：2026-09-17。

范围：只读审查正文、表格生成源及已有证据；不更改正文、数据、权重，不训练或重新评估模型。本文件记录改稿过程中的审稿意见；条目是否已经处理，应以最终正文和主审汇总为准。

## 第一轮：竞争力、贡献主次与证据结构

### 核心判断

原版本的准确性边界较完整，但正文偏实现交接和证据审计。完整系统的较大收益先出现，LRS-GFDR 相对完整 FDR/FGL 移植的主比较较晚；容易让读者将作者原创定位设计理解为移植后的附属数值修补。

可成立的统一主线是：分布定位既需要细粒度表达，也需要可行的几何解码和明确的逐层监督分配。LRS-GFDR 对这两个接口作出设计；局部专家在共同的分布参考框内扩展定位核心。该主线不能扩大为几何错误在正式航拍预测中普遍发生、训练收敛已获证明或每项修改独立提升 AP。

### P0：已建议的主要重构

1. 将 Original FDR → LRS-GFDR 作为主要定位比较，提前于完整系统的较大收益；全部 Clean 中间行保留。
2. 方法先定义设计和数学，再由机制表和实验解释 Original、Clean、preliminary 和额外 DN-FDR 监督的历史配置区别。
3. 协议差异、历史对照限制和 test 可见性等事实集中披露；删减逐段重复的防御性解释，但不删除任何实质限制。
4. 将几何贡献描述为显式可行性要求和明确的反向优化选择。几何的解析性质、受控数值回归、AP 观察属于不同证据。
5. 强调 G 承担主要定位设计，Full 是具有额外准确率和成本的局部视觉扩展。G+B 不能被描述为独立有效。

建议的实验顺序：协议 → 完整移植及内部定位版本 → 几何数值证据 → G/B/F 配置及匹配程度 → 完整模型 test → 公开文献背景 → 批量成本。

### P1：方法解释与表达质量

- GB → Full 的 +0.832 AP 是最直接匹配的共享 P3 对照；不要根据不同匹配程度的四行历史结果宣称 F/B 因果协同。
- 选择性传递的关键直觉是：部分边替换必须检查实际混合框；完整 teacher 的高 IoU 不能认证部分替换的质量。
- 第三项贡献应描述分析所区分的核心收益和完整配置成本，而不是笼统宣称做了实验。
- 相关工作可收束为航拍/局部视觉证据、分布定位、定位知识传递三部分，明确 D-FINE 已研究 FDR 的跨 DETR 迁移。

### 可采用的英文表达

方法开头：

> LRS-GFDR couples two operations on the same localization path: a center-preserving decoder that enforces feasible extents, and a depth-dependent rule that redistributes matched-object supervision. The representation retains D-FINE's discrete edge distributions and adjacent-bin localization loss. The proposed design specifies how these distributions become boxes and how matched objects supervise them.

主结果解释：

> The localization core accounts for most of the recorded improvement over RT-DETR-L. The complete configuration adds 0.489 AP over G, with its computation reported separately. Within the expert-equipped configurations, the directly matched G+B--Full comparison yields a 0.832-point AP increase when shared P3 refinement is enabled. The historical G+B result alone does not demonstrate an independent expert benefit.

局部边检查直觉：

> Edge selection changes only part of a box. Consequently, the geometry that must be checked is the mixed box actually proposed for transfer. A high-quality complete expert box is insufficient to certify this partial correction.

如使用纯解析示意，可取相同高度的矩形对应区间：GT=[0,1]，S=[-0.1,0.7]，T=[0.2,1.1]。IoU 分别为 0.636、0.727；仅替换左边的 mixed=[0.2,0.7]，IoU=0.500。必须标为 schematic，不能声称该例通过 FGL 边门控或来自真实预测。

### 无法仅靠本次写作消除的边界

- 单数据集、单种子。
- 历史定位版本不全部具有严格匹配的源码和初始化。
- Clean-FDR 比最终 G 高 0.076 AP；几何单行记录下降 0.335；G+B 低于 G 0.343。
- 与 D-FINE 的 common evaluator 对齐预测和评分，但没有对齐优化器、有效 batch 和增强。
- test 已在先前开发中可见；不能称 untouched/blind。
- converted-label 协议不具备完整原始 ignore 信息，不能按官方排行榜直接排名。
- B 为专家及其监督的联合配置，不能区分专家、直接监督与 KD 的各自因果收益。
- Full 相对 G 成本较大；GFLOPs 小增量不能代替实测延迟证据。

## 第二轮：新版 Abstract / Introduction / Related Work / Method 3.2

新版已经明确将 LRS-GFDR 写为原创定位设计，同时归属 D-FINE 的表示构件；未再把 G 整体降格为纯移植。发现以下可直接纠正的表述：

1. `preserving feasible boxes` 过宽。正宽高但低于 floor 的框仍改变。替换为 `preserving boxes whose extents already satisfy the floors`。
2. `Distributional localization resolves fine boundary positions` 把表示能力写成效果。替换为 `represents fine-grained boundary positions`。
3. 低 IoU 到早层更需要收缩之间缺少实测桥梁。将 `Early decoder layers therefore motivate...` 写成设计选择：`We apply stronger moderation in early layers and recover the original quality weighting at the final layer.`
4. 固定分布参考框是 FDR 的既有结构；使用 incoming decoder reference 和停用 preliminary-box supervision 是当前定位集成选择。需将两者归属分清。
5. `Low weights move upward and high weights move downward` 应明确相对 eligible-group mean。精确算术下，q'_i-q'_j=(1-alpha)(q_i-q_j)，故同一 eligible group 内顺序保持。不能推广为跨组排序或浮点绝对顺序保证。
6. `Individually preferable edges` 可改成 `Expert edges with lower FGL losses`，避免将较低分布损失等同于逐边几何更优。
7. 贡献末句可改为完整配置相对定位核心的准确率和成本，避免暗示 B 独立有正增益。

主审反馈：上述五项关键修正已采纳。归档时不据此宣称所有后续修改版本已被逐字验收。

## 第三轮：重排后的 Experiments / Discussion 交叉核对

### 独立核对的原始记录

读取四份完整 CSV，按 validation AP 选择最大值，核对共 100 个 epoch、AP/AP50、选中 epoch 和 provenance 中的 SHA-256：

| 定位版本 | epoch 数 | 选中 epoch | AP | AP50 | 哈希匹配 |
|---|---:|---:|---:|---:|---|
| Full FDR/FGL transfer / Original FDR | 100 | 92 | 29.078 | 48.473 | 是 |
| Clean-FDR | 100 | 88 | 29.696 | 49.320 | 是 |
| Clean-FDR + geometry | 100 | 91 | 29.361 | 49.130 | 是 |
| LRS-GFDR | 100 | 92 | 29.620 | 49.382 | 是 |

来源：`inputs/historical_fdr_results.csv`、`clean_fdr_results.csv`、`geometry_fdr_results.csv`、`lrs_gfdr_results.csv`，以及 `lrs_comparison_provenance.json`。

读取 `inputs/batch8_verified.json`，独立复算 throughput=8000/median_batch_ms，五行均匹配：

| 配置 | 整批 ms | 张/秒 |
|---|---:|---:|
| Baseline | 59.559 | 134.321 |
| G | 66.200 | 120.846 |
| G+F | 69.044 | 115.868 |
| G+B | 104.897 | 76.266 |
| Full | 107.920 | 74.129 |

独立复算的差值：Original→G +0.542；Clean→geometry -0.335；geometry→G +0.259；Clean-G +0.076；GB-G -0.343；Full-GB +0.832；Full-G +0.489；native test +5.861；common final +1.579；common best +1.550；common final APs +1.237。正文和表格显示值一致。

### 范围与因果主张核对通过

- 完整 FDR/FGL 移植仍是主要定位参考，明确不是完整官方 D-FINE detector。
- Clean 保留为中间配置，三个重要负结果均在正文和对应表中保留。
- 内部版本和组件明确只报告 validation；test 为完整 detector 对照。
- native 和 common test 各有清晰 evaluator、checkpoint 和指标口径，未混用。
- common evaluator 的 batch one 属于精度评估配置；效率章节仍只有 batch eight。
- test 先前可见、source revision 差异、有效 batch 和训练 recipe 差异、converted labels 缺少完整 ignore 信息均保留。
- 数值回归仍描述为合成/受控 stress case，没有扩大成训练中发生率。
- Discussion 保留单数据集/种子、历史对照和方法性质无法单独证明 AP/gradient variance/convergence 的限制。

### 第三轮发现及建议

1. **明确的维度混淆**：`The gains span all ten categories at this endpoint, including small-object AP...` 将尺寸子集 APs 包含在类别维度中。建议：`Class AP improves for all ten categories at this endpoint; Table X additionally reports higher small-object AP.`
2. **避免历史对照的强因果连接**：`Full adds 0.489 validation AP through the complete local visual extension` 的 `through` 可改为 `Full records 0.489 higher validation AP with the complete local visual extension`。前文已说明历史配置匹配有限，不必用因果介词强化。
3. **小幅术语一致性**：对 Clean 的 `removes the preliminary reference` 最好改为 `disables the preliminary-reference path`，避免被理解为 preliminary head 从模型状态中物理删除。
4. **几何范围一致性**：`An FP64 regression verifies that ordinary feasible boxes remain unchanged` 可写成 `the tested boxes whose extents satisfy the floors remain unchanged`，与方法中的精确保持条件一致。

总体结论：未发现新增数字错误、内部 test 越界、负结果删除或完整移植对照身份错置。需要处理的是上述表述范围与一个 APs/类别的概念混淆。

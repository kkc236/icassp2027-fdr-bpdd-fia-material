# 新稿结构与归因终审

日期：2026-09-17。只读范围：本轮新稿 `source/body.tex`、`figures/motivation.tikz`，结合此前已核对的核心/组件/系统数值与独立 GT 核验。未修改正文或图源；未重新审计所有技术公式，也不声称完成 PDF 版面视觉检查。

## 总结

**未发现阻断交付的严重结构或证据归因问题。** 新稿已经把任务尺度事实、解析几何示例、设计规则性质和模型结果分成不同证据层；完整 FDR/FGL 仍是主要技术参照，两个核心设计获得独立子节，专家降为一个扩展小节。摘要、贡献与结论的主张基本一致。

下面两处小范围澄清可以进一步确保读者独立阅读时不误解统计协议和模块归属；不需要开启新一轮大改。

## 1. 必要的小范围澄清

### 1.1 让动机图图注本身携带 common evaluator 限定

位置：`figures/motivation.tikz` 图注的 (a)。

当前正文引言和实验设置已明确“common evaluator's stretched input”，但图注只说 independent-axis resizing to 640×640，图内标题为“Object scales at the detector input”。独立看图时，读者可能理解为整个模型的所有 native training/evaluation 输入统计。

建议将图注改为含有以下意思的一句：

> after the independent-axis resizing to 640×640 used by the common evaluator.

同时，APs 的区别可写成“original-image COCO area ranges used to compute APs”，省去括号内 `A<32²`。本轮统计采用明确的严格小于阈值，但不需要用这张任务图重新定义 COCOeval 的完整面积分组。正文现有“the figure's 32-pixel threshold is not the APs grouping”应保留。

### 1.2 引言中的新增 operating point 归给整个扩展

位置：`source/body.tex` 引言扩展段末句，审读快照约第18行。

当前为：

> The expert thus supplies an additional accuracy--cost operating point on top of LRS-GFDR.

建议将主语 `The expert` 换成 `This local visual extension`。前文和实证中的新增 Full 配置包含共享 P3 与专家；单独 G+B 的 AP 低于 G，而最紧配对支持 F 在专家配置下的条件效应。使用整个扩展作主语能与贡献2、组件结果和结论的归属完全一致。此处并不是必须增加新限制段落。

## 2. 已通过的主要论证检查

| 检查点 | 结论与依据 |
|---|---|
| 任务尺度 → 定位问题 | 85.9%明确对应 equivalent side、converted val、common 640 stretch；位移示例明确等尺寸且垂直位置相同，数字正确。段末明示不测 detector errors 或 invalid-box incidence。 |
| 定位问题 → FDR | D-FINE 被明确归属为分布表示来源。新稿没有把 GT 尺寸统计写成 FDR 优于点回归的受控实验，也没有把继承收益全部归给原创。 |
| FDR → GFDR/LRS | 新稿用两个 design questions 连接：signed offsets 的代数可行性与 IoU 权重的监督分配。这是表示/目标函数属性，未宣称已诊断真实训练失效率。 |
| 原创焦点与章节层级 | 3.2 Geometry-feasible decoding、3.3 Layerwise supervision allocation 各自可见；3.4将 F、expert、selection 组织为 Local visual extension。核心的阅读入口比旧稿清楚。 |
| 完整 FDR 的主参照身份 | 第一核心比较仍为29.078→29.620；完整移植包含 host integration，未冒称完整 D-FINE detector。 |
| 中间结果与机制归因 | Clean=29.696、geometry=29.361、LRS-GFDR=29.620均保留；正文指出Clean高0.076，并明确历史比较无法隔离每一修改。 |
| 数值性质与精度证据 | 合成极端解码仍明确是压力测试、非真实模型失败频率；没有将数值检查等同AP证据。 |
| 专家与 F 的归因 | 实验明确G+B低于G、B整体尚未独立证明；G+B→Full被限于专家配置内共享P3的效果。 |
| 内部 val / 系统 test | 内部设计、组件比较继续val-only；完整系统test另节展示；没有将test表扩展为内部消融。 |
| 外部 D-FINE 对照 | common evaluator 对齐预测/评分；不同训练配方、batch、优化及终点定义仍明确。final主终点、best次终点一致。 |
| 摘要—贡献—结论 | 三者都以LRS-GFDR规则与完整FDR主比较为核心，专家为扩展。末尾仍保留单数据集/单seed、历史非全链隔离、性质不保证准确率或收敛增益的边界。 |
| 缺失数据 | 新稿没有补造逐图预测案例、UAVDT结果或机载性能。解析图不伪装成模型可视化。 |

## 3. 关于3.4仍占方法约45%

**不把此前建议的30%当作硬性删除指标。** 3.4确实较长，但其中不仅有专家网络描述，还有对应关系、支持域、actual mixed-box gate、蒸馏归一化和梯度路径。保留这些事实有复现价值，不能为了表面篇幅比例删去已审过的限定。

现阶段，独立的3.2/3.3标题、引言的核心定位、第一核心结果表以及3.4统一的扩展标题，已经有效改变主次。两张扩展机制图仍使扩展拥有较大视觉面积；是否合并应由最终排版决定，不作为本轮内容正确性的阻断项。

若最终排页确实需要压缩，以下是真正可去掉的重复说明，均不删除定义或关键限制：

1. **3.5开头第二、三句**重复说明“专家同一几何解码器、直接监督、teacher detached”；3.4直接监督段和KL段已完整保留这些事实。可以只留第一句交叉引用后直接定义总目标。
2. **3.4 Shared visual features 段末句**“This topology avoids propagating the same change through all pyramid levels…”重复解释前句明确给出的“P4 reads original P3、refinement confined to P3”。保留具体连线事实即可。
3. **3.4 Joint box geometry 段中**“The gate evaluates the actual combination proposed for transfer”与该段首句/式定义重复，可删这一句；保留“better complete expert box is insufficient”、未选边仍是student、rejected weights零、以及不保证optimizer update后IoU提高。

这些删减仅能节约数十词，属于排版选项，不必为了达到任意比例继续损害方法的可复现性。

## 4. 独立统计验证交叉引用

`reviews/MOTIVATION_INDEPENDENT_CHECK_ZH.md` 已独立核验全38,759个框：

- 输入空间面积小于32²：33,281，85.8665084%。
- 原图空间面积小于32²：26,586，68.5931010%。
- 8/32像素等尺寸框水平移1像素的IoU：0.7777778 / 0.9393939。
- 一般等尺寸二维平移公式与矩形坐标交集420次对照，最大绝对差0。

图中将高于64的两个内部核验箱合为一箱时，合计898个标注、2.3168812%，显示2.3%正确。分箱展示值经过各自舍入，不要求显示数值相加刚好100.0%。

**审读状态：内容结构可以进入最终装配与视觉检查。仅建议完成上面两处小范围澄清，不建议重新扩写公式、引入新模型实验或反复进行措辞评分。**

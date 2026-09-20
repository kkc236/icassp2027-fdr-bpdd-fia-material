# 实验设计与呈现审计：身份、参照、取舍与归因

日期：2026-09-17。

审计依据：本轮权威目录 `output/cvm_literature_architecture_20260917` 中的 `source/body.tex`、`build.py`、相关 `inputs`，包括版本来源、四个训练结果文件的登记、Original/Clean authority、当前联合方法说明、D-FINE scratch 配方、batch8效率记录。此报告只读论文与已有材料；没有改稿、训练、模型推理、访问服务器或新增模型结果。其他分支负责技术来源和外部文献核查，本报告不代替其结论。

优先级：**P1**＝会影响贡献身份、核心比较或因果解释，改版必须处理/保持；**P2**＝影响阅读效率、信息完整性或上下文公平性，可在不破坏P1边界下优化。某些P1边界当前已处理得当，明确标记为“保留”，不把已经解决的问题冒充新缺陷。

## 一、总判断

**当前最值得改的不是删数据，而是让表格本身说清每行是谁的设计、回答哪个问题。**

`Clean-FDR` 是本研究探索出的参考框与监督改写，最高29.696 AP是作者这条设计路线的结果。现表只在最后一行写 `LRS-GFDR (ours)`，而 `Clean-FDR` 没有作者身份提示。快速阅读会把最高行误认成一个外部“干净FDR基线”，进而得到“作者不如别人FDR”的印象；正文稍后解释它是中间配置，不能完全修复表格造成的第一印象。

重新分为 **Transfer reference** 和 **Our localization variants** 两组，可以同时做到：

1. 承认并明确继承自D-FINE的分布表示/FGL；
2. 将作者的参考框与监督改写放回作者名下；
3. 保留比最终方案更高的作者中间版本；
4. 将最终LRS-GFDR的理由表述为明确的几何/监督行为与所记录的精度，而非假装它逐项单调涨点。

这是真实身份更清楚带来的竞争力，不是通过视觉弱化负结果制造更大的提升。

## 二、命名方案：采用角色分组，停止将内部alias当作方法身份

### 2.1 推荐落地方案

主任务拟采用的双栏表方案可用：

| 角色组 | 展示行名 | Path redesign | Feasible decoding | LRS | AP | AP50 |
|---|---|---:|---:|---:|---:|---:|
| Transfer reference | Full FDR/FGL transfer reference | — | — | — | 29.078 | 48.473 |
| Our localization variants | Path redesign | ✓ | — | — | **29.696** | 49.320 |
| Our localization variants | Path redesign + geometry | ✓ | ✓ | — | 29.361 | 49.130 |
| Our localization variants | LRS-GFDR | ✓ | ✓ | ✓ | 29.620 | **49.382** |

实际排版用组标题而非逐行重复第一列。列名 `Redesigned path` 也可以；正文和caption必须有确切定义。`Feasible decoding` 比 `Feasible geometry` 更直接表示一项规则开关，避免让未打勾行被误读成“所有预测框都非法”。

表名建议为 **Localization design comparison**；不要称为严格受控的逐项消融。

### 2.2 四个名字是否准确

| 拟用名称 | 判断 | 必要限定 |
|---|---|---|
| Full FDR/FGL transfer reference | 准确，优于Original FDR | Full修饰FDR/FGL移植范围，不是完整D-FINE detector；均在本项目RT-DETR host中实现。不能把D-FINE全部其他模块也纳入“完整”的暗示。 |
| Our reference-and-supervision redesign | 准确地交代作者身份，但行名长 | “ours”指本研究提出/实现的这一适配配置，不代表每个构成原语都是绝对首创；incoming reference与关闭额外监督是区别。 |
| Path redesign | 推荐的紧凑行名 | 分组已标Our，caption解释它是上一完整名称的简称；不能只凭短名省去具体差异。 |
| Ours + geometry | 不推荐单独使用 | “Ours”可能被读成最终LRS-GFDR，再加geometry就逻辑不清；应写Path redesign + geometry，明确加入到哪一配置。 |
| LRS-GFDR | 保留正式核心名称 | 定义为path redesign + explicit feasible decoding + LRS；性能增量来自整体设计比较，不能只归给后两项。 |

不要再引入 `R` 代表path redesign：方法中 `R(P3)` 已表示共享特征变换。表格分组和三个开关足够清楚，无需增加新缩写。

### 2.3 需要同时出现在caption/相邻正文中的四点

- 所有行均保留并归属D-FINE的离散边分布、固定分布坐标系、积分解码、累计细化和基础FGL。
- `Path redesign` 使用incoming decoder reference，取消额外preliminary-box路径/监督和额外DN-FDR监督；RT-DETR自身denoising仍保留。
- 前一行是完整移植参照，后三行是本研究的定位变体；中间版本不是外部方法。
- 四行是100轮历史版本的native-validation-selected结果；不能据此声称全部源文件、初始化和其他训练条件已经逐项匹配。

`Clean-FDR` 与 `Original FDR` 可从主文显示名移除，保留在作者侧新旧命名映射和冻结来源说明。**冻结CSV、配置、authority、commit、hash及原始运行名不改名、不改内容。** 新增一张显示名→历史alias→证据文件映射即可；重命名不能改变任何checkpoint身份。

## 三、逐项审计：问题 → 误读机制 → 改法 → 必留内容

### P1-01｜版本表作者身份不对称（需改）

**问题：** 只有最终行显式写ours；Clean命名看起来像D-FINE的通用简化版，而非作者探索版本。

**误读机制：** 审稿人先看粗体29.696，再看旁边没有ours，容易把结果理解为一个更强的外部基线。无意中弱化了本研究的参考框/监督改写，也让最终方案与外部工作的关系变得不清楚。

**改法：** 采用上文角色分组；把mechanism表和Introduction/Experiments/Conclusion中的Original全面统一为Full FDR/FGL transfer reference；把Clean主文统一为Path redesign，并在定义处写作者身份。

**必留：** 四个AP/AP50、最高值粗体规则、所有中间行、继承机制归属、历史来源映射。不能把Path redesign移到补充而在主文只留较弱移植参照。

### P1-02｜四版本的“进步链”容易被误当严格因果链（现正文已有保护，改表须保持）

**问题：** 三个开关天然形成递增阶梯；新命名虽然更公允，也更容易让人误以为每一步是固定其他条件的单因素消融。

**误读机制：** 表面结构从off到on，与标准ablation表相同；但档案只明确它们是历史版本，不是已认证的全链同源同初始化实验。

**改法：** 表名用design comparison；caption保留historical/source-initialization匹配范围；正文先评价整体设计对完整移植的主要对照，再描述作者变体内的取舍。用“records”“observed difference”“design comparison”，不写“proves the isolated contribution”。

**必留：** Path redesign→geometry为−0.335；geometry→LRS-GFDR为+0.259；最终比Path redesign低0.076。它们都是记录差异，不能升级为机制净效应。

### P1-03｜最终核心为何选LRS-GFDR，不能只靠把参照换弱（需把已有事实组织好）

**问题：** 若只强调最终相对transfer的+0.542，同时把较高Path redesign解释成无关历史行，审稿人仍会问为什么不提交最高AP版本。

**误读机制：** 最终设计看起来只是挑了一个更容易赢的参照，而没有说明所选择配置的设计目的。

**改法：** 主文给出两个同时成立的观察：作者的Path redesign已达到29.696；最终核心加入显式可行解码和LRS后为29.620，AP50为49.382（比Path redesign高0.062），并具有论文定义的几何与权重分配性质。这解释的是最终设计选择，不是声称性质必然带来AP收益。

**必留：** AP落后0.076的事实；不能用“仅0.076”“相当”“无损”“统计上没有下降”抹去单seed下无方差估计的边界。也不能将AP50单独改成主指标，以绕开主要AP的非最高结果。

**最公允的数字叙事：**

| 比较 | ΔAP | ΔAP50 | 可以支持什么 |
|---|---:|---:|---|
| Path redesign − transfer | +0.618 | +0.847 | 作者探索版本对移植参照的记录差异 |
| Path redesign + geometry − transfer | +0.283 | +0.657 | 带显式几何规则版本的整体记录 |
| LRS-GFDR − transfer | +0.542 | +0.909 | 论文最终核心对主要参照的整体差异 |
| LRS-GFDR − Path redesign | −0.076 | +0.062 | 最终核心与较高AP作者中间版本的准确率取舍 |

无需将此差值表另加到主文；它规定正文应如何解释已有四行。

### P1-04｜组件表中的B并非单独KD，G也并非只含原创规则（当前界定基本合格，必须保持）

**问题：** G/B/F打勾表很容易被当作三个独立、同等新颖且各自涨点的模块消融。

**误读机制：** Baseline→G +7.709看起来像GFDR/LRS原创贡献；B看起来只是蒸馏损失；Full最大似乎就能推出三者协同。

**改法：** Baseline改显示为`RT-DETR-L host reference`或明确caption中Baseline身份；G显示/定义为LRS-GFDR localization core。B继续明确“expert + direct supervision + selected localization transfer”的整体；表caption保留G+B与Full为最紧配对，必要时以同一符号标记这两行。

**必留：** G+B=29.277低于G=29.620；G+F=29.773；Full=30.109。保留+7.709包含继承表示的说明；+0.832只支持F在专家配置下的条件差异；+0.489是Full对G的validation差异。没有同结构仅关KD的训练对照，不得单独宣称KD的准确率收益。

**不建议：** 重排成每一行都成功涨点的阶梯、移走G+B、把B改标为“distillation only”、根据这些历史行计算并宣称严格的统计交互/协同效应。

### P1-05｜Native/common系统比较的身份、端点与口径不能混（当前基本合格，保持并改善可扫读性）

**问题：** 同一个Full在两个test表有23.604、24.133、24.229，D-FINE-L又可能被误认为官方论文结果。

**误读机制：** 如果表或图脱离长协议段阅读，这些数值差异可能被看成不一致或挑选最优；“Native validation-selected best”也可能被看成native评测值而非仅指checkpoint选择方式。

**改法：** native表明确“Native evaluator; validation-selected checkpoints”；common表明确“Common evaluator; final checkpoints (primary)”和“Validation-selected checkpoints (secondary)”。D-FINE行可用`D-FINE-L (reprod.)`并在caption写scratch-adapted。两表可放同一小节相邻，或同一表的独立panel，但不做混合排名。

**必留：** final为主、best为次；不同训练配方和有效batch；converted-label、maxDet、共同预处理；test曾在此前开发可见。Full对RT-DETR的+5.861与对D-FINE的+1.579回答完整系统问题，不回答LRS/GFDR/B/F的独立贡献。

### P1-06｜OOM说明只能解释D-FINE物理batch调整（当前措辞合格，防止新一轮美化扩大）

**问题：** 新加batch8在4090 24GB上OOM、转batch4，容易被用于给所有训练不匹配作统一解释，或暗示本模型比D-FINE普遍更省显存。

**误读机制：** 缺少“under our training setup”的限定时，硬件约束会被读成架构固有属性。把batch4与Full物理batch8并列也会遮住effective4对约64的差别。

**改法：** 保留当前限定句；若用协议简表，分别列precision、physical batch、gradient accumulation/effective batch、optimizer、augmentation、checkpoint。OOM原因可作为D-FINE物理batch行脚注。

**必留：** D-FINE FP32、AdamW、无梯度累积/effective4；Full AMP、MuSGD、累积后约64；其他差异不能全部归因OOM。不能称“equal training budget”“fairness established by the same GPU”，也不能据此宣称general memory efficiency。

### P2-07｜内部既定外部评估计划的完整披露范围待核查

**问题：** `inputs/dfine_scratch_protocol.md` 的事先计划写明val/test×cap100/300×best/final八种组合均应公布。当前主文只需test/cap300的两个端点，但本轮目录显式打包的外部源主要是final_test.cap300及报告。

**误读机制：** 若只看到有利的主表，读者无法知道其他事先约定口径是否完成、结论是否对其敏感。当前“不同比较端点差异均为正”的结论仅涉及已展示final/best，不应扩大成所有选择/截断口径都稳定。

**改法：** 主任务只读核查本地既有完整comparison报告；如果已存在可靠八格结果，在补充/复现包给一张完整表，主文仍锁定final test@300。若缺部分，不填估计值、不新推理，写明披露覆盖范围。该计划是内部先定方案，不应宣称为公开预注册研究。

**必留：** 原计划及原始结果身份；不能看到结果后更换主终点。外部Full-vs-D-FINE的val/test口径表与“内部组件仅val”不冲突。

### P2-08｜文献validation context的职责应更窄，不宜显得像排名表

**问题：** 目前只放RemDet-L、BDNet和Full，又用100/300 epochs、params、AP形成直观排行榜；实际训练/数据处理不匹配。BDNet的31.2 AP和更小模型是真实不利参照。

**误读机制：** 读者可能将“同640、无预训练”误当协议一致；100比300容易被偷换为三倍训练效率。若只删掉BDNet，则更像选择性取样。

**改法：** 保留为`Published validation context`，正文解释选这两项的具体目的，例如展示相近参数规模和更小模型的已报道范围，而非“最先进方法完整比较”。本表无需单立较长小节，可并入系统比较末段；另一路须核对数值与协议来源。

**必留：** 所有原行、epochs与协议差异、BDNet更高AP与更小参数；不要只保留有利RemDet。不能据epoch差异宣称更快收敛、等计算预算或SOTA。若文献数值经来源核查不适合这个表，应按可比性原则重构整个context表，而不是只移走对自己不利的一行。

### P2-09｜效率结果离组件收益较远，读者难以评价扩展价值

**问题：** 组件AP在前，效率表在独立末节，Full的0.489 AP收益和额外28.247 GFLOPs/41.720 ms batch时间未同时进入视野。

**误读机制：** 强调74.129 images/s会遮住G本身120.846 images/s；强调G只多0.20% GFLOPs又可能使读者忽略实测运行开销。

**改法：** 优先把两表相邻、在组件段直接给G与Full的关键成本。若版式适合，可将五个同名配置合成一张双栏“Accuracy and cost of the core and local extension”：Variant、Val AP、AP50、Params、GFLOPs、Batch ms、Images/s。无需保留冗余G/B/F打勾列；完整模块定义放caption。

**必留：** Baseline/G/G+F/G+B/Full五行；GPU/精度/batch8、固定随机输入、predict范围/不含I/O；batch时间与throughput；Full相对G的+0.489 AP与+26.70% GFLOPs。只LRS没有推理分支，整个G有运行增量，整个B有推理成本。

**不建议：** 为核心四版本补推测性的效率值、把batch摊销时间称单请求latency、宣称已经机载实时部署、用训练OOM给推理速度作因果解释。

### P2-10｜数值检查应按性质陈述，少用修bug的时间线

**问题：** 现文字以pre-repair/post-repair、归档回归名字串联，容易把主要贡献写成代码修复日志；反过来，过度包装又会把合成极端情况说成真实模型崩溃。

**误读机制：** 审稿人不知道这些checks究竟在回答“算子是否实现所称性质”还是“训练为何提分”。

**改法：** 保留一个正文性质验证段，按“正且可表示extent / 已满足约束框不变 / 中心保持 / 有限梯度”组织。输入dtype/参考尺寸压力矩阵、测试名字、修复时间和全部日志进入补充或复现包。只有需要读者理解有限精度理由的最小压力例留主文。

**必留：** synthetic features、identity wrapper、固定Integral输出等非真实训练设定；正reference/有限值假设、最小FP16下溢属于假设外压力案例；不测真实非法框频率，不证明几何规则单独提高AP或防止真实训练崩溃。

### P2-11｜新动机图和类AP图的证据职责应保持明确

**问题：** 当前没有逐图预测案例，新增GT/解析图和十类AP图容易在后续润色中被统称为“qualitative mechanism evidence”。

**误读机制：** 一张真实标注统计图看起来更像数据证据，读者可能自然将其接成“模型错误已诊断”；十类都是正值也容易被说成机制对各种场景均稳定。

**改法：** 动机图明确是全converted-val GT输入尺度+解析平移；类AP图明确是final checkpoint、common evaluator、完整系统。正文不把它们改名成模型行为/attention/失败案例。

**必留：** 85.9%是640stretch后的等价边长统计，非APs分组；解析示例不是预测误差。十类图全部类别、不挑子集、差值从未舍入值算；不同训练配方限定。没有新逐图预测素材就不增加对应小节。

### P2-12｜“all intermediate configurations”范围过宽

**问题：** 引言“All intermediate configurations are reported”读起来像所有开发试验全覆盖，但inputs还保留Capacity v2/v3等历史支线。

**误读机制：** 读者会期待全文完整开发史；如果只列与当前定位设计有关的四行，宽泛“all”反而制造不必要的披露疑问。

**改法：** 改成明确范围，例如“the transfer reference and intermediate localization designs are reported together”，或说明“the three author-designed localization variants”。实验选择依据应是回答当前设计问题，不是把一切旧run堆进主文。

**必留：** 与当前主张直接相关的更高Path redesign、geometry下降、G+B下降。v2/v3完整历史可留补充；若主文重新声称v3机制解决了v2联合退化，就必须给对应历史比较及其多改动不可隔离的限制。

## 四、推荐实验结构与每张表的唯一问题

| 建议位置 | 表/图 | 只回答的问题 | 主要可见限制 |
|---|---|---|---|
| 4.1 Protocol | 可选简短配方表 | 我们在什么数据、训练和评测条件下比较？ | converted-label、native/common、effective4 vs约64、OOM限具体setup |
| 4.2 Localization design comparison | 四版本双栏表 | 本研究的定位路线相对完整移植怎样；规则加入后的记录怎样？ | 三行ours、四行都保留、历史非全链控制 |
| 4.2后段 Properties | 简短性质验证段，必要时小表 | 几何规则是否实现所称前向/梯度性质？ | 合成压力，不是AP机制证据 |
| 4.3 Local extension and cost | 组件与效率表相邻或合并 | 加局部扩展得到多少validation AP、付出多少代价？ | B是整体；紧配对F效应；五行含负结果 |
| 4.4 Complete-system comparisons | native/common独立表或panel | 当前完整系统与host、另一完整检测器分别如何？ | 评测口径不可横混；训练不同；final主 |
| 4.4后段 | final十类AP图 | 完整系统的差异如何分布到类别？ | 无模块归因、无逐图机理 |
| 4.4末段或小节 | published validation context | 已报道的参数/AP量级是什么？ | 不构成严格排名或等训练预算 |

方法中的mechanism表继续承担继承/原创边界；它与实验四版本表职责不同，没必要为了减少表数强行合并。新的四版本表加开关列后，应在caption定义差异，避免读者必须来回查两页才能认出哪行是作者工作。

## 五、主文与补充：选择原则和具体方案

### 5.1 选择原则

1. **会改变对核心贡献或效果的判断，就留主文。** 这包括更高Path redesign、geometry下降、G+B下降、effective batch差异、主要参照身份；不能只放脚注或补充来降低可见性。
2. **需要逐项追溯才能复现，但不改变读者主判断的细节，可放补充。** 如hash、commit、源配置完整字段、dtype测试日志、精确采样点枚举。
3. **只因某行不利，不能将其移走；只因现有文件多，也不必全塞主文。** 围绕当前主张定义范围，同一范围内保持完整。
4. **先固定主问题和主要端点，再决定表格位置。** 不从最漂亮的结果倒推哪个口径成为主终点。
5. **每图一项证据职责。** 示意讲机制，GT讲任务，validation讲设计记录，test讲完整系统，效率讲成本。图的美观不改变证据类型。
6. 当前约12页、上限14页，**没有必须把关键实验迁出的空间压力**。先解决身份和归因；是否合并或迁移取决于阅读是否改善。目标渠道的补充规则由主任务官方核查后再决定，不能假定独立supplement一定可提交。

### 5.2 当前最推荐：主文保留全部核心结果，只集中辅助细节

**主文保留：**

- 完整FDR/FGL transfer与三个ours变体的全部四行；主要AP、AP50、开关与历史对照边界。
- 全部五个系统配置的validation结果与推理成本；两表相邻或一张双栏表均可。
- native test表和common final/best两个端点；scratch-adapted与配方差异在主文可见。
- 几何性质的一段或紧凑小表；任务动机图；十类AP图若版面宽裕可继续保留。
- 两行已发表context（来源核验通过后），紧凑呈现；不为迁移而迁移。

**补充/复现材料集中：**

- 显示名与历史alias/commit/配置/CSV/初始状态映射，Frozen source不改名。
- 完整训练协议；D-FINE adaptation与OOM用户提供事实的来源登记，不能把用户补充伪装成新读取的日志。
- 全部几何回归覆盖与日志；本文用到的公式性质推导或详细数值表。
- 外部比较事先计划的八组合结果表（仅当已有本地权威结果可核验），并明确主/次口径。
- 当前专家的完整结构与采样常数；v2/v3路线历史仅在相关主张需要时引用。

### 5.3 若实际排版接近14页，按这个顺序压缩

1. 先删同一限制或机制在引言、caption、实验解释中逐字重复的说明；保留最靠近结果的限制与关键总述。
2. 合并组件/效率或缩短其重复五行模块标记，成本与AP同时可见。
3. 类AP大图可缩成单栏或放补充，因为aggregate+APs的主要系统结论仍在主表；保留正文一句全十类结果及明确引用。不能只展示增益最大的类别。
4. 数值检查的完整输入矩阵、修复历程移补充，正文保留性质验证与synthetic限定。
5. 已发表context若不参与主要论证，可整体移补充，并保持两项文献而非挑不利行迁移。

**绝不优先迁移：** 更高的作者Path redesign、geometry负差异、G+B负差异、不同配方/effective batch、不同evaluator与checkpoint身份。这些都是判断当前方法所必需的信息。

## 六、主任务可执行清单

### 第一轮：身份与主要比较（优先）

- [ ] 四版本表改为Transfer reference / Our localization variants两组。
- [ ] 三个规则开关定义清晰；Path redesign作者归属可在表本身读到。
- [ ] 全文展示名统一；不修改任何冻结证据文件。
- [ ] 作者侧映射保留Original/Clean历史alias，方便后续核对。
- [ ] 保留最高AP粗体在Path redesign、最高AP50粗体在LRS-GFDR。
- [ ] 主文明确最终对完整transfer +0.542，但对作者Path redesign为−0.076；不宣称无损或显著。

### 第二轮：系统结果与代价（次优先）

- [ ] 组件与效率靠近；所有五行仍在；B整体身份和紧配对范围清楚。
- [ ] native/common结果与端点在表头/caption可独立识别。
- [ ] D-FINE复现身份、OOM适用范围及effective batch差异不弱化。
- [ ] 从本地查既定八组合外部结果的披露范围，不新推理不补空数。
- [ ] 文献context由另一分支完成来源核验后决定保留/整表迁移。

### 第三轮：材料分层（按实际版面决定）

- [ ] 数值checks保留性质、不复述代码修复史；仍明确非真实失效率。
- [ ] 图表证据职责不变，缺失预测案例不由示意图替代。
- [ ] 主文接近页数上限才按既定顺序压缩，避免为了显得简洁移走关键负结果。

**审计结论：建议实施命名与角色分组，以及组件收益/成本的邻近呈现。现有结果的限制决定主张强度，不妨碍更公允地展示作者确实做出的设计。Clean-FDR最高AP应成为“作者中间设计的真实表现”，而不是被误认为外部基线优势，也不是被隐藏。**

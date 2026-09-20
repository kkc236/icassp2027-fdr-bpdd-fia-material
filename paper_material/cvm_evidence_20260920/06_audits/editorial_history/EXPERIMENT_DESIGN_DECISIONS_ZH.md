> 历史决策快照：本轮实验顺序及主文/附录位置已更新，以 FEEDBACK_APPLICATION_ZH.md 为准。本文件保留其形成时的设计理由。

> 当前章节与证据位置以EVIDENCE_FOCUS_DECISIONS_ZH.md为准；本文件保留相应前版的研究和命名依据。

> 当前命名已更新为GCDL / LQS；本文件保留此前取舍过程，旧名与当前名的对应见NAMING_DECISIONS_ZH.md。

# 实验叙事与呈现设计：本轮决策

## 核心判断

论文的竞争力应来自清楚的贡献身份、恰当的比较对象，以及结论与证据的一一对应。旧稿的主要问题是把内部运行名直接当成学术角色：Clean-FDR 看起来像外部基线，实际上它的 incoming-reference 与监督路径改写属于作者的设计探索。

本轮主线调整为：**航拍小目标对边界误差敏感 → 在已归属 D-FINE 的分布表示上重新设计定位路径、几何解码与逐层监督 → 用局部视觉扩展提供更高精度的完整配置 → 分别验证性质、定位设计、完整系统和处理成本。**

这不是把每个已有机制都重新命名为原创。固定分布坐标系、离散边 logits、非均匀支撑、积分解码、累计细化与基础 FGL 仍明确归属 D-FINE。作者路径设计的贡献在于参考选择与监督组织；源码核查确认解码与 FGL target 同步使用 incoming reference。

## 检索和取舍的方法

本轮是围绕写作决策的定向文献审查，不是覆盖整个领域的系统综述。先复用上一版对 CVM 2025/2026 六篇全文的笔记，再核对强相关 DETR 论文与外部比较方法的实验组织。检索重点是“比较对象是谁、模块加入到什么基础配置、训练条件如何标识、负结果如何解释、精度与成本如何配对”，不以文章是否录用来推断某种包装必然有效。

| 原始来源与实际阅读位置 | 可借鉴的做法 | 本稿落实 | 不照搬的结论 |
|---|---|---|---|
| [D-FINE，ICLR 2025 正式记录](https://proceedings.iclr.cc/paper_files/paper/2025/hash/6cf58a87e3097e7d1f9be3e8693a93de-Abstract-Conference.html)，最终版 Tables 4–5；详细定位见 research 文献记录 | 区分作者基础配置、结构/训练调整、FDR/蒸馏实验的配置范围；中间行并非都提高 AP | 将移植参照与作者定位变体分组，机制表交代继承与改写 | 不把不同配置范围的数值混作单因素消融 |
| DEIM 正式主文 Table 6 与补充 §3；链接和版本见 research/COMPARATIVE_EXPERIMENT_PRACTICES_ZH.md | 明确说明基础配置已改动 BN、调度器和激活函数 | “Path redesign”必须定义，不能沿用会误认成外部基线的 Clean 名称 | 不把不同 epoch 的比较说成严格等预算模块因果证据 |
| [SD-Net，CVM 2026 官方论文](https://iccvm.org/2026/files/papers/691.pdf)，Table 4 | strong baseline 在局部实验中有明确组件范围 | 五臂表明确 RT-DETR-L host、G 和扩展配置，标注最直接配对的两行 | 不把局部实验底座与原生检测器混称 baseline |
| [FGHDet，CVM 2025 官方论文](https://iccvm.org/2025/papers/s8p2-368-jcst.pdf)，Tables 5、8 | 用接近的替代设计回答具体设计问题 | 四版本表保留作者路径变体与几何变体，避免只选较弱参照 | 不在缺少对照时宣称每个机制独立有效 |
| [DASSF，CVM 2025 官方论文](https://iccvm.org/2025/papers/lncs/813.pdf)，Tables 5–6 | 将模块替代与跨模型适配分开 | 定位设计比较与完整 D-FINE detector 比较承担不同职责 | 不混用不同表中条件不明的基础值 |
| [LME-DETR，CVM 2026 官方论文](https://iccvm.org/2026/files/papers/265.pdf)，实验和组件表 | 从整体性能进入尺度和组件分析 | 保留全十类 AP 图；用同一表配对五臂 AP 与成本 | 不把 EMA 分类损失与本文 image–layer FGL 权重规则混同 |
| [Sphere-CenterNet，CVM 2026 官方论文](https://iccvm.org/2026/files/papers/274.pdf)，Table 4 | 任务几何动机先于模块；保留单项下降 | G 的几何性质与其 AP 证据分开；不删 geometry 下降行 | 不从全配置最优推断严格协同效应 |
| [CADSpotting，CVM 2026 官方论文](https://iccvm.org/2026/files/papers/297.pdf)，Tables 6–7、10 | 表格区分表示、骨干、推理选择及其评价范围 | 原创定位路径、视觉扩展、推理成本有各自证据角色 | 不把同批数据上的多种评分当独立实验 |
| [RemDet，作者 v2 全文](https://arxiv.org/html/2412.10040v2)，主文整体设计实验及附录 Tables 5、8；[AAAI 正式出版记录](https://ojs.aaai.org/index.php/AAAI/article/view/32490) | 精度、速度、复杂度共同解释设计取舍；标识不同图像处理方式 | 合并组件与效率表，保留 G+F 的中间成本选择 | 不移植异平台速度进行公平排名；不将训练轮数当算力预算 |
| [BDNet，CVPR 2026 正式记录](https://openaccess.thecvf.com/content/CVPR2026/html/Guan_BDNetBio-Inspired_Dual-Backbone_Small_Object_Detection_Network_CVPR_2026_paper.html)，§4、Tables 2、4–5 | 区分优化后的实验底座、文献结果和同条件复现 | 文献表按 published / our native protocol 分组并说明选取目的 | 不把作者优化底座当原封不动 YOLO，也不隐藏 BDNet 的较高 AP 与较小参数 |

DEIMv2 只按已核验的预印本版本用于方法组织参考；未核实正式会议信息，未向论文参考文献或会议比较表加入未经确认的出版身份。完整阅读范围、页码和来源在 research 的专题报告中记录。上表的比较分析是本轮编辑判断，不是上述论文作者对本稿的背书。

## 逐项落地

| 风险/误读 | 已采用的处理 | 明确保留的证据边界 |
|---|---|---|
| Clean-FDR 像外部基线，最高 AP 被错误归因 | 主文去掉历史 alias；版本表分成 Transfer reference / Our localization variants；作者行使用 Path redesign | 四行原数值、最高值加粗均保留；新旧名称映射与冻结来源一起打包 |
| “完整移植版”被误读成完整官方 D-FINE detector | 使用 Full FDR/FGL transfer reference，并声明 RT-DETR host integration | 外部 D-FINE-L 完整模型另表比较，主文标 scratch-adapted reproduction |
| 原创仅剩两项小规则，忽略作者路径改写 | 方法增加 Reference and supervision path 段；摘要、引言、贡献、机制表同步体现路径设计 | 固定分布坐标系及 FDR/FGL 表示仍归属 D-FINE |
| “移除 preliminary/DN”描述超过代码事实 | 明确改变 reference/extra-loss path，保留 preliminary prediction head 与 stock denoising losses | DN queries 仍经过分布定位路径；不是取消整个 denoising 机制 |
| 台阶式开关表看似严格单因素因果链 | 表名改 Localization design comparison，caption说明历史来源匹配范围 | +0.542 属整体设计比较；不归给任一单独规则 |
| 最终 G 不是四版本最高 AP，选择理由缺失 | 同时写出 Path redesign +0.618 和最终 +0.542；解释 G 所选择的显式几何及监督性质 | G 比 Path redesign 低0.076 AP、AP50高0.062，均如实写出；不称无损或统计相当 |
| G 的 +7.709 被误称全部原创收益 | 明确其中包含继承的 FDR 表示；原创近邻参照是完整 FDR/FGL 移植 | 保留 RT-DETR-L 到完整系统的总体收益，它回答完整系统问题 |
| B 看似单独蒸馏模块，Full最高被误称三个模块协同 | B 定义为专家、直接监督和选择性转移的整体；用同一标记指出 G+B / Full 配对 | 保留 G+B 低于 G 0.343；+0.832 支持 F 在专家配置下的差异，不是 KD 单独作用 |
| 精度和效率相隔多页，Full 看起来无代价 | 合并五臂 AP/AP50/参数/GFLOPs/batch ms/吞吐量；叙述成本紧接组件 | G、G+F、G+B 全部保留；Full多0.489 AP及26.70% GFLOPs明确可见 |
| batch吞吐量被称作实时单图延迟 | 保持batch8、硬件、FP32、计时范围和暖机/样本量 | 13.490 ms 仅为摊销；未测机载性能；固定输入不含采集和传输 |
| native/common结果像数字不一致 | 表题/分区明确 evaluator、checkpoint、maxDet；final主、best次 | 两种协议不混排；converted-label和此前test可见范围保留 |
| OOM 成为所有配方不匹配的理由 | 原因只解释本文 D-FINE 训练设置的 physical batch8→4 | Full累积后约64 vs D-FINE effective4，以及optimizer/precision/augmentation差异继续披露 |
| 只展示两个有利外部端点像选择性汇报 | 附录公布原记录的8组完整detector评分 | final test@300保持主终点；同一训练/重叠数据不作为8次独立试验；内部组件仍val only |
| 文献表像SOTA排行榜 | 解释选取RemDet-L的相近参数规模、BDNet的小模型参考；按结果来源分组 | BDNet更高AP/更小参数保留；不称同预算、训练更快或全面超越 |
| 几何证据像修bug日志，或被夸大为真实模型失效率 | 按正extent、已可行框不变、中心与有限梯度组织性质验证 | 合成wrapper/固定输出/精度假设与FP16下溢范围保留；不声称单独提分或训练崩溃率 |
| 动机与类别图被错误用于因果归因 | 图1只承担GT尺度/解析敏感性；图6承担完整系统全类别轮廓 | 不称模型错误统计或证明LRS单独有效；不加入无来源逐图案例 |

## 保留在主文与移入作者资料的内容

- **主文保留**：四定位设计行、五臂精度与成本、native/common完整模型结果、两项文献参照、完整八组合附录、数值性质及关键限制。不能为了版面优雅把影响最终配置选择的中间结果移走。
- **作者工程包保留**：旧alias映射、原CSV/config/source、公式检查、来源指纹、研究笔记与审稿意见。它们服务于追溯，不能直接替代匿名补充材料。
- **本版不加入**：新增训练/推理、多seed、未完成的UAVDT、逐图预测案例、内部模块test、未测的延迟/机载声明。与既定工作范围一致。

## 本轮能改善与不能改变的事情

本轮能修复“谁提出了什么、哪个数值支持哪项结论、为何选择这个配置”的可读性与可信度，也利用完整既有记录排除了只看两个外部端点的呈现缺口。它不改变单数据集、单seed、历史配置匹配不完整，以及D-FINE训练配方不一致的事实；不能给出可信录用概率，也不能承诺录用。

当前版本按 [CVM 2027 官方投稿要求](https://iccvm.org/2027/submission.htm) 使用匿名模板，含参考文献不超过14页。最终页数、数值检查和视觉验收以 verification.json / RELEASE_METADATA.json 为准。

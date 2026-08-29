# ICASSP 2027 论文蓝图与写作执行清单：LRS-FDR / BPDD / FIA

> 状态日期：2026-08-29
>
> 文档身份：当前投稿路线的论文大纲、证据地图和跨对话写作交接入口
>
> 当前方法：RT-DETR-L + LRS-FDR + BPDD + FIA
>
> 证据纪律：已完成结果写实数；未完成的 G/H/I、UAVDT Full 和最终复杂度只保留占位符

## 0. 投稿约束与当前结论

ICASSP 2027 官方页面规定：论文最多使用 **4 页技术内容**，其中包含正文、图和
参考文献；允许增加第 5 页，但第 5 页只能放参考文献、funding acknowledgements
和 Compliance with Ethical Standards statement。Full Paper Submission Deadline 为
**2026-09-16**。最终提交时间点与时区仍需以投稿系统显示为准。

- 官方长度说明：<https://2027.ieeeicassp.org/publishing-and-paper-presentation-options/>
- 官方日期说明：<https://2027.ieeeicassp.org/call-for-papers/>

因此正文采用紧凑 conference-paper 结构，而不是把现有全部材料搬进四页：

1. 一张多面板方法图；
2. 一张外部/主结果表；
3. 一张双面板消融表；
4. 一张效率与第二数据集小表，版面不足时将效率并入消融表；
5. 十类别、四尺度、末十轮趋势、完整配置和历史路线放补充材料或公开仓库。

当前可冻结的核心判断是：

- NA-FDR 是有独立正向证据的 native-aligned foundation；
- LRS-FGL 相对 NA-FDR 的主要指标特征是 AP75/Recall 提升，而不是总体 mAP 大幅提升；
- BPDD 和 FIA 已有历史机制证据，但最终 LRS-FDR 组合必须使用 G/H/I 新结果；
- UAVDT 只做 Baseline 与 Full，两臂用于第二数据集 effectiveness，不承担模块归因；
- 单 seed 在当前 B 类会议同类论文中可以作为描述性结果，但全文不得使用统计显著性措辞。

EQuAL、AP-FDR、DCF-FDR 和官方 D-FINE-S 均保留为历史审计路线，不再作为当前
论文方法或等待切换回正文。

## 1. Paper Configuration Record

| 参数 | 冻结值 |
|---|---|
| Paper type | IEEE conference paper |
| Target venue | ICASSP 2027 |
| Candidate technical area | Image, Video and Multidimensional Signal Processing；具体 track 待作者在投稿系统确认 |
| Body language | English |
| Citation style | IEEE numeric |
| Main dataset | VisDrone2019-DET |
| Second dataset | UAVDT，不写作 UAT |
| Base detector | Ultralytics RT-DETR-L |
| Final method | LRS-FDR + BPDD + FIA |
| Main evidence mode | fixed-protocol, seed-0 descriptive experiments |
| Main metric | mAP50-95；同时报告 AP50、AP75；LRS 相关表保留 Recall |
| Working word budget | 约 2,300--2,600 个英文单词，不含第 5 页参考文献 |
| Figure budget | 1 张主方法图；可选 1 张定性图放补充材料 |
| Table budget | 正文 3 张为目标，最多 4 张紧凑表 |
| Output workflow | Markdown 蓝图 -> IEEE LaTeX -> PDF 校验 |
| Review criteria binding | `criteria_binding_unavailable`：venue 已知，但具体 technical track/article metadata 尚未由作者完整确认 |

### 1.1 研究问题

**RQ1.** 如何把 D-FINE 风格的边界分布定位构件重新组织到原生 RT-DETR-L
定位路径中，避免历史 preliminary reference 与额外 DN-FDR 监督造成的适配冲突？

**RQ2.** 能否在不改变最终层目标、总 FGL 权重和推理图的条件下，重新分配浅层
匹配查询的可靠性权重，从而改善严格 IoU 定位与 Recall？

**RQ3.** 训练期未来层蒸馏和 P3-only 特征增强能否从优化与表征两个不同位置补充
LRS-FDR，并形成正向的完整系统？

**RQ4.** 完整系统能否在 VisDrone 和 UAVDT 的匹配协议下均超过各自基线，同时
保持可接受的参数量与推理速度？

### 1.2 中心命题

论文不能写成“三个插件都涨点”。中心命题固定为：

> Dense UAV detection suffers from coupled deficiencies in native-aligned
> localization supervision, cross-layer decoder optimization, and
> high-resolution feature representation. We address these deficiencies with
> a coherent LRS-FDR--BPDD--FIA pipeline: LRS-FDR reorganizes fine-grained
> boundary distributions around native RT-DETR references and reliable
> shallow-layer supervision, BPDD transfers only beneficial future-layer
> distribution knowledge during training, and FIA refines the P3 feature path.

对应的数据依赖为：

```text
Image
  -> Backbone / Hybrid Encoder
  -> P3 -- FIA --> enhanced P3
  -> Decoder queries + native references
  -> LRS-FDR per-layer boundary distributions
       -> boxes and scores
       -> BPDD future-layer teacher (training only)
```

### 1.3 原创与继承边界

| 内容 | 论文身份 | 写作要求 |
|---|---|---|
| 33-bin 四边分布、non-uniform Integral、累计细化、基础 FGL | 来源于 D-FINE | 主动引用，不声称原创 |
| NA-FDR | native reference、stock assignment、normal matched-query supervision 的统一对齐 | 第一创新的基础设计 |
| LRS-FGL | representability-aware、同图像同层、总权重守恒、随层衰减的 reliability shrinkage | 第一创新内部的新机制 |
| BPDD | all-future softmin teacher + better-only gate | 第二创新；GO-LSD 只作为问题启发与近邻工作 |
| FIA | P3-only 双残差细化、联合通道/空间门控、零初始化残差和私有 RNG | 第三创新；只声称当前具体构造与集成 |

### 1.4 三项贡献的写作锚点

#### LRS-FDR

**问题**：历史 FDR 的 reference、assignment 和额外分布监督范围与原生 RT-DETR
路径未完全对齐，浅层低 IoU 正常匹配又容易获得过弱的 FGL 权重。

**设计**：NA-FDR 完成 native alignment；LRS-FGL 在可表示的浅层 normal matches
中执行随层衰减、总权重守恒的可靠性收缩。

**证据**：NA-FDR 相对 Original FDR 的 mAP/AP75 为 `+0.616/+0.699 pp`；LRS
相对 NA-FDR 的 AP75/Recall 为 `+0.471/+0.227 pp`，mAP 为 `+0.011 pp`。

#### BPDD

**问题**：固定最终层教师并不保证对每个目标和每条边都优于当前 decoder 层。

**设计**：从全部未来层按目标边质量构造 softmin teacher，并只在 teacher 更优时
执行 training-only distillation。

**证据**：旧 AP-FDR 严格配对中 val/test mAP 分别为 `+0.239/+0.283 pp`；这只
支持机制，LRS-FDR 新组合贡献等待 G 臂。

#### FIA

**问题**：640 输入下密集小目标依赖高分辨率 P3，级联修改 P4/P5 会扩大干预面。

**设计**：只在 P3 插入双残差 depth-wise refinement 和联合通道/空间门控，使用
零初始化残差与 private RNG 保持可控插入。

**证据**：fresh P3-only FIA-only 在 val/test 上的描述性 mAP 算术增益为
`+0.795/+0.810 pp`；与 LRS-FDR 的新组合贡献等待 H/I 臂。

## 2. 标题、摘要和贡献列表

### 2.1 推荐标题

**首选：**

> LRS-FDR: Native-Aligned Fine-Grained Distribution Refinement for Dense UAV Object Detection

这个标题把最可解释、内部消融最完整的 LRS-FDR 放在中心；BPDD 和 FIA 作为完整
系统中的互补设计进入摘要和贡献列表，不强迫标题塞入三个缩写。

**备选：**

1. Reliable Fine-Grained Localization with Progressive Decoder Distillation for UAV Object Detection
2. Native-Aligned Distribution Refinement and Feature Interaction for Dense UAV Detection
3. A Reliable Localization and Distillation Framework for Transformer-Based UAV Detection

最终标题在 Full 和 UAVDT 结果完成后冻结。若 Full 没有形成组合正增益，保留首选
标题并弱化“完整三模块系统”表述，不为了保留缩写而夸大结果。

### 2.2 Abstract 写作槽位（150--170 words）

Abstract 最后写，严格采用五句结构：

1. **Problem**：密集 UAV 图像中，小目标的边界不确定性、浅层 decoder 监督和
   高分辨率特征不足相互影响。
2. **Observation**：直接保留历史 FDR 的 preliminary/DN distribution paths 与
   原生 RT-DETR 定位组织并不匹配。
3. **Method**：提出 LRS-FDR，并用 BPDD 与 FIA 分别从训练优化和 P3 表征补充。
4. **Results**：填写 `[VISDRONE_FULL_RESULT]`、`[LRS_AP75_RECALL_RESULT]`、
   `[UAVDT_RESULT]` 和 `[FINAL_COMPLEXITY]`；未完成前不得写入旧 AP-FDR Full 数值。
5. **Significance**：强调 native-aligned、training-only distillation 和有限推理开销，
   不写 statistically significant、universally robust 或 SOTA。

### 2.3 最终贡献列表

正文建议只列三条：

1. **LRS-FDR.** We develop a native-aligned fine-grained distribution refinement
   module that uses native decoder references, stock assignments, and normally
   matched queries, together with representability-aware layerwise reliability
   shrinkage that preserves image-layer FGL weight and leaves the final-layer
   objective unchanged.
2. **BPDD.** We introduce a training-only progressive boundary-distribution
   distillation strategy that forms target-edge teachers from all future decoder
   layers and activates distillation only when the teacher is better than the
   current layer.
3. **FIA and system validation.** We enhance only the P3 feature path with a
   lightweight zero-initialized interaction module and evaluate the three
   components through internal VisDrone ablations, an efficiency analysis, and
   a Baseline-vs-Full UAVDT comparison.

第三条必须等 G/H/I 和 UAVDT Full 完成后保留“evaluate”措辞；若 UAVDT 尚未完成，
改为 “we study the complementarity on VisDrone”，不能预告不存在的跨数据集结果。

## 3. 四页正文详细大纲

### 1. Introduction（约 380--430 words）

#### Paragraph 1：任务与痛点

- 介绍 UAV 俯视图像中的小目标、密集分布、遮挡与边界像素敏感性；
- 解释为什么 AP75 比 AP50 更容易暴露定位质量问题；
- 引用 VisDrone/UAVDT 数据集论文和近期 UAV detection 工作；
- 不在第一段堆叠所有方法名。

#### Paragraph 2：现有方法缺口

- RT-DETR 提供端到端检测与原生 decoder reference/assignment；
- D-FINE 提供细粒度边界分布表示，但直接迁移历史路径会引入 native reference、
  preliminary reference、normal query 和 DN query 之间的组织冲突；
- 仅靠最终层或固定教师的跨层监督不能保证逐目标、逐边更可靠；
- 仅修改 P4/P5 或全 neck 会扩大对小目标任务的干预范围。

#### Paragraph 3：方法概览

- 用一段话给出 NA-FDR -> LRS-FGL -> BPDD -> FIA；
- 明确 FIA 在特征侧，LRS-FDR 在定位侧，BPDD 在训练优化侧；
- 强调 BPDD 与 LRS 权重分支在推理时均移除，只有 FIA 增加推理成本。

#### Paragraph 4：证据概览

- 当前可先写：NA-FDR 相对 Original FDR 的 mAP/AP75 为 `+0.616/+0.699 pp`；
- 当前可先写：LRS 相对 NA-FDR 的 AP75/Recall 为 `+0.471/+0.227 pp`，mAP
  基本保持 `+0.011 pp`；
- `[PENDING]` Full 相对 LRS、Baseline 和外部方法的位置；
- `[PENDING]` UAVDT Baseline-vs-Full；
- 最后接三条贡献。

**Transition：** 从“现有方法分别解决单个问题”过渡到 Related Work 中的三个
研究脉络。

### 2. Related Work（约 240--300 words）

#### 2.1 UAV Small-Object Detection

- 聚类裁剪/高分辨率路线：ClusDet、QueryDet、UFPMP-Det；
- 特征增强和近期轻量路线：HIC-YOLOv5、UAV-DETR、RAFDE、CFIA、VARDet；
- 归纳缺口：大量方法主要从输入/特征侧处理小目标，较少同时约束原生 DETR
  边界分布监督和跨 decoder 层的可靠知识传递。

#### 2.2 Distributional Localization and Decoder Distillation

- RT-DETR：端到端 detector 与 stock reference/assignment；
- GFL/DFL 类工作：离散分布定位背景；
- D-FINE：四边分布、non-uniform Integral、累计 refinement、FGL 与 GO-LSD；
- 本文差异：NA-FDR 的 native-aligned 组织、LRS 的均值保持可靠性收缩、BPDD 的
  all-future softmin 与 better-only gate。

**压缩规则：** Related Work 只保留与三项设计直接相关的 15--18 篇文献，不写
完整综述。外部结果表中的每个方法不必都在正文逐一介绍。

**Transition：** 以 “These observations motivate a native-aligned localization
pipeline with complementary optimization and feature refinement” 引入方法。

### 3. Proposed Method（约 760--850 words）

#### 3.1 Overall Architecture（约 90 words）

- 配合 Fig. 1(a) 说明 FIA、LRS-FDR、BPDD 的位置与数据依赖；
- 实线为推理路径，虚线为训练期 loss/weight path；
- 一句话说明 stock backbone、Hybrid Encoder、query classification、Hungarian
  matching 和 NMS-free inference 保持不变。

#### 3.2 Native-Aligned FDR（约 170 words）

必须包含：

- native decoder reference 替代 learned preliminary reference；
- stock Hungarian assignment 被直接复用；
- 额外分布监督只用于 normal matched queries；
- stock DN classification/L1/GIoU 仍保留，仅关闭额外 DN-FDR；
- 33-bin 分布、累计细化、Integral 与基础 FGL 明确归因 D-FINE。

建议保留一组紧凑公式：

\[
z_l=\sum_{j=0}^{l}\Delta z_j,\quad
d_l=\operatorname{Integral}(z_l),\quad
b_l=\operatorname{Decode}(r_l,d_l).
\]

#### 3.3 Layerwise Reliability Shrinkage（约 220 words）

必须解释四件事：

1. 只处理同图像、同浅层、四边目标均可表示的 normal matches；
2. IoU 权重停止梯度，并向该 image-layer group 的均值收缩；
3. 六层 `alpha=[0.25,0.20,0.15,0.10,0.05,0.00]`；
4. 每组总 FGL 权重守恒，final layer 完全等同 NA-FDR。

正文保留：

\[
\widetilde q_{b,l,k}=(1-\alpha_l)q_{b,l,k}
 +\alpha_l\bar q^R_{b,l},\qquad
\alpha_l=\alpha_0\left(1-\frac{l}{L-1}\right).
\]

以及一句守恒结论：

\[
\sum_k\widetilde q_{b,l,k}=\sum_k q_{b,l,k}.
\]

不要在正文展开 FP64 residual audit、所有防火墙单元测试和历史 EAW/DCF 失败；这些
放仓库补充材料。

#### 3.4 BPDD（约 170 words）

- 输入为 LRS-FDR 的逐层四边概率分布；
- 对早期层只使用未来层 `k>l`；
- 用目标插值 NLL 的 softmin 构造教师；
- 教师、误差和混合权重停止梯度；
- better-only margin 仅保留优于学生的目标边；
- 只处理 final stock assignment 的 normal queries，排除 DN；
- 正式参数：`weight=0.5`、`temperature=0.5`、`margin=0.02`、`eps=1e-6`；
- 训练后移除，不增加推理参数或 FLOPs。

正文最多保留教师公式和一条门控损失公式，详细推导放补充材料。

#### 3.5 FIA and Overall Objective（约 140 words）

- FIA 只增强 256-channel P3；P4/P5 保持原路径；
- 两个 depth-wise dual-residual blocks + channel/spatial attention；
- `Y=X+alpha(F(X)-X)`，`alpha` 零初始化；
- private RNG 保持后续 P4/P5/decoder 初始化轨迹；
- 总目标写成 stock RT-DETR losses + LRS-weighted FGL + BPDD，FIA 不引入额外
  detection loss；
- 推理时保留 LRS-FDR box path 和 FIA，移除 BPDD/LRS 权重计算。

**Transition：** 由“不同阶段、不同开销身份”过渡到实验中的两级消融与效率表。

### 4. Experiments（约 820--920 words）

#### 4.1 Datasets and Implementation Details（约 150 words）

必须报告：

- VisDrone train/val 为 6,471/548 张，10 类；本地 held-out test 不写成官方
  challenge server；
- UAVDT 的 split、类别映射、ignored-region 处理和 annotation conversion 必须来自
  最终 authority，当前不预填；
- VisDrone：100 epochs、seed 0、deterministic、640、batch 8、workers 8、MuSGD、
  `lr0=0.01`、`lrf=0.01`、AMP；
- 每臂按 best-val mAP50-95 选 checkpoint；
- independent evaluator：`conf=0.001`、`max_det=300`、`nms=false`、FP32；
- 主指标为 mAP50-95/AP50/AP75；LRS 消融额外报告 Recall；
- 单 seed 结果均标为 descriptive。

#### 4.2 Comparison with Existing Methods（约 140 words）

Table 1 使用明确 split 的正式会议论文结果。优先保留：

- 640-val 近邻：TPH-YOLOv5-x+UGS、UAV-DETR-EV2、UAV-DETR-R18、RAFDE、
  DM-EFS；
- 同会近邻：EMA、VARDet、ResBiDet；
- 不同高分辨率处理路线：QueryDet、UFPMP-Det，仅作协议背景。

最终表中的本文行必须替换为 **新 LRS-FDR+BPDD+FIA** 结果。旧 AP-FDR Full
`0.2961/0.2337` 只能保留在历史材料，不能改名进入新表。不同 input、backbone、
pretraining 和 evaluator 的结果只作 reported-value comparison，不计算因果增益，也
不声称 SOTA。

#### 4.3 LRS-FDR Internal Ablation（约 170 words）

Table 2(a) 固定为：

| Method | Native alignment | LRS | Recall | AP50 | AP75 | mAP50-95 |
|---|:---:|:---:|---:|---:|---:|---:|
| Original FDR | No | No | 0.491417 | 0.484700 | 0.294070 | 0.290698 |
| NA-FDR (`w/o LRS`) | Yes | No | 0.498339 | **0.493119** | 0.301061 | 0.296855 |
| LRS-FDR | Yes | Yes | **0.500606** | 0.491805 | **0.305773** | **0.296968** |

结果解释只写两层：

- NA-FDR 相对 Original：mAP/AP75/Recall `+0.616/+0.699/+0.692 pp`；
- LRS 相对 NA-FDR：AP75/Recall `+0.471/+0.227 pp`，mAP `+0.011 pp`，同时
  AP50/Precision 有所回落。

主文不展开 Large 130 GT 和十类别表；用一句话披露 LRS 相对 NA-FDR 的 Tiny/Small
mAP 回落，完整数据指向仓库补充材料。

#### 4.4 System Ablation and Complementarity（约 170 words）

Table 2(b) 使用同一声明协议的四行：

| Method | BPDD | FIA | P | R | AP50 | AP75 | mAP50-95 | 状态 |
|---|:---:|:---:|---:|---:|---:|---:|---:|---|
| LRS-FDR | No | No | 0.579512 | 0.500606 | 0.491805 | 0.305773 | 0.296968 | 已冻结 |
| LRS-FDR + BPDD (`g`) | Yes | No | `[G]` | `[G]` | `[G]` | `[G]` | `[G]` | 待新结果 |
| LRS-FDR + FIA (`h`) | No | Yes | `[H]` | `[H]` | `[H]` | `[H]` | `[H]` | 待新结果 |
| Full (`i`) | Yes | Yes | `[I]` | `[I]` | `[I]` | `[I]` | `[I]` | 待新结果 |

写作逻辑：

- `g - LRS-FDR` 归因 BPDD；
- `h - LRS-FDR` 归因 FIA；
- `Full - g` 和 `Full - h` 检查两者能否互补；
- `Full - RT-DETR-L` 是系统总体增益；
- G/H/I 共享最终 launcher 和协议，旧 AP-FDR 组合不参与新组合归因。

#### 4.5 Efficiency and UAVDT（约 150 words）

Table 3 采用两个紧凑 panel：

**Panel A：Efficiency**

| Method | Params | GFLOPs | Median latency | FPS |
|---|---:|---:|---:|---:|
| RT-DETR-L | `[FINAL]` | `[FINAL]` | `[FINAL]` | `[FINAL]` |
| LRS-FDR | `[FINAL]` | `[FINAL]` | `[FINAL]` | `[FINAL]` |
| LRS-FDR + BPDD | 与 LRS-FDR 推理图相同 | 相同 | `[FINAL]` | `[FINAL]` |
| Full | `[FINAL]` | `[FINAL]` | `[FINAL]` | `[FINAL]` |

可以提前写的机制结论：BPDD 不进入推理图；LRS 不增加参数或推理操作；Full 的新增
推理开销只能来自 FIA。最终数值仍需用新 checkpoint 统一实测。

**Panel B：UAVDT**

| Method | AP50 | AP75 | mAP50-95 |
|---|---:|---:|---:|
| Baseline | `[UAVDT_BASELINE_AUTHORITY]` | `[PENDING]` | `[PENDING]` |
| Full | `[PENDING]` | `[PENDING]` | `[PENDING]` |

UAVDT 只支持 matched in-domain second-dataset effectiveness / multi-dataset
applicability。不要写 zero-shot transfer、cross-domain generalization 或单模块贡献。

### 5. Conclusion（约 90--120 words）

结论用三句：

1. 总结 native-aligned LRS-FDR、training-only BPDD 和 P3-only FIA；
2. 写入最终 VisDrone 与 UAVDT 结果，不重复全部表格数字；
3. 限制为 single-seed descriptive evidence，并给出多 seed/更大输入分辨率作为未来工作。

不要在 Conclusion 新增没有在实验中验证的机制解释。

## 4. 图表与版面规划

### Fig. 1：唯一正文主图，建议三面板

- **(a) Overall pipeline**：FIA -> LRS-FDR -> BPDD；实线/虚线区分推理与训练；
- **(b) Native alignment**：Original FDR 与 NA-FDR 的 reference/query 组织差异；
- **(c) LRS-FGL**：representability firewall、mean shrinkage、alpha schedule、sum conservation。

图内不出现历史 runtime aliases、EQuAL、DCF 或 AP-FDR；不画未经测量的实际 IoU
分布；不把 BPDD 画成独立 teacher network。

### 正文表格

| 表 | 内容 | 当前状态 | 版面策略 |
|---|---|---|---|
| Table 1 | 外部 VisDrone 对比 + 新 Full | 外部行已存在；新 Full 待填 | 只保留 7--10 个最相关方法 |
| Table 2(a) | Original / NA / LRS | 完成 | 保留 Recall、AP50、AP75、mAP |
| Table 2(b) | LRS / G / H / Full | G/H/I 待填 | 与 2(a) 合成双 panel |
| Table 3(a) | Params/GFLOPs/Latency/FPS | 新 Full 待测 | 数字过多时只保留 Params/GFLOPs/FPS |
| Table 3(b) | UAVDT Baseline / Full | 待完成 | 两行即可 |

### 仓库补充材料

- 十类别和 Tiny/Small/Medium/Large；
- epoch 91--100 mean/slope；
- BPDD 详细门控和 FIA topology；
- 完整训练超参数、authority、checkpoint hashes；
- 失败路线 EAW/DCF 和旧 D-FINE-S 重跑只作审计，不进入主文。

## 5. Claim--Evidence Map

| Claim ID | 论文主张 | 当前证据 | 状态 | 可用措辞 |
|---|---|---|---|---|
| C1 | NA-FDR 比 Original FDR 更适合原生 RT-DETR-L | mAP +0.616、AP75 +0.699、全部总体指标为正 | 已完成 | improves under the frozen fixed-seed protocol |
| C2 | LRS 改善严格 IoU 定位与 Recall | AP75 +0.471、Recall +0.227、mAP +0.011 vs NA | 已完成 | improves AP75 and recall while maintaining mAP |
| C3 | 完整 LRS-FDR 优于 Original FDR | mAP +0.627、AP75 +1.170、Recall +0.919 | 已完成 | the complete module yields descriptive gains |
| C4 | BPDD 是无推理增量的 future-layer distillation | 公式/代码 + 旧严格 paired + 相同推理图 | 机制已完成，新组合待验证 | training-only and inference-free；组合精度待 G |
| C5 | FIA 是轻量 P3-only 增强 | fresh FIA-only val/test +0.795/+0.810 pp 算术增益 | standalone 已完成，新组合待验证 | improves the corresponding baseline in historical standalone runs |
| C6 | BPDD/FIA 与 LRS-FDR 互补 | G/H/I | 待完成 | 未完成前禁止写 |
| C7 | Full 在 VisDrone 具有竞争力 | 新 I 与外部表 | 待完成 | competitive；除非证据充分，不写 SOTA |
| C8 | Full 在 UAVDT 也有效 | matched Baseline/Full | 待完成 | second-dataset effectiveness，不写 universal generalization |
| C9 | Full 保持合理效率 | 新 checkpoint 统一 benchmark | 待完成 | lightweight / real-time 仅在最终数值支持时使用 |

## 6. 最终实验矩阵与论文判定规则

### 6.1 VisDrone

| 臂 | 方法 | 论文用途 | 状态 |
|---|---|---|---|
| A | RT-DETR-L Baseline | 系统总体基线 | 已有 canonical 结果，最终表前核对协议身份 |
| B | Original FDR | 历史 FDR 对照 | 已完成 |
| C | NA-FDR | LRS-FDR 的 native-aligned foundation | 已完成 |
| D | LRS-FDR | 第一创新完整模块 | 已完成 |
| G | LRS-FDR + BPDD | BPDD 消融 | 待完成/待入库 |
| H | LRS-FDR + FIA | FIA 消融 | 待完成/待入库 |
| I | LRS-FDR + BPDD + FIA | 最终 Full | 待完成/待入库 |

### 6.2 结果分支

| 结果形态 | 论文处理 |
|---|---|
| `I > G, H, D`，且 G/H 均不低于 D | 最强路径：三模块互补，按当前三贡献投稿 |
| `I > D`，但 I 低于 G 或 H | 不写“additive complementarity”；最终方法改为数值最优组合，较弱模块降为辅助分析 |
| G 或 H 单独为负，但 I 为全表最好 | 可讨论 interaction，但必须披露负的单模块臂，不写每项独立有效 |
| `I <= D` | 不把 Full 作为最终方法；以 LRS-FDR + 最强正模块重组论文 |
| UAVDT Full > Baseline | 支持第二数据集 effectiveness |
| UAVDT Full <= Baseline | 保留 VisDrone 结论，删除 across-dataset 改善主张并将 UAVDT 写入 limitation |

“正”主要按预先指定的 mAP50-95 判断。AP75/Recall 可以解释机制，但不能在 mAP
失败后临时替换主指标选模。也不要求 Precision、Recall、AP50、AP75 全部同时上升。

## 7. 接下来必须完成的工作

### P0：没有这些不能冻结结果段和 Abstract

- [ ] 完成 G/H/I 各 100 epochs，并保存 `results.csv`、`args.yaml`、`best.pt`、
  `last.pt`、train log 和 launch authority；
- [ ] 每臂按 best-val mAP50-95 选择 checkpoint；
- [ ] 对 D/G/H/I 使用同一 evaluator 得到 P、R、AP50、AP75、mAP50-95；
- [ ] 生成 G/H/I comparison JSON/CSV 和 SHA-256 manifest；
- [ ] 用新 checkpoint 重做统一 Params、GFLOPs、median/P90 latency、FPS；
- [ ] 绑定 UAVDT Baseline 的真实 authority、split、class mapping、initialization 和
  metrics；
- [ ] 完成 UAVDT-specific launcher、dry-run、Full 训练和成对评估；
- [ ] 把最终证据提交到材料仓库，旧 AP-FDR 结果保持历史身份。

### P1：可以立刻写，不需要等待训练

- [ ] 用 IEEE LaTeX 创建 `main.tex` 和 `references.bib`；
- [ ] 先写 Section 3 Method，因为公式、配置和边界已经冻结；
- [ ] 写 Section 4.1 Setup，所有参数从 authority/runbook 抽取；
- [ ] 写 Section 4.3 LRS-FDR internal ablation；
- [ ] 写 Related Work 初稿，并核验每条 BibTeX/DOI；
- [ ] 按三面板方案画 Fig. 1；
- [ ] 从外部对比表筛选 7--10 个正文方法；
- [ ] 写 Introduction 的前三段，结果概览段保留占位符；
- [ ] 准备 Data Availability、Ethics、Funding、Conflict of Interest、Author
  Contributions 和 AI-use disclosure 的真实信息，缺失信息不代填。

### P2：结果完成后再写

- [ ] 填 Table 1 的新 Full 行；
- [ ] 填 Table 2(b) 的 G/H/I；
- [ ] 填 Table 3 efficiency 与 UAVDT；
- [ ] 按结果分支决定最终系统身份；
- [ ] 写 Section 4.2、4.4、4.5 的分析；
- [ ] 写 Conclusion；
- [ ] 最后写 Abstract、标题和贡献列表的结果句；
- [ ] 全文检查所有 “improve/competitive/efficient” 是否都有表格证据。

### P3：投稿前质量门

- [ ] 参考文献 18--25 篇，正文引用与 `.bib` 零孤儿；
- [ ] 核对 RT-DETR、D-FINE/GO-LSD、VisDrone、UAVDT、GFL/DFL 和近期 UAV
  detection 论文的原始页面/DOI；
- [ ] 禁止用旧 Full 数值填新 Full；
- [ ] 禁止把本地 held-out test 写成官方 VisDrone challenge test；
- [ ] 禁止使用 significant、robust across seeds、universal、first-ever 和 SOTA，
  除非另有足够证据；
- [ ] 将 main content 压入官方 4 页，第 5 页仅放官方允许内容；
- [ ] 检查匿名要求、作者信息、PDF 字体嵌入、图中文字大小和 IEEE PDF compliance；
- [ ] 进行一次学术完整性检查和一次对抗性 reviewer audit；
- [ ] 至少提前一天完成投稿系统上传与 PDF 预览。

## 8. 从现在到投稿的时间表

| 日期 | 主要产物 | 完成定义 |
|---|---|---|
| 8/29--8/31 | 方法、Setup、LRS 消融英文初稿；Fig. 1 草图 | 不依赖 G/H/I 的正文完成 |
| 9/1--9/4 | G/H/I 证据冻结与统一评估 | comparison + manifest 可复查 |
| 9/5--9/7 | UAVDT Baseline authority + Full；最终复杂度 | 两臂表和效率表可填 |
| 9/8--9/10 | Results、Introduction、Related Work 完整初稿 | 四页内容第一次闭环 |
| 9/11--9/12 | Abstract、Conclusion、图表压缩、引用核验 | 无占位符、无孤儿引用 |
| 9/13 | 第一轮 reviewer/对抗性审计 | 所有 Major 问题有修订动作 |
| 9/14 | IEEE 模板、声明、PDF compliance | 可上传 PDF |
| 9/15 | 投稿系统预上传与最终校对 | 留出至少一天缓冲 |
| 9/16 | 正式提交 | 以投稿系统实际时区为准 |

如果训练时间拖延，优先顺序固定为：**G/H/I -> UAVDT Full -> 最终复杂度 ->
多 seed**。不再新增第四个机制，不恢复 EAW/DCF，不重新调 `alpha0=0.25`。

## 9. 文献使用计划

### 必须覆盖的来源族

1. RT-DETR 与 DETR-family real-time detection；
2. GFL/DFL 与 distributional box regression；
3. D-FINE 与 GO-LSD；
4. VisDrone 和 UAVDT 数据集/benchmark；
5. UAV small-object detection：ClusDet、QueryDet、UFPMP-Det、HIC-YOLOv5、
   UAV-DETR、RAFDE、CFIA、SR-TOD、DQ-DETR、EvOD、VARDet/ResBiDet；
6. 只选能直接支撑本文问题、机制或外部表的文献，不为凑数量加入无关论文。

### 已有可用来源入口

- [VisDrone 外部会议方法对比](../results/EXTERNAL_VISDRONE_COMPARISON_ZH.md)
- [机器可读外部结果](../results/external_visdrone_comparison.json)
- [来源清单](../evidence/source_manifest.json)
- [D-FINE 固定来源边界](../../third_party/dfine_7fe2f888/AUTHORITY.json)

文献数量达到 18--25 篇且下面三类均有覆盖即可停止搜索：任务/数据集、定位与
蒸馏机制、近期 UAV 检测对比。无需为了形式扩大到系统综述规模。

## 10. 允许与禁止的结果措辞

### 当前已经可以使用

> Under the frozen single-seed VisDrone protocol, NA-FDR improves mAP50-95 and
> AP75 over Original FDR by 0.616 and 0.699 percentage points, respectively.

> Adding LRS-FGL further improves AP75 and recall by 0.471 and 0.227 percentage
> points while maintaining mAP50-95 (+0.011 points).

> The complete LRS-FDR improves mAP50-95 and AP75 over Original FDR by 0.627
> and 1.170 percentage points, respectively.

### 必须等新结果

- “BPDD and FIA are complementary to LRS-FDR”；
- “The Full model achieves ... on VisDrone”；
- “The method improves UAVDT”；
- “The Full system runs at ... FPS”；
- “The method is competitive with / outperforms [external method]”。

### 禁止句式

- We first propose discrete boundary distribution regression / Integral / FGL.
- LRS significantly improves overall mAP.
- Every component independently improves every metric.
- Our model improves all scales and all classes.
- The old AP-FDR Full checkpoint is the new LRS-FDR Full model.
- Single-seed results demonstrate statistical stability or universal generalization.

## 11. 写作产物清单

最终论文目录至少应包含：

```text
paper/
  main.tex
  references.bib
  figures/
    method_overview.pdf
  tables/
    visdrone_main.tex
    ablation.tex
    efficiency_uavdt.tex
  supplement/
    class_scale_results.pdf or .tex
    reproducibility.md
  submission/
    main.pdf
    source-package.zip
```

本材料仓库不应存储 PAT、服务器密码或其他凭据。源码与证据通过公开仓库 URL、
tag、commit 和 SHA-256 绑定。

## 12. 权威材料

- [当前实验状态](../CURRENT_RERUN_STATUS_ZH.md)
- [LRS-FDR 方法](../methods/FDR_ZH.md)
- [BPDD 方法](../methods/BPDD_ZH.md)
- [FIA 方法](../methods/FIA_ZH.md)
- [LRS-FDR 结果](../results/LRS_FDR_RESULTS_ZH.md)
- [LRS-FDR 证据包](../evidence/lrs_fdr_formal100_20260828/README.md)
- [最终 VisDrone 实验交接](../experiments/VISDRONE_FINAL_EXPERIMENT_HANDOFF_ZH.md)
- [创新定位与对抗性审计](NOVELTY_POSITIONING_AND_ADVERSARIAL_AUDIT_ZH.md)
- [图表规划](../figures/FIGURE_PLAN_ZH.md)
- [冻结源码 runbook](https://github.com/kkc236/uav-detection-baselines/blob/visdrone-lrs-system-v1/docs/VISDRONE_LRS_SYSTEM_RUNBOOK_ZH.md)

这份蓝图是当前写作源文件。任何最终数值更新先进入机器证据和结果页，再回填本文档
和 LaTeX；不得从聊天记录或历史别名直接复制数字。

# Clean-FDR 的作者身份、继承边界与出版命名核查

核查日期：2026-09-17。范围：只读历史源码、冻结输入、正文和构建脚本；仅进行文本比较和文件哈希核对。未运行神经模型、训练、内部组件测试、逐图推理或服务器命令。本文是给主稿重构使用的研究报告，不修改任何冻结证据、正文或构建脚本。

## 1. 结论先行

**Clean-FDR 是作者在 RT-DETR 宿主上设计并实现的一种定位路径配置，不能作为外部官方 FDR 基线呈现。** 它把分布解码及 FGL 目标共同使用的参考，从第一层传统回归头给出的 preliminary box，改为进入解码器的 reference；同时停用额外 preliminary-box 监督与额外 DN-FDR 监督，保留 RT-DETR 的检测、辅助层和 stock DN 损失。这个成组设计属于作者路线，后续 GFDR / LRS-GFDR 延续了它。

**D-FINE 的继承部分必须继续明确归属。** 每边 33 个离散候选、非均匀支撑、softmax 后积分解码、跨层累积边界 logits、在一个固定参考框坐标系中表达各层修正，以及相邻 bin 的 IoU 加权 FGL，都已在 D-FINE 中存在。作者改变的是固定坐标系的起点和宿主中的监督路径；不能把“固定六层坐标系”本身改写为作者首创。

**实现存在一项直接影响措辞的细节：Clean 配置没有从计算图中删除 preliminary head。** 精确历史源码仍计算 preliminary box，只是不把它选为分布参考，且不施加额外 preliminary 损失。不能写成“remove the preliminary head”、由此推断少了参数或相应 FLOPs。应写“bypass the preliminary prediction when selecting the distribution reference”或“disable preliminary-reference use and additional preliminary supervision”。

**命名建议：将 Original / Clean 两个历史工程别名移到证据映射说明，正文用构造描述，并对全部作者内部版本统一标记 ours。** “作者设计”不等于已证明文献首次、独立全新算法，也不等于已经隔离出每项设计的精度贡献。

## 2. 核查依据与身份链

所有相对路径均相对工作区 `C:/Users/16946/Documents/OBJECTIVE CHECK PAPER`。本节中的源码行号取自注明的 Git 提交，不是当前工作树。

| 对象 | 精确权威来源 | 本次核查结果 |
| --- | --- | --- |
| 历史 preliminary-reference 集成（V02；旧名 Original FDR） | `output/cvm_literature_architecture_20260917/inputs/original_fdr_run.json`；提交 `d97e1eb7f98414752a1c1f38287697db3f2a0679` | 本地仓库 `tmp-work/lrs-system-visdrone-rebuild` 保有真实提交对象；已读取 head、loss、host glue、initial-state loader。 |
| 作者 incoming-reference 配置（V03；旧名 Clean-FDR） | `inputs/clean_fdr_authority.json`；提交 `ec4e2a463db7a53f7c4c9c4bc9edabdf5c39f40b` | 同一仓库保有真实提交对象；已读取对应配置与上述源码，避免从后续几何版本反推。 |
| 冻结 Clean 配置 | `inputs/clean_fdr_historical_config.yaml` | 与 `ec4e2a46:configs/rtdetr-l-clean-fdr.yaml` **逐字节相同**；SHA256 `774c2ef5da96366610b7a7ffa39bf3087077e0b63ac7222d2a014f6244bee6e6`。 |
| 冻结 Clean loss | `inputs/clean_fdr_historical_loss.py` | 与 `ec4e2a46:src/fdr_loss.py` **逐字节相同**；SHA256 `d9f1743f0d3c29e5f3a40aeeae4c12bb07b9d54c0898692d9e436eae887d4406`。 |
| 冻结 Clean math | `inputs/clean_fdr_historical_math.py` | 与 `ec4e2a46:src/fdr_math.py` **逐字节相同**，也与 `d97e1eb7:src/fdr_math.py` 相同；SHA256 `794af04c8cb1ca89c110943a5f3749f120ef3e9f8bc5b0175d9cb33946427401`。 |
| 后续几何 / LRS | `inputs/geometry_evidence/source_f56b210/src/fdr_head.py`、`inputs/frozen_fdr_math.py`、`inputs/frozen_fdr_loss.py` | 用来确认后续扩展边界，不冒充 V03 实验源码。 |
| D-FINE 官方代码 | 官方仓库固定提交 `7fe2f8889f0b7b817f20c315b40fc15a4fb64ae6` | 本次在线读取固定提交 raw decoder、criterion、utils；关键实现与论文描述相符。 |

上表中 `inputs/` 的完整前缀为 `output/cvm_literature_architecture_20260917/inputs/`。

两个历史 head 文件的精确 Git blob 内容 SHA256：

- `d97e1eb7:src/fdr_head.py`：`c8f800d43d3ac8ed91bbf53d5a76e84641e3c313fd115ad75921b19a63b02da2`。
- `ec4e2a46:src/fdr_head.py`：`027d312cee359002f8637a0a8690e51ac7179570b5d5ebf550fb338d80919ab3`。

### 2.1 初始化：有已知相同项，也有尚未证明的项

V02 和 V03 的权威记录均指向相同初始状态文件，SHA256 均为：

`51AAB2EB3FB7D123501C69C7B8DC90FF3EA0B9344A108EDEEF2C7D6DCDBB742D`。

源码进一步支持这个登记项并非纯文本装饰：`ec4e2a46:scripts/train_dcf_fdr.py:48–58` 为 clean arm 选中 Clean YAML；`112–116` 把 initial-state 路径交给 `FDRTrainer`。`src/rtdetr_fdr.py:473–477` 以 `variant="fdr"` 加载；`src/fdr_protocol.py:405–421` 合并登记的 `fdr_public_state` 与 `private_state` 并 strict load。唯一允许的额外初始化前缀是 distribution-feedback 模块（`src/rtdetr_fdr.py:384–396`），但 Clean YAML 的该功能为 false。

可写“V02 与 V03 的运行记录绑定同一冻结初始化文件，并有严格装载代码支持”。仍不宜写“所有历史行都完全匹配”，因为提交、构造入口等不同；本次没有重放启动状态，也未逐项认证全部训练执行轨迹。两提交之间存在 YAML 封装和 private generator 初始化实现变化，不能把整个 Git diff 直接等同为一项机制消融。不过，strict load 的证据也意味着不能凭初始化代码不同，就断言 V02/V03 实际加载了不同权重。

## 3. 精确来源矩阵

| 机制 / 决定 | 谁的已有机制或设计 | 直接证据 | 出版表述边界 |
| --- | --- | --- | --- |
| 33-bin 边分布、非均匀支撑、积分解码、累积 logits | D-FINE 的 FDR；作者移植到 RT-DETR | 官方 decoder:428–431；官方 utils `weighting_function`；Clean math:16–36、62–99；V02/V03 math 哈希完全相同 | 应明确 “adopt / build on D-FINE”；不能作为 Clean 新数学。 |
| 固定分布参考跨六层；attention reference 随预测更新 | D-FINE 已有两种 reference 的分工 | 官方 decoder:423–425 建立 `ref_points_initial`；429–440 重复使用；446 更新 `ref_points_detach` | “固定 frame”及其带来的跨层坐标一致性属于继承。 |
| 选择 incoming decoder reference 作为这个固定 frame | 作者在 RT-DETR 宿主中的具体路径选择 | Clean head:297、316–324、341–351；V02 head:151–165 固定使用 preliminary | 可作为作者设计点解释；不是声称全领域首次使用输入 reference。 |
| FGL target 与新 frame 同步 | 作者集成选择的必要组成 | Clean host `src/rtdetr_fdr.py:320–335`；Clean loss:227–235 | 不是仅换展示名称：解码与 GT-to-bin 映射都改变参考。 |
| 停用额外 preliminary-box L1/GIoU | 作者 Clean 路径的监督选择 | Clean YAML:46；host:255–258；loss:411–419 | 可以说额外监督关闭；不能说计算头已被删除。 |
| 停用额外 DN-FDR / DN-FGL 及 DN preliminary 监督 | 作者 Clean 路径的监督选择 | Clean YAML:47；loss:421–449 | 不等于删除 stock DN；也不等于 DN query 不再经过分布头。 |
| 保留 stock 检测、辅助与 DN 损失、匹配接口 | 作者选择沿用 RT-DETR 宿主契约，机制本身属于 RT-DETR | loss:1–6、157–171、367–373；host:315–335 | “retain stock DN”是集成界限，不应包装为全新 DN 算法。 |
| 普通 query 相邻-bin FGL，按 detached IoU 加权 | D-FINE 的 FGL，被作者接入 stock assignment | Clean loss:227–255、397–409；官方 criterion:139–185 | FGL本体与 IoU 权重来自已有工作；matching/normalization 的宿主实现需如实说明。 |
| 显式 reference-scale / precision extent floors，中心保持、identity surrogate | 后续作者 GFDR 路径 | frozen math:248–298；Clean math 只有旧 `distance2bbox`:174–195 | 与 Clean 区分；不要把该后续规则倒记为 Clean 的实验处理。 |
| 同图同层 eligible IoU 向均值收缩，随层减弱 | 后续作者 LRS 规则 | frozen loss:57–115、341–351 | 与原始 IoU 加权区分；不是声称权重中的 IoU 是新发明。 |
| 外部完整 D-FINE-L detector | D-FINE 作者的模型；稿件另有本地 scratch reproduction | 官方论文描述 FDR、GO-LSD 和架构调整；官方 criterion:296–307、188 起等 | 不得与 V02、V03 同名或合并成一个“官方 FDR 基线”。 |

### 3.1 Reference 的准确文字和最小公式

令进入 decoder 的参考为 `r_in`，第一层传统回归输出为 `p`。两历史版本均遵循“后续边界分布在固定参考下解释”的 FDR 结构，但采用不同起点：

- V02：`r* = stop_gradient(p)`。
- V03：`r* = stop_gradient(r_in)`。
- 每层分布 logits 仍累加；解码仍使用同一个 `r*`。
- 更新的预测框继续供下一层 attention 使用；它并没有取代分布解码的固定 `r*`。

这里的 `r_in` 是进入 decoder 的当前 query 参考，不能泛称“原图 GT 框”或所有层共享的同一个全局 anchor。各 query 有自己的参考。`ec4e2a46:src/fdr_head.py:297` 对 incoming logits 做 sigmoid，直到 index 0 选择固定参考前都没有赋予该变量新的框值。

更关键的是，`src/rtdetr_fdr.py:320–325` 同步让 FGL 使用 `evidence.references[0]`，而非未被选中的 preliminary box。因此，作者选择改变了实际的分布几何意义与监督坐标；不是仅仅删掉一个 loss 项。

### 3.2 “关闭 preliminary”到底关闭什么

`ec4e2a46:src/fdr_head.py:317–319` 无条件执行 preliminary MLP 与 sigmoid；`:320–324` 的条件只选择初始参考；`:360` 还缓存 preliminary 输出。因此当前证据支持：

1. 不把 preliminary 输出选作分布参考。
2. 不施加该分支额外定位损失。
3. FGL target 同步改用 incoming reference。

不支持：物理删除 head、从模型参数中移除 head、证明减少相应计算、改变 backbone/分类头。损失没有依赖该输出时，preliminary 预测对最终优化路径的作用可被旁路；这与“源码不再计算该分支”是不同层面的陈述。

### 3.3 “关闭 DN-FDR”到底关闭什么

Clean loss 的 `super().forward(...dn_bboxes, dn_scores, dn_meta...)` 在额外 FDR gates 之前始终调用。`supervise_dn_fdr` 只控制之后加入的分布 FGL 与附加 preliminary 项。DN queries 仍可经过分布定位头，其输出仍接受 stock DN box/class 损失。

推荐用语是 **“retain RT-DETR denoising losses while disabling additional DN-side FDR supervision”**。不要写“remove DN”、 “no denoising”、 “apply the localization head only to normal queries”。“FGL only on ordinary queries”则是对损失作用范围的准确描述。

## 4. 为什么 V02 也不应叫 Original / complete official transfer

V02 已经是作者在 Ultralytics RT-DETR 中的宿主集成，不是官方 D-FINE 检测器。其 `d97e1eb7:src/rtdetr_fdr.py:162–170` 采用作者 `FDRDetectionLoss`；`:220–235` 保留 encoder-first 的 stock RT-DETR loss 契约，传入 normal / DN FGL 及 preliminary 输出。V02 的 official math 与 FGL机制并不使整个模型成为官方模型。

官方 D-FINE 另外有 GO-LSD / DDF、跨层 matching union、自己的模型结构与 loss 实现；官方 criterion:296–307 组合各层匹配，:188 起有 teacher-corners distillation。作者历史 loss 复用 stock matching 而不采用这套完整损失。因此“complete FDR/FGL transfer”即使想表达“我们当时移入的几项都开启”，也容易使读者以为这是功能完全等价的官方移植。更可靠的名词是 **“preliminary-reference FDR integration in RT-DETR”**，随后列清本版本实际打开的监督。

需同时避免另一个方向的过度收缩：集成并非“完全没有作者工作”。源码记录了新增分布头、缓存和切分 normal/DN tensors、把 FGL 接到宿主 assignment、构造选项与 frozen initialization 适配。它们属于作者实现与系统设计工作；该事实本身并不证明需要把所有工程工作都提升为独立算法贡献。

## 5. 出版级标签建议

### 5.1 推荐主方案：正文用构造名称，历史别名仅供映射

| ID | 推荐表格短标签 | 正文第一次出现时的完整解释 | 历史归档别名 |
| --- | --- | --- | --- |
| V02 | **FDR + preliminary reference (ours)** | Our preliminary-reference FDR integration in RT-DETR, with ordinary/DN FGL and additional preliminary-box supervision. | Original FDR |
| V03 | **FDR + incoming reference (ours)** | Our incoming-reference localization design, with ordinary-query FGL and stock RT-DETR DN retained, and additional preliminary/DN-FDR supervision disabled. | Clean-FDR |
| V04 | **Incoming-reference FDR + geometry (ours)** | V03 construction with the registered geometry-constrained decoding version. | Clean-FDR + geometry |
| V06 | **LRS-GFDR (ours)** | Incoming-reference construction with feasible decoding and layerwise reliability shrinkage. | LRS-GFDR |

短标签省略了 loss 开关，所以机制表必须有 reference、ordinary FGL、extra preliminary supervision、extra DN-FDR、stock DN、geometry、LRS 等列或逐项说明。不能让短标签暗示 V02→V03 只改变 reference 一个变量。

若表格列宽有限，可使用 **“Preliminary-reference design” / “Incoming-reference design” / “+ geometry” / “+ geometry + LRS”**，并在 caption 首句明说四行均为作者的 RT-DETR localization designs。这样既承认作者身份，又不为了归属强造新的缩写或“全新算法”名称。

不推荐继续使用 “Clean” 作为正式方法身份：读者容易理解成官方实现的干净重现或纯清理。也不推荐 “Original FDR”，因为 Original 的默认参照往往是 FDR 原论文。`Vanilla FDR`、`pure FDR`、`official FDR`、`full D-FINE transfer`也有类似问题。

### 5.2 可供主稿采用的英语段落（只是建议，未改正文）

> We develop an incoming-reference localization path for RT-DETR using the distributional primitives of D-FINE. The incoming query reference defines a shared frame for distribution decoding and FGL targets across decoder layers. We retain ordinary-query FGL and RT-DETR's detection, auxiliary, and denoising losses, while bypassing the preliminary prediction for reference selection and disabling additional preliminary-box and DN-side FDR supervision. The fixed-frame refinement and adjacent-bin FGL follow D-FINE; the reference selection and supervision configuration are our host-specific design choices. Geometrically feasible decoding and layerwise reliability shrinkage extend this construction.

内部结果表的建议 caption：

> Historical localization designs implemented in our RT-DETR host. All rows adopt D-FINE's distributional representation. The preliminary-reference and incoming-reference rows differ in reference selection and additional supervision, as specified in the mechanism table. The registered V02 and V03 runs share an initial-state artifact; the table does not establish a fully matched, multi-seed ablation across all historical versions.

不必把“历史”二字放到每个方法名中，但在实验设计说明中交代版本来自不同源码记录是必要的。

## 6. 结果应如何支持作者设计，而不越界归因

冻结的四行原值保持：

| ID | 构造 | AP | AP50 | best epoch |
| --- | --- | ---: | ---: | ---: |
| V02 | 作者 preliminary-reference 集成 | 29.078 | 48.473 | 92 |
| V03 | 作者 incoming-reference 设计 | **29.696** | 49.320 | 88 |
| V04 | incoming-reference + geometry | 29.361 | 49.130 | 91 |
| V06 | LRS-GFDR | 29.620 | **49.382** | 92 |

来源：`inputs/internal_localization_versions.md`、`inputs/lrs_comparison_provenance.json`；AP 单位是百分数，差值为百分点。

- V02→V03 的记录差值为 **+0.618 AP / +0.847 AP50**。可以作为“作者 incoming-reference 与监督配置这一成组设计的记录结果”，不可拆成某一个开关的独立因果收益。
- V03→V04 为 **−0.335 AP**。明确保留这一行，不把几何规则写成已经被该表证明的纯精度提升。
- V04→V06 为 **+0.259 AP**；这支持描述历史版本之间的结果变化，不证明所有配置、所有 seed、所有数据集都受益。
- V06 相对 V02 为 **+0.542 AP / +0.909 AP50**，相对 V03 为 **−0.076 AP / +0.062 AP50**。因此不能把 LRS-GFDR 写成四行 AP 的最优者，也不能让名称更换掩盖 V03 的最高 AP。
- 这四行不能给出真实训练中非正 extent 的发生频率、低 IoU 监督不足的频率、各机制独立贡献、运行稳定性的跨数据集保证。几何属性和权重恒等式可以由解析与代码说明，但这些不是检测收益的替代证明。

“作者的设计探索”与“已经建立充分独立算法新颖性”应分开：当前记录足以支持前者，不能仅由开关/源码归属推导后者。尤其 D-FINE 官方论文已经讨论向多种 DETR 迁移，不能把“将 FDR 用于 RT-DETR”单独当作从未出现的研究问题。

## 7. 当前正文 / 构建脚本的具体命名风险

以下为核查时 `output/cvm_literature_architecture_20260917` 版本；主任务若已继续修改，应按语义定位，不机械依赖行号。

1. `source/body.tex:20`、`:36`、`:50`、`:241–248` 和 `build.py:24–54` 高密度出现 complete / Original / intermediate。虽 `body.tex:242` 已声明是 our host integration，并非 unmodified D-FINE，但表头与短标签更显眼，仍会把 V03 的作者设计压成外部方法删减版。建议把机制表也加入 incoming-reference 这一作者阶段，或至少在两列表中明确它在最终方法中的来源。
2. `body.tex:68` 对 fixed frame 继承关系已经准确，应保留其技术实质。需要加强的是 incoming reference 与监督构造的作者定位，及这些选择早于 GFDR/LRS；不是抹掉 D-FINE 的固定 frame。
3. `body.tex:112` 的 stock DN 保留和 extra DN-FDR 关闭总体准确；应避免其他位置用笼统“no DN”覆盖它。
4. `build.py:51–54` 仅最终行标 `(ours)`，前面几行缺少统一作者身份，会放大用户指出的误解。应在四行统一标注或 caption 中显著一次说明。
5. 摘要和结论中的 “complete transfer” 应改成机制明确的内部比较名称，保证读者不误解为 29.078 是官方 D-FINE / 官方 FDR 的公开指标。
6. 不要仅以“架构简化”为包装宣布新的独立算法，也不要以“只是删减”否认真实设计；按参考选择、目标坐标、监督开关、已测结果四个可核实层次描述即可。

## 8. 一手文献与核对范围

- [ICLR 2025 官方论文登记](https://proceedings.iclr.cc/paper_files/paper/2025/hash/6cf58a87e3097e7d1f9be3e8693a93de-Abstract-Conference.html)：确认作者、FDR / GO-LSD 构成，以及其已经研究向多种 DETR 的迁移。此次官方 conference PDF 在线获取未成功，不能宣称已按该版全文页码核对。
- [D-FINE 作者 arXiv v1](https://arxiv.org/abs/2410.13842v1)：本地 `tmp-work/detr_presentation_review_20260916/dfine.pdf` 首页面标明 v1，SHA256 `284f73d46f92f9de3b4dcd06aa1c68bae7cb5dd2dd4b4a551d9d99177802e716`。本次读 §4.1，pp.4–5，Fig.2 与 Eqs.(2)–(5)：initial reference、残差 logits、非均匀权重、IoU 加权相邻-bin FGL；§4.2，p.6，Fig.3 与 Eq.(6)：GO-LSD/DDF。这里的节页号明确属于 v1，未冒充最终会议版页码。
- [官方固定提交 decoder](https://github.com/Peterande/D-FINE/blob/7fe2f8889f0b7b817f20c315b40fc15a4fb64ae6/src/zoo/dfine/dfine_decoder.py#L421)：固定初始 preliminary reference 与更新 attention reference 的关键来源。
- [官方固定提交 criterion](https://github.com/Peterande/D-FINE/blob/7fe2f8889f0b7b817f20c315b40fc15a4fb64ae6/src/zoo/dfine/dfine_criterion.py#L139)：FGL、IoU 权重、DDF、匹配 union 及 DN/preliminary 监督。
- [官方固定提交 utils](https://github.com/Peterande/D-FINE/blob/7fe2f8889f0b7b817f20c315b40fc15a4fb64ae6/src/zoo/dfine/dfine_utils.py)：非均匀权重和距离 / 框变换。

在线 raw 文件精确 SHA256：decoder `56cb60dcdca9076d922dbb38b78e2c86ae6a42f8c773feed2911c62e6c7ec677`；criterion `9cd2fb3f6e6884712751efad4316ff2dbfb719d3399dd2d549d1d822676e4272`；utils `a363e9b785235b85f0da45f5423c0f870d73416d2f668c8140f2adec041d9670`。本地 `third_party/dfine_7fe2f888/AUTHORITY.json` 所列对应哈希采用 Windows CRLF 字节；将本次官方 raw 的 LF 转为 CRLF 后三者全部吻合，差异来自换行编码而非源码内容。

本次核查确定的是：**哪些机制来自文献、作者实际改变了什么、已有记录可以支持怎样的文字**。没有把发表本身当作审稿要求，也没有把本地源码差异当作全领域新颖性证明。

# ICASSP 2027 写作提纲

## 论文主线

建议主线为“边界不确定性—早期层弱监督—高分辨率表征不足”三个相互关联的问题，而不是“AP-FDR、BPDD、FIA 三个模块”的并列清单。本文首先面向 stock RT-DETR-L 提出 AP-FDR，以 localization-only 路径、stock-head-informed preliminary geometry、normal/DN 匹配一致监督和隔离初始化建立细粒度定位；其边界分布基础构件受 D-FINE 启发并明确归因。继而针对 AP-FDR 产生的逐层分布提出 BPDD，并以 FIA 补充 P3 高分辨率表征。

## 写作规则

全文采用“问题—设计—证据”顺序：先说明现有 RT-DETR 在密集 UAV 小目标上的具体不足，再写本文为解决该不足改变了什么结构、监督关系或特征流，最后紧跟对应的严格结果、消融状态或复杂度证据。正式 ICASSP 论文仅作为这种组织方式的内部写法样本；与本研究没有直接技术关系的样本不进入 Related Work、外部比较表或参考文献，也不能被用来替代本文自身的创新论证。

## 贡献组织

1. **边界不确定性 → AP-FDR → 严格定位增益**：stock RT-DETR-L 的连续框路径不显式表达逐边不确定性。AP-FDR 在保留分类、查询选择、Decoder 主体、stock matching 与后处理合同的同时，构建 stock-head-informed preliminary 分支、normal/DN 匹配一致的逐边分布监督和隔离初始化机制。基础分布构件受 D-FINE 启发并归于参考工作；完整 AP-FDR 的严格 val mAP/AP75 增益支撑整体方法，内部组件只在单因素实验完成后分别归因。
2. **早期层监督不足 → BPDD → 严格配对增益**：BPDD 是由本文独立提出并实现的原创算法。它不用固定最终层无条件监督所有目标边，而是通过未来层 softmin 混合教师、better-only 逐边门控和 stock assignment 复用渐进改善定位监督。严格配对 val/test 与 AP75 结果支撑其训练期收益，统一复杂度结果支撑其不增加推理分支。
3. **P3 表征不足 → FIA → 正向兼容性与有限开销**：FIA 以 P3-only 方式增强高分辨率特征，同时让 P4/P5 从原分支重建。fresh FIA-only、完整三模块的 val/test 正向结果和统一复杂度表共同说明有效性与代价；既有 cascading FDR+FIA 作为不同拓扑的补充记录单独报告。

第三点的方法细节已绑定当前 `src/fia.py`：双 depth-wise 残差细化、联合通道/空间注意力、零初始化残差缩放和构造期 RNG 隔离。fresh FIA-only 与三模块均登记为 P3-only；既有 FDR+FIA checkpoint 仍是 cascading，三者的拓扑身份和证据来源须分开书写。

## 章节结构

### 1. Introduction

第一段交代无人机图像中小目标、遮挡和边界像素敏感性；第二段收窄到 RT-DETR 的三个缺口：连续框难以表达逐边不确定性、早期 Decoder 层缺少可靠的目标边监督、640 输入下 P3 细节易受限；第三段分别给出 AP-FDR、BPDD、FIA 的解决动作；末段只列贡献和已登记证据。Introduction 不展开 D-FINE 组件清单，也不把任何无关 ICASSP 写法样本当作相关工作。

### 2. Related Work

只覆盖与本文技术链直接相关的 transformer detector、分布式框回归、跨层蒸馏和 UAV 小目标特征增强。用一句话明确 AP-FDR 的边界分布基础构件“受 D-FINE 启发”，随后把差异收束到架构保持、stock-head preliminary geometry、匹配一致和 normal/DN 统一监督。将 GO-LSD 作为 BPDD 的最接近相关工作，先承认它启发跨层定位问题，再用教师来源、可靠性门控、匹配合同、查询范围和损失形式说明 BPDD 的独立算法构造。把 ICASSP 2026 ResBiDet/VARDet 作为最近的同会、同任务工作：ResBiDet 用低分辨率粗分支引导高分辨率精分支，VARDet 用 visual autoregressive multi-scale prediction 与 CLIP-guided semantics；本文聚焦 AP-FDR 定位分布、训练期 BPDD 和 640 输入下的 FIA 表征增强。IJCAI 2025 RAFDE 作为 640 输入的近邻强方法，代表区域自适应融合与边界增强下采样路线。相关工作只比较问题与设计路径，不把不同协议的绝对数值写成公平优劣，也不收录仅用于学习行文方式的无关论文。

### 3. Method

- 3.1 Overall Architecture：先用三个问题标注 RT-DETR-L baseline、FDR decoder、训练期 BPDD 与 P3-only FIA 的职责和依赖方向，避免画成任意插件堆叠。
- 3.2 Architecture-Preserving Fine-grained Distribution Refinement：先说明“连续框路径不足但完整 detector 替换不可控”，再写架构保持、匹配一致监督、preliminary 分支以及分布表示与解码；基础构件来源放在结构设计之后，用一段完成归因。
- 3.3 Boundary Progressive Distribution Distillation：先说明固定末层教师对每个目标边未必可靠，再给出“由本文独立提出并实现”的 future-layer softmin 教师、better-only 激活条件和损失；正文或补充材料加入 BPDD–GO-LSD 六维差异表。
- 3.4 FIA：先说明只增强 P3 的必要性，再描述双基础块、联合通道/空间注意力、恒等安全残差缩放及 P3-only 插入位置，明确 P4/P5 绕过 FIA 重建。
- 3.5 Training Objective and Inference：总损失、BPDD 仅训练期、FDR/FIA 推理期角色。

### 4. Experiments

- 4.1 Dataset and Protocol：VisDrone、RT-DETR-L、scratch、640、seed 0、100 epochs 与统一评估器。
- 4.2 Main Results：正式 exact 核心表放 baseline、FDR 和 FDR+BPDD；三模块 P3-only 的正向 val/test 作为补充观察。
- 论文 A–E 主消融表的 E 行逐项绑定四位小数 val 文本：`P=0.5693、R=0.4991、AP50=0.4898、AP75=0.3042、mAP=0.2961、+0.384 pp`；checkpoint 的 `0.29618` 作为交叉印证，不跨证据拼接 P/R。
- 4.2 同时加入 [VisDrone CCF A/B 会外部方法对比](../results/EXTERNAL_VISDRONE_COMPARISON_ZH.md)：正式表只采用 AAAI、CVPR、ICCV、IJCAI、ICASSP、ICRA、ICME、IROS full/regular paper；逐行标明 A/B，按同 split 的 mAP50–95 分成不高于本文和高于本文，split/input/mAP 未报告行放补充表，不计算跨论文涨点。正文优先用 TPH-UGS、UAV-DETR-EV2 和 RT-DETR-R50 作为接近但不高于本文的 640 对照；DM-EFS、UAV-DETR-R18、RAFDE 作为近邻上界；ResBiDet/VARDet 保留同会和强协议边界。
- 4.3 Ablation Studies：分开报告 fresh P3-only FIA-only 与既有 cascading FDR+FIA 的 exact val/test。FIA-only val mAP50–95=`0.2270563951`，相对 canonical val baseline `0.21911` 为 `+0.7946 pp`；test mAP50–95=`0.1855174641`，相对 protocol-comparable canonical test baseline `0.1774164317` 为 `+0.8101 pp`。两项都是 split 内算术差，不能跨 val/test 拼接。FDR+FIA 保留既有 val/test 算术差 `+0.5280/+0.6644 pp`。
- 4.3 的 AP-FDR 内部表只保留 Full、`w/o preliminary reference` 和 `w/o DN FDR supervision` 三行。后两行已在源码提交 `ebb349ae` 中冻结为单因素配置，按同一 seed0/100-epoch 协议顺序训练；机器证据登记前不填写结果数字。
- 4.4 Analysis：呈现 FDR/BPDD 的可审计分析，以及 FIA 各 checkpoint 的总体与 AP75；只有已有逐类证据的记录才展示 10 类结果，所有指标直接取自已登记记录，不反推。
- 4.5 Efficiency：加入已完成的 [统一复杂度与实时性表](../results/COMPLEXITY_ZH.md)。同一 RTX 4090、batch=1 FP32 端到端实测表明，BPDD 的严格配对推理 Params/FLOPs/峰值显存完全相同且延迟差仅为测量波动；FIA 增加 0.301 M 参数、3.419 GFLOPs 和 0.861 ms 中位延迟，三模块保持 25.21 FPS。

投稿前不补第三数据集、不强行三种子；唯一新增的 [FDR 与 FDR+BPDD 严格配对](../experiments/BPDD_STRICT_PAIR_PROTOCOL_ZH.md) 已完成训练及 best.pt 统一 val/test 复评：mAP50–95 配对增益为 `+0.239/+0.283 pp`，AP75 为 `+0.072/+0.276 pp`。统一复杂度/延迟也已完成，训练和效率实验均已收口。

### 5. Conclusion

总结三部分的职责，但最终效果结论必须以完整新版 FIA 证据为准。

## 当前允许主张

- strict 证据下，FDR 相对 RT-DETR-L 的 mAP50–95 为 +0.07055，AP75 为 +0.07951。
- AP-FDR 是本文第一项方法创新；允许主张其架构保持型定位改造、stock-head-informed preliminary 分支、normal/DN 匹配一致监督和公平初始化合同。基础离散分布、FGL 与 Integral 需注明参考来源。
- BPDD 是由本文独立提出并实现的原创算法；它依赖 FDR 边界分布、只在训练期工作且无参数，不增加推理图。GO-LSD 是问题启发和最近相关工作，不是 BPDD 的公式或代码来源。
- fresh P3-only FIA-only best.pt 的 independent exact val 为 P=`0.4871962209`、R=`0.4253173434`、F1=`0.4509443663`、AP50=`0.3987451873`、AP75=`0.2218076018`、mAP50–95=`0.2270563951`，相对 canonical val baseline `0.21911` 为 `+0.7946 pp`。independent exact test 为 P=`0.4482592210`、R=`0.3776360333`、F1=`0.3954178960`、AP50=`0.3366417705`、AP75=`0.1820114030`、mAP50–95=`0.1855174641`，相对 canonical test baseline `0.1774164317` 为 `+0.8101 pp`；不得把两个 split 互作参照。
- 既有 FDR+FIA cascading best.pt 的 val/test mAP50–95 为 `0.294940/0.234645`，相对 FDR 的同 split 算术差为 `+0.5280/+0.6644 pp`；该记录不得标成 P3-only。
- 正确 P3-only 三模块四位小数 val 为 P=0.5693、R=0.4991、F1=0.5285、AP50=0.4898、AP75=0.3042、mAP50–95=0.2961；相对当前 BPDD val 为 +0.384 pp 的算术观察。checkpoint best-val `0.29618` 与其一致。
- 三模块 test 为 P=0.5189、R=0.4361、F1=0.4634、AP50=0.4081、AP75=0.2327、mAP50–95=0.2337，相对 BPDD test 为 +0.204 pp；因此三模块 val/test 均为正增长。
- CCF A/B 会正式论文的同 split 结果可用于说明竞争位置；640-val 的 `0.2961` 高于 A 会 TPH-YOLOv5-x+UGS `0.2900`、B 会 UAV-DETR-EV2 `0.2870` 和 RT-DETR-R50 `0.2840`，并接近 A 会 DM-EFS `0.2971`、B 会 UAV-DETR-R18 `0.2980` 与 A 会 RAFDE `0.3000`。参数量不是筛选条件；split/input 未明确的行只放补充区，不做 mAP 或速度排名。
- ICASSP 2026 ResBiDet 正式摘要报告 VisDrone2019 AP50=`0.387`，本文为 `0.4898`；只能作同会 AP50 描述性对照，因为其可访问摘要未给 split、精确输入和 mAP50–95。
- ICASSP 2026 VARDet 在 ResNet-50、1333×800、统一重实现协议下报告 VisDrone val `AP50=0.617、AP75=0.391、mAP=0.365`；这用于定位最近竞品，不与本文 640 结果计算公平涨点。

## 当前禁止主张

- 把既有 FDR+FIA cascading best.pt 称为 P3-only，或把任一非严格配对算术差写成严格因果增益。
- 把旧 FIA-only cascading checkpoint 的负向数值继续当作当前结果；fresh FIA-only P3-only val 已取代该记录。
- 新三模块 best-val 观察是严格配对因果增益、完整评估或最终论文主表结果。
- “本文首次发明离散边界分布、FGL、Integral、非均匀积分或相邻 bin 监督”；允许表述为“本文提出 AP-FDR，其基础分布算子参考既有工作”。
- “BPDD 是文献史上第一个跨层定位蒸馏”或“BPDD 与 GO-LSD 完全无关”；应写成问题启发相关、具体 formulation 与实现独立。
- “BPDD 可脱离 FDR 单独使用”或“BPDD 具有推理期零总开销”。
- 混用 val/test、不同 checkpoint、不同 evaluator 或不同源码 authority。
- 把顶会、期刊、仅预印本、仅聚合页或 split 未报告结果写进正式 val/test 主对比，或对测速协议不完整的 FPS 排名。

写作数值统一从 [论文结果汇总](../results/RESULTS_ZH.md)提取，FIA 证据状态以 [FIA 结果状态](../results/FIA_RESULTS_STATUS_ZH.md) 为准，外部方法来源与协议边界以 [外部 VisDrone 对比](../results/EXTERNAL_VISDRONE_COMPARISON_ZH.md) 为准，核心贡献文案与审稿风险按 [创新定位与对抗性审计](NOVELTY_POSITIONING_AND_ADVERSARIAL_AUDIT_ZH.md) 执行。

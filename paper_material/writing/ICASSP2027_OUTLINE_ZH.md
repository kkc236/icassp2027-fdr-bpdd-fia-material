# ICASSP 2027 写作提纲

## 论文主线

建议主线为“细粒度分布细化基础—训练期渐进蒸馏—高分辨率特征增强”。FDR 是从固定版本 D-FINE 适配而来的结构基础，不是本文发明；BPDD 和 FIA 在 RT-DETR-L/VisDrone 系统中分别处理优化监督与高分辨率表征。

## 贡献组织

1. **分布定位基础而非原创冒领**：将来自 D-FINE 的 FDR 边界分布表示和相关监督稳定适配到 Ultralytics RT-DETR-L/VisDrone；不把 FDR、FGL 或 Integral 写成本文从零发明。
2. **主要方法创新**：提出依赖 FDR 逐边分布的训练期 BPDD，通过未来层加权教师和 better-only 门控渐进改善定位监督，且不增加推理分支。
3. **高分辨率增强**：集成 FIA，并用 fresh FIA-only P3-only 的 val 正增益以及 FDR+FIA、完整三模块的补充结果说明其有效性与组合兼容性；不同拓扑和证据等级分别报告。

第三点的方法细节已绑定当前 `src/fia.py`：双 depth-wise 残差细化、联合通道/空间注意力、零初始化残差缩放和构造期 RNG 隔离。fresh FIA-only 与三模块均登记为 P3-only；既有 FDR+FIA checkpoint 仍是 cascading，三者的拓扑身份和证据来源须分开书写。

## 章节结构

### 1. Introduction

围绕无人机场景小目标、遮挡和定位不确定性展开问题，说明定位分布、训练监督和高分辨率表征三个层面的互补性。

### 2. Related Work

覆盖 transformer detector、分布式框回归、蒸馏和小目标特征增强；明确 FDR/FGL/Integral 的来源。把 ICASSP 2026 VARDet 作为最近的同会、同任务工作：其 visual autoregressive multi-scale prediction 与 CLIP-guided semantics 面向跨尺度及语义混淆，而本文聚焦 FDR 定位分布、训练期 BPDD 和 640 输入下的 FIA 表征增强。相关工作只比较问题与设计路径，不把不同协议的绝对数值写成公平优劣。

### 3. Method

- 3.1 Overall Architecture：RT-DETR-L baseline、FDR decoder、训练期 BPDD 与修改后 FIA 的关系。
- 3.2 Fine-grained Distribution Refinement：分布表示与解码。
- 3.3 Boundary Progressive Distribution Distillation：教师构造、激活条件和损失。
- 3.4 FIA：描述双基础块、联合通道/空间注意力、恒等安全残差缩放及 P3 插入位置。
- 3.5 Training Objective and Inference：总损失、BPDD 仅训练期、FDR/FIA 推理期角色。

### 4. Experiments

- 4.1 Dataset and Protocol：VisDrone、RT-DETR-L、scratch、640、seed 0、100 epochs 与统一评估器。
- 4.2 Main Results：正式 exact 核心表放 baseline、FDR 和 FDR+BPDD；三模块 P3-only 的正向 val/test 作为补充观察。
- 论文 A–E 主消融表的 E 行逐项绑定四位小数 val 文本：`P=0.5693、R=0.4991、AP50=0.4898、AP75=0.3042、mAP=0.2961、+0.384 pp`；checkpoint 的 `0.29618` 作为交叉印证，不跨证据拼接 P/R。
- 4.2 同时加入 [VisDrone CCF A/B 会外部方法对比](../results/EXTERNAL_VISDRONE_COMPARISON_ZH.md)：正式表只采用 AAAI、CVPR、ICCV、ICASSP、ICRA、ICME、IROS full/regular paper；逐行标明 A/B，按同 split 的 mAP50–95 分成不高于本文和高于本文，split/input 未报告行放补充表，不计算跨论文涨点。VARDet（ICASSP 2026）单独标为直接竞品，并注明其 ResNet-50、1333×800、统一重实现协议与本文 640 协议不同。
- 4.3 Ablation Studies：分开报告 fresh P3-only FIA-only 与既有 cascading FDR+FIA 的 exact val/test。FIA-only val mAP50–95=`0.2270563951`，相对 canonical val baseline `0.21911` 为 `+0.7946 pp`；test mAP50–95=`0.1855174641`，相对 protocol-comparable canonical test baseline `0.1774164317` 为 `+0.8101 pp`。两项都是 split 内算术差，不能跨 val/test 拼接。FDR+FIA 保留既有 val/test 算术差 `+0.5280/+0.6644 pp`。
- 4.4 Analysis：呈现 FDR/BPDD 的可审计分析，以及 FIA 各 checkpoint 的总体与 AP75；只有已有逐类证据的记录才展示 10 类结果，所有指标直接取自已登记记录，不反推。
- 4.5 Efficiency：加入 [统一复杂度与实时性表](../results/COMPLEXITY_ZH.md)。BPDD 训练期工作、不增加推理分支；四行 Params/FLOPs/FPS/Latency 只能在同一硬件和统一 batch=1 FP32 协议实测后填入。

投稿前不补第三数据集、不强行三种子；唯一新增的 [FDR 与 FDR+BPDD 严格配对](../experiments/BPDD_STRICT_PAIR_PROTOCOL_ZH.md) 已完成训练及 best.pt 统一 val/test 复评：mAP50–95 配对增益为 `+0.239/+0.283 pp`，AP75 为 `+0.072/+0.276 pp`。训练实验已收口，剩余实验材料仅为统一复杂度/延迟表。

### 5. Conclusion

总结三部分的职责，但最终效果结论必须以完整新版 FIA 证据为准。

## 当前允许主张

- strict 证据下，FDR 相对 RT-DETR-L 的 mAP50–95 为 +0.07055，AP75 为 +0.07951。
- BPDD 是依赖 FDR 边界分布的训练期、无参数蒸馏，不增加推理图或参数。
- fresh P3-only FIA-only best.pt 的 independent exact val 为 P=`0.4871962209`、R=`0.4253173434`、F1=`0.4509443663`、AP50=`0.3987451873`、AP75=`0.2218076018`、mAP50–95=`0.2270563951`，相对 canonical val baseline `0.21911` 为 `+0.7946 pp`。independent exact test 为 P=`0.4482592210`、R=`0.3776360333`、F1=`0.3954178960`、AP50=`0.3366417705`、AP75=`0.1820114030`、mAP50–95=`0.1855174641`，相对 canonical test baseline `0.1774164317` 为 `+0.8101 pp`；不得把两个 split 互作参照。
- 既有 FDR+FIA cascading best.pt 的 val/test mAP50–95 为 `0.294940/0.234645`，相对 FDR 的同 split 算术差为 `+0.5280/+0.6644 pp`；该记录不得标成 P3-only。
- 正确 P3-only 三模块四位小数 val 为 P=0.5693、R=0.4991、F1=0.5285、AP50=0.4898、AP75=0.3042、mAP50–95=0.2961；相对当前 BPDD val 为 +0.384 pp 的算术观察。checkpoint best-val `0.29618` 与其一致。
- 三模块 test 为 P=0.5189、R=0.4361、F1=0.4634、AP50=0.4081、AP75=0.2327、mAP50–95=0.2337，相对 BPDD test 为 +0.204 pp；因此三模块 val/test 均为正增长。
- CCF A/B 会正式论文的同 split 结果可用于说明竞争位置；640-val 的 `0.2961` 高于 A 会 TPH-YOLOv5-x+UGS `0.2900`，并接近 A 会 DM-EFS `0.2971` 与 B 会 UAV-DETR-R18 `0.2980`。参数量不是筛选条件；AAAI 2025 的 4090 训练表因 split/input 未明确只放补充区，不做精度或速度排名。
- ICASSP 2026 VARDet 在 ResNet-50、1333×800、统一重实现协议下报告 VisDrone val `AP50=0.617、AP75=0.391、mAP=0.365`；这用于定位最近竞品，不与本文 640 结果计算公平涨点。

## 当前禁止主张

- 把既有 FDR+FIA cascading best.pt 称为 P3-only，或把任一非严格配对算术差写成严格因果增益。
- 把旧 FIA-only cascading checkpoint 的负向数值继续当作当前结果；fresh FIA-only P3-only val 已取代该记录。
- 新三模块 best-val 观察是严格配对因果增益、完整评估或最终论文主表结果。
- “本文发明 FDR、FGL、Integral、非均匀积分或相邻 bin 监督”。
- “BPDD 可脱离 FDR 单独使用”或“BPDD 具有推理期零总开销”。
- 混用 val/test、不同 checkpoint、不同 evaluator 或不同源码 authority。
- 把顶会、期刊、仅预印本、仅聚合页或 split 未报告结果写进正式 val/test 主对比，或对测速协议不完整的 FPS 排名。

写作数值统一从 [论文结果汇总](../results/RESULTS_ZH.md)提取，FIA 证据状态以 [FIA 结果状态](../results/FIA_RESULTS_STATUS_ZH.md) 为准，外部方法来源与协议边界以 [外部 VisDrone 对比](../results/EXTERNAL_VISDRONE_COMPARISON_ZH.md) 为准。

# 当前方法：LRS-GFDR + Capacity-BPDD-v3-Safe + FIA

更新：2026-09-15，对抗性审计修订。本文是当前方法入口；同目录 FDR_ZH/BPDD_ZH/FIA_ZH 中的早期设计与历史结果不可整段移用于当前 Full。

## 身份与依据

- G = LRS-GFDR；B = Capacity-BPDD-v3-Safe；F = P3-only FIA；Full = G+B+F。
- 当前 VisDrone Full 训练源码 commit：`a43056af2a843ec9bae109d3420367c13f3bcef6`。
- [运行配置](../evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/rtdetr-l-lrs-gfdr-capacity-v3-safe-bpdd-fia.yaml)、[训练 authority](../evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/joint-authority.json)、[权重与写作交接](../PAPER_WRITING_HANDOFF_20260915_ZH.md) 共同限定本页对象。YAML 的 nc=80 是模板，运行时数据集 nc=10。
- 根目录旧 train.py 不是当前 Capacity Full 入口。部署代码、训练时代码、导出模型和评估脚本分别记录，不能只凭同名配置认定是同一模型。

## G：可靠的逐边分布定位

Clean-FDR 使用四条边各 33 个 bin 的定位分布，在 6 层 decoder 中累计细化；`reg_max=32`、`reg_scale=4.0`、`up=0.5`、300 queries。几何可行域处理约束解码框的有效性，与 baseline 的推理锚点宽高校准不是同一个机制。

当前开关：`preliminary_box=false`、`distribution_feedback=false`、`feasible_geometry=true`；额外 FDR 损失 `fgl_weight=0.15`，`supervise_pre_boxes=false`、`supervise_dn_fdr=false`、`edge_adaptive_fgl=false`。关闭额外 FDR 的 DN 监督不等于关闭 RT-DETR 自身 DN。

LRS-FGL 以停止梯度的匹配 IoU 为可靠性权重，对同图、同层符合条件的权重向均值收缩；基础收缩系数 0.25，逐层减弱，末层保持原权重。它改变监督权重，不增加推理预测分支。

创新表述应围绕本文在 RT-DETR 内采用的定位路径、可行域处理与可靠性监督的组合及具体修改；离散边界、Integral、基础 FGL 等与 D-FINE 的关系须正常引用并逐项界定。本页不认证文献绝对首创。

## B：局部专家与质量门控定位蒸馏

当前 B 是一个整体模块，包含三部分，而不是旧 BPDD 的简单改名：

1. **局部视觉专家**：读取原始 P2/P3/P4，在预测框邻域采样局部特征，用注意力产生类别与边界分布残差；保留 base decoder 路径。
2. **专家监督**：专家最终预测复用固定匹配，独立接受真实标签监督。它不是仅靠 KD 训练的分支。
3. **专家到基础层的定位 KD**：教师停止梯度；检查 query/GT 身份、可表示边界支持域、逐边 NLL 改善及解码 IoU 门控，再进行定位分布蒸馏。

当前 v3-Safe 的 `loc_weight=0.15`、`cls_weight=0.0`、`loc_margin=0.02`、`loc_tau=0.10`；completed-epoch 调度 warmup 10–20、decay 80–100。关闭分类 KD 不等于关闭类别头或专家分类监督。

**推理时使用专家细化后的框和类别输出。** 因此整个 B 增加参数及推理计算；只有 KD 损失仅在训练期计算。不能引用旧 BPDD 的“无参数、无推理分支、零额外 FLOPs”作为当前 B 的结论。

“BPDD-only”表示 G+B、无 FIA，不是没有 G 的 stock RT-DETR 加一个独立 BPDD 检测器。旧 future-layer softmin 教师属于旧 BPDD，不是当前局部专家教师。

## F：P3-only 特征增强

FIA 用卷积、通道/空间注意力与零初始化可学习残差系数增强 P3。归档图中层 22 从原 P3（21）读取；构造 P4 的层 23 也读取 21，所以 P4/P5 不级联 FIA 输出。

普通 decoder 保持 P3/P4/P5 路径；额外 P2 供局部专家使用，不将整个 decoder 写成四尺度。当前 decoder 来源索引为 `[1,22,25,28]`。FIA-P3 也会进入局部专家，不能声称 B/F 没有交互。

## 论文主张与现有证据

| 主张 | 当前可用证据 | 不应扩大为 |
|---|---|---|
| 联合配置改善原生 val | Full 30.109%，G 29.620%；差 +0.489 pp | 每个组件在任何组合、每个 split 都独立涨点 |
| 当前外部共同评估 | D-FINE-L/Full 的 final 与 best 均有完成结果；final 主终点、best 次终点 | 等训练预算算法归因、官方 VisDrone 排名 |
| B 是容量＋监督＋KD 的整体设计 | 固定源码、训练记录和组合结果 | 已隔离证明 KD 本身贡献了全部差值 |
| v3-Safe 改善已运行的联合配置 | v2 Full 29.736%，v3 Full 30.109% | 已证明冲突唯一来自分类 KD，或每个改动各自有效 |
| 当前 test 表现 | 原生 640 Full 相对 G 基本持平；800 小幅高于 G | 明显、普遍的联合泛化增益 |

如果要单独验证 KD 的训练贡献，需要同专家、同 FIA、同专家监督而仅关闭 KD 的训练对照；测试时关闭 KD 没有区分力。本次没有启动此类训练。历史正式结果若找到，先核验再复用。

## 历史材料边界

[早期 FDR](FDR_ZH.md)、[旧 BPDD](BPDD_ZH.md)、[FIA 历史变体](FIA_ZH.md)、[旧复杂度](../results/COMPLEXITY_ZH.md) 保留追溯用途。原始 CSV、评估 JSON 和 checkpoint 身份不得重命名成当前版本以消除差异。最新表格与缺项见[写作交接](../PAPER_WRITING_HANDOFF_20260915_ZH.md)及[逐项修复状态](../reviews/AUDIT_REMEDIATION_20260915_ZH.md)。

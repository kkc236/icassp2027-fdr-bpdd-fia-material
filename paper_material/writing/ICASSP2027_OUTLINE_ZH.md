# ICASSP 2027 写作提纲

## 论文定位

基线为 Ultralytics RT-DETR-L，目标任务为 VisDrone 小目标与密集目标检测。核心问题分成三层：连续四维框回归缺少显式边界分布；早期解码层未充分利用后续层的更优分布；高分辨率 P3 特征仍需受控的局部与注意力增强。

建议将论文主线写为“分布式定位基础—训练期渐进蒸馏—高分辨率特征增强”。FDR 是从固定版本 D-FINE 适配而来的结构基础，不是本文发明；BPDD 和 FIA 在该 RT-DETR-L/VisDrone 系统中分别处理优化监督与 P3 表征。

## 三项贡献

1. 将 D-FINE 的四边分布表示、累计细化、Integral 与 FGL 结构化适配到 Ultralytics RT-DETR-L，保留分类、匹配及主要解码器合同，并提供可隔离配置与训练证据。
2. 构建 BPDD：从未来解码层按目标误差 softmin 形成停止梯度教师，仅在教师优于当前层时蒸馏；该监督训练期有效、无参数，最小宿主为 FDR。
3. 构建 FIA：只增强 P3 的两个局部深度卷积细化块和通道/空间注意力，通过零初始化残差缩放保持训练起点恒等，并在推理期保留。

## 章节结构

### 1. Introduction

- 说明 VisDrone 小目标密集、边界定位敏感的任务特征。
- 指出 RT-DETR-L 连续框回归、早期层监督和 P3 表征三个具体缺口。
- 用三项贡献收束，不在引言中写未验证的实时性、显著性或多种子结论。

### 2. Related Work

- 实时端到端检测与 RT-DETR。
- 分布式框回归与 D-FINE；明确 FDR/FGL/Integral 的先验来源。
- 深层监督、自蒸馏与未来层教师。
- 局部卷积、通道注意力和空间注意力。

### 3. Method

- 3.1 Overall Architecture：RT-DETR-L baseline、P3 FIA、FDR decoder 与训练期 BPDD 的关系。
- 3.2 Structured FDR Adaptation：preliminary box、四边 33-bin 表示、六层累计 logits、Integral、FGL 与 stock 损失隔离。
- 3.3 Best-Progressive Distribution Distillation：未来层 softmin 教师、相邻 bin 目标误差、better-only 可靠性与 KL 项。
- 3.4 P3 Feature Interaction and Attention：两级局部细化、通道/空间门、`Y=X+alpha(F(X)-X)` 与私有初始化。
- 3.5 Training Objective and Inference：总损失、BPDD 仅训练期、FDR/FIA 推理期保留。

### 4. Experiments

- 4.1 Dataset and Protocol：VisDrone 6,471/548、10 类、RT-DETR-L、scratch、640、seed 0、100 epochs 与统一评估器。
- 4.2 Main Results：先呈现四行绝对值，再只对 strict 行报告配对差值；明确另外两种证据等级。
- 4.3 Ablation Studies：已配置的 FDR 单因素独立训练；未来补充 FIA 单独、FDR+FIA。BPDD 单独不成立。
- 4.4 Analysis：BPDD 活跃边比例、教师改善等训练统计，以及 FIA 参数量；仅在补齐原始证据后讨论速度、显存或分尺度结果。

### 5. Conclusion

总结三部分在同一 RT-DETR-L 框架中的职责与现有证据。把跨 authority 和截图结果写成阶段性验证，并将严格 BPDD/FIA 配对消融列为后续工作。

## 允许主张

- strict 证据下，FDR 相对 RT-DETR-L 的 mAP50–95 为 `+0.07055`，AP75 为 `+0.07951`。
- BPDD 是依赖 FDR 边界分布的训练期、无参数蒸馏，不增加推理图或参数。
- FIA 只插入 P3，保持张量形状，`alpha` 零初始化，C=256 时约 301,476 个参数，推理期有效。
- BPDD 与完整模型可报告现有绝对值，但必须同时显示各自证据等级。

## 禁止主张

- “本文发明 FDR、FGL、Integral、非均匀积分或相邻 bin 监督”。
- “BPDD 可脱离 FDR 单独使用”或“BPDD 具有推理期零总开销”。
- “FIA 零参数、零计算、推理期移除”或“FIA 单独增益已证实”。
- 把 `cross_authority_exact` 写成严格配对增益，把 `screenshot_rounded` 写成精确值，或补造完整模型 AP75。
- 混用 val/test、不同 checkpoint、不同 evaluator 或不同源码 authority；宣称多种子均值、显著性、GFLOPs、FPS、延迟、显存及分尺度收益而没有对应证据。

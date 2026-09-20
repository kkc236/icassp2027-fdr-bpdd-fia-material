# 表达、图1与 CVM 相关工作审查

审查日期：2026-09-17。

## 范围与结论

- 完整阅读上一版正文、表格构建和五幅图，并查看其全部 11 页渲染图。
- 复核本版摘要、引言、相关工作和结论的英文表达。
- 本代理仅修改 `figures/overview.tikz`，并生成 `qa/overview_review/` 独立预览；没有改正文、原始证据或模型结果。
- 本版已将 LRS-GFDR 与完整 FDR/FGL 移植参照的比较前移，把数值正确性、组件结果、完整系统结果分开论证。该顺序让主创新与其直接证据更接近。
- 不以录用论文中未经充分控制的结果作为我方性能结论依据，也不据此估算录用概率。

## 两篇 CVM 2026 原始论文

### LME-DETR

**题名：** LME-DETR: Lightweight and Multi-Scale Feature-Enhanced End-to-End Object Detection for Aerial Images。

**作者顺序：** Feifei Xu, Yu Xie, Dongyang Li, Luobin Huang, Zhihao Guo。

**来源：** [CVM 2026 官方全文，14 页](https://iccvm.org/2026/files/papers/265.pdf)；[官方议程，P38](https://iccvm.org/2026/program.htm)。

论文围绕感受野、跨尺度特征交互和样本权重安排方法章节。其第 3.3 节 EMA-SVFL 使用正样本 IoU 的跨训练步运行中心，对分类目标作分段调权。其组织值得借鉴之处是将模块职责对应到具体问题，再给出总体架构和实验。

**与本稿的明确区别：** LRS-GFDR 的主要对象是边界分布的解码和 FGL 回归监督。LRS 在同图、同解码层的合格匹配组内保持权重总量，系数随解码深度改变，最后一层恢复原权重；它不维护跨训练步的 EMA 中心。本版相关工作已体现这一差异。不能把一般性的 IoU 调权动机都表述为我方首次提出。

**使用边界：** 作为定性相关工作引用；不把其主表 AP/FPS 自动视为与本稿同训练、同输入处理或同测速协议的结果。

### SD-Net

**题名：** SD-Net: Synergistic and Dynamic Learning for Small Object Detection in Aerial Images。

**作者顺序：** Jiaxin Yang, Wenbo Liu, Tao Deng, Fei Yan。

**来源：** [CVM 2026 官方全文，14 页](https://iccvm.org/2026/files/papers/691.pdf)；[官方议程，P37](https://iccvm.org/2026/program.htm)。

官方 PDF 摘要和方法介绍明确其宿主为 YOLOv11：SC2f 用于骨干的内容自适应计算，S2B 用于颈部的跨尺度调制，HCB 用于高分辨率特征细化；其数据集为 VisDrone 和 TinyPerson。

**值得借鉴：** 用稀疏视觉信息这一共同问题串联特征提取、尺度融合和细化，使多个组件有共同目标。本稿对应的统一问题是边界分布的几何可行性与监督分配，再以经过几何检查的局部专家扩展主线。

**与本稿的区别：** SD-Net 主要改变视觉特征处理，本稿主创新位于边界分布的解码与监督。不得把定性差异扩展为未经实验验证的性能优势。

## 图1改动

1. 为 G 设置独立蓝色主框，框内显式并列解码几何与 LRS-FGL；不再让主创新与一般特征节点具有相同视觉权重。
2. 保留 F 对两个预测路径的 P3 共享关系，以及原 P3 构造 P4 的说明。
3. B 显式接收基础框、query 和 logits，并接收 P2/P3/P4 局部证据；其预测连接到最终输出。
4. 将原图脚注中的专家监督关系画为回路：专家分布经配对、边质量和混合框 IoU 检查，再向所有六个基础层提供 KL 监督。此回路用虚线和训练期图例区分。
5. 使用短标签、统一色彩、较宽的主框和图例。没有加入虚构图像、实测热图或新性能数据。

**验证：** 独立使用 pdfLaTeX、Times 字体和原 TikZ 样式编译，查看 `qa/overview_review/overview.png`，无标签重叠和裁切；日志无 overfull 或超高浮动体。独立预览缺少整篇引用，因此交叉引用显示为占位；主稿负责完整解析。图保持 ASCII、原 `figure*` 标签和约 16.7 cm 宽度，兼容单文件主稿。

## 正文末轮英文建议

以下均为 copyediting 建议，未直接改 `source/body.tex`；保留全部数字和比较范围。

### 1. 摘要首句：明确问题发生的集成范围，减少并列从句

**原文：** Distributional localization represents fine-grained boundary positions, but signed edge predictions still admit nonpositive box extents, while direct quality weighting can leave poorly localized matches with little supervision.

**建议：** Distributional localization models fine-grained boundary positions. In an RT-DETR integration, however, signed edge offsets can produce nonpositive box extents, while direct IoU weighting can leave low-overlap matches weakly supervised.

### 2. 摘要专家句：替换不自然的 checked on

**原文：** A box-conditioned expert extends this core using shared visual features and selective localization transfer checked on the actual partial boundary correction.

**建议：** A box-conditioned expert extends this core using shared visual features. Its localization targets are accepted only when the proposed partial edge correction improves overlap with the matched object.

### 3. 引言首段：displacement 不宜搭配 occupy

**原文：** In datasets such as VisDrone, a slight boundary displacement can occupy a substantial fraction of an object's width or height.

**建议：** In datasets such as VisDrone, even a small boundary error can be large relative to an object's width or height.

保留原句中的 VisDrone 引文。

### 4. 结论对比句：明确 final 的含义，避免重复 under

**原文：** Under the common evaluator, final AP exceeds our scratch-adapted D-FINE-L reproduction by 1.579 points under their respective training recipes.

**建议：** Using the common evaluator, the final checkpoint exceeds our scratch-adapted D-FINE-L reproduction by 1.579 AP points; the models use different training recipes.

### 5. 结论总括句：用 quantify 代替带揭露语气的 expose

**原文：** These results characterize accurate UAV-image detection with high-throughput batch processing and expose the cost of adding local visual evidence.

**建议：** These results support accurate UAV-image detection with high-throughput batch processing and quantify the additional cost of local visual refinement.

## 保留的证据边界

不通过文风处理消除实质限制：一个数据集、一个种子；部分历史配置并非严格单变量；完整专家扩展增加推理成本；共同 evaluator 不等于共同训练配方；几何和权重守恒性质本身不证明 AP、梯度方差或收敛收益。本稿可以清楚集中披露这些限制，同时避免每段重复解释。

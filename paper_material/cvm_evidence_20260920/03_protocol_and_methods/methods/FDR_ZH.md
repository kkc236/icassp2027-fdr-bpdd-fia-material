# AP-FDR：面向 RT-DETR-L 的架构保持型细粒度分布细化

> **历史设计说明（2026-09-15 修订）**：本页保留 AP-FDR 早期设计，包含当前 Full 已关闭的 preliminary/额外 DN 等分支；不是当前运行开关的权威说明。当前 G/B/F 的实现与证据边界统一见 [CURRENT_JOINT_METHOD_ZH.md](CURRENT_JOINT_METHOD_ZH.md)。旧 A–E 数值不可改名为当前联合。

本文将所提出的 Architecture-Preserving Fine-grained Distribution Refinement 记为 **AP-FDR**；为与既有配置、checkpoint 和结果表保持一致，后文仍沿用简称 **FDR**。AP-FDR 解决的不是“如何把一个现成检测器嵌入 RT-DETR”，而是如何在保持 stock RT-DETR-L 检测合同的条件下，为密集小目标建立可训练、可比较的逐边分布定位路径。

## 技术问题

VisDrone 中的小目标边界只占少量像素，遮挡与尺度变化又会放大四条边的定位不确定性。stock RT-DETR-L 由每层框头直接输出四个连续框量，虽然结构简洁，却没有显式表示每条边的多粒度概率分布。另一方面，直接采用 D-FINE 的完整 detector 会同时改变分类质量建模、Decoder 宽度、查询处理和训练组件，难以判断增益究竟来自分布定位还是来自整套架构变化。

因此，本文把研究问题限定为：能否只重构 RT-DETR-L 的 localization branch，同时保留分类、查询选择、Decoder 主体、匹配和后处理合同，并让新增分布监督在 normal 与 denoising 查询上复用同一 assignment？AP-FDR 正是针对这一受控问题设计，而不是对既有完整 detector 的整体替换。

## 本文原创设计

围绕上述问题，AP-FDR 面向 Ultralytics RT-DETR-L 提出四项相互约束、共同定义方法身份的设计：

1. **架构保持型定位路径**：为隔离分布定位本身的作用，只改造 localization branch，保留 stock 分类头、查询选择、六层 Decoder attention/FFN、Hungarian matching 与后处理合同；同时不引入 LQE、DDF、GO-LSD 或 Decoder widening。
2. **stock-head-informed preliminary geometry**：为避免随机粗框分支破坏原有回归起点，从 stock 第一层框头复制 preliminary head，以既有回归几何初始化六层共享参考框。
3. **normal/DN 匹配一致监督**：为避免分布监督和连续框监督学习不同的 query–GT 关系，FGL、preliminary-box L1/GIoU 与连续框损失沿用 stock criterion 已产生的逐层 assignment，不增加第二套 matcher，并把同一合同显式扩展到 normal 与 denoising 两条路径。
4. **隔离初始化与公平比较合同**：为使新增头不改变对照模型的公共随机轨迹，分布头使用私有 RNG，避免改变公共参数初始化、数据顺序和后续训练随机状态。

这四项结构与监督设计是本文对 AP-FDR 的原创主张，也是内部单因素消融需要验证的对象。

## 基础构件来源

受 D-FINE 启发，AP-FDR 基于固定 commit `7fe2f8889f0b7b817f20c315b40fc15a4fb64ae6` 已公开的边界分布基础构件。生产实现沿用 `weighting_function`、`Integral`、`translate_gt`、`bbox2distance`、`distance2bbox` 与 `unimodal_distribution_focal_loss` 的数学行为，并固定相应的 33-bin 表示和 FGL 设置。逐边离散表示、非均匀投影、Integral、相邻 bin FGL 与累计分布细化不作为本文原创点；D-FINE 的完整 detector、LQE、DDF、GO-LSD 和 Decoder widening 没有进入 AP-FDR。该段只界定基础机制的来源；本文方法主张仍由上一节四项 RT-DETR 专用结构与监督设计定义。

## 问题与模块位置

VisDrone 中小目标密集、边界像素占比高，解码器直接输出四个连续框量时难以显式表达每条边的不确定性。AP-FDR 将细粒度分布建模限制在 Ultralytics RT-DETR-L 的框回归路径内；Backbone、Hybrid Encoder、300 个查询、六层解码器的注意力与 FFN、分类头、Hungarian 匹配及后处理合同保持原有实现。该 localization-only 设计避免把分类质量估计、额外蒸馏或 Decoder 扩宽混入 FDR 的主效应，使定位改造可以被独立验证。

输入是三尺度编码特征和查询状态，输出仍为归一化 `cxcywh` 框及类别分数。每个解码层不再直接输出 4 个框量，而是输出左、上、右、下四条边各 33 个 bin 的 logits，即每查询 132 维。正式配置固定 `reg_max=32`、`reg_scale=4.0`、`up=0.5`、六个解码层和 300 个查询。

## 定位表示与 preliminary box

第一解码层先通过从 stock 框头私有复制的 preliminary head 生成初始框：

\[
b^{pre}=\sigma\!\left(h_{pre}(q_1)+\sigma^{-1}(b^0)\right).
\]

启用 `preliminary_box=true` 时，`b^{pre}` 经停止梯度后成为六层分布解码共享的参考框；它同时复用既有匹配结果接受 L1 与 GIoU 定位监督，不触发额外匹配。与完全独立初始化一个粗框分支不同，AP-FDR 从 stock 第一层框头复制 preliminary head，并使用私有随机源初始化新增分布头，从而保留公共参数初始化与训练随机序列的可比性。该设计把“参考位置”与“相对四边分布”分开，使后续层围绕同一初始框逐步细化。

## 累积分布细化与 FGL

第 \(l\) 层产生四边分布增量 \(\Delta z_l\)。正式模型按层累加 logits：

\[
z_l=\sum_{j=1}^{l}\Delta z_j,\qquad
d_l=\operatorname{Integral}(z_l),\qquad
b_l=\operatorname{Decode}(b^{pre},d_l).
\]

`Integral` 对每条边的 33-bin softmax 使用固定的非均匀投影值求期望，再由 `distance2bbox` 相对 `b^{pre}` 解码。层间框参考和查询残差在训练时按实现停止梯度，避免改变 stock 解码器层的梯度合同。`cumulative=false` 配置仅用于独立训练消融，不能用完整模型权重临时关闭开关来替代消融实验。

FGL 将连续目标边距离映射到相邻两个 bin，以线性权重组合两项交叉熵，并用停止梯度的匹配框 IoU 加权：

\[
\mathcal L_{FGL}=w_{IoU}\left(w_L\,CE(z,k)+w_R\,CE(z,k+1)\right).
\]

正式配置的 FGL 权重为 0.15。对 normal queries，最后一层形成主 FGL 项，前五层求和形成辅助项；preliminary box 另接收 L1 与 GIoU。若存在 `dn_meta`，实现会把缓存的四边 logits 和 preliminary box 按查询维拆成 normal/DN 两部分，并对 DN queries 追加主/辅助 FGL 以及 preliminary-box L1/GIoU。两侧都复用 stock criterion 已产生的逐层匹配，不引入第二套 matcher。由此，连续框监督、逐边分布监督和粗框监督共享相同的 query–GT 关系，构成 AP-FDR 的 assignment-consistent supervision。新增的 FDR 监督可概括为：

\[
\mathcal L_{FDR}=\mathcal L_{FGL}^{normal}+\mathcal L_{pre}^{normal}
+\mathbf 1_{dn}\left(\mathcal L_{FGL}^{dn}+\mathcal L_{pre}^{dn}\right),
\]

并与 stock VFL、L1、GIoU、辅助及去噪损失共同优化。

## 训练与推理

- 训练：保存六层累计四边 logits、共享参考框和 preliminary box；在 stock 损失之后，为 normal queries 增加 FGL 与可选 preliminary-box 定位项，并在 `dn_meta` 存在时对 DN queries 增加对应的 FGL 和 preliminary-box L1/GIoU。
- 推理：分布头、累计细化、Integral 和框解码仍在图中；损失分支不执行，只输出 `eval_idx` 对应的框与类别结果。
- FDR 会增加解码框头参数和推理计算，不能套用 BPDD 的“零推理参数增量”表述。

## 可执行来源

- `src/fdr_head.py`：132 维分布头、preliminary box、六层累计细化和训练证据缓存。
- `src/fdr_loss.py`：normal/DN 两侧的 FGL、preliminary-box L1/GIoU 监督以及 stock 匹配复用。
- `src/rtdetr_fdr.py`：模型、训练损失和推理路径集成。
- `src/fdr_math.py`：参考固定版本 D-FINE 公式实现的非均匀投影、Integral、距离编解码与 FGL 基础算子。
- `configs/rtdetr-l-fdr.yaml`：正式结构与损失参数。
- `configs/rtdetr-l-fdr-no-prebox.yaml`、`configs/rtdetr-l-fdr-no-dn.yaml`、`configs/rtdetr-l-fdr-no-prebox-loss.yaml`、`configs/rtdetr-l-fdr-no-fgl.yaml`、`configs/rtdetr-l-fdr-no-cumulative.yaml`：单因素消融入口。其中 no-DN 配置仅关闭额外 DN FDR 监督，stock DN 损失保持不变。

## 主张边界

允许表述：本文针对 stock RT-DETR-L 连续框路径缺少逐边不确定性表达、完整 detector 替换又会混入多项架构变化的问题，提出 AP-FDR；其 localization-only 结构、stock-head-informed preliminary 分支、normal/DN 匹配一致监督与隔离初始化构成本文原创设计。受 D-FINE 启发的边界分布基础构件按上述来源边界明确归因。

禁止表述：不得声称本文首次发明离散边界分布、FGL、Integral、相邻 bin 软标签或非均匀 weighting；不得把可加载消融 YAML 当作已完成的消融结果；不得把 `+7.055 pp` 拆分归因给尚未独立训练验证的任一内部开关；不得在没有实测时宣称零开销、特定延迟或特定参数增幅。

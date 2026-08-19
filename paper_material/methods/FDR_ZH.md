# AP-FDR：面向 RT-DETR-L 的架构保持型细粒度分布细化

本文将所提出的 Architecture-Preserving Fine-grained Distribution Refinement 记为 **AP-FDR**；为与既有配置、checkpoint 和结果表保持一致，后文仍沿用简称 **FDR**。AP-FDR 参考 D-FINE 的逐边离散分布思想与基础解码算子，但其贡献对象是面向 Ultralytics RT-DETR-L 的架构保持、匹配一致和 normal/DN 双路径监督设计，而不是对完整 D-FINE 网络的复现。

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

`Integral` 对每条边的 33-bin softmax 使用参考 D-FINE 固定公式实现的非均匀投影值求期望，再由 `distance2bbox` 相对 `b^{pre}` 解码。层间框参考和查询残差在训练时按实现停止梯度，避免改变 stock 解码器层的梯度合同。`cumulative=false` 配置仅用于独立训练消融，不能用完整模型权重临时关闭开关来替代消融实验。

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

## AP-FDR 的独立设计

相对于直接把一套完整分布检测器替换进 RT-DETR，AP-FDR包含四项相互约束的设计：

1. **架构保持型定位改造**：只改造 box path，保留分类、查询选择、Decoder 主体、匹配与后处理合同；
2. **定位分支解耦**：不引入 LQE、DDF、GO-LSD 或 Decoder widening，使 FDR 的因果边界保持清晰；
3. **匹配一致监督**：FGL 和 preliminary-box 损失复用 stock criterion 已产生的 normal/DN 匹配，不重复分配；
4. **公平初始化合同**：preliminary head 继承 stock 框头，新增分布头使用私有 RNG，避免污染公共参数和数据顺序随机状态。

这四点共同定义本文的 AP-FDR。33-bin 表示、非均匀 Integral、相邻 bin 软标签与 FGL 基础形式只作为被参考的数学构件，不单独计作本文原创。

## 与参考方案的差异边界

| 维度 | D-FINE 完整检测框架 | 本文 AP-FDR |
|---|---|---|
| 改造范围 | 围绕分布定位构建完整 detector，并结合 GO-LSD 等组件 | 仅改造 stock RT-DETR-L localization branch |
| 分类与 Decoder | 包含自身的分类质量与 Decoder 设计 | 保留 stock 分类头、查询选择、六层 Decoder attention/FFN |
| preliminary 分支 | 独立定义 preliminary box head | 从 stock 第一层框头复制，保留原始几何初始化 |
| 匹配关系 | 使用其原生 criterion 与输出组织 | FGL、pre-box 与连续框监督复用 stock 逐层 assignment |
| normal/DN 合同 | 在其原生训练框架内处理 | 显式映射到 Ultralytics normal/DN 两条损失路径 |
| 蒸馏边界 | 完整方法包含 GO-LSD/DDF 相关监督 | AP-FDR 本身不含蒸馏；本文另行提出 BPDD |
| 可比性控制 | 原框架训练合同 | 新增 head 私有 RNG，不改变公共初始化与数据随机序列 |

正文不需要展开这张表的全部工程细节，但应至少写清前三项方法差异；完整表适合放补充材料或 rebuttal。

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
- `configs/rtdetr-l-fdr-no-prebox.yaml`、`configs/rtdetr-l-fdr-no-prebox-loss.yaml`、`configs/rtdetr-l-fdr-no-fgl.yaml`、`configs/rtdetr-l-fdr-no-cumulative.yaml`：单因素消融入口。

## 主张边界

允许表述：本文提出 AP-FDR，一种面向 RT-DETR-L 的架构保持型细粒度分布细化方法。它参考已有逐边分布和 FGL 基础公式，原创重点在 localization-only 结构、stock-head-informed preliminary 分支、normal/DN 匹配一致监督以及公平初始化合同。

禁止表述：不得声称本文首次发明离散边界分布、FGL、Integral、相邻 bin 软标签或非均匀 weighting；不得把可加载消融 YAML 当作已完成的消融结果；不得把 `+7.055 pp` 拆分归因给尚未独立训练验证的任一内部开关；不得在没有实测时宣称零开销、特定延迟或特定参数增幅。

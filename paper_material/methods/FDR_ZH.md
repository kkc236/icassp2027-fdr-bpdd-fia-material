# FDR：RT-DETR-L 的细粒度分布细化适配

## 问题与模块位置

VisDrone 中小目标密集、边界像素占比高，解码器直接输出四个连续框量时难以显式表达每条边的不确定性。FDR 仅替换 Ultralytics RT-DETR-L 解码器的框回归路径；Backbone、Hybrid Encoder、300 个查询、六层解码器的注意力与 FFN、分类头、Hungarian 匹配及后处理合同保持原有实现。

输入是三尺度编码特征和查询状态，输出仍为归一化 `cxcywh` 框及类别分数。每个解码层不再直接输出 4 个框量，而是输出左、上、右、下四条边各 33 个 bin 的 logits，即每查询 132 维。正式配置固定 `reg_max=32`、`reg_scale=4.0`、`up=0.5`、六个解码层和 300 个查询。

## 定位表示与 preliminary box

第一解码层先通过从 stock 框头私有复制的 preliminary head 生成初始框：

\[
b^{pre}=\sigma\!\left(h_{pre}(q_1)+\sigma^{-1}(b^0)\right).
\]

启用 `preliminary_box=true` 时，`b^{pre}` 经停止梯度后成为六层分布解码共享的参考框；它同时复用既有匹配结果接受 L1 与 GIoU 定位监督，不触发额外匹配。该设计把“参考位置”与“相对四边分布”分开，使后续层围绕同一初始框逐步细化。

## 累积分布细化与 FGL

第 \(l\) 层产生四边分布增量 \(\Delta z_l\)。正式模型按层累加 logits：

\[
z_l=\sum_{j=1}^{l}\Delta z_j,\qquad
d_l=\operatorname{Integral}(z_l),\qquad
b_l=\operatorname{Decode}(b^{pre},d_l).
\]

`Integral` 对每条边的 33-bin softmax 使用 D-FINE 的非均匀投影值求期望，再由 `distance2bbox` 相对 `b^{pre}` 解码。层间框参考和查询残差在训练时按实现停止梯度，避免改变 stock 解码器层的梯度合同。`cumulative=false` 配置仅用于独立训练消融，不能用完整模型权重临时关闭开关来替代消融实验。

FGL 将连续目标边距离映射到相邻两个 bin，以线性权重组合两项交叉熵，并用停止梯度的匹配框 IoU 加权：

\[
\mathcal L_{FGL}=w_{IoU}\left(w_L\,CE(z,k)+w_R\,CE(z,k+1)\right).
\]

正式配置的 FGL 权重为 0.15。对 normal queries，最后一层形成主 FGL 项，前五层求和形成辅助项；preliminary box 另接收 L1 与 GIoU。若存在 `dn_meta`，实现会把缓存的四边 logits 和 preliminary box 按查询维拆成 normal/DN 两部分，并对 DN queries 追加主/辅助 FGL 以及 preliminary-box L1/GIoU。两侧都复用 stock criterion 已产生的匹配，不引入新匹配器。新增的 FDR 监督可概括为：

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
- `src/fdr_math.py`：固定版本的 D-FINE 非均匀投影、Integral、距离编解码与 FGL 基础算子。
- `configs/rtdetr-l-fdr.yaml`：正式结构与损失参数。
- `configs/rtdetr-l-fdr-no-prebox.yaml`、`configs/rtdetr-l-fdr-no-prebox-loss.yaml`、`configs/rtdetr-l-fdr-no-fgl.yaml`、`configs/rtdetr-l-fdr-no-cumulative.yaml`：单因素消融入口。

## 主张边界

允许表述：本工作把固定版本 D-FINE 的细粒度边界分布表示、Integral 与 FGL 结构化适配到 Ultralytics RT-DETR-L，在 VisDrone 上完成定位路径替换、损失隔离、声明式配置和统一验证。

禁止表述：不得声称本工作发明 FDR、FGL、Integral、相邻 bin 软标签或非均匀 weighting；不得把可加载消融 YAML 当作已完成的消融结果；不得在没有实测时宣称零开销、特定延迟或特定参数增幅。

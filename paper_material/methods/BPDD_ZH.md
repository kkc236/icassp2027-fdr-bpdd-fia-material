# BPDD：训练期渐进式分布蒸馏

## 问题与最小宿主

FDR 的早期解码层已有四边概率分布，但定位质量通常弱于后续层。BPDD 利用同一次前向中未来解码层的分布，为较早层构造按目标质量加权的教师，不增加独立教师网络。

BPDD 的输入是 FDR 的累计四边 logits、preliminary box、真实框和 stock 最终层匹配。它要求至少两个解码层的边界分布；本项目宿主为六层 FDR。因此最小有效宿主是 FDR，“BPDD 单独”既没有所需分布，也不是合法消融行。

## 未来层 softmin 教师

对匹配查询的每条边，将第 \(l\) 层分布记为 \(p_l\)，相邻 bin 目标下的插值负对数似然记为 \(e_l\)。早期层只使用其未来层 \(k>l\)：

\[
\omega_{l,k}=\frac{\exp(-e_k/\tau)}{\sum_{j>l}\exp(-e_j/\tau)},\qquad
T_l=\sum_{k>l}\omega_{l,k}p_k.
\]

概率、误差、softmin 权重和教师分布均停止梯度。正式配置温度 \(\tau=0.5\)，因此目标误差较低的未来层获得更大权重，同时不强制只选最后一层。

## better-only 门控与损失

教师只有在比当前层至少好一个 margin 时才产生监督。实现中的可靠性为：

\[
r_l=\operatorname{clip}\left(
\frac{e_l-e(T_l)-m}{\max(e_l,\varepsilon)},0,1
\right),
\]

其中正式配置 `margin=0.02`、`eps=1e-6`。最终损失在所有可用早期层、匹配查询和四条边上平均：

\[
\mathcal L_{BPDD}=\frac{\lambda}{N}
\sum_{l,q,s}r_{lqs}\,D_{KL}(T_{lqs}\Vert p_{lqs}),
\qquad \lambda=0.5.
\]

若没有匹配查询、功能关闭或权重为零，损失严格为零。正式版本只使用 normal queries 的最终 stock assignment，排除 denoising queries。

## 训练与推理

- 训练期：先执行完整 stock+FDR criterion，再读取已记录的最终匹配并追加 `loss_bpdd`。
- 参数：BPDD 仅由张量运算与冻结超参数组成，没有可训练参数。
- 推理期：模型把 `bpdd_runtime_enabled` 关闭，预测路径不调用 BPDD；其模块不进入推理图，不增加推理参数或前向算子。
- BPDD 与 FDR 模型 state contract 相同；“不增加推理图/参数”不等于“训练零开销”。

## 可执行来源

- `src/bpdd_loss.py`：相邻 bin 目标评分、未来层 softmin 教师、better-only 可靠性和 KL 损失。
- `src/rtdetr_fdr_bpdd.py`：训练期 criterion 集成、运行期开关与模型 state 合同。
- `src/fdr_loss.py`：FDR 累积分布、preliminary box 与 stock 匹配快照的上游来源。
- `configs/rtdetr-l-fdr-bpdd.yaml`：`weight=0.5`、`temperature=0.5`、`margin=0.02`、最终匹配及排除去噪查询的正式配置。

## 主张边界

允许表述：本工作提出并实现了一个依赖 FDR 逐层边界分布的训练期、无参数、未来层加权蒸馏策略，并用目标质量改善门控不可靠教师。

论文定位：BPDD 是三部分中主要的方法创新。同一源码、同一 `seed=0`、同一协议的 FDR/FDR+BPDD 配对训练及 best.pt 统一复评已经完成：val/test mAP50–95 分别提高 `+0.239/+0.283 pp`，AP75 分别提高 `+0.072/+0.276 pp`；两个推理图均为 32,334,278 Params / 103.7 GFLOPs。历史跨 authority 的 `+0.557 pp` 只作为背景观察，不替代新配对 AP75。

禁止表述：不得把 BPDD 写成可脱离 FDR 的通用检测头；不得声称它修改推理输出、训练零成本或对所有解码层都必然有效；不得将历史 cross-authority 精确结果表述为严格配对因果增益。

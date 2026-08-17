# ACR-BPDD：面向 FDR 的有效置信重归一化渐进分布蒸馏

## 1. 方案定位

ACR-BPDD 是 BPDD v1 的最小必要性修正版，服务于已经成熟的 FDR 定位分支。它只在训练期增加辅助监督，不新增部署参数，不改变 Backbone、Encoder、Query selection、Decoder layer、分类头、匹配、后处理和 FDR 推理表达。

它要解决的不是“FDR 还不会定位”，而是以下更窄的问题：

1. BPDD v1 中只有约 52.17% 的候选边产生有效教师信号，但损失仍按全部候选边平均，导致有效梯度被稀释；
2. BPDD v1 的定位蒸馏梯度同时进入共享 Decoder，可能扰动已经成熟的 Query/分类表征。这与已有结果中 Precision 上升、Recall 下降相符。

历史证据为：FDR+BPDD v1 相对 FDR 的 Test mAP、AP50、AP75 分别提高约 0.366、0.535、0.375 pp，但 Recall 下降约 0.554 pp。因此当前应保留“渐进分布蒸馏有效”这一信号，只修复监督密度和梯度作用域，不应重新设计 FDR 或简单增大 BPDD 权重。

## 2. 核心方法

### 2.1 有效置信重归一化

BPDD 对早期第 `l` 层和边 `e` 计算教师可靠性 `r(l,e)` 及分布 KL 项。原 BPDD 按全部可选边数 `N` 归一化：

`L_v1 = lambda * sum(r_i * KL_i) / N`

ACR-BPDD 改为：

`L_ACR = lambda * sum(r_i * KL_i) / max(sum(stopgrad(r_i)), rho * N)`

固定参数：

- `lambda = 0.5`，不提高原 BPDD 权重；
- `rho = 0.5`；
- 最大归一化增益为 `1/rho = 2`；
- reliability mass 完全 detach，模型不能通过改变分母投机；
- 无匹配或全零可靠性时，损失严格为有限的 0。

这不是无约束地放大损失，而是让稀疏的有效教师信号不再被大量零项稀释，同时用 2 倍上限控制风险。

### 2.2 Detached distribution-head replay

训练时仅在一次真实 Decoder 前向期间注册临时 pre-hook，记录六个 FDR 分布回归头的真实输入并立即 detach。真实前向结束后立刻移除 hook，再使用同一组分布 MLP 对 detached 输入做一次轻量重放，按 FDR 原机制累计六层角点 logits。

重放分布必须满足：

`max_abs(replayed_logits - original_logits) <= 1e-6`

由此得到两个性质：

- BPDD 仍可更新六个 `dec_bbox_head` 分布头；
- BPDD 对 Backbone、Encoder、共享 Decoder、分类头、Query selection、pre-box 头的梯度路径不存在。

相比“再反传一次共享网络后减去梯度”，该实现只增加六个小 MLP 的前向与 BPDD 自身反向，速度、显存和恢复安全性更好。

## 3. 与 FDR/BPDD v1 的关系

| 项目 | FDR | BPDD v1 | ACR-BPDD |
|---|---|---|---|
| FDR 分布头 | 保留 | 保留 | 保留 |
| BPDD future-mixture teacher | 无 | 有 | 有，公式不变 |
| 匹配索引 | 原匹配 | 复用 final stock match | 同 BPDD v1 |
| DN Query | 原训练 | BPDD 不使用 | 同 BPDD v1 |
| BPDD 归一化 | 无 | 全 eligible edge | reliability mass + 0.5N floor |
| BPDD 梯度作用域 | 无 | 分布头 + 共享 Decoder | 仅分布头 |
| 推理结构/参数 | FDR | 与 FDR 相同 | 与 FDR 相同 |

旧 BPDD YAML 保持不变，新候选使用独立文件 `configs/rtdetr-l-fdr-acr-bpdd.yaml`，便于做 FDR、FDR+BPDD、FDR+ACR、FDR+ACR-BPDD 消融。

## 4. 冻结训练协议

继承成熟 FDR 协议：

- Ultralytics RT-DETR-L / Ultralytics 8.4.90；
- VisDrone train 6471、val 548、10 类；
- seed 0、pretrained=False、fresh start；
- 100 epochs、imgsz 640、batch 8、workers 8、device 0；
- MuSGD、lr0 0.01、momentum 0.937、weight decay 0.0005；
- AMP=True、固定 scale 128；
- Query 300、max_det 300、NMS=False；
- 数据增强与已冻结 FDR authority 完全一致；
- 初始状态 SHA256：`51AAB2EB3FB7D123501C69C7B8DC90FF3EA0B9344A108EDEEF2C7D6DCDBB742D`。

本轮为单臂候选验证，使用已有成熟 FDR100 作初步跨 run 参考，证据必须标记：

- `evidence_level = preliminary_cross_run`；
- `strict_paired = false`。

最终论文消融再重跑同批次严格 FDR 对照，不能把本轮写成严格配对结果。

## 5. 已完成的工程检验

- ACR 数学、零匹配、全零可靠性、FP16 和分母 detach 测试；
- ACR 与旧 BPDD v1 向后兼容测试；
- 六层 replay 累计值等价测试；
- BPDD 对共享参数梯度为 `None`、对分布头保留梯度；
- FDR 与 ACR-BPDD state_dict/参数量完全一致；
- eval 推理输出逐元素一致；
- 临时 hook 在每次前向后清空；
- deepcopy、checkpoint pickle、resume authority 和逐 epoch 不可变证据契约；
- 定向 ACR/BPDD/FDR 回归测试 80/80 通过；训练入口扩展回归 104/104 通过。

完整历史仓库测试为 1862 passed、7 skipped、25 failed；25 项均来自当前基线分支缺失旧 IBER/ITBER 资产、旧 authority 哈希漂移或缺失历史 evidence，不涉及 ACR 文件和定向测试。不能将其表述为全仓库全绿。

## 6. 运行和判定建议

部署前仍需在目标 4090 上执行一次真实 `batch=8 + MuSGD + AMP128` CUDA preflight，验证 forward/backward、有限梯度、checkpoint reload、replay 误差和峰值显存。当前会话不占用服务器。

Formal100 结束后优先比较：

1. mAP50-95、AP50、AP75；
2. Precision、Recall、F1，重点检查 BPDD v1 的 Recall 下降是否收敛；
3. tiny/small/medium/large；
4. 10 类 AP/AP50/AP75；
5. 尾 5 轮均值与 best/last 差异；
6. 参数、GFLOPs、FP16 latency 和显存；
7. replay max error、normalization gain、reliability mass、active-edge ratio。

建议第一轮成功标准：相对成熟 FDR 参考，mAP 与 AP75 均正向，Recall 不再明显下降；若要作为比 BPDD v1 更强的论文版本，应至少超过 BPDD v1 的 mAP，并表现出更好的 Recall/Precision 平衡。

## 7. 成功率和失败后处理

基于 BPDD v1 已有正收益，预计：

- ACR-BPDD 高于 FDR：约 65%–75%；
- 高于 BPDD v1：约 50%–60%；
- 相对 FDR 达到 +0.5 pp mAP：约 40%–50%；
- 同时修复 Recall 下降：约 55%–65%。

这些是研究决策概率，不是结果保证。

若失败，按单变量处理：

- loss/梯度过强：把 `reliability_floor` 从 0.5 提高到 0.75，使最大放大从 2 倍降至 1.33 倍；
- Recall 恢复但 mAP 无提升：说明梯度隔离正确但监督覆盖不足，再评估 trajectory-consistent extra points；
- AP75 上升但 AP50/Recall 下降：保留 head replay，降低归一化增益，不直接提高 BPDD weight；
- replay 不等价或恢复失败：判定为工程失败，不进入训练，不调整科学阈值。

禁止的首轮操作包括：直接增大 BPDD weight、粗暴 tiny/small 加权、引入 FIA/GLGM、修改 Query/匹配、打开 DN-BPDD 或同时加入多个新变量。


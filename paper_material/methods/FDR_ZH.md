# LRS-FDR：原生对齐与分层可靠性收缩的细粒度分布细化

> **当前方法身份（2026-08-28）**：论文第一项定位创新固定为 **LRS-FDR**。
> **NA-FDR** 是其原生对齐基础和 `w/o LRS` 内部消融。历史运行标识
> `Clean FDR` 对应 NA-FDR，历史运行标识 `Clean FDR + LRS-FGL` / `lrs_fdr`
> 对应 LRS-FDR；原始日志、checkpoint 和配置名称不回写。

## 1. 研究问题与统一设计

RT-DETR 的连续四维框回归难以显式表达密集小目标四条边的不确定性。已有 FDR
通过逐边离散分布、non-uniform Integral、FGL 和跨层累计细化提供了更细的定位
表示，但历史实现中的 learned preliminary reference 和扰动 DN query 上的额外
FDR 监督未得到内部实验支持；同时，基础 FGL 直接用匹配框 IoU 加权，使浅层中
低 IoU 但仍有学习价值的正常匹配获得较弱的分布监督。

LRS-FDR 用一个统一模块解决这两个问题：

1. **NA-FDR 原生对齐基础**重新组织分布锚点和监督范围；
2. **LRS-FGL 可靠性收缩**在 NA-FDR 内部重新分配浅层正常匹配的 FGL 权重。

完整数据流为：

```text
RT-DETR decoder query + native reference
  -> 4 × 33-bin boundary logits
  -> cumulative distribution refinement
  -> non-uniform Integral and box decoding
  -> stock normal-query Hungarian assignment (training)
  -> representability firewall (mask) + layerwise reliability shrinkage (shallow layers only)
  -> weighted matched-query FGL (training)
```

LRS-FDR 不增加第二套 matcher、query、分类分支、蒸馏教师或推理后处理。

## 2. NA-FDR：Native-Aligned FDR

NA-FDR 不是“清理版”命名，而是 LRS-FDR 的原生对齐基础设计。它联合固定两个
对齐合同。

### 2.1 原生 reference 对齐

NA-FDR 关闭 learned preliminary-box reference，直接使用 RT-DETR decoder 的
原生 reference 组织逐层分布回归。第 (l) 层预测四边 33-bin 分布增量
\(\Delta z_l\)，并保留累计细化：

\[
z_l=\sum_{j=0}^{l}\Delta z_j,
\qquad
d_l=\operatorname{Integral}(z_l),
\qquad
b_l=\operatorname{Decode}(r_0,d_l),
\]

其中 \(r_0\) 是固定的初始原生 decoder reference，所有层累计分布共用该
解码锚点；attention 使用的 reference 仍逐层更新，不能与分布解码锚点混同。
`preliminary_box=false` 同时移除
preliminary-box L1/GIoU，不让额外粗框分支改变几何起点。

### 2.2 原生 assignment 与有效查询对齐

NA-FDR 的 FGL 直接复用 stock criterion 已产生的逐层 Hungarian assignment，
不调用第二套 matcher。额外细粒度分布监督只作用于 normal matched queries；
`supervise_dn_fdr=false` 只取消扰动 DN queries 上额外的 FDR/FGL，stock RT-DETR
的 DN 分类、L1 和 GIoU 仍完整存在。

对正常匹配查询，连续目标边距离映射到相邻两个 bin。基础 FGL 为：

\[
\mathcal L_{FGL}=q\left(w_L\,CE(z,k)+w_R\,CE(z,k+1)\right),
\]

其中 \(q=\operatorname{sg}(IoU(b,g))\)。NA-FDR 保留 `fgl_weight=0.15`、
33-bin 表示、non-uniform Integral 和累计分布细化，并关闭 EAW，避免在 LRS 内部
消融中混入第二种权重机制。

## 3. LRS-FGL：分层可靠性收缩

### 3.1 动机

浅层正常匹配的 IoU 较低时，基础 FGL 权重也较低；极端情况下 \(q=0\) 会使该
查询得不到 FDR-specific 分布梯度，尽管 stock L1/GIoU 仍存在。直接提高所有低
IoU 权重会改变总损失尺度并可能放大不可表示的边界目标，因此 LRS-FGL 只在固定
可表示集合内做均值保持的权重收缩。

### 3.2 可表示性防火墙

对图像 (b)、decoder 层 (l) 的 normal matched-query 集合 (M_{b,l})，定义
(R_{b,l}\) 为四条相邻-bin 目标索引都严格位于 FDR 支持内部的子集。任何一条边
落在支持边界的匹配、DN query 和 unmatched query 都不参与收缩。

### 3.3 均值保持变换

对 (k\in R_{b,l})：

\[
q_{b,l,k}=\operatorname{sg}(IoU(b_{b,l,k},g_{b,l,k})),
\]

\[
\bar q^R_{b,l}=\frac{1}{|R_{b,l}|}\sum_{k\in R_{b,l}}q_{b,l,k},
\]

\[
\widetilde q_{b,l,k}=(1-\alpha_l)q_{b,l,k}+\alpha_l\bar q^R_{b,l},
\qquad
\alpha_l=\alpha_0\left(1-\frac{l}{L-1}\right).
\]

正式配置固定 `alpha0=0.25`。六层日程为：

```text
[0.25, 0.20, 0.15, 0.10, 0.05, 0.00]
```

不满足可表示条件的匹配保持 \(\widetilde q=q\)。最后一层
\(\alpha_{L-1}=0\)，因此主 FGL 目标与 NA-FDR 完全相同；LRS 只调整前五层辅助
FGL。每个图像、每个层满足：

\[
\sum_{k\in M_{b,l}}\widetilde q_{b,l,k}
=\sum_{k\in M_{b,l}}q_{b,l,k}.
\]

该守恒合同意味着 LRS 重新分配而不整体增加 FGL 权重。完整权重路径停止梯度，
FP32 执行收缩，FP64 只用于计算亚 ULP 守恒残差。

## 4. 冻结配置与消融身份

### 4.1 LRS-FDR 完整配置

```yaml
cumulative: true
preliminary_box: false
distribution_feedback: false

fdr_loss:
  fgl_weight: 0.15
  supervise_pre_boxes: false
  supervise_dn_fdr: false
  edge_adaptive_fgl: false
  reliability_shrinkage_alpha: 0.25
```

### 4.2 唯一直接内部消融

NA-FDR 与完整 LRS-FDR 只差：

```yaml
reliability_shrinkage_alpha: 0.0  # NA-FDR / w/o LRS
reliability_shrinkage_alpha: 0.25 # LRS-FDR / Full
```

`alpha0=0` 使用显式 legacy short path。模型参数、state dict、decoder 输出、
matcher、VFL/L1/GIoU、DN 损失和推理图均不改变，因此 NA-FDR 是 LRS 的直接内部
对照。Original FDR 则用于验证整个 NA-FDR → LRS-FDR 重构相对历史实现的总体
效果。

## 5. 训练、推理与模块兼容

- **训练期**：NA-FDR 产生正常匹配的逐边分布损失；LRS 只改变浅层、可表示、
  normal matched queries 的停止梯度 FGL 标量权重。
- **推理期**：执行四边分布、累计细化、Integral 和框解码；LRS 权重分支不执行。
- **参数与 checkpoint**：LRS 不增加参数或 state-dict key，NA-FDR 与 LRS-FDR
  checkpoint schema 相同。
- **BPDD**：BPDD 仍可读取逐层 FDR 分布；LRS 不改变 BPDD 输入张量或蒸馏公式。
- **FIA**：FIA 位于 P3 特征路径，接口上与 LRS-FDR 的 decoder 输入兼容。

兼容性只说明接口和计算图合同；现有 AP-FDR+BPDD/FIA checkpoint 不能重命名为
LRS-FDR 组合结果，最终组合仍需按 LRS-FDR 配置重新训练或明确标成历史证据。

## 6. 已登记证据

本节数值绑定历史 Formal100 源码，不是 2026-09-06 v2 数值修复的重新训练结果。
当前 v2 的四臂与本地验证见[无服务器部署证据](../evidence/no_server_correctness_v2_20260906/README_ZH.md)。

统一冻结评估结果见 [LRS-FDR 结果页](../results/LRS_FDR_RESULTS_ZH.md) 和
[证据包](../evidence/lrs_fdr_formal100_20260828/README.md)。关键结果为：

| 方法 | Precision | Recall | AP50 | AP75 | mAP50-95 |
|---|---:|---:|---:|---:|---:|
| Original FDR | 0.570249 | 0.491417 | 0.484700 | 0.294070 | 0.290698 |
| NA-FDR | **0.587045** | 0.498339 | **0.493119** | 0.301061 | 0.296855 |
| LRS-FDR | 0.579512 | **0.500606** | 0.491805 | **0.305773** | **0.296968** |

- NA-FDR 相对 Original FDR：mAP `+0.616 pp`、AP75 `+0.699 pp`；
- LRS-FDR 相对 NA-FDR：mAP `+0.011 pp`、AP75 `+0.471 pp`、Recall
  `+0.227 pp`；
- LRS-FDR 相对 Original FDR：mAP `+0.627 pp`、AP75 `+1.170 pp`、Recall
  `+0.919 pp`。

## 7. 原创性与主张边界

### 允许主张

1. NA-FDR 将 FDR 的几何锚点和分布监督范围统一对齐到 stock RT-DETR 的原生
   reference、assignment 和正常匹配查询；
2. LRS-FGL 在固定可表示集合内进行同图像、同层、总权重守恒的可靠性收缩，并
   沿 decoder 深度退火到完全不变的最终层；
3. LRS-FDR 是上述设计组成的统一定位模块，且相对 Original FDR 在总体
   Precision、Recall、AP50、AP75 和 mAP 上均为正。

### 必须限定

- LRS 相对 NA-FDR 的 mAP 只有 `+0.011 pp`，只能描述为数值非负；
- LRS 相对 NA-FDR 的 Tiny/Small mAP 分别下降 `0.851/0.181 pp`，不得声称全尺度
  或 Tiny 全面增强；
- epoch 91--100 平均 mAP 低于 NA-FDR，不能声称终末平台更稳；
- 当前证据是 VisDrone、seed 0 的描述性消融，不是统计显著性或跨数据集泛化
  证明。

### 禁止主张

- 本文首次提出离散四边分布、non-uniform Integral、累计 FDR 或基础 FGL；
- NA-FDR 的收益等于 LRS 的收益；
- 删除 preliminary/DN-FDR 本身自动构成创新；创新主张必须落在原生对齐的统一
  设计与对应正向证据上；
- 现有 AP-FDR+BPDD/FIA 结果等同于 LRS-FDR+BPDD/FIA。

## 8. 来源、实现和可复训入口

- 冻结设计：[`2026-08-28-lrs-fdr-material-freeze-design.md`](../../docs/superpowers/specs/2026-08-28-lrs-fdr-material-freeze-design.md)
- 算法设计源：source commit `9fa9078011d92cc23fc1f0eec06ff34983986ff0`
- LRS 配置：`configs/rtdetr-l-lrs-fdr.yaml`（实验源码分支 `codex/lrs-fgl`）
- LRS 损失：`src/fdr_loss.py`（同一 source commit）
- Formal100 启动器：`scripts/train_lrs_fdr.py`（同一 source commit）
- Gate0：`scripts/audit_lrs_fgl_gate0.py`（同一 source commit）
- 训练 authority、参数、日志与冻结评估：
  [`lrs_fdr_formal100_20260828`](../evidence/lrs_fdr_formal100_20260828/README.md)

D-FINE commit `7fe2f8889f0b7b817f20c315b40fc15a4fb64ae6` 是 33-bin 边界表示、
non-uniform Integral、累计细化和基础 FGL 的来源边界；LRS-FDR 不声称重新发明
这些基础构件。

# EQuAL：边缘自适应、查询对齐定位

EQuAL（Edge-adaptive Query-Aligned Localization）是对原 AP-FDR 训练组织的整体重构，不是附加在 FDR 外部的新分支。它保留逐边离散分布、非均匀 Integral、相邻 bin FGL 和累计细化等受 D-FINE 启发的定位基础，但重新规定分布锚点、监督查询范围与四边梯度分配方式。

## 1. 统一设计

EQuAL 的数据流为：

```text
RT-DETR 原生 decoder query/reference
  -> 左/上/右/下四边离散分布
  -> 相邻 bin 目标概率
  -> 框内边缘难度归一化
  -> edge-adaptive FGL
  -> Integral 解码与累计框细化
```

正式配置固定为：

```yaml
reg_max: 32
reg_scale: 4.0
up: 0.5
cumulative: true
preliminary_box: false

fdr_loss:
  fgl_weight: 0.15
  supervise_pre_boxes: false
  supervise_dn_fdr: false
  edge_adaptive_fgl: true
```

三项设置共同定义一个完整定位方法：

1. `preliminary_box: false`：以 RT-DETR 原生 decoder reference 作为唯一分布锚点，不再让 learned preliminary reference 驱动细化，也不施加 preliminary-box L1/GIoU。
2. `supervise_dn_fdr: false`：保留 stock RT-DETR 的 DN 分类、L1 和 GIoU，只取消扰动 DN queries 上额外的 FDR/FGL；细粒度分布监督集中在 clean matched queries。
3. `edge_adaptive_fgl: true`：同一个匹配框的四条边不再共享完全相同的调制强度，而是按各边目标概率反映的学习难度重新分配梯度。

## 2. 边缘自适应监督

对匹配查询的第 `e` 条边，连续目标落在相邻两个 bin 上。令插值后的目标概率为 `p_e`，边缘难度为：

```text
d_e = max(1 - p_e, 1e-6)
m_e = clamp(d_e / mean(d_1, d_2, d_3, d_4), 0.5, 2.0)
w_e = detach(IoU_box) * m_e
```

`p_e`、插值权重、IoU 和调制系数均在权重路径上停止梯度。该设计只在框内重新分配四边的监督强度：目标概率低的困难边获得更高权重，已学好的边降低权重；框内平均调制接近 1，不通过整体放大 localization loss 获益。

## 3. 保持不变的合同

- stock Hungarian matching、分类路径、query selection、decoder blocks 和 post-processing 不变；
- 仍使用 33-bin 四边分布、non-uniform Integral、累计细化和 `fgl_weight=0.15`；
- stock DN 训练仍存在，只取消 DN queries 上额外的分布监督；
- edge-adaptive weighting 不引入可训练参数或新的推理分支。

运行时历史标识为 `ACE-FDR/ace_fdr`，论文名称为 EQuAL；两者通过 alias 记录绑定到同一算法语义，原始 checkpoint、日志和目录不改名。

## 4. 贡献边界

D-FINE 应被引用为离散四边表示、non-uniform Integral 和基础相邻-bin FGL 的来源。本文可主张的是 EQuAL 的统一组织：原生 query/reference 对齐、clean-query 分布监督和框内逐边难度均衡。不得声称本文首次提出离散分布回归、Integral 或基础 FGL。

EQuAL standalone 已通过 val mAP/AP75 和 test 方向门槛；它与 BPDD/FIA 的新组合仍需重训。旧 AP-FDR+BPDD、AP-FDR+FIA 与三模块 checkpoint 不能只改名为 EQuAL 组合结果。

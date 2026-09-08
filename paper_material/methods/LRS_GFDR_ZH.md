# LRS-GFDR：可靠性收缩与可行域几何 FDR

## 正式命名

LRS-GFDR（Layerwise Reliability Shrinkage with Geometrically Feasible FDR）是本项目对“LRS-FDR + 几何校正”组合的统一封装名。它不是新增一次训练，而是把已完成、协议相同的 LRS-FDR 几何校正版作为一个可复现模块发布。

## 处理流程

1. FDR 在四条边上预测离散分布，并用累积残差逐层细化框。
2. LRS 按层对定位监督进行可靠性收缩，抑制早期层的不稳定梯度。
3. 几何可行域解码把四边距离约束为非负并满足合法框关系，避免第二数据集上的越界/退化框。

几何校正属于推理路径的一部分；LRS 属于训练与解码共同使用的 FDR 变体。BPDD、FIA 不包含在本模块中。

## 等价性与证据边界

已有同 seed、同 private seed 的构图检查显示，旧 `LRS-FDR + feasible_geometry` 与新 `LRS-GFDR` 的 state-dict key、参数量和初始化逐项一致。因此不重复训练，不把后续被停止的重复 GFDR 运行当作结果。正式指标引用 `paper_material/evidence/lrs_gfdr_track_20260909/RESULTS.md`。

## 复现入口

- 配置：[`configs/rtdetr-l-lrs-gfdr.yaml`](../../configs/rtdetr-l-lrs-gfdr.yaml)
- 训练/验证代码：以仓库根目录 `src/` 与 `scripts/` 的 FDR/LRS 实现为准
- 几何开关：`feasible_geometry: true`


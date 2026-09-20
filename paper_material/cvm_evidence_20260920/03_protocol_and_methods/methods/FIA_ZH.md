# FIA：高分辨率特征增强模块

> **版本边界（2026-09-15）**：本页包含 FIA 的基础实现和多个历史宿主/拓扑结果。当前 Capacity Full 必须按 [当前方法入口](CURRENT_JOINT_METHOD_ZH.md) 的 P3-only 图解释；旧 cascading、fresh FIA-only 与当前 G+F/Full 的指标不能互换。

## 定位

FIA 位于 RT-DETR-L 的高分辨率特征路径，用于在 decoder 前增强小目标相关表征。它是推理图中的特征模块，不是 BPDD 的辅助损失。

当前实现接收 BCHW 格式的 256 通道 P3 特征，由两个 `FIABaseBlock` 和一个联合通道/空间注意力单元组成。每个基础块使用 `1×1` 投影、`3×3` depth-wise 卷积、GELU 和两条内部残差；注意力分支结合全局平均池化通道门控与通道 mean/max 生成的 `7×7` 空间门控。模块输出为

\[
Y = X + \alpha\bigl(\mathcal{F}(X)-X\bigr),
\]

其中可学习标量 \(\alpha\) 以 0 初始化，使模块插入时严格从恒等映射开始。构造过程使用私有 RNG 隔离，避免 FIA 的参数初始化改变后续 P4/P5 与 decoder 的初始化轨迹。

## 与另外两模块的关系

- FIA-only 检查相对 stock baseline 的独立贡献。
- FDR+FIA 检查 FIA 与细粒度分布定位表示的兼容性。
- FDR+BPDD+FIA 检查完整组合；其中 BPDD 仍只在训练期工作。

## 已登记拓扑

| 身份 | 连接 | 使用范围 |
|---|---|---|
| current P3-only FIA-only | raw graph 的 FIA 层 22 使用 `f=-1`，即读取上一层 21；层 23 显式 `f=21`；decoder 为 `[22,25,28]` | fresh FIA-only `best.pt` exact val/test |
| published cascading FDR+FIA | FIA 位于层 22，层 23 使用 `f=-1`，P4/P5 延续 FIA 输出 | 既有 FDR+FIA `best.pt` 消融 |
| P3-only three-module | FIA 增强 decoder P3，层 23 显式回到原始 P3（`f=21`），decoder 为 `[22,25,28]` | FDR+BPDD+FIA checkpoint 观察 |

层 22 的 `f=-1` 本身不表示 cascading：在 fresh FIA-only raw graph 中它只表示“读取上一层 21”。区分拓扑的关键是层 23：`f=21` 是正确 P3-only，旧 FIA-only/FDR+FIA 的层 23 `f=-1` 才会继续级联 FIA 输出。旧 FIA-only cascading 记录已被 fresh P3-only checkpoint 取代；既有 FDR+FIA 仍保持 cascading 身份。

## 当前证据结论

- fresh P3-only FIA-only exact val 的 P/R/F1/AP50/AP75/mAP50–95 为 `0.4871962209/0.4253173434/0.4509443663/0.3987451873/0.2218076018/0.2270563951`，相对 canonical baseline `0.21911` 为 `+0.7946 pp` 的非严格配对算术增益。
- FDR+FIA exact val mAP50–95 为 `0.2949403207`，相对 FDR `+0.5280 pp`，支持 FIA 与 FDR 的互补兼容性。
- independent exact test 中，fresh FIA-only 的 P/R/F1/AP50/AP75/mAP50–95 为 `0.4482592210/0.3776360333/0.3954178960/0.3366417705/0.1820114030/0.1855174641`，相对 protocol-comparable canonical test baseline `0.1774164317` 为 `+0.8101 pp`。既有 FDR+FIA 的 mAP50–95/AP75 为 `0.2346453866/0.2358787301`，相对登记 FDR 的 test mAP 算术差为 `+0.6644 pp`；所有差值只在各自 split 内成立。
- FDR+BPDD+FIA P3-only 四位小数 val 文本的 mAP50–95 为 `0.2961`，相对 FDR+BPDD 为 `+0.384 pp` 的算术观察；checkpoint best-val `0.29618` 与其一致。
- 三模块四位小数 test 文本的 P/R/F1/AP50/AP75/mAP50–95 为 `0.5189/0.4361/0.4634/0.4081/0.2327/0.2337`，相对 FDR+BPDD test 为 `+0.204 pp`，说明完整组合在 val/test 两个 split 上均呈正增长。

论文可表述为“FIA 面向高分辨率小目标表征，fresh P3-only FIA-only 在 canonical val baseline 上取得 `+0.7946 pp` 的算术增益，并在 FDR+FIA 与完整三模块中呈现兼容性观察”。不得把不同 topology/authority 的算术差写成严格因果收益，也不得继续把旧 FIA-only cascading 的负向值当作当前结果。

证据详情见 [论文结果统一汇总](../results/RESULTS_ZH.md)与 [FIA 结果状态](../results/FIA_RESULTS_STATUS_ZH.md)。

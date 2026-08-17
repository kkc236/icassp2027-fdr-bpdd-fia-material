# FIA：高分辨率特征增强模块

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

## 两种已登记拓扑

| 身份 | 连接 | 使用范围 |
|---|---|---|
| published cascading standalone | FIA 位于层 22，层 23 使用 `f=-1`，P4/P5 延续 FIA 输出 | 现有 FIA-only、FDR+FIA best.pt 消融 |
| P3-only three-module | FIA 增强 decoder P3，层 23 显式回到原始 P3（`f=21`） | FDR+BPDD+FIA checkpoint 观察 |

因此不能把 standalone 的结果标成 P3-only，也不能把两个拓扑拼成严格成对实验。

## 当前证据结论

- FIA-only exact val mAP50–95 为 `0.2167954534`，相对 baseline `−0.2315 pp`，说明 FIA 单独并未稳定涨点。
- FDR+FIA exact val mAP50–95 为 `0.2949403207`，相对 FDR `+0.5280 pp`，支持 FIA 与 FDR 的互补兼容性。
- independent exact test 中，FIA-only / FDR+FIA 的 mAP50–95 为 `0.1771764568` / `0.2346453866`，AP75 为 `0.1716130742` / `0.2358787301`；相对登记 baseline/FDR 的 mAP 算术差分别为 `−0.0240 pp` / `+0.6644 pp`。
- FDR+BPDD+FIA P3-only checkpoint best-val mAP50–95 为 `0.29618`，相对 FDR+BPDD 为 `+0.3922 pp` 的非严格观察。

论文应把 FIA 的贡献表述为“面向高分辨率特征的增强设计，并在 FDR 组合中显示正向兼容性”，不能声称 FIA-only 一定提升，也不能把算术差写成严格因果收益。

证据详情见 [论文结果统一汇总](../results/RESULTS_ZH.md)与 [FIA 结果状态](../results/FIA_RESULTS_STATUS_ZH.md)。

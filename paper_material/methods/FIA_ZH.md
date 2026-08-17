# FIA：高分辨率特征增强模块

## 定位

FIA 位于 RT-DETR-L 的高分辨率特征路径，用于在 decoder 前增强小目标相关表征。它是推理图中的特征模块，不是 BPDD 的辅助损失。

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
- FDR+BPDD+FIA P3-only checkpoint best-val mAP50–95 为 `0.29618`，相对 FDR+BPDD 为 `+0.3922 pp` 的非严格观察。

论文应把 FIA 的贡献表述为“面向高分辨率特征的增强设计，并在 FDR 组合中显示正向兼容性”，不能声称 FIA-only 一定提升，也不能把算术差写成严格因果收益。

证据详情见 [FIA 结果状态](../results/FIA_RESULTS_STATUS_ZH.md)。

# LRS-GFDR+AC-BPDD

LRS-GFDR+AC-BPDD 是 LRS-GFDR 与 AC-BPDD 的联合训练路线。AC-BPDD（Adaptive-Consistency Boundary Progressive Distribution Distillation）只在训练期消费 FDR 的逐层边界分布，通过 future-layer softmin 教师、better-only 可靠性门控和一致匹配约束改善早期层定位监督；推理图不增加 BPDD 分支。

本材料结果来自已经完成的 `LRS-FDR + AC-BPDD` 运行。该运行的几何解码已启用，因此以显式 `feasible_geometry: true` 的配置封装为 **LRS-GFDR+AC-BPDD**。这是方法名与配置显式化，不是声称重新训练了一次。

- 配置：[`configs/rtdetr-l-lrs-gfdr-ac-bpdd.yaml`](../../configs/rtdetr-l-lrs-gfdr-ac-bpdd.yaml)
- AC-BPDD 权重：`0.15`；temperature：`0.5`；margin：`0.02`
- 训练期模块，不增加推理参数
- 结果与证据等级见 [`LRS_GFDR_RESULTS_ZH.md`](../results/LRS_GFDR_RESULTS_ZH.md)


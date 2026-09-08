# LRS-GFDR+AC-BPDD（兼容入口）

> 正式文件已更名为 [`LRS_GFDR_AC_BPDD_ZH.md`](LRS_GFDR_AC_BPDD_ZH.md)。本页保留为旧链接兼容入口。

LRS-GFDR+AC-BPDD 在 LRS-GFDR 的逐边分布上增加训练期 AC-BPDD（Adaptive-Consistency Boundary Progressive Distribution Distillation）。AC-BPDD 复用 stock assignment，仅向更可靠的未来层传递 softmin 教师信号；推理图不增加 BPDD 分支。

本材料中的结果来自已经完成的 `LRS-FDR + AC-BPDD` 运行。由于该运行的几何解码默认已启用，现以显式 `feasible_geometry: true` 的配置封装为 **LRS-GFDR+AC-BPDD**。这是命名与配置显式化，不是声称重新训练了一次。

- 配置：[`configs/rtdetr-l-lrs-gfdr-ac-bpdd.yaml`](../../configs/rtdetr-l-lrs-gfdr-ac-bpdd.yaml)
- BPDD 权重：`0.15`；temperature：`0.5`；margin：`0.02`
- 训练期模块，不增加推理参数
- 与 LRS-GFDR 的比较必须注明“历史已完成 AC-BPDD 运行的封装映射”，不能写成 fresh paired rerun

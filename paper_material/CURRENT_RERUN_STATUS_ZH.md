# 当前重跑状态（2026-08-22）

## 当前唯一论文主线

论文实验现切换为官方 D-FINE-S 路线。首个运行固定为官方代码提交 `7fe2f8889f0b7b817f20c315b40fc15a4fb64ae6`、HGNetv2-B0 stage1、VisDrone 10 类、640 输入、batch 8、seed 0、132 epochs 和 AMP。训练使用官方损失、匹配与多尺度训练配置，不混入旧 Ultralytics 实现。

当前运行目录为 `/home/ubuntu/dfine-runs/dfine-s-visdrone-seed0-official7fe2`。正式结果必须来自该运行的 best checkpoint，并在冻结的 val/test 评估协议下复评后才能写入论文表格。

## 当前不得作为新稿结论的内容

- EQuAL、AP-FDR 和旧 FDR 的 standalone 数值；
- 基于旧 Ultralytics RT-DETR-L 的 A–E 主表及其涨点；
- 旧 FDR+BPDD、FDR+FIA、FDR+BPDD+FIA 的组合数值；
- 由不同源码、训练 authority 或拓扑拼接得到的算术增量；
- 围绕旧结果形成的当前论文提纲、主张和图表安排。

这些内容只作为历史审计材料保留，不再从当前论文入口引用。Git 历史、原始日志、checkpoint 哈希和机器证据不删除，避免后续无法复核。

## 继续保留并复用的内容

- BPDD 的训练期渐进式边界分布蒸馏思想与实现；
- FIA 的 P3-only 高分辨率增强思想与实现；
- VisDrone 数据映射、原始 val/test 文本和逐类证据；
- 外部 VisDrone 正式论文比较资料及来源；
- 复杂度测量脚本、证据清单和完整 Git 历史。

保留不等于沿用旧数值。BPDD 和 FIA 接入官方 D-FINE 后必须重新训练与评估，旧组合权重不能改名复用。

## 结果替换顺序

1. 官方 D-FINE-S / VisDrone 基线；
2. 同源码、同 seed、同协议的 D-FINE-S + BPDD；
3. 同条件的 D-FINE-S + FIA；
4. D-FINE-S + BPDD + FIA；
5. 对四个 best checkpoint 做统一 val/test 与 Params/FLOPs/Latency 复评；
6. 仅用新结果重建论文主表、消融表、复杂度表和写作提纲。

在第 6 步完成前，`results/`、`experiments/` 和 `writing/` 中的旧路线页面均视为历史快照，而不是当前投稿定稿。

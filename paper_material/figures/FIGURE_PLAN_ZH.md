# ICASSP 四图规划

所有图采用白底、黑灰线条和可独立理解的图注；虚线统一表示“仅训练期”，实线表示推理路径。证据等级不得只靠颜色区分。

## 图 1：整体架构

- 目的：展示 RT-DETR-L Backbone/Hybrid Encoder、三尺度特征、P3-only FIA、FDR decoder 和训练期 BPDD 的关系。
- 必须标注：stock P3 经 FIA 后送入 decoder；P4/P5 绕过 FIA；FDR 输出四边分布并解码框；BPDD 用虚线连接损失端。
- 源码依据：`configs/rtdetr-l-fdr-bpdd-fia.yaml`、`src/fdr_head.py`、`src/rtdetr_fdr.py`、`src/rtdetr_fdr_bpdd.py`、`src/rtdetr_fdr_bpdd_fia.py`。
- 禁止标签：BPDD inference branch、FIA on P4/P5、new backbone、FDR invented here、zero-overhead full model；不得绘制代码中不存在的额外检测头。

## 图 2：BPDD 渐进监督

- 目的：以六层 FDR 边界分布为纵轴，说明早期层只从未来层构造教师。
- 必须标注：相邻 bin 目标误差、future-only softmin、停止梯度教师、better-only reliability、最终 stock assignment、normal queries、KL loss。
- 源码依据：`src/bpdd_loss.py`、`src/fdr_loss.py`、`src/rtdetr_fdr_bpdd.py`、`configs/rtdetr-l-fdr-bpdd.yaml`。
- 禁止标签：bidirectional distillation、past-layer teacher、trainable teacher、denoising-query BPDD、BPDD at inference、standalone BPDD；不得画成所有教师边都无条件激活。

## 图 3：FIA 模块

- 目的：展开两个串联局部细化块、通道注意力、空间 mean/max 注意力和外层残差缩放。
- 必须标注：每个细化块的 1×1—DW 3×3—1×1 及两条内部残差；通道 `AvgPool, C→C/4→C`；空间 `Mean/Max, 7×7`；`Y=X+alpha(F(X)-X)`、`alpha init=0`、输入输出同形状。
- 源码依据：`src/fia.py`、`src/rtdetr_fdr_bpdd_fia.py`、`configs/rtdetr-l-fdr-bpdd-fia.yaml`。
- 禁止标签：multi-scale FIA、resolution change、alpha fixed at zero、parameter-free、removed at inference、attention invented here；不得把 P4/P5 画进 FIA 内部。

## 图 4：结果比较

- 目的：并列呈现四个模型的 mAP50–95，并在独立子图呈现前三个有值模型的 AP75。
- 必须标注：每根柱或点的模块组合、数值、`strict`/`cross_authority_exact`/`screenshot_rounded`；完整模型 mAP 使用 `≈`，AP75 显示 unavailable 而不是零值。
- 数据依据：`paper_material/results/main_results.json`、`paper_material/results/MAIN_TABLE_ZH.md`、`paper_material/evidence/source_manifest.json`、`paper_material/evidence/bpdd_val_exact.json`。
- 禁止标签：paired BPDD gain、paired FIA gain、statistically significant、multi-seed mean、test-set result、exact full-model score；不得补造完整模型 AP75、误差条或显著性符号。

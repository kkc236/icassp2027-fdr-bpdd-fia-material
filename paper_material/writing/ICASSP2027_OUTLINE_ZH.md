# ICASSP 2027 写作提纲

## 论文主线

建议主线为“细粒度分布细化基础—训练期渐进蒸馏—高分辨率特征增强”。FDR 是从固定版本 D-FINE 适配而来的结构基础，不是本文发明；BPDD 和 FIA 在 RT-DETR-L/VisDrone 系统中分别处理优化监督与高分辨率表征。

## 贡献组织

1. 将 FDR 的边界分布表示和相关监督稳定适配到 Ultralytics RT-DETR-L。
2. 构建依赖 FDR 逐边分布的训练期 BPDD，不增加推理分支。
3. 集成修改后的 FIA 高分辨率特征增强模块，并以独立消融验证其与 FDR、BPDD 的兼容性。

第三点的方法细节已绑定当前 `src/fia.py`：双 depth-wise 残差细化、联合通道/空间注意力、零初始化残差缩放和构造期 RNG 隔离。published standalone 与 P3-only 三模块的拓扑身份仍须分开书写。

## 章节结构

### 1. Introduction

围绕无人机场景小目标、遮挡和定位不确定性展开问题，说明定位分布、训练监督和高分辨率表征三个层面的互补性。

### 2. Related Work

覆盖 transformer detector、分布式框回归、蒸馏和小目标特征增强；明确 FDR/FGL/Integral 的来源。

### 3. Method

- 3.1 Overall Architecture：RT-DETR-L baseline、FDR decoder、训练期 BPDD 与修改后 FIA 的关系。
- 3.2 Fine-grained Distribution Refinement：分布表示与解码。
- 3.3 Boundary Progressive Distribution Distillation：教师构造、激活条件和损失。
- 3.4 FIA：描述双基础块、联合通道/空间注意力、恒等安全残差缩放及 P3 插入位置。
- 3.5 Training Objective and Inference：总损失、BPDD 仅训练期、FDR/FIA 推理期角色。

### 4. Experiments

- 4.1 Dataset and Protocol：VisDrone、RT-DETR-L、scratch、640、seed 0、100 epochs 与统一评估器。
- 4.2 Main Results：正式核心表放 baseline、FDR 和 FDR+BPDD；三模块 P3-only best-val 作为补充观察。
- 4.3 Ablation Studies：分开报告现有 best.pt 的 FIA-only 与 FDR+FIA exact val/test；val ΔmAP 为 −0.2315/+0.5280 pp，test ΔmAP 为 −0.0240/+0.6644 pp，且均不是严格配对、不是 P3-only。
- 4.4 Analysis：呈现 FDR/BPDD 的可审计分析，以及 FIA standalone 的总体、AP75 和 10 类 test 结果；尺度分析仅使用已有核心行，不为 FIA 反推缺失值。

### 5. Conclusion

总结三部分的职责，但最终效果结论必须以完整新版 FIA 证据为准。

## 当前允许主张

- strict 证据下，FDR 相对 RT-DETR-L 的 mAP50–95 为 +0.07055，AP75 为 +0.07951。
- BPDD 是依赖 FDR 边界分布的训练期、无参数蒸馏，不增加推理图或参数。
- 现有 standalone best.pt 独立 val 中，FIA-only mAP50–95=0.216795（相对 baseline −0.2315 pp），FDR+FIA=0.294940（相对 FDR +0.5280 pp）；independent exact test 分别为 0.177176（−0.0240 pp）与 0.234645（+0.6644 pp），且 AP75 与 10 类明细已补齐。这支持“FIA 与 FDR 组合兼容”，不支持“FIA 单独稳定增益”。
- 已确认正确 P3-only 新三模块 checkpoint 的 best-val 为 P=0.56996、R=0.49848、AP50=0.48982、mAP50–95=0.29618；相对当前 BPDD val 绝对值为 +0.3922 pp 的算术观察。
- 该三模块观察仍缺 AP75、test 和冻结 evaluator 独立复评。

## 当前禁止主张

- 把 standalone best.pt 结果称为 P3-only 或严格配对因果增益。
- 宣称 FIA-only 正增益；当前直接复评显示其 val mAP 略低于 baseline。
- 新三模块 best-val 观察是严格配对因果增益、完整评估或最终论文主表结果。
- “本文发明 FDR、FGL、Integral、非均匀积分或相邻 bin 监督”。
- “BPDD 可脱离 FDR 单独使用”或“BPDD 具有推理期零总开销”。
- 混用 val/test、不同 checkpoint、不同 evaluator 或不同源码 authority。

写作数值统一从 [论文结果汇总](../results/RESULTS_ZH.md)提取，FIA 证据状态以 [FIA 结果状态](../results/FIA_RESULTS_STATUS_ZH.md) 为准。

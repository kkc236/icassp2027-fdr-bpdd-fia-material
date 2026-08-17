# ICASSP 2027 写作提纲

## 论文主线

建议主线为“细粒度分布细化基础—训练期渐进蒸馏—高分辨率特征增强”。FDR 是从固定版本 D-FINE 适配而来的结构基础，不是本文发明；BPDD 和 FIA 在 RT-DETR-L/VisDrone 系统中分别处理优化监督与高分辨率表征。

## 贡献组织

1. 将 FDR 的边界分布表示和相关监督稳定适配到 Ultralytics RT-DETR-L。
2. 构建依赖 FDR 逐边分布的训练期 BPDD，不增加推理分支。
3. 集成修改后的 FIA 高分辨率特征增强模块，并以独立消融验证其与 FDR、BPDD 的兼容性。

第三点的方法细节必须在最新 FIA 源码完成绑定后定稿，不能从旧实现或旧实验反推。

## 章节结构

### 1. Introduction

围绕无人机场景小目标、遮挡和定位不确定性展开问题，说明定位分布、训练监督和高分辨率表征三个层面的互补性。

### 2. Related Work

覆盖 transformer detector、分布式框回归、蒸馏和小目标特征增强；明确 FDR/FGL/Integral 的来源。

### 3. Method

- 3.1 Overall Architecture：RT-DETR-L baseline、FDR decoder、训练期 BPDD 与修改后 FIA 的关系。
- 3.2 Fine-grained Distribution Refinement：分布表示与解码。
- 3.3 Boundary Progressive Distribution Distillation：教师构造、激活条件和损失。
- 3.4 FIA：在最新源码绑定后描述结构和插入位置。
- 3.5 Training Objective and Inference：总损失、BPDD 仅训练期、FDR/FIA 推理期角色。

### 4. Experiments

- 4.1 Dataset and Protocol：VisDrone、RT-DETR-L、scratch、640、seed 0、100 epochs 与统一评估器。
- 4.2 Main Results：当前正式表只放 baseline、FDR 和 FDR+BPDD。
- 4.3 Ablation Studies：FIA-only、FDR+FIA 和三模块在新版证据完成后加入；不得引用修改前 FIA 数据。
- 4.4 Analysis：先呈现 FDR/BPDD 的现有可审计分析；FIA 的总体、尺度、类别和效率分析待新版独立复评补齐。

### 5. Conclusion

总结三部分的职责，但最终效果结论必须以完整新版 FIA 证据为准。

## 当前允许主张

- strict 证据下，FDR 相对 RT-DETR-L 的 mAP50–95 为 +0.07055，AP75 为 +0.07951。
- BPDD 是依赖 FDR 边界分布的训练期、无参数蒸馏，不增加推理图或参数。
- 已确认正确 P3-only 新三模块 checkpoint 的 best-val 为 P=0.56996、R=0.49848、AP50=0.48982、mAP50–95=0.29618；相对当前 BPDD val 绝对值为 +0.3922 pp 的算术观察。
- 该三模块观察仍缺 AP75、test 和冻结 evaluator 独立复评。

## 当前禁止主张

- 任何修改前 FIA 指标、截图或旧方向性结论仍可作为参考。
- 单 FIA 与 FDR+FIA 的正式数值已经取得；目前只有用户报告新版均为正增益，尚无可审计资产。
- 新三模块 best-val 观察是严格配对因果增益、完整评估或最终论文主表结果。
- “本文发明 FDR、FGL、Integral、非均匀积分或相邻 bin 监督”。
- “BPDD 可脱离 FDR 单独使用”或“BPDD 具有推理期零总开销”。
- 混用 val/test、不同 checkpoint、不同 evaluator 或不同源码 authority。

FIA 证据状态以 [FIA 结果状态](../results/FIA_RESULTS_STATUS_ZH.md) 为准。

# FIA：高分辨率特征增强模块

## 定位

FIA 面向 RT-DETR-L 的高分辨率特征路径，用于在进入 decoder 前增强小目标相关表征。论文中的模块结构、插入位置和参数统计必须以修改后 FIA 的源码与配置为准；修改前实现及其所有实验结果不再具有证据效力。

当前私密仓库中的 src/fia.py、相关 YAML 和训练入口可用于代码定位，但在完成与最新修改提交的逐文件绑定前，本页不冻结更细的内部算子公式、层索引或复杂度数值，避免把旧实现细节误写成最终方法。

## 运行角色

- FIA 是推理图中的特征模块，不是 BPDD 的辅助损失。
- FIA-only 用于检验其相对 stock baseline 的独立贡献。
- FDR+FIA 用于检验其与定位分布细化的兼容性。
- FDR+BPDD+FIA 用于检验三模块整体组合；BPDD 仍只在训练期工作。

## 当前实验状态

- 修改前 FIA-only 和 FDR+FIA 数据全部撤销，不能作为历史补充。
- 用户报告修改后的 standalone FIA 与 FDR+FIA 均为正增益，但新版可审计资产尚未找到，因此不写具体数值。
- 已确认 DFR-BDPP-FIA-best.pt 是修改后、正确 P3-only 拓扑的三模块 checkpoint。其 best-val 为 P=0.56996、R=0.49848、AP50=0.48982、mAP50–95=0.29618；相对当前 BPDD val 绝对值是 +0.3922 pp 的算术观察。
- 上述三模块 checkpoint 尚缺 AP75、test 和冻结 evaluator 独立复评，不能写成严格配对的 FIA 因果增益。

## 论文表述边界

允许表述：FIA 是高分辨率特征增强模块；新版三模块 checkpoint 已显示正向 best-val 观察，但完整独立复评仍待补。

禁止表述：修改前 FIA 数值仍有参考价值；旧截图可以补充证明趋势；单 FIA 或 FDR+FIA 的正式涨点已经取得；三模块 best-val 观察等同于严格配对、完整指标或最终论文结果。

状态与导入清单见 [FIA 结果状态](../results/FIA_RESULTS_STATUS_ZH.md)。

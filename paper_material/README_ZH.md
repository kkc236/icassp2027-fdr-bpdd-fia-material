# ICASSP 2027 论文材料入口

本目录汇总 FDR、BPDD 与 FIA 在 RT-DETR-L/VisDrone 项目中的方法、协议、结果和写作边界。正文只采用可由代码、配置和登记证据共同支持的事实；不同数据划分、评估器或源码状态的结果不得拼接成配对增益。

> FIA 证据状态已更正：修改前 FIA 的全部指标、截图、运行记录和派生结论均已撤销，不得作为历史补充、趋势观察或论文证据继续引用。当前正式结果仅保留不含 FIA 的三条模型行。详见 [FIA 结果状态](results/FIA_RESULTS_STATUS_ZH.md)。

## 阅读顺序

1. 方法基础：[FDR：细粒度分布细化](methods/FDR_ZH.md)
2. 训练监督：[BPDD：渐进式分布蒸馏](methods/BPDD_ZH.md)
3. 特征增强：[FIA：模块状态与写作边界](methods/FIA_ZH.md)
4. 冻结设置：[实验协议](experiments/PROTOCOL_ZH.md)
5. FIA 实验入口：[FIA-only 与 FDR+FIA 实验脚手架](experiments/FIA_ABLATION_SCAFFOLD_ZH.md)
6. FIA 新版结果：[FIA 消融新版结果](results/FIA_ABLATION_RELEASE_RESULTS_ZH.md)
7. FIA 证据状态：[新版结果状态与导入条件](results/FIA_RESULTS_STATUS_ZH.md)
8. 可引用数值：[主结果表](results/MAIN_TABLE_ZH.md)
9. val/test 涨点：[不含 FIA 的已核验对比](results/SPLIT_GAIN_COMPARISON_ZH.md)
10. 论文组织：[ICASSP 2027 写作提纲](writing/ICASSP2027_OUTLINE_ZH.md)
11. 绘图交接：[四图规划](figures/FIGURE_PLAN_ZH.md)

## 当前可引用证据

- RT-DETR-L baseline：已有登记的 val/test 结果。
- RT-DETR-L+FDR：已有登记的 val/test 结果；同协议部分可与 baseline 作严格差值。
- RT-DETR-L+FDR+BPDD：已有登记的 val/test 精确绝对值；跨 authority 差值必须明确标注边界。
- FIA-only 与 FDR+FIA：网页模型与 log 已审计，但现有 standalone checkpoint 均为修改前 cascading 拓扑；修改后 P3-only 正式数值仍待导入，不得从旧附件取值。
- FDR+BPDD+FIA：正确 P3-only 新 checkpoint 已定位，best-val 记录为 P=0.56996、R=0.49848、AP50=0.48982、mAP50–95=0.29618；相对当前 BPDD val 绝对值为 +0.3922 pp 的算术观察。AP75、test 和独立复评仍待补，因此不进入正式主表。

修改后 FIA 的人类可读结果入口为 [FIA 消融新版结果](results/FIA_ABLATION_RELEASE_RESULTS_ZH.md)，机器状态与导入条件以 [FIA 结果状态](results/FIA_RESULTS_STATUS_ZH.md) 为准。旧 FIA 内容或附件即使可从 Git 历史找回，也不具有任何证据效力。

## 机器可读证据

- [正式 val 主结果](results/main_results.json)：只含当前可进入正式表的三条无 FIA 结果，并另列新版三模块 checkpoint 观察。
- [组合状态与 val/test 总体结果](results/split_gain_comparison.json)：覆盖全部 8 种开关组合并区分撤销、待导入和已核验状态。
- [val/test 总体 CSV](results/split_overall_results.csv)、[尺度 CSV](results/split_scale_results.csv)、[类别 CSV](results/split_class_results.csv)：仅保留无 FIA 的有效结构化结果。
- [FIA 消融新版结果](results/FIA_ABLATION_RELEASE_RESULTS_ZH.md)：覆盖旧同名页面，只呈现修改后 FIA 的有效结果与待补项。
- [FIA 机器状态](evidence/fia_results_status.json)：记录撤销范围、新三模块 checkpoint 观察及新版 standalone 导入条件。
- [来源清单](evidence/source_manifest.json)：绑定有效结果与新版三模块 checkpoint 的来源和哈希。

## 最小依赖与使用原则

- FDR 是定位表示基础，替换 RT-DETR-L 解码器的连续四维框回归路径。
- BPDD 消费 FDR 的逐层四边分布，因此最小有效宿主是 FDR；“BPDD 单独”不是合法模型行。
- FIA 的论文实现描述和实验身份必须绑定到修改后的源码、配置、checkpoint 与评估输出。
- 用户已报告新版 FIA-only 与 FDR+FIA 均为正增益，但当前尚未获得可审计数值，且在 GitHub 当前可见内容中未找到可确认的新版 standalone 资产；因此这两条报告只记录为待核验状态。
- FDR/FGL/Integral 及非均匀积分来自固定版本的 D-FINE 先验。本项目可主张的是面向 Ultralytics RT-DETR-L 与 VisDrone 的结构化适配、隔离集成和验证，不是这些基础机制的发明。

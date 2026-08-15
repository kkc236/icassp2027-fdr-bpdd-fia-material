# ICASSP 2027 论文材料入口

本目录汇总 FDR、BPDD 与 FIA 在 RT-DETR-L/VisDrone 项目中的方法、协议、结果和写作边界。正文只采用可由代码、配置或登记证据支持的事实；不同数据划分、评估器或源码 authority 的结果不得拼接成配对增益。

## 阅读顺序

1. 方法基础：[FDR：细粒度分布细化](methods/FDR_ZH.md)
2. 训练监督：[BPDD：渐进式分布蒸馏](methods/BPDD_ZH.md)
3. 特征增强：[FIA：P3 特征增强模块](methods/FIA_ZH.md)
4. 冻结设置：[实验协议](experiments/PROTOCOL_ZH.md)
5. 可引用数值：[主结果表](results/MAIN_TABLE_ZH.md)
6. 论文组织：[ICASSP 2027 写作提纲](writing/ICASSP2027_OUTLINE_ZH.md)
7. 绘图交接：[四图规划](figures/FIGURE_PLAN_ZH.md)

## 机器可读证据

- [归一化主结果](results/main_results.json)：论文表格的机器数值源。
- [来源清单](evidence/source_manifest.json)：结果行与源码提交、原始证据的绑定关系。
- [BPDD 精确验证结果](evidence/bpdd_val_exact.json)：BPDD 行的结构化精确指标。

以上 JSON 由证据整合阶段提供；Markdown 不替代其中的来源标识与精度信息。

## 最小依赖与使用原则

- FDR 是定位表示基础，替换 RT-DETR-L 解码器的连续四维框回归路径。
- BPDD 消费 FDR 的逐层四边分布，因此最小有效宿主是 FDR；“BPDD 单独”不是合法模型行。
- FIA 位于高分辨率 P3 路径，训练和推理均参与前向计算。
- 只有 `strict` 行之间才可写严格配对差值；`cross_authority_exact` 仅表示数值精确，不表示配对；`screenshot_rounded` 只能近似展示。
- FDR/FGL/Integral 及非均匀积分来自固定版本的 D-FINE 先验。本项目的可主张贡献是面向 Ultralytics RT-DETR-L 与 VisDrone 的结构化适配、隔离集成和验证，不是这些基础机制的发明。

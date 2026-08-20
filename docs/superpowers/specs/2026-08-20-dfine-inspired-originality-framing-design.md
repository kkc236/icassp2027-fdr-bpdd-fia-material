# D-FINE 启发来源与原创性表述设计

## 目标

统一论文材料对 AP-FDR 与 BPDD 的来源和原创性表述：明确两者的研究动机均受到 D-FINE 启发，同时把可归属于本文的具体结构、监督合同与算法机制说清楚。BPDD 作为本文独立提出并实现的原创算法重点呈现；AP-FDR 不冒领 D-FINE 已公开的离散边界分布、FGL、Integral 或非均匀投影公式。

## 核心口径

1. 使用学术表达“受 D-FINE 启发”，不使用口语化的“看完论文后照着设计”。
2. 将本文方法称为 AP-FDR，强调它是对 RT-DETR-L 定位路径的独立重构；结果表因历史配置继续简称 FDR。
3. BPDD 明确写成“由本文独立提出并实现的原创算法”。D-FINE/GO-LSD只提供“跨层定位知识可能有价值”的问题启发，不提供 BPDD 的具体算法构造。
4. BPDD 与 GO-LSD 用可核验机制隔离：教师来源、教师选择、可靠性门控、匹配合同、查询范围和损失形式均不同。
5. “纯原创”限定为 BPDD 的具体 formulation 与实现未复用 GO-LSD 公式或代码，不扩张成未经系统检索证明的“文献史上首次”。

## AP-FDR 的正文呈现顺序

AP-FDR 采用“原创贡献先行、基础来源后置”的组织方式。正文先用一个完整段落或四个紧凑要点说明本文原创设计：

1. 只改造 RT-DETR-L localization branch，保留 stock 分类、查询选择、Decoder attention/FFN、匹配与后处理合同；
2. 从 stock 框回归头获得初始几何先验，构建 stock-head-informed preliminary reference；
3. normal 与 denoising 查询均复用已有 assignment 组织 FGL 和 preliminary-box 监督，不增加重复匹配；
4. 对新增分布头采用私有随机数生成器和隔离初始化，避免改变公共参数初始化与数据随机序列。

随后只用一句来源声明交代 D-FINE 的基础构件，不在 Abstract、Introduction 或 Contributions 中罗列函数名。完整来源清单只放在方法页的可复现性说明或补充材料。

## 基础来源的精确边界

论文正文不反复使用“复用”一词。首选措辞为“基于”“沿用已公开的基础算子”“采用 D-FINE 的基础分布构件”或英文 `builds on / adopts established primitives from D-FINE`。“复用”仅在机器实现、代码来源或审计清单中使用一次，以保持来源透明。

固定 D-FINE commit `7fe2f8889f0b7b817f20c315b40fc15a4fb64ae6` 提供的基础实现包括：

- `weighting_function` 与非均匀 bin 投影；
- `Integral` 概率积分解码；
- `translate_gt`、`bbox2distance` 和 `distance2bbox` 的目标编码与框变换；
- `unimodal_distribution_focal_loss` / FGL 相邻 bin 基础损失；
- `reg_max=32`、`reg_scale=4`、`loss_fgl=0.15` 等绑定设置。

逐边 33-bin 表示、非均匀投影、Integral、相邻 bin FGL 以及累计分布细化不作为本文原创点。D-FINE 的完整 detector、LQE、DDF、GO-LSD 和 Decoder widening 没有进入 AP-FDR。生产代码中的 RT-DETR-L 接入、损失路由、匹配合同、初始化隔离和兼容性检查属于本文实现。

## 篇幅比例

- Abstract：D-FINE 只出现一次，使用半句说明启发来源；其余篇幅描述 AP-FDR 的问题、设计和结果。
- Introduction/Contributions：来源声明最多一句，AP-FDR 原创设计至少占四句或一个完整贡献条目。
- Method：先写原创结构，再用一段短句说明基础来源；函数级来源清单放在段末、脚注或 Supplementary。
- Related Work：正常引用 D-FINE 和 GO-LSD，但不在该段替本文贡献下结论。
- 中文材料总体上保持基础来源与原创设计约 `1:4` 的篇幅比例；减少来源篇幅不等于删除必要归因。

推荐核心句式：

> 基于 D-FINE 已公开的非均匀边界分布、Integral 解码与 FGL 基础算子，本文提出 AP-FDR；其核心贡献在于面向 stock RT-DETR-L 构建架构保持型定位路径、由原始框头提供几何先验的 preliminary branch、normal/DN 匹配一致监督以及隔离初始化机制。

## 修改范围

- `paper_material/README_ZH.md`：统一总览贡献口径。
- `paper_material/methods/FDR_ZH.md`：增加启发链和 AP-FDR 独立重构声明。
- `paper_material/methods/BPDD_ZH.md`：增加原创性声明及 GO-LSD 差异表。
- `paper_material/writing/ICASSP2027_OUTLINE_ZH.md`：重写贡献点和 Related Work/Method 写作指令。
- `paper_material/writing/NOVELTY_POSITIONING_AND_ADVERSARIAL_AUDIT_ZH.md`：强化对抗性审计、英文贡献文案和禁用句式。
- `tests/test_material_integrity.py`：锁定关键归因与原创性边界，防止后续文档漂移。

## 审稿风险控制

- 不写“本文首次提出 FDR”，因为 D-FINE 已使用该名称。
- 不写“BPDD 与 GO-LSD 完全无关”，而写“问题启发相关、算法构造独立”。
- 不把 AP-FDR 的全部增益归因给本文独立结构，内部双消融完成前只归因给完整 AP-FDR。
- 不使用“证明绝对原创”等不可证措辞；采用“independently formulated and implemented in this work”。

# D-FINE 启发来源与原创性表述设计

## 目标

统一论文材料对 AP-FDR 与 BPDD 的来源和原创性表述：明确两者的研究动机均受到 D-FINE 启发，同时把可归属于本文的具体结构、监督合同与算法机制说清楚。BPDD 作为本文独立提出并实现的原创算法重点呈现；AP-FDR 不冒领 D-FINE 已公开的离散边界分布、FGL、Integral 或非均匀投影公式。

## 核心口径

1. 使用学术表达“受 D-FINE 启发”，不使用口语化的“看完论文后照着设计”。
2. 将本文方法称为 AP-FDR，强调它是对 RT-DETR-L 定位路径的独立重构；结果表因历史配置继续简称 FDR。
3. BPDD 明确写成“由本文独立提出并实现的原创算法”。D-FINE/GO-LSD只提供“跨层定位知识可能有价值”的问题启发，不提供 BPDD 的具体算法构造。
4. BPDD 与 GO-LSD 用可核验机制隔离：教师来源、教师选择、可靠性门控、匹配合同、查询范围和损失形式均不同。
5. “纯原创”限定为 BPDD 的具体 formulation 与实现未复用 GO-LSD 公式或代码，不扩张成未经系统检索证明的“文献史上首次”。

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

# ICASSP 既有方法论文写法迁移设计

## 目标

学习正式 ICASSP 论文处理“既有基础—任务改造—本文贡献”的写作方式，用于改写 AP-FDR/BPDD/FIA 的叙事；这些论文与本文研究问题没有直接关系，因此不进入本文 Related Work、方法对比表或参考文献。

## 写法规则

1. **不引入无关文献**：YOLO-SAM2、SpaRSep、Pitch-SSL、ICASSP YOLO 重构等材料只作为内部写作样本，不作为本文技术依据或相关工作。
2. **问题先行**：每个方法段先指出 VisDrone/RT-DETR 的具体缺口，再说明本文设计，最后用一句话交代基础机制来源。
3. **贡献按动作定义**：避免用“集成了某模块”作为贡献，改写为本文改变了什么路径、监督关系、教师构造或特征流。
4. **来源一次说清**：D-FINE 只在 Related Work 和 AP-FDR 方法边界中准确归因；不反复强调，也不隐藏其基础分布算子来源。
5. **证据紧随主张**：AP-FDR、BPDD、FIA 的贡献分别绑定严格结果、内部消融状态、推理开销和拓扑证据；未完成实验不写成已验证结论。
6. **不借先例自证创新**：正文不出现“ICASSP 已接受类似迁移，因此本文也有创新”之类论证。创新性只由本文问题、机制差异和消融支持。

## 具体改写结构

### AP-FDR

按“密集小目标边界不确定性 → stock RT-DETR 连续框路径的限制 → 架构保持型分布定位 → 四项本文设计 → D-FINE 基础算子来源”的顺序写。贡献主体为 localization-only 合同、stock-head-informed preliminary geometry、normal/DN assignment-consistent supervision 和隔离初始化。

### BPDD

按“早期解码层定位不足 → 固定末层教师的局限 → all-future target-conditioned teacher → better-only gate → training-only zero-inference-overhead”的顺序写。GO-LSD 仅作为最近问题背景，BPDD 的公式、教师、门控、匹配和实现均按现有证据描述。

### FIA

按“P3 小目标细节需求 → 只增强 P3 且绕开 P4/P5 重建 → 双 depth-wise 细化与联合门控 → 正增益和有限开销”的顺序写。不得将 cascading 与 P3-only 结果混写。

## 修改范围

- `paper_material/methods/FDR_ZH.md`：把方法开头和主张边界改为问题驱动、贡献动作驱动。
- `paper_material/writing/ICASSP2027_OUTLINE_ZH.md`：重写 Introduction、Related Work、Method 的写作指令；明确无关 ICASSP 先例不入参考文献。
- `paper_material/writing/NOVELTY_POSITIONING_AND_ADVERSARIAL_AUDIT_ZH.md`：加入“只学写法、不引论文”的边界和可直接使用的贡献句式。
- `paper_material/README_ZH.md`：统一材料入口中的方法定位。
- `tests/test_material_integrity.py`：仅在已有测试结构适合时锁定“不把写法样本列作相关工作”的边界；不增加脆弱的整段文本断言。

## 验收标准

- 上述无关 ICASSP 论文的标题、作者、DOI 不进入论文材料正文。
- D-FINE 来源仍被准确保留，AP-FDR 原创边界不扩大。
- 三个贡献均以“问题—设计—证据”组织，不写成模块清单。
- 不新增结果数字，不改变现有 val/test、strict/non-paired 和拓扑口径。
- Markdown、机器测试和仓库状态通过验证后再推送。

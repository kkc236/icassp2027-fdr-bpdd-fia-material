# 独立终审：技术表述与证据边界

审阅日期：2026-09-17。审阅者未参与改稿。本次只读 `source/body.tex`、`build.py`、五张 TikZ 图及必要的 `inputs` 证据；未训练、未推理、未访问服务器，未修改正文或任何实验数字。

## 总体判断

当前版本已清楚区分原创 LRS-GFDR 规则、继承自 D-FINE 的表示，以及完整系统的测试结果。Original FDR 被明确限定为 RT-DETR 内的完整 FDR/FGL 定位移植，未误写为整个官方 D-FINE 检测器。没有发现已读公式与冻结实现之间的实质矛盾；AP 差值、GFLOPs 每图口径及 batch-eight 吞吐单位均一致。下面的改动主要消除残留的因果措辞，并修正一处计时描述歧义。

## 最多五处可直接修改的句子

### 1. 历史定位链：把“添加模块导致变化”改为记录差值（建议修改）

定位：Sec. 4.2，`Within the intermediate configurations, adding geometry changes AP ...`

建议替换：

> Across the historical intermediate configurations, Clean-FDR + geometry records 29.361 AP versus 29.696 for Clean-FDR (−0.335), while LRS-GFDR records 29.620 AP, 0.259 points above the geometry-equipped configuration.

理由：`inputs/lrs_comparison_provenance.json` 明确说明这些行未全部建立同源码、同初态对照；原句的 “adding ... changes/increases” 仍容易被读成单因素因果结果。上文的局限声明不能完全消除这一局部含义。

### 2. LRS“恢复精度”的总结过于因果化（建议修改）

定位：紧接上述比较的 `The recorded result is therefore an accuracy recovery with LRS after imposing explicit geometric feasibility ...`

建议替换：

> These records place LRS-GFDR between Clean-FDR and Clean-FDR + geometry in AP; its positive difference from Original FDR compares the overall localization redesign, including the reference and supervision construction, without isolating the contribution of each change.

理由：保留全部正负结果及主要比较，同时不把尚未充分匹配的 +0.259 归因为 LRS 的独立精度恢复。

### 3. Baseline 到 G 的“accounts for”可再收紧（可选修改）

定位：Sec. 4.3，`The localization core accounts for most of the recorded improvement over RT-DETR-L ...`

建议替换：

> The largest recorded validation difference is between Baseline and the localization core: AP is 21.911 and 29.620, respectively (+7.709), with the latter configuration including the inherited FDR representation.

理由：该差值真实且已注明继承部分，但 “accounts for” 仍有模块贡献分解的意味；历史源码/训练连续性差异使观察性表述更稳妥。

### 4. 完整扩展的证据总结应与其最强匹配对照一致（可选修改）

定位：Sec. 4.3 末句，`The evidence supports the complete extension and, most directly, the value of its shared P3 input within the matched pair.`

建议替换：

> Full has the highest recorded validation AP among these configurations, and the matched pair most directly supports the benefit of shared P3 refinement within the expert-equipped system.

理由：原句基本可接受，但“supports the complete extension”可能被扩大为 B、F、KD 均获独立验证；现有最强证据是 G+B 与 Full 的 +0.832，而 G+B 相对 G 为负。

### 5. 推理计时中的 hook 名称与融合口径（建议修改）

定位：Sec. 4.6，`Timing includes preprocessing, model execution, postprocessing, and the lightweight expert-checking hook, but excludes disk I/O.`

建议替换：

> Timing uses the predictor's native GPU fusion and includes preprocessing, model execution, postprocessing, and a lightweight expert-forward counter, while excluding disk I/O.

理由：`inputs/batch8_verified.json` 将该 hook 明确记录为 `per-expert forward counter`，并记录 `native predictor fusion on GPU`；“expert-checking”容易与训练期的质量门控混淆。补充实际融合设置也解释了为何计时使用融合预测器，而参数统计采用完整未融合模型。

## 标题、英文摘要与结论

- 当前标题准确指向几何可行的分布定位，没有不支持的实时、机载、SOTA 或独立跨数据集主张。虽然标题未展开 LRS，摘要和正文已给出其具体规则，不构成必须修改的问题。
- 英文摘要可读且范围基本恰当：29.620 对 29.078 明确为 validation，5.861 明确为 native test，1.579 绑定 scratch-adapted D-FINE-L 与不同训练配方；吞吐已绑定 RTX 4090、FP32 和 batch eight。
- 结论保留了单数据集单 seed、历史对照不完全隔离、不同训练配方及性质不等于精度/收敛收益的边界，未发现新增硬性夸大。不要把“actual partial correction”进一步改写为“保证优化步提高 IoU”；当前正文已正确排除这种保证。

## 当前仍取决于更多证据的关键风险

1. **主贡献的独立精度贡献仍有限定。** 代数与实现支持可行性、总权重守恒及收缩性质；历史结果支持设计间观察差值，但未证明两个原创规则分别造成精度提升。Clean-FDR 的 AP 仍比 LRS-GFDR 高 0.076；这一负结果必须继续保留。这里的证据缺口不能靠措辞或测试记录补成独立因果结论。
2. **专家、直接监督与 KD 的收益没有分离。** 现有证据更直接支持专家系统中共享 P3 的作用，无法把 Full 的差值单独归给选择性 KD。当前捆绑报告和局限声明合理。
3. **外部 D-FINE 比较仅支持当前复现与当前配方下的系统差值。** 共用评估器不能消除优化器、有效 batch、增广和训练计算量差异；不得升级为对官方 D-FINE 的等预算算法优越性。
4. **数值回归不是真实样本故障频率。** 归档 BF16 用例确有零宽高失败记录，修复后同名检查通过；但 pre-fix 完整源码与完全相同初始张量未归档。当前“stress case”而非真实坏框率的表述合适，不能据此加入真实数据数值改善幅度。
5. **泛化与部署范围仍窄。** converted-label VisDrone、一个 seed、曾参与早期开发的 test 以及桌面 GPU 固定随机输入吞吐，只支持已明示的范围。当前未做 UAVDT、逐图预测分析或机载评估，不应暗示已有相应证据。

## 核验依据

读取并比对了 `frozen_fdr_math.py`、`frozen_fdr_loss.py`、`current_joint_method.md`、`lrs_comparison_provenance.json`、`batch8_verified.json`、几何 evidence manifest/current-function/correctness 汇总，以及外部逐类图 verification。几何公式、LRS 系数与归一化、33-bin 支持、batch 吞吐换算及原始/修复测试边界均与这些已读材料一致。本次没有进行穷尽文献新颖性检索，不以此认证绝对首创，也不推断录用结果。

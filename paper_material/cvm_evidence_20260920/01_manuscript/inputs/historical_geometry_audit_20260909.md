# AC-BPDD 调整与重新设计：基于实测日志的对抗性审计

审计日期：2026-09-09。范围：现行 VisDrone AC-BPDD、其 LRS-GFDR 基座和已存在的 R/M 候选。状态：ANALYZED；完成服务器日志读取、源码检查与合成机制回归，未进行候选正式训练。本文是技术建议，不修改现有训练代码、权重、实验身份或材料仓历史结果。

## 1. 审计结论

当前证据更支持“蒸馏覆盖不低，但权重偏弱且目标/梯度方向未受定位质量充分约束”，不支持“assignment gate 几乎关闭”或“LRS 已经吃掉所有 BPDD 增益”的定论。

推荐先单独验证现有 residual_gradient_only（R），再根据真实梯度诊断选择可靠性重标定或几何方向约束。不要直接把现有 R+M+IoU 全开候选当作最优版本，也不要靠放大 weight、降低 margin 或移除几何校正来试错。

最强反对意见：BPDD 可能只是在已有六层 L1/GIoU/FGL 上增加了一个较弱、部分重复的监督项；改善末期平台不等于教师知识产生额外定位价值。如果几何期望蒸馏的改进可由相同预算的直接 GT 辅助回归复现，就应承认它主要是监督重分配，而不能把全部增益解释为跨层知识传递。

## 2. 本次读取的真实训练证据

运行根目录：`/root/sj-tmp/runs/`。

- F：`visdrone-v2-existing-state-20260907/formal-seed0-lrs_fdr_feasible-v2`
- G：`visdrone-v2/formal-seed0-lrs_fdr_ac_bpdd-v2`
- 无 LRS 几何对照：`visdrone-v2-clean-fdr-geometry-20260908/formal-seed0-clean-fdr-geometry-v1`
- 既有候选冒烟：`visdrone-v2-joint-candidate-smoke-20260908/candidate-smoke-v2`

F/G 均有 100 行 `results.csv` 和 100 行 `full-runtime.jsonl`。候选只有一轮冒烟，不能证明学习收益。无 LRS 几何对照没有同名 runtime 日志，不能假装已比较其内部蒸馏统计。

| 指标 | F：LRS-GFDR | G：+AC-BPDD | G−F |
|---|---:|---:|---:|
| best mAP50-95 | 0.29620（92轮） | 0.29628（92轮） | +0.008 pp |
| 81–90轮平均 mAP50-95 | 0.294459 | 0.294123 | −0.0336 pp |
| 91–100轮平均 mAP50-95 | 0.294712 | 0.295283 | +0.0571 pp |
| epoch100 mAP50-95 | 0.29371 | 0.29510 | +0.139 pp |

这说明 best 改善很小、末期有小幅正向观察；不能只挑最好看的末轮差，也不能只看 best 就宣布完全无效。连续轮次不是独立 seed，均值不提供统计显著性。

F 的记录提交为 c1ac0b25，G 为 f56b210。本次再次检查两提交间的 `fdr_head.py`、`fdr_math.py`、`fdr_loss.py`、`bpdd_loss.py`、`rtdetr_fdr.py` 以及两个 F/G YAML，git diff 为空。此前“提交不同所以必须重跑”的说法过强：应判断有效执行代码、配置与协议，而不是提交号本身。实际运行快照与未提交改动的身份仍应核对，但这不是自动否定已有对照的依据。

### 2.1 蒸馏覆盖与强度

下表是 G 的 epoch 日志统计；区间行是逐轮统计的等权均值，日志内部比例是 batch 等权均值，不是全数据逐边加权频率。

| 阶段 | 存在同 query/GT 未来教师的比例 | 活跃边比例 | 平均可靠性 r | 已加权 BPDD loss |
|---|---:|---:|---:|---:|
| 1–10轮 | 87.012% | 38.133% | 0.025685 | 0.000687 |
| 41–60轮 | 90.959% | 44.050% | 0.038539 | 0.002485 |
| 91–100轮 | 95.001% | 44.712% | 0.027382 | 0.001032 |
| 第100轮 | 95.120% | 44.635% | 0.026859 | 0.000990 |

`stable_match_ratio` 只表示每个源匹配至少有一个同目标未来教师，不代表全部未来层或中间层匹配均稳定。平均 r 包含零权重边。loss 数值小不等于梯度必然小；现有日志没有 BPDD 与主损失的分项梯度范数/cosine。`gradients_finite: null` 表示未记录，不能当作梯度非有限。

### 2.2 几何相关异常线索

91–100轮，对相应计数求和后除以 `geometry_total`：

| 解码前几何下限触发 | F | G |
|---|---:|---:|
| 横向 pair < minimum_extent | 0.004483% | 0.226048% |
| 纵向 pair < minimum_extent | 0.005329% | 0.095686% |

G/F 比值约 50.4 / 18.0，但绝对比例仍低于 0.23% / 0.10%。不能只报倍数放大问题。

统计包含训练 forward 的各层、normal/unmatched/DN 等预测，并非“匹配目标坏框率”；阈值为正的 minimum_extent，也不等于严格负宽高计数。与机器精度 floor 的全部触发也不是同一个统计。这里是值得定位的信号，不能断定 BPDD 损坏了正样本。F/G 抽查日志的 nonfinite_geometry_observations 为0，表示所记录的非有限几何观察未出现，不是完整数值安全证明。

## 3. 逐项对抗性审计

### A. “放宽 assignment 就能涨点”——依据不足

证据：后十轮稳定源匹配约95%、活跃边约45%。当前不是教师全面缺失。放开 query/GT 一致性可能重新引入不同目标之间的蒸馏；若跨 query 找同 GT 教师，其分布参考框不同，必须先做坐标重映射，不能直接 KL。

裁决：不作为首轮改动。置信度5/5（日志与代码）；真实 tiny 子集覆盖仍未测。

### B. 可靠性权重受目标插值熵影响——已确认的公式性质

现公式（`src/bpdd_loss.py:553` 起）：

`r = clamp((e_student − e_teacher − margin) / max(e_student, eps), 0, 1)`。

FGL 目标 t 为相邻两 bin 插值标签，`e_student = H(t) + KL(t || p_student)`。分子里的 H(t) 抵消，分母仍保留。因此相同 teacher/student 超额交叉熵差，会因 GT 落在 bin 边缘或中间而得到不同蒸馏强度。

合成数值验证：student KL=0.1、teacher KL=0.02、margin=0.02。

- t 为单 bin：H=0，r=0.600000。
- t 为相邻两 bin 各0.5：H=ln2，r=0.075648。

约7.93倍差异来自插值熵而非这里设定的 KL 改善。它不是数学实现错误，也不能直接说明低 r 全由此造成，但需要检查真实数据中的相关性，避免把低权重一律解释成教师不可靠。

候选改法：用改善幅度 `a=max(e_student−e_teacher−margin,0)` 构造有界权重 `r_new=a/(a+tau)`，tau>0，停止梯度。它去掉上述分母对目标熵的直接依赖；仍不保证几何质量，tau 也会改变整体预算。另一选项是超额交叉熵分母，但近完美学生会出现相对量不稳定，不推荐直接用 eps 硬顶。

裁决：值得独立验证，先测分箱熵/目标尺度与 r、梯度范数的关系，再固定 tau。置信度5/5（代数与数值），真实收益未测。

### C. 同为0.15不代表 BPDD/FGL 力度相同——已确认

FGL 每层按匹配框数归一化后对六层求和；BPDD 将五个源层的所有候选边整体平均，再乘 r 和0.15。

六层各M个匹配时，源边 BPDD 标量系数为 `0.15*r/(20M)`；同层 FGL 为 `0.15*w/M`。两者梯度函数不同，这不是梯度比。把 weight 机械乘20、除以平均 r 或除以活跃样本数，会同时放大稀疏噪声和坏方向。

此外，现有 `temperature=0.5` 控制未来教师的 softmin 混合，student/teacher 的分布 softmax 并未除以该温度。调这个字段不等于经典 KD 的软标签温度调整。

裁决：记录相同参数组上的分项梯度再定固定预算，首轮维持当前分母。置信度5/5（源码）。

### D. 更好的教师终点不保证 KL 更新改善定位——反例已重新通过

`tests/test_bpdd_joint_mechanism.py` 复现：teacher NLL 与 IoU 均更好，IoU gate 放行后，一个合成独立 logits 更新仍降低学生 IoU。

`∇z KL(q||p)=p−q`，而期望坐标梯度为 `∂mu/∂z_i=p_i(W_i−mu)`；这两个方向不由教师终点误差大小自动对齐。

裁决：单加更严格的 IoU 门控不是完整修复。先测真实样本中有害方向的频率、量级及其对主损失的影响。置信度5/5（构造反例）；真实频率未知。

### E. assignment 过滤未隔离累计残差历史——已确认的路径

FDR 使用 `z_l=sum(delta_z_k,k<=l)`。query 依次匹配 A/B/B 时，第2层向第3层学 B，蒸馏仍可通过累计加法直接更新第1层残差。

现有 `residual_gradient_only` 用 `stopgrad(z_l)+(r_l−stopgrad(r_l))`，`r_l=z_l−z_(l−1)`，维持 BPDD 前向值，取消直接历史加法路径。共享 Transformer 特征仍会间接受影响；也不能阻止浅层更新改变后续累计输出。

裁决：R-only 是第一项最清楚、容易归因的机制候选。它也可能减少有益深监督，不承诺涨点。置信度5/5（合成梯度回归）。

### F. 原 R+M+IoU 全开候选可能继续饿死监督——高优先级反对意见

当前 M 同时要求：assignment一致、NLL改善、GT在支持内、teacher均值更近、teacher与student在GT同侧、有效完整框IoU改善；最后还乘原小 r，使用相同大分母。

风险一：早期 source/teacher IoU均为0，即使坐标更接近GT也会被拒绝。

风险二：teacher轻微越过GT但误差更小，当前代码全部拒绝。对于独立 logits 的均值 Huber，局部方向条件是 `(mu_s−mu_gt)*(mu_s−mu_t)>0`，并不要求teacher必须与student在GT同侧。若担心有限步越界，可以将停止梯度教师均值投影到 `[min(mu_s,mu_gt),max(mu_s,mu_gt)]`，而不是一律丢弃；投影变成GT时又会增加直接监督成分。

风险三：期望损失的 Jacobian 在概率极度饱和时可能很小；数值稳定、方向正确不等于训练信号足够。

裁决：不直接部署全开版本。M需要与等预算直接GT期望损失比较，并测真实覆盖、饱和和梯度。置信度5/5（门控源码与代数）；覆盖损失大小未测。

### G. 当前记录无法验证“混合老师优于最终层”

consistent 分支返回的 `mixture_beats_final_ratio`、`mean_mixture_advantage_over_final` 是固定零占位值（`src/bpdd_loss.py:599`附近），runtime也未持久化真实比较。不能拿这些零宣称混合老师没有价值，或沿用历史 final 模式诊断器来宣布新版通过/失败。

既有 `run_bpdd_mature_signal_probe.py` 固定旧 checkpoint identity 和旧配置，并依赖这些字段。应适配当前语义后使用，不能原样执行后把结果解释为新版机制验证。

裁决：增加真实 final-only 同 assignment 教师对照；它有可能以更简单机制提供相同收益。置信度5/5（源码）。

## 4. 建议的重设计顺序与可证伪标准

### 第一步：固定训练集批次做诊断

使用独立加载的可用 checkpoint 副本，固定16–32个训练批次，覆盖有/无增强、密集与小目标场景。仅诊断，不写回正式checkpoint、不用验证集挑权重。没有保存的早期checkpoint不能假装已经评测。

逐层统计：候选数、各gate前后覆盖率、NLL差、GT标签熵、原始支持越界、teacher/student均值与IoU差、raw extent与floor、分布熵/期望Jacobian。normal matched、unmatched、DN分开。

分项测 BPDD/FGL/L1+GIoU 的梯度范数和cosine，参数组至少分 FDR私有头、decoder共享参数。离线一步测试在副本上进行，显式冻结/恢复BN buffers、RNG、匹配与优化器状态；这里真实优化器为MuSGD，不照搬旧文档的Adam分析。单纯logits微步与实际MuSGD更新分别记录。

检查 teacher 混合与 final-only 的真实几何质量；correctness样本通过不替代数据分布上的频率。

### 第二步：只测试能解释结果的单因素候选

| 候选 | 相对现有G的唯一主要改动 | 什么证据支持继续 | 什么结果反驳它 |
|---|---|---|---|
| R | residual_gradient_only=true，其余保持 | 跨匹配历史梯度干扰明显，真实更新方向改善 | 有益浅层学习被削弱，真实主损失/几何更差 |
| S | 改善幅度权重取代相对NLL权重 | 现有r对标签熵敏感、BPDD梯度小且方向多数正 | 提高梯度后坏方向或floor明显增加 |
| M（修订后） | 学几何期望方向，避免多重冗余gate | KL坏方向真实频率/量级不可忽略 | 主要退化成GT辅助回归，或Jacobian饱和导致近零梯度 |

R现有实现可用，S是本次设计提案，M修订尚未实现。不要把三项同时改完后只跑一个新100轮。

最小部署候选先用R：assignment_mode=consistent、weight=0.15、temperature=0.5、margin=0.02、distribution_objective=kl、decoded_iou_gate=false、residual_gradient_only=true。保留现有LRS与几何解码。它的优先级来自可隔离性，不是已经测得的成功率。

若进入M路线：保留同query/GT与共同参考，FGL监督分布形状；教师均值在学生与可表示GT之间做有限步目标约束。用正常的几何误差诊断评估，不把IoU=0当作全部无用。M具有降级为额外回归的实质风险，因此等预算GT-only辅助项是必要的简化对照。

### 第三步：解释与LRS的交互

| 几何固定 | AC-BPDD关闭 | 当前AC-BPDD开启 |
|---|---:|---:|
| LRS关闭 | 0.29361 | 未完成 |
| LRS开启 | 0.29620 | 0.29628 |

缺失的无LRS+AC-BPDD臂才可检验“LRS与BPDD收益重叠”。不能从三个已知角推导第四个角，也不能为了使增益数字更好看更换基座。

该2×2针对现有AC-BPDD版本；用改版结果填入缺角会同时改变BPDD版本，无法隔离LRS交互。先核对有效源码/初态/协议；能复用的既有对照不因改名或提交号不同而自动重跑。

### 第四步：决定是否保留

固定主指标为同协议best-val mAP50-95，后十轮平均与末轮为次指标，禁止事后互换。进入正式训练前约定最小实用增益；例如+0.1或+0.2 pp仅可作为项目预算阈值，不能当作统计显著性阈值。

短程训练只能排除崩溃、无梯度与明显坏方向，不能据早期AP宣布最终优胜；当前日志已经显示中期和末期差值可能换符号。通过诊断后只选一个候选完成既定100轮；若有稳定正向观察，再补关键seed或独立测试集验证。连续epoch不当作多seed。

若有效梯度已足够、方向多数合理、final-only/GT-only同样好，继续堆BPDD机制的收益依据不足。此时保留零/小增益结果，降低其论文主张强度即可。

## 5. 本次执行验证及来源

本地命令：`C:\uav_env\Scripts\python.exe -m pytest tests/test_bpdd_joint_mechanism.py tests/test_bpdd_iou_gate.py -q -p no:cacheprovider`。

本次输出：**31 passed in 34.57s**。范围是已有合成机制、候选构图/梯度与IoU门控测试；不代表新S/M方案实现或正式训练成功。分箱熵权重反例另以独立算术脚本复算。

相关代码（相对 `tmp-work/lrs-system-visdrone-rebuild/`）：

- `src/bpdd_loss.py`：教师混合、r、分母、R/M和占位统计。
- `src/fdr_loss.py`：每层FGL、LRS与归一化。
- `src/fdr_head.py`：累计logits与各层几何统计聚合。
- `src/fdr_math.py`：固定参考、非均匀支持和带代理梯度的extent floor。
- `src/lrs_runtime_evidence.py`：batch平均口径、缺失指标与全层统计范围。
- `docs/FDR_BPDD_JOINT_MECHANISM_AUDIT_ZH.md`：既有R/M候选和合成反例的历史审查。

外部原始来源只用于定位已有研究范围：

- [D-FINE 原论文](https://arxiv.org/abs/2410.13842)：FDR/GO-LSD已有定位自蒸馏设计。
- [Localization Distillation，CVPR 2022](https://openaccess.thecvf.com/content/CVPR2022/html/Zheng_Localization_Distillation_for_Dense_Object_Detection_CVPR_2022_paper.html)：定位知识蒸馏及选择性蒸馏区域已有研究。

因此“跨层蒸馏”“只蒸馏有价值目标”本身不足以主张新颖性；新的贡献应绑定具体处理规则及其对照效果。本次不据这些相关工作推断作者独立推导过程，也未进行穷尽新颖性检索。

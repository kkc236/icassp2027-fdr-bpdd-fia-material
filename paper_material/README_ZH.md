# ICASSP 2027 论文材料入口

> **当前整理版本：2026-09-15。** 论文主结果已收敛到 Ultralytics RT-DETR-L 的 `LRS-GFDR + Capacity-BPDD-v3-Safe + FIA` 联合 Formal100；官方 D-FINE 路线和 EQuAL standalone 作为外部/历史对照保留。当前联合 best E97 的 val mAP50–95 为 `0.30109`，最新 BPDD-only 已完成 E100（best E80=`0.29277`，独立 test 待评估）。旧路线、旧拓扑和跨 authority 算术差值均保留审计链，但不得混入严格增量。

本目录汇总面向 VisDrone 密集小目标的三层方法链：LRS-GFDR 负责架构保持型逐边分布定位，Capacity-BPDD-v3-Safe 负责训练期跨层定位蒸馏，FIA 负责 P3 高分辨率表征增强。材料按“问题—设计—证据”组织；val/test、方法代际、P3-only/cascading 以及 strict/non-paired 不得混写。

**全部实验总表**：见 [ALL_EXPERIMENTS_SUMMARY_20260915_ZH.md](results/ALL_EXPERIMENTS_SUMMARY_20260915_ZH.md)，机器可读索引见 [all_experiments_summary.json](results/all_experiments_summary.json)。该总表同时列出当前正式结果、严格配对、跨协议共同评估、失败/短跑路线和 UAVDT 分开结果，并为每行标注证据等级。

**最新三模块联合主记录**：`LRS-GFDR + Capacity-BPDD-v3-Safe + FIA` 已完成 VisDrone Formal100，best E97 的 mAP50–95 为 `0.30109`。它已替换旧的 `RT-DETR-L + FDR + BPDD + FIA` 作为当前联合结果；旧记录仍保留但标为历史，不得混入新联合的增量计算。入口见 [`当前联合证据包`](evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/README.md)。

## 阅读顺序

1. [论文结果统一汇总](results/RESULTS_ZH.md)
2. [val 主结果表](results/MAIN_TABLE_ZH.md)
3. [当前联合证据包](evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/README.md)
4. [LRS-GFDR 方法](methods/FDR_ZH.md)
5. [BPDD：渐进式分布蒸馏](methods/BPDD_ZH.md)
6. [FIA：高分辨率特征增强](methods/FIA_ZH.md)
7. [冻结实验协议](experiments/PROTOCOL_ZH.md)
8. [BPDD 严格配对补充实验](experiments/BPDD_STRICT_PAIR_PROTOCOL_ZH.md)
9. [FIA 消融实验入口](experiments/FIA_ABLATION_SCAFFOLD_ZH.md)
10. [FIA 证据状态](results/FIA_RESULTS_STATUS_ZH.md)
11. [val/test 涨点总对比](results/SPLIT_GAIN_COMPARISON_ZH.md)
12. [统一复杂度与实时性表](results/COMPLEXITY_ZH.md)
13. [VisDrone CCF A/B 会外部方法对比](results/EXTERNAL_VISDRONE_COMPARISON_ZH.md)
14. [历史 EQuAL standalone](methods/EQUAL_ZH.md)
15. [EQuAL Formal100 与 exact val/test](results/EQUAL_RESULTS_ZH.md)
16. [ICASSP 2027 写作提纲](writing/ICASSP2027_OUTLINE_ZH.md)
17. [创新定位、核心文案与对抗性审计](writing/NOVELTY_POSITIONING_AND_ADVERSARIAL_AUDIT_ZH.md)
18. [四图规划](figures/FIGURE_PLAN_ZH.md)

## 当前结果口径

- 当前三模块联合 Formal100 已完成 100 epochs，best E97 val 为 `P=0.60482、R=0.49693、AP50=0.49890、mAP=0.30109`；这是当前论文主系统。EQuAL standalone 的 exact val/test 只作为历史候选和外部定位参照。
- 最新 `LRS-GFDR + Capacity-BPDD-v3-Safe` BPDD-only Formal100 已完成 100 epochs，best E80 val mAP=`0.29277`，E100=`0.28939`；该记录的独立 test 尚待评估，不能替代严格配对 BPDD 证据。完整原始 CSV、args、权重 SHA 和边界说明见当前联合证据包。
- RT-DETR-L、FDR、FDR+BPDD 是正式核心行。新增同 authority、同 seed 的 FDR/FDR+BPDD 配对训练及 best.pt 统一 val/test 复评均已完成：BPDD 的 val/test mAP50–95 增益为 `+0.239/+0.283 pp`，AP75 增益为 `+0.072/+0.276 pp`。A–E 表的旧 C 行继续作为用户确认的 cross-authority 标准展示值；BPDD 的主要因果增益引用新严格配对表。
- A–E val 主表的 D 行已与统一结果页对齐：FDR+FIA 为 `P=0.57752、R=0.49089、AP50=0.48631、AP75=0.29972、mAP=0.29494`，相对 FDR 为 `+0.528 pp` 的非严格配对算术差，不再保留“待整理”占位。
- FIA-only 已切换到 fresh P3-only `best.pt`。冻结 evaluator 独立 val 为 `P=0.4871962209、R=0.4253173434、F1=0.4509443663、AP50=0.3987451873、AP75=0.2218076018、mAP=0.2270563951`；相对 canonical baseline `0.21911` 为 `+0.7946 pp` 的同 split 算术差。
- 同一 FIA-only checkpoint 的独立 test 为 `P=0.4482592210、R=0.3776360333、F1=0.3954178960、AP50=0.3366417705、AP75=0.1820114030、mAP=0.1855174641`；相对 protocol-comparable canonical test baseline `0.1774164317` 为 `+0.8101 pp`。该值只作 test 内算术比较，不从 val/test 之间推导涨点。
- fresh FIA-only 图为正确 P3-only：FIA 层 22 的 `f=-1` 读取上一层 21，层 23 显式 `f=21`，decoder 输入为 `[22,25,28]`。checkpoint SHA-256 为 `c00cae89aaeb722854f8c845d14507c3598f75d509c2b12a3222b35a004157a6`，源码 SHA 为 `118ad631eff93ad806f85ea47819578e6e00bfc5`。旧 FIA-only cascading（层 23 `f=-1`）结果已被取代，仅可作历史记录。
- FDR+FIA 仍采用既有发布版 cascading `best.pt`：val/test mAP50–95 为 `0.2949403207/0.2346453866`，相对 FDR 的 val/test 算术差为 `+0.5280/+0.6644 pp`；不得把该 checkpoint 标成 P3-only。
- 旧 FDR+BPDD+FIA 三模块文本记录（val `0.2961`、test `0.2337`）已被新的 LRS-GFDR + Capacity-BPDD-v3-Safe + FIA 联合 Formal100 结果替换为当前主记录；原文本和截图仅保留作 `superseded_history`，不再作为当前联合指标。
- 统一复杂度与实时性已完成：在同一 RTX 4090、640、batch=1、FP32 端到端协议下，Baseline/FDR/FDR+BPDD/三模块分别为 `28.85/25.73/25.77/25.21 FPS`。严格配对 FDR 与 FDR+BPDD 的 Params/FLOPs/峰值显存完全一致；FIA 仅增加 `0.861 ms` 中位延迟与 `0.301 M` 参数。
- 外部 VisDrone 正式表收录 CCF A/B 类会议 full/regular paper，并标明会议等级与相对本文的绝对 mAP 位置。当前覆盖 AAAI、CVPR、ICCV、IJCAI、ICASSP、ICRA、ICME、IROS；同 split 的结果分成“不高于本文/高于本文”，split 或 input 未报告的结果单列为不可排序。IJCAI 2025 RAFDE 已作为 640 近邻上界登记；ICASSP 2026 ResBiDet 的正式摘要 AP50 和 VARDet 的 1333×800 结果作为带边界的同会参照。期刊、预印本与来源不明结果不进入正式表。

## 机器可读材料

- [EQuAL 机器汇总](results/equal_results.json)
- [EQuAL 私密 Release（best/last、日志、authority、exact val/test）](https://github.com/kkc236/icassp2027-fdr-bpdd-fia-material/releases/tag/equal-seed0-formal100-20260821)
- [EQuAL val exact JSON](evidence/equal_formal100_20260821/equal_val.json)
- [EQuAL test exact JSON](evidence/equal_formal100_20260821/equal_test.json)
- [EQuAL val/test 逐类 CSV](results/equal_class_results.csv)
- [正式 val 主结果](results/main_results.json)
- [最新 BPDD-only Formal100 完成摘要](evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/bpdd-current-completion.json)
- [最新 BPDD-only 逐 epoch 曲线](evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/bpdd-current-results.csv)
- [D-FINE-L 最近一次失败状态快照](evidence/visdrone_dfine_l_external_20260913/queued-run-status-20260914.json)
- [BPDD 严格配对实验合同](experiments/BPDD_STRICT_PAIR_PROTOCOL_ZH.md)
- [统一复杂度与实时性说明](results/COMPLEXITY_ZH.md)
- [统一复杂度机器合同](results/complexity_results.json)
- [统一复杂度原始 1,500 个延迟样本](evidence/unified_complexity_20260820/unified_complexity_raw.json)
- [组合状态与总体结果](results/split_gain_comparison.json)
- [val/test 总体 CSV](results/split_overall_results.csv)
- [尺度 CSV](results/split_scale_results.csv)
- [类别 CSV](results/split_class_results.csv)
- [FIA standalone val CSV（按 checkpoint SHA 核对；旧 FIA-only 行仅为历史）](results/fia_existing_best_val_results.csv)
- [FIA standalone test CSV（按 checkpoint SHA 核对；旧 FIA-only 行仅为历史）](results/fia_existing_best_test_results.csv)
- [FIA best.pt 机器证据（按 checkpoint SHA 核对；旧 FIA-only 记录已被 fresh P3-only 结果取代）](evidence/fia_existing_best_evaluation.json)
- [三模块 val 四位小数原始文本](evidence/fdr_bpdd_fia_val.txt)
- [三模块 test 四位小数原始文本](evidence/fdr_bpdd_fia_test.txt)
- [三模块 val/test 总体与逐类 CSV](results/fdr_bpdd_fia_text_report_class_results.csv)
- [外部 VisDrone 对比说明](results/EXTERNAL_VISDRONE_COMPARISON_ZH.md)
- [外部 VisDrone 对比 JSON](results/external_visdrone_comparison.json)
- [外部 VisDrone 对比 CSV](results/external_visdrone_comparison.csv)
- [FIA 状态机](evidence/fia_results_status.json)
- [来源清单](evidence/source_manifest.json)

## 方法依赖

- **逐边定位不确定性 → LRS-GFDR（AP-FDR 代际）**：当前主系统沿用 `LRS-GFDR` 命名。它面向 stock RT-DETR-L 提出架构保持型 localization path、stock-head-informed preliminary geometry、normal/DN 匹配一致监督、几何可行域修复与 LRS-FGL（alpha=0.25）。其边界分布基础构件受 D-FINE 启发并按固定版本归因，但 D-FINE 的完整 detector、LQE、DDF 与 GO-LSD 不属于本文实现。
- **早期层定位监督不足 → Capacity-BPDD-v3-Safe**：BPDD 是由本文独立提出并实现的原创算法。D-FINE/GO-LSD 只启发“跨层定位知识能否改善早期层”这一研究问题；BPDD 的 future-layer softmin 教师、better-only 可靠性门控、stock assignment 复用、localization-only、warmup/decay 和训练期边界均由本文独立设计。它消费 LRS-GFDR 的逐边分布，只在训练期工作且不增加推理分支；严格 FDR/FDR+BPDD 配对结果与最新 v3-safe 训练记录共同构成证据，BPDD-only 不作为独立推理模型行。
- **P3 小目标表征不足 → FIA**：FIA 以 P3-only 拓扑增强高分辨率特征，同时保持 P4/P5 从原分支构建。fresh P3-only FIA-only 在 canonical val baseline 上获得 `+0.7946 pp` 的非严格配对算术增益；FDR+FIA 与三模块结果继续作为不同拓扑、不同证据等级的兼容性观察，复杂度表登记其有限推理代价。

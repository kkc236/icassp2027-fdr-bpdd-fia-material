# ICASSP 2027 论文材料入口

本目录汇总 RT-DETR-L、FDR、BPDD 与 FIA 在 VisDrone 上的方法、协议、结果和证据边界。核心结果与补充消融分开呈现；val/test、P3-only/cascading 以及 strict/non-paired 不得混写。

## 阅读顺序

1. [AP-FDR：架构保持型细粒度分布细化](methods/FDR_ZH.md)
2. [BPDD：渐进式分布蒸馏](methods/BPDD_ZH.md)
3. [FIA：高分辨率特征增强](methods/FIA_ZH.md)
4. [冻结实验协议](experiments/PROTOCOL_ZH.md)
5. [BPDD 严格配对补充实验](experiments/BPDD_STRICT_PAIR_PROTOCOL_ZH.md)
6. [AP-FDR 内部双消融协议](experiments/AP_FDR_INTERNAL_ABLATION_PROTOCOL_ZH.md)
7. [FIA 消融实验入口](experiments/FIA_ABLATION_SCAFFOLD_ZH.md)
8. [论文结果统一汇总](results/RESULTS_ZH.md)
9. [FIA best.pt 结果](results/FIA_ABLATION_RELEASE_RESULTS_ZH.md)
10. [FIA 证据状态](results/FIA_RESULTS_STATUS_ZH.md)
11. [val 主结果表](results/MAIN_TABLE_ZH.md)
12. [val/test 涨点总对比](results/SPLIT_GAIN_COMPARISON_ZH.md)
13. [统一复杂度与实时性表](results/COMPLEXITY_ZH.md)
14. [VisDrone CCF A/B 会外部方法对比](results/EXTERNAL_VISDRONE_COMPARISON_ZH.md)
15. [ICASSP 2027 写作提纲](writing/ICASSP2027_OUTLINE_ZH.md)
16. [创新定位、核心文案与对抗性审计](writing/NOVELTY_POSITIONING_AND_ADVERSARIAL_AUDIT_ZH.md)
17. [四图规划](figures/FIGURE_PLAN_ZH.md)

## 当前结果口径

- RT-DETR-L、FDR、FDR+BPDD 是正式核心行。新增同 authority、同 seed 的 FDR/FDR+BPDD 配对训练及 best.pt 统一 val/test 复评均已完成：BPDD 的 val/test mAP50–95 增益为 `+0.239/+0.283 pp`，AP75 增益为 `+0.072/+0.276 pp`。A–E 表的旧 C 行继续作为用户确认的 cross-authority 标准展示值；BPDD 的主要因果增益引用新严格配对表。
- A–E val 主表的 D 行已与统一结果页对齐：FDR+FIA 为 `P=0.57752、R=0.49089、AP50=0.48631、AP75=0.29972、mAP=0.29494`，相对 FDR 为 `+0.528 pp` 的非严格配对算术差，不再保留“待整理”占位。
- FIA-only 已切换到 fresh P3-only `best.pt`。冻结 evaluator 独立 val 为 `P=0.4871962209、R=0.4253173434、F1=0.4509443663、AP50=0.3987451873、AP75=0.2218076018、mAP=0.2270563951`；相对 canonical baseline `0.21911` 为 `+0.7946 pp` 的同 split 算术差。
- 同一 FIA-only checkpoint 的独立 test 为 `P=0.4482592210、R=0.3776360333、F1=0.3954178960、AP50=0.3366417705、AP75=0.1820114030、mAP=0.1855174641`；相对 protocol-comparable canonical test baseline `0.1774164317` 为 `+0.8101 pp`。该值只作 test 内算术比较，不从 val/test 之间推导涨点。
- fresh FIA-only 图为正确 P3-only：FIA 层 22 的 `f=-1` 读取上一层 21，层 23 显式 `f=21`，decoder 输入为 `[22,25,28]`。checkpoint SHA-256 为 `c00cae89aaeb722854f8c845d14507c3598f75d509c2b12a3222b35a004157a6`，源码 SHA 为 `118ad631eff93ad806f85ea47819578e6e00bfc5`。旧 FIA-only cascading（层 23 `f=-1`）结果已被取代，仅可作历史记录。
- FDR+FIA 仍采用既有发布版 cascading `best.pt`：val/test mAP50–95 为 `0.2949403207/0.2346453866`，相对 FDR 的 val/test 算术差为 `+0.5280/+0.6644 pp`；不得把该 checkpoint 标成 P3-only。
- FDR+BPDD+FIA 已补入与终端截图对应的四位小数文本记录。val 为 `P=0.5693、R=0.4991、F1=0.5285、AP50=0.4898、AP75=0.3042、mAP=0.2961`（相对 BPDD `+0.384 pp`）；test 为 `P=0.5189、R=0.4361、F1=0.4634、AP50=0.4081、AP75=0.2327、mAP=0.2337`（`+0.204 pp`）。checkpoint `0.29618` 与终端截图作为互证。
- 统一复杂度与实时性已完成：在同一 RTX 4090、640、batch=1、FP32 端到端协议下，Baseline/FDR/FDR+BPDD/三模块分别为 `28.85/25.73/25.77/25.21 FPS`。严格配对 FDR 与 FDR+BPDD 的 Params/FLOPs/峰值显存完全一致；FIA 仅增加 `0.861 ms` 中位延迟与 `0.301 M` 参数。
- 外部 VisDrone 正式表收录 CCF A/B 类会议 full/regular paper，并标明会议等级与相对本文的绝对 mAP 位置。当前覆盖 AAAI、CVPR、ICCV、IJCAI、ICASSP、ICRA、ICME、IROS；同 split 的结果分成“不高于本文/高于本文”，split 或 input 未报告的结果单列为不可排序。IJCAI 2025 RAFDE 已作为 640 近邻上界登记；ICASSP 2026 ResBiDet 的正式摘要 AP50 和 VARDet 的 1333×800 结果作为带边界的同会参照。期刊、预印本与来源不明结果不进入正式表。

## 机器可读材料

- [正式 val 主结果](results/main_results.json)
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

- AP-FDR（结果表中沿用 FDR）是本文第一项方法创新：受 D-FINE 启发，我们没有复现其完整检测器，而是在 Ultralytics RT-DETR-L 中独立重构 localization path，提出 localization-only 的架构保持改造、stock-head-informed preliminary 分支、normal/DN 匹配一致监督和公平初始化合同。
- BPDD 是由本文独立提出并实现的原创算法，也是论文的第二项方法创新。D-FINE/GO-LSD 只启发了“跨层定位知识能否改善早期层”这一研究问题；BPDD 的未来层 softmin 教师、better-only 可靠性门控、stock assignment 复用和训练期边界均由本文独立设计。它消费 AP-FDR 的逐边分布，只在训练期工作且不增加推理分支；BPDD-only 不是合法模型行。
- FIA 是面向高分辨率小目标表征的推理期增强模块。fresh P3-only FIA-only 在 canonical val baseline 上获得 `+0.7946 pp` 的非严格配对算术增益；FDR+FIA 与三模块结果继续作为不同拓扑、不同证据等级的兼容性观察。
- AP-FDR 参考固定版本 D-FINE 的离散边界表示、FGL、Integral 与非均匀投影公式。本文不主张首次发明这些基础算子，原创主张落在上述 RT-DETR 专用结构、监督合同与公平实验设计；BPDD 的具体算法构造和实现则作为本文独立原创贡献。

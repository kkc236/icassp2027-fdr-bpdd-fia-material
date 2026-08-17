# ICASSP 2027 论文材料入口

本目录汇总 RT-DETR-L、FDR、BPDD 与 FIA 在 VisDrone 上的方法、协议、结果和证据边界。核心结果与补充消融分开呈现；val/test、P3-only/cascading 以及 strict/non-paired 不得混写。

## 阅读顺序

1. [FDR：细粒度分布细化](methods/FDR_ZH.md)
2. [BPDD：渐进式分布蒸馏](methods/BPDD_ZH.md)
3. [FIA：高分辨率特征增强](methods/FIA_ZH.md)
4. [冻结实验协议](experiments/PROTOCOL_ZH.md)
5. [FIA 消融实验入口](experiments/FIA_ABLATION_SCAFFOLD_ZH.md)
6. [论文结果统一汇总](results/RESULTS_ZH.md)
7. [FIA 发布版 best.pt 结果](results/FIA_ABLATION_RELEASE_RESULTS_ZH.md)
8. [FIA 证据状态](results/FIA_RESULTS_STATUS_ZH.md)
9. [val 主结果表](results/MAIN_TABLE_ZH.md)
10. [val/test 涨点总对比](results/SPLIT_GAIN_COMPARISON_ZH.md)
11. [ICASSP 2027 写作提纲](writing/ICASSP2027_OUTLINE_ZH.md)
12. [四图规划](figures/FIGURE_PLAN_ZH.md)

## 当前结果口径

- RT-DETR-L、FDR、FDR+BPDD 是正式核心行。FDR 相对 baseline 可作严格差值；BPDD 行是跨 authority 精确绝对值，算术差不是严格配对因果增益。
- FIA-only 与 FDR+FIA 按当前决策直接采用 Release 中各自的 `best.pt`，不再重训。冻结 evaluator 独立 val 的 mAP50–95 分别为 `0.2167954534` 与 `0.2949403207`；独立 test 的 mAP50–95 分别为 `0.1771764568` 与 `0.2346453866`。
- FIA-only 相对 baseline 为 `−0.2315 pp`；FDR+FIA 相对 FDR 为 `+0.5280 pp`。两者是非严格配对算术差。
- 两个 standalone checkpoint 均为 published cascading topology（`model[23].f=-1`），不能称为 P3-only。
- 两个 standalone `best.pt` 均已在 VisDrone test（1,610 images / 75,102 instances）完成 exact 独立复评；FIA-only / FDR+FIA 的 AP75 分别为 `0.1716130742` / `0.2358787301`。val 与 test 结果分别报告；对既有对照的任何 test 算术差也不是 strict paired 因果增益。
- FDR+BPDD+FIA 的论文 A–E 主表直接绑定终端 val 面板：`P≈0.569、R≈0.499、AP50≈0.490、mAP≈0.296、约 +0.37 pp`。checkpoint 内的 `0.29618/+0.3922 pp` 作为独立补充正向记录；同一终端证据的 test 为 `≈0.234`（`≈+0.234 pp`）。

## 机器可读材料

- [正式 val 主结果](results/main_results.json)
- [组合状态与总体结果](results/split_gain_comparison.json)
- [val/test 总体 CSV](results/split_overall_results.csv)
- [尺度 CSV](results/split_scale_results.csv)
- [类别 CSV](results/split_class_results.csv)
- [FIA standalone exact val CSV](results/fia_existing_best_val_results.csv)
- [FIA standalone exact test CSV（总体 + 逐类）](results/fia_existing_best_test_results.csv)
- [FIA best.pt 完整证据](evidence/fia_existing_best_evaluation.json)
- [FIA 状态机](evidence/fia_results_status.json)
- [来源清单](evidence/source_manifest.json)

## 方法依赖

- FDR 是定位分布表示基础。
- BPDD 消费 FDR 的逐边分布，只在训练期工作；BPDD-only 不是合法模型行。
- FIA 是推理期高分辨率特征模块。当前证据说明 FIA 与 FDR 组合具有正向兼容性，但 FIA-only 并未显示稳定增益。
- FDR/FGL/Integral 及非均匀积分来自固定版本 D-FINE 先验；本文主张的是面向 Ultralytics RT-DETR-L 与 VisDrone 的适配、组合和验证。

# ICASSP 2027 论文材料入口

> **当前路线已于 2026-08-28 由作者固定。** 论文回到 Ultralytics RT-DETR-L /
> VisDrone 主线，第一项完整定位模块为 **LRS-FDR**，其基础内部消融为
> **NA-FDR**。官方 D-FINE-S 重跑、EQuAL、AP-FDR 和 DCF-FDR 均保留为历史审计
> 材料，不再作为当前投稿方法。

当前论文问题链固定为：

```text
边界分布定位
  -> NA-FDR 原生 reference / assignment / normal-query 对齐
  -> LRS-FDR 浅层可靠性收缩
  -> BPDD 跨层分布监督
  -> FIA 高分辨率 P3 表征
```

其中 LRS-FDR 的 standalone Formal100 与三臂统一复评已经完成；LRS-FDR 与
BPDD/FIA 的最终组合尚未按新 FDR 身份重训，因此旧 AP-FDR 组合只作兼容性和历史
证据，不直接改名。

最终源码已发布并冻结：仓库
`https://github.com/kkc236/uav-detection-baselines`，branch
`codex/lrs-system-visdrone-rebuild`，tag `visdrone-lrs-system-v1`，commit
`445120b7337dad0ccc41d18ad081b6b33580dcd2`。组合运行入口为
`scripts/train_visdrone_lrs_system.py`；中文 runbook 为
[`VISDRONE_LRS_SYSTEM_RUNBOOK_ZH.md`](https://github.com/kkc236/uav-detection-baselines/blob/visdrone-lrs-system-v1/docs/VISDRONE_LRS_SYSTEM_RUNBOOK_ZH.md)。
Source-focused verification suites 已通过；这不等同于 G/H/I 的 Formal100 结果。

## 当前阅读顺序

1. [当前重跑与证据状态](CURRENT_RERUN_STATUS_ZH.md)
2. [LRS-FDR：NA-FDR 原生对齐与分层可靠性收缩](methods/FDR_ZH.md)
3. [NA-FDR / LRS-FDR Formal100 结果](results/LRS_FDR_RESULTS_ZH.md)
4. [LRS-FDR 三臂机器证据](evidence/lrs_fdr_formal100_20260828/README.md)
5. [BPDD：渐进式分布蒸馏](methods/BPDD_ZH.md)
6. [FIA：高分辨率特征增强](methods/FIA_ZH.md)
7. [论文写作提纲](writing/ICASSP2027_OUTLINE_ZH.md)
8. [创新定位与对抗性审计](writing/NOVELTY_POSITIONING_AND_ADVERSARIAL_AUDIT_ZH.md)
9. [图表规划](figures/FIGURE_PLAN_ZH.md)
10. [冻结实验协议](experiments/PROTOCOL_ZH.md)
11. [VisDrone 最终组合实验交接](experiments/VISDRONE_FINAL_EXPERIMENT_HANDOFF_ZH.md)
12. [统一复杂度与实时性历史表](results/COMPLEXITY_ZH.md)
13. [VisDrone 外部会议方法对比](results/EXTERNAL_VISDRONE_COMPARISON_ZH.md)

## 当前 FDR 结果口径

三个方法均在各自训练日志中独立选择 best checkpoint，再使用同一冻结评估器在
VisDrone val 上复评：

| 方法 | P | R | F1 | AP50 | AP75 | mAP50-95 |
|---|---:|---:|---:|---:|---:|---:|
| Original FDR | 0.570249 | 0.491417 | 0.527907 | 0.484700 | 0.294070 | 0.290698 |
| NA-FDR | **0.587045** | 0.498339 | **0.539067** | **0.493119** | 0.301061 | 0.296855 |
| LRS-FDR | 0.579512 | **0.500606** | 0.537177 | 0.491805 | **0.305773** | **0.296968** |

分层归因固定为：

- **NA-FDR − Original FDR**：mAP `+0.616 pp`、AP75 `+0.699 pp`、Recall
  `+0.692 pp`；
- **LRS-FDR − NA-FDR**：mAP `+0.011 pp`、AP75 `+0.471 pp`、Recall
  `+0.227 pp`，同时 Precision `-0.753 pp`、AP50 `-0.131 pp`；
- **LRS-FDR − Original FDR**：mAP `+0.627 pp`、AP75 `+1.170 pp`、Recall
  `+0.919 pp`。

NA-FDR 是有独立正向证据的基础设计；历史运行标识 “Clean FDR” 不再作为论文
名称，只用于证据文件映射。LRS-FGL 的直接内部贡献是 AP75/Recall
取向，不能把最终相对 Original FDR 的全部收益都归给 LRS。

## 方法身份与证据状态

| 模块/路线 | 当前身份 | 证据状态 | 论文用途 |
|---|---|---|---|
| NA-FDR | LRS-FDR 的原生对齐基础 | Formal100 + 独立总体/类别/尺度复评完成 | 第一创新的基础设计与 `w/o LRS` |
| LRS-FDR | 最终完整 FDR 模块 | Formal100 + Gate0 + 独立复评完成 | 第一创新主方法 |
| BPDD | 训练期跨层分布蒸馏 | 旧 AP-FDR 上严格配对完成 | 第二创新机制证据；新组合待重训 |
| FIA | P3-only 特征增强 | standalone 与旧组合证据存在 | 第三创新机制证据；新组合待重训 |
| EQuAL | 放弃的边缘自适应路线 | standalone 历史结果完整 | 仅历史审计 |
| DCF-FDR | 放弃的反馈路线 | Formal100 为负 | 仅失败证据 |
| 官方 D-FINE-S 重跑 | 放弃的替代 detector 路线 | 保留原始运行材料 | 仅历史审计 |

## 当前主张边界

可以写：

- NA-FDR 通过原生 reference、原生 assignment 与 normal matched-query 分布监督
  的统一对齐，相对 Original FDR 在所有总体指标上为正；
- LRS-FDR 对浅层可表示匹配执行同图像、同层、总权重守恒的可靠性收缩；
- LRS-FDR 相对 Original FDR 的总体 P/R/AP50/AP75/mAP 均为正；
- LRS 相对 NA-FDR 提高 AP75 和 Recall，同时总体 mAP 数值非负。

不能写：

- LRS-FGL 显著或全面提高 mAP；
- LRS-FDR 在所有尺度、所有类别上提升；
- 当前单 seed 结果证明统计稳定性；
- 当前 VisDrone 结果证明跨数据集泛化；
- 旧 AP-FDR+BPDD/FIA checkpoint 就是 LRS-FDR 的组合结果。

## 下一实验矩阵

主数据集 VisDrone 已承担 Original FDR / NA-FDR / LRS-FDR 的内部归因。第二数据集
正式名称为 **UAVDT**，只冻结两个同域、协议匹配的臂：

1. **Baseline**（作者已确认完成；artifact identity 与 metrics 仍待既有 authority 绑定）；
2. **Full**（Baseline + 完整投稿方法，尚未完成，不填数）。

UAVDT 不运行 NA-FDR、LRS-only、G/H 或其他模块级消融。Baseline-vs-Full 仅支持第二
数据集 effectiveness / multi-dataset applicability 的描述性判断，不支持 zero-shot
transfer 或 module-level attribution；单 seed 结果仍为 descriptive。annotation conversion、
split 与 protocol matching 必须在 UAVDT authority 中单独记录，不能借用 VisDrone 结果。

## 当前机器材料

- [FDR 三组统一 comparison JSON](evidence/lrs_fdr_formal100_20260828/independent-evaluation/comparison.json)
- [LRS-FDR 训练 authority](evidence/lrs_fdr_formal100_20260828/authority/lrs_fdr_authority.json)
- [LRS-FGL Gate0](evidence/lrs_fdr_formal100_20260828/authority/lrs_fdr_gate0.json)
- [证据 SHA-256 清单](evidence/lrs_fdr_formal100_20260828/MANIFEST.sha256)
- [NA-FDR / LRS-FDR 冻结设计](../docs/superpowers/specs/2026-08-28-lrs-fdr-material-freeze-design.md)
- [BPDD 严格配对实验合同](experiments/BPDD_STRICT_PAIR_PROTOCOL_ZH.md)
- [FIA standalone 机器证据](evidence/fia_existing_best_evaluation.json)
- [外部 VisDrone 对比 JSON](results/external_visdrone_comparison.json)
- [外部 VisDrone 对比 CSV](results/external_visdrone_comparison.csv)
- [来源清单](evidence/source_manifest.json)

## 历史材料入口

以下文件保持原始身份，不作为当前路线：

- [EQuAL 方法](methods/EQUAL_ZH.md)、[EQuAL 结果](results/EQUAL_RESULTS_ZH.md)与
  [EQuAL 机器结果](results/equal_results.json)；
- [AP-FDR 内部双消融旧协议](experiments/AP_FDR_INTERNAL_ABLATION_PROTOCOL_ZH.md)；
- [旧组合结果汇总](results/RESULTS_ZH.md)与[旧 val 主表](results/MAIN_TABLE_ZH.md)；
- [旧模块拆分对比](results/SPLIT_GAIN_COMPARISON_ZH.md)、
  [机器摘要](results/split_gain_comparison.json)、
  [总体 CSV](results/split_overall_results.csv)、
  [尺度 CSV](results/split_scale_results.csv)与
  [类别 CSV](results/split_class_results.csv)；
- [FIA 消融脚手架](experiments/FIA_ABLATION_SCAFFOLD_ZH.md)、
  [发布结果](results/FIA_ABLATION_RELEASE_RESULTS_ZH.md)、
  [状态页](results/FIA_RESULTS_STATUS_ZH.md)、
  [状态 JSON](evidence/fia_results_status.json)、
  [existing-best 评估](evidence/fia_existing_best_evaluation.json)、
  [val CSV](results/fia_existing_best_val_results.csv)与
  [test CSV](results/fia_existing_best_test_results.csv)；
- [旧三模块 val 文本](evidence/fdr_bpdd_fia_val.txt)、
  [test 文本](evidence/fdr_bpdd_fia_test.txt)与
  [类别 CSV](results/fdr_bpdd_fia_text_report_class_results.csv)；
- `paper_material/evidence/dfine_s_equal_fia_matched_20260823/` 下的 D-FINE-S
  切换实验；
- `experiments/clean-dcf-fdr-formal100-seed0-20260824/` 下的 DCF-FDR 失败记录。

保留历史不等于继续采用；Git 历史、原始数值、checkpoint 哈希和运行别名不得被
新方法名覆盖。

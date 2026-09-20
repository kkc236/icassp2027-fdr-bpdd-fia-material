# 当前论文主张与证据对应表

归档对象：`01_manuscript` 中的 CVM 稿，13 页、6 张实际渲染表、4 幅图、11 个公式。本文从当前目录出发链接归档文件；机器可读完整数值见 [claim_evidence.json](claim_evidence.json)。

## 使用规则

- **原件优先。** 数值以指定原始报告/CSV为准；编译检查和历史转录不替代原始实验报告。
- **保持评价器边界。** Native 与 common evaluator 分面独立比较。Table 1 当前 Native Full 是 **23.604**，不是另一个历史复评快照的 23.602。
- **当前时间指标只用 batch 8。** 旧 `efficiency/v3` 可追溯参数和初始化，但其 batch 1 时间不进入当前表。每图摊销时间不等于单张请求响应延迟。
- **保留身份边界。** UAVDT Full 为作者确认；不能写成 checkpoint 已独立核验，附带旧源码的冲突也不能删除。
- **保留历史对照边界。** G+B/Full 为最直接匹配的 FIA-off/on 对照；其他历史行不全具备同等匹配条件。Baseline 21.911 的原件明确是历史独立验证报告，不能改称已核验训练 CSV 峰值。
- **索引不创造实验。** 历史几何 runtime 未取回、原始预测/权重是否物理归档等状态，应和已保存报告分开。失效旧绝对路径仅保留出处，本页链接指向现有归档路径。

## 六表四图导航

| 当前编号 | 内容 | 证据条目 |
|---|---|---|
| 表 1 | VisDrone 完整检测器比较 | table1 |
| 表 2 | UAVDT 本地转换标签验证 | table2 |
| 表 3 | 完整 FDR/FGL 移植与定位设计变体 | table3 |
| 表 4 | 五臂验证精度、参数、计算量与 batch 8 吞吐量 | table4 |
| 表 5 | 八组共同评价器敏感性 | table5 |
| 表 6 | 文献报告上下文 | table6 |
| 图 1 | 参数–AP–GFLOPs 气泡图 | figure1 |
| 图 2 | 当前方法整合架构 | figure2 |
| 图 3 | 全十类共同评价器 AP | figure3 |
| 图 4 | 标注尺度分布与解析 IoU 动机 | figure4 |

注意：归档内保留的 `table_native.tex`、`table_external.tex`、`table_mechanism.tex` 等旧文件不额外计为当前渲染表。以 `build.py` 和正文实际插入关系为准。

## table1 — Table 1 / tab:system / source/table_system.tex

VisDrone完整检测器比较；native与common evaluator分面独立比较。

**关键记录：** Native AP：17.743 → 23.604（+5.861 pp）；共同评价器 final test：22.554 → 24.133（未舍入差值 +1.5791397734 pp）。高精度值在 JSON 及原报告中。

**证据文件：**

- [01_manuscript/source/table_system.tex](../01_manuscript/source/table_system.tex)
- [02_evidence/reevaluation_completion_20260915/baseline_best_800_20260915/files/test/imgsz640/summary.json](../02_evidence/reevaluation_completion_20260915/baseline_best_800_20260915/files/test/imgsz640/summary.json)
- [02_evidence/reevaluation_completion_20260915/baseline_best_800_20260915/files/test/imgsz640/BEST_EPOCH_IDENTITY.json](../02_evidence/reevaluation_completion_20260915/baseline_best_800_20260915/files/test/imgsz640/BEST_EPOCH_IDENTITY.json)
- [02_evidence/reevaluation_completion_20260915/baseline_best_800_20260915/comparisons/FULL_CAPACITY_B_F/test/imgsz640/summary.json](../02_evidence/reevaluation_completion_20260915/baseline_best_800_20260915/comparisons/FULL_CAPACITY_B_F/test/imgsz640/summary.json)
- [02_evidence/reevaluation_completion_20260915/baseline_best_800_20260915/MANIFEST.json](../02_evidence/reevaluation_completion_20260915/baseline_best_800_20260915/MANIFEST.json)
- [01_manuscript/inputs/external_sensitivity/dfine_final_test.cap300.json](../01_manuscript/inputs/external_sensitivity/dfine_final_test.cap300.json)
- [01_manuscript/inputs/external_sensitivity/joint_final_test.cap300.json](../01_manuscript/inputs/external_sensitivity/joint_final_test.cap300.json)
- [01_manuscript/inputs/external_sensitivity/dfine_best_test.cap300.json](../01_manuscript/inputs/external_sensitivity/dfine_best_test.cap300.json)
- [01_manuscript/inputs/external_sensitivity/joint_best_test.cap300.json](../01_manuscript/inputs/external_sensitivity/joint_best_test.cap300.json)
- [01_manuscript/inputs/external_sensitivity/cross-protocol-manifest.json](../01_manuscript/inputs/external_sensitivity/cross-protocol-manifest.json)

**解释边界：**

- Native Full精确源为0.23604003874539384（23.604）；另一NATIVE_TEST_RERUN历史快照23.602不是本表来源。
- 仅在各分面内比较；D-FINE-L为scratch-adapted reproduction，训练配方及有效batch不同。
- 原始common-evaluator预测JSONL未由本条证明已在本地归档；报告/哈希与完整预测资产应区分。

## table2 — Table 2 / tab:uavdt / source/table_uavdt.tex

UAVDT本地转换标签validation上，作者确认的Full相对Baseline的导出指标。

**关键记录：** AP 14.12 → 16.96；AP50 24.21 → 29.16；AP75 14.97 → 17.50。三类 car/truck/bus 完整列出。

**证据文件：**

- [01_manuscript/source/table_uavdt.tex](../01_manuscript/source/table_uavdt.tex)
- [01_manuscript/inputs/uavdt/baseline-exp/paper_data.txt](../01_manuscript/inputs/uavdt/baseline-exp/paper_data.txt)
- [01_manuscript/inputs/uavdt/exp/paper_data.txt](../01_manuscript/inputs/uavdt/exp/paper_data.txt)
- [01_manuscript/inputs/uavdt/metrics_review.json](../01_manuscript/inputs/uavdt/metrics_review.json)
- [01_manuscript/inputs/uavdt/author_confirmation.json](../01_manuscript/inputs/uavdt/author_confirmation.json)
- [01_manuscript/inputs/uavdt/inventory.json](../01_manuscript/inputs/uavdt/inventory.json)
- [01_manuscript/inputs/uavdt/previous_export_comparison.json](../01_manuscript/inputs/uavdt/previous_export_comparison.json)
- [01_manuscript/inputs/uavdt/configs/UAVDT.yaml](../01_manuscript/inputs/uavdt/configs/UAVDT.yaml)
- [01_manuscript/inputs/uavdt/src](../01_manuscript/inputs/uavdt/src)
- [01_manuscript/inputs/uavdt/RESULT_REVIEW_ZH.md](../01_manuscript/inputs/uavdt/RESULT_REVIEW_ZH.md)

**解释边界：**

- 作者确认Full身份不等于checkpoint独立核验；不得改写为checkpoint_verified=true。
- 导出包附带的旧源码与当前VisDrone Full源码不一致，须保留冲突记录。
- 官方benchmark split映射及完成训练的确切配方未独立闭合；这是本地转换标签validation结果。

## table3 — Table 3 / tab:lrsversions / source/table_lrsversions.tex

完整FDR/FGL移植、路径重设计、几何变体与GCDL的100轮历史设计比较。

**关键记录：** Original / Path / Path+geometry / GCDL 的 AP：29.078 / 29.696 / 29.361 / 29.620；每条训练记录均 100 轮。

**证据文件：**

- [01_manuscript/source/table_lrsversions.tex](../01_manuscript/source/table_lrsversions.tex)
- [01_manuscript/inputs/historical_fdr_results.csv](../01_manuscript/inputs/historical_fdr_results.csv)
- [01_manuscript/inputs/clean_fdr_results.csv](../01_manuscript/inputs/clean_fdr_results.csv)
- [01_manuscript/inputs/geometry_fdr_results.csv](../01_manuscript/inputs/geometry_fdr_results.csv)
- [01_manuscript/inputs/lrs_gfdr_results.csv](../01_manuscript/inputs/lrs_gfdr_results.csv)
- [01_manuscript/inputs/original_fdr_run.json](../01_manuscript/inputs/original_fdr_run.json)
- [01_manuscript/inputs/clean_fdr_authority.json](../01_manuscript/inputs/clean_fdr_authority.json)
- [01_manuscript/inputs/lrs_comparison_provenance.json](../01_manuscript/inputs/lrs_comparison_provenance.json)
- [01_manuscript/inputs/clean_fdr_historical_config.yaml](../01_manuscript/inputs/clean_fdr_historical_config.yaml)
- [01_manuscript/inputs/clean_fdr_historical_math.py](../01_manuscript/inputs/clean_fdr_historical_math.py)
- [01_manuscript/inputs/clean_fdr_historical_loss.py](../01_manuscript/inputs/clean_fdr_historical_loss.py)

**解释边界：**

- Original是完整FDR/FGL移植；Clean是中间路径variant，不能替代主移植参照。
- Original额外preliminary-box与DN-FDR监督开启，Clean/geometry/G关闭；表内同时改变了参考和监督路径。
- 这些是历史设计运行，并非全源码和全初始化严格匹配消融；Path redesign AP略高于GCDL必须保留。
- GCDL相对host的大幅增益包括继承FDR表示的贡献，不能全部归因于几何/LQS。

## table4 — Table 4 / tab:components, tab:efficiency / source/table_components.tex

五种配置的VisDrone验证精度、完整未融合参数、执行计算量和batch8吞吐量。

**关键记录：** Baseline / G / G+F / G+B / Full 的 AP：21.911 / 29.620 / 29.773 / 29.277 / 30.109。Full：35.244 M、134.051 GFLOPs、107.920 ms/8张、74.129 images/s。RTX4090、FP32、640×640、预热100批、计时300批/臂。

**证据文件：**

- [01_manuscript/source/table_components.tex](../01_manuscript/source/table_components.tex)
- [01_manuscript/inputs/lrs_gfdr_results.csv](../01_manuscript/inputs/lrs_gfdr_results.csv)
- [02_evidence/visdrone_g_f_training_20260909/results.csv](../02_evidence/visdrone_g_f_training_20260909/results.csv)
- [02_evidence/visdrone_g_f_training_20260909/args.yaml](../02_evidence/visdrone_g_f_training_20260909/args.yaml)
- [02_evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/joint-results.csv](../02_evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/joint-results.csv)
- [02_evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/bpdd-current-results.csv](../02_evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/bpdd-current-results.csv)
- [02_evidence/batch8_efficiency_20260916/v1/efficiency.json](../02_evidence/batch8_efficiency_20260916/v1/efficiency.json)
- [02_evidence/batch8_efficiency_20260916/v1/measure.py](../02_evidence/batch8_efficiency_20260916/v1/measure.py)
- [02_evidence/batch8_efficiency_20260916/verification.json](../02_evidence/batch8_efficiency_20260916/verification.json)
- [02_evidence/audit_remediation_20260915/full_flops/v2/complete_report.json](../02_evidence/audit_remediation_20260915/full_flops/v2/complete_report.json)
- [02_evidence/audit_remediation_20260915/full_flops/v2/arithmetic_count.json](../02_evidence/audit_remediation_20260915/full_flops/v2/arithmetic_count.json)
- [02_evidence/audit_remediation_20260915/full_flops/v2/trace.py](../02_evidence/audit_remediation_20260915/full_flops/v2/trace.py)
- [02_evidence/audit_remediation_20260915/full_flops/v2/counter_source.py](../02_evidence/audit_remediation_20260915/full_flops/v2/counter_source.py)
- [02_evidence/audit_remediation_20260915/efficiency/v3/efficiency.json](../02_evidence/audit_remediation_20260915/efficiency/v3/efficiency.json)
- [07_historical_context/results/main_results.json](../07_historical_context/results/main_results.json)
- [02_evidence/baseline_strict_val/fdr-vs-control-strict-final-paper-metrics.json](../02_evidence/baseline_strict_val/fdr-vs-control-strict-final-paper-metrics.json)
- [02_evidence/baseline_strict_val/fdr-formal-seed0-control-d97e1eb7-epoch-0100.json](../02_evidence/baseline_strict_val/fdr-formal-seed0-control-d97e1eb7-epoch-0100.json)
- [02_evidence/baseline_strict_val/FDR_RTDETR_L_STRICT_CONTROL_AND_RESULTS_2026-08-09_ZH.md](../02_evidence/baseline_strict_val/FDR_RTDETR_L_STRICT_CONTROL_AND_RESULTS_2026-08-09_ZH.md)

**解释边界：**

- batch8_efficiency_20260916/v1是当前论文唯一时间数据来源。efficiency/v3中的batch1时间仅为历史记录，不进入本表。
- 13.49 ms若由整批耗时摊销得到，不能描述为单张请求响应延迟；吞吐量是固定输入模型批处理测量。
- GFLOPs按v2口径统计已执行模型forward，MAC=2；参数采用完整未融合模型口径，不与fused count混用。
- Baseline 21.911的原始文档将其定义为统一独立val复评结果，而非已核验的训练CSV峰值；归档保留该口径差异，不能改称所有行均来自同一种日志。
- 其他历史配置不全是严格配对；G+B低于G，且B为专家与监督的组合，表不能单独证明KD或gate的AP收益。

## table5 — Table 5 / tab:sensitivity / source/table_sensitivity.tex

完整8种split/checkpoint/cap组合下共同评价器AP敏感性。

**关键记录：** final/best × val/test × cap100/300，完整8组。主终点 final/test/300；所有展示差值来自未舍入AP。

**证据文件：**

- [01_manuscript/source/table_sensitivity.tex](../01_manuscript/source/table_sensitivity.tex)
- [01_manuscript/inputs/external_sensitivity/EXTERNAL_SENSITIVITY.json](../01_manuscript/inputs/external_sensitivity/EXTERNAL_SENSITIVITY.json)
- [01_manuscript/inputs/external_sensitivity/cross-protocol-manifest.json](../01_manuscript/inputs/external_sensitivity/cross-protocol-manifest.json)
- [01_manuscript/inputs/external_sensitivity/dfine_final_val.cap100.json](../01_manuscript/inputs/external_sensitivity/dfine_final_val.cap100.json)
- [01_manuscript/inputs/external_sensitivity/dfine_final_val.cap300.json](../01_manuscript/inputs/external_sensitivity/dfine_final_val.cap300.json)
- [01_manuscript/inputs/external_sensitivity/dfine_final_test.cap100.json](../01_manuscript/inputs/external_sensitivity/dfine_final_test.cap100.json)
- [01_manuscript/inputs/external_sensitivity/dfine_final_test.cap300.json](../01_manuscript/inputs/external_sensitivity/dfine_final_test.cap300.json)
- [01_manuscript/inputs/external_sensitivity/dfine_best_val.cap100.json](../01_manuscript/inputs/external_sensitivity/dfine_best_val.cap100.json)
- [01_manuscript/inputs/external_sensitivity/dfine_best_val.cap300.json](../01_manuscript/inputs/external_sensitivity/dfine_best_val.cap300.json)
- [01_manuscript/inputs/external_sensitivity/dfine_best_test.cap100.json](../01_manuscript/inputs/external_sensitivity/dfine_best_test.cap100.json)
- [01_manuscript/inputs/external_sensitivity/dfine_best_test.cap300.json](../01_manuscript/inputs/external_sensitivity/dfine_best_test.cap300.json)
- [01_manuscript/inputs/external_sensitivity/joint_final_val.cap100.json](../01_manuscript/inputs/external_sensitivity/joint_final_val.cap100.json)
- [01_manuscript/inputs/external_sensitivity/joint_final_val.cap300.json](../01_manuscript/inputs/external_sensitivity/joint_final_val.cap300.json)
- [01_manuscript/inputs/external_sensitivity/joint_final_test.cap100.json](../01_manuscript/inputs/external_sensitivity/joint_final_test.cap100.json)
- [01_manuscript/inputs/external_sensitivity/joint_final_test.cap300.json](../01_manuscript/inputs/external_sensitivity/joint_final_test.cap300.json)
- [01_manuscript/inputs/external_sensitivity/joint_best_val.cap100.json](../01_manuscript/inputs/external_sensitivity/joint_best_val.cap100.json)
- [01_manuscript/inputs/external_sensitivity/joint_best_val.cap300.json](../01_manuscript/inputs/external_sensitivity/joint_best_val.cap300.json)
- [01_manuscript/inputs/external_sensitivity/joint_best_test.cap100.json](../01_manuscript/inputs/external_sensitivity/joint_best_test.cap100.json)
- [01_manuscript/inputs/external_sensitivity/joint_best_test.cap300.json](../01_manuscript/inputs/external_sensitivity/joint_best_test.cap300.json)

**解释边界：**

- final test/cap300是预先登记的主要外部终点；其余为完整披露的敏感性结果。
- cap100复用每图总上限300的导出预测并应用COCOeval每类别截断，不是把检测器改成只输出100个预测。
- 两个训练配方不一致，不能将差值称为同配方结构因果效应。

## table6 — Table 6 / tab:literature / source/table_literature.tex

文献报告的VisDrone val上下文比较，区别于本项目复测。

**关键记录：** RemDet-L：35.3 M、29.3 AP；BDNet：2.59 M、31.2 AP；Full：35.244 M、30.109 AP。外部均300轮、本稿100轮。

**证据文件：**

- [01_manuscript/source/table_literature.tex](../01_manuscript/source/table_literature.tex)
- [01_manuscript/inputs/references.json](../01_manuscript/inputs/references.json)
- [04_literature/comparison_candidates/CANDIDATES_ZH.md](../04_literature/comparison_candidates/CANDIDATES_ZH.md)
- [04_literature/comparison_candidates/B_CONFERENCE_NO_RETEST_ZH.md](../04_literature/comparison_candidates/B_CONFERENCE_NO_RETEST_ZH.md)
- [04_literature/comparison_candidates/sources/BDNet_CVPR2026.pdf](../04_literature/comparison_candidates/sources/BDNet_CVPR2026.pdf)
- [04_literature/comparison_candidates/sources/BDNet_CVPR2026_supplement.pdf](../04_literature/comparison_candidates/sources/BDNet_CVPR2026_supplement.pdf)

**解释边界：**

- 文献配方及评价流程不同，不是同协议复测排名。
- RemDet AP/AP50来自作者论文，35.3M来自官方仓库；当前索引所见本地副本主要是来源审计，若无原PDF/仓库快照，不得称两者均已物理归档。
- RemDet作者全文：https://xinzhongzhu.github.io/document/RemDet_AAAI.pdf；官方仓库：https://github.com/HZAI-ZJNU/RemDet。

## figure1 — Figure 1 / fig:bubble / source/figure_bubble.tex

VisDrone验证AP–参数量–计算量气泡图，保留各论文来源与协议边界。

**关键记录：** 8个点；纵轴AP、横轴参数量、气泡面积GFLOPs。源于各自论文报告，非统一复测。

**证据文件：**

- [01_manuscript/source/figure_bubble.tex](../01_manuscript/source/figure_bubble.tex)
- [01_manuscript/source/bubble_plot_data.json](../01_manuscript/source/bubble_plot_data.json)
- [01_manuscript/source/bubble_comparison_data.csv](../01_manuscript/source/bubble_comparison_data.csv)
- [01_manuscript/source/build_bubble_figures.py](../01_manuscript/source/build_bubble_figures.py)
- [01_manuscript/assets/bubble_comparison.png](../01_manuscript/assets/bubble_comparison.png)
- [04_literature/research_notes/BUBBLE_DATA_AUDIT_ZH.md](../04_literature/research_notes/BUBBLE_DATA_AUDIT_ZH.md)
- [04_literature/cvm_papers/03_FGHDet_CVM2025.pdf](../04_literature/cvm_papers/03_FGHDet_CVM2025.pdf)
- [04_literature/comparison_candidates/sources/BDNet_CVPR2026.pdf](../04_literature/comparison_candidates/sources/BDNet_CVPR2026.pdf)
- [04_literature/comparison_candidates/sources/BDNet_CVPR2026_supplement.pdf](../04_literature/comparison_candidates/sources/BDNet_CVPR2026_supplement.pdf)

**解释边界：**

- FGHDet和其YOLOv7行使用Tables2/5的val精度及Table6同名结构的640成本，不使用Table6 test精度。
- FGHDet预训练情况未报告；不能声称全图所有点均scratch或同一训练/成本统计协议。
- BDNet论文中的YOLO11/12/26为其作者重训，非本项目复测；保留原表标签与审计说明。
- 气泡图数据中的旧绝对路径是历史出处；本条evidence给归档内可用路径。

## figure2 — Figure 2 / fig:overview / source/figure_overview.tex

当前GCDL、共享FIA、box-conditioned expert与选择性监督的整合架构。

**关键记录：** 6层解码器、300 ordinary queries、33 bins，专家访问P2–P4；当前Full源码提交a43056a。

**证据文件：**

- [01_manuscript/source/figure_overview.tex](../01_manuscript/source/figure_overview.tex)
- [01_manuscript/source/body.tex](../01_manuscript/source/body.tex)
- [01_manuscript/assets/architecture_dense.png](../01_manuscript/assets/architecture_dense.png)
- [01_manuscript/inputs/publication_name_mapping.json](../01_manuscript/inputs/publication_name_mapping.json)
- [01_manuscript/inputs/sampling_points.json](../01_manuscript/inputs/sampling_points.json)
- [02_evidence/audit_remediation_20260915/source-a43056a/src/fdr_head.py](../02_evidence/audit_remediation_20260915/source-a43056a/src/fdr_head.py)
- [02_evidence/audit_remediation_20260915/source-a43056a/src/fdr_math.py](../02_evidence/audit_remediation_20260915/source-a43056a/src/fdr_math.py)
- [02_evidence/audit_remediation_20260915/source-a43056a/src/fdr_loss.py](../02_evidence/audit_remediation_20260915/source-a43056a/src/fdr_loss.py)
- [02_evidence/audit_remediation_20260915/source-a43056a/src/fia.py](../02_evidence/audit_remediation_20260915/source-a43056a/src/fia.py)
- [02_evidence/audit_remediation_20260915/source-a43056a/src/bpdd_capacity.py](../02_evidence/audit_remediation_20260915/source-a43056a/src/bpdd_capacity.py)
- [02_evidence/audit_remediation_20260915/source-a43056a/src/bpdd_capacity_loss.py](../02_evidence/audit_remediation_20260915/source-a43056a/src/bpdd_capacity_loss.py)
- [02_evidence/audit_remediation_20260915/source-a43056a/src/rtdetr_bpdd_capacity_fia.py](../02_evidence/audit_remediation_20260915/source-a43056a/src/rtdetr_bpdd_capacity_fia.py)
- [03_protocol_and_methods/methods/CURRENT_JOINT_METHOD_ZH.md](../03_protocol_and_methods/methods/CURRENT_JOINT_METHOD_ZH.md)

**解释边界：**

- 架构图是实现示意，不能替代功能源码证据。
- 旧UAVDT导出源码不用于证明本图与当前VisDrone Full实现一致。
- 论文改名不更改旧训练run和源码目录标识。

## figure3 — Figure 3 / fig:externalclasses / source/figure_external_classes.tex

共同评价器final test全部10类AP对照。

**关键记录：** 1610张test图、全部10类、final checkpoints、cap300；包含每类未舍入指标。

**证据文件：**

- [01_manuscript/source/figure_external_classes.tex](../01_manuscript/source/figure_external_classes.tex)
- [01_manuscript/source/build_external_figure.py](../01_manuscript/source/build_external_figure.py)
- [01_manuscript/assets/class_comparison.png](../01_manuscript/assets/class_comparison.png)
- [01_manuscript/inputs/external_class_profile/numeric_values.json](../01_manuscript/inputs/external_class_profile/numeric_values.json)
- [01_manuscript/inputs/external_class_profile/source/dfine_final_test.report.json](../01_manuscript/inputs/external_class_profile/source/dfine_final_test.report.json)
- [01_manuscript/inputs/external_class_profile/source/joint_final_test.report.json](../01_manuscript/inputs/external_class_profile/source/joint_final_test.report.json)
- [01_manuscript/inputs/external_class_profile/source/dfine_final_test.cap300.json](../01_manuscript/inputs/external_class_profile/source/dfine_final_test.cap300.json)
- [01_manuscript/inputs/external_class_profile/source/joint_final_test.cap300.json](../01_manuscript/inputs/external_class_profile/source/joint_final_test.cap300.json)
- [01_manuscript/inputs/external_class_profile/SHA256_MANIFEST.json](../01_manuscript/inputs/external_class_profile/SHA256_MANIFEST.json)

**解释边界：**

- 全10类均保留，不能只挑增益较大的类别。
- 报告来源为common evaluator；不得混入native类别指标。
- 展示完整检测器差异，不单独归因于某个模块；训练配方差异仍适用。

## figure4 — Figure 4 / fig:motivation / source/figure_motivation.tex

全部验证标注的输入尺度分布及理想化边界位移IoU动机。

**关键记录：** 548图、38,759框；五档计数6856 / 14011 / 12414 / 4580 / 898；640拉伸输入下等效边长<32px占85.9%。

**证据文件：**

- [01_manuscript/source/figure_motivation.tex](../01_manuscript/source/figure_motivation.tex)
- [01_manuscript/source/build_motivation_figure.py](../01_manuscript/source/build_motivation_figure.py)
- [01_manuscript/assets/scale_and_geometry.png](../01_manuscript/assets/scale_and_geometry.png)
- [01_manuscript/inputs/motivation_profile.json](../01_manuscript/inputs/motivation_profile.json)
- [01_manuscript/qualitative/gt_reconstructed/instances_val.json.gz](../01_manuscript/qualitative/gt_reconstructed/instances_val.json.gz)
- [01_manuscript/qualitative/asset_manifest.json](../01_manuscript/qualitative/asset_manifest.json)
- [02_evidence/visdrone_dfine_l_external_20260913/common_evaluation_20260915/dataset-preflight.json](../02_evidence/visdrone_dfine_l_external_20260913/common_evaluation_20260915/dataset-preflight.json)
- [02_evidence/visdrone_dfine_l_external_20260913/convert_visdrone_yolo_to_coco.py](../02_evidence/visdrone_dfine_l_external_20260913/convert_visdrone_yolo_to_coco.py)

**解释边界：**

- 32px阈值为拉伸到640输入后等效边长，不等于COCO按原图面积定义的APs分组。
- IoU位移曲线是解析几何示例，不是训练检测器实测误差分布。
- qualitative目录中的GT现为该图真实依赖，不能因取消定性图片而剔除。

## mechanism_geometry — Method feasible decoding; Appendix numerical checks / sec:geometryevidence

参考尺度/精度下界约束可表示正extent，保留隐含中心；反向使用identity surrogate。

**关键记录：** 名义尺寸0.1/1e-8 × FP16/BF16/FP32/FP64共8例；六层CPU BF16合成fixture以四边Integral=-4检查FP32输出与正corner extent。当前解码函数与冻结测试版本AST一致。

**证据文件：**

- [01_manuscript/source/body.tex](../01_manuscript/source/body.tex)
- [01_manuscript/inputs/frozen_fdr_math.py](../01_manuscript/inputs/frozen_fdr_math.py)
- [01_manuscript/inputs/geometry_evidence/current_function_check.json](../01_manuscript/inputs/geometry_evidence/current_function_check.json)
- [01_manuscript/inputs/geometry_evidence/geometry_evidence_manifest.json](../01_manuscript/inputs/geometry_evidence/geometry_evidence_manifest.json)
- [01_manuscript/inputs/geometry_evidence/correctness_test_summary.json](../01_manuscript/inputs/geometry_evidence/correctness_test_summary.json)
- [01_manuscript/inputs/geometry_evidence/archived_correctness/red.xml](../01_manuscript/inputs/geometry_evidence/archived_correctness/red.xml)
- [01_manuscript/inputs/geometry_evidence/archived_correctness/numerical.xml](../01_manuscript/inputs/geometry_evidence/archived_correctness/numerical.xml)
- [01_manuscript/inputs/geometry_evidence/archived_correctness/regression-final.xml](../01_manuscript/inputs/geometry_evidence/archived_correctness/regression-final.xml)
- [01_manuscript/inputs/geometry_evidence/source_f56b210/tests/test_no_server_correctness.py](../01_manuscript/inputs/geometry_evidence/source_f56b210/tests/test_no_server_correctness.py)
- [01_manuscript/inputs/geometry_evidence/source_f56b210/tests/test_fdr_feasible_geometry.py](../01_manuscript/inputs/geometry_evidence/source_f56b210/tests/test_fdr_feasible_geometry.py)
- [01_manuscript/inputs/geometry_evidence/source_f56b210/src/fdr_math.py](../01_manuscript/inputs/geometry_evidence/source_f56b210/src/fdr_math.py)

**解释边界：**

- 测试为受控合成数值检查，不证明训练失败频率、检测AP收益或所有实数范围安全。
- 1e-8为名义输入：转换至FP16后会下溢为0；八例不能均描述为实际严格正参考。
- 中心保持的针对性检查包括FP64普通/非对称情形；不能从PASS虚构具体修复后数值。
- 历史runtime JSONL缺失和secondary-summary触发率不作为正文主要证据。

## mechanism_lqs — Method layerwise quality shrinkage / sec:lrssupervision

同图同层合格匹配的detached IoU权重向组均值收缩，保持总和与排序并降低方差。

**关键记录：** 首层alpha=0.25、末层alpha=0；合格组至少2个匹配，方差乘以(1-alpha)^2，总权重守恒；FGL系数0.15。

**证据文件：**

- [01_manuscript/source/body.tex](../01_manuscript/source/body.tex)
- [01_manuscript/source/check_formulation.py](../01_manuscript/source/check_formulation.py)
- [01_manuscript/inputs/frozen_fdr_loss.py](../01_manuscript/inputs/frozen_fdr_loss.py)
- [02_evidence/audit_remediation_20260915/source-a43056a/src/fdr_loss.py](../02_evidence/audit_remediation_20260915/source-a43056a/src/fdr_loss.py)
- [02_evidence/audit_remediation_20260915/source-a43056a/src/fdr_math.py](../02_evidence/audit_remediation_20260915/source-a43056a/src/fdr_math.py)
- [01_manuscript/inputs/lrs_comparison_provenance.json](../01_manuscript/inputs/lrs_comparison_provenance.json)

**解释边界：**

- 均值/总和/方差性质主要由公式与源码保证；不能自动推导独立AP收益。
- 全零组保持零；不提供无条件正监督下界。
- 严格代数性质在精确算术成立，实现在浮点中另作总和残差修正。

## mechanism_selective_transfer — Method correspondence, edge selection and joint box geometry

只对同图/同query/同GT匹配进行专家监督；混合学生保留边与拟替换专家边后再检查整框IoU。

**关键记录：** 六层均核对图/query/GT对应关系，在共同固定分布参考系解码学生、专家及混合边，检查拟转移混合框。

**证据文件：**

- [01_manuscript/source/body.tex](../01_manuscript/source/body.tex)
- [02_evidence/audit_remediation_20260915/source-a43056a/src/bpdd_loss.py](../02_evidence/audit_remediation_20260915/source-a43056a/src/bpdd_loss.py)
- [02_evidence/audit_remediation_20260915/source-a43056a/src/bpdd_capacity.py](../02_evidence/audit_remediation_20260915/source-a43056a/src/bpdd_capacity.py)
- [02_evidence/audit_remediation_20260915/source-a43056a/src/bpdd_capacity_loss.py](../02_evidence/audit_remediation_20260915/source-a43056a/src/bpdd_capacity_loss.py)
- [02_evidence/audit_remediation_20260915/source-a43056a/src/fdr_head.py](../02_evidence/audit_remediation_20260915/source-a43056a/src/fdr_head.py)
- [02_evidence/audit_remediation_20260915/source-a43056a/src/fdr_math.py](../02_evidence/audit_remediation_20260915/source-a43056a/src/fdr_math.py)
- [01_manuscript/inputs/sampling_points.json](../01_manuscript/inputs/sampling_points.json)

**解释边界：**

- gate检查当前预测下拟转移target的几何质量，不保证下一次optimizer update后IoU改善。
- 同reference解码应按冻结源码解释，不能虚构reference rebase。
- 当前五臂表联合改变专家与监督，不隔离gate/KD独立准确率效应。

## controlled_fia_pair — Experiments five-arm comparison / G+B versus Full

G+B与Full为当前最直接匹配的FIA-off/on对照；共享源码和共享初始化一致。

**关键记录：** best AP 29.277 → 30.109（+0.832 pp）；final AP 28.939 → 30.065（+1.126 pp）。239个共享源码文件与994个共享初始state张量一致，新增19个FIA state条目，gamma初始0。

**证据文件：**

- [02_evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/joint-results.csv](../02_evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/joint-results.csv)
- [02_evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/bpdd-current-results.csv](../02_evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/bpdd-current-results.csv)
- [02_evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/joint-authority.json](../02_evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/joint-authority.json)
- [02_evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/bpdd-authority.json](../02_evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/bpdd-authority.json)
- [02_evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/fia_controlled_pair_authority.json](../02_evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/fia_controlled_pair_authority.json)
- [02_evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/joint-args.yaml](../02_evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/joint-args.yaml)
- [02_evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/bpdd-current-args.yaml](../02_evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/bpdd-current-args.yaml)
- [02_evidence/audit_remediation_20260915/SOURCE_PAIR_RESOLUTION_ZH.md](../02_evidence/audit_remediation_20260915/SOURCE_PAIR_RESOLUTION_ZH.md)
- [02_evidence/audit_remediation_20260915/source_pair_comparison.json](../02_evidence/audit_remediation_20260915/source_pair_comparison.json)
- [02_evidence/audit_remediation_20260915/source-recovery.json](../02_evidence/audit_remediation_20260915/source-recovery.json)
- [02_evidence/audit_remediation_20260915/efficiency/v3/initialization_probe.json](../02_evidence/audit_remediation_20260915/efficiency/v3/initialization_probe.json)
- [02_evidence/audit_remediation_20260915/efficiency/v3/measure.py](../02_evidence/audit_remediation_20260915/efficiency/v3/measure.py)

**解释边界：**

- 该对照支持专家配置下加入F的条件差异，不等于F在所有基座都有效。
- 两臂best epoch不同不等于协议失配；应同时保留100轮CSV与final方向。
- 共享state相同不意味着额外FIA参数不存在；额外分支gamma初始化为0。
- 不是多随机种子统计显著性证明。

## source_identity — Current implementation and naming provenance

当前VisDrone Full冻结源码、历史G+B源码、权重指纹与名称映射分别保存。

**关键记录：** 当前Full a43056a、G+B 5ef5747；保留checkpoint哈希与GCDL/LQS对历史名称的映射。

**证据文件：**

- [02_evidence/audit_remediation_20260915/source-a43056a](../02_evidence/audit_remediation_20260915/source-a43056a)
- [02_evidence/audit_remediation_20260915/source-5ef5747](../02_evidence/audit_remediation_20260915/source-5ef5747)
- [02_evidence/audit_remediation_20260915/source-recovery.json](../02_evidence/audit_remediation_20260915/source-recovery.json)
- [02_evidence/audit_remediation_20260915/source_pair_comparison.json](../02_evidence/audit_remediation_20260915/source_pair_comparison.json)
- [02_evidence/batch8_efficiency_20260916/v1/efficiency.json](../02_evidence/batch8_efficiency_20260916/v1/efficiency.json)
- [01_manuscript/inputs/publication_name_mapping.json](../01_manuscript/inputs/publication_name_mapping.json)
- [01_manuscript/inputs/uavdt/author_confirmation.json](../01_manuscript/inputs/uavdt/author_confirmation.json)
- [01_manuscript/inputs/uavdt/inventory.json](../01_manuscript/inputs/uavdt/inventory.json)

**解释边界：**

- 源代码与checkpoint哈希能证明记录身份，不等于所有权重实体均存储于此Git归档。
- UAVDT作者确认单独登记，其旧源码冲突不能用当前VisDrone源码覆盖。
- 历史AC-BPDD命名不得自动映射为当前Capacity-BPDD-v3-Safe。

## build_and_scope — Current rendered manuscript / build_manifest.json, verification.json

归档针对当前13页稿的实际6表4图11公式，保留构建与内容核验。

**关键记录：** 13页、6表、4图、11公式、25条参考文献；验证报告保留。

**证据文件：**

- [01_manuscript/build.py](../01_manuscript/build.py)
- [01_manuscript/build_manifest.json](../01_manuscript/build_manifest.json)
- [01_manuscript/verification.json](../01_manuscript/verification.json)
- [01_manuscript/source/body.tex](../01_manuscript/source/body.tex)
- [01_manuscript/inputs/original_source_hashes.json](../01_manuscript/inputs/original_source_hashes.json)

**解释边界：**

- build.py仍保存被pop的旧表定义；table_native/table_external/table_mechanism等存在不代表当前独立渲染表。
- 旧source_files绝对路径及hash不是物理原件；应结合归档实际文件和manifest查验。
- 本索引不是新实验，不改变现有数值与图表。

## baseline_validation_provenance — Table 4 Baseline validation row

Baseline验证AP 21.911与AP50 38.663来自历史统一独立复评，并关联相同epoch100权重。

**关键记录：** 原始报告AP=0.2191068567584638、AP50=0.3866331521256526，显示为21.911/38.663；548图、38759框、164400预测。报告SHA256为8FFD439C…44333E8。

**证据文件：**

- [02_evidence/baseline_strict_val/fdr-vs-control-strict-final-paper-metrics.json](../02_evidence/baseline_strict_val/fdr-vs-control-strict-final-paper-metrics.json)
- [02_evidence/baseline_strict_val/fdr-formal-seed0-control-d97e1eb7-epoch-0100.json](../02_evidence/baseline_strict_val/fdr-formal-seed0-control-d97e1eb7-epoch-0100.json)
- [02_evidence/baseline_strict_val/FDR_RTDETR_L_STRICT_CONTROL_AND_RESULTS_2026-08-09_ZH.md](../02_evidence/baseline_strict_val/FDR_RTDETR_L_STRICT_CONTROL_AND_RESULTS_2026-08-09_ZH.md)
- [07_historical_context/results/main_results.json](../07_historical_context/results/main_results.json)

**解释边界：**

- 未找到将21.911确认为100轮训练CSV最佳值的原始CSV证据；不得把历史转录标签等同训练原件。
- 该值不同于2026-09-15新冻结环境下的640重评值；应保持当前表实际使用口径，不混写为一次统一新复评。
- checkpoint实体不必嵌入Git，按权重索引记录本地路径、发布地址与SHA256。



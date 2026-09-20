# 审查记录的版本范围

## 当前同会研读与结构版

- MOTIVATION_INDEPENDENT_CHECK_ZH.md：独立读取冻结 GT，用面积分箱与矩形交集核验新图数值。
- STRUCTURE_FINAL_REVIEW_ZH.md：审读本轮 source/body.tex 的任务动机、核心主次、归因和结论。
- 当前 EDITORIAL_CHECKS.json：最终编译稿、渲染图及新增统计的验收状态。
- STRUCTURE_AND_REVISION_BLUEPRINT_ZH.md：主线程综合六篇官方全文、三名代理的阅读与论证分析。

终审建议的两项修改均落实：图 1 caption 自身标明 common evaluator 的坐标变换并区分原图 APs；引言将新的精度—成本配置归给整个 local visual extension。

## 从前一版保留的历史记录

DETR_TECHNICAL_REVIEW_ZH.md、CVM_REVIEW_ZH.md、PRESENTATION_AND_RELATED_WORK_ZH.md、FINAL_INDEPENDENT_REVIEW_ZH.md、RESOLUTION_ZH.md 和 PREVIOUS_REVISION_EDITORIAL_CHECKS.json 对应 cvm_multireviewer_revision_20260917，供追溯技术修正；不冒称这些代理审查了后续新增图和改写内容。

formulation_checks.json 是当前重新运行的标准库算术/源码结构检查，不运行神经网络。所有代理审查均是辅助分析，不是正式会议同行评审。

## 后续作者事实补充

BATCH_MEMORY_CLARIFICATION_ZH.md 记录 D-FINE-L physical batch=8 在 RTX 4090 24 GB 上 OOM 后降至 4 的作者确认、独立措辞审读及最新 PDF 视觉检查。此前视觉报告对应其中注明的旧哈希；本次第 8–11 页已重新查看，其余八页像素与上一已验收稿一致。

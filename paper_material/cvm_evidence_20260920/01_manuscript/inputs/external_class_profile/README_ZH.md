# 外部完整系统类别对比图

- 只使用已保存 final test 指标与对应 checkpoint 报告，无训练、推理或重新评价。
- 完整保留 10 类，按数据集类别 ID 排序；AP 原始小数乘 100，图上保留两位，正文范围与总体差值保留三位。
- 图中 D-FINE-L 是本项目 scratch-adapted 复现；训练配方与 Full 不同。
- 可支持“在该共同评价协议中，Full 的所有十类 AP 高于该复现”的限定结论；不能支持所有评价指标、所有训练条件或每个模块都占优。
- 这是完整系统类别剖面，不是内部模块消融，也不替代逐图成功／失败案例。
- external_classes.tikz 是自包含 TikZ figure*，仅要求主文件加载 TikZ；不需要 PGFPlots、外部图片或 shell escape。
- SHA256_MANIFEST.json 记录五份直接来源的路径与 SHA256；numeric_values.json 保存不舍入数值和图中展示值。
- build_external_figure.py 可从已存在归档重新生成全部图形与数值文件。

# 第二数据集待核对表

全部 AP、P、R 按百分数显示；差值单位为 pp。数值由证据文件生成，保留三位小数。

## U1 UAVDT 总体结果：已填数，待统一数据统计

| Run | P | R | AP50 | AP | Epochs |
| --- | --- | --- | --- | --- | --- |
| RT-DETR-L baseline | 52.700 | 31 | 27.700 | 15.600 | 79 |
| Joint export (identity pending) | 41.690 | 33.100 | 29.160 | 16.960 | 100 |

baseline 是可靠服务器报告。其17165张/342686目标与联合历史截图16592张/375883目标不一致；新导出没有同等完整数据清单，不能据此确认相同评估样本。联合记录还需 best.pt/配置与当前 v3-Safe 身份绑定。15.60→16.96 的 +1.36 pp 暂不进入摘要或主结论。该实验属于第二数据集训练/验证，不写零样本迁移。

证据：[all_experiments_summary.json · H11](../results/all_experiments_summary.json)；[all_experiments_summary.json · H12](../results/all_experiments_summary.json)；[paper_data.txt](../evidence/uavdt_capacity_v3_safe_joint_20260913/user_export_20260915/paper_data.txt)；[rtdetr_baseline_test_results.md](../evidence/uavdt_capacity_v3_safe_joint_20260913/baseline_reference_20260915/rtdetr_baseline_test_results.md)

## U2 UAVDT 类别诊断

| Run | Car AP | Truck AP | Bus AP |
| --- | --- | --- | --- |
| RT-DETR-L baseline | 29.300 | 6.210 | 11.200 |
| Joint export | 34.650 | 4.060 | 12.190 |

与 U1 相同的评估身份待核对。truck 的低 AP 必须保留讨论；不同样本分布下的类别差值不能归因于模块。

证据：[all_experiments_summary.json · H11](../results/all_experiments_summary.json)；[all_experiments_summary.json · H12](../results/all_experiments_summary.json)

# 第二数据集待核对表

全部 AP、P、R 按百分数显示；差值单位为 pp。数值由证据文件生成，保留三位小数。

## U1 UAVDT 总体结果：当前联合模型，待统一评估复核

| Run | P | R | AP50 | AP | Epochs |
| --- | --- | --- | --- | --- | --- |
| RT-DETR-L baseline | 52.700 | 31 | 27.700 | 15.600 | 79 |
| Current joint model export | 41.690 | 33.100 | 29.160 | 16.960 | 100 |

联合臂的方法身份已由作者确认，为当前 LRS-GFDR + Capacity-BPDD-v3-Safe + FIA。baseline 是可靠服务器报告；但 baseline 的17165张/342686目标与联合臂的16592张/375883目标不一致，因此尚未通过“同一评估清单”核验。15.60→16.96 的 +1.36 pp 不进入摘要或正文主结论；本表仅保留为复评前审计记录。该实验属于第二数据集训练/验证，不写零样本迁移。

证据：[all_experiments_summary.json · H11](../results/all_experiments_summary.json)；[all_experiments_summary.json · H12](../results/all_experiments_summary.json)；[paper_data.txt](../evidence/uavdt_capacity_v3_safe_joint_20260913/user_export_20260915/paper_data.txt)；[rtdetr_baseline_test_results.md](../evidence/uavdt_capacity_v3_safe_joint_20260913/baseline_reference_20260915/rtdetr_baseline_test_results.md)

## U2 UAVDT 类别诊断

| Run | Car AP | Truck AP | Bus AP |
| --- | --- | --- | --- |
| RT-DETR-L baseline | 29.300 | 6.210 | 11.200 |
| Joint export | 34.650 | 4.060 | 12.190 |

与 U1 相同的评估清单问题仍待复核。truck 的低 AP 必须保留讨论；不同样本分布下的类别差值不能归因于模块。

证据：[all_experiments_summary.json · H11](../results/all_experiments_summary.json)；[all_experiments_summary.json · H12](../results/all_experiments_summary.json)

# 正文：主结果与大模块消融

全部 AP、P、R 按百分数显示；差值单位为 pp。数值由证据文件生成，保留三位小数。

## T1 外部方法：VisDrone test 共同评估

| Method | Params (M) | AP | AP50 | AP75 | APs | APm | APl |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D-FINE-L (retrained) | 31.146 | 22.679 | 38.940 | 22.713 | 13.478 | 32.226 | 40.858 |
| Ours (Full) | 35.244 | 24.229 | 42.009 | 24.208 | 14.618 | 34.290 | 44.873 |
| Delta (pp) | — | 1.550 | 3.069 | 1.495 | 1.140 | 2.064 | 4.016 |

AP 指标为百分数。1610 张项目 test 图像；YOLO 标签转 COCO，maxDet=300、640、FP32、无 TTA/额外 NMS。两者都按各自原生 val AP 选择 best；训练配方不同（D-FINE batch=4/AdamW/FP32，本方法 batch=8/MuSGD/AMP）。这是本地共同评估结果，不是官方 VisDrone challenge 排名。参数为实际模型登记总量，不代表已剔除训练分支的部署开销。

证据：[dfine_best_test.cap300.json](../evidence/visdrone_dfine_l_external_20260913/common_evaluation_20260915/dfine_best_test.cap300.json)；[joint_best_test.cap300.json](../evidence/visdrone_dfine_l_external_20260913/common_evaluation_20260915/joint_best_test.cap300.json)；[bs4-run-authority.json](../evidence/visdrone_dfine_l_external_20260913/bs4-run-authority.json)；[joint_best_test.report.json](../evidence/visdrone_dfine_l_external_20260913/common_evaluation_20260915/joint_best_test.report.json)

## T2 大模块消融：只比较 G、B、F 三个组件

| Model | G | B | F | P | R | AP50 | AP |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Base | off | off | off | 46.761 | 41.731 | 38.663 | 21.911 |
| G | on | off | off | 59.480 | 49.366 | 49.382 | 29.620 |
| G+F | on | off | on | 59.391 | 50.049 | 49.548 | 29.773 |
| G+B | on | on | off | 59.826 | 48.524 | 48.783 | 29.277 |
| Full | on | on | on | 60.482 | 49.693 | 49.890 | 30.109 |

G=LRS-GFDR，B=Capacity-BPDD-v3-Safe，F=FIA P3-only。各行所有指标取同一 AP-best 轮。Base/G/G+F 是已登记参考运行；G+B/Full 的数据、初始状态及已记录训练设置匹配。共同 protocol ID 是事后归档分组，不替代源码差异审计。无 G 的 B 依赖不存在，未运行的组合不填造数。

证据：[all_experiments_summary.json · V01](../results/all_experiments_summary.json)；[all_experiments_summary.json · V06](../results/all_experiments_summary.json)；[all_experiments_summary.json · V09](../results/all_experiments_summary.json)；[all_experiments_summary.json · V12](../results/all_experiments_summary.json)；[all_experiments_summary.json · V13](../results/all_experiments_summary.json)；[bpdd-authority.json](../evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/bpdd-authority.json)；[joint-authority.json](../evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/joint-authority.json)；[bpdd-current-results.csv](../evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/bpdd-current-results.csv)；[joint-results.csv](../evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/joint-results.csv)

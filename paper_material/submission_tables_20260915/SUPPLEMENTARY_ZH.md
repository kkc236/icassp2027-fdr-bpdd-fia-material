# 支持性检验

全部 AP、P、R 按百分数显示；差值单位为 pp。数值由证据文件生成，保留三位小数。

## S1 FIA 开关的独立 test 检验

| Model | AP | AP50 | AP75 | APs | APm | APl |
| --- | --- | --- | --- | --- | --- | --- |
| G+B | 24.111 | 41.668 | 24.197 | 14.334 | 34.136 | 44.423 |
| Full | 24.229 | 42.009 | 24.208 | 14.618 | 34.290 | 44.873 |
| Delta (pp) | 0.118 | 0.341 | 0.011 | 0.284 | 0.155 | 0.451 |

固定各自原生 val 选出的 best checkpoint，再以共同 test 口径评估。Full 相对 G+B 的 test AP 为 +0.118 pp，原生 val best 为 +0.832 pp；两者不能替换。单 seed 观测没有置信区间，不写统计显著。

证据：[bpdd-independent-test-cap300.json](../evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/bpdd-independent-test-cap300.json)；[joint_best_test.cap300.json](../evidence/visdrone_dfine_l_external_20260913/common_evaluation_20260915/joint_best_test.cap300.json)；[bpdd-independent-test-manifest.json](../evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/bpdd-independent-test-manifest.json)

## S2 末轮稳健性：共同评估下的 best 与 final

| Model | Checkpoint | Val AP | Test AP |
| --- | --- | --- | --- |
| D-FINE-L | best | 28.796 | 22.679 |
| D-FINE-L | final | 28.501 | 22.554 |
| Full | best | 30.727 | 24.229 |
| Full | final | 30.528 | 24.133 |

best 来自原生验证选择，final 为第100轮；没有用 test 再选 checkpoint。共同评估 val 与训练日志 val 是不同口径。

证据：[dfine_best_val.cap300.json](../evidence/visdrone_dfine_l_external_20260913/common_evaluation_20260915/dfine_best_val.cap300.json)；[dfine_best_test.cap300.json](../evidence/visdrone_dfine_l_external_20260913/common_evaluation_20260915/dfine_best_test.cap300.json)；[dfine_final_val.cap300.json](../evidence/visdrone_dfine_l_external_20260913/common_evaluation_20260915/dfine_final_val.cap300.json)；[dfine_final_test.cap300.json](../evidence/visdrone_dfine_l_external_20260913/common_evaluation_20260915/dfine_final_test.cap300.json)；[joint_best_val.cap300.json](../evidence/visdrone_dfine_l_external_20260913/common_evaluation_20260915/joint_best_val.cap300.json)；[joint_best_test.cap300.json](../evidence/visdrone_dfine_l_external_20260913/common_evaluation_20260915/joint_best_test.cap300.json)；[joint_final_val.cap300.json](../evidence/visdrone_dfine_l_external_20260913/common_evaluation_20260915/joint_final_val.cap300.json)；[joint_final_test.cap300.json](../evidence/visdrone_dfine_l_external_20260913/common_evaluation_20260915/joint_final_test.cap300.json)

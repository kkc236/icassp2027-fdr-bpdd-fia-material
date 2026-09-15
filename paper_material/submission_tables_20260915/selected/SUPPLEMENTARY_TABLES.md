# 论文选用表格

AP 表示 mAP50–95；P、R 和 AP 的单位均为 %，差值单位为 pp。G=LRS-GFDR，B=Capacity-BPDD-v3-Safe，F=FIA P3-only。原生 val 与共同 test 分别标明，不混排指标。数值沿用源表的三位小数显示精度。

## 表 S1　FIA 开关的独立 test 检验

| Model | AP | AP50 | AP75 | APs | APm | APl |
| --- | --- | --- | --- | --- | --- | --- |
| G+B | 24.111 | 41.668 | 24.197 | 14.334 | 34.136 | 44.423 |
| Full | 24.229 | 42.009 | 24.208 | 14.618 | 34.290 | 44.873 |
| Delta (pp) | 0.118 | 0.341 | 0.011 | 0.284 | 0.155 | 0.451 |

表注：固定各自原生 val 选出的 best checkpoint，再以共同 test 口径评估。Full 相对 G+B 的 test AP 为 +0.118 pp，原生 val best 为 +0.832 pp；两者不能替换。单 seed 观测没有置信区间，不写统计显著。


## 表 S2　best 与 final 的共同评估结果

| Model | Checkpoint | Val AP | Test AP |
| --- | --- | --- | --- |
| D-FINE-L | best | 28.796 | 22.679 |
| D-FINE-L | final | 28.501 | 22.554 |
| Full | best | 30.727 | 24.229 |
| Full | final | 30.528 | 24.133 |

表注：best 来自原生验证选择，final 为第100轮；没有用 test 再选 checkpoint。共同评估 val 与训练日志 val 是不同口径。

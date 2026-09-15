# 论文可直接使用的实验结果包（更新至 2026-09-15）

## Material Passport

- **用途**：ICASSP/B 会论文的结果章节、消融章节和补充材料排版底稿。
- **主数据集**：VisDrone；**迁移验证集**：UAVDT。
- **主模型**：`LRS-GFDR + Capacity-BPDD-v3-Safe + FIA`。
- **选择规则**：Ultralytics 训练原生表按验证集 `mAP50–95(B)` 选 best；共同评估表另行固定推理口径，不能混用。
- **完整索引**：[全部实验结果总表](ALL_EXPERIMENTS_SUMMARY_20260915_ZH.md)；机器可读版：[all_experiments_summary.json](all_experiments_summary.json)。
- **证据原则**：严格配对、独立精确复评、训练原生结果、用户导出和截图分别标注，不把跨 authority 算术差写成因果增益。

## 表 1：VisDrone 主结果（正文主表）

| 方法 | best epoch | Precision | Recall | AP50 | mAP50–95 |
|---|---:|---:|---:|---:|---:|
| RT-DETR-L baseline | — | 0.46761 | 0.41731 | 0.38663 | 0.21911 |
| RT-DETR-L + Original FDR | 92 | 0.57064 | 0.49006 | 0.48473 | 0.29078 |
| RT-DETR-L + Clean-FDR | 88 | 0.58777 | 0.49849 | 0.49320 | 0.29696 |
| RT-DETR-L + LRS-GFDR | 92 | 0.59480 | 0.49366 | 0.49382 | 0.29620 |
| **RT-DETR-L + LRS-GFDR + Capacity-BPDD-v3-Safe + FIA** | **97** | **0.60482** | **0.49693** | **0.49890** | **0.30109** |

表 1 是论文主线的版本演进和最终主记录，不把相邻行差值解释为严格单变量因果。最终联合记录的末轮 mAP 为 `0.30065`，与 best `0.30109` 接近。

## 表 2：VisDrone 内部模块消融（补充/消融章节）

| 组件/版本 | mAP50–95（best） | 证据解释 |
|---|---:|---|
| LRS-GFDR（无 BPDD/FIA） | 0.29620 | 当前 GFDR 基座 |
| LRS-GFDR + AC-BPDD-v2 | 0.29628 | 跨运行观察，+0.008 pp |
| LRS-GFDR + AC-BPDD residual-v1 | 0.29576 | 未优于基座 |
| LRS-GFDR + Capacity-BPDD-v2 | 0.29848 | 历史容量版候选 |
| LRS-GFDR + FIA（P3-only） | 0.29773 | FIA 兼容性观察 |
| LRS-GFDR + Capacity-BPDD-v3-Safe | 0.29277 | BPDD-only，best E80；test@300=0.241106 |
| **LRS-GFDR + Capacity-BPDD-v3-Safe + FIA** | **0.30109** | 当前联合主记录 |

E（BPDD-only）与 F（Full）在训练主体协议上是一致的：数据集、初始状态、seed=0、
100 epochs、batch=8、640、MuSGD、AMP、增强和确定性设置均相同；F 相比 E 额外打开
FIA。两次记录的 best 轮为 E80/F97，但 final 也同方向（0.28939→0.30065，+1.126 pp）。
由于两条 authority 的源码提交和配置哈希不同，表 2 的 `+0.831 pp` 应写成
“协议匹配的 Full vs BPDD-only 受控对照”，而不是无条件宣称纯 FIA 的严格因果增益。
完整内部表和失败候选见 [内部消融与模块证据表](ABLATION_TABLES_ZH.md)。

## 表 3：BPDD 严格配对证据（唯一可写因果增益）

| split | FDR | FDR + BPDD（旧版） | ΔmAP50–95 | ΔAP75 |
|---|---:|---:|---:|---:|
| val | 0.290380 | 0.292770 | **+0.239 pp** | +0.072 pp |
| test | 0.231124 | 0.233959 | **+0.283 pp** | **+0.276 pp** |

两臂使用同源码提交、同 protocol、同初始状态、同 seed=0 和 100 epochs，并采用同一
冻结 evaluator。该表对应旧版 BPDD，不能改称 `Capacity-BPDD-v3-Safe` 的严格增益。

## 表 4：跨协议 D-FINE-L 共同评估

| 选择 | split | D-FINE-L | 当前联合 | 联合 − D-FINE-L |
|---|---|---:|---:|---:|
| final / final | val | 0.285010 | 0.305282 | **+2.027 pp** |
| final / final | test | 0.225544 | 0.241335 | **+1.579 pp** |
| best / best | val | 0.287959 | 0.307270 | **+1.931 pp** |
| best / best | test | 0.226785 | 0.242285 | **+1.550 pp** |

双方只在推理侧统一为 PIL 640、FP32、无 TTA/额外 NMS、COCOeval 2.0.11；训练框架、
优化器、batch、AMP 和增强不一致。因此表 4 是“统一评估下的绝对位置”，不是训练
协议完全相同的公平因果比较。

## 表 5：UAVDT 迁移结果

| 方法 | Precision | Recall | F1 | AP50 | AP75 | mAP50–95 |
|---|---:|---:|---:|---:|---:|---:|
| RT-DETR-L baseline | 0.5270 | 0.3100 | — | 0.2770 | — | **0.1560** |
| 当前三模块联合 | 0.4169 | 0.3310 | 0.3690 | 0.2916 | 0.1750 | **0.1696** |
| 联合 − baseline | −11.01 pp | +2.10 pp | — | +1.46 pp | — | **+1.36 pp** |

UAVDT 的 baseline 来自完整服务器测试报告并由截图互证，联合行来自 `exp/paper_data.txt`
精确导出；两者的总体指标属于已登记结果之间的算术比较。联合模型逐类 `car/truck/bus` mAP
分别为 `0.3465/0.0406/0.1219`，其中 truck 低于 baseline 的 `0.0621`，应作为
论文限制披露。完整表见 [UAVDT 结果与论文表](UAVDT_RESULTS_ZH.md)。

## 表 6：证据分层与论文放置

| 层级 | 内容 | 论文位置 | 能否写严格因果 |
|---|---|---|:---:|
| A | V13 当前 VisDrone Formal100 | 正文主表 | 否（主结果，不是配对消融） |
| B | P01–P04 FDR/BPDD 严格配对 | 消融表 | **是，限旧版 BPDD** |
| C | X01–X04 D-FINE 共同评估 | 外部比较 | 否，跨训练协议 |
| D | UAVDT U1/U2 | 泛化/迁移实验 | 否，联合 checkpoint/manifest 不完整且验证统计待对齐 |
| E | H04–H10 失败/筛选 | 补充材料 | 否，短跑/负结果不排位 |

## 可直接粘贴到论文的结果段落

> 在 VisDrone 上，当前 `LRS-GFDR + Capacity-BPDD-v3-Safe + FIA` 在 100 个训练
> epoch 中以第 97 轮达到 0.30109 mAP50–95（AP50=0.49890），末轮仍保持 0.30065。
> 在严格配对的旧版 BPDD 实验中，mAP50–95 在 val/test 上分别提高 0.239/0.283
> 个百分点，说明 BPDD 带来小幅但方向一致的定位收益。将当前联合模型与 D-FINE-L
> 的预测统一到同一推理评估器后，best/best 的 val/test mAP 分别为 0.30727/0.24229，
> 相对 D-FINE-L 提高 1.931/1.550 个百分点；该比较用于统一推理口径下的外部定位，
> 不承担训练协议完全一致的因果结论。迁移到 UAVDT 后，联合模型总体 mAP50–95 为
> 0.1696，较已登记 baseline 的 0.1560 提高 1.36 个百分点，但 truck 类下降到
> 0.0406，表明类别级泛化仍是限制因素。

## 论文排版顺序

1. 正文 Results：表 1 + 表 3；
2. 正文 External Comparison：表 4；
3. 正文 Generalization：表 5（同时披露 truck 风险）；
4. Supplementary：表 2 + 表 6 + 完整 [总表](ALL_EXPERIMENTS_SUMMARY_20260915_ZH.md)。

不要把表 1 的 `0.30109`、表 3 的 `+0.239/+0.283 pp` 和表 4 的 `+1.931/+1.550 pp`
合并成一条“总提升”。它们分别回答主结果、单变量 BPDD 因果和跨协议外部位置三个不同问题。

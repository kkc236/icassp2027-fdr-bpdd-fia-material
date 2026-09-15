# UAVDT 结果与论文表（更新至 2026-09-15）

## Material Passport

- **材料类型**：实验结果整理 / 跨数据集迁移证据
- **数据集**：UAVDT，3 类，类别顺序 `car / truck / bus`
- **当前联合模型**：`LRS-GFDR + Capacity-BPDD-v3-Safe + FIA`
- **证据边界**：服务器截图 + 用户导出的精确验证报告；导出目录没有 checkpoint、seed、原始预测或 best epoch，因此不把它标为新的独立训练臂。
- **原始材料**：[`user_export_20260915`](../evidence/uavdt_capacity_v3_safe_joint_20260913/user_export_20260915/)，配置/代码交接包见 [`uavdt_capacity_v3_safe_joint_20260913`](../evidence/uavdt_capacity_v3_safe_joint_20260913/README.md)。

## 表 U1：UAVDT 主结果（可直接放论文）

| 方法 | 训练完成 | Precision | Recall | F1 | AP50 | AP75 | mAP50–95 | 证据口径 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| RT-DETR-L baseline | 79 epochs | 0.5270 | 0.3100 | — | 0.2770 | — | **0.1560** | 服务器验证截图（四舍五入） |
| LRS-GFDR + Capacity-BPDD-v3-Safe + FIA | 100 epochs | 0.4169 | 0.3310 | 0.3690 | 0.2916 | 0.1750 | **0.1696** | 用户导出的四位小数报告，并与截图一致 |
| 联合 − baseline | — | −11.01 pp | **+2.10 pp** | — | **+1.46 pp** | — | **+1.36 pp** | 同一已登记 UAVDT 结果之间的算术差 |

这里的 `pp` 是百分点。由于 baseline 的截图没有提供 AP75/F1，空白不是零。训练轮数和
best epoch 的选择规则没有在 `exp` 导出中出现，因此 U1 不声称是“best-to-best”比较。

## 表 U2：UAVDT 逐类别结果

| 类别 | Precision | Recall | F1 | AP50 | AP75 | mAP50–95 |
|---|---:|---:|---:|---:|---:|---:|
| car | 0.7504 | 0.5912 | 0.6613 | 0.6432 | 0.3275 | **0.3465** |
| truck | 0.1677 | 0.1264 | 0.1442 | 0.0648 | 0.0457 | **0.0406** |
| bus | 0.3326 | 0.2755 | 0.3014 | 0.1667 | 0.1518 | **0.1219** |
| all（平均） | 0.4169 | 0.3310 | 0.3690 | 0.2916 | 0.1750 | **0.1696** |

已有 baseline 截图记录的 `truck mAP50–95=0.0621`。因此联合模型的 truck 为
`0.0406`，变化为 `−2.15 pp`；这必须在论文中作为类别级失败/限制披露，不能只报告
总体 `+1.36 pp`。

## 表 U3：复杂度与速度（当前联合模型）

| 参数 | 数值 |
|---|---:|
| GFLOPs | 107.1 |
| 参数量 | 32,621,369 |
| 权重大小 | 193.4 MB |
| 前处理 | 0.000235 s/图 |
| 推理 | 0.005463 s/图 |
| 后处理 | 0.000099 s/图 |
| FPS（全流程） | 172.48 |
| FPS（仅推理） | 183.03 |

速度字段直接来自 `paper_data.txt`，未推断硬件、batch 或精度模式；论文正文应把它
标成“该导出报告的运行统计”，除非能补回硬件与评估配置。

## 表 U4：外部 UAVDT 论文位置（只作背景，不混入严格排名）

| 外部方法 | UAVDT 报告指标 | 与本文的关系 |
|---|---|---|
| VARDet（ICASSP 2026） | val mAP=0.248，AP50=0.401，AP75=0.372 | ResNet-50、1333×800 统一重实现；与本文 Ultralytics RT-DETR-L 640 协议不匹配 |
| ResBiDet（ICASSP 2026） | 摘要 AP50=0.402；mAP50–95 未报告 | 只能做 AP50 描述性对照，不能排序 |

U4 的外部数值保留在 [外部方法对比](EXTERNAL_VISDRONE_COMPARISON_ZH.md) 中。不同
输入尺寸、骨干、切块/多尺度策略和 evaluator 不同时，不把它们与 U1 做严格优劣结论。

## 论文可直接使用的结果表述

> 在 UAVDT 三类迁移实验中，当前联合模型取得 0.1696 mAP50–95，相对已登记的
> RT-DETR-L baseline（0.1560）提高 1.36 个百分点，Recall 和 AP50 分别提高 2.10
> 和 1.46 个百分点。类别级结果显示，car、bus 的 mAP50–95 分别为 0.3465 和
> 0.1219，而 truck 仅为 0.0406，低于 baseline 的 0.0621，说明联合模块在总体指标
> 改善的同时仍存在对 UAVDT truck 类的泛化风险。

这段话只陈述当前 U1/U2 证据，不把 UAVDT 的结果外推为 VisDrone 上的严格模块因果增益。

## 可直接引用的图像证据

- 训练曲线：[`BoxP_curve.png`](../evidence/uavdt_capacity_v3_safe_joint_20260913/user_export_20260915/BoxP_curve.png)、[`BoxR_curve.png`](../evidence/uavdt_capacity_v3_safe_joint_20260913/user_export_20260915/BoxR_curve.png)、[`BoxPR_curve.png`](../evidence/uavdt_capacity_v3_safe_joint_20260913/user_export_20260915/BoxPR_curve.png)、[`BoxF1_curve.png`](../evidence/uavdt_capacity_v3_safe_joint_20260913/user_export_20260915/BoxF1_curve.png)。
- 混淆矩阵：[`confusion_matrix.png`](../evidence/uavdt_capacity_v3_safe_joint_20260913/user_export_20260915/confusion_matrix.png)、[`confusion_matrix_normalized.png`](../evidence/uavdt_capacity_v3_safe_joint_20260913/user_export_20260915/confusion_matrix_normalized.png)。
- 验证样例：`val_batch{0,1,2}_{labels,pred}.jpg` 均在同一导出目录中。

## 复核清单

- `paper_data.txt` SHA-256：`76DEFFF8CF85031C4FE70885DEC6652FCF1BD4D18E8D07D39549BDB303AF084F`
- 导出曲线、混淆矩阵和验证样例图均保留在 `user_export_20260915/`。
- 该导出没有 checkpoint 或原始 prediction，不能单独重跑 COCOeval；若要升级为严格
  UAVDT best-to-best 证据，需要补回 baseline/joint 的 checkpoint、seed、dataset
  manifest、评估命令和逐图预测。

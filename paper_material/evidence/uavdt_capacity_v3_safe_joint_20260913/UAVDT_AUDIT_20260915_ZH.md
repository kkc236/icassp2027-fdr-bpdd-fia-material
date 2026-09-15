# UAVDT baseline 与当前联合模型核对记录（2026-09-15）

## Material Passport

- **目的**：判定 UAVDT 的 baseline 与当前联合模型能否进入论文正文“表 4：UAVDT baseline 与联合模型总体结果”。
- **核对对象**：H11 `RT-DETR-L baseline` 与 H12 `LRS-GFDR + Capacity-BPDD-v3-Safe + FIA`。
- **方法身份**：H12 为当前联合模型；此身份由作者于 2026-09-15 明确确认，保留为作者确认事实。
- **审计状态**：`NOT_READY_FOR_MATCHED_MAIN_TABLE`。

## 已核对事实

| 核对项 | Baseline (H11) | 当前联合模型 (H12) | 结论 |
| --- | --- | --- | --- |
| 模型身份 | RT-DETR-L | LRS-GFDR + Capacity-BPDD-v3-Safe + FIA | 已确认 |
| 训练完成 | 79 epochs | 100 epochs | 已记录，但不是相同训练长度 |
| 总体 AP | 0.1560 | 0.1696 | 各自输出可登记 |
| 验证图像数 | 17,165 | 16,592 | 不一致 |
| 验证实例数 | 342,686 | 375,883 | 不一致 |
| 逐类 truck AP | 0.0621 | 0.0406 | 联合臂较低，必须披露 |
| 可复评输入 | 结果报告、运行名、best/last 文件名 | 汇总导出和曲线图 | 联合臂缺 checkpoint、数据清单、评估命令 |

## 判定

H11 与 H12 的图像数和实例数均不一致。图像数相差 573，实例数相差 33,197；这不是显示精度造成的差异。因此现有材料不能证明它们用了同一份评估清单与同一标签过滤规则。

两项模型各自的结果可以保存为真实运行记录；但 `0.1696 - 0.1560 = +1.36 pp` 仅是跨运行的算术差，不能写作“当前联合方法相对 baseline 的严格提升”，也不能用于模块因果归因。`truck` 的 `0.0406 < 0.0621` 应保留为类别级限制。

**结论：不将 U1 升为正文表 4；U2 保留在补充/审计材料。**

## 升级为正文表 4 的最小补件（不需要重新训练）

1. 取回 baseline 与当前联合模型各自的 `best.pt`；
2. 选择并冻结一份 UAVDT `val` 图像清单与对应 YOLO 标签（文件路径、图像数、实例数、SHA-256）；
3. 使用同一版本 Ultralytics、同一 `imgsz=640`、同一 `max_det=300`、无 TTA/额外 NMS 的命令，对两个权重各验证一次；
4. 保存两份原始终端输出、`args.yaml`、数据 YAML、评估命令和每个 checkpoint 的 SHA-256；
5. 若两次输出的 images/instances 完全相同，再将 U1 移入正文并将 U2 放入补充材料。

这一步是**复评**，不是重训；不改变任何已有模型权重。

## 证据

- [baseline 完整报告](baseline_reference_20260915/rtdetr_baseline_test_results.md)
- [baseline 原始协议](baseline_reference_20260915/UAVDT_Baseline实验方案.md)
- [当前联合模型导出](user_export_20260915/paper_data.txt)
- [当前联合模型导出清单](user_export_20260915/manifest.json)

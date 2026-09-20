# AP-FDR 内部双消融协议

> **状态更新（2026-08-21）**：本协议属于 EQuAL 重构前的 AP-FDR 内部诊断。当前论文候选 EQuAL 已统一采用 `preliminary_box=false`、`supervise_dn_fdr=false` 和 `edge_adaptive_fgl=true`，并通过 standalone exact val/test 门槛。旧消融继续保留用于解释设计演化，但不能把单个关闭项的结果冒充为 EQuAL 效果；EQuAL 的正式结果以 [`EQUAL_RESULTS_ZH.md`](../results/EQUAL_RESULTS_ZH.md) 为准。

## 目的

本轮只补两条对投稿影响最大的 AP-FDR 内部消融，用来回答：

1. stock-head-informed preliminary reference 是否是有效设计；
2. AP-FDR 在 denoising queries 上追加的 assignment-consistent distribution supervision 是否有效。

AP-FDR Full 已有正式结果，不重复训练。其余 w/o FGL、w/o preliminary-box loss 和 w/o cumulative refinement 保留为后备筛选，不在主双消融完成前占用正式算力。

## 三行正式表

| 行 | 配置 | 唯一变化 | 解释目标 |
|---|---|---|---|
| AP-FDR Full | configs/rtdetr-l-fdr.yaml | — | 完整方法 |
| w/o preliminary reference | configs/rtdetr-l-fdr-no-prebox.yaml | preliminary_box: true → false | 验证共享初始几何参考 |
| w/o DN FDR supervision | configs/rtdetr-l-fdr-no-dn.yaml | supervise_dn_fdr: true → false | 验证 DN 侧额外 FGL/pre-box 监督 |

w/o DN FDR supervision 只移除 loss_fgl_dn、loss_fgl_aux_dn、loss_bbox_pre_dn 和 loss_giou_pre_dn。Ultralytics 原生 DN classification/L1/GIoU、normal-query FGL、normal preliminary-box loss、网络参数和推理图全部保留，因此该行不会把 stock denoising training 一并删掉。

## 源码权威

- 仓库：kkc236/uav-detection-baselines
- 实现提交：ebb349aeb2cf092d4880751e165e22614c3c9d8c
- 训练入口：scripts/train_ap_fdr_ablation.py
- 本地聚焦验证：65 tests passed；compileall 与 git diff --check 通过。

训练入口拒绝未提交的 tracked source，并在启动前登记源码、配置、initial state、数据和完整 settings 指纹。现有未跟踪文件不进入训练身份。

## 冻结训练协议

- 数据：VisDrone2019 train/val；
- 模型：RT-DETR-L；
- 初始化：与 AP-FDR Full 相同的冻结 FDR initial state；
- seed：0；
- input：640；
- batch：8；
- workers：8；
- epochs：100；
- optimizer：MuSGD；
- pretrained/cache：false；
- AMP/deterministic：true；
- 训练顺序：先 w/o preliminary reference，成功结束后再运行 w/o DN FDR supervision；
- 服务器保持开机，不自动关机。

## best 选择与统一评估

每条运行从自身 results.csv 中按 val mAP50–95 最大值选择 best epoch，并登记 checkpoint SHA-256。随后用同一 best checkpoint 分别评估 val 与 test：

- imgsz=640
- batch=8
- workers=8
- conf=0.001
- max_det=300
- nms/cache/half/rect=false

正式表报告 P、R、AP50、AP75 与 mAP50–95，差值以 AP-FDR Full 为参照，优先解释 AP75。screen、中断运行、last checkpoint 或不同 split 数值不得写入正式消融表。

## 当前状态

截至 2026-08-20，源码、配置、训练入口和本地测试已经完成并推送；正式训练结果尚未登记。服务器 SSH 在认证前关闭连接，因此本文件只登记协议，不填结果占位。恢复连接后按上述顺序启动，机器证据入库后再更新 RESULTS_ZH.md 和论文表格。

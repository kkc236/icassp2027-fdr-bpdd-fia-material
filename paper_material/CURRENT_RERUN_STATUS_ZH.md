# 当前重跑状态（2026-09-14）

## 当前论文主线

当前主系统是 Ultralytics RT-DETR-L 的 `LRS-GFDR + Capacity-BPDD-v3-Safe + FIA` 联合 Formal100。它使用固定 VisDrone authority、seed0、100 epochs、640 输入、batch8、MuSGD、`pretrained=false`、AMP 和 deterministic；best val mAP50–95 为 `0.30109`（E97）。同系列 BPDD-only 已完成 100/100，best E80=`0.29277`，固定 test 独立评估 mAP@300=`0.24111`。

D-FINE-L 仅作为外部论文对照/跨协议实验；2026-09-14 最近一次官方训练在 epoch 2 因 `generalized_box_iou` 的非法框几何断言失败，尚无可用 checkpoint 或指标。修复并重新启动前不写入正式结果表。D-FINE-S 旧路线和 EQuAL standalone 作为历史/外部定位材料保留。

## 当前不得作为新稿结论的内容

- 未完成或仅跨协议的 D-FINE 训练数值；
- 不同 authority、拓扑或 evaluator 拼接得到的算术增量；
- 旧 AP-FDR A–E 行直接改名为当前 LRS-GFDR/Capacity 组合；
- 围绕旧结果形成的当前论文提纲、主张和图表安排。

这些内容只作为历史审计材料保留，不再从当前论文入口引用。Git 历史、原始日志、checkpoint 哈希和机器证据不删除，避免后续无法复核。

## 继续保留并复用的内容

- 最新 LRS-GFDR、Capacity-BPDD-v3-Safe 和 FIA 的训练期实现与联合结果；
- BPDD 的训练期渐进式边界分布蒸馏思想与实现；
- FIA 的 P3-only 高分辨率增强思想与实现；
- VisDrone 数据映射、原始 val/test 文本和逐类证据；
- 外部 VisDrone 正式论文比较资料及来源；
- 复杂度测量脚本、证据清单和完整 Git 历史。

保留不等于沿用旧数值。当前联合与 BPDD-only 的 authority、曲线和限制说明以当前联合证据包为准；D-FINE 外部对照仍须完成独立评估后才可排序。

## 结果使用顺序

1. 论文主结果引用当前 `LRS-GFDR + Capacity-BPDD-v3-Safe + FIA` Formal100 best；
2. BPDD 因果增益引用 2026-08-19 同 authority 严格 FDR/FDR+BPDD val/test 配对；
3. 最新 BPDD-only 曲线与独立 test 报告一并作为当前版本证据；严格因果仍引用同 authority 配对；
4. D-FINE-L 完成后，按同一 VisDrone split/input 记录为外部跨协议对照，不回写当前 Ultralytics 消融表；
5. 只有在 evaluator、split、checkpoint 和 authority 全部一致时，才计算严格增量。

旧路线页面继续作为历史快照；当前投稿定稿优先引用 `results/RESULTS_ZH.md`、`results/MAIN_TABLE_ZH.md` 和当前联合证据包。

# EQuAL Formal100 与统一 val/test 结果

## 1. 实验身份

- 论文方法：EQuAL（Edge-adaptive Query-Aligned Localization）
- 原始运行标识：ACE-FDR / `ace_fdr`
- 训练源码：`fca7763679b6e10ed68f98971a362a054ecd4853`
- 训练：seed 0、100 epochs、`pretrained=False`、MuSGD、640、batch 8
- checkpoint：`best.pt`，best epoch 91
- checkpoint SHA-256：`06c5809af89c9a6b944f8615ac4a92c28322b36db6eb872c73407a58e54c3bca`

同一个 `best.pt` 先后完成 val 和 test 的一次独立评估。固定 evaluator 为 `imgsz=640`、`batch=8`、`workers=8`、`conf=0.001`、`max_det=300`、`nms/cache/half/rect=False`。

## 2. Exact 结果

| split | Images / Instances | P | R | F1 | AP50 | AP75 | mAP50–95 |
|---|---:|---:|---:|---:|---:|---:|---:|
| val | 548 / 38,759 | 0.594055 | 0.488666 | 0.536231 | 0.490477 | 0.301026 | **0.294378** |
| test | 1,610 / 75,102 | 0.521576 | 0.428839 | 0.470683 | 0.406246 | 0.235363 | **0.234610** |

## 3. 相对登记 AP-FDR 的逐项变化

| split | ΔP | ΔR | ΔAP50 | ΔAP75 | ΔmAP50–95 |
|---|---:|---:|---:|---:|---:|
| val | +2.494 pp | −0.411 pp | +0.580 pp | **+0.850 pp** | **+0.472 pp** |
| test | +1.817 pp | −0.284 pp | +0.791 pp | **+0.646 pp** | **+0.661 pp** |

参照为材料仓已登记的 AP-FDR val 行及 exact test 结果。EQuAL 在两个 split 的 AP50、AP75 和 mAP50–95 上均为正向，已通过 standalone 采用门槛；Recall 略降，因此论文应写“定位精度提高”，不能写所有指标全面提高。

这些差值属于相同 split、相同 evaluator 协议下的登记 authority 算术比较，但不是同一新源码提交下同时重跑的 fresh strict pair。机器记录保留 `strict_paired=false`。

## 4. 历史采用状态

EQuAL standalone 判定为 `pass`，曾作为新的第一定位方法候选。随后完成的 `LRS-GFDR + Capacity-BPDD-v3-Safe + FIA` 联合 Formal100 已成为当前论文主系统，因此本页结果作为历史/外部定位候选保留；不能将旧 checkpoint 改名为当前联合组合：

| 下一实验 | 状态 | 用途 |
|---|---|---|
| EQuAL + BPDD | 未列入当前主线 | 旧候选组合，未形成当前论文证据 |
| EQuAL + FIA | 未列入当前主线 | 旧候选组合，未形成当前论文证据 |
| EQuAL + BPDD + FIA | 未列入当前主线 | 当前主系统已由 LRS-GFDR/Capacity/FIA Formal100 替代 |

不能把旧 `AP-FDR+BPDD/FIA` checkpoint 直接改名为 EQuAL 组合。A–E 标准表仍是 AP-FDR 代际的历史完整链，EQuAL exact 结果单独呈现；当前主结果请转到 [论文结果统一汇总](RESULTS_ZH.md)。

## 5. 证据入口

- [私密 GitHub Release（含 best/last、训练日志和完整证据包）](https://github.com/kkc236/icassp2027-fdr-bpdd-fia-material/releases/tag/equal-seed0-formal100-20260821)
- [机器汇总](equal_results.json)
- [val exact JSON](../evidence/equal_formal100_20260821/equal_val.json)
- [test exact JSON](../evidence/equal_formal100_20260821/equal_test.json)
- [完成清单](../evidence/equal_formal100_20260821/completion-manifest.json)
- [训练 results.csv](../evidence/equal_formal100_20260821/results.csv)
- [训练 args.yaml](../evidence/equal_formal100_20260821/args.yaml)
- [逐类 CSV](equal_class_results.csv)

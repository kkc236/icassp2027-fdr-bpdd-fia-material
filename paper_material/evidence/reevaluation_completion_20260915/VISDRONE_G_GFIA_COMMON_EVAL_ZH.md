# VisDrone：G 与 G+F 的共同复评

## 目的

原计划补齐 `G=LRS-GFDR`（V06）与 `G+F=LRS-GFDR+FIA P3-only`（V09）的同一评估器
test 结果，用于检查 FIA 在 G 基座上的贡献。复核后发现 V06 权重标签与实际配置不一致，
因此本文件同时保留诊断结果并明确撤销该配对结论。此操作是**验证已有权重**，不是重新训练。

## 已完成的共同复评（2026-09-15）

已在原服务器使用 V06 对应的历史最佳权重（`existing-state-20260907`）和 V09 的
`LRS-GFDR+FIA` 权重，以同一 Ultralytics 验证器、同一 VisDrone val authority 完成
548 张图的共同复评。结果见 `output/common_evaluation.json`。

| 臂 | P | R | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|
| LRS-GFDR（V06） | 59.324% | 49.467% | 49.377% | 29.610% |
| LRS-GFDR+FIA（V09） | 59.437% | 49.958% | 49.529% | 29.759% |
| FIA − G | +0.112 pp | +0.491 pp | +0.152 pp | **+0.150 pp** |

两臂使用相同的 `data_yaml_sha256`、`imgsz=640`、`batch=8`、`conf=0.001`、
`max_det=300`、FP32 推理和 8 workers。该结果是冻结权重的 matched validation，支持
“FIA 在 G 基座上带来约 0.15 pp mAP50-95 增益”的报告；它不是重新训练的单变量因果
消融，也不是 test 集结果。

## Test 共同复评（2026-09-15）

随后使用完整的 VisDrone test 标注（1610 张图、75102 个实例）完成同一脚本的 test
评估。test authority 为 `/root/sj-tmp/evidence/visdrone_test_authority_20260915.yaml`，
校验信息见 `output/common_test_evaluation.json`。复核模型摘要后发现，该文件中的第一臂
实际加载的是 `rtdetr-l-lrs-fdr`，没有显式 `feasible_geometry: true`，不能命名为 GFDR。

| 臂 | P | R | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|
| LRS-FDR（无显式 geometry，诊断用） | 52.586% | 43.768% | 41.103% | 23.622% |
| LRS-GFDR+FIA | 52.719% | 43.281% | 40.617% | 23.219% |

这两行不是严格的 G 与 G+F 配对，不得计算 FIA 增益。真正的 `rtdetr-l-lrs-gfdr` 训练
目录只完成到第 14 轮，当前没有可用于正式 test 对比的已训练 GFDR checkpoint。

此前基于错误基座标签得出的“FIA −0.403 pp”必须撤回，不能宣称 FIA 在两个 split 上
稳定提升。

作为评估链路的交叉检查，独立的 `Clean-FDR+Geometry` checkpoint 在同一 test 口径下
得到 mAP50-95=23.812%，结果记录于 `output/clean_fdr_geometry_common_test.json`。这说明
test 评估器和标签转换链路可以正常工作；当前缺的不是评估器，而是训练到足够轮数的
真正 LRS-GFDR checkpoint。

## Full（三模块）Test 评估（2026-09-15）

服务器上最新的 `rtdetr-l-lrs-gfdr-capacity-v3-safe-bpdd-fia` checkpoint（LRS-GFDR +
Capacity-BPDD + FIA）也已在同一 test authority 下完成评估：

| 臂 | P | R | mAP50 | mAP50-95 | 参数量 |
|---|---:|---:|---:|---:|---:|
| Full（三模块） | 53.848% | 43.644% | 41.242% | **23.602%** | 34.42M |

相对本次共同 test 的 LRS-FDR 诊断基座，Full 为 **−0.020 pp** mAP50-95；相对 G+F，
Full 为 **+0.383 pp**。Full 使用 Capacity-BPDD/FIA 专用源码 checkout，故这些是
matched-test 性能差异，不应写成严格 single-variable 增益。

## 已核对的限制

主材料仓仍只保存 V06/V09 的 `results.csv` 汇总；本次共同复评使用的是服务器上的
checkpoint，并已将 val/test 的校验信息分别写入 `output/common_evaluation.json` 与
`output/common_test_evaluation.json`。V09 的历史非 LRS `FDR+FIA` release 不能代替本次
test 结果。

## 需要从原服务器取回的最小文件

1. V06 的 `weights/best.pt`；
2. V09 的 `weights/best.pt`；
3. VisDrone test 对应的冻结 `data.yaml`；
4. 可加载两种 checkpoint 的代码 checkout。若二者来自不同源码快照，保留二者的 commit
   与 `git status --porcelain` 输出，不要用新代码强行改写权重。

## 运行

在材料仓根目录执行；这里的 `batch=8` 仅为默认值，显存不足可两臂一起改为 `4`，绝不只改一臂。

```bash
python scripts/run_common_checkpoint_eval.py \
  --dataset VisDrone \
  --code-root /data/uav-detection-baselines \
  --data-yaml /data/VisDrone/common_test.yaml \
  --split test --imgsz 640 --batch 8 --workers 8 --device 0 \
  --conf 0.001 --max-det 300 \
  --checkpoint g=/data/runs/v06/weights/best.pt \
  --checkpoint g_fia=/data/runs/v09/weights/best.pt \
  --output-dir /data/evidence/visdrone_g_gfia_common_test_20260915
```

完成后将整个输出目录（尤其是 `common_evaluation.json`、两个 `results.csv` 和控制台日志）
原样放回本目录下的 `output/`。只有 `status=complete`、两臂的
`contract.data_yaml_sha256` 相同，且 metrics 由同一脚本产生时，才能报告 G→G+F 的 test 差值。

## 写作边界

即使共同 test 完成，它只证明冻结 checkpoint 在同一 test 口径下的差异；若 V06/V09 训练源码、
初始状态或训练 authority 没有完全匹配，表注仍应使用“matched evaluation of existing
checkpoints”，不要升级为 FIA 的 fresh single-variable training causal ablation。

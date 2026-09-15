# VisDrone：G 与 G+F 的共同复评

## 目的

补齐 `G=LRS-GFDR`（V06）与 `G+F=LRS-GFDR+FIA P3-only`（V09）的同一评估器 test
结果，用于检查 FIA 在 G 基座上的贡献。此操作是**验证已有权重**，不是重新训练。

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

## 已核对的限制

主材料仓仍只保存 V06/V09 的 `results.csv` 汇总；本次共同复评使用的是服务器上的
checkpoint，并已将其校验信息写入 `output/common_evaluation.json`。目前完成的是 val
口径，不能把它写成 test 数字，也不能把 V09 的历史非 LRS `FDR+FIA` release 代替它。

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

# VisDrone：G 与 G+F 的共同复评

## 目的

原计划补齐 `G=LRS-GFDR`（V06）与 `G+F=LRS-GFDR+FIA P3-only`（V09）的同一评估器
test 结果，用于检查 FIA 在 G 基座上的贡献。最新运行时核对确认 V06/V09 解码器的
`feasible_geometry` 都为 True。此前仅凭 YAML 缺项否认 V06 几何校正的判断已纠正。
此操作是**验证已有权重**，不是重新训练。完整审计见 `EVALUATION_RUNTIME_AUDIT_ZH.md`。

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
校验信息见 `output/common_test_evaluation.json`。第一臂保留旧名称 `rtdetr-l-lrs-fdr`，
但实际解码器 `model.28.decoder.feasible_geometry=True`；第二臂相应开关也为 True。

| 臂 | P | R | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|
| G（历史 LRS-FDR，运行时带几何） | 52.586% | 43.768% | 41.103% | 23.622% |
| LRS-GFDR+FIA | 52.719% | 43.281% | 40.617% | 23.219% |

这两份冻结权重在本次原生评估下相差 −0.403 pp。该数值是观测差异，训练期几何路径和
源码等价性仍需历史证据确认。显式 GFDR 命名的另一个运行只有14轮，不等于历史100轮
基座没有几何校正。不能仅凭目录名或 YAML 缺项撤销历史实验。

作为评估链路的交叉检查，独立的 `Clean-FDR+Geometry` checkpoint 在同一 test 口径下
得到 mAP50-95=23.812%，结果记录于 `output/clean_fdr_geometry_common_test.json`。
成功跑完另一模型只说明流程能执行，不能单独证明评估器或标签转换完全正确。

## Full（三模块）Test 评估（2026-09-15）

服务器上最新的 `rtdetr-l-lrs-gfdr-capacity-v3-safe-bpdd-fia` checkpoint（LRS-GFDR +
Capacity-BPDD + FIA）也已在同一 test authority 下完成评估：

| 臂 | P | R | mAP50 | mAP50-95 | 参数量 |
|---|---:|---:|---:|---:|---:|
| Full（三模块） | 53.848% | 43.644% | 41.242% | **23.602%** | 34.42M |

相对本次原生 test 的 G 基座，Full 为 **−0.020 pp** mAP50-95；相对 G+F，
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

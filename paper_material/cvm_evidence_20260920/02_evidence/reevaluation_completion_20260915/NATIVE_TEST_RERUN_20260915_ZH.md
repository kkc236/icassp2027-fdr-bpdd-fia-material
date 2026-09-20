# VisDrone 原生 test 复跑（之前效果不佳的消融臂）

## 目的与口径

针对此前 test 泛化偏低的消融臂，按项目最早约定的原生 Ultralytics RT-DETR
评估器重新执行，不使用 D-FINE/COCOeval 跨协议流程。四臂均使用同一 test authority
（VisDrone test，1610 张图、75102 个实例）和同一参数：`imgsz=640`、`batch=8`、
`workers=8`、`conf=0.001`、`max_det=300`、`nms=false`、`half=false`、`cache=false`、
`rect=false`，并检查完整处理数为 1610。每个臂单独保留 checkpoint SHA256、模型类型和
原生 `metrics.box` 报告。

服务器证据目录：
`/root/sj-tmp/evidence/visdrone_native_test_rerun_20260915_v3/`。
目录内四个臂的 JSON 和 `RUN_COMPLETE.json` 均已生成；结果没有覆盖此前目录。

## 复跑结果

| 臂 | P | R | mAP50 | mAP50-95 | 参数量 |
|---|---:|---:|---:|---:|---:|
| G：LRS-GFDR | 52.586% | 43.768% | 41.103% | **23.622%** | 32.334M |
| G+F：LRS-GFDR + FIA | 52.719% | 43.281% | 40.617% | **23.219%** | 32.636M |
| G+B：LRS-GFDR + Capacity-BPDD | 53.335% | 43.737% | 41.095% | **23.621%** | 34.120M |
| Full：LRS-GFDR + Capacity-BPDD + FIA | 53.848% | 43.644% | 41.242% | **23.602%** | 34.421M |

相对 G 基座的 mAP50-95 变化：G+F **−0.403 pp**，G+B **−0.001 pp**，Full
**−0.020 pp**。因此“test 低”在原生评估器复跑后仍然存在，不能归因于先前误用了
跨协议评估器；它是当前冻结 checkpoint 在该 test split 上的真实观测。Full 相对 G+F
提高 **+0.383 pp**，但由于训练源码/authority 不完全同一，不能写成 FIA 或 BPDD 的
严格单变量因果增益。

## 可复核信息

- 四个臂均 `processed_images=1610`、`prediction_passes=1`；
- test YAML 的 SHA256 在四臂中一致；
- 同一原生 evaluator 使用 `CachedScaleRTDETRValidator`，同时输出原生 box 指标及
  tiny/small/medium/large 尺度统计；
- checkpoint SHA256 已写入每个臂 JSON，便于与服务器文件核对；
- 本次是冻结权重的重新评估，不是重新训练，不改变历史训练结果。

## 写作边界

正文可写为“在统一的原生 VisDrone test 评估下，四个冻结 checkpoint 的结果如表所示”。
不能把这些数字与 D-FINE 的 COCOeval AP 混在同一表中，也不能据此声称四臂满足严格
single-variable fresh-training 消融；若要作因果消融，仍需同一源码、初始化和 authority
重新训练成对实验。

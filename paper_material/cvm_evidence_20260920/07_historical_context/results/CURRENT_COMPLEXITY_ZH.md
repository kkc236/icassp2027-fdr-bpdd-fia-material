# 当前 VisDrone 五臂推理效率实测

日期：2026-09-15。测量已完成；不是训练、精度复评或部署分支剪枝实验。以下数值只属于当前冻结 checkpoint 与声明的统一运行环境，替代沿用旧 Full 25.21 FPS 的做法。

2026-09-16已另行完成[batch=8五臂推理补测](CURRENT_BATCH8_EFFICIENCY_ZH.md)。本页保留原batch=1结果，不用批处理摊销时间覆盖单张延迟。

## 同机结果

| 模型 | 总参数/未融合 (M) | 总参数/原生融合后 (M) | 延迟中位数 (ms) | P90 (ms) | FPS | 峰值分配显存 (MiB) |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 32.827 | 32.004 | 30.592 | 30.749 | 32.688 | 234.202 |
| G | 33.157 | 32.334 | 42.788 | 42.916 | 23.371 | 235.628 |
| G+F | 33.458 | 32.636 | 43.849 | 43.987 | 22.806 | 244.344 |
| G+B | 34.942 | 34.120 | 85.415 | 85.603 | 11.708 | 264.639 |
| Full | 35.244 | 34.421 | 86.075 | 86.608 | 11.618 | 272.634 |

参数统计为当前模型对象的全部参数，未宣称已经剔除所有未执行训练分支；融合前/后分列，不与历史不同口径混用。FPS=1000/延迟中位数，不是批量吞吐，也不是 AP 评估日志中的平均前向速度。

## 固定测量条件

- GPU：NVIDIA GeForce RTX 4090；Python 3.10.21，PyTorch 2.5.1+cu121，CUDA 12.1，Ultralytics 8.4.90。
- 640×640、batch=1、FP32，8 CPU threads；TF32=false，cudnn benchmark=false；conf=0.001、max_det=300，无TTA/额外NMS。
- 一张固定seed生成的uint8 BGR随机图，反复输入；不包含磁盘读取。计时范围为 Ultralytics predict 的预处理、模型与后处理，CUDA同步后计时。
- 每臂预热100次、计时300次；使用原生GPU融合。记录全部1500个单次延迟值、P90、显存和checkpoint前后SHA-256。只做一轮基准，不把300次重复推理当成300个训练种子或独立设备重复。
- 为验证专家路径，测量期间保留轻量 forward hook；G+B与Full各记录300次专家前向，其余三臂0次。因此当前Capacity专家确实参与推理，不能称零开销。
- G/G+F的旧序列化head缺少后来新增的专家路由布尔键。仅在确认无专家且有三个输入后，在内存补 local_expert_preserve_base=false，进入原有三尺度路径；其他选项与权重不改。补值记录逐臂保留。此表属于统一兼容运行时测量，不冒充每个历史原环境的原始FPS。

## FLOPs 与论证边界

后续完整算子测量已完成：Baseline/G/G+F/G+B/Full分别为105.597/105.804/109.280/130.575/134.051 GFLOPs，按640、batch1、MAC=2及声明的算术口径。详见[完整GFLOPs与成本合表](CURRENT_FULL_GFLOPS_ZH.md)。本次旧延迟JSON中的partial_only和完成标记中的full_model_flops_certified=false仅描述当时的部分profiler结果，原文件保留不改；新增证据另行归档。

这些固定输入、单机单次基准只说明本测量条件下的速度和成本，不能单独证明真实部署稳定帧率、等训练预算或算法统计显著性。当前证据可优先用参数与测得延迟说明成本，不借用旧版复杂度。

## 配对初始化与失败记录

复用原initial-state，重放两臂初始化：994个共有状态张量完全相等；19个新增状态项仅属于FIA；其残差系数为0。未执行训练。v1因误用旧模块导入名失败；v2测完baseline后，G因旧序列化head缺新布尔键而失败。v3修正测量入口后五臂全部完成，失败目录保留，不覆盖或伪造成功状态。

## 原始证据

- [完整效率 JSON（含1500个延迟样本）](../evidence/audit_remediation_20260915/efficiency/v3/efficiency.json)
- [完成标记](../evidence/audit_remediation_20260915/efficiency/v3/COMPLETE.json)、[初始化张量比较](../evidence/audit_remediation_20260915/efficiency/v3/initialization_probe.json)
- [逐文件传输SHA-256](../evidence/audit_remediation_20260915/efficiency/transport_manifest.json)、[实际执行脚本](../evidence/audit_remediation_20260915/efficiency/v3/measure.py)
- [v1失败日志](../evidence/audit_remediation_20260915/efficiency/v1/measurement.log)、[v2失败记录](../evidence/audit_remediation_20260915/efficiency/v2/FAILED.json)

脚本重建：在材料仓根目录执行 node scripts/build_current_efficiency_report.cjs；先验证传输哈希、完成状态、原始样本中位数和专家调用数，再生成本文。

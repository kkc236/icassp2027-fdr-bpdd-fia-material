# 当前 VisDrone batch=8 五臂推理效率

2026-09-16。已实际测量，不是按batch=1结果乘除估算；五臂均捕获模型真实输入为 **[8,3,640,640]、CUDA FP32**。联合模型原来的训练batch=8未改变，本次只测推理。

## 同条件八张批处理结果

| 模型 | 整批中位延迟 ms | 整批P90 ms | 每图摊销 ms | 吞吐量 images/s | 峰值分配显存 MiB |
|---|---:|---:|---:|---:|---:|
| Baseline | 59.559 | 59.731 | 7.445 | 134.321 | 795.960 |
| G | 66.200 | 66.460 | 8.275 | 120.846 | 803.028 |
| G+F | 69.044 | 69.213 | 8.630 | 115.868 | 870.184 |
| G+B | 104.897 | 105.138 | 13.112 | 76.266 | 942.949 |
| Full | 107.920 | 108.279 | 13.490 | 74.129 | 994.351 |

G=LRS-GFDR；B=Capacity-BPDD-v3-Safe整体模块；F=P3-only FIA。吞吐量=8000/整批中位毫秒数。每图摊销时间=整批时间/8，**不是单张请求的响应延迟**，不能以该摊销值宣称batch=1实时性能。全部采样时段的累计吞吐量也保存在JSON中。

## 与此前 batch=1 的对应结果

| 模型 | 原batch=1 ms/张 | 原batch=1 images/s | 本次batch=8 images/s | 吞吐比值 |
|---|---:|---:|---:|---:|
| Baseline | 30.592 | 32.688 | 134.321 | 4.109× |
| G | 42.788 | 23.371 | 120.846 | 5.171× |
| G+F | 43.849 | 22.806 | 115.868 | 5.081× |
| G+B | 85.415 | 11.708 | 76.266 | 6.514× |
| Full | 86.075 | 11.618 | 74.129 | 6.381× |

同一GPU型号/设备环境、软件版本、checkpoint、推理源码、640尺寸、FP32、TF32关闭、8 CPU线程及原生融合。batch=1复用9月15日原始测量，batch=8在9月16日新增；不是同一时刻交错测量，表中比值不单独证明所有负载下的提速。

## 测量合同

- GPU：NVIDIA GeForce RTX 4090；PyTorch 2.5.1+cu121；CUDA 12.1；Ultralytics 8.4.90。
- 显式输入8张固定seed的640×640 uint8 BGR随机图，各图不同；首图与旧batch=1生成规则相同。输入指纹在原始JSON。不是自然图像整套数据集评测，也不含AP评估。
- 每臂额外执行一次输入形状审计，随后预热100批、计时300批；共1500个整批样本、12000张计时图像。仅一轮固定输入微基准，不能当作独立设备/训练重复。
- CUDA同步墙钟计时：Ultralytics predict的预处理、模型和后处理；不含磁盘读取；conf=0.001、max_det=300，无TTA/额外NMS。
- 与旧测量相同，保留轻量专家前向计数hook；只在预热前审计输入shape，计时期间移除shape hook。G+B和Full各记录300次专家调用，每次实际处理8张。
- 显存为PyTorch峰值allocated/reserved，不等于nvidia-smi的整进程显存；reserved也见JSON。
- G/G+F仅复用之前已登记的旧head布尔键兼容补值；没有修改几何公式、chunk_size、权重、训练代码或预测策略。
- 五臂checkpoint前后指纹相同，八个核心源码文件前后及与旧batch=1一致。未训练、未处理UAVDT、未推送GitHub。

本次不是重测GFLOPs；既有134.051 GFLOPs等数值仍属于[声明的640单图完整前向口径](CURRENT_FULL_GFLOPS_ZH.md)。训练batch、推理batch、每图理论计算量三者不要混用。

## 可复核资料

- [完整原始结果与1500个整批耗时](../evidence/batch8_efficiency_20260916/v1/efficiency.json)
- [完成标记](../evidence/batch8_efficiency_20260916/v1/COMPLETE.json)、[独立重算验证](../evidence/batch8_efficiency_20260916/verification.json)
- [实际服务器测量脚本](../evidence/batch8_efficiency_20260916/v1/measure.py)、[运行日志](../evidence/batch8_efficiency_20260916/v1/measurement.log)
- [文件传输SHA-256与大小](../evidence/batch8_efficiency_20260916/transport_manifest.json)、[旧batch=1报告](CURRENT_COMPLEXITY_ZH.md)

重建：node scripts/build_batch8_efficiency_report.cjs。必须先通过原始传输文件校验、五臂配对、实际输入shape和统计重算，不能只凭日志的batch参数宣布完成。

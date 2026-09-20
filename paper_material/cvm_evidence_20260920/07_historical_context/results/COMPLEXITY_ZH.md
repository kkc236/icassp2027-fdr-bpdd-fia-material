# 历史版本：统一复杂度与实时性结果

> **本页不覆盖当前 Capacity-BPDD-v3-Safe Full。** 以下 checkpoint、25.21 FPS 和 BPDD 零新增推理开销均属于 2026-08-20 旧方法。当前 Capacity 专家参与推理，不能将本表改名使用。最新测量/待测状态见 [CURRENT_COMPLEXITY_ZH.md](CURRENT_COMPLEXITY_ZH.md)，旧原始记录保持不变。

四个论文配置已在同一台 NVIDIA GeForce RTX 4090、同一软件环境和同一 FP32 batch=1 协议下完成测量。延迟为完整 `predict` 路径的端到端时间，包含预处理、网络推理和后处理；每个模型预热 100 次、正式测量 300 次，并在计时前后执行 CUDA synchronize。FPS 定义为 `1000 / median latency(ms)`。

## 论文目标表

| 模型 | Params (M) | FLOPs (G) | Peak VRAM (MiB) | FPS | Latency median / P90 (ms) | AP75 | mAP50–95 |
|---|---:|---:|---:|---:|---:|---:|---:|
| RT-DETR-L Baseline | 32.827 | 108.032 | 233.8 | 28.85 | 34.66 / 35.29 | 0.21302 | 0.21911 |
| RT-DETR-L + FDR | 33.157 | 108.229 | 364.0 | 25.73 | 38.86 / 39.46 | 0.29253 | 0.28966 |
| RT-DETR-L + FDR + BPDD | 33.157 | 108.229 | 364.0 | 25.77 | 38.80 / 39.48 | 0.29810 | 0.29226 |
| RT-DETR-L + FDR + BPDD + FIA | 33.458 | 111.648 | 374.1 | 25.21 | 39.66 / 40.35 | 0.3042 | 0.2961 |

表中精度列保持用户确认的 A–E VisDrone val 口径；复杂度列绑定各行列出的 exact checkpoint SHA。BPDD 是否增加推理开销不依赖跨 authority 的精度比较，而由下面的严格配对 checkpoint 直接复核。

Params/FLOPs 按统一脚本在 predictor fusion 前对 checkpoint 原始架构统计，与既有静态报告口径一致。严格 BPDD 复评日志中的 `32,334,278 Params / 103.7 GFLOPs` 是 predictor 融合后的部署图摘要；两种数字作用不同，不应混为矛盾，也不影响 BPDD 两臂完全相等的结论。

## BPDD 推理开销严格配对

| 配对 checkpoint | Params | FLOPs | Peak VRAM | FPS | Median / P90 |
|---|---:|---:|---:|---:|---:|
| FDR strict-pair control | 33,156,614 | 108.229 G | 363.98 MiB | 25.72 | 38.887 / 39.416 ms |
| FDR+BPDD strict-pair | 33,156,614 | 108.229 G | 363.98 MiB | 25.77 | 38.802 / 39.480 ms |

两行的 Params、FLOPs 和峰值显存完全相等。FDR+BPDD 的中位延迟比配对 FDR 低 `0.085 ms`，P90 高 `0.063 ms`，均属于测量波动，不主张 BPDD 加速。可以稳定写成：**BPDD 只在训练期提供监督，不增加推理分支，也不引入推理参数、FLOPs 或可测的额外推理延迟。**

## FIA 额外成本

相对 FDR+BPDD，加入 FIA 后增加：

- `301,476` Params（`+0.91%`）；
- `3.419` GFLOPs（`+3.16%`）；
- `10.10 MiB` 峰值显存（`+2.78%`）；
- `0.861 ms` 中位端到端延迟（`+2.22%`），FPS 从 `25.77` 降至 `25.21`。

因此三模块仍保持约 25 FPS 的 batch=1 FP32 端到端速度。FIA 带来的计算成本较小，没有破坏实时性；论文中不应将本表的 FP32 端到端 FPS 与其他论文的 FP16、TensorRT、纯网络 forward 或不同输入尺寸速度直接排名。

## 冻结协议与证据

- `imgsz=640`、`batch=1`、FP32；固定 seeded uint8 RGB 输入；`conf=0.001`、`max_det=300`；
- 预热 100 次、正式测量 300 次；每次计时前后 CUDA synchronize；
- 环境：Python 3.10.12、PyTorch 2.5.1+cu121、CUDA 12.1、cuDNN 90100、Ultralytics 8.4.90；
- 原始 1,500 个延迟样本、checkpoint 哈希、模型图身份及环境信息见 [`../evidence/unified_complexity_20260820/unified_complexity_raw.json`](../evidence/unified_complexity_20260820/unified_complexity_raw.json)；机器汇总见 [`complexity_results.json`](complexity_results.json)。

首轮诊断因显式传入已弃用的 `half=False` 参数而在每次调用内打印警告，延迟被日志 I/O 污染，未进入材料。当前结果来自去除该参数后的干净复测；模型加载后显式转为 FP32，并由脚本校验参数 dtype。

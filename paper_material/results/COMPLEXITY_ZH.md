# 统一复杂度与实时性表

这张表用于回答两个问题：BPDD 的小幅增益是否值得，以及三个模块是否破坏 RT-DETR 的实时性。精度列采用当前 VisDrone val 登记结果；复杂度与速度列必须在同一硬件、同一软件环境和同一输入协议下重新测量。

## 论文目标表

| 模型 | Params | FLOPs | FPS | Latency | AP75 | mAP50–95 |
|---|---:|---:|---:|---:|---:|---:|
| RT-DETR-L Baseline | 待统一实测 | 待统一实测 | 待统一实测 | 待统一实测 | 0.21302 | 0.21911 |
| RT-DETR-L + FDR | 待统一实测 | 待统一实测 | 待统一实测 | 待统一实测 | 0.29253 | 0.28966 |
| RT-DETR-L + FDR + BPDD | 待统一实测 | 待统一实测 | 待统一实测 | 待统一实测 | 0.29810 | 0.29226 |
| RT-DETR-L + FDR + BPDD + FIA | 待统一实测 | 待统一实测 | 待统一实测 | 待统一实测 | 0.3042 | 0.2961 |

状态：`pending_unified_measurement`。服务器当前被占用，本机虽然有 RTX 4070 Laptop GPU，但现有 PyTorch 为 CPU-only，因此今天不把不同硬件或不同模型 authority 的旧速度拼成“统一实测”。机器合同见 [`complexity_results.json`](complexity_results.json)。

## 冻结测速协议

- 四个 checkpoint 在同一 GPU、同一功耗模式、同一 CUDA/cuDNN/PyTorch/Ultralytics 环境下测量；
- `imgsz=640`、`batch=1`、FP32（`half=False`）；
- 预热 100 次，正式测量 300 次，每次计时前后执行 CUDA synchronize；
- Latency 同时报中位数和 P90，范围包含 preprocess、network inference 与 postprocess；
- FPS 定义为 `1000 / median end-to-end latency(ms)`；
- Params 与 FLOPs 使用同一个 640×640 输入和同一统计工具；同时记录峰值显存；
- 不用 val/test 数据加载耗时替代模型 latency，不混用 batch=8 的评估速度与 batch=1 的实时性速度。

## BPDD 的复杂度判定

BPDD 只在训练期产生蒸馏监督，不增加推理分支。因而在同一 FDR 推理配置下，`FDR+BPDD` 的 Params、FLOPs、FPS 与 Latency 应与 `FDR` 一致；这不是用旧速度猜测，而是待统一测量复核的结构合同。若实测或模型统计不一致，优先视为配置/checkpoint 身份问题。

## 已有但不可填入主表的参考

- 严格静态报告记录 baseline 为 32,826,626 Params / 108.0318976 GFLOPs，FDR 为 33,156,614 Params / 108.2291200 GFLOPs。
- 三模块四位小数文本记录 32,635,754 Params / 109.0 GFLOPs，并分别记录 val/test 端到端 54.08/81.49 FPS；但硬件身份未绑定，且模型 authority 与前两行不同。

这些数字保留用于审计和发现异常，不进入“同硬件统一设置”论文表。测速完成后，只替换目标表中的“待统一实测”，不改动已冻结的 AP75/mAP 证据来源。

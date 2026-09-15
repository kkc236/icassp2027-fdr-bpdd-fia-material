# D-FINE-L VisDrone 跨协议最终记录（2026-09-15）

## 结论摘要

服务器上的 D-FINE-L batch=4、FP32、从头训练已完成 100/100 轮，训练进程已退出；本记录对应正式输出目录 `dfine-l-visdrone-bs4-scratch-cross-20260914`。验证集原生 D-FINE COCO AP 的全局最佳出现在第 93 轮（日志使用 0-based `epoch=92`）。

| 选择 | 轮次 | AP50-95 | AP50 | AP75 | 参数量 |
|---|---:|---:|---:|---:|---:|
| global best（用于外部对比） | 93 | 28.7726% | 47.1488% | 29.2692% | 30,715,991 |
| 最后一轮 EMA 快照 | 100 | 28.4742% | 46.6781% | 29.1343% | 30,715,991 |

上述百分比直接由 `test_coco_eval_bbox` 的原生 COCO 评测数组换算；完整逐轮日志保存在 `server_final_20260915/dfine_l_bs4_log.jsonl`，不能把末轮误写成 global best。

## 固定训练协议

- 官方 D-FINE 源码固定提交：`267a6da`；独立 D-FINE 环境，不注册为 Ultralytics 模块。
- VisDrone 10 类，项目既有 train/val/test 划分；输入 640×640，100 轮，seed=0，`pretrained=False`。
- 实际 batch=4，不做梯度累积；FP32（`use_amp=False`），AdamW，`lr=0.00025`，betas=(0.9, 0.999)，weight decay=0.000125。
- 骨干可训练（`freeze_at=-1`、`freeze_norm=False`），EMA 开启；配置见 `dfine_l_visdrone_bs4_scratch.yml`。
- 统一外部评测约定：PIL 直接拉伸到 640×640、无 TTA、无额外 NMS、原生输出最多 300 个候选，COCOeval 同时报告 maxDets=300/100。

## 权重与用途

Release 中的两个 `.pth` 均为已校验完整文件：

1. `dfine-l-visdrone-bs4-scratch-global_best.pth`：第 93 轮 global-best，跨协议主比较权重。
2. `dfine-l-visdrone-bs4-scratch-last_evaluated.pth`：第 100 轮末次 EMA 推理快照，用于 final/last 口径复核。

完整优化器恢复文件 `last.pth` 不是跨协议评分所必需，且体积显著更大，因此本次不上传；这不影响使用两个推理快照完成外部对比。若后续明确需要续训，再单独上传并记录其 SHA-256。

## 可比性边界

D-FINE-L 与 Ultralytics 联合模型的框架、优化器、AMP、有效 batch 和增强策略不同；因此应作为“外部 common-evaluation reference”，不能冒充同协议 leaderboard，也不能据此归因 FDR/BPDD/FIA 的单模块增益。论文中应同时给出 final 与 validation-best 两套结果，并保留协议差异表。

## 证据入口

- `server_final_20260915/dfine_l_bs4_run-authority.json`：权威配置、环境与源码哈希。
- `server_final_20260915/dfine_l_bs4_global-best.json`：global-best 元数据。
- `server_final_20260915/dfine_l_bs4_progress.json`：100/100 完成快照（其中 `status` 字段为旧进程遗留值，完成性以进程退出、逐轮日志和权重文件三者交叉确认）。
- `server_final_20260915/dfine_l_bs4_chronological-validation.jsonl`：按真实循环轮次记录的验证结果。
- `server_final_20260915/dfine_l_bs4_log.jsonl`：完整训练/验证 JSONL 日志。
- `DFINE_L_ASSET_MANIFEST_20260915.json`：Release 资产与证据 SHA-256 清单。

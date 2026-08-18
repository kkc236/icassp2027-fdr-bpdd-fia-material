# ACR-BPDD 最终评估入口

`scripts/evaluate_acr_bpdd_formal.py` 用于对完成 100 epoch 的
`fdr_acr_bpdd` Formal100 运行做独立最终评估。入口只部署普通 FDR 推理图；
ACR-BPDD 仍然是纯训练期机制。

## 运行条件

评估会在推理前失败关闭地核验以下 authority：

- `<run-dir>/acr-bpdd-run.json` 必须是 `variant=fdr_acr_bpdd`、
  `stage=formal`、seed 0 的冻结运行身份；
- `<run-dir>/acr-bpdd-epochs.jsonl` 必须恰好覆盖 completed epoch 1–100，
  每条身份一致且梯度有限；
- manifest 指向的 publication queue 必须恰好覆盖 epoch 1–100；
- `--publication-ledger` 必须恰好覆盖 epoch 1–100，每条均为 `verified=true`，
  且 ledger 的 queue-record SHA256 和 checkpoint SHA256 必须逐 epoch
  对应 queue；
- `--checkpoint` 只能是 queue 中 completed epoch 100 对应的
  `epoch99.pt`，文件内容 SHA256 必须一致；checkpoint 内 raw epoch 必须为
  99、optimizer 不得剥离，并且必须存在 EMA 或 model tensor state；
- 运行数据 YAML 的根目录、10 类名称和 val 路径必须与
  `--dataset-root` 一致。

示例：

```powershell
python scripts/evaluate_acr_bpdd_formal.py `
  --run-dir D:\runs\formal-seed0-fdr_acr_bpdd-v1 `
  --checkpoint D:\runs\formal-seed0-fdr_acr_bpdd-v1\weights\epoch99.pt `
  --publication-ledger D:\evidence\publication-ledger.jsonl `
  --dataset-root D:\datasets\VisDrone `
  --split val `
  --fdr-evaluation D:\reports\fdr-formal-val.json `
  --bpdd-evaluation D:\reports\bpdd-formal-val.json `
  --output D:\reports\acr-bpdd-formal-val.json `
  --device cuda:0
```

`--fdr-evaluation` 和 `--bpdd-evaluation` 均可省略。输出文件是
create-only；目标已存在时，入口会在加载 checkpoint 或执行推理前拒绝运行。

## 固定评估与性能协议

检测评估固定为 `imgsz=640`、`batch=8`、`max_det=300`、`NMS=False`，
并且只执行一次预测。P、R、F1、AP50、AP75、mAP50–95、
tiny/small/medium/large 以及 10 类 AP/AP50/AP75 都来自同一次预测缓存；
缺失任一要求指标都会失败，不会用 0、`null` 或其他估计值补齐。

性能评估会从同一 `epoch99.pt` 独立重载相同 tensor state，记录参数量、
GFLOPs，以及 FP16、batch 1、warmup 50、runs 200 的 mean/median/p95
延迟和按 mean latency 计算的 FPS。报告同时记录 GPU、Python、PyTorch、
TorchVision、Ultralytics、CUDA 和 cuDNN 信息。

## split authority 与比较口径

`val` 必须恰好包含 548 张图像。`test` 不使用 548 限制。两种 split 都会
记录图像数、标签数、总字节数、逐文件相对路径/字节数/内容 SHA256，
以及由“相对路径 + 文件内容 SHA256”组成的 split 聚合 SHA256。

任何参考 JSON 都只产生显式 `cross_run_difference`。报告顶层比较口径永远是
`comparison_scope=preliminary_cross_run`、`strict_paired=false`；入口不会因
参考 JSON 的自述而升级为 strict paired。参考中缺少尺度或类别指标时，对应
差值字段直接不生成。

## SHA256 inventory

`artifact_sha256_inventory` 覆盖全部不可变评估输入：run manifest、epoch
records、publication queue、publication ledger、checkpoint、训练数据 YAML、
已提供的参考 JSON，以及选定 split 的每个图像和标签文件。SHA256 inventory
不包含输出 JSON 自身，因为把文件自身摘要嵌入该文件会形成不可满足的自引用；
输出落盘后可由外部发布流程对最终 JSON 再计算 SHA256。

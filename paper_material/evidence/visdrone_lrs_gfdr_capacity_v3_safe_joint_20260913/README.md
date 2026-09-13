# VisDrone Formal100：LRS-GFDR + Capacity-BPDD-v3-Safe（含 FIA）

本目录是 2026-09-13 整理的可复现证据包，记录服务器上当前联合实验的完整结果，以及随后启动的 BPDD-only 对照。它只包含结果、启动参数、权威记录、配置和启动脚本；不包含模型权重、初始权重文件、数据集或缓存。

## 实验身份

| 臂 | 方法 | 状态 | 服务器输出目录 |
|---|---|---|---|
| Joint | `LRS-GFDR + Capacity-BPDD-v3-Safe + FIA` | 已完成 100/100 | `/root/sj-tmp/runs/formal-safe-capacity-fia-20260912-lrsv2/formal-seed0-capacity-v3-safe-fia` |
| BPDD-only | `LRS-GFDR + Capacity-BPDD-v3-Safe`（去除 FIA） | 运行中；尚无 epoch 结果 | `/root/sj-tmp/runs/formal-safe-capacity-bpdd-20260913-lrsv2/formal-seed0-capacity-v3-safe-bpdd` |

## Joint 已完成结果

`joint-results.csv` 共 100 行（epoch 1–100）。按 `metrics/mAP50-95(B)` 选出的 best 为 epoch 97：

| 选择 | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|
| best（E97） | 0.60482 | 0.49693 | 0.49890 | **0.30109** |
| final（E100） | 0.59526 | 0.50472 | 0.50005 | 0.30065 |

best 选择规则必须以验证集 `metrics/mAP50-95(B)` 为准；不要用最后一轮替代 best。

## 协议与可复现锚点

- 数据集：VisDrone，文件数 14,038；数据签名见两个 `*-authority.json`。
- 初始状态：统一 `seed=0` 的 `/root/sj-tmp/protocols/lrs-v2-f56b210/initial-state-seed0.pt`；本包只记录 SHA-256，不上传该文件。
- Formal100：100 epochs、batch 8、imgsz 640、MuSGD、`pretrained=false`、AMP、deterministic、`close_mosaic=10`、workers 8、`cache=false`、device 0。
- LRS-GFDR 使用现有几何可行域修复和 LRS-FGL（alpha=0.25）。Capacity-BPDD-v3-Safe 使用 localization KD，`loc_weight=0.15`，warmup 10–20、decay 80–100；classification KD 关闭（`cls_weight=0`）。联合臂额外启用 FIA；BPDD-only 不启用 FIA。
- `joint-authority.json` 与 `bpdd-authority.json` 是启动时写入的 authority record，包含配置、数据、初始状态、源代码 commit/tree hash 及冻结训练设置。

## 源代码对应关系

- Joint authority source commit：`a43056af2a843ec9bae109d3420367c13f3bcef6`。
- BPDD-only authority source commit：`5ef57473e89e3b91aa5236a18066aed99f5afc0f`。
- 代码仓库：`/root/sj-tmp/lrs-v2/bpdd-capacity-v2-fia-code`。
- 本目录同时保存两个配置、两个正式启动脚本以及 BPDD-only 的排队脚本，便于从上述 commit 复核。

## BPDD-only 当前状态

在本包生成时，远端父进程仍在运行（PID 39900，含 dataloader 子进程），`results.csv` 尚未生成，因此不记录任何尚未观测到的指标。完成后应从服务器下载完整 `results.csv`、最终 authority 和 best/last 权重的尺寸/哈希，再追加到新的完成证据提交中。

启动日志：`/root/sj-tmp/logs/formal-seed0-capacity-v3-safe-bpdd-lrsv2.log`。

## 传输与异常记录

BPDD-only 启动前曾存在一次不同源 commit 产生的 dry-run authority；该旧记录已在服务器保留为 `*.stale-dryrun-a43056af.json`，正式运行使用的 authority 是本目录中的 `bpdd-authority.json`，两者不可混用。

## 文件索引

- `joint-results.csv`：Joint 的逐 epoch 训练/验证曲线。
- `joint-args.yaml`、`bpdd-args.yaml`：Ultralytics 实际解析后的完整参数。
- `joint-authority.json`、`bpdd-authority.json`：数据、初始状态、配置和源代码身份锚点。
- `rtdetr-l-lrs-gfdr-capacity-v3-safe-bpdd-fia.yaml`、`rtdetr-l-lrs-gfdr-capacity-v3-safe-bpdd.yaml`：两个臂的模型配置。
- `train_lrs_gfdr_capacity_v3_safe_fia.py`、`train_lrs_gfdr_capacity_v3_safe_bpdd.py`：正式启动器。
- `queue_v3_safe_bpdd_after_joint.sh`：BPDD-only 启动脚本（当前已手动启动，脚本仅作复核材料）。


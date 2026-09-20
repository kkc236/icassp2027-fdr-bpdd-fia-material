# VisDrone Formal100：LRS-GFDR + Capacity-BPDD-v3-Safe（含 FIA）

本目录是 2026-09-14 更新的可复现证据包，记录服务器上当前联合实验的完整结果，以及最新完成的 BPDD-only 对照。它包含逐 epoch 结果、启动参数、权威记录、配置、启动脚本和权重校验信息；不包含模型权重、初始权重文件、数据集或缓存。

## 实验身份

| 臂 | 方法 | 状态 | 服务器输出目录 |
|---|---|---|---|
| Joint | `LRS-GFDR + Capacity-BPDD-v3-Safe + FIA` | 已完成 100/100 | `/root/sj-tmp/runs/formal-safe-capacity-fia-20260912-lrsv2/formal-seed0-capacity-v3-safe-fia` |
| BPDD-only | `LRS-GFDR + Capacity-BPDD-v3-Safe`（去除 FIA） | 已完成 100/100；独立 test 已完成 | `/root/sj-tmp/runs/formal-safe-capacity-bpdd-20260913-lrsv2/formal-seed0-capacity-v3-safe-bpdd` |

## Joint 已完成结果

`joint-results.csv` 共 100 行（epoch 1–100）。按 `metrics/mAP50-95(B)` 选出的 best 为 epoch 97：

| 选择 | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|
| best（E97） | 0.60482 | 0.49693 | 0.49890 | **0.30109** |
| final（E100） | 0.59526 | 0.50472 | 0.50005 | 0.30065 |

best 选择规则必须以验证集 `metrics/mAP50-95(B)` 为准；不要用最后一轮替代 best。

## 最新 BPDD-only 结果（2026-09-14）

服务器上的 v3-safe formal100 已完整写出 100 个 epoch。按验证集 `metrics/mAP50-95(B)` 选择 best 为 E80；E100 仅作为最终状态保留：

| 选择 | Epoch | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|---:|
| best | 80 | 0.59826 | 0.48524 | 0.48783 | **0.29277** |
| final | 100 | 0.60235 | 0.48596 | 0.48627 | 0.28939 |

原始逐 epoch 文件为 `bpdd-current-results.csv`，Ultralytics 实际解析参数为 `bpdd-current-args.yaml`，完整机器可读摘要为 `bpdd-current-completion.json`。best/last 权重不上传仓库，仅记录尺寸和 SHA-256，便于在服务器侧核验。

该臂已补充固定 test split 的独立精确评估：1610 张图、PIL 640、FP32、无 TTA/NMS，使用
`pycocotools.COCOeval 2.0.11`。maxDet=300 的 test mAP50–95 为 `0.2411058095`，maxDet=100
为 `0.2407863216`。V12 与 V13 是由同一工作流按同一数据、初始状态和训练主体协议部署的
FIA-off/on 受控组件对照；V12 test 与 V13 test 的差值可作为该对照的支持性观察。由于两次
启动记录保存的是不同时间点的源码提交，当前材料不宣称“字节级严格单变量因果增益”；严格的
FDR→FDR+BPDD 因果结论仍以 `bpdd_strict_pair_20260819` 为准。

## 协议与可复现锚点

- 数据集：VisDrone，文件数 14,038；数据签名见两个 `*-authority.json`。
- 初始状态：统一 `seed=0` 的 `/root/sj-tmp/protocols/lrs-v2-f56b210/initial-state-seed0.pt`；本包只记录 SHA-256，不上传该文件。
- Formal100：100 epochs、batch 8、imgsz 640、MuSGD、`pretrained=false`、AMP、deterministic、`close_mosaic=10`、workers 8、`cache=false`、device 0。
- LRS-GFDR 使用现有几何可行域修复和 LRS-FGL（alpha=0.25）。Capacity-BPDD-v3-Safe 使用 localization KD，`loc_weight=0.15`，warmup 10–20、decay 80–100；classification KD 关闭（`cls_weight=0`）。联合臂额外启用 FIA；BPDD-only 不启用 FIA。
- `joint-authority.json` 与 `bpdd-authority.json` 是启动时写入的 per-run authority record，包含配置、数据、初始状态、源代码 commit/tree hash 及冻结训练设置。
- `fia_controlled_pair_authority.json` 是两臂共用的 protocol authority：它把相同数据、初始状态和训练合同绑定到同一个 `protocol_authority_id`，同时原样保留两次运行各自的 source/config 哈希。这样可以做真实的 FIA-off/on 受控对照，不用“改哈希”伪造同一源码。

## 源代码对应关系

- Joint authority source commit：`a43056af2a843ec9bae109d3420367c13f3bcef6`。
- BPDD-only authority source commit：`5ef57473e89e3b91aa5236a18066aed99f5afc0f`。
- 代码仓库：`/root/sj-tmp/lrs-v2/bpdd-capacity-v2-fia-code`。
- 两次实验均由同一工作树和同一操作流程部署；提交号不同表示 FIA 运行前后代码处于不同时间点，
  不等于“换了实验人员或换了训练协议”。本目录保存两个配置、两个正式启动脚本以及 BPDD-only
  的排队脚本，便于继续做逐文件 active-path 复核。

## BPDD-only 复核状态

该臂已完成 100/100，并已完成独立 test。服务器启动日志为 `/root/sj-tmp/logs/formal-seed0-capacity-v3-safe-bpdd-lrsv2.log`；
权重校验、运行目录、配置和源代码身份均集中记录在 `bpdd-current-completion.json` 与 `bpdd-authority.json`。
test 报告见 `bpdd-independent-test-cap300.json`、`bpdd-independent-test-cap100.json` 和
`bpdd-independent-test-manifest.json`；服务器预测文件只保留 SHA-256，不上传原始预测大文件。

## 传输与异常记录

BPDD-only 启动前曾存在一次不同源 commit 产生的 dry-run authority；该旧记录已在服务器保留为 `*.stale-dryrun-a43056af.json`，正式运行使用的 authority 是本目录中的 `bpdd-authority.json`，两者不可混用。

## 文件索引

- `joint-results.csv`：Joint 的逐 epoch 训练/验证曲线。
- `bpdd-current-results.csv`：最新 BPDD-only 的逐 epoch 训练/验证曲线（E1–E100）。
- `bpdd-current-args.yaml`：最新 BPDD-only 的 Ultralytics 实际解析参数。
- `bpdd-current-completion.json`：best/final 指标、权重 SHA-256、运行目录和证据边界。
- `bpdd-independent-test-cap300.json`、`bpdd-independent-test-cap100.json`：固定 test split 的 COCOeval 报告。
- `bpdd-independent-test-report.json`：test 导出模型、checkpoint 和预测文件校验信息。
- `bpdd-independent-test-manifest.json`：test 评估协议、文件关系和服务器预测路径。
- `joint-args.yaml`、`bpdd-args.yaml`：Ultralytics 实际解析后的完整参数。
- `joint-authority.json`、`bpdd-authority.json`：数据、初始状态、配置和源代码身份锚点。
- `rtdetr-l-lrs-gfdr-capacity-v3-safe-bpdd-fia.yaml`、`rtdetr-l-lrs-gfdr-capacity-v3-safe-bpdd.yaml`：两个臂的模型配置。
- `train_lrs_gfdr_capacity_v3_safe_fia.py`、`train_lrs_gfdr_capacity_v3_safe_bpdd.py`：正式启动器。
- `queue_v3_safe_bpdd_after_joint.sh`：BPDD-only 启动脚本（当前已手动启动，脚本仅作复核材料）。

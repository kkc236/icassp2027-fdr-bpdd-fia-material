# LRS 系统 v2：服务器 Gate 0 与 Formal100 启动证据

日期：2026-09-06。该目录补充无服务器交付包之后取得的真实服务器证据，不能与完整 Formal100 结果混为一谈。

## 身份与初始化口径

- 材料父提交：`f2fb3d612016d718407a95d624a38b6b1b2c397b`。
- 实验源码：`uav-detection-baselines@f56b210798acab96d628308a5127a2e1399d00dc`。
- 方法修订：`v2-fp32-extent-logspace-ac-bpdd`。
- 四臂使用当前服务器按 seed 0 生成的一份公共初始化；不使用旧服务器状态，也不要求历史初始化哈希。
- 公共初始化 SHA-256：`935D68428BFC5848DE51F82844658ABBC7EC8C99CBBF6BBF823166D38CB65D5B`。
- F/G 加载后完整状态指纹相同；H/I 加载后完整状态指纹相同；四臂共享张量差异计数为 0。FIA 的 19 个私有张量由固定私有 seed 20000 初始化。

## 已通过的真实 Gate 0

在 RTX 4090、PyTorch 2.5.1+cu121、Ultralytics 8.4.90 上，F/G/H/I 均完成同一真实 VisDrone 增强批次的以下检查：

- 输入形状 `8×3×640×640`；
- CUDA FP16 autocast，GradScaler 初值与更新后均为 128；
- MuSGD 前向、反向和一次参数更新；
- loss、梯度、推理输出均为有限值，未发生 AMP 跳步；
- G/I 观察到 AC-BPDD loss，F/H 未观察到；
- 四臂共享初始化加载差异计数均为 0。

PyTorch 对 CUDA `grid_sample` backward 给出“无确定性实现”的警告。`CUBLAS_WORKSPACE_CONFIG=:4096:8` 已设置，但该警告仍需如实保留：本轮是相同代码、数据协议、初始状态和训练设置的严格同源对照，不宣称逐位复现。

## Formal100 状态

正式队列按 F→G→H→I 串行启动。上传本证据时 F 臂已经进入 epoch 1 并持续产生 `optimizer-evidence.jsonl`；完整 100 epoch、其余三臂和最终精度尚未完成，因此本目录不报告 AP 或涨点。

## 文件

- `GATE0_REPORT.json`：四臂真实 batch8/640/AMP128/MuSGD 单步原始报告。
- `DEPLOYMENT_STATUS.json`：服务器环境、数据集、源码、初始化、测试与队列状态快照。
- `authority/*.json`：四臂 Formal100 启动 authority，记录各自 YAML 与共同源码、数据集、初始化及冻结训练参数。

公共初始化 `.pt` 约 250 MiB，不提交到材料仓；其校验值、生成口径和张量分区保存在状态与 Gate 0 报告中。旧正式 checkpoint 仅作历史检查材料，没有被用作本轮四臂初始化。

## 本次材料校验

本目录 6 个服务器 JSON 均可解析，且 `SHA256SUMS` 与服务器原文件逐字节一致。复跑材料仓既有五文件测试集合得到 44 通过、1 失败；失败来自父提交已有的旧方法名扫描器命中 `no_server_correctness_v2_20260906/RUNBOOK_ZH.md` 和其中的 `source.zip`，不来自本目录。该既有负结果如实保留，不能写成本轮 45 项全绿。

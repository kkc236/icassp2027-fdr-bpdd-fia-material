# BPDD 严格配对补充实验

## 决策

这是投稿前唯一新增训练实验。状态为 **已完成训练**：FDR 与 FDR+BPDD 均已完成 100 epochs；best-val selection 的 P/R/AP50/mAP 已归档，AP75 与 test 仍待两个 `best.pt` 在冻结 evaluator 下独立精确复评。不追加第三数据集，也不强行做三种子。

目的不是追求更高绝对值，而是在同一源码提交、同一数据、同一 seed 和同一训练/评估协议下严格配对一次 `FDR` 与 `FDR+BPDD`，把 BPDD 的效果从跨 authority 算术观察升级为可信配对证据。

## 两个实验臂

| 项目 | FDR 对照 | FDR+BPDD 方法 |
|---|---|---|
| 源码 | 同一源码提交；运行前登记完整 commit | 与左列完全相同 |
| 模型差异 | FDR | 仅打开 BPDD 训练监督 |
| 初始化 | `pretrained=False` | `pretrained=False` |
| seed | `seed=0` | `seed=0` |
| 数据 | 同一 VisDrone YAML 及文件哈希 | 与左列完全相同 |
| 输入 | 640 | 640 |
| 训练 | 100 epochs；其余 optimizer、LR、增强、batch、workers 全部相同 | 与左列完全相同 |
| checkpoint | 按同一 val mAP50–95 规则选择各自 `best.pt` | 同左 |
| 评估 | 同一 evaluator，分别跑 val 与 test | 与左列完全相同 |

运行记录必须同时保存：源码 commit、配置文件 SHA-256、数据 YAML SHA-256、完整命令、环境版本、GPU、开始/结束时间、`results.csv`、`args.yaml`、`best.pt` 和 val/test 原始日志。

## 指标与判定

- 主要指标：`AP75`，用于检验 BPDD 是否改善边界定位质量。
- 次要指标：mAP50–95、AP50、Precision、Recall。
- 当前历史跨 authority 观察：AP75 从 `0.29253` 到 `0.29810`，约 `+0.557 pp`；mAP50–95 从 `0.28966` 到 `0.29226`，约 `+0.260 pp`。这两项只作为复现实验的背景参照，不预设新跑必须得到相同数值。
- 新表只报告两个新实验臂之间的配对差；不得拿旧 checkpoint 替代其中一臂，也不得跨 commit、数据 YAML 或 evaluator 拼接。

## 已完成结果

运行 authority 为源码提交 `848f00cb7a40907e3884885ecd5bbd474450758a`、protocol manifest SHA-256 `52c4e49e822100acf882e60562335d27ac5c24ba07bb26160a0f0c65c8c1ca24`、初始状态 SHA-256 `51aab2eb3fb7d123501c69c7b8dc90ff3ea0b9344a108edeef2c7d6dcdbb742d`。两臂均为 `seed=0`、100 epochs、`imgsz=640`、`batch=8`、`workers=8`。

| 配置 | best epoch | P | R | AP50 | AP75 | mAP50–95 |
|---|---:|---:|---:|---:|---:|---:|
| FDR | 97 | 0.58080 | 0.47923 | 0.48232 | 待 exact | 0.29047 |
| FDR+BPDD | 93 | 0.57937 | 0.49101 | 0.48657 | 待 exact | 0.29278 |
| 配对差 | — | −0.143 pp | +1.178 pp | +0.425 pp | 待补 | **+0.231 pp** |

这证明 BPDD 的总体 mAP 正增益在同 authority、同 seed 下成立。FDR 臂从其 authority-bound `last.pt` 在第 25 轮继续确定性训练至第 100 轮；该运行事实已在证据摘要中显式保留。原始产物及哈希见 [`../evidence/bpdd_strict_pair_20260819/strict_pair_summary.json`](../evidence/bpdd_strict_pair_20260819/strict_pair_summary.json)。

BPDD 只在训练期消费 FDR 的逐边分布并产生蒸馏损失，不增加推理分支。因此严格配对实验还应确认导出的 FDR 与 FDR+BPDD 推理图在参数量和 FLOPs 上一致；若不一致，应先排查配置或 checkpoint 身份，不能直接写入论文。

## 论文使用

正文现在可写“在同 authority、同 seed 的配对训练中，BPDD 将 val mAP50–95 从 `0.29047` 提高到 `0.29278`，提升 `+0.231 pp`”。AP75 在独立精确复评完成前仍保持为空，不能引用历史 `+0.557 pp` 作为新配对结果。BPDD 训练期工作、推理期不增加分支的结构结论保持不变。

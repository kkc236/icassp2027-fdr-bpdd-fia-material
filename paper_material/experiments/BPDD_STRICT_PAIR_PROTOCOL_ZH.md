# BPDD 严格配对补充实验

## 决策

这是投稿前唯一新增训练实验。状态为 **待执行**：当前服务器被占用，本页先冻结实验合同，不把现有跨 authority 数值冒充新跑结果，也不追加第三数据集或强行做三种子。

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

BPDD 只在训练期消费 FDR 的逐边分布并产生蒸馏损失，不增加推理分支。因此严格配对实验还应确认导出的 FDR 与 FDR+BPDD 推理图在参数量和 FLOPs 上一致；若不一致，应先排查配置或 checkpoint 身份，不能直接写入论文。

## 论文使用

在新实验完成前，正文可写“BPDD 的现有绝对结果为正，严格配对验证待补”，不可把 `+0.260 pp/+0.557 pp` 写成严格因果增益。完成后，用新跑的 AP75 与 mAP 差值替换这一边界说明，并保留 BPDD 训练期工作、推理期不增加分支的结构结论。

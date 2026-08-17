# 冻结实验协议

## 数据与模型

| 项目 | 冻结值 |
|---|---:|
| 数据集 | VisDrone |
| 训练集 | 6,471 张图像 |
| 验证集 | 548 张图像 |
| 类别数 | 10 |
| 基线 | Ultralytics RT-DETR-L |
| 初始化 | pretrained=False，从零训练 |
| 输入尺寸 | imgsz=640 |
| 查询数 / 解码层数 | 300 / 6 |
| 随机种子 | seed=0 |
| 正式训练轮数 | 100 epochs |

数据配置入口为 configs/VisDrone.yaml。FDR、FDR+BPDD 和 FDR+BPDD+FIA 分别使用各自独立配置与训练入口。任何包含 FIA 的结果必须额外绑定修改后 FIA 的源码身份，不能仅凭相同模型名、文件名或目录名认定实验兼容。

## 评估设置

严格 val/test 复评应显式固定：

- imgsz=640；
- batch=8；
- workers=8；
- conf=0.001；
- max_det=300；
- NMS=False；
- cache=False；
- half=False；
- rect=False；
- 单次 prediction pass；
- 同一数据集 YAML、类别映射和 evaluator 版本。

val 与 test 必须分别报告，不得跨 split 计算涨点。训练日志 best-val 只能描述 checkpoint 选择过程，不能替代冻结 evaluator 的独立复评。

## 当前证据合同

- RT-DETR-L、FDR、FDR+BPDD：保留现有可审计结果及各自证据等级。
- 旧 standalone FIA 与旧 FDR+FIA：属于模块修改前实验，证据全部撤销。
- 新 standalone FIA 与新 FDR+FIA：用户报告均为正增益，但尚未取得可审计数值，GitHub 当前可见内容中未找到可确认的新版资产。
- 新 FDR+BPDD+FIA：已定位正确 P3-only checkpoint；best-val 记录为 P=0.56996、R=0.49848、AP50=0.48982、mAP50–95=0.29618，相对当前 BPDD val 绝对值为 +0.3922 pp 的算术观察。AP75、test 和冻结 evaluator 独立复评仍待补。

## FIA 新结果的最低导入条件

1. 修改后 FIA 源码提交与配置 blob；
2. checkpoint 文件及其 SHA-256；
3. 数据集身份、环境版本和完整评估命令；
4. val/test 分开的结构化总体指标；
5. AP75、四尺度和十类别结果；
6. 对照臂身份与严格配对状态。

在满足这些条件前，新三模块记录只能作为正向 checkpoint 观察；单 FIA 与 FDR+FIA 不得填数。统一状态见 [FIA 结果状态](../results/FIA_RESULTS_STATUS_ZH.md)。

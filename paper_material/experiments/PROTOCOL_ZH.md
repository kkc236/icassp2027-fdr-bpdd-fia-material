# 冻结实验协议

## 数据与训练

| 项目 | 冻结值 |
|---|---:|
| 数据集 | VisDrone |
| 训练集 / 验证集 | 6,471 / 548 张图像 |
| 类别数 | 10 |
| 基线 | Ultralytics RT-DETR-L |
| 初始化 | pretrained=False |
| 输入尺寸 | 640 |
| 查询数 / 解码层数 | 300 / 6 |
| seed | 0 |
| 正式训练 | 100 epochs |

FDR、FDR+BPDD 与三模块使用各自独立配置。BPDD 必须依赖 FDR。FIA checkpoint 必须同时登记计算图身份，不能只按文件名判断。

## 统一评估器

standalone `best.pt` 的独立 val/test 复评显式固定：

- `split=val` 或 `split=test`，两个 split 分开运行和报告；
- `imgsz=640`、`batch=8`、`workers=8`；
- `conf=0.001`、`max_det=300`、`nms=False`；
- `cache=False`、`half=False`、`rect=False`；
- 同一 VisDrone YAML、10 类映射与 Ultralytics 8.4.90；
- checkpoint 统一选择 `best.pt`。

FIA-only 与 FDR+FIA 的 exact val/test 均按此协议从现有发布版 best checkpoint 独立得到。val 为 548 images / 38,759 instances；test 为 1,610 images / 75,102 instances。两个 split 不混算，且 standalone 与既有对照之间的算术差均不升级为 strict paired 因果效应。

## FIA 证据合同

| 实验臂 | 拓扑 | val | test |
|---|---|---|---|
| FIA-only | cascading，`model[23].f=-1` | exact independent best.pt val | exact independent best.pt test |
| FDR+FIA | cascading，`model[23].f=-1` | exact independent best.pt val | exact independent best.pt test |
| FDR+BPDD+FIA | P3-only，`model[23].f=21` | checkpoint embedded best-val | 归档终端截图舍入结果；独立 exact 待补 |

standalone 不再重训。其 val/test 算术差可用于普通消融描述，但不是 strict paired 因果效应。三模块的 P3-only val/test 正向观察与 standalone cascading 结果分开标注；三模块 test 只使用截图显示的 P/R/AP50/mAP，不反推 AP75 或 F1。

完整状态见 [FIA 结果状态](../results/FIA_RESULTS_STATUS_ZH.md)，机器协议与逐类别值见 [FIA best.pt 证据](../evidence/fia_existing_best_evaluation.json)。

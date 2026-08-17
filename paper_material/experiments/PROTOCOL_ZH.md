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
| FDR+BPDD+FIA | P3-only，`model[23].f=21` | 四位小数 val 文本 + checkpoint/截图互证 | 四位小数 test 文本 + 截图互证 |

standalone 不再重训。其 val/test 算术差可用于普通消融描述，但不是 strict paired 因果效应。三模块的 P3-only val/test 正向观察与 standalone cascading 结果分开标注；三模块四位小数文本已直接提供 P/R/F1/AP50/AP75/mAP 和十类结果，不再从截图反推缺失项。

完整状态见 [FIA 结果状态](../results/FIA_RESULTS_STATUS_ZH.md)，standalone 机器协议见 [FIA best.pt 证据](../evidence/fia_existing_best_evaluation.json)，三模块原始记录见 [val 文本](../evidence/fdr_bpdd_fia_val.txt) 与 [test 文本](../evidence/fdr_bpdd_fia_test.txt)。

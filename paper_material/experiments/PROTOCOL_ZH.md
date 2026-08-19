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

fresh P3-only FIA-only 与既有 cascading FDR+FIA 的 exact val/test 均按此协议对各自 `best.pt` 独立得到。val 为 548 images / 38,759 instances；test 为 1,610 images / 75,102 instances。两个 split 不混算；只报告各 split 的原始指标和明确给定的同 split 参照差值，不从 val/test 之间推导涨点。standalone 与既有对照之间的算术差均不升级为 strict paired 因果效应。

## FIA 证据合同

| 实验臂 | 拓扑 | val | test |
|---|---|---|---|
| FIA-only | P3-only：层 22 `f=-1`（上一层 21），层 23 `f=21`，decoder `[22,25,28]` | exact independent best.pt val | exact independent best.pt test |
| FDR+FIA | 既有 cascading：层 23 `f=-1` | exact independent best.pt val | exact independent best.pt test |
| FDR+BPDD+FIA | P3-only：层 23 `f=21`，decoder `[22,25,28]` | 四位小数 val 文本 + checkpoint/截图互证 | 四位小数 test 文本 + 截图互证 |

FIA-only 当前 checkpoint SHA-256 为 `c00cae89aaeb722854f8c845d14507c3598f75d509c2b12a3222b35a004157a6`，源码 SHA 为 `118ad631eff93ad806f85ea47819578e6e00bfc5`。它的 P3-only 身份由 raw graph 确认；旧 FIA-only cascading（层 23 `f=-1`）checkpoint 与负向结果已被取代。FDR+FIA 仍按既有 cascading checkpoint 登记，三模块仍按自己的 P3-only 记录登记。

各臂的 val/test 算术差可用于普通消融描述，但不是 strict paired 因果效应。三模块四位小数文本已直接提供 P/R/F1/AP50/AP75/mAP 和十类结果，不再从截图反推缺失项；fresh FIA-only 本次只登记已提供的总体精确指标，不扩写逐类结果或 test 差值。

完整状态见 [FIA 结果状态](../results/FIA_RESULTS_STATUS_ZH.md)。既有 [FIA best.pt 机器证据](../evidence/fia_existing_best_evaluation.json) 必须按 checkpoint SHA 核对，其中旧 FIA-only 记录只作历史；三模块原始记录见 [val 文本](../evidence/fdr_bpdd_fia_val.txt) 与 [test 文本](../evidence/fdr_bpdd_fia_test.txt)。

## 投稿前唯一新增训练实验

不追加第三数据集，也不强制三种子。唯一新增训练任务是在同一源码提交、`seed=0`、同一训练与评估协议下配对 `FDR` 和 `FDR+BPDD`，现已完成 100 epochs：best-val mAP50–95 为 `0.29047/0.29278`，BPDD 增益 `+0.231 pp`。AP75 与 test 待两个 `best.pt` 在冻结 evaluator 下独立精确复评；完整 authority、产物和哈希见 [BPDD 严格配对补充实验](BPDD_STRICT_PAIR_PROTOCOL_ZH.md)。

统一复杂度/实时性不需要训练，但四个 checkpoint 必须在同一硬件、同一 FP32 batch=1 协议下重新测量。目标表与机器合同见 [统一复杂度与实时性表](../results/COMPLEXITY_ZH.md)。

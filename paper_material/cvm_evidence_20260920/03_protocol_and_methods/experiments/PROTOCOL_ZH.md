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

## EQuAL Formal100 与采用门槛

EQuAL 的 raw runtime 标识为 `ACE-FDR/ace_fdr`，论文名称通过 alias 绑定为 EQuAL。正式 run 使用源码 `fca7763679b6e10ed68f98971a362a054ecd4853`、`seed=0`、`pretrained=False`、MuSGD、640、batch 8 连续完成 100 epochs；best epoch 为 91，checkpoint SHA-256 为 `06c5809af89c9a6b944f8615ac4a92c28322b36db6eb872c73407a58e54c3bca`。

同一个 `best.pt` 按本页统一 evaluator 各执行一次 val 和 test，禁止依据 test 重新选择 checkpoint。采用门槛为：val mAP 严格高于登记 AP-FDR、val AP75 不退化，并用 test mAP/AP75 检查方向。当前三项门槛均通过。该比较不是同一新源码提交下同时重跑的 fresh strict pair，因此只登记为同 split、同 evaluator 协议的非严格算术比较。

EQuAL 改变了分布锚点和监督组织。现有 AP-FDR+BPDD、AP-FDR+FIA 及 AP-FDR+BPDD+FIA checkpoint 不能改名复用；组合实验必须从 EQuAL 配置重新训练。最高优先级为 `EQuAL + BPDD`，通过后再生成完整 `EQuAL + BPDD + FIA` 结果。

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

不追加第三数据集，也不强制三种子。唯一新增训练任务是在同一源码提交、`seed=0`、同一训练与评估协议下配对 `FDR` 和 `FDR+BPDD`，现已完成 100 epochs 及两个 `best.pt` 的冻结 evaluator val/test 精确复评：BPDD 的 val/test mAP50–95 增益为 `+0.239/+0.283 pp`，AP75 增益为 `+0.072/+0.276 pp`。完整 authority、产物和哈希见 [BPDD 严格配对补充实验](BPDD_STRICT_PAIR_PROTOCOL_ZH.md)。

统一复杂度/实时性不需要训练，现已在同一 NVIDIA GeForce RTX 4090 上完成。四个论文 checkpoint 及严格 BPDD 配对 FDR 控制统一采用 `imgsz=640`、`batch=1`、FP32、预热 100 次、正式 300 次、逐次 CUDA synchronize；端到端延迟包含 preprocess、inference 与 postprocess，FPS 为 `1000/median latency`。目标表、机器汇总和原始样本见 [统一复杂度与实时性结果](../results/COMPLEXITY_ZH.md)。

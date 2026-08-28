# NA-FDR / LRS-FDR Formal100 证据包

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: validate
- Origin Date: 2026-08-28
- Verification Status: ANALYZED
- Source Commit: `9fa9078011d92cc23fc1f0eec06ff34983986ff0`
- Scope: VisDrone val、seed 0、100 epochs、三个独立 best checkpoint

## 名称与原始记录映射

| 论文名称 | 原始运行/文件标识 | 作用 |
|---|---|---|
| Original FDR | `original_fdr` | 历史原始 FDR 对照 |
| NA-FDR | `clean_fdr` / Clean FDR | 原生对齐基础设计、`w/o LRS` 内部消融 |
| LRS-FDR | `clean_fdr_plus_lrs_fgl` / `lrs_fdr` | 最终完整 FDR 模块 |

导入时只改变材料目录中的展示文件名，没有修改 JSON、CSV、YAML 的原始字节或其
内部历史标识。历史名称用于绑定运行与 checkpoint；论文正文统一使用 NA-FDR 和
LRS-FDR。

## 冻结评估协议

三个训练日志各自按最高 `metrics/mAP50-95(B)` 选择 best checkpoint，再由同一
冻结评估器各执行一次预测并复用缓存统计总体、十类别和四尺度指标：

- VisDrone val：548 张图、38,759 个目标；
- `imgsz=640`、`batch=8`、`workers=8`；
- `conf=0.001`、`max_det=300`、`nms=false`；
- FP32：`half=false`；
- `cache=false`、`rect=false`、`plots=false`；
- 单 seed 描述性消融，不提供显著性或稳定性结论。

## 总体结果

| 方法 | Best epoch | Precision | Recall | F1 | AP50 | AP75 | mAP50-95 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Original FDR | 92 | 0.570249 | 0.491417 | 0.527907 | 0.484700 | 0.294070 | 0.290698 |
| NA-FDR | 88 | **0.587045** | 0.498339 | **0.539067** | **0.493119** | 0.301061 | 0.296855 |
| LRS-FDR | 84 | 0.579512 | **0.500606** | 0.537177 | 0.491805 | **0.305773** | **0.296968** |

### 固定差值

| 对比 | ΔP | ΔR | ΔAP50 | ΔAP75 | ΔmAP50-95 |
|---|---:|---:|---:|---:|---:|
| NA-FDR − Original FDR | +1.680 pp | +0.692 pp | +0.842 pp | +0.699 pp | +0.616 pp |
| LRS-FDR − NA-FDR | -0.753 pp | +0.227 pp | -0.131 pp | +0.471 pp | +0.011 pp |
| LRS-FDR − Original FDR | +0.926 pp | +0.919 pp | +0.711 pp | +1.170 pp | +0.627 pp |

NA-FDR 相对 Original FDR 在全部总体指标上为正。LRS-FDR 相对 NA-FDR 只支持
AP75/Recall 取向的内部增益；`+0.011 pp` mAP 只是数值非负点估计，不能表述为
显著、稳定或全面提升。

## 尺度结果

尺度按网络输入坐标中的 `sqrt(area)` 定义：Tiny `<16`、Small `16--32`、
Medium `32--96`、Large `>=96`。

| 方法 | Tiny (20,860) | Small (12,420) | Medium (5,349) | Large (130) |
|---|---:|---:|---:|---:|
| Original FDR | 0.147025 | 0.291050 | 0.395473 | 0.380301 |
| NA-FDR | **0.157561** | **0.300759** | 0.400317 | **0.472407** |
| LRS-FDR | 0.149050 | 0.298944 | **0.400401** | 0.368274 |

LRS-FDR 相对 Original FDR 的 Tiny、Small、Medium mAP 为正；相对 NA-FDR 的
Tiny/Small mAP 分别下降 `0.851/0.181 pp`。Large 只有 130 个 GT，结果波动大，
不得用于核心机制主张。

## 训练末段与门检边界

- Epoch 91--100 平均 mAP：Original `0.289968`、NA-FDR `0.296102`、
  LRS-FDR `0.295253`；
- LRS-FDR 的末十轮斜率为 `-0.00024321/epoch`，不支持更高终末平台；
- LRS-FGL Gate0 在五个浅层全部通过，受益匹配占比 `33.6%--34.8%`，权重/数量
  比 `0.818--0.830`，受益边界饱和数为 0，最大守恒误差 `2.98e-8`；
- 预注册 strong GO 未通过；Tiny AP 门失败；低 IoU 下一层转移诊断未记录。

## Checkpoint 身份

| 方法 | SHA-256 |
|---|---|
| Original FDR best | `7F0F19D46AAC5C8A0629FCE275C9FE4CBDF3FA14A2ACAB7D0E6F10D3AD3776F1` |
| NA-FDR best | `87139A4AFBB85690A2B0EC48F382F902655FB58E20CE8E90C995DF3E1C236550` |
| LRS-FDR best | `BA5CDFFE8E2A0E147CE0D6D30CCBD3A0D25E31A7DCF69F8B247D2A079B492DFA` |

权重本体未进入 Git；哈希用于绑定服务器上的原始 checkpoint。

## 文件说明

- `independent-evaluation/comparison.json`：总体、类别、尺度及三组差值权威；
- `independent-evaluation/*.json`：每组冻结评估完整记录；
- `training/*_results.csv`：100 轮未经改写的训练日志；
- `authority/lrs_fdr_authority.json`：source/config/initial-state/dataset/协议身份；
- `authority/lrs_fdr_gate0.json`：训练前机制可行性门检；
- `authority/lrs_fdr_args.yaml`：原始训练参数；
- `MANIFEST.sha256`：本证据包文件字节校验。

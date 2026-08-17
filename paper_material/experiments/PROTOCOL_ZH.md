# 冻结实验协议

## 数据与模型

| 项目 | 冻结值 |
|---|---:|
| 数据集 | VisDrone |
| 训练集 | 6,471 张图像 |
| 验证集 | 548 张图像 |
| 类别数 | 10 |
| 基线 | Ultralytics RT-DETR-L |
| 初始化 | `pretrained=False`，从零训练 |
| 输入尺寸 | `imgsz=640` |
| 查询数 / 解码层数 | 300 / 6 |
| 随机种子 | `seed=0` |
| 正式训练轮数 | 100 epochs |

数据配置入口为 `configs/VisDrone.yaml`，其数据根现为仓库相对路径 `VisDrone`。FDR、FDR+BPDD 和 FDR+BPDD+FIA 分别使用 `configs/rtdetr-l-fdr.yaml`、`configs/rtdetr-l-fdr-bpdd.yaml` 和 `configs/rtdetr-l-fdr-bpdd-fia.yaml`。训练冻结值由 `scripts/train_rtdetr_fdr.py` 继承到 `scripts/train_rtdetr_bpdd.py` 与 `scripts/train_rtdetr_bpdd_fia.py`；数据集的 10 类设置在建模时覆盖模型 YAML 的通用 `nc` 占位值。

源码提交 `1d083140` 另补齐 FIA-only 与 FDR+FIA 的配置和入口，详见 [FIA 消融实验脚手架](FIA_ABLATION_SCAFFOLD_ZH.md)。这些入口证明消融拓扑可配置，但其默认 `workers=4`、分设备训练和 `split=test,batch=4` 验证参数不是本页冻结的最终论文比较合同；产生主表结果前必须显式对齐本页协议。

## 评估设置

严格 val 复评设置冻结如下；评估器支持相应选项时必须显式使用这些值，不得静默改写：

- `split=val`；
- `imgsz=640`；
- `batch=8`；
- `workers=8`；
- `conf=0.001`；
- `max_det=300`；
- `nms=False`；
- `cache=False`；
- `half=False`；
- `rect=False`；
- 同一 548 图 VisDrone val、同一图像预处理、同一类别映射和同一指标实现。

主表报告 Precision、Recall、AP50、AP75 和 mAP50–95。若某来源没有导出 AP75，必须标记“不可用”，不得从其他轮次、截图或相邻模型补值。

## 证据等级

| 等级 | 含义 | 允许的论文用法 |
|---|---|---|
| `strict` | 数据划分、训练 authority、评估器和比较合同满足严格配对要求 | 可报告同等级配对行的有符号差值 |
| `cross_authority_exact` | 指标保存为结构化精确数值，但与参照行不属于同一完整 authority | 可报告绝对值；跨行差只能称算术差，不能称严格配对增益 |
| `exact_single_arm` | checkpoint、协议和独立评估绝对值完整，但没有同 authority 配对对照 | 可报告该臂精确总体、尺度、类别和效率；不得把历史参考差写成因果增益 |
| `screenshot_rounded` | 仅有终端截图中的舍入显示值 | 使用 `≈`；不可恢复更多小数、缺失指标或精确差值 |

证据绑定以 `paper_material/evidence/source_manifest.json` 为准；表格机器值以 `paper_material/results/main_results.json` 为准；BPDD 与三模块的精确来源分别见 `paper_material/evidence/bpdd_val_exact.json` 和 `paper_material/evidence/fdr_bpdd_fia_val_exact.json`。

## 禁止混用

- 禁止将 val 与 test、development 子集与完整 val、不同图像数的划分相减。
- 禁止将不同源码提交、初始状态、训练协议、checkpoint 或 evaluator 的结果写成严格配对增益。
- 禁止用训练日志末轮指标替代统一独立评估，再与另一行相减。
- 禁止把精确绝对值自动解释成配对证据；数值精度与 authority 可比性是两个独立维度。
- 禁止从三位小数截图反推更多小数或统计显著性。

若后续补实验，必须先冻结 split、source commit、initial state、seed、checkpoint SHA-256、evaluator commit 与参数，再登记原始预测和指标 JSON。只有 authority 全部一致的行才能升级为 `strict`。

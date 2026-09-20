# CVM 论文证据冻结包

分支：`codex/cvm-evidence-20260920`。冻结基准：2026-09-19 完成的 **13 页、6 表、4 图、25 条参考文献**的 UAVDT 版论文。

## 先从哪里看

1. [当前论文](01_manuscript/MANUSCRIPT_CVM.pdf)及[独立 LaTeX](01_manuscript/main.tex)。
2. [表、图、结论到证据的映射](00_index/CLAIM_EVIDENCE_MAP_ZH.md)：按论文位置查原始结果。
3. [文献索引](00_index/REFERENCE_INDEX_ZH.md)与[图稿索引](00_index/FIGURE_INDEX_ZH.md)：区分原文版本、当前图源和备选图。
4. [证据状态说明](00_index/EVIDENCE_STATUS_ZH.md)：作者确认、源码核验和缺失材料分别记录。

## 目录

| 目录 | 内容 |
|---|---|
| `00_index/` | 证据映射、来源路径、文献和图稿索引、模型权重登记及校验结果 |
| `01_manuscript/` | 当前 PDF、单文件 LaTeX、原工程包、源文件、依赖和已有科学核验记录 |
| `02_evidence/` | 训练曲线、原始评估 JSON、五臂计时样本、GFLOPs 计数、源码恢复记录、完整 UAVDT 来包 |
| `03_protocol_and_methods/` | 方法说明、训练评估协议、测量脚本与对应测试 |
| `04_literature/` | 本地文献全文、版本说明、引用记录、实际阅读过的页图及图表设计分析 |
| `05_figures/` | 已采纳架构图的制作记录，以及尚未替换 PDF 的可编辑 HTML、低饱和配色方案 |
| `06_audits/` | 稿件检查、编译记录、审稿意见与编辑决策 |
| `07_historical_context/` | 旧结果汇总、交接文件、当前构建记录引用的原始前序文件；不作为最新数值入口 |
| `tools/` | 收集、清单生成与独立完整性核验工具；不运行模型 |

## 核验

在本目录运行：

```text
python tools/verify_evidence.py
```

该命令只读取冻结文件，不连接服务器、不训练、不加载 checkpoint。它核对全部清单内文件的 SHA-256、复制来源、论文文件、结论证据映射中的路径及文献全文指纹，以及 native test、UAVDT 和 1,500 条 batch=8 计时数据。论文原有的 122 个表格数值核验记录保留在 `01_manuscript/verification.json`。

文件目录与指纹见 [MANIFEST.json](MANIFEST.json)、[SHA256SUMS.txt](SHA256SUMS.txt)。所有复制件保持原字节；`.gitattributes` 禁止换行转换。

## 使用约定

- 当前 Full 的 UAVDT 身份按作者明确确认登记；源码快照和实际 checkpoint 配置核验的区别保留。
- 内部模块 test、旧 batch=1、失败候选和旧口径若出现在历史记录中，只作追溯；本次整理没有把它们加回论文。
- 当前 PDF 四张图的实际来源以图稿索引为准；可编辑 HTML 是后续资产，浏览器中未导出的临时编辑不属于本次文件冻结。
- 原始报告中的服务器绝对路径、较早文件链接与旧结论保留原样。追溯路径可查 `00_index/source_origins.json`；当前解释以本目录的新索引为准。
- 大型模型权重和完整数据集用登记表记录位置、已知指纹及可用性，不将历史同名权重当成当前 checkpoint。
- 这是研究证据分支，含作者内部核验材料；正式投稿使用匿名 PDF。本次整理不改变论文内容，也不构成新的模型复现实验。

# HF-D-FINE 涨点核验

核验日期：2026-08-21。

## 可直接引用的主结果

HF-D-FINE 正式发表于 *Image and Vision Computing* 165 (2026)，文章号 105834，DOI：<https://doi.org/10.1016/j.imavis.2025.105834>。

| 数据集 | 对照 | 指标 | 官方摘要报告的提升 | 建议论文写法 |
|---|---|---:|---:|---|
| VisDrone | D-FINE-S | AP / mAP50–95 | +3.2 | `+3.2 AP` 或 `+3.2 pp` |
| VisDrone | D-FINE-S | AP50 | +4.3 | `+4.3 AP50` 或 `+4.3 pp` |

注意：原文摘要使用 “increased by 3.2% / 4.3%” 的表述，但目标检测表格中的 AP 是百分制分数。比较论文时宜把它写成 **3.2/4.3 个 AP 点（pp）**，不要在缺少绝对基线值时换算成相对百分比。

## 目前不能从公开正式页面确认的数值

- ScienceDirect 公开预览没有给出 D-FINE-S 与 HF-D-FINE 的绝对 AP、AP50 数值。
- 公开预览没有显示 HF Hybrid Encoder、CAF、Outer-SNWD 各自的逐项消融涨点。
- 摘要确认实验覆盖 VisDrone、AI-TOD、UAVDT，但没有公开 AI-TOD 与 UAVDT 的精确涨点。

因此，材料中暂时只把 VisDrone 的 `+3.2 AP / +4.3 AP50` 当作可直接追溯到正式论文的定量结论；逐模块和另外两个数据集的数字需要取得全文表格后再补，不能由摘要或第三方解读反推。

## 方法构成

HF-D-FINE 明确写作 built upon D-FINE，新增三部分：

1. **HF Hybrid Encoder**：向编码器选择性注入骨干高分辨率特征，并通过通道压缩控制冗余。
2. **CAF**：结合跨尺度通道注意力与动态上采样，融合高分辨率细节和高层语义。
3. **Outer-SNWD**：结合 Shape-IoU 与 NWD，引入长宽比一致性惩罚和辅助框，改善微小目标回归。

官方摘要称这些设计只带来很小的 FLOPs 增量，但公开预览没有给出精确增量。

## 来源

- 正式论文页面：<https://www.sciencedirect.com/science/article/pii/S0262885625004226>
- DOI：<https://doi.org/10.1016/j.imavis.2025.105834>
- 作者代码：<https://github.com/HaveFun4ever/HF-DFINE>
- 本目录中的 `HF-D-FINE_Elsevier.xml` 与 `HF-D-FINE_Crossref.json` 保存了正式题录元数据。


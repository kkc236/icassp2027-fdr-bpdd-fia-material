# 图稿来源与当前采用状态

本索引对应 `01_manuscript/` 的当前主稿。实际嵌入由 [build.py](../01_manuscript/build.py) 决定：四张PNG以无损方式进入独立 `main.tex`。后续HTML和低饱和配色版均未替换当前PDF。

## 当前PDF采用的四图

| 图号 | 用途 | 当前PNG | 图注/插入源码 |
|---|---|---|---|
| 1 | 性能气泡图 | [bubble_comparison.png](../01_manuscript/assets/bubble_comparison.png) | [源码](../01_manuscript/source/figure_bubble.tex) |
| 2 | 尺度分布与解析几何动机 | [scale_and_geometry.png](../01_manuscript/assets/scale_and_geometry.png) | [源码](../01_manuscript/source/figure_motivation.tex) |
| 3 | 四面板总架构图 | [architecture_dense.png](../01_manuscript/assets/architecture_dense.png) | [源码](../01_manuscript/source/figure_overview.tex) |
| 4 | 完整模型十类别比较 | [class_comparison.png](../01_manuscript/assets/class_comparison.png) | [源码](../01_manuscript/source/figure_external_classes.tex) |

### 图1：性能气泡图

- [绘图脚本](../01_manuscript/source/build_bubble_figures.py)、[完整数据与来源](../01_manuscript/source/bubble_plot_data.json)、[外部点CSV](../01_manuscript/source/bubble_comparison_data.csv)、[重建说明](../01_manuscript/source/BUBBLE_FIGURES_README.md)。
- [FGHDet官方会议稿](../04_literature/cvm_papers/03_FGHDet_CVM2025.pdf)、[BDNet主文](../04_literature/comparison_candidates/sources/BDNet_CVPR2026.pdf)、[BDNet补充材料](../04_literature/comparison_candidates/sources/BDNet_CVPR2026_supplement.pdf)、[来源审计](../04_literature/research_notes/BUBBLE_DATA_AUDIT_ZH.md)。
- 外部六点为来源论文报告值，两个点为我方宿主和Full的native val结果。AP为0.50:0.95；泡面积表示GFLOPs。FGHDet的val精度与同名640架构成本跨表对应；不同论文训练和评估协议未统一。
- [SVG](../01_manuscript/assets/bubble_comparison.svg) / [PDF](../01_manuscript/assets/bubble_comparison.pdf) 为可复用导出。

### 图2：尺度与几何动机

- [绘图脚本](../01_manuscript/source/build_analysis_figures.py)、[统计重建脚本](../01_manuscript/source/build_motivation_figure.py)、[冻结统计](../01_manuscript/inputs/motivation_profile.json)、[548张图的转换后GT](../01_manuscript/qualitative/gt_reconstructed/instances_val.json.gz)。
- 左图是38,759个GT框经640×640拉伸后的尺度统计；右图是同尺寸框水平位移的解析IoU，不是检测错误分布或真实预测案例。
- [SVG](../01_manuscript/assets/scale_and_geometry.svg) / [PDF](../01_manuscript/assets/scale_and_geometry.pdf) 为导出。

### 图3：当前批准的四面板架构

- [当前PNG](../01_manuscript/assets/architecture_dense.png) 与 [批准图历史中的最终副本](../05_figures/approved_figure_history/gcdl_architecture_corrected.png) 内容一致，1448×1086。
- [采用和审查记录](../05_figures/approved_figure_history/REVIEW_ZH.md)、[初轮提示词](../05_figures/approved_figure_history/generation_prompt.txt)、[修订提示词](../05_figures/approved_figure_history/generation_prompt_v5.txt) 记录生成与修正过程。
- [源码参数审计](../04_literature/research_notes/FIGURE_PARAMETERS_SOURCE_AUDIT.json) 和 [结构语义审查](../04_literature/research_notes/STRUCTURE_SEMANTICS_REVIEW.json) 作为形成过程证据；其中早期面板映射应结合最终图注/采用记录解读，不能覆盖最终G(b)/F(c)编号。
- 当前批准图为栅格图。`previous_native_figure/` 中的SVG、PDF、生成脚本属于上一阶段图稿，不是这张PNG的精确矢量源。

### 图4：十类别比较

- [绘图脚本](../01_manuscript/source/build_analysis_figures.py)、[D-FINE完整结果](../01_manuscript/inputs/external_class_profile/source/dfine_final_test.cap300.json)、[Full完整结果](../01_manuscript/inputs/external_class_profile/source/joint_final_test.cap300.json)。
- 最终checkpoint、common evaluator、maxDet=300。类别AP差值先由未舍入数值计算，再显示；两模型训练配方不同。
- [SVG](../01_manuscript/assets/class_comparison.svg) / [PDF](../01_manuscript/assets/class_comparison.pdf) 为导出。

## 备选和历史图稿：不在当前PDF中

| 资产 | 路径与用途 | 当前状态 |
|---|---|---|
| 原生HTML编辑器 | [独立HTML](../05_figures/editable_html_not_in_pdf/architecture.html)、[SVG](../05_figures/editable_html_not_in_pdf/architecture.svg)、[2×PNG](../05_figures/editable_html_not_in_pdf/architecture-2x.png)、[说明](../05_figures/editable_html_not_in_pdf/README_ZH.md)、[验证](../05_figures/editable_html_not_in_pdf/verification.json) | 根据低饱和图重建，49节点、56连接，无栅格节点；可后续编辑，未替换论文图 |
| 低饱和配色最终图 | [最终PNG](../05_figures/muted_palette_not_in_pdf/architecture_muted_final.png)、[说明](../05_figures/muted_palette_not_in_pdf/README_ZH.md)、[来源记录](../05_figures/muted_palette_not_in_pdf/source_record.json)、[配色提示词](../05_figures/muted_palette_not_in_pdf/recolor_prompt.txt)、[箭头修复提示词](../05_figures/muted_palette_not_in_pdf/restore_mean_arrow_prompt.txt) | 独立配色方案，未替换论文图；当前只归档最终图及形成记录 |
| 内部五臂气泡图 | [PNG](../01_manuscript/assets/bubble_internal.png)、[SVG](../01_manuscript/assets/bubble_internal.svg)、[CSV](../01_manuscript/source/bubble_internal_data.csv) | 内部配置备选；不能充当外部SOTA比较 |
| 早期TikZ图 | [overview](../01_manuscript/figures/overview.tikz)、[lrs](../01_manuscript/figures/lrs.tikz)、[expert](../01_manuscript/figures/expert.tikz)、[selection](../01_manuscript/figures/selection.tikz)、[类别图](../01_manuscript/figures/external_classes.tikz)、[动机图](../01_manuscript/figures/motivation.tikz) | 保留早期结构/画法，不被当前build.py嵌入 |
| 批准图之前的候选 | [candidate_v4](../05_figures/approved_figure_history/candidate_v4.png)、[旧原生图目录](../05_figures/approved_figure_history/previous_native_figure/) | 形成过程证据，不代表当前批准图 |

## 文件指纹与编辑边界

- `01_manuscript/assets/architecture_dense.png`：`a870c6b4d2bd67ebe48715d7570fcfd439b6c725b96b3a854aa4bbdabc42f9ea`。
- `05_figures/approved_figure_history/gcdl_architecture_corrected.png`：`a870c6b4d2bd67ebe48715d7570fcfd439b6c725b96b3a854aa4bbdabc42f9ea`。
- `05_figures/muted_palette_not_in_pdf/architecture_muted_final.png`：`3eddc7d82fec7ca06ed2f95cf0b0d2817e8ea91b4c771675084bcb2bac596028`。
- `05_figures/editable_html_not_in_pdf/architecture-2x.png`：`2f608d8c589341e0d0f572783db546eeb90e6da06b84f7972251e467c902665d`。

- HTML版不声称与生成位图像素一致。其构建器、模板和JS模块已随目录保留；不能把PNG导出叫作可编辑矢量。
- 浏览器中的自动保存编辑状态只有另存为HTML后才进入文件归档；这里记录的是目录中已保存的资产。
- 图稿/研究记录中的原工作区绝对路径是历史来源信息；当前重建入口使用归档内主稿和各编辑目录，不能据旧路径名称推断文件已被采用。
- 当前四图的插入与无损编码依赖 [嵌入器](../01_manuscript/source/embed_raster.py) 和 [主构建器](../01_manuscript/build.py)。

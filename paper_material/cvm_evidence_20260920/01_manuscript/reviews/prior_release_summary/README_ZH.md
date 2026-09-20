# CVM 2027：同会全文研读与结构优化版

题目：**LRS-GFDR: Geometry-Feasible Distributional Refinement for UAV Detection**

本版把 LRS-GFDR 作为论文主贡献：分布表示来自 D-FINE，原创定位设计集中在几何可行解码与逐层监督分配。完整 FDR/FGL 移植版（Original FDR）是主要定位参照；Clean-FDR 是完整保留结果的中间配置。局部专家与共享 P3 作为定位核心的扩展。

应用定位：**面向无人机航拍监测，提供高精度目标检测与高速批量处理能力。**

## 一次粘贴使用

1. 在 Overleaf 新建空白项目。
2. 将本目录 main.tex 全文粘贴为项目的 main.tex。
3. 选择 pdfLaTeX 编译，直至交叉引用稳定；本地已在只有 main.tex 的空目录连续编译三遍验证。

main.tex 内嵌 CVM 官方样式、全部 TikZ 图和参考文献，不需要单独上传图像或 bib，不需要 BibTeX 或 shell escape。常用宏包由完整 TeX Live/MiKTeX 提供。也可导入 CVM2027_SUBMISSION_READY.zip，以根目录 main.tex 为主文件。

当前稿件采用 CVM 官方匿名审稿格式，12 页（含参考文献）、7 张表、6 张矢量图、11 个编号公式、19 篇参考文献。页数及最终准确状态见 verification.json 和 RELEASE_METADATA.json。

## 本轮实质变化

- 精读 CVM 2025/2026 官方程序中的六篇相关全文，先形成 STRUCTURE_AND_REVISION_BLUEPRINT_ZH.md，再据此改稿。
- 新增图 1：全部验证集标注的输入尺度分布，以及等尺寸框的解析位移—IoU 曲线。640×640 拉伸下 85.9% 的框等效边长小于 32 像素；这与原图 APs 的面积分组不同。
- 重写引言，让任务事实先于设计；区分任务动机、几何性质、历史配置结果和完整系统证据。
- 方法按“表示起点 → 几何解码 → 逐层监督 → 局部视觉扩展 → 训练/推理”组织。G 的两项规则各有独立主节；共享 P3、专家与选择性转移归入扩展。
- 相关工作补入更贴近航拍问题的 FGHDet 与 DASSF，替换两篇关联较弱的引用；保留 LME-DETR/SD-Net 及 FDR/FGL 归属。
- 全部既有指标、公式性质、负结果与比较边界保留。没有将标注统计当作模型错误率或模块因果证据。

## 数值与实验范围

定位主比较：Original FDR 29.078 AP → LRS-GFDR 29.620 AP，差值 +0.542。Clean-FDR 29.696、Clean-FDR + geometry 29.361 全部保留；历史配置并非全部同源同初始化单因素实验。

完整模型：native test AP 23.604，对 Baseline +5.861；common final test AP 24.133，对 scratch-adapted D-FINE-L +1.579。两类评估值分别解释，D-FINE 与 Full 的训练配方和有效 batch 差异在协议中披露。 D-FINE-L 在本文训练配置下以 physical batch=8 在 RTX 4090 24 GB 上发生显存不足，因此改为 batch=4；此原因由作者本轮确认，解释批大小调整，不将其扩大为其他配方差异的原因。

效率：RTX 4090、640×640、FP32、batch=8；Full 中位整批 107.920 ms，吞吐量 74.129 张/秒。13.490 ms 为每图摊销成本，不是单请求响应延迟。共同精度评估器的 batch=1 是评估配置，不是 batch=1 测速。

没有新增训练、模型推理、权重修改或外部投稿。内部组件仅 val；test 保留完整模型。本版按用户选择不含逐图预测案例。UAVDT 待未来当前版本数据到位后另加，不占位造数。

## 文件与审阅记录

| 文件/目录 | 用途 |
|---|---|
| main.tex | 可直接粘贴并编译的完整论文 |
| MANUSCRIPT_CVM.pdf | 编译后的匿名审稿稿件 |
| source/body.tex | 英文正文可编辑源文件 |
| STRUCTURE_AND_REVISION_BLUEPRINT_ZH.md | 六篇全文的启示、唯一主线与各章节/图表职责 |
| build.py / figures/ | 表格组装与可编辑矢量图 |
| inputs/ | 冻结数据、源码、原始训练 CSV 和证据索引 |
| reviews/ | 独立审稿、技术检查、同会论文分析与终审 |
| REVISION_NOTES_ZH.md | 修改与验收摘要 |
| ADVERSARIAL_AUDIT_ZH.md | 逐项问题处理与仍需更多证据的边界 |
| verification.json / RELEASE_METADATA.json | 独立编译、数据核验、视觉检查与打包记录 |
| qualitative/ | 用户排除于本版的可选未来逐图工作流 |

持续改稿请编辑 source/body.tex、build.py 的表格或 figures/，再运行 build.py；组装会覆盖 main.tex。图 1 可从冻结 GT 用 source/build_motivation_figure.py 重建。公式检查和 GT 统计不运行模型。

## 投稿前最后的用户信息

投稿系统生成编号后，将 `\def\cvmPaperID{****}` 中的星号替换为真实 paper ID。匿名行号与审稿标尺保留。没有执行外部投稿。

工程 ZIP 包含作者用的证据及审稿记录，不应直接当匿名补充材料上传；正式论文文件是 MANUSCRIPT_CVM.pdf。本文的写作、证据组织和技术准确性已改进，录用仍由真实证据、审稿标准和竞争稿件决定，不能承诺概率或结果。

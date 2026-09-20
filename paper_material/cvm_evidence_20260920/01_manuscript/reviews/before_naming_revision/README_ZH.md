# CVM 2027：实验身份与精度成本呈现优化版

题目：**LRS-GFDR: Geometry-Feasible Distributional Refinement for UAV Detection**

本版将 LRS-GFDR 定位为主要贡献：在明确归属 D-FINE 的分布表示上，作者重新组织 incoming reference 与监督路径，并提出几何可行解码和逐层权重分配。局部视觉专家与共享 P3 是核心之上的扩展。

应用定位：**面向无人机航拍监测，提供高精度目标检测与高速批量处理能力。**

## 一次粘贴使用

1. 在 Overleaf 新建空白项目，将本目录 main.tex 全文粘贴进去。
2. 选择 pdfLaTeX，编译直至交叉引用稳定。本地已用只有 main.tex 的空目录连续编译三次。
3. 投稿系统分配编号后，替换 `\def\cvmPaperID{****}` 的星号；保留匿名审稿格式与行号。

main.tex 内嵌官方样式、全部 TikZ 图和参考文献，不需要外部图片、BibTeX 或 shell escape。完整 TeX Live/MiKTeX 提供常用宏包。也可导入 CVM2027_SUBMISSION_READY.zip。

当前：**12页（含参考文献），7表、6图、11个编号公式、19篇参考文献**。没有执行外部投稿。工程 ZIP 含作者证据、原始路径和内部审阅记录，应作为作者工程使用，不能直接当匿名补充材料上传。

## 本轮变化

- 将原 Clean-FDR 显示为作者组内的 **Path redesign**。四行分成“移植参照”和“作者定位变体”；保留29.696 AP最高值及全部原数值。旧alias和冻结文件不变，映射见 inputs/publication_name_mapping.json。
- 方法新增 reference/supervision 段，摘要、贡献和机制表同步交代作者的路径设计。preliminary head及stock DN实际仍保留，固定分布坐标系的继承归属也保留。
- 合并五臂精度、参数、GFLOPs、整批耗时及吞吐量为同一张表；G+B / Full用同一标记说明最直接匹配的比较。全部负结果仍可见。
- 外部比较明确common/native、final/best与复现身份；附录补齐既有val/test×final/best×cap100/300共八组完整模型记录。16份源JSON与原manifest一致，未重新运行模型。
- 主线和实验取舍的理由见 EXPERIMENT_DESIGN_DECISIONS_ZH.md；它连接具体文献表格、误读风险和落实决定。

## 主要数值与范围

完整 FDR/FGL 移植参照29.078 AP；作者Path redesign29.696、+geometry29.361；LRS-GFDR29.620。最终核心相对移植+0.542，低于作者路径变体0.076 AP。几何性质与AP增益分开论证，历史版本不宣称全部为同源同初始化单因素实验。

Full native test AP23.604，对RT-DETR-L+5.861；common final test AP24.133，对scratch-adapted D-FINE-L+1.579。八组合差值+1.550至+2.027均来自未舍入原值。附录不改变final test@300主终点，也不把重复评分当独立试验。

D-FINE-L在本文训练设置下，RTX4090 24GB physical batch8显存不足，改为4；这是作者确认的原因。本说明不消除Full effective batch约64与D-FINE effective4、优化器、精度和增强的差异。

效率仅报告640×640、FP32、RTX4090、batch8：Full107.920 ms/整批、74.129张/秒。13.490 ms是摊销成本，不是单请求延迟。G为120.846张/秒；Full相对G增加0.489 val AP及26.70% GFLOPs。common accuracy evaluator中的batch1是评估设置，不是batch1测速。

内部模块只使用val；test仅用于完整模型。未新增训练、模型推理、权重修改、服务器连接、UAVDT或逐图预测案例。

## 文件入口

| 文件 | 用途 |
|---|---|
| main.tex / MANUSCRIPT_CVM.pdf | 独立可编译源与匿名审稿PDF |
| EXPERIMENT_DESIGN_DECISIONS_ZH.md | 当前叙事、实验角色和取舍决策 |
| research/*.md | 定向文献阅读、源码身份、完整性核查；不把第三方论文文件放入工程包 |
| source/body.tex / build.py / figures/ | 可编辑正文、表格与矢量图；build会覆盖main.tex |
| inputs/ | 原始证据、新旧名称映射、16份外部评分JSON和哈希索引 |
| reviews/ | 当前独立审读和历史记录，精确版本由对应哈希识别 |
| verification.json / EDITORIAL_CHECKS.json / RELEASE_METADATA.json | 数值、编译、视觉和工程打包验收 |

论文仍受单数据集、单seed、历史配置匹配范围与外部训练配方差异限制。此次完善贡献表达和证据呈现，不承诺录用概率。

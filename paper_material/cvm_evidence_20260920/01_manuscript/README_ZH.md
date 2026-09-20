# CVM 论文：加入 UAVDT 第二数据集

本版在已批准架构图版本的基础上加入 UAVDT；模型身份按作者于 2026-09-19 的明确确认标为 **Full (ours)**。

## 使用

- `MANUSCRIPT_CVM.pdf`：13 页论文，含附录、参考文献。
- `main.tex`：可独立编译的单文件 LaTeX，已内嵌模板、四张图和参考文献，无需另外上传图片或执行 BibTeX。
- `CVM2027_SUBMISSION_READY.zip`：完整编辑及复核材料。
- `CVM_FIGURES.zip`：现有图稿。

将 main.tex 放入空目录，用 pdfLaTeX 连续编译三次，或在 Overleaf 选择 pdfLaTeX 编译。Windows 和类 Unix 系统也可分别使用附带的 compile.ps1、compile.sh。

修改正文可编辑 source/body.tex；本次表格位于 source/table_uavdt.tex。运行 build.py 重新生成 main.tex。修改后运行 verify.py 可在空目录检验独立编译和冻结数值，依赖见 requirements-verification.txt。验证会将视觉状态重置为 pending，交付前需重新检查页面。

## 本次变化

- 新增第 4.3 节 Results on UAVDT 和表 2：总体 AP/AP50/AP75 及 car/truck/bus 的 AP。
- Full 相对包内 baseline：AP 14.12 → 16.96，AP50 24.21 → 29.16，AP75 14.97 → 17.50。
- 摘要、引言、贡献描述及结论同步加入第二数据集结果。
- 新增 UAVDT 原始 ECCV 2018 文献，参考文献由 24 条增至 25 条。
- 原 VisDrone 结果、图稿和效率数值保留。摘要明确 74.129 images/s 来自 VisDrone 配置，避免误认为本次 UAVDT 实测速率。

## 证据状态

Full 身份来自作者直接确认，记录在 inputs/uavdt/author_confirmation.json。包内代码为较早实现，未包含实际 checkpoint 元数据；表注保留配置对应关系不能独立验证的说明。当前本地 val 划分与官方 UAVDT 划分的映射也尚未核实。

本版未重训、未重新测评，未将本包 batch=4 验证速度替换到现有 batch=8 效率表。inputs/uavdt/ 下保留原始报告、脚本和检阅记录，先前检阅报告中的待确认身份状态应结合更新后的作者确认记录阅读。

## 投稿前

`cvmPaperID` 仍为 `****`，需替换为真实投稿编号。压缩包包含供作者编辑和复核的材料，不代表已完成正式提交；匿名 PDF 保持匿名。UAVDT 实际运行配置与数据划分信息仍需在正式提交前补齐。

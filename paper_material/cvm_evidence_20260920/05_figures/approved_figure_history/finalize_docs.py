from pathlib import Path
import json

R = Path(__file__).resolve().parents[1]
readme = r'''# CVM 2027：确认采用的结构图修正版

2026-09-19。本版在用户确认的四面板构图上修正连线，已放入论文第 4 页。

## 直接使用

- 阅读 `MANUSCRIPT_CVM.pdf`：12 页，含附录和参考文献；4 图、5 表、11 个编号公式、24 篇参考文献。
- `main.tex` 为可直接复制的单文件 LaTeX，内嵌官方样式、四幅图片和参考文献。选择 pdfLaTeX，编译至引用稳定（本地验证为三次）。不依赖外部图片、BibTeX、Python、网络或 shell escape。
- `CVM2027_SUBMISSION_READY.zip` 是作者工程包，包含来源材料；不是已完成投稿，也不应原样作为匿名补充材料上传。
- `CVM_FIGURES.zip` 收录当前图片。当前结构图为 PNG，其他统计图保留原有 SVG/PDF 源。

## 本次修正

1. (a) final query 从 Attention + FFN 独立引出，在 B 前与基础预测汇合；共享特征输入保持独立。
2. (b) 固定参考 r0 的线连续进入 Reference + offsets，避开 G.2 标题。
3. (d) 教师明确为停止梯度的 base edge logits + edge residual。
4. 正文同步为 G(b)、F(c)、B(d)，P3* 统一；图中质量符号 s_i 与正文 q_{l,i} 的关系已说明。
5. 图注定义共享输入来源、固定解码参考与动态注意力参考，并说明省略标准检测损失。

## 核验结果与图像格式

- 12 页渲染已检查；第 3–5 页另外复核图文衔接。没有溢出、未定义引用或缺字。
- 104 个表格数字及原有数值一致性核验通过；实验正文和附录没有改动，未训练或运行模型。
- 当前结构图 `assets/architecture_dense.png` 为内置 imagegen 编辑生成的 **1448×1086 栅格 PNG**，并非矢量图。全宽放置；最小辅助标签需放大查看。无损嵌入不等于增加源图细节。
- 图的生成提示词与审阅记录在 `figure_revision/`。旧矢量结构图另存于 `figure_revision/previous_native_figure/`，不属于当前图，也未打包成当前图的可编辑版本。
- 官方审稿模板、匿名模式和行号保持原样；投稿时需填入实际 paper ID。

历史分析文件沿用上版存档，其关于旧构图或全部图可编辑的描述不适用于本版；以本说明、当前 PDF 和 RELEASE_METADATA.json 为准。
'''
dependencies = r'''# Dependencies

## Compile the delivered paper

Only main.tex and a standard pdfLaTeX installation are needed. Three official CVM style files, four lossless RGB image streams and the bibliography are embedded. No external image, BibTeX, shell escape, Python or network access is required. Compile three times for references and page backreferences.

Standard packages: fontenc, times, graphicx, amsmath, amssymb, booktabs, array, balance, xcolor, tikz and hyperref. The official styles remain unchanged. Compiler validation is recorded in verification.json.

## Optional author editing

- Reassemble main.tex: Python 3 + Pillow; run python build.py. This uses the current delivered PNG files.
- Independent verification: Python 3 + Pillow + pypdf and pdfLaTeX; run python verify.py.
- Statistical plots: use their supplied SVG/PDF sources or matplotlib builders. Their data are retained.
- Current architecture: raster PNG, 1448x1086, edited with the built-in imagegen tool. There is no vector source for this version. The prompts are supplied in figure_revision. The old architecture builder and vector files are archived separately and must not be used to regenerate the current architecture.
- Package reviewed outputs: python package_approved_release.py. It requires completed visual QA in verification.json and verifies archive extraction and source assembly.

Neural-model execution is not needed to rebuild the manuscript. Source paths in evidence records are provenance, not paper-compilation dependencies.
'''
review = '''# 结构图采用记录

日期：2026-09-19。用户确认保留上版四面板构图，修正连接和表述后采用。

最终文件：assets/architecture_dense.png；同内容副本：figure_revision/gcdl_architecture_corrected.png。
最终 PNG：1448×1086。内置 imagegen 编辑模式，未使用 API/CLI 回退。两轮提示词均已保存；第二轮以前一轮输出为编辑对象。工具未按提示词请求输出更大像素，故如实记录实际尺寸，不通过简单放大声称高清或矢量。

审查结果：
- final query 从 Attention + FFN 独立绕过两个 heads，在 B 前以实心节点汇合。
- 固定参考 r0 连续进入 Reference + offsets 顶部，不穿过 G.2 标题。
- 教师为 sg(base edge logits + edge residual)，不是残差单独作为目标。
- G 的累计、中心旁路、extent floor、动态 attention reference 与 F 跳连保留。
- 新图编号 G(b)/F(c) 与正文和图注一致。
- 共享特征采用命名输入，来源在图注中明确，不增加冗长的交叉连线。

独立视觉复核通过。最终 PDF 第 4 页通栏使用；第 3–5 页图文衔接复核通过，12 页缩略总览无越界或异常空页。主代理另查看完整第 4 页。最小辅助文字偏小，但主结构、公式与图注可辨。
'''
for name, content in [('README_ZH.md',readme), ('DEPENDENCIES.md',dependencies),
                      ('REVISION_NOTES_ZH.md',review), ('VISUAL_REVISION_ZH.md',review),
                      ('figure_revision/REVIEW_ZH.md',review)]:
    (R/name).write_text(content, encoding='utf-8')
for name in ['package_visual_release.py','package_release.py']:
    (R/name).write_text('from pathlib import Path\nimport runpy\nrunpy.run_path(str(Path(__file__).resolve().parent / "package_approved_release.py"), run_name="__main__")\n', encoding='ascii')
v = json.loads((R/'verification.json').read_text(encoding='utf-8'))
assert v['pages'] == 12
v['visual_review'] = 'passed_all_12_pages'
v['visual_review_details'] = {'overview_page': 4, 'overview_checked_full_page': True,
                             'all_page_contact_sheet_reviewed': True,
                             'independent_transition_pages_reviewed': [3,4,5],
                             'architecture_raster_pixels': [1448,1086],
                             'limitation': 'Small auxiliary labels require zoom; no vector source.'}
(R/'verification.json').write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8')
print('Documentation and visual QA record updated.')

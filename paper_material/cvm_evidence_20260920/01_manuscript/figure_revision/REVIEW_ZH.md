# 结构图采用记录

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

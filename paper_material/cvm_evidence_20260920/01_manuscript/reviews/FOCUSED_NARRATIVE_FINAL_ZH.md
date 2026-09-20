# 聚焦叙事终审：4.2 至附录与第 7–12 页

日期：2026-09-17。范围限于 `source/body.tex` 第 4.2 节至附录，以及实际通过 `view_image` 查看并输出给审阅者的 `qa/pages/page-07.png` 至 `page-12.png` 六张页面。未重新审计旧运行、扩展文献检索或修改稿件；第 1–6 页由主任务审阅。

## 结论

**通过；未发现必要 P1 / P2 修复。**

### 内容与解释范围

- 主文 `body.tex:243–245` 仍说明 transfer reference 含作者的 RT-DETR host integration，并保留 D-FINE 表示及 fixed-frame 归属；+0.542 AP 明确用于整体定位设计比较。
- 主文没有隐去较高的 path-only AP：明确写出 29.696、GCDL 低 0.076 AP / 高 0.062 AP50，并引用附录 A 的完整比较和历史 source-matching scope。
- 附录 A / Table 6 保留四行全部数值、geometry 行的负差值、最高值加粗和“并非全行同源码/初始化严格配对”的范围说明。没有把历史运行标为无效，也没有把几何规则的独立精度收益写成已证实。
- `:247–248` 与附录 B 区分几何算子性质、合成数值检查和检测精度；保留 FP16 最小输入下溢的例外说明，没有由测试通过推断真实坏框率或收敛收益。
- `:257` 的 F 分支结果限于已有最直接配对的 expert-equipped 配置；其余历史行仍说明不能建立 expert-and-supervision bundle 的独立收益。“raises AP”在该段没有扩展成普遍因果保证。
- 主文 Scope 保留一个数据集/一个 seed、历史版本非逐项隔离、expert 与监督联合评估、外部训练配方不同；附录 C 明确八行不是独立试验或统计显著性证据。范围说明足够，无需恢复重复限制句。

### 实际视觉核查

| 页 | 检查结果 |
| --- | --- |
| 7 | Eqs. (8)–(11)、选择规则、训练目标和实验标题清晰；无越栏、重叠或裁切。 |
| 8 | Figure 5 流程及 caption 完整；4.2 标题保持完整单行，并接有足量正文。 |
| 9 | 4.2 的主结果与附录指引、4.3 组件比较和 4.4 成本段落可读，节标题没有严重孤立。 |
| 10 | Tables 2–5、相关正文引用及结论起始段清楚；表头与数值对齐，无碰撞。 |
| 11 | Figure 6 完整；附录 A、B、C 按顺序出现。A 引用 Table 6、C 引用 Table 7；B 跨栏续接可辨认。References 标题后有完整首条文献。 |
| 12 | Table 6 跨双栏、Table 7 左栏浮动显示，caption/编号完整；四版本和八种外部设置均完整。参考文献从 [2] 接续至 [19]，长 DOI 正常折行，无丢条、重叠或裁切。 |

附录表 6、7 从第 11 页文字引用浮动到第 12 页，仍能凭编号清楚对应；没有达到必须重排的可读性问题。已查 `build.py` 与 `main.tex`：保留了 balance 包加载，但没有执行 `\balance` 或其他所查强制平衡命令；末页实际排版完整，不需为追求左右等高重新强制 balance。

## 版本身份

PDF：`MANUSCRIPT_CVM.pdf`，12 页。实际 SHA256 与主任务给定值一致：

`e97d0bff7bf0d94f852feb946bdef5e12878e7dd0ff71d41b67d79138794a7a3`

所审 `source/body.tex` SHA256：

`6c1b14da4cbe055038bc196737136f1e8d4204c9e89bd97af2d46f956c5c0745`

| 实际查看 PNG | SHA256 |
| --- | --- |
| `qa/pages/page-07.png` | `e0dd4734080104b393bc977dd52653edfe474c092fd59745a87b8e19a56c8cee` |
| `qa/pages/page-08.png` | `59122b6224c91e1100d8b2b736ea98398b4c6e584a9a6224e9c9646e4dad90a0` |
| `qa/pages/page-09.png` | `55c94a688fe924168014e7a5d61febe21ebfb6a63b731bdf40379b240ef8400d` |
| `qa/pages/page-10.png` | `7bd2684a2cdf1e289e23280d9bc732ec318c514b7c32d4c73f1cf2a89c8315ac` |
| `qa/pages/page-11.png` | `f11dca9931c90730f6291640968edf36f6644ddd02d0bdb6e18862e247c9336e` |
| `qa/pages/page-12.png` | `9061321d6e8827accdac7e21f9e54d1e1b1efc634dc9dc56882f2d8c294ffec0` |

相对路径的根目录为 `output/cvm_focused_narrative_20260917/`。

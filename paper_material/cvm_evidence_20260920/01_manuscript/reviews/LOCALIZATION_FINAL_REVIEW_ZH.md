# 定位设计目标终审

日期：2026-09-17。只审本轮 reference/supervision 段、机制表、四行角色与选择 G 的解释；沿用上一轮已核实的冻结源码，不新增文献检索或模型运行。未修改正文、构建脚本或输入。

## P1 / P2 结论

**未发现需要修改的 P1 / P2 问题。无必要替换句。**

- `source/body.tex:69` 准确区分“旁路 preliminary 作为参考、关闭额外监督”和“删除 preliminary head”；明确保留 stock DN。与已核实的历史及后续源码一致。
- 同段及 `:243` 明确固定分布 frame 继承自 FDR，作者设计是 incoming-reference 选择、解码与 FGL target 的一致使用及额外监督配置。没有把继承机制重新包装为原创，也没有将作者路径设计淡化为外部基线。
- `build.py` 的机制表把继承表示、作者路径、作者几何与层间权重规则分开；四行表的 “Transfer reference / Our localization variants” 分组与正文 `:243–245` 一致。正文已说明 transfer reference 含作者 host-interface integration，未把它冒称为未经改动的 D-FINE detector。当前角色分组可采用，不必给四行都加 `(ours)`。
- `source/body.tex:249` 保留 path-only 的最高 AP、加入 geometry 的负差值及 LRS-GFDR 与 path-only 的差值；选择 G 的解释落在已定义的几何和监督属性，而非不存在的 AP 第一或实测稳定性优势。该解释技术上成立，未不必要削弱作者设计身份。

“source and initialization matching are not established across all rows” 是对整张历史表的限定，未断言 V02/V03 初始化不同；与这两行共享登记初始化文件的已有证据不冲突。

## 本次所审文件

- `output/cvm_experiment_design_20260917/source/body.tex` SHA256：`63bdbeb562cd1f1ff04adab3a47d3086d4002cb62c5e85c9f1edd4515fd90303`。
- `output/cvm_experiment_design_20260917/build.py` SHA256：`6c1c28466f35cab804b4dcdd0d855a558347b3fd9881b972ad305fbe44f1f5f7`。

本结论是上述内容的目标技术终审，不替代最终 PDF 的排版核查。

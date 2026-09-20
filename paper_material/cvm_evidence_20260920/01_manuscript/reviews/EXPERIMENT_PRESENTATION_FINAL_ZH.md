# 实验呈现定向终稿审读

日期：2026-09-17。

**结论：通过。本次范围内没有必要修改项。** 不要求新训练、新推理或增加实验。只审读文本与表格生成定义，不代替最终 PDF 布局验收。

审读对象：`source/body.tex`、`build.py`、`EXPERIMENT_DESIGN_DECISIONS_ZH.md`；额外只核对生成八组外部表格所用的既有 `inputs/external_sensitivity/EXTERNAL_SENSITIVITY.json`。未扩检索、未改稿。

## 核查结果

1. **文献建议落实准确。** 方法与定位比较表区分完整 FDR/FGL 移植参照、作者路径改写和几何/LRS规则，未把历史 Clean 别名包装成外部原生基线。定位表明确历史 source/initialization 匹配不完整；正文保留 geometry 的 −0.335 AP，并明确最终 G 比 path-only 低 0.076 AP。继承表示的收益与作者设计的比较范围没有混写。决策文件对 D-FINE、DEIM、SD-Net 的可借鉴点及不适用结论，与此前文献核查相符。

2. **五臂精度—成本合表没有掩盖 G+B 负结果。** `build.py` 的 COMPONENTS 表完整列出 G+B 的 29.277 AP、130.575 GFLOPs 和 76.266 images/s；`body.tex` 的 “Localization core and local visual extension” 段明确其比 G 低 0.343 AP，且未声称专家/监督组合独立有效。最直接匹配的 G+B→Full 对应 +0.832 AP，被限定为专家配置下增加 F 的比较。正文也保留 G+F 中间配置及 Full 相对 G 的 +0.489 AP、+26.70% GFLOPs，未用 Full 最高精度遮盖代价。外部 D-FINE 比较不被混进此表；其训练配方、effective batch、checkpoint定义和 common evaluator 的对齐范围另有清楚披露。

3. **八组外部敏感性解释合理，专业语气可接受。** 表格从既有记录生成全部 final/best × val/test × 100/300 组合，差值确为 +1.550 至 +2.027 AP；final test@300 保持主终点。附录明确 100-cap 是对已导出 300 上限预测进行 COCOeval 逐类截断，未误称重新配置检测器；也明确这些行不独立、不提供显著性或内部组件 test 归因，仍受训练配方差异限制。正文虽多次提醒比较范围，但这些提醒落在对应结果处，尚未形成需要阻止定稿的自我辩护语气。压缩版面时保留决定读法的表注、G+B 下降句、配方差异与附录独立性说明即可，无须再添加解释段。

## 审读快照

以下指纹用于说明本次读到的内容；后续布局压缩若改变文件，不代表自动产生新的内容问题。

| 文件 | SHA-256 |
|---|---|
| source/body.tex | `8e6854485c4946ed3daf65ec344a38c61f81e6dcfa098b40624f983d2e83b125` |
| build.py | `5cf35bfb11f920126c5892d26266d87476737e126aa4044e095de5083d3057a2` |
| EXPERIMENT_DESIGN_DECISIONS_ZH.md | `f6d54b9b897dca751b81a0a3b601da6c71058607cec99b2f123cd57d9488446f` |

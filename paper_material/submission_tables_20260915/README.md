# 论文实验表交付包

以现有证据组织实验章节，更新至 2026-09-15。主方法固定为 **LRS-GFDR + Capacity-BPDD-v3-Safe + FIA**。本包完成表格设计、数值填充和来源核对；尚不是整篇论文的投稿完成认证。

## 直接使用

- [整套表格预览](preview.html)：本地浏览器打开，可打印。
- [主结果与大模块消融](MAIN_TABLES_ZH.md)：T1、T2。
- [内部设计消融](INTERNAL_ABLATIONS_ZH.md)：T3、T4。
- [支持性检验](SUPPLEMENTARY_ZH.md)：S1、S2。
- [UAVDT 待核对表](UAVDT_PENDING_ZH.md)：U1、U2，暂不进入主结论。
- [论文结构与结果解读](PAPER_PLAN_ZH.md)：每张表回答什么、推荐结论、剩余证据。
- [英文 LaTeX 表格](tables.tex)：可粘贴进论文，导言区需要 `booktabs`。包含 T1–T4、S1–S2，保留必要表注；需在目标会议模板中最终排版。
- [结构化表格](tables.json)、[证据哈希和核验范围](provenance.json)：便于共同作者复核。

## 表格分工

| 编号 | 回答的问题 | 内容 | 建议位置 |
|---|---|---|---|
| T1 | 与外部检测器相比表现如何？ | D-FINE-L 与 Full，共同 test，AP/AP50/AP75/尺度 AP/参数 | 正文主结果 |
| T2 | 三个大模块组合后怎样？ | Base、G、G+F、G+B、Full | 正文大模块消融 |
| T3 | 定位模块内部设计怎样？ | Original FDR、Clean、几何修正、LRS-GFDR | 内部设计消融 |
| T4 | BPDD 修改为何与联合训练有关？ | Capacity v2/v3-Safe × FIA off/on | 内部设计消融 |
| S1 | FIA 验证增益能否延伸到 test？ | 当前 G+B 与 Full 的独立 test | 建议正文简述，完整表可放补充 |
| S2 | 提升是否只出现在 best？ | 外部共同评估的 best/final | 补充材料 |
| U1 | 第二数据集总体表现？ | UAVDT baseline 与新导出 | 待数据统计和模型身份核对 |
| U2 | 第二数据集哪些类别有问题？ | UAVDT car/truck/bus AP | 同 U1 |

短篇正文优先放 T1、T2、T3、T4，并在文字中报告 S1 的 test 增量；版面允许时将 S1 独立成表。不要把两个不同问题的表格合成一个排名榜。

## 统计与来源规则

1. P、R、AP 统一显示百分数，三位小数；所有增量以未舍入源值计算后再舍入，单位 pp。
2. 原生验证 best 的一行指标来自同一个 epoch；各臂 best 轮不同是相同选择规则下的正常结果。
3. 共同 test 使用固定 checkpoint 与项目转换标签，不能宣称官方 challenge 排名，也不直接拼接文献中的原生指标。
4. T2 的 B 固定为 v3-Safe。旧 BPDD 的 0.292770、最新 v3-Safe 的 0.29277 恰好数值相近，不能互换实验身份。
5. 共同 protocol authority 是整理时增加的索引；它记录匹配事实，不能通过命名让未核对的源码自动等价。实际生效代码只差目标开关才支持更强归因，提交号本身不要求相同，也不能仅因不同而判无效。
6. 单 seed 表不标注“显著提升”，不生成标准差或 p 值。

## 不放入正文的材料

短跑、BTDSE、IOQC-SA、VSF-RMR、FrequencyCM、自适应候选、EQuAL、旧三模块和旧代际 standalone 消融均保留在[完整实验档案](../results/ALL_EXPERIMENTS_SUMMARY_20260915_ZH.md)，本包不列入正文。与当前论证有关的负结果继续保留：几何修正的 AP 下降、v3-Safe BPDD-only 的下降、v2 联合退化、UAVDT truck 低 AP。

## 生成与核验

从仓库根目录运行 `node scripts/build_submission_tables.cjs` 可重建全部数值表、英文 LaTeX、HTML 和来源清单。生成器核对当前两臂的100轮日志、best/final、同一最佳轮的 P/R/AP50/AP、训练记录共有设置、FDR/BPDD 配置块、评估版本与图像数。其他历史行引用现有汇总记录，不冒充新服务器复测。

当前没有新启动训练、没有新增模型实验、没有改写原始指标。历史全源码运行路径审计、UAVDT 同一数据划分复评和当前模型同机推理开销测量仍是独立工作。

# 论文选用表格：正文 3 张 + 补充 2 张 + UAVDT 预留

先打开 [正文选用表](MAIN_TABLES.md) 或 [预览页](preview.html)。写作时可直接复制表格；英文 LaTeX 入口为 [main_tables.tex](main_tables.tex)。

| 论文编号 | 内容 | 来源 | 放置位置 |
| --- | --- | --- | --- |
| 1 | VisDrone test 外部方法比较 | T1 | 正文 |
| 2 | VisDrone val 大模块组合消融 | T2 | 正文 |
| 3 | 内部设计对照：定位设计与 BPDD 联合兼容性 | T3 + T4 | 正文 |
| S1 | FIA 开关的独立 test 检验 | S1 | 补充材料 |
| S2 | best 与 final 的共同评估结果 | S2 | 补充材料 |
| 4 | UAVDT 总体结果（预留，待统一评估复核） | U1 | 待复评预留 |
| S3 | UAVDT 逐类别 AP（补充表预留） | U2 | 待复评预留 |

- [正文 3 张表](MAIN_TABLES.md)：表 3 含两个独立子表，分别回答定位设计和蒸馏兼容性问题。
- [补充表 S1–S2](SUPPLEMENTARY_TABLES.md)：test 检验、best/final 稳健性。
- [UAVDT 表 4 / S3 草稿](UAVDT_TABLE_4_DRAFT.md)：当前联合方法名称保留；复评前不写严格 +1.36 pp 增益。
- [来源清单](selection_manifest.json)：原表编号和证据路径，数值没有重新计算或替换。

LaTeX 需要 booktabs；main_tables.tex 已合并正文三张表，也可以选用 table_*.tex 单表文件。不要同时导入合并文件和单表文件。表 3 的两个子表共用一个编号；补充材料单独排号。尚未在目标会议模板中编译，最终字号和浮动位置需结合正文检查。

从仓库根目录执行 node scripts/build_submission_tables.cjs，再执行 node scripts/extract_selected_paper_tables.cjs，可重建全部选表。

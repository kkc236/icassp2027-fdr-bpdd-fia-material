# VisDrone 外部方法对比材料设计

## 目标

为 ICASSP 2027 材料仓补充一套可直接用于论文写作的 VisDrone 外部方法对比材料。表格必须区分原论文报告值与本项目实测值，分开呈现 val/test，并显式记录输入尺寸、骨干、预训练和来源，避免跨协议数值被写成严格排名。

## 采用方案

采用“论文页 + 机器证据 + 入口同步”的完整方案：

1. 新增 `paper_material/results/EXTERNAL_VISDRONE_COMPARISON_ZH.md`，提供论文写作版 val/test 表、协议边界和允许主张。
2. 新增 `paper_material/results/external_visdrone_comparison.json`，逐行登记方法、split、指标、输入、骨干、训练/预训练说明、证据类型、原论文表号与 URL/DOI。
3. 新增 `paper_material/results/external_visdrone_comparison.csv`，供论文制表和后续筛选。
4. 更新 `paper_material/README_ZH.md`、`paper_material/results/RESULTS_ZH.md` 与 `paper_material/writing/ICASSP2027_OUTLINE_ZH.md`，将外部表纳入统一入口和实验章节。
5. 更新 `paper_material/evidence/source_manifest.json`，登记机器材料来源；新增完整性测试，保证 JSON/CSV/Markdown 行一致且所有外部行都有原始论文定位。

## 数据范围

优先纳入与 RT-DETR/DETR、VisDrone、小目标检测直接相关且原论文表格可核对的方法：

- Drone-DETR
- MCG-RTDETR
- UAV-DETR
- VRF-DETR
- NRQO
- RT-UAV-SOD
- 本项目 RT-DETR-L baseline 与 FDR+BPDD+FIA

800 或 1333×800 等非 640 输入方法可以作为补充行，但必须与 640 主组分开；split 未被原论文明确说明的方法不得塞入 val 或 test 排名。

## 证据与写作边界

- `our_run`：来自材料仓现有可审计结果，可用于本项目内部增量。
- `reported_by_original_paper`：只表示原论文报告值，不表示本项目复现。
- val、test-dev/test 和原论文未明确 split 的结果分表或分组。
- 不同骨干、输入尺寸、预训练、训练周期和 evaluator 的结果不能表述为严格公平比较。
- 不跨表推导原论文未报告的 AP75、参数量、GFLOPs 或 FPS。
- 不宣称 SOTA；允许表述为“在相同 640 输入的已报告结果范围内具有竞争力”，前提是正文同时披露骨干和训练差异。
- 所有外部数字必须绑定原论文 URL/DOI、表号、split 和展示精度。

## 表格结构

论文页至少包含：

1. `VisDrone val`：Method、Venue、Backbone、Input、Pretrain、AP、AP50、AP75、Params、Evidence。
2. `VisDrone test/test-dev`：相同字段，单独呈现。
3. `Split 未明确或不同输入补充`：不得参与同协议排序。

机器 JSON/CSV 额外保存 `source_url`、`source_table`、`protocol_notes` 和 `comparison_scope`。

## 验证

- JSON 可解析且 schema 版本固定。
- CSV 与 JSON 的行数、方法、split、指标和来源一致。
- 每个外部行都有非空 `source_url` 与 `source_table`。
- 每个本项目行都绑定现有材料仓 source ID。
- Markdown 明确出现 `reported_by_original_paper`、`our_run`、val/test 分离和禁止 SOTA 主张。
- 全套材料完整性测试通过，工作树无意外文件。


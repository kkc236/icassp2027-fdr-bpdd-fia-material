# VisDrone 外部方法对比材料设计

## 目标

为 ICASSP 2027 材料仓补充一套可直接用于论文写作的 VisDrone 外部方法对比材料。表格必须区分原论文报告值与本项目实测值，分开呈现 val/test，并显式记录输入尺寸、骨干、预训练和来源，避免跨协议数值被写成严格排名。

## 采用方案

采用“论文页 + 机器证据 + 入口同步”的完整方案：

1. 新增 `paper_material/results/EXTERNAL_VISDRONE_COMPARISON_ZH.md`，提供论文写作版 CCF B 会 val/test 表、协议边界和允许主张。
2. 新增 `paper_material/results/external_visdrone_comparison.json`，逐行登记方法、split、指标、输入、骨干、训练/预训练说明、证据类型、原论文表号与 URL/DOI。
3. 新增 `paper_material/results/external_visdrone_comparison.csv`，供论文制表和后续筛选。
4. 更新 `paper_material/README_ZH.md`、`paper_material/results/RESULTS_ZH.md` 与 `paper_material/writing/ICASSP2027_OUTLINE_ZH.md`，将外部表纳入统一入口和实验章节。
5. 更新 `paper_material/evidence/source_manifest.json`，登记机器材料来源；新增完整性测试，保证 JSON/CSV/Markdown 行一致且所有外部行都有原始论文定位。

## 数据范围

正式方法集合限定为 CCF 当前目录中的 B 类会议 full/regular paper：

- EMA（ICASSP 2023）
- HIC-YOLOv5（ICRA 2024）
- UAV-DETR（IROS 2025）
- NRQO（ICME 2025）
- UAV-DETR Table I 中统一报告的 YOLOv8 与 RT-DETR 标准基线
- 本项目 RT-DETR-L baseline 与 FDR+BPDD+FIA

800 或 1333×800 等非 640 输入方法可以作为补充行，但必须与 640 主组分开；split 未被原论文明确说明的方法不得塞入 val 或 test 排名。

不再为了 RTX 4090 硬件匹配引入其他层级来源。若 B 会论文没有完整报告 GPU、batch、precision、backend 与 latency scope，则 FPS 仅作元数据，不进入速度排名。仅预印本既不进入正式表，也不进入补充表或机器 CSV/JSON。

## 可比性优先级

外部行不按绝对 AP 高低优先选取，而按与本项目协议的接近程度排序：

1. 相同 VisDrone split：val 与 val、1,610-image test/test-dev 与 test 对齐。
2. 相同输入尺寸：优先 `640×640`，其他尺寸放入独立补充组。
3. 相同训练来源：优先 scratch 对 scratch；使用 ImageNet、COCO 或 Objects365 预训练的行单独标记，不与 scratch 结果写成严格胜负。
4. 相近评估器：优先 COCO AP、相同类别、`max_det=300` 或明确报告最大检测数的结果；未报告项写为 `not_reported`。
5. 效率比较要求 GPU、batch、precision、backend、输入和 latency scope 一致。只有全部一致的行才设置 `fps_comparison_allowed=true`。

参数量不作为外部方法准入或排序条件，只作为表格字段，并与 GFLOPs/FPS 一起用于解释精度—效率权衡。每个表先展示“协议最接近组”，再展示“相关但不严格可比组”。论文正文只对最接近组作有限比较，其余方法仅提供领域位置参考。

## 证据与写作边界

- `our_run`：来自材料仓现有可审计结果，可用于本项目内部增量。
- `reported_by_original_paper`：只表示原论文报告值，不表示本项目复现。
- val、test-dev/test 和原论文未明确 split 的结果分表或分组。
- 不同骨干、输入尺寸、预训练、训练周期和 evaluator 的结果不能表述为严格公平比较。
- FPS 只有在 GPU、输入、batch、精度、推理后端及计时范围一致时才允许直接排序；否则只并列展示。
- 预印本、ResearchGate-only 手稿和无法确认正式出处的结果不进入任何论文表或机器材料。
- 不跨表推导原论文未报告的 AP75、参数量、GFLOPs 或 FPS。
- 不宣称 SOTA；允许表述为“在相同 640 输入的已报告结果范围内具有竞争力”，前提是正文同时披露骨干和训练差异。
- 所有外部数字必须绑定原论文 URL/DOI、表号、split 和展示精度。

## 表格结构

论文页至少包含：

1. `VisDrone val`：Method、Venue、Backbone、Input、Pretrain、AP、AP50、AP75、Params、Evidence。
2. `VisDrone test/test-dev`：相同字段，单独呈现。
3. `Split 未明确或不同输入补充`：不得参与同协议排序。
4. `效率边界`：只登记 B 会论文实际报告的 GPU、Batch、Precision、Backend、Latency Scope 和 FPS；协议不全时禁止排序。

机器 JSON/CSV 额外保存 `source_url`、`source_table`、`protocol_notes`、`comparison_scope`、`gpu`、`batch`、`precision`、`backend`、`latency_scope` 和 `fps_comparison_allowed`。

## 验证

- JSON 可解析且 schema 版本固定。
- CSV 与 JSON 的行数、方法、split、指标和来源一致。
- 每个外部行都有非空 `source_url` 与 `source_table`。
- 每个外部行都有正式发表状态；测试拒绝 `preprint`、`arxiv_only`、`researchgate_only` 和 `unverified`。
- 每个带 FPS 的行都登记 GPU、batch、precision、backend 和 latency scope；未知项显式为 `not_reported`，不得留空。
- 每个本项目行都绑定现有材料仓 source ID。
- Markdown 明确出现 `reported_by_original_paper`、`our_run`、val/test 分离和禁止 SOTA 主张。
- 全套材料完整性测试通过，工作树无意外文件。

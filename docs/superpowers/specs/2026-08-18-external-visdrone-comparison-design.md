# VisDrone 外部方法对比材料设计

## 目标

为 ICASSP 2027 材料仓补充一套可直接用于论文写作的 VisDrone 外部方法对比材料。表格必须区分原论文报告值与本项目实测值，分开呈现 val/test，并显式记录输入尺寸、骨干、预训练和来源，避免跨协议数值被写成严格排名。

## 采用方案

采用“论文页 + 机器证据 + 入口同步”的完整方案：

1. 新增 `paper_material/results/EXTERNAL_VISDRONE_COMPARISON_ZH.md`，提供论文写作版 val/test 表、RTX 4090 效率补充表、协议边界和允许主张。
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
- BGF-YOLOv10
- WaveUAV-YOLO
- YOLO-TME
- 本项目 RT-DETR-L baseline 与 FDR+BPDD+FIA

800 或 1333×800 等非 640 输入方法可以作为补充行，但必须与 640 主组分开；split 未被原论文明确说明的方法不得塞入 val 或 test 排名。

RTX 4090 效率组优先采用正式同行评审论文在同一 4090 上统一测得的 YOLOv8/YOLOv9/YOLOv10 与 RT-DETR 基线，以及明确报告 4090 推理设置的 UAV 专用 YOLO。FBRT-YOLO 的 AAAI 论文只作为其 Table 1 中统一硬件基线数字的来源，不作为“普通 B 会方法水平”的门槛对标。LAF-YOLOv10 等预印本既不进入正式表，也不进入补充表或机器 CSV/JSON。

## 可比性优先级

外部行不按绝对 AP 高低优先选取，而按与本项目协议的接近程度排序：

1. 相同 VisDrone split：val 与 val、1,610-image test/test-dev 与 test 对齐。
2. 相同输入尺寸：优先 `640×640`，其他尺寸放入独立补充组。
3. 相近模型规模：优先参数量接近本项目 `32.64M` 的方法；主邻域定义为 `25M–40M`，更小/更大模型保留但降级到规模补充组。
4. 相同训练来源：优先 scratch 对 scratch；使用 ImageNet、COCO 或 Objects365 预训练的行单独标记，不与 scratch 结果写成严格胜负。
5. 相近评估器：优先 COCO AP、相同类别、`max_det=300` 或明确报告最大检测数的结果；未报告项写为 `not_reported`。
6. 效率比较再要求 RTX 4090、batch、precision、backend、输入和 latency scope 一致。只有全部一致的行才设置 `fps_comparison_allowed=true`。

每个表先展示“协议/规模最接近组”，再展示“相关但不严格可比组”。论文正文只对最接近组作有限比较，其余方法仅提供领域位置参考。

## 证据与写作边界

- `our_run`：来自材料仓现有可审计结果，可用于本项目内部增量。
- `reported_by_original_paper`：只表示原论文报告值，不表示本项目复现。
- val、test-dev/test 和原论文未明确 split 的结果分表或分组。
- 不同骨干、输入尺寸、预训练、训练周期和 evaluator 的结果不能表述为严格公平比较。
- FPS 只有在 GPU、输入、batch、精度、推理后端及计时范围一致时才允许直接排序；仅同为 RTX 4090 但 TensorRT/PyTorch、FP16/FP32 或纯 forward/end-to-end 不同的结果，只并列展示。
- 预印本、ResearchGate-only 手稿和无法确认正式出处的结果不进入任何论文表或机器材料。
- 不跨表推导原论文未报告的 AP75、参数量、GFLOPs 或 FPS。
- 不宣称 SOTA；允许表述为“在相同 640 输入的已报告结果范围内具有竞争力”，前提是正文同时披露骨干和训练差异。
- 所有外部数字必须绑定原论文 URL/DOI、表号、split 和展示精度。

## 表格结构

论文页至少包含：

1. `VisDrone val`：Method、Venue、Backbone、Input、Pretrain、AP、AP50、AP75、Params、Evidence。
2. `VisDrone test/test-dev`：相同字段，单独呈现。
3. `Split 未明确或不同输入补充`：不得参与同协议排序。
4. `RTX 4090 效率补充`：Method、Input、Batch、Precision、Backend、Latency Scope、AP、AP50、Params、GFLOPs、FPS、Evidence；按可比协议分组，不跨组加粗最快值。

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

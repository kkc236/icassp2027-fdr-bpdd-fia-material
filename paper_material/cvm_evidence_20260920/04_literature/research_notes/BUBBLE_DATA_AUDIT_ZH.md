# 参数量–AP–GFLOPs 气泡图数据核验

## 结论

按用户最新更正，纵轴为 **AP（IoU 0.50:0.95）**，横轴为参数量 M，气泡面积对应每张图 GFLOPs；AP50 仅保留为可选数据。只读核对了原指定四篇 PDF、随后根任务提供的 BDNet 正文/补充材料及当前稿输入，没有运行模型、训练或服务器操作。

**现已有 8 个可用候选：6 个外部报告点 + 2 个本稿归档点；全部精度来自明确的 VisDrone val，输入为 640。** BDNet 及其作者重训的 YOLO11/12/26 提供完整三元组；FGHDet 与其 YOLOv7 基线的 val 精度配以同结构640成本。FGHDet 两行预训练未披露；BDNet 明确不预训练，三种 YOLO 则由作者 same experimental conditions 声明关联。不要把整张图写成全部无预训练、同配方公平排名。

LME/SD 的 6 个原候选已移至 JSON held_candidates_not_for_current_plot，不用于当前 val 图。未用任何 Fig.1 气泡/标签推定数值。DASSF 仍缺 Params/GFLOPs。

## 当前 8 个图候选

|候选|Params M|AP .50:.95|AP50|GFLOPs|来源/归属|
|---|---:|---:|---:|---:|---|
|Full (ours)|35.244|30.109|49.89|134.051|our archived result|
|RT-DETR-L (our host)|32.827|21.911|38.663|105.597|our archived reproduction|
|FGHDet [FGHDet paper]|43.9|32.1|53.8|238.9|source paper own method|
|YOLOv7 [FGHDet paper]|37.2|27.2|48.6|105.3|baseline reported by FGHDet paper|
|BDNet [BDNet paper]|2.59|31.2|50.5|52.44|source paper own method|
|YOLO11 [BDNet paper]|25.3|28.7|46.1|87.28|retrained by BDNet authors; not our reproduction and not original YOLO paper result|
|YOLO12 [BDNet paper]|29.2|29.3|47.3|89.4|retrained by BDNet authors; not our reproduction and not original YOLO paper result|
|YOLO26 [BDNet paper]|26.3|27.7|45.2|93.8|retrained by BDNet authors; not our reproduction and not original YOLO paper result|

### BDNet：新补齐的 4 个点

- 主文 PDF p.7（印刷页32730）Table 2 标题明确 VisDrone2019 validation set，四行全部数值已实际 view_image 核对。主文 p.6（32729）§4.2 明确：有引用的比较行来自文献；YOLO11、YOLO12、YOLO26 则由 BDNet 作者在与 BDNet 相同的实验条件下重训。我们只采用后者3行及其自家BDNet，不把其他引文行自动套入其训练配方。
- 补充材料 p.2 §B 明确 640×640、batch8、SGD、lr0.01、warmup3、300epochs、BDNet整个过程不使用预训练权重；Ultralytics8.3.78/PyTorch2.7.1/RTX3090Ti。p.3明确 VisDrone mAP50–95 的阈值范围。三种YOLO的配方依据是§4.2的same-conditions陈述，不是我们独立验证训练日志。
- **原表标签实际印为 YOLO11-I / YOLO12-I / YOLO26-I，大写 I。** 原图和 PDF 字符提取一致（NimbusRomNo9L-Regu 中字符 I；非OCR误识别）。推定是 large 的小写 l 属于合理推断，但原文没有明确解释。为不把推断写成原表事实，建议图标签用 YOLO11 / YOLO12 / YOLO26 并引 BDNet，精确source_label_verbatim留在数据与说明中；若作者决定规范化成-l，须保留这项说明。
- 三行标为“retrained/reported by the BDNet authors”，**不是我们复测，也不是 YOLO 方法首发论文的原始成绩**。主文称 VisDrone 指标为YOLO format；标注转换/maxDet/checkpoint选择与我们是否一致未确认，不宣称统一评估。
- BDNet正文 SHA256 `98df28644f522e5cab0004625947d89a9653d3ad1c57f6f75a322103c96f4058`；补充材料 SHA256 `10bf2d6b8c9b8907562e1c5d4e714d4a0e90ad7ae79e4ee5f77b1951b2d057c0`。

### FGHDet：确认 val，但成本需跨表注明

- PDF p.7 §5.1 将 mAP 定义为 IoU 0.50–0.95 十阈值均值；§5.3 明确 Table 2 是 VisDrone validation。p.8 Table 2 和 p.9 Table 5 的 640 行数值一致。
- p.9 Table 6 的 caption 明确为 test set。本审计**只**取其同名、同参数、同 640 结构的 GFLOPs，不取 test accuracy。FGHDet 的 val AP 32.1 / AP50 53.8，绝不能换成 Table 6 的 test AP 25.6 / AP50 44.5；YOLOv7 同理只用 val 27.2 / 48.6。
- Table 2 自家三行印为 FGFDet；正文、论文题名、Table 5/6 对应的是 FGHDet。报告保留这项原文拼写说明，不能据此额外造一个模型。
- §5.2：300 epochs，640 时 batch 4，Adam，初始学习率 0.01，decay 1e-5；未报告预训练情况、评价器/maxDet/标注处理或 checkpoint 选择规则。GFLOPs 统计工具与 MAC 计数方式也未说明。
- YOLOv7 点注明“as reported by FGHDet”，并引用 FGHDet 表；不是我们复测，也不声称取自 YOLOv7 原论文。

### SD-Net：数值完整，split 未明确

- PDF p.8 Table 1 已实际看图核对；p.7 §4.1.2 明确 mAP.5:.95。p.8 §4.1.3 说明 200 epochs、batch 4、SGD、640×640、最后 10 epochs 关闭 Mosaic。
- §4.1.1 只列出 train/val/test 的数量；Table 1 标题与 §4.2.1 没有指定这张主表的评估 split。不能根据数值或常见 YOLO 习惯推定 val。预训练没有披露。
- SD-Net-n/s 为论文自己的模型结果；其余 YOLOv11-s、RT-DETR-r18、DMR-RTDETR 是“SD-Net 论文所报告的相应行”。原方法论文没有在本任务里逐一核查。paper-level 的 all models recipe 不应升级成逐行独立审计结论。

### LME-DETR：split 和 AP 定义均须补证

- PDF p.9 Table 1 已实际看图核对：LME-DETR 14M、46G、AP 31.8、AP50 48.6、640×640。
- PDF p.8 §4.1 明确 300 epochs 上限、batch 4、AdamW、early stopping patience 20。未说明主表实际停止 epoch、主表 split 或预训练。
- 该节明确 AP50 的 IoU=0.5，但没有明确 Table 1 的 AP 列是 .50:.95；不能只根据惯例自动把该列填入确认的 AP50:95 数据。JSON 保留 reported_ap_column_percent=31.8，而 ap50_95_percent=null。
- 若之后取得 split 与 AP 定义的直接证据，可解除 hold；不能把 SD-Net 论文中同名模型的精度与 LME 中的参数/成本拼接。

### DASSF：缺少气泡图必要维度

- PDF p.6 Table 1：mAP50 42.1、mAP50:95 25.2；p.8 Table 4 的 VisDrone 自家最终行一致。
- 原文没有找到参数量与 GFLOPs；SD-Net Table 1 对 DASSF 的两列也均为横杠。不能从 YOLOv8n 名义基线或其他模型补值。
- §4.2（p.6–7）：200 epochs、batch 8、SGD、lr 0.0001。input size、主结果 split、预训练未明确披露。

## 本稿两点与内部备选

- Full：35.244M / AP 30.109 / AP50 49.890 / 134.051 GFLOPs。RT-DETR-L host：32.827M / AP 21.911 / AP50 38.663 / 105.597 GFLOPs。核对 source/table_components.tex 和 body.tex；评估是本稿 native val，非 test/common evaluator 值。
- 两者为 100 epochs、640、scratch 的本稿归档结果；GFLOPs 是每张图、2 operations/MAC、完整未融合模型参数量。与外部统计口径可能不同。
- JSON 的 internal_only_alternative 单列已有 5 个配置，供内部 accuracy–cost 图备选；不能用这 5 行声称完成不同外部模型比较。
- 当前 literature 表中的 BDNet 已由这次一手原表补齐 GFLOPs。RemDet-L 不纳入本次推荐：根任务正在处理其作者README（66.7GF）与正式PDF（67.4GF）的版本差异；本审计不选取其中一个冒称已核。

## 图稿可用措辞与最小处理

可写：“Reported VisDrone validation accuracy and model cost at 640 input. External results are reported by the cited studies; the three YOLO rows are retrained by the BDNet authors. Training and evaluation recipes differ. For FGHDet and YOLOv7, validation accuracy is from Tables 2/5 and 640-input architecture cost from Table 6.” 当前8点满足有限外部背景图的数量目标。预训练信息在表/数据注释中单独列明，不给全图统一写no pretraining。

图中用不同标记/图例区分 our runs 与 published reports；不要连接外部点形成优化轨迹或给出受控优越性结论。气泡应按面积比例而非半径比例编码 GFLOPs，并给气泡大小图例。机制 Table 1 的删除及结果总表改 Table 1 属于根任务修改，本审计未改正文/build。

## 原始来源与实际视觉核验

- LME-DETR：[01_LME-DETR_CVM2026.pdf](C:/Users/16946/Documents/OBJECTIVE CHECK PAPER/downloads/CVM_Visual_Papers_2025_2026/01_LME-DETR_CVM2026.pdf)；[官方 PDF](https://iccvm.org/2026/files/papers/265.pdf)；SHA256 `3c39348271fe29dc4fd8fa77bac238dd246d1bf834d88bd40a95913d09944186`。实际查看页：8, 9。
- SD-Net：[02_SD-Net_CVM2026.pdf](C:/Users/16946/Documents/OBJECTIVE CHECK PAPER/downloads/CVM_Visual_Papers_2025_2026/02_SD-Net_CVM2026.pdf)；[官方 PDF](https://iccvm.org/2026/files/papers/691.pdf)；SHA256 `636f2f2a0d762a320f8661ca745e55fec0b3002bafaf5772a81704f1770aa3e3`。实际查看页：7, 8。
- FGHDet：[03_FGHDet_CVM2025.pdf](C:/Users/16946/Documents/OBJECTIVE CHECK PAPER/downloads/CVM_Visual_Papers_2025_2026/03_FGHDet_CVM2025.pdf)；[官方 PDF](https://iccvm.org/2025/papers/s8p2-368-jcst.pdf)；SHA256 `7b3a78a7a55db9b280042dcbcd7f4997e64fcbdf2e79dca1960b50fcc47317f0`。实际查看页：7, 8, 9。
- DASSF：[04_DASSF_CVM2025.pdf](C:/Users/16946/Documents/OBJECTIVE CHECK PAPER/downloads/CVM_Visual_Papers_2025_2026/04_DASSF_CVM2025.pdf)；[官方 PDF](https://iccvm.org/2025/papers/lncs/813.pdf)；SHA256 `d1e3ec596e988b713c1c7f5063bcb1383a0a17c268c13f91428ebc7304efe00c`。实际查看页：6, 7, 8。

实际调用 view_image 并将图像输出供视觉检查：原四篇10张页面，加BDNet正文2张/补充2张，共14张页面PNG。SHA256 均在 candidate_bubbles.json 的 inspected_page_png_sha256 内；文字抽取只用于定位与交叉核对，数值不是仅凭 OCR 抄录。

- BDNet：[官方正文 PDF](https://openaccess.thecvf.com/content/CVPR2026/papers/Guan_BDNetBio-Inspired_Dual-Backbone_Small_Object_Detection_Network_CVPR_2026_paper.pdf)；[官方补充 PDF](https://openaccess.thecvf.com/content/CVPR2026/supplemental/Guan_BDNetBio-Inspired_Dual-Backbone_Small_CVPR_2026_supplemental.pdf)。实际查看正文p.6–7、补充p.2–3；本次使用本地已有PDF，未重新请求网络。

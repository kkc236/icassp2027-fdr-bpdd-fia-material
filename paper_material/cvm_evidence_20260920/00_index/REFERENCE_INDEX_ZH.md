# 当前25条参考文献索引

盘点日期：2026-09-20。本文献索引对应 [当前主稿](../01_manuscript/main.tex) 的25条引用。题录原值保存在 [机器可读索引](reference_index.json)，与 [基础题录](../01_manuscript/inputs/references.json) 及 [追加题录](../01_manuscript/source/additional_references.json) 一致；来源URL直接取原JSON，没有手工重拼。

## 读取状态

- **15项**已找到同一作品的完整PDF，**10项**未找到本地全文。
- “同作品全文”不等于“所引出版版本已核验”。本地包含作者预印本、会议托管稿和正式开放版本。
- 出版版本字段：`true`为已识别对应官方版本；`false`为已识别不同或较早版本；`null`为版本一致性未建立（也包括缺少全文）。
- 对应状态为3项true、5项false、17项null。未联网补齐，也未用其他论文中的引文代替本篇全文。

## 逐条映射

| 主稿编号 / key | 题名 | 本地全文 | 所引版本 | 原始来源 |
|---|---|---|---|---|
| 1 / `zhu2018visdrone` | Vision Meets Drones: A Challenge | 未找到 | 未建立一致性 | [来源](https://arxiv.org/abs/1804.07437) |
| 2 / `guan2026bdnet` | BDNet:Bio-Inspired Dual-Backbone Small Object Detection Network | [归档PDF](../04_literature/comparison_candidates/sources/BDNet_CVPR2026.pdf) | 已核验 | [来源](https://openaccess.thecvf.com/content/CVPR2026/html/Guan_BDNetBio-Inspired_Dual-Backbone_Small_Object_Detection_Network_CVPR_2026_paper.html) |
| 3 / `bi2025fghdet` | FGHDet: Delving into Fine-Grained Features with Head Selection for UAV Object Detection | [归档PDF](../04_literature/cvm_papers/03_FGHDet_CVM2025.pdf) | 不同/较早版本 | [来源](https://jcst.ict.ac.cn/article/doi/10.1007/s11390-025-5252-z) |
| 4 / `carion2020detr` | End-to-End Object Detection with Transformers | [归档PDF](../04_literature/detr_foundations/detr.pdf) | 未建立一致性 | [来源](https://arxiv.org/abs/2005.12872) |
| 5 / `zhao2024rtdetr` | DETRs Beat YOLOs on Real-time Object Detection | [归档PDF](../04_literature/detr_foundations/rt_detr.pdf) | 未建立一致性 | [来源](https://arxiv.org/abs/2304.08069) |
| 6 / `peng2025dfine` | D-FINE: Redefine Regression Task of DETRs as Fine-grained Distribution Refinement | [归档PDF](../04_literature/detr_reading/dfine.pdf) | 不同/较早版本 | [来源](https://proceedings.iclr.cc/paper_files/paper/2025/file/6cf58a87e3097e7d1f9be3e8693a93de-Paper-Conference.pdf) |
| 7 / `akyon2022sahi` | Slicing Aided Hyper Inference and Fine-tuning for Small Object Detection | [归档PDF](../04_literature/detr_reading/sahi.pdf) | 未建立一致性 | [来源](https://arxiv.org/abs/2202.06934) |
| 8 / `li2025dassf` | DASSF: Dynamic-Attention Scale-Sequence Fusion for Aerial Object Detection | [归档PDF](../04_literature/cvm_papers/04_DASSF_CVM2025.pdf) | 不同/较早版本 | [来源](https://link.springer.com/chapter/10.1007/978-981-96-5809-1_12) |
| 9 / `li2025remdet` | RemDet: Rethinking Efficient Model Design for UAV Object Detection | 未找到 | 未建立一致性 | [来源](https://ojs.aaai.org/index.php/AAAI/article/view/32490) |
| 10 / `fang2025nrqo` | Revisiting DETR for Small Object Detection via Noise-Resilient Query Optimization | [归档PDF](../04_literature/comparison_candidates/sources/NRQO_ICME2025_author.pdf) | 未建立一致性 | [来源](https://arxiv.org/abs/2507.19059) |
| 11 / `zhang2025sodetr` | SO-DETR: Leveraging Dual-Domain Features and Knowledge Distillation for Small Object Detection | [归档PDF](../04_literature/detr_reading/so_detr.pdf) | 未建立一致性 | [来源](https://arxiv.org/abs/2504.11470) |
| 12 / `hu2025domedetr` | Dome-DETR: DETR with Density-Oriented Feature-Query Manipulation for Efficient Tiny Object Detection | [归档PDF](../04_literature/detr_reading/dome_detr.pdf) | 未建立一致性 | [来源](https://arxiv.org/html/2505.05741v2) |
| 13 / `xu2026lme` | LME-DETR: Lightweight and Multi-Scale Feature-Enhanced End-to-End Object Detection for Aerial Images | [归档PDF](../04_literature/cvm_papers/01_LME-DETR_CVM2026.pdf) | 已核验 | [来源](https://iccvm.org/2026/files/papers/265.pdf) |
| 14 / `yang2026sdnet` | SD-Net: Synergistic and Dynamic Learning for Small Object Detection in Aerial Images | [归档PDF](../04_literature/cvm_papers/02_SD-Net_CVM2026.pdf) | 已核验 | [来源](https://iccvm.org/2026/files/papers/691.pdf) |
| 15 / `woo2018cbam` | CBAM: Convolutional Block Attention Module | 未找到 | 未建立一致性 | [来源](https://openaccess.thecvf.com/content_ECCV_2018/papers/Sanghyun_Woo_Convolutional_Block_Attention_ECCV_2018_paper.pdf) |
| 16 / `qiu2020borderdet` | BorderDet: Border Feature for Dense Object Detection | 未找到 | 未建立一致性 | [来源](https://www.ecva.net/papers/eccv_2020/papers_ECCV/papers/123460528.pdf) |
| 17 / `ye2023cascadedetr` | Cascade-DETR: Delving into High-Quality Universal Object Detection | 未找到 | 未建立一致性 | [来源](https://openaccess.thecvf.com/content/ICCV2023/html/Ye_Cascade-DETR_Delving_into_High-Quality_Universal_Object_Detection_ICCV_2023_paper.html) |
| 18 / `zhu2021deformable` | Deformable DETR: Deformable Transformers for End-to-End Object Detection | [归档PDF](../04_literature/detr_foundations/deformable_detr.pdf) | 未建立一致性 | [来源](https://openreview.net/forum?id=koX9F3hvCG) |
| 19 / `li2022dndetr` | DN-DETR: Accelerate DETR Training by Introducing Query DeNoising | [归档PDF](../04_literature/detr_foundations/dn_detr.pdf) | 不同/较早版本 | [来源](https://openaccess.thecvf.com/content/CVPR2022/papers/Li_DN-DETR_Accelerate_DETR_Training_by_Introducing_Query_DeNoising_CVPR_2022_paper.pdf) |
| 20 / `zhang2023dino` | DINO: DETR with Improved DeNoising Anchor Boxes for End-to-End Object Detection | [归档PDF](../04_literature/detr_foundations/dino.pdf) | 不同/较早版本 | [来源](https://openreview.net/forum?id=3mRwyG5one) |
| 21 / `li2020gfl` | Generalized Focal Loss: Learning Qualified and Distributed Bounding Boxes for Dense Object Detection | 未找到 | 未建立一致性 | [来源](https://proceedings.neurips.cc/paper_files/paper/2020/hash/f0bda020d2470f2e74990a07a607ebd9-Abstract.html) |
| 22 / `zheng2022ld` | Localization Distillation for Dense Object Detection | 未找到 | 未建立一致性 | [来源](https://openaccess.thecvf.com/content/CVPR2022/html/Zheng_Localization_Distillation_for_Dense_Object_Detection_CVPR_2022_paper.html) |
| 23 / `chang2023detrdistill` | DETRDistill: A Universal Knowledge Distillation Framework for DETR-families | 未找到 | 未建立一致性 | [来源](https://openaccess.thecvf.com/content/ICCV2023/html/Chang_DETRDistill_A_Universal_Knowledge_Distillation_Framework_for_DETR-families_ICCV_2023_paper.html) |
| 24 / `lin2014coco` | Microsoft COCO: Common Objects in Context | 未找到 | 未建立一致性 | [来源](https://arxiv.org/abs/1405.0312) |
| 25 / `du2018uavdt` | The Unmanned Aerial Vehicle Benchmark: Object Detection and Tracking | 未找到 | 未建立一致性 | [来源](https://www.ecva.net/papers/eccv_2018/papers_ECCV/html/Dawei_Du_The_Unmanned_Aerial_ECCV_2018_paper.php) |

## 已归档全文的版本备注

- **guan2026bdnet**：CVF 官方开放版本，11页；首页说明除水印外与录用版本一致。主文及补充材料与冻结气泡图来源记录对应。
  - [BDNet补充材料](../04_literature/comparison_candidates/sources/BDNet_CVPR2026_supplement.pdf)。
- **bi2025fghdet**：CVM 2025 官方会议托管稿，14页；当前题录引用 JCST 40(5):1301--1315 期刊终版。已确认是同一作品的不同排版版本。
- **carion2020detr**：作者全文，26页；首页标识 arXiv:2005.12872v3，2020-05-28。尚未与 ECCV 出版版本逐页核对。
- **zhao2024rtdetr**：作者全文，14页；首页标识 arXiv:2304.08069v3，2024-04-03。尚未与 CVPR 出版版本逐页核对。
- **peng2025dfine**：作者预印本 arXiv:2410.13842v1，2024-10-17，18页；当前引用指向17页 ICLR 2025 官方论文。不能将本地文件标为该官方版。
- **akyon2022sahi**：作者全文，5页；首页标识 arXiv:2202.06934v5，2022-10-24。尚未与所引 ICIP 出版版本逐页核对。
- **li2025dassf**：CVM 2025 官方会议托管稿，11页；当前题录引用 Springer LNCS 15663:212--227 的16页出版版本。
- **fang2025nrqo**：作者全文，6页；首页标识 arXiv:2507.19059v1，2025-07-25。尚未与 ICME 出版版本逐页核对。
- **zhang2025sodetr**：作者全文，8页；首页题名、作者与当前题录对应。IJCNN 出版版本一致性未核实。
- **hu2025domedetr**：作者全文，15页；首页标识 arXiv:2505.05741v2，2025-08-08，对应题录所列作者版本；ACM 出版版本一致性未核实。
- **xu2026lme**：CVM 2026 官方托管全文，14页；当前题录URL指向同一官方稿，归档SHA与原来源清单一致。
- **yang2026sdnet**：CVM 2026 官方托管全文，14页；当前题录URL指向同一官方稿，归档SHA与原来源清单一致。
- **zhu2021deformable**：全文16页，首页标明 ICLR 2021 会议论文及 arXiv:2010.04159v4，2021-03-18；与当前 OpenReview 版本的文件一致性未逐页核实。
- **li2022dndetr**：同题作者版本 arXiv:2203.01305v3，2022-12-08，13页，采用期刊式扩展排版；不得标为当前引用的 CVPR 2022 正式版本。
- **zhang2023dino**：作者预印本 arXiv:2203.03605v4，2022-07-11，23页；当前题录引用 ICLR 2023，所归档为较早作者版本。

## 缺少全文与历史调研的边界

未找到本地全文的10项：`zhu2018visdrone`, `li2025remdet`, `woo2018cbam`, `qiu2020borderdet`, `ye2023cascadedetr`, `li2020gfl`, `zheng2022ld`, `chang2023detrdistill`, `lin2014coco`, `du2018uavdt`。其中 RemDet 仅有题录及官方URL，本归档不标作已获得全文。

- [CVM来源清单](../04_literature/cvm_papers/sources.json) 的六份PDF均已与其记录SHA核对。BiCoR-Seg和TexHOI是视觉设计参考，并非当前25条引用。
- [图表调研笔记](../04_literature/research_notes/CVM_ADDITIONAL_VISUAL_READING_ZH.md) 记录实际阅读版本、查看页码和可借鉴设计。FastMAE等也属于设计参考。
- [外部比较调研](../04_literature/comparison_candidates/CANDIDATES_ZH.md) 与 [气泡数据审计](../04_literature/research_notes/BUBBLE_DATA_AUDIT_ZH.md) 应与原文一起阅读；跨论文数值不是同协议实测。
- D-FINE本地18页预印本与当前引用的ICLR官方17页版本不同；本地副本一致性不等于出版版本一致性。
- 本索引只登记本次找到的独立文件；不宣称已逐一检查所有历史压缩包内部。

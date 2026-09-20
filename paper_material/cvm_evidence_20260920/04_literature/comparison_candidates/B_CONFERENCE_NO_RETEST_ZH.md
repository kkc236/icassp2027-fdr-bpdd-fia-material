# B 会 DETR 外部对比筛选：不新增复测

核查日期：2026-09-15。

## 结论

本轮没有核实到同时满足以下条件的新增 DETR：近期 CCF B 类主会、有可引用的 VisDrone 成绩、参数约 30–40M、AP 接近且低于 Full 原生 val 30.109。这个结论表示当前证据不足，不表示不存在这样的论文。

不复测可以采用注明来源与实验设置的文献比较。当前可用组合仍为 RemDet-L 原文值、已有 D-FINE-L 实验值和 BDNet 原文值。DEIM-RT-DETRv2-M 缺少所选型号的 VisDrone 成绩，退出当前推荐，不安排新增训练。

## 1. 有实验表的 B 会论文

| 方法 | 正式发表 | 原文 VisDrone AP / AP50 | 参数 | 与本次要求的关系 |
|---|---|---|---|---|
| NRQO | ICME 2025，B | 32.1 / 51.7 | 63M | 原文数字可核查，但明显超过约 35M；也不满足报告 AP 低于 30.109 的要求。其公开正文未明确定位 val/test 划分，不并入明确标成 val 的主表。 |
| DQ-DETR | ECCV 2024，B | val 37.0 / 60.9 | 本轮未核实 | 原文 Table 3 明确 train→val；分数超出用户期望的接近范围，且年份较早。 |

### NRQO 的证据

完整题名：Revisiting DETR for Small Object Detection via Noise-Resilient Query Optimization。

- [ICME 2025 论文集目录](https://www.proceedings.com/content/082/082644webtoc.pdf)收录此文，目录列起始页 5667。
- [作者论文全文](https://arxiv.org/html/2507.19059v1) Table I 给出 VisDrone AP 32.1、AP50 51.7、参数 63M。
- 作者 PDF 第 4 页表格已下载、提取并渲染核对。实现段说明 ResNet-50、12 epochs、AdamW、batch 2、RTX 3090；本轮没有在公开正文中定位到明确的 VisDrone 划分与输入尺寸。
- 它可作为相关工作来源，但当前不能作为“同规模、略低分”的新 DETR 行。

### DQ-DETR 的证据

完整题名：DQ-DETR: DETR with Dynamic Query for Tiny Object Detection。

- [ECCV 2024 正式论文](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/09775.pdf)第 10 页 Table 3，VisDrone val 37.0 / 60.9 / 37.9（AP / AP50 / AP75）。
- 该表明确训练使用 train、评价使用 val。不能把同文 AI-TOD-V2 的 AP 30.2 换成 VisDrone 成绩。

## 2. 已定位发表记录，但未取得可核实实验表的线索

以下均不是已选定对比方法，不填写推测 AP 或参数。

| 方法 | 发表记录 | 当前缺项 |
|---|---|---|
| SODMAMBA-DETR | ICME 2025，B；DOI 10.1109/ICME59968.2025.11210059 | 检索摘要提及 VisDrone 和 AI-TOD；本轮未取得公开全文，参数、AP、划分及输入尺寸未核实。 |
| IG-DETR | ICASSP 2026，B；官方程序 PaperNum 2673 | 已确认题名、作者与会议信息；VisDrone 实验、参数和 AP 均未核实。 |
| CBR-DETR | ICASSP 2026，B；官方程序 PaperNum 16297 | 已确认题名、作者与会议信息；VisDrone 实验、参数和 AP 均未核实。 |

证据入口：

- SODMAMBA-DETR：上述 [ICME 论文集目录](https://www.proceedings.com/content/082/082644webtoc.pdf)列起始页 4855；[IEEE 记录](https://ieeexplore.ieee.org/document/11210059/)。IEEE 页面本轮未返回可读取全文，Semantic Scholar 的开放全文元数据也为空。
- IG-DETR：[ICASSP 2026 官方程序](https://www.cmsworkshops.com/ICASSP2026/view_paper.php?PaperNum=2673&bare=1)，完整题名 Instance-Guided Dynamic Queries for Small Object Detection；View Manuscript 指向 IEEE document 11465098，本轮未取得实验表。
- CBR-DETR：[ICASSP 2026 官方程序](https://www.cmsworkshops.com/ICASSP2026/view_paper.php?PaperNum=16297&bare=1)，完整题名 An Enhanced RT-DETR with Multi-Level Context Fusion and Bi-Level Routing；IEEE document 11462514，本轮未取得实验表。

## 3. 类别核对与排除

类别依据 [2026 年 CCF 目录全文镜像](https://dengpingfan.github.io/papers/CCF-Recommend-2026.pdf)：第 48 页列 ICASSP、ICME、ICMR 为 B；第 58 页列 ECCV 为 B；第 59 页列 BMVC 为 C。此前检索更新曾将 BMVC 当作 B 会候选，应纠正。

- DAMM：BMVC 2025，C，不能满足 B 会条件。其[原文](https://bmva-archive.org.uk/bmvc/2025/assets/papers/Paper_131/paper.pdf)还报告 VisDrone AP 39.5，超出接近范围。
- CFPT：已定位正式记录为 TGRS 2025 期刊，DOI 10.1109/TGRS.2025.3572706，不采用“ICASSP 2025 B 会”的错误标签。[作者仓库](https://github.com/duzw9311/CFPT)。
- RACDet：ICMR 2025 有论文线索，但本轮未完成 DETR 身份和所需数值核查，不纳入新增 DETR 推荐。

## 4. 当前论文可采用的组织方式

**文献比较表**：RemDet-L（AAAI 2025）val AP 29.3、AP50 47.4、35.3M；BDNet（CVPR 2026）val AP 31.2、AP50 50.5、2.59M。两者输入 640、训练 300 epochs。Full 原生 val AP 30.109、AP50 49.890，训练 100 epochs，登记参数约 35.244M。

**已有共同评估表**：D-FINE-L 与 Full 的 best/val 分别为 28.796 和 30.727；best/test 分别为 22.679 和 24.229。沿用已经完成的结果，不新增复测。

文献比较表注可写：

> 外部方法结果取自已发表论文或作者官方资料，† 表示文献报告值。表中列出各方法报告的输入尺寸和训练轮数；由于训练配方及评估实现可能不同，该表用于文献结果比较。共同评估结果另表列出。

不把本项目 native val 30.109、common val 30.727、common test 24.229 混作同一个结果。缺少精确型号、划分或 AP 的候选保持缺省；不增加复测工作，也不填入推测值。

## 5. 核验与本地材料

- 本轮没有运行模型训练、推理或评估。
- NRQO 作者 PDF 第 4 页已进行表头、行列和数值的图像核对。
- 已保存 NRQO 作者 PDF、CCF 2026 目录 PDF、文本提取结果和 NRQO 第 4 页图片；哈希登记于同目录 `verification.json`。
- 其他已核实方法的来源和协议详见同目录 `CANDIDATES_ZH.md`。

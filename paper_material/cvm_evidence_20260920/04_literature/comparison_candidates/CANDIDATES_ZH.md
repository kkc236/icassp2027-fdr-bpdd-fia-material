# 外部对比候选核查

核查日期：2026-09-15。任务范围：为当前 VisDrone、RT-DETR-L 论文选择近期 YOLO、DETR 和高分 A 类会议参照；本轮仅检索与核对，没有运行训练或评估。

## 当前推荐组合：不新增复测，采用有来源的文献结果

用户要求 VisDrone 成绩接近、新增 DETR 参数接近 Full 的约 35.244M，并最新明确“不复测，可以找 B 会”。当前以约 30–40M 为筛选范围；优先 2025–2026 年 A/B 主会，2024 年方法仅列出明确年份的备选。不根据 COCO AP 判断在 VisDrone 上的强弱。下面的 DEIM-M 与 RT-DETR-R34 已退出可直接使用的推荐表；保留其核查记录。B 会筛选详见同目录 `B_CONFERENCE_NO_RETEST_ZH.md`，目前没有核实到同时满足所有条件的新增 DETR。

| 角色 | 方法与建议变体 | 正式发表 | CCF 类别 | 已有证据及使用方式 |
|---|---|---|---|---|
| YOLO 系对比 | RemDet-L | AAAI 2025 主会 | A | 原文 VisDrone val AP 29.3、640 输入；官方仓库登记 35.3M 参数，接近我们的约 35.244M。作者提供代码、配置和 VisDrone 权重，优先新增。|
| DETR 系对比 | D-FINE-L，保留已完成结果 | ICLR 2025 主会 | A，按 2026 年目录 | 已有共同评估 best/val：28.796，对应 Full 30.727；best/test：22.679，对应 Full 24.229。训练配方不同，属于外部系统比较。|
| 近期高分文献参照 | BDNet | CVPR 2026 主会 | A | 原文 VisDrone val mAP50-95 为 31.2，mAP50 为 50.5；本次未找到能够确认属于作者的公开代码仓库。先用于明确标识的文献报告表。|

RemDet-L 29.3 与 Full 原生 val 30.109 的报告数值相差 0.809 pp；BDNet 31.2 则高 1.091 pp。两者都不是统一协议实测差值。D-FINE 的 28.796 必须对应共同评估 Full 30.727，不能与原生 30.109 相减。

会议类别参考 [CCF 目录入口](https://www.ccf.org.cn/Academic_Evaluation/By_category/)及[2026 年目录全文镜像](https://dengpingfan.github.io/papers/CCF-Recommend-2026.pdf)第 57 页的 AI A 类列表；该版本列出 ICLR。正式主会身份依据会议论文集；不是根据仓库名称或预印本年份推定。[D-FINE 的 ICLR 2025 正式论文](https://proceedings.iclr.cc/paper_files/paper/2025/file/6cf58a87e3097e7d1f9be3e8693a93de-Paper-Conference.pdf)。

DEIM-D-FINE-S 的约 10M 参数不符合用户追加的规模要求，已撤出当前推荐。现有资料尚未同时确认“2025–2026 年 A/B 主会、约 30–40M、该具体变体的 VisDrone AP 低于 Full”三项要求，不能通过挪用 S 型成绩补齐 M 型证据。新增 DETR 仍属于候选阶段，没有运行训练或评估。

### 历史同规模候选 1：DEIM-RT-DETRv2-M（R34）；因缺少 VisDrone 成绩退出当前推荐

- [DEIM 官方模型表](https://github.com/Intellindust-AI-Lab/DEIM)的 `DEIM-RT-DETRv2` 分支中，M 为约 31M、92 GFLOPs；该表 AP 50.9 对应 COCO，不是 VisDrone。
- 从该 M 行直接跳转核实的[官方配置](https://github.com/Intellindust-AI-Lab/DEIM/blob/main/configs/deim_rtdetrv2/deim_r34vd_120e_coco.yml)为 R34，并包含 `rtdetrv2_r34vd_120e_coco.yml`。不要误选 M* 行链接的 `deim_r50vd_m_60e_coco.yml`，也不要与 DEIM-D-FINE-M 混同。
- 按公开参数口径，31M 比 Full 35.244M 少约 12%，属于相近量级；文献表应标注为作者报告的参数量，不声称已统一统计配置。
- 方法属于 DEIM 的 CVPR 2025 论文，官方代码可用。本次未核实到该 R34 变体的独立 VisDrone 报告，AP 暂留空。

### 历史同规模候选 2：RT-DETR-R34；原文对比行的划分待核实

- [官方仓库](https://github.com/lyuwenyu/RT-DETR)确认 RT-DETR 发表于 CVPR 2024，R34 型登记约 31M、640 输入、92 GFLOPs。
- [FBRT-YOLO 的 AAAI 2025 论文](https://ojs.aaai.org/index.php/AAAI/article/download/32937/35092)第 5 页 Table 1：RT-DETR-R34 的 VisDrone AP 27.2、AP50 46.0、参数 31.0M。它是后续论文的对比行，不是原始 RT-DETR 官方 VisDrone 成绩。
- 本轮未定位到 FBRT 正文明确写出该行的 val/test 身份及完整基线训练配置，因此不得直接标成同协议 val AP 或与 Full 30.109 相减。
- 该模型与 Full 同属 RT-DETR 家族，骨干和具体实现不同。适合补充另一骨干规模的外部系统对比；论文里仍需保留本项目自己的基线与已有 D-FINE-L。
- 年份比优先范围早，需作为取舍说明；不能标成 2025 方法。

### 已撤出当前推荐：DEIM-D-FINE-S 的历史核查

- 方法发表：[DEIM 的 CVPR 2025 正式论文页](https://openaccess.thecvf.com/content/CVPR2025/html/Huang_DEIM_DETR_with_Improved_Matching_for_Fast_Convergence_CVPR_2025_paper.html)。DEIM 是训练框架，比较时写完整的基础检测器和规模。
- 可执行模型：[官方 S 配置](https://github.com/Intellindust-AI-Lab/DEIM/blob/main/configs/deim_dfine/deim_hgnetv2_s_coco.yml)，属于 `DEIM-D-FINE` 模型表；[官方仓库](https://github.com/Intellindust-AI-Lab/DEIM)提供代码、配置、自定义 COCO 格式数据说明及 COCO 权重。官方表登记约 10M 参数、25 GFLOPs，COCO AP 49.0；不能把 49.0 当作 VisDrone AP。
- VisDrone 成绩线索：[AUHF-DETR: A Lightweight Transformer with Spatial Attention and Wavelet Convolution for Embedded UAV Small Object Detection](https://www.mdpi.com/2072-4292/17/11/1920)，Remote Sensing 2025，Table 7 明确标题为 VisDrone2019-val，DEIM-S 行为 AP 28.1、AP50 46.9、10.18M 参数、25 GFLOPs。
- 该行的规模与官方 D-FINE-S 支系吻合，因此推荐固定官方 DEIM-D-FINE-S；第三方没有在该表给出配置提交与 checkpoint 身份，本轮没有完成其复现实验审计。28.1 是后续研究的报告值，不是 DEIM 原论文官方 VisDrone 分数，更不是本项目的实测值。
- 28.1 的报告值接近 Full 原生 val 30.109，但双方协议未统一，不能把相减得到的约 2 点直接写成已验证的性能增益。
- 其参数约为 Full 的三成，适合作为轻量 DETR 参照。D-FINE-L 继续承担较大规模的现有外部对比；不能只保留 S 型并据此宣称同等模型规模下优于其他 DETR。

## 1. 保留候选：YOLOv12-L，暂不优先

完整题名：YOLOv12: Attention-Centric Real-Time Object Detectors。

- [NeurIPS 2025 正式论文集](https://proceedings.neurips.cc/paper_files/paper/2025/hash/7103444259031cc58051f8c9a4868533-Abstract-Conference.html)
- [作者官方代码](https://github.com/sunsmarterjie/yolov12)
- 选择理由：近期正式 YOLO 论文；补足现有实验中的 YOLO 系外部参照。
- 建议 L 规模：官方仓库当前 Turbo-L 登记约 26.5M 参数，与我们的登记总参数约 35.244M 处于相近规模；此理由是实验设计判断，不意味着容量相等。
- 版本需固定：仓库同时列 Turbo 和 v1.0；最终方法行必须写清实际版本、配置和提交，不能混用两者的性能与参数。
- 仓库主性能表为 COCO。不能将其中的 AP 直接填入 VisDrone 对比表；本次没有确认到该原始论文提供可直接用于我们主表的 VisDrone 结果。
- 作者维护了自己的 Ultralytics 分支；复现优先采用作者仓库，并固定版本。

## 2. 保留候选：DEIM-D-FINE-L，暂不优先新增

完整题名：DEIM: DETR with Improved Matching for Fast Convergence。

- [CVPR 2025 正式论文页](https://openaccess.thecvf.com/content/CVPR2025/html/Huang_DEIM_DETR_with_Improved_Matching_for_Fast_Convergence_CVPR_2025_paper.html)
- [作者官方代码](https://github.com/Intellindust-AI-Lab/DEIM)
- 原文的核心是 Dense O2O 匹配和 Matchability-Aware Loss，可应用于 RT-DETR 和 D-FINE；DEIM 不是一个不依赖基础检测器的唯一网络。
- 建议固定 DEIM-D-FINE-L，官方模型表约 31M 参数。它与已完成的 D-FINE-L 对比形成连续参照，也与当前论文的分布定位及监督组织直接相关。
- 其公开主结果为 COCO；本次没有核实到所选 L 变体的可引用 VisDrone 成绩，因此在“不复测”方案中不新增该行。
- 保留当前已经完成的 D-FINE-L 行。DEIM 行是新增外部训练框架的系统比较，不是我们的独立模块消融。
- 本次未确认 DEIMv2 的正式 A/B 主会论文记录，因此不将其当作已发表 CVPR 2026 方法代替 DEIM。

## 3. BDNet：满足“近期 A 会、原文数值高于我们”的参照

完整题名：BDNet:Bio-Inspired Dual-Backbone Small Object Detection Network。

作者：Wenchao Guan、Chuan Lin、Sihan Huang、Xiongzhen Wang、Xintao Pang。

- [CVPR 2026 正式论文页](https://openaccess.thecvf.com/content/CVPR2026/html/Guan_BDNetBio-Inspired_Dual-Backbone_Small_Object_Detection_Network_CVPR_2026_paper.html)
- [主论文 PDF](https://openaccess.thecvf.com/content/CVPR2026/papers/Guan_BDNetBio-Inspired_Dual-Backbone_Small_Object_Detection_Network_CVPR_2026_paper.pdf)
- [补充材料 PDF](https://openaccess.thecvf.com/content/CVPR2026/supplemental/Guan_BDNetBio-Inspired_Dual-Backbone_Small_CVPR_2026_supplemental.pdf)

### 已逐项核实的结果与设置

| 项目 | BDNet 原文 | 当前 Full |
|---|---|---|
| 数据划分 | VisDrone2019 validation，548 张 | 项目转换的 VisDrone val，548 张 |
| 输入 | 640×640 | 原生验证 640 |
| mAP50-95 | 31.2 | 30.109 |
| mAP50 | 50.5 | 49.890 |
| 参数 M | 2.59，原文口径 | 35.244，现有共同评估登记总参数口径 |
| GFLOPs | 52.44，原文口径 | 当前 Full 尚缺绑定实际推理图的完整测量 |
| 训练轮数 | 300 | 100 |
| 初始化 | 不加载预训练权重 | 无预训练 |
| 物理 batch | 8 | 8 |
| 优化器 | SGD | MuSGD |
| 评价实现 | 原文为 YOLO 格式 mAP50/mAP50-95 | 项目原生 RTDETRValidator；另有独立共同 COCO 评估 |

主论文第 7 页 Table 2（印刷页 32730）给出 31.2/50.5/2.59/52.44；第 6 页说明采用优化 YOLO12、无预训练，并区分文献引用结果与作者重训结果。补充材料第 2 页 Sec. B 给出 640、batch 8、SGD、300 epochs、无预训练及官方数据划分。

31.2 - 30.109 = 1.091 pp 只是已报告数值之间的差距。双方训练轮数、增强、评估实现、标签处理与权重选择没有建立完全一致性，不能据此声称同协议下 BDNet 已经击败 Full。尤其不能拿 BDNet 的 val 31.2 与我们 common test 24.229 相减。

BDNet 的颜色/边缘双骨干设计与航拍小目标任务贴合，适合作为近期强参照。获取代码前，不应把自己根据论文重写的近似实现称为“官方复现”，也不要把同名的其他 BDNet 论文代码当作此文代码。

## 可执行的对比组织建议：尊重不复测的要求

1. 文献比较表采用 RemDet-L 的 VisDrone val AP 29.3、AP50 47.4、35.3M，以及 BDNet 的 val AP 31.2、AP50 50.5、2.59M；显示原文输入尺寸、训练轮数和来源。两者都是 640、300 epochs，Full 原生 val 为 30.109、100 epochs。
2. 现有共同评估表保留 D-FINE-L 与 Full：best/val 28.796 对 30.727，best/test 22.679 对 24.229。无需为这一轮检索重新运行。
3. 文献值可用于说明方法在已发表研究中的位置。表注标明“外部方法取自原文报告，训练和评估设置可能不同”；不把它们写成本项目复现值或严格受控增益。
4. 不新增 DEIM-M 训练计划；没有核实到所选型号的 VisDrone 成绩时保持缺省。RT-DETR-R34 的第三方 27.2 行在划分核实前也不并入 val 主表。
5. 当前 B 会检索没有核实到“约 30–40M、近期主会、VisDrone AP 接近且低于 Full”的完整匹配；NRQO、DQ-DETR 以及尚未取得实验表的线索均在 B 会筛选记录中解释，不强行补齐新增 DETR 行。
6. 本轮没有运行训练、模型推理或模型评估。下载论文和核对实验表不属于模型复测。

## 优先新增：RemDet-L

RemDet（AAAI 2025，A）是当前首选的 YOLO 系航拍对比。完整题名为 RemDet: Rethinking Efficient Model Design for UAV Object Detection。

- [正式论文页](https://ojs.aaai.org/index.php/AAAI/article/view/32490)
- [官方仓库与权重入口](https://github.com/HZAI-ZJNU/RemDet)
- 原文 640/val：RemDet-L AP 29.3，RemDet-X AP 29.9；都不能用作“高于我们 val 30.109”的同尺寸数值例子。
- 原文 RemDet-X† AP 40.0 使用 1024 加 cluster-aware crops，属于不同推理流程，不能填到我们的 640 单图主表。
- RemDet-L 原文 AP50 为 47.4；官方仓库登记参数为 35.3M。与 Full 的登记参数规模接近，是优先 L 而非 74.1M 的 X 的理由。
- 原文使用 300 epochs，而 Full 为 100；在“不复测”方案中可以直接用于带来源和设置说明的文献比较。原文训练与指标见[作者提供的论文全文](https://xinzhongzhu.github.io/document/RemDet_AAAI.pdf)。

## 另一个接近的 YOLO 备用：FBRT-YOLO

完整题名：FBRT-YOLO: Faster and Better for Real-Time Aerial Image Detection。

- [AAAI 2025 正式论文页](https://ojs.aaai.org/index.php/AAAI/article/view/32937)
- [正式论文 PDF](https://ojs.aaai.org/index.php/AAAI/article/download/32937/35092)
- [论文指定的官方仓库](https://github.com/galaxy-oss/FCM)
- 原文第 5 页 Table 1：FBRT-YOLO-L 的 VisDrone AP 为 29.7，AP50 为 47.7，14.6M 参数；X 为 30.1、48.4、22.8M。原文实现段为 300 epochs、SGD、batch 4。
- X 的 AP 报告值约等于我们的原生 val 30.109，不能把四舍五入的 30.1 解释为严格更高或更低。
- 本轮正文可检索文本没有明确定位该表的 validation 划分或 640 输入声明；这些细节仍需配置与权重核验，不把第三方汇总表当成作者原文证据。
- 仓库 README 提供 Vis-FBRT 权重入口，但复现文档简略；存在关于完整训练结构 YAML 的[未解决反馈 #9](https://github.com/galaxy-oss/FCM/issues/9)。该反馈是使用者报告，本轮未完成整个代码库审计，不能据此断言模型无法复现。考虑到 RemDet 的配置与结果更明确，FBRT 先列备用。

## 我方 D-FINE 对比来源

已核对本地 `tmp-work/icassp2027-fdr-bpdd-fia-material/paper_material/evidence/visdrone_dfine_l_external_20260913/common_evaluation_20260915/COMPARISON.md`。所列 best/val 和 best/test 均取 maxDet=300，使用项目转换标签和共同 COCO 评估器；不是官方 VisDrone challenge 协议，也不是匹配训练配方的模块消融。

## 核验记录

- 方法年份与主会身份：正式 NeurIPS/CVF/AAAI 论文集。
- 代码可用性：作者官方仓库公开页面；没有安装代码或下载模型权重。
- BDNet：下载 CVF 主文与补充材料，文本提取并核对相关页面图像。源 PDF 保存在 `sources` 中。
- 我方值：本地 `output/paper_review_20260915/METHOD_EXPERIMENT_ZH.md` 及其已核验的来源材料。

# 新窗口论文写作交接：LRS-GFDR + Capacity-BPDD-v3-Safe + FIA

交接日期：2026-09-15。用途：在新窗口基于现有项目、代码和真实实验，从头组织并撰写会议论文；不是重新训练项目。

**逐项修订入口**：[审计修复状态](reviews/AUDIT_REMEDIATION_20260915_ZH.md)。当前方法统一见 [CURRENT_JOINT_METHOD_ZH.md](methods/CURRENT_JOINT_METHOD_ZH.md)。V12/V13 固定源码已从服务器恢复，之前“BPDD-only 源码取不回”的状态已过时。用户最新要求 UAVDT 暂不处理，留待其另一台服务器单独核验。

## 0. 新窗口启动说明

可将本文件交给新窗口，并发送：

> 请完整读取这份交接文档，并访问其中列出的本地材料与源码。从现有真实实验出发，先确定论文主线、贡献边界和正文/补充表格，再开始撰写论文。当前方法是 LRS-GFDR + Capacity-BPDD-v3-Safe + FIA，不是材料仓根目录旧 train.py 对应的三模块。保留已确认的 baseline 校准及尺度分析口径，不重新训练、不更改指标，不用旧版结果冒充新版。发现资料冲突时，给出具体来源和解决方式，不凭文件标题或 commit 是否相同一刀切判断。先汇报你读到的方法身份、拟用表格和真正缺少的信息，然后开始写作。

本文件是普通项目交接，不是已通过全文完整性审查、预注册或投稿就绪认证。首次创建后已按用户要求进行审计修订；新增资料核验/推理测量不等于重新训练。新窗口后续以用户的新指令为准。

## 1. 用户目标与已确定偏好

- 写出有竞争力的计算机视觉会议论文，用户称目标为“B 会”；历史项目名为 ICASSP 2027，但本轮尚未重新确认具体会议、track、页数和模板。不要承诺录用或默认所有 B 会要求相同。
- 项目基于 **Ultralytics RT-DETR-L**，不是把完整官方 D-FINE 当作自己的 detector。D-FINE 是相关工作和外部比较对象。
- 当前三个模块统一记为 **G=LRS-GFDR、B=Capacity-BPDD-v3-Safe、F=FIA（P3-only）**；Full=G+B+F。
- 用户希望设计故事精致、机理清楚，但必须基于实际实现；不要凭“包装”增加未经验证的首创、零开销或因果结论。B 按“专家＋监督＋KD”的整体模块报告；未隔离证明 KD 单独贡献。
- 用户后续明确选择“整体模块”：KD独立关闭对照不作为当前整体模块主张的必补项，不启动该重训；方法中描述KD机制，但不声称其独立贡献已经隔离。
- 用户不想重新训练自己的模型；写作优先消化已有成果。补实验需先说明必要性，不能默认启动昂贵作业。
- 2026-09-16 用户要求补测batch=8推理，已完成五臂同机640/FP32测量；Full为107.920 ms/8张、摊销13.490 ms/张、74.129张/秒。详见[batch=8实测报告](results/CURRENT_BATCH8_EFFICIENCY_ZH.md)。此前86.075 ms是batch=1整张响应，不是训练batch；不能把batch=8的摊销时间写成单张请求延迟。原始权重/训练源码均未改。
- 比较训练进度时用户默认要多臂、同期 best；论文固定结果则使用各臂按 val AP 选出的 best，不必是同一 epoch。所有 P/R/AP50/AP 必须取同一 best 行，不能拼各指标的最高值。
- Baseline 当前默认使用已安装的锚点宽高校准协议；具体规则见第 6 节。
- 用户已确认：**baseline 的正常尺度退化不自动否定消融增益；完整模块的抗退化收益可计入总体效果，但不得重复计数或把整个差距归给 BPDD/FIA。**

## 2. 文件位置与版本：先读本地，不要只拉旧分支

工作区：

```text
C:/Users/16946/Documents/OBJECTIVE CHECK PAPER
```

本地材料仓根目录：

```text
C:/Users/16946/Documents/OBJECTIVE CHECK PAPER/tmp-work/icassp2027-fdr-bpdd-fia-material
```

本交接文档相对材料仓的位置：`paper_material/PAPER_WRITING_HANDOFF_20260915_ZH.md`。下文 Markdown 链接均相对此文档，可以随整个仓库移动。

材料仓：<https://github.com/kkc236/icassp2027-fdr-bpdd-fia-material>

交接时本地分支为 `codex/uavdt-capacity-v3-safe-joint-20260913`，HEAD 为 `292fa39ecb039d5054a2f3a24724ac0246fe0b61`。**HEAD 不包含当前全部成果**：工作树中有未提交/未推送的校准代码、证据和最新设计文档；不要 reset、clean、checkout 覆盖它们。此次没有核验远端与本地完全同步，不能声称“GitHub 已全部最新”。

尤其需要保留：

- `paper_material/experiments/BASELINE_CURRENT_POLICY_ZH.md`
- `paper_material/experiments/ABLATION_AND_SCALE_DESIGN_ZH.md`
- `paper_material/evidence/reevaluation_completion_20260915/baseline_anchor_test800/`
- `paper_material/evidence/reevaluation_completion_20260915/baseline_anchor_scale_installed_20260915/`
- `paper_material/evidence/reevaluation_completion_20260915/baseline_best_800_20260915/`
- `src/inference_anchor_scale.py`、`scripts/eval_baseline_anchor_scale.py` 及相应测试

若新窗口运行在同一台机器，读取本地即可；若换机器，只发本 MD 能了解背景，但不能获得全部代码、JSON 和日志，需要另行提供材料仓及未提交增补。无需为了写作搬运全部数据集或 checkpoint。

## 3. 必读顺序与证据优先级

建议先读以下七项，再按写作需要查原始文件，不必通读每个历史实验目录：

1. [当前消融与尺度分析设计（含已填 S4/S5）](experiments/ABLATION_AND_SCALE_DESIGN_ZH.md)
2. [当前 Baseline 约定](experiments/BASELINE_CURRENT_POLICY_ZH.md)
3. [正文三张选用表](submission_tables_20260915/selected/MAIN_TABLES.md) 与 [补充 S1/S2/S4/S5/S6](submission_tables_20260915/selected/SUPPLEMENTARY_TABLES.md)
4. [当前联合及 BPDD-only 证据包](evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/README.md)
5. [当前 Full 的实际归档配置](evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/rtdetr-l-lrs-gfdr-capacity-v3-safe-bpdd-fia.yaml)
6. [D-FINE 跨协议完成结果](evidence/visdrone_dfine_l_external_20260913/common_evaluation_20260915/COMPARISON.md) 与 [训练/评估协议](evidence/visdrone_dfine_l_external_20260913/CROSS_PROTOCOL_BS4_ZH.md)
7. [VisDrone 逐项修复与证据边界](reviews/AUDIT_REMEDIATION_20260915_ZH.md)。UAVDT 本轮暂不处理，不列为当前写作必读项。

发生冲突时：

- **指标事实**：对应 run 的 CSV、summary JSON、评估协议及 checkpoint 身份优先于旧 README/聊天记忆。
- **方法身份**：训练时固定的配置、源码和实际运行开关优先于泛称“FDR/BPDD/FIA”的旧说明。
- **解释与写作选择**：采用第 1/2 项最新已确认口径；用户确认解释不等于自动补齐缺失的训练路径证据。
- 相同数值可能来自不同模型；不同小数也可能来自同一权重的不同评估实现。不要按数值相近合并记录，不要跨评估器择高填表。

## 4. 当前三个模块到底是什么

### 4.1 G：LRS-GFDR

当前 G 将 Clean-FDR、几何可行域处理和 LRS-FGL 合并为一个定位模块。可把“有效的逐边分布定位 + 稳定的监督权重”作为整体研究对象，不必把所有实现细节都命名成第四、第五个创新点。

- FDR 定位路径使用四条边各 33 个 bin 的分布，`reg_max=32`、`reg_scale=4.0`、`up=0.5`、累计细化、6 层 decoder、300 queries。
- 当前 Full 配置：`preliminary_box=false`、`distribution_feedback=false`、`feasible_geometry=true`。
- 当前额外 FDR 监督：`fgl_weight=0.15`、`supervise_pre_boxes=false`、`supervise_dn_fdr=false`、`edge_adaptive_fgl=false`。关闭的是额外 FDR/DN 分支，不等于 stock DN 全部关闭。
- LRS 的 `reliability_shrinkage_alpha=0.25` 是收缩系数，不是 FGL 的损失权重。固定源码中，它对符合条件的同图、同层匹配 IoU 权重向均值收缩；收缩强度随 decoder 层次减弱，末层保持原权重。
- 几何约束属于 G 的定义；不能用 baseline 的锚点宽高校准补丁来代称 G 的几何修正，两者是不同位置、不同对象的处理。

来源与归因：D-FINE 启发和基础算子必须正常引用；不能未经核验宣称离散边界、Integral 或基础 FGL 是本文首次发明。作者对自己的设计和数学构造有独立提出的主张，应结合具体实现与相关工作逐项界定，不能凭相似名称认定抄袭，也不能反过来直接认证文献绝对首创。

**旧文档陷阱**：[FDR 方法说明](methods/FDR_ZH.md) 有 AP-FDR 早期 preliminary/额外 DN 监督设计，其默认开启状态不等于当前 G 的实际开关。它可提供基础背景，不能照抄成为当前 Full 的算法描述。

### 4.2 B：Capacity-BPDD-v3-Safe

“BPDD-only”在当前主线中指 **G+B、无 FIA**，不是没有 FDR 的独立 BPDD 检测器。

当前 B 不是旧版未来层 softmin 混合教师的简单改名，而是 **局部边界专家 + 质量门控定位蒸馏** 的容量增强版本：

- 局部专家读取 P2/P3/P4 特征，在预测框附近采样局部信息，以注意力模块生成分布/类别残差；最终层专家预测独立接受固定匹配监督。
- 普通 RT-DETR decoder 主体仍读取 P3/P4/P5；`local_expert_preserve_base=true` 用于保留基础路径，不能写成“整个 decoder 改为四尺度”。
- 蒸馏使用停止梯度的专家输出；要求 query/GT 身份一致、目标边在表示支持域内，并结合逐边 NLL 改善和解码 IoU 门控。
- v3-Safe：定位 KD `loc_weight=0.15`；分类 KD **`cls_weight=0`**；`loc_margin=0.02`、`loc_tau=0.10`；warmup 10–20、decay 80–100，具体使用 completed-epoch 计数，以源码为准。
- 分类 KD 关闭不等于分类头、专家类别预测或其监督都被移除。
- **当前局部专家参与推理、输出专家细化结果，因此 B 整体增加参数和推理计算。** 只有 KD 损失是训练期使用，不能称当前 Capacity-BPDD“无参数、零推理分支”。

**旧文档陷阱**：[BPDD 方法说明](methods/BPDD_ZH.md) 中未来层 softmin、`weight=0.5`、`temperature=0.5`、纯训练期和旧严格配对 +0.239/+0.283 pp 是旧 BPDD 证据，不能替代当前 v3-Safe。两者恰好出现过相近 AP 数值，更不能据此视为同一臂。

### 4.3 F：FIA，当前为 P3-only

- 高分辨率特征增强；模块内部有卷积、通道/空间注意力和零初始化的可学习残差系数。
- 当前 Full 配置图层 22 读取原始 P3（21）；图层 23 也直接从 21 构造 P4，**P4/P5 不级联 FIA 输出**。
- decoder 输入索引 `[1,22,25,28]`：P2 提供局部专家上下文；FIA-P3/P4/P5 送入相应路径。
- P3 增强与 B 的局部专家、蒸馏作用有关联，但“存在梯度/分类目标冲突”是设计动机和可检验解释，不能仅凭联合分数变化就写成已证明的唯一原因。
- [FIA 旧说明](methods/FIA_ZH.md) 混有早期 cascading、旧三模块及 fresh FIA-only 数据；写当前 Full 以当前 YAML 和固定源码为准。

### 4.4 当前源码去哪里看

材料仓根目录的 `train.py`、旧 `src/` 不包含全部当前 Capacity 联合实现，**不要从这个旧入口反推当前方法**。

当前 VisDrone Full 训练源码 commit：`a43056af2a843ec9bae109d3420367c13f3bcef6`。

本机存在可只读查看该 commit 的代码仓：

```text
C:/Users/16946/Documents/OBJECTIVE CHECK PAPER/tmp-work/bpdd-capacity-v2-fia
```

该目录当前 HEAD 不等于 Full 当时 commit。使用 `git show` 精确读取，不必切换或覆盖当前工作树：

```powershell
git -C "C:/Users/16946/Documents/OBJECTIVE CHECK PAPER/tmp-work/bpdd-capacity-v2-fia" show a43056af2a843ec9bae109d3420367c13f3bcef6:src/bpdd_capacity_loss.py
```

同一 commit 下重点文件：`src/fdr_head.py`、`src/fdr_loss.py`、`src/fdr_math.py`、`src/bpdd_capacity.py`、`src/bpdd_capacity_loss.py`、`src/rtdetr_bpdd_capacity.py`、`src/rtdetr_bpdd_capacity_fia.py`、`src/fia.py`。

后续逐项修复已从服务器恢复 Full 与 BPDD-only 的固定源码，两个提交239个共有文件字节一致；新增文件只有无FIA配置、启动器和排队脚本。配置差异核实为FIA插入、P4 bypass与索引调整。实际初始化重放的994个共有状态张量也完全相等，新增19项仅FIA且残差初值为0。见[最新配对结论](evidence/audit_remediation_20260915/SOURCE_PAIR_RESOLUTION_ZH.md)及材料仓内[Full源码快照](evidence/audit_remediation_20260915/source-a43056a/src/rtdetr_bpdd_capacity_fia.py)。不再沿用“源码取不回”限制V12/V13，也不自动推广至其他历史行。

UAVDT 部署代码另有固定版本 `b9f492320d7be35b846c504de84ea3a85077df76`，来源见 [UAVDT 源码身份](evidence/uavdt_capacity_v3_safe_joint_20260913/source-identity.json)，不要误当成 VisDrone Full 的训练提交。

## 5. 写论文用的结果：严格按口径分组

所有表中 AP 指 mAP50–95，表格数值为百分数，差值为百分点 pp；不是相对增长百分比。

### 5.1 原生训练 val：正文大模块表

| 模型 | best epoch | P | R | AP50 | AP |
|---|---:|---:|---:|---:|---:|
| Baseline（登记训练日志） | 参考记录 | 46.761 | 41.731 | 38.663 | 21.911 |
| G | 92 | 59.480 | 49.366 | 49.382 | 29.620 |
| G+F | 97 | 59.391 | 50.049 | 49.548 | 29.773 |
| G+B（v3-Safe） | 80 | 59.826 | 48.524 | 48.783 | 29.277 |
| Full | 97 | 60.482 | 49.693 | 49.890 | 30.109 |

来源：[正文表 2](submission_tables_20260915/selected/MAIN_TABLES.md)、[Full 100 轮 CSV](evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/joint-results.csv)、[B-only 100 轮 CSV](evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/bpdd-current-results.csv)。Full E100 AP=30.065%，B-only E100 AP=28.939%。

按上述记录计算：Full−G=+0.489 pp；G+F−G=+0.153 pp；G+B−G=−0.343 pp；Full−(G+B)=+0.832 pp。**部分旧总表写成 +0.831，是算术/显示误差，不要继续复制。** Full 并不是每项 test 都比 G 明显更高，见后两节。

这些是有来源的真实结果；是否能对某一因素作严格归因，要看对应两臂的训练和有效路径控制。不要因为归档 authority 名称不同直接全盘否定，也不要事后改 authority 使其看起来相同。G+B/Full 的源码、配置与已有共同训练设置现已补证；Base/G/G+F 与其他历史内部版本仍按各自核验范围解释。表 2 使用“组合对照”，不暗示所有行均完成单变量路径认证。

### 5.2 内部设计：正文表 3，不与大模块混排

| 定位版本 | AP50 | AP |
|---|---:|---:|
| Original FDR | 48.473 | 29.078 |
| Clean-FDR | 49.320 | 29.696 |
| Clean-FDR + geometry（无 LRS） | 49.130 | 29.361 |
| LRS-GFDR | 49.382 | 29.620 |

几何版本−Clean 为 −0.335 pp；加 LRS 后相对 geometry 为 +0.259 pp。几何可作为整体有效性设计，不支持“几何单独在 VisDrone 必然涨点”。用户曾报告第二数据集无几何会崩溃，但正式机制结论必须绑定对应原始报错/修复日志，不把口述替代实验。

| BPDD 路线 | 无 FIA AP | 有 FIA AP |
|---|---:|---:|
| Capacity v2 | 29.848 | 29.736 |
| Capacity v3-Safe | 29.277 | 30.109 |

这是联合兼容性版本对照。v3-Safe 联合比 v2 联合高 +0.373 pp，但 BPDD-only 更低，不能写“新版 B 在任何组合都更强”。v2→v3 是一组修改，尚不能把差值逐个归因给关闭分类 KD、衰减调度等。

### 5.3 外部 D-FINE 比较：共同 PIL/COCOeval 640

| endpoint | split | D-FINE-L AP | Full AP | Full−D-FINE（pp） |
|---|---|---:|---:|---:|
| final | val | 28.501 | 30.528 | +2.027 |
| final | test | 22.554 | 24.133 | +1.579 |
| best | val | 28.796 | 30.727 | +1.931 |
| best | test | 22.679 | 24.229 | +1.550 |

上表 maxDet=300。cap100 的完整结果见 [共同评估原报告](evidence/visdrone_dfine_l_external_20260913/common_evaluation_20260915/COMPARISON.md)。按原方案 final 为主终点、best 为次终点；修订后的正文表 1 已同时列出两组，并将 final 放在前面。

次终点 best test 的 AP50：D-FINE 38.940%、Full 42.009%；AP75：22.713% / 24.208%。同一口径的 G+B test AP=24.111%，Full−(G+B)=+0.118 pp（不是 +0.832 pp，后者是原生训练 val）。

训练配方不同：Full batch=8/MuSGD/AMP；D-FINE batch=4/AdamW/FP32，从头训练适配。Full 预热后还存在基础 Trainer 梯度累积，两者并非等有效 batch、等更新次数。可以报告统一推理评估下的外部系统对比，不称严格同训练协议消融，也不叫官方 D-FINE 公开 benchmark 分数。

共同评估使用 PIL 双线性拉伸、FP32、batch=1、无额外 NMS/TTA、score>0.001、最多 300 输出，pycocotools.COCOeval；不能与原生 validator 数值互换。项目 YOLO 转换标注不保留完整 ignore 区域，不是官方 VisDrone challenge 排名。

### 5.4 当前原生 640/800 test：尺度分析

| 模型 | 640 AP | 800 AP | 800 AP50 | 800−640（pp） |
|---|---:|---:|---:|---:|
| 当前校准 Baseline | 17.7426 | 15.4847 | 29.9670 | −2.2578 |
| G | 23.6188 | 24.0595 | 42.3871 | +0.4407 |
| Full | 23.6040 | 24.1598 | 42.4634 | +0.5558 |

来源：[校准 test 与比较汇总 JSON](evidence/reevaluation_completion_20260915/baseline_anchor_test800/RESULTS.json)、[完整报告](evidence/reevaluation_completion_20260915/baseline_anchor_test800/BASELINE_TEST800_ZH.md)。1610 张、75102 个实例；原生 RTDETRValidator、batch=8、workers=8、FP32、conf=0.001、max_det=300、nms=False、rect=False、cache=False、无 TTA。

- 800：G−当前 Baseline=+8.5748 pp；Full−当前 Baseline=+8.6751 pp；Full−G=+0.1003 pp。
- 640：G−Baseline=+5.8762 pp；Full−Baseline=+5.8615 pp；Full−G=−0.0148 pp。
- 这里 Full 的 24.1598% 与上一节 24.229% 不是谁更新就替换谁：尺寸、预处理和 evaluator 分组不同。
- [先前原生四臂 test 复测](evidence/reevaluation_completion_20260915/output/native_test_rerun_20260915.json) 已含 G、G+F、G+B、Full，不要沿用旧总表空格说“都没测过”。该较早复测 G=23.6216%、G+F=23.2187%、G+B=23.6205%、Full=23.6020%；与本节冻结尺度快照有小差异，保留各自协议/实现记录，不拼成新一张“完全同次复测”表。

## 6. Baseline 修复及已确认的解释口径

默认执行入口：[eval_baseline_anchor_scale.py](../scripts/eval_baseline_anchor_scale.py)，实现：[inference_anchor_scale.py](../src/inference_anchor_scale.py)。固定 `--anchor-scale-reference 640`：800 时锚点宽高乘 0.8；640 时恒等操作，保留原生缓存行为。checkpoint 不变，不重训，不修改类别分数或事后挑权重。

| split / 尺寸 | 原生 AP | 校准 AP | 恢复（pp） |
|---|---:|---:|---:|
| val / 640 | 21.9174 | 21.9174 | 0 |
| val / 800 | 15.5931 | 19.1080 | +3.5150 |
| test / 800 | 12.8241 | 15.4847 | +2.6607 |

640 冻结权重复评 21.9174% 与登记训练日志 21.911% 分开，不能只把表 2 的 baseline 换成新复评、其他行仍保留旧日志。

修复版 test 已完成，1610 张且权重/数据前后指纹一致。历史安装验收 JSON 的 `test_not_rerun=true` 只指安装当次；后续 test 证据已补齐，不要据这个旧字段判断当前未测。修复只验证 stock VisDrone baseline，不自动套到 G/Full、UAVDT 或 D-FINE。

已采用的表述原则：

1. baseline 的正常退化不自动否定受控消融；若几何/解码是模块定义，抗退化能力可包含在完整模块收益里。
2. 保留 640 主消融、800 尺度分析、校准控制三类问题；不把 baseline 的 +2.6607 pp 再加到模块增益中。
3. 不因为已有差距较大就声称都是 B/F 的功劳；800 Full−G 仅 +0.1003 pp，640 基本持平。
4. 固定系数 0.8 在修复版 test 前已经 val 验证，本次没有对 test 再搜系数；但 800 及修复研究是看到部分 test 后的诊断扩展，不能写成从未使用 test 的盲测/预注册。
5. 旧原生 800 结果仍保留；当前报告采用较强的校准 baseline，不专挑最低 baseline 最大化收益。

## 7. UAVDT：数据真实，但当前不能直接填入严格增益结论

**用户最新要求：UAVDT 本轮暂不处理，属于另一台服务器的单独实验。** 保留原报告和作者确认，不继续查本台服务器或启动 UAVDT 复评。后续独立处理时有两项需核验：导出绑定实际 checkpoint/配置/专家分支，以及评估样本清单。32,621,369 参数是架构核查线索，不能仅凭数值认定用了旧版，也不能凭作者命名代替权重绑定。

| 对象 | 图像 / 实例 | AP | AP50 | truck AP |
|---|---|---:|---:|---:|
| Baseline | 17165 / 342686 | 15.60 | 27.70 | 6.21 |
| 当前联合导出 | 16592 / 375883 | 16.96 | 29.16 | 4.06 |

baseline 报告为 79 epochs，联合导出为 100 epochs；图像/实例数也不同。+1.36 pp 是两条真实记录的算术差，不是已经通过共同清单复评的模块收益。不能用“作者确认当前方法”替代数据清单一致性检查。

原始用户导出见 [paper_data.txt](evidence/uavdt_capacity_v3_safe_joint_20260913/user_export_20260915/paper_data.txt)，[Baseline 报告](evidence/uavdt_capacity_v3_safe_joint_20260913/baseline_reference_20260915/rtdetr_baseline_test_results.md)，[预留表 4/S3](submission_tables_20260915/selected/UAVDT_TABLE_4_DRAFT.md)。

写作时表 4 先保留为有明确状态的草稿；若未核对完成，不能在摘要写“第二数据集严格提升 +1.36 pp”。truck 的下降也必须保留。该实验是第二数据集上训练/验证，不是 VisDrone→UAVDT 零样本测试。

## 8. 参数、算力、速度：防止沿用旧版数字

- 当前外部比较表登记：D-FINE-L 31.146M，Full 35.244M；这是登记总参数，不等于已剔除所有训练分支的部署参数。
- 较早原生 test 运行摘要的融合模型参数：G 32,334,278；G+B 34,119,764；Full 34,421,240。不要与未融合参数互相替换。
- [旧复杂度表](results/COMPLEXITY_ZH.md) 的 Full 33.458M、约 25 FPS 属于早期方法与其绑定权重，不代表当前 Capacity Full。不能直接拿它给新版填 FPS/GFLOPs。
- UAVDT 是 3 类，VisDrone 是 10 类；不同类别数参数不同，也不能交叉引用。
- 当前五臂同机实测已完成，见[完整效率报告](results/CURRENT_COMPLEXITY_ZH.md)：640、batch1、FP32、含预处理/模型/后处理，100次预热＋300次计时/臂。Baseline/G/G+F/G+B/Full分别为32.688/23.371/22.806/11.708/11.618 FPS。Full中位延迟86.075ms，总参数35,243,576，融合后34,421,240；专家参与推理。该固定输入单机测量不代表所有部署条件。
- 后续[完整GFLOPs测量](results/CURRENT_FULL_GFLOPS_ZH.md)已补齐：Baseline/G/G+F/G+B/Full为105.597/105.804/109.280/130.575/134.051 GFLOPs。按640、batch1、MAC=2及声明的稠密浮点算术合同；所有观察算子有计数或明确的非浮点类别。复合/分解两条记录路径输出完全相同，主要乘加一致，标量差异全部解释。不是硬件指令数，不含外部预处理/评价器及训练损失。旧efficiency.json的partial标记保留，不能据旧字段说当前尚未补齐。

## 9. 论文结构与表格计划

沿用已确定安排：

| 编号 | 内容 | 位置 |
|---|---|---|
| 1 | D-FINE-L 与 Full 的 640 共同 test，final 主、best 次 | 正文，披露跨训练配方 |
| 2 | 640 原生 val：Base/G/G+F/G+B/Full | 正文大模块组合对照 |
| 3(a) | Original/Clean/geometry/LRS 内部版本 | 正文内部设计 |
| 3(b) | Capacity v2/v3-Safe 与 FIA 的兼容性 | 与 3(a) 合为同编号的两个子表 |
| S1 | G+B/Full 的独立共同 test | 补充，正文交代小增量 |
| S2 | D-FINE/Full best 与 final | 补充，避免挑 best |
| 4 / S3 | UAVDT 总体 / 逐类别 | 核对完成后再转正式 |
| S4 | 640/800 尺度响应及完整方案差距 | 补充，正文简述 |
| S5 | Baseline 锚点校准 val/test 控制 | 补充 |
| S6 | 原生 640 test 的 G/G+F/G+B/Full 同次快照 | 补充，保留下降与近似持平 |

现有 Markdown/LaTeX/HTML 入口：[选表 README](submission_tables_20260915/selected/README.md)、[合并正文 LaTeX](submission_tables_20260915/selected/main_tables.tex)、[预览页](submission_tables_20260915/selected/preview.html)。修订后的生成器已包含 S4/S5/S6；原始 JSON 不改，源值核验后生成。尚未在目标会议模板内编译 LaTeX，不据此声称最终排版完成。

建议新窗口先形成会议论文提纲：引言 → 相关工作 → 方法（G/B/F 及联合训练）→ 实验（协议/外部/大模块/内部/尺度）→ 局限与结论。主线可围绕“可靠的分布定位、局部专家监督与推理细化、P3 特征增强的联合设计”。现有证据支持特定配置的 val 改善，test 相对 G 的增量有限；不把 KD 独立有效、梯度冲突已排除或文献首创写成已证实。

方法图须按实际图画：FIA 位于 P3，P4 绕过 FIA；局部专家读取 P2/P3/P4；主 decoder 保留 P3/P4/P5；标清专家监督与停止梯度 KD、推理仍保留的专家路径。

## 10. 需要新窗口处理的事项（不必因此暂停全部写作）

1. 确认目标会议/track、页数模板、写作语言、作者信息。其他已明确的模型/数据/结果不必从零反复问用户。
2. 用固定源码完成当前 G/B/F 的符号、公式、结构图映射；旧方法页默认开关和 Capacity 机制有冲突，必须纠正后再写正文。
3. 把主张与证据关联：完整方案效果、组件受控观察、严格配对旧实验、尺度诊断分级，不把缺失证据写成已经完成。
4. 使用现有文献材料起步，但最终引用、D-FINE 机制对比、论文排名和会议规则需要按原文/官方来源核验；本交接未新增外部文献检索。
5. 使用已生成的正文3表和补充5表，将 S4/S5/S6 纳入最终文稿对应位置。不要把暂缓的 UAVDT 或旧版复杂度混入主结果。
6. 既有 test 已参与开发和诊断；论文如实说明，不继续按 test 选最优设置。单 seed 不声称统计显著，图像 bootstrap 也不能代替训练 seed 重复。
7. 新窗口先给出完整提纲、三项贡献定义、表格选择和缺项清单，然后按章节写；不要先默认新一轮训练、修改模块或删除历史失败记录。

## 11. 可追溯对象与服务器线索（写作通常不需要连接）

已确认的关键冻结权重：

| 对象 | 服务器路径 | SHA-256 |
|---|---|---|
| Baseline val-best EMA（归档 epoch100） | `/root/sj-tmp/checkpoints/fdr-formal-d97e1eb7/fdr-formal-seed0-control-d97e1eb7-epoch-0100.pt` | `9C242711F44B7E68B360AF904AB7C44F64505C7136B7E7F90481092AE3308AF7` |
| G，existing-state，非早停封装短跑 | `/root/sj-tmp/runs/visdrone-v2-existing-state-20260907/formal-seed0-lrs_fdr_feasible-v2/weights/best.pt` | `DF76A0C8BD5B215D378ACB87EB240D7D1DFB44190167CD8C1E19F86FA18C969D` |
| Full E97 | `/root/sj-tmp/runs/formal-safe-capacity-fia-20260912-lrsv2/formal-seed0-capacity-v3-safe-fia/weights/best.pt` | `39F006DF9548B4D5DA968B9302FC14678FABAF2009802BC09A68FB23DD146BC6` |

Baseline 的归档名字虽然带 epoch100，此前已核对它就是该训练记录的验证 best；不要仅因文件名判断“错拿 final”。G 则不要仅凭 `visdrone-v2-lrs-gfdr-20260908` 的目录名误取另一个短跑 checkpoint。

当前 Full 主训练协议：100 epochs、imgsz640、batch8、seed0、MuSGD、pretrained=False、AMP、workers8、nbs64、close_mosaic10；详细以 [joint-authority.json](evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/joint-authority.json) 和 [joint-args.yaml](evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/joint-args.yaml) 为准。公共初始状态 SHA-256=`935D68428BFC5848DE51F82844658ABBC7EC8C99CBBF6BBF823166D38CB65D5B`。

服务器历史工作路径：`/root/sj-tmp/lrs-v2/code`；Python 环境 `/root/miniconda3/envs/lrs-v2/bin/python`。本机 SSH 交互桥为工作区 `tmp-work/suanjia_shell_bridge.py`；服务商可能需要交互菜单而非直接 exec。**不在交接/仓库保存密码或 token**；若用户另行授权服务器操作，再通过安全输入提供。本文未实时检查服务器是否有其他任务，不据此宣称 GPU 空闲。

## 12. 本轮交接的完成边界

- 本 MD 汇总写作状态和入口，不替代原始数据，不复制全部大文件。
- 本轮没有重训、重新挑 best、修改模型、修改历史实验 identity，也没有完成整篇论文或会议审稿认证。
- 已补齐V12/V13固定源码和994个共有初始化状态张量核验、五臂1500个原始推理延迟样本，以及后续声明口径下的完整前向GFLOPs；checkpoint不变。表格保留协议差异和负结果。其他历史配对不能自动认证；B作为整体模块，不要求此轮补独立KD重训；UAVDT按用户要求暂缓。
- 资料中“尚未测 test”“纯训练期 BPDD”“旧 Full 33.458M”等描述必须按其日期和对象理解；不要因为它们位于旧主页面就覆盖本文所指向的新证据。

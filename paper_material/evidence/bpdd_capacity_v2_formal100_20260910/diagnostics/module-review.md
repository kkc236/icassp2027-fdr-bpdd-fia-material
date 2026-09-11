# 改进版 BPDD Capacity v2 技术审查

审查对象是当前 C：LRS-GFDR + 独立局部精修 + quality-gated capacity BPDD。本地提交 `0ec7f489`，远端执行提交 `4fd54d2e926b93107304a9ba51ba66edd7d75c99`。已核对七个核心文件内容一致：`bpdd_capacity.py`、`bpdd_capacity_loss.py`、`rtdetr_bpdd_capacity.py`、`fdr_head.py`、`fdr_loss.py`、`rtdetr_fdr.py`、v2 launcher。

本次为代码审查与隔离诊断。生产代码、训练参数、训练进程未被修改；新增文件仅为本地审查报告、摘要和可复现诊断脚本。审查末次训练观察：第 27/100 轮、614/809 batch，优化器尝试 3150 的三组梯度有限，AMP scale=128 且未跳步。此为观察时点状态，不是对所有未来批次的保证。

## 判断

v1 的关键工程缺口已经有实质修正，当前模型可以继续完成既定训练。尚未发现要求立即废弃本次训练的致命接线错误。但是，分类 KD 的目标与基础 VFL 存在可复现方向冲突，层平均实现会稀释有效 KD，新版机制日志没有接通；第 26 轮的小样本检查还显示精修教师优势较弱。当前不能把“新增约 1.79M 参数”直接解释成更强教师或大幅提升。

## 1. 已确认：分类门控没有与质量感知分类目标对齐

位置：`src/bpdd_capacity_loss.py:299-319`；集成使用 `use_vfl=True`，见 `src/rtdetr_bpdd_capacity.py:132`。

分类门控用 one-hot GT 的 BCE 衡量教师，奖励更接近类别概率 1 的预测；基础 VFL 对匹配正类采用框 IoU 作为软目标。分类 KD 不检查教师相对于学生的解码框质量。两者并不总是方向一致。

调用实际新损失及实际 FDR 分类损失的反例：10 类、学生与教师 IoU 都是 0.4、学生 GT 类概率 0.5、教师为 0.9，其余类概率都为 0.01。

| 实测量 | 数值 |
|---|---:|
| 分类门控激活比例 | 1.0 |
| 加权分类 KD | 0.001028474886 |
| 分类 KD 对学生 GT logit 的梯度 | -0.001117712585 |
| 基础 VFL 对同一 logit 的梯度 | +0.039999999106 |

梯度下降时 KD 要提高分数，VFL 要降低分数，方向相反。这个反例证明目标冲突可以发生；没有证明它主导当前 mAP 差距，反例中的 KD 梯度也小于 VFL 梯度。

第 26 轮的真实抽查中，末层共有 7 个匹配通过分类门控，其中 5 个教师框 IoU 低于学生。这支持继续检查分类与定位质量脱节，但不能仅凭这 5 个框断言它们都造成了 AP 降低。

后续候选应先按基础模型的质量感知目标评估分类教师，并检查 GT 类校准误差、负类抑制与定位质量。只加“教师 IoU 不差”仍不能排除上面同 IoU、过度自信的反例；直接降低阈值或加大分类权重不解决目标不一致。

## 2. 已确认：无激活样本的层也进入均值，与设计不一致

位置：`src/bpdd_capacity_loss.py:296-322`。只要层间身份一致，代码就往 `loc_terms/cls_terms` 追加一项，即使这一层没有任何激活边或分类匹配；最后对所有追加项取均值。设计要求对有 eligible 样本的源层取均值。

实际反例中，只有一层有分类 KD 时损失为 `0.001028474886`；增加五个身份一致、但没有分类 KD 的层后，损失降到 `0.000171412481`，恰为 1/6。

这是可复现的归一化问题。真实训练受影响幅度取决于各层激活分布；不能据单层验证抽查认定全训练都被稀释六倍。后续应分别对定位、分类的有效层做平均，保留全空时的连图零，并记录实际有效层数。这会改变训练目标，应进入独立修订版本。

## 3. 已确认：新版统计未写入运行证据

生产者 `src/rtdetr_bpdd_capacity.py` 输出 `last_capacity_statistics`，损失名为 `loss_bpdd_capacity_loc/cls`。但 `src/lrs_runtime_evidence.py:57-62` 仍读取旧 `last_bpdd_statistics` 与 `loss_bpdd`，且写入旧 `SYSTEM_REVISION`；v2 launcher 直接使用该 recorder。

真实第 26 轮 JSONL 为 `bpdd_observations=0`，active ratio、reliability、loss 全是 null，method revision 仍是 `v2-fp32-extent-logspace-ac-bpdd`。这不是 KD 关闭的证据，而是记录接口没有对接。小型集成反向已经验证新增损失进入总损失、模块能产生非零梯度。

同时，`gradients_finite` 查询了不存在的字段；优化器 JSONL 实际叫 `gradient_norm_finite`。优化器记录可以核验三组范数与 AMP 状态，但没有各分项损失梯度余弦。

`fdr_head.py:553` 丢弃精修解码的 geometry statistics；后续汇总的是原六层。因此既有几何计数不能当作精修分支的完整健康记录。

应接通独立版本的记录器：教师优势、支持越界、有效层数、loc/cls 激活及损失、三组梯度与显存；通过离线 checkpoint 诊断补充当前运行。已经丢失的训练期统计不能追溯性伪造。

## 4. 实测：精修有小幅正向信号，尚未成为明显更强的教师

读取固定已保存的 `weights/epoch25.pt`，其中原始 epoch 字段为 25，即完成第 26 轮；使用其中 EMA、CPU FP32、12 张按文件名排序均匀抽取的验证图像、640×640 拉伸、原第六层 Hungarian assignment。比较同一匹配的原末层与精修输出，并调用生产版 KD 函数检查末层门控。没有训练更新，也没有占用训练 GPU。

| 指标 | 抽查结果 |
|---|---:|
| 图像 / 匹配目标数 | 12 / 943 |
| 原末层平均 IoU | 0.5992793441 |
| 精修后平均 IoU | 0.6000819802 |
| 平均 IoU 差 | +0.0008026069 |
| IoU 改善 / 下降的匹配比例 | 47.51% / 43.90% |
| 末层定位 KD 活跃边 | 1065 / 3772，28.23% |
| 末层分类 KD 活跃匹配 | 7 / 943，0.74% |
| 可表示边比例 | 94.72% |

平均 IoU 差若换成百分点为 +0.0803 pp，**不是 mAP 提升**。这是同 checkpoint 的内部机制检查，也不是独立 B/C 训练对照或正式全验证集评估；不能把末层激活率推广成训练期六层平均。

分类 BCE 对 10 类先平均，又使用 0.02 margin。例如其余类相同、GT 概率从 0.7 升到 0.8，BCE 均值只改善约 0.01335，不会通过门控。阈值本身可以是设计选择，但当前抽查显示它的实际作用较稀疏，后续必须结合有效梯度校准，而不是只看配置中写着 cls_weight=0.10。

精修仍依赖同一 query 和固定 FDR 支持，P2 细节和参数增加没有直接扩大输出范围。约 5.28% 抽查边超支持，应持续分层测量；目前不足以认定它是主要瓶颈。

## 5. 已修正或本次未发现错误的路径

- YAML `[1,21,24,27]` 拆分为 P2/P3/P4 局部输入和 P3/P4/P5 原 decoder 输入。
- 精修只覆盖 normal 查询；小型实际 head+criterion 反向中 DN=200、normal=5，原 decoder 保留六层。
- 原末层 assignment 被复用；小型集成 stock matcher 调用为 7 次，没有新增精修 matcher 调用。
- 独立精修直接监督进入总损失，精修输出层有非零梯度；教师在 KD 中 detach。
- 私有专家使用显式 CPU Generator，修正了原全局 manual_seed 方案；注意力有非重入 checkpoint。
- 原 v1 的 NLL 更优但框更差反例，经过新定位门控后 KD=0、active_edges=0。
- 专家、FDR、公共参数分成三组，真实优化器记录中三组范数存在；最新记录有限且未跳步。

本次新鲜回归：`test_bpdd_capacity.py`、`test_bpdd_capacity_v2.py`、`test_bpdd_capacity_loss.py`、`test_rtdetr_bpdd_capacity.py` 共 **17 passed in 6.73s**。另有独立实际 head/criterion backward 和三项反例探针。通过这些检查不代表模型性能成功，也不覆盖所有部署模式。

## 6. 次要工程缺口

- eval 返回精修后的框与类别，但 `last_corner_logits` 仍保存原末层分布（`fdr_head.py:593`）。验证 FGL 使用原分布和精修框质量权重，诊断口径混合；普通 P/R/mAP 来自精修预测，没有由此发现 mAP 计算错误。
- launcher 无 resume 参数，`CapacityBPDDTrainer.get_model()` 明确拒绝 weights，当前是 fresh-only。checkpoint 存在不等于已验证可从中断处续训；设计中的恢复检查尚未落实。
- 计划所列完整集成、launcher/recorder 测试尚不齐全。现有 v2 head 测试不能替代新版训练记录接口验证。

## 建议

保留当前运行完成既定 100 轮，用现有 checkpoint 做阶段性原末层/精修比较。优先准备记录接口修订，再解决有效层归一化与分类质量目标一致性；不建议现在仅凭小样本直接扩大 KD 权重或再次加参数。若后段精修优势仍很小，应先查精修的直接监督、采样信息和共享梯度，再决定结构调整。

当前跳过 B 后先运行 C 符合用户速度优先的决定。但 C 相对已有基座的结果是完整增容系统结果，单凭它不能量化 KD 独立收益。

补正此前状态描述：`results.csv` 已有逐轮验证 mAP，“尚没有 mAP、要等结束”的表述不正确。

复现文件：`capacity_v2_audit_probe.py`、`capacity_v2_checkpoint_audit.py`；真实抽查汇总：`2026-09-10-capacity-v2-checkpoint-audit-summary.json`。后者为工具输出观测值转录，原始训练产物保留在远端。

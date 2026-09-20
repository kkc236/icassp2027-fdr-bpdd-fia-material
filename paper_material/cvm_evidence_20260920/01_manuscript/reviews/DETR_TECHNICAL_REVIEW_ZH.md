# DETR / D-FINE 技术审稿与公式核验

审查日期：2026-09-17。审查对象：`output/cvm_submission_revision_20260916/source/body.tex`、`build.py`、冻结方法源码，以及训练版本 `a43056af2a843ec9bae109d3420367c13f3bcef6` 的本地归档。该报告供当前多审稿人修订使用，不是新的模型实验，也不认证录用概率。

## 结论

发现一处必须修正的几何公式求值顺序，以及三处宜明确的技术边界。固定参考、LRS eligibility、专家采样、partial-edge IoU gate 与 KD 归一化主公式均与训练源码一致。未重训、未改权重、未连接服务器、未生成检测预测。

## 1. P1：几何公式必须保留括号

旧稿写为 `sg(max(v,f)) + v - sg(v)`，而实现为 `bounded.detach() + (raw_extent - raw_extent.detach())`。理想实数代数相同，但前者若按左结合执行会改变 forward floor。正文应保留 `sg(max(v,f)) + (v - sg(v))`，并说明零值括号项先求值。

冻结源码：[`inputs/frozen_fdr_math.py`](../inputs/frozen_fdr_math.py)，函数 `decode_feasible_fdr_boxes`，第 279–287 行，关键表达式在第 287 行。文件 SHA256：`ac60364c008b048d3dfda619354ce3c1c0e5367b3d8a55de54c49ee43ebebb9a`。

IEEE binary32 反例（仅标量数值）：

| 项目 | 值 |
|---|---:|
| raw extent `v` | -1.0 |
| floor `f=float32(0.00025)` | 0.0002500000118743628 |
| `(f+v)-v`，逐操作 binary32 舍入 | 0.0002499818801879883 |
| `f+(v-v)`，逐操作 binary32 舍入 | 0.0002500000118743628 |

左结合结果小于声明的 floor。这一量级可以对应归一化参考宽度 1、参考缩放 4、两侧 signed distance 均为 -4 的原始 extent，并非只能在巨量非归一化输入下构造的例子。

建议英文：

> The parenthesized zero-valued term is evaluated before addition to the detached bounded extent, preserving the forward floor in floating-point arithmetic while retaining the identity surrogate gradient.

## 2. P1：有限性与可行域前提

“finite inputs and positive reference sizes”本身不能排除后续运算溢出。应说明使用归一化 incoming references、正参考尺度、有界 Integral 输出、至少 FP32，并将实现性质的前提限定为 finite intermediate quantities。

这里的 feasible 是正且可表示的宽高；没有把框中心或全部边界裁进图像。预测框可能延伸到图像外，专家在采样时屏蔽无效坐标。论文不宜让读者误以为该规则也保证 image-contained boxes。

建议英文：

> Decoding is performed outside autocast in at least FP32. With normalized incoming references, positive reference sizes, and finite intermediate quantities, the first floor specifies a minimum extent relative to the reference, while the second accounts for coordinate resolution in the decoding dtype. Here, feasible geometry means positive, representable extents; boxes may extend beyond the image.

实现使用显式 identity surrogate；它不是 hard projection 的数学导数。几何压力测试可以支持实现性质，不能据此声明训练稳定性、真实数据错误频率或 AP 因果提升。

## 3. P2：专家直接损失也反传共享及 base 路径

当前教师不是完全独立参数、独立训练的离线教师。直接专家损失使用未 detach 的专家输出；专家输出又由未 detach 的 base logits 加残差得到。query/features 路径也保留梯度。

以下文件均在训练归档根目录：

`tmp-work/icassp2027-fdr-bpdd-fia-material/paper_material/evidence/audit_remediation_20260915/source-a43056a/src/`

- `bpdd_capacity.py:116`：只为分布描述符对 `corners` detach；不是对后续所有 base logits detach。
- `bpdd_capacity.py:120`：`query = query + self.distribution(...)`，保留原 query 梯度。
- `bpdd_capacity.py:143`：`return corners + self.box_out(h), classes + self.class_out(h)`，两个 residual base-logit 路径均未 detach。
- `fdr_head.py:546`：向专家传入 base query、cumulative corners 和 class logits；第 550 行只对采样框 `refined` detach。
- `rtdetr_bpdd_capacity.py:77`：调用 `fixed_assignment_expert_loss`，第 78–80 行传入未 detach 的专家 boxes/scores/corners。
- `rtdetr_bpdd_capacity.py:91`：只有在 KD 调用处显式传入 `expert_corners.detach()`，第 92 行相同处理 expert scores。
- `frozen_fdr_loss.py:450`：`fixed_assignment_expert_loss` 定义；第 463 行开始调用直接检测损失，随后调用单层 FGL。

建议英文：

> Direct expert supervision also updates the shared feature/query path and the base logits through the residual connection. Sampling coordinates and distribution descriptors are detached; the expert distributions are additionally detached when used as localization targets.

这里描述计算图可达路径，不意味着任意样本、任意初始化时刻所有参数梯度都非零；例如零初始化 residual head 会在初始步限制其上游梯度。

## 4. P2：LRS 最值得强调的数学性质

`frozen_fdr_loss.py:57` 定义 LRS；第 131 行定义 eligibility；第 308 行把其接入 normal-query FGL。冻结文件 SHA256：`ac60523868ebfdeaeaf63e906095225813f6c250a833f2beb1feea84585c2ecb`。

对于同图同层 eligible group，令 `q'=(1-alpha)q+alpha mean(q)`。理想算术下：

- 总权重保持。
- 两个对象的权重差变为原差的 `1-alpha` 倍，因此保持质量排序并降低集中程度。
- 组内方差乘以 `(1-alpha)^2`。
- `q'_i >= alpha mean(q)`；只要 alpha 和组均值为正，eligible 零 IoU 对象可获得非零 FGL 权重。
- 全零组保持全零，单例、末层和 ineligible match 保持原权重。
- 不同图像不交换权重；ineligible 对象不参与收缩均值，但仍接受原始 FGL。

实现的 FP32 residual correction 会有微小舍入扰动，不应把理想实数中的精确排序/总和性质说成所有浮点输入下无条件的 bitwise 保证。

建议正文用“moderates weight concentration without reversing quality ordering”概括。`reliability` 是 IoU quality proxy，并没有校准实验；不应暗示概率校准、降低梯度方差或保证收敛。

## 5. 关键一致性审查结果

| 项目 | 审核结果与证据 |
|---|---|
| 固定分布参考 | 当前 `fdr_head.py:483` 设置 `initial_reference`，六层及专家共用；第 608 行仅更新 attention 的 `reference`，不能混写两者 |
| FDR cumulative path | `fdr_head.py:491` 用当前 query 与上一层 detach query 的和生成 residual；第 503 行后累积 corner logits |
| LRS eligibility | 全部四边左 interpolation-bin 索引严格 `0 < index < 31`；不是只检查一个边，也不是删除边界目标监督 |
| expert sampling | `bpdd_capacity.py:10` 定义两套各 20 点加中心，41 点乘三尺度共 123 tokens；无效坐标 mask |
| descriptor 与 geometry | descriptor mean 使用均匀 bin-index 坐标；实际解码仍使用非均匀 support |
| 直接监督 | 最后 base layer 的匹配复用，分类/L1/GIoU/FGL 均存在，不能称无监督教师 |
| correspondence | `bpdd_capacity_loss.py` 的 `_identity_mask` 同时检查 image/query/GT identity |
| support 与 edge weight | `raw_fdr_targets` 使用未截断距离检查逐边支持域；margin=0.02、tau=0.10 |
| partial-edge IoU gate | `bpdd_loss.py:110` 起，inactive edges 保留 student；第 128–129 行同一 feasible decoder；第 141 行严格 IoU improvement |
| KD 归一化 | `bpdd_capacity_loss.py:335` 按 active edge 数归一化，之后平均 active layers；不是除以权重和 |
| 教师与部署 | KD teacher detach；推理保留专家输出，IoU gate 不是推理时动态择优 |

## 6. D-FINE 归属边界

已重新检查官方固定版本 `7fe2f8889f0b7b817f20c315b40fc15a4fb64ae6`：离散边分布、非均匀 support、Integral、cumulative logits、初始固定分布参考、adjacent-bin FGL 属于继承部分。官方 decoder 第 385–408 行清楚体现 fixed initial reference 与逐层 attention reference 的区别。

主来源：

- [D-FINE 官方 decoder 固定版本](https://raw.githubusercontent.com/Peterande/D-FINE/7fe2f8889f0b7b817f20c315b40fc15a4fb64ae6/src/zoo/dfine/dfine_decoder.py)
- [D-FINE 官方 criterion 固定版本](https://raw.githubusercontent.com/Peterande/D-FINE/7fe2f8889f0b7b817f20c315b40fc15a4fb64ae6/src/zoo/dfine/dfine_criterion.py)
- [D-FINE ICLR 2025 原文](https://openreview.net/pdf?id=MFZjrTFE7h)

其论文已经研究 FDR 向其他 DETR 的移植。我们的可辨识设计集中在 center-preserving extent floors + surrogate、同图同层质量权重重分配及深度调度、shared decoder 下 actual partial-edge target check。Original FDR 是完整 FDR/FGL 移植参考，不是完整官方 D-FINE 检测器，也不等于 Clean-FDR。

## 7. 非模型公式检查

[`source/check_formulation.py`](../source/check_formulation.py) 仅使用 Python 标准库 `struct`、`Fraction`、`ast` 等，输出 [`formulation_checks.json`](formulation_checks.json)。

检查内容包括：binary32 括号反例；冻结几何源码 AST 的求值结构；4,650 个小规模有理数组/层组合的预算、排序、方差、凸包及末层性质；零权重、全零组、单例、ineligible 和跨图像隔离案例。LRS 检查使用精确矩阵形式，验证独立不变量；不执行生产损失函数，不把软件检查当作检测实验。有限例子用于辅助核验公式，不构成通过穷举证明任意输入性质；通用结论来自上述代数恒等式。

## 8. 不能靠改写消除的风险

单数据集单种子；历史 localization rows 未全做 source/init matched single-factor 对照；Clean-FDR 在记录中比 G 高 0.076 AP；G+B 低于 G，不能隔离证明专家或 KD 独立增益；外部 D-FINE 训练配方/有效 batch 不同；几何压力测试不等于真实数据失败率。

处理原则：集中交代协议与证据适用范围，保留数据，不在全文重复防御性表述；以已有设计性质和可比端点支持贡献，不用夸大因果主张掩盖边界。

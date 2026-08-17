# ICASSP 2027 四图规划

## 图 1：整体架构

- 目的：展示 RT-DETR-L Backbone/Hybrid Encoder、三尺度特征、FDR decoder、训练期 BPDD 和修改后 FIA 的关系。
- 当前可画：baseline、FDR 与 BPDD 的已绑定数据流。
- FIA 部分：只保留待最新源码核验的占位边界；完成源码与配置绑定后再冻结插入位置和连接索引。
- 禁止标签：BPDD inference branch、FDR invented here、未经源码验证的 FIA 内部结构或额外检测头。

## 图 2：BPDD 解码器监督

- 目的：展示相邻 decoder layer 的 FDR 边分布、教师筛选与渐进蒸馏。
- 必须标注：训练期监督、教师停止梯度、有效边激活条件、BPDD 不进入推理图。
- 源码依据：src/bpdd_loss.py、src/rtdetr_fdr_bpdd.py 及对应配置。
- 禁止标签：feature distillation、trainable teacher、denoising-query BPDD、standalone BPDD 或无条件激活全部教师边。

## 图 3：FIA 模块

- 目的：呈现修改后 FIA 的真实特征增强结构。
- 当前状态：暂不复用旧 FIA 示意图；待最新源码、配置和 P3-only checkpoint 身份完成绑定后，从代码重新绘制。
- 必须验证：输入输出、内部算子、残差路径、插入尺度、训练和推理行为。
- 禁止标签：从旧实现推断的层数、注意力结构、公式、参数量或开销；不得把修改前模块图继续标成最终 FIA。

## 图 4：结果比较

- 正式子图：只展示 RT-DETR-L、RT-DETR-L+FDR 和 RT-DETR-L+FDR+BPDD 三条当前可审计结果，并明确证据等级。
- 待核验标记：可在图注中说明正确 P3-only 新三模块 checkpoint 已取得 mAP50–95=0.29618 的 best-val 正向观察，相对当前 BPDD val 绝对值为 +0.3922 pp；不与正式柱形混排。
- 待补字段：新三模块 AP75、test 和冻结 evaluator 独立复评；新版 FIA-only 与 FDR+FIA 资产。
- 禁止内容：任何修改前 FIA 数值、截图柱形、旧方向性结论、伪造误差条、显著性符号或把 best-val 观察标成严格配对结果。

FIA 图与结果图的启用条件见 [FIA 结果状态](../results/FIA_RESULTS_STATUS_ZH.md)。

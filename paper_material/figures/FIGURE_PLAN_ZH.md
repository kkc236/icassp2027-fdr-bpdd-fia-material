# ICASSP 2027 四图规划

## 图 1：整体架构

- 目的：展示 RT-DETR-L Backbone/Hybrid Encoder、三尺度特征、FDR decoder、训练期 BPDD 和修改后 FIA 的关系。
- 当前可画：baseline、FDR 与 BPDD 的已绑定数据流。
- FIA 部分：按当前源码画成 P3 上的恒等安全增强块；P3-only 三模块中 FIA 和 P4 重建都读取原始 P3，decoder 使用增强 P3、P4、P5。
- 禁止标签：BPDD inference branch、FDR invented here、额外检测头，或把 published cascading standalone 画成 P3-only。

## 图 2：BPDD 解码器监督

- 目的：展示相邻 decoder layer 的 FDR 边分布、教师筛选与渐进蒸馏。
- 必须标注：训练期监督、教师停止梯度、有效边激活条件、BPDD 不进入推理图。
- 源码依据：src/bpdd_loss.py、src/rtdetr_fdr_bpdd.py 及对应配置。
- 禁止标签：feature distillation、trainable teacher、denoising-query BPDD、standalone BPDD 或无条件激活全部教师边。

## 图 3：FIA 模块

- 目的：呈现修改后 FIA 的真实特征增强结构。
- 当前可画：两个 `FIABaseBlock` 顺序细化后接通道/空间联合注意力，外层使用零初始化标量残差 `Y=X+α(F(X)−X)`。
- 必须标注：`1×1—DWConv 3×3—1×1`、每块两条内部残差、通道平均池化门控、mean/max 空间门控、P3 输入输出和构造期 RNG 隔离。
- 禁止标签：未经测量的参数量/延迟，或把 published cascading standalone 的结果身份标成 P3-only。

## 图 4：结果比较

- 正式子图：展示 RT-DETR-L、RT-DETR-L+FDR 和 RT-DETR-L+FDR+BPDD 三条核心结果，并明确证据等级。
- 消融附图：可加入现有 best.pt 的 FIA-only `0.216795` 与 FDR+FIA `0.294940` 独立 val，分别标注相对 baseline `−0.231 pp`、相对 FDR `+0.528 pp`。
- test 附图：可加入 FIA-only / FDR+FIA 的 mAP50–95 `0.177176` / `0.234645` 与 AP75 `0.171613` / `0.235879`，或使用 10 类 mAP 对比；明确证据为 independent exact test。
- 三模块标记：正确 P3-only checkpoint 的 mAP50–95=0.29618，作为 best-val 观察，不与 exact 独立复评混成同一证据等级。
- 禁止内容：把 standalone best.pt 标成 P3-only、混写 val/test、伪造误差条或显著性符号、把算术差写成严格配对因果结果。

FIA 图与结果图的启用条件见 [FIA 结果状态](../results/FIA_RESULTS_STATUS_ZH.md)。

# ICASSP 2027 四图规划

## 图 1：整体架构

- 目的：展示 RT-DETR-L Backbone/Hybrid Encoder、三尺度特征、AP-FDR decoder、训练期 BPDD 和修改后 FIA 的关系。
- 当前可画：baseline、AP-FDR（结果表标签 FDR）与 BPDD 的已绑定数据流。
- FIA 部分：按当前源码画成 P3 上的恒等安全增强块；fresh FIA-only 与 P3-only 三模块中，FIA 层 22 读取上一层 21，层 23 也显式读取原始 P3（`f=21`），decoder 使用 `[22,25,28]`。
- 禁止标签：BPDD inference branch、FGL/Integral invented here、额外检测头，或把层 23 仍为 `f=-1` 的旧 cascading checkpoint 画成 P3-only。

## 图 2：BPDD 解码器监督

- 目的：展示相邻 decoder layer 的 AP-FDR 边分布、教师筛选与渐进蒸馏。
- 必须标注：训练期监督、教师停止梯度、有效边激活条件、BPDD 不进入推理图。
- 源码依据：src/bpdd_loss.py、src/rtdetr_fdr_bpdd.py 及对应配置。
- 禁止标签：feature distillation、trainable teacher、denoising-query BPDD、standalone BPDD 或无条件激活全部教师边。

## 图 3：FIA 模块

- 目的：呈现修改后 FIA 的真实特征增强结构。
- 当前可画：两个 `FIABaseBlock` 顺序细化后接通道/空间联合注意力，外层使用零初始化标量残差 `Y=X+α(F(X)−X)`。
- 必须标注：`1×1—DWConv 3×3—1×1`、每块两条内部残差、通道平均池化门控、mean/max 空间门控、P3 输入输出和构造期 RNG 隔离。
- 禁止标签：未经测量的参数量/延迟，或把既有 FDR+FIA cascading 结果身份标成 P3-only。

## 图 4：结果比较

- 正式子图：展示 RT-DETR-L、RT-DETR-L+FDR 和 RT-DETR-L+FDR+BPDD 三条核心结果，并明确证据等级。
- 消融附图：可加入 fresh P3-only FIA-only `0.227056` 与既有 cascading FDR+FIA `0.294940` 的独立 val，分别标注相对 canonical baseline `+0.7946 pp`、相对 FDR `+0.5280 pp`，同时标明 topology 不同。
- test 附图：可加入 FIA-only / FDR+FIA 的 mAP50–95 `0.185517` / `0.234645` 与 AP75 `0.182011` / `0.235879`；fresh FIA-only 可标注相对 protocol-comparable canonical test baseline 的 `+0.8101 pp`，但不得跨 val/test 计算。若画逐类图，fresh FIA-only 只使用新 exact JSON/CSV 中与 checkpoint SHA `c00cae89…` 绑定的十类结果，不复用旧 cascading 行。
- 三模块标记：正确 P3-only 的四位小数 val/test mAP50–95 分别为 0.2961（+0.384 pp）和 0.2337（+0.204 pp），两者均为正增长；可同时展示 AP75=0.3042/0.2327，证据标为 `user_supplied_text_report_4dp`。
- 禁止内容：把既有 FDR+FIA cascading best.pt 标成 P3-only、把旧 FIA-only cascading 数值当作当前结果、混写 val/test、伪造误差条或显著性符号、把算术差写成严格配对因果结果。

FIA 图与结果图的启用条件见 [FIA 结果状态](../results/FIA_RESULTS_STATUS_ZH.md)。

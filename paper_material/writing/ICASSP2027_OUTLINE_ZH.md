# ICASSP 2027 写作提纲：LRS-FDR / BPDD / FIA

> **方法身份冻结于 2026-08-28。** 当前第一定位方法为 LRS-FDR；NA-FDR 是其
> 原生对齐基础与 `w/o LRS` 内部消融。EQuAL、AP-FDR、DCF-FDR 和官方 D-FINE-S
> 替代 detector 路线仅保留为历史审计，不再等待切换回正文。

## 1. 中心命题

论文不写成三个任意插件的列表，而按密集 UAV 检测中的三类相互依赖问题组织：

```text
逐边定位表示与浅层监督失衡
  -> LRS-FDR（NA-FDR 原生对齐 + LRS-FGL 可靠性收缩）
早期 decoder 层缺乏可靠跨层知识
  -> BPDD（训练期边界分布蒸馏）
高分辨率 P3 表征不足
  -> FIA（轻量 P3-only 增强）
```

LRS-FDR 产生逐层四边分布，BPDD 消费这些分布进行训练期跨层优化，FIA 从特征侧
增强高分辨率输入。三者存在明确的数据依赖，不是平行堆叠。

## 2. 三项贡献

### 贡献 1：LRS-FDR 统一定位模块

**问题**：历史 FDR 的 learned preliminary reference 与额外 DN-FDR 监督未得到
内部结果支持；基础 IoU-weighted FGL 又会使浅层低 IoU 正常匹配获得较弱分布
监督。

**设计**：NA-FDR 把分布几何锚点、Hungarian assignment 和额外分布监督范围统一
对齐到 stock RT-DETR 的 native reference 与 normal matched queries；LRS-FGL
在四边目标均可表示的同图像、同层集合内执行停止梯度、总权重守恒、随 decoder
深度衰减的 IoU 可靠性收缩。二者共同组成一个最终 LRS-FDR 模块。

**证据**：NA-FDR 相对 Original FDR 的 mAP/AP75 为 `+0.616/+0.699 pp`；LRS-FDR
相对 NA-FDR 的 mAP/AP75/Recall 为 `+0.011/+0.471/+0.227 pp`；完整 LRS-FDR
相对 Original FDR 为 `+0.627 pp` mAP、`+1.170 pp` AP75 和 `+0.919 pp`
Recall。结果来自同一冻结评估器的 seed0 描述性消融。

### 贡献 2：BPDD 训练期跨层分布蒸馏

**问题**：早期 decoder 层定位较弱，固定最终层教师不能保证对每个目标边更可靠。

**设计**：BPDD 从全部未来层构造目标边质量加权教师，只在教师优于当前层时执行
better-only 蒸馏，并复用 stock assignment。BPDD 只在训练期工作，不增加推理
参数、FLOPs 或分支。

**证据**：旧 AP-FDR 严格配对中，BPDD 的 val/test mAP 增益为
`+0.239/+0.283 pp`，test AP75 为 `+0.276 pp`。该结果支持 BPDD 机制，但不是
LRS-FDR+BPDD 新组合结果；新组合必须重训后才能进入最终主表。

### 贡献 3：FIA 高分辨率表征增强

**问题**：640 输入下的密集小目标依赖 P3，级联修改 P4/P5 会扩大干预范围。

**设计**：FIA 以 P3-only 拓扑插入双 depth-wise 残差细化、联合通道/空间门控和
零初始化残差缩放，同时保持 P4/P5 从原路径构建。

**证据**：fresh P3-only FIA-only 在 val/test 上相对相应 baseline 的描述性算术
增益为 `+0.7946/+0.8101 pp`。既有 AP-FDR+FIA 和三模块结果只作历史兼容性
证据，不能改名为 LRS-FDR 组合。

## 3. 论文结构

### 1. Introduction

1. 无人机俯视图像的小目标、遮挡、边界像素敏感和密集背景；
2. RT-DETR 的三个缺口：定位分布与浅层监督、跨层可靠知识、高分辨率表征；
3. LRS-FDR、BPDD、FIA 的依赖链和本文范围；
4. 贡献列表只引用已经登记的证据强度，不使用 `significant` 或 `SOTA`。

### 2. Related Work

- Transformer-based UAV detection；
- Distributional box regression 与 D-FINE；
- Query quality weighting 与低质量匹配监督；
- Decoder-layer self-distillation / GO-LSD；
- UAV 小目标的高分辨率特征增强。

必须明确：33-bin 四边分布、non-uniform Integral、累计细化和基础 FGL 来自
D-FINE；本文第一贡献是 NA-FDR 的原生对齐组织和 LRS-FGL 的具体可靠性收缩合同。

### 3. Method

- **3.1 Overall Architecture**：RT-DETR-L → LRS-FDR → training-only BPDD；FIA
  只增强 P3；
- **3.2 NA-FDR Native Alignment**：native reference、stock assignment、
  normal matched-query FGL；
- **3.3 LRS-FGL**：可表示性防火墙、同图像同层均值、六层 alpha 日程、总权重
  守恒、最终层恒等；
- **3.4 BPDD**：未来层教师、better-only gate 和仅训练期边界；
- **3.5 FIA**：P3-only 拓扑和零初始化残差；
- **3.6 Objective and Inference**：总损失、参数/推理身份和组合接口。

### 4. Experiments

- **4.1 Setup**：VisDrone、split、640、seed0、100 epochs、best-val 选择、冻结
  evaluator、单 seed 限制；
- **4.2 FDR Main Result**：Original FDR / NA-FDR / LRS-FDR；
- **4.3 Internal Ablation**：NA-FDR 是 `w/o LRS`，完整 LRS-FDR 是 Full；不重放
  EAW、DCF 或 historical preliminary/DN 开关；
- **4.4 Scale and Class Analysis**：总体、Tiny/Small/Medium/Large、十类别方向与
  late-training；
- **4.5 BPDD/FIA Evidence**：先报告各自真实历史机制证据；LRS-FDR 新组合完成后
  才加入当前主表；
- **4.6 External Comparison and Complexity**：按 split/input/协议分层，不声称
  不受控跨论文 SOTA；
- **4.7 Second Dataset**：Baseline / Baseline+NA-FDR / 完整投稿方法三组。

### 5. Conclusion and Limitations

结论限定为：LRS-FDR 在 VisDrone seed0 上相对 Original FDR 总体正向；NA-FDR
提供主要基础增益，LRS 进一步形成 AP75/Recall 取向。限制明确写单 seed、第二
数据集尚未完成、Tiny/Small 内部回落、LRS 末十轮平台不优于 NA-FDR，以及最终
BPDD/FIA 新组合仍需训练。

## 4. 正文 FDR 表格

### 4.1 总体主表

| Method | P | R | F1 | AP50 | AP75 | mAP50-95 |
|---|---:|---:|---:|---:|---:|---:|
| Original FDR | 0.570249 | 0.491417 | 0.527907 | 0.484700 | 0.294070 | 0.290698 |
| NA-FDR | **0.587045** | 0.498339 | **0.539067** | **0.493119** | 0.301061 | 0.296855 |
| LRS-FDR | 0.579512 | **0.500606** | 0.537177 | 0.491805 | **0.305773** | **0.296968** |

### 4.2 内部消融表

| Method | Native alignment | LRS | mAP | AP75 | Recall |
|---|:---:|:---:|---:|---:|---:|
| Original FDR | 否 | 否 | 0.290698 | 0.294070 | 0.491417 |
| NA-FDR (`w/o LRS`) | 是 | 否 | 0.296855 | 0.301061 | 0.498339 |
| LRS-FDR (`Full`) | 是 | 是 | **0.296968** | **0.305773** | **0.500606** |

这张表是第一创新的完整内部归因，不再使用历史运行别名作为论文行名。

## 5. 图表安排

1. Fig. 1：RT-DETR-L / LRS-FDR / BPDD / FIA 总体依赖；
2. Fig. 2：NA-FDR 与 Original FDR 的 reference/query 组织差异；
3. Fig. 3：LRS-FGL 可表示性防火墙、均值收缩、alpha 日程和守恒；
4. Fig. 4：三臂总体/尺度结果与 LRS AP75-Recall trade-off；
5. Table 1：与近期 VisDrone 会议方法比较；
6. Table 2：Original FDR / NA-FDR / LRS-FDR；
7. Table 3：最终系统消融，待 LRS-FDR+BPDD+FIA 新组合完成后填入。

禁止伪造误差条、显著性符号、未运行组合行或第二数据集结果。

## 6. 投稿前实验优先级

1. 固定并训练 LRS-FDR + BPDD + FIA 的最终 VisDrone 组合；
2. 执行第二数据集三组矩阵；
3. 对最终组合统一测 Params/FLOPs/Latency；
4. 若剩余算力足够，再为 NA-FDR/LRS-FDR 关键臂补多 seed；
5. 不继续调 `alpha0`，不恢复 EAW/DCF，不增加第四个定位机制。

## 7. 禁止句式

- “本文首次提出离散分布框回归、Integral、FGL 或累计 FDR”；
- “LRS-FGL 显著提高总体 mAP”；
- “LRS-FDR 全尺度、全类别提升”；
- “NA-FDR 只是删除两个开关，因此不需要单独归因”；
- “旧 AP-FDR+BPDD/FIA checkpoint 等同于新 LRS-FDR 组合”；
- “单数据集、单 seed 已证明泛化和稳定性”。

## 8. 权威链接

- [LRS-FDR 方法](../methods/FDR_ZH.md)
- [LRS-FDR 结果](../results/LRS_FDR_RESULTS_ZH.md)
- [LRS-FDR 证据包](../evidence/lrs_fdr_formal100_20260828/README.md)
- [当前实验状态](../CURRENT_RERUN_STATUS_ZH.md)
- [冻结设计](../../docs/superpowers/specs/2026-08-28-lrs-fdr-material-freeze-design.md)

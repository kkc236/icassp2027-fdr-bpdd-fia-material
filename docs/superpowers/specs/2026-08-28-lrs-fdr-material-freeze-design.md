# NA-FDR / LRS-FDR 主材料冻结设计

## 1. 目标与作者裁决

本设计冻结 ICASSP 2027 主材料中的第一项定位创新。作者已明确裁决：

- 不再以 D-FINE-S 或 EQuAL 作为当前投稿路线；
- 不再把 `Clean FDR` 作为论文方法名；
- 将原 `Clean FDR` 的算法语义固定为 **NA-FDR**；
- 将 NA-FDR 加入 LRS-FGL 后的算法固定为最终完整模块
  **LRS-FDR**；
- `Original FDR`、`Clean FDR`、`lrs_fdr` 等旧名称只作为原始运行、配置、
  checkpoint 和历史证据标识保留，不回写或伪造历史记录。

主材料的规范方法链为：

```text
Original FDR
  -> NA-FDR（原生 reference 与有效查询监督对齐）
  -> LRS-FDR（加入分层可靠性收缩后的最终完整模块）
```

## 2. 规范命名与身份映射

| 规范论文名称 | 历史运行名称 | 算法身份 | 论文角色 |
|---|---|---|---|
| Original FDR | Original FDR / AP-FDR | preliminary reference、额外 DN-FDR 等历史完整实现 | 来源与外部/历史对照 |
| NA-FDR | Clean FDR | native reference、normal-query FGL、关闭 preliminary/DN-FDR/EAW | LRS-FDR 的基础设计和 `w/o LRS` 内部消融 |
| LRS-FDR | Clean FDR + LRS-FGL / `lrs_fdr` | NA-FDR + LRS-FGL，`alpha0=0.25` | 最终完整 FDR 模块 |

“Clean FDR”不得继续出现在论文标题、贡献点、方法图、方法正文或主消融表的
方法名称中。它只允许出现在括号中的历史证据映射，例如
“NA-FDR（历史运行标识：Clean FDR）”。

## 3. NA-FDR：原生对齐基础设计

NA-FDR 表示 **Native-Aligned Fine-grained Distribution Refinement**。它不是
简单的“清理版本”，而是对 FDR 几何锚点和分布监督范围的联合重组：

1. **原生 reference 对齐**：关闭 learned preliminary-box reference，直接使用
   RT-DETR decoder 的原生 reference 组织累计四边分布细化；
2. **原生 assignment 对齐**：FGL 复用 stock Hungarian matching，不增加第二套
   matcher；
3. **有效查询对齐**：额外分布监督只作用于 normal matched queries，不在扰动
   DN queries 上追加 FDR/FGL；stock DN 分类、L1 和 GIoU 仍完整保留；
4. **隔离变量**：关闭 preliminary-box loss 和 EAW，保留 33-bin 四边分布、
   non-uniform Integral、累计细化和 `fgl_weight=0.15`。

规范配置语义为：

```yaml
cumulative: true
preliminary_box: false
distribution_feedback: false

fdr_loss:
  fgl_weight: 0.15
  supervise_pre_boxes: false
  supervise_dn_fdr: false
  edge_adaptive_fgl: false
  reliability_shrinkage_alpha: 0.0
```

NA-FDR 的创新主张限定为“原生 reference 与原生 assignment/有效查询监督的统一
对齐组织”。D-FINE 的离散四边表示、non-uniform Integral、累计细化和基础 FGL
必须明确归因，不得声称由本文首次提出。

## 4. LRS-FDR：最终完整模块

LRS-FDR 在 NA-FDR 内部加入一个参数为零、仅训练期生效的
**Layerwise Reliability Shrinkage for FGL（LRS-FGL）**。对同一图像、同一浅层
decoder 中目标完全可表示的 normal matches，将停止梯度的 IoU 权重向该组均值
收缩：

\[
\widetilde q_{b,l,k}=(1-\alpha_l)q_{b,l,k}+\alpha_l\bar q^R_{b,l},
\qquad
\alpha_l=0.25\left(1-\frac{l}{L-1}\right).
\]

六层固定日程为 `[0.25, 0.20, 0.15, 0.10, 0.05, 0.00]`。只有四条目标边均位于
FDR 支持内部的 normal matches 参与均值；边界饱和目标、DN queries、unmatched
queries 和最终 decoder 层保持原始 FGL 权重。每个图像、每个层的总 FGL 权重严格
守恒，因此该机制重新分配监督而不整体放大损失。

最终配置只在 NA-FDR 上把：

```yaml
reliability_shrinkage_alpha: 0.25
```

从 `0.0` 改为 `0.25`。模型参数、state dict、matcher、decoder boxes/scores、推理图、
GFLOPs 和推理延迟不因 LRS-FGL 改变。LRS-FDR 是一个统一 FDR 模块；NA-FDR 是其
基础结构和内部消融，不作为与 LRS-FDR 并列的第二个论文模块。

## 5. 固定证据统计

三组均使用各自训练日志选择的 best checkpoint，并通过同一个冻结评估器在
VisDrone val 上独立复评。数据为 548 张图、38,759 个目标，`imgsz=640`、
`batch=8`、`conf=0.001`、`max_det=300`、FP32。

| 方法 | P | R | F1 | AP50 | AP75 | mAP50-95 |
|---|---:|---:|---:|---:|---:|---:|
| Original FDR | 0.570249 | 0.491417 | 0.527907 | 0.484700 | 0.294070 | 0.290698 |
| NA-FDR | **0.587045** | 0.498339 | **0.539067** | **0.493119** | 0.301061 | 0.296855 |
| LRS-FDR | 0.579512 | **0.500606** | 0.537177 | 0.491805 | **0.305773** | **0.296968** |

### 5.1 NA-FDR 相对 Original FDR

- Precision `+1.680 pp`；
- Recall `+0.692 pp`；
- AP50 `+0.842 pp`；
- AP75 `+0.699 pp`；
- mAP50-95 `+0.616 pp`。

该结果支持 NA-FDR 作为基础设计，而不是把它描述成无贡献的“清理对照”。

### 5.2 LRS-FDR 相对 NA-FDR（内部消融）

- Recall `+0.227 pp`；
- AP75 `+0.471 pp`；
- mAP50-95 `+0.011 pp`；
- Precision `-0.753 pp`；
- AP50 `-0.131 pp`。

该结果只支持 LRS-FGL 带来严格 IoU/Recall 取向的监督重分配；不得写成全面、稳定
或显著提升。

### 5.3 LRS-FDR 相对 Original FDR（最终方法）

- Precision `+0.926 pp`；
- Recall `+0.919 pp`；
- AP50 `+0.711 pp`；
- AP75 `+1.170 pp`；
- mAP50-95 `+0.627 pp`。

这是正文中最终 FDR 模块相对原始实现的主要总体结果。

## 6. 尺度证据与边界

| 方法 | Tiny mAP | Small mAP | Medium mAP | Large mAP |
|---|---:|---:|---:|---:|
| Original FDR | 0.147025 | 0.291050 | 0.395473 | 0.380301 |
| NA-FDR | **0.157561** | **0.300759** | 0.400317 | **0.472407** |
| LRS-FDR | 0.149050 | 0.298944 | **0.400401** | 0.368274 |

LRS-FDR 相对 Original FDR 的 Tiny、Small、Medium mAP 为正；相对 NA-FDR 的
Tiny 与 Small mAP 分别下降 `0.851/0.181 pp`。Large 组只有 130 个 GT，波动性高，
不得作为机制主张。论文不得声称 LRS-FGL 全尺度提升或专门增强 Tiny 目标。

## 7. 主材料修改范围

实施阶段统一修改以下权威入口：

1. `paper_material/README_ZH.md`：撤销 D-FINE-S/EQuAL 当前路线口径，设置
   LRS-FDR/BPDD/FIA 为投稿链；
2. `paper_material/CURRENT_RERUN_STATUS_ZH.md`：记录路线切回、完成状态和剩余
   第二数据集工作；
3. `paper_material/methods/FDR_ZH.md`：改写为 NA-FDR → LRS-FDR 的规范方法页；
4. `paper_material/writing/ICASSP2027_OUTLINE_ZH.md`：更新第一创新点和消融表；
5. `paper_material/writing/NOVELTY_POSITIONING_AND_ADVERSARIAL_AUDIT_ZH.md`：
   更新原创边界、证据强度和审稿攻击；
6. `paper_material/figures/FIGURE_PLAN_ZH.md`：把 FDR 主图和内部消融改为规范名称；
7. 新增 `paper_material/evidence/lrs_fdr_formal100_20260828/`，保存统一评估 JSON、
   结果说明和 SHA-256 清单；
8. 更新所有上述文件直接引用的结果入口，但不改写旧实验目录中的原始名称。

EQuAL、DCF、D-FINE-S 和旧 AP-FDR 页面保留并明确标记为历史/放弃路线。旧 checkpoint、
CSV、authority JSON、Release 名称及 commit 不重命名。

## 8. 成功标准

- 主材料所有“当前/最终 FDR”表述均指向 LRS-FDR；
- `Clean FDR` 在论文口径中全部映射为 NA-FDR，仅在历史标识说明中保留；
- 方法页、结果表、提纲、创新审计和图规划使用相同定义与数值；
- NA-FDR 的基础创新与 LRS-FGL 的增量贡献分开归因，不把 `+0.627 pp` 全部归给
  LRS-FGL；
- Tiny/Small、late-training、单 seed 和第二数据集未完成等限制保持可见；
- 新证据文件能通过 JSON 解析和 SHA-256 复核；
- Git 差异无格式错误，提交推送后远端 OID 与本地 HEAD 一致。

# FDR + BPDD + FIA Formal100 详细结果

## 证据身份

本结果来自全量 VisDrone、seed 0、100 epoch 训练后的 epoch100 exact-final EMA，并在 548 张 VisDrone val 图像上完成一次独立评估。原始运行中的第三模块历史标识已按当前代码树规范化为 FIA；数值、checkpoint、数据集和协议哈希均保持不变。

- 数据集 SHA-256：`FD92E9FF4B3B58FCDD5A32F7E770FC3398E566B627DB0E188CB5FF9F3B7BBDAB`
- checkpoint SHA-256：`3EA6CD138C20AD38A35EF652407B6D77C423379A06E669028F771517843E069F`
- EMA state SHA-256：`CC45CDCD7F4B5788E2E713DF6B5FF3D3F16E34B7730BF59CC77FDABE9390876F`
- 训练：100/100 epoch，全部梯度有限
- 评估：`imgsz=640`、`batch=8`、`workers=8`、`conf=0.001`、`max_det=300`、`NMS=False`

机器可读来源为 [`../evidence/fdr_bpdd_fia_val_exact.json`](../evidence/fdr_bpdd_fia_val_exact.json)。

## 总体指标

| 方法 | Precision | Recall | F1 | AP50 | AP75 | mAP50–95 |
|---|---:|---:|---:|---:|---:|---:|
| RT-DETR-L+FDR+BPDD+FIA | 0.555762 | 0.498344 | 0.525489 | 0.481241 | 0.295104 | 0.289953 |

该行是精确单臂绝对结果。报告内的 FDR 和 FDR+BPDD 仅为历史参考，原始评估明确标记 `strict_paired=false`，因此下列差值只能称为跨运行算术差：

| 参考方法 | ΔPrecision | ΔRecall | ΔF1 | ΔAP50 | ΔAP75 | ΔmAP50–95 |
|---|---:|---:|---:|---:|---:|---:|
| 相对 FDR | −1.335 pp | +0.557 pp | +0.065 pp | −0.344 pp | +0.258 pp | +0.029 pp |
| 相对 FDR+BPDD | −1.487 pp | +0.388 pp | −0.434 pp | −0.517 pp | −0.299 pp | −0.231 pp |

因此该次 Formal100 证明三模块可以稳定完成训练和独立评估，但不支持“FIA 在 BPDD 上形成严格稳定正增益”的结论。

## 分尺度结果

尺度在网络输入像素空间定义：tiny `<16`、small `[16,32)`、medium `[32,96)`、large `>=96`，边长均使用 `sqrt(area)`。

| 尺度 | GT | AP50 | AP75 | mAP50–95 |
|---|---:|---:|---:|---:|
| Tiny | 20,860 | 0.304535 | 0.114305 | 0.146315 |
| Small | 12,420 | 0.465661 | 0.325173 | 0.293543 |
| Medium | 5,349 | 0.527770 | 0.432948 | 0.385438 |
| Large | 130 | 0.497520 | 0.440549 | 0.406022 |

CSV：[`fdr_bpdd_fia_val_scale_results.csv`](fdr_bpdd_fia_val_scale_results.csv)。Large 仅有 130 个 GT，不应据此做强机制归因。

## 逐类别结果

| 类别 | AP50 | AP75 | mAP50–95 |
|---|---:|---:|---:|
| pedestrian | 0.560844 | 0.226861 | 0.273099 |
| people | 0.494524 | 0.134114 | 0.209015 |
| bicycle | 0.235960 | 0.083191 | 0.109711 |
| car | 0.857594 | 0.688439 | 0.612552 |
| van | 0.532140 | 0.433556 | 0.382599 |
| truck | 0.377583 | 0.287637 | 0.255531 |
| tricycle | 0.357445 | 0.217063 | 0.206514 |
| awning-tricycle | 0.185264 | 0.126992 | 0.112734 |
| bus | 0.604031 | 0.509210 | 0.441885 |
| motor | 0.607025 | 0.243974 | 0.295889 |

CSV：[`fdr_bpdd_fia_val_class_results.csv`](fdr_bpdd_fia_val_class_results.csv)。

## 效率

| 参数量 | GFLOPs | FP16 中位延迟 | FP16 P95 | FPS | 峰值显存 |
|---:|---:|---:|---:|---:|---:|
| 33,458,090 | 111.648143 | 27.488 ms | 27.943 ms | 36.379 | 248.925 MiB |

效率协议为 RTX 4090、batch 1、FP16、warmup 50、测量 200 次。当前缺少 Control、FDR 和 FDR+BPDD 的同协议效率 JSON，不计算跨协议速度差。

## 与终端截图的关系

仓库仍保留终端截图作为历史观察，其中 val 显示约 `0.296` mAP50–95、test 显示约 `0.234`。截图缺少 checkpoint、命令和 exact run identity，不能覆盖本页的 Formal100 精确结果，也不能用于报告精确 FIA 增益。

## 论文表述边界

可以写：三模块完成 seed0 Formal100，exact val mAP50–95 为 `0.289953`，AP75 为 `0.295104`，并有完整尺度、类别和效率记录。

不能写：FIA 已被严格配对证明带来稳定提升；三模块的 `0.289953` 可以与不同 authority 行直接作因果差值；截图约 `0.296` 是可复现的精确正式结果。

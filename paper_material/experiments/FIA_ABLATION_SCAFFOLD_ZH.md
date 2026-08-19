# FIA-only 与 FDR+FIA 消融入口

## 当前执行决策

FIA-only 当前采用 fresh P3-only `best.pt`；FDR+FIA 继续采用 GitHub Release `DFR-BDPP-FIA` 中的既有 cascading `best.pt`。两份 checkpoint 均已在统一 VisDrone val/test evaluator 下完成独立精确复评。fresh FIA-only 本次登记 checkpoint/source SHA 和总体指标，不补造未提供的十类别结果。

## 文件矩阵

| 消融 | 配置 / 入口 | 当前 checkpoint | 对照 |
|---|---|---|---|
| FIA-only | `configs/rtdetr-l-fia.yaml` / `val_fia.py` | fresh P3-only `best.pt`，SHA-256 `c00cae89aaeb722854f8c845d14507c3598f75d509c2b12a3222b35a004157a6` | RT-DETR-L canonical val `0.21911` |
| FDR+FIA | `configs/rtdetr-l-fdr-fia.yaml` / `val_fdr_fia.py` | Release FDR+FIA `best.pt` | RT-DETR-L+FDR |
| FDR+BPDD+FIA | `configs/rtdetr-l-fdr-bpdd-fia.yaml` | `DFR-BDPP-FIA-best.pt` | RT-DETR-L+FDR+BPDD |

## 当前消融结果

| 实验臂 | val mAP50–95 | 相对参照 | 结论 |
|---|---:|---:|---|
| FIA-only | 0.22705639514425527 | +0.7946 pp | fresh P3-only exact val；相对 canonical baseline `0.21911` |
| FDR+FIA | 0.2949403207 | +0.5280 pp | 与 FDR 组合呈正向兼容 |
| FDR+BPDD+FIA | 0.2961 | +0.384 pp | P3-only 四位小数 val 文本；checkpoint 0.29618 互证 |

同一三模块的四位小数 test 文本为 P=`0.5189`、R=`0.4361`、F1=`0.4634`、AP50=`0.4081`、AP75=`0.2327`、mAP50–95=`0.2337`，相对 FDR+BPDD test mAP `0.231659` 为 `+0.204 pp`，同样是正增长。原始 val/test 文本和结构化十类结果均已归档。

FIA-only 为正确 P3-only：raw graph 中 FIA 层 22 的 `f=-1` 指向上一层 21，层 23 显式 `f=21`，decoder 输入 `[22,25,28]`；源码 SHA 为 `118ad631eff93ad806f85ea47819578e6e00bfc5`。FDR+FIA 是既有 cascading（层 23 `f=-1`），第三行三模块也是单独登记的 P3-only。所有差值均按各自指定的同 split 参照计算，除 FDR 核心严格实验外，不写成 strict paired 因果增益。

test 已用各自 checkpoint 完成独立精确复评：fresh FIA-only 为 P=`0.4482592209945812`、R=`0.377636033342981`、F1=`0.3954178960043504`、AP50=`0.33664177054432`、AP75=`0.18201140298044138`、mAP50–95=`0.18551746406283812`，相对 protocol-comparable canonical test baseline `0.1774164316787175` 为 `+0.8101 pp`；FDR+FIA 的 AP75 / mAP50–95 仍为 `0.2358787301` / `0.2346453866`。test 与 val 分开报告，不跨 split 推导差值。

旧 FIA-only cascading checkpoint 及其负向 val 记录已被 fresh P3-only 结果取代，只能在带有“历史/已 superseded”标记的材料中引用。

统一结果见 [FIA 发布版结果](../results/FIA_ABLATION_RELEASE_RESULTS_ZH.md)。

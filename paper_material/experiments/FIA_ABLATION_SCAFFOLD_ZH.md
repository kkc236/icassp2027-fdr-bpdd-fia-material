# FIA-only 与 FDR+FIA 消融实验脚手架

## 证据更正

旧 standalone FIA 和旧 FDR+FIA 训练包属于 FIA 修改前实验，全部作废，不得作为历史补充或趋势观察。单 FIA 与 FDR+FIA 的修改后资产在 GitHub 当前可见内容中尚未找到，因此这两条正式结果仍待导入。

另已确认同一发布位置中的 DFR-BDPP-FIA-best.pt 是修改后、正确 P3-only 拓扑的三模块 checkpoint。其 best-val 记录为 P=0.56996、R=0.49848、AP50=0.48982、mAP50–95=0.29618；相对当前 BPDD val 绝对值的算术观察为 +0.3922 pp。该 checkpoint 尚缺 AP75 和冻结 evaluator 的独立复评，因此只能登记为新版正向 checkpoint 观察，不能升级为正式主表精确行或严格配对因果增益。

## 文件矩阵

| 消融 | 模型配置 | 训练入口 | 评估入口 | 对照 |
|---|---|---|---|---|
| FIA-only | configs/rtdetr-l-fia.yaml | train_fia.py | val_fia.py | 同协议 RT-DETR-L |
| FDR+FIA | configs/rtdetr-l-fdr-fia.yaml | train_fdr_fia.py | val_fdr_fia.py | 同协议 FDR |
| FDR+BPDD+FIA | configs/rtdetr-l-fdr-bpdd-fia.yaml | scripts/train_rtdetr_bpdd_fia.py | scripts/evaluate_bpdd_fia_formal.py | 同协议 FDR+BPDD |

上述入口只用于定位实验臂。正式结果必须以修改后 FIA 源码和与之匹配的配置、checkpoint、评估输出为准，不能沿用修改前 standalone 运行的默认权重路径或证据身份。

## 冻结要求

正式补实验和复评必须：

1. 绑定修改后 FIA 的源码提交与配置 blob；
2. 对照臂与 FIA 臂使用同一 initial state、seed、数据顺序、增强随机序列和训练设备合同；
3. val 与 test 分开运行，并显式冻结 imgsz、batch、workers、conf、max_det、NMS、cache、half 与 rect；
4. 保存 checkpoint SHA-256、命令、数据集 SHA-256，以及精确总体、尺度和类别 JSON；
5. FIA-only 只与 baseline 配对，FDR+FIA 只与 FDR 配对，三模块只与 FDR+BPDD 配对。

## 当前状态

| 实验臂 | 当前状态 | 允许表述 |
|---|---|---|
| FIA-only | 修改前数据已撤销；新版资产未找到 | 待导入，不报告数值或涨点 |
| FDR+FIA | 修改前数据已撤销；新版资产未找到 | 待导入，不报告数值或涨点 |
| FDR+BPDD+FIA | 正确 P3-only 新 checkpoint 已定位 | 可报告 best-val 正向观察及其不完整性；AP75、test 和独立复评待补 |

统一状态见 [FIA 结果状态](../results/FIA_RESULTS_STATUS_ZH.md)。

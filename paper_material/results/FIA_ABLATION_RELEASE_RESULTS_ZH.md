# FIA 消融新版结果

## 覆盖声明

本页已用修改后 FIA 的当前有效证据完全覆盖。修改前拓扑产生的 FIA-only、FDR+FIA、FDR+BPDD+FIA 数值及其截图、训练包、哈希和派生结论均已撤销，不得继续引用。

## 当前结果状态

| 实验臂 | 修改后结果状态 | 当前可登记数值 |
|---|---|---:|
| FIA-only | 用户报告新版为正增益；可审计新版资产待导入 | 不填数 |
| FDR+FIA | 用户报告新版为正增益；可审计新版资产待导入 | 不填数 |
| FDR+BPDD+FIA | 正确 P3-only checkpoint 已核验 | best-val mAP50–95 = 0.29618 |

“新版为正增益”只登记实验方向，不替代数值证据。FIA-only 与 FDR+FIA 在 checkpoint、训练源码、配置哈希和评估输出完成绑定前，不进入数值表，也不据此计算涨点。

## 已核验的三模块新版观察

已定位的 `DFR-BDPP-FIA-best.pt` 具有正确 P3-only 计算图：FIA 层 22 读取原始 P3（层 21），层 23 同样读取原始 P3，decoder 输入为 `[22,25,28]`。checkpoint 内训练历史的 best-validation 记录位于 epoch 96：

| P | R | AP50 | AP75 | mAP50–95 | 证据等级 |
|---:|---:|---:|---:|---:|---|
| 0.56996 | 0.49848 | 0.48982 | 待补 | 0.29618 | `checkpoint_embedded_best_val` |

- checkpoint SHA-256：`fd972586e2833a28aa02d04ac9e460b0d7c8cfc4e6e8bcb48da273f0e905593c`
- 相对当前 FDR+BPDD val mAP50–95 `0.29225786956881444` 的算术观察：`+0.3922 pp`
- 严格配对状态：否
- 正式主表资格：否，需完成冻结 evaluator 的独立复评和运行身份绑定

该正向观察只能表述为“修改后三模块 checkpoint 的嵌入式 best-val mAP50–95 为 0.29618”。不得将 `+0.3922 pp` 写成 FIA 的严格配对因果增益。

## 尚待补齐

- 修改后 FIA-only 与 FDR+FIA 的 checkpoint、日志和精确 val/test 输出；
- 三个实验臂的训练源码 commit、配置 blob、seed 和数据集身份；
- 统一 evaluator 下的 P、R、AP50、AP75、mAP50–95；
- val/test 四尺度与十类别结构化结果；
- 与相应对照臂的严格配对判定。

机器可读状态见 [`../evidence/fia_results_status.json`](../evidence/fia_results_status.json)，完整证据边界与导入清单见 [`FIA_RESULTS_STATUS_ZH.md`](FIA_RESULTS_STATUS_ZH.md)。


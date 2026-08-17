# FIA 消融新版结果

## 覆盖声明

本页已用修改后 FIA 的当前有效证据完全覆盖。修改前拓扑产生的 FIA-only、FDR+FIA、FDR+BPDD+FIA 数值及其截图、训练包、哈希和派生结论均已撤销，不得继续引用。

## 当前结果状态

| 实验臂 | 修改后结果状态 | 当前可登记数值 |
|---|---|---:|
| FIA-only | 网页 ZIP、模型和 log 已找到，但 checkpoint 是修改前 cascading 拓扑；修改后 P3-only 资产仍待定位 | 不填数 |
| FDR+FIA | 网页 ZIP、模型和 log 已找到，但 checkpoint 是修改前 cascading 拓扑；修改后 P3-only 资产仍待定位 | 不填数 |
| FDR+BPDD+FIA | 正确 P3-only checkpoint 已核验 | best-val mAP50–95 = 0.29618 |

“新版为正增益”只登记实验方向，不替代数值证据。FIA-only 与 FDR+FIA 在 checkpoint、训练源码、配置哈希和评估输出完成绑定前，不进入数值表，也不据此计算涨点。

## 网页模型与日志审计

网页附件已找到并重新下载核验。[GitHub Release `DFR-BDPP-FIA`](https://github.com/kkc236/uav-detection-baselines/releases/tag/DFR-BDPP-FIA) 显示 `Assets 10`：其中 8 个是自定义附件，另外 2 个是 GitHub 自动生成的源码归档，并不存在被折叠隐藏的另一组 standalone 新模型。

| 网页附件组 | 计算图核验 | 裁定 |
|---|---|---|
| FIA-only ZIP、内部 best/last 模型、`log1.log` | `model[23].f = -1`，P4/P5 继续读取 FIA 输出 | 修改前 cascading，作废 |
| FDR+FIA ZIP、内部 best/last 模型、`log2.log` | `model[23].f = -1`，P4/P5 继续读取 FIA 输出 | 修改前 cascading，作废 |
| `DFR-BDPP-FIA-best.pt` / `last.pt` | `model[23].f = 21`，FIA 只增强 decoder P3 | 修改后 P3-only 三模块，有效 |

因此，“网页里有模型文件和 log”本身成立，但不能证明这些 standalone 文件来自修改后 FIA。旧 standalone ZIP/log 继续只作为撤销审计对象，不能恢复其指标；正确新版 standalone checkpoint 必须满足 `model[23].f = 21`。

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

- 修改后 P3-only FIA-only 与 FDR+FIA 的 checkpoint、日志和精确 val/test 输出；
- 三个实验臂的训练源码 commit、配置 blob、seed 和数据集身份；
- 统一 evaluator 下的 P、R、AP50、AP75、mAP50–95；
- val/test 四尺度与十类别结构化结果；
- 与相应对照臂的严格配对判定。

机器可读状态见 [`../evidence/fia_results_status.json`](../evidence/fia_results_status.json)，完整证据边界与导入清单见 [`FIA_RESULTS_STATUS_ZH.md`](FIA_RESULTS_STATUS_ZH.md)。

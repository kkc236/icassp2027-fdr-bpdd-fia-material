# FIA 结果状态

## 当前裁定

修改前 FIA 的全部实验数据已撤销。旧 standalone FIA、旧 FDR+FIA、旧截图、旧训练包及其派生表格和结论均不得作为历史补充、趋势观察或论文证据继续使用。

用户报告修改后的 FIA 相关实验均为正增益。当前证据状态需要分开处理：

| 实验臂 | 当前状态 | 正式数值状态 |
|---|---|---|
| FIA-only | 网页已有模型与 log，但内部图为修改前 cascading；修改后 P3-only 资产未找到 | 待导入，不填数 |
| FDR+FIA | 网页已有模型与 log，但内部图为修改前 cascading；修改后 P3-only 资产未找到 | 待导入，不填数 |
| FDR+BPDD+FIA | 正确 P3-only 新 checkpoint 已定位 | best-val 正向观察已登记；独立复评待补 |

## 网页附件为何不能直接使用

已展开并审计 GitHub Release `DFR-BDPP-FIA` 的全部附件。网页显示 10 项，其中 8 项为自定义附件，2 项为 GitHub 自动生成的源码归档，没有隐藏的另一组新版 standalone 文件。

- FIA-only ZIP 内 best checkpoint：`model[23].f = -1`；
- FDR+FIA ZIP 内 best checkpoint：`model[23].f = -1`；
- 修改后 P3-only standalone 的必要指纹：`model[23].f = 21`。

因此，网页上的 `log1.log`、`log2.log` 以及两个 standalone ZIP 均属于修改前实验，继续作废。网页上的 `DFR-BDPP-FIA-best.pt` 则满足 `model[23].f = 21`，属于正确三模块新图，两类附件不能混为一批。

## 已确认的新三模块 checkpoint

已确认 DFR-BDPP-FIA-best.pt 对应修改后 FIA 的正确 P3-only 三模块计算图。当前可登记的 best-validation 记录为：

| P | R | AP50 | AP75 | mAP50–95 |
|---:|---:|---:|---:|---:|
| 0.56996 | 0.49848 | 0.48982 | 待补 | 0.29618 |

相对当前 FDR+BPDD val 绝对值的 mAP50–95 算术观察为 +0.3922 pp。该差值尚未证明为严格配对因果增益，因为还需要确认完全一致的训练与评估 authority。

checkpoint SHA-256 已登记为 `fd972586e2833a28aa02d04ac9e460b0d7c8cfc4e6e8bcb48da273f0e905593c`；计算图核验结果为 FIA 层 22 读取原始 P3（层 21）、层 23 同样读取原始 P3，decoder 输入为 `[22,25,28]`。

当前缺失项：

- checkpoint 内缺少可验证的训练源码 commit；
- 训练时配置 blob 与当前修改后配置指纹的直接绑定；
- 冻结 evaluator 的独立 val 复评；
- AP75；
- test 总体结果；
- 四尺度和十类别结构化结果；
- 严格配对状态。

## 当前正式表格规则

- 正式主表暂时只保留 RT-DETR-L、RT-DETR-L+FDR 和 RT-DETR-L+FDR+BPDD 三条不含 FIA 的可审计行。
- 新三模块 checkpoint 的 best-val 记录只能放在“待独立复评”区，不与 formal exact 行混排。
- FIA-only 与 FDR+FIA 不得依据用户口述填入数值；待新版资产定位并审计后再导入。
- 任何修改前 FIA 数值、截图或 checkpoint 都不能恢复为补充材料。

## 新版结果导入清单

每个 FIA 实验臂至少需要：

1. 修改后源码 commit 与干净工作树身份；
2. 精确模型配置及其 blob/digest；
3. checkpoint 文件、SHA-256 和 epoch/EMA 身份；
4. 数据集 YAML、类别映射和数据集摘要；
5. 完整评估命令、环境版本和 evaluator 配置；
6. val/test 分开的精确 P、R、AP50、AP75、mAP50–95；
7. 四尺度与十类别结构化输出；
8. 对照臂以及 strict paired 判定。

满足清单后，才可更新主结果 JSON、CSV、Markdown 表和论文图。

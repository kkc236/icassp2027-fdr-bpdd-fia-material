# 外部完整模型八组合敏感性结果：独立核验与数据交付

日期：2026-09-17。

## 1. 结论与交付

**核验通过。** 两个完整检测器（scratch-adapted D-FINE-L reproduction 与 Full）的 checkpoint final/best × val/test × COCOeval maxDets100/300，共八组比较、16份原始指标JSON，均与归档manifest中的SHA-256及嵌入指标一致。没有新训练、模型推理或COCOeval重算。

文件已复制到：

`output/cvm_experiment_design_20260917/inputs/external_sensitivity/`

该目录包含：

- 16份原封不动的 `{dfine,joint}_{best,final}_{val,test}.cap{100,300}.json`；
- 原封不动的 `cross-protocol-manifest.json`；
- 新生成的 `EXTERNAL_SENSITIVITY.json`，用于附录表格自动装配和来源追溯。

新汇总JSON只整理已有结果。`main.tex`、`build.py`、`verify.py`均未修改。

## 2. 八组可直接使用的结果

AP是百分数；差值为Full减D-FINE，以百分点计。每一个差值均由未舍入原始AP计算后再保留三位，不通过显示AP相减生成。

| Checkpoint | Split | COCOeval maxDets | 图像数 | D-FINE-L AP | Full AP | ΔAP（pp） |
|---|---|---:|---:|---:|---:|---:|
| final | val | 100 | 548 | 28.477 | 30.501 | +2.024 |
| final | val | 300 | 548 | 28.501 | 30.528 | +2.027 |
| final | test | 100 | 1,610 | 22.511 | 24.097 | +1.586 |
| final | test | 300 | 1,610 | 22.554 | 24.133 | +1.579 |
| best | val | 100 | 548 | 28.773 | 30.703 | +1.929 |
| best | val | 300 | 548 | 28.796 | 30.727 | +1.931 |
| best | test | 100 | 1,610 | 22.637 | 24.190 | +1.553 |
| best | test | 300 | 1,610 | 22.679 | 24.229 | +1.550 |

八组差值均为正。最小差值为 **1.5499885429928584 pp**（best/test/300），最大为 **2.0272227900448136 pp**（final/val/300），显示为 **1.550–2.027 pp**。

例如final/val/100：

`(0.30501095688246216 - 0.2847661095608445) × 100 = 2.0244847321617634 pp`

因此三位显示为+2.024。best/val/100的显示AP相减30.703−28.773会得到1.930，但由原始值计算应显示+1.929；这正是必须保留原始浮点计算的原因。

## 3. 来源与哈希核验范围

归档源目录：

`tmp-work/icassp2027-fdr-bpdd-fia-material/paper_material/evidence/visdrone_dfine_l_external_20260913/common_evaluation_20260915/`

### 核验结果

| 检查 | 结果 |
|---|---|
| 16份cap指标JSON实际SHA与manifest `files`登记 | 16/16通过 |
| 16份复制后的JSON与对应源文件SHA | 16/16通过 |
| 16份JSON的AP/AP50/AP75/APs/APm/APl/AR与manifest嵌入报告 | 16/16通过 |
| 所有逐类AP及stats数组与manifest嵌入报告 | 全部一致 |
| 指标JSON中命名AP与stats[0] | 全部一致 |
| 图像数、max_det、evaluator和version | 全部正确：val548、test1610，pycocotools.COCOeval 2.0.11 |
| 八组差值与manifest记录 | 全部一致（容差1e−12） |
| 八组显示结果与原COMPARISON.md | 全部一致 |
| 源manifest与复制manifest | SHA完全一致 |
| 八份归档export report与manifest hash | 8/8通过，均为complete |
| 相同模型/endpoint用于val与test的checkpoint哈希 | 四对全部一致 |
| 旧权威与新稿inputs中已有两个final-test300指标JSON | 两个目录共四次字节哈希核对，全部一致 |

源manifest及其复制品SHA-256：

`3f953a8267105978a0038695a8a03aa3578b8cd3c59e88345e43322ad222fdf8`

当前已有final-test300两份文件的共同SHA：

- D-FINE：`f2056f7b8ff0d7e5574e105e9c0129c5c942382f064cb934e0686f12070d3cac`
- Full（文件前缀joint）：`bdbd7b8d8a8131706fb9997dd960685820c0a2d5763d2d84543e0ee31b704283`

每份cap JSON的源路径、复制路径、manifest登记SHA、实际源SHA和复制SHA均存入汇总JSON的 `files`。manifest自身只核验源/复制一致；没有将其说成经过外部签名认证。

本次确认的是归档结果的身份、一致性和整理算术。没有读取完整原始预测来重新计算AP，也没有把哈希检查表述成独立模型复现实验。

## 4. maxDets100与300的准确含义

归档 `cross_protocol_bs4_pipeline.sh` 对每个模型、checkpoint、split只导出一次预测JSONL，再用同一JSONL分别调用 `evaluate_common.py --max-det 100` 与 `--max-det 300`。

独立阅读 `evaluate_common.py` 确认：

1. 转换函数保留导出的全部detections，没有因cap100而另行筛选成每图100条输出；
2. 评估器设置 `evaluator.params.maxDets = [1, 10, max_det]`；
3. AP从请求cap对应的precision张量显式提取，避免默认summarize中固定100口径的影响；
4. evaluator源文件实际SHA与manifest登记一致。

评估器源码SHA-256：

`aadfe82f25a0a9ca2981e5de7b4d730b8548dd58de1509b74460530ac84e8d5f`

因此：

- 模型导出仍使用**每图至多300条原生候选输出**；
- `maxDets=100` 是COCOeval对这些已有预测施加的**每图、每类评估截断上限**；
- 这不是重新执行模型、将模型输出上限改成100的实验；
- 它支持“在这两个已记录评估截断值下差异仍为正”，不支持“模型在不同推理候选预算下都保持同样速度/准确率”。

推理共同协议保持640×640 PIL bilinear independent-axis stretch、RGB/255、FP32、batch1、confidence0.001、无TTA/额外NMS。上述协议不是native evaluator的别名，也不是训练配方对齐。

## 5. 汇总JSON接口

路径：

`inputs/external_sensitivity/EXTERNAL_SENSITIVITY.json`

表格装配可直接遍历 `comparisons`，共有8条，顺序与上表一致。每条提供：

```text
checkpoint             final / best
split                  val / test
max_det                100 / 300
display_dfine_ap        三位百分数AP字符串
display_full_ap         三位百分数AP字符串
display_delta_ap        带正号的三位百分点差值字符串
is_primary             仅final/test/300为true
image_count            548 / 1610
evaluator              pycocotools.COCOeval
evaluator_version      2.0.11
dfine.ap_raw           未舍入0–1 AP数值
dfine.ap_raw_source_token  源JSON中原始AP数值文字
full.ap_raw            未舍入0–1 AP数值
full.ap_raw_source_token   源JSON中原始AP数值文字
delta_ap_pp_unrounded   从未舍入AP直接计算的百分点差值
```

`dfine`和`full`对象另含未舍入百分数AP、三位字符串、image_count/evaluator、源文件名及source/copy SHA。顶层保留 `source_manifest`、`verification`、`protocol`、`rounding`、`limitations`、`range`、`files` 和原COMPARISON.md核对记录。

## 6. 论文可以如何使用

主文已固定的主要结果继续是 **final checkpoint、test split、maxDets300**；八行附录表用于完整披露checkpoint/split/评估截断的敏感性，不能看到更大的validation差值后重新指定主终点。

可以陈述：在这八种已记录外部完整模型比较设置中，Full相对本项目scratch-adapted D-FINE-L复现的AP差值均为正，范围1.550–2.027个百分点。

必须同时保留：

- 两个完整检测器训练配方和有效batch不同；
- 单seed，无统计显著性或训练随机性排除结论；
- YOLO-derived converted-label协议缺原始ignore-region信息；
- test此前在开发中可见；
- 这是完整系统外部比较，不能归因到LRS、几何、专家或F的独立作用；
- 内部模块比较继续val-only，本表不新增任何内部模块test消融。

八格完整性已由现有归档补齐，前述实验呈现审计中“外部敏感性披露范围待核查”的事项现在可以标为已完成，条件是论文附录/复现包实际引用本次交付内容。

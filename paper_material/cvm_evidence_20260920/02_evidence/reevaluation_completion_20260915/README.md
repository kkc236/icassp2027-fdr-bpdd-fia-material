# 2026-09-15：三项严谨性补强包

本包不重新训练任何模型。它只对已经完成训练的冻结 checkpoint 执行统一复评，
并把“能够证明的事实”和“尚缺的原始输入”分开记录。

| 项目 | 当前状态 | 产物 | 能否立即写入正文 |
|---|---|---|---|
| G 与 G+F 的共同 test | 已提供 fail-closed 复评入口；V06/V09 的 `best.pt` 未随材料归档 | `VISDRONE_G_GFIA_COMMON_EVAL_ZH.md` | 否，先跑复评 |
| V12/V13 源码路径审计 | 已完成，保留匹配与不匹配边界 | `SOURCE_AND_MECHANISM_AUDIT_ZH.md` | 仅可写 protocol-matched，不可写 byte-identical causal |
| UAVDT 统一复评与同机开销 | 已提供可执行入口；两个原 checkpoint、共同 data YAML 仍未归档 | `UAVDT_COMMON_EVALUATION_ZH.md` | 否，先跑复评 |

统一入口是仓库根目录的：

```text
scripts/run_common_checkpoint_eval.py
```

它在运行前对 data YAML 与每个 checkpoint 写入 SHA-256；两个以上模型必须使用同一
data YAML、同一 split、输入尺寸、batch、workers、阈值及 max_det。任何 checkpoint
不存在、路径是符号链接，或输出目录已有内容，都会直接失败，不会生成半真半假的表格。

复评输出中的 `common_evaluation.json` 是唯一可进入后续表格生成器的输入；不要从终端
截图手工抄数。

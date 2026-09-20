# 后续默认 Baseline 约定（2026-09-15）

用户确认：“以后 baseline 就用这个。”本约定指刚完成安装及回归的锚点宽高校准版，不指重新训练或替换权重。

## 默认对象与推理规则

- 对象：当前 VisDrone 10 类 stock RT-DETR-L strict-control baseline 的验证集 best-epoch EMA；继续使用原 checkpoint，不另选权重。
- 后续执行入口：`scripts/eval_baseline_anchor_scale.py`，固定携带 `--anchor-scale-reference 640`。
- 800 输入：参考锚点宽高乘以 640/800=0.8，标记为 **Baseline (anchor-calibrated inference)**。
- 640 输入：系数为 1，保留原生缓存与结果；主消融若仍按 640 展示，其 baseline 数值不因此改变。
- CLI 保留“省略校准参数即原生”的能力，专门用于原生复核/历史对照；这不改变本项目后续默认执行时携带校准参数的约定。
- 不把此修复自动套用到 UAVDT、D-FINE、FDR、LRS-GFDR 或 BPDD/FIA 联合头。那些对象不属于本次已验证的修复范围。

## 已验证结果

| 当前默认 baseline | split | mAP50-95 | 状态 |
|---|---|---:|---|
| 640，校准系数 1 | val | 21.9174% | 已复评，与原生完全一致 |
| 800，校准系数 0.8 | val | 19.1080% | 已复评；相对原生 800 的 15.5931% 恢复 3.5150 pp |
| 800，校准系数 0.8 | test | 15.4847% | 1610 张完整实测；相对原生 800 的 12.8241% 恢复 2.6607 pp |

本次 test 沿用 val 已固定的系数 0.8，同一验证集 best-epoch EMA，未重训、未按 test 改参数。校准 800 test 仍比同一 baseline 的原生 640 test（17.7426%）低 2.2578 pp；不能称为完全消除尺度退化。这里的 test 指项目转换的 VisDrone test-dev 标注与原生 RTDETRValidator，不是官方挑战完整评估器分数。

## 后续汇报与论文使用

后续提到“当前 baseline”时采用上述版本，同时写清 split、输入尺寸和校准状态。640 与 800 分开比较，不将 800 baseline 与其他臂的 640 数值算作同尺度增益。

原生 800 的旧结果保留为历史/尺度敏感性证据，不覆盖、不改名；锚点校准的恢复量不计作 FDR/BPDD/FIA 的训练模块增益。改用该 baseline 不自动消除训练或推理协议差异，也不自动形成新的严格消融结论。

**解释澄清（用户已确认）**：baseline 的尺度退化本身不否定消融。若除待研究模块外的条件受控，完整模块带来的抗退化能力可以包含在其总体收益中；几何/解码处理若属于模块定义，不机械地当成额外变量。这里需要区分的是“完整方案优势”“特定模块归因”和“同模型的尺寸变化”，而不是把所有退化相关增益都排除。采用 [消融与尺度分析设计](ABLATION_AND_SCALE_DESIGN_ZH.md)：640 主消融保留，800 尺度分析和 baseline 校准控制分表，披露本分析为已有 test 观察后的诊断扩展。

本约定本身仅更新后续默认选择；上述 test 已按后续“修复 test 测试”的指令完成。未修改已经发布的历史数值。

## 证据与入口

- [使用说明](../../docs/BASELINE_ANCHOR_SCALE_ZH.md)
- [安装与回归验收](../evidence/reevaluation_completion_20260915/baseline_anchor_scale_installed_20260915/INSTALLATION_VERIFIED_ZH.md)
- [机器可核验验收结果](../evidence/reevaluation_completion_20260915/baseline_anchor_scale_installed_20260915/VERIFIED.json)
- [固定校准版 test 实测及多臂对比](../evidence/reevaluation_completion_20260915/baseline_anchor_test800/BASELINE_TEST800_ZH.md)
- [test 精确指标与差值](../evidence/reevaluation_completion_20260915/baseline_anchor_test800/RESULTS.json)

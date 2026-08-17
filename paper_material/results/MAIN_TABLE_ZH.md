# VisDrone val 主结果表

下表统一展示当前可审计的 VisDrone val 绝对指标。`✓` 表示模型包含对应模块；`—` 表示不包含。完整模型已补入 epoch100 exact-final EMA 独立评估，因此不再用终端截图舍入值占据主表。

| 方法 | FDR | BPDD | FIA | Precision | Recall | AP50 | AP75 | mAP50–95 | 证据等级 | 可安全表述 |
|---|:---:|:---:|:---:|---:|---:|---:|---:|---:|---|---|
| RT-DETR-L | — | — | — | 0.46761 | 0.41731 | 0.38663 | 0.21302 | 0.21911 | `strict` | 严格基线绝对值 |
| RT-DETR-L+FDR | ✓ | — | — | 0.56911 | 0.49278 | 0.48468 | 0.29253 | 0.28966 | `strict` | 可与上一行作严格配对差值 |
| RT-DETR-L+FDR+BPDD | ✓ | ✓ | — | 0.5706336342 | 0.4944641371 | 0.4864074914 | 0.2980956482 | 0.2922578696 | `cross_authority_exact` | 精确绝对值；不得写成严格配对 BPDD 增益 |
| RT-DETR-L+FDR+BPDD+FIA | ✓ | ✓ | ✓ | 0.5557616181 | 0.4983437446 | 0.4812409327 | 0.2951036299 | 0.2899528643 | `exact_single_arm` | 精确单臂绝对值；历史参考差值不是严格 FIA 因果增益 |

## 差值边界

唯一可直接写为严格配对差值的是 `+FDR` 相对 RT-DETR-L：

| 指标 | 绝对差 | 百分点差 |
|---|---:|---:|
| Precision | +0.10150 | +10.150 pp |
| Recall | +0.07547 | +7.547 pp |
| AP50 | +0.09805 | +9.805 pp |
| AP75 | +0.07951 | +7.951 pp |
| mAP50–95 | +0.07055 | +7.055 pp |

`+FDR+BPDD` 与 `+FDR` 的已展示数值算术差依次为 Precision `+0.0015236342`、Recall `+0.0016841371`、AP50 `+0.0017274914`、AP75 `+0.0055656482`、mAP50–95 `+0.0025978696`。这些只可称“跨 authority 算术差”，不能归因为严格配对的 BPDD 收益。

完整模型与 `+FDR+BPDD` 的跨运行算术差依次为 Precision `−0.0148720161`、Recall `+0.0038796075`、AP50 `−0.0051665587`、AP75 `−0.0029920184`、mAP50–95 `−0.0023050052`。原始评估明确标记 `strict_paired=false`，只能据此说明该次三模块运行没有显示稳定叠加协同，不能归因为 FIA 的严格独立效应。

终端截图中的 val `≈0.296` 和 test `≈0.234` 继续作为补充观察保存，但其 checkpoint、命令和 exact run identity 不可用，不能覆盖 Formal100 精确行，也不能与主表计算精确差值。

完整尺度、类别、效率和 checkpoint 信息见 [FDR+BPDD+FIA Formal100 详细结果](FDR_BPDD_FIA_DETAILED_ZH.md)。

## 必补消融

- FIA 单独：Release 已登记 val 训练日志 exact 记录与 test 截图舍入结果，但该运行属于历史 topology，且 training source commit 未验证、AP75 缺失，不能写入正式主表。当前 P3-only 配置仍需按冻结协议重新训练和独立复评。
- FDR+FIA：Release 已登记 val 训练日志 exact 记录与 test 截图舍入结果，但同样不满足严格可比合同；只能作为 FIA 与 FDR 可能互补的阶段性观察，不能报告正式交互增益。
- BPDD 单独：不应设置，因为 BPDD 消费 FDR 的逐层四边分布，缺少 FDR 时方法定义不成立。

Release target commit `7b20c610` 早于配置提交 `1d083140`；Release graph 还让 FIA 输出参与 P4/P5 重建，而当前规范化配置为 P3-only。其 val 来自训练日志 best epoch，test 来自三位小数截图，AP75 未导出。以上未来正式行必须按同一冻结协议独立训练并由同一 evaluator 复评，不能用 Release 或现有组合行反推。完整边界见 [FIA-only 与 FDR+FIA Release 结果审计](FIA_ABLATION_RELEASE_RESULTS_ZH.md)。

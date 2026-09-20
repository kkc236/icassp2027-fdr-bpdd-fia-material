# 当前 Baseline：固定锚点校准版 800 test 实测

按用户确认的当前默认 baseline，使用已在 val 验证的固定系数 640/800=0.8 进行一次 test 评估。未训练、未改系数、未另选 checkpoint，原有结果不覆盖。

测试集：项目转换的 VisDrone test-dev 标注，1610 张、75102 个实例；原生 RTDETRValidator，batch=8、FP32、conf=0.001、max_det=300、nms=False、rect=False。不是 VisDrone 官方挑战完整评估器分数。

## 同为 800 的 test 对比

| 模型及推理方式 | mAP50-95 (%) | AP50 (%) | AP75 (%) | P (%) | R (%) |
|---|---:|---:|---:|---:|---:|
| Baseline anchor-calibrated | 15.4847 | 29.9670 | 14.4425 | 40.5059 | 35.2200 |
| Baseline native | 12.8241 | 27.8854 | 10.3708 | 37.8889 | 33.9059 |
| LRS-GFDR native | 24.0595 | 42.3871 | 24.1524 | 53.9144 | 44.7050 |
| LRS-GFDR + Capacity-BPDD + FIA native | 24.1598 | 42.4634 | 24.2186 | 54.5902 | 44.1799 |

当前校准 baseline 相对原生 800：mAP50-95 **+2.6607 pp**；AP50 **+2.0816 pp**；AP75 **+4.0717 pp**。

G/Full 同为 800 时分别高于当前校准 baseline 8.5748/8.6751 pp；这些是所列推理协议下的分数差，不把 baseline 校准或跨协议差异算作新训练模块因果贡献。

## 640 历史 test 参照（与上表分开）

| 模型 | mAP50-95 (%) | AP50 (%) | AP75 (%) | P (%) | R (%) |
|---|---:|---:|---:|---:|---:|
| Baseline native | 17.7426 | 32.2539 | 17.5650 | 41.9759 | 37.2449 |
| LRS-GFDR native | 23.6188 | 41.1008 | 23.6445 | 52.6088 | 43.7767 |
| LRS-GFDR + Capacity-BPDD + FIA native | 23.6040 | 41.2409 | 23.5464 | 53.8393 | 43.6336 |

同一 baseline 的校准 800 相对原生 640：mAP50-95 -2.2578 pp。这是尺寸/推理协议敏感性，不是同尺度模块增益。

## 记录与边界

- 默认 baseline 版本不因本次 test 结果而再次换参数；后续仍按用户已确认的协议使用。
- 640 的修复系数为 1，已在前次回归证实原生行为不变；此处复用已有 640 test，未重复训练或评估。
- 19.1080% 是此前 800 val 分数，不能填入 test。表中校准 test 来自本次完整实测。
- `files/test800/summary.json` 为本次原始指标，`files/evaluation.log` 为完整日志。
- `files/runner.py` 与 `files/code/` 记录实际命令、修复实现；前后 checkpoint/data 哈希及源码指纹已核验。
- `RESULTS.json` 含精确指标、差值和历史比较来源，`MANIFEST.json` 为传输校验。
- 更新本地材料目录；本轮未推送 GitHub。

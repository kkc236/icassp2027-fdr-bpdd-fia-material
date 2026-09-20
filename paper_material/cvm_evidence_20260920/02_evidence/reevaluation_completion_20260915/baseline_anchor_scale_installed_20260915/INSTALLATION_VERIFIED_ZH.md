# Baseline 锚点宽高校准：安装与回归验收

已将用户选定的参考框宽高校准安装到服务器 `/root/sj-tmp/lrs-v2/code`，并使用正式新增入口完成 640/800 验证集回归。不是只保留临时诊断脚本。

| 验证项 | 结果 |
|---|---|
| 本地测试 | 46 通过（新增/相关入口 28；既有评估 18） |
| 服务器测试 | 25 通过 |
| 640 val mAP50-95 | 21.9174%，与原生完全匹配 |
| 800 val mAP50-95 | 19.1080%，复现原诊断结果 |
| 相对原生 800 val | +3.5150 pp |
| checkpoint/data YAML | 前后哈希一致；使用原 best epoch EMA |

## 已安装入口

```bash
cd /root/sj-tmp/lrs-v2/code
/root/miniconda3/envs/lrs-v2/bin/python scripts/eval_baseline_anchor_scale.py \
  --checkpoint /root/sj-tmp/checkpoints/fdr-formal-d97e1eb7/fdr-formal-seed0-control-d97e1eb7-epoch-0100.pt \
  --data-yaml /root/sj-tmp/evidence/visdrone_test_authority_20260915.yaml \
  --split val --imgsz 800 --batch 8 --workers 8 --device 0 \
  --anchor-scale-reference 640 --expected-images 548 \
  --output-dir /root/sj-tmp/evidence/baseline800_anchor_calibrated_next
```

上述命令要求输出目录尚不存在。验收的已完成结果位于 `/root/sj-tmp/evidence/baseline_anchor_scale_installed_20260915_v3/val_calibrated_800`；无需为了确认安装重复执行。

## 保留边界

- 校准只在 `--anchor-scale-reference 640` 显式开启，原有评估入口不变。
- 640 系数为 1，保留原锚点缓存，避免细微精度漂移。
- 不修改训练/模型参数，不自动作用于自定义 FDR/联合头。
- 本次未复测 test，未覆盖旧结果，未推送 GitHub。不要把 val 的 19.1080% 写成 test。
- 第一次服务器入口尝试因 `select_device(batch=...)` 参数不兼容而在评估前失败。第二次提前将模型转到 GPU，使原生 CPU 卷积融合变为 GPU 融合，640 出现 -0.000908 pp 的微小差异，严格回归门槛未放行。最终使用原生 AutoBackend 的融合/设备迁移顺序并补真实运行时测试；未通过放宽容差掩盖差异。日志保存在 `files/previous_attempt_v1/`、`files/previous_attempt_v2/`，旧入口备份在 `files/previous_code/`。
- 按测试先行流程添加边界保护；按完成前验证流程逐一核验已安装源码与本地文件一致、46/25 项测试通过及两组完整 val 分数。

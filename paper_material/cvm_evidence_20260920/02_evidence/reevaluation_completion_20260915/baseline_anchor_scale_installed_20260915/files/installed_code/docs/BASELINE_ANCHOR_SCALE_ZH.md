# Baseline 高分辨率锚点宽高校准

这是已验证的 **baseline 推理协议修复**，不是 LRS-GFDR 内部的可行域几何校正，不改训练、不增参数、不写回 pt。

## 使用

在项目根目录执行（将权重和数据路径换成实际路径，输出目录必须尚不存在）：

```bash
python scripts/eval_baseline_anchor_scale.py \
  --checkpoint /path/to/baseline-best.pt \
  --data-yaml /path/to/data.yaml \
  --split val --imgsz 800 --batch 8 --workers 8 --device 0 \
  --anchor-scale-reference 640 \
  --output-dir /path/to/new-baseline800-anchor-calibrated
```

开启参数为 `--anchor-scale-reference 640`。省略它就是原生推理；设 `--imgsz 640` 时校准系数为 1，完全保留原有锚点缓存，不强制重建。

只支持当前已验证的 stock RT-DETR、10 类 VisDrone baseline；自定义 FDR、LRS-GFDR、BPDD/FIA 联合模型会被拒绝，不能悄悄套用尚未验证的修改。该参数还要求 checkpoint 记录的训练 imgsz 确为 640。

## 修复机制与边界

- 在原生 `_generate_anchors` 内将 `grid_size` 乘以 `reference_imgsz / inference_imgsz`；640→800 时为 0.8。
- 不缩放框中心，不改分类分数，不对最终输出框直接乘 0.8。
- 仅作用于本次加载的模型实例，评估结束（包括报错）恢复原方法和缓存；不改 Ultralytics 全局类或 site-packages。请勿并发共享同一模型实例，亦勿在校准上下文中改变设备或模型 dtype。
- 训练模式、输入实际尺寸不符、重复启用等情况直接报错。
- 原生 val 800 的 mAP50-95 为 15.5931%；诊断校准为 19.1080%，恢复 3.5150 pp。它仍低于原生 640 的 21.9174%，不是完整恢复。
- 正式结果必须标记 `anchor-calibrated inference`；不能把校准后的数值冒充原生 baseline，也不能归为你的训练模块增益。
- 不回填或覆盖旧实验报告。主论文协议如何选取仍需保持比较双方规则透明一致。

## 记录与验证

新输出目录包括 `protocol.json`、完成后原子落盘的 `summary.json`、原生 validator 产物；失败则写 `FAILED.json`。记录校准开关、系数、实际输入大小、图数、checkpoint/data YAML 的前后哈希和代码指纹。哈希用于确认本次未改文件，不要求不同训练机器的随机状态文件同哈希。

```bash
python -m pytest tests/test_inference_anchor_scale.py tests/test_baseline_anchor_scale_cli.py -q
```

本修复不改变历史 test 结果；新增回归优先在 val 验证既定系数，不在 test 上搜索系数。

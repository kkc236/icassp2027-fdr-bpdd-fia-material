# batch=4 部署与验证记录

- 部署日期：2026-09-14；服务器时区Asia/Shanghai。
- 主训练PID：425321；supervisor PID：425293。
- 新运行：`/root/sj-tmp/dfine-runs/dfine-l-visdrone-bs4-scratch-cross-20260914`。
- 配置SHA256：`50359501038ac1eebf86ef92bab235e7b1175d3a1a92337119a0b9617a037ac0`。
- 预检查：31,145,998参数；31,145,996可训练参数；骨干无冻结参数，80个BatchNorm层；所有AdamW组LR=0.00025。
- 第一轮已完成：607.10秒；原生验证AP50:95=0.01885302455310022。
  这是训练初期原生指标，不是最终统一评测结果。
- 第一轮最大PyTorch allocated：10,308,088,320 bytes（约9.60 GiB），最大reserved：10,865,344,512 bytes。
  累计峰值不能作为显存持续泄漏的证明，短期通过也不代表100轮必定稳定。
- 独立保存的global_best.pth及last_evaluated.pth已由真实第一轮验证触发。
- 本地针对性回归：17通过；覆盖完美框AP@300、空预测、缺失图像、尺寸、ID映射、非正方形预处理/坐标和分类平均。
- 服务器端两张真实val图片：两个模型均完成CPU加载、预测导出、COCO-ID转换和公共评测。
  `export-smoke-result.json`记录passed；联合模型results.csv确认100轮。该小样本仅检查连通性，不能用于报告模型优劣。
- 正常跑完100轮自动进入final/best × val/test × cap100/300的完整对比。评测完成前不填造最终成绩。
- 原batch8的OOM日志及checkpoint完整保留；没有重训/修改联合模型权重，没有删除数据。

详见[CROSS_PROTOCOL_BS4_ZH.md](CROSS_PROTOCOL_BS4_ZH.md)。本次为从头训练适配与跨协议比较，不能标为同协议消融或官方挑战赛成绩。

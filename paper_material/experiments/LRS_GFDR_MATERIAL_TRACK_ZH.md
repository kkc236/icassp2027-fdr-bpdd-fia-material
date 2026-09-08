# VisDrone LRS-GFDR 材料轨迹（2026-09-09）

## 冻结命名映射

| 材料名 | 旧运行名 | 几何校正 | BPDD | 证据状态 |
|---|---|---:|---:|---|
| FDR+geometry（控制项） | Clean-FDR + geometry | 是 | 否 | 已完成 |
| LRS-GFDR | LRS-FDR + feasible geometry | 是 | 否 | 已完成，等价封装 |
| LRS-GFDR+AC-BPDD | LRS-FDR + AC-BPDD | 是 | 是 | 已完成，显式配置封装 |

这里的 FDR 行是几何校正控制项，不改写仓库原有的纯 FDR 历史记录。LRS-GFDR 是本文对 LRS-FDR 几何校正版的正式方法名。

## 协议

- 数据集：VisDrone；输入尺寸、seed、private seed 和训练周期沿用各运行 authority。
- 比较指标：best epoch 的 val mAP50-95 为主，同时保留 final epoch 记录。
- 不上传 checkpoint、数据集或服务器密码；仅提交可复现配置、来源路径和数值证据。
- 2026-09-09 启动但随后停止的重复 GFDR 训练只作过程记录，不进入正式表。

## 论文使用边界

本页是 transfer-track（迁移封装轨迹），不替换 README 中已有的 EQuAL 主路线表。若写入主表，应保留“非 fresh-paired/等价封装”的证据等级标注。

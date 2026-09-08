# LRS-GFDR 结果汇总

这是与既有 EQuAL 主路线并行保存的 FDR/LRS 迁移材料轨迹，避免把不同代际结果混入同一主表。

| 方法 | best mAP50-95 | 相对上一项 | 说明 |
|---|---:|---:|---|
| FDR+geometry | 0.29361 | — | 几何校正控制项 |
| LRS-GFDR | 0.29620 | +0.259 pp | LRS-FDR 几何校正版的等价封装 |
| LRS-GFDR+BPDD | 0.29628 | +0.008 pp | 已完成 LRS-FDR+AC-BPDD 的显式命名封装 |

完整来源、epoch、运行目录和证据边界见 [`evidence/lrs_gfdr_track_20260909/RESULTS.md`](../evidence/lrs_gfdr_track_20260909/RESULTS.md)。


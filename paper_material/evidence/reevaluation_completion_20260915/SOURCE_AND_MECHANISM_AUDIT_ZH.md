# V12/V13 源码与机制审计（2026-09-15）

## 结论等级

V12（无 FIA）与 V13（当前 Full）具备**训练协议匹配**的证据：相同 VisDrone 数据摘要、
相同初始状态 SHA-256、seed=0、100 epochs、batch=8、640、MuSGD、AMP、增强与 BPDD
超参数。它们可以报告为 `protocol-matched FIA-off/on observation`。

它们目前**不具备 byte-level single-variable causal ablation**：V12 source commit
`5ef57473e89e3b91aa5236a18066aed99f5afc0f` 与 V13 source commit
`a43056af2a843ec9bae109d3420367c13f3bcef6` 不同；审计时 V12 commit 已不能由
`https://github.com/kkc236/uav-detection-baselines.git` 取回，因此无法逐文件证明两次
部署只改变 FIA。不得重写旧 commit、tree hash 或把它们伪造成同一源码。

## 已验证的配置层差异

归档的 V12/V13 YAML 做忽略注释的差异比对后，功能性差异是：

1. V13 在 P3 输出（图层 21）插入 `FIA[256]`；
2. P4 仍直接读取 21，不经过 FIA；
3. decoder 输入从 `[1,21,24,27]` 调整为 `[1,22,25,28]`，即只将 P3 换成 FIA-P3。

两份 YAML 中以下内容相同：`feasible_geometry=true`、`local_expert=true`、
`reliability_shrinkage_alpha=0.25`、`fgl_weight=0.15`，及 Capacity-BPDD 的
`loc_weight=0.15`、`cls_weight=0`、warmup 10–20、decay 80–100。

## V13 可回溯源码证据

V13 commit 可获取。关键 blob ID：

| 文件 | git blob |
|---|---|
| `configs/rtdetr-l-lrs-gfdr-capacity-v3-safe-bpdd-fia.yaml` | `ebe699238e16a97bc5d656290b1c2d7f2d75a828` |
| `src/rtdetr_bpdd_capacity_fia.py` | `f366361c40fa954885cfa91d7b1e6353ccb2c0a8` |
| `src/rtdetr_bpdd_capacity.py` | `ab2a821afab143b2c0623e77bc4ba031d4fddc20` |
| `src/rtdetr_fdr.py` | `6fbe56cf76a08025972335a94e8289acdbc10a6d` |
| `src/fdr_head.py` | `4f91d9590781fbb6cf3f1800d9cefddb180487f6` |
| `src/fdr_loss.py` | `1e594a8bda83c4a9bfefa73e2a4069271150dff7` |
| `src/fdr_math.py` | `396168af942eaf9143f9a520bbc37e05735234b4` |
| `src/fia.py` | `25a5b0097282a212de79332433026ac978c895ad` |

该源码中 `CapacityBPDDFIASafeDetectionModel` 强制冻结 v3-Safe 的 localization-only
BPDD 参数；`initialize_capacity_fia_graph` 验证 FIA 位于 P3，P4 bypass FIA，并将
`residual_scale` 初始化为 0。FDR decoder 的配置启用 feasible geometry，LRS 收缩由
`reliability_shrinkage_alpha=0.25` 注入损失。BPDD loss 仅在 `model.training` 为真时启用，
因此不增加测试期蒸馏损失。

## 可写与不可写

- 可写：Full 在 protocol-matched V12/V13 中 best-val AP 增加 0.832 pp，final-val 增加
  1.126 pp；这是受控观察。
- 可写：几何可行性修正、LRS 收缩、Capacity-BPDD 的定位蒸馏与 P3-only FIA 的结构职责。
- 不可写：仅 FIA 是两臂**唯一**源码差异；或由当前 CSV 推导任何未保存的机制统计量。

要提升到 byte-level 级别，唯一合法路径是恢复 V12 原 checkout（含 commit 对象或完整源码
压缩包）后，对 V12/V13 的 active-path 文件执行哈希和差异审计；不能事后修改历史 authority。

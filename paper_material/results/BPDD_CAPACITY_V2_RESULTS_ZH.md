# BPDD Capacity v2：VisDrone Formal100 结果

## Material Passport

- Experiment: `formal-seed0-lrs_gfdr_capacity_v2_bpdd`
- Status: `COMPLETED / VALIDATED-CSV`
- Primary split: `val`
- Selection rule: `results.csv` 中验证集 mAP50–95 最大行
- Raw evidence: [results.csv](../evidence/bpdd_capacity_v2_formal100_20260910/result/results.csv)
- Run record: [args.yaml](../evidence/bpdd_capacity_v2_formal100_20260910/result/args.yaml)

## 当前版本

100 轮已完成。best mAP50–95 出现在第 87 轮；best checkpoint 的独立验证四舍五入结果为 P=`0.609`、R=`0.487`、AP50=`0.496`、mAP50–95=`0.298`。

| 选择口径 | epoch | Precision | Recall | AP50 | mAP50–95 |
|---|---:|---:|---:|---:|---:|
| CSV best mAP 行 | 87 | 0.60448 | 0.49038 | 0.49620 | **0.29848** |
| CSV 最后一轮 | 100 | 0.60051 | 0.49153 | 0.49328 | 0.29511 |
| 后十轮均值 | 91–100 | — | — | — | 0.29562 |

best 与最后一轮相差 `0.337 pp`，因此论文和部署应绑定 `best.pt` 及其 epoch，而不能用 `last.pt` 代替最佳结果。

## 同服务器横向参考

| 实验 | best mAP50–95 | 与当前差值 |
|---|---:|---:|
| LRS-GFDR + capacity-v2 AC-BPDD（当前） | **0.29848** | — |
| LRS-GFDR + FIA | 0.29773 | +0.075 pp |
| LRS-GFDR（无 BPDD） | 0.29620 | +0.228 pp |
| LRS-FDR + AC-BPDD-v2 | 0.29628 | +0.220 pp |
| Clean-FDR + 几何校正 | 0.29361 | +0.487 pp |

这些是同服务器已登记结果的算术横向比较；源码、初始状态或 authority 不完全相同，不能升级为严格因果增益。要归因 BPDD，必须完成同一增容架构下的 expert-only 对照，并比较 `C-B`，而不是把当前完整系统的 `+0.228 pp` 全部写成 BPDD 独立收益。

## 有效结论与限制

- 有效：该版本确实完成了 100 轮，`results.csv` 有 100 个 epoch 行，best/last 权重均在远端保存；本包保存可复核的配置、逐轮 CSV 和运行证据。
- 有效：当前 best 峰值高于已登记的 LRS-GFDR 参考，但后期稳定性弱于 LRS-GFDR+FIA；这是候选结果，不是多 seed 结论。
- 不可宣称：尚未提供同增容 expert-only 的严格配对，因此不能量化 BPDD 的独立贡献；未上传 `.pt`，也未据此给出 test mAP。

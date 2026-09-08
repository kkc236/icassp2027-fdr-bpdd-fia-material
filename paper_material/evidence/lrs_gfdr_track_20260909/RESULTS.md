# LRS-GFDR transfer track results

来源：VisDrone、RTX 4090 服务器；以下均为 val 结果，mAP50-95 为主指标。

| 公开材料名 | 来源运行 | best epoch | P | R | mAP50 | mAP50-95 | final epoch mAP50-95 |
|---|---|---:|---:|---:|---:|---:|---:|
| FDR+geometry（控制项） | `/root/sj-tmp/runs/visdrone-v2-clean-fdr-geometry-20260908/formal-seed0-clean-fdr-geometry-v1` | 91 | — | — | 0.49130 | 0.29361 | 0.29193 |
| LRS-GFDR | `/root/sj-tmp/runs/visdrone-v2-existing-state-20260907/formal-seed0-lrs_fdr_feasible-v2` | 92 | — | — | 0.49382 | 0.29620 | 0.29371 |
| LRS-GFDR+AC-BPDD | `/root/sj-tmp/runs/visdrone-v2/formal-seed0-lrs_fdr_ac_bpdd-v2` | 92 | 0.58538 | 0.50029 | 0.49368 | 0.29628 | 0.29510 |

## 差值（best）

- LRS-GFDR 相对 FDR+geometry：`+0.00259`（+0.259 pp）。
- LRS-GFDR+AC-BPDD 相对 LRS-GFDR：`+0.00008`（+0.008 pp）。

LRS-GFDR 的初始状态 SHA-256：`935D68428BFC5848DE51F82844658ABBC7EC8C99CBBF6BBF823166D38CB65D5B`。本目录不包含 `.pt`、数据集和凭据；服务器路径用于审计追溯。BPDD 行的 P/R/mAP50/mAP50-95 来自运行 `results.csv` 第 92 行，final 来自第 100 行。

# FIA-only 与 FDR+FIA 消融入口

## 当前执行决策

standalone 消融不再从头训练，直接采用 GitHub Release `DFR-BDPP-FIA` 中 FIA-only 与 FDR+FIA 的 `best.pt`。两份 checkpoint 已在统一 VisDrone val evaluator 下复评，并登记 checkpoint SHA-256、总体指标和十类别指标。

## 文件矩阵

| 消融 | 配置 / 入口 | 当前 checkpoint | 对照 |
|---|---|---|---|
| FIA-only | `configs/rtdetr-l-fia.yaml` / `val_fia.py` | Release FIA-only `best.pt` | RT-DETR-L |
| FDR+FIA | `configs/rtdetr-l-fdr-fia.yaml` / `val_fdr_fia.py` | Release FDR+FIA `best.pt` | RT-DETR-L+FDR |
| FDR+BPDD+FIA | `configs/rtdetr-l-fdr-bpdd-fia.yaml` | `DFR-BDPP-FIA-best.pt` | RT-DETR-L+FDR+BPDD |

## 当前消融结果

| 实验臂 | val mAP50–95 | 相对参照 | 结论 |
|---|---:|---:|---|
| FIA-only | 0.2167954534 | −0.2315 pp | 略有负增益，不作为独立性能主张 |
| FDR+FIA | 0.2949403207 | +0.5280 pp | 与 FDR 组合呈正向兼容 |
| FDR+BPDD+FIA | 0.29618 | +0.3922 pp | P3-only checkpoint best-val 正向观察 |

前两行是 published cascading standalone（`model[23].f=-1`）的独立 exact val，不是 P3-only。第三行是 P3-only（`model[23].f=21`）的 checkpoint 内嵌观察。所有差值均按各自指定参照计算，除 FDR 核心严格实验外，不写成 strict paired 因果增益。

test 只使用 Release 截图舍入值：FIA-only mAP50–95=`0.177`，FDR+FIA=`0.235`；AP75 缺失。

统一结果见 [FIA 发布版结果](../results/FIA_ABLATION_RELEASE_RESULTS_ZH.md)。

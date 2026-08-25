# Clean FDR vs DCF-FDR Formal100

- Decision: `failed_negative`
- Primary metric: `metrics/mAP50-95(B)`

| Arm | Epoch | Precision | Recall | AP50 | mAP50-95 |
|---|---:|---:|---:|---:|---:|
| Clean FDR | 88 | 0.58777 | 0.49849 | 0.49320 | 0.29696 |
| DCF-FDR | 89 | 0.58646 | 0.49590 | 0.49258 | 0.29661 |

All values are read from the untouched Formal100 CSV files. The decision
uses unrounded best mAP50-95 values; unfavorable results remain published.

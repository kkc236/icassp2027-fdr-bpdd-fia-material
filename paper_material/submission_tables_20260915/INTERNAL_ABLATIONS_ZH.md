# 内部设计消融

全部 AP、P、R 按百分数显示；差值单位为 pp。数值由证据文件生成，保留三位小数。

## T3 G 内部设计：迁移、Clean、几何修正与 LRS

| Variant | Geometry | LRS | AP50 | AP | Best epoch |
| --- | --- | --- | --- | --- | --- |
| Original FDR | reference | reference | 48.473 | 29.078 | 92 |
| Clean-FDR | off | off | 49.320 | 29.696 | 88 |
| Clean-FDR + geometry | on | off | 49.130 | 29.361 | 91 |
| LRS-GFDR | on | on | 49.382 | 29.620 | 92 |

此表是已登记内部设计版本对照，源码、初始化完整配对情况仍待逐项回溯。Clean→几何修正的 AP 为 -0.335 pp；几何修正→加 LRS 为 +0.259 pp。几何修正应解释为可行域约束；现有 VisDrone 精度不支持“几何修正单独涨点”。第二数据集崩溃原因及修复效果需对应日志，不能由本表推断。Original FDR 的开关未按当前实现映射，使用 reference。

证据：[all_experiments_summary.json · V02](../results/all_experiments_summary.json)；[all_experiments_summary.json · V03](../results/all_experiments_summary.json)；[all_experiments_summary.json · V04](../results/all_experiments_summary.json)；[all_experiments_summary.json · V06](../results/all_experiments_summary.json)

## T4 B 内部设计：蒸馏方案与 FIA 联合兼容性

| BPDD recipe | FIA | AP50 | Best AP | Final AP | Best epoch |
| --- | --- | --- | --- | --- | --- |
| Capacity v2 | off | 49.620 | 29.848 | 29.511 | 87 |
| Capacity v2 | on | 49.585 | 29.736 | 29.198 | 83 |
| Capacity v3-Safe | off | 48.783 | 29.277 | 28.939 | 80 |
| Capacity v3-Safe | on | 49.890 | 30.109 | 30.065 | 97 |

v2→v3-Safe 是一组兼容性修改；目前不足以把定位蒸馏、分类蒸馏关闭、调度等因素逐个归因。保留同一路线联合退化行以说明设计选择。v3-Safe 的 BPDD-only 低于 v2；Full 优于 v2 联合。它支持“改善联合配置的表现”，不支持“新版 BPDD 在任何组合都更强”。

证据：[all_experiments_summary.json · V10](../results/all_experiments_summary.json)；[all_experiments_summary.json · V11](../results/all_experiments_summary.json)；[all_experiments_summary.json · V12](../results/all_experiments_summary.json)；[all_experiments_summary.json · V13](../results/all_experiments_summary.json)

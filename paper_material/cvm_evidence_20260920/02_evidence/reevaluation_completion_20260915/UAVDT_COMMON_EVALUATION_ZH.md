# UAVDT：baseline 与当前联合模型的统一复评

## 目标

H11 baseline 报告为 17,165 图 / 342,686 实例，而 H12 当前联合模型导出为 16,592 图 /
375,883 实例。两者不能直接相减。下列复评要求同一份冻结 `uavdt.yaml` 同时评估两份现有
`best.pt`，不重训。

## 所需最小输入

1. H11 baseline `weights/best.pt`；
2. H12 当前 `LRS-GFDR + Capacity-BPDD-v3-Safe + FIA` 的 `weights/best.pt`；
3. 一份冻结 UAVDT `uavdt.yaml`，类别顺序必须是 `car, truck, bus`；
4. 当前联合源码 checkout（训练证据指定 commit
   `b9f492320d7be35b846c504de84ea3a85077df76`，配置
   `configs/rtdetr-l-lrs-gfdr-capacity-v3-safe-bpdd-fia-uavdt.yaml`）。

不要用 VisDrone 十类权重或初始状态；本操作只读加载两份 UAVDT 三类 checkpoint。

## 运行

```bash
cd /data/icassp2027-fdr-bpdd-fia-material
python scripts/run_common_checkpoint_eval.py \
  --dataset UAVDT \
  --code-root /data/uav-detection-baselines \
  --data-yaml /data/UAVDT/uavdt_frozen.yaml \
  --split val --imgsz 640 --batch 8 --workers 8 --device 0 \
  --conf 0.001 --max-det 300 \
  --checkpoint baseline=/data/uavdt/runs/baseline/weights/best.pt \
  --checkpoint joint=/data/uavdt/runs/current_joint/weights/best.pt \
  --output-dir /data/evidence/uavdt_common_val_20260915
```

若联合臂在 `batch=8` 显存不足，则两臂一起使用 `batch=4` 重新执行该命令。评估 batch 不改变
checkpoint，不会改变模型参数量；它只是同一评估的吞吐设置。

## 产出与验收

`common_evaluation.json` 同时记录：两份 checkpoint 的 SHA-256、数据 YAML 的 SHA-256、
参数量、每张图预处理/推理/后处理耗时，以及 P/R/AP50/AP50-95 的原始 evaluator 输出。
只有该 JSON 与两臂对应 `results.csv` 归档后，才将 UAVDT 总体 AP 填入论文表 4；truck 逐类
结果放补充材料，并保留其困难类别结论而不回避。

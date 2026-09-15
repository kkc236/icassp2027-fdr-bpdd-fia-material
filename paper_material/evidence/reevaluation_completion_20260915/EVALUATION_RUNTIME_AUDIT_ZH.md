# 评估口径与几何开关复核

本报告纠正 414a1fd 中仅凭 YAML 缺项判定无几何校正的错误；保留全部实测指标。

## 运行时证据

在服务器 `/root/sj-tmp/lrs-v2/code` 下加载原 checkpoint 后直接检查解码器属性：

- G：`visdrone-v2-existing-state-20260907/formal-seed0-lrs_fdr_feasible-v2/weights/best.pt`，`model.28.decoder.feasible_geometry=True`。
- G+F：`visdrone-v2-lrs-gfdr-fia-20260909/formal-seed0-lrs_gfdr_fia-v1/weights/best.pt`，`model.29.decoder.feasible_geometry=True`。
- `src/fdr_head.py` 中默认开关为 True，旧对象缺少属性时恢复为 True，forward 根据此属性调用 `decode_feasible_fdr_boxes`。
- 这证明本次推理启用几何校正。它不单独证明历史训练期源码；历史配置缺项不能作为关闭开关的证据。

## Full 的两个 test 数值来自不同流程

本次服务器 Full JSON 与历史 `joint_best_test.report.json` 记录的权重 SHA256 均为：
`39F006DF9548B4D5DA968B9302FC14678FABAF2009802BC09A68FB23DD146BC6`。

| 流程 | test AP50-95 | test AP50 |
|---|---:|---:|
| 既有 PIL 640 + COCOeval 2.0.11，maxDet=300 | 24.229% | 42.009% |
| 本次 RTDETR.val 原生评估，batch=8，FP32 | 23.602% | 41.242% |

同一权重下差异为 −0.6265 pp AP，不能解释成训练退化。已确认两条流程使用不同的
预处理入口、模型加载入口、源码 checkout 和 AP 计算器；尚未通过逐项控制实验分摊
每项差异的贡献。原生参数计数34.42M与既有导出35.24M也须区分模型融合/计数时点，
不能未经核对就宣布架构变化。

既有统一评估报告路径：
`../visdrone_dfine_l_external_20260913/common_evaluation_20260915/`。

## 同一 COCO 流程的 val/test 参照

| 模型（native best） | val AP | test AP | val减test |
|---|---:|---:|---:|
| D-FINE-L | 28.796% | 22.679% | 6.117 pp |
| Full | 30.727% | 24.229% | 6.499 pp |

Full 相对 D-FINE-L 的增益从 val +1.931 pp 到 test +1.550 pp，缩小约0.381 pp。
因此两组 split 的绝对分差不足以单独认定 Full 异常泛化失败。也不能据此保证内部
FIA/BPDD 增益；原生 test 中 Full 与 G 的AP接近仍是需要解释的观测。

## 已完成的原生 test 复跑（2026-09-15）

为排除评估器混用，已按最早约定的原生 `CachedScaleRTDETRValidator` 流程重新评估
G、G+F、G+B 和 Full 四个冻结 checkpoint；结果与 `NATIVE_TEST_RERUN_20260915_ZH.md`
及 `output/native_test_rerun_20260915.json` 一致。四臂均处理 1610 张 test 图，固定
`imgsz=640/batch=8/conf=0.001/max_det=300/FP32`。原生复跑后 G=23.622%、G+F=23.219%、
G+B=23.621%、Full=23.602%（mAP50-95），因此先前低 test 结果不是跨协议评估器误差。

## 尚需核对

1. 将 G/G+F 纳入既有冻结 COCO 导出/评估流程，和 G+B/Full 同口径比较（仅用于跨协议参照）。
2. 对历史训练几何路径、数据及初始化来源做源码证据核验。
3. 原生与COCO结果分别标注，不能选择其中较高值拼表。
4. test 为项目1610张 test-dev 转换标注，未执行官方完整 ignore 规则；不能标为官方挑战赛成绩。

本次只核查和修订证据，没有修改模型或重训，也未根据 test 调参。

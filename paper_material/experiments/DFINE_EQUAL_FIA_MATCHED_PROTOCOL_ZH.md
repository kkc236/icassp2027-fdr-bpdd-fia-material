# D-FINE-S official 与 D-FINE-S + EQuAL + FIA 对照协议

## 1. 对照目标

本实验比较两个训练臂：control 为官方 `D-FINE-S`，treatment 为 `D-FINE-S + EQuAL + FIA`。两臂固定 VisDrone2019-DET、HGNetv2-B0 同一预训练权重、seed 0、132 epochs、640 输入、总 batch 8、有效 workers 4、AMP、EMA 和同一 COCO 评测器。

本文件只冻结静态协议和归因边界，不登记处理臂精度结论。机器可读合同位于 `evidence/dfine_s_equal_fia_matched_20260823/protocol.json`。

## 2. 数据与选模规则

- train：6,471 张、343,204 个实例。
- val：548 张、38,759 个实例；标注 SHA-256 为 `200d58ff...cca477`。
- test：1,610 张、75,102 个实例；标注 SHA-256 为 `b699bf1b...0fa3fd7`。
- 只用 val 选择 best，依据为 132 轮中最高的 COCO AP50–95。
- test 不参与选模；best 一经 val 冻结，才分别执行 val/test 独立评测。
- 这里的 test 是项目本地 `local held-out` split，不是 VisDrone challenge server 提交结果，论文不得把它描述成官方测试服务器成绩。

## 3. 统一评测口径

两臂使用统一 COCO evaluator，即 `pycocotools.COCOeval` 的 bbox 评测，`maxDets=[1,10,100]`，论文 AP 指标采用 `maxDets=100`。主要报告 COCO AP50–95、AP50 与 AP75。

本协议不会从 COCO evaluator 反推 P/R/F1。历史 Ultralytics 表中的 P/R/F1 定义和聚合方式不同，因此 P/R/F1 不与 COCO AP 混用，也不横向拼接为同口径表格。若未来确需报告 P/R/F1，必须为两臂新增同一实现、同一阈值和同一聚合定义的独立评测。

## 4. 为什么不是源码严格配对

control 的 source commit 为 `7fe2f8889f0b7b817f20c315b40fc15a4fb64ae6`；treatment 的 source commit 为 `24c9cb1fba1357b5930f483a26f9e2d787a4e7ef`。虽然新开关关闭时已经做过 default-off 回归，证明新增实现不会在默认关闭状态下改变上游路径，但两臂仍来自不同 source commit。因此机器合同明确记录 `strict_paired=false`。

这不妨碍将其称为“协议匹配的受控比较”：数据、初始化权重、seed、轮数、尺寸、batch、有效 workers、AMP/EMA 与 evaluator 均被冻结一致；但不能把它写成“同一源码提交下只切一个开关”的 source-identical strict pair。

## 5. Bundle 归因边界

treatment 同时启用 EQuAL 与 FIA，所以当前可检验单位是 `EQuAL+FIA bundle`。与 control 的差值只能归因到整个 bundle，不能拆分归因到 EQuAL 或 FIA 单项，也不能据此声称某个子组件贡献了特定 pp。只有加入专门的组件消融后，才允许进行单项贡献归因。

## 6. 后续证据写入规则

训练完成后另行保存 treatment 的完成清单、val 选择的 best checkpoint SHA-256，以及同一 best 在 val/test 上的原始 COCO 输出与机器可读摘要。test 只能用于冻结后的泛化评估。新增结果证据不得回写或覆盖本静态协议，也不得改写旧 RT-DETR-L A–E 表。

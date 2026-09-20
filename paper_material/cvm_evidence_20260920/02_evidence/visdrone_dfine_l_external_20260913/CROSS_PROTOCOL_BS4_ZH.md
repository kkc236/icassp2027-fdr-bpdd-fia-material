# VisDrone 跨训练协议、统一评测方案（batch=4）

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: plan + implementation
- Origin Date: 2026-09-14
- Version Label: dfine_bs4_scratch_cross_v1
- Verification Status: 部署与测试单独记录；完整训练及最终精度待完成。

## 目的和工作量

比较现有 LRS-GFDR + Capacity-BPDD-v3-Safe + FIA 联合模型与本项目从头复现的 D-FINE-L。
只新增一次 D-FINE-L 的100轮训练，不重训联合模型，不引入梯度累积实现或新一轮超参数搜索。
这是不同训练配方下的外部性能对比，不能用于隔离 FDR/BPDD/FIA 的因果增益；内部同协议消融承担后者。

## 固定训练配方与差异

| 项目 | 现有联合模型 | 本次 D-FINE-L |
|---|---|---|
| 框架 | 现有固定 Ultralytics / 自定义联合模型 | 官方源码267a6da，独立目录 |
| 初始化 | 原统一随机初始状态，无预训练 | seed=0随机初始化，无预训练 |
| 实际 batch | 8 | 4 |
| 梯度累积 | 配置nbs=64；服务器基础Trainer在预热后累积8批，约64张/更新 | 不累积，4张/更新 |
| 轮数 | 已完成100 | 从头100；不续接此前batch=8失败运行 |
| 优化器 | MuSGD，lr0=0.01 | AdamW，lr=0.00025，betas=(0.9,0.999) |
| 精度 | AMP | FP32（此前FP16发生DN溢出） |
| 骨干/BN | 沿用已训练模型 | 全部骨干可训练；BN正常更新 |
| 图像增强 | 沿用历史权威配置 | 官方光度/扩图/裁剪/翻转与480–800多尺度；72轮阶段切换 |
| 调度 | 原配置warmup3轮、lrf=.01 | 官方500步预热、MultiStepLR里程碑500（100轮内无该衰减） |
| 阶段行为 | 历史训练实现 | 保留官方72轮后best_stg1恢复及EMA调整；记录真实循环轮次 |

将随机初始化骨干冻结、并给它预训练微调时0.05倍学习率是不合理的起点。本次显式使用
`freeze_at=-1`、`freeze_norm=False`，骨干和头均用0.00025；norm/bn参数不施加权重衰减。
这属于本项目的从头训练适配，应标为“D-FINE-L（本项目复现，scratch-adapted）”，不能标为完整官方训练配方。
这些修改在本次正式启动前固定，不根据最终对比结果选择。
预热后联合模型的基础累积规则已核对服务器代码；它与D-FINE的有效batch及更新次数不匹配，不能称为等训练预算。

## 数据与评测规则

使用现有同一份VisDrone项目划分：train6471张、val548张、test1610张；类别10类。
COCO标注从现有YOLO标签转换，保存各划分JSON哈希和样本数量。预测文件名通过
COCO `file_name` 映射到数值 `image_id`，逐图检查覆盖率和原图尺寸，禁止漏图后仍输出成绩。

双方共同采用PIL双线性直接拉伸到640×640、RGB/255、FP32推理、batch=1、无TTA、无额外NMS、
score>0.001、最多300条原生检测输出。输出坐标分别按x/y缩放回原图；不采用letterbox逆变换。
保留模型各自原生的类别/候选解码，这是被比较系统的一部分。双方共同预处理的
PIL插值可能与历史Ultralytics原生OpenCV评测产生差异，因此统一评测结果单独成表，不能混用旧CSV数值。

统一运行同版本pycocotools.COCOeval；保存完整预测、AP50:95、AP50、AP75、APs/APm/APl、AR、逐类AP。
主口径maxDets=300；附加maxDets=100复用预测，无需再次训练或推理。注明COCO的maxDets是
类别内评测截断，同时模型输出总上限仍是300。指标从precision/recall张量显式提取，避免COCO
默认summarize的AP[0]固定取100导致maxDets=300时错报-1。缺少有效GT的分项保留NA，不作负增益计算。

项目YOLO标注没有保留完整原始ignore区域，因此这些结果不等于官方VisDrone挑战赛协议；
不能和采用不同忽略规则、切图、预训练或测试划分的论文数值直接严格排位。
历史test划分是否已参与开发无法认证，因此两个划分均完整报告，不称该test为首次使用的盲测集。

## 预先固定的两组比较

1. 主终点：第100轮末次已评测EMA快照 vs 联合模型现有第100轮last.pt，AP50:95@300。
   该比较规避跨框架不同best选择公式，但D-FINE仍保留官方阶段恢复行为，不代表100轮连续同一优化轨迹。
2. 次终点：D-FINE在100轮内按原生验证AP取得的global_best.pth vs 已存在的联合best.pt。
   两者都只按验证数据选择，框架的原生指标实现不同，明确披露。禁止在看到test后改选权重。
3. 同时公布val/test、cap100/300、best/final的全部8组差值，统一用百分点pp；不得只挑有利单元格。
4. 若只在best或某个上限领先，结论表述为对选择/评测口径敏感。单seed不声称统计显著或排除训练随机性。

不额外训练3个seed或跑庞大网格。若未来需要显著性，另行做独立训练重复；
对图片bootstrap也不能替代训练seed重复。

## 运行和自动交付

入口：`bash /root/sj-tmp/eval/visdrone_dfine_bs4_cross_20260914/run_bs4_cross.sh`。
已运行时不要重复启动，supervisor具有互斥锁和非空输出保护。

- 正式输出：`/root/sj-tmp/dfine-runs/dfine-l-visdrone-bs4-scratch-cross-20260914`
- 实时日志：`/root/sj-tmp/eval/visdrone_dfine_bs4_cross_20260914/training.log`
- 权威配置、源码哈希、环境和优化器组：`run-authority.json`
- 每轮真实循环轮次/原生AP/显存峰值：`chronological-validation.jsonl`及`progress.json`
- 自动原子保存：`global_best.pth`、`last_evaluated.pth`（推理快照；续训应使用官方全状态checkpoint）
- 正常100轮退出后：自动执行`cross_protocol_bs4_pipeline.sh`，部署兼容入口名为`cross_protocol_pipeline.sh`
- 交付：`/root/sj-tmp/eval/visdrone_dfine_bs4_results_20260914/COMPARISON.md`及`cross-protocol-manifest.json`

训练中断写failure.json并结束，不自动降低batch或跳过异常批次。单次训练超时上限72小时。
实时状态由训练日志和progress记录；部署完成不等于100轮训练已经完成。
保留此前batch8失败checkpoint与日志；不删除数据、不向GitHub上传原始图片/权重/凭据。

## 已发现并处理的问题

1. Scratch骨干冻结和预训练低学习率：改为可训练骨干/BN与统一基础学习率，另起配置。
2. D-FINE旧导出在padding后按原尺寸直接缩放：改为与训练一致的640直接拉伸。
3. 联合旧导出使用letterbox的scale_boxes：独立x/y逆变换，加入非正方形图测试。
4. 预测stem与COCO从1编号ID不一致：按file_name映射，并要求逐图覆盖完整。
5. COCO AP@300返回-1及空预测崩溃：直接读取正确维度的AP、支持零检测。
6. 仅依赖best_stg2可能漏全局best或无法准确表示末轮：只读包装原生evaluate，按循环轮次另存快照。

这些修复不证明任何方法精度领先。结果出来后按已固定的规则解释。

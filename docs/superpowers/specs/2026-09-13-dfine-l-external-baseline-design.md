# D-FINE-L VisDrone 外部基线准备包设计

## 目标

在不重新训练、不修改现有 Ultralytics 联合版的前提下，准备一个可在服务器上独立执行的 D-FINE-L VisDrone 基线包。该基线用于与当前 `LRS-GFDR + Capacity-BPDD-v3-Safe + FIA` checkpoint 做同数据、同划分、同输入和同评测器的受控外部比较。

结果在论文中标记为 **controlled external baseline**，不表述为完全相同训练框架下的严格配对实验。

## 范围与不变项

### 纳入范围

- 使用官方 D-FINE PyTorch 实现及 D-FINE-L 原始结构。
- 使用 VisDrone2019-DET 官方 train/val/test 划分和 10 类标签。
- 使用 640×640 输入、100 epochs、batch=8、seed=0 的首轮控制实验。
- 生成确定性的 COCO 标注、预测文件、评测结果、参数量/GFLOPs 和运行元数据。
- 支持断点续训、best checkpoint 选择和 test 一次性复评。

### 明确不做

- 不把 D-FINE-L 移植进 Ultralytics。
- 不重新训练或覆盖现有联合版 checkpoint。
- 不把第三方 VisDrone 数值直接写入严格主表。
- 不上传模型权重、原始数据或服务器凭据到 GitHub；只保存可审计元数据和哈希。

## 方案架构

准备包放在：

`paper_material/evidence/visdrone_dfine_l_external_20260913/`

建议包含以下文件：

- `README.md`：服务器端从环境变量到训练、续训、评测的完整步骤。
- `dfine_hgnetv2_l_visdrone_control.yml`：D-FINE-L VisDrone 配置，数据路径由服务器端替换或环境变量注入。
- `run_train.sh`：首轮训练入口，固定 seed、epochs、输出目录。
- `run_resume.sh`：从 `last.pth` 续训入口，禁止改变配置和输出目录。
- `run_test_eval.sh`：使用锁定的 `best_stg2.pth` 生成 test 结果。
- `collect_metrics.py`：读取 D-FINE 日志/评测输出，生成标准化 JSON/CSV。
- `result_template.json`：未填充的结果模板，防止把未完成实验误写为正式结果。
- `authority.json`：数据签名、代码提交、配置哈希、checkpoint 哈希和评测环境字段。
- `SHA256SUMS.txt`：对配置、脚本、结果和日志做完整性登记。

## 数据流

```text
VisDrone YOLO images/labels
        |
        v
deterministic YOLO -> COCO conversion
        |
        +--> instances_train.json / instances_val.json / instances_test.json
        |
        v
official D-FINE-L trainer (train/val)
        |
        +--> last.pth, best_stg1.pth, best_stg2.pth, log.txt
        |
        v
locked best_stg2.pth -> common COCO prediction/evaluation contract
        |
        v
val selection + one-time test report + complexity metadata
```

转换阶段必须校验：val 为 548 张图像、38,759 个标注；test 为 1,610 张图像、75,102 个标注。计数或类别映射不一致时停止，不发布 JSON。

## 训练协议

首轮 D-FINE-L 控制实验使用：

- `pretrained=false`，从头训练，避免与当前联合版的初始化条件混淆；
- 100 epochs；
- batch=8、workers=8；
- 640×640；
- seed=0、AMP 开启、确定性开关开启；
- 训练只使用 train，val 仅用于逐轮选择 best；
- test 标注不得参与训练或选模。

D-FINE 的 HGNetv2-B4、D-FINE Transformer、FDR 和 GO-LSD 保持官方实现。若服务器无法支持官方配置，应记录为阻塞，不自行改写核心算法后冒充 D-FINE-L。

## 统一评测合同

你的 Ultralytics 联合版和 D-FINE-L 都要导出到相同的 COCO detection JSON 结构，然后使用同一评测实现。固定：

- `split=val` 选择 best，`split=test` 做最终复评；
- `imgsz=640`；
- `conf=0.001`；
- `max_det=300`；
- 关闭 TTA、half、rect 和 cache；
- 报告 mAP50-95、AP50、AP75、AP_S/M/L、Precision、Recall、F1；
- 同时报告参数量和 GFLOPs，并注明参数统计口径。

当前联合版 checkpoint 只读复评，不重新训练。D-FINE-L 与当前模型的差值只有在共同评测合同下才可计算；论文中仍需注明两者训练框架不同。

## 错误处理与可恢复性

- 数据路径不存在、标注计数不符、类别越界、NaN/Inf 或缺少标签时立即失败。
- 训练输出目录必须是新的、唯一的目录；脚本拒绝覆盖已有非空目录。
- 训练中断时只允许从同一配置的 `last.pth` 续训，禁止用 `best_stg2.pth` 继续训练。
- 评测前校验 checkpoint 存在、文件大小非零、哈希已登记。
- 任何缺失的指标写为 `null`，不得用公开论文数字补齐本次实验。

## 验证计划

实现后必须完成：

1. 配置静态检查：10 类、B4、640、100 epochs、seed=0、数据路径字段齐全。
2. 转换脚本检查：确定性输出、类别映射、val/test 计数和 SHA-256。
3. 训练入口 dry-run：确认官方 D-FINE-L 构图和数据加载，不启动完整训练。
4. 续训入口检查：无 `last.pth` 时明确失败，有 checkpoint 时参数一致。
5. 结果收集检查：未完成训练不能生成 `status=complete`。
6. 现有材料完整性测试必须继续通过。

## 完成标准

准备工作完成的定义是：服务器可按 README 执行；配置、脚本和数据转换均通过静态/单元检查；能够生成独立输出目录和审计模板；现有联合版文件、结果和主表没有被修改。完整训练结果只有在服务器实际运行结束并通过 checkpoint、日志和评测复核后才登记。

# 无服务器 v2：对抗性检查、修复与源码交付

日期：2026-09-06。当前方法修订：`v2-fp32-extent-logspace-ac-bpdd`。
这是本地数值正确性与代码执行交付，不是 Formal100 或精度提升报告。

验收：相关代码回归 **176 通过、1 项 CUDA 跳过**；材料完整性与新部署检查
**45 通过**。源码 602 个 tracked 文件的 ZIP 内容已逐一与 Git blob 校验一致。

## 先读这三项

1. [对抗性审计与建议裁决](ADVERSARIAL_AUDIT_ZH.md)：修正先前建议，不否定作者独立提出 BPDD 数学构造的声明。
2. [本地验证与服务器运行手册](RUNBOOK_ZH.md)：F/G/H/I 的同版本对照、启动入口与待测边界。
3. [机器验证报告](TEST_REPORT.json)与[源码身份](SOURCE_AUTHORITY.json)：确切 commit、环境、测试命令和校验值。

## 已补齐什么

- FP32 直接框解码及机器精度宽高下限，避免 BF16 下微小正框在 XYXY 转换后归零。
  保留历史 distance-space 下限，不增加固定归一化 1e-3 小目标尺寸先验。
- AC-BPDD 候选、混合教师和质量评分全部使用 log-space；较差的 NLL40 教师不能
  因概率裁剪而监督 NLL20 学生。空教师门控为零，教师停止梯度。
- 补充 F 基线及四臂相同配置/初始化合同；VisDrone 与 UAVDT 共用运行记录器。
- 四臂完整模型的 FP32/CPU BF16 前向、criterion、反向、一步更新与 eval 测试。
- 神经网络与 FP32 几何间的精度转换边界；CPU 纯 FP16 明确拒绝保护。

本机 CPU FP16 的 stock `grid_sample` 对有限输入出现 NaN，同输入 FP32 正常。
保护测试证明此模式被明确拒绝，**不是 FP16 推理成功**。没有修改 FIA 结构，
没有宣称修复 PyTorch 上游，也不把该本机现象外推到 CUDA。

## 源码包与验证

代码维护分支：[codex/no-server-correctness-v2](https://github.com/kkc236/uav-detection-baselines/tree/codex/no-server-correctness-v2)。
确切源码以 `SOURCE_AUTHORITY.json` 中的完整 commit 为准，而非未来可能移动的分支。

[source.zip](source.zip) 由该 commit 的 `git archive` 直接生成，含全部 tracked
文件，不含本地权重、数据集、token、未跟踪文件或本轮生成的 local-validation。
ZIP comment 保存 source commit。交付时还逐文件对照 Git blob ID 验证了 archive；
SHA-256 用于检查下载损坏，不是外部签名或独立审核背书。

在材料仓根目录执行：

```bash
python -m pytest tests/test_material_integrity.py tests/test_lrs_fdr_material.py tests/test_equal_material.py tests/test_dfine_equal_fia_material.py tests/test_no_server_v2_deployment.py -q -p no:cacheprovider
```

代码回归命令完整记录在 `TEST_REPORT.json`。固定 D-FINE commit 的精确原语比对
需要其测试文件声明的 upstream checkout；其获取方式由源码测试入口负责。

## 原始执行证据

- `red.xml`：初始对抗性回归，含新增 API/对照臂缺失与数值行为失败，不全部算历史代码 bug。
- `half-red.xml`：完整 `.half()` 模型的 Float/Half 类型冲突。
- `half-green.xml`：中间运行，虽文件名含 green，实际仍有 1 个 NaN 失败，**不是通过证据**。
- `half-guard-red.xml`：明确拒绝 CPU FP16 的保护尚未实现时，两项失败。
- `regression-final.xml`：最终源码回归的权威原始结果；中间记录不与其累计计算。
- `material-regression.xml`：首次材料检查 44 通过、1 失败，发现方法页遗漏了已有
  `representability firewall` 术语；恢复该术语，未削弱测试断言。
- `material-regression-final.xml`：修正后的材料检查，45 通过。

上述 XML 的原始校验值在 `TEST_REPORT.json`。失败证据保留原样，不删除负结果。

## 仍未完成

CUDA FP16/AMP、正式数据与真实初始化文件的部署检查、640/batch8 训练、四臂 v2
Formal100、UAVDT Full 和导出后 engine 均未验证。随机 128 输入不提供 AP 或收敛证据。
旧 LRS-FDR、旧 final-assignment BPDD 与旧组合数值保持其原始源码身份，不移填到 v2。

实验优化建议也已修正：不因 g−f 未增益就取消 i−h；不能用固定 0.2–0.3 pp
充当统计显著性阈值。没有服务器时先冻结上述执行与证据边界，不凭合成测试填新结果。

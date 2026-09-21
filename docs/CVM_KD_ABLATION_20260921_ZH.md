# 当前 Full 的最小 KD 对照

基于正式 Full 提交 `a43056af2a843ec9bae109d3420367c13f3bcef6`。本入口不更改模型图、专家直接监督、FIA、FGL/LQS、初始化方式、100 epoch训练设置或KD日程。

| mode | 定位KD | edge-NLL/support/assignment筛选 | mixed-box IoU筛选 |
|---|---|---|---|
| `no_kd` | 关闭 | 仅计算诊断 | 仅计算诊断 |
| `edge_only` | 开启 | 保留 | 仅计算诊断，不作用于loss |
| `mixed` | 开启 | 保留 | 原Full规则 |

分类KD始终为0。no_kd保留专家直接classification/L1/GIoU/FGL监督和专家推理输出。所有模式的原始Safe构造器均先验证原配置；随后显式应用消融选项并写入authority与checkpoint元数据。

## 部署与启动

运行前提交本次修改，入口要求干净tracked工作树。使用原 `/root/miniconda3/envs/lrs-v2/bin/python` 环境，先运行关键测试。以下 `$DATASET_ROOT` 需指向原authority的数据根目录，不能指向另一个转换版本。

```bash
/root/miniconda3/envs/lrs-v2/bin/python -m pytest -q tests/test_cvm_kd_ablation.py tests/test_bpdd_capacity_loss.py tests/test_capacity_fia.py

CUDA_VISIBLE_DEVICES=0 /root/miniconda3/envs/lrs-v2/bin/python scripts/train_cvm_kd_ablation.py --mode no_kd --dataset-root "$DATASET_ROOT" --initial-state /root/sj-tmp/protocols/lrs-v2-f56b210/initial-state-seed0.pt --output-root /root/sj-tmp/runs/cvm-kd-ablation-20260921 --dry-run

CUDA_VISIBLE_DEVICES=1 /root/miniconda3/envs/lrs-v2/bin/python scripts/train_cvm_kd_ablation.py --mode edge_only --dataset-root "$DATASET_ROOT" --initial-state /root/sj-tmp/protocols/lrs-v2-f56b210/initial-state-seed0.pt --output-root /root/sj-tmp/runs/cvm-kd-ablation-20260921 --dry-run
```

核验authority中的数据hash、initial-state hash与原Full相同后，删除对应命令的`--dry-run`即可正式启动。每个进程内部仍使用device=0；CUDA_VISIBLE_DEVICES分别映射物理GPU。默认名称分别为`formal-seed0-kd-no_kd`、`formal-seed0-kd-edge_only`。mixed行可复用旧Full，但需保留旧来源身份并完成默认loss/梯度等价测试，不能改写旧commit/hash。

## 记录和恢复

- `authority/<name>.json`：新代码身份、原Full来源、原配置hash、实际生效KD选项、数据、初始化、环境和训练设置。
- `<name>/kd-effective.json`：实际模型模式/options、完整fresh模型初始化张量hash、参数量。两臂的hash及参数量必须一致。
- `<name>/full-runtime.jsonl`：沿用原记录器。
- `<name>/kd-runtime.jsonl`：补充候选边、mixed gate原本会拒绝的边、选中边、应用边、权重和loss统计。
- `edge_candidates_before_iou`是edge-NLL/support/assignment筛选后的候选；`active_edges`是按当前模式选中的边，**在noKD及零日程阶段仍可能非零**；`applied_edges`仅在有效定位KD权重大于0时计数。`selected_weight_sum`不是已乘日程/全局系数的loss。拒绝计数包含IoU相等情况，不可全称“有害边”。

中断后保持同一代码、环境、数据、输出名称与参数，在原命令后加：

```bash
--resume /root/sj-tmp/runs/cvm-kd-ablation-20260921/formal-seed0-kd-no_kd/weights/last.pt
```

恢复仅接受该run自己的`weights/last.pt`、原authority和相同checkpoint KD模式；交叉臂或旧Full权重会拒绝。保留`optimizer-evidence.jsonl`，原固定AMP训练器需要它核验恢复。完成100轮、已去除优化器的权重不能续训。恢复沿用Ultralytics的epoch/优化器/EMA恢复；它不保存完整数据加载/RNG状态，因此不宣称和未中断训练逐位一致。恢复事件和权重hash另记`authority/<name>.resumes.jsonl`。

## 比较口径

三臂统一使用native validation AP50:95选best，同时保留epoch100。先看同一评估器下专家最终输出；如另做base输出诊断须标记。两臂训练数据、初始state分别应匹配原Full摘要`FD92E9FF...BBDAB`及`935D6842...65D5B`。不得由两份旧/新实验自动声称多种子重复或统计显著。

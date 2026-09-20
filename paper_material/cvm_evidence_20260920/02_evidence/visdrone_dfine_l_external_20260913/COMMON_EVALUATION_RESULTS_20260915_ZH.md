# VisDrone 联合模型与 D-FINE-L 统一评估结果

## 当前状态

2026-09-15 北京时间 08:12，训练后的自动评估完成。服务器已产生 `supervisor-complete.txt`、`COMPARISON.md` 和状态为 `evaluation_complete` 的 `cross-protocol-manifest.json`。

比较模型：LRS-GFDR + Capacity-BPDD-v3-Safe + FIA，版本标识 `v3-safe-loc-kd-decay80-100-no-cls-kd`；对照是 D-FINE-L 本项目从头训练适配版。双方均使用已有权重执行推理，无需再次训练。

## 统一评估结果（maxDets=300）

指标为百分比，差值为“联合模型减 D-FINE-L”的百分点（pp）。

| 权重选择 | 划分 | D-FINE AP50-95 | 联合 AP50-95 | 差值 pp | D-FINE AP50 | 联合 AP50 | 差值 pp |
|---|---|---:|---:|---:|---:|---:|---:|
| final / final | val | 28.501 | 30.528 | +2.027 | 46.765 | 50.561 | +3.796 |
| final / final | test | 22.554 | 24.133 | +1.579 | 38.656 | 41.885 | +3.229 |
| best / best | val | 28.796 | 30.727 | +1.931 | 47.248 | 50.803 | +3.555 |
| best / best | test | 22.679 | 24.229 | +1.550 | 38.940 | 42.009 | +3.069 |

预先固定的主终点为第 100 轮 final 对 final、AP50-95@300；次终点为各自原生验证集选择的 best 对 best。全部 8 组比较（包括 maxDets=100）保存在 [COMPARISON.md](common_evaluation_20260915/COMPARISON.md)。16 份 `*.cap100.json` / `*.cap300.json` 同时含 AP75、APs/APm/APl、AR、逐类 AP。

## 证据核验

- val 双方均为 548 张，test 双方均为 1,610 张；标注清单与 SHA-256 保存在 `dataset-preflight.json`。
- 同一 `pycocotools.COCOeval` 2.0.11；双方都使用 PIL 双线性直接拉伸到 640×640、FP32、score>0.001、最多 300 个原生检测输出、无额外 NMS、无 TTA。
- D-FINE best SHA-256 为 `7b2e19b7244a128882710f35589c85b0b9841e08d4e355b26e5b6a98972f8d00`；final 为 `c9a535bfb8ff6ad9187d6acf7512a8b0f3dcc376353e3f49915cd84b672b2a42`，与 Release 中的权重一致。
- 联合 best SHA-256 为 `39f006df9548b4d5da968b9302fc14678fabaf2009802bc09a68fb23dd146bc6`；final 为 `1e826e331af4ff5e4b4b3a6459b45950418dc08a202188d101594a33aee35b5a`。
- 从服务器下载的 16 份指标报告、8 份推理报告，全部 24 个文件哈希与生成时的清单匹配。原始字节保留，防止 Git 换行转换使哈希改变。
- 轻量原始证据包 `dfine-bs4-common-eval-evidence-20260915.tar.gz`：25,235 字节，SHA-256 `72085d1fe587a797dbf9df8719b0ce3d7538a301c476d4a7091a56adec35f4f7`。

## 现在具体怎么操作

1. 读取本表及 `common_evaluation_20260915/COMPARISON.md`，将外部统一评估单独列入论文实验部分。
2. 保留 `common_evaluation_20260915/`、两个 D-FINE 权重以及联合模型的 best/last 权重。Release 提供 D-FINE 权重与本次轻量评估证据包。
3. 在已部署的同一服务器上，需要复评时仅运行下面的评估入口。新输出目录自动带时间；程序按既有配置读取双方权重，导出预测并重新评分。

```bash
cd /root/sj-tmp/eval/visdrone_dfine_bs4_cross_20260914
export EVAL_ROOT="/root/sj-tmp/eval/visdrone_dfine_bs4_recheck_$(date +%Y%m%d_%H%M%S)"
nohup bash cross_protocol_bs4_pipeline.sh > "${EVAL_ROOT}.log" 2>&1 &
```

复评前提是原服务器的两个 Python 环境、D-FINE 源码/配置、冻结联合模型源码、数据、双方权重和 `completion.json` 都保留。执行 `run_bs4_cross.sh` 会走训练入口，当前没有必要重训。原有输出目录 `/root/sj-tmp/eval/visdrone_dfine_bs4_results_20260914` 已有完整结果。

原始 JSONL 预测和 COCO 预测仍保存在服务器结果目录，共约 723 MiB；本次轻量证据包收录它们的清单哈希及指标报告。重新计算指标可使用原始预测，或从冻结权重重新导出预测。

## 论文表述边界

这些结果支持“在共同评估设置下，本项目联合模型优于本项目复现的 D-FINE-L”。训练 batch、有效 batch、优化器、数值精度与增强仍不同，应披露为跨训练协议的外部比较；内部同协议消融承担模块增益归因。

这里的 test 是项目既有 1,610 张有标签测试划分；YOLO 转换标注缺少完整官方 ignore 区域，且该划分此前是否参与开发无法认证。论文应写明划分及规则，不声称首次盲测或官方 VisDrone 挑战赛成绩。训练日志中的原生 AP 与本次统一评估 AP 分别保存，避免把 28.7726% 的原生验证值和 28.7959% 的统一验证值混列。

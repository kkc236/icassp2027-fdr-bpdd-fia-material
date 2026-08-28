# VisDrone LRS-FDR / BPDD / FIA 最终实验交接计划

> **For agentic workers:** REQUIRED SUB-SKILL: 使用 `executing-plans` 逐项执行；若要
> 并行训练，必须由作者明确授权后再使用 `subagent-driven-development`。所有步骤均
> 使用本文的复选框记录进度。

**目标：** 在 VisDrone2019-DET 上完成 LRS-FDR、BPDD、FIA 的同身份系统消融，
生成可直接进入 C 类会议论文主表的训练、评估、复杂度和可复现性证据。

**架构：** 以 LRS-FDR 为统一定位底座，在同一个最终源码 commit 上构建四个实验
臂：LRS-FDR、LRS-FDR+BPDD、LRS-FDR+FIA、Full。BPDD 只改变训练损失，FIA 只
增强 P3；所有臂共享数据、初始权重、seed、训练超参数和 best 选择规则。

**技术栈：** Python、PyTorch、Ultralytics RT-DETR-L、CUDA、VisDrone2019-DET、
COCO 风格评估器。

---

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: plan
- Origin Date: 2026-08-28
- Verification Status: ANALYZED
- Version Label: visdrone_lrs_system_handoff_v1
- Paper Route: RT-DETR-L → LRS-FDR → BPDD → FIA
- Primary Metric: VisDrone val mAP50-95
- Selection Seed: 0
- Formal Epochs: 100

## 1. 接手者必须先知道的事实

### 1.1 当前论文方法身份

| 论文身份 | 内部组成 | 论文用途 |
|---|---|---|
| Original FDR | 历史 FDR 实现 | 第一创新外部历史对照 |
| NA-FDR | native reference/assignment/normal-query 对齐 | LRS-FDR 的 `w/o LRS` 内部消融 |
| LRS-FDR | NA-FDR + LRS-FGL | 第一项完整创新 |
| BPDD | future-layer softmin teacher + better-only gate | 第二项创新，训练期模块 |
| FIA | P3-only 特征增强 | 第三项创新，推理期模块 |
| Full | LRS-FDR + BPDD + FIA | 最终投稿系统 |

历史运行名 `Clean FDR` 只用于绑定既有日志和 checkpoint。新配置、结果表和正文必须
使用 NA-FDR / LRS-FDR；不得回写或重命名历史原始文件。

### 1.2 已冻结、无需为本任务重复制造的证据

| 对比 | 已有结果 | 状态 |
|---|---:|---|
| NA-FDR − Original FDR | mAP `+0.616 pp`，AP75 `+0.699 pp` | 已完成 |
| LRS-FDR − NA-FDR | mAP `+0.011 pp`，AP75 `+0.471 pp`，Recall `+0.227 pp` | 已完成 |
| LRS-FDR − Original FDR | mAP `+0.627 pp`，AP75 `+1.170 pp` | 已完成 |
| 旧 AP-FDR+BPDD − 旧 AP-FDR | val/test mAP `+0.239/+0.283 pp` | 仅机制证据 |
| FIA-only − corresponding baseline | val/test mAP `+0.7946/+0.8101 pp` | 仅 standalone 证据 |

权威材料：

- [LRS-FDR 方法](../methods/FDR_ZH.md)
- [LRS-FDR 三臂结果](../results/LRS_FDR_RESULTS_ZH.md)
- [LRS-FDR 冻结证据包](../evidence/lrs_fdr_formal100_20260828/README.md)
- [BPDD 方法](../methods/BPDD_ZH.md)
- [FIA 方法](../methods/FIA_ZH.md)
- [当前路线状态](../CURRENT_RERUN_STATUS_ZH.md)

### 1.3 已发布的最终源码冻结（组合身份已解决）

最终 LRS 系统源码已经在公开仓库中按 branch/tag/commit 冻结；本节只登记来源和
验证入口，不把 Formal100 训练或 G/H/I 结果标记为完成。

| 项目 | 冻结值 |
|---|---|
| Repository | `https://github.com/kkc236/uav-detection-baselines` |
| Source branch | `codex/lrs-system-visdrone-rebuild` |
| Release tag | `visdrone-lrs-system-v1` |
| Release commit | `445120b7337dad0ccc41d18ad081b6b33580dcd2` |
| Launcher | `scripts/train_visdrone_lrs_system.py` |
| Runbook | [`docs/VISDRONE_LRS_SYSTEM_RUNBOOK_ZH.md`](https://github.com/kkc236/uav-detection-baselines/blob/visdrone-lrs-system-v1/docs/VISDRONE_LRS_SYSTEM_RUNBOOK_ZH.md) |

该 release 已签入组合配置与启动器；source-focused verification suites 已通过。
材料只保留这一结论并绑定 release tag，不合并其他 review 的测试计数。正式
VisDrone G/H/I（对应下表的 `lrs_fdr_bpdd` / `lrs_fdr_fia` / `full`）仍为待训练、
待评估，不能填入 Formal100 结果。

| 标签 | 方法身份 | 配置 |
|---|---|---|
| `g` | LRS-FDR+BPDD | `configs/rtdetr-l-lrs-fdr-bpdd.yaml` |
| `h` | LRS-FDR+FIA | `configs/rtdetr-l-lrs-fdr-fia.yaml` |
| `i` | LRS-FDR+BPDD+FIA（Full） | `configs/rtdetr-l-lrs-fdr-bpdd-fia.yaml` |

旧配置仍然禁止用于新系统证据：`configs/rtdetr-l-fdr-bpdd.yaml`、
`configs/rtdetr-l-fdr-fia.yaml`、`configs/rtdetr-l-fdr-bpdd-fia.yaml` 及其旧启动器
保持历史身份。不得用旧 BPDD/FIA 运行目录改名为 LRS-FDR。

### 1.4 GitHub 凭据安全合同

GitHub PAT、SSH 私钥、服务器密码不得写入本文、YAML、authority、日志、shell
历史或 Git commit。用户在 2026-08-28 对话中发送过一个 PAT；该 token 应视为已经
暴露，必须在 GitHub Settings → Developer settings 中撤销并轮换。

下一次服务器会话使用以下两种方式之一：

**推荐：GitHub CLI 设备授权，不复制 PAT：**

```bash
gh auth login --hostname github.com --git-protocol https --web
gh auth status --hostname github.com
gh auth setup-git
```

**必须使用新 PAT 时：仅在当前 shell 静默注入：**

```bash
read -rsp 'GitHub token: ' GITHUB_TOKEN
export GITHUB_TOKEN
echo
test -n "$GITHUB_TOKEN"
gh auth status --hostname github.com
```

禁止使用 `echo TOKEN`、把 token 放在 clone URL 中，或将 token 写入 `.env` 后提交。
任务结束执行 `unset GITHUB_TOKEN`。材料仓库的 PAT 扫描测试必须保持通过。

## 2. 最终实验矩阵

### 2.1 严格默认矩阵：三臂训练 + 冻结控制参考

| Variant ID | 方法 | Native alignment | LRS | BPDD | FIA | 主要对照 |
|---|---|:---:|:---:|:---:|:---:|---|
| `lrs_fdr` | LRS-FDR | ✓ | ✓ | × | × | 已冻结的历史控制参考，不是本 launcher 的 arm |
| `lrs_fdr_bpdd` | LRS-FDR+BPDD | ✓ | ✓ | ✓ | × | 相对 `lrs_fdr` 隔离 BPDD |
| `lrs_fdr_fia` | LRS-FDR+FIA | ✓ | ✓ | × | ✓ | 相对 `lrs_fdr` 隔离 FIA |
| `full` | LRS-FDR+BPDD+FIA | ✓ | ✓ | ✓ | ✓ | 最终投稿方法 |

必须计算六个方向：

1. `lrs_fdr_bpdd − lrs_fdr`：BPDD 主效应；
2. `lrs_fdr_fia − lrs_fdr`：FIA 主效应；
3. `full − lrs_fdr_bpdd`：BPDD 存在时的 FIA 增益；
4. `full − lrs_fdr_fia`：FIA 存在时的 BPDD 增益；
5. `full − lrs_fdr`：BPDD+FIA 联合增益；
6. `full − RT-DETR-L`：最终系统总体增益。

### 2.2 算力受限矩阵：仅在 Gate 0 全通过后允许

若复用既有 LRS-FDR checkpoint，只新增训练：

1. `lrs_fdr_bpdd`；
2. `lrs_fdr_fia`；
3. `full`。

采用该方案前，必须证明最终组合源码在 BPDD/FIA 关闭时与冻结 LRS-FDR 控制参考的
模型配置、共享参数初始化和预测输出一致。若 control reference 的 source commit、
初始权重、数据签名或默认关闭输出不能绑定，应按单独的 `scripts/train_lrs_fdr.py`
接口重训控制；当前 pending run list 仍只有 g/h/i。

## 3. Task 0：建立最终同身份实现

### 源码装配边界（release 复核入口）

从上节指定的 release tag checkout；不要重新装配或混用旧分支。以下文件已经由
release 提供，训练前仍需按 Gate 0 复核其关闭态与运行 authority：

- `configs/rtdetr-l-lrs-fdr-bpdd.yaml`
- `configs/rtdetr-l-lrs-fdr-fia.yaml`
- `configs/rtdetr-l-lrs-fdr-bpdd-fia.yaml`
- `scripts/train_visdrone_lrs_system.py`
- `src/rtdetr_lrs_system.py`
- `tests/test_lrs_system_configs.py`
- `tests/test_lrs_system_fia.py`
- `tests/test_lrs_system_launcher.py`
- `tests/test_lrs_system_models.py`

不得修改已有 LRS、BPDD、FIA 的原始证据文件。若需要组合模型类，应新建明确的
LRS 身份文件，不能让旧 `rtdetr_fdr_bpdd*.py` 的默认行为静默改变。

### 配置合同

- [ ] 三个新配置从 `rtdetr-l-lrs-fdr.yaml` 的 FDR 配置出发；
- [ ] 全部保持 `preliminary_box=false`；
- [ ] 全部保持 `distribution_feedback=false`；
- [ ] 全部保持 `supervise_pre_boxes=false`；
- [ ] 全部保持 `supervise_dn_fdr=false`；
- [ ] 全部保持 `edge_adaptive_fgl=false`；
- [ ] 全部保持 `reliability_shrinkage_alpha=0.25`；
- [ ] BPDD 配置固定 `weight=0.5`、`temperature=0.5`、`margin=0.02`、
  `include_dn=false`；
- [ ] FIA 使用 P3-only 拓扑：FIA 读取层 21，下一条 P4 路径也读取原层 21，
  decoder 输入为 FIA P3 与原 P4/P5；
- [ ] FIA 残差缩放继续零初始化并使用私有 RNG；
- [ ] g/h/i 与冻结控制参考使用同一 300-query、6-layer decoder 合同。

### 统一启动器接口

`scripts/train_visdrone_lrs_system.py` 已提供：

```text
--arm {g,h,i}
--dataset-root PATH
--initial-state PATH
--output-root PATH
--name NAME
--dry-run
```

启动器必须拒绝：脏工作区、已存在且 authority 不一致的运行目录、错误的初始权重、
不完整的数据集以及从非零 epoch 伪装的新 Formal100。允许恢复时必须从本臂自己的
`last.pt` 精确恢复，并保留原 run ID。

### 论文定稿评估 gate（尚未签入）

该 release 尚未签入新的 unified independent evaluator/comparator。能够生成 AP75、
逐类/逐尺度结果并进行同协议差值比较的脚本路径目前不存在，不能在本手册中虚构
`evaluate_visdrone_lrs_system.py`、`compare_visdrone_lrs_system.py` 或相应测试文件。
这不是训练 blocker：在 relaxed reference standard 下，训练与 best-val 选择使用
release launcher 的同 Trainer validation 和 `results.csv`。论文定稿前必须把统一
evaluator/comparator（含 AP75、per-class、scale、identity/protocol checks）签入
源码并单独复核；在该 gate 通过前，不得把 G/H/I 的 AP75 或逐类结果写入正式论文表。

## 4. Gate 0：训练前工程门

以下检查必须全部通过，任何一项失败都不得开始 Formal100。

### 4.1 身份与来源

- [ ] 最终源码已经提交，`git status --porcelain` 为空；
- [ ] `git rev-parse HEAD` 写入每个运行 authority；
- [ ] 冻结 LRS 算法 commit `9fa907...` 是最终 commit 的祖先或其改动被逐字合入；
- [ ] 记录三个新 YAML 的 SHA-256；
- [ ] 记录 initial-state SHA-256；
- [ ] 记录 train/val/test annotation SHA-256；
- [ ] g/h/i 使用同一个 initial-state 文件；冻结控制参考沿用其既有 identity。

### 4.2 Default-off 与状态隔离

- [ ] `full` 中 BPDD 关闭、FIA 不插入时，配置退化为 `lrs_fdr`；
- [ ] 相同 batch 下共享参数与 `lrs_fdr` 初始化逐张量一致；
- [ ] BPDD 关闭时预测与损失逐项一致；
- [ ] FIA 零门控时 P3 输出与输入逐元素一致；
- [ ] FIA 私有 RNG 不改变 P4/P5、decoder 和 LRS-FDR 共享参数；
- [ ] LRS 最终 decoder 层 `alpha=0`；
- [ ] LRS 每图像、每层可靠性权重总和守恒；
- [ ] state-dict 缺键、重键和意外键均为零或显式登记的 FIA 私有参数。

### 4.3 一批真实数据 smoke test

- [ ] 使用真实 VisDrone batch 执行一次 FP32 前向/反向；
- [ ] g/h/i 三个待训练臂的损失均有限；冻结控制参考只绑定既有 authority；
- [ ] LRS 统计存在且有限；
- [ ] BPDD 臂含 `loss_bpdd`，非 BPDD 臂不含；
- [ ] BPDD active-edge ratio 大于零；
- [ ] FIA 参数获得有限梯度；
- [ ] AMP 单步无 NaN/Inf；
- [ ] 保存 Gate 0 JSON，状态必须为 `PASS`。

## 5. 服务器环境与冻结变量

### 5.1 跨服务器目标环境

已有冻结评估记录的成功环境为：

| 项目 | 精确值 |
|---|---|
| OS userland | Ubuntu |
| Python | `3.10.12` |
| GPU | `NVIDIA GeForce RTX 4090` |
| NVIDIA driver | `550.142` |
| CUDA runtime | `12.1` |
| PyTorch | `2.5.1+cu121` |
| torchvision | `0.20.1+cu121` |
| Ultralytics | `8.4.90` |

驱动可以高于 `550.142`，但必须兼容 CUDA 12.1；Python、torch、torchvision 和
Ultralytics 必须保持上述版本。若 GPU 型号改变，训练精度仍可比较，但 latency/FPS
不能与 4090 表直接合并。

### 5.2 下载与镜像优先级

依赖下载顺序固定为：

1. 已验证的本地 wheelhouse；
2. 清华 PyPI 镜像下载普通 Python 包；
3. PyTorch 官方 CUDA 12.1 wheel index 下载 torch/torchvision；
4. 官方源仅作为上述源失败后的人工回退。

不要通过未经校验的 GitHub 反向代理下载源码或 checkpoint。源码从 GitHub 官方地址
获取后必须 checkout 到指定 commit；数据和初始权重无论从哪里传输都必须通过本文
SHA-256。

公开源码仓库不需要 PAT。训练服务器必须按已发布 branch/tag/commit 复核源码：

```bash
set -euo pipefail

export REPO_ROOT="/data/uav/code/uav-detection-baselines"
export SOURCE_URL="https://github.com/kkc236/uav-detection-baselines.git"
export SOURCE_BRANCH="codex/lrs-system-visdrone-rebuild"
export SOURCE_TAG="visdrone-lrs-system-v1"
export SOURCE_COMMIT="445120b7337dad0ccc41d18ad081b6b33580dcd2"

if [ ! -d "$REPO_ROOT/.git" ]; then
  git clone --filter=blob:none "$SOURCE_URL" "$REPO_ROOT"
fi

cd "$REPO_ROOT"
test "$(git remote get-url origin)" = "$SOURCE_URL"
git fetch --prune origin "$SOURCE_BRANCH" --tags
test "$(git rev-parse "refs/remotes/origin/$SOURCE_BRANCH")" = "$SOURCE_COMMIT"
test "$(git rev-list -n 1 "$SOURCE_TAG^{commit}")" = "$SOURCE_COMMIT"
git switch --detach "$SOURCE_TAG"
test "$(git rev-parse HEAD)" = "$SOURCE_COMMIT"
test -f scripts/train_visdrone_lrs_system.py
test -f configs/rtdetr-l-lrs-fdr-bpdd.yaml
test -f configs/rtdetr-l-lrs-fdr-fia.yaml
test -f configs/rtdetr-l-lrs-fdr-bpdd-fia.yaml
test -f docs/VISDRONE_LRS_SYSTEM_RUNBOOK_ZH.md
```

不要重新创建或强制覆盖已有分支，也不要在服务器上编辑 release 文件。训练服务器
只 checkout 上述 detached tag，并将 `git rev-parse HEAD` 写入每个 authority。

在首台可联网服务器构建 wheelhouse：

```bash
set -euo pipefail

export WHEELHOUSE="/data/uav/wheelhouse/py310-cu121-20260828"
mkdir -p "$WHEELHOUSE"

python3.10 -m pip download \
  --dest "$WHEELHOUSE" \
  --index-url https://pypi.tuna.tsinghua.edu.cn/simple \
  --extra-index-url https://download.pytorch.org/whl/cu121 \
  torch==2.5.1+cu121 torchvision==0.20.1+cu121 \
  ultralytics==8.4.90 pytest requests

cd "$WHEELHOUSE"
find . -maxdepth 1 -type f ! -name MANIFEST.sha256 -printf '%P\0' \
  | sort -z \
  | xargs -0 sha256sum > MANIFEST.sha256
sha256sum -c MANIFEST.sha256
```

在每台训练服务器从 wheelhouse 安装：

```bash
set -euo pipefail

export REPO_ROOT="/data/uav/code/uav-detection-baselines"
export WHEELHOUSE="/data/uav/wheelhouse/py310-cu121-20260828"

python3.10 -m venv "$REPO_ROOT/.venv"
source "$REPO_ROOT/.venv/bin/activate"
python -m pip install --no-index --find-links "$WHEELHOUSE" \
  torch==2.5.1+cu121 torchvision==0.20.1+cu121 \
  ultralytics==8.4.90 pytest requests

python - <<'PY'
import platform
import torch
import torchvision
import ultralytics

assert platform.python_version() == "3.10.12", platform.python_version()
assert torch.__version__ == "2.5.1+cu121", torch.__version__
assert torchvision.__version__ == "0.20.1+cu121", torchvision.__version__
assert ultralytics.__version__ == "8.4.90", ultralytics.__version__
assert torch.version.cuda == "12.1", torch.version.cuda
assert torch.cuda.is_available()
print("ENVIRONMENT_LOCK=PASS")
print(torch.cuda.get_device_name(0))
PY
```

若 wheelhouse 不在新服务器，优先通过对象存储或 `rsync` 整体传输 wheelhouse 及其
manifest，传输后先运行 `sha256sum -c MANIFEST.sha256`。完整 `pip freeze` 在
5.6 节创建运行目录后保存。

### 5.3 不可变输入哈希

| 输入 | SHA-256 / 固定计数 |
|---|---|
| LRS 算法源 commit | `9fa9078011d92cc23fc1f0eec06ff34983986ff0` |
| LRS 源 tree SHA-256 | `2345E1B06301A1E1563163481691BEB00A15D4FDC5028AF4399A1ABA2AE8AE3E` |
| 原 LRS YAML | `6225C4BBC6B67C3C364E23476FC12A078F2091D61223632468765EA260160C87` |
| Formal initial-state | `51AAB2EB3FB7D123501C69C7B8DC90FF3EA0B9344A108EDEEF2C7D6DCDBB742D` |
| VisDrone dataset signature | `FD92E9FF4B3B58FCDD5A32F7E770FC3398E566B627DB0E188CB5FF9F3B7BBDAB` |
| Dataset file count | `14,038` |
| train | 6,471 images / 343,204 instances |
| val | 548 images / 38,759 instances |
| test local held-out | 1,610 images / 75,102 instances |

三个新组合 YAML 会产生新的 SHA-256，这是正常现象；但每个 YAML 必须从 release
commit 读取并写入各自 authority，不能在服务器上临时编辑。冻结控制参考若需重训，
使用 release 中 `scripts/train_lrs_fdr.py` 的独立接口和独立 authority。

### 5.4 目录变量与启动前检查

在 Ubuntu 服务器进入最终源码目录后执行：

```bash
set -euo pipefail

export REPO_ROOT="/data/uav/code/uav-detection-baselines"
export VISDRONE_ROOT="/data/uav/datasets/VisDrone2019-DET"
export INITIAL_STATE="/data/uav/pretrained/rtdetr-l-formal-initial-state.pt"

cd "$REPO_ROOT"
export SOURCE_COMMIT="$(git rev-parse HEAD)"
export EXPERIMENT_TAG="visdrone-lrs-system-$(git rev-parse --short=8 HEAD)"
export RUN_ROOT="/data/uav/runs/$EXPERIMENT_TAG"

test -d "$VISDRONE_ROOT"
test -f "$INITIAL_STATE"
test -z "$(git status --porcelain)"
test ! -e "$RUN_ROOT"
mkdir -p "$RUN_ROOT"

python --version
nvidia-smi
test "$(sha256sum "$INITIAL_STATE" | awk '{print toupper($1)}')" = \
  "51AAB2EB3FB7D123501C69C7B8DC90FF3EA0B9344A108EDEEF2C7D6DCDBB742D"
git show -s --format='%H %s' HEAD
```

如果实际服务器不使用 `/data/uav`，只修改本节四个绝对路径变量；不得修改运行名称、
数据协议或实验超参数来适配路径。

### 5.5 冻结训练参数：必须逐项一致

| 类别 | 参数 | 固定值 |
|---|---|---|
| 任务 | task / mode | `detect` / `train` |
| 数据 | epochs / patience | `100` / `100` |
| 数据 | batch / imgsz / workers | `8` / `640` / `8` |
| 设备 | device | `0` |
| 权重 | pretrained / resume | `false` / `false`（新 Formal100） |
| 保存 | save / save_period / exist_ok | `true` / `-1` / `false` |
| 随机性 | seed / deterministic | `0` / `true` |
| 随机性 | CUBLAS_WORKSPACE_CONFIG | `:4096:8` |
| 优化器 | optimizer | `MuSGD` |
| 优化器 | lr0 / lrf | `0.01` / `0.01` |
| 优化器 | momentum / weight_decay | `0.937` / `0.0005` |
| 优化器 | nbs | `64` |
| warm-up | epochs / momentum / bias_lr | `3.0` / `0.8` / `0.0` |
| 调度 | cos_lr | `false` |
| 训练 | amp / cache / val / plots | `true` / `false` / `true` / `true` |
| 训练 | EMA | Ultralytics `8.4.90` 默认启用，checkpoint 记录 EMA |
| 训练 | fraction / dropout / multi_scale | `1.0` / `0.0` / `0.0` |
| 训练 | rect / compile / freeze | `false` / `false` / `null` |
| 检测 | max_det / nms | `300` / `false` |
| 损失 | box / cls / dfl | `7.5` / `0.5` / `1.5` |
| 增强 | mosaic / close_mosaic | `1.0` / `10` |
| 增强 | mixup / cutmix / copy_paste | `0.0` / `0.0` / `0.0` |
| 增强 | scale / translate | `0.5` / `0.1` |
| 增强 | degrees / shear / perspective | `0.0` / `0.0` / `0.0` |
| 增强 | flipud / fliplr | `0.0` / `0.5` |
| 增强 | hsv_h / hsv_s / hsv_v | `0.015` / `0.7` / `0.4` |
| 验证 | split / iou | `val` / `0.7` |

模型专属参数：

| 模块 | 参数 | 固定值 |
|---|---|
| FDR | reg_max / bins | `32` / `33` |
| FDR | reg_scale / up | `4.0` / `0.5` |
| FDR | cumulative | `true` |
| NA | preliminary_box / supervise_pre_boxes | `false` / `false` |
| NA | distribution_feedback / supervise_dn_fdr | `false` / `false` |
| LRS | edge_adaptive_fgl | `false` |
| LRS | fgl_weight | `0.15` |
| LRS | reliability_shrinkage_alpha | `0.25` |
| LRS | six-layer schedule | `[0.25,0.20,0.15,0.10,0.05,0.00]` |
| BPDD | enabled / weight | `true` / `0.5` |
| BPDD | temperature / margin / eps | `0.5` / `0.02` / `1e-6` |
| BPDD | matched_layer / include_dn | `final` / `false` |
| FIA | channels / topology | `256` / `P3-only` |
| Decoder | hidden_dim / queries / layers | `256` / `300` / `6` |

VisDrone data YAML 将模型的 `nc` 统一覆盖为 `10`。源模型 YAML 中的模板 `nc=80`
无需手动改写；必须保证 g/h/i 由同一数据 YAML 执行相同覆盖，冻结控制参考的
YAML/authority 单独核验。

Best selection 固定为 val mAP50-95 最大值；test 永远不参与选模。启动器必须从冻结
`FROZEN_SETTINGS` 读取参数，不能在命令行临时覆盖 optimizer、学习率、scheduler、
augmentation、batch 或 workers。

### 5.6 跨服务器一致性报告

每台服务器在 dry-run 前生成：

```bash
cd "$REPO_ROOT"
source "$REPO_ROOT/.venv/bin/activate"

python -m pip freeze | sort > "$RUN_ROOT/environment.freeze.txt"

python - <<'PY' > "$RUN_ROOT/runtime-identity.json"
import json
import platform
import subprocess
import torch
import torchvision
import ultralytics

payload = {
    "python": platform.python_version(),
    "torch": torch.__version__,
    "torchvision": torchvision.__version__,
    "torch_cuda": torch.version.cuda,
    "ultralytics": ultralytics.__version__,
    "gpu": torch.cuda.get_device_name(0),
    "source_commit": subprocess.check_output(
        ["git", "rev-parse", "HEAD"], text=True
    ).strip(),
}
print(json.dumps(payload, indent=2, sort_keys=True))
PY

sha256sum "$RUN_ROOT/runtime-identity.json" \
  "$RUN_ROOT/environment.freeze.txt" > "$RUN_ROOT/environment.sha256"
```

g/h/i authority 必须引用同一个 `runtime-identity.json` SHA；冻结控制参考沿用其既有
authority。不同服务器运行的臂只有
在 source/data/initial/config/training/runtime identity 全部一致时才标为严格可比；
GPU 型号不同则训练结果可作相同协议比较，但实时性单列。

## 6. Task 1：Dry-run 与 authority 冻结

当前 pending run list 只有 release launcher 的三个 arm：g、h、i。冻结的既有
LRS-FDR control 仅作为历史参考，不是该 launcher 的 arm；如需重训 control，使用
`scripts/train_lrs_fdr.py` 的独立接口和独立 authority。

三个待训练 arm 都先执行 dry-run：

```bash
cd "$REPO_ROOT"

python scripts/train_visdrone_lrs_system.py \
  --arm g \
  --dataset-root "$VISDRONE_ROOT" \
  --initial-state "$INITIAL_STATE" \
  --output-root "$RUN_ROOT" \
  --name formal-seed0-lrs_fdr_bpdd-v1 \
  --dry-run

python scripts/train_visdrone_lrs_system.py \
  --arm h \
  --dataset-root "$VISDRONE_ROOT" \
  --initial-state "$INITIAL_STATE" \
  --output-root "$RUN_ROOT" \
  --name formal-seed0-lrs_fdr_fia-v1 \
  --dry-run

python scripts/train_visdrone_lrs_system.py \
  --arm i \
  --dataset-root "$VISDRONE_ROOT" \
  --initial-state "$INITIAL_STATE" \
  --output-root "$RUN_ROOT" \
  --name formal-seed0-lrs_fdr_bpdd_fia-v1 \
  --dry-run
```

验收：

- [ ] 三个 pending-arm authority JSON 均存在；
- [ ] source commit 完全相同；
- [ ] dataset/initial-state 签名完全相同；
- [ ] 除 arm、配置 SHA 和模块私有字段外，训练设置完全相同；
- [ ] `exist_ok=false`；
- [ ] 没有创建伪造的训练 epoch 记录。

## 7. Task 2：Formal100 训练

单卡默认串行执行 g/h/i，避免显存竞争和吞吐变化。冻结的既有 LRS-FDR control
不在此 launcher 的 pending list 中；若作者决定重训 control，另行使用
`scripts/train_lrs_fdr.py` 的 `--dataset-root`、`--initial-state`、`--output-root`、
`--name`（可选 `--dry-run`）接口并保存独立 authority。

```bash
cd "$REPO_ROOT"

python scripts/train_visdrone_lrs_system.py \
  --arm g \
  --dataset-root "$VISDRONE_ROOT" \
  --initial-state "$INITIAL_STATE" \
  --output-root "$RUN_ROOT" \
  --name formal-seed0-lrs_fdr_bpdd-v1

python scripts/train_visdrone_lrs_system.py \
  --arm h \
  --dataset-root "$VISDRONE_ROOT" \
  --initial-state "$INITIAL_STATE" \
  --output-root "$RUN_ROOT" \
  --name formal-seed0-lrs_fdr_fia-v1

python scripts/train_visdrone_lrs_system.py \
  --arm i \
  --dataset-root "$VISDRONE_ROOT" \
  --initial-state "$INITIAL_STATE" \
  --output-root "$RUN_ROOT" \
  --name formal-seed0-lrs_fdr_bpdd_fia-v1
```

### 训练监控

每 10 分钟检查一次，不要因暂时低于对照而中止：

- [ ] 训练进程仍存活；
- [ ] GPU 利用率和显存非零且稳定；
- [ ] `results.csv` epoch 连续增长；
- [ ] train/val loss 和 P/R/AP 均为有限值；
- [ ] BPDD 统计保持有限且 active-edge ratio 不长期为零；
- [ ] FIA 残差缩放参数离开零值且有限；
- [ ] 磁盘至少保留两个 checkpoint 和全部日志的空间；
- [ ] 不自动重试崩溃运行；保留现场、记录错误并交由作者决定。

每个 Formal100 运行的硬超时为 24 小时。超时只用于发现卡死，不代表可以删除运行
目录或从其他臂 checkpoint 接续。

### 每臂必须保留

- `authority/*.json`
- `args.yaml`
- `results.csv`
- 完整 stdout/stderr 日志
- `weights/best.pt`
- `weights/last.pt`
- 模块诊断 JSONL/CSV
- 运行完成清单及全部 SHA-256

## 8. Task 3：Best checkpoint 选择

每个实验臂独立按 `results.csv` 中最大的 val `metrics/mAP50-95(B)` 选 best。禁止：

- 用 AP75 或 Recall 重新挑选；
- 用 test 指标挑选；
- 使用手动判断“后期趋势更好”替代最大 mAP；
- 把其他 epoch 重命名为 `best.pt`；
- 在不同臂使用不同选择标准。

选择记录必须包含：variant、best epoch、best val mAP、checkpoint SHA-256、
results.csv SHA-256 和选择脚本 source commit。

## 9. Task 4：统一 val 复评（论文定稿 gate）

以下是待签入 unified independent evaluator 的冻结参数；它们不是 release launcher 的
训练前置条件：

| 参数 | 值 |
|---|---:|
| split | `val` |
| imgsz | 640 |
| batch | 8 |
| workers | 8 |
| conf | 0.001 |
| max_det | 300 |
| nms | false |
| half | false |
| cache | false |
| rect | false |
| prediction passes | 1 / checkpoint |

release 当前不能执行该 independent evaluation。gate 签入后，每个 JSON 必须同时包含：

- Overall：Precision、Recall、F1、AP50、AP75、mAP50-95；
- Scale：Tiny、Small、Medium、Large 的 GT/AP50/AP75/mAP；
- Class：十类别的 class ID/AP50/AP75/mAP；
- Identity：checkpoint path/SHA、variant、source commit、dataset signature；
- Protocol：全部冻结评估参数和 prediction pass 数量。

## 10. Task 5：统一 test 复评（论文定稿 gate）

只有 unified independent evaluator 签入并完成 val gate 后，才运行 test。当前 release
不提供该 evaluator，因此本任务保持 pending，不得伪造命令或 JSON。test 仍必须使用
val 冻结后的 best checkpoint，且 AP75、逐类/逐尺度结果和 identity/protocol checks
必须由同一签入 evaluator 生成。

当前仓库的 test 口径是本地 held-out，**不是 VisDrone 官方 challenge server**。
论文和材料必须明确写出这一点；若未来提交官方服务器，单独登记官方结果，不能覆盖
本地 held-out 文件。

## 11. Task 6：结果比较与判定（论文定稿 gate）

unified comparator 尚未签入 release。定稿 gate 必须在 evaluator 之后提供，并验证
评估协议、数据签名、source commit 和 split 一致后才计算差值；在此之前不生成 G/H/I
的 AP75、逐类/逐尺度 comparison JSON/CSV，也不将其结果写入 Formal100 主表。

### 科学结果等级

| 单种子 ΔmAP | 标签 | 允许表述 |
|---:|---|---|
| `≤0 pp` | FAIL | 不支持正增益 |
| `(0,+0.1) pp` | WEAK_POSITIVE | 数值非负/极弱正向，不写显著 |
| `[+0.1,+0.2) pp` | SMALL_POSITIVE | 小幅正增益 |
| `≥+0.2 pp` | CLEAR_POSITIVE | 清晰单种子正增益，仍不等于统计显著 |

最低投稿门：

- [ ] `lrs_fdr_bpdd − lrs_fdr` 的 val mAP 大于零；
- [ ] `lrs_fdr_fia − lrs_fdr` 的 val mAP 大于零；
- [ ] `full − lrs_fdr` 的 val mAP 大于零；
- [ ] Full 相对 RT-DETR-L baseline 明确为正；
- [ ] Full 没有未解释的 AP75/Recall 严重退化；
- [ ] 所有负向类别或尺度都在结果页如实保留。

理想门：Full 同时高于 `lrs_fdr_bpdd` 和 `lrs_fdr_fia`。若不满足，不得声称三个模块
可加性成立；仍可按真实结果决定是否采用二模块最终系统。

## 12. Task 7：复杂度与实时性

至少比较 RT-DETR-L、LRS-FDR、LRS-FDR+BPDD、LRS-FDR+FIA、Full，并固定：

- 同一 GPU；
- `imgsz=640`；
- batch 1；
- FP32；
- 相同 warm-up 与计时次数；
- 同一进程环境；
- 记录 CUDA、PyTorch、驱动和 GPU 型号。

必须输出 Params、GFLOPs、峰值显存、median/p90 latency 和 FPS。BPDD 臂的推理
参数、GFLOPs和分支必须与 LRS-FDR 相同；Full 的新增推理开销只能来自 FIA。

## 13. Task 8：材料发布

实验完成后按实际完成日期生成新目录，不覆盖 `lrs_fdr_formal100_20260828`：

```bash
export EVIDENCE_DATE="$(date +%Y%m%d)"
export EVIDENCE_DIR="paper_material/evidence/visdrone_lrs_system_formal100_${EVIDENCE_DATE}"
test ! -e "$EVIDENCE_DIR"
mkdir -p "$EVIDENCE_DIR"/{authority,training,evaluation,complexity}
```

```text
$EVIDENCE_DIR/
  README.md
  MANIFEST.sha256
  authority/
  training/
  evaluation/
  complexity/
```

发布必须同时更新：

- `paper_material/evidence/source_manifest.json`
- `paper_material/CURRENT_RERUN_STATUS_ZH.md`
- `paper_material/results/RESULTS_ZH.md`
- `paper_material/writing/ICASSP2027_OUTLINE_ZH.md`
- `paper_material/figures/FIGURE_PLAN_ZH.md`

旧 AP-FDR+BPDD/FIA checkpoint 保持旧名称；只有本计划产生的新 checkpoint 才能写成
LRS-FDR+BPDD、LRS-FDR+FIA 或 Full。

## 14. 完成定义

只有以下全部满足才可将本交接标记为完成：

- [ ] release 中三个组合配置、launcher、模型源文件和 source tests 已核验；
- [ ] Gate 0 全部通过；
- [ ] 选定矩阵的 Formal100 全部完成且 epoch 连续；
- [ ] g/h/i best 选择规则一致；
- [ ] unified independent evaluator/comparator 签入并完成 val 复评（论文定稿 gate）；
- [ ] evaluator 签入后 test 在 val 冻结后一次性完成；
- [ ] Overall/Scale/Class 三层结果完整；
- [ ] 六个规定方向差值全部生成；
- [ ] 复杂度与实时性完成；
- [ ] authority、日志、checkpoint SHA 和证据 manifest 完整；
- [ ] 材料仓库只使用新的规范方法名，没有重命名旧证据；
- [ ] 论文结果页明确单 seed、单数据集与本地 held-out 边界。

## 15. 失败处理

- 工程失败：保留运行目录、stdout/stderr、最后 checkpoint 和 authority；不静默重试。
- 磁盘不足：先停止启动下一臂，不删除当前或既有关键证据。
- 单臂科学结果为负：仍完成其统一评估和归档，不调整 best 选择规则追正结果。
- Full 未超过两个二模块臂：不伪造可加性，交由作者决定使用最佳二模块系统还是保留
  Full 作为兼容性结果。
- 协议或 hash 不一致：该比较标成 `NON_STRICT`，不得进入严格消融主表。

本文件是执行合同，不是结果文件。任何新数值都必须来自冻结评估 JSON；不得手工把
训练终端中的近似值填成正式结果。

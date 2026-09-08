# LRS-GFDR 运行代码交接

材料仓保存协议、配置和结果证据；可直接部署的运行时实现仍以代码仓 `uav-detection-baselines` 的冻结提交为准：

- 仓库：<https://github.com/kkc236/uav-detection-baselines>
- 冻结提交：`1db154cc`（`codex/bpdd-decoded-iou-candidate`）
- 配置：`configs/rtdetr-l-lrs-gfdr.yaml`、`configs/rtdetr-l-lrs-gfdr-fia.yaml`、`configs/rtdetr-l-lrs-fdr-bpdd.yaml`
- 核心实现：`src/rtdetr_lrs_system.py`、`src/fdr_head.py`、`src/fdr_math.py`、`src/fdr_loss.py`、`src/rtdetr_fdr.py`、`src/rtdetr_fdr_bpdd.py`
- 启动脚本：`scripts/train_lrs_gfdr.py`、`scripts/train_visdrone_lrs_system.py`

本材料仓新增的 `configs/rtdetr-l-lrs-gfdr-bpdd.yaml` 是显式几何开关版本，便于他人复现封装后的命名。两仓之间以配置内容和提交号核对，不上传 `.pt`、数据集或服务器凭据。


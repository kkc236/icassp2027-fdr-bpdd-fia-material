# BPDD Capacity v2：实测版本说明

## Material Passport

- Origin: VisDrone Formal100 seed0 远端训练
- Version: `bpdd-capacity-v2`
- Verification status: `VERIFIED-RUN / VALID-VAL-EVIDENCE`
- Scope: `LRS-GFDR + capacity-v2 AC-BPDD`
- Evidence: [Formal100 evidence bundle](../evidence/bpdd_capacity_v2_formal100_20260910/)
- Boundary: 本页是补充实验记录，不替换材料仓当前主路线，也不包含 FIA。

## 方法边界

该版本把 BPDD 扩展为“独立局部精修教师 + 质量门控蒸馏”：保留 LRS-GFDR 的六层逐边分布和可行几何解码，在 P2/P3/P4 局部特征上增加独立精修分支，再用固定末层 assignment、共同支持检查和解码框 IoU 门控进行 BPDD。教师输出停止梯度；DN queries 不进入局部精修和蒸馏。

这是一个增容版本，不能继续沿用旧 BPDD 的“零推理参数/零推理开销”表述。当前模型摘要为 34,119,764 参数、130.2 GFLOPs；新增容量来自局部精修专家，而不是把新增收益全部归因于 BPDD。

## 固定协议

- 数据：VisDrone，远端 authority 数据文件
- 输入/训练：640、batch 8、100 epochs、seed 0、确定性、AMP、MuSGD、`pretrained=false`
- LRS 收缩系数：`alpha=0.25`
- BPDD：定位权重 `0.15`、分类权重 `0.10`，warm-up 10–20 epochs；配置见证据目录中的 YAML
- 初始状态 SHA-256：`935D68428BFC5848DE51F82844658ABBC7EC8C99CBBF6BBF823166D38CB65D5B`

## 可复核来源

训练使用的远端源码树提交为 `4fd54d2e926b93107304a9ba51ba66edd7d75c99`；对应公共开发分支基线为 `codex/bpdd-capacity-v1` 的 `0ec7f48987dfe91b335f1750a420468c9ee08621`。由于远端部署树含有部署时生成的提交，完整源文件不在本证据包中；`source_manifest.json` 记录了远端各文件 SHA-256，避免把未绑定的本地草稿冒充训练源码。

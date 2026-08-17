# ACR-BPDD 本地设计交接

## 当前结论

ACR-BPDD 已完成本地结构设计、实现和 CPU 侧定向回归，但尚未在本会话连接服务器或启动训练。下一会话必须先在目标 RTX 4090 执行真实 CUDA preflight，通过后才允许启动 Formal100。

该候选只改训练期 BPDD 监督：

1. 用带 `0.5N` 下限的 reliability-mass 重归一化，修复 BPDD v1 有效边约 52.17% 时的梯度稀释；
2. 对六层 FDR 分布回归头执行 detached input replay，使 BPDD 梯度只进入 `dec_bbox_head`；
3. eval 和部署图仍是普通 FDR，参数量、GFLOPs 和推理逻辑不变；
4. 独立 YAML 保留旧 BPDD/FDR 路径，便于消融与回退。

## 关键文件

- 模型与损失：`src/rtdetr_fdr_acr_bpdd.py`、`src/bpdd_loss.py`
- detached replay：`src/acr_bpdd_replay.py`
- 模型 YAML：`configs/rtdetr-l-fdr-acr-bpdd.yaml`
- 协议：`src/acr_bpdd_protocol.py`
- 协议生成：`scripts/prepare_acr_bpdd_protocol.py`
- RTX4090 门禁：`scripts/run_acr_bpdd_cuda_preflight.py`
- Formal100 入口：`scripts/train_rtdetr_acr_bpdd.py`
- 方法和实验说明：`docs/ACR_BPDD_DESIGN_AND_RUNBOOK_ZH.md`

## 已验证内容

- 定向回归：`109 passed, 1 skipped`；
- Python 编译检查通过；
- state_dict 和可训练参数集合与 FDR 一致；
- eval 输出逐元素一致；
- BPDD 对共享网络梯度为 `None`，对六个分布头梯度非零且有限；
- 临时 hook 在正常、异常、deepcopy 和 checkpoint 流程中均不残留；
- Formal100 缺少、篡改或 authority 不匹配的 preflight 报告时 fail-closed。

跳过项是 Windows 当前账户无创建 symlink 权限。真实 RTX4090 preflight 是独立强制命令，尚未在本会话执行，不能由 pytest 结果替代。完整历史仓库仍有 25 个与旧 IBER/ITBER 资产、旧 authority 哈希和历史 evidence 有关的既存失败；这些不涉及本候选，但不能宣称全仓库全绿。

## 不可擅自改变的协议

- Ultralytics RT-DETR-L 8.4.90；
- VisDrone train 6471 / val 548 / 10 类；
- seed0、pretrained=False、fresh Formal100；
- imgsz640、batch8、workers8、device0；
- MuSGD、lr0=0.01、momentum=0.937、weight_decay=0.0005；
- AMP=True、固定 scale128；
- 300 Query、max_det=300、NMS=False；
- FDR 初始状态 SHA256：`51AAB2EB3FB7D123501C69C7B8DC90FF3EA0B9344A108EDEEF2C7D6DCDBB742D`；
- ACR：weight=0.5、temperature=0.5、margin=0.02、reliability_floor=0.5；
- `include_dn=false`，BPDD 不监督 DN Query；
- 现阶段比较必须写为 `preliminary_cross_run / strict_paired=false`。

## 服务器执行门

1. 使用最终 clean commit 生成 protocol manifest；
2. 运行 `run_acr_bpdd_cuda_preflight.py`；
3. 确认报告 status=passed，且 replay error ≤1e-6、loss_bpdd>0、共享 BPDD 梯度数为0、分布头非零梯度数>0；
4. 将同一 preflight report 传给 Formal100 dry-run；
5. dry-run 通过后 fresh 启动100轮，逐 epoch 保存并非阻塞上传；
6. 若工程失败，仅从经过验证的 last checkpoint 续跑到新的不可变 run；不得覆盖旧证据；
7. 100轮后做独立 val/test、尺度/类别、开销、SHA256 和尾轮稳定性评估。

## 科学判定

相对成熟 FDR，至少要求 mAP 与 AP75 正向，并重点确认 BPDD v1 的 Recall 下降是否被缓解。若要替换 BPDD v1 作为论文版本，应超过 BPDD v1 mAP，或在相近 mAP 下给出显著更好的 Recall/Precision 平衡。最终论文仍需同批次重跑严格 FDR 对照。

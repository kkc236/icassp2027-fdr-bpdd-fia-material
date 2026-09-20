# D-FINE-L 训练批大小：作者补充与措辞审查

## 来源与范围

作者在本轮对话直接确认：D-FINE-L 在 RTX 4090 24 GB 条件下以 batch=8 训练时发生显存不足，因此调整为 batch=4。结构审读代理独立审查了拟加入的英文句子，确认需限定为本文的训练配置，并明确说 physical batch size。

本轮没有重新训练、测试显存上限、访问关闭的服务器或取得新的 OOM 日志。该事实的依据是作者陈述，记录于 inputs/dfine_batch_memory_note.json。

## 正文修改

位置：实验协议 4.1 中 D-FINE-L 的具体训练配置之后。

> Under our D-FINE-L training setup, a physical batch size of eight caused an out-of-memory error on an RTX 4090 with 24 GB of GPU memory; we therefore reduced the physical batch size to four.

该句解释此次物理批大小由 8 降至 4 的实际原因。原文关于 FP32、无梯度累积、effective batch=4，以及与 Full 的优化器、精度、有效 batch 和增强差异均保留。没有将本次 OOM 扩大为所有 D-FINE-L 配置的显存限制，也没有用它声称两种训练配方已受控一致。

模型精度、GFLOPs、参数量和 batch=8 推理效率均不修改。训练显存不足与已有批量推理测速属于不同操作。

## 验收

新增句子、作者来源记录与原有训练差异说明由 verify.py 检查。PDF、单文件 LaTeX 和作者 ZIP 同步更新，最终页数、哈希及视觉检查见 verification.json、EDITORIAL_CHECKS.json 和 RELEASE_METADATA.json。


最终 PDF SHA256：`34ce92ef651a6a8c6e226d3c285011a9119dff7a6f1f711450c9f081f32edb54`。

实际重新查看第 8–11 页：新增 OOM 说明完整可读；后续表格、图 6、正文、结论与参考文献无重叠、裁切或标题孤置。其余八页 PNG 与上一已验收版本逐字节一致。全部 12 页通过。

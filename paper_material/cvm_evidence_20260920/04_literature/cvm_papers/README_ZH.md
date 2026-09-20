# CVM 视觉论文阅读包（2025–2026）

整理日期：2026-09-17。共 6 篇，均由 CVM 官方会议日程链接至公开 PDF；文件保留官网版本。

选文依据：优先与你的航拍小目标检测、RT-DETR 改进和实验组织相关的论文，再补充遥感分割及三维重建作为写作参考。

## 优先阅读：航拍与小目标检测

| 顺序 | 论文 | 年份 | 适合关注的内容 |
|---|---|---|---|
| 1 | [LME-DETR](01_LME-DETR_CVM2026.pdf) | CVM 2026 | 轻量化 DETR、跨尺度特征和损失设计；观察精度与计算成本如何一起呈现。 |
| 2 | [SD-Net](02_SD-Net_CVM2026.pdf) | CVM 2026 | 航拍小目标检测；观察多模块方法的动机、组件消融与检测结果。 |
| 3 | [FGHDet](03_FGHDet_CVM2025.pdf) | CVM 2025 | 无人机检测中的细粒度特征与检测头选择；观察模块作用与成本的比较。 |
| 4 | [DASSF](04_DASSF_CVM2025.pdf) | CVM 2025 | 多尺度融合；观察模块组合、上采样替换和跨模型实验的分工。 |

## 扩展阅读：其他视觉任务

| 顺序 | 论文 | 年份 | 适合关注的内容 |
|---|---|---|---|
| 5 | [BiCoR-Seg](05_BiCoR-Seg_CVM2026.pdf) | CVM 2026 | 高分辨率遥感分割；观察特征交互、分层监督、效率与可视化的组织。 |
| 6 | [TexHOI](06_TexHOI_CVM2025.pdf) | CVM 2025 | 单目手物交互场景的三维纹理重建；观察基线比较、针对性消融、失败案例与局限。 |

## 完整题名与官方来源

1. **LME-DETR: Lightweight and Multi-Scale Feature-Enhanced End-to-End Object Detection for Aerial Images**  
   [官方 PDF](https://iccvm.org/2026/files/papers/265.pdf)
2. **SD-Net: Synergistic and Dynamic Learning for Small Object Detection in Aerial Images**  
   [官方 PDF](https://iccvm.org/2026/files/papers/691.pdf)
3. **FGHDet: Delving Into Fine-grained Features With Head Selection for UAV Object Detection**  
   [官方 PDF](https://iccvm.org/2025/papers/s8p2-368-jcst.pdf)
4. **DASSF: Dynamic-Attention Scale-Sequence Fusion for Aerial Object Detection**  
   [官方 PDF](https://iccvm.org/2025/papers/lncs/813.pdf)
5. **BiCoR-Seg: Bidirectional Co-Refinement Framework for High-Resolution Remote Sensing Image Segmentation**  
   [官方 PDF](https://iccvm.org/2026/files/papers/301.pdf)
6. **TexHOI: Reconstructing Textures of 3D Unknown Objects in Monocular Hand-Object Interaction Scenes**  
   [官方 PDF](https://iccvm.org/2025/papers/s1p4-592-tvcg.pdf)

会议日程：[CVM 2026](https://iccvm.org/2026/program.htm)、[CVM 2025](https://iccvm.org/2025/program.htm)。

这些是会议官网提供的不同发表路线版本，页数和版式不一定一致；投稿页数仍以目标年度的投稿说明为准。

## 对照自己的论文时，建议记录四件事

- 实验以完整系统结果还是组件分析开场，各部分分别回答什么问题。
- 消融表每一行改变什么，以及正文是否只解释关键差值。
- 精度、参数量、计算量和实测速度是否使用清楚的测试条件。
- 哪些机制图留在主文，哪些实现细节进入附录，定性结果如何支持结论。

`sources.json` 记录各 PDF 的来源链接、实际页数、文件大小、SHA-256 和获取方式。前四篇复用工作区已有官网文件；其余两篇本次从官网获取。

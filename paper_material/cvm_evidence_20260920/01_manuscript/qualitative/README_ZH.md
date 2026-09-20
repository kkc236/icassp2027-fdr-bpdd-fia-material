# 作者可选工具：将来的真实定性图

**本版论文按作者决定不包含逐图预测案例。这里保留可选的未来工具，不是本版待完成任务。** 当前 Full 与 D-FINE 的两份真实逐图预测缓存未在本地取得；未用报告中的汇总指标冒充预测，也未进行模型推理或训练。

## 已核验的素材与版本

- 验证集原图：工作区 `datasets/VisDrone/images/val`，548 张。`image_manifest.json` 保存逐图内容哈希；脚本同时核对哈希与尺寸。
- 项目转换 GT：`gt_reconstructed/instances_val.json`。该文件由归档转换脚本从本地图像与 YOLO 标签生成，SHA256 与服务器既有评估记录完全一致：`92d2866fe6e6ff4c3101b82c01b7718eb78b3759399042c4501d893798fc8bfa`，含 548 图、38,759 个目标。小包可包含其无损 gzip；首次使用会解压并校验。
- 这份 GT 是项目 YOLO 派生版本，不等同于 VisDrone 官方 ignore-region 评估协议。
- 预测框必须是原图像素 `bbox_xyxy`，不能再次执行 letterbox 逆变换。类别为 0–9，顺序是 pedestrian、people、bicycle、car、van、truck、tricycle、awning-tricycle、bus、motor。

未来使用需要两份**已经生成过的 final-val 缓存**。在取得之前，工具不会生成科研定性案例。

| 文件 | 对应权重 | 已记录 SHA256 |
|---|---|---|
| `dfine_final_val.jsonl` | D-FINE-L `last_evaluated.pth` | `9f2892072bfc5b60991f8d0543664ffca177e492a3c01304a4ee5de3a8dbf51c` |
| `joint_final_val.jsonl` | Full `last.pt` | `d946fc4fff304873707ea558f9b702644873f1a7c7b00496fb9512ca74783d72` |

历史远程目录记录为 `/root/sj-tmp/eval/visdrone_dfine_bs4_results_20260914/`；服务器关闭时不能把记录中的路径宣称为当前已访问验证的文件。final 与论文外部主表一致，不将 best 混入 final 对照。原始版本记录在 `asset_manifest.json`。

## 未来选择使用时的步骤

依赖 Python 和 Pillow。脚本只读已有缓存、图像及 GT，没有网络调用或模型加载。

将两份 JSONL 放入本目录 `raw/`，执行：

```powershell
python prepare_qualitative.py rank --images "实际的 datasets/VisDrone/images/val 路径"
```

若本目录仍位于含 `datasets/VisDrone/images/val` 的工作区中，可省略 `--images`。脚本从自身位置向父目录查找，不依赖固定目录深度；独立解压小包时请显式指定原图位置。默认还读取同目录的 `image_manifest.json`，可用 `--image-manifest` 指定其位置。

排序会生成候选清单和逐图诊断。固定 score ≥ 0.25、同类 IoU ≥ 0.50，按置信度降序一对一匹配；这是选图诊断，**不是 COCO AP 评估**。原始输入的内容哈希、类别映射、图像覆盖、原图尺寸全部通过后才执行。

人工审阅候选图及原始 VisDrone 标注后，保存 `selection.json`：`examples` 每项包含真实 `image_id`、整数像素 `crop_xyxy`、`label`、`show_labels`。例如只规定结构而不预设任何真实案例：

```json
{"examples": []}
```

以上空结构是说明模板，直接渲染会明确报错；不要把它当作完成了定性图。确定真实案例后执行：

```powershell
python prepare_qualitative.py render --selection selection.json --images "实际的验证集原图目录"
```

输出三栏 PNG、合并 PNG/PDF 和 `render_manifest.json`。绿色为 GT，青色为匹配预测，粉色为未匹配预测，虚线黄色为漏检 GT。GT / D-FINE / Full 使用同一整数裁剪和固定阈值，显示所有保留预测。高置信度框后绘制、重复框使用不同描边宽度、标签避让，减轻完全重合造成的误读。

匹配在**整张原图**上执行，裁剪仅改变视图。图注明确这一点；清单分别记录整图 TP/FP/FN 和裁剪中可见的目标/预测索引，不能把整图计数当作裁剪计数。跨出裁剪的框自然裁切，图像缩放不改变其原始匹配状态。选择文件、输出图和输入图都记录内容哈希。

用于论文时应同时展示改善和不足，并说明是选定的说明案例，不能把候选排序解释成改善发生频率，也不能只保留对本方法有利的框。

## 单文件 TeX 与验证边界

`source/qualitative/embed_raster.py` 可将真实完成的 RGB 栅格图以内嵌 PDF XObject 方式写入 ASCII TeX。Flate 路径保留每个像素，分条避免大型 TeX 参数；编译不需要外部图片或 shell escape。JPEG 路径会明确记录是否有损，分别保存输入像素和实际编码后像素的哈希。

本次可选工具修复使用了**明确标为 SYNTHETIC 的绘图/格式边界测试**，验证重复框、错类、阈值边界、非法裁剪、图像内容替换拒绝，以及单文件 TeX 的色块方向、跨条连续性、多图资源隔离和透明底色。测试不导入模型。`SYNTHETIC_QA_REPORT.json` 只证明这些软件行为；不证明真实预测已排序或渲染。人工也查看了测试绘图及测试 PDF 的渲染页。

如需复跑可选 QA：`python test_synthetic_workflow.py`，额外依赖 pypdf、pypdfium2 和可用的 `pdflatex`（可用环境变量 `PDFLATEX` 指定路径）。所有测试输出进入 `synthetic_qa_NOT_PAPER_EVIDENCE/`；不得将该目录中的图片或虚构坐标加入论文。

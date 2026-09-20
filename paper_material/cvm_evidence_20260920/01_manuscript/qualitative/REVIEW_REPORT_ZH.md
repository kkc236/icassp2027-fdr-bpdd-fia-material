# 可选定性图工具独立复核

本版按作者决定排除逐图预测案例。所有修改仅发生在本目录；未修改主稿，未访问服务器，未执行模型训练/推理。

## 实质性修复

1. **图像内容身份**：原脚本仅核对尺寸，替换成同尺寸图片仍会通过。现在逐张核对已归档 image_manifest.json 中的 SHA256。
2. **裁剪坐标一致性**：Pillow 会对小数 crop 隐式取整，原框坐标却减去未取整值。现在只接受整数像素边界，并按实际缩放后的宽高分别缩放坐标。
3. **完成状态**：原脚本接受空 examples 并输出 0 例。现在拒绝空选择，避免假完成。
4. **裁剪解释**：整图匹配与裁剪显示可能不一致。图下注明匹配范围，清单独立记录可见 GT、预测、漏检，避免拿整图数字解释裁剪。
5. **重合框与标签**：低分重复框原先可能遮住高分正确框；错类框可能完全遮住漏检 GT。现在调整绘制顺序、描边宽度、漏检虚线层级和标签避让，并对右边界标签钳位。
6. **路径可移植性**：移除硬编码 parents[2] 深度，从自身目录逐层寻找数据集；独立分发时明确要求 --images。
7. **输入规范化与溯源**：整数值浮点类别规范为 int，拒绝 bool 类别；记录选择清单和输出图哈希；拒绝 GT 重复图像 stem。
8. **JPEG 内嵌元数据**：原 rgb_sha256 对重新压缩 JPEG 指向编码前像素，无法核对最终 XObject。现在它指向编码后解码像素，另外保存 input_rgb_sha256；Flate 仍逐像素无损。

## 验证

test_synthetic_workflow.py 创建显式 SYNTHETIC 的坐标和图像，仅用于软件边界 QA。14 项检查通过；同一测试验证两张图的独立 PDF 资源、RGB 四象限真实方向、跨多个条带的位置、RGBA 白底合成、无 shell escape 单文件编译。测试图和 PDF 渲染页已人工查看，示例含醒目 synthetic 标识，PDF 只含测试色块。没有将任何测试数据放入科研主稿。

原有固定 GT/预测 SHA256、score 0.25 / IoU 0.50、原图坐标和 0–9 类别合同保持不变。真实两份 JSONL 未取得，因此没有宣称真实预测全流程已跑通。

## 集成建议

- prepare_qualitative.py、README_ZH.md、REVIEW_REPORT_ZH.md、test_synthetic_workflow.py 放入新版 qualitative/。
- embed_raster.py 放入新版 source/qualitative/。
- image_manifest.json 保留原已归档文件；本目录副本内容未修改。
- SYNTHETIC_QA_REPORT.json 可放进 qualitative/ 作为作者工具检查记录。整个 synthetic_qa_NOT_PAPER_EVIDENCE/ 无需进投稿包。
- 不向 main.tex / PDF 增加定性案例或 synthetic 图，也不把此工具描述成当前缺失工作。

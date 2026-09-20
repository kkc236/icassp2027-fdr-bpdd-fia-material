# 改名终审：术语及第 7–12 页视觉核查

日期：2026-09-17。范围：`source/body.tex`、`figures/overview.tikz`、`figures/lrs.tikz` 的命名、定义与归属；逐页通过 `view_image` 打开并实际查看 `qa/pages/page-07.png` 至 `page-12.png`。未用 OCR 代替视觉检查，未修改稿件。第 1–6 页由主任务独立核查。

## 必要修复

**未发现必要修复；本次范围内无 P1 / P2 问题。**

## 术语核查

- **GCDL** 在摘要 `body.tex:2` 首次展开为 `Geometry-Constrained Distributional Localization`；正文 `:16` 再次展开，并明确包含 incoming-reference / supervision-path redesign、geometry-feasible decoding、LQS 三部分。名称没有把整个核心缩成几何算子。
- **LQS** 在摘要 `:2` 和正文 `:16` 展开为 `layerwise quality shrinkage`。`:88–108` 将 quality 明确定义为 detached matched-box IoU，并说明收缩的是 loss weights、分组局限于同图同层、末层恢复原权重；与现有公式一致。
- **D-FINE 归属保留**：`:36` 归属 discrete representation、nonuniform support、integral decoding、cumulative refinement、FGL；`:55–60` 对分布公式注明 Following D-FINE；`:69` 明确 fixed frame follows FDR；`:39` 保留 D-FINE GO-LSD 身份。没有因改名将这些继承机制归入新发明。
- **作者路径边界保留**：`:69` 说明 incoming reference 同时用于解码与 FGL targets，关闭额外 preliminary / DN-FDR 监督但保留 stock DN，且没有删除 preliminary prediction head。
- `overview.tikz:13–20` 使用 GCDL、FGL with LQS，并明确 LQS 为训练监督；`:60` 将核心与 expert / shared P3 extension 分开。主任务为第 4 页版式把第 17 行 `(training only)` 缩短为 `(train)`，本次已读取并确认此标签仍准确，且第 20 行保留完整的 during training 说明。`lrs.tikz:9、25、42–45` 的 LQS、均值收缩算例、适用对象与正文一致。
- 旧文件名 `lrs.tikz`、内部节点 `(lrs)`、交叉引用标识 `fig:lrs` / `eq:lrs` 不作为读者可见方法名输出；无需为此次展示改名而改动这些内部标识。

## 第 7–12 页实际视觉结果

| 页 | 实际所见与结果 |
| --- | --- |
| 7 | 选择规则 Eqs. (8)–(10)、总目标 Eq. (11) 清晰；“FGL with LQS”显示完整；公式号、双栏正文和页边行号没有相互侵占；通过。 |
| 8 | Figure 5 的步骤、箭头、公式、训练说明及 caption 均可辨认；新标题“4.2. GCDL: design and geometric validity”保持完整单行，后接足量正文，无严重孤立标题；通过。 |
| 9 | GCDL、LQS 在版本结果、数值性质与成本段落中显示正常；节标题与段落间距合理，未见重叠或裁切；通过。 |
| 10 | Tables 2–4 完整。Table 2 的 LQS 列、GCDL 行、角色分组和最高值粗体清楚；Table 3 的 G: GCDL 定义及成本列对齐正常；通过。 |
| 11 | Figure 6 的类别、两组数值、差值条形及图注清楚；Tables 5–6 可读；GCDL 结论段与 Scope 段未发生挤压、遮挡或页末裁切；通过。 |
| 12 | Table 7、附录标题与正文、References 标题及参考文献 [1]–[19] 均完整；长 DOI 正常折行，未见跨栏、重叠或裁切；通过。 |

正文中的正常词内断行不构成必要修复。本轮改名未在已查看页面引入严重孤立标题、不可读标签或内容遮挡。

## 文件身份

最终 PDF：`MANUSCRIPT_CVM.pdf`，12 页。实际计算 SHA256 与主任务提供值一致：

`10e43284ae637ae613dce0cc029486dcf8ba0052ad87a16b74426519f3af5067`

首次逐页视觉核查所对应 PDF SHA256 为 `c1af6d4b305f904037d0efa2949948888da3d5e1a4caa0bcf26cf8f3e7d61de8`。随后主任务仅缩短 overview 的训练标签，生成上述最终 PDF。正文与 `lrs.tikz` 哈希未变；第 7–12 页重新核对的 PNG 哈希均与已实际查看的图像相同，沿用本轮视觉结论。第 4 页修复与视觉确认由主任务负责，本报告不冒充已审该页。

| 所审源文件 | SHA256 |
| --- | --- |
| `source/body.tex` | `6cb7a152e64d23eccfebb04c4b7bc79f328346a26c07f14a2c07effe44930576` |
| `figures/overview.tikz` | `7b6194ccd90ba159781d5dd1a04dcc6eec140a0c44516d49682bb15643d3f72f` |
| `figures/lrs.tikz` | `9b1ca10659236a86c86b423b9deac28b484ac0c4c2ce6d0cfaed8cff4c5e7d55` |

| 实际查看 PNG | SHA256 |
| --- | --- |
| `qa/pages/page-07.png` | `d2dbd54422c3e0a04f73d5fb1110a425ed22045bea04a769ef57a6f1bca0a940` |
| `qa/pages/page-08.png` | `b33d353f6923e95140c63ba2a2f7867bc8337b6947012a73a4c79ac46e3a7a9a` |
| `qa/pages/page-09.png` | `c1ec992260891c1cc5e2be48e83927ed51b7186f083f9091cf2c8c0f2417b977` |
| `qa/pages/page-10.png` | `99f43cb73226733004745206123802c957dce407316e4f06ae875507c3ac29c8` |
| `qa/pages/page-11.png` | `b10114c7d442fb850cb35ad2a19de38640e2ff6385fe19642fd400e269f02418` |
| `qa/pages/page-12.png` | `3e3c9b46350a599120325de2e5d7dae2382c540e797ef8823f3760fd28f4d0f0` |

以上路径相对 `output/cvm_naming_revision_20260917/`。本结论限于所列文件和页面，不代替第 1–6 页视觉核查。

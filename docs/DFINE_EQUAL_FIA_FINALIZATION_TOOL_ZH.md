# D-FINE-S + EQuAL + FIA 最终证据收尾工具

## 用途与边界

`tools/prepare_dfine_equal_fia_finalization.py` 只处理已经从服务器拉到本地的完整证据。它不会连接服务器、启动训练或评测、修改现有材料、执行 Git 操作，也不会上传 GitHub。工具复用 `tools/generate_dfine_equal_fia_matched_results.py` 的 DF-0/DF-1 指标生成逻辑，不维护第二套结果公式。

工具在写出任何文件前完成以下门禁：

- `postrun_status.json` 必须为 `status=complete`，并严格包含 treatment val、treatment test、control val、control test 四项；
- 两臂必须各自证明 132 个 epoch、best-val 选择、checkpoint epoch/stage、一致的 checkpoint SHA-256/字节数和可恢复 EMA；
- 四项评测均须返回 0、使用各自同一个 best checkpoint，并保留 `--use-amp --seed 0 --test-only`；
- 本地 `evaluation.log`、`evaluation_metrics.json`、`eval.pth` 必须与状态文件登记的路径、字节数和 SHA-256 一致；
- 每项必须有 12 个有限 COCO bbox stats，本地指标 JSON 必须与状态文件逐字段相等；
- frozen VisDrone 数据哈希、Formal132 训练协议、COCO evaluator 与指标边界不得漂移；
- source manifest 中同名 source ID 只能不存在或与拟合并记录完全相同。

任何门禁失败都会返回退出码 2，且不生成半成品输出。

## 本地证据布局

拉取目录固定采用以下语义布局；远端绝对路径继续保留在 `postrun_status.json` 中用于绑定，不直接用作本地路径：

```text
pulled-evidence/
├── postrun_status.json
├── runs/
│   ├── treatment/{log.txt,train.log,<selected-best>.pth}
│   └── control/{log.txt,train.log,<selected-best>.pth}
└── evaluations/
    ├── treatment/{val,test}/{evaluation.log,evaluation_metrics.json,eval.pth}
    └── control/{val,test}/{evaluation.log,evaluation_metrics.json,eval.pth}
```

checkpoint 和 `eval.pth` 会被完整读取并校验，但不会列入材料仓库复制计划；它们只进入私密 GitHub Release 资产清单。日志、精确指标 JSON 与 `postrun_status.json` 会进入材料仓库复制计划。

## 命令

```powershell
python tools/prepare_dfine_equal_fia_finalization.py `
  --postrun-status C:\path\to\pulled-evidence\postrun_status.json `
  --evidence-root C:\path\to\pulled-evidence `
  --protocol paper_material\evidence\dfine_s_equal_fia_matched_20260823\protocol.json `
  --material-root paper_material `
  --output-root C:\path\to\new-empty-finalization
```

`postrun_status.json` 必须位于 `evidence-root` 内。`output-root` 必须不存在或为空，工具拒绝覆盖非空目录。

## 输出

收尾包只包含确定性文件：

- `paper_material/evidence/dfine_s_equal_fia_matched_20260823/pair_summary.json`；
- 独立的 D-FINE 匹配结果 JSON 与中文 Markdown，不覆盖旧 A–E、`main_results.json`、`MAIN_TABLE_ZH.md` 或 `RESULTS_ZH.md`；
- `MANIFEST.sha256` 与局部 `* -text` 的 `.gitattributes`，避免 Git 换行转换破坏证据哈希；
- `source_manifest.fragment.json`，合并策略为 `require_absent_or_byte_equivalent`；
- `material_docs.patch`，只建议更新 `CURRENT_RERUN_STATUS_ZH.md` 和 `README_ZH.md`；
- `material_apply_plan.json`，明确小型证据复制、生成文件、source manifest 合并和文档 patch 的目标；
- `github_release_assets.json`，列出 checkpoint、训练日志和四项评测资产的本地路径、建议名称、字节数与 SHA-256，但 `automatic_upload=false`；
- `internal_audit_status.json`，与正式结果隔离保存早期诊断和 claim gate。

工具本身不应用 patch、不合并 source manifest，也不上传 Release。执行这些有状态操作前，应再次核对收尾包、运行材料测试并确认私密仓库目标。

## 内部审计与论文主张门禁

`completed_matched_eval_outcome` 只根据完成后的 matched val/test AP 差值判定：两者均为正才允许 bundle 增益主张；两者均为负则记为 negative；一正一负或含零记为 mixed/zero，并阻止正式增益主张。EQuAL 与 FIA 没有单独消融时，任何 outcome 都不允许拆分到单组件。

当前早期约 `-8.1 pp` 的 treatment 落后、pre-box head 精确全零和 DN-FGL 关闭后的 DDF 异常只进入 `early_training_internal_context`。该字段同时记录只读审计未发现协议、预训练、初始化或 evaluator 错误，但明确设置 `formal_result_use_allowed=false`。这些诊断不得写入正式最终数值、旧 A–E 表或作为未完成训练的结论。

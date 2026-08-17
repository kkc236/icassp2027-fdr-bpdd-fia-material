# FIA Release 结果页覆盖设计

## 目标

恢复 `paper_material/results/FIA_ABLATION_RELEASE_RESULTS_ZH.md`，并用修改后 FIA 的当前有效结果状态完全覆盖旧内容。旧拓扑产生的 FIA-only、FDR+FIA 与三模块数值、截图、哈希和结论不得保留。

## 选定方案

采用原路径直接覆盖。相比新增跳转页或只保留 `FIA_RESULTS_STATUS_ZH.md`，这一方案能维持已有文件入口，同时确保读者不会误读旧 Release 数据。

## 页面内容

- 开头明确声明修改前 FIA 数据全部作废。
- FIA-only 与 FDR+FIA：登记用户报告的新版正增益方向，但在新版可审计资产尚未定位时不填具体数值。
- FDR+BPDD+FIA：登记已核验的正确 P3-only checkpoint best-val 指标：P `0.56996`、R `0.49848`、AP50 `0.48982`、mAP50–95 `0.29618`，AP75 与 test 待补。
- `+0.3922 pp` 只能描述为相对现有 FDR+BPDD val 的算术观察，不得写成严格配对因果增益。
- 页面链接机器可读状态文件 `../evidence/fia_results_status.json`，并将 `FIA_RESULTS_STATUS_ZH.md` 作为一致口径的详细状态页。

## 一致性更新

- 材料完整性测试改为要求旧路径存在且不含撤销数值、旧运行名和旧资产引用。
- README 增加旧路径入口，避免恢复后成为孤立文件。
- 不恢复任何被删除的旧截图、旧 CSV 或旧 evidence JSON。

## 验证标准

1. 两个状态页不存在相互矛盾的指标或证据等级。
2. 旧 FIA 数值与运行标识不出现在恢复页面。
3. Markdown 链接可解析，JSON 可解析。
4. FIA 材料与入口测试全部通过。
5. Git 工作树只包含本次覆盖需要的文件。

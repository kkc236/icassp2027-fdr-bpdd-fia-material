# 四个定位版本的运行有效性：有限证据核查

日期：2026-09-17。只读本地冻结输入、既有证据和 Git 对象；未运行模型、组件测试或服务器命令。收到用户澄清后停止继续深挖，本报告仅汇总已经核实的有限结果，不启动新的全面审计。

## 结论

**现有证据不足以将四个已报告定位运行中的任何一个标为 invalid，或以“致命实现错误”为由排除其精度记录。** 这不等于完成了四个 checkpoint 的全面正确性认证；具体区别如下：

| 历史版本 / 当前角色 | 已核实身份与结果 | 本次有效性判断 |
| --- | --- | --- |
| Original FDR / Transfer reference | `original_fdr_run.json` 绑定 `d97e1eb7f98414752a1c1f38287697db3f2a0679`；100 行 CSV，best epoch 92，AP 29.078。 | 与最终结构不同：preliminary reference 及额外监督开启。未找到足以使该 accuracy 记录无效的、与其运行绑定的致命问题。 |
| Clean-FDR / Path redesign | `clean_fdr_authority.json` 绑定 `ec4e2a463db7a53f7c4c9c4bc9edabdf5c39f40b`；100 行 CSV，best epoch 88，AP 29.696。 | incoming reference、额外监督关闭属于作者有意设计；未采用后续几何规则不等于实现错误。该行最高 AP 不是排除理由。 |
| Clean-FDR + geometry / Path redesign + geometry | `lrs_track_results.md` 绑定运行目录 `visdrone-v2-clean-fdr-geometry-20260908/formal-seed0-clean-fdr-geometry-v1`；100 行 CSV，best epoch 91，AP 29.361。 | AP 较低不能证明实现出错。几何开关源码可追溯到修复后的提交，但本次未找到该运行完整的原始 authority，不能把源码存在直接当作全部执行身份已经认证。这个缺口同样不支持将其判为 invalid。 |
| LRS-GFDR / GCDL core G | `geometry_evidence/historical_training_secondary_summary.json` 与历史审计记录源码为 `c1ac0b25e534f6dc5ba85ade418046a30a51a011`；100 行 CSV，best epoch 92，AP 29.620。 | 该提交已经包含 precision-safe decode，与修复提交的关键源码相同。不能把修复前的合成失败套用于此行。运行绑定部分来自既有二级记录，应保留其证据层级。 |

上述四份 CSV 的 epoch 均为 1–100；本次静态检查其可解析数值没有 NaN/Inf，报告中的 best AP 与对应 epoch 一致。**CSV 数值有限只说明表内记录完整，不证明训练内部从未出现异常，也不证明所有比较都是严格配对。**

## 几何精度修复：能关联到哪里

1. `inputs/geometry_evidence/archived_correctness/red.xml` 的时间为 **2026-09-06 12:14:10 +08:00**。其中 BF16 decoder-wrapper 回归出现零 extent；其他多项失败是新 precision-safe 函数尚不存在的检查。这是本地合成回归，不是四个已报告 checkpoint 的验证失败日志。
2. 同目录 `numerical.xml`（12:16:26）和 `regression-final.xml`（12:46:04）中，同名 BF16 回归通过。已保存的 `geometry_evidence_manifest.json` 明确说明：没有完整 pre-fix 源码清单，也没有相同初始张量的严格配对记录；不能从中推断真实检测失效频率或精度损失。
3. 修复提交 **`f56b210798acab96d628308a5127a2e1399d00dc`** 于 9 月 6 日 12:50:42 创建。GCDL 基座所登记的 **`c1ac0b25...`** 是其后代。本次比较这两个真实 Git 对象，`src/fdr_head.py`、`src/fdr_math.py`、`src/fdr_loss.py` **逐字节相同**。head:324 使用 FP32 incoming reference；:378 关闭 autocast；:380 调用 `decode_feasible_fdr_boxes`。
4. 几何对照开关提交 **`0cc887d6fd420ba8dbcf9b4f65a1633251c37060`**（9 月 8 日）也是 `f56b210` 后代；新增的 `configs/rtdetr-l-clean-fdr-geometry.yaml` 设置 `feasible_geometry: true`。其 math 与修复提交相同，head 保留 FP32 / precision-safe 路径。因此已查源码链不支持“geometry 对照一定用了修复前错误实现”。但缺少该运行完整 authority 时，也不声称已经逐项证明其实际加载状态。

关键源码内容 SHA256：

- `f56b210` 与 `c1ac0b25` 的 `src/fdr_head.py`：`fd7d21a7c1196e2922ab90ad3840ce9ad12d4c96c9fcfc17b06e190abdaa56d6`。
- 两者以及 `0cc887d6` 的 `src/fdr_math.py`：`ac60364c008b048d3dfda619354ce3c1c0e5367b3d8a55de54c49ee43ebebb9a`。
- 三者的 `src/fdr_loss.py`：`b8b43bc92245ff4406cf2a7e240de117b24e03826647a74eadcaafe94518c2a9`。

另须避免字母身份串用：9 月 9 日审计中的历史 **F** 是现在的定位核心 G；该审计中的历史 **G** 是 legacy AC-BPDD，并不是当前 GCDL 核心。旧 AC-BPDD 的公式/监督问题不能凭同一个字母转移到四个定位版本。

## 三类事实应分开

- **与最终结构不同**：参考来源、监督开关、是否启用 geometry / LQS 不同。这决定版本用途与比较边界，不自动使结果失效。
- **实现有错且已有证据**：修复前合成 BF16 回归确有失败。但要否定特定 accuracy 记录，还需要证明错误位于该 checkpoint 的真实训练/评估路径，并足以破坏对应记录的含义；本次没有建立这条链。
- **只是 AP 较低或结果不单调**：V03→V04 的 −0.335 AP、V06 比 V03 低 0.076 AP，都是已记录的结果关系，不是 bug 证据。不能反过来用这些差值证明坏实现。

“未找到完整原始 authority”“后续增加了一个修复”“与最终源码不同”也不能单独当作某运行无效的证明。反之，完成 100 epoch 或几项回归通过，也不能提升成无条件数值正确性证明。

## 与本轮呈现调整的关系

可以按论文问题聚焦主文，将历史四版本完整表和数值修复细节移到附录，压缩重复的限制说明。主文保留 path-only 的较高 AP 及历史比较并非完全同源码/同初始化的简短边界，即可让读者理解整体路径结果而不把正文变成审计记录。

**这属于组织层级调整，不是把不利记录判为无效。** 当前材料不能支持删除某行后宣称所有设计单独涨点、GCDL 是四行最高 AP，或几何对照的较低 AP 已被证实由 bug 引起。

## 本地证据位置

冻结证据前缀：`output/cvm_naming_revision_20260917/inputs/`。

- `original_fdr_run.json`、`clean_fdr_authority.json`、`lrs_comparison_provenance.json`。
- `historical_fdr_results.csv`、`clean_fdr_results.csv`、`geometry_fdr_results.csv`、`lrs_gfdr_results.csv`。
- `lrs_track_results.md`、`historical_geometry_audit_20260909.md`。
- `geometry_evidence/geometry_evidence_manifest.json`、`historical_training_secondary_summary.json`、`raw_manifest_PENDING.json`。
- `geometry_evidence/archived_correctness/{red,numerical,regression-final}.xml`。

Git 对象所在本地仓库：`tmp-work/lrs-system-visdrone-rebuild/`。辅助历史说明：该仓库的 `docs/evidence/VISDRONE_PRIOR_TWO_RESULTS_20260908_ZH.md` 和 `docs/VISDRONE_V2_EXISTING_STATE_HANDOFF_ZH.md`。后者解释了 `935D...` 现有初始化协议与早先 `CA8B...` 计划协议的不同；协议名称不一致不等于已完成运行的 accuracy 自身无效。

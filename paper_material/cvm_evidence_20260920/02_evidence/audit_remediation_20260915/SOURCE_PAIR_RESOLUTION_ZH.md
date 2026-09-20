# V12/V13 源码缺口已补齐：FIA-off/on 配对核验

日期：2026-09-15。仅限 V12=G+B 与 V13=Full；不能自动推广至 Base/G/G+F 或所有内部历史版本。

## 新取得的证据

服务器 `/root/sj-tmp/lrs-v2/bpdd-capacity-v2-fia-code` 仍保留此前本地/远端无法取回的 V12 提交 `5ef57473e89e3b91aa5236a18066aed99f5afc0f`。已只读导出它和 V13 `a43056af2a843ec9bae109d3420367c13f3bcef6` 的 src/configs/scripts，保持原 commit 和原 authority 不变。

每份传输先核验完整压缩包字节数与 SHA-256，再逐文件校验 Git blob ID。校验结果见 [source_pair_comparison.json](source_pair_comparison.json)；原始树与差异清单见 [source-recovery.json](source-recovery.json)。

## 结果

- **239 个共有文件字节一致**，无共有文件修改或删除。
- V12 相对 V13 只新增三个文件：无 FIA 配置、`train_lrs_gfdr_capacity_v3_safe_bpdd.py`、等待联合完成的排队脚本。
- 两臂配置在解析相对图索引、移除 FIA 并恢复后续索引后完全一致；Full 的 P4 绕过 FIA。`-1` 与显式 P3 索引在对应层语义相同，不能当成额外拓扑改动。
- 原始 authority 的数据摘要、初始状态和除运行路径外的训练设置一致；loss 配置、定位 KD、分类 KD 关闭与 warmup/decay 一致。
- 两个启动器复用同一 `FROZEN_SETTINGS`、100 epochs、seed=0 与同一 completed-epoch 回调。Full 使用带 FIA 的初始化映射及 FIA 私有初始化；这些属于 FIA 插入所需的实现，不是隐藏 BPDD 改版。

因此，**此前“V12 源码不可得，无法排除额外代码修改”的保留理由撤回**。现有源码与配置支持该配对是同一 Capacity-v3-Safe 路线上的 FIA-off/on，而不是不同 BPDD 算法的比较。归档名字无需伪造为相同。

运行时初始化重放已通过：复用原 initial-state，994个共有状态张量完全相等；新增19项仅属于FIA，残差系数初始为0。见[动态比较原始JSON](efficiency/v3/initialization_probe.json)和[实际执行脚本](efficiency/v3/measure.py)。这不是重训，也不把静态源码一致自动当作动态通过。单 seed、不同评估器下的小 test 差值和是否普遍泛化仍是不同问题。

## 可引用边界

可报告这个具体配对：val AP-best Full−(G+B)=+0.832 pp，final-val=+1.126 pp。共同 PIL/COCOeval test 为 +0.11793293 pp；原生 validator 另一固定快照为 −0.01857309 pp。按各自协议分别解释，不择一个评估器声称跨口径稳定提升。

不能由本核验推导 KD 的独立因果贡献，不能据此证明其他历史 G/geometry/LRS 对照全部配对，也不能写统计显著。

## 可携带源码

- [Full 固定源码压缩包](source-a43056af2a843ec9bae109d3420367c13f3bcef6.tar.gz)，SHA-256 `039274df02eafdd3ae5aea24c4d6cfab5f872ee590effd98bb98477d3aac1e8f`。
- [BPDD-only 固定源码压缩包](source-5ef57473e89e3b91aa5236a18066aed99f5afc0f.tar.gz)，SHA-256 `5d22be64ec119851dce16715defe2a0abae8713ae62e1e6b5a0da436cf58d6f1`。
- 阅读入口：[Full 模型整合源码](source-a43056a/src/rtdetr_bpdd_capacity_fia.py)、[共享 Capacity 模型](source-a43056a/src/rtdetr_bpdd_capacity.py)、[BPDD-only 启动器](source-5ef5747/scripts/train_lrs_gfdr_capacity_v3_safe_bpdd.py)。

压缩包仅包含声明的源码范围，不含完整 Git 历史、环境安装包、数据集或权重。新窗口可直接读取本材料仓的快照，不必依赖另一个本地工作树。

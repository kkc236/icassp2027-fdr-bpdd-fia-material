# 当前命名审计

GCDL表示整套作者定位设计，LQS仅指其训练权重规则；FDR/FGL/GO-LSD继续采用原始归属。摘要/引言给出全称，图表与正文术语同步。当前独立技术与视觉终审见reviews/NAMING_FINAL_REVIEW_ZH.md，最终文件状态见verification.json。

以下为上一轮实验呈现审计的保留结论；其旧审阅报告适用于对应历史版本。

# 当前对抗性审计结论

本版按“归属准确、实验角色明确、负结果完整、成本可见、口径可恢复”审查。具体逐项处理见 EXPERIMENT_DESIGN_DECISIONS_ZH.md，而不是通过删除结果制造竞争力。

## 已关闭的呈现问题

- Clean-FDR作者身份不明：已改角色分组和展示名，并保存旧alias映射。
- 作者路径改写描述权重不足：摘要、引言贡献、方法和机制表均补齐；技术终审确认未误写成删除preliminary head或stock DN。
- 最终版本并非所有定位变体AP最高却缺选择理由：保留最高行，给出几何/监督性质和完整AP取舍。
- 组件与效率分离：五臂合表，G+F和G+B仍在；+0.832的归因限制明确。
- 外部评价覆盖不完整：附录补齐原计划八格；主终点、截断语义及重复数据限制明确。
- 文献比较似排行榜：明确相近模型规模/小模型参考目的，保留更高AP的BDNet，跨配方不称控制实验。

## 仍有证据边界

1. 单数据集、单seed，不能解释细小差值的统计可靠性。
2. 历史四版本不是已证明全部同源码同初始化的单因素链；不能把+0.542单独归给geometry或LRS。
3. B同时包含专家和训练监督，没有仅关闭KD的匹配训练对照。
4. 外部common evaluator统一评分，不能统一不同optimizer/effective batch/augmentation；OOM仅解释physical batch。
5. converted labels缺完整ignore-region，test此前在开发期间可见；不是官方盲测排名。
6. batch8吞吐量不是单请求延迟或机载部署验证；未虚构实时场景指标。
7. 几何合成压力测试证明有限范围的数值实现性质，不是实测训练失效率或单项AP因果证明。

这些边界主文均保留。当前目标是增强论文可读性和贡献可信度，不给出无法证明的录用保证。

## 审阅记录

当前独立技术终审：reviews/LOCALIZATION_FINAL_REVIEW_ZH.md。
当前实验呈现终审：reviews/EXPERIMENT_PRESENTATION_FINAL_ZH.md。
当前视觉验收：reviews/FINAL_VISUAL_AND_RESOLUTION_ZH.md及reviews/VISUAL_PAGES_07_12_ZH.md。
原始审计与身份查验：research/EXPERIMENT_EDITORIAL_AUDIT_ZH.md、research/LOCALIZATION_IDENTITY_ZH.md、research/EXTERNAL_SENSITIVITY_AUDIT_ZH.md。

根目录verification.json与RELEASE_METADATA.json记录当前最终指纹；其他历史审阅文件仅适用于其记录的版本，不替代本次终审。

# 逐项修复：VisDrone 论文材料与证据

日期：2026-09-15。对应[原对抗性审计](PAPER_HANDOFF_ADVERSARIAL_AUDIT_20260915_ZH.md)。用户已要求 UAVDT 暂不处理，它在另一台服务器单跑；本轮没有启动 UAVDT 工作，也没有重新训练任何模型。

## 结论

当前方法入口、版本归属、表格分工和主张边界已修订；V12/V13 曾缺失的固定源码已真实找回，不是改 authority 名字制造一致。旧失败、负结果和不同评价协议均保留。推理测量独立归档，不能把材料修订等同于所有科学问题均已解决。

## 逐项状态

| 审计项 | 本轮处理 | 当前状态与证据 |
|---|---|---|
| M1 当前与旧 BPDD 混用 | 增加当前 G/B/F 方法页，重写主入口；旧FDR、BPDD、FIA与复杂度页增加历史版本警示 | 已修。B是局部专家＋专家监督＋质量门控定位KD；专家参与推理，分类KD关闭不等于分类监督关闭。[当前方法](../methods/CURRENT_JOINT_METHOD_ZH.md) |
| M2 联合 test 泛化叙述过强 | 生成补充S6，同快照列G/G+F/G+B/Full；S1/S4按各自口径保留 | 报告问题已修；额外泛化收益有限这一结果没有“修成涨点”。不称稳定test提升或统计显著。[补充五表](../submission_tables_20260915/selected/SUPPLEMENTARY_TABLES.md) |
| M3 专家容量、监督与KD没有隔离 | 用户确认B作为整体模块，删除KD独立贡献的强归因，v2→v3写成一组兼容性修改 | 当前整体主张不把KD独立对照列为必补项；若将来改为单独证明KD，再考虑等容量、同监督的训练对照。本轮不重训 |
| M4 UAVDT身份与清单 | 保留原始导出和草稿，不混进VisDrone结果 | 用户暂缓；另一台服务器单独处理，不列为本轮完成条件 |
| M5 FIA-off/on源码缺口及历史配对 | 恢复Full a43056a与BPDD-only 5ef5747固定源码；验证Git blob、配置图映射与已有训练设置；重放初始化 | V12/V13补证完成：239个共有文件字节一致，只有3个新增无FIA配置/脚本；994个共有状态张量相同，新增19项仅FIA且残差初值0。其他历史行不自动认证。[配对结论](../evidence/audit_remediation_20260915/SOURCE_PAIR_RESOLUTION_ZH.md) |
| M6 当前推理成本缺失 | 用现有冻结权重做五臂延迟、参数、完整算子计数及指纹核验 | 已补齐声明口径下的完整前向GFLOPs：Full134.051、G105.804；Full35.244M、86.075ms、11.618FPS。见[完整GFLOPs](../results/CURRENT_FULL_GFLOPS_ZH.md)及[延迟报告](../results/CURRENT_COMPLEXITY_ZH.md)。旧Full25.21FPS不适用，未知算子0项 |
| m1 外部只展示best | 表1同时列final主终点与best次终点；S2保留完整val/test | 已修。final test差+1.579pp；best test差+1.550pp，训练配方差异完整保留 |
| m2 差值表达缺括号 | 交接与写作计划统一Full−(G+B)、Full−(G+F) | 已修；未改原数值 |
| m3 新窗口依赖另一本地代码仓 | 材料仓内增加两份固定源码压缩包、可读快照和逐文件校验；交接指向新入口 | 本地可携带源码依赖已补；GitHub尚未推送，不声称远端最新。仅发送MD不会附带所有数据，跨机器需一起传材料包 |

## 最重要的结论修正

此前“BPDD-only源码取不回，因此不能排除换了BPDD版本”的理由，对当前V12/V13已撤回。恢复的实际内容证明是同一Capacity-v3-Safe路线上的FIA off/on，commit不同本身不是不一致。这项补证不增加指标值，也不消除单seed或test增量有限的限制。

同一当前配对：原生val AP-best Full−(G+B)=+0.832pp，末轮=+1.126pp。共同PIL/COCOeval test为+0.11793293pp；原生validator四臂快照为−0.01857309pp。协议分别陈述，不能择高证明评估器无关的提升。

## 可直接用于写作的文件

- [新窗口完整交接](../PAPER_WRITING_HANDOFF_20260915_ZH.md)
- [当前方法定义与真实训练/推理路径](../methods/CURRENT_JOINT_METHOD_ZH.md)
- [正文3张表](../submission_tables_20260915/selected/MAIN_TABLES.md)：外部final/best；大模块组合；内部定位与BPDD兼容性两个子表
- [补充5张表](../submission_tables_20260915/selected/SUPPLEMENTARY_TABLES.md)：共同test、best/final、尺度响应、baseline校准、原生test四臂
- [当前效率测量](../results/CURRENT_COMPLEXITY_ZH.md)
- [固定源码配对与校验](../evidence/audit_remediation_20260915/SOURCE_PAIR_RESOLUTION_ZH.md)

全套11张源表、39行结果由生成器从原始证据构建；29项输入有SHA-256记录。正文3张包含两个内部子表，故源表数量与最终表编号数量不同。UAVDT的2张草稿仍在档案，不进入本轮正文。

## 验收与尚未做的事

源码归档先验证传输长度与SHA-256，再逐文件核验Git blob；初始化重放不执行训练；效率原始样本与完成状态独立校验。表格检查真实CSV的100轮、best/final及同一best行指标，所有数值必须有限，输入指纹可复算。

效率取回包共22个文件，各文件SHA-256已验证；v1/v2失败日志和v3成功输出一起归档。服务器网关有终端帧字节混入，解码仅去除非Base64的替换字符，并强制核验完整压缩包长度与SHA-256；校验不通过不生成报告。未用不完整传输填数。

最终本地回归：39项通过（源码/归档、兼容边界、表格来源、效率样本、共同评估入口与既有baseline校准测试）。12份当前入口文档的173个本地链接、29项表格输入指纹通过核验；详见[资料包校验记录](../evidence/audit_remediation_20260915/package_verification.json)。这些是代码和材料检查，不是新增39次训练或精度实验。

没有改历史CSV、评估JSON、原authority、训练代码或checkpoint；没有删除失败证据，没有按test重新挑权重或调参，没有启动正式训练或GitHub推送。只新增隔离的推理测量脚本与输出，兼容旧权重所需的无专家布尔键仅补于内存。

后续GFLOPs补测新增17项公式/真实调用覆盖测试通过；与原有39项分开记录，不把它们当训练实验。完整前向GFLOPs限定640、batch1、MAC=2与声明的算术合同，不等于GPU机器指令或其他尺寸的成本。原始部分计数不覆盖，新增完整报告另存。

仍需在写作中如实处理：不单独主张KD因果贡献；Base/G/G+F及历史内部版本未全部达到V12/V13这次的源码与动态初始化核验等级；单seed；test已参与历史诊断；跨训练配方比较不等于等预算消融；目标会议模板和最终LaTeX排版尚未验收。这些不应通过改名或“已注明风险”宣称解决。

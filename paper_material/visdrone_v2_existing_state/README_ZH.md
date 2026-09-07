# VisDrone LRS v2 现有初始状态交付包

本目录对应代码仓库分支 `codex/visdrone-v2-existing-state-handoff-20260907`，代码交接提交为 `c1ac0b2`。完整可执行命令见该分支的 `docs/VISDRONE_V2_EXISTING_STATE_HANDOFF_ZH.md`。

## 运行身份

- 方法 revision：`v2-fp32-extent-logspace-ac-bpdd`
- 四臂：f=LRS-FDR+v2 geometry；g=f+AC-BPDD；h=f+FIA；i=f+AC-BPDD+FIA
- 训练：100 epochs、seed 0、batch 8、640、fresh start
- 数据签名：`FD92E9FF4B3B58FCDD5A32F7E770FC3398E566B627DB0E188CB5FF9F3B7BBDAB`

## 初始状态

`initial-state-seed0.pt` 不提交到 GitHub，需单独传输到服务器。文件大小为 `261864454` bytes，SHA-256 为：

`935D68428BFC5848DE51F82844658ABBC7EC8C99CBBF6BBF823166D38CB65D5B`

SHA 不一致时必须停止；不得用当前 G 的 `best.pt` 初始化其他臂。

## 已有进展

旧 v2 G 运行 best（epoch 92）mAP50-95=`0.29628`，历史 LRS-FDR best=`0.29703`，差=`-0.075 pp`。F 仅完成 44 轮，H/I 未运行；该结果是进展参考，不是新四臂正式主表。

## 交付边界

仓库只保存代码、配置、命令、哈希和摘要；不保存 `.pt` 二进制、数据集、密码或服务器密钥。

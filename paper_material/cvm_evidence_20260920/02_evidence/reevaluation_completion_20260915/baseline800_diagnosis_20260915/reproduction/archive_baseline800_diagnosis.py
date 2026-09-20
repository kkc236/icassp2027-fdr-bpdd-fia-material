"""Archive verified diagnostic evidence; no checkpoint or training mutation."""
import base64,hashlib,json,re,zlib
from pathlib import Path

workspace=Path(__file__).resolve().parent
raw=(workspace/'baseline800_diagnosis_bundle.log').read_text(encoding='utf-8')
assert 'BUNDLE_END' in raw
expected=re.search(r'BUNDLE_SHA256 ([0-9a-f]{64})',raw).group(1)
chunks=re.findall(r'^BUNDLE_CHUNK ([A-Za-z0-9+/=]+)\s*$',raw,re.M)
payload=zlib.decompress(base64.b64decode(''.join(chunks),validate=True))
assert hashlib.sha256(payload).hexdigest()==expected
bundle=json.loads(payload)
root=workspace/'icassp2027-fdr-bpdd-fia-material/paper_material/evidence/reevaluation_completion_20260915/baseline800_diagnosis_20260915'
root.mkdir(parents=True,exist_ok=True)
manifest=[]
for relative,record in bundle['files'].items():
    dest=(root/'files'/relative).resolve()
    assert dest.is_relative_to((root/'files').resolve())
    data=base64.b64decode(record['base64'],validate=True)
    assert hashlib.sha256(data).hexdigest()==record['sha256']
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists(): assert dest.read_bytes()==data, f'Refusing overwrite: {dest}'
    else: dest.write_bytes(data)
    manifest.append({'path':str(dest.relative_to(root)),'remote_path':record['remote_path'],'sha256':record['sha256']})
(root/'MANIFEST.json').write_text(json.dumps({'bundle_sha256':expected,'files':manifest,'remote_raw_predictions':bundle['raw_prediction_artifacts']},indent=2)+'\n',encoding='utf-8')
for script in ['deploy_baseline800_diagnostics.py','extend_baseline800_precision_diagnostics.py','analyze_baseline800_diagnostics.py','fetch_baseline800_diagnosis.py','archive_baseline800_diagnosis.py']:
    data=(workspace/script).read_bytes()
    dest=root/'reproduction'/script
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists(): assert dest.read_bytes()==data
    else: dest.write_bytes(data)

reports={p.parent.name:json.loads(p.read_text()) for p in (root/'files').glob('*/summary.json')}
assert len(reports)==10
assert all(x['status']=='complete' for x in json.loads((root/'files/COMPLETE.json').read_text()))
assert all(x['exit_code']==0 for x in json.loads((root/'files/PRECISION_COMPLETE.json').read_text()))
analysis=json.loads((root/'files/ANALYSIS.json').read_text())
assert set(analysis['metrics'])==set(reports)
for name,report in reports.items():
    assert report['image_count']==548
    assert report['raw_to_validator_box_maxabs_px']==0
    assert report['protocol']['split']=='val'
    assert report['protocol']['half'] is False
    assert report['protocol']['batch']==8
    assert report['protocol']['conf']==.001
    assert report['protocol']['max_det']==300
    assert report['metrics']==analysis['metrics'][name]
    assert analysis['gt_checks'][name]['same_images_and_classes']
    assert analysis['gt_checks'][name]['normalized_gt_maxabs']<1e-6
    assert all(shape[-2:]==[report['protocol']['imgsz']]*2 for shape in report['input_shapes'])
assert analysis['equivalence']['B_fresh800']['max_normalized_box_diff_rank_aligned']==0
assert analysis['equivalence']['B_fresh800']['max_score_diff_rank_aligned']==0
assert analysis['anchor_intervention_isolation']['encoder_max_score_diff']==0
assert analysis['anchor_intervention_isolation']['encoder_class_disagreements']==0
assert analysis['anchor_intervention_isolation']['encoder_max_center_diff']<1e-6
known={'B_native640':'9c242711f44b7e68b360af904ab7c44f64505c7136b7e7f90481092ae3308af7','G_native640':'df76a0c8bd5b215d378acb87eb240d7d1dfb44190167cd8c1e19f86fa18c969d'}
for name,sha in known.items():
    assert analysis['checkpoint_sha256_after_diagnostics'][reports[name]['protocol']['model']]==sha

def metric(name,key='map'): return reports[name]['metrics'][key]*100
drop=metric('B_native640')-metric('B_native800')
recovery=metric('B_anchor800')-metric('B_native800')
remaining=metric('B_native640')-metric('B_anchor800')
result={'validation_drop_pp':drop,'anchor_probe_recovery_pp':recovery,'fraction_of_observed_drop_recovered':recovery/drop,'remaining_gap_pp':remaining,
        'fresh640_delta_pp':metric('B_fresh640')-metric('B_native640'),'fp16anchors800_delta_pp':metric('B_fp16anchors800')-metric('B_native800'),
        'nofuse800_delta_pp':metric('B_nofuse800')-metric('B_native800'),'diagnostic_only':True,'test_not_used_for_interventions':True}
(root/'FINDINGS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
lines=['# Baseline 640→800 退化：因果诊断记录','','## 结论边界','',
'已定位到一个主要、可干预复现的因素：该冻结 baseline 在 800 输入下的 encoder 参考框宽高产生明显上偏，后续解码未能完全纠正。不是仅凭总体 AP 下降猜测。',
f'只调整参考锚点宽高（固定系数 640/800=0.8），验证集恢复 {recovery:.4f} pp，约为观察到降幅的 {100*recovery/drop:.2f}%；仍落后 640 原生结果 {remaining:.4f} pp。因此不能声称已解释全部损失，也不能将恢复比例理解为独立、可加的因果贡献分解。',
'这说明该 checkpoint 的跨分辨率适配有问题，不等于 Ultralytics 的归一化锚点设计本身错误，也不否定原生 640 baseline 的有效性。','',
'## 固定条件与排除项','',
'Baseline 的 8 个条件共用其同一冻结 checkpoint/EMA；LRS-GFDR 的 2 个条件共用其自身冻结 checkpoint/EMA。全部使用同一验证集 548 张、38,759 个实例，同一 RTDETRValidator，FP32、batch=8、conf=0.001、max_det=300、nms=False、rect=False。十个条件逐图核对文件顺序、类别和归一化 GT 坐标。',
'两份 checkpoint 记录均为训练 imgsz=640、multi_scale=0.0；存在 scale=0.5 和 mosaic=1.0 的训练增强，但这不等于启用了网络输入分辨率的 multi_scale 训练。该记录支持固定 640 训练背景，不能单独证明退化的全部原因。',
'所有条件的 raw 归一化框到 validator 像素框误差为 0；GT 归一化最大差异 <1e-6。800 的特征网格为 100×100、50×50、25×25，锚点数 13,125；640 为 80×80、40×40、20×20，锚点数 8,400。',
'强制刷新 800 锚点后，所有最终预测框与分数逐值完全一致；关闭融合、改变锚点生成精度的变化远小于主降幅。','',
'## 验证集单变量诊断（百分数）','','| 条件 | mAP50-95 | AP50 | AP75 |','|---|---:|---:|---:|']
labels={'B_native640':'Baseline 原生 640','B_native800':'Baseline 原生 800','B_fresh800':'800 强制刷新锚点','B_nofuse800':'800 关闭融合','B_anchor800':'800 锚点宽高×0.8（诊断）','B_boxwh800':'800 最终输出宽高×0.8（反证）','B_fresh640':'640 强制 FP32 重建锚点','B_fp16anchors800':'800 FP16 生成锚点再转 FP32','G_native640':'LRS-GFDR 原生 640','G_native800':'LRS-GFDR 原生 800'}
for name,label in labels.items(): lines.append(f'| {label} | {metric(name):.4f} | {metric(name,"map50"):.4f} | {metric(name,"map75"):.4f} |')
lines+=['','## 框几何证据','','固定 conf≥0.1，对每个 GT 选同类别 IoU 最高预测；以下宽高比中位数仅统计 IoU≥0.25 的 GT。它不是官方一对一召回率，不应替换论文 AP。','',
'| 模型与尺寸 | encoder 宽/真值 | encoder 高/真值 | final 宽/真值 | final 高/真值 |','|---|---:|---:|---:|---:|']
for name in ['B_native640','B_native800','B_anchor800','G_native640','G_native800']:
    a=analysis['analyses'][name]
    vals=[a[stage]['geometry_on_gt_iou_ge_0p25'][key] for stage in ['encoder','final'] for key in ['width','height']]
    lines.append('| '+labels[name]+' | '+' | '.join(f'{x:.4f}' for x in vals)+' |')
lines+=['','## 代码路径与因果证据','',
'1. `RTDETRDecoder._generate_anchors` 生成归一化参考宽高 0.05、0.1、0.2；它们在 640 下对应 32/64/128 像素，在 800 下对应 40/80/160 像素。归一化先验不变本身并非错误，但该模型的学习偏移未完全适配尺度变化。',
'2. `_get_decoder_input` 在 encoder 回归偏移上加参考框 logit，再 sigmoid 得到候选框。800 原生候选框出现约 24.6% 的宽高上偏。',
'3. 只改锚点宽高为原来的 0.8；encoder 分数和类别逐值不变，中心仅有浮点级差异。即没有换图、改标签、重新选 checkpoint 或通过分类分数人为改变候选排序。',
'4. 参考框进入 query 位置嵌入和 deformable attention 采样，再经迭代框回归。因此在解码入口修正尺度和在最终输出直接乘 0.8 不是同一种操作。后者 AP 更差，排除“最后统一缩框即可解决”的解释。',
'5. LRS-GFDR 在 800 下也存在 encoder 候选框上偏（宽/高约 1.2603/1.2373），但 final 宽/高约为 1.0226/1.0416，残余偏差小于 baseline。这把两者表现差异进一步定位到后续解码对偏差的纠正能力；由于是不同的学习后权重，不能仅凭此证明几何校正单独的因果贡献。',
'',
'## 未解释部分与使用建议','',
f'- 剩余 {remaining:.4f} pp 未被单一锚点干预恢复。特征尺度、候选竞争和 decoder 残差适配仍可能参与；本轮未独立识别其各自贡献，不能写成已证实原因。',
'- 不改模型、不重训的既定比较应保留 640 主口径；800 可列冻结推理尺度敏感性分析。',
'- 本轮全部新增干预在 val 上完成；没有再次用 test 搜索参数，没有把诊断条件替换为正式实验结果。',
'- checkpoint SHA256 在诊断后与诊断前记录一致；未修改生产代码、未替换权重、未提交或推送 GitHub。',
'- 早期 `summary.json` 的 `anchor_wh_first=[1,1]` 是首个无效边界锚点被 inf 掩码后的 sigmoid 值，不能用作有效锚点宽高。精度控制报告记录了有效锚点宽高集合；本报告采用有效锚点定义。','',
'## 可核验证据','',
'- `files/ANALYSIS.json`：逐图 GT 检查、encoder/final 几何、锚点干预隔离和 checkpoint 校验。',
'- `files/*/summary.json`：10 次原始评估摘要。',
'- `files/sources.json`、`files/decoder_sources.json`：服务器实际运行类的源码。',
'- `files/diagnose*.py`、runner 与日志：实际诊断实现。',
'- `MANIFEST.json`：下载文件逐一校验；10 份原始预测张量留在服务器并记录路径、长度与 SHA256。',
'- `reproduction/`：部署、分析、取证脚本。','']
(root/'BASELINE_800_CAUSE_ZH.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'verified_runs':len(reports),'verified_files':len(manifest),'raw_prediction_files':len(bundle['raw_prediction_artifacts']),'findings':result,'report':str(root/'BASELINE_800_CAUSE_ZH.md')},ensure_ascii=False,indent=2))
print('TRAIN_ARGS',json.dumps(analysis['checkpoint_training_args'],ensure_ascii=False))

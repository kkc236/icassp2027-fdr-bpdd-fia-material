// Recompute batch accounting and compare only matching frozen batch1/batch8 models.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),base=path.join(root,'paper_material/evidence/batch8_efficiency_20260916');
const read=(dir,name)=>JSON.parse(fs.readFileSync(path.join(dir,name),'utf8'));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const checkManifest=(dir,name)=>{
  const manifest=read(dir,name);
  for(const [name,item] of Object.entries(manifest.files)){
    const bytes=fs.readFileSync(path.join(dir,name));assert.equal(bytes.length,item.size);assert.equal(sha(bytes),item.sha256);
  }
};
checkManifest(base,'transport_manifest.json');
const oldBase=path.join(root,'paper_material/evidence/audit_remediation_20260915/efficiency');
checkManifest(oldBase,'transport_manifest.json');
const report=read(base,'v1/efficiency.json'),complete=read(base,'v1/COMPLETE.json');
const prior=read(oldBase,'v3/efficiency.json'),deployment=read(base,'v1/deployment.json');
assert.equal(report.status,'completed');assert.equal(complete.status,'completed');
assert.equal(report.training_started,false);assert.equal(complete.training_started,false);
assert.equal(report.uavdt_in_scope,false);assert.equal(report.protocol.batch,8);
assert.equal(report.protocol.dtype,'float32');assert.equal(report.protocol.imgsz,640);
assert.equal(report.protocol.iterations,300);assert.equal(report.protocol.warmup,100);
assert.equal(complete.arms,5);assert.equal(complete.measured_batches,1500);assert.equal(complete.measured_images,12000);
assert.equal(complete.checkpoints_unchanged,true);assert.equal(complete.training_sources_unchanged,true);
assert.deepEqual(report.source_sha256_before,report.source_sha256_after);
assert.deepEqual(report.source_sha256_before,Object.fromEntries(Object.entries(prior.source_sha256).map(([k,v])=>[k,v.toLowerCase()])));
assert.equal(report.prior_batch1_report_sha256,sha(fs.readFileSync(path.join(oldBase,'v3/efficiency.json'))));
assert.equal(report.helper_sha256,sha(fs.readFileSync(path.join(oldBase,'v3/measure.py'))));
assert.equal(report.measurement_source_sha256,sha(fs.readFileSync(path.join(base,'v1/measure.py'))));
assert.equal(report.measurement_source_sha256,deployment.source_sha256);
for(const key of ['python','torch','cuda','ultralytics','gpu'])assert.equal(report.environment[key],prior.environment[key]);
for(const key of ['conf','max_det','seed','cpu_threads','tf32','cudnn_benchmark'])assert.equal(report.protocol[key],prior.protocol[key]);
assert.equal(report.input_sha256.length,8);assert.equal(new Set(report.input_sha256).size,8);
assert(report.input_sha256.every(s=>/^[a-f0-9]{64}$/.test(s)));
const close=(a,b)=>assert(Math.abs(a-b)<1e-8,`${a} != ${b}`);
const expectedArms=['Baseline','G','G+F','G+B','Full'];
assert.deepEqual(report.rows.map(r=>r.arm),expectedArms);
const rows=report.rows.map(row=>{
  const old=prior.rows.find(r=>r.arm===row.arm);
  assert.equal(row.sha256_before,row.sha256_after);assert.equal(row.sha256_before,old.sha256_before.toLowerCase());
  assert.equal(row.parameters_unfused,old.parameters_unfused);assert.equal(row.parameters_fused,old.parameters_fused);
  assert.deepEqual(row.observed_forward_input,{shape:[8,3,640,640],dtype:'torch.float32',device:'cuda:0'});
  assert.equal(row.expert_forward_calls_measured,['G+B','Full'].includes(row.arm)?300:0);
  assert.equal(row.sample_count,300);assert.equal(row.latency_samples_ms.length,300);
  assert(row.latency_samples_ms.every(s=>Number.isFinite(s)&&s>0));
  const ordered=[...row.latency_samples_ms].sort((a,b)=>a-b),median=(ordered[149]+ordered[150])/2;
  close(row.batch_median_ms,median);close(row.batch_p90_ms,ordered[269]+.1*(ordered[270]-ordered[269]));
  close(row.amortized_ms_per_image,median/8);close(row.images_per_second_from_median,8000/median);
  close(row.images_per_second_from_total_measured_time,300*8000/row.latency_samples_ms.reduce((a,b)=>a+b,0));
  assert(Number.isFinite(row.peak_allocated_mib)&&row.peak_allocated_mib>0);
  assert(row.peak_reserved_mib>=row.peak_allocated_mib);
  return {...row,prior_batch1_ms:old.median_ms,prior_batch1_images_per_second:old.fps,
    throughput_ratio_vs_prior_batch1:row.images_per_second_from_median/old.fps};
});
const verification={status:'pass',measured_batches:1500,measured_images:12000,arms:5,
  observed_model_batch_size:8,unchanged_checkpoints:true,unchanged_training_sources:true,
  same_environment_and_base_protocol_as_prior_batch1:true,prior_batch1_not_remeasured_this_run:true,
  measurement_source_sha256:report.measurement_source_sha256};
fs.writeFileSync(path.join(base,'verification.json'),JSON.stringify(verification,null,2)+'\n');
const f=n=>n.toFixed(3);
const document=`# 当前 VisDrone batch=8 五臂推理效率

2026-09-16。已实际测量，不是按batch=1结果乘除估算；五臂均捕获模型真实输入为 **[8,3,640,640]、CUDA FP32**。联合模型原来的训练batch=8未改变，本次只测推理。

## 同条件八张批处理结果

| 模型 | 整批中位延迟 ms | 整批P90 ms | 每图摊销 ms | 吞吐量 images/s | 峰值分配显存 MiB |
|---|---:|---:|---:|---:|---:|
${rows.map(r=>`| ${r.arm} | ${f(r.batch_median_ms)} | ${f(r.batch_p90_ms)} | ${f(r.amortized_ms_per_image)} | ${f(r.images_per_second_from_median)} | ${f(r.peak_allocated_mib)} |`).join('\n')}

G=LRS-GFDR；B=Capacity-BPDD-v3-Safe整体模块；F=P3-only FIA。吞吐量=8000/整批中位毫秒数。每图摊销时间=整批时间/8，**不是单张请求的响应延迟**，不能以该摊销值宣称batch=1实时性能。全部采样时段的累计吞吐量也保存在JSON中。

## 与此前 batch=1 的对应结果

| 模型 | 原batch=1 ms/张 | 原batch=1 images/s | 本次batch=8 images/s | 吞吐比值 |
|---|---:|---:|---:|---:|
${rows.map(r=>`| ${r.arm} | ${f(r.prior_batch1_ms)} | ${f(r.prior_batch1_images_per_second)} | ${f(r.images_per_second_from_median)} | ${f(r.throughput_ratio_vs_prior_batch1)}× |`).join('\n')}

同一GPU型号/设备环境、软件版本、checkpoint、推理源码、640尺寸、FP32、TF32关闭、8 CPU线程及原生融合。batch=1复用9月15日原始测量，batch=8在9月16日新增；不是同一时刻交错测量，表中比值不单独证明所有负载下的提速。

## 测量合同

- GPU：${report.environment.gpu}；PyTorch ${report.environment.torch}；CUDA ${report.environment.cuda}；Ultralytics ${report.environment.ultralytics}。
- 显式输入8张固定seed的640×640 uint8 BGR随机图，各图不同；首图与旧batch=1生成规则相同。输入指纹在原始JSON。不是自然图像整套数据集评测，也不含AP评估。
- 每臂额外执行一次输入形状审计，随后预热100批、计时300批；共1500个整批样本、12000张计时图像。仅一轮固定输入微基准，不能当作独立设备/训练重复。
- CUDA同步墙钟计时：Ultralytics predict的预处理、模型和后处理；不含磁盘读取；conf=0.001、max_det=300，无TTA/额外NMS。
- 与旧测量相同，保留轻量专家前向计数hook；只在预热前审计输入shape，计时期间移除shape hook。G+B和Full各记录300次专家调用，每次实际处理8张。
- 显存为PyTorch峰值allocated/reserved，不等于nvidia-smi的整进程显存；reserved也见JSON。
- G/G+F仅复用之前已登记的旧head布尔键兼容补值；没有修改几何公式、chunk_size、权重、训练代码或预测策略。
- 五臂checkpoint前后指纹相同，八个核心源码文件前后及与旧batch=1一致。未训练、未处理UAVDT、未推送GitHub。

本次不是重测GFLOPs；既有134.051 GFLOPs等数值仍属于[声明的640单图完整前向口径](CURRENT_FULL_GFLOPS_ZH.md)。训练batch、推理batch、每图理论计算量三者不要混用。

## 可复核资料

- [完整原始结果与1500个整批耗时](../evidence/batch8_efficiency_20260916/v1/efficiency.json)
- [完成标记](../evidence/batch8_efficiency_20260916/v1/COMPLETE.json)、[独立重算验证](../evidence/batch8_efficiency_20260916/verification.json)
- [实际服务器测量脚本](../evidence/batch8_efficiency_20260916/v1/measure.py)、[运行日志](../evidence/batch8_efficiency_20260916/v1/measurement.log)
- [文件传输SHA-256与大小](../evidence/batch8_efficiency_20260916/transport_manifest.json)、[旧batch=1报告](CURRENT_COMPLEXITY_ZH.md)

重建：node scripts/build_batch8_efficiency_report.cjs。必须先通过原始传输文件校验、五臂配对、实际输入shape和统计重算，不能只凭日志的batch参数宣布完成。
`;
fs.writeFileSync(path.join(root,'paper_material/results/CURRENT_BATCH8_EFFICIENCY_ZH.md'),document);
console.log(JSON.stringify({verification,rows:rows.map(({arm,batch_median_ms,amortized_ms_per_image,images_per_second_from_median,peak_allocated_mib})=>({arm,batch_median_ms,amortized_ms_per_image,images_per_second_from_median,peak_allocated_mib}))}));

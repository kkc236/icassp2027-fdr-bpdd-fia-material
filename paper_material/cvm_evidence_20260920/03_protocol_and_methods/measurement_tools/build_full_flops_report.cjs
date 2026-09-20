// Generate the auditable, convention-explicit five-arm GFLOPs report.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const ev=path.join(root,'paper_material/evidence/audit_remediation_20260915');
const dir=path.join(ev,'full_flops/v2');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const trace=read(path.join(dir,'inventory.json')),counts=read(path.join(dir,'arithmetic_count.json'));
const transport=read(path.join(dir,'transport_manifest.json'));
for(const [name,entry] of Object.entries(transport.files)) {
 const bytes=fs.readFileSync(path.join(dir,name));assert.equal(bytes.length,entry.bytes);assert.equal(sha(bytes),entry.sha256);
}
assert.equal(counts.status,'complete_under_declared_convention');
const previous=read(path.join(ev,'efficiency/v3/efficiency.json'));
const line=fs.readFileSync(path.join(ev,'flops_integrity_receipt.log'),'utf8').match(/RECEIPT (\{[^\r\n]+\})/);
assert(line,'complete runtime integrity receipt required');const receipt=JSON.parse(line[1]);
assert.equal(receipt.status,'pass');assert.equal(receipt.training_started,false);assert.equal(receipt.checkpoint_files_written,false);
assert.deepEqual(receipt.source_sha256,previous.source_sha256);
assert.equal(receipt.trace_script_sha256.toLowerCase(),transport.files['trace.py'].sha256);
const rows=[];
for(const old of previous.rows) {
 const arm=old.arm,record=counts.arms[arm];
 assert.equal(trace.arms[arm].checkpoint_sha256,old.sha256_before);
 assert.equal(receipt.checkpoint_sha256_after[arm],old.sha256_before);
 assert.equal(record.status,'covered');assert.deepEqual(record.unsupported,{});
 assert.equal(record.no_grad_crosscheck.status,'covered');assert.deepEqual(record.no_grad_crosscheck.unsupported,{});
 assert(record.official_major_match&&record.no_grad_crosscheck.official_major_match);
 for(const [counted,expected] of [[record,trace.arms[arm].official_by_op],
                                [record.no_grad_crosscheck,trace.arms[arm].no_grad_official_by_op]]) {
   const actual=Object.fromEntries(Object.keys(expected).map(k=>[k,0]));
   for(const [op,detail] of Object.entries(counted.ops)) {
     const packet=op.split('.').slice(0,2).join('.');
     if(Object.hasOwn(actual,packet))actual[packet]+=Object.entries(detail.categories)
       .filter(([key])=>['conv_mac2','matrix_mac2','attention_mac2'].includes(key)).reduce((n,[,v])=>n+v,0);
   }
   assert.deepEqual(actual,expected,arm+': every registered operator must match independently');
 }
 assert(record.composite_lowered_major_match&&record.composite_lowered_total_match_after_predicate_normalization);
 assert(record.output_max_abs_errors.every(e=>e===0));
 rows.push({arm,parameters_unfused:old.parameters_unfused,parameters_fused:old.parameters_fused,
   gflops:record.gflops,major_mac_gflops:record.major_arithmetic_flops/1e9,
   additional_arithmetic_gflops:(record.total_flops-record.major_arithmetic_flops)/1e9,
   median_ms:old.median_ms,fps:old.fps,checkpoint_sha256:old.sha256_before,
   composite_operator_types:record.operator_types,composite_operator_calls:record.operator_calls,
   lowered_operator_types:record.no_grad_crosscheck.operator_types,unsupported_operator_types:0});
}
const snapshots={};
for(const [original,target] of [['scripts/count_inference_flops.py','counter_source.py'],['tests/test_full_inference_flops.py','formula_tests.py']]) {
 const bytes=fs.readFileSync(path.join(root,original)),dest=path.join(dir,target);
 if(fs.existsSync(dest))assert.equal(sha(fs.readFileSync(dest)),sha(bytes),'versioned snapshot already differs');
 else fs.writeFileSync(dest,bytes,{flag:'wx'});
 snapshots[target]=sha(bytes);
}
const report={status:'complete_under_declared_convention',date:'2026-09-15',
 protocol:{input:[1,3,640,640],classes:10,dtype:'float32',warmup:2,model_mode:'eval',
  fusion:'native model.fuse; same checkpoint as latency report',seed:20260915,
  scope:'executed model forward including decoder/expert and in-model decoding; excludes image I/O, external preprocessing/evaluator/NMS, training losses',
  convention:counts.convention,mac_flops:2,transcendental_equivalent_ops:1,
  explicitly_excluded:['comparison/selection/predicates','integer and index arithmetic','memory movement/views/casts','nearest-neighbor copies'],
  dense_nominal_work:true,hardware_instruction_count:false},
 environment:receipt.environment,rows,
 verification:{runtime_receipt:receipt,source_snapshots_sha256:snapshots,
  inventory_sha256:sha(fs.readFileSync(path.join(dir,'inventory.json'))),
  arithmetic_count_sha256:sha(fs.readFileSync(path.join(dir,'arithmetic_count.json'))),
  all_observed_ops_classified:true,unknown_arithmetic_treated_as_zero:false,
  all_outputs_identical_across_modes:true,all_major_counts_match_lowered_and_official_registry:true,
  all_registered_operator_counts_individually_match:true,
  remaining_scalar_difference_fully_explained_by_isfinite_decomposition:true},
 whole_module_policy:'Capacity-BPDD is evaluated as a whole; independent KD-only attribution is not claimed',
 training_started:false,uavdt_in_scope:false,github_pushed:false};
fs.writeFileSync(path.join(dir,'complete_report.json'),JSON.stringify(report,null,2)+'\n');
const f=n=>n.toFixed(3),get=n=>rows.find(r=>r.arm===n),delta=(a,b)=>get(a).gflops-get(b).gflops;
const md=`# 当前 VisDrone 完整前向 GFLOPs：五臂测量与算子覆盖

2026-09-15。已完成当前冻结权重的模型前向采集和算子计数。这里“完整”指：**在声明的理论浮点运算口径下，实际执行图中所有观察到的算子均已计数或明确归为非浮点运算；未知算子为0项**。不是GPU机器指令数，也不是所有工具都必须给出同一小数。

## 可用于论文的同口径效率表

G=LRS-GFDR；B=Capacity-BPDD-v3-Safe整体模块；F=P3-only FIA。VisDrone 10类、640×640、batch=1、FP32、原生融合，MAC按2 FLOPs。

| 模型 | 未融合总参数 (M) | GFLOPs / image | 原实测延迟 (ms) | 原实测FPS |
|---|---:|---:|---:|---:|
${rows.map(r=>`| ${r.arm} | ${f(r.parameters_unfused/1e6)} | ${f(r.gflops)} | ${f(r.median_ms)} | ${f(r.fps)} |`).join('\n')}

GFLOPs是本次模型前向计数；延迟/FPS复用同一权重的已完成300次/臂测量，其范围还包含外部预处理与后处理，二者范围不混称。未融合参数包括模型对象全部参数，不假称剔除了所有未执行的训练期参数；GFLOPs只计eval实际调用路径，不把未执行层全部加进去。

Full相对G增加 **${f(delta('Full','G'))} GFLOPs（+${((get('Full').gflops/get('G').gflops-1)*100).toFixed(2)}%）**；B加入G增加${f(delta('G+B','G'))} GFLOPs；FIA在G或G+B上均增加${f(delta('Full','G+B'))} GFLOPs。该一致性是执行图成本核验，不是精度独立贡献证明。KD损失不参与推理；当前专家参与推理，其成本已包含。

## 主要乘加与其余算术

| 模型 | 卷积/矩阵/注意力主要乘加 GFLOPs | 其余算术 GFLOPs | 合计 |
|---|---:|---:|---:|
${rows.map(r=>`| ${r.arm} | ${f(r.major_mac_gflops)} | ${f(r.additional_arithmetic_gflops)} | ${f(r.gflops)} |`).join('\n')}

其余算术包括bias、归一化、激活、归约、边界解码、双线性插值及坐标/权重运算。矩阵向量乘同样计入；不能用默认计数器漏掉的结果代替本表。不同工具可能采用MAC=1或省略非乘加运算，文献/工具的GFLOPs不能不注明口径直接拼表。PyTorch的[2.5.1计数实现](https://github.com/pytorch/pytorch/blob/v2.5.1/torch/utils/flop_counter.py)与[fvcore口径说明](https://detectron2.readthedocs.io/en/stable/modules/fvcore.html)可核对这些差别。

## 可复核的计数合同

- 卷积：2 × 输出元素数 × 每个输出的卷积核乘积项数；含group/depthwise形状；有bias另计一次加法/输出。矩阵乘法同样按每个乘加2次，显式计bias/非单位缩放。
- 注意力：QK与AV两次矩阵乘法，另计缩放、浮点mask相加和softmax。masked位置按稠密名义运算计，不按某张图像的掩码稀疏性降算力；本图无causal/GQA/dropout训练路径。
- Softmax按减最大值、exp、求和、除法记4N−R（最大值比较不计）；exp/log/sin/cos/erf/pow等各按1次标量等价操作，非硬件周期。sigmoid=4N、SiLU=5N、精确形式GELU=5N。
- LayerNorm采用声明的两遍方差展开：含仿射时8N+2R；eval BatchNorm含仿射时4N+2C。它们是统一的数学计数合同，不冒充cuDNN实际实现步骤。
- 双线性采样：每个输出4次稠密乘加，即8次；共享坐标反归一化和4个插值权重另计，align_corners=false时每采样点20次。越界零填充仍按稠密名义工作量计；边界判断、floor及索引不计浮点算术。实现依据可核对[采样内核](https://github.com/pytorch/pytorch/blob/v2.5.1/aten/src/ATen/native/cuda/GridSampler.cu)和[坐标变换](https://github.com/pytorch/pytorch/blob/v2.5.1/aten/src/ATen/native/cuda/GridSampler.cuh)。
- 求和按N−R，均值再加R次除法；池化按相应区域实际形状。比较/排序/top-k/截断/predicate、整数索引、内存访问、reshape/copy/cast和最近邻复制明确不计浮点算术。清单保留，不能称这些操作没有运行开销。
- 不包括读取图像、外部预处理、额外NMS/评价器、反向传播或训练损失。包含完整eval检测器、局部专家和模型内部的框解码。

## 两条记录路径交叉核验

1. inference_mode下记录复合ATen算子，每次调用只计一层，不把其内核展开再加一遍。
2. no_grad下另采集分解后的算子，核对卷积、矩阵、融合注意力的计数，并与PyTorch官方registry覆盖部分逐项一致。
3. 五臂两条路径的全部输出张量最大差均为0；主要乘加完全一致。分解路径的额外标量工作精确等于isfinite内部展开的abs：Baseline/G/G+F/G+B/Full分别为0/6/6/24607/24607次；按predicate排除规则归一后总量完全一致，没有未解释差额。
4. 当前环境下，直接在inference_mode调用默认FlopCounterMode会只记0.7168 GFLOPs，因为复合conv2d/linear等未被该registry拦截；该不完整中间结果保留但不进论文表。仅把unknown忽略并不能完成测量。

| 模型 | 复合算子种类 | 复合算子调用数 | 分解算子种类 | 未覆盖种类 |
|---|---:|---:|---:|---:|
${rows.map(r=>`| ${r.arm} | ${r.composite_operator_types} | ${r.composite_operator_calls} | ${r.lowered_operator_types} | 0 |`).join('\n')}

## 原始证据与复现

- [完成报告与五臂checkpoint指纹](../evidence/audit_remediation_20260915/full_flops/v2/complete_report.json)
- [逐算子计数及交叉核验](../evidence/audit_remediation_20260915/full_flops/v2/arithmetic_count.json)
- [两种模式的原始调用/形状记录](../evidence/audit_remediation_20260915/full_flops/v2/inventory.json)、[传输校验](../evidence/audit_remediation_20260915/full_flops/v2/transport_manifest.json)
- [实际服务器采集代码](../evidence/audit_remediation_20260915/full_flops/v2/trace.py)、[冻结计数公式](../evidence/audit_remediation_20260915/full_flops/v2/counter_source.py)、[公式测试](../evidence/audit_remediation_20260915/full_flops/v2/formula_tests.py)
- [先前同机参数与1500次延迟测量](CURRENT_COMPLEXITY_ZH.md)

在材料仓根目录可先运行python scripts/count_inference_flops.py（指定inventory.json和输出JSON），再运行node scripts/build_full_flops_report.cjs。计数失败、未知算子、输出或独立计数不一致时不认证完成。

八个核心运行源码文件与五个checkpoint的测后指纹核验通过；未重训、未改模型、未改精度数据、未启动UAVDT、未推送GitHub。服务器测量结束时没有GPU计算进程。本次只补齐已声明640推理配置的理论运算量，不推导训练算力或在其他输入尺寸的数字。
`;
fs.writeFileSync(path.join(root,'paper_material/results/CURRENT_FULL_GFLOPS_ZH.md'),md,'utf8');
console.log(JSON.stringify({status:report.status,rows:rows.map(({arm,gflops})=>({arm,gflops})),unsupported:0}));

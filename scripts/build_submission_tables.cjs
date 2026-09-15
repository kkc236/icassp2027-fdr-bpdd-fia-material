// Generate manuscript tables from registered experiment evidence; no training.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const dest = path.join(root, 'paper_material/submission_tables_20260915');
const inputs = new Map();
function read(p) {
  const b = fs.readFileSync(path.join(root, p));
  inputs.set(p, crypto.createHash('sha256').update(b).digest('hex'));
  return b.toString('utf8').replace(/^\uFEFF/, '');
}
const json = p => JSON.parse(read(p));
const summaryPath = 'paper_material/results/all_experiments_summary.json';
const records = json(summaryPath).records;
const R = id => { const r = records.find(x => x.id === id); assert(r, id); return r; };
const ep = 'paper_material/evidence/visdrone_lrs_gfdr_capacity_v3_safe_joint_20260913/';
const cp = 'paper_material/evidence/visdrone_dfine_l_external_20260913/common_evaluation_20260915/';
const offAuth = json(ep + 'bpdd-authority.json'), onAuth = json(ep + 'joint-authority.json');
assert.equal(offAuth.dataset.sha256, onAuth.dataset.sha256);
assert.equal(offAuth.initial_state.sha256, onAuth.initial_state.sha256);
const excluded = new Set(['data', 'model', 'name', 'project']);
const allKeys = new Set([...Object.keys(offAuth.settings), ...Object.keys(onAuth.settings)]);
const matchedKeys = [...allKeys].filter(k => !excluded.has(k));
for (const k of matchedKeys) assert.deepEqual(offAuth.settings[k], onAuth.settings[k], k);
// Validate actual formal100 logs against the registered selection, without changing them.
function verifyCsv(file, id) {
  const lines = read(ep + file).trim().split(/\r?\n/);
  const head = lines.shift().split(',').map(s => s.trim());
  const rows = lines.map(line => Object.fromEntries(line.split(',').map((v,i) => [head[i], Number(v)])));
  assert.equal(rows.length, 100);
  const best = rows.reduce((a,b) => b['metrics/mAP50-95(B)'] > a['metrics/mAP50-95(B)'] ? b : a);
  const r = R(id);
  assert.equal(best.epoch, r.best_epoch);
  for (const [key,col] of [['map50_95','mAP50-95'],['ap50','mAP50'],['precision','precision'],['recall','recall']]) {
    assert.equal(best[`metrics/${col}(B)`], r.val[key], id + ':' + key);
  }
  assert.equal(rows.at(-1)['metrics/mAP50-95(B)'], r.final.map50_95);
}
verifyCsv('bpdd-current-results.csv', 'V12');
verifyCsv('joint-results.csv', 'V13');
const D = json(cp + 'dfine_best_test.cap300.json');
const F = json(cp + 'joint_best_test.cap300.json');
const B = json(ep + 'bpdd-independent-test-cap300.json');
for (const j of [D,F,B]) { assert.equal(j.image_count,1610); assert.equal(j.max_det,300); assert.equal(j.evaluator_version,'2.0.11'); }
json(ep + 'bpdd-independent-test-manifest.json');
const data = json(cp + 'dataset-preflight.json');
const dAuth = json('paper_material/evidence/visdrone_dfine_l_external_20260913/bs4-run-authority.json');
const fReport = json(cp + 'joint_best_test.report.json');
const offConfig = read(ep+'rtdetr-l-lrs-gfdr-capacity-v3-safe-bpdd.yaml');
const onConfig = read(ep+'rtdetr-l-lrs-gfdr-capacity-v3-safe-bpdd-fia.yaml');
assert(!offConfig.includes(', FIA,')); assert(onConfig.includes(', FIA,'));
assert.equal(offConfig.split('fdr_loss:')[1],onConfig.split('fdr_loss:')[1]);
const tables=[];
function add(id, group, title, en, headers, rows, note, enNote, sources) {
  for(const row of rows) assert.equal(row.length, headers.length, id);
  tables.push({id,group,title,caption_en:en,headers,rows,note,caption_note_en:enNote,sources});
}
const pct = n => +(n*100).toFixed(9);
const diff = (a,b) => pct(a-b);
const metricKeys=['mAP50_95','AP50','AP75','AP_small','AP_medium','AP_large'];
const mrow = j => metricKeys.map(k=>pct(j[k]));
add('T1','main','外部方法：VisDrone test 共同评估',
  'Cross-recipe comparison on the project VisDrone test split.',
  ['Method','Params (M)','AP','AP50','AP75','APs','APm','APl'],
  [['D-FINE-L (retrained)',dAuth.parameters/1e6,...mrow(D)],['Ours (Full)',fReport.parameters/1e6,...mrow(F)],['Delta (pp)',null,...metricKeys.map(k=>diff(F[k],D[k]))]],
  'AP 指标为百分数。1610 张项目 test 图像；YOLO 标签转 COCO，maxDet=300、640、FP32、无 TTA/额外 NMS。两者都按各自原生 val AP 选择 best；训练配方不同（D-FINE batch=4/AdamW/FP32，本方法 batch=8/MuSGD/AMP）。这是本地共同评估结果，不是官方 VisDrone challenge 排名。参数为实际模型登记总量，不代表已剔除训练分支的部署开销。',
  'AP values are percentages. Both checkpoints were selected by native validation AP and evaluated on the same 1,610 project test images using YOLO-derived COCO annotations, 640 input, FP32 and maxDet=300, without TTA or extra NMS. Training recipes differ: D-FINE uses batch 4, AdamW and FP32; ours uses batch 8, MuSGD and AMP. Parameters are registered model totals, not deployment-pruned counts. This is not an official challenge ranking.',
  [cp+'dfine_best_test.cap300.json',cp+'joint_best_test.cap300.json','paper_material/evidence/visdrone_dfine_l_external_20260913/bs4-run-authority.json',cp+'joint_best_test.report.json']);
const macroIds=['V01','V06','V09','V12','V13'];
const flags=[['Base','off','off','off'],['G','on','off','off'],['G+F','on','off','on'],['G+B','on','on','off'],['Full','on','on','on']];
add('T2','main','大模块消融：只比较 G、B、F 三个组件',
  'Component comparison on native VisDrone validation results.',
  ['Model','G','B','F','P','R','AP50','AP'],
  macroIds.map((id,i)=>{const v=R(id).val; return [...flags[i],pct(v.precision),pct(v.recall),pct(v.ap50),pct(v.map50_95)];}),
  'G=LRS-GFDR，B=Capacity-BPDD-v3-Safe，F=FIA P3-only。各行所有指标取同一 AP-best 轮。Base/G/G+F 是已登记参考运行；G+B/Full 的数据、初始状态及已记录训练设置匹配。共同 protocol ID 是事后归档分组，不替代源码差异审计。无 G 的 B 依赖不存在，未运行的组合不填造数。',
  'G: LRS-GFDR; B: Capacity-BPDD-v3-Safe; F: P3-only FIA. All metrics in a row are from the same validation-AP-best epoch. Base, G and G+F are registered reference runs; G+B and Full share recorded data, initialization and training settings. Source-path equivalence remains to be audited. The table is not a fully verified factorial experiment.',
  macroIds.map(id=>summaryPath+'#'+id).concat([ep+'bpdd-authority.json',ep+'joint-authority.json',ep+'bpdd-current-results.csv',ep+'joint-results.csv']));
const gi=['V02','V03','V04','V06'];
add('T3','internal','G 内部设计：迁移、Clean、几何修正与 LRS',
  'Internal design comparison of the localization module.',
  ['Variant','Geometry','LRS','AP50','AP','Best epoch'],
  gi.map((id,i)=>{const r=R(id);return [['Original FDR','Clean-FDR','Clean-FDR + geometry','LRS-GFDR'][i],['reference','off','on','on'][i],['reference','off','off','on'][i],pct(r.val.ap50),pct(r.val.map50_95),r.best_epoch];}),
  '此表是已登记内部设计版本对照，源码、初始化完整配对情况仍待逐项回溯。Clean→几何修正的 AP 为 -0.335 pp；几何修正→加 LRS 为 +0.259 pp。几何修正应解释为可行域约束；现有 VisDrone 精度不支持“几何修正单独涨点”。第二数据集崩溃原因及修复效果需对应日志，不能由本表推断。Original FDR 的开关未按当前实现映射，使用 reference。',
  'These are registered design variants, not a fully source-matched toggle experiment. Geometry reduces validation AP relative to Clean-FDR in these runs; LRS recovers part of that difference. The table does not establish a standalone accuracy gain from geometry or prove a second-dataset stability claim. Reference denotes switches not mapped to the current implementation.',
  gi.map(id=>summaryPath+'#'+id));
const bi=['V10','V11','V12','V13'];
add('T4','internal','B 内部设计：蒸馏方案与 FIA 联合兼容性',
  'BPDD recipe comparison with and without FIA.',
  ['BPDD recipe','FIA','AP50','Best AP','Final AP','Best epoch'],
  bi.map((id,i)=>{const r=R(id);return [i<2?'Capacity v2':'Capacity v3-Safe',i%2?'on':'off',pct(r.val.ap50),pct(r.val.map50_95),pct(r.final.map50_95),r.best_epoch];}),
  'v2→v3-Safe 是一组兼容性修改；目前不足以把定位蒸馏、分类蒸馏关闭、调度等因素逐个归因。保留同一路线联合退化行以说明设计选择。v3-Safe 的 BPDD-only 低于 v2；Full 优于 v2 联合。它支持“改善联合配置的表现”，不支持“新版 BPDD 在任何组合都更强”。',
  'The v2-to-v3-Safe change is a recipe bundle, not an isolated toggle for each distillation or scheduling choice. The v3-Safe BPDD-only run is worse than v2, while its joint run is better. These results motivate compatibility-oriented design rather than universally improved standalone BPDD.',
  bi.map(id=>summaryPath+'#'+id));
add('S1','support','FIA 开关的独立 test 检验',
  'Held-out test comparison of the current FIA-off/on pair.',
  ['Model','AP','AP50','AP75','APs','APm','APl'],
  [['G+B',...mrow(B)],['Full',...mrow(F)],['Delta (pp)',...metricKeys.map(k=>diff(F[k],B[k]))]],
  '固定各自原生 val 选出的 best checkpoint，再以共同 test 口径评估。Full 相对 G+B 的 test AP 为 +0.118 pp，原生 val best 为 +0.832 pp；两者不能替换。单 seed 观测没有置信区间，不写统计显著。',
  'The checkpoints selected by native validation AP are evaluated once under the common test protocol. Test AP improves by 0.118 percentage points, compared with 0.832 points in native validation. These single-seed observations do not establish statistical significance.',
  [ep+'bpdd-independent-test-cap300.json',cp+'joint_best_test.cap300.json',ep+'bpdd-independent-test-manifest.json']);
add('S2','support','末轮稳健性：共同评估下的 best 与 final',
  'Best and final checkpoints under the common evaluator.',
  ['Model','Checkpoint','Val AP','Test AP'],
  ['dfine','joint'].flatMap(name=>['best','final'].map(choice=>[name==='dfine'?'D-FINE-L':'Full',choice,pct(json(cp+`${name}_${choice}_val.cap300.json`).mAP50_95),pct(json(cp+`${name}_${choice}_test.cap300.json`).mAP50_95)])),
  'best 来自原生验证选择，final 为第100轮；没有用 test 再选 checkpoint。共同评估 val 与训练日志 val 是不同口径。',
  'Best checkpoints were selected on native validation AP, whereas final denotes epoch 100. Test results were not used for checkpoint selection. Common-evaluator validation differs from the native training metric.',
  ['dfine','joint'].flatMap(n=>['best','final'].flatMap(s=>['val','test'].map(p=>cp+`${n}_${s}_${p}.cap300.json`))));
const uBase=R('H11'), uFull=R('H12');
add('U1','pending','UAVDT 总体结果：当前联合模型，待统一评估复核',
  'Current UAVDT joint-model results pending common-evaluation reconciliation.',
  ['Run','P','R','AP50','AP','Epochs'],
  [uBase,uFull].map((r,i)=>[i?'Current joint model export':'RT-DETR-L baseline',pct(r.val.precision),pct(r.val.recall),pct(r.val.ap50),pct(r.val.map50_95),r.epochs_completed]),
  '联合臂的方法身份已由作者确认，为当前 LRS-GFDR + Capacity-BPDD-v3-Safe + FIA。baseline 是可靠服务器报告；但 baseline 的17165张/342686目标与联合臂的16592张/375883目标不一致，因此尚未通过“同一评估清单”核验。15.60→16.96 的 +1.36 pp 不进入摘要或正文主结论；本表仅保留为复评前审计记录。该实验属于第二数据集训练/验证，不写零样本迁移。',
  'The author confirms that the joint export is the current LRS-GFDR + Capacity-BPDD-v3-Safe + FIA method. However, the reported image/instance totals differ between baseline and joint evaluation. Until both checkpoints are evaluated against one frozen manifest, this table is an audit record only and must not be reported as a matched improvement or zero-shot transfer.',
  [summaryPath+'#H11',summaryPath+'#H12','paper_material/evidence/uavdt_capacity_v3_safe_joint_20260913/user_export_20260915/paper_data.txt','paper_material/evidence/uavdt_capacity_v3_safe_joint_20260913/baseline_reference_20260915/rtdetr_baseline_test_results.md']);
add('U2','pending','UAVDT 类别诊断',
  'UAVDT per-class AP in the registered exports.',
  ['Run','Car AP','Truck AP','Bus AP'],
  [['RT-DETR-L baseline',...['car','truck','bus'].map(c=>pct(uBase.val.class_metrics[c].map50_95))],['Joint export',...['car','truck','bus'].map(c=>pct(uFull.class_metrics[c].map50_95))]],
  '与 U1 相同的评估清单问题仍待复核。truck 的低 AP 必须保留讨论；不同样本分布下的类别差值不能归因于模块。',
  'The common-manifest caveat of U1 applies. Low truck AP should be discussed; differences across unmatched samples cannot be attributed to individual components.',
  [summaryPath+'#H11',summaryPath+'#H12']);
// Register every referenced local source and preserve immutable input hashes in the package.
for(const t of tables) for(const ref of t.sources) read(ref.split('#')[0]);
const fmt=x=>x==null?'—':typeof x==='number'?(Number.isInteger(x)?String(x):x.toFixed(3)):String(x);
const mdTable=t=>`## ${t.id} ${t.title}\n\n| ${t.headers.join(' | ')} |\n| ${t.headers.map(()=> '---').join(' | ')} |\n${t.rows.map(r=>'| '+r.map(fmt).join(' | ')+' |').join('\n')}\n\n${t.note}\n\n证据：${t.sources.map(s=>{const [p,id]=s.split('#');return '['+path.basename(p)+(id?' · '+id:'')+']('+path.posix.relative('paper_material/submission_tables_20260915',p)+')';}).join('；')}\n`;
fs.mkdirSync(dest,{recursive:true});
const write=(f,s)=>fs.writeFileSync(path.join(dest,f),s,'utf8');
for(const [file,title,groups] of [['MAIN_TABLES_ZH.md','正文：主结果与大模块消融',['main']],['INTERNAL_ABLATIONS_ZH.md','内部设计消融',['internal']],['SUPPLEMENTARY_ZH.md','支持性检验',['support']],['UAVDT_PENDING_ZH.md','第二数据集待核对表',['pending']]]) write(file,`# ${title}\n\n全部 AP、P、R 按百分数显示；差值单位为 pp。数值由证据文件生成，保留三位小数。\n\n`+tables.filter(t=>groups.includes(t.group)).map(mdTable).join('\n'));
write('tables.json',JSON.stringify({generated_from:'registered evidence as of 2026-09-15',unit:'percentage, deltas in percentage points',tables},null,2)+'\n');
write('provenance.json',JSON.stringify({inputs:Object.fromEntries(inputs),verification:{formal100_csv_best_and_final:'pass',recorded_protocol_fields_matched:matchedKeys,excluded_path_identity_fields:[...excluded],shared_fdr_bpdd_yaml_loss_block:'pass',full_source_active_path_equivalence:'not_verified',retrospective_authority_id_is_not_experimental_proof:true},omitted:{unrelated:['H01','H02','H03','H05','H06','H07','H08','H09','H10','H13','P09','P10'],legacy_only:['P01','P02','P03','P04','P05','P06','P07','P08','P11','P12','V05','V07','V08','H04']},criteria_binding_unavailable:true},null,2)+'\n');
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
write('preview.html',`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>论文实验表</title><style>body{font:16px/1.65 system-ui,sans-serif;background:#f3f5f7;color:#202c39;margin:0}main{max-width:1200px;margin:auto;padding:32px}h1{margin-bottom:6px}section{background:white;padding:24px;margin:24px 0;border-radius:12px;overflow:auto}table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}th,td{text-align:right;border-bottom:1px solid #e4e8ed;padding:9px 12px;white-space:nowrap}th:first-child,td:first-child{text-align:left}th{background:#eef3f7}p{color:#485b6b}nav a{margin-right:18px;color:#17618f}.pending{border-left:5px solid #b4832b}@media print{body{background:white}main{padding:0}section{break-inside:avoid;margin:12px 0}nav{display:none}}</style><main><h1>论文实验表 · 2026-09-15</h1><p>主方法：LRS-GFDR + Capacity-BPDD-v3-Safe + FIA。AP / P / R 单位为 %，增量为 pp。</p><nav>${tables.map(t=>`<a href="#${t.id}">${t.id}</a>`).join('')}</nav>${tables.map(t=>`<section id="${t.id}" class="${t.group}"><h2>${esc(t.id+' '+t.title)}</h2><table><thead><tr>${t.headers.map(h=>`<th>${esc(h)}</th>`).join('')}</tr></thead><tbody>${t.rows.map(r=>`<tr>${r.map(c=>`<td>${esc(fmt(c))}</td>`).join('')}</tr>`).join('')}</tbody></table><p>${esc(t.note)}</p></section>`).join('')}</main></html>`);
const tx=s=>String(s).replace(/[&%$#_{}]/g,c=>'\\'+c).replaceAll('—','--');
write('tables.tex','% Requires \\usepackage{booktabs}; English captions; AP values are percentages.\n% T3/T4 are design comparisons; source equivalence is not fully verified.\n'+tables.filter(t=>t.group!=='pending').map(t=>`\n\\begin{table*}[t]\n\\centering\n\\small\n\\caption{${tx(t.caption_en+' '+t.caption_note_en)}}\n\\label{tab:${t.id.toLowerCase()}}\n\\begin{tabular}{l${'r'.repeat(t.headers.length-1)}}\n\\toprule\n${t.headers.map(tx).join(' & ')} \\\\\n\\midrule\n${t.rows.map(r=>r.map(c=>tx(fmt(c))).join(' & ')+' \\\\').join('\n')}\n\\bottomrule\n\\end{tabular}\n\\end{table*}\n`).join(''));
assert.equal(tables.length,8);
assert(Math.abs(diff(R('V13').val.map50_95,R('V12').val.map50_95)-0.832)<1e-8);
console.log(JSON.stringify({tables:tables.length,rows:tables.reduce((n,t)=>n+t.rows.length,0),sources:inputs.size,output:dest,checks:'passed',test_fia_delta_pp:diff(F.mAP50_95,B.mAP50_95),full_parameters:fReport.parameters},null,2));

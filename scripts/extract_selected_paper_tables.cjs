// Extract the short-paper selection from the existing evidence-backed tables.
// Run build_submission_tables.cjs first when the registered results change.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const source = 'paper_material/submission_tables_20260915/tables.json';
const outRel = 'paper_material/submission_tables_20260915/selected';
const out = path.join(root, outRel);
const bytes = fs.readFileSync(path.join(root, source));
const original = JSON.parse(bytes).tables;
const get = id => { const t = original.find(t => t.id === id); assert(t, id); return t; };
const select = (id, indices) => {
  const t = get(id);
  return {source_id:id, headers:indices.map(i=>t.headers[i]), rows:t.rows.map(row=>indices.map(i=>row[i])),
    note:t.note, enNote:t.caption_note_en, sources:t.sources};
};
const tables = [
  {number:'1',file:'table_1_external',group:'main',title:'VisDrone test 外部方法比较',
   caption:'Comparison on the project VisDrone test split under a common evaluator.',panels:[select('T1',[0,1,2,3,4,5,6,7])]},
  {number:'2',file:'table_2_components',group:'main',title:'VisDrone val 大模块组合消融',
   caption:'Component comparison on native VisDrone validation results.',panels:[select('T2',[0,1,2,3,4,5,6,7])]},
  {number:'3',file:'table_3_internal',group:'main',title:'内部设计对照：定位设计与 BPDD 联合兼容性',
   caption:'Internal design comparisons on native VisDrone validation results.',
   panels:[{...select('T3',[0,1,2,3,4]),title:'(a) 定位设计：Clean、几何修正与 LRS',enTitle:'(a) Localization design'},
           {...select('T4',[0,1,2,3]),title:'(b) BPDD 设计与 FIA 联合兼容性',enTitle:'(b) BPDD recipe and FIA compatibility'}]},
  {number:'S1',file:'table_s1_test',group:'supplement',title:'FIA 开关的独立 test 检验',
   caption:'Held-out test comparison of the current FIA-off/on pair.',panels:[select('S1',[0,1,2,3,4,5,6])]},
  {number:'S2',file:'table_s2_final',group:'supplement',title:'best 与 final 的共同评估结果',
   caption:'Best and final checkpoints under the common evaluator.',panels:[select('S2',[0,1,2,3])]},
  {number:'4',file:'table_4_uavdt_DRAFT',group:'pending',title:'UAVDT 总体结果（预留，待统一评估复核）',
   caption:'DRAFT ONLY: UAVDT reported results pending evaluation alignment.',panels:[select('U1',[0,1,2,3,4,5])]},
  {number:'S3',file:'table_s3_uavdt_DRAFT',group:'pending',title:'UAVDT 逐类别 AP（补充表预留）',
   caption:'DRAFT ONLY: UAVDT per-class reported AP pending evaluation alignment.',panels:[select('U2',[0,1,2,3])]}
];
const fmt = v => v == null ? '—' : typeof v === 'number' ? v.toFixed(3) : v;
const cell = v => v === 'on' ? '✓' : v === 'off' ? '—' : fmt(v);
const mdGrid = p => '| '+p.headers.join(' | ')+' |\n| '+p.headers.map(()=> '---').join(' | ')+' |\n'+p.rows.map(row=>'| '+row.map(cell).join(' | ')+' |').join('\n');
const mdTable = t => `## 表 ${t.number}　${t.title}\n\n`+t.panels.map(p=>
  (p.title?'### '+p.title+'\n\n':'')+mdGrid(p)+'\n\n表注：'+p.note+'\n\n').join('');
const tx = s => String(s).replace(/\\/g,'\\textbackslash{}').replace(/[&%$#_]/g,c=>'\\'+c)
  .replaceAll('—','--').replaceAll('✓','+');
const texCell = v => tx(v === 'on' ? '+' : v === 'off' ? '--' : fmt(v));
const texGrid = p => '\\begin{tabular}{l'+'r'.repeat(p.headers.length-1)+'}\n\\toprule\n'+
  p.headers.map(tx).join(' & ')+' \\\\\n\\midrule\n'+p.rows.map(row=>row.map(texCell).join(' & ')+' \\\\').join('\n')+
  '\n\\bottomrule\n\\end{tabular}\n';
const texTable = t => `% Source tables: ${t.panels.map(p=>p.source_id).join(', ')}\n`+
  (t.group==='pending'?'% DRAFT ONLY: do not include before evaluation reconciliation.\n':'')+
  '\\begin{table*}[t]\n\\centering\n\\small\n\\setlength{\\tabcolsep}{4pt}\n'+
  '\\caption{'+tx(t.caption)+'}\n\\label{tab:selected-'+t.number.toLowerCase()+'}\n'+
  t.panels.map(p=>(p.enTitle?'\\textbf{'+tx(p.enTitle)+'}\\par\\smallskip\n':'')+texGrid(p)+
    '\\par\\smallskip\n\\begin{minipage}{0.97\\textwidth}\\footnotesize '+tx(p.enNote)+'\\end{minipage}\n\\par\\medskip\n').join('')+
  '\\end{table*}\n';
fs.mkdirSync(out,{recursive:true});
const write = (name,text) => fs.writeFileSync(path.join(out,name),`${text.trimEnd()}\n`,'utf8');
const prefix = '# 论文选用表格\n\nAP 表示 mAP50–95；P、R 和 AP 的单位均为 %，差值单位为 pp。G=LRS-GFDR，B=Capacity-BPDD-v3-Safe，F=FIA P3-only。原生 val 与共同 test 分别标明，不混排指标。数值沿用源表的三位小数显示精度。\n\n';
write('MAIN_TABLES.md',prefix+tables.filter(t=>t.group==='main').map(mdTable).join('\n')+
  '\n## 正文配套说明\n\nFIA 开关的 test AP 差为 +0.118 pp（补充表 S1），小于原生 val 的 +0.832 pp；两项结果建议在大模块消融段落一并交代。内部对照保留几何修正与 BPDD-only 的下降结果；这些表不提供单种子之外的统计显著性证据。\n');
write('SUPPLEMENTARY_TABLES.md',prefix+tables.filter(t=>t.group==='supplement').map(mdTable).join('\n'));
write('UAVDT_TABLE_4_DRAFT.md',prefix+'**状态：表 4 和 S3 已搭好并填入原报告值，尚未纳入正文 LaTeX。待同一验证清单复评完成后更新。**\n\n'+tables.filter(t=>t.group==='pending').map(mdTable).join('\n'));
for(const t of tables) write(t.file+'.tex',texTable(t));
for(const [name,group] of [['main_tables.tex','main'],['supplementary_tables.tex','supplement']])
  write(name,'% Requires \\usepackage{booktabs}. Full-width floats for two-column conference layouts.\n'+tables.filter(t=>t.group===group).map(texTable).join('\n'));
const manifest = {source,source_sha256:crypto.createHash('sha256').update(bytes).digest('hex'),
  main_table_count:3,main_panel_count:4,groups:tables.map(t=>({number:t.number,title:t.title,group:t.group,
    file:t.file+'.tex',source_ids:t.panels.map(p=>p.source_id),sources:t.panels.flatMap(p=>p.sources)})),
  validation:{extraction_only:true,new_evaluation:false,latex_compilation:'not_performed',uavdt_not_in_main:true}};
write('selection_manifest.json',JSON.stringify(manifest,null,2)+'\n');
write('README.md',`# 论文选用表格：正文 3 张 + 补充 2 张 + UAVDT 预留\n\n`+
  `先打开 [正文选用表](MAIN_TABLES.md) 或 [预览页](preview.html)。写作时可直接复制表格；英文 LaTeX 入口为 [main_tables.tex](main_tables.tex)。\n\n`+
  `| 论文编号 | 内容 | 来源 | 放置位置 |\n| --- | --- | --- | --- |\n`+
  tables.map(t=>`| ${t.number} | ${t.title} | ${t.panels.map(p=>p.source_id).join(' + ')} | ${t.group==='main'?'正文':t.group==='supplement'?'补充材料':'待复评预留'} |`).join('\n')+
  `\n\n- [正文 3 张表](MAIN_TABLES.md)：表 3 含两个独立子表，分别回答定位设计和蒸馏兼容性问题。\n`+
  `- [补充表 S1–S2](SUPPLEMENTARY_TABLES.md)：test 检验、best/final 稳健性。\n`+
  `- [UAVDT 表 4 / S3 草稿](UAVDT_TABLE_4_DRAFT.md)：当前联合方法名称保留；复评前不写严格 +1.36 pp 增益。\n`+
  `- [来源清单](selection_manifest.json)：原表编号和证据路径，数值没有重新计算或替换。\n\n`+
  `LaTeX 需要 booktabs；main_tables.tex 已合并正文三张表，也可以选用 table_*.tex 单表文件。不要同时导入合并文件和单表文件。`+
  `表 3 的两个子表共用一个编号；补充材料单独排号。尚未在目标会议模板中编译，最终字号和浮动位置需结合正文检查。\n\n`+
  `从仓库根目录执行 node scripts/build_submission_tables.cjs，再执行 node scripts/extract_selected_paper_tables.cjs，可重建全部选表。\n`);
const html = s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const render = t=>`<section class="${t.group}"><h2>表 ${t.number}　${html(t.title)}</h2>`+t.panels.map(p=>
  (p.title?'<h3>'+html(p.title)+'</h3>':'')+'<div class="grid"><table><thead><tr>'+p.headers.map(h=>'<th>'+html(h)+'</th>').join('')+
  '</tr></thead><tbody>'+p.rows.map(r=>'<tr>'+r.map(v=>'<td>'+html(cell(v))+'</td>').join('')+'</tr>').join('')+
  '</tbody></table></div><p class="note">'+html(p.note)+'</p>').join('')+'</section>';
write('preview.html','<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'+
  '<title>论文选用表格</title><style>body{font:16px/1.65 "Microsoft YaHei",sans-serif;color:#202833;margin:0;background:#f6f7f9}main{max-width:1160px;margin:auto;padding:30px}section{background:white;padding:24px;margin:22px 0;border:1px solid #dce1e6;border-radius:8px}.grid{overflow-x:auto}table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}th,td{padding:8px 10px;text-align:right;white-space:nowrap;border-bottom:1px solid #ddd}th:first-child,td:first-child{text-align:left}thead{border-top:2px solid #222;border-bottom:1px solid #222}tbody tr:last-child{border-bottom:2px solid #222}.note{font-size:13px;color:#48535f}h2{font-size:20px}h3{font-size:16px}.pending{border-left:4px solid #a57b23}a{color:#215b87}@media print{body{background:white}main{padding:0}section{break-inside:avoid;border:0;padding:12px 0}.pending{display:none}nav{display:none}}</style></head><body><main>'+
  '<h1>论文选用表格</h1><p>正文 3 张，内部设计为双子表；补充 2 张。AP、P、R 单位为 %。UAVDT 表预留，打印时暂不包含。</p><nav><a href="MAIN_TABLES.md">正文 Markdown</a> · <a href="main_tables.tex">正文 LaTeX</a> · <a href="UAVDT_TABLE_4_DRAFT.md">UAVDT 草稿</a></nav>'+tables.map(render).join('')+'</main></body></html>');
// Ensure each extracted value is identical to its original table field.
for(const t of tables) for(const p of t.panels) {
  const src=get(p.source_id); assert.equal(p.rows.length,src.rows.length);
  for(let i=0;i<p.rows.length;i++) for(let k=0;k<p.headers.length;k++)
    assert.deepEqual(p.rows[i][k],src.rows[i][src.headers.indexOf(p.headers[k])]);
  for(const ref of p.sources) assert(fs.existsSync(path.join(root,ref.split('#')[0])),ref);
}
const mainTex=fs.readFileSync(path.join(out,'main_tables.tex'),'utf8');
assert.equal((mainTex.match(/\\begin\{table\*\}/g)||[]).length,3);
assert(!mainTex.includes('selected-4'));
console.log(JSON.stringify({output:out,main_tables:3,internal_panels:2,supplementary_tables:2,pending_tables:2,source_value_comparison:'pass',source_paths:'pass',latex_compiled:false},null,2));

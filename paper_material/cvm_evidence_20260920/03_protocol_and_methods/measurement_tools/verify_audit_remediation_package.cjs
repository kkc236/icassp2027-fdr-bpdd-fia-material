// Check only this remediation's document entry points and frozen evidence inputs.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const docs=[
 'paper_material/README_ZH.md',
 'paper_material/PAPER_WRITING_HANDOFF_20260915_ZH.md',
 'paper_material/methods/CURRENT_JOINT_METHOD_ZH.md',
 'paper_material/results/CURRENT_COMPLEXITY_ZH.md',
 'paper_material/results/CURRENT_FULL_GFLOPS_ZH.md',
 'paper_material/results/CURRENT_BATCH8_EFFICIENCY_ZH.md',
 'paper_material/reviews/AUDIT_REMEDIATION_20260915_ZH.md',
 'paper_material/evidence/audit_remediation_20260915/SOURCE_PAIR_RESOLUTION_ZH.md',
 'paper_material/experiments/ABLATION_AND_SCALE_DESIGN_ZH.md',
 'paper_material/submission_tables_20260915/README.md',
 'paper_material/submission_tables_20260915/PAPER_PLAN_ZH.md',
 'paper_material/submission_tables_20260915/selected/README.md',
 'paper_material/submission_tables_20260915/selected/MAIN_TABLES.md',
 'paper_material/submission_tables_20260915/selected/SUPPLEMENTARY_TABLES.md'];
let links=0;const checked={};
for(const relative of docs) {
 const bytes=fs.readFileSync(path.join(root,relative));checked[relative]=sha(bytes);
 for(const match of bytes.toString('utf8').matchAll(/\]\(([^\n]+?)\)/g)) {
   let link=match[1].replace(/^<|>$/g,'').split('#')[0];
   if(!link||/^(?:https?:|mailto:)/i.test(link))continue;
   link=decodeURIComponent(link);
   const target=path.resolve(path.dirname(path.join(root,relative)),link);
   assert(fs.existsSync(target),relative+' -> '+link);links++;
 }
}
const provenance=JSON.parse(fs.readFileSync(path.join(root,'paper_material/submission_tables_20260915/provenance.json')));
for(const [relative,expected] of Object.entries(provenance.inputs))assert.equal(sha(fs.readFileSync(path.join(root,relative))),expected,relative);
const report={status:'pass',document_count:docs.length,local_links_checked:links,
 table_input_count:Object.keys(provenance.inputs).length,document_sha256:checked,
 source_and_initialization_scope:'V12/V13 only',uavdt:'deferred_by_user_separate_server',
 training_started:false,github_pushed:false,raw_metrics_modified:false,
 whole_bpdd_module_policy:true,
 full_flops_status:'complete_under_declared_convention_640_batch1_mac2',
 scientific_limits:['KD-only causality not claimed; whole BPDD module scope','all historical pairs not certified','single seed','test historically used for diagnosis','cross-recipe external comparison'],
 claim:'document/evidence package verification, not publication acceptance certification'};
fs.writeFileSync(path.join(root,'paper_material/evidence/audit_remediation_20260915/package_verification.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({status:report.status,documents:docs.length,links,table_inputs:report.table_input_count}));

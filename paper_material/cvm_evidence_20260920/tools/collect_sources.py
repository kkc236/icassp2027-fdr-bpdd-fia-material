"""Copy explicitly selected local evidence, retaining bytes and provenance. No model execution."""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess, os

OUT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--workspace', required=True)
parser.add_argument('--uavdt-zip', required=True)
args = parser.parse_args()
ROOT = Path(args.workspace).resolve()
MATERIAL = ROOT/'tmp-work/icassp2027-fdr-bpdd-fia-material'
MANUSCRIPT = ROOT/'output/cvm_uavdt_revision_20260919'
copied, omitted = [], []
SKIP = {'.git','__pycache__','.pytest_cache','node_modules','.venv','qa'}
def native(p):
    s=str(Path(p).resolve())
    return '\\\\?\\'+s if os.name=='nt' and not s.startswith('\\\\?\\') else s
def sha(p):
    h=hashlib.sha256()
    with open(native(p),'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def copy_file(src, relative):
    src=Path(src)
    if not src.is_file(): raise FileNotFoundError(src)
    if src.is_symlink(): raise ValueError('Symlink is not a frozen file: '+str(src))
    dst=OUT/relative
    assert dst.resolve().is_relative_to(OUT.resolve())
    digest=sha(src)
    if dst.exists():
        assert sha(dst)==digest, f'Conflicting destination {dst}'
    else:
        Path(native(dst.parent)).mkdir(parents=True,exist_ok=True)
        shutil.copy2(native(src),native(dst))
    assert sha(dst)==digest
    copied.append({'path':dst.relative_to(OUT).as_posix(),
                   'source':src.as_posix(),
                   'source_workspace_relative':src.relative_to(ROOT).as_posix() if src.is_relative_to(ROOT) else None,
                   'bytes':src.stat().st_size,'sha256':digest})

def copy_tree(src, relative, skip=SKIP):
    src=Path(src)
    assert src.is_dir(),src
    for f in sorted(src.rglob('*')):
        if not f.is_file(): continue
        parts=f.relative_to(src).parts
        if any(x in skip for x in parts) or f.suffix in {'.pyc','.pyo','.pt','.pth','.engine','.onnx'}:
            omitted.append({'source':f.as_posix(),'reason':'cache, transient build output, or large model payload'});continue
        copy_file(f,Path(relative)/f.relative_to(src))

# Exact current manuscript, including its pre-existing standalone delivery archives.
copy_tree(MANUSCRIPT,'01_manuscript')
for name in ['final_compile.log','extracted_text.txt']:
    copy_file(MANUSCRIPT/'qa'/name,'06_audits/manuscript_qa/'+name)
copy_file(ROOT/'output/CURRENT_SUBMISSION_TARGET.json','00_index/current_submission_target.json')
copy_file(ROOT/'output/cvm2027_preparation_20260916/SUBMISSION_TARGET.json','00_index/submission_target_record.json')

# Raw evaluation, timing, counter, recovered-source and source-pair records.
copy_tree(MATERIAL/'paper_material/evidence','02_evidence',skip={'.git','__pycache__','.pytest_cache'})
copy_tree(ROOT/'tmp/all_experiments_20260915/server_runs/visdrone-v2-lrs-gfdr-fia-20260909/formal-seed0-lrs_gfdr_fia-v1','02_evidence/visdrone_g_f_training_20260909')
copy_file(ROOT/'tmp/all_experiments_20260915/server-inventory.tar.gz','02_evidence/visdrone_g_f_training_20260909/original_server_inventory.tar.gz')
for name in ['fdr-vs-control-strict-final-paper-metrics.json','fdr-formal-seed0-control-d97e1eb7-epoch-0100.json']:
    copy_file(ROOT/'tmp-work/baseline-800-inputs'/name,'02_evidence/baseline_strict_val/'+name)
copy_file(MATERIAL/'docs/FDR_RTDETR_L_STRICT_CONTROL_AND_RESULTS_2026-08-09_ZH.md','02_evidence/baseline_strict_val/FDR_RTDETR_L_STRICT_CONTROL_AND_RESULTS_2026-08-09_ZH.md')
for name in ['methods','experiments']:
    copy_tree(MATERIAL/'paper_material'/name,'03_protocol_and_methods/'+name)
copy_tree(MATERIAL/'paper_material/results','07_historical_context/results')
copy_tree(MATERIAL/'paper_material/reviews','06_audits/material_reviews')
copy_file(MATERIAL/'paper_material/PAPER_WRITING_HANDOFF_20260915_ZH.md','07_historical_context/PAPER_WRITING_HANDOFF_20260915_ZH.md')
for name in ['count_inference_flops.py','measure_batch8_efficiency.py','trace_current_model_ops.py',
             'attest_full_flops_runtime.py','verify_recovered_capacity_pair.py','verify_audit_remediation_package.cjs',
             'build_batch8_efficiency_report.cjs','build_full_flops_report.cjs']:
    copy_file(MATERIAL/'scripts'/name,'03_protocol_and_methods/measurement_tools/'+name)
for name in ['test_batch8_efficiency.py','test_full_inference_flops.py','test_audit_remediation.py']:
    copy_file(MATERIAL/'tests'/name,'03_protocol_and_methods/measurement_tests/'+name)

# Current paper's original-source hashes include predecessor documents and CSVs.
for relative, expected in json.loads((MANUSCRIPT/'inputs/original_source_hashes.json').read_text(encoding='utf-8')).items():
    rel=relative.replace('\\','/')
    src=ROOT/rel
    assert sha(src)==expected, 'Original source changed: '+rel
    copy_file(src,'07_historical_context/original_sources/'+rel)

# Literature read for method, comparisons and layout; no new network acquisition.
copy_tree(ROOT/'downloads/CVM_Visual_Papers_2025_2026','04_literature/cvm_papers')
copy_tree(ROOT/'output/cvm_approved_architecture_20260919/research','04_literature/research_notes')
copy_tree(ROOT/'tmp-work/detr_presentation_review_20260916','04_literature/detr_reading')
for stem in ['detr','rt_detr','deformable_detr','dn_detr','dino']:
    for ext in ['pdf','txt']:
        copy_file(ROOT/'tmp/pdfs/detr_review'/f'{stem}.{ext}',f'04_literature/detr_foundations/{stem}.{ext}')
copy_tree(ROOT/'output/external_comparison_candidates_20260915','04_literature/comparison_candidates')
copy_tree(MATERIAL/'paper_material/literature','04_literature/material_literature')

# Figure derivation and later editable alternatives are explicitly separate.
copy_tree(ROOT/'output/cvm_approved_architecture_20260919/figure_revision','05_figures/approved_figure_history')
copy_tree(ROOT/'output/architecture_html_1to1_20260919','05_figures/editable_html_not_in_pdf')
for name in ['architecture_muted_final.png','README_ZH.md','recolor_prompt.txt','restore_mean_arrow_prompt.txt','source_record.json']:
    copy_file(ROOT/'output/architecture_palette_20260919'/name,'05_figures/muted_palette_not_in_pdf/'+name)
for name in ['ADVERSARIAL_AUDIT_ZH.md','EXPERIMENT_DESIGN_DECISIONS_ZH.md','NAMING_DECISIONS_ZH.md',
             'FEEDBACK_APPLICATION_ZH.md','EVIDENCE_FOCUS_DECISIONS_ZH.md','STRUCTURE_AND_REVISION_BLUEPRINT_ZH.md']:
    copy_file(ROOT/'output/cvm_approved_architecture_20260919'/name,'06_audits/editorial_history/'+name)

# Keep the complete user-provided ZIP and all real prediction plots for provenance.
copy_file(Path(args.uavdt_zip),'02_evidence/uavdt_user_package_20260919/original_server_results.zip')
copy_tree(ROOT/'output/uavdt_result_review_20260919','02_evidence/uavdt_user_package_20260919/review',skip={'.git','__pycache__','.pytest_cache'})
copy_file(MANUSCRIPT/'inputs/uavdt/author_confirmation.json','02_evidence/uavdt_user_package_20260919/author_confirmation.json')

def git_info(folder):
    def run(*a): return subprocess.check_output(['git','-C',str(folder),*a],text=True,encoding='utf-8',errors='replace').strip()
    return {'head':run('rev-parse','HEAD'),'branch':run('branch','--show-current'),
            'tracked_diff_sha256':hashlib.sha256(subprocess.check_output(['git','-C',str(folder),'diff','HEAD','--'])).hexdigest()}
origin={'date':'2026-09-20','scope':'Local evidence used by the current 13-page CVM manuscript; historical context and figure alternatives explicitly labeled',
        'source_workspace':ROOT.as_posix(),'source_manuscript':MANUSCRIPT.as_posix(),
        'source_repositories':{'workspace':git_info(ROOT),'material':git_info(MATERIAL)},
        'destination_branch':'codex/cvm-evidence-20260920','new_training':False,'new_model_evaluation':False,
        'copied_files':copied,'omitted_files':omitted}
(OUT/'00_index').mkdir(exist_ok=True)
(OUT/'00_index/source_origins.json').write_text(json.dumps(origin,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'copied_files':len(copied),'bytes':sum(x['bytes'] for x in copied),'omitted_files':len(omitted)},ensure_ascii=False))

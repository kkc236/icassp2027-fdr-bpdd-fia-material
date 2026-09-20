"""Package the reviewed UAVDT manuscript and verify portable assembly."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys, tempfile, zipfile

R = Path(__file__).resolve().parent
ROOT = R.parent.parent
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

v = json.loads((R/'verification.json').read_text(encoding='utf-8'))
assert v['status'] == 'compiled_and_content_verified'
assert v['pages'] < 14 and v['visual_review'] == f"passed_all_{v['pages']}_pages"
assert v['main_tex_sha256'] == sha(R/'main.tex')
assert v['pdf_sha256'] == sha(R/'MANUSCRIPT_CVM.pdf')

roots = ['main.tex','MANUSCRIPT_CVM.pdf','README_ZH.md','REVISION_NOTES_ZH.md',
         'DEPENDENCIES.md','requirements-drawing.txt','requirements-verification.txt',
         'build.py','verify.py','package_release.py','compile.ps1','compile.sh',
         'build_manifest.json','verification.json','references.bib','cvm.bst',
         'cvm.sty','cvm_eso.sty','eso-pic.sty']
paths = [R/n for n in roots]
for folder in ['source','inputs','official_template','assets','figures','reviews']:
    paths.extend(p for p in (R/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
paths.append(R/'qualitative/gt_reconstructed/instances_val.json.gz')
assert len(paths) == len(set(paths)) and all(p.is_file() for p in paths)
zip_path = R/'CVM2027_SUBMISSION_READY.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(paths): z.write(p,p.relative_to(R).as_posix())
figzip = R/'CVM_FIGURES.zip'
with zipfile.ZipFile(figzip,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted((R/'assets').iterdir()):
        if p.is_file(): z.write(p,p.relative_to(R).as_posix())
    z.write(R/'source/figure_overview.tex','source/figure_overview.tex')

dest=Path(tempfile.mkdtemp(prefix='portable_uavdt_',dir=R/'qa'))
with zipfile.ZipFile(zip_path) as z:
    assert z.testzip() is None
    for name in z.namelist(): assert (dest/name).resolve().is_relative_to(dest.resolve())
    z.extractall(dest)
run=subprocess.run([sys.executable,'build.py'],cwd=dest,capture_output=True,text=True,errors='replace',timeout=120)
assert run.returncode==0,run.stdout+run.stderr
assert sha(dest/'main.tex')==sha(R/'main.tex')
assert sha(dest/'MANUSCRIPT_CVM.pdf')==sha(R/'MANUSCRIPT_CVM.pdf')
with zipfile.ZipFile(figzip) as z: assert z.testzip() is None

report={'revision':R.name,'status':'reviewed_and_packaged','pages':v['pages'],
        'tables':v['tables'],'figures':v['figures'],'references':v['references'],
        'main_tex_sha256':sha(R/'main.tex'),'pdf_sha256':sha(R/'MANUSCRIPT_CVM.pdf'),
        'zip':zip_path.as_posix(),'zip_sha256':sha(zip_path),'zip_entries':len(paths),
        'figure_zip':figzip.as_posix(),'portable_assembly_verified':True,
        'standalone_compile_verified':True,'visual_review':v['visual_review'],
        'uavdt':v['uavdt'],'new_training':False,'new_model_evaluation':False,
        'external_submission_performed':False,'pending_metadata':['real CVM paper ID','UAVDT actual checkpoint/configuration record','UAVDT official split mapping']}
(R/'RELEASE_METADATA.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')

target_file=ROOT/'output/cvm2027_preparation_20260916/SUBMISSION_TARGET.json'
target=json.loads(target_file.read_text(encoding='utf-8'))
review={'updated':'2026-09-19','active_revision':R.name,
        'base_revision':'cvm_approved_architecture_20260919',
        'scope':'Added author-confirmed Full UAVDT results with protocol and source-snapshot qualifications; existing VisDrone values unchanged',
        'scientific_results_changed':True,'new_dataset':'UAVDT','architecture_vector_source':False}
target.update({'stage':'UAVDT added; author-confirmed Full identity; provenance and paper ID pending',
               'existing_latex_source':(R/'main.tex').as_posix(),'manuscript_pdf':(R/'MANUSCRIPT_CVM.pdf').as_posix(),
               'project_zip':zip_path.as_posix(),'verification':(R/'verification.json').as_posix(),
               'pages_including_references':v['pages'],'tables':v['tables'],'figures':v['figures'],'references':v['references'],
               'visual_revision':(R/'REVISION_NOTES_ZH.md').as_posix(),'figure_assets':figzip.as_posix(),
               'external_submission_performed':False,'layout_review':review,'uavdt':v['uavdt']})
target_file.write_text(json.dumps(target,indent=2,ensure_ascii=False),encoding='utf-8')
pointer={'active_target':'CVM 2027','target_record':target_file.as_posix(),'stage':target['stage'],
         'current_manuscript':(R/'main.tex').as_posix(),'current_pdf':(R/'MANUSCRIPT_CVM.pdf').as_posix(),
         'current_project_zip':zip_path.as_posix(),'current_figure_zip':figzip.as_posix(),'layout_review':review}
(ROOT/'output/CURRENT_SUBMISSION_TARGET.json').write_text(json.dumps(pointer,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))

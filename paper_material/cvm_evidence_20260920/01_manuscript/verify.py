"""Independent frozen-value audit and clean-directory standalone compilation."""
from pathlib import Path
from decimal import Decimal as D
import hashlib,json,re,shutil,subprocess,tempfile
from pypdf import PdfReader

OUT=Path(__file__).resolve().parent
ROOT=OUT.parent.parent
PY=Path('C:/Users/16946/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe')
COMPILER=shutil.which('pdflatex') or 'C:/Users/16946/AppData/Local/Programs/MiKTeX/miktex/bin/x64/pdflatex.exe'
formulation_run=subprocess.run([str(PY),str(OUT/'source/check_formulation.py')],cwd=OUT,capture_output=True,text=True,timeout=30)
assert formulation_run.returncode==0,formulation_run.stdout+formulation_run.stderr
formulation=json.loads((OUT/'reviews/formulation_checks.json').read_text(encoding='utf-8'))
assert formulation['status']=='passed' and formulation['check_count']==8
single=Path(tempfile.mkdtemp(prefix='single_file_',dir=OUT/'qa'))
shutil.copy2(OUT/'main.tex',single/'main.tex')
assert [p.name for p in single.iterdir()]==['main.tex']
for run in range(1,4):
    p=subprocess.run([COMPILER,'-interaction=nonstopmode','-halt-on-error','-file-line-error','-no-shell-escape','-recorder','main.tex'],cwd=single,capture_output=True,text=True,errors='replace',timeout=180)
    (single/f'pass-{run}.txt').write_text(p.stdout+p.stderr,encoding='utf-8')
    assert p.returncode==0,p.stdout[-3500:]
log=(single/'main.log').read_text(encoding='utf-8',errors='replace')
for forbidden in ('Overfull \\hbox','Overfull \\vbox','undefined','Missing character','LaTeX Error','Rerun to get cross-references'):
    assert forbidden not in log,forbidden+'\n'+ '\n'.join(x for x in log.splitlines() if forbidden in x)
tex=(OUT/'main.tex').read_text(encoding='ascii')
body=tex[tex.rindex(r'\begin{document}'):]
tables=re.findall(r'\\begin\{tabular\*\}.*?\\toprule(.*?)\\bottomrule',body,re.S)
expected=[
 [],
 [['17.743','32.254','17.565'],['23.604','41.241','23.546']],
 [['22.554','38.656','22.720','13.338'],['24.133','41.885','24.044','14.575'],['22.679','38.940','22.713','13.478'],['24.229','42.009','24.208','14.618']],
 [['300','35.3','29.3','47.4'],['300','2.59','31.2','50.5'],['100','35.244','30.109','49.890']],
 [['21.911','38.663'],['29.620','49.382'],['29.773','49.548'],['29.277','48.783'],['30.109','49.890']],
 [['29.078','48.473'],['29.696','49.320'],['29.361','49.130'],['29.620','49.382']],
 [['32.827','105.597','59.559','134.321'],['33.157','105.804','66.200','120.846'],['33.458','109.280','69.044','115.868'],['34.942','130.575','104.897','76.266'],['35.244','134.051','107.920','74.129']]
]
# Expected rows are indexed by scientific role, independent of narrative order.
efficiency_expected=expected[6]
combined=[a+c for a,c in zip(expected[4],efficiency_expected)]
sensitivity=json.loads((OUT/'inputs/external_sensitivity/EXTERNAL_SENSITIVITY.json').read_text(encoding='utf-8'))
sensitivity_expected=[[str(r['max_det']),r['display_dfine_ap'],r['display_full_ap'],r['display_delta_ap']] for r in sensitivity['comparisons']]
expected=[expected[1]+expected[2],expected[5],combined,sensitivity_expected,expected[3]]
uavdt_expected=[['14.12','24.21','14.97'],['16.96','29.16','17.50'],['+2.84','+4.95','+2.53'],['30.38','34.65','+4.27'],['2.58','4.06','+1.48'],['9.40','12.19','+2.79']]
expected.insert(1,uavdt_expected)
assert len(tables)==6
checks=[]
for ti,(table,want) in enumerate(zip(tables,expected),1):
    got=[]
    for line in table.splitlines():
        if '&' not in line:continue
        vals=[]
        for cell in line.split('&')[1:]:
            cell=re.sub(r'\\textbf\{([^}]+)\}',r'\1',cell).strip().removesuffix(r'\\').strip()
            if re.fullmatch(r'[+-]?\d+(?:\.\d+)?',cell): vals.append(cell)
        if vals: got.append(vals)
    assert got==want,(ti,got,want)
    checks.extend({'table':ti,'row':ri+1,'values':row} for ri,row in enumerate(got))
differences=[('23.604','17.743','5.861'),('41.241','32.254','8.987'),('23.546','17.565','5.981'),('24.133','22.554','1.579'),('14.575','13.338','1.237'),('24.229','22.679','1.550'),('30.109','29.277','0.832'),('30.109','29.620','0.489'),('29.620','29.277','0.343'),('35.244','33.157','2.087'),('134.051','105.804','28.247'),('130.575','105.804','24.771'),('134.051','130.575','3.476')]
differences += [('29.620','21.911','7.709'),('30.109','21.911','8.198'),('29.620','29.078','0.542'),('29.696','29.361','0.335'),('29.620','29.361','0.259'),('29.696','29.620','0.076'),('33.157','32.827','0.330'),('105.804','105.597','0.207')]
differences += [('49.382','48.473','0.909')]
differences += [('29.696','29.078','0.618'),('49.382','49.320','0.062')]
# Check all original arithmetic, without requiring redundant prose for values visible in tables.
for a,b,c in differences:assert D(a)-D(b)==D(c)
table_only_differences={'0.335','0.259','0.618'}
for a,b,c in differences:
    if c not in table_only_differences: assert c in body
assert body.index(r'\subsection{Complete-system comparisons}') < body.index(r'\subsection{Localization design analysis}') < body.index(r'\subsection{Components and computational cost}')
assert body.index(r'\label{tab:lrsversions}') < body.index(r'\appendix')
assert 'does not isolate the selective supervision rule' in body
assert round((D('134.051')-D('105.804'))/D('105.804')*100,2)==D('26.70')
for row in efficiency_expected: assert abs(8000/float(row[2])-float(row[3]))<.002
assert body.count(r'\begin{equation}')==11
assert body.count(r'\begin{figure*}')==4
assert body.count(r'\begin{table}')==3 and body.count(r'\begin{table*}')==3
assert body.count(r'\bibitem{')==25
assert len(json.loads((OUT/'inputs/sampling_points.json').read_text())['normalized_offsets'])==41
citations=set(k for c in re.findall(r'\\cite\{([^}]+)\}',body) for k in c.split(','))
assert citations==set(re.findall(r'\\bibitem\{([^}]+)\}',body))
assert not re.search(r'\\(?:includegraphics|input|include|bibliography)\s*\{',body)
assert not any(s in body for s in ('30.592','42.788','43.849','85.415','86.075','23.622','23.621','23.219','24.111','archived component test','et al.'))
assert 'report validation results only' in body
assert 'not single-request response latency' in body
assert 'Native and common results are reported separately.' in body
assert 'test is not an untouched blind set' in body
assert 'fixed, detached incoming decoder reference box $r_0$' in body
assert 'GO-LSD' in body
assert 'not a guarantee of improved IoU after an optimizer update' in body
assert 'do not establish an independent benefit' in body
assert 'variability across training seeds remains unmeasured' in body
assert 'Full is the author-confirmed run' in body
assert 'exact configuration parity with VisDrone cannot be verified' in body
assert 'In the VisDrone configuration, Full processes 74.129 images/s' in body
identity=json.loads((OUT/'inputs/uavdt/author_confirmation.json').read_text(encoding='utf-8'))
assert identity['status']=='author_confirmed_full' and identity['checkpoint_verified'] is False
assert body.index(r'\subsection{Complete-system comparisons}') < body.index(r'\subsection{Results on UAVDT}') < body.index(r'\subsection{Localization design analysis}')
# Independently recover UAVDT values from the two original text exports.
uavdt_rows={}
for run in ['baseline-exp','exp']:
    lines=(OUT/'inputs/uavdt'/run/'paper_data.txt').read_text(encoding='utf-8').splitlines()
    rows={}
    for line in lines[2:]:
        parts=line.split()
        rows[parts[0]]=[D(s)*100 for s in parts[1:]]
    uavdt_rows[run]=rows
uavdt_base=uavdt_rows['baseline-exp'];uavdt_joint=uavdt_rows['exp']
for rows,want in [(uavdt_base,uavdt_expected[0]),(uavdt_joint,uavdt_expected[1])]:
    vals=rows[next(k for k in rows if k.startswith('all'))]
    assert [vals[5],vals[3],vals[4]]==[D(s) for s in want]
for c,want in zip(['car','truck','bus'],uavdt_expected[3:]):
    a,b=uavdt_base[c][5],uavdt_joint[c][5]
    assert [a,b,b-a]==[D(s) for s in want]
assert [D(b)-D(a) for a,b in zip(uavdt_expected[0],uavdt_expected[1])]==[D(s) for s in uavdt_expected[2]]
assert r'\bigl[v-\operatorname{sg}(v)\bigr]' in body
assert 'finite intermediate quantities' in body
assert 'quality ordering is preserved' in body
assert 'An all-zero group remains zero' in body
assert 'Direct expert losses also update' in body
assert '134.051' in body and '74.129 images/s' in body
assert 'Full FDR/FGL transfer' in body
assert 'full FDR/FGL transfer reference integrates' in body
assert 'Our localization variants' in body
assert 'Path redesign & \\checkmark & -- & -- & \\textbf{29.696}' in body
assert 'Clean-FDR' not in body and 'Original FDR' not in body
assert 'they do not remove the preliminary prediction head' in body
assert "retaining RT-DETR's stock denoising losses" in body
assert 'A fixed distribution frame follows FDR' in body
assert 'not the highest-AP row' in body
assert 'high-throughput batch processing' in body
assert 'UAV aerial monitoring' in body
assert 'proposed GCDL' in body
assert not re.search(r'\bLRS\b|LRS-GFDR|LRS-FDR|LRS-FGL|Layerwise Reliability Shrinkage',body)
assert 'Geometry-Constrained Distributional Localization' in body
assert 'layerwise quality shrinkage (LQS)' in body
assert 'LQS shrinks these loss weights' in body
assert 'FGL with LQS' in body
assert body.count('GO-LSD')>=1 and body.count('Fine-grained Distribution Refinement')>=1
assert 'not an unmodified D-FINE detector' in body
assert 'same image and layer' in body
assert 'Detector architecture and module details' in body
assert 'combined expert edge logits---base logits plus edge residual' in body
assert r'Figure~\ref{fig:overview}(b) details our reference' in body
assert r'The shared branch in Fig.~\ref{fig:overview}(c)' in body
assert r'\widetilde P_3' not in body
assert 'shows their dependencies within GCDL' in body
assert 'scratch-adapted reproduction' in body
assert 'accumulates eight physical batches after warmup' in body
assert 'physical and effective batch four without accumulation' in body
memory_note=json.loads((OUT/'inputs/dfine_batch_memory_note.json').read_text(encoding='utf-8'))
assert memory_note['status']=='author_confirmed_training_constraint'
assert memory_note['attempted_physical_batch_size']==8 and memory_note['used_physical_batch_size']==4
assert 'Under our D-FINE-L training setup, a physical batch size of eight caused an out-of-memory error on an RTX 4090 with 24 GB of GPU memory; we therefore reduced the physical batch size to four.' in body
assert 'equal epoch counts do not imply equal optimizer-update counts' in body
assert "Full's trainer accumulates" in body
assert 'evaluated EMA snapshot from actual loop epoch 100' in body
assert 'controlled six-layer decoder-wrapper test' in body
assert 'not an observed failure frequency' in body
assert 'smallest FP16 input underflows to zero' in body
import xml.etree.ElementTree as ET
geometry=OUT/'inputs/geometry_evidence'
case_name='test_decoder_geometry_survives_actual_cpu_bfloat16_autocast'
geometry_checks=[]
for name,failed in [('red.xml',True),('numerical.xml',False),('regression-final.xml',False)]:
    root=ET.parse(geometry/'archived_correctness'/name).getroot()
    matches=[t for t in root.iter('testcase') if t.get('name')==case_name]
    assert len(matches)==1
    case=matches[0]
    assert (case.find('failure') is not None)==failed
    assert case.find('error') is None and case.find('skipped') is None
    geometry_checks.append({'record':name,'controlled_BF16_case':'failure' if failed else 'pass'})
final_root=ET.parse(geometry/'archived_correctness/regression-final.xml').getroot()
nominal_cases=[t for t in final_root.iter('testcase') if t.get('name','').startswith('test_feasible_decode_retains_positive_xyxy_extent[') and '[0.0-' not in t.get('name','')]
assert len(nominal_cases)==8
assert all(not list(t) for t in nominal_cases)
center_case=[t for t in final_root.iter('testcase') if t.get('name')=='test_feasible_decode_keeps_ordinary_boxes_and_preserves_asymmetric_center']
assert len(center_case)==1 and not list(center_case[0])
geometry_identity=json.loads((geometry/'current_function_check.json').read_text())
assert geometry_identity['same_function_ast'] is True
import ast
for record in geometry_identity['comparison']:
    tree=ast.parse((OUT/record['file']).read_text(encoding='utf-8'))
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==record['function'])
    assert hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest()==record['ast_sha256']
import gzip
gt_bytes=gzip.decompress((OUT/'qualitative/gt_reconstructed/instances_val.json.gz').read_bytes())
gt_sha=hashlib.sha256(gt_bytes).hexdigest()
assert gt_sha=='92d2866fe6e6ff4c3101b82c01b7718eb78b3759399042c4501d893798fc8bfa'
gt=json.loads(gt_bytes)
assert len(gt['images'])==548 and len(gt['annotations'])==38759
# Independent area-threshold calculation; the figure builder uses equivalent sides.
motivation=json.loads((OUT/'inputs/motivation_profile.json').read_text())
image_sizes={im['id']:(D(str(im['width'])),D(str(im['height']))) for im in gt['images']}
area_bins=[0]*5
original_below_32=0
for ann in gt['annotations']:
    width,height=map(lambda x:D(str(x)),ann['bbox'][2:])
    image_width,image_height=image_sizes[ann['image_id']]
    area=width*height*D(640)**2/(image_width*image_height)
    index=sum(area>=D(edge)**2 for edge in [8,16,32,64])
    area_bins[index]+=1
    original_below_32+=width*height<D(32)**2
assert area_bins==[6856,14011,12414,4580,898]
assert original_below_32==26586
assert [row['count'] for row in motivation['input_scale_profile']['bins']]==area_bins
assert motivation['source']['uncompressed_json_sha256']==gt_sha
assert motivation['input_scale_profile']['below_32_px_count']==sum(area_bins[:3])==33281
motivation_figure=(OUT/'figures/motivation.tikz').read_text(encoding='ascii')
for count,row in zip(area_bins,motivation['input_scale_profile']['bins']):
    assert row['display_percentage']==f'{100*count/38759:.1f}'
    assert row['display_percentage']+r'\%' in motivation_figure
analytic_samples=0
for curve in motivation['analytic_iou']['curves']:
    width=curve['box_width_px']
    for sample in curve['samples']:
        shift=sample['displacement_px']
        # Explicit rectangle intersection with an arbitrary common height.
        left_a,right_a,left_b,right_b=0.0,width,shift,shift+width
        intersection=max(0.0,min(right_a,right_b)-max(left_a,left_b))*7.0
        union=2*width*7.0-intersection
        assert abs(intersection/union-sample['iou'])<1e-12
        analytic_samples+=1
assert analytic_samples==243
assert '85.9' in body and '0.778' in body and '0.939' in body and '70.7' in body
assert 'common evaluator' in motivation_figure and 'original-image COCO area ranges' in motivation_figure
assert 'not a measurement of model localization errors' in motivation_figure
assert 'not the $\\mathrm{AP}_s$ grouping' in body
method=body.split(r'\section{Method}',1)[1].split(r'\section{Experiments}',1)[0]
assert re.findall(r'\\subsection\{([^}]+)\}',method)==[
 'Framework and distributional representation','Geometry-feasible decoding',
 'Layerwise supervision allocation','Local visual extension','Training and inference']
assert re.findall(r'\\subsubsection\{([^}]+)\}',method)==['Box-conditioned expert','Selective localization transfer']
reference_records=json.loads((OUT/'inputs/references.json').read_text(encoding='utf-8'))
reference_map={r['key']:r for r in reference_records}
assert reference_map['bi2025fghdet']['type']=='article'
assert reference_map['bi2025fghdet']['doi']=='10.1007/s11390-025-5252-z'
assert reference_map['li2025dassf']['doi']=='10.1007/978-981-96-5809-1_12'
assert reference_map['li2025dassf']['type']=='inproceedings'
profile=OUT/'inputs/external_class_profile'
class_values=json.loads((profile/'numeric_values.json').read_text())
dfine_profile=json.loads((profile/'source/dfine_final_test.cap300.json').read_text())
full_profile=json.loads((profile/'source/joint_final_test.cap300.json').read_text())
assert dfine_profile['image_count']==full_profile['image_count']==1610
assert dfine_profile['max_det']==full_profile['max_det']==300
assert len(class_values['classes'])==10
class_figure=(OUT/'figures/external_classes.tikz').read_text(encoding='ascii')
class_metric_checks=[]
for row in class_values['classes']:
    key=str(row['category_id'])
    a=dfine_profile['per_class_AP'][key]*100
    b=full_profile['per_class_AP'][key]*100
    assert abs(row['dfine_final_test_AP']-a)<1e-10
    assert abs(row['full_final_test_AP']-b)<1e-10
    assert abs(row['delta_AP_points']-(b-a))<1e-10 and b>a
    assert row['display_dfine_AP']==f'{a:.2f}'
    assert row['display_full_AP']==f'{b:.2f}'
    assert row['display_delta_AP_points']==f'{b-a:+.2f}'
    for key in ['display_dfine_AP','display_full_AP','display_delta_AP_points']:
        assert '{'+row[key]+'}' in class_figure
    class_metric_checks.append({'category_id':row['category_id'],'AP_values':[a,b],'difference':b-a})
assert [r['category_id'] for r in class_values['classes']]==list(range(10))
assert '0.465' in body and '4.131' in body
assert 'differences use unrounded AP' in class_figure
# Independently recover every archived complete-detector AP and its display value.
sensitivity_checks=[]
sensitivity_dir=OUT/'inputs/external_sensitivity'
for row in sensitivity['comparisons']:
    raw=[]
    for prefix in ('dfine','joint'):
        name=f"{prefix}_{row['checkpoint']}_{row['split']}.cap{row['max_det']}.json"
        path=sensitivity_dir/name
        metric=json.loads(path.read_text(encoding='utf-8'))
        assert metric['image_count']==(548 if row['split']=='val' else 1610)
        assert metric['max_det']==row['max_det']
        assert metric['evaluator_version']=='2.0.11'
        raw.append(metric['mAP50_95']*100)
        # Verify against the original local evidence when available.
        original=ROOT/'tmp-work/icassp2027-fdr-bpdd-fia-material/paper_material/evidence/visdrone_dfine_l_external_20260913/common_evaluation_20260915'/name
        if original.exists(): assert path.read_bytes()==original.read_bytes()
    assert row['display_dfine_ap']==f'{raw[0]:.3f}'
    assert row['display_full_ap']==f'{raw[1]:.3f}'
    assert row['display_delta_ap']==f'{raw[1]-raw[0]:+.3f}'
    sensitivity_checks.append({'checkpoint':row['checkpoint'],'split':row['split'],'max_det':row['max_det'],'AP':raw,'delta':raw[1]-raw[0]})
assert len(sensitivity_checks)==8
assert {(r['checkpoint'],r['split'],r['max_det']) for r in sensitivity_checks}=={(c,s,d) for c in ('best','final') for s in ('val','test') for d in (100,300)}
assert 'neither independent trials nor evidence of statistical significance' in body
assert 'do not provide test-set component attribution' in body
name_map=json.loads((OUT/'inputs/publication_name_mapping.json').read_text(encoding='utf-8'))
assert len(name_map['rows'])==4 and name_map['higher_intermediate_AP_preserved'] is True
assert name_map['rows'][3]['display']=='GCDL' and name_map['rows'][3]['legacy_alias']=='LRS-GFDR'
assert name_map['legacy_source_and_run_identifiers_unchanged'] is True
assert all(x not in body for x in ['distributional reference $G$', '$G$: distributional reference', 'adopted distributional reference'])
import csv
raw_checks=[]
for name,ap,ap50 in [('historical_fdr_results.csv','29.078','48.473'),('clean_fdr_results.csv','29.696','49.320'),('geometry_fdr_results.csv','29.361','49.130'),('lrs_gfdr_results.csv','29.620','49.382')]:
    rows=list(csv.DictReader((OUT/'inputs'/name).open(encoding='utf-8-sig',newline='')))
    best=max(rows,key=lambda r:D(r['metrics/mAP50-95(B)']))
    assert D(best['metrics/mAP50-95(B)'])*100==D(ap)
    assert D(best['metrics/mAP50(B)'])*100==D(ap50)
    raw_checks.append({'file':name,'rows':len(rows),'best_epoch':best['epoch'],'AP':ap,'AP50':ap50})
track=(OUT/'inputs/lrs_track_results.md').read_text(encoding='utf-8')
assert '| 91 |' in track and '0.29361' in track and '0.49130' in track
assert '| 92 |' in track and '0.29620' in track and '0.49382' in track
assert r'\cvmfinalcopy' not in re.sub(r'%[^\n]*','',tex[tex.rindex(r'\documentclass'):tex.rindex(r'\begin{document}')])
def norm(p): return '\n'.join(x.rstrip() for x in p.read_text(encoding='ascii').splitlines())
for name in ('cvm.sty','cvm_eso.sty','eso-pic.sty'):
    assert norm(single/name)==norm(OUT/'official_template'/name)
pdf=PdfReader(single/'main.pdf')
assert len(pdf.pages)<14
assert not pdf.metadata.get('/Author')
page_text=[p.extract_text() for p in pdf.pages]
assert all(abs(float(p.mediabox.width)-612)<.01 and abs(float(p.mediabox.height)-792)<.01 for p in pdf.pages)
assert all('CVM PAPER ID:' in t for t in page_text)
fonts=set()
for page in pdf.pages:
    for ref in page['/Resources'].get('/Font',{}).values():
        f=ref.get_object();assert f['/Subtype']!='/Type3'
        d=f.get('/FontDescriptor')
        if d:assert any(k in d.get_object() for k in ('/FontFile','/FontFile2','/FontFile3'))
        fonts.add(str(f.get('/BaseFont')))
from PIL import Image
asset_files={'Bubble':'bubble_comparison.png','Overview':'architecture_dense.png','Classes':'class_comparison.png','Motivation':'scale_and_geometry.png'}
image_stream_checks=[]
for name,filename in asset_files.items():
    im=Image.open(OUT/'assets'/filename).convert('RGB')
    for page in pdf.pages:
        x=page['/Resources']['/XObject']['/'+name].get_object()
        assert (x['/Width'],x['/Height'])==im.size
        assert x.get_data()==im.tobytes(),name
    image_stream_checks.append({'name':name,'size':list(im.size),'lossless_rgb_matches':True})
fls=(single/'main.fls').read_text(errors='replace')
assert not any(ext in x.lower() for x in fls.splitlines() if x.startswith('INPUT ') for ext in ('.png','.jpg','.eps','.bib'))
manifest=json.loads((OUT/'build_manifest.json').read_text(encoding='utf-8'))
origin_checks=0
for name,sha in manifest['source_files'].items():
    origin=ROOT/Path(name.replace('\\','/'))
    if origin.exists():
        assert hashlib.sha256(origin.read_bytes()).hexdigest()==sha
        origin_checks+=1
for name,sha in manifest['packaged_inputs'].items(): assert hashlib.sha256((OUT/name).read_bytes()).hexdigest()==sha
shutil.copy2(single/'main.pdf',OUT/'MANUSCRIPT_CVM.pdf')
shutil.copy2(single/'main.log',OUT/'qa/final_compile.log')
(OUT/'qa/extracted_text.txt').write_text('\n\n'.join(page_text),encoding='utf-8')
report={'status':'compiled_and_content_verified','single_file_test':True,'initial_files':['main.tex'],'compiler_passes':3,'pages':len(pdf.pages),'page_word_counts':[len(t.split()) for t in page_text],
 'tables':6,'figures':4,'equations':11,'references':25,'numeric_table_cells_checked':sum(len(v) for t in expected for v in t),'table_checks':checks,'derived_differences_checked':len(differences),'exact_sample_points':41,'historical_csv_checks':raw_checks,'geometry_lrs_source':'complete 100-epoch CSVs and registered track report; not a matched-source ablation certification',
 'uavdt':{'numeric_cells_checked':18,'raw_text_exports_verified':True,'AP_gain':2.84,'current_full_identity':'author_confirmed_not_checkpoint_verified','official_split_mapping':'unverified','new_training':False},
 'overfull_boxes':0,'undefined_references':0,'missing_characters':0,'official_styles_unchanged':True,'letter_paper':True,'anonymous':True,'review_line_rulers':True,'fonts_embedded':True,'type3_fonts':False,
 'new_training':False,'new_model_evaluation':False,'efficiency_batch_sizes':[8],'internal_components':'validation only','original_sources_unchanged':True if origin_checks==len(manifest['source_files']) else 'origin unavailable; packaged inputs verified','origin_hashes_checked':origin_checks,'external_images_required':False,'bibtex_required':False,'shell_escape':False,
 'known_template_warnings':['Official cvm_eso.sty identifies itself as everyshi','Legacy hyperref letterpaper option unused','epstopdf notes shell escape disabled; no EPS used'],
 'archived_geometry_checks':geometry_checks,'nominal_size_dtype_cases_passed':len(nominal_cases),'center_preservation_case_passed':True,'current_geometry_function_matches_archive':True,'historical_training_trigger_rates_in_main_text':False,
 'external_class_AP_values_checked':20,'external_class_differences_checked':10,'external_class_profile_checks':class_metric_checks,'external_class_profile_endpoint':'final; common converted-label test; complete systems only',
 'qualitative_figure_status':'excluded from current revision by explicit user choice; optional tooling retained for future work','qualitative_gt_sha256':gt_sha,'qualitative_gt_counts':{'images':548,'annotations':38759},
 'motivation_checks':{'all_converted_val_annotations':True,'method':'independent Decimal area thresholds and rectangle intersection/union','input_area_bins':area_bins,'input_below_32_count':33281,'original_area_below_32_count':original_below_32,'analytic_curve_samples_checked':analytic_samples,'model_execution':False},
 'method_hierarchy_verified':True,'reference_publication_types_verified':True,
 'external_sensitivity_checks':sensitivity_checks,'external_sensitivity_AP_values_checked':16,'external_sensitivity_differences_checked':8,'publication_identity_mapping_verified':True,'accuracy_and_cost_merged':True,'historical_designs_location':'Main localization-design section; all four rows retained','numerical_implementation_checks_location':'Appendix A; developer failure chronology excluded from paper','publication_terminology':{'core':'GCDL','weight_rule':'LQS','legacy_run_identifiers_unchanged':True},
 'dfine_batch_reduction_reason':{'source':'direct author clarification','physical_batch':{'attempted':8,'used':4},'hardware':'RTX 4090, 24 GB','reason':'out-of-memory under this training setup','new_memory_test':False,'other_recipe_differences_retained':True},
 'formulation_checks':{'status':formulation['status'],'check_count':formulation['check_count'],'scope':formulation['scope']},
 'image_stream_checks':image_stream_checks,'visual_review':'pending','main_tex_sha256':hashlib.sha256((OUT/'main.tex').read_bytes()).hexdigest(),'pdf_sha256':hashlib.sha256((OUT/'MANUSCRIPT_CVM.pdf').read_bytes()).hexdigest()}
(OUT/'verification.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='table_checks'}))

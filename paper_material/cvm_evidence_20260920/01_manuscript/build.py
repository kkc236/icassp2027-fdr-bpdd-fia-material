"""Assemble the CVM review paper; main.tex is the standalone distributable."""
from pathlib import Path
import hashlib, json, re, shutil

OUT=Path(__file__).resolve().parent
ROOT=OUT.parent.parent
INPUTS=OUT/'inputs'
TEMPLATE=OUT/'official_template'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def esc(s):
    return ''.join({'&':r'\&','%':r'\%','_':r'\_','#':r'\#'}.get(c,c) for c in s)
def authors(full):
    names=[]
    for name in full.split(' and '):
        words=name.split()
        initials=' '.join('-'.join(t[0]+'.' for t in w.split('-')) if not w.endswith('.') else w for w in words[:-1])
        names.append(initials+' '+words[-1])
    return ', '.join(names[:-1])+', and '+names[-1] if len(names)>2 else ' and '.join(names)

tables={
'MECHANISM':r'''
\begin{table*}[t]
\centering
\caption{Inherited representation and author design choices in the RT-DETR host. The complete FDR/FGL transfer is the reference; Table~\ref{tab:lrsversions} separates our path redesign from the two additional rules.}
\label{tab:mechanism}
\small\setlength{\tabcolsep}{5pt}\renewcommand{\arraystretch}{1.12}
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}p{2.5cm}p{6.25cm}p{7.1cm}@{}}
\toprule
Design aspect & Full FDR/FGL transfer reference & GCDL (ours) \\
\midrule
\multicolumn{3}{@{}l}{\emph{Inherited distributional representation~\cite{peng2025dfine}}}\\[2pt]
Distributional core & Discrete edges, nonuniform support, integral decoding, cumulative logits, fixed distribution frame, and adjacent-bin FGL & Retains these representation primitives and their attribution \\
\midrule
\multicolumn{3}{@{}l}{\emph{Our reference and supervision path}}\\[2pt]
Reference choice & Predicted preliminary box shared across decoder layers & Incoming decoder reference shared across layers and the expert \\
Additional supervision & Normal/DN FGL and preliminary-box L1/GIoU & Normal-query FGL; extra preliminary-box and DN-FDR terms disabled; stock DN retained \\
\midrule
\multicolumn{3}{@{}l}{\emph{Our geometry and layerwise allocation rules}}\\[2pt]
Geometry and gradient & Decode signed edge offsets relative to the reference box & Preserve the implied center; enforce reference-scale and precision-aware extent floors with an explicit identity surrogate \\
Quality weights & Detached matched-box IoU weights in FGL & Shrink eligible same-image, same-layer weights toward their group mean, preserving the total \\
Depth dependence & Apply the direct quality-weighting rule & Decay shrinkage from $0.25$ to zero across six layers; keep final-layer, singleton, and ineligible weights unchanged \\
\bottomrule
\end{tabular*}
\end{table*}
''',
'LRSVERSIONS':r'''
\begin{table*}[t]
\centering
\caption{Localization design comparison on native validation after 100 epochs. The path redesign changes the reference and extra supervision; all rows retain the attributed FDR/FGL representation. Checkpoints are selected by validation AP. These are historical design variants, not a fully source- and initialization-matched ablation. Bold marks the highest value in each metric.}
\label{tab:lrsversions}
\small\setlength{\tabcolsep}{5pt}\renewcommand{\arraystretch}{1.10}
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lcccrr@{}}
\toprule
Localization design & Redesigned path & Feasible decoding & LQS & AP & $\mathrm{AP}_{50}$ \\
\midrule
\multicolumn{6}{@{}l}{\emph{Transfer reference}}\\[2pt]
Full FDR/FGL transfer & -- & -- & -- & 29.078 & 48.473 \\
\midrule
\multicolumn{6}{@{}l}{\emph{Our localization variants}}\\[2pt]
Path redesign & \checkmark & -- & -- & \textbf{29.696} & 49.320 \\
Path redesign + geometry & \checkmark & \checkmark & -- & 29.361 & 49.130 \\
GCDL & \checkmark & \checkmark & \checkmark & 29.620 & \textbf{49.382} \\
\bottomrule
\end{tabular*}
\end{table*}
''',
'NATIVE':r'''
\begin{table}[t]
\centering
\caption{Complete-system VisDrone test results. Native evaluator; validation-selected checkpoints; 640 input; at most 300 detections.}
\label{tab:native}
\small
\begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}}lrrr@{}}
\toprule
Model & AP & $\mathrm{AP}_{50}$ & $\mathrm{AP}_{75}$ \\
\midrule
RT-DETR-L & 17.743 & 32.254 & 17.565 \\
\textbf{Full (ours)} & \textbf{23.604} & \textbf{41.241} & \textbf{23.546} \\
\bottomrule
\end{tabular*}
\end{table}
''',
'EXTERNAL':r'''
\begin{table}[t]
\centering
\caption{Complete-system VisDrone test comparison. Common evaluator with $\texttt{maxDet}=300$. D-FINE-L denotes our scratch-adapted reproduction; training recipes and effective batches differ (Sec.~\ref{sec:protocol}). Final is primary; best is selected by each model's native validation.}
\label{tab:external}
\small\setlength{\tabcolsep}{3pt}
\begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}}lrrrr@{}}
\toprule
Model & AP & $\mathrm{AP}_{50}$ & $\mathrm{AP}_{75}$ & $\mathrm{AP}_{s}$ \\
\midrule
\multicolumn{5}{@{}l}{\emph{Final checkpoint (primary)}}\\[2pt]
D-FINE-L (reprod.) & 22.554 & 38.656 & 22.720 & 13.338 \\
\textbf{Full (ours)} & \textbf{24.133} & \textbf{41.885} & \textbf{24.044} & \textbf{14.575} \\
\midrule
\multicolumn{5}{@{}l}{\emph{Validation-selected checkpoints (secondary)}}\\[2pt]
D-FINE-L (reprod.) & 22.679 & 38.940 & 22.713 & 13.478 \\
\textbf{Full (ours)} & \textbf{24.229} & \textbf{42.009} & \textbf{24.208} & \textbf{14.618} \\
\bottomrule
\end{tabular*}
\end{table}
''',
'LITERATURE':r'''
\begin{table}[t]
\centering
\caption{Published VisDrone validation context and our native result. All rows use 640 input without pretraining. Training and evaluation recipes differ.}
\label{tab:literature}
\small\setlength{\tabcolsep}{3pt}
\begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}}lrrrr@{}}
\toprule
Method & Epochs & Params (M) & AP & $\mathrm{AP}_{50}$ \\
\midrule
\multicolumn{5}{@{}l}{\emph{Published results}}\\[2pt]
RemDet-L~\cite{li2025remdet} & 300 & 35.3 & 29.3 & 47.4 \\
BDNet~\cite{guan2026bdnet} & 300 & 2.59 & 31.2 & 50.5 \\
\midrule
\multicolumn{5}{@{}l}{\emph{Our native protocol}}\\[2pt]
Full (ours) & 100 & 35.244 & 30.109 & 49.890 \\
\bottomrule
\end{tabular*}
\end{table}
''',
'COMPONENTS':r'''
\begin{table*}[t]
\centering
\caption{Accuracy and cost of the localization core and local extension. $G$: GCDL; $F$: shared P3 refinement; $B$: expert with direct and selective supervision. Accuracy uses native validation-selected checkpoints. The $\dagger$ rows form the most directly matched pair. Efficiency uses RTX 4090, $640\times640$, FP32, and batch eight; batch time is the median of 300 synchronized predict calls after 100 warmup batches. GFLOPs are per image.}
\label{tab:components}\label{tab:efficiency}
\small\setlength{\tabcolsep}{4pt}\renewcommand{\arraystretch}{1.1}
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lrrrrrr@{}}
\toprule
Configuration & Val AP & $\mathrm{AP}_{50}$ & Params (M) & GFLOPs & Batch (ms) & Images/s \\
\midrule
\multicolumn{7}{@{}l}{\emph{Host reference}}\\[2pt]
RT-DETR-L & 21.911 & 38.663 & 32.827 & 105.597 & 59.559 & 134.321 \\
\midrule
\multicolumn{7}{@{}l}{\emph{Our localization core and extension variants}}\\[2pt]
$G$ & 29.620 & 49.382 & 33.157 & 105.804 & 66.200 & 120.846 \\
$G+F$ & 29.773 & 49.548 & 33.458 & 109.280 & 69.044 & 115.868 \\
$G+B\,\dagger$ & 29.277 & 48.783 & 34.942 & 130.575 & 104.897 & 76.266 \\
\textbf{Full} ($G+B+F$)$\,\dagger$ & \textbf{30.109} & \textbf{49.890} & 35.244 & 134.051 & 107.920 & 74.129 \\
\bottomrule
\end{tabular*}
\end{table*}
'''
}

# All eight rows come from already archived external complete-detector evaluations.
sensitivity=json.loads((INPUTS/'external_sensitivity/EXTERNAL_SENSITIVITY.json').read_text(encoding='utf-8'))
rows=[]
for row in sensitivity['comparisons']:
    rows.append(row['checkpoint'].capitalize()+' & '+row['split'].capitalize()+' & '+str(row['max_det'])+' & '+row['display_dfine_ap']+' & '+row['display_full_ap']+' & '+row['display_delta_ap']+r' \\')
tables['SENSITIVITY']=r'' + '\n'.join([
 r'\begin{table}[t]',r'\centering',
 r'\caption{Complete external AP results under the common evaluator. Final test at 300 is primary; other rows assess recorded evaluation choices. Differences use unrounded AP.}',
 r'\label{tab:sensitivity}',r'\small\setlength{\tabcolsep}{2.5pt}',
 r'\begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}}llrrrr@{}}',r'\toprule',
 r'Checkpoint & Split & Cap & D-FINE-L & Full & $\Delta$ \\',r'\midrule',
 *rows,r'\bottomrule',r'\end{tabular*}',r'\end{table}',
])

body=(OUT/'source/body.tex').read_text(encoding='ascii')
for name in ['bubble','overview','external_classes','motivation']:
    fig=(OUT/f'source/figure_{name}.tex').read_text(encoding='ascii')
    body=body.replace('% FIGURE_'+name.upper(),fig)
tables.pop('MECHANISM')
tables.pop('NATIVE')
tables.pop('EXTERNAL')
tables['SYSTEM']=(OUT/'source/table_system.tex').read_text(encoding='ascii')
tables['UAVDT']=(OUT/'source/table_uavdt.tex').read_text(encoding='ascii')
for name,table in tables.items():
    body=body.replace('% TABLE_'+name,table)
    (OUT/f'source/table_{name.lower()}.tex').write_text(table,encoding='ascii')
assert '% FIGURE_' not in body and '% TABLE_' not in body

refs=json.loads((INPUTS/'references.json').read_text(encoding='utf-8'))+json.loads((OUT/'source/additional_references.json').read_text(encoding='utf-8'))
refmap={r['key']:r for r in refs}
keys=[]
for match in re.findall(r'\\cite\{([^}]+)\}',body):
    for key in match.split(','):
        if key not in keys: keys.append(key)
assert set(keys)==set(refmap)
bib=[r'\begin{thebibliography}{99}',r'\fontsize{9}{11}\selectfont',r'\interlinepenalty=10000']
for key in keys:
    r=refmap[key]
    # Balance the last reference page after the appendix floats have cleared.
    # Let references flow naturally after figure-height changes.
    title=r['title'].replace('BDNet:Bio','BDNet: Bio')
    entry=esc(authors(r['authors']))+'. '+esc(title)+'. '
    entry+=(r'In: \emph{'+esc(r['venue'])+'}, ' if r['type']=='inproceedings' else esc(r['venue'])+', ')+str(r['year'])
    if r.get('volume'):
        entry+=', '+('LNCS ' if r.get('series')=='Lecture Notes in Computer Science' else '')+str(r['volume'])
        if r.get('number'): entry+='('+str(r['number'])+')'
    if r.get('pages'): entry+=', '+r['pages']
    if r.get('doi'):entry+=r'. doi: \href{https://doi.org/'+r['doi']+r'}{\nolinkurl{'+r['doi']+'}}'
    elif r['key'] in ('xu2026lme','yang2026sdnet'): entry+=r'. \href{'+r['url']+r'}{Official conference manuscript}'
    bib.append(r'\bibitem{'+key+'} '+entry+'.')
bib.append(r'\end{thebibliography}')

# Optional author bibliography: the same records as the inline distributable.
bibtex=[]
for key in keys:
    r=refmap[key]
    fields={'author':r['authors'],'title':'{'+r['title']+'}',
            'journal' if r['type']=='article' else 'booktitle' if r['type']=='inproceedings' else 'howpublished':r['venue'],
            'year':str(r['year'])}
    for name in ('series','volume','number','pages','doi','url'):
        if r.get(name): fields[name]=str(r[name])
    bibtex.append('@'+r['type']+'{'+key+',\n'+',\n'.join('  '+k+' = {'+v+'}' for k,v in fields.items())+'\n}')
(OUT/'references.bib').write_text('\n\n'.join(bibtex)+'\n',encoding='ascii')

preamble=r'''
\documentclass[10pt,twocolumn,letterpaper]{article}
\usepackage{cvm}
\usepackage[T1]{fontenc}
\usepackage{times}
\usepackage{graphicx,amsmath,amssymb,booktabs,array,balance}
\usepackage{xcolor,tikz}
\usetikzlibrary{arrows.meta,calc,positioning}
\usepackage[pagebackref=true,breaklinks=true,letterpaper=true,colorlinks,bookmarks=false]{hyperref}
\hypersetup{pdftitle={GCDL: Geometry-Constrained Distributional Localization for UAV Detection},pdfauthor={},pdfsubject={Anonymous CVM review submission},citecolor=blue,linkcolor=blue,urlcolor=blue}
\newcommand{\keywords}[1]{{\bfseries\emph{Keywords: #1}}}
% Review mode is intentional. Do not enable \cvmfinalcopy for submission.
% Replace only **** below with the real submission-system paper ID.
\def\cvmPaperID{****}
\def\httilde{\mbox{\tt\raisebox{-.5ex}{\symbol{126}}}}
\ifcvmfinal\pagestyle{empty}\fi
\definecolor{ink}{HTML}{22364A}
\definecolor{basefill}{HTML}{EDF2F7}
\definecolor{expertcolor}{HTML}{236B9C}
\definecolor{expertfill}{HTML}{E5F1F8}
\definecolor{featurecolor}{HTML}{A76115}
\definecolor{featurefill}{HTML}{FBF0DF}
\begin{document}
\title{GCDL: Geometry-Constrained Distributional Localization for UAV Detection}
\author{}
\maketitle
'''
styles=['cvm.sty','cvm_eso.sty','eso-pic.sty']
parts=['% Standalone CVM 2027 review manuscript. Compile three times with pdfLaTeX.\n% Official style files below are embedded verbatim; figures and references are inline.']
for style in styles:
    data=(TEMPLATE/style).read_text(encoding='ascii')
    parts.append(r'\begin{filecontents*}[overwrite]{'+style+'}\n'+data.rstrip()+'\n'+r'\end{filecontents*}')
    shutil.copy2(TEMPLATE/style,OUT/style)
import sys
sys.path.insert(0,str(OUT/'source'))
from embed_raster import embed_assets
embedded=embed_assets({
 'Bubble':OUT/'assets/bubble_comparison.png',
 'Overview':OUT/'assets/architecture_dense.png',
 'Classes':OUT/'assets/class_comparison.png',
 'Motivation':OUT/'assets/scale_and_geometry.png'})
preamble=preamble.replace(r'\begin{document}',embedded+'\n'+r'\begin{document}')
parts.extend([preamble,body,'\n\n'.join(bib),r'\end{document}'])
tex='\n\n'.join(parts)+'\n'
assert tex.isascii()
(OUT/'main.tex').write_text(tex,encoding='ascii')
(OUT/'source/references.tex').write_text('\n\n'.join(bib),encoding='ascii')
shutil.copy2(TEMPLATE/'cvm.bst',OUT/'cvm.bst')
(OUT/'qa').mkdir(exist_ok=True)
manifest={
 'target':'CVM 2027','format':'official anonymous review template',
 'official_template_url':'https://iccvm.org/2027/files/template.zip',
 'official_submission_url':'https://iccvm.org/2027/submission.htm',
 'official_style_hashes':{s:sha(TEMPLATE/s) for s in styles},
 'single_file':True,'external_images_required':False,'bibtex_required':False,'shell_escape_required':False,
 'compiler':'pdfLaTeX','tables':6,'figures':4,'equations':11,'references':len(keys),
 'source_files':json.loads((INPUTS/'original_source_hashes.json').read_text(encoding='utf-8')),
 'packaged_inputs':{p.relative_to(OUT).as_posix():sha(p) for folder in [INPUTS,TEMPLATE] for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts},
 'new_training':False,'new_model_evaluation':False,'efficiency_batch_sizes':[8],
 'internal_components':'validation only','pending_user_metadata':['real CVM paper ID'],
 'embedded_dependencies':styles+['four embedded lossless figures','25 inline references'],
 'uavdt':{'role':'additional archived comparison','current_full_identity':'author_confirmed_not_checkpoint_verified','local_split_to_official_protocol':'unverified','reported_AP':[14.12,16.96],'source':'inputs/uavdt'},
 'task_motivation':'all converted-label validation GT at common-evaluator input scale plus analytic translation IoU; no new model evaluation',
 'batch8_evidence':json.loads((INPUTS/'batch8_verified.json').read_text(encoding='utf-8'))
}
(OUT/'build_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'main_tex_bytes':len(tex),'tables':6,'figures':4,'equations':11,'references':len(keys),'standalone':True}))

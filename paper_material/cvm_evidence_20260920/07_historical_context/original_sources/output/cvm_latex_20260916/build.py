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
'NATIVE':r'''
\begin{table}[t]
\centering
\caption{Complete-system VisDrone test results under the native evaluator. Both checkpoints are validation-selected; input resolution is 640.}
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
\caption{External VisDrone test comparison under the common evaluator. Training recipes differ. Final is primary; best is selected by each model's native validation.}
\label{tab:external}
\small\setlength{\tabcolsep}{3pt}
\begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}}lrrrr@{}}
\toprule
Model & AP & $\mathrm{AP}_{50}$ & $\mathrm{AP}_{75}$ & $\mathrm{AP}_{s}$ \\
\midrule
\multicolumn{5}{@{}l}{\emph{Final checkpoint (primary)}}\\[2pt]
D-FINE-L & 22.554 & 38.656 & 22.720 & 13.338 \\
\textbf{Full (ours)} & \textbf{24.133} & \textbf{41.885} & \textbf{24.044} & \textbf{14.575} \\
\midrule
\multicolumn{5}{@{}l}{\emph{Native validation-selected best (secondary)}}\\[2pt]
D-FINE-L & 22.679 & 38.940 & 22.713 & 13.478 \\
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
RemDet-L~\cite{li2025remdet} & 300 & 35.3 & 29.3 & 47.4 \\
BDNet~\cite{guan2026bdnet} & 300 & 2.59 & 31.2 & 50.5 \\
Full (ours) & 100 & 35.244 & 30.109 & 49.890 \\
\bottomrule
\end{tabular*}
\end{table}
''',
'COMPONENTS':r'''
\begin{table}[t]
\centering
\caption{Native validation component results. $G$: distributional reference; $B$: expert with direct and selective supervision; $F$: shared P3 refinement. $G+B$ and Full form the most directly matched pair.}
\label{tab:components}
\small\setlength{\tabcolsep}{3pt}
\begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}}lcccrr@{}}
\toprule
Variant & $G$ & $B$ & $F$ & Val AP & $\mathrm{AP}_{50}$ \\
\midrule
Baseline & -- & -- & -- & 21.911 & 38.663 \\
$G$ & \checkmark & -- & -- & 29.620 & 49.382 \\
$G+F$ & \checkmark & -- & \checkmark & 29.773 & 49.548 \\
$G+B$ & \checkmark & \checkmark & -- & 29.277 & 48.783 \\
\textbf{Full} & \checkmark & \checkmark & \checkmark & \textbf{30.109} & \textbf{49.890} \\
\bottomrule
\end{tabular*}
\end{table}
''',
'EFFICIENCY':r'''
\begin{table}[t]
\centering
\caption{Batch-eight inference efficiency on RTX 4090 at $640\times640$ in FP32. GFLOPs are per image; batch times are medians of 300 synchronized predict calls after 100 warmup batches.}
\label{tab:efficiency}
\small\setlength{\tabcolsep}{2.5pt}
\begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}}lrrrr@{}}
\toprule
Variant & Params (M) & GFLOPs & Batch (ms) & Images/s \\
\midrule
Baseline & 32.827 & 105.597 & 59.559 & 134.321 \\
$G$ & 33.157 & 105.804 & 66.200 & 120.846 \\
$G+F$ & 33.458 & 109.280 & 69.044 & 115.868 \\
$G+B$ & 34.942 & 130.575 & 104.897 & 76.266 \\
Full & 35.244 & 134.051 & 107.920 & 74.129 \\
\bottomrule
\end{tabular*}
\end{table}
'''
}

body=(OUT/'source/body.tex').read_text(encoding='ascii')
offsets=json.loads((INPUTS/'sampling_points.json').read_text())['normalized_offsets']
assert len(offsets)==len(set(map(tuple,offsets)))==41
for name in ['overview','expert','selection']:
    fig=(OUT/f'figures/{name}.tikz').read_text(encoding='ascii')
    if name=='expert':
        points=[]
        for i,(x,y) in enumerate(offsets):
            color='expertcolor' if i<20 else 'featurecolor' if i<40 else 'ink'
            points.append(f'\\fill[{color}] ({x},{y}) circle[radius=.021];')
        fig=fig.replace('% EXACT_SAMPLING_POINTS','\n'.join(points))
    body=body.replace('% FIGURE_'+name.upper(),fig)
for name,table in tables.items():
    body=body.replace('% TABLE_'+name,table)
    (OUT/f'source/table_{name.lower()}.tex').write_text(table,encoding='ascii')
assert '% FIGURE_' not in body and '% TABLE_' not in body

refs=json.loads((INPUTS/'references.json').read_text(encoding='utf-8'))
refmap={r['key']:r for r in refs}
keys=[]
for match in re.findall(r'\\cite\{([^}]+)\}',body):
    for key in match.split(','):
        if key not in keys: keys.append(key)
assert set(keys)==set(refmap)
bib=[r'\clearpage\balance',r'\begin{thebibliography}{99}',r'\fontsize{9}{11}\selectfont']
for key in keys:
    r=refmap[key]
    title=r['title'].replace('BDNet:Bio','BDNet: Bio')
    entry=esc(authors(r['authors']))+'. '+esc(title)+'. '
    entry+=(r'In: \emph{'+esc(r['venue'])+'}, ' if r['type']=='inproceedings' else esc(r['venue'])+', ')+str(r['year'])
    if r.get('pages'): entry+=', '+r['pages']
    if r.get('doi'):entry+=r'. doi: \href{https://doi.org/'+r['doi']+r'}{\nolinkurl{'+r['doi']+'}}'
    bib.append(r'\bibitem{'+key+'} '+entry+'.')
bib.append(r'\end{thebibliography}')

preamble=r'''
\documentclass[10pt,twocolumn,letterpaper]{article}
\usepackage{cvm}
\usepackage[T1]{fontenc}
\usepackage{times}
\usepackage{graphicx,amsmath,amssymb,booktabs,array,balance}
\usepackage{xcolor,tikz}
\usetikzlibrary{arrows.meta,calc,positioning}
\usepackage[pagebackref=true,breaklinks=true,letterpaper=true,colorlinks,bookmarks=false]{hyperref}
\hypersetup{pdftitle={Local Visual Refinement for Distributional UAV Object Detection},pdfauthor={},pdfsubject={Anonymous CVM review submission},citecolor=blue,linkcolor=blue,urlcolor=blue}
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
\title{Local Visual Refinement for Distributional UAV Object Detection}
\author{}
\maketitle
'''
styles=['cvm.sty','cvm_eso.sty','eso-pic.sty']
parts=['% Standalone CVM 2027 review manuscript. Compile twice with pdfLaTeX.\n% Official style files below are embedded verbatim; figures and references are inline.']
for style in styles:
    data=(TEMPLATE/style).read_text(encoding='ascii')
    parts.append(r'\begin{filecontents*}[overwrite]{'+style+'}\n'+data.rstrip()+'\n'+r'\end{filecontents*}')
    shutil.copy2(TEMPLATE/style,OUT/style)
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
 'compiler':'pdfLaTeX','tables':5,'figures':3,'equations':9,'references':len(keys),
 'source_files':json.loads((INPUTS/'original_source_hashes.json').read_text(encoding='utf-8')),
 'packaged_inputs':{p.relative_to(OUT).as_posix():sha(p) for folder in [INPUTS,TEMPLATE] for p in folder.iterdir() if p.is_file()},
 'new_training':False,'new_model_evaluation':False,'efficiency_batch_sizes':[8],
 'internal_components':'validation only','pending_user_metadata':['real CVM paper ID'],
 'embedded_dependencies':styles+['three inline TikZ figures','17 inline references'],
 'batch8_evidence':json.loads((INPUTS/'batch8_verified.json').read_text(encoding='utf-8'))
}
(OUT/'build_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'main_tex_bytes':len(tex),'tables':5,'figures':3,'equations':9,'references':len(keys),'standalone':True}))

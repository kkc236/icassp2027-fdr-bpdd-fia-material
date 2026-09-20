"""One-time, bounded layout revision from the results-first release."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
old=R.parent/'cvm_results_first_20260917'
b=(old/'source/body.tex').read_text(encoding='ascii')
b=b.replace('% FIGURE_MOTIVATION','% FIGURE_BUBBLE')
b=b.replace('% TABLE_MECHANISM','')
for k in ['LRS','EXPERT','SELECTION']:b=b.replace('% FIGURE_'+k,'')
b=b.replace('Table~\\ref{tab:mechanism} separates these additions from the inherited representation and compares them with the complete transfer configuration.', 'Figure~\\ref{fig:overview}(b,c) details our reference, geometry, and supervision paths; Table~\\ref{tab:lrsversions} evaluates the complete transfer and our localization variants.')
b=b.replace('Table~\\ref{tab:mechanism} makes the distinction from the complete FDR/FGL transfer explicit; Sec.~\\ref{sec:localizationresults} evaluates that reference and the intermediate configurations.', 'The distributional representation is inherited from D-FINE; the incoming-reference path, feasible geometry, and LQS define GCDL. Section~\\ref{sec:localizationresults} evaluates the complete transfer and the intermediate configurations.')
b=b.replace('(Table~\\ref{tab:mechanism})','(Sec.~\\ref{sec:lrs})')
b=b.replace('Figure~\\ref{fig:lrs} illustrates the two additions.', 'Figure~\\ref{fig:overview}(c) illustrates the two additions with analytical examples, not measured training statistics.')
b=b.replace('Figure~\\ref{fig:expert} shows their exact geometry.', 'Figure~\\ref{fig:overview}(e) summarizes the sampling and attention path; the equations above define the exact offsets.')
b=b.replace('Fig.~\\ref{fig:selection}', 'Fig.~\\ref{fig:overview}(e)')
b=b.replace('The scale profile in Fig.~\\ref{fig:motivation}(a)', 'The scale profile in Appendix Fig.~\\ref{fig:motivation}(a)')
b=b.replace('Our evaluation connects geometric and supervision properties with design-level accuracy and complete-system performance.', 'Figure~\\ref{fig:bubble} places the full detector in the reported VisDrone accuracy--size landscape. Our evaluation connects geometric and supervision properties with design-level accuracy and complete-system performance.')
b=b.replace('% TABLE_NATIVE','% TABLE_SYSTEM').replace('% TABLE_EXTERNAL','')
b=b.replace('Table~\\ref{tab:native} evaluates', 'Table~\\ref{tab:system}(a) evaluates')
b=b.replace('Table~\\ref{tab:external}', 'Table~\\ref{tab:system}(b,c)')
b=b.replace('Table~\\ref{tab:literature} situates', 'Appendix Table~\\ref{tab:literature} situates')
b=b.replace('% TABLE_LITERATURE','')
b=b.replace('DETR~\\cite{carion2020detr} formulates detection as set prediction, and RT-DETR', 'DETR~\\cite{carion2020detr} formulates detection as set prediction, and RT-DETR')
needle='\\subsection{Distributional localization and its integration}\n'
paragraph='Deformable DETR~\\cite{zhu2021deformable} concentrates attention on sparse locations around reference points. DN-DETR~\\cite{li2022dndetr} and DINO~\\cite{zhang2023dino} improve query training through denoising. These developments motivate efficient spatial access and stable query optimization. GCDL focuses on the geometry and loss allocation of the decoded distributions within this framework.\n\nGeneralized Focal Loss~\\cite{li2020gfl} represents box locations as distributions and incorporates localization quality into detection learning. This establishes a broader distributional-regression context for the fine-grained edge representation used here. '
b=b.replace(needle,needle+paragraph)
needle='Box-guided refinement makes feature access depend on a localization hypothesis.'
b=b.replace(needle,'Channel and spatial attention, exemplified by CBAM~\\cite{woo2018cbam}, provide complementary feature modulation. Our shared P3 branch computes its two gates in parallel from the same features and uses a zero-initialized residual blend. '+needle)
b += '\n\\section{Task scale and published context}\n\\label{sec:visualcontext}\nFigure~\\ref{fig:motivation} shows the annotation-scale distribution and its analytical localization motivation. Table~\\ref{tab:literature} retains the published accuracy--size context, with training and evaluator differences stated explicitly.\n\n% FIGURE_MOTIVATION\n\n% TABLE_LITERATURE\n'
(R/'source/body.tex').write_text(b,encoding='ascii')

build=(old/'build.py').read_text(encoding='ascii')
start=build.index('offsets=json.loads')
end=build.index('for name,table in tables.items():',start)
build=build[:start]+'''for name in ['bubble','overview','external_classes','motivation']:
    fig=(OUT/f'source/figure_{name}.tex').read_text(encoding='ascii')
    body=body.replace('% FIGURE_'+name.upper(),fig)
tables.pop('MECHANISM')
tables.pop('NATIVE')
tables.pop('EXTERNAL')
tables['SYSTEM']=(OUT/'source/table_system.tex').read_text(encoding='ascii')
'''+build[end:]
build=build.replace("refs=json.loads((INPUTS/'references.json').read_text(encoding='utf-8'))", "refs=json.loads((INPUTS/'references.json').read_text(encoding='utf-8'))+json.loads((OUT/'source/additional_references.json').read_text(encoding='utf-8'))")
build=build.replace("    if key == 'bi2025fghdet': bib.append(r'\\balance')", "    # Final-page balance is checked after float placement.")
build=build.replace("parts.extend([preamble,body,", "import sys\nsys.path.insert(0,str(OUT/'source'))\nfrom embed_raster import embed_assets\nembedded=embed_assets({\n 'Bubble':OUT/'assets/bubble_comparison.png',\n 'Overview':OUT/'assets/architecture_dense.png',\n 'Classes':OUT/'assets/class_comparison.png',\n 'Motivation':OUT/'assets/scale_and_geometry.png'})\npreamble=preamble.replace(r'\\begin{document}',embedded+'\\n'+r'\\begin{document}')\nparts.extend([preamble,body,")
build=build.replace("'tables':7,'figures':6", "'tables':5,'figures':4").replace("['six inline TikZ figures','19 inline references']", "['four embedded lossless figures','24 inline references']")
(R/'build.py').write_text(build,encoding='ascii')

figs={
'bubble':r'''\begin{figure*}[t]
\centering
\visualBubble{0.88\textwidth}
\caption{VisDrone validation accuracy--size context at $640\times640$. AP is averaged over IoU thresholds 0.50:0.95; bubble area denotes GFLOPs per image. Blue points are reported by BDNet~\cite{guan2026bdnet}; green points by FGHDet~\cite{bi2025fghdet}. Gray and red are our host and full detector. Published training and evaluation protocols differ. The three recent YOLO labels abbreviate the source rows YOLO11-I, YOLO12-I, and YOLO26-I.}
\label{fig:bubble}
\end{figure*}''',
'overview':r'''\begin{figure*}[t]
\centering
\visualOverview{\textwidth}
\caption{Overview and expanded computation of the proposed detector. (a) GCDL refines boundary distributions, while shared P3 features serve the base decoder and local expert. (b) The incoming distribution reference is fixed across layers; accumulated logits retain gradients and detached boxes update attention. (c) Feasible decoding preserves the center, and LQS conserves an image--layer group's total weight; values are analytical illustrations. (d) Two residual blocks feed parallel channel and spatial gates with an identity-initialized blend. (e) The expert refines base logits using 123 local tokens and supplies detached localization targets through geometric selection. Solid arrows indicate prediction paths and orange dashed arrows training-only transfer. Sampling dots are schematic; the text specifies all 41 offsets.}
\label{fig:overview}\label{fig:lrs}\label{fig:expert}\label{fig:selection}
\end{figure*}''',
'external_classes':r'''\begin{figure*}[t]
\centering
\visualClasses{\textwidth}
\caption{Complete-system category results on converted-label VisDrone test under the common evaluator (final checkpoints; $\texttt{maxDet}=300$). Left: per-class AP of Full and our scratch-adapted D-FINE-L reproduction. Right: their AP differences, computed before rounding. Training recipes differ as specified in Sec.~\ref{sec:protocol}.}
\label{fig:externalclasses}
\end{figure*}''',
'motivation':r'''\begin{figure*}[t]
\centering
\visualMotivation{\textwidth}
\caption{Task scale and analytical localization motivation. (a) All 38,759 converted-label boxes from 548 validation images, measured after the common evaluator's $640\times640$ stretch. Input-scale groups differ from original-image COCO area ranges. (b) IoU of equal-size boxes under horizontal displacement, with aligned vertical spans. This is analytic geometry, not a measurement of model localization errors.}
\label{fig:motivation}
\end{figure*}'''}
for k,v in figs.items():(R/f'source/figure_{k}.tex').write_text(v+'\n',encoding='ascii')

table=r'''\begin{table*}[t]
\centering
\caption{Complete-detector comparisons on converted-label VisDrone test. All use 640 input and at most 300 detections. Panels have separate evaluation pipelines and must be compared within each panel. D-FINE-L is our scratch-adapted reproduction; training recipes and effective batches differ (Sec.~\ref{sec:protocol}). Panel (b) is the primary external endpoint; panel (c) uses native validation selection.}
\label{tab:system}\label{tab:native}\label{tab:external}
\small\setlength{\tabcolsep}{5pt}\renewcommand{\arraystretch}{1.12}
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}llrrrr@{}}
\toprule
Model & Checkpoint & AP & $\mathrm{AP}_{50}$ & $\mathrm{AP}_{75}$ & $\mathrm{AP}_{s}$ \\
\midrule
\multicolumn{6}{@{}l}{\emph{(a) Native evaluator: complete-system improvement over the host}}\\[2pt]
RT-DETR-L & Validation-selected & 17.743 & 32.254 & 17.565 & -- \\
\textbf{Full (ours)} & Validation-selected & \textbf{23.604} & \textbf{41.241} & \textbf{23.546} & -- \\
\midrule
\multicolumn{6}{@{}l}{\emph{(b) Common evaluator: final checkpoints (primary)}}\\[2pt]
D-FINE-L (reprod.) & Final & 22.554 & 38.656 & 22.720 & 13.338 \\
\textbf{Full (ours)} & Final & \textbf{24.133} & \textbf{41.885} & \textbf{24.044} & \textbf{14.575} \\
\midrule
\multicolumn{6}{@{}l}{\emph{(c) Common evaluator: validation-selected checkpoints (secondary)}}\\[2pt]
D-FINE-L (reprod.) & Validation-selected & 22.679 & 38.940 & 22.713 & 13.478 \\
\textbf{Full (ours)} & Validation-selected & \textbf{24.229} & \textbf{42.009} & \textbf{24.208} & \textbf{14.618} \\
\bottomrule
\end{tabular*}
\end{table*}
'''
(R/'source/table_system.tex').write_text(table,encoding='ascii')
refs=[
dict(key='zhu2021deformable',authors='Xizhou Zhu and Weijie Su and Lewei Lu and Bin Li and Xiaogang Wang and Jifeng Dai',title='Deformable DETR: Deformable Transformers for End-to-End Object Detection',venue='ICLR',year=2021,type='inproceedings',url='https://openreview.net/forum?id=koX9F3hvCG'),
dict(key='li2022dndetr',authors='Feng Li and Hao Zhang and Shilong Liu and Jian Guo and Lionel M. Ni and Lei Zhang',title='DN-DETR: Accelerate DETR Training by Introducing Query DeNoising',venue='CVPR',year=2022,type='inproceedings',pages='13619--13627',url='https://openaccess.thecvf.com/content/CVPR2022/papers/Li_DN-DETR_Accelerate_DETR_Training_by_Introducing_Query_DeNoising_CVPR_2022_paper.pdf'),
dict(key='zhang2023dino',authors='Hao Zhang and Feng Li and Shilong Liu and Lei Zhang and Hang Su and Jun Zhu and Lionel M. Ni and Heung-Yeung Shum',title='DINO: DETR with Improved DeNoising Anchor Boxes for End-to-End Object Detection',venue='ICLR',year=2023,type='inproceedings',url='https://openreview.net/forum?id=3mRwyG5one'),
dict(key='li2020gfl',authors='Xiang Li and Wenhai Wang and Lijun Wu and Shuo Chen and Xiaolin Hu and Jun Li and Jinhui Tang and Jian Yang',title='Generalized Focal Loss: Learning Qualified and Distributed Bounding Boxes for Dense Object Detection',venue='NeurIPS',year=2020,type='inproceedings',volume='33',url='https://proceedings.neurips.cc/paper_files/paper/2020/hash/f0bda020d2470f2e74990a07a607ebd9-Abstract.html'),
dict(key='woo2018cbam',authors='Sanghyun Woo and Jongchan Park and Joon-Young Lee and In So Kweon',title='CBAM: Convolutional Block Attention Module',venue='ECCV',year=2018,type='inproceedings',pages='3--19',url='https://openaccess.thecvf.com/content_ECCV_2018/papers/Sanghyun_Woo_Convolutional_Block_Attention_ECCV_2018_paper.pdf')]
(R/'source/additional_references.json').write_text(json.dumps(refs,indent=2),encoding='ascii')
print('Revised visual layout, first model table, figure roles, and five verified references.')

"""Regenerate the class-profile TikZ using packaged frozen metric JSON only."""
from pathlib import Path
import json
OUT=Path(__file__).resolve().parents[1]
raw=OUT/'inputs/external_class_profile/source'
d=json.loads((raw/'dfine_final_test.cap300.json').read_text())
f=json.loads((raw/'joint_final_test.cap300.json').read_text())
NAMES=['pedestrian','people','bicycle','car','van','truck','tricycle','awning-tricycle','bus','motor']
assert d['image_count']==f['image_count']==1610
assert d['max_det']==f['max_det']==300
rows=[]
for i,name in enumerate(NAMES):
    a=d['per_class_AP'][str(i)]*100
    b=f['per_class_AP'][str(i)]*100
    rows.append({'category_name':name,'delta_AP_points':b-a,'display_dfine_AP':f'{a:.2f}','display_full_AP':f'{b:.2f}','display_delta_AP_points':f'{b-a:+.2f}'})
tikz = [r'\begin{figure*}[t]', r'\centering', r'\begin{tikzpicture}[x=1cm,y=1cm,font=\sffamily\footnotesize]',
        r'\definecolor{classink}{HTML}{273449}', r'\definecolor{classgain}{HTML}{127A79}',
        r'\definecolor{classwash}{HTML}{F2F6F8}', r'\path[use as bounding box] (0,-0.16) rectangle (16.8,5.10);',
        r'\node[anchor=west,font=\sffamily\bfseries\small,text=classink] at (0,4.90) {Final checkpoints: complete-system class profile};',
        r'\node[anchor=east,font=\sffamily\footnotesize,text=classink] at (16.8,4.90) {Overall AP: 22.55 $\rightarrow$ 24.13\quad ($+1.58$)};']
for half, offset in enumerate([0, 8.65]):
    tikz.extend([f'\\begin{{scope}}[shift={{({offset},0)}}]',
                 r'\node[anchor=west,font=\sffamily\bfseries\scriptsize,text=classink] at (0,4.33) {Category};',
                 r'\node[font=\sffamily\bfseries\scriptsize,text=classink] at (2.38,4.33) {D-FINE-L$^\dagger$};',
                 r'\node[font=\sffamily\bfseries\scriptsize,text=classink] at (3.57,4.33) {Full};',
                 r'\node[font=\sffamily\bfseries\scriptsize,text=classink] at (6.23,4.33) {$\Delta$AP (percentage points)};',
                 r'\draw[classink!35,line width=.45pt] (0,4.10) -- (8.15,4.10);'])
    for tick in range(5):
        x = 4.53 + tick * .59
        tikz.append(f'\\draw[classink!12,line width=.4pt] ({x:.3f},.76) -- ({x:.3f},3.98);')
        tikz.append(f'\\node[anchor=north,font=\\sffamily\\scriptsize,text=classink!75] at ({x:.3f},.65) {{{tick}}};')
    tikz.append(r'\draw[classink!40,line width=.45pt] (4.53,.76) -- (7.185,.76);')
    for j, row in enumerate(rows[half * 5:half * 5 + 5]):
        y = 3.72 - j * .62
        if j % 2 == 0:
            tikz.append(f'\\fill[classwash] (0,{y-.25:.3f}) rectangle (4.10,{y+.25:.3f});')
        end_x = 4.53 + row['delta_AP_points'] * .59
        category_tex = r'\shortstack[l]{awning-\\tricycle}' if row['category_name'] == 'awning-tricycle' else row['category_name']
        tikz.extend([f'\\node[anchor=west,text=classink] at (.05,{y:.3f}) {{{category_tex}}};',
                     f'\\node[text=classink] at (2.38,{y:.3f}) {{{row["display_dfine_AP"]}}};',
                     f'\\node[text=classink] at (3.57,{y:.3f}) {{{row["display_full_AP"]}}};',
                     f'\\fill[classgain] (4.53,{y-.10:.3f}) rectangle ({end_x:.6f},{y+.10:.3f});',
                     f'\\node[anchor=east,text=classgain,font=\\sffamily\\bfseries\\footnotesize] at (8.10,{y:.3f}) {{{row["display_delta_AP_points"]}}};'])
    tikz.append(r'\end{scope}')
tikz.extend([r'\draw[classink!18] (8.40,.76) -- (8.40,4.33);',
             r'\node[anchor=west,font=\sffamily\scriptsize,text=classink!85] at (0,.04) {$^\dagger$Our scratch-adapted reproduction. All ten classes; identical evaluation protocol, different training recipes.};',
             r'\end{tikzpicture}',
             r'\caption{Class AP of final checkpoints on the 1,610-image VisDrone test split under the common converted-label protocol (IoU 0.50:0.95; maxDets=300). Classes follow dataset order; bars start at zero and show Full minus our scratch-adapted D-FINE-L reproduction. Displayed values are rounded; differences use unrounded AP. All ten category differences are positive. This complete-system profile uses different training recipes and does not isolate individual module effects.}',
             r'\label{fig:externalclasses}', r'\end{figure*}'])
(OUT / 'figures/external_classes.tikz').write_text('\n'.join(tikz) + '\n', encoding='ascii')

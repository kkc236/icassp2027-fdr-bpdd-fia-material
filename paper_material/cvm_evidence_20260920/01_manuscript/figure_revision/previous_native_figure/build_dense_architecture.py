"""Draw an editable, source-checked architecture figure (no model execution)."""
from pathlib import Path
from html import escape
import math, json, hashlib, subprocess, sys

ROOT=Path(__file__).resolve().parents[1]
local_deps=ROOT/'qa/drawing_dependencies'
if not local_deps.exists():
    local_deps=ROOT.parent/'cvm_visual_redesign_20260917/qa/drawing_dependencies'
if local_deps.exists():sys.path.insert(0,str(local_deps))
from svglib.svglib import svg2rlg
from svglib.fonts import register_font
from reportlab.graphics import renderPDF
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
for name,file in [('PaperSerif','times.ttf'),('PaperSerif-Bold','timesbd.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'C:/Windows/Fonts/'+file))
pdfmetrics.registerFontFamily('PaperSerif',normal='PaperSerif',bold='PaperSerif-Bold',italic='PaperSerif',boldItalic='PaperSerif-Bold')
register_font('Times New Roman','C:/Windows/Fonts/times.ttf',weight='normal',rlgFontName='PaperSerif')
register_font('Times New Roman','C:/Windows/Fonts/timesbd.ttf',weight='bold',rlgFontName='PaperSerif-Bold')

W,H=1600,1200
ink='#202B35'; blue='#225E9C'; teal='#287B77'; amber='#B1661E'
grey='#879099'; bfill='#F0F5FC'; gfill='#F0F8EE'; yfill='#FFF5D9'; pfill='#FBF0F5'
parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',f'<rect width="{W}" height="{H}" fill="white"/>']
def txt(x,y,s,size=22,anchor='middle',bold=False,color=ink):
    for plain,mathtext in [('q_prev','qₗ₋₁'),('z_prev','zₗ₋₁'),('q_l','qₗ'),('z_l','zₗ'),('r0','r₀'),('α_l','αₗ'),('γ_init','γ₀'),('P2','P₂'),('P3','P₃'),('P4','P₄'),('P5','P₅')]:
        s=s.replace(plain,mathtext)
    parts.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Times New Roman" font-size="{size}" font-weight="{"bold" if bold else "normal"}" fill="{color}">{escape(s)}</text>')
def gate_formula(x,y,size=20):
    # Position true subscripts explicitly to avoid unsupported Unicode substitutes.
    pieces=[('R = v × g',size,0),('c',size*.72,5),('(v) × g',size,0),('s',size*.72,5),('(v)',size,0)]
    widths=[pdfmetrics.stringWidth(t,'PaperSerif',fs) for t,fs,dy in pieces]
    cursor=x-sum(widths)/2
    for (t,fs,dy),w in zip(pieces,widths):
        txt(cursor,y+dy,t,fs,anchor='start',color=teal)
        cursor+=w
def lines(x,y,ss,size=22,gap=25,**kw):
    for i,s in enumerate(ss):txt(x,y+i*gap,s,size,**kw)
def rect(x,y,w,h,fill='white',stroke=ink,r=3,dash=None,sw=1.7):
    d=f' stroke-dasharray="{dash}"' if dash else ''
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
def node(x,y,w,h,label,fill='white',size=21,bold=False,stroke=ink,shape='rect'):
    if shape=='rule':
        cut=min(h*.34,14)
        poly([(x+cut,y),(x+w-cut,y),(x+w,y+h/2),(x+w-cut,y+h),(x+cut,y+h),(x,y+h/2)],fill,stroke,1.7)
    elif shape=='fusion':
        cut=min(h*.20,16)
        poly([(x,y),(x+w,y),(x+w-cut,y+h),(x+cut,y+h)],fill,stroke,1.7)
    elif shape=='loss':
        parts.append(f'<ellipse cx="{x+w/2}" cy="{y+h/2}" rx="{w/2}" ry="{h/2}" fill="{fill}" stroke="{stroke}" stroke-width="1.7"/>')
    elif shape=='terminal':
        rect(x,y,w,h,fill,stroke,min(h/2,14))
    else:
        rect(x,y,w,h,fill,stroke)
    ls=label.split('\n'); gap=size+3
    lines(x+w/2,y+h/2-(len(ls)-1)*gap/2+size*.34,ls,size,gap,bold=bold)
def path(points,color=ink,sw=1.7,dash=None,arrow=True):
    d='M '+' L '.join(f'{x},{y}' for x,y in points)
    extra=f' stroke-dasharray="{dash}"' if dash else ''
    parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linejoin="round"{extra}/>')
    if arrow:
        (x0,y0),(x,y)=points[-2:]; a=math.atan2(y-y0,x-x0); l=min(8,math.hypot(x-x0,y-y0)*.85); z=min(3.5,l*.44)
        p=[(x,y),(x-l*math.cos(a)+z*math.sin(a),y-l*math.sin(a)-z*math.cos(a)),(x-l*math.cos(a)-z*math.sin(a),y-l*math.sin(a)+z*math.cos(a))]
        parts.append('<polygon points="'+' '.join(f'{a:.2f},{b:.2f}' for a,b in p)+f'" fill="{color}"/>')
def circ(x,y,r,label=None,fill='white',stroke=ink,size=23):
    parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>')
    if label:txt(x,y+size*.32,label,size)
def panel(x,y,w,h,title,fill):
    rect(x,y,w,h,fill,ink,14,'8 6',1.35);txt(x+w/2,y+29,title,25,bold=True)
def dot(x,y,color=ink):circ(x,y,3,fill=color,stroke=color)

def poly(points,fill,stroke=ink,sw=1.4):
    parts.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in points)+f'" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

# F detail fragment. Uses the builder's existing drawing helpers and palette.
# Parent: (24, 24, 530, 340). Data ports: input (50, 137), output (543, 289).
# The two residual additions are one block; the enclosing group repeats twice.
f_ink = '#205E52'
rect(24, 24, 530, 340, 'white', f_ink, r=0, sw=1.8)
rect(25, 25, 528, 37, '#E9F2EB', 'none', r=0, sw=0)
path([(24, 62), (554, 62)], f_ink, 1.2, arrow=False)
txt(289, 49, '(b) Shared P3 refinement (F)', 23, bold=True, color=f_ink)

# Nested repeated transform: x + DWConv(GELU(Conv(x))), then u + Conv(GELU(u)).
rect(78, 70, 340, 164, '#FBFDFB', '#88A69B', r=0, sw=1.1)
txt(248, 90, 'Residual block × 2', 20, bold=True)
txt(51, 123, 'P3', 19, bold=True, color=f_ink)
node(109, 115, 236, 44, 'Conv 1×1 → GELU\n→ DWConv 3×3', 'white', 17)
circ(385, 137, 12, '+', size=21)
path([(50, 137), (109, 137)], teal)
path([(345, 137), (373, 137)], teal)
path([(95, 137), (95, 103), (385, 103), (385, 125)], teal)
dot(95, 137, teal)

node(109, 178, 236, 36, 'GELU → Conv 1×1', 'white', 18)
circ(385, 196, 12, '+', size=21)
path([(385, 149), (385, 168), (95, 168), (95, 196), (109, 196)], teal)
path([(345, 196), (373, 196)], teal)
path([(95, 168), (84, 168), (84, 223), (385, 223), (385, 208)], teal)
dot(95, 168, teal)

# v feeds both gates and the unweighted multiplicative input through one trunk.
path([(397, 196), (435, 196), (435, 238), (98, 238), (98, 315)], teal, arrow=False)
txt(450, 219, 'v', 19, color=teal)
node(112, 244, 198, 38, 'Channel gate\nGAP → MLP → σ', '#F4F8F4', 17)
node(112, 296, 198, 38, 'Spatial gate\nMean/Max → 7×7 → σ', '#F4F8F4', 17)
path([(98, 263), (112, 263)], teal)
path([(98, 315), (112, 315)], teal)
dot(98, 263, teal)
dot(98, 289, teal)
circ(348, 289, 13, '×', size=23)
path([(98, 289), (335, 289)], teal)
path([(310, 263), (348, 263), (348, 276)], teal)
path([(310, 315), (348, 315), (348, 302)], teal)

# Identity blending receives R and the original P3 independently.
txt(458, 254, 'γ_init = 0', 18, color=teal)
node(382, 265, 151, 49, 'P3 + γ(R − P3)', '#E3EFE7', 17, shape='fusion')
path([(361, 289), (387, 289)], teal)
txt(371, 278, 'R', 18, color=teal)
dot(65, 137, teal)
path([(65, 137), (65, 343), (457, 343), (457, 314)], teal)
path([(529, 289), (543, 289)], teal)
txt(520, 327, 'P3*', 19, color=teal)

# Box-conditioned expert: self-contained drawing calls for the shared builder.
# Bounds: x=600..1576, y=24..364. Uses existing txt/node/path/circ/rect helpers.
b_border = '#705080'
b_pale = '#F1EAF5'
b_fill = '#F8F5FA'
rect(600,24,976,340,'white',b_border,0,sw=1.65)
rect(601,25,974,37,b_pale,'none',0,sw=0)
path([(600,62),(1576,62)],b_border,1.2,arrow=False)
txt(1088,51,'(d) Box-conditioned local expert (B)',23,bold=True,color=b_border)

# Local visual tokens; coordinate gradients stop, feature gradients remain.
txt(738,88,'P2 / P3* / P4',19,color=teal)
path([(738,93),(738,103)],teal)
node(616,103,245,44,'Bilinear sampling\n41 points / scale',b_fill,19,stroke=b_border)
txt(721,169,'sg(base box)',18,anchor='end',color=blue)
path([(625,161),(608,161),(608,125),(616,125)],blue)
node(616,193,245,47,'Projection + position\n123 local tokens, d=256',b_fill,18,stroke=b_border)
path([(738,147),(738,193)],teal)

# Query augmentation is outside the repeated local-attention block.
txt(990,87,'q, sg(μ, H)',18)
path([(990,91),(990,101)])
node(900,101,195,37,'Query augmentation',b_fill,19,stroke=b_border)
# Repeat contains current-query concatenation, residual attention and FFN.
rect(880,146,318,108,'#FCFAFD',b_border,6,'4 4',1.1)
txt(1174,172,'×2',19,bold=True,color=b_border)
node(886,195,171,42,'Residual attention\n8 heads',b_pale,17,stroke=b_border)
node(1076,195,120,42,'Residual FFN\n1024',b_pale,17,stroke=b_border)
path([(1057,216),(1076,216)])
# Q comes from the current block query; the repeat refreshes that query each block.
path([(990,138),(990,195)])
txt(979,191,'Q',17,anchor='end')
# Fixed local tokens reach the concatenation from above.
path([(861,216),(874,216),(874,156),(1128,156),(1128,170)],teal)
# The crossing is not a junction: Q passes over local tokens.
path([(990,148),(990,166)],'white',5,arrow=False)
path([(990,148),(990,166)],ink,1.7,arrow=False)
# Current query is also a K/V token, in addition to the 123 local tokens.
path([(990,180),(1118,180)],teal)
dot(990,180,teal)
txt(1053,171,'current query',17,color=teal)
circ(1128,180,10,'C',fill='#EAF2EE',stroke=teal,size=17)
path([(1128,190),(1041,190),(1041,195)],teal)
txt(1161,190,'K/V',17,color=teal)
# The final normalization is outside the repeat boundary.
node(1210,195,67,42,'Final\nLN',b_fill,17,stroke=b_border)
path([(1196,216),(1210,216)])

# Distinct residual heads and distinct base-logit skip inputs.
node(1298,105,116,36,'Class residual',b_fill,17,stroke=b_border)
node(1298,195,116,36,'Edge residual',b_fill,17,stroke=b_border)
path([(1277,216),(1285,216),(1285,123),(1298,123)])
path([(1285,216),(1285,213),(1298,213)])
dot(1285,216)
circ(1452,123,13,'+',size=22)
circ(1452,213,13,'+',size=22)
path([(1414,123),(1439,123)])
path([(1414,213),(1439,213)])
txt(1452,88,'base class',17,color=blue)
path([(1452,94),(1452,110)],blue)
txt(1452,178,'base edge',17,color=blue)
path([(1452,184),(1452,200)],blue)
path([(1465,123),(1559,123)],blue)
txt(1516,109,'classes',18,color=blue)
# Combined edge logits, not residual-only logits, feed both decode and teacher.
node(1485,194,76,39,'Decode', '#FFF1CF',18,shape='rule')
path([(1465,213),(1485,213)],blue)
txt(1523,177,'same r0',17,color=blue)
path([(1523,182),(1523,194)],blue)
path([(1561,213),(1569,213)],blue)
txt(1523,248,'boxes',18,color=blue)

# Training-only selection; the teacher tap precedes geometric decoding.
rect(618,278,940,78,'#FFFAF0',amber,7,'5 4',1.1)
txt(1170,297,'Selective transfer · training only',18,color=amber)
node(624,311,132,35,'Same assignment','#FFF1DD',17,stroke=amber)
node(770,311,82,35,'Support','#FFF1DD',18,stroke=amber,shape='rule')
node(866,307,140,44,'Better edges\nm=.02, τ=.10','#FFF1DD',17,stroke=amber,shape='rule')
node(1020,311,174,35,'Mixed ΔIoU > 0','#FFF1DD',18,stroke=amber,shape='rule')
node(1210,311,286,35,'KL → G · peak λ=.15','#FFF1DD',18,stroke=amber,shape='loss')
for a,b in [(756,770),(852,866),(1006,1020),(1194,1210)]:
    path([(a,328),(b,328)],amber,1.5,'5 4')
path([(1475,213),(1475,269),(690,269),(690,311)],amber,1.5,'5 4')
dot(1475,213,amber)
rect(921,258,225,21,'white','white',0,sw=0)
txt(1034,273,'sg(combined edge logits)',17,color=amber)


# (a) Complete detector. G is an embedded localization path, not the host decoder.
rect(24,397,1552,331,'white','#ADB4BB',0,sw=1.25)
txt(44,427,'(a) Complete detector',25,anchor='start',bold=True)
# Top-right margin is kept clear for the expert expansion guide.
rect(50,448,570,216,'#FAFBFC','#ADB4BB',0,sw=1.1)
txt(335,474,'Feature extraction',23,bold=True)
rect(660,448,545,216,'#FAFBFC','#ADB4BB',0,sw=1.1)
txt(932,476,'RT-DETR decoder · 6 layers',23,bold=True)
# Three expansion links end on their actual modules. They have no arrowheads.
path([(454,364),(482,397),(482,541)],'#79A092',1.45,'3 5',False)
path([(1430,364),(1430,397),(1350,520)],'#9C81AD',1.45,'3 5',False)
path([(1105,631),(1190,670),(1190,728),(1147,761)],'#729ABF',1.45,'3 5',False)
node(68,510,129,64,'Backbone','#EDF0F3',22)
node(237,502,147,80,'Hybrid\nencoder','#EDF0F3',22,shape='fusion')
path([(197,542),(245,542)])
txt(62,491,'Image',20,anchor='start')
path([(83,495),(83,510)])
node(440,541,125,45,'F · P3 refine','#DEEEE3',21,bold=True,stroke=teal)
path([(374,560),(440,563)],teal);txt(406,550,'P3',19,color=teal)
path([(383,509),(675,509),(675,528),(682,528)])
txt(523,501,'P5',19)
path([(378,533),(670,533),(670,548),(682,548)])
txt(602,527,'P4',19)
node(682,519,185,64,'Attention + FFN\n300 queries','#EDF0F3',21)
path([(565,563),(682,563)],teal);txt(611,551,'P3*',19,color=teal)
node(967,500,170,38,'Class head','#EDF0F3',22)
node(967,583,170,48,'G · GCDL\nlocalization','#DCEAF8',21,bold=True,stroke=blue)
path([(867,551),(1245,551)])
dot(923,551)
path([(923,551),(923,519),(967,519)])
path([(923,551),(923,607),(967,607)])
txt(1174,542,'final q',18)
node(1245,520,160,82,'B · local\nexpert','#EBE0F0',22,bold=True,stroke='#775789')
path([(1137,519),(1215,519),(1215,534),(1245,534)])
txt(1175,509,'class',18)
path([(1137,607),(1228,607),(1228,578),(1245,578)],blue)
txt(1210,627,'box, logits, r0',18,color=blue)
node(1452,530,102,64,'Classes\n+ boxes','#F6F7F8',21,shape='terminal')
path([(1405,561),(1452,561)])
# Local image information is shared, with P2 bypassing the hybrid encoder.
node(102,614,61,28,'P2','#EDF0F3',20)
path([(132,574),(132,614)])
routes=[[(132,642),(132,699),(1325,699),(1325,602)],[(598,563),(598,699)],[(638,533),(638,699)]]
for p in routes:path(p,'white',5,arrow=False)
for j,p in enumerate(routes):path(p,teal,1.7,arrow=j==0)
for p in [(598,563),(598,699),(638,533),(638,699)]:dot(*p,teal)
txt(914,691,'Shared local features: P2, P3*, P4',21,color=teal)
txt(1367,647,'after the final layer',18,color='#775789')

# (c) One parent, three internal mechanisms. G.1/G.2/G.3 are not peer modules.
rect(24,761,1552,396,'white',blue,0,sw=1.6)
rect(25,762,1550,48,'#E7EFF8','none',0,sw=0)
txt(46,793,'(c) GCDL localization path (G)',26,anchor='start',bold=True,color=blue)
node(1210,774,342,32,'r0 = sg(incoming reference)','#F8FBFF',20,stroke=blue)
txt(935,794,'same frame for all six layers',19,color=blue)
# Child boundaries are subordinate to the enclosing G parent.
rect(44,841,724,159,'#FBFDFF','#B2C5D8',0,sw=1)
txt(60,866,'G.1  Distribution accumulation',21,anchor='start',bold=True)
rect(810,841,744,159,'#FBFDFF','#B2C5D8',0,sw=1)
txt(826,866,'G.2  Feasible geometry',21,anchor='start',bold=True)
node(60,900,102,40,'Query q_l','#F0F5FB',21)
circ(184,920,12,'+',size=22)
path([(162,920),(172,920)])
path([(184,890),(184,908)]);txt(169,887,'sg(q_prev)',18,anchor='end')
node(216,899,113,42,'Edge head','#DDE9F6',21)
path([(196,920),(216,920)])
circ(370,920,15,'+',size=24)
path([(329,920),(355,920)]);txt(344,889,'Δz_l',18)
path([(370,974),(370,935)]);txt(354,981,'z_prev',18,anchor='end')
node(475,894,146,52,'Softmax\nIntegral','white',21)
path([(385,920),(475,920)]);txt(428,887,'4 × 33',19,color=blue)
txt(539,979,'z_l = z_prev + Δz_l',21,color=blue)
path([(621,920),(822,920)],blue)
txt(717,909,'offsets',20,color=blue)
node(822,890,151,58,'Reference\n+ offsets','#F4F8FD',20)
path([(1210,790),(1184,790),(1184,824),(800,824),(800,901),(822,901)],blue)
dot(1184,824,blue)
path([(973,920),(994,920)],blue);dot(994,920,blue)
node(1037,880,113,38,'Center','white',21)
node(1037,937,113,34,'Raw extent','white',19)
path([(994,920),(994,899),(1037,899)],blue)
path([(994,920),(994,954),(1037,954)],blue)
node(1198,936,160,36,'Extent floor','#FFF2CF',21,shape='rule')
path([(1150,954),(1198,954)],blue)
txt(1277,917,'δ=10⁻³, ε',19,color=blue)
path([(994,920),(994,924),(1278,924),(1278,936)],blue)
node(1390,896,128,54,'Box\nassembly','#F3F7FC',21,shape='fusion')
path([(1150,899),(1374,899),(1374,879),(1454,879),(1454,896)],blue)
txt(1246,888,'center unchanged',18,color=blue)
path([(1358,954),(1374,954),(1374,923),(1395,923)],blue)
txt(1204,990,'reference-scale + precision floor',18,color=blue)
path([(1513,923),(1563,923),(1563,1015),(44,1015)],blue)
rect(500,1002,717,24,'white','none',0,sw=0)
txt(858,1020,'sg(box) → attention reference of the next decoder layer',20,color=blue)
# G supervision is an internal training child, not a fourth peer module.
rect(44,1034,1510,109,'#FFF9EF',amber,0,'6 4',1.15)
txt(60,1057,'G.3  LQS-weighted FGL · training only',21,anchor='start',bold=True,color=amber)
node(60,1080,165,36,'sg(matched IoU)','#FFF1DA',19,stroke=amber)
node(255,1080,155,36,'Eligible mean','#FFF1DA',20,stroke=amber)
path([(225,1098),(255,1098)],amber,1.5,'5 4')
node(455,1076,278,45,'q′ = (1−α_l)q + α_lq̄','#FFF0D1',22,stroke=amber,shape='rule')
path([(410,1098),(455,1098)],amber,1.5,'5 4')
path([(237,1098),(237,1126),(497,1126),(497,1121)],amber,1.5,'5 4');dot(237,1098,amber)
txt(648,1069,'α_l: 0.25 → 0',18,color=amber)
node(783,1080,155,36,'FGL weights','#FFF1DA',21,stroke=amber)
path([(733,1098),(783,1098)],amber,1.5,'5 4')
txt(851,1132,'Σq′ = Σq',17,color=amber)
node(979,1076,180,45,'FGL loss','#FFEDC4',23,stroke=amber,shape='loss')
path([(938,1098),(979,1098)],amber,1.5,'5 4')
txt(1070,1059,'edge logits',18,color=amber);path([(1070,1064),(1070,1076)],amber,1.5,'5 4')
node(1242,1080,181,36,'Target encoding','#FFF1DA',20,stroke=amber)
path([(1242,1098),(1159,1098)],amber,1.5,'5 4')
path([(1184,824),(1540,824),(1540,1064),(1332,1064),(1332,1080)],amber,1.4,'5 4')
txt(1475,1086,'GT',20,color=amber)
path([(1460,1098),(1423,1098)],amber,1.5,'5 4')

# Visual grammar: hierarchy uses containment; line styles are reserved for relations.
path([(31,1184),(74,1184)]);txt(85,1190,'Prediction / features',19,anchor='start')
path([(365,1184),(408,1184)],amber,1.6,'5 4');txt(420,1190,'Training only',19,anchor='start')
path([(670,1184),(713,1184)],'#879099',1.4,'3 5',False);txt(725,1190,'Module expansion',19,anchor='start')
txt(1050,1190,'sg: stop-gradient',19,anchor='start')
txt(1332,1190,'C: concatenation',19,anchor='start')

parts.append('</svg>')
out=ROOT/'assets';out.mkdir(exist_ok=True)
svg=out/'architecture_dense.svg';svg.write_text('\n'.join(parts),encoding='utf-8')
drawing=svg2rlg(str(svg));renderPDF.drawToFile(drawing,str(out/'architecture_dense.pdf'))
poppler='C:/Users/16946/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe'
subprocess.run([poppler,'-r','150','-png','-singlefile',str(out/'architecture_dense.pdf'),str(out/'architecture_dense')],check=True,capture_output=True)
print(json.dumps({'svg':str(svg),'canvas':[W,H],'density':'explicit host and localization-path hierarchy; peripheral F/B details and full-width G mechanisms','source_snapshot':'a43056a','new_model_execution':False}))

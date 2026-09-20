"""Publication plots from frozen metrics and annotation summaries only."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]
deps=ROOT/'qa/drawing_dependencies'
if deps.exists(): sys.path.insert(0,str(deps))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.labelsize':9,
                     'axes.titlesize':10,'svg.fonttype':'none','pdf.fonttype':42,
                     'axes.spines.top':False,'axes.spines.right':False})
OUT=ROOT/'assets'
def save(fig,name):
    for ext in ['pdf','svg','png']:fig.savefig(OUT/f'{name}.{ext}',dpi=360,bbox_inches='tight',facecolor='white')
    plt.close(fig)

p=json.loads((ROOT/'inputs/motivation_profile.json').read_text())
fig,(a,b)=plt.subplots(1,2,figsize=(7.2,2.6),gridspec_kw={'wspace':.36})
counts=np.array([r['count'] for r in p['input_scale_profile']['bins']])
values=counts/counts.sum()*100
a.bar(range(5),values,color=['#436D91']*3+['#CAD2D9']*2,width=.67)
for i,v in enumerate(values):a.text(i,v+.6,f'{v:.1f}%',ha='center',fontsize=8)
a.set_xticks(range(5),['0–8','8–16','16–32','32–64','≥64']);a.set_ylim(0,42)
a.set_xlabel('Equivalent side at 640 × 640 (pixels)');a.set_ylabel('Validation boxes (%)')
a.set_title('(a) Object scale profile',loc='left',fontweight='bold')
a.text(.96,.91,'85.9% below 32 px',ha='right',va='top',transform=a.transAxes,color='#225E9C',fontsize=9)
for c,color in zip(p['analytic_iou']['curves'],['#BC493A','#B98A35','#436D91']):
    x=[r['displacement_px'] for r in c['samples']];y=[r['iou'] for r in c['samples']]
    b.plot(x,y,color=color,lw=1.8,label=f"Width {c['box_width_px']} px")
b.axvline(1,color='#89939D',lw=.8,ls=':');b.set_xlim(0,4);b.set_ylim(.3,1.02)
b.set_xlabel('Horizontal displacement (pixels)');b.set_ylabel('IoU')
b.set_title('(b) Analytic overlap sensitivity',loc='left',fontweight='bold');b.legend(frameon=False,fontsize=8,loc='lower left')
fig.subplots_adjust(bottom=.21,top=.86,left=.08,right=.985)
save(fig,'scale_and_geometry')

raw=ROOT/'inputs/external_class_profile/source'
d=json.loads((raw/'dfine_final_test.cap300.json').read_text());f=json.loads((raw/'joint_final_test.cap300.json').read_text())
names=['Pedestrian','People','Bicycle','Car','Van','Truck','Tricycle','Awning-\ntricycle','Bus','Motor']
da=np.array([d['per_class_AP'][str(i)]*100 for i in range(10)])
fa=np.array([f['per_class_AP'][str(i)]*100 for i in range(10)])
fig,axes=plt.subplots(1,2,figsize=(7.2,3.05),gridspec_kw={'width_ratios':[1.55,1],'wspace':.13})
y=np.arange(10)
a,b=axes
for i in range(10):a.plot([da[i],fa[i]],[i,i],color='#CDD2D7',lw=2)
a.scatter(da,y,s=24,c='#768A9B',label='D-FINE-L (reprod.)',zorder=3)
a.scatter(fa,y,s=24,c='#BC493A',label='Full (ours)',zorder=3)
a.set_yticks(y,names);a.invert_yaxis();a.tick_params(axis='y',length=0,labelsize=8)
a.set_xlabel('Per-class AP (%)');a.set_xlim(0,max(fa)*1.08)
a.set_title('(a) Complete-system class AP',loc='left',fontweight='bold');a.legend(frameon=False,fontsize=7.5,loc='upper right')
b.barh(y,fa-da,color='#39817B',height=.58);b.set_yticks(y,[]);b.invert_yaxis();b.set_xlim(0,4.8)
for i,v in enumerate(fa-da):b.text(v+.07,i,f'+{v:.2f}',va='center',fontsize=8,color='#286D66')
b.set_xlabel('AP gain (percentage points)');b.set_title('(b) Full minus reproduction',loc='left',fontweight='bold')
for ax in axes:ax.xaxis.grid(True,color='#E7EBEE',lw=.6);ax.set_axisbelow(True);ax.spines['left'].set_visible(False)
fig.subplots_adjust(left=.14,right=.98,bottom=.17,top=.88)
save(fig,'class_comparison')
print('Built scale_and_geometry and class_comparison from frozen records.')

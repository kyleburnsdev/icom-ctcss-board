"""Draw B1's operator layout and actual sliced extrusion paths.

Uses matplotlib and Pillow bundled with FreeCAD 1.1's Python. Run after the
CAD and slicer generators. Mesh outlines come from the delivered STL files;
colored component envelopes in the layout are explicitly schematic.
"""
from pathlib import Path
import json
import re
import math
import zipfile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon
from matplotlib.collections import LineCollection

ROOT=Path(__file__).resolve().parents[1]
IMG=ROOT/'docs/images/bench-holder'
EV=ROOT/'docs/verification/bench-holder'
OUT=ROOT/'manufacturing/bench-holder'
IMG.mkdir(parents=True,exist_ok=True)
g=json.loads((EV/'geometry.json').read_text())
r=json.loads((EV/'slicer.json').read_text())


def layout():
    fig,ax=plt.subplots(figsize=(10,10))
    ax.add_patch(Rectangle((0,0),210,220,fc='#edf1f4',ec='#33495b',lw=2))
    ax.add_patch(Rectangle((0,0),210,90,fc='#d2e0ea',ec='#33495b',lw=2))
    ax.add_patch(Rectangle((25,105),150,100,fc='#b9dfc0',ec='#246d40',lw=2))
    for x,y in g['board_holes_mm']:ax.add_patch(Circle((x,y),3.75,fc='white',ec='#246d40'))
    ax.text(100,163,'POPULATED PCB\n150 × 100 mm\ncomponents face up',ha='center',va='center',fontsize=14)
    ax.text(100,132,'All four existing mounts\n12 mm support above floor',ha='center',va='center',fontsize=11)
    ax.add_patch(Rectangle((12,25),80,40,fc='#25765e',ec='#164936'))
    ax.add_patch(Rectangle((18,39),65,15,fc='#cce5c8'))
    ax.text(52,46.5,'Grove V4.0',ha='center',va='center',fontsize=10)
    for x,y in g['lcd_holes_mm']:ax.add_patch(Circle((x,y),2,fc='white',ec='#164936'))
    labels={'Encoder':'TONE','Bypass':'BYPASS','PttButton':'PTT TEST',
            'MicAdapter':'MIC','RadioAdapter':'RADIO','PttLed':'PTT','BypassLed':'BYPASS'}
    for name,x,y,d in g['control_holes']:
        ax.add_patch(Circle((x,y),d/2,fc='#f9fafb',ec='#33495b',lw=1.3))
        ax.text(x,y+max(d/2,4)+4,labels[name],ha='center',va='bottom',fontsize=8)
    ax.text(105,94,'Harness combs → leave slack → PCB headers',ha='center',fontsize=10)
    ax.annotate('',xy=(210,-10),xytext=(0,-10),arrowprops={'arrowstyle':'<->'})
    ax.text(105,-15,'210 mm',ha='center',va='top',fontsize=11)
    ax.annotate('',xy=(-12,220),xytext=(-12,0),arrowprops={'arrowstyle':'<->'})
    ax.text(-18,110,'220 mm',rotation=90,ha='center',va='center',fontsize=11)
    ax.text(105,-29,'FRONT / OPERATOR',ha='center',fontsize=11,weight='bold')
    ax.set(xlim=(-28,226),ylim=(-38,235),aspect='equal')
    ax.axis('off')
    fig.suptitle('B1 mounting layout — control panel shown flat',fontsize=18,weight='bold')
    fig.text(.5,.025,'PCB plan and flattened control face; component bodies are schematic.\nPanel rises 30° from front Z30 to rear Z75; PCB underside Z15. Units: mm.',ha='center',fontsize=10)
    fig.savefig(IMG/'layout.png',dpi=160,bbox_inches='tight');plt.close(fig)


def wiring():
    fig,ax=plt.subplots(figsize=(12,6));ax.set(xlim=(0,12),ylim=(0,6));ax.axis('off')
    def box(x,y,w,h,text,color):
        ax.add_patch(Rectangle((x,y),w,h,fc=color,ec='#33495b',lw=1.5))
        ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=11)
    box(.2,3.5,2.4,1.6,'PROGRAMMABLE\nSUPPLY\n8.00 V','#dde8ee')
    box(4,1.2,4.5,4.1,'PCB HEADERS / TEST POINTS\n\nJ2/2   RAW (+8 V)\nJ2/6   GND\n\nJ1/5   PTT SENSE\nJ1/6   GND','#d4e9d6')
    ax.annotate('+',xy=(4,4.15),xytext=(2.6,4.65),arrowprops={'arrowstyle':'->','color':'#b63f35'},color='#b63f35',fontsize=13)
    ax.annotate('−',xy=(4,3.7),xytext=(2.6,3.75),arrowprops={'arrowstyle':'->','color':'#33495b'},fontsize=13)
    box(9.1,1.9,2.6,1.3,'16 mm BUTTON\nNormally open','#f6e6c8')
    ax.plot([8.5,9.1],[2.55,2.75],color='#33495b');ax.plot([8.5,9.1],[2.1,2.3],color='#33495b')
    box(.3,.2,11.4,.65,'TP3 (+5 V) ── 10 kΩ temporary pull-up ── TP8 (RADIO_PTT)', '#edf1f4')
    ax.text(6,5.75,'Radio-free wiring — schematic, use PCB contact numbers',ha='center',fontsize=16,weight='bold')
    ax.text(6,1.05,'Radio and hand mic disconnected. USB disconnected whenever RAW power is on.',ha='center',fontsize=10)
    fig.savefig(IMG/'wiring.png',dpi=150,bbox_inches='tight');plt.close(fig)


def clearance():
    fig,ax=plt.subplots(figsize=(12,5))
    rear=90*math.cos(math.radians(g['panel_angle_deg']))
    ax.add_patch(Rectangle((0,0),220,3,fc='#607c91',ec='#33495b'))
    ax.add_patch(Polygon([(0,3),(rear,3),(rear,75),(0,30)],fc='#c7d3dc',ec='#33495b'))
    ax.plot([0,rear],[30,75],lw=5,color='#b48d51')
    for y in [111,199]:ax.add_patch(Rectangle((y-3.75,3),7.5,12,fc='#607c91',ec='#33495b'))
    ax.add_patch(Rectangle((105,15),100,1.5,fc='#3e8d55',ec='#246d40'))
    ax.plot([150,150],[15,13],lw=3,color='#a66e36')
    ax.annotate('',xy=(165,13),xytext=(165,3),arrowprops={'arrowstyle':'<->','lw':1.5})
    ax.text(169,8,'10 mm clearance\nwith 2 mm lead tail',va='center',fontsize=10)
    ax.annotate('PCB underside Z15',xy=(195,15),xytext=(165,33),arrowprops={'arrowstyle':'->'},fontsize=10)
    ax.annotate('Upper 6 mm M3 thread\nOpen lower clearance bore',xy=(111,12),xytext=(95,49),arrowprops={'arrowstyle':'->'},fontsize=10)
    ax.text(18,56,'Control panel\n30° above horizontal',fontsize=11)
    ax.text(15,6,'Open wiring space between side rails',fontsize=9)
    ax.set(xlim=(-8,230),ylim=(-5,86),aspect='equal',xlabel='Front → rear, assembly Y (mm)',ylabel='Z (mm)')
    ax.grid(alpha=.12)
    ax.set_title('B1 side projection — board clearance and mounting',fontsize=16,weight='bold')
    fig.text(.5,.01,'Dimensioned schematic projection. Lead-tail allowance is the existing assembly requirement; inspect the populated board before clamping.',ha='center',fontsize=9)
    fig.savefig(IMG/'clearance.png',dpi=160,bbox_inches='tight');plt.close(fig)


def slices():
    colors={'Outer wall':'#153b53','Inner wall':'#227ca0','Bottom surface':'#208f75',
            'Top surface':'#208f75','Internal solid infill':'#64acac','Sparse infill':'#b4c8c7',
            'Bridge':'#dd692b','Overhang wall':'#ad4ca0','Brim':'#999999','Gap infill':'#e8a632'}
    for p in r['plates']:
        targets={1:[.2,1.5,3.2,8.6,9.3,14.8],2:[.2,3,8.6,9.3,15.4,71],3:[.2,1.4,2.8,3.2,8.8,10.2]}[p['id']]
        with zipfile.ZipFile(OUT/'bench-holder-b1.3mf') as z:code=z.read(f"Metadata/plate_{p['id']}.gcode").decode()
        heights=sorted({round(float(line.split(':')[1]),3) for line in code.splitlines() if line.startswith('; Z_HEIGHT:')})
        targets=[min(heights,key=lambda h:abs(h-t)) for t in targets]
        selected={t:[] for t in targets};pos={'X':0.,'Y':0.};height=None;feature='';counts={}
        for line in code.splitlines():
            if line.startswith('; Z_HEIGHT:'):height=round(float(line.split(':')[1]),3)
            if line.startswith('; FEATURE:'):feature=line.split(':',1)[1].strip()
            if not line.startswith(('G1 ','G2 ','G3 ')):continue
            values={k:float(v) for k,v in re.findall(r'([XYEIJ])(-?\d*\.?\d+)',line.split(';')[0])}
            previous=(pos['X'],pos['Y']);pos.update({k:v for k,v in values.items() if k in 'XY'});end=(pos['X'],pos['Y'])
            if height is None or values.get('E',0)<=0 or previous==end or feature not in colors:continue
            counts[height]=counts.get(height,0)+1
            if height in selected:
                if line.startswith(('G2 ','G3 ')) and ('I' in values or 'J' in values):
                    cx=previous[0]+values.get('I',0);cy=previous[1]+values.get('J',0)
                    a=math.atan2(previous[1]-cy,previous[0]-cx);b=math.atan2(end[1]-cy,end[0]-cx)
                    span=(b-a)%(2*math.pi) if line.startswith('G3 ') else -((a-b)%(2*math.pi))
                    radius=math.hypot(previous[0]-cx,previous[1]-cy)
                    n=max(2,int(abs(span)/.08)+1)
                    points=[(cx+radius*math.cos(a+span*i/n),cy+radius*math.sin(a+span*i/n)) for i in range(n+1)]
                    selected[height].extend((points[i],points[i+1],colors[feature]) for i in range(n))
                else:selected[height].append((previous,end,colors[feature]))
        fig,axs=plt.subplots(2,3,figsize=(12,9),layout='constrained')
        for ax,t in zip(axs.flat,targets):
            seg=selected[t];assert seg,(p['id'],t)
            ax.add_collection(LineCollection([(a,b) for a,b,c in seg],colors=[c for a,b,c in seg],linewidths=.45))
            ax.set(xlim=(0,256),ylim=(0,256),aspect='equal',title=f'Z {t:.1f} mm',xlabel='X (mm)',ylabel='Y (mm)')
            ax.grid(alpha=.15)
        fig.suptitle(p['name']+' — actual extrusion paths',fontsize=15)
        fig.savefig(EV/f"slice-{p['id']}.png",dpi=130);plt.close(fig)
        p['inspected_layer_heights_mm']=targets;p['extrusion_layer_count']=len(counts)
    (EV/'layer-checks.json').write_text(json.dumps({'revision':'B1','project_sha256':r['sha256'],
        'plates':[{'id':p['id'],'layers':p['inspected_layer_heights_mm'],'extrusion_layer_count':p['extrusion_layer_count']} for p in r['plates']]},indent=2))


if __name__=='__main__':layout();wiring();clearance();slices()

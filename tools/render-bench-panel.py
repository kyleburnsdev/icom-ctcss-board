"""Render B2 dimensioned assembly instructions and actual G-code layer views.

Run with FreeCAD 1.1's bundled Python (matplotlib). No CAD geometry is edited.
"""
from pathlib import Path
import json, math, re, zipfile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from matplotlib.collections import LineCollection

ROOT=Path(__file__).resolve().parents[1]
EV=ROOT/'docs/verification/bench-panel-b2'
IMG=ROOT/'docs/images/bench-panel-b2'
OUT=ROOT/'manufacturing/bench-panel-b2'
IMG.mkdir(parents=True,exist_ok=True)
g=json.loads((EV/'cad-checks.json').read_text())
r=json.loads((EV/'slicer-checks.json').read_text())

def layout():
    fig,axs=plt.subplots(3,1,figsize=(12,12),layout='constrained',height_ratios=[1,1,1.1])
    for ax in axs[:2]:
        ax.add_patch(Rectangle((0,0),210,90,fc='#e1e8ed',ec='#344e61',lw=2))
        for x,y in [(7,8),(203,8),(7,82),(203,82)]:ax.add_patch(Circle((x,y),1.7,fc='white',ec='#344e61'))
        ax.add_patch(Rectangle(g['window_mm'][:2],*g['window_mm'][2:],fc='#acc6ae',ec='#344e61',lw=1.5))
        for x,y,d in [(120,48,7.2),(155,48,6.5),(190,48,16.3),(120,18,16.2),(165,18,16.2),(148,72,5.2),(172,72,5.2)]:ax.add_patch(Circle((x,y),d/2,fc='white',ec='#344e61'))
        ax.set(xlim=(-4,214),ylim=(-5,95),aspect='equal');ax.axis('off')
    axs[0].set_title('FRONT — screen window, engraved labels, unchanged base holes',fontsize=14,weight='bold')
    for text,x,y in [('LCD',55,73),('TONE',120,66),('BYPASS',155,57),('PTT TEST',190,63),('PTT',148,79),('BYPASS',172,79),('MIC',120,4),('RADIO',165,4)]:axs[0].text(x,y,text,ha='center',fontsize=8)
    axs[0].text(53,46,'65.5 × 15.5',ha='center',va='center',fontsize=10)
    ax=axs[1];ax.set_title('REAR — shown through face in the same XY coordinates',fontsize=14,weight='bold')
    ax.add_patch(Rectangle(g['lcd_pcb_origin_mm'],80,40,fc='#6da483',alpha=.6,ec='#276547'))
    for x,y in g['all_six_ear_centers_mm']:
        ax.add_patch(Circle((x,y),2.1,fc='#6da483',ec='#276547'))
        ax.add_patch(Circle((x,y),1.15,fc='white',ec='#276547'))
    for x,y in g['clamp_centers_mm']:
        ax.add_patch(Circle((x,y),8.5,fc='#c5cbd1',ec='#45515e',alpha=.85))
        ax.add_patch(Circle((x,y),2.5,fc='#657887',ec='#45515e'))
    ax.annotate('4 printed thumb screws\nheads overlap mounting ears',xy=g['clamp_centers_mm'][0],xytext=(4,-18),fontsize=10,arrowprops={'arrowstyle':'->'})
    ax.annotate('Grove socket + cable stay inside',xy=(39,29),xytext=(100,90),fontsize=10,arrowprops={'arrowstyle':'->'})
    ax.set_ylim(-22,102)
    ax=axs[2];ax.axis('off');ax.set(xlim=(-4,40),ylim=(-22,12))
    ax.set_title('SECTION AT ONE LOWER EAR — schematic, axial references in mm',fontsize=14,weight='bold')
    # X here is distance along the panel; Z is the actual panel-local normal.
    ax.add_patch(Rectangle((0,0),32,3,fc='#9db5c8',ec='#344e61'))
    depth=g['support_depth_mm'];pcb_rear=-depth-1.6
    ax.add_patch(Rectangle((5.2,-depth),9.6,depth,fc='#9db5c8',ec='#344e61'))
    ax.add_patch(Rectangle((14.9,-depth),4.2,depth,fc='#9db5c8',ec='#344e61'))
    ax.add_patch(Rectangle((14.9,pcb_rear),12,1.6,fc='#6da483',ec='#276547'))
    ax.add_patch(Rectangle((1.5,pcb_rear-2.4),17,2.4,fc='#c5cbd1',ec='#45515e'))
    ax.add_patch(Rectangle((7.5,pcb_rear),5,7,fc='#657887',ec='#45515e'))
    ax.annotate('Front Z+3 / rear Z0',xy=(27,2),xytext=(18,9),fontsize=10,arrowprops={'arrowstyle':'->'})
    ax.annotate(f'Ear seats: Z−{depth:.2f}\nPCB rear: Z{pcb_rear:.2f} nominal',xy=(18,-depth),xytext=(21,-5),fontsize=10,arrowprops={'arrowstyle':'->'})
    ax.text(2,-21,'Finger-tight head clamps the ear; glass is not in the clamping stack.',fontsize=10)
    fig.savefig(IMG/'layout.png',dpi=160);plt.close(fig)

def layers():
    colors={'Outer wall':'#153b53','Inner wall':'#227ca0','Bottom surface':'#208f75',
        'Top surface':'#208f75','Internal solid infill':'#64acac','Sparse infill':'#b4c8c7',
        'Bridge':'#e27625','Overhang wall':'#ae4b9b','Brim':'#999999','Gap infill':'#e8a632'}
    record=[]
    for i in [1,2]:
        with zipfile.ZipFile(OUT/'bench-panel-b2.3mf') as z:lines=z.read(f'Metadata/plate_{i}.gcode').decode().splitlines()
        heights=sorted({float(s.split(':')[1]) for s in lines if s.startswith('; Z_HEIGHT:')})
        targets=[min(heights,key=lambda h:abs(h-t)) for t in [.2,.44,1.04,1.52,4.04,g['support_depth_mm']+4.2]]
        selected={t:[] for t in targets};pos={'X':0.,'Y':0.};height=None;feature=''
        for line in lines:
            if line.startswith('; Z_HEIGHT:'):height=float(line.split(':')[1])
            if line.startswith('; FEATURE:'):feature=line.split(':',1)[1].strip()
            if not line.startswith(('G1 ','G2 ','G3 ')):continue
            values={k:float(v) for k,v in re.findall(r'([XYEIJ])(-?\d*\.?\d+)',line.split(';')[0])}
            old=(pos['X'],pos['Y']);pos.update({k:v for k,v in values.items() if k in pos});end=(pos['X'],pos['Y'])
            if height not in selected or values.get('E',0)<=0 or feature not in colors:continue
            if line.startswith(('G2 ','G3 ')) and ('I' in values or 'J' in values):
                cx=old[0]+values.get('I',0);cy=old[1]+values.get('J',0)
                a=math.atan2(old[1]-cy,old[0]-cx);b=math.atan2(end[1]-cy,end[0]-cx)
                span=(b-a)%(2*math.pi) if line.startswith('G3 ') else -((a-b)%(2*math.pi))
                n=max(2,int(abs(span)/.08)+1);rad=math.hypot(old[0]-cx,old[1]-cy)
                pts=[(cx+rad*math.cos(a+span*j/n),cy+rad*math.sin(a+span*j/n)) for j in range(n+1)]
                selected[height].extend((pts[j],pts[j+1],colors[feature]) for j in range(n))
            else:selected[height].append((old,end,colors[feature]))
        fig,axes=plt.subplots(2,3,figsize=(12,9),layout='constrained')
        for ax,t in zip(axes.flat,targets):
            seg=selected[t];assert seg,(i,t)
            ax.add_collection(LineCollection([(a,b) for a,b,c in seg],colors=[c for a,b,c in seg],linewidths=.5))
            ax.set(xlim=(15,240),ylim=(25,180),aspect='equal',title=f'Z {t:.2f} mm',xlabel='X mm',ylabel='Y mm')
        fig.suptitle(f'B2 plate {i} — actual extrusion; bridges orange / overhangs magenta',fontsize=14)
        fig.savefig(EV/f'slice-{i}.png',dpi=150);plt.close(fig)
        record.append({'plate':i,'inspected_heights_mm':targets,'layers':len(heights)})
    (EV/'layer-checks.json').write_text(json.dumps({'revision':'B2','project_sha256':r['sha256'],'plates':record},indent=2)+'\n')

if __name__=='__main__':layout();layers()

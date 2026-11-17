"""Render engineering schematics for C1; ordinary Python with matplotlib."""
from pathlib import Path
import json
import math
import re
import zipfile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon
from matplotlib.collections import LineCollection

ROOT=Path(__file__).resolve().parents[1]
IMG=ROOT/'docs/images/enclosure-c1'
EV=ROOT/'docs/verification/enclosure-c1'

def main():
    c=json.loads((EV/'cad-checks.json').read_text())
    fig,axes=plt.subplots(1,2,figsize=(13,8),layout='constrained',width_ratios=[1,1.2])
    ax=axes[0]
    ax.add_patch(Rectangle((0,0),156,240,fc='#e4e9ed',ec='#294454',lw=2))
    ax.add_patch(Rectangle((28,84),100,150,fc='#b8d4b6',ec='#37664e',lw=1.8))
    for x,y in c['board_holes_mm']:
        ax.add_patch(Circle((x,y),2,fc='white',ec='#37664e'))
        direction=-1 if x<78 else 1
        ax.add_patch(Rectangle((x-18 if direction<0 else x-4,y-5),22,10,fc='#70869c',ec='#294454'))
    ax.add_patch(Rectangle((0,0),156,77.94,fc='#aabcca',ec='#294454',alpha=.7))
    for x in [1,143]:ax.add_patch(Rectangle((x,0),9 if x==1 else 12,77.94,fc='#526c82'))
    ax.text(78,154,'UNCHANGED PCB\n100 across × 150 deep\n90° from bench holder',ha='center',va='center',fontsize=11)
    ax.text(78,42,'CONTROL PANEL\n156 × 90 surface\n30° above the bench',ha='center',va='center',fontsize=11)
    ax.annotate('Cover slides rearward\nfor removal',xy=(146,238),xytext=(180,188),arrowprops={'arrowstyle':'->'},fontsize=10)
    ax.text(78,-12,'FRONT / OPERATOR',ha='center',weight='bold')
    ax.annotate('',(0,254),(156,254),arrowprops={'arrowstyle':'<->'})
    ax.text(78,257,'156 mm',ha='center')
    ax.annotate('',(-13,0),(-13,240),arrowprops={'arrowstyle':'<->'})
    ax.text(-20,120,'240 mm',rotation=90,ha='center',va='center')
    ax.set(xlim=(-29,239),ylim=(-20,271),aspect='equal');ax.axis('off')
    ax.set_title('BASE PLAN — schematic, mm',weight='bold')
    ax=axes[1]
    ax.add_patch(Rectangle((0,0),156,90,fc='#e4e9ed',ec='#294454',lw=2))
    ax.add_patch(Rectangle(c['window_mm'][:2],*c['window_mm'][2:],fc='#afc7ac',ec='#37664e'))
    for name,x,y,d in c['control_holes']:
        ax.add_patch(Circle((x,y),d/2,fc='white',ec='#294454'))
    for x,y in c.get('panel_pin_centres_mm',[[5.5,8],[149,8],[5.5,82],[149,82]]):
        ax.add_patch(Circle((x,y),1.7,fc='white',ec='#294454'))
    for text,x,y in [('LCD',48,66),('TONE',110,61),('BYPASS',135,59),('PTT',106,82),('BYP',132,82),('MIC',80,29),('RADIO',122,29)]:
        ax.text(x,y,text,ha='center',fontsize=8)
    ax.text(78,-12,'PTT test button removed; PTT status LED retained',ha='center',fontsize=10)
    ax.set(xlim=(-6,162),ylim=(-20,130),aspect='equal');ax.axis('off')
    ax.set_title('COMPACT PANEL — front, flattened',weight='bold')
    fig.savefig(IMG/'layout.png',dpi=160);plt.close(fig)

    fig,axes=plt.subplots(2,1,figsize=(11,8),layout='constrained')
    ax=axes[0]
    ax.add_patch(Rectangle((0,0),105,40,fc='#d5dde3',ec='#294454',lw=2))
    ax.add_patch(Rectangle((105,0),50,40,fc='#e8ecef',ec='#294454',hatch='///'))
    for y,z in c['radio_holes_local_yz_mm']:ax.add_patch(Circle((y,z),2.2,fc='white',ec='#294454',lw=1.5))
    for a,b,h,label in [(0,39,49,'39'),(39,88,49,'49'),(0,88,60,'88 = 39 + 49')]:
        ax.annotate('',(a,h),(b,h),arrowprops={'arrowstyle':'<->'})
        ax.text((a+b)/2,h+1,label,ha='center',fontsize=10)
    ax.annotate('',(96,0),(96,20),arrowprops={'arrowstyle':'<->'})
    ax.text(99,10,'20',va='center')
    ax.text(-3,20,'FACEPLATE\nFLAT',ha='right',va='center',fontsize=10)
    ax.text(130,20,'Rear /\nheat sink\nenvelope',ha='center',va='center')
    ax.text(0,-7,'User dimensions: 39 mm front datum, 49 mm pitch, 20 mm height. Both sides alike.',fontsize=10)
    ax.set(xlim=(-28,160),ylim=(-13,69),aspect='equal');ax.axis('off')
    ax.set_title('RADIO SIDE INTERFACE — schematic; all dimensions mm',weight='bold')
    ax=axes[1]
    ax.add_patch(Rectangle((0,0),240,3,fc='#859aaf',ec='#294454'))
    ax.add_patch(Rectangle((90,59.3),150,3,fc='#859aaf',ec='#294454'))
    ax.add_patch(Polygon([(0,32),(77.94,77),(76.44,79.6),(-1.5,34.6)],fc='#859aaf',ec='#294454'))
    a=math.radians(12)
    pts=[(84,100),(84+155*math.cos(a),100-155*math.sin(a)),
         (84+155*math.cos(a)+40*math.sin(a),100-155*math.sin(a)+40*math.cos(a)),
         (84+40*math.sin(a),100+40*math.cos(a))]
    ax.add_patch(Polygon(pts,fc='#d5dde3',ec='#294454',lw=2))
    ax.add_patch(Polygon([(84,62.3),(239,62.3),(239,67.05),(84,100)],fc='#9bb4c7',ec='#294454'))
    ax.text(166,108,'12° radio angle',ha='center',fontsize=12)
    ax.annotate('Two side saddles;\ncenter underside open',xy=(192,72),xytext=(259,82),arrowprops={'arrowstyle':'->'},fontsize=10)
    ax.text(50,16,'30° control panel',rotation=30,fontsize=11)
    ax.annotate('Vented cover / captured rails',xy=(200,61),xytext=(140,25),arrowprops={'arrowstyle':'->'},fontsize=10)
    ax.set(xlim=(-10,352),ylim=(-7,148),aspect='equal');ax.axis('off')
    ax.set_title('INSTALLED SIDE ENVELOPE — schematic, plugs and hardware omitted',weight='bold')
    fig.savefig(IMG/'radio-interface.png',dpi=160);plt.close(fig)

def layers():
    report=json.loads((EV/'slicer-checks.json').read_text())
    colors={'Outer wall':'#153b53','Inner wall':'#227ca0','Bottom surface':'#208f75',
        'Top surface':'#208f75','Internal solid infill':'#64acac','Sparse infill':'#b4c8c7',
        'Bridge':'#e27625','Overhang wall':'#ae4b9b','Brim':'#999999','Gap infill':'#e8a632'}
    records=[]
    target_sets={1:[.2,2,15,18.6],2:[.2,15,50.2,58.8],3:[.2,3.2,16.6,18.6],4:[.2,6.2,9,30]}
    with zipfile.ZipFile(ROOT/'manufacturing/enclosure-c1/ctcss-c1.3mf') as z:
        for i,requested in target_sets.items():
            lines=z.read(f'Metadata/plate_{i}.gcode').decode().splitlines()
            heights=sorted({float(s.split(':')[1]) for s in lines if s.startswith('; Z_HEIGHT:')})
            targets=[min(heights,key=lambda h:abs(h-t)) for t in requested]
            selected={h:[] for h in targets};pos={'X':0.,'Y':0.};height=None;feature=''
            relative_e=True;last_e=0.
            for line in lines:
                if line.startswith('; Z_HEIGHT:'):height=float(line.split(':')[1])
                if line.startswith('; FEATURE:'):feature=line.split(':',1)[1].strip()
                if line.startswith('M83'):relative_e=True
                if line.startswith('M82'):relative_e=False
                if line.startswith('G92 E'):last_e=float(line.split(';')[0].split('E')[1].split()[0])
                if not line.startswith(('G1 ','G2 ','G3 ')):continue
                v={k:float(n) for k,n in re.findall(r'([XYEIJ])(-?\d*\.?\d+)',line.split(';')[0])}
                old=(pos['X'],pos['Y']);pos.update({k:n for k,n in v.items() if k in pos});end=(pos['X'],pos['Y'])
                extruded=v.get('E',0) if relative_e else v.get('E',last_e)-last_e
                if 'E' in v:last_e=v['E']
                if height not in selected or extruded<=0 or feature not in colors:continue
                if line.startswith(('G2 ','G3 ')) and ('I' in v or 'J' in v):
                    cx=old[0]+v.get('I',0);cy=old[1]+v.get('J',0)
                    a=math.atan2(old[1]-cy,old[0]-cx);b=math.atan2(end[1]-cy,end[0]-cx)
                    span=(b-a)%(2*math.pi) if line.startswith('G3 ') else -((a-b)%(2*math.pi))
                    n=max(2,int(abs(span)/.08)+1);rad=math.hypot(old[0]-cx,old[1]-cy)
                    pts=[(cx+rad*math.cos(a+span*j/n),cy+rad*math.sin(a+span*j/n)) for j in range(n+1)]
                    selected[height].extend((pts[j],pts[j+1],colors[feature]) for j in range(n))
                else:selected[height].append((old,end,colors[feature]))
            fig,axes=plt.subplots(2,2,figsize=(10,10),layout='constrained')
            for ax,h in zip(axes.flat,targets):
                seg=selected[h];assert seg,(i,h)
                ax.add_collection(LineCollection([(a,b) for a,b,c in seg],colors=[c for a,b,c in seg],linewidths=.45))
                ax.set(xlim=(0,256),ylim=(0,256),aspect='equal',title=f'Z {h:.2f} mm',xlabel='X mm',ylabel='Y mm')
            fig.suptitle(f'C1 plate {i} — actual extrusion; bridges orange / overhangs magenta',fontsize=13)
            fig.savefig(EV/f'layers-{i}.png',dpi=170);plt.close(fig)
            records.append({'plate':i,'heights_mm':targets,'layer_count':len(heights)})
    (EV/'layer-checks.json').write_text(json.dumps({'revision':'C1','project_sha256':report['sha256'],'plates':records},indent=2)+'\n')

if __name__=='__main__':
    main()
    if (EV/'slicer-checks.json').exists():layers()

"""Draw the N1 mating stack and inspect actual embedded slicer toolpaths.

Ordinary Python, matplotlib. Dimensions from current CAD verification JSON;
layer paths from delivered Bambu Studio 3MF, not reconstructed CAD outlines.
"""
from pathlib import Path
import json,re,math,zipfile
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,Rectangle,RegularPolygon,Polygon
from matplotlib.collections import LineCollection

ROOT=Path(__file__).resolve().parents[1]
IMG=ROOT/'docs/images/ec11-flange-nut';IMG.mkdir(parents=True,exist_ok=True)
EV=ROOT/'docs/verification/ec11-flange-nut'
g=json.loads((EV/'cad-checks.json').read_text())

def stack():
    fig,(a,b)=plt.subplots(1,2,figsize=(13,6))
    for ax in [a,b]:ax.set_aspect('equal');ax.axis('off')
    a.add_patch(Circle((0,0),g['seat_diameter_mm']/2,fc='#eadcc7',ec='#83643e',lw=2))
    a.add_patch(Circle((0,0),g['flange_diameter_mm']/2,fc='#b9c7d1',ec='#33495b',lw=2))
    a.add_patch(RegularPolygon((0,0),6,radius=g['hex_across_flats_mm']/math.sqrt(3),orientation=math.pi/6,fc='#d4dce2',ec='#33495b',lw=2))
    a.add_patch(Circle((0,0),3.6,fc='white',ec='#33495b',ls='--'))
    a.annotate('20 mm recessed seat',xy=(0,10),xytext=(-11,13),arrowprops={'arrowstyle':'-'},fontsize=12)
    a.annotate('14 mm integrated washer',xy=(7,0),xytext=(-12,-13),arrowprops={'arrowstyle':'-'},fontsize=12)
    a.annotate('11 mm hex across flats',xy=(4,3),xytext=(0,11),arrowprops={'arrowstyle':'-'},fontsize=11)
    a.text(0,-17,'Face view: washer covers the 7.2 mm hole\n3.4 mm radial coverage; 3 mm seat clearance',ha='center',fontsize=11)
    a.set(xlim=(-16,16),ylim=(-20,18))
    # Section through center. Bushing is a schematic envelope; no claim about
    # this generic encoder's measured threaded length is made.
    for x in [-10,3.6]:b.add_patch(Rectangle((x,-1.5),6.4,1.5,fc='#eadcc7',ec='#83643e',hatch='//'))
    for x in [-7,3.5]:
        b.add_patch(Rectangle((x,0),3.5,.72,fc='#b9c7d1',ec='#33495b'))
    for x in [-5.5,3.5]:b.add_patch(Rectangle((x,.72),2,2.28,fc='#d4dce2',ec='#33495b'))
    b.add_patch(Rectangle((-3.5,-2.3),7,5.6,fc='#c1c1b6',ec='#66665f'))
    for z in [i*.75 for i in range(5)]:b.plot([-3.5,3.5],[z,z],color='#77776c',lw=.7)
    b.annotate('Nut height 3.0 mm',xy=(5.5,2),xytext=(-11,8),arrowprops={'arrowstyle':'-'},fontsize=12)
    b.annotate('Washer 0.72 mm',xy=(-6,.4),xytext=(-13,5.5),arrowprops={'arrowstyle':'-'},fontsize=12)
    b.annotate('Panel land 1.5 mm',xy=(-8,-.8),xytext=(-13,-4.5),arrowprops={'arrowstyle':'-'},fontsize=12)
    b.text(0,-8,'Encoder body below panel; shaft/knob above.\nFlat washer face bears on the recessed land.\nBushing shown schematically; check ≥3 mm\nthread exposed above the panel before tightening.',ha='center',va='top',fontsize=11)
    b.set(xlim=(-16,16),ylim=(-18,14))
    fig.suptitle('N1 flanged encoder nut on the current B1 control panel',fontsize=18,weight='bold')
    fig.text(.5,.02,'Dimensions in mm from current native CAD. Section is schematic; no separate washer is fitted.',ha='center',fontsize=11)
    fig.savefig(IMG/'seat-stack.png',dpi=160);plt.close(fig)

def parse(code):
    paths=defaultdict(list);x=y=0.;z=None;feature=''
    for line in code.splitlines():
        if line.startswith('; Z_HEIGHT:'):z=round(float(line.split(':')[1]),4)
        if line.startswith('; FEATURE:'):feature=line.split(':',1)[1].strip()
        if not line.startswith(('G1 ','G2 ','G3 ')):continue
        v={k:float(n) for k,n in re.findall(r'([XYEIJ])(-?\d*\.?\d+)',line.split(';')[0])}
        prev=(x,y);x=v.get('X',x);y=v.get('Y',y)
        if z is None or v.get('E',0)<=0 or (x,y)==prev:continue
        points=[prev,(x,y)]
        if line.startswith(('G2 ','G3 ')) and ('I' in v or 'J' in v):
            cx=prev[0]+v.get('I',0);cy=prev[1]+v.get('J',0)
            aa=math.atan2(prev[1]-cy,prev[0]-cx);bb=math.atan2(y-cy,x-cx)
            span=(bb-aa)%(2*math.pi) if line.startswith('G3 ') else -((aa-bb)%(2*math.pi))
            rr=math.hypot(prev[0]-cx,prev[1]-cy);n=max(2,math.ceil(abs(span)/.05))
            points=[(cx+rr*math.cos(aa+span*i/n),cy+rr*math.sin(aa+span*i/n)) for i in range(n+1)]
        paths[z].extend((p,q,feature) for p,q in zip(points,points[1:]))
    return paths

def layers():
    colors={'Outer wall':'#2d6585','Inner wall':'#d38b2f','Top surface':'#4a9966',
            'Bottom surface':'#4a9966','Internal solid infill':'#759f6b','Sparse infill':'#b35a82','Brim':'#a5adb3'}
    checks=[]
    with zipfile.ZipFile(ROOT/'manufacturing/ec11-flange-nut/ec11-flange-nut-n1.3mf') as archive:
        for i in [1,2]:
            code=archive.read(f'Metadata/plate_{i}.gcode').decode();p=parse(code)
            fig,axs=plt.subplots(2,2,figsize=(12,9))
            targets=[.12,.72,1.2,1.56]
            for ax,t in zip(axs.flat,targets):
                z=min(p,key=lambda q:abs(q-t));segments=p[z]
                for feature in set(e[2] for e in segments):
                    ss=[(a,b) for a,b,f in segments if f==feature]
                    ax.add_collection(LineCollection(ss,colors=colors.get(feature,'#777777'),linewidths=.7))
                ax.set(xlim=(32,113),ylim=(42,64),aspect='equal',title=f'Actual extrusion paths at Z{z:.2f} mm')
                ax.set_xlabel('Plate X / mm');ax.set_ylabel('Plate Y / mm')
                ax.grid(alpha=.2)
            checks.append({'plate':i,'layer_count':len(p),'z_min':min(p),'z_max':max(p),
                'estimated_time':re.search(r'; model printing time: (.*)',code).group(1),
                'filament_g':float(re.search(r'; total filament weight \[g\] : ([\d.]+)',code).group(1))})
            assert all(any(abs(z-t)<.002 for z in p) for t in [1.2,1.56])
            # Each bore retains a closed-looking outer-wall path with a varying
            # radius, resolving the helical thread rather than a plain round hole.
            for cx in [42,72,102]:
                rr=[math.hypot(a[0]-cx,a[1]-52) for a,b,f in p[1.2]
                    if f=='Outer wall' and 2.5<math.hypot(a[0]-cx,a[1]-52)<4.5]
                assert len(rr)>20 and max(rr)-min(rr)>.1,(i,cx,rr)
            fig.suptitle('N1 plate '+str(i)+' — '+('independent thread-fit coupons' if i==1 else 'three alternative flanged nuts'),fontsize=17,weight='bold')
            fig.text(.5,.02,'Blue: outer walls, including threaded bores. Orange: inner walls. Green: solid skins. Gray: brim.',ha='center',fontsize=10)
            fig.tight_layout(rect=[0,.05,1,.94]);fig.savefig(EV/f'toolpaths-plate-{i}.png',dpi=150);plt.close(fig)
    (EV/'layer-checks.json').write_text(json.dumps({'plates':checks,'three_threaded_bores_present_per_plate':True},indent=2)+'\n')
    print(json.dumps(checks,indent=2))

if __name__=='__main__':stack();layers()

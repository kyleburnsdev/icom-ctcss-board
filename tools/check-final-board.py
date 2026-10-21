"""Read-only independent KiCad-native inventory and conservative body-spacing check.

Run with KiCad's bundled python.exe; never calls SaveBoard or mutates objects.
"""
import collections
import json
import math
from pathlib import Path
import pcbnew

board=pcbnew.LoadBoard('electronics/icom-ctcss-board.kicad_pcb')
mm=lambda v:v/1e6
tracks=list(board.GetTracks())
layer_counts=collections.Counter(board.GetLayerName(t.GetLayer()) for t in tracks)
vias=sum(isinstance(t,pcbnew.PCB_VIA) for t in tracks)
assert vias==0 and set(layer_counts)=={'B.Cu'}
assert not list(board.Zones())
assert min(mm(t.GetWidth()) for t in tracks)>=.5-1e-6
footprints=list(board.GetFootprints())
pads=[p for f in footprints for p in f.Pads() if f.GetReference()[0]!='H']
assert len(pads)==111
assert 'R16' not in {f.GetReference() for f in footprints}
assert len([f for f in footprints if not f.GetReference().startswith('H')])==38
assert not any('OFFSET' in t.GetNetname() for t in tracks)
assert not any('OFF' in t.GetText() or 'R16' in t.GetText() for t in board.GetDrawings() if isinstance(t,pcbnew.PCB_TEXT))
assert all(p.GetAttribute()==pcbnew.PAD_ATTRIB_PTH for p in pads)
holes=[]
body=[]
positions=[]
lengths=collections.defaultdict(float)
for t in tracks:lengths[t.GetNetname()]+=mm(t.GetLength())
for f in footprints:
    ref=f.GetReference()
    x,y=mm(f.GetPosition().x),mm(f.GetPosition().y)
    rotation=f.GetOrientationDegrees()
    positions.append({'reference':ref,'x':x,'y':y,'rotation':rotation,'footprint':str(f.GetFPID().GetLibItemName())})
    if ref.startswith('H'):
        p=list(f.Pads())[0]
        assert p.GetAttribute()==pcbnew.PAD_ATTRIB_NPTH and abs(mm(p.GetDrillSize().x)-4)<1e-6
        holes.append({'reference':ref,'x':x,'y':y,'diameter':4})
        continue
    if ref.startswith('R') and not ref.startswith('RV'):
        rect=(.74,-.8,4.34,.8)
    elif ref in ('C1','C2','C4','C5'):
        rect=(-.25,-1,2.75,1)
    elif ref=='C3':rect=(-1.1,-2.5,6.1,2.5)
    elif ref=='C6':rect=(-1.1,-5.5,6.1,5.5)
    elif ref=='Q1':rect=(-.06,-2.48,5.14,1.75)
    elif ref=='RV1':rect=(-7.305,-2.41,2.225,2.42)
    elif ref=='U1':rect=(-21.76,-9.12,15.24,9.12)
    elif ref.startswith('J'):
        n=len(list(f.Pads()))
        rect=(-1.27,-1.27,1.27,(n-1)*2.54+1.27)
    else:rect=(-1.5,-1.5,1.5,1.5)
    rad=math.radians(rotation)
    def transform(a,b):return x+a*math.cos(rad)+b*math.sin(rad),y-a*math.sin(rad)+b*math.cos(rad)
    corners=[transform(a,b) for a in (rect[0],rect[2]) for b in (rect[1],rect[3])]
    bounds=(min(a for a,b in corners),min(b for a,b in corners),max(a for a,b in corners),max(b for a,b in corners))
    assert bounds[0]>=50 and bounds[1]>=50 and bounds[2]<=150 and bounds[3]<=200
    body.append({'reference':ref,'bounds':bounds})
gaps=[]
for i,a in enumerate(body):
    for b in body[:i]:
        p,q=a['bounds'],b['bounds']
        dx=max(0,p[0]-q[2],q[0]-p[2]);dy=max(0,p[1]-q[3],q[1]-p[3])
        gaps.append({'references':[a['reference'],b['reference']],'gap_mm':round(math.hypot(dx,dy),4)})
gaps.sort(key=lambda a:a['gap_mm'])
result={'source':'read-only KiCad pcbnew.LoadBoard after Konnect save','track_count':len(tracks),'track_layers':dict(layer_counts),'widths_mm':sorted({mm(t.GetWidth()) for t in tracks}),'via_count':vias,'zone_count':0,'circuit_parts':38,'mounting_holes':holes,'electrical_pads':len(pads),'native_top_pad_count':sum(p.IsOnLayer(pcbnew.F_Cu) for p in pads),'native_bottom_pad_count':sum(p.IsOnLayer(pcbnew.B_Cu) for p in pads),'track_lengths_mm':dict(lengths),'component_positions':positions,'body_envelopes':body,'closest_body_gaps':gaps[:12],'body_gaps_below_2mm':[a for a in gaps if a['gap_mm']<1.999],'body_assumptions':'Nominal selected bodies; 37x18.24 module/socket envelope including 3mm-wide socket strips. Actual socket and USB cable fit still require dry fit.'}
Path('docs/verification/final-board-inventory.json').write_text(json.dumps(result,indent=2))
print(json.dumps({k:v for k,v in result.items() if k not in ('component_positions','body_envelopes','track_lengths_mm')},indent=2))

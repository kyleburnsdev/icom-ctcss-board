"""Read-only independent KiCad-native inventory and conservative body-spacing check.

Run with KiCad's bundled python.exe; never calls SaveBoard or mutates objects.
"""
import collections
import json
import math
import hashlib
from pathlib import Path
import pcbnew

board=pcbnew.LoadBoard('electronics/icom-ctcss-board.kicad_pcb')
mm=lambda v:v/1e6
tracks=list(board.GetTracks())
layer_counts=collections.Counter(board.GetLayerName(t.GetLayer()) for t in tracks)
vias=sum(isinstance(t,pcbnew.PCB_VIA) for t in tracks)
assert vias==0 and set(layer_counts)=={'B.Cu'}
zones=list(board.Zones())+[z for fp in board.GetFootprints() for z in fp.Zones()]
assert all(z.GetIsRuleArea() for z in zones), 'Copper pours are prohibited'
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
        expected = {'H1':(56,56,4), 'H2':(144,56,4), 'H3':(144,194,4), 'H4':(56,194,4),
                    'H5':(70,70,4.03), 'H6':(70,180,4.03), 'H7':(120,70,4.12), 'H8':(120,180,4.12)}
        ex,ey,diameter=expected[ref]
        assert p.GetAttribute()==pcbnew.PAD_ATTRIB_NPTH and abs(mm(p.GetDrillSize().x)-diameter)<1e-6
        assert abs(x-ex)<1e-6 and abs(y-ey)<1e-6
        holes.append({'reference':ref,'x':x,'y':y,'diameter':diameter,
                      'purpose':'enclosure_mount' if ref in ('H1','H2','H3','H4') else 'jig_registration'})
        continue
    if ref.startswith('R') and not ref.startswith('RV'):
        rect=(.74,-.8,4.34,.8)
    elif ref in ('C1','C2','C4','C5'):
        rect=(-.75,-1.3,3.25,1.3)  # Vishay K104K15X7RF5TL2 maximum body
    elif ref=='C3':rect=(-1.25,-2.55,6.25,2.55)  # KEMET R82DC4100AA60J maxima
    elif ref=='C6':rect=(-1.5,-3.5,16.5,3.5)  # TDK B32522C0475J000, 15mm pitch
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
assert {h['reference'] for h in holes} == {'H1','H2','H3','H4','H5','H6','H7','H8'}
jig_clearances=[]
for h in holes:
    if h['purpose']!='jig_registration': continue
    body_gaps=[]
    for item in body:
        l,t,r,b=item['bounds']
        gap=math.hypot(max(l-h['x'],0,h['x']-r),max(t-h['y'],0,h['y']-b))-h['diameter']/2
        body_gaps.append((gap,item['reference']))
    nearest,reference=min(body_gaps)
    assert nearest>=1
    track_gaps=[]
    for track in tracks:
        ax,ay=mm(track.GetStart().x),mm(track.GetStart().y)
        bx,by=mm(track.GetEnd().x),mm(track.GetEnd().y)
        dx,dy=bx-ax,by-ay
        fraction=max(0,min(1,((h['x']-ax)*dx+(h['y']-ay)*dy)/(dx*dx+dy*dy))) if dx*dx+dy*dy else 0
        track_gaps.append(math.hypot(h['x']-ax-fraction*dx,h['y']-ay-fraction*dy)-mm(track.GetWidth())/2-h['diameter']/2)
    pad_gaps=[]
    for pad in pads:
        bb=pad.GetBoundingBox()
        pad_gaps.append(math.hypot(max(mm(bb.GetLeft())-h['x'],0,h['x']-mm(bb.GetRight())),max(mm(bb.GetTop())-h['y'],0,h['y']-mm(bb.GetBottom())))-h['diameter']/2)
    assert min(track_gaps)>=1 and min(pad_gaps)>=1
    jig_clearances.append({'reference':h['reference'],'nearest_body':reference,'hole_edge_to_body_mm':round(nearest,4),
                           'hole_edge_to_track_copper_mm':round(min(track_gaps),4),'hole_edge_to_pad_box_mm':round(min(pad_gaps),4)})
result={'source':'read-only native KiCad pcbnew.LoadBoard on saved PCB','track_count':len(tracks),'track_layers':dict(layer_counts),'widths_mm':sorted({mm(t.GetWidth()) for t in tracks}),'via_count':vias,'zone_count':0,'circuit_parts':38,'mounting_holes':holes,'electrical_pads':len(pads),'native_top_pad_count':sum(p.IsOnLayer(pcbnew.F_Cu) for p in pads),'native_bottom_pad_count':sum(p.IsOnLayer(pcbnew.B_Cu) for p in pads),'track_lengths_mm':dict(lengths),'component_positions':positions,'body_envelopes':body,'closest_body_gaps':gaps[:12],'body_gaps_below_2mm':[a for a in gaps if a['gap_mm']<1.999],'body_assumptions':'Selected maximum capacitor bodies and nominal other bodies; 37x18.24 module/socket envelope including 3mm-wide socket strips. Actual socket and USB cable fit still require dry fit.'}
result['board_sha256']=hashlib.sha256(Path('electronics/icom-ctcss-board.kicad_pcb').read_bytes()).hexdigest()
result['saved_board_thickness_mm']=mm(board.GetDesignSettings().GetBoardThickness())
result['required_stock_thickness_mm']=1.5
result['board_thickness_matches_stock']=abs(result['saved_board_thickness_mm']-1.5)<1e-6
result['jig_body_clearances']=jig_clearances
assert result['board_thickness_matches_stock']
assert len(zones)==4
keepouts=[]
for ref in ('H5','H6','H7','H8'):
    fp=next(f for f in footprints if f.GetReference()==ref)
    areas=list(fp.Zones())
    assert len(areas)==1
    z=areas[0]
    assert z.GetIsRuleArea() and set(z.GetLayerSet().Seq())=={pcbnew.F_Cu,pcbnew.B_Cu}
    flags={kind:getattr(z,'GetDoNotAllow'+kind)() for kind in ['Tracks','Vias','Pads','ZoneFills','Footprints']}
    assert all(flags.values())
    centre=fp.GetPosition()
    points=[z.GetCornerPosition(i) for i in range(z.Outline().TotalVertices())]
    edge_distances=[]
    for a,b in zip(points,points[1:]+points[:1]):
        dx,dy=b.x-a.x,b.y-a.y
        fraction=max(0,min(1,((centre.x-a.x)*dx+(centre.y-a.y)*dy)/(dx*dx+dy*dy)))
        edge_distances.append(math.hypot(centre.x-a.x-fraction*dx,centre.y-a.y-fraction*dy))
    radius=mm(min(edge_distances))
    assert radius>=mm(list(fp.Pads())[0].GetDrillSize().x)/2+1
    keepouts.append({'reference':ref,'owner':'footprint','layers':['F.Cu','B.Cu'],
                     'minimum_inscribed_radius_mm':radius,'flags':flags})
result['jig_keepout_status']='PASS: four footprint-owned all-copper rule areas, all five exclusion flags verified'
result['jig_keepouts']=keepouts
result['rule_area_count']=len(zones)
Path('docs/verification/final-board-inventory.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('component_positions','body_envelopes','track_lengths_mm')},indent=2))

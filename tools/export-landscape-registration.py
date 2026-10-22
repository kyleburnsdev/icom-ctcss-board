"""Transform exported manufacturing geometry only; never read/write KiCad sources.

Requires gerbonara. Run from repository root. CNC coordinates are lower-left XY.
Native Gerber -> landscape top: X=-nativeY-50, Y=nativeX-50.
Landscape bottom after the specified Y-axis flip: X=150-topX, Y=topY.
"""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from gerbonara import GerberFile, ExcellonFile

PACKAGE=Path('manufacturing/pcb/carvera-air')
ROOT=PACKAGE/'native-exports'
OUT=PACKAGE/'landscape-y-flip'
OUT.mkdir(exist_ok=True)
NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)

def point(x,y,bottom=False):
    u,v=-y-50,x-50
    return (150-u if bottom else u),v

def transform(file,bottom=False):
    for o in file.objects:
        assert type(o).__name__ in ('Line','Arc','Flash'),type(o).__name__
        a=o.aperture
        # These exports use circular strokes/holes and square lands only.
        if hasattr(a,'w'):assert abs(a.w-a.h)<1e-9
        if hasattr(o,'x'):
            o.x,o.y=point(o.x,o.y,bottom)
        else:
            o.x1,o.y1=point(o.x1,o.y1,bottom)
            o.x2,o.y2=point(o.x2,o.y2,bottom)
            if hasattr(o,'cx'):
                dx,dy=-o.cy,o.cx
                o.cx,o.cy=(-dx if bottom else dx),dy
                if bottom:o.clockwise=not o.clockwise
    if hasattr(file,'file_attrs'):
        file.file_attrs.pop('.SameCoordinates',None)
        file.file_attrs.pop('.CreationDate',None)
    return file

def svg(file,path,registered=False,bottom=False):
    root=ET.fromstring(str(file.to_svg(force_bounds=((0,0),(150,100)),bg='none')))
    art=ET.Element(f'{{{NS}}}g',{'id':'PROCESS_ARTWORK'})
    for child in list(root):root.remove(child);art.append(child)
    root.append(art)
    if registered:
        guides=ET.SubElement(root,f'{{{NS}}}g',{'id':'REGISTRATION_GUIDES_DO_NOT_MACHINE','stroke':'#0066cc','fill':'none','stroke-width':'0.15'})
        for ref,x,y in [('H1',6,6),('H2',6,94),('H3',144,94),('H4',144,6)]:
            x=150-x if bottom else x
            sy=100-y
            ET.SubElement(guides,f'{{{NS}}}circle',{'cx':str(x),'cy':str(sy),'r':'2','data-reference':ref})
            ET.SubElement(guides,f'{{{NS}}}path',{'d':f'M{x-1.5},{sy} H{x+1.5} M{x},{sy-1.5} V{sy+1.5}'})
        ET.SubElement(guides,f'{{{NS}}}rect',{'x':'0.1','y':'0.1','width':'149.8','height':'99.8','stroke-dasharray':'1 1'})
    ET.indent(root)
    ET.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)

jobs=[('icom-ctcss-board-F_Silkscreen.gto','top-legend.gto',False),
      ('icom-ctcss-board-B_Cu.gbl','bottom-copper-Y-FLIPPED.gbl',True),
      ('icom-ctcss-board-Edge_Cuts.gm1','board-outline.gm1',False)]
for src,dst,bottom in jobs:
    g=transform(GerberFile.open(ROOT/src),bottom)
    g.save(OUT/dst)
    # Gerbonara emits a bare G75 line; terminate it explicitly for CAM readers.
    plotted=(OUT/dst).read_text().replace('G75\n','G75*\n')
    (OUT/dst).write_text(plotted,encoding='utf-8',newline='\n')
    # Reopen serialized artifact before deriving its actual preview.
    g=GerberFile.open(OUT/dst)
    if 'legend' in dst:
        svg(g,OUT/'top-legend.svg')
        svg(g,OUT/'top-legend-REGISTERED.svg',True,False)
    elif 'copper' in dst:
        svg(g,OUT/'bottom-copper-Y-FLIPPED-REGISTERED.svg',True,True)

for src,dst,bottom,count in [('icom-ctcss-board-NPTH.drl','registration-holes.drl',False,4),
                             ('icom-ctcss-board-PTH.drl','bottom-electrical-holes-Y-FLIPPED.drl',True,111)]:
    e=transform(ExcellonFile.open(ROOT/src),bottom)
    assert len(e.objects)==count
    e.save(OUT/dst)
    e2=ExcellonFile.open(OUT/dst)
    assert len(e2.objects)==count
    original=ExcellonFile.open(ROOT/src)
    for a,b in zip(original.objects,e2.objects):
        u,v=point(a.x,a.y,bottom)
        assert abs(u-b.x)<2e-6 and abs(v-b.y)<2e-6
    if count==4:
        actual={(round(o.x,6),round(o.y,6)) for o in e2.objects}
        assert actual=={(6,6),(144,6),(6,94),(144,94)},actual
        assert all(abs(o.aperture.diameter-4)<1e-6 for o in e2.objects)
    assert all(0<o.x<150 and 0<o.y<100 for o in e2.objects)

# Check the full asymmetric copper inventory against the coordinate equations.
native=GerberFile.open(ROOT/'icom-ctcss-board-B_Cu.gbl')
bottom=GerberFile.open(OUT/'bottom-copper-Y-FLIPPED.gbl')
inventory=json.loads(Path('docs/verification/final-board-inventory.json').read_text())
expected_copper_objects=inventory['track_count']+inventory['electrical_pads']
assert len(native.objects)==len(bottom.objects)==expected_copper_objects
for a,b in zip(native.objects,bottom.objects):
    for x,y,xx,yy in ([(a.x,a.y,b.x,b.y)] if hasattr(a,'x') else [(a.x1,a.y1,b.x1,b.y1),(a.x2,a.y2,b.x2,b.y2)]):
        u,v=point(x,y,True)
        assert abs(u-xx)<2e-6 and abs(v-yy)<2e-6
index=next(i for i,o in enumerate(native.objects) if o.attrs.get('.P')==('J1','1'))
pad=bottom.objects[index]
assert (pad.x,pad.y)==(20,40)
original_legend=GerberFile.open(ROOT/'icom-ctcss-board-F_Silkscreen.gto')
landscape_legend=GerberFile.open(OUT/'top-legend.gto')
assert len(original_legend.objects)==len(landscape_legend.objects)>0
for a,b in zip(original_legend.objects,landscape_legend.objects):
    for x,y,xx,yy in [(a.x1,a.y1,b.x1,b.y1),(a.x2,a.y2,b.x2,b.y2)]:
        u,v=point(x,y)
        assert abs(u-xx)<2e-6 and abs(v-yy)<2e-6
    if hasattr(a,'cx'):
        assert abs(-a.cy-b.cx)<2e-6 and abs(a.cx-b.cy)<2e-6
manifest={'frame_mm':[150,100],'origin':'lower-left in CNC XY',
 'top_transform':'X=-GerberY-50; Y=GerberX-50',
 'bottom_transform':'X=150-topX; Y=topY; ALREADY APPLIED',
 'hole_centers_mm':[[6,6],[144,6],[6,94],[144,94]],
 'hole_pitch_mm':[138,88],'hole_diameter_mm':4,
 'asymmetric_check':{'feature':'J1 pin 1','top_xy_mm':[130,40],'bottom_xy_mm':[20,40]},
 'checks':{'electrical_holes':111,'mounting_holes':4,'copper_objects':expected_copper_objects,'legend_objects':len(landscape_legend.objects),'all_copper_coordinates_verified':True,'all_legend_coordinates_verified':True},
 'cam_project_status':'Existing .mkc projects are user work and are not regenerated or validated by this geometry exporter; reimport revised copper, drill and legend files.',
 'files':{p.name:{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted(OUT.iterdir()) if p.is_file() and p.suffix in ('.gbl','.gto','.gm1','.drl','.svg')}}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in manifest.items() if k!='files'},indent=2))

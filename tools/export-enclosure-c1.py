"""Run main() through Robust MCP after the C1 builder; exports exact saved C1.

Native STEP retains assembly positions. Mesh copies have explicit print transforms.
Does not open or save any other document. Results record actual unsaved edits by
saving this agent-created C1 document before export, never loading a stale copy.
"""
from pathlib import Path
import hashlib
import json
import math
import FreeCAD as App
import Part
import MeshPart

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'manufacturing/enclosure-c1'
EV=ROOT/'docs/verification/enclosure-c1'
CAD=ROOT/'mechanical/enclosure/c1/ctcss-c1.FCStd'

def main():
    d=next(d for d in App.listDocuments().values() if d.FileName and Path(d.FileName).resolve()==CAD.resolve())
    d.recompute()
    (OUT/'supporting/stl').mkdir(parents=True,exist_ok=True)
    (OUT/'supporting/step').mkdir(parents=True,exist_ok=True)
    groups=[d.getObject(n) for n in ['EnclosureParts','IndependentFitCoupons']]
    bodies=[o for g in groups for o in g.Group if o.TypeId=='PartDesign::Body']
    data=json.loads((EV/'cad-checks.json').read_text())
    data['panel_pin_centres_mm']=[[g.Center.x,g.Center.y] for g in d.getObject('PanelScrewClearanceSketch').Geometry]
    checks={'revision':'C1','parts':[],'intersections_mm3':{},'slide_sweep_mm3':[]}
    # Check all printed instances, not only unique exported bodies.
    instances=list(groups[0].Group)
    for i,a in enumerate(instances):
        for b in instances[i+1:]:
            if a.Shape.BoundBox.intersect(b.Shape.BoundBox):
                v=a.Shape.common(b.Shape).Volume
                checks['intersections_mm3'][a.Name+'/'+b.Name]=v
                assert v<1e-5,(a.Name,b.Name,v)
    # Check actual PCB/display/control references against the saved solids.
    for key in data['intersections_mm3']:
        a,b=key.split('/')
        v=d.getObject(a).Shape.common(d.getObject(b).Shape).Volume
        checks['intersections_mm3'][key]=v
        assert v<1e-5,(key,v)
    for dy in [0,10,50,100,150,165]:
        sh=d.getObject('SlidingCover').Shape.copy();sh.translate(App.Vector(0,dy,0))
        v=sh.common(d.getObject('Base').Shape).Volume
        checks['slide_sweep_mm3'].append({'rearward_translation_mm':dy,'base_collision_mm3':v})
        assert v<1e-5,(dy,v)
    for o in bodies:
        assert o.Shape.isValid() and len(o.Shape.Solids)==1,o.Name
        sh=o.Shape.copy();sh.Placement=o.Placement.inverse().multiply(sh.Placement)
        rotation=App.Rotation()
        if o.Name in ['ControlPanel','PcbCornerStrap','DisplayFitCoupon','SlidingCover','CoverTongueCoupon']:
            rotation=App.Rotation(App.Vector(1,0,0),180)
        elif o.Name=='LeftRadioSaddle':rotation=App.Rotation(App.Vector(0,1,0),90)
        elif o.Name=='RightRadioSaddle':rotation=App.Rotation(App.Vector(0,1,0),-90)
        elif 'RadioCheek' in o.Name:rotation=App.Rotation(App.Vector(0,1,0),90)
        sh.Placement=App.Placement(App.Vector(),rotation).multiply(sh.Placement)
        bb=sh.BoundBox;shift=App.Vector(-bb.XMin,-bb.YMin,-bb.ZMin);sh.translate(shift)
        mesh=MeshPart.meshFromShape(Shape=sh,LinearDeflection=.025,AngularDeflection=.10,Relative=False)
        bb=mesh.BoundBox
        assert mesh.isSolid() and abs(bb.ZMin)<1e-5 and max(bb.XLength,bb.YLength,bb.ZLength)<246.01,o.Name
        path=OUT/'supporting/stl'/(o.Name.lower()+'.stl');mesh.write(str(path))
        checks['parts'].append({'name':o.Name,'bounds_mm':[bb.XLength,bb.YLength,bb.ZLength],
            'closed':mesh.isSolid(),'facets':mesh.CountFacets,'rotation_quaternion':rotation.Q,
            'print_shift_mm':[shift.x,shift.y,shift.z],'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    step=OUT/'supporting/step/ctcss-c1-assembly.step'
    # Part.export skips App Links in this build. Flatten native shape copies only
    # for exchange; the editable source retains its Bodies and App Links.
    exchange=App.newDocument('C1StepSnapshot')
    snapshots=[]
    for o in instances:
        f=exchange.addObject('Part::Feature',o.Name);f.Label=o.Label;f.Shape=o.Shape.copy();snapshots.append(f)
    Part.export(snapshots,str(step));App.closeDocument(exchange.Name)
    reread=Part.read(str(step))
    assert reread.isValid() and len(reread.Solids)==len(instances)
    assert abs(reread.Volume-sum(o.Shape.Volume for o in instances))<.01
    checks['step_solid_count']=len(reread.Solids)
    saved_volumes={o.Name:o.Shape.Volume for o in bodies+instances}
    d.saveAs(str(CAD))
    # Native saved readback in a separate document without touching the live C1.
    copy=ROOT/'.agent-scratch/enclosure-c1/reopen-check.FCStd'
    copy.parent.mkdir(parents=True,exist_ok=True)
    copy.write_bytes(CAD.read_bytes());readback=App.openDocument(str(copy));readback.recompute()
    for name,v in saved_volumes.items():
        o=readback.getObject(name)
        assert o.Shape.isValid() and len(o.Shape.Solids)==1
        assert abs(o.Shape.Volume-v)<1e-5,(name,'saved readback')
    checks['native_reopen']=True;App.closeDocument(readback.Name);App.setActiveDocument(d.Name)
    checks['native_source_sha256']=hashlib.sha256(CAD.read_bytes()).hexdigest()
    checks['step_sha256']=hashlib.sha256(step.read_bytes()).hexdigest()
    checks['physical_acceptance']='not run'
    data['source_sha256']=checks['native_source_sha256'];data['intersections_mm3']=checks['intersections_mm3']
    data['generator_sha256']=hashlib.sha256((ROOT/'tools/build-enclosure-c1.py').read_bytes()).hexdigest()
    (EV/'cad-checks.json').write_text(json.dumps(data,indent=2)+'\n')
    (EV/'export-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    return checks

if __name__=='__main__':main()

"""Review B1 through the running FreeCAD Robust MCP XML-RPC bridge.

Run with ordinary Python after the CAD build. FreeCAD must have no documents
open; the helper refuses to replace live work. Saves the assembly display,
checks interference, and renders the native view into the illustrated guide.
"""
import xmlrpc.client
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
server=xmlrpc.client.ServerProxy('http://localhost:9875')
code=r'''
import FreeCAD as App, FreeCADGui as Gui
from pathlib import Path
import json,hashlib
root=Path(__ROOT__)
path=root/'mechanical/bench-holder/bench-holder-b1.FCStd'
assert not App.listDocuments(), 'Do not replace live documents'
d=App.openDocument(str(path))
for o in d.Objects:
    if o.ViewObject: o.Visibility=False
production=d.getObject('ProductionParts');production.Visibility=True
refs=d.getObject('ReferenceEnvelopes');refs.Visibility=True
for name,color in [('Base',(0.30,0.38,0.45)),('ControlPanel',(0.76,0.61,0.40)),('LedKeeper',(0.76,0.61,0.40))]:
    b=d.getObject(name);b.Visibility=True
    for child in b.Group:
        if child.ViewObject:child.Visibility=False
    b.Tip.Visibility=True
    b.ViewObject.ShapeColor=color;b.Tip.ViewObject.ShapeColor=color
    b.ViewObject.LineColor=(0.15,0.15,0.15);b.Tip.ViewObject.LineColor=(0.15,0.15,0.15)
for child in refs.Group:child.Visibility=False
pcb=d.getObject('PcbReference');pcb.Visibility=True;pcb.ViewObject.ShapeColor=(0.20,0.55,0.30)
d.getObject('LcdBodyReference').Visibility=True
d.getObject('MicAdapterRearEnvelope').Visibility=True
d.getObject('RadioAdapterRearEnvelope').Visibility=True
d.getObject('FitCoupons').Visibility=False
d.getObject('PcbSpacer').Visibility=False
Gui.activeDocument().activeView().viewAxonometric();Gui.activeDocument().activeView().fitAll()
d.recompute();d.save()
Gui.activeDocument().activeView().saveImage(str(root/'docs/images/bench-holder/native-assembly.png'),1600,1100,'White')
g=json.loads((root/'docs/verification/bench-holder/geometry.json').read_text())
g['source_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
g['gui_native_review']=True
g['native_presenter']='Robust MCP XML-RPC bridge; native API visibility and saved view'
g['production_intersections_mm3']={}
for a,b in [('Base','ControlPanel'),('Base','PcbReference'),('ControlPanel','LedKeeper')]:
    g['production_intersections_mm3'][a+' / '+b]=d.getObject(a).Shape.common(d.getObject(b).Shape).Volume
assert g['production_intersections_mm3']['Base / ControlPanel']<1e-6
assert g['production_intersections_mm3']['Base / PcbReference']<1e-6
import Part
g['pcb_screw_path_checks']=[]
for x,y in g['board_holes_mm']:
    shape=d.getObject('Base').Shape
    lower=shape.common(Part.makeCylinder(1.65,8.8,App.Vector(x,y,.1))).Volume
    core=shape.common(Part.makeCylinder(1.2,15.2,App.Vector(x,y,-.1))).Volume
    ring=Part.makeCylinder(1.7,5.6,App.Vector(x,y,9.2)).cut(Part.makeCylinder(1.32,5.6,App.Vector(x,y,9.2)))
    thread_material=shape.common(ring).Volume
    assert lower<1e-6 and core<1e-6 and thread_material>0
    g['pcb_screw_path_checks'].append({'center_mm':[x,y],'lower_clearance_obstruction_mm3':lower,
        'through_core_obstruction_mm3':core,'upper_thread_material_mm3':thread_material})
(root/'docs/verification/bench-holder/geometry.json').write_text(json.dumps(g,indent=2))
print(g['production_intersections_mm3'])
'''
result=server.execute(code.replace('__ROOT__',repr(str(ROOT))))
print(result)
assert result['success'],result

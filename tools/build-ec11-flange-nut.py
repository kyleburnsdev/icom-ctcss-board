"""Build editable EC11 M7x0.75 flanged nuts and independent thread coupons.

Run main() through the running FreeCAD Robust MCP execute_python bridge.
FreeCAD 1.1+, no extra workbench; export sources/STEP/STL through native APIs.
The generator owns the dimensions below. Existing bench-holder CAD is read only.
"""
from pathlib import Path
import json,math,hashlib
import FreeCAD as App
import Part,Sketcher,MeshPart

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'manufacturing/ec11-flange-nut'
EV=ROOT/'docs/verification/ec11-flange-nut'
CAD=ROOT/'mechanical/bench-holder/ec11-flange-nut-n1.FCStd'
PITCH=.75
DIAMETER=7.0
FLANGE_D=14.0
FLANGE_H=.72
NUT_H=3.0
HEX_AF=11.0
COUPON_H=2.25
VARIANTS=[('A',.05),('B',.10),('C',.15)]

def profile(doc,body,name,z=0,xz=False):
    s=doc.addObject('Sketcher::SketchObject',name);body.addObject(s)
    s.Placement=App.Placement(App.Vector(0,0,z),App.Rotation(App.Vector(1,0,0),90) if xz else App.Rotation())
    return s

def circle(s,r):
    i=s.addGeometry(Part.Circle(App.Vector(),App.Vector(0,0,1),r),False)
    s.addConstraint(Sketcher.Constraint('Coincident',i,3,-1,1))
    s.addConstraint(Sketcher.Constraint('Radius',i,r))

def polygon(s,pts):
    for i,p in enumerate(pts):
        q=pts[(i+1)%len(pts)]
        idx=s.addGeometry(Part.LineSegment(App.Vector(p[0],p[1],0),App.Vector(q[0],q[1],0)),False)
        s.addConstraint(Sketcher.Constraint('Block',idx))

def feature(doc,body,kind,name,s,length=None):
    prev=body.Tip
    f=body.newObject('PartDesign::'+kind,name);f.Profile=s
    if length is not None:f.Length=length
    if kind=='Pocket':f.Reversed=True
    doc.recompute()
    if prev and prev!=s:prev.Visibility=False
    s.Visibility=False
    return f

def build_body(doc,letter,allowance,coupon=False):
    name=('Coupon' if coupon else 'Nut')+letter
    b=doc.addObject('PartDesign::Body',name)
    b.Label=f'{name} - M7 x 0.75 - radial +{allowance:.2f} mm'
    for prop,val in [('ThreadPitch',PITCH),('RadialAllowance',allowance),('FlangeDiameter',FLANGE_D),
                     ('FlangeThickness',FLANGE_H),('AcrossFlats',HEX_AF),('OverallHeight',COUPON_H if coupon else NUT_H)]:
        b.addProperty('App::PropertyLength',prop,'Dimensions');setattr(b,prop,val)
    height=COUPON_H if coupon else NUT_H
    s=profile(doc,b,name+'FlangeProfile');circle(s,FLANGE_D/2)
    feature(doc,b,'Pad',name+'FlangePad',s,height if coupon else FLANGE_H)
    if not coupon:
        s=profile(doc,b,name+'HexagonProfile',FLANGE_H)
        r=HEX_AF/math.sqrt(3)
        polygon(s,[(r*math.cos(i*math.pi/3),r*math.sin(i*math.pi/3)) for i in range(6)])
        feature(doc,b,'Pad',name+'HexagonPad',s,height-FLANGE_H)
    minor=(DIAMETER-1.082532*PITCH)/2+allowance
    major=DIAMETER/2+allowance
    s=profile(doc,b,name+'ThreadCoreProfile');circle(s,minor)
    feature(doc,b,'Pocket',name+'ThroughCore',s,height+.1)
    # Explicit revolved lead-ins give bed-edge relief before the helix cut.
    s=profile(doc,b,name+'LeadInProfile',xz=True)
    polygon(s,[(minor-.03,-.01),(major+.22,-.01),(minor-.03,.36)])
    polygon(s,[(minor-.03,height+.01),(major+.22,height+.01),(minor-.03,height-.36)])
    prev=b.Tip
    f=b.newObject('PartDesign::Groove',name+'ThreadLeadIns');f.Profile=s
    f.ReferenceAxis=(s,['V_Axis']);f.Angle=360;f.Refine=True
    doc.recompute();prev.Visibility=False;s.Visibility=False
    s=profile(doc,b,name+'ThreadFlankProfile',xz=True)
    half_root=PITCH/16
    half_mouth=half_root+(major-minor)/math.sqrt(3)
    polygon(s,[(minor-.04,-half_mouth-.025),(major,-half_root),
               (major,half_root),(minor-.04,half_mouth+.025)])
    previous=b.Tip
    f=b.newObject('PartDesign::SubtractiveHelix',name+'M7Thread')
    f.Profile=s;f.ReferenceAxis=(s,['V_Axis']);f.Mode='pitch-height-angle'
    f.Pitch=PITCH;f.Height=height+PITCH;f.LeftHanded=False;f.Reversed=False;f.Refine=True
    doc.recompute();previous.Visibility=False;s.Visibility=False
    assert not f.Shape.isNull() and f.Shape.isValid() and len(f.Shape.Solids)==1,(name,f.State)
    # Countable external notches: A=1, B=2, C=3; no text too fine to print.
    s=profile(doc,b,name+'IdentificationProfile')
    for j in range(ord(letter)-ord('A')+1):
        angle=(j-1)*.17
        # Small rectangular edge nicks on the +X flange edge, away from bore.
        rr,tt=6.75,angle
        center=(rr*math.cos(tt),rr*math.sin(tt))
        polygon(s,[(center[0]+dx,center[1]+dy) for dx,dy in [(-.2,-.27),(.6,-.27),(.6,.27),(-.2,.27)]])
    f=feature(doc,b,'Pocket',name+'IdentificationNotches',s,height if coupon else FLANGE_H)
    assert f.Shape.isValid() and len(f.Shape.Solids)==1,name
    b.Placement.Base=App.Vector((ord(letter)-65)*22,26 if coupon else 0,0)
    b.ViewObject.ShapeColor=(.25,.42,.60) if coupon else (.72,.76,.80)
    f.ViewObject.ShapeColor=b.ViewObject.ShapeColor
    return b

def main():
    assert not any(d.Name=='EC11FlangeNutN1' or (d.FileName and Path(d.FileName).resolve()==CAD.resolve())
                   for d in App.listDocuments().values()),'Existing nut document must be closed before rebuilding'
    OUT.mkdir(parents=True,exist_ok=True);EV.mkdir(parents=True,exist_ok=True)
    holder=App.getDocument('bench_holder_b1')
    assert holder and Path(holder.FileName).resolve()==(ROOT/'mechanical/bench-holder/bench-holder-b1.FCStd').resolve()
    assert holder.getObject('EncoderBoreSketch').Geometry[0].Radius==3.6
    assert holder.getObject('EncoderLandSketch').Geometry[0].Radius==10
    assert float(holder.getObject('EncoderLand').Length)==1.5
    holder_hash=hashlib.sha256(Path(holder.FileName).read_bytes()).hexdigest()
    doc=App.newDocument('EC11FlangeNutN1');doc.Label='EC11 flanged nut N1 - M7 x 0.75'
    prod=doc.addObject('App::DocumentObjectGroup','ProductionAlternatives')
    prod.Label='Install ONE matching nut - A/B/C are clearance alternatives'
    tests=doc.addObject('App::DocumentObjectGroup','IndependentThreadCoupons')
    tests.Label='Print first - one/two/three notches identify A/B/C'
    bodies=[]
    for coupon in [False,True]:
        for letter,allowance in VARIANTS:
            b=build_body(doc,letter,allowance,coupon)
            (tests if coupon else prod).addObject(b);bodies.append(b)
    # Actual native panel seat, cropped for an understandable assembly reference.
    panel=holder.getObject('ControlPanel')
    seat=panel.Shape.copy();seat.transformShape(panel.Placement.inverse().toMatrix())
    seat.translate(App.Vector(-120,-48,-1.5))
    seat=seat.common(Part.makeCylinder(12,5,App.Vector(0,0,-2)))
    seat.translate(App.Vector(22,0,0))
    ref=doc.addObject('PartDesign::Feature','PanelSeatReference')
    ref.Label='REFERENCE - actual B1 seat crop - excluded from print exports';ref.Shape=seat
    ref.addProperty('App::PropertyString','SourceFile','Source');ref.SourceFile='bench-holder-b1.FCStd / ControlPanel'
    ref.ViewObject.ShapeColor=(.68,.50,.27)
    doc.recompute()
    checks={'revision':'N1','holder_sha256':holder_hash,'source_holder':str(Path(holder.FileName).relative_to(ROOT)),
        'panel_hole_mm':7.2,'seat_diameter_mm':20,'land_thickness_mm':1.5,
        'flange_diameter_mm':FLANGE_D,'flange_height_mm':FLANGE_H,'nut_height_mm':NUT_H,
        'hex_across_flats_mm':HEX_AF,'pitch_mm':PITCH,'thread_hand':'right',
        'flange_radial_coverage_mm':(FLANGE_D-7.2)/2,'flange_seat_radial_clearance_mm':(20-FLANGE_D)/2,
        'parts':[],'panel_intersection_mm3':doc.getObject('NutB').Shape.common(seat).Volume}
    assert checks['panel_intersection_mm3']<1e-7
    for b in bodies:
        sh=b.Shape.copy();sh.translate(-b.Placement.Base)
        sh.translate(App.Vector(FLANGE_D/2,FLANGE_D/2,0))
        assert sh.isValid() and len(sh.Solids)==1
        # Export a copied shape; the assembly/source body stays in place.
        temp=doc.addObject('PartDesign::Feature','PrintExport_'+b.Name);temp.Shape=sh
        Part.export([temp],str(OUT/(b.Name.lower()+'.step')))
        mesh=MeshPart.meshFromShape(Shape=sh,LinearDeflection=.018,AngularDeflection=.08,Relative=False)
        mesh.write(str(OUT/(b.Name.lower()+'.stl')))
        bb=mesh.BoundBox
        # OCC's conservative translated spline bounds can include control points
        # beyond a trimmed helix; actual mesh vertices establish print bed bounds.
        assert abs(bb.ZMin)<1e-5 and abs(bb.ZMax-float(b.OverallHeight))<1e-5,(b.Name,str(bb))
        checks['parts'].append({'name':b.Name,'valid':sh.isValid(),'solids':len(sh.Solids),
            'volume_mm3':sh.Volume,'bounds_mm':[bb.XLength,bb.YLength,bb.ZLength],
            'bed_z_mm':bb.ZMin,'triangles':mesh.CountFacets,'mesh_solid':mesh.isSolid(),
            'radial_allowance_mm':float(b.RadialAllowance),'thread_feature_type':doc.getObject(b.Name+'M7Thread').TypeId,
            'fully_constrained_profiles':all(o.FullyConstrained for o in b.Group if o.TypeId=='Sketcher::SketchObject')})
        assert mesh.isSolid()
        doc.removeObject(temp.Name)
    assert hashlib.sha256(Path(holder.FileName).read_bytes()).hexdigest()==holder_hash
    doc.recompute();doc.saveAs(str(CAD))
    checks['cad_sha256']=hashlib.sha256(CAD.read_bytes()).hexdigest()
    (EV/'cad-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    if App.GuiUp:
        import FreeCADGui as Gui
        Gui.activeDocument().activeView().viewAxonometric();Gui.activeDocument().activeView().fitAll()
        Gui.activeDocument().activeView().saveImage(str(EV/'native-model.png'),1500,1000,'White')
    return checks

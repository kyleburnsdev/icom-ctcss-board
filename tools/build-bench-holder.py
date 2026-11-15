"""Build the B1 open bench holder with FreeCAD's native API.

Run with FreeCAD 1.1's bundled Python from the repository root:
  & 'C:/Program Files/FreeCAD 1.1/bin/python.exe' tools/build-bench-holder.py
Dimensions are mm. The generator owns layout; individual fully constrained
sketches and Pad/Pocket lengths remain editable in the saved native document.
No existing enclosure or electrical source is opened or modified.
"""
from pathlib import Path
import hashlib
import json
import math
import importlib.util
import FreeCAD as App
import Part
import Sketcher
import MeshPart
import Draft

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'manufacturing/bench-holder'
CAD = ROOT / 'mechanical/bench-holder/bench-holder-b1.FCStd'
EVIDENCE = ROOT / 'docs/verification/bench-holder'
BOARD_HOLES = [(31,111),(169,111),(31,199),(169,199)]
PANEL_PINS = [(7,8),(203,8),(7,82),(203,82)]
LCD_HOLES = [(22,25),(62,25),(42,65),(82,65)]
CONTROL_HOLES = [('Encoder',120,48,7.2),('Bypass',155,48,6.5),
                 ('PttButton',190,48,16.3),('MicAdapter',120,18,16.2),
                 ('RadioAdapter',165,18,16.2),('PttLed',148,72,5.2),
                 ('BypassLed',172,72,5.2)]
PARTS = ['Base','ControlPanel','LedKeeper','PcbSpacer','InterfaceCoupon','MountCoupon','InsertCoupon']
PRODUCTION = ['Base','ControlPanel','LedKeeper','PcbSpacer']
COUPONS = ['InterfaceCoupon','MountCoupon','InsertCoupon']
# Panel coordinates are local to its mounting face. Positive local Y goes
# uphill toward the PCB; local Z points out of the control face.
PANEL_ANGLE_DEG = 30
PANEL_FRONT_Z = 30
PCB_STAND = 12
PCB_Z = 3 + PCB_STAND
PCB_THREAD_LENGTH = 6
PCB_THREAD_START_Z = PCB_Z - PCB_THREAD_LENGTH
INSERT_PILOT_D = 4.6  # Trial default: qualify 4.4 / 4.6 / 4.8 coupon first.
INSERT_POCKET_DEPTH = 5.5
spec=importlib.util.spec_from_file_location('bench_threads',Path(__file__).with_name('bench-holder-threads.py'))
thread_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(thread_module)


class Builder:
    def __init__(self, doc):
        self.doc = doc
        self.text_profiles=doc.addObject('App::DocumentObjectGroup','LabelProfiles')
        self.text_profiles.Label='Editable label text profiles'

    def body(self, name):
        return self.doc.addObject('PartDesign::Body', name)

    def sketch(self, body, name, z):
        s = self.doc.addObject('Sketcher::SketchObject', name + 'Sketch')
        body.addObject(s)
        s.Placement.Base.z = z
        return s

    def locate(self, s, geo, point, x, y):
        for axis, value, reference in [('X',x,-2),('Y',y,-1)]:
            if abs(value) < 1e-8:
                s.addConstraint(Sketcher.Constraint('PointOnObject',geo,point,reference))
            else:
                s.addConstraint(Sketcher.Constraint('Distance'+axis,geo,point,value))

    def rect(self, s, x, y, w, h):
        start = s.GeometryCount
        pts = [(x,y),(x+w,y),(x+w,y+h),(x,y+h)]
        for i,p in enumerate(pts):
            q = pts[(i+1)%4]
            s.addGeometry(Part.LineSegment(App.Vector(*p,0),App.Vector(*q,0)),False)
        for i in range(4):
            s.addConstraint(Sketcher.Constraint('Coincident',start+i,2,start+(i+1)%4,1))
            s.addConstraint(Sketcher.Constraint('Horizontal' if i%2 == 0 else 'Vertical',start+i))
        self.locate(s,start,1,x,y)
        s.addConstraint(Sketcher.Constraint('Distance',start,w))
        s.addConstraint(Sketcher.Constraint('Distance',start+1,h))

    def circle(self,s,x,y,r):
        i = s.addGeometry(Part.Circle(App.Vector(x,y,0),App.Vector(0,0,1),r),False)
        self.locate(s,i,3,x,y)
        s.addConstraint(Sketcher.Constraint('Radius',i,r))

    def feature(self,body,name,s,length,cut=False,reverse=False):
        previous = body.Tip
        f = body.newObject('PartDesign::Pocket' if cut else 'PartDesign::Pad',name)
        f.Profile = s
        f.Length = length
        f.Reversed = reverse
        f.Refine = True
        self.doc.recompute()
        if f.Shape.isNull() or not f.Shape.isValid() or len(f.Shape.Solids)!=1:
            raise RuntimeError(f'{name}: {f.State}')
        if previous and previous.ViewObject: previous.Visibility = False
        if s.ViewObject: s.Visibility = False
        return f

    def rectangle(self,b,name,rect,z,length,cut=False,reverse=False):
        s=self.sketch(b,name,z)
        self.rect(s,*rect)
        return self.feature(b,name,s,length,cut,reverse)

    def circles(self,b,name,centres,r,z,length,cut=False,reverse=False):
        s=self.sketch(b,name,z)
        for x,y in centres: self.circle(s,x,y,r)
        return self.feature(b,name,s,length,cut,reverse)

    def polygon(self,s,points):
        start=s.GeometryCount
        for i,p in enumerate(points):
            q=points[(i+1)%len(points)]
            index=s.addGeometry(Part.LineSegment(App.Vector(*p,0),App.Vector(*q,0)),False)
            s.addConstraint(Sketcher.Constraint('Block',index))

    def angled_panel_sketch(self,body,name):
        s=self.sketch(body,name,0)
        s.Placement=App.Placement(App.Vector(0,0,PANEL_FRONT_Z),
                                  App.Rotation(App.Vector(1,0,0),PANEL_ANGLE_DEG))
        return s

    def panel_side_rails(self,body):
        # A native YZ trapezoid, padded along X, puts continuous extrusion
        # under the inclined mounting face without tall separate posts.
        for label,x in [('Left',1),('Right',197)]:
            s=self.sketch(body,label+'PanelRail',0)
            s.Placement=App.Placement(App.Vector(x,0,0),
                App.Rotation(App.Vector(0,1,0),App.Vector(0,0,1),App.Vector(1,0,0),'ZXY'))
            rear_y=90*math.cos(math.radians(PANEL_ANGLE_DEG))
            rear_z=PANEL_FRONT_Z+90*math.sin(math.radians(PANEL_ANGLE_DEG))
            self.polygon(s,[(0,3),(rear_y,3),(rear_y,rear_z),(0,PANEL_FRONT_Z)])
            self.feature(body,label+'PanelRail',s,12)

    def pcb_threads(self,body,centres,name):
        minor=(3-1.082532*.5)/2+.10
        self.circles(body,name+'Core',centres,minor,PCB_Z,PCB_Z+.5,True)
        self.circles(body,name+'LowerClearance',centres,1.7,
                     PCB_THREAD_START_Z,PCB_THREAD_START_Z+.5,True)
        for i,(x,y) in enumerate(centres,1):
            thread_module.cut_m3_thread(self.doc,body,name+str(i),x,y,
                                       PCB_THREAD_START_Z,PCB_THREAD_LENGTH)
        for x,y in centres:
            assert body.Shape.common(Part.makeCylinder(1.2,PCB_Z,App.Vector(x,y,0))).Volume<1e-6
        return body.Tip

    def lettering(self,body,name,text,x,y,z,size=3,placement=None):
        previous=body.Tip
        letters=Draft.makeShapeString(String=text,FontFile='C:/Windows/Fonts/arialbd.ttf',Size=size,Tracking=0)
        letters.Label=name+' text profile'
        self.text_profiles.addObject(letters)
        self.doc.recompute()
        bb=letters.Shape.BoundBox
        local=App.Placement(App.Vector(x-(bb.XMin+bb.XMax)/2,y-bb.YMin,z),App.Rotation())
        letters.Placement=placement.multiply(local) if placement else local
        # A named PartDesign Pad over the native ShapeString keeps each legend
        # editable without generating triangulated or custom-serialized text.
        f=body.newObject('PartDesign::Pad',name);f.Profile=letters;f.Length=.6;f.Refine=True
        self.doc.recompute()
        assert f.Shape.isValid() and len(f.Shape.Solids)==1, name
        if previous.ViewObject:previous.Visibility=False
        if letters.ViewObject:letters.Visibility=False
        return f


def build():
    OUT.mkdir(parents=True,exist_ok=True)
    CAD.parent.mkdir(parents=True,exist_ok=True)
    EVIDENCE.mkdir(parents=True,exist_ok=True)
    if CAD.exists() and any(d.FileName == str(CAD) for d in App.listDocuments().values()):
        raise RuntimeError('Close this exact bench-holder document before rebuilding.')
    doc=App.newDocument('CTCSS_BenchHolder_B1')
    doc.Label='CTCSS B1 - assembled-board bench holder'
    doc.Comment='Temporary PLA bench support. Fully soldered PCB; no soldering on holder.'
    m=Builder(doc)
    b=m.body('Base')
    m.rectangle(b,'InsulatingFloor',(0,0,210,220),0,3)
    s=m.sketch(b,'LowEdgeRim',3)
    m.rect(s,0,0,210,220);m.rect(s,2,2,206,216)
    m.feature(b,'LowEdgeRim',s,3)
    m.circles(b,'PcbSupports',BOARD_HOLES,3.75,3,PCB_STAND)
    m.pcb_threads(b,BOARD_HOLES,'PrintedM3PcbThreads')
    m.panel_side_rails(b)
    s=m.angled_panel_sketch(b,'PanelInsertPockets')
    for x,y in PANEL_PINS:m.circle(s,x,y,INSERT_PILOT_D/2)
    m.feature(b,'PanelInsertPockets',s,INSERT_POCKET_DEPTH,True)
    # Open combs support harness bundles without introducing purchased ties.
    s=m.sketch(b,'HarnessCombs',3)
    for x in [12,24,36,174,186,198]: m.rect(s,x-1,92,2,8)
    m.feature(b,'HarnessCombs',s,6)

    p=m.body('ControlPanel')
    m.rectangle(p,'PanelSkin',(0,0,210,90),0,3)
    m.circles(p,'PanelScrewBores',PANEL_PINS,1.7,3,3,True)
    for name,x,y,d in CONTROL_HOLES:
        m.circles(p,name+'Bore',[(x,y)],d/2,3,3,True)
    for name,x,y,r,depth in [('EncoderLand',120,48,10,1.5),
                             ('BypassLand',155,48,7,1.5),
                             ('MicLand',120,18,13.5,1),
                             ('RadioLand',165,18,13.5,1)]:
        m.circles(p,name,[(x,y)],r,3,depth,True)
    m.circles(p,'LedFlangeSeats',[(148,72),(172,72)],3.5,0,1.6,True,True)
    m.circles(p,'KeeperSockets',[(160,68),(160,76)],1.6,0,1.8,True,True)
    m.circles(p,'LcdSupports',LCD_HOLES,2,3,6)
    m.circles(p,'LcdLocators',LCD_HOLES,.95,9,2.3)
    # These slots accept a relaxed insulated-wire loop through an LCD mounting
    # ear if needed; the loop must not cross or press the viewing glass.
    s=m.sketch(p,'LcdRetentionSlots',3)
    for x,y in LCD_HOLES: m.rect(s,x-3.5,y-1,1.2,2)
    m.feature(p,'LcdRetentionSlots',s,3,True)
    for name,text,x,y,size in [('LcdLabel','LCD',52,73,3),('ToneLabel','TONE',120,66,3),
            ('BypassLabel','BYPASS',155,57,2.8),('PttTestLabel','PTT TEST',190,63,2.8),
            ('PttLedLabel','PTT',148,79,2.5),('BypassLedLabel','BYPASS',172,79,2.5),
            ('MicLabel','MIC',120,1.6,2.8),('RadioLabel','RADIO',165,1.6,2.8)]:
        m.lettering(p,name,text,x,y,3,size)

    k=m.body('LedKeeper')
    m.rectangle(k,'KeeperBridge',(142,66,36,12),0,2)
    s=m.sketch(k,'LeadEscapeSlots',2)
    for x in [148,172]: m.rect(s,x-2.25,65,4.5,7)
    m.feature(k,'LeadEscapeSlots',s,2,True)
    # Deliberate 0.1 mm diametral interference, qualified on the coupon.
    m.circles(k,'KeeperPins',[(160,68),(160,76)],1.65,2,2)

    w=m.body('PcbSpacer')
    m.circles(w,'SpacerDisc',[(0,0)],4,0,2)
    m.circles(w,'SpacerClearance',[(0,0)],1.7,2,2,True)

    c=m.body('InterfaceCoupon')
    m.rectangle(c,'CouponSkin',(0,0,122,45),0,3)
    for name,x,y,d in [('Ptt',15,19,16.3),('Gx',42,19,16.2),
                        ('Encoder',68,19,7.2),('Toggle',90,19,6.5),('Led',110,19,5.2)]:
        m.circles(c,'Fit'+name,[(x,y)],d/2,3,3,True)
    m.circles(c,'FitGxLand',[(42,19)],13.5,3,1,True)
    m.circles(c,'FitEncoderLand',[(68,19)],10,3,1.5,True)
    m.circles(c,'FitToggleLand',[(90,19)],7,3,1.5,True)
    m.circles(c,'FitLedSeat',[(110,19)],3.5,0,1.6,True,True)
    m.circles(c,'FitKeeperSocket',[(110,35)],1.6,0,1.8,True,True)

    c=m.body('MountCoupon')
    m.rectangle(c,'MountCouponFoot',(0,0,96,52),0,3)
    m.circles(c,'FitPcbSupports',[(4,8),(92,8)],3.75,3,PCB_STAND)
    m.pcb_threads(c,[(4,8),(92,8)],'FitPrintedM3Threads')
    # Represents both the LCD's 40 mm mounting pattern and the actual keeper pin.
    m.circles(c,'FitLcdSupports',[(10,36),(50,36)],2,3,6)
    m.circles(c,'FitLcdPins',[(10,36),(50,36)],.95,9,2.3)
    m.circles(c,'FitKeeperPin',[(87,36)],1.65,3,2)

    c=m.body('InsertCoupon')
    m.rectangle(c,'InsertCouponFoot',(0,0,90,25),0,3)
    for number,x in enumerate([9,39,69],1):
        s=m.sketch(c,'InsertCouponRail'+str(number),0)
        s.Placement=App.Placement(App.Vector(x,0,0),
            App.Rotation(App.Vector(0,1,0),App.Vector(0,0,1),App.Vector(1,0,0),'ZXY'))
        m.polygon(s,[(0,3),(25,3),(25,12+25*math.tan(math.radians(30))),(0,12)])
        m.feature(c,'InsertCouponRail'+str(number),s,12)
    for x,dia in [(15,4.4),(45,4.6),(75,4.8)]:
        s=m.sketch(c,'Pilot'+str(int(dia*10)),0)
        s.Placement=App.Placement(App.Vector(0,0,12),App.Rotation(App.Vector(1,0,0),30))
        m.circle(s,x,12,dia/2)
        m.feature(c,'Pilot'+str(int(dia*10)),s,INSERT_POCKET_DEPTH,True)
        m.lettering(c,'PilotLabel'+str(int(dia*10)),str(dia),x,18,0,2.5,
            App.Placement(App.Vector(0,0,12),App.Rotation(App.Vector(1,0,0),30)))

    # Native reference geometry is kept in its own group and excluded from export.
    refs=doc.addObject('App::DocumentObjectGroup','ReferenceEnvelopes')
    def reference(name,shape):
        o=doc.addObject('Part::Feature',name);o.Shape=shape;refs.addObject(o)
        if o.ViewObject: o.Visibility=False
        return o
    board=Part.makeBox(150,100,1.5,App.Vector(25,105,PCB_Z))
    for x,y in BOARD_HOLES: board=board.cut(Part.makeCylinder(2,1.5,App.Vector(x,y,PCB_Z)))
    reference('PcbReference',board)
    panel_placement=App.Placement(App.Vector(0,0,PANEL_FRONT_Z),App.Rotation(App.Vector(1,0,0),PANEL_ANGLE_DEG))
    def panel_reference(name,shape):
        shape.Placement=panel_placement.multiply(shape.Placement)
        reference(name,shape)
    panel_reference('LcdBodyReference',Part.makeBox(80,40,13.5,App.Vector(12,25,9)))
    for name,x,y,d in CONTROL_HOLES:
        if name.endswith('Adapter'):panel_reference(name+'RearEnvelope',Part.makeCylinder(12,30,App.Vector(x,y,-30)))
    p.Placement=panel_placement
    k.Placement=panel_placement.multiply(App.Placement(App.Vector(0,0,-2.2),App.Rotation()))
    production=doc.addObject('App::DocumentObjectGroup','ProductionParts')
    production.Label='Production parts - assembly coordinates'
    production.addObjects([doc.getObject(n) for n in PRODUCTION])
    qualification=doc.addObject('App::DocumentObjectGroup','FitCoupons')
    qualification.Label='Fit coupons - separate print plate'
    qualification.addObjects([doc.getObject(n) for n in COUPONS])
    doc.recompute()
    doc.saveAs(str(CAD))

    records=[]
    for name in PARTS:
        obj=doc.getObject(name)
        shape=obj.Shape.copy()
        if name in ['ControlPanel','LedKeeper']:
            # Undo only the assembly rotation; preserve each body's local
            # feature geometry before translating its minimum onto the bed.
            shape.Placement=obj.Placement.inverse().multiply(shape.Placement)
        # Shape includes its assembly placement; export a translation-only print
        # copy. Wide flat skins are down; all other features grow upward.
        bb=shape.BoundBox
        normalization=App.Vector(-bb.XMin,-bb.YMin,-bb.ZMin)
        shape.translate(normalization)
        bb=shape.BoundBox
        mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.015,AngularDeflection=.10,Relative=False)
        path=OUT/(name.lower()+'.stl');mesh.write(str(path))
        records.append({'name':name,'bounds_mm':[bb.XLength,bb.YLength,bb.ZLength],
                        'solid_count':len(shape.Solids),'valid':shape.isValid(),
                        'mesh_closed':mesh.isSolid(),'mesh_facets':mesh.CountFacets,
                        'print_translation_mm':[normalization.x,normalization.y,normalization.z],
                        'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        if not mesh.isSolid(): raise RuntimeError(name+' mesh is not closed')
    # STEP preserves the three production pieces in assembly coordinates.
    Part.export([doc.getObject(n) for n in ['Base','ControlPanel','LedKeeper']],str(OUT/'bench-holder-b1.step'))
    App.closeDocument(doc.Name)
    reopened=App.openDocument(str(CAD));reopened.recompute()
    errors=[o.Name for o in reopened.Objects if 'Invalid' in o.State]
    assert not errors, errors
    assert all(reopened.getObject(n).Shape.isValid() for n in PARTS)
    # Validity alone cannot establish that a generated cut survived recompute.
    for name,centres in [('Base',BOARD_HOLES),('MountCoupon',[(4,8),(92,8)])]:
        shape=reopened.getObject(name).Shape
        for x,y in centres:
            assert shape.common(Part.makeCylinder(1.2,PCB_Z,App.Vector(x,y,0))).Volume<1e-6
            assert shape.common(Part.makeCylinder(1.65,8.8,App.Vector(x,y,.1))).Volume<1e-6
    report={'revision':'B1','freecad_version':App.Version(),'native_reopen':True,
            'parts':records,'board_holes_mm':BOARD_HOLES,'lcd_holes_mm':LCD_HOLES,
            'panel_pins_mm':PANEL_PINS,'control_holes':CONTROL_HOLES,
            'pcb_underside_z_mm':PCB_Z,'pcb_support_height_mm':PCB_STAND,'panel_front_underside_z_mm':PANEL_FRONT_Z,
            'panel_angle_deg':PANEL_ANGLE_DEG,'insert_pilot_diameter_mm':INSERT_PILOT_D,
            'insert_pocket_depth_mm':INSERT_POCKET_DEPTH,
            'pcb_underlead_floor_clearance_for_2mm_leads_mm':PCB_STAND-2,
            'pcb_screw_holes':'upper 6 mm modeled M3 x 0.5 thread, lower 3.4 mm clearance bore; no blind floor',
            'pcb_thread_length_mm':PCB_THREAD_LENGTH,'pcb_thread_start_z_mm':PCB_THREAD_START_Z,
            'panel_labels':['LCD','TONE','BYPASS','PTT TEST','PTT','BYPASS','MIC','RADIO'],
            'source_sha256':hashlib.sha256(CAD.read_bytes()).hexdigest(),
            'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (EVIDENCE/'geometry.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    App.closeDocument(reopened.Name)
    print(json.dumps({'native_source':str(CAD),'parts':records},indent=2))


if __name__=='__main__': build()

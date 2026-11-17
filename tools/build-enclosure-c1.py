"""Build the C1 bench-derived enclosure study through Robust MCP.

Invoke main() in FreeCAD's console, through the bridge. Millimetres. This is a
new document; never overwrites B1/B2/P1 or their unsaved live documents. Layout
constants own regeneration; named native constrained sketches/Pad/Pocket features
remain editable. Radio centers use user measurements; bolts use Icom parts evidence.
"""
from pathlib import Path
import importlib.util
import hashlib
import json
import math

import FreeCAD as App
import Part
import Sketcher
import MeshPart
import Draft

ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / 'mechanical/enclosure/c1/ctcss-c1.FCStd'
EV = ROOT / 'docs/verification/enclosure-c1'
IMG = ROOT / 'docs/images/enclosure-c1'
OUT = ROOT / 'manufacturing/enclosure-c1'
WIDTH, DEPTH = 156., 240.
PCB_X, PCB_Y, PCB_Z = 28., 84., 15.
HOLES = [(34.,90.), (122.,90.), (34.,228.), (122.,228.)]
CLAMP_CENTRES = [(21.,90.), (135.,90.), (21.,228.), (135.,228.)]
PANEL_PINS = [(5.5,8.), (149.,8.), (5.5,82.), (149.,82.)]
PANEL_PLACEMENT = App.Placement(App.Vector(0,0,32), App.Rotation(App.Vector(1,0,0),30))
EARS = [(20.,28.9),(60.,28.9),(40.,73.1),(80.,73.1)]
LCD_CLAMPS = [(x,y+(-7.5 if y<50 else 7.5)) for x,y in EARS]
WINDOW = (15.15,44.39,65.5,15.5)
CONTROLS = [('Encoder',110.,47.,7.2),('Bypass',135.,47.,6.5),
            ('Mic',80.,14.,16.2),('Radio',122.,14.,16.2),
            ('PttLed',106.,74.,5.2),('BypassLed',132.,74.,5.2)]
PILOT_D = 4.6
RADIO_PLACEMENT = App.Placement(App.Vector(8,84,100),App.Rotation(App.Vector(1,0,0),-12))
RADIO_HOLES = [(39.,20.),(88.,20.)]  # user: 39 from faceplate, 49 spacing, 20 above bottom


def main():
    for p in [CAD.parent,EV,IMG,OUT]: p.mkdir(parents=True,exist_ok=True)
    assert not any(d.FileName and Path(d.FileName).resolve()==CAD.resolve()
                   for d in App.listDocuments().values()), 'Close C1 before regenerating; preserve manual edits.'
    inputs = [ROOT/'mechanical/bench-holder/bench-holder-b1.FCStd',
              ROOT/'mechanical/bench-holder/bench-panel-b2.FCStd']
    hashes = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    spec=importlib.util.spec_from_file_location('bench_builder',ROOT/'tools/build-bench-holder.py')
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    doc=App.newDocument('CTCSS_C1')
    doc.Label='C1 - narrow enclosure and 12 degree radio cradle - PLA PROTOTYPE'
    m=old.Builder(doc)
    production=doc.addObject('App::DocumentObjectGroup','EnclosureParts')
    coupons=doc.addObject('App::DocumentObjectGroup','IndependentFitCoupons')
    refs=doc.addObject('App::DocumentObjectGroup','ReferenceEnvelopes')
    refs.Label='Reference envelopes - excluded from printing'
    def body(name, group=production):
        b=m.body(name);group.addObject(b);return b
    def inserts(b,name,centres,z,depth=5.5):
        return m.circles(b,name,centres,PILOT_D/2,z,depth,True)
    def ref(name,shape,color=(.25,.55,.35),placement=None):
        if placement:shape.Placement=placement.multiply(shape.Placement)
        o=doc.addObject('Part::Feature',name);o.Shape=shape;refs.addObject(o)
        o.ViewObject.ShapeColor=color;o.ViewObject.Transparency=30
        return o
    def yz_sketch(b,name,x,points,length):
        s=m.sketch(b,name,0)
        s.Placement=App.Placement(App.Vector(x,0,0),
            App.Rotation(App.Vector(0,1,0),App.Vector(0,0,1),App.Vector(1,0,0),'ZXY'))
        m.polygon(s,points);return m.feature(b,name,s,length)
    def xz_sketch(b,name,y,points,length):
        s=m.sketch(b,name,0)
        s.Placement=App.Placement(App.Vector(0,y,0),App.Rotation(App.Vector(1,0,0),90))
        m.polygon(s,points);return m.feature(b,name,s,length)
    def engrave(b,name,text,x,y,z,size):
        prev=b.Tip
        t=Draft.makeShapeString(String=text,FontFile='C:/Windows/Fonts/arialbd.ttf',Size=size,Tracking=0)
        m.text_profiles.addObject(t);doc.recompute();bb=t.Shape.BoundBox
        t.Placement.Base=App.Vector(x-(bb.XMin+bb.XMax)/2,y-bb.YMin,z)
        f=b.newObject('PartDesign::Pocket',name);f.Profile=t;f.Length=.4
        doc.recompute();prev.Visibility=False;t.Visibility=False
        assert f.Shape.isValid() and len(f.Shape.Solids)==1,name

    b=body('Base')
    m.rectangle(b,'InsulatingFloor',(0,0,WIDTH,DEPTH),0,3)
    m.circles(b,'PcbSupportSeats',HOLES,4.5,3,12)
    # 3.6 pin is 0.4 diametral clearance in the existing 4 mm enclosure holes.
    # 2.1 high: projects 0.6 through nominal 1.5 PCB; straps have relief above it.
    m.circles(b,'PcbLocatingNubs',HOLES,1.8,15,2.1)
    for i,(x,y) in enumerate(CLAMP_CENTRES,1):
        m.rectangle(b,'CornerClampPedestal'+str(i),(x-5,y-5,10,10),3,13.5)
    inserts(b,'CornerClampInsertPilots',CLAMP_CENTRES,16.5)
    # Front panel rails follow B1's proven load path, with the narrower span.
    rear=90*math.cos(math.pi/6)
    for label,x in [('Left',1.),('Right',143.)]:
        yz_sketch(b,label+'PanelRail',x,[(0,3),(rear,3),(rear,77),(0,32)],9 if label=='Left' else 12)
    s=m.sketch(b,'PanelInsertPilots',0);s.Placement=PANEL_PLACEMENT
    for x,y in PANEL_PINS:m.circle(s,x,y,PILOT_D/2)
    m.feature(b,'PanelInsertPilots',s,5.5,True)
    # Side walls, inward bearing shelves, retaining lips; positive Y removal.
    for label,x in [('Left',0.),('Right',153.)]:
        m.rectangle(b,label+'RearWall',(x,78,3,162),3,56)
    for label,x in [('Left',3.),('Right',144.)]:
        m.rectangle(b,label+'CoverBearing',(x,90,9,146.7),50,3)
    xz_sketch(b,'LeftBearingGusset',236.7,[(3,41),(12,50),(3,50)],146.7)
    xz_sketch(b,'RightBearingGusset',236.7,[(153,41),(144,50),(153,50)],146.7)
    xz_sketch(b,'LeftCoverRetainingLip',236.7,[(3,54),(3,59),(8,59)],146.7)
    xz_sketch(b,'RightCoverRetainingLip',236.7,[(153,54),(153,59),(148,59)],146.7)
    # Positive stop joins side walls ahead of PCB; no change to board geometry.
    m.rectangle(b,'CoverFrontStop',(3,80,150,3),3,45)
    for label,x in [('Left',23.5),('Right',132.5)]:
        m.rectangle(b,label+'CoverLatchBoss',(x-4.5,201,9,13.5),3,56.3)
    inserts(b,'RearCoverLatchInsertPilots',[(23.5,210),(132.5,210)],59.3)

    p=body('ControlPanel')
    m.rectangle(p,'PanelSkin',(0,0,156,90),0,3)
    m.circles(p,'PanelScrewClearance',PANEL_PINS,1.7,3,3,True)
    m.rectangle(p,'LcdViewingWindow',WINDOW,3,3,True)
    for name,x,y,d in CONTROLS:m.circles(p,name+'Bore',[(x,y)],d/2,3,3,True)
    for name,x,y,r,depth in [('Encoder',110,47,10,1.5),('Bypass',135,47,7,1.5),
                            ('Mic',80,14,13.5,1),('Radio',122,14,13.5,1)]:
        m.circles(p,name+'MountingLand',[(x,y)],r,3,depth,True)
    m.circles(p,'LedFlangeSeats',[(106,74),(132,74)],3.5,0,1.6,True,True)
    # Same ear geometry as B2, now retained with off-board M3 insert clamps.
    m.circles(p,'DisplayEarSeats',EARS,2.1,0,14,reverse=True)
    m.circles(p,'DisplayLocatingNubs',EARS,.9,-14,1.2,reverse=True)
    m.circles(p,'DisplayInsertBosses',LCD_CLAMPS,5,0,15.6,reverse=True)
    # Insert from rear: pocket grows into the panel, so use reversed Pocket.
    m.circles(p,'DisplayInsertPilots',LCD_CLAMPS,PILOT_D/2,-15.6,5.5,True,True)
    for name,text,x,y,size in [('Tone','TONE',110,61,2.8),('Bypass','BYPASS',135,59,2.4),
                              ('Ptt','PTT',106,82,2.5),('BypassLed','BYP',132,82,2.5),
                              ('Mic','MIC',80,29,2.7),('Radio','RADIO',122,29,2.7)]:
        engrave(p,'Engraved'+name,text,x,y,3,size)
    m.circles(p,'LedKeeperInsertBosses',[(119,66),(119,82)],5,0,5.5,reverse=True)
    m.circles(p,'LedKeeperInsertPilots',[(119,66),(119,82)],PILOT_D/2,-5.5,5.5,True,True)
    p.Placement=PANEL_PLACEMENT

    keeper=body('LedKeeper')
    m.rectangle(keeper,'KeeperBridge',(101,61,36,26),-8.5,3)
    m.circles(keeper,'KeeperScrewClearance',[(119,66),(119,82)],1.7,-5.5,3,True)
    m.circles(keeper,'KeeperFlangePads',[(106,74),(132,74)],3.5,-5.5,3.9)
    m.circles(keeper,'LedLeadPassages',[(106,74),(132,74)],2.25,-1.6,7,True)
    keeper.Placement=PANEL_PLACEMENT

    # Four identical PCB corner straps, with the screw outside the board edge.
    # 3 mm grip + M3x8 -> 5 mm projection, engaging the complete L4 insert.
    strap=body('PcbCornerStrap')
    m.rectangle(strap,'StrapSkin',(0,-5,22,10),0,3)
    m.circles(strap,'StrapScrewClearance',[(5,0)],1.7,3,3,True)
    m.circles(strap,'NubRelief',[(18,0)],2.1,0,1.0,True,True)
    strap.Placement=App.Placement(App.Vector(16,90,16.5),App.Rotation())
    for i,(x,y,angle) in enumerate([(16,228,0),(140,90,180),(140,228,180)],2):
        link=doc.addObject('App::Link','InstalledPcbStrap'+str(i));link.setLink(strap)
        link.LinkPlacement=App.Placement(App.Vector(x,y,16.5),App.Rotation(App.Vector(0,0,1),angle))
        production.addObject(link)
    # Rear display clips: rounded broad head, no screw through LCD's small holes.
    clip=body('DisplayEarClip')
    m.rectangle(clip,'ClipSkin',(-5,-4,10,14),0,3)
    m.circles(clip,'ClipScrewClearance',[(0,0)],1.7,3,3,True)
    clip.Placement=PANEL_PLACEMENT.multiply(App.Placement(App.Vector(*LCD_CLAMPS[0],-18.6),App.Rotation()))
    for i,(x,y) in enumerate(LCD_CLAMPS[1:],2):
        link=doc.addObject('App::Link','InstalledDisplayClip'+str(i));link.setLink(clip)
        angle=180 if y>50 else 0
        link.LinkPlacement=PANEL_PLACEMENT.multiply(App.Placement(App.Vector(x,y,-18.6),App.Rotation(App.Vector(0,0,1),angle)))
        production.addObject(link)

    c=body('SlidingCover')
    m.rectangle(c,'CoverRoof',(8.3,90,139.4,150),59.3,3)
    for label,x in [('Left',8.3),('Right',144.3)]:
        m.rectangle(c,label+'CoverWeb',(x,90,3.4,150),53.3,6)
    xz_sketch(c,'LeftSlidingTongue',240,[(3.3,53.3),(11.7,53.3),(11.7,55.7),(5.1,55.7)],150)
    xz_sketch(c,'RightSlidingTongue',240,[(152.7,53.3),(144.3,53.3),(144.3,55.7),(150.9,55.7)],150)
    m.rectangle(c,'RearClosure',(3.3,237,149.4,3),3.3,59)
    m.circles(c,'CoverLatchScrewClearance',[(23.5,210),(132.5,210)],1.7,62.3,3,True)
    # Roof vents preserve solid side load paths and a transverse middle beam.
    s=m.sketch(c,'RoofVentSlots',62.3)
    for x in [30,42,54,66,78,90,102,114]:
        for y in [111,174]:m.rect(s,x,y,5,45)
    m.feature(c,'RoofVentSlots',s,3,True)
    # Wide supports at the side edges leave the central underside open. The side
    # cheeks use the supplied radio pattern; retain before applying a load.
    for label,x in [('Left',8.),('Right',136.)]:
        saddle=body(label+'RadioSaddle')
        yz_sketch(saddle,label+'CradleWedge',x,[(84,62.3),(239,62.3),(239,67.05),(84,100)],12)
        # Vertical screw access recesses end 3 mm above deck.
        for n,y in enumerate([104.,218.],1):
            m.circles(saddle,label+'ScrewAccess'+str(n),[(x+6,y)],3.2,110,44.7,True)
            m.circles(saddle,label+'ScrewClearance'+str(n),[(x+6,y)],1.7,65.3,3,True)
        # Side saddle bases overhang roof by 0.3 mm at X; attachment within roof.
        m.circles(c,label+'SaddleInsertBosses',[(x+6,104),(x+6,218)],4.5,59.3,6,reverse=True)
    inserts(c,'SaddleInsertPilots',[(14,104),(14,218),(142,104),(142,218)],62.3)

    # Side retaining cheeks: M4 OEM radio interface; M3x8 insert joints into
    # the cradle. The radio is not supported by its sheet-metal cover screws.
    for label,x,reverse in [('Left',-3.3,True),('Right',140.3,False)]:
        cheek=body(label+'RadioCheek')
        yz_sketch(cheek,label+'CheekPlate',x,[(23,-10),(104,-10),(104,27),(23,27)],3)
        # Pocket starts at outermost face, toward the part.
        sx=x if label=='Left' else x+3
        s=m.sketch(cheek,label+'RadioMountingHoles',0)
        s.Placement=App.Placement(App.Vector(sx,0,0),App.Rotation(App.Vector(0,1,0),App.Vector(0,0,1),App.Vector(1,0,0),'ZXY'))
        for y,z in RADIO_HOLES:m.circle(s,y,z,2.2)
        m.feature(cheek,label+'RadioMountingHoles',s,3,True,reverse)
        s=m.sketch(cheek,label+'CradleAttachmentHoles',0)
        s.Placement=App.Placement(App.Vector(sx,0,0),App.Rotation(App.Vector(0,1,0),App.Vector(0,0,1),App.Vector(1,0,0),'ZXY'))
        for y in [34.,94.]:m.circle(s,y,-7,1.7)
        m.feature(cheek,label+'CradleAttachmentHoles',s,3,True,reverse)
        cheek.Placement=RADIO_PLACEMENT
        saddle=doc.getObject(label+'RadioSaddle')
        s=m.sketch(saddle,label+'CheekInsertPilots',0)
        inner_x=0 if label=='Left' else 140
        s.Placement=RADIO_PLACEMENT.multiply(App.Placement(App.Vector(inner_x,0,0),App.Rotation(App.Vector(0,1,0),App.Vector(0,0,1),App.Vector(1,0,0),'ZXY')))
        for y in [34.,94.]:m.circle(s,y,-7,PILOT_D/2)
        m.feature(saddle,label+'CheekInsertPilots',s,5.5,True,reverse)

    # Independent actual interfaces, not a production part disguised as a test.
    q=body('NubAndStrapCoupon',coupons)
    m.rectangle(q,'CouponFloor',(0,0,36,22),0,3)
    m.circles(q,'CouponSupportSeat',[(23,11)],4.5,3,12)
    m.circles(q,'CouponLocatingNub',[(23,11)],1.8,15,2.1)
    m.rectangle(q,'CouponClampPedestal',(5,6,10,10),3,13.5)
    inserts(q,'CouponClampInsertPilot',[(10,11)],16.5)
    q=body('InsertPilotCoupon',coupons)
    m.rectangle(q,'InsertCouponBase',(0,0,46,18),0,9)
    for i,d in enumerate([4.4,4.6,4.8]):
        m.circles(q,'Pilot'+str(i),[(8+15*i,9)],d/2,9,5.5,True)
        engrave(q,'PilotLabel'+str(i),str(d),8+15*i,1,9,2)
    q=body('CoverRailCoupon',coupons)
    m.rectangle(q,'RailCouponFoot',(0,0,20,35),0,3)
    m.rectangle(q,'RailCouponWall',(0,0,3,35),3,18)
    m.rectangle(q,'RailCouponBearing',(3,0,9,35),12,3)
    xz_sketch(q,'RailCouponGusset',35,[(3,3),(12,12),(3,12)],35)
    xz_sketch(q,'RailCouponLip',35,[(3,16),(3,21),(8,21)],35)
    q=body('CoverTongueCoupon',coupons)
    xz_sketch(q,'TongueCouponFlange',35,[(0,0),(8.4,0),(8.4,2.4),(1.8,2.4)],35)
    m.rectangle(q,'TongueCouponWeb',(5,0,3.4,35),2.4,6.6)
    m.rectangle(q,'TongueCouponRoof',(5,0,12,35),6,3)
    q=body('RadioPatternCoupon',coupons)
    m.rectangle(q,'RadioPatternTemplate',(0,0,105,30),0,2)
    m.circles(q,'RadioPatternClearance',[(39,15),(88,15)],2.2,2,2,True)
    engrave(q,'FaceplateDatumLabel','FRONT',11,2,2,2.5)
    q=body('DisplayFitCoupon',coupons)
    m.rectangle(q,'DisplayCouponSkin',(5,13,92,74),0,3)
    m.rectangle(q,'DisplayCouponWindow',WINDOW,3,3,True)
    m.circles(q,'CouponDisplayEarSeats',EARS,2.1,0,14,reverse=True)
    m.circles(q,'CouponDisplayNubs',EARS,.9,-14,1.2,reverse=True)
    m.circles(q,'CouponDisplayBosses',LCD_CLAMPS,5,0,15.6,reverse=True)
    m.circles(q,'CouponDisplayInsertPilots',LCD_CLAMPS,PILOT_D/2,-15.6,5.5,True,True)

    board=Part.makeBox(100,150,1.5,App.Vector(PCB_X,PCB_Y,PCB_Z))
    for x,y in HOLES:board=board.cut(Part.makeCylinder(2,1.5,App.Vector(x,y,15)))
    ref('PcbReference',board)
    ref('PcbComponentAllowance',Part.makeBox(100,150,30,App.Vector(28,84,16.5)))
    ref('PcbLeadAllowance',Part.makeBox(100,150,2,App.Vector(28,84,13)))
    lcd=Part.makeBox(80,40,1.6,App.Vector(10,31,-15.6))
    for x,y in EARS:
        lcd=lcd.fuse(Part.makeCylinder(2.1,1.6,App.Vector(x,y,-15.6)))
        lcd=lcd.cut(Part.makeCylinder(1.15,1.6,App.Vector(x,y,-15.6)))
    ref('DisplayPcbReference',lcd,placement=PANEL_PLACEMENT)
    ref('DisplayBezelReference',Part.makeBox(70.8,23.8,9.8,App.Vector(12.5,42.49,-14)),placement=PANEL_PLACEMENT)
    ref('DisplayRearElectronicsAllowance',Part.makeBox(70,25,2.1,App.Vector(15,37,-17.7)),placement=PANEL_PLACEMENT)
    ref('GrovePlugAndBendAllowance',Part.makeBox(18,23,9,App.Vector(25,25,-14)),placement=PANEL_PLACEMENT)
    for name,x,y,d in CONTROLS:
        if name in ['Mic','Radio']:
            ref(name+'RearEnvelope',Part.makeCylinder(12,30,App.Vector(x,y,-30)),placement=PANEL_PLACEMENT)
            ref(name+'MatedPlugAllowance',Part.makeCylinder(13,45,App.Vector(x,y,3)),placement=PANEL_PLACEMENT)
        if name=='Encoder':ref('EncoderRearEnvelope',Part.makeBox(20,25,20,App.Vector(x-10,y-12.5,-20)),placement=PANEL_PLACEMENT)
        if name=='Bypass':ref('ToggleRearEnvelope',Part.makeBox(15,25,15,App.Vector(x-7.5,y-12.5,-15)),placement=PANEL_PLACEMENT)
    radio=Part.makeBox(140,155,40)
    ref('RadioReference_140x155x40',radio,(.15,.17,.20),RADIO_PLACEMENT)

    # Do not let fit coupons or allowance blocks obscure the human assembly view.
    doc.recompute()
    doc.saveAs(str(CAD))
    for o in doc.Objects:
        if o.ViewObject:o.Visibility=False
    production.Visibility=True
    for o in production.Group:
        o.Visibility=True
        if o.TypeId=='PartDesign::Body':o.Tip.Visibility=True
        if o.TypeId=='PartDesign::Body':o.ViewObject.ShapeColor=(.24,.28,.34) if o.Name!='ControlPanel' else (.33,.37,.43)
    refs.Visibility=True
    for o in refs.Group:o.Visibility=False
    for name in ['PcbReference','DisplayPcbReference','DisplayBezelReference','RadioReference_140x155x40']:
        doc.getObject(name).Visibility=True
    doc.recompute()
    checks={'revision':'C1','status':'PLA fit prototype; OEM radio bolt interface documented by part match',
        'freecad_version':App.Version(),'base_mm':[WIDTH,DEPTH],
        'panel_mm':[156,90,3],'panel_angle_deg':30,'radio_angle_deg':12,
        'board_mm':[100,150,1.5],'board_holes_mm':HOLES,
        'pcb_transform':'X=28+boardX; Y=84+boardY; Z=15+boardZ; 90 degrees from B1 placement',
        'nub_diameter_mm':3.6,'nub_height_mm':2.1,'pcb_hole_diameter_mm':4,
        'insert_pilot_mm':4.6,'insert_pocket_depth_mm':5.5,
        'screw_standard':'M3 x 8 socket head cap; radio OEM screws pending identification',
        'side_slide_clearance_mm':.3,'lower_slide_clearance_mm':.3,'upper_diagonal_vertical_clearance_mm':.4,
        'control_holes':CONTROLS,'lcd_ears_mm':EARS,'lcd_clamps_mm':LCD_CLAMPS,
        'window_mm':WINDOW,'parts':[],'intersections_mm3':{},'baseline_sha256':hashes,
        'radio_holes_local_yz_mm':RADIO_HOLES,'radio_screw':'8820000530, M4 x 8 inferred by Icom part-number match',
        'physical_acceptance':'not run','remaining':['radio bolt engagement acceptance','installed cable envelopes','PLA load/temperature acceptance','insert quantity']}
    for o in production.Group:
        if o.TypeId=='PartDesign::Body':
            assert o.Shape.isValid() and len(o.Shape.Solids)==1,o.Name
            checks['parts'].append({'name':o.Name,'solids':len(o.Shape.Solids),'volume_mm3':o.Shape.Volume})
    for n in ['Base','ControlPanel','SlidingCover']:
        for r in ['PcbReference','DisplayPcbReference','DisplayBezelReference','GrovePlugAndBendAllowance','EncoderRearEnvelope','ToggleRearEnvelope','MicRearEnvelope','RadioRearEnvelope']:
            checks['intersections_mm3'][n+'/'+r]=doc.getObject(n).Shape.common(doc.getObject(r).Shape).Volume
    for a,bn in [('Base','ControlPanel'),('Base','SlidingCover'),('SlidingCover','PcbComponentAllowance')]:
        checks['intersections_mm3'][a+'/'+bn]=doc.getObject(a).Shape.common(doc.getObject(bn).Shape).Volume
    for pth in inputs:assert hashlib.sha256(pth.read_bytes()).hexdigest()==hashes[str(pth.relative_to(ROOT))]
    doc.saveAs(str(CAD))
    if App.GuiUp:
        import FreeCADGui as Gui
        v=Gui.activeDocument().activeView();v.viewAxonometric();v.fitAll()
        v.saveImage(str(IMG/'assembly.png'),1600,1100,'White')
        doc.getObject('RadioReference_140x155x40').Visibility=False
        doc.getObject('SlidingCover').Visibility=False
        doc.getObject('LeftRadioSaddle').Visibility=False;doc.getObject('RightRadioSaddle').Visibility=False
        v.fitAll();v.saveImage(str(IMG/'base-and-panel.png'),1600,1100,'White')
        for n in ['RadioReference_140x155x40','SlidingCover','LeftRadioSaddle','RightRadioSaddle']:doc.getObject(n).Visibility=True
        v.fitAll();doc.save()
    checks['source_sha256']=hashlib.sha256(CAD.read_bytes()).hexdigest()
    checks['generator_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (EV/'cad-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    return checks


if __name__=='__main__':main()

"""Build the B2 rear-display panel using FreeCAD's native API.

Run main() through Robust MCP execute_python. B1 is read only; the saved native
file is copied whole before native loading, never edited as an archive.
Dimensions below own regeneration. Reference envelopes are not print parts.
"""
from pathlib import Path
import importlib.util, json, hashlib, math, shutil
import FreeCAD as App
import Part, Sketcher, MeshPart, Draft

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'manufacturing/bench-panel-b2'
EV=ROOT/'docs/verification/bench-panel-b2'
CAD=ROOT/'mechanical/bench-holder/bench-panel-b2.FCStd'
WORK=ROOT/'.agent-scratch/panel-rear-display'
_lcd_spec=importlib.util.spec_from_file_location('grove_lcd_v4',Path(__file__).with_name('grove-lcd-v4.py'))
lcd=importlib.util.module_from_spec(_lcd_spec);_lcd_spec.loader.exec_module(lcd)
# Include the unused side ear: x15.6 - R2.1 leaves 0.5 mm to B1's x13 rail.
LCD_ORIGIN=(15.6,25.0)
EARS=lcd.holes(LCD_ORIGIN)
ALL_EARS=lcd.holes(LCD_ORIGIN,all_six=True)
CLAMPS=[(x,y+(-7 if y<45 else 7)) for x,y in EARS]
SUPPORT_DEPTH=lcd.support_depth()
PCB_REAR_Z=-SUPPORT_DEPTH-lcd.DATA['pcb_thickness_mm']
PITCH=1.0  # Deliberately coarse PRINTED thread; not standard M5 hardware.
WINDOW=lcd.window(LCD_ORIGIN)
NAMES=['ControlPanel','DisplayThumbScrew','DisplayFitCoupon','ThreadFitA','ThreadFitB','ThreadFitC']

def load_builder():
    spec=importlib.util.spec_from_file_location('b1_builder',ROOT/'tools/build-bench-holder.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod

def thread(m,b,name,x,y,z,length,internal=True,allowance=.15):
    """Coarse 5 mm diameter/1 mm pitch trapezoidal thread, native helix."""
    s=m.sketch(b,name+'Flank',0)
    s.Placement=App.Placement(App.Vector(x,y,z),App.Rotation(App.Vector(1,0,0),90))
    if internal:
        pts=[(1.96,-.44),(2.5+allowance,-.16),(2.5+allowance,.16),(1.96,.44)]
    else:
        pts=[(1.9,-.37),(2.5,-.10),(2.5,.10),(1.9,.37)]
    m.polygon(s,pts);prev=b.Tip
    f=b.newObject('PartDesign::SubtractiveHelix' if internal else 'PartDesign::AdditiveHelix',name)
    f.Profile=s;f.ReferenceAxis=(s,['V_Axis']);f.Mode='pitch-height-angle'
    f.Pitch=PITCH;f.Height=length;f.LeftHanded=False;f.Reversed=False;f.Refine=True
    m.doc.recompute();prev.Visibility=False;s.Visibility=False
    assert f.Shape.isValid() and len(f.Shape.Solids)==1,(name,f.State)
    return f

def socket(m,b,name,centers,bottom=-14,top=0,allowance=.15):
    m.circles(b,name+'Boss',centers,4.8,top,top-bottom,reverse=True)
    # Blind core from rear; 3 mm solid panel remains untouched at z0..3.
    m.circles(b,name+'Core',centers,2.0+allowance,bottom,top-bottom,True,True)
    for i,(x,y) in enumerate(centers):thread(m,b,name+'Thread'+str(i),x,y,bottom,top-bottom,True,allowance)

def main():
    for path in (OUT,EV,WORK):path.mkdir(parents=True,exist_ok=True)
    assert not any(d.FileName and Path(d.FileName).resolve()==CAD.resolve() for d in App.listDocuments().values()),'Close B2 before rebuilding'
    src=ROOT/'mechanical/bench-holder/bench-holder-b1.FCStd'
    original_hash=hashlib.sha256(src.read_bytes()).hexdigest()
    live=[d for d in App.listDocuments().values() if d.FileName and Path(d.FileName).resolve()==src.resolve()]
    assert not live or not live[0].isTouched(),'Preserve unsaved B1 work'
    checkpoint=WORK/'b1-read-only-copy.FCStd';shutil.copyfile(src,checkpoint)
    doc=App.openDocument(str(checkpoint));doc.Label='B2 / L1 corrected LCD - 9.13 mm measured projection'
    mod=load_builder();m=mod.Builder(doc)
    p=doc.getObject('ControlPanel');original=p.Shape.copy();place=p.Placement
    # Roll back the native feature history at the unchanged keeper sockets.
    group=list(p.Group);idx=next(i for i,o in enumerate(group) if o.Name=='KeeperSockets')
    for o in reversed(group[idx+1:]):doc.removeObject(o.Name)
    # Remove original panel text profiles whose consuming pads were rolled back.
    # Keep profiles still used by the unchanged B1 insert trials.
    old_profiles=doc.getObject('LabelProfiles')
    for o in list(old_profiles.Group):
        if not any(parent!=old_profiles for parent in o.InList):doc.removeObject(o.Name)
    p.Tip=doc.getObject('KeeperSockets');doc.recompute()
    m.rectangle(p,'DisplayViewingWindow',WINDOW,3,3,True)
    # Support only the mounting ears, with no preload on glass or electronics.
    m.circles(p,'DisplayEarSeats',EARS,2.1,0,SUPPORT_DEPTH,reverse=True)
    m.circles(p,'DisplayEarLocators',EARS,.9,-SUPPORT_DEPTH,1.2,reverse=True)
    socket(m,p,'DisplayClamp',CLAMPS,bottom=-SUPPORT_DEPTH)
    # Engrave labels to allow front-face-down printing of integral rear posts.
    for name,text,x,y,size in [('Lcd','LCD',55,73,3),('Tone','TONE',120,66,3),
        ('Bypass','BYPASS',155,57,2.8),('PttTest','PTT TEST',190,63,2.8),
        ('PttLed','PTT',148,79,2.5),('BypassLed','BYPASS',172,79,2.5),
        ('Mic','MIC',120,1.6,2.8),('Radio','RADIO',165,1.6,2.8)]:
        prev=p.Tip
        s=Draft.makeShapeString(String=text,FontFile='C:/Windows/Fonts/arialbd.ttf',Size=size,Tracking=0)
        doc.recompute();bb=s.Shape.BoundBox;s.Placement.Base=App.Vector(x-(bb.XMin+bb.XMax)/2,y-bb.YMin,3)
        m.text_profiles.addObject(s)
        f=p.newObject('PartDesign::Pocket','Engraved'+name);f.Profile=s;f.Length=.4
        doc.recompute();prev.Visibility=False;s.Visibility=False
        assert f.Shape.isValid() and len(f.Shape.Solids)==1,name

    screw=m.body('DisplayThumbScrew')
    m.circles(screw,'ThumbHead',[(0,0)],8.5,0,2.4)
    m.circles(screw,'ThumbCore',[(0,0)],1.95,2.4,7)
    thread(m,screw,'ThumbCoarseThread',0,0,2.4,6.6,False)
    # Clip the start/end helix to exact head/shank extents with a native pocket.
    s=m.sketch(screw,'TrimThreadEnd',9.4);m.circle(s,0,0,3)
    m.feature(screw,'TrimThreadEnd',s,1,True,True)
    # Flat head down on the bed; grip its broad rim with fingers, no driver.

    # Independent actual-size display fixture, including window and all four ears.
    c=m.body('DisplayFitCoupon');m.rectangle(c,'DisplayCouponSkin',(15,12,80,68),0,3)
    m.rectangle(c,'CouponWindow',WINDOW,3,3,True)
    m.circles(c,'CouponEarSeats',EARS,2.1,0,SUPPORT_DEPTH,reverse=True)
    m.circles(c,'CouponEarLocators',EARS,.9,-SUPPORT_DEPTH,1.2,reverse=True)
    socket(m,c,'CouponClamp',CLAMPS,bottom=-SUPPORT_DEPTH)
    for letter,a in [('A',.10),('B',.15),('C',.20)]:
        c=m.body('ThreadFit'+letter)
        m.rectangle(c,'TrialFoot'+letter,(-7,-7,14,14),0,3)
        socket(m,c,'Trial'+letter,[(0,0)],-7,0,a)

    # Replace the old front-display block with dimensioned rear references.
    refs=doc.getObject('ReferenceEnvelopes')
    doc.removeObject('LcdBodyReference')
    def ref(name,shape):
        shape.Placement=place.multiply(shape.Placement)
        o=doc.addObject('Part::Feature',name);o.Shape=shape;refs.addObject(o)
        o.ViewObject.ShapeColor=(.15,.45,.32);return o
    pcb=Part.makeBox(80,40,1.6,App.Vector(*LCD_ORIGIN,PCB_REAR_Z))
    for x,y in ALL_EARS:
        pcb=pcb.fuse(Part.makeCylinder(2.1,1.6,App.Vector(x,y,PCB_REAR_Z)))
        pcb=pcb.cut(Part.makeCylinder(1.15,1.6,App.Vector(x,y,PCB_REAR_Z)))
    ref('RearDisplayPcbReference',pcb)
    bx,by,bw,bh=lcd.bezel(LCD_ORIGIN)
    bezel=Part.makeBox(bw,bh,lcd.DATA['measured_pcb_front_to_bezel_front_mm'],App.Vector(bx,by,-SUPPORT_DEPTH))
    ref('RearDisplayBezelReference',bezel)
    ref('DisplayRearElectronicsAllowance',Part.makeBox(70,25,2.1,App.Vector(LCD_ORIGIN[0]+5,31,PCB_REAR_Z-2.1)))
    # Plug plus initial wire bend allowance, routed inboard toward harness combs.
    plug=Part.makeBox(18,23,9,App.Vector(LCD_ORIGIN[0]+15,19,-SUPPORT_DEPTH))
    ref('DisplayPlugAndBendAllowance',plug)
    installed=[]
    for i,(x,y) in enumerate(CLAMPS,1):
        sh=screw.Shape.copy();sh.translate(App.Vector(x,y,PCB_REAR_Z-2.4))
        ref('InstalledPrintedClamp'+str(i),sh)
        installed.append('InstalledPrintedClamp'+str(i))
    for o in doc.Objects:
        if o.ViewObject:o.Visibility=False
    doc.getObject('ProductionParts').Visibility=True;p.Visibility=True;p.Tip.Visibility=True
    # Fit/test parts excluded from assembly view and exchange export.
    group=doc.addObject('App::DocumentObjectGroup','RearDisplayPrintParts')
    group.addObjects([doc.getObject(n) for n in NAMES[1:]])
    doc.recompute()
    checks={'revision':'B2','base_source_sha256':original_hash,'parts':[],
        'ear_centers_mm':EARS,'clamp_centers_mm':CLAMPS,'window_mm':WINDOW,'lcd_pcb_origin_mm':LCD_ORIGIN,
        'support_depth_mm':SUPPORT_DEPTH,'lcd_interface_revision':'L1','all_six_ear_centers_mm':ALL_EARS,'thread':'custom 5 mm x 1 mm right hand; not M5',
        'lcd_definition_sha256':hashlib.sha256(lcd.DEFINITION.read_bytes()).hexdigest(),
        'source_drawing':'https://files.seeedstudio.com/wiki/Grove_LCD_RGB_Backlight/res/JHD1313%20FP-RGB-1%201.4.pdf#page=23',
        'axial_envelope':{'measured_front_projection_mm':lcd.DATA['measured_pcb_front_to_bezel_front_mm'],'bezel_gap_mm':lcd.DATA['bezel_to_panel_rear_gap_mm']},
        'physical_acceptance':'not run'}
    checks['base_difference_mm3']=doc.getObject('Base').Shape.cut((live[0] if live else doc).getObject('Base').Shape).Volume
    assert checks['base_difference_mm3']<1e-7
    # Outside the display region and shallow label band, original solid is identical.
    old=original.copy();old.Placement=place.inverse().multiply(old.Placement)
    new=p.Shape.copy();new.Placement=place.inverse().multiply(new.Placement)
    outside=Part.makeBox(110,90,3,App.Vector(100,0,0))
    # Text engraving is intentionally different only in the top .4 mm.
    protected=Part.makeBox(210,90,2.59)
    protected=protected.cut(Part.makeBox(88,70,3,App.Vector(10,12,0)))
    a=old.common(protected);b=new.common(protected)
    checks['protected_interface_difference_mm3']=a.cut(b).Volume+b.cut(a).Volume
    assert checks['protected_interface_difference_mm3']<1e-5
    checks['reference_intersections_mm3']={}
    for name in ['RearDisplayPcbReference','RearDisplayBezelReference','DisplayRearElectronicsAllowance','DisplayPlugAndBendAllowance']:
        r=doc.getObject(name)
        for target in ['Base','ControlPanel']:
            v=r.Shape.common(doc.getObject(target).Shape).Volume
            checks['reference_intersections_mm3'][name+'/'+target]=v
            assert v<1e-5,(name,target,v)
    checks['installed_screw_intersections_mm3']=[]
    for name in installed:
        sh=doc.getObject(name).Shape
        values={n:sh.common(doc.getObject(n).Shape).Volume for n in ['ControlPanel','RearDisplayPcbReference']}
        assert max(values.values())<1e-5,(name,values)
        checks['installed_screw_intersections_mm3'].append(values)
    for name in NAMES:
        o=doc.getObject(name);sh=o.Shape.copy()
        sh.Placement=o.Placement.inverse().multiply(sh.Placement)
        # Front face down: body-local Z3 becomes bed Z0; rear posts grow upward.
        if name!='DisplayThumbScrew':sh.rotate(App.Vector(),App.Vector(1,0,0),180)
        bb=sh.BoundBox;sh.translate(App.Vector(-bb.XMin,-bb.YMin,-bb.ZMin))
        mesh=MeshPart.meshFromShape(Shape=sh,LinearDeflection=.015,AngularDeflection=.08,Relative=False)
        assert sh.isValid() and len(sh.Solids)==1 and mesh.isSolid(),name
        bb=mesh.BoundBox
        assert abs(bb.ZMin)<1e-5 and max(bb.XLength,bb.YLength,bb.ZLength)<246
        path=OUT/(name.lower()+'.stl');mesh.write(str(path))
        checks['parts'].append({'name':name,'bounds_mm':[bb.XLength,bb.YLength,bb.ZLength],
            'mesh_closed':mesh.isSolid(),'solids':len(sh.Solids),'triangles':mesh.CountFacets,
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    Part.export([doc.getObject('Base'),p,doc.getObject('LedKeeper')]+[doc.getObject(n) for n in installed],str(OUT/'bench-panel-b2-assembly.step'))
    doc.recompute();doc.saveAs(str(CAD))
    checks['source_sha256']=hashlib.sha256(CAD.read_bytes()).hexdigest()
    checks['b1_unchanged']=hashlib.sha256(src.read_bytes()).hexdigest()==original_hash
    assert checks['b1_unchanged']
    (EV/'cad-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    if App.GuiUp:
        import FreeCADGui as Gui
        refs.Visibility=True
        for o in refs.Group:o.Visibility=False
        for n in ['Base','LedKeeper','PcbSpacer']:doc.getObject(n).Visibility=False
        for n in ['RearDisplayPcbReference','RearDisplayBezelReference']+installed:doc.getObject(n).Visibility=True
        img=ROOT/'docs/images/bench-panel-b2';img.mkdir(parents=True,exist_ok=True)
        v=Gui.getDocument(doc.Name).activeView()
        v.setCameraOrientation(place.Rotation.Q);v.fitAll();v.saveImage(str(img/'native-front.png'),1600,800,'White')
        v.setCameraOrientation(place.Rotation.multiply(App.Rotation(App.Vector(1,0,0),180)).Q)
        v.fitAll();v.saveImage(str(img/'native-rear.png'),1600,800,'White')
        doc.save()
        checks['source_sha256']=hashlib.sha256(CAD.read_bytes()).hexdigest()
    checks['generator_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (EV/'cad-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    return checks

if __name__=='__main__':
    import traceback
    try: main()
    except Exception:
        (WORK/'build-error.txt').write_text(traceback.format_exc())
        raise

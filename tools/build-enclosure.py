"""Native FreeCAD P1 enclosure. Execute build(root), then export(root), inside FreeCAD.

All dimensions are mm. Sketch/Pad/Pocket history and spreadsheet parameters are
saved in the FCStd; this script is a reproducible authoring tool, not a dependency.
"""
from pathlib import Path
import math, json, hashlib
import FreeCAD as App
import FreeCADGui as Gui
import Part, Sketcher, Draft, MeshPart, Mesh

PRODUCTION = ['Base','Cover','Fascia','DisplayInsert','LedKeeper','PcbWasher','WireKeeper','EncoderKnob','KnobAccentRing']
COUPONS = ['MountCoupon','ControlCoupon','GxCoupon','ShaftCoupon']

class Builder:
    def __init__(self, doc):
        self.doc=doc
        self.assembly=doc.addObject('App::Part','EnclosureAssembly')
        self.params=doc.addObject('Spreadsheet::Sheet','Dimensions')
        self.values=dict(CaseWidth=200,CaseDepth=195,CaseHeight=68,Wall=3,Floor=3,CoverThickness=3,
            PcbStand=6.35,PcbThickness=1.5,Fit=0.3,ScrewBore=3.4,NutAF=5.7,NutDepth=2.6,
            GxBore=16.2,GxNutAF=20.5,GxLand=2,EncoderBore=7.2,ToggleBore=6.5,LedBore=5.2,
            LedFlange=7,LcdWindowWidth=72,LcdWindowHeight=25,LcdHoleWidth=75,LcdHoleHeight=31,
            ShaftBore=6.2,KnobRadius=15,RearPlugLength=45,CableBendAllowance=30)
        for row,(k,v) in enumerate(self.values.items(),1):
            self.params.set('A'+str(row),k);self.params.set('B'+str(row),str(v)+' mm');self.params.setAlias('B'+str(row),k)
        self.params.setColumnWidth('A',200)
        self.params.set('D1','Design revision');self.params.set('E1','P1')
    def val(self,x):
        if not isinstance(x,str):return x
        for k,v in sorted(self.values.items(),key=lambda kv:-len(kv[0])):x=x.replace('Dimensions.'+k,str(v))
        return eval(x,{'__builtins__':{},'sqrt':math.sqrt})
    def body(self,name):
        b=self.doc.addObject('PartDesign::Body',name);self.assembly.addObject(b);return b
    def sketch(self,b,name,plane='xy',offset=0):
        s=self.doc.addObject('Sketcher::SketchObject',name+'Sketch');b.addObject(s)
        if plane=='xy':pos=App.Vector(0,0,self.val(offset));rot=App.Rotation()
        elif plane=='xz':pos=App.Vector(0,self.val(offset),0);rot=App.Rotation(App.Vector(1,0,0),90)
        else:
            pos=App.Vector(self.val(offset),0,0);rot=App.Rotation(App.Vector(0,1,0),App.Vector(0,0,1),App.Vector(1,0,0),'ZXY')
        s.Placement=App.Placement(pos,rot)
        if isinstance(offset,str):s.setExpression('Placement.Base.'+{'xy':'z','xz':'y','yz':'x'}[plane],offset)
        return s
    def dim(self,s,c,name,v):
        i=s.addConstraint(c);s.renameConstraint(i,name)
        if isinstance(v,str):s.setExpression('Constraints.'+name,v)
    def point(self,s,g,p,x,y,prefix):
        for axis,v in [('X',x),('Y',y)]:
            n=self.val(v)
            if abs(n)<1e-9:s.addConstraint(Sketcher.Constraint('PointOnObject',g,p,-2 if axis=='X' else -1))
            else:self.dim(s,Sketcher.Constraint('Distance'+axis,g,p,n),prefix+axis,v)
    def rect(self,s,x,y,w,h):
        vs=[(self.val(x),self.val(y)),(self.val(x)+self.val(w),self.val(y)),(self.val(x)+self.val(w),self.val(y)+self.val(h)),(self.val(x),self.val(y)+self.val(h))]
        start=s.GeometryCount
        for i in range(4):s.addGeometry(Part.LineSegment(App.Vector(*vs[i],0),App.Vector(*vs[(i+1)%4],0)),False)
        for i in range(4):
            s.addConstraint(Sketcher.Constraint('Coincident',start+i,2,start+(i+1)%4,1))
            s.addConstraint(Sketcher.Constraint('Horizontal' if i%2==0 else 'Vertical',start+i))
        self.point(s,start,1,x,y,'Rect'+str(start))
        self.dim(s,Sketcher.Constraint('Distance',start,self.val(w)),'Width'+str(start),w)
        self.dim(s,Sketcher.Constraint('Distance',start+1,self.val(h)),'Height'+str(start),h)
    def circle(self,s,x,y,r):
        i=s.addGeometry(Part.Circle(App.Vector(self.val(x),self.val(y),0),App.Vector(0,0,1),self.val(r)),False)
        self.point(s,i,3,x,y,'Circle'+str(i));self.dim(s,Sketcher.Constraint('Radius',i,self.val(r)),'Radius'+str(i),r)
    def poly(self,s,pts):
        n=s.GeometryCount
        for i,p in enumerate(pts):
            q=pts[(i+1)%len(pts)];s.addGeometry(Part.LineSegment(App.Vector(*p,0),App.Vector(*q,0)),False)
        for i,p in enumerate(pts):
            s.addConstraint(Sketcher.Constraint('Coincident',n+i,2,n+(i+1)%len(pts),1));self.point(s,n+i,1,*p,'Vertex'+str(n+i))
    def hex(self,s,x,y,af):
        r=self.val(af)/math.sqrt(3);self.poly(s,[(x+r*math.cos(i*math.pi/3),y+r*math.sin(i*math.pi/3)) for i in range(6)])
    def rounded(self,s,x,y,w,h,r):
        # Independent fully constrained corner arcs, joined with coincident edges.
        a,b,c,d,e=map(self.val,(x,y,w,h,r));centers=[(a+c-e,b+e),(a+c-e,b+d-e),(a+e,b+d-e),(a+e,b+e)]
        arcs=[]
        for k,(cx,cy) in enumerate(centers):
            ang=(-.5+k*.5)*math.pi
            i=s.addGeometry(Part.ArcOfCircle(Part.Circle(App.Vector(cx,cy,0),App.Vector(0,0,1),e),ang,ang+math.pi/2),False);arcs.append(i)
            self.point(s,i,3,cx,cy,'Corner'+str(i));self.dim(s,Sketcher.Constraint('Radius',i,e),'CornerRadius'+str(i),r)
            s.addConstraint(Sketcher.Constraint('Vertical' if k%2==0 else 'Horizontal',i,1,i,3))
            s.addConstraint(Sketcher.Constraint('Horizontal' if k%2==0 else 'Vertical',i,2,i,3))
        for k,i in enumerate(arcs):
            j=arcs[(k+1)%4];p=s.Geometry[i].EndPoint;q=s.Geometry[j].StartPoint
            line=s.addGeometry(Part.LineSegment(p,q),False)
            s.addConstraint(Sketcher.Constraint('Coincident',line,1,i,2));s.addConstraint(Sketcher.Constraint('Coincident',line,2,j,1))
    def feature(self,b,name,s,length,cut=False,reverse=False):
        prev=b.Tip
        f=b.newObject('PartDesign::Pocket' if cut else 'PartDesign::Pad',name);f.Profile=s;f.Length=self.val(length);f.Reversed=reverse;f.Refine=True
        if isinstance(length,str):f.setExpression('Length',length)
        self.doc.recompute()
        if f.Shape.isNull() or not f.Shape.isValid() or len(f.Shape.Solids)!=1:raise RuntimeError(name+': invalid solid; '+str(f.State))
        s.Visibility=False
        if prev:prev.Visibility=False
        return f
    def rect_feature(self,b,name,x,y,w,h,offset,length,plane='xy',cut=False,reverse=False):
        s=self.sketch(b,name,plane,offset);self.rect(s,x,y,w,h);return self.feature(b,name,s,length,cut,reverse)
    def circles(self,b,name,centres,r,offset,length,plane='xy',cut=False,reverse=False):
        s=self.sketch(b,name,plane,offset)
        for x,y in centres:self.circle(s,x,y,r)
        return self.feature(b,name,s,length,cut,reverse)
    def hexes(self,b,name,centres,af,offset,length,plane='xy',reverse=False):
        s=self.sketch(b,name,plane,offset)
        for x,y in centres:self.hex(s,x,y,af)
        return self.feature(b,name,s,length,True,reverse)
    def rounded_feature(self,b,name,x,y,w,h,r,offset,length,plane='xy',cut=False,reverse=False):
        s=self.sketch(b,name,plane,offset);self.rounded(s,x,y,w,h,r);return self.feature(b,name,s,length,cut,reverse)
    def text(self,b,name,text,x,z,y,size,depth,stencil=True,rear=False):
        font='C:/Windows/Fonts/STENCIL.TTF' if stencil else 'C:/Windows/Fonts/arialbd.ttf'
        t=Draft.makeShapeString(String=text,FontFile=font,Size=size,Tracking=0);t.Label=name+' lettering';self.doc.recompute()
        box=t.Shape.BoundBox;cx=(box.XMin+box.XMax)/2
        if rear:
            rot=App.Rotation(App.Vector(-1,0,0),App.Vector(0,0,1),App.Vector(0,1,0),'ZXY');pos=App.Vector(x+cx,y,z-box.YMin)
        else:rot=App.Rotation(App.Vector(1,0,0),90);pos=App.Vector(x-cx,y,z-box.YMin)
        t.Placement=App.Placement(pos,rot);self.doc.recompute();return self.feature(b,name,t,depth,True)
    def link(self,b,name,delta):
        l=self.doc.addObject('App::Link',name);self.assembly.addObject(l);l.LinkedObject=b;l.LinkPlacement=App.Placement(App.Vector(*delta),App.Rotation());return l


def build(root):
    root=Path(root)
    if any(d.Name=='CTCSS_Enclosure_P1' or (d.FileName and Path(d.FileName).resolve()==(root/'mechanical/enclosure/icom-ctcss-enclosure.FCStd').resolve()) for d in App.listDocuments().values()):raise RuntimeError('Save edits and close CTCSS_Enclosure_P1 before rebuilding.')
    doc=App.newDocument('CTCSS_Enclosure_P1');doc.Label='Icom IC-229H companion enclosure - P1'
    doc.Comment='P1 - IC-229H companion enclosure; front fascia, printed supports and three-plate build.'
    m=Builder(doc)
    base=m.body('Base')
    m.rounded_feature(base,'Floor',0,0,'Dimensions.CaseWidth','Dimensions.CaseDepth',4,0,'Dimensions.Floor')
    s=m.sketch(base,'Walls',offset='Dimensions.Floor');m.rounded(s,0,0,200,195,4);m.rect(s,3,3,194,189);m.feature(base,'Walls',s,62)
    m.rect_feature(base,'FrontPanelOpening',3,3,194,62,0,4,'xz',True)
    holes=[(31,61),(169,61),(169,149),(31,149)]
    wire=[(60,42),(80,42),(135,42),(155,42)]
    m.circles(base,'PcbSupports',holes,3.75,3,'Dimensions.PcbStand')
    m.circles(base,'HarnessSupports',wire,3.8,3,6)
    # Native root fillets relieve screw preload at the four PCB support roots.
    prev=base.Tip;edges=[]
    for i,e in enumerate(prev.Shape.Edges,1):
        if hasattr(e.Curve,'Radius') and abs(e.Curve.Radius-3.75)<1e-5 and abs(e.BoundBox.ZMin-3)<1e-5 and e.BoundBox.ZLength<1e-5:edges.append('Edge'+str(i))
    f=base.newObject('PartDesign::Fillet','PcbSupportRootFillets');f.Base=(prev,edges);f.Radius=1;doc.recompute()
    if f.Shape.isNull() or not f.Shape.isValid():raise RuntimeError('Root fillet failed')
    prev.Visibility=False
    m.circles(base,'PcbScrewHoles',holes,'Dimensions.ScrewBore/2',9.35,6.35,cut=True)
    m.circles(base,'HarnessScrewHoles',wire,'Dimensions.ScrewBore/2',9,6,cut=True)
    m.hexes(base,'SupportNutSeats',holes+wire,'Dimensions.NutAF',6.8,'Dimensions.NutDepth')
    s=m.sketch(base,'SupportNutEntries',offset=6.8)
    for x,y in holes+wire:m.rect(s,x-5,y-2.85,5,5.7)
    m.feature(base,'SupportNutEntries',s,2.6,True)
    fastening=[(12,9),(188,9),(7,45),(193,45)]
    m.circles(base,'UndersideFastenerBores',fastening,1.7,3,3,cut=True)
    m.circles(base,'UndersideHeadSeats',fastening,3.1,0,1,cut=True,reverse=True)
    m.circles(base,'RadioNutCradle',[(40,49)],13,195,7,'xz')
    s=m.sketch(base,'RadioCradleGusset','yz',27);m.poly(s,[(188,36),(192.2,31.8),(192.2,38)]);m.feature(base,'RadioCradleGusset',s,26)
    m.hexes(base,'RadioNutSeat',[(40,49)],'Dimensions.GxNutAF',188,5,'xz')
    m.circles(base,'RadioBore',[(40,49)],'Dimensions.GxBore/2',195,8,'xz',True,True)
    s=m.sketch(base,'RadioBoreRoof','xz',195);m.poly(s,[(34,54),(40,60.456),(46,54)]);m.feature(base,'RadioBoreRoof',s,8,True,True)
    m.circles(base,'RearCoverScrewHoles',[(12,59),(188,59)],1.7,195,5,'xz',True,True)
    m.text(base,'RadioLegend','RADIO',40,30,195,3.5,.65,False,True)

    yield 'Base complete'
    cover=m.body('Cover')
    m.rounded_feature(cover,'CoverSkin',0,0,200,195,4,65,3)
    s=m.sketch(cover,'LocatingRails',offset=65)
    for r in [(3.3,60,1.8,112),(194.9,60,1.8,112),(25,189.9,150,1.8)]:m.rect(s,*r)
    m.feature(cover,'LocatingRails',s,2,reverse=True)
    m.circles(cover,'FrontAttachmentColumns',[(7,45),(193,45)],3.75,65,62,reverse=True)
    m.circles(cover,'FrontColumnBores',[(7,45),(193,45)],1.7,3,10,cut=True,reverse=True)
    m.hexes(cover,'FrontColumnNutSeats',[(7,45),(193,45)],5.7,6.8,2.6)
    s=m.sketch(cover,'FrontColumnNutEntries',offset=6.8);m.rect(s,7,42.15,5,5.7);m.rect(s,188,42.15,5,5.7);m.feature(cover,'FrontColumnNutEntries',s,2.6,True)
    s=m.sketch(cover,'RearAttachmentTabs',offset=65);m.rect(s,6,184,12,8);m.rect(s,182,184,12,8);m.feature(cover,'RearAttachmentTabs',s,12,reverse=True)
    m.circles(cover,'RearTabScrewHoles',[(12,59),(188,59)],1.7,192,9,'xz',True,True)
    m.hexes(cover,'RearTabNutSeats',[(12,59),(188,59)],5.7,184,4.6,'xz')

    yield 'Cover complete'
    fascia=m.body('Fascia')
    m.rounded_feature(fascia,'FasciaPanel',3,3,194,62,4,0,4,'xz',reverse=True)
    s=m.sketch(fascia,'BottomAttachmentEars','xy',3);m.rect(s,7,3.8,10,9.2);m.rect(s,183,3.8,10,9.2);m.feature(fascia,'BottomAttachmentEars',s,6)
    m.circles(fascia,'BottomEarBores',[(12,9),(188,9)],1.7,3,7,cut=True,reverse=True)
    m.hexes(fascia,'BottomEarNutSeats',[(12,9),(188,9)],5.7,6.8,2.6)
    s=m.sketch(fascia,'BottomEarNutEntries',offset=6.8);m.rect(s,9.15,9,5.7,5);m.rect(s,185.15,9,5.7,5);m.feature(fascia,'BottomEarNutEntries',s,2.6,True)
    m.circles(fascia,'MicrophoneNutCradle',[(181,23)],13,4,3,'xz',reverse=True)
    m.hexes(fascia,'MicrophoneNutSeat',[(181,23)],20.5,7,5,'xz',True)
    m.circles(fascia,'MicrophoneBore',[(181,23)],8.1,0,8,'xz',True)
    m.circles(fascia,'EncoderBore',[(24,36)],'Dimensions.EncoderBore/2',0,4,'xz',True)
    m.circles(fascia,'ToggleBore',[(159,39)],'Dimensions.ToggleBore/2',0,4,'xz',True)
    m.circles(fascia,'ControlMountingLands',[(24,36),(159,39)],8,4,2.5,'xz',True,True)
    m.circles(fascia,'LedLensBores',[(156,56),(181,56)],2.6,0,4,'xz',True)
    m.circles(fascia,'LedFlangeSeats',[(156,56),(181,56)],3.5,4,1.6,'xz',True,True)
    m.rect_feature(fascia,'LedKeeperKey',163.5,51,10,8,4,6,'xz',reverse=True)
    m.circles(fascia,'LedKeeperScrewBore',[(168.5,55)],1.7,10,8,'xz',True,True)
    m.hexes(fascia,'LedKeeperNutSeat',[(168.5,55)],5.7,6.4,2.6,'xz')
    m.rect_feature(fascia,'LedKeeperNutEntry',168.5,52.15,7,5.7,6.4,2.6,'xz',True)
    m.circles(fascia,'DisplayMountingBores',[(42,36),(142,36)],1.7,0,4,'xz',True)
    m.hexes(fascia,'DisplayMountingNutSeats',[(42,36),(142,36)],5.7,3.4,2.6,'xz',True)
    s=m.sketch(fascia,'DisplayNutLoading','xz',3.4);m.rect(s,42,33.15,4,5.7);m.rect(s,138,33.15,4,5.7);m.feature(fascia,'DisplayNutLoading',s,2.6,True,True)
    m.rounded_feature(fascia,'DisplayRecess',44.7,7.7,94.6,54.6,2.3,0,4,'xz',True)
    for name,r in [('LegendSpineRecess',(135.7,25.2,15.6,40)),('LedLegendRecess',(144.7,59.7,48.6,5.6)),('PlLegendRecess',(147.7,46.9,18.6,5.4)),('BypLegendRecess',(147.7,25.2,19.6,5.4))]:m.rect_feature(fascia,name,*r,0,4,'xz',True)
    m.text(fascia,'MicrophoneLegend','MIC',181,5,0,3.5,.65,False)

    s=m.sketch(fascia,'EncoderBodyGuides','xz',3.8);m.rect(s,11.7,25.7,2,20.6);m.rect(s,34.3,25.7,2,20.6);m.feature(fascia,'EncoderBodyGuides',s,8.2,reverse=True)
    yield 'Fascia complete'
    insert=m.body('DisplayInsert')
    m.rounded_feature(insert,'DisplaySurround',45,8,94,54,2,1.2,2.8,'xz',reverse=True)
    for name,r in [('LegendSpine',(136,25.5,15,39.3)),('LedLegendWing',(145,60,48,4.8)),('PlLegendWing',(148,47.2,18,4.8)),('BypLegendWing',(148,25.5,19,4.8))]:m.rect_feature(insert,name,*r,1.2,2.8,'xz',reverse=True)
    m.rect_feature(insert,'LcdWindow',56,26.5,'Dimensions.LcdWindowWidth','Dimensions.LcdWindowHeight',1.2,3,'xz',True)
    s=m.sketch(insert,'MountingRamps',offset=31);m.poly(s,[(45,3.8),(46,3.8),(46,11),(38,11)]);m.poly(s,[(138,3.8),(139,3.8),(146,11),(138,11)]);m.feature(insert,'MountingRamps',s,10)
    s=m.sketch(insert,'SurroundAttachmentEars','xz',11);m.rect(s,38,31,8,10);m.rect(s,138,31,8,10);m.feature(insert,'SurroundAttachmentEars',s,2,reverse=True)
    m.circles(insert,'SurroundMountingBores',[(42,36),(142,36)],1.7,13,12,'xz',True,True)
    lcdholes=[(54.5,23.5),(129.5,23.5),(54.5,54.5),(129.5,54.5)]
    m.circles(insert,'LcdSupportPosts',lcdholes,3.5,4,6.2,'xz',reverse=True)
    m.circles(insert,'LcdScrewBores',lcdholes,1.4,10.2,6.2,'xz',True,True)
    m.hexes(insert,'LcdNutSeats',lcdholes,5.2,6,2.2,'xz')
    s=m.sketch(insert,'LcdNutLoading','xz',6)
    for x,z in lcdholes:m.rect(s,x-4,z-2.6,4,5.2)
    m.feature(insert,'LcdNutLoading',s,2.2,True)
    yield 'Display support geometry complete'
    for name,text,x,z,size in [('CtcssLegend','CTCSS',92,11,4.5),('PttLegend','PTT',156,60.1,3.8),('BypassLedLegend','BYPASS',181,60.1,3.8),('PlLegend','PL',159,47.3,3.8),('BypLegend','BYP',159,25.6,3.8)]:
        m.text(insert,name,text,x,z,1.2,size,4)
        yield name+' complete'

    yield 'Display insert complete'
    keeper=m.body('LedKeeper');m.rounded_feature(keeper,'LedKeeperBridge',147,49,44,12,1.2,9,3,'xz',reverse=True)
    m.circles(keeper,'LedRetainingStems',[(156,56),(181,56)],3.3,9,4.7,'xz')
    m.circles(keeper,'LeadPassages',[(156,56),(181,56)],2.25,12,8,'xz',True,True)
    m.circles(keeper,'KeeperMountingBore',[(168.5,55)],1.7,12,8,'xz',True,True)
    m.rect_feature(keeper,'KeyedKeeperRecess',163,50.5,11,9,9,1,'xz',True)
    washer=m.body('PcbWasher');s=m.sketch(washer,'WasherRing',offset=10.85);m.circle(s,31,61,3.9);m.circle(s,31,61,1.7);m.feature(washer,'WasherRing',s,1)
    for name,delta in [('PcbWasherFrontRight',(138,0,0)),('PcbWasherRearLeft',(0,88,0)),('PcbWasherRearRight',(138,88,0))]:m.link(washer,name,delta)
    clamp=m.body('WireKeeper');m.rounded_feature(clamp,'HarnessBridge',55,38,30,8,1,9,3);m.circles(clamp,'HarnessBridgeBores',[(60,42),(80,42)],1.7,12,3,cut=True);m.link(clamp,'WireKeeperRight',(75,0,0))

    yield 'Small retainers complete'
    knob=m.body('EncoderKnob');m.circles(knob,'KnobCore',[(24,36)],15,-18,9.5,'xz',reverse=True)
    s=m.sketch(knob,'GripRibs','xz',-17.5)
    for i in range(24):a=i*math.pi/12;m.circle(s,24+14.8*math.cos(a),36+14.8*math.sin(a),.65)
    m.feature(knob,'GripRibs',s,6.5,reverse=True)
    s=m.sketch(knob,'AccentGroove','xz',-11);m.circle(s,24,36,17);m.circle(s,24,36,13.5);m.feature(knob,'AccentGroove',s,2,True)
    m.circles(knob,'ShaftCollar',[(24,36)],8,-8.5,6,'xz',reverse=True)
    m.rect_feature(knob,'ClampEars',28,28,7,16,-8.5,6,'xz',reverse=True)
    m.circles(knob,'ShaftSocket',[(24,36)],'Dimensions.ShaftBore/2',-2.5,11.5,'xz',True,True)
    m.rect_feature(knob,'ClampSplit',24,35.5,12,1,-8.5,6,'xz',True)
    m.circles(knob,'ClampBoltBore',[(31.5,-5.5)],1.7,44,16,cut=True)
    m.hexes(knob,'ClampNutSeat',[(31.5,-5.5)],5.7,28,3.6,reverse=True)
    ring=m.body('KnobAccentRing');s=m.sketch(ring,'AccentBand','xz',-10.8);m.circle(s,24,36,15.6);m.circle(s,24,36,13.65);m.feature(ring,'AccentBand',s,1.6,reverse=True)
    m.rect_feature(ring,'RingExpansionGap',23.2,19,1.6,5,-11,3,'xz',True)

    yield 'Knob complete'
    b=m.body('MountCoupon');m.rounded_feature(b,'MountCouponFloor',0,0,30,22,2,0,3);m.circles(b,'CouponPost',[(15,11)],3.75,3,6.35);m.circles(b,'CouponScrewBore',[(15,11)],1.7,9.35,6.35,cut=True);m.hexes(b,'CouponNutSeat',[(15,11)],5.7,6.8,2.6);m.rect_feature(b,'CouponNutEntry',10,8.15,5,5.7,6.8,2.6,cut=True)
    b=m.body('ControlCoupon');m.rounded_feature(b,'ControlCouponPlate',0,0,72,30,2,0,4)
    for name,x,r in [('Encoder',14,3.6),('Toggle',38,3.25),('Led',60,2.6)]:m.circles(b,'Coupon'+name+'Bore',[(x,15)],r,4,4,cut=True)
    m.circles(b,'CouponControlLands',[(14,15),(38,15)],8,4,2.5,cut=True);m.circles(b,'CouponLedFlange',[(60,15)],3.5,4,1.6,cut=True)
    b=m.body('GxCoupon');m.rounded_feature(b,'GxCouponPlate',0,0,34,34,2,0,7);m.hexes(b,'CouponGxNutSeat',[(17,17)],20.5,7,5);m.circles(b,'CouponGxBore',[(17,17)],8.1,7,7,cut=True)
    b=m.body('ShaftCoupon');m.rounded_feature(b,'ShaftCouponPlate',0,0,44,20,2,0,6)
    for x,r in [(9,3),(22,3.1),(35,3.2)]:m.circles(b,'ShaftGauge'+str(x),[(x,10)],r,6,6,cut=True)
    # Coupons are a separate group and offset in the assembly display only.
    cg=doc.addObject('App::DocumentObjectGroup','FitCoupons')
    for i,name in enumerate(COUPONS):
        b=doc.getObject(name);m.assembly.removeObject(b);cg.addObject(b);b.Placement.Base=App.Vector(i*80,-140,0)

    yield 'Coupons complete'
    refs=doc.addObject('App::DocumentObjectGroup','InstalledHardware')
    def box(name,pos,size,color=(.18,.42,.25),visible=False):
        o=doc.addObject('Part::Box',name);refs.addObject(o);o.Length,o.Width,o.Height=size;o.Placement.Base=App.Vector(*pos);o.ViewObject.ShapeColor=color;o.Visibility=visible;return o
    def cylinder(name,x,y,z,r,h,axis=(0,0,1),visible=False,color=(.5,.5,.5)):
        o=doc.addObject('Part::Cylinder',name);refs.addObject(o);o.Radius=r;o.Height=h;o.Placement=App.Placement(App.Vector(x,y,z),App.Rotation(App.Vector(0,0,1),App.Vector(*axis)));o.Visibility=visible;o.ViewObject.ShapeColor=color;return o
    box('CarrierPcb',(25,55,9.35),(150,100,1.5));box('CarrierComponentEnvelope',(25,55,10.85),(150,100,25))
    box('LcdEnvelope',(51,5.2,20),(82,25,38));box('EncoderEnvelope',(14,4,26),(20,25,20));box('ToggleEnvelope',(151.5,4,31.5),(15,25,15))
    box('SocketedProMicro',(110.88,76.5,19.35),(18.24,37,1.6));box('VisibleLcdGlass',(57,5.2,27.5),(70,.8,23),(.36,.48,.23),True)
    for label,x,y,z,direction in [('Microphone',181,2,23,(0,1,0)),('Radio',40,193,49,(0,-1,0))]:cylinder(label+'RearEnvelope',x,y,z,12,30,direction)
    cylinder('FrontMatingPlug',181,0,23,12,45,(0,-1,0));cylinder('FrontCableBend',181,-45,23,12,30,(0,-1,0));cylinder('RearMatingPlug',40,195,49,12,45,(0,1,0));cylinder('RearCableBend',40,240,49,12,30,(0,1,0))
    cylinder('MicShell',181,-3,23,10,3,(0,1,0),True)
    for name,x,color in [('PttLens',156,(.9,.05,.02)),('BypassLens',181,(.05,.8,.1))]:cylinder(name,x,-1.5,56,2.5,4,(0,1,0),True,color)
    cylinder('BypassLever',159,-9,39,1.5,10,(0,1,0),True)
    for i,(x,y) in enumerate([(15,24),(185,24),(15,180),(185,180)]):cylinder('CompliantFoot'+str(i+1),x,y,-3,6,3,visible=True,color=(.08,.08,.08))
    doc.recompute()
    for o in doc.Objects:
        if o.TypeId=='PartDesign::Body':
            for c in o.Group:
                if hasattr(c,'ViewObject'):c.Visibility=False
            o.Visibility=o.Name in PRODUCTION;o.Tip.Visibility=True
            color=(.13,.14,.15)
            if o.Name=='DisplayInsert':color=(.55,.54,.48)
            if o.Name=='KnobAccentRing':color=(.95,.39,.08)
            o.ViewObject.ShapeColor=color;o.Tip.ViewObject.ShapeColor=color
    for o in doc.Objects:
        if o.TypeId=='PartDesign::Body' and o.Name in COUPONS:o.Visibility=False
    doc.recompute();Gui.activeDocument().activeView().viewAxonometric();Gui.activeDocument().activeView().fitAll()
    result=check(doc,root)
    if result['interferences']:raise RuntimeError('Printed parts interfere: '+str(result['interferences']))
    doc.recompute();doc.saveAs(str(root/'mechanical/enclosure/icom-ctcss-enclosure.FCStd'))
    yield result


def check(doc,root):
    bodies=[doc.getObject(n) for n in PRODUCTION]+[o for o in doc.Objects if o.TypeId=='App::Link']
    overlaps=[]
    for i,a in enumerate(bodies):
        for b in bodies[i+1:]:
            if not a.Shape.BoundBox.intersect(b.Shape.BoundBox):continue
            v=a.Shape.common(b.Shape).Volume
            if v>1e-5:overlaps.append([a.Name,b.Name,round(v,5)])
    report={'revision':'P1','units':'mm','case_envelope_mm':[200,195,68],
        'pcb_envelope_mm':[150,100,1.5],'pcb_hole_centres_xy_mm':[[31,61],[169,61],[169,149],[31,149]],
        'pcb_local_to_case':'X=175-boardY; Y=55+boardX; Z=9.35+boardZ',
        'native_feature_errors':[o.Name for o in doc.Objects if 'Invalid' in o.State],
        'unconstrained_sketches':[o.Name for o in doc.Objects if o.TypeId=='Sketcher::SketchObject' and not o.FullyConstrained],
        'production_parts':[{ 'name':b.Name,'valid':b.Shape.isValid(),'solids':len(b.Shape.Solids),'volume_mm3':b.Shape.Volume} for b in bodies],
        'clamp_socket_head_overlap_mm3':Part.makeCylinder(2.75,3,App.Vector(31.5,-5.5,44)).common(doc.EncoderKnob.Shape).Volume,
        'interferences':overlaps,'carrier_base_overlap_mm3':doc.Base.Shape.common(doc.CarrierPcb.Shape).Volume,
        'carrier_allocation_clearances_mm':{n:doc.CarrierComponentEnvelope.Shape.distToShape(doc.getObject(n).Shape)[0] for n in ['LcdEnvelope','EncoderEnvelope','ToggleEnvelope','MicrophoneRearEnvelope','RadioRearEnvelope']}}
    dest=Path(root)/'docs/verification/enclosure-p1';dest.mkdir(parents=True,exist_ok=True);(dest/'cad-checks.json').write_text(json.dumps(report,indent=2))
    return report


def export(root, names=None):
    root=Path(root);doc=next((d for d in App.listDocuments().values() if d.getObject('Dimensions') and d.getObject('DisplayInsert')),None)
    if doc is None:raise RuntimeError('Open the P1 source before exporting.')
    out=root/'manufacturing/enclosure/supporting';(out/'stl').mkdir(parents=True,exist_ok=True);(out/'step').mkdir(parents=True,exist_ok=True)
    evidence=root/'docs/verification/enclosure-p1/mesh-checks.json'
    report=json.loads(evidence.read_text()) if names is not None and evidence.exists() else {'revision':'P1','meshes':[]}
    if names is not None:report['meshes']=[r for r in report['meshes'] if r['name'] not in names]
    for name in (names if names is not None else PRODUCTION+COUPONS):
        b=doc.getObject(name)
        if name=='DisplayInsert':mesh=MeshPart.meshFromShape(Shape=b.Shape,Fineness=2,SecondOrder=0,Optimize=1,AllowQuad=0,MaxLength=2,MinLength=.05)
        else:mesh=MeshPart.meshFromShape(Shape=b.Shape,LinearDeflection=.06,AngularDeflection=.12,Relative=False)
        mat=App.Matrix()
        face='floor down'
        if name=='Cover':mat.A22=-1;mat.A33=-1;face='exterior top down'
        elif name in ['Fascia','DisplayInsert','EncoderKnob','KnobAccentRing']:
            mat.A22=0;mat.A23=-1;mat.A32=1;mat.A33=0;face='front face down'
        elif name=='LedKeeper':mat.A22=0;mat.A23=1;mat.A32=-1;mat.A33=0;face='rear bridge face down'
        mesh.transform(mat);bb=mesh.BoundBox;mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin)
        path=out/'stl'/('p1-'+name.lower()+'.stl');mesh.write(str(path));r=Mesh.Mesh(str(path));bb=r.BoundBox
        item=dict(mesher='Netgen' if name=='DisplayInsert' else 'OCC',name=name,file=str(path.relative_to(root)).replace('\\','/'),bed_face=face,dimensions_mm=[bb.XLength,bb.YLength,bb.ZLength],z_min_mm=bb.ZMin,facets=r.CountFacets,closed=r.isSolid(),nonmanifold=r.hasNonManifolds(),self_intersections=r.hasSelfIntersections(),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        report['meshes'].append(item);report['meshes'].sort(key=lambda r:(PRODUCTION+COUPONS).index(r['name']));(root/'docs/verification/enclosure-p1/mesh-checks.json').write_text(json.dumps(report,indent=2))
        if not item['closed'] or item['nonmanifold'] or item['self_intersections']:raise RuntimeError('Mesh failed: '+name)
        if max(bb.XLength+10,bb.YLength+10)>236 or bb.ZLength>256 or abs(bb.ZMin)>1e-5:raise RuntimeError('Print envelope failed: '+name)
        yield item
    export_step(doc,root)
    return report













def export_step(doc,root):
    """Expand linked instances in a transient export document; leave source native."""
    objects=[doc.getObject(n) for n in PRODUCTION]+[o for o in doc.Objects if o.TypeId=='App::Link']
    interchange=App.newDocument('EnclosureStepExport')
    try:
        features=[]
        for source in objects:
            f=interchange.addObject('Part::Feature',source.Name);f.Label=source.Label
            f.Shape=source.Shape.copy();features.append(f)
        interchange.recompute()
        path=Path(root)/'manufacturing/enclosure/supporting/step/p1-enclosure-assembly.step'
        Part.export(features,str(path))
        reread=Part.read(str(path))
        report=dict(revision='P1',valid=reread.isValid(),solids=len(reread.Solids),
                    volume_mm3=reread.Volume,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        assert report['valid'] and report['solids']==len(objects),report
        (Path(root)/'docs/verification/enclosure-p1/step-checks.json').write_text(json.dumps(report,indent=2))
        return report
    finally:
        App.closeDocument(interchange.Name);App.setActiveDocument(doc.Name)

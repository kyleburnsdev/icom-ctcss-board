"""Native editable M3 x 0.5 SubtractiveHelix features for the bench holder.

The caller supplies a body with its core/clearance bores already pocketed.
Dimensions are mm; 0.10 mm radial allowance is a selected FDM fit default,
not a certified 6H thread. Qualify with the matching printed mount coupon.
"""
import math
import FreeCAD as App
import Part
import Sketcher


def cut_m3_thread(doc,body,name,x,y,start_z=9,length=6,radial_allowance=.10):
    pitch=.5
    minor=(3-1.082532*pitch)/2+radial_allowance
    major=1.5+radial_allowance
    half_root=pitch/16
    half_mouth=half_root+(major-minor)/math.sqrt(3)
    previous=body.Tip
    sketch=doc.addObject('Sketcher::SketchObject',name+'Profile');body.addObject(sketch)
    sketch.Label='M3 thread flank profile - 60 degrees'
    sketch.Placement=App.Placement(App.Vector(x,y,start_z),App.Rotation(App.Vector(1,0,0),90))
    points=[(minor-.05,-half_mouth-.03),(major,-half_root),
            (major,half_root),(minor-.05,half_mouth+.03)]
    for i,p in enumerate(points):
        q=points[(i+1)%len(points)]
        index=sketch.addGeometry(Part.LineSegment(App.Vector(*p,0),App.Vector(*q,0)),False)
        sketch.addConstraint(Sketcher.Constraint('Block',index))
    feature=body.newObject('PartDesign::SubtractiveHelix',name)
    feature.Label='PCB mount M3 x 0.5 - upper 6 mm'
    feature.Profile=sketch;feature.ReferenceAxis=(sketch,['V_Axis'])
    feature.Mode='pitch-height-angle';feature.Pitch=pitch;feature.Height=length
    feature.LeftHanded=False;feature.Reversed=False;feature.Refine=True
    doc.recompute()
    assert not feature.Shape.isNull() and feature.Shape.isValid() and len(feature.Shape.Solids)==1
    if previous.ViewObject:previous.Visibility=False
    if sketch.ViewObject:sketch.Visibility=False
    return feature

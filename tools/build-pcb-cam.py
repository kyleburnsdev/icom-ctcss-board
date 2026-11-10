"""Build native FreeCAD CAM jobs via Robust MCP Server execute_python.

Load this module in FreeCAD, then call build(root). Uses prepared Gerber-derived
geometry; never reads or writes KiCad source. NC is a review deliverable until
the setup and process acceptance in the manufacturing README is complete.
"""
import importlib.util
import hashlib
import json
import math
import re
from pathlib import Path as FilePath

import FreeCAD as App
import FreeCADGui as Gui
import Part
from Path.Main import Job
from Path.Op import Engrave, Helix, PocketShape
from Path.Tool import Controller
from Path.Tool.toolbit import ToolBit

V = App.Vector


def cam_document(root):
    """Bind the open project by its exact filename; FreeCAD renames on reopen."""
    path=(FilePath(root)/'mechanical/pcb/icom-ctcss-pcb-cam.FCStd').resolve()
    matches=[doc for doc in App.listDocuments().values()
             if doc.FileName and FilePath(doc.FileName).resolve()==path]
    if len(matches)!=1:
        raise RuntimeError('Open exactly one saved PCB CAM project: '+str(path))
    return matches[0]


def feature(doc, name, shape, group):
    obj = doc.addObject('Part::Feature', name)
    obj.Shape = shape
    group.addObject(obj)
    obj.Visibility = False
    return obj


def setup_point(x, y, face):
    if face == 'preparation':
        return V(x,y,0)
    return V((150-x if face=='bottom' else x)+0.10,y+0.10,0)


def wire_geometry(doc, name, lines, face, group):
    wires=[]
    for points in lines:
        vectors=[setup_point(x,y,face) for x,y in points]
        wires.append(Part.makePolygon(vectors))
    return feature(doc,name,Part.makeCompound(wires),group)


def controller(job, name, number, diameter, feed, plunge, shape='endmill.fcstd'):
    bit=ToolBit.from_shape_id(shape).attach_to_doc(doc=job.Document)
    bit.Diameter=diameter
    bit.ShankDiameter=3.175
    bit.Length=38
    if hasattr(bit,'CuttingEdgeHeight'):
        bit.CuttingEdgeHeight=5.5
    if shape=='v-bit.fcstd':
        # Physical V-bit; offset geometry uses effective width at cutting depth.
        bit.CuttingEdgeAngle=30
        if hasattr(bit,'TipDiameter'):
            bit.TipDiameter=0.2
    bit.Label=name
    tc=Controller.Create(name,tool=bit,toolNumber=number)
    tc.HorizFeed=f'{feed} mm/min'
    tc.VertFeed=f'{plunge} mm/min'
    tc.SpindleSpeed=12000
    job.Proxy.addToolController(tc)
    return tc


def depths(op, final, step=0.3, clearance=15, safe=2):
    for key,value in [('StartDepth',0),('FinalDepth',final),('StepDown',step),
                      ('ClearanceHeight',clearance),('SafeHeight',safe)]:
        if hasattr(op,key):
            op.setExpression(key,None)
            setattr(op,key,value)


def create_job(doc,name,face,top_z=0):
    stock=doc.addObject('Part::Box',name+'_Board')
    stock.Label=name+' | 150 x 100 x 1.5 mm blank'
    stock.Length=150; stock.Width=100; stock.Height=1.5
    p=setup_point(0,0,'preparation' if face=='preparation' else 'top')
    stock.Placement.Base=V(p.x,p.y,top_z-1.5)
    doc.recompute()
    job=Job.Create(name,[stock])
    job.Label=name.replace('_',' ')
    job.PostProcessor=''
    job.OrderOutputBy='Operation'
    for tc in list(job.Tools.Group):
        bit=tc.Tool
        doc.removeObject(tc.Name)
        if bit: doc.removeObject(bit.Name)
    job.Description='REVIEW: actual jig stack, tool/holder clearance, surface probing and coupon qualification required'
    for prop in ('ExtXneg','ExtXpos','ExtYneg','ExtYpos','ExtZneg','ExtZpos'):
        if hasattr(job.Stock,prop): setattr(job.Stock,prop,0)
    stock.Visibility=False
    return job


def circular_geometry(doc,name,holes,face,group,floors=False,floor_z=-1.65):
    shapes=[]
    for hole in holes:
        p=setup_point(hole['x'],hole['y'],face)
        if floors: p.z=floor_z
        wire=Part.Wire([Part.makeCircle(hole['diameter']/2,p)])
        shapes.append(Part.Face(wire) if floors else wire)
    return feature(doc,name,Part.makeCompound(shapes),group)


def pocket(job,name,holes,face,tc,group,top_z=0,final_z=-1.65):
    region=circular_geometry(job.Document,name+'_Floors',holes,face,group,True,final_z)
    op=PocketShape.Create(name,parentJob=job)
    op.Base=[(region,[f'Face{i+1}' for i in range(len(holes))])]
    op.ToolController=tc
    depths(op,final_z)
    op.StartDepth=top_z
    op.SafeHeight=top_z+2
    op.StepOver=40
    op.KeepToolDown=True
    op.Comment='Full circular pockets; no loose plugs. Through-cut requires sacrificial protection.'
    job.Document.recompute()
    assert op.Path.Commands, name
    return op



def setup_summary(doc,data,root):
    sheet=doc.addObject('Spreadsheet::Sheet','SetupSummary')
    sheet.Label='Trial settings | offsets preserve the selected surface datum'
    rows=[('Board thickness mm',1.5,'BoardThickness'),
          ('PCB underside above jig floor mm',data['settings']['support_height_above_floor_mm'],'SupportHeight'),
          ('Hole breakthrough below PCB mm',data['settings']['hole_breakthrough_mm'],'Breakthrough'),
          ('Pad tool initial spring overtravel mm',data['mask_removal']['spring_overtravel_below_copper_mm'],'MaskOvertravel'),
          ('Pad clearing repeat-pass Z offset mm',0,'MaskPassOffset'),
          ('Drag initial spring preload mm',data['settings']['drag_preload_mm'],'DragPreload'),
          ('Bottom drag repeat-pass Z offset mm',0,'BottomDragPassOffset'),
          ('Drag feed mm/min',data['settings']['drag_feed_mm_min'],'DragFeed'),
          ('Drag plunge mm/min',data['settings']['drag_plunge_mm_min'],'DragPlunge'),
          ('Pad tool spindle rpm',6000,'MaskRPM'),
          ('Pad tool feed mm/min',400,'MaskFeed'),
          ('Pad tool plunge mm/min',200,'MaskPlunge'),
          ('Top drag repeat-pass Z offset mm',0,'TopDragPassOffset')]
    for row,(label,value,alias) in enumerate(rows,1):
        sheet.set('A'+str(row),label);sheet.set('B'+str(row),str(value));sheet.setAlias('B'+str(row),alias)
    sheet.set('A14','PCB SHA256');sheet.set('B14',hashlib.sha256((root/'electronics/icom-ctcss-board.kicad_pcb').read_bytes()).hexdigest())
    sheet.set('A15','CAM inputs SHA256');sheet.set('B15',hashlib.sha256((root/'manufacturing/pcb/carvera-air/cam-inputs.json').read_bytes()).hexdigest())
    sheet.set('A17','Trial: pad and drag initial overtravel 0.05 mm. Repeat offsets start at zero; lower only the operation offset after inspection.')
    sheet.set('A18','10/20: original bottom copper Z0/map. 25/40: new mask-surface Z0. 50: new aluminium-floor Z0, NO copper map.')
    sheet.set('A19','All coating/curing in place. No probing between copper mapping and pad clearing except tool-length setting.')
    sheet.set('A20','Floor setup assumes PCB underside Z+1.00 and final Z+0.85; match actual support height before using file 50.')
    sheet.set('A21','Inventory preflight incomplete; review CAM is not a claim of stock completeness or machine qualification.')
    return sheet


def create_mask_job(doc, inputs, data):
    settings=data['mask_removal']
    job=create_job(doc,'Job20_BottomMaskRemoval','bottom')
    job.Description='Same bonded setup as Job10. Retain original bottom copper Z0 AND height map. NO probing except tool-length setting between initial copper map and pad clearing. All coating/curing stays in jig. Before any circuit holes. First pass conservative; inspect before lowering MaskPassOffset.'
    tc=controller(job,'T4 Makera spring mask remover | 0.3 mm 30 deg',4,2,400,200,'v-bit.fcstd')
    tc.SpindleSpeed=6000;tc.Tool.TipDiameter=.3;tc.Tool.Length=50
    tc.Tool.CuttingEdgeHeight=3
    tc.setExpression('SpindleSpeed','SetupSummary.MaskRPM')
    tc.setExpression('HorizFeed','SetupSummary.MaskFeed / 60')
    tc.setExpression('VertFeed','SetupSummary.MaskPlunge / 60')
    bands={}
    for points in settings['centerlines']:
        bands.setdefault(int(points[0][1]//10),[]).append(points)
    for band,lines in sorted(bands.items()):
        geo=wire_geometry(doc,f'BottomMaskGeometry_Y{band*10:03d}',lines,'bottom',inputs)
        op=Engrave.Create(f'OpenBottomPads_Y{band*10:03d}',parentJob=job)
        op.Label=f'Open pads Y{band*10} to {band*10+10} mm'
        op.BaseShapes=[geo];op.ToolController=tc
        depths(op,-settings['spring_overtravel_below_copper_mm'],1)
        op.setExpression('FinalDepth','-SetupSummary.MaskOvertravel + SetupSummary.MaskPassOffset')
        op.Comment='Spring tool only; 0.05 mm initial overtravel. Pressure, not copper-cutting depth. Retain copper Z0/map. No circuit holes yet. Inspect, then lower operation offset slightly if needed.'
        doc.recompute();assert op.Path.Commands
        yield {'stage':'bottom pad opening','band_mm':band*10,'commands':len(op.Path.Commands)}


def create_drag_job(doc,inputs,data,face):
    bottom=face=='bottom'
    job=create_job(doc,'Job25_BottomLegend' if bottom else 'Job40_TopLegend',face)
    job.Description=f'{face.title()} diamond-drag legend. NEW finished-mask surface Z0 after pad clearing, preserve jig XY. No copper height map. T6 1/4 inch shank, 90 degree tip, NONROTATING. First pass conservative; inspect before lowering {face.title()}DragPassOffset. Remove contrasting coat only; retain base mask.'
    tc=controller(job,'T6 diamond drag | 6.35 mm shank | spindle OFF',6,.127,300,100,'v-bit.fcstd')
    tc.SpindleSpeed=0;tc.Tool.ShankDiameter=6.35;tc.Tool.CuttingEdgeAngle=90
    tc.Tool.TipDiameter=.001
    tc.Tool.Length=95.25  # Matching-model reference, not measured owned-tool length.
    tc.setExpression('HorizFeed','SetupSummary.DragFeed / 60')
    tc.setExpression('VertFeed','SetupSummary.DragPlunge / 60')
    job.addProperty('App::PropertyString','ToolReference','Process')
    job.ToolReference='Owned 6.35 mm shank, 90/120 deg tips. 95.25 mm length / 0.127 mm line width are matching WidgetWorks model references only. Set actual tool length by mechanical/manual contact, not electrical diamond-tip probing.'
    # Two-mm bands bound FreeCAD Engrave's quadratic wire-ordering cost and
    # expose manageable, named regions in the native tree.
    bands={}
    for points in data['bottom_legend_hatch' if bottom else 'legend_hatch']:
        bands.setdefault(int(points[0][1]//2),[]).append(points)
    for band,lines in sorted(bands.items()):
        stem=f'{face.title()}Legend_Y{band*2:03d}'
        geo=wire_geometry(doc,stem+'_Geometry',lines,face,inputs)
        op=Engrave.Create('Drag'+stem,parentJob=job)
        op.Label=f'{face.title()} drag legend Y{band*2} to {band*2+2} mm'
        op.BaseShapes=[geo];op.ToolController=tc
        depths(op,-data['settings']['drag_preload_mm'],1)
        op.setExpression('FinalDepth','-SetupSummary.DragPreload + SetupSummary.'+('BottomDragPassOffset' if bottom else 'TopDragPassOffset'))
        op.Comment='SPINDLE OFF. Finished-mask surface reference; initial 0.05 mm spring preload, not groove depth. Reveal base color; inspect before increasing pressure.'
        doc.recompute();assert op.Path.Commands
        yield {'stage':face+' drag legend','band_mm':band*2,'commands':len(op.Path.Commands)}


def build(root):
    root=FilePath(root)
    saved_path=(root/'mechanical/pcb/icom-ctcss-pcb-cam.FCStd').resolve()
    if any(doc.FileName and FilePath(doc.FileName).resolve()==saved_path for doc in App.listDocuments().values()) or 'CTCSS_PCB_CAM' in App.listDocuments():
        raise RuntimeError('Preserve and close the existing PCB CAM before regeneration')
    data=json.loads((root/'manufacturing/pcb/carvera-air/cam-inputs.json').read_text())
    for filename,digest in data['source_hashes'].items():
        if hashlib.sha256((root/'manufacturing/pcb/carvera-air/native-exports'/filename).read_bytes()).hexdigest()!=digest:
            raise RuntimeError('Stale CAM inputs: '+filename)
    doc=App.newDocument('CTCSS_PCB_CAM')
    doc.Label='CTCSS PCB | in-jig coating / two-color drag legend trial'
    inputs=doc.addObject('App::DocumentObjectGroup','ManufacturingGeometry')
    inputs.Label='Native artwork-derived geometry | one face transform'
    sheet=setup_summary(doc,data,root)
    def checkpoint():
        doc.recompute();doc.saveAs(str(saved_path))
    prep=create_job(doc,'Job00_RegistrationPreparation','preparation')
    prep.Description='Only for unprepared blanks. Jig absent; independent blank-corner XY / copper-top Z0 on sacrificial wasteboard. Skip for accepted prepared blank.'
    tprep=controller(prep,'T3 Corn 0.8 mm',3,.8,500,100)
    pocket(prep,'PrepareFourJigHoles',[h for h in data['holes'] if h['diameter']>4],'preparation',tprep,inputs)
    checkpoint();yield {'stage':'registration preparation'}
    bottom=create_job(doc,'Job10_BottomCopper','bottom')
    bottom.Description='Bottom up. Register/bond/withdraw PCB pins. Establish copper Z0 and thorough copper map. Preserve same seating, zero AND map through coating/curing and Job20. Tool-length setting only; no intervening surface probing.'
    tc=controller(bottom,'T2 V-bit 30 deg tip 0.2 mm',2,3.175,100,30,'v-bit.fcstd')
    geo=wire_geometry(doc,'BottomIsolationCenterlines',data['isolation_centerlines'],'bottom',inputs)
    op=Engrave.Create('IsolateMergedBottomCopper',parentJob=bottom)
    op.BaseShapes=[geo];op.ToolController=tc;depths(op,-.1,.1)
    op.Comment='0.15 mm offset; 30 deg / 0.2 mm tip; inspect exposed copper before in-jig coating.'
    checkpoint();yield {'stage':'bottom isolation','commands':len(op.Path.Commands)}
    yield from create_mask_job(doc,inputs,data)
    checkpoint()
    yield from create_drag_job(doc,inputs,data,'bottom')
    checkpoint()
    yield from create_drag_job(doc,inputs,data,'top')
    checkpoint()
    support=float(sheet.get('B2'));breakthrough=float(sheet.get('B3'))
    assert support>breakthrough>0
    top_z=support+1.5;final_z=support-breakthrough
    holes_job=create_job(doc,'Job50_BottomHoles','bottom',top_z)
    holes_job.Description='AFTER both coatings and legends. Remove board, set NEW Z0 at aluminium floor, add sacrificial backing, remount bottom up. Preserve jig XY. NO copper map. Default PCB underside +1.00 / copper plane +2.50 / tip floor +0.85 mm. Adjust support geometry/settings to actual stack, regenerate and check. Never below Z0; excludes jig holes.'
    for diameter,feed in [(.9,55),(1.1,135)]:
        holes=[h for h in data['holes'] if abs(h['diameter']-diameter)<1e-6]
        tc=controller(holes_job,f'T3 Corn 0.8 | {diameter} mm bore feed',3,.8,feed,50)
        geo=circular_geometry(doc,f'ElectricalHoles_{diameter}'.replace('.','p'),holes,'bottom',inputs)
        op=Helix.Create(f'BoreElectrical_{diameter}'.replace('.','p'),parentJob=holes_job)
        op.Base=[(geo,[f'Edge{i+1}' for i in range(len(holes))])];op.ToolController=tc
        depths(op,final_z,.01 if diameter==.9 else .03)
        op.StartDepth=top_z;op.SafeHeight=top_z+2
        op.setExpression('StartDepth','SetupSummary.SupportHeight + SetupSummary.BoardThickness')
        op.setExpression('FinalDepth','SetupSummary.SupportHeight - SetupSummary.Breakthrough')
        op.setExpression('SafeHeight','SetupSummary.SupportHeight + SetupSummary.BoardThickness + 2')
        op.StartSide='Inside';op.StartRadius=0;op.StepOver=40
        op.Comment='Final floor-referenced bore after BOTH faces. 0.8 mm corn interpolation, not a twist drill. No height compensation; minimum tool-tip Z must remain positive.'
        checkpoint();yield {'stage':op.Name,'holes':len(holes),'commands':len(op.Path.Commands)}
    tc=controller(holes_job,'T3 Corn 0.8 | enclosure mounts',3,.8,500,100)
    op=pocket(holes_job,'PocketFourEnclosureMounts',[h for h in data['holes'] if abs(h['diameter']-4)<1e-6],'bottom',tc,inputs,top_z,final_z)
    op.setExpression('StartDepth','SetupSummary.SupportHeight + SetupSummary.BoardThickness')
    op.setExpression('FinalDepth','SetupSummary.SupportHeight - SetupSummary.Breakthrough')
    for geo in inputs.Group:geo.Visibility=False
    for obj in doc.Objects:
        if obj.Name.startswith('Job') and hasattr(obj,'Stock'):
            obj.Visibility=False;obj.Stock.Visibility=False
    for obj in doc.Objects:
        if hasattr(obj,'ViewObject') and hasattr(obj.ViewObject,'Visibility'):
            obj.ViewObject.Visibility=False
    doc.IsolateMergedBottomCopper.ViewObject.Visibility=True
    checkpoint()
    Gui.activeDocument().activeView().viewTop();Gui.activeDocument().activeView().fitAll()
    yield {'stage':'saved','file':str(saved_path)}


JOBS=[('Job00_RegistrationPreparation','00-registration-preparation.nc'),
      ('Job10_BottomCopper','10-bottom-copper.nc'),
      ('Job20_BottomMaskRemoval','20-bottom-mask-removal.nc'),
      ('Job25_BottomLegend','25-bottom-legend-drag.nc'),
      ('Job40_TopLegend','40-top-legend-drag.nc'),
      ('Job50_BottomHoles','50-bottom-holes.nc')]


def export_milling(root):
    root=FilePath(root);doc=cam_document(root);doc.recompute()
    sheet=doc.SetupSummary
    if not float(sheet.get('B2'))>float(sheet.get('B3'))>0:
        raise RuntimeError('Sacrificial support must exceed hole breakthrough; no floor crossing')
    if any(float(sheet.get(cell))>0 for cell in ('B5','B7','B13')):
        raise RuntimeError('Repeat-pass offsets must be zero or negative')
    spec=importlib.util.spec_from_file_location('ctcss_air_post',root/'tools/post/makera_legacy_post.py')
    post=importlib.util.module_from_spec(spec);spec.loader.exec_module(post)
    out=root/'manufacturing/pcb/carvera-air/review-nc';out.mkdir(exist_ok=True)
    report={}
    for name,filename in JOBS:
        job=doc.getObject(name);objects=[];previous_tool=None
        for op in job.Operations.Group:
            assert op.Active and op.Path.Commands and 'Invalid' not in op.State
            tc=op.ToolController
            if tc.ToolNumber!=previous_tool:
                tc.Proxy.execute(tc);objects.append(tc);previous_tool=tc.ToolNumber
            objects.append(op)
        text=post.export(objects,str(out/filename),'--no-show-editor --precision 5 --preamble "G90 G94\nG17\nG54\nM5" --postamble "M5\nG0 Z15\nM30"')
        lines=['(REVIEW ONLY - IN-JIG COATING AND TWO-COLOR DRAG TRIAL)', '('+job.Description.replace('(','[').replace(')',']')+')']
        drag=name in ('Job25_BottomLegend','Job40_TopLegend')
        for line in text.splitlines():
            if line.strip()=='G4':continue
            if drag and re.match(r'^M[34]\b',line):
                # OEM mill post emits M3 S0 for a zero-speed controller.
                # Drag must never enable spindle rotation. Keep native motion,
                # replace only this spindle command with an explicit stop.
                if not re.fullmatch(r'M[34]\s+S0(?:\.0+)?',line.strip()):
                    raise RuntimeError('Unexpected spindle start in drag export: '+line)
                lines.append('M5');continue
            if drag and not line.lstrip().startswith('('):
                # The OEM post appends its cached SPINDLE_SPEED to feed moves,
                # including when the next zero-RPM controller has no M3 command.
                # Remove speed words in nonrotating jobs; retain explicit M5.
                line=re.sub(r'\s+S-?\d+(?:\.\d*)?', '', line)
            lines.append(line)
            if line.startswith('M3 '):lines.append('G4 S2')
        (out/filename).write_text('\n'.join(lines)+'\n')
        report[name]={'file':str((out/filename).relative_to(root)),'description':job.Description,
                      'operations':[{'name':op.Name,'commands':len(op.Path.Commands),'start_depth_mm':op.StartDepth.Value,'final_depth_mm':op.FinalDepth.Value} for op in job.Operations.Group]}
    (root/'docs/verification/pcb-cam-jobs.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


def inspect_saved(root):
    root=FilePath(root);path=root/'mechanical/pcb/icom-ctcss-pcb-cam.FCStd'
    if any(doc.FileName and FilePath(doc.FileName).resolve()==path.resolve() for doc in App.listDocuments().values()):
        raise RuntimeError('Preserve and close CAM before independent reopen')
    doc=App.openDocument(str(path))
    data=json.loads((root/'manufacturing/pcb/carvera-air/cam-inputs.json').read_text())
    assert doc.SetupSummary.get('B14')==hashlib.sha256((root/'electronics/icom-ctcss-board.kicad_pcb').read_bytes()).hexdigest()
    assert doc.SetupSummary.get('B15')==hashlib.sha256((root/'manufacturing/pcb/carvera-air/cam-inputs.json').read_bytes()).hexdigest()
    states=[]
    for name,_ in JOBS:
        job=doc.getObject(name);assert job is not None and job.Operations.Group
        if 'Legend' in name:
            assert all(op.ToolController.SpindleSpeed==0 and op.ToolController.Tool.ShankDiameter.Value==6.35 for op in job.Operations.Group)
        for op in job.Operations.Group:
            assert op.Path.Commands and 'Invalid' not in op.State,op.Name
            if name=='Job50_BottomHoles':
                assert op.FinalDepth.Value>0
                for cmd in op.Path.Commands:
                    assert cmd.Parameters.get('Z',1)>=0,(op.Name,cmd)
            states.append({'job':name,'operation':op.Name,'commands':len(op.Path.Commands),'state':list(op.State),'final_depth_mm':op.FinalDepth.Value})
    report={'saved_fcstd_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'freecad_version':App.Version(),'reopen':'PASS','native_operations':states,
            'helix_pitch_mm':[.01,.03],'j1_pin1_bottom_jig_mm':[20.1,40.1],'j1_pin1_top_jig_mm':[130.1,40.1],
            'scope':'Saved native jobs and paths; no machine run or holder/fixture collision qualification.'}
    (root/'docs/verification/pcb-cam-reopen.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

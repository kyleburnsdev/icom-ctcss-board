"""Build native FreeCAD CAM jobs via Robust MCP Server execute_python.

Load this module in FreeCAD, then call build(root). Uses prepared Gerber-derived
geometry; never reads or writes KiCad source. NC is a review deliverable until
the setup and process acceptance in the manufacturing README is complete.
"""
import importlib.util
import hashlib
import json
import math
from pathlib import Path as FilePath

import FreeCAD as App
import FreeCADGui as Gui
import Part
from Path.Main import Job
from Path.Op import Engrave, Helix, PocketShape
from Path.Tool import Controller
from Path.Tool.toolbit import ToolBit

V = App.Vector
LASER_POWER = 0.05
LASER_FEED = 500


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


def create_job(doc,name,face):
    stock=doc.addObject('Part::Box',name+'_Board')
    stock.Label=name+' | 150 x 100 x 1.5 mm blank, top Z0'
    stock.Length=150; stock.Width=100; stock.Height=1.5
    p=setup_point(0,0,'preparation' if face=='preparation' else 'top')
    stock.Placement.Base=V(p.x,p.y,-1.5)
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


def circular_geometry(doc,name,holes,face,group,floors=False):
    shapes=[]
    for hole in holes:
        p=setup_point(hole['x'],hole['y'],face)
        if floors: p.z=-1.65
        wire=Part.Wire([Part.makeCircle(hole['diameter']/2,p)])
        shapes.append(Part.Face(wire) if floors else wire)
    return feature(doc,name,Part.makeCompound(shapes),group)


def pocket(job,name,holes,face,tc,group):
    region=circular_geometry(job.Document,name+'_Floors',holes,face,group,True)
    op=PocketShape.Create(name,parentJob=job)
    op.Base=[(region,[f'Face{i+1}' for i in range(len(holes))])]
    op.ToolController=tc
    depths(op,-1.65)
    op.StepOver=40
    op.KeepToolDown=True
    op.Comment='Full circular pockets; no loose plugs. Through-cut requires sacrificial protection.'
    job.Document.recompute()
    assert op.Path.Commands, name
    return op


def create_mask_job(doc, inputs, data):
    """Native spring-tool engraving using the original copper work datum."""
    if doc.getObject('Job20_BottomMaskRemoval'):
        raise RuntimeError('Preserve existing mask job; do not duplicate/replace edits')
    settings=data['mask_removal']
    job=create_job(doc,'Job20_BottomMaskRemoval','bottom')
    job.Label='Job20 Bottom solder mask pad opening | before electrical drilling'
    job.Description='Fully cured bottom mask; retain G54 copper Z0 established before trace cutting. Never re-zero on mask. Z-0.20 is commanded spring-tool overtravel below known copper, NOT intended copper removal; actual compression includes mask thickness. Run before initial electrical/enclosure holes, never over open holes. After remounting reproduce original seating and retain work zero. Qualify preload and copper preservation.'
    tc=controller(job,'T4 Makera spring solder-mask remover | 0.3 mm 30 deg',4,2,settings['feed_mm_min'],settings['plunge_mm_min'],'v-bit.fcstd')
    tc.SpindleSpeed=settings['rpm']
    tc.Tool.TipDiameter=settings['tip_mm']
    tc.Tool.ShankDiameter=3.175
    tc.Tool.Length=50
    tc.Tool.CuttingEdgeHeight=3
    job.addProperty('App::PropertyString','ToolProfileSource','Process')
    job.ToolProfileSource='Makera product specifications accessed 2026-10-31; OEM fctb retained with documented RPM/shank discrepancies.'
    job.addProperty('App::PropertyLength','ConservativeContactDiameter','Process')
    job.ConservativeContactDiameter=2*settings['envelope_radius_mm']
    summary=doc.getObject('SetupSummary')
    if summary:
        for row,(key,value) in enumerate([
            ('Mask spindle rpm',settings['rpm']),('Mask feed mm/min',settings['feed_mm_min']),
            ('Mask plunge mm/min',settings['plunge_mm_min']),
            ('Mask spring overtravel below original copper mm',settings['spring_overtravel_below_copper_mm']),
            ('Mask pad inset mm',settings['inset_mm']),
            ('Mask conservative envelope diameter mm',2*settings['envelope_radius_mm'])],22):
            summary.set('A'+str(row),key);summary.set('B'+str(row),str(value))
        summary.set('A29','Retain original pre-isolation copper G54 Z0 for every subsequent program; never re-zero on coating or after remount/flip.')
    bands={}
    for points in settings['centerlines']:
        bands.setdefault(int(points[0][1]//10),[]).append(points)
    for band,lines in sorted(bands.items()):
        geo=wire_geometry(doc,f'BottomMaskGeometry_Y{band*10:03d}',lines,'bottom',inputs)
        op=Engrave.Create(f'OpenBottomPads_Y{band*10:03d}',parentJob=job)
        op.Label=f'Open solder pads Y{band*10} to {band*10+10} mm'
        op.BaseShapes=[geo]; op.ToolController=tc
        depths(op,-settings['spring_overtravel_below_copper_mm'],settings['spring_overtravel_below_copper_mm'])
        op.Comment='Pad flashes only; >=0.10 mm masked rim. Conservative V envelope, 0.12 mm fill pitch. Retain pre-isolation copper Z0; Z-0.20 is spring-tool overtravel, not copper cutting. Electrical holes not yet drilled.'
        doc.recompute()
        assert op.Path.Commands
        yield {'stage':'bottom mask pad opening','band_mm':band*10,'commands':len(op.Path.Commands)}
    for geo in inputs.Group: geo.Visibility=False
    job.Visibility=False; job.Stock.Visibility=False


def build(root):
    root=FilePath(root)
    saved_path=(root/'mechanical/pcb/icom-ctcss-pcb-cam.FCStd').resolve()
    if 'CTCSS_PCB_CAM' in App.listDocuments() or any(doc.FileName and FilePath(doc.FileName).resolve()==saved_path for doc in App.listDocuments().values()):
        raise RuntimeError('Close/preserve the existing CTCSS_PCB_CAM before regeneration')
    data=json.loads((root/'manufacturing/pcb/carvera-air/cam-inputs.json').read_text())
    for filename,digest in data['source_hashes'].items():
        path=root/'manufacturing/pcb/carvera-air/native-exports'/filename
        if hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
            raise RuntimeError('Stale CAM inputs; regenerate from exports: '+filename)
    doc=App.newDocument('CTCSS_PCB_CAM')
    doc.Label='CTCSS PCB | Carvera Air jig | review CAM'
    output=root/'mechanical/pcb'; output.mkdir(parents=True,exist_ok=True)
    def checkpoint():
        doc.recompute()
        doc.saveAs(str(output/'icom-ctcss-pcb-cam.FCStd'))
    inputs=doc.addObject('App::DocumentObjectGroup','ManufacturingGeometry')
    inputs.Label='Gerber-derived geometry | regeneration inputs in manufacturing package'
    params=doc.addObject('Spreadsheet::Sheet','SetupSummary')
    params.Label='Setup summary | laser power drives post; feed comes from controller'
    for row,(key,value) in enumerate([
        ('Board thickness mm',1.5),('Through depth mm',1.65),('Clearance above face mm',15),
        ('Jig XY offset mm',0.10),('V-bit angle deg',30),('V-bit tip mm',0.2),
        ('Isolation depth mm',0.10),('Isolation offset mm',0.15),
        ('Corn bit mm',0.8),('Corn spindle rpm',12000),('Corn feed mm/min',500),
        ('Helix feed 0.9 mm/min',55),('Helix feed 1.1 mm/min',135),
        ('Laser hatch pitch mm',0.05),('Laser marking power fraction',LASER_POWER),
        ('Laser marking feed mm/min',LASER_FEED)],1):
        params.set(f'A{row}',key); params.set(f'B{row}',str(value))
    params.set('A17','Laser power B15 drives post; feed is set in native tool controller. Other rows summarize candidate process settings.')
    params.set('A19','PCB SHA256')
    params.set('B19',hashlib.sha256((root/'electronics/icom-ctcss-board.kicad_pcb').read_bytes()).hexdigest())
    params.set('A20','CAM inputs SHA256')
    params.set('B20',hashlib.sha256((root/'manufacturing/pcb/carvera-air/cam-inputs.json').read_bytes()).hexdigest())
    prep=create_job(doc,'Job00_RegistrationPreparation','preparation')
    prep.Description='FIRST: blank lower-left XY0, copper-top Z0, independent edge datum/bond on sacrificial wasteboard; jig absent. No perimeter trim on finished-size stock.'
    tprep=controller(prep,'T3 Corn 0.8 mm',3,0.8,500,100)
    registration=[h for h in data['holes'] if h['diameter']>4]
    pocket(prep,'PrepareFourJigHoles',registration,'preparation',tprep,inputs)
    checkpoint()
    yield {'stage':'registration preparation','operations':len(prep.Operations.Group)}

    bottom=create_job(doc,'Job10_BottomCopper','bottom')
    bottom.Description='Jig Anchor 1 XY0; register/bond/withdraw all PCB pins/probe exposed copper. Copper isolation only; holes are an independent repeatable job.'
    vbit=controller(bottom,'T2 V-bit 30 deg tip 0.2 mm',2,3.175,100,30,'v-bit.fcstd')
    source=wire_geometry(doc,'BottomIsolationCenterlines',data['isolation_centerlines'],'bottom',inputs)
    op=Engrave.Create('IsolateMergedBottomCopper',parentJob=bottom)
    op.BaseShapes=[source]; op.ToolController=vbit
    depths(op,-0.1,0.1)
    op.Comment='0.15 mm offset around merged retained copper; 30 degree / 0.2 mm V-bit; ideal width 0.25359 at 0.10 depth. Coupon required.'
    doc.recompute()
    assert op.Path.Commands
    checkpoint()
    yield {'stage':'bottom isolation','commands':len(op.Path.Commands)}
    yield from create_mask_job(doc,inputs,data)
    holes_job=create_job(doc,'Job30_BottomHoles','bottom')
    holes_job.Description='Independent bottom-frame electrical bores and enclosure mounts. Run initially after bottom mask pad opening; repeat only if needed after BOTH face coatings, before assembly. Retain original pre-isolation copper G54 Z0; never capture a new work zero. Reproduce original seating after remounting, remove PCB pins, and verify protected breakthrough. Never recut jig registration holes.'
    for diameter,feed in [(0.9,55),(1.1,135)]:
        holes=[h for h in data['holes'] if abs(h['diameter']-diameter)<1e-6]
        tc=controller(holes_job,f'T3 Corn 0.8 | {diameter} mm bore feed',3,0.8,feed,50)
        geo=circular_geometry(doc,f'ElectricalHoles_{diameter}'.replace('.','p'),holes,'bottom',inputs)
        op=Helix.Create(f'BoreElectrical_{diameter}'.replace('.','p'),parentJob=holes_job)
        op.Base=[(geo,[f'Edge{i+1}' for i in range(len(holes))])]
        op.ToolController=tc
        # The pinned OEM corn bit specifies a maximum 2-degree ramp. With
        # tiny orbital radii, 0.05 mm/revolution would exceed that limit.
        depths(op,-1.65,0.01 if diameter==0.9 else 0.03)
        op.StartSide='Inside'; op.StartRadius=0; op.StepOver=40
        op.Comment='0.8 mm corn bit interpolation; reduced centreline feed; qualify hole/lead fit and tool suitability before use.'
        doc.recompute()
        assert op.Path.Commands
        checkpoint()
        yield {'stage':op.Name,'holes':len(holes),'commands':len(op.Path.Commands)}
    mounts=[h for h in data['holes'] if abs(h['diameter']-4)<1e-6]
    tmount=controller(holes_job,'T3 Corn 0.8 | enclosure mounts',3,0.8,500,100)
    pocket(holes_job,'PocketFourEnclosureMounts',mounts,'bottom',tmount,inputs)
    checkpoint()
    yield {'stage':'bottom holes','operations':len(holes_job.Operations.Group)}

    top=create_job(doc,'Job40_TopLegend','top')
    top.Description='Mark fully UV-cured white solder mask after bottom inspection and Y-axis flip. Retain original copper G54 Z0; set optical focus at the programmed plane without resetting work zero. Register/bond/withdraw/check and reproduce seating. First-board trial: 5 percent, 500 mm/min, 0.05 mm hatch, one pass. Inspect after IPA cleaning; no separate legend coupon.'
    laser=controller(top,'Laser focus placeholder | no spindle post',99,0.05,LASER_FEED,100)
    laser.SpindleSpeed=0
    # FreeCAD Engrave orders wires with a quadratic nearest-neighbour search.
    # Two-mm Y bands bound that cost and expose meaningful regions in the tree.
    bands={}
    for points in data['legend_hatch']:
        bands.setdefault(int(points[0][1]//2),[]).append(points)
    for band,lines in sorted(bands.items()):
        geo=wire_geometry(doc,f'TopLegendGeometry_Y{band*2:03d}',lines,'top',inputs)
        op=Engrave.Create(f'ExposeLegend_Y{band*2:03d}',parentJob=top)
        op.Label=f'Mark legend Y{band*2} to {band*2+2} mm'
        op.BaseShapes=[geo]; op.ToolController=laser
        depths(op,0,0.1,clearance=0,safe=0)
        op.Comment='Planar hatch; dedicated laser post only. Y band bounds native wire-ordering cost.'
        doc.recompute()
        assert op.Path.Commands
        if band % 10 == 0:
            checkpoint()
        yield {'stage':'top legend band','y_mm':band*2,'commands':len(op.Path.Commands)}
    for obj in inputs.Group: obj.Visibility=False
    for job in [prep,bottom,doc.Job20_BottomMaskRemoval,holes_job,top]:
        job.Visibility=False
        job.Stock.Visibility=False
    bottom.Visibility=True
    doc.recompute()
    checkpoint()
    Gui.activeDocument().activeView().viewTop()
    Gui.activeDocument().activeView().fitAll()
    yield {'stage':'saved','file':'mechanical/pcb/icom-ctcss-pcb-cam.FCStd'}


def export_milling(root):
    root=FilePath(root)
    doc=cam_document(root)
    spec=importlib.util.spec_from_file_location('ctcss_air_post',root/'tools/post/makera_legacy_post.py')
    post=importlib.util.module_from_spec(spec); spec.loader.exec_module(post)
    out=root/'manufacturing/pcb/carvera-air/review-nc'; out.mkdir(exist_ok=True)
    report={}
    for job,filename in [(doc.Job00_RegistrationPreparation,'00-registration-preparation.nc'),
                         (doc.Job10_BottomCopper,'10-bottom-copper.nc'),
                         (doc.Job20_BottomMaskRemoval,'20-bottom-mask-removal.nc'),
                         (doc.Job30_BottomHoles,'30-bottom-holes.nc')]:
        objects=[]
        previous_tool=None
        for op in job.Operations.Group:
            tc=op.ToolController
            if tc.ToolNumber!=previous_tool:
                tc.Proxy.execute(tc)
                objects.append(tc)
                previous_tool=tc.ToolNumber
            objects.append(op)
        text=post.export(objects,str(out/filename),'--no-show-editor --precision 5 --preamble "G90 G94\\nG17\\nG54" --postamble "M5\\nG0 Z15\\nM30"')
        lines=['(REVIEW ONLY - KEEP OUT OF MACHINE ACTIVE JOB FOLDER)',
               '(Require qualified hole fit, surface mapping, fixture clearance and protected breakthrough)',
               '(Preparation: XY blank corner Z copper top; Production: XY jig Anchor 1 Z copper top)']
        if job.Name=='Job30_BottomHoles':
            lines.extend(['(Initial holes AFTER bottom mask pad opening; optional repeat after BOTH coatings)',
                          '(Retain original pre-isolation copper G54 Z0; never capture a new work zero)',
                          '(Verify registration and sacrificial breakthrough; excludes jig registration holes)'])
        if job.Name=='Job20_BottomMaskRemoval':
            lines[-1]='(XY jig Anchor 1; retain original pre-isolation copper G54 Z0 - NEVER RE-ZERO ON MASK)'
            lines.extend(['(T4 MAKERA SPRING TOOL ONLY - not an ordinary rigid engraving bit)',
                          '(Z-0.20 is spring-tool overtravel below known copper; compression also includes mask thickness)',
                          '(Run BEFORE initial electrical/enclosure holes; do not run across open holes)',
                          '(Qualify preload, coating removal and intact copper before production)'])
        for line in text.splitlines():
            if line.strip()=='G4': continue
            lines.append(line)
            if line.startswith('M3 '): lines.append('G4 S2')
        (out/filename).write_text('\n'.join(lines)+'\n')
        report[job.Name]={'file':str((out/filename).relative_to(root)),
                          'operations':[{'name':op.Name,'commands':len(op.Path.Commands)} for op in job.Operations.Group]}
    (root/'docs/verification/pcb-cam-jobs.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


def export_laser(root, power=None):
    """Translate planar native Engrave paths for the pinned Air laser semantics.

    M321/M322 select laser mode; M3 S0 arms with zero requested power. Only
    nonzero XY G1 motion receives power. All rapids, entries and Z moves carry
    explicit S0. Mark fully UV-cured white mask; first-board trial, not a
    physically validated marking recipe. Default power comes from the saved sheet.
    """
    root=FilePath(root)
    doc=cam_document(root)
    summary=doc.getObject('SetupSummary') or doc.getObject('SetupParameters')
    if power is None:
        power=float(summary.get('B15'))
    assert 0 < power <= 1
    job=doc.Job40_TopLegend
    lines=['(REVIEW - FIRST FULL BOARD TRIAL - DARK LEGEND ON FULLY UV CURED WHITE MASK)',
           '(One pass; inspect readability and coating integrity after IPA cleaning)',
           '(Retain original pre-isolation copper G54 Z0; adjust optical focus without resetting work zero)',
           'M5','G90 G94','G17','G21','G54','G0 Z15 S0','M321','G0 Z0 S0','M3 S0']
    current={'X':None,'Y':None,'Z':0}
    exposed=0
    for op in job.Operations.Group:
        assert op.Active
        lines.append(f'({op.Label})')
        for cmd in op.Path.Commands:
            if cmd.Name.startswith('('): continue
            if cmd.Name not in ('G0','G00','G1','G01'):
                raise RuntimeError('Unexpected laser motion: '+cmd.Name)
            values=cmd.Parameters
            target={axis:values.get(axis,current[axis]) for axis in current}
            if target['Z'] is not None and abs(target['Z'])>1e-6:
                raise RuntimeError('Laser CAM must stay on focus plane')
            moving=all(current[a] is not None and target[a] is not None for a in ('X','Y')) and math.hypot(target['X']-current['X'],target['Y']-current['Y'])>1e-7
            cutting=cmd.Name in ('G1','G01') and moving
            words=[cmd.Name]+[f'{a}{v:.5f}' for a,v in values.items() if a in ('X','Y','Z')]
            words.append(f'S{power:.5f}' if cutting else 'S0')
            if cutting:
                words.append(f'F{values.get("F",LASER_FEED/60)*60:.3f}')
                exposed+=1
            lines.append(' '.join(words))
            current=target
    lines.extend(['M5','M322','G0 Z15 S0','M30'])
    path=root/'manufacturing/pcb/carvera-air/review-nc/40-top-legend-laser.nc'
    path.write_text('\n'.join(lines)+'\n')
    return {'file':str(path.relative_to(root)),'powered_xy_segments':exposed,
            'bands':len(job.Operations.Group),'power_fraction':power,
            'process':'Laser mark fully UV-cured white solder mask; one pass; full board is the test piece.',
            'qualification':'First-board trial; verify installed firmware and focus, then inspect dark marking retention after IPA cleaning and reject damaged coating.'}


def inspect_saved(root):
    """Reopen a caller-closed saved project and record native path integrity.

    Refuse an open document rather than discarding possible manual edits.
    This does not recalculate or save sources and does not simulate holders.
    """
    root=FilePath(root)
    path=root/'mechanical/pcb/icom-ctcss-pcb-cam.FCStd'
    if 'CTCSS_PCB_CAM' in App.listDocuments() or any(doc.FileName and FilePath(doc.FileName).resolve()==path.resolve() for doc in App.listDocuments().values()):
        raise RuntimeError('Preserve edits and close CTCSS_PCB_CAM before independent reopen inspection')
    doc=App.openDocument(str(path))
    data=json.loads((root/'manufacturing/pcb/carvera-air/cam-inputs.json').read_text())
    bands=len({int(points[0][1]//2) for points in data['legend_hatch']})
    mask_bands=len({int(points[0][1]//10) for points in data['mask_removal']['centerlines']})
    jobs=[doc.Job00_RegistrationPreparation,doc.Job10_BottomCopper,doc.Job20_BottomMaskRemoval,doc.Job30_BottomHoles,doc.Job40_TopLegend]
    assert [len(job.Operations.Group) for job in jobs]==[1,1,mask_bands,3,bands]
    mask_tc=doc.Job20_BottomMaskRemoval.Operations.Group[0].ToolController
    assert mask_tc.ToolNumber==4 and mask_tc.SpindleSpeed==6000
    assert abs(mask_tc.Tool.TipDiameter.Value-0.3)<1e-9
    assert abs(mask_tc.Tool.ShankDiameter.Value-3.175)<1e-9
    assert all(abs(op.FinalDepth.Value+0.2)<1e-9 for op in doc.Job20_BottomMaskRemoval.Operations.Group)
    assert abs(doc.BoreElectrical_0p9.StepDown.Value-.01)<1e-9
    assert abs(doc.BoreElectrical_1p1.StepDown.Value-.03)<1e-9
    summary=doc.getObject('SetupSummary') or doc.getObject('SetupParameters')
    assert summary.get('B19')==hashlib.sha256((root/'electronics/icom-ctcss-board.kicad_pcb').read_bytes()).hexdigest()
    assert summary.get('B20')==hashlib.sha256((root/'manufacturing/pcb/carvera-air/cam-inputs.json').read_bytes()).hexdigest()
    assert abs(float(summary.get('B15'))-LASER_POWER)<1e-9
    assert abs(float(summary.get('B16'))-LASER_FEED)<1e-9
    assert all(abs(op.ToolController.HorizFeed.Value-LASER_FEED/60)<1e-9 for op in doc.Job40_TopLegend.Operations.Group)
    states=[]
    for job in jobs:
        for op in job.Operations.Group:
            assert op.Path.Commands and 'Invalid' not in op.State,op.Name
            states.append({'job':job.Name,'operation':op.Name,'commands':len(op.Path.Commands),'state':list(op.State)})
    centres=[(edge.Curve.Center.x,edge.Curve.Center.y) for edge in doc.ElectricalHoles_1p1.Shape.Edges]
    assert any(abs(x-20.1)<1e-6 and abs(y-40.1)<1e-6 for x,y in centres)
    report={'saved_fcstd_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'reopen':'PASS',
            'native_operations':states,'helix_pitch_mm':[.01,.03],
            'j1_pin1_bottom_jig_mm':[20.1,40.1],'j1_pin1_top_jig_mm':[130.1,40.1],
            'scope':'Native saved project reopens with paths; no fixture/holder simulation or physical qualification.'}
    (root/'docs/verification/pcb-cam-reopen.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

"""Verify current PCB CAM inputs and posted review motion; no machine connection.

Requires gerbonara and Shapely, matching prepare-pcb-cam.py. This is a planar
cutter/path check, not a tool-holder/fixture collision simulation.
"""
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path
import importlib.util
from importlib.metadata import version

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('prepare_pcb_cam',ROOT/'tools/prepare-pcb-cam.py')
geometry=importlib.util.module_from_spec(spec); spec.loader.exec_module(geometry)
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union


def parse(path):
    position={'X':None,'Y':None,'Z':None}
    tool=None; feed=None; moves=[]; changes=[]
    for raw in path.read_text().splitlines():
        line=re.sub(r'\([^)]*\)','',raw).strip()
        if not line: continue
        values={key:float(value) for key,value in re.findall(r'([XYZIJFST])\s*(-?\d+(?:\.\d*)?)',line)}
        if re.search(r'\bM0?6\b',line):
            tool=int(values['T']); changes.append(tool)
        if 'F' in values: feed=values['F']
        match=re.match(r'G(0?[0123])(?:\s|$)',line)
        if not match: continue
        code=int(match[1]); target={a:values.get(a,position[a]) for a in position}
        if all(position[a] is not None and target[a] is not None for a in position):
            points=[(position['X'],position['Y'],position['Z'])]
            if code in (2,3):
                cx=position['X']+values.get('I',0); cy=position['Y']+values.get('J',0)
                radius=math.hypot(position['X']-cx,position['Y']-cy)
                start=math.atan2(position['Y']-cy,position['X']-cx)
                end=math.atan2(target['Y']-cy,target['X']-cx)
                delta=(end-start)%(2*math.pi) if code==3 else -((start-end)%(2*math.pi))
                if abs(delta)<1e-8: delta=(1 if code==3 else -1)*2*math.pi
                # Chord deviation below 0.002 mm; preserve helical Z.
                step=2*math.acos(max(-1,1-0.002/radius)) if radius>0.002 else math.pi/4
                count=max(2,math.ceil(abs(delta)/step))
                points.extend((cx+radius*math.cos(start+delta*i/count),cy+radius*math.sin(start+delta*i/count),position['Z']+(target['Z']-position['Z'])*i/count) for i in range(1,count))
            points.append((target['X'],target['Y'],target['Z']))
            moves.append({'code':code,'tool':tool,'feed':feed,'s':values.get('S'), 'points':points})
        position=target
    return moves,changes


def main():
    folder=ROOT/'manufacturing/pcb/carvera-air'
    data=json.loads((folder/'cam-inputs.json').read_text())
    for name,digest in data['source_hashes'].items():
        assert hashlib.sha256((folder/'native-exports'/name).read_bytes()).hexdigest()==digest
    copper=geometry.artwork(folder/'native-exports/icom-ctcss-board-B_Cu.gbl')
    # Transform unmirrored top-frame copper once to the bottom jig setup.
    from shapely.affinity import affine_transform
    copper=affine_transform(copper,[-1,0,0,1,150.1,0.1])
    result={'scope':'Posted review NC, planar ideal cutter; physical holder/fixture/Z-stack qualification excluded.','files':{}}
    for name in ['00-registration-preparation.nc','10-bottom-copper.nc','20-bottom-mask-removal.nc','25-bottom-legend-drag.nc','40-top-legend-drag.nc','50-bottom-holes.nc']:
        path=folder/'review-nc'/name
        text=path.read_text()
        assert 'G21' in text and 'G54' in text and 'G90 G94' in text and 'M30' in text
        assert 'G28' not in text and 'G91' not in text
        # User's datum strategy: programs select G54 but never redefine it.
        assert not re.search(r'\bG(?:10|92)(?:\.\d+)?(?:\s|$)',text)
        moves,changes=parse(path)
        pts=[p for move in moves for p in move['points']]
        record={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'tool_changes':changes,
                'bounds_mm':{a:[min(p[i] for p in pts),max(p[i] for p in pts)] for i,a in enumerate('XYZ')},
                'parsed_motion_count':len(moves)}
        if name.startswith('00'):
            assert changes==[3]
            assert abs(record['bounds_mm']['Z'][0]+1.65)<1e-6
        elif name.startswith('10'):
            assert changes==[2]
            assert abs(record['bounds_mm']['Z'][0]+0.1)<1e-6
            cuts=[LineString([(x,y) for x,y,z in m['points']]) for m in moves if m['tool']==2 and m['code']!=0 and any(z<0 for x,y,z in m['points']) and len(set((x,y) for x,y,z in m['points']))>1]
            swept=unary_union([line.buffer(geometry.RADIUS,quad_segs=24) for line in cuts])
            overlap=swept.intersection(copper).area
            assert overlap<1e-6,overlap
            record['posted_isolation_copper_overlap_mm2']=overlap
        elif name.startswith('20'):
            mask=data['mask_removal']
            assert changes==[4] and re.search(r'\bM3\s+S6000(?:\D|$)',text)
            assert abs(record['bounds_mm']['Z'][0]+mask['spring_overtravel_below_copper_mm'])<1e-6
            assert 'NO probing except tool-length setting' in text and 'height map' in text
            cuts=[LineString([(x,y) for x,y,z in m['points']]) for m in moves
                  if m['code']!=0 and any(z<0 for x,y,z in m['points'])
                  and len(set((x,y) for x,y,z in m['points']))>1]
            assert cuts and all(m['feed']<=400.0001 for m in moves if m['code']!=0)
            swept=unary_union([line.buffer(mask['envelope_radius_mm'],quad_segs=24) for line in cuts])
            openings=[affine_transform(Polygon(p['opening'][0]),[-1,0,0,1,150.1,0.1]) for p in mask['pads']]
            allowed=unary_union(openings)
            outside=swept.difference(allowed.buffer(0.00003)).area
            assert outside<1e-6,outside
            assert len(openings)==111 and all(swept.intersection(p).area>0.1 for p in openings)
            nominal=unary_union([line.buffer(mask['tip_mm']/2,quad_segs=24) for line in cuts])
            # Check useful clearing on every pad, allowing the deliberately
            # conservative extra masked rim at the nominal spring-tip contact.
            coverage=[nominal.intersection(p).area/p.area for p in openings]
            assert min(coverage)>0.70,min(coverage)
            record.update({'pads_checked':111,'rpm':6000,'feed_mm_min':400,'plunge_mm_min':200,
                           'spring_tool_overtravel_below_original_copper_mm':mask['spring_overtravel_below_copper_mm'],'original_pre_isolation_copper_z0':True,
                           'conservative_envelope_outside_inset_pads_mm2':outside,
                           'minimum_nominal_tip_opening_area_fraction':min(coverage),
                           'process':'Fully cured bottom mask; before electrical drilling. Spring preload and intact copper require physical qualification.'})
        elif name.startswith('50'):
            assert changes==[3]
            support=data['settings']['support_height_above_floor_mm']
            final=support-data['settings']['hole_breakthrough_mm']
            assert abs(record['bounds_mm']['Z'][0]-final)<1e-6
            assert all(z>0 for m in moves for x,y,z in m['points'])
            # Match every cutting endpoint against the original 115 bore/mount
            # circles. The four registration holes must never be recut here.
            holes=[h for h in data['holes'] if h['diameter']<=4]
            assert len(holes)==115
            reached=set()
            for move in moves:
                if move['code']==0: continue
                for x,y,z in move['points']:
                    if z>=support+1.5: continue
                    matches=[i for i,h in enumerate(holes)
                             if math.hypot(x-(150.1-h['x']),y-(h['y']+0.1))<=h['diameter']/2-0.4+0.006]
                    assert len(matches)==1,(x,y,z,matches)
                    reached.update(matches)
            assert len(reached)==115
            record['electrical_and_mount_holes_checked']=len(reached)
            record['reference']='Aluminium floor Z0; no height compensation'
            record['all_tool_tip_motion_above_floor']=True
        else:
            assert changes==[6] and 'M5' in text
            assert not re.search(r'\bM0?[34](?:\s|$)',text)
            executable='\n'.join(re.sub(r'\([^)]*\)','',line) for line in text.splitlines())
            assert not re.search(r'\bS-?\d',executable),'Drag NC must have no spindle-speed words'
            assert 'M321' not in text and 'M322' not in text
            assert abs(record['bounds_mm']['Z'][0]+data['settings']['drag_preload_mm'])<1e-6
            face='bottom' if name.startswith('25') else 'top'
            legend=geometry.artwork(folder/f'native-exports/icom-ctcss-board-{ "B" if face=="bottom" else "F" }_Silkscreen.{ "gbo" if face=="bottom" else "gto" }')
            legend=affine_transform(legend,[-1,0,0,1,150.1,.1] if face=='bottom' else [1,0,0,1,.1,.1])
            from shapely.prepared import prep
            allowed=prep(legend.buffer(.00003))
            cuts=0
            for move in moves:
                xy=math.dist(move['points'][0][:2],move['points'][-1][:2])
                if move['code']==0 and xy>1e-7:
                    assert all(z>=0 for x,y,z in move['points'])
                if move['code']!=0 and xy>1e-7 and any(z<0 for x,y,z in move['points']):
                    assert allowed.covers(LineString([(x,y) for x,y,z in move['points']])),(name,move)
                    assert move['feed']<=data['settings']['drag_feed_mm_min']+.0001
                    cuts+=1
            assert cuts==len(data['bottom_legend_hatch' if face=='bottom' else 'legend_hatch']),(cuts,face)
            record.update({'drag_xy_segments':cuts,'spindle_start_commands':0,'feed_mm_min':300,
                           'initial_preload_mm':data['settings']['drag_preload_mm'],
                           'reference':'New finished-mask Z0; no copper height map',
                           'process':'Conservative first pass; inspect before lowering the independent operation offset. Retain base mask.',
                           'coverage':'Centerline containment in positive legend; actual groove width/pressure and coating removal are physical trial results.'})
        result['files'][name]=record
    (ROOT/'docs/verification/pcb-posted-motion.json').write_text(json.dumps(result,indent=2)+'\n')
    source_paths=sorted(p for p in (ROOT/'electronics').rglob('*') if p.is_file() and
                        (p.suffix in ('.kicad_pcb','.kicad_pro','.kicad_sch','.kicad_mod','.kicad_sym','.kicad_dru') or p.name in ('fp-lib-table','sym-lib-table')) and
                        '.history' not in p.parts and not any(part.endswith('-backups') for part in p.parts))
    digest=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    sources={p.relative_to(ROOT).as_posix():digest(p) for p in source_paths}
    native_manifest={'date':'2026-11-10','source_sha256':sources,
                     'coordinate_policy':'Native unmirrored KiCad plots. FreeCAD applies panel mapping and one face transform.',
                     'physical_copper_layers':['B.Cu'],'holes':{'electrical':111,'enclosure':4,'jig':4},
                     'status':'CAD/CAM migration verified; physical process qualification pending',
                     'files':{p.name:digest(p) for p in sorted((folder/'native-exports').iterdir()) if p.is_file() and p.name!='manifest.json'}}
    (folder/'native-exports/manifest.json').write_text(json.dumps(native_manifest,indent=2)+'\n')
    reports=['final-drc.json','erc-complete.json','final-board-inventory.json','pcb-cam-geometry.json','pcb-cam-jobs.json','pcb-cam-reopen.json','pcb-posted-motion.json','pcb-bottom-legend.json','pcb-inventory-preflight.json','schematic-complete.net']
    drc=json.loads((ROOT/'docs/verification/final-drc.json').read_text())
    violations=drc['violations']+drc['unconnected_items']+drc['schematic_parity']
    erc=json.loads((ROOT/'docs/verification/erc-complete.json').read_text())
    reopened=json.loads((ROOT/'docs/verification/pcb-cam-reopen.json').read_text())
    assert reopened['reopen']=='PASS' and reopened['saved_fcstd_sha256']==digest(ROOT/'mechanical/pcb/icom-ctcss-pcb-cam.FCStd')
    netlist_check=subprocess.check_output(['python',str(ROOT/'tools/check-netlist.py')],cwd=ROOT,text=True)
    assert netlist_check.startswith('PASS:'),netlist_check
    assertion_count=int(re.search(r'(\d+) assertions',netlist_check)[1])
    checks={'DRC_errors':sum(v['severity']=='error' for v in violations),
            'unconnected':len(drc['unconnected_items']),
            'DRC_warnings':sum(v['severity']=='warning' for v in violations),
            'ERC_errors':erc['errors'],'ERC_warnings':erc['warnings'],
            'netlist_assertions':assertion_count,'saved_CAM_reopen':'PASS',
            'posted_planar_copper_overlap_mm2':result['files']['10-bottom-copper.nc']['posted_isolation_copper_overlap_mm2']}
    inventory=json.loads((ROOT/'docs/verification/final-board-inventory.json').read_text())
    bottom_check=json.loads((ROOT/'docs/verification/pcb-bottom-legend.json').read_text())
    assert bottom_check['board_sha256']==digest(ROOT/'electronics/icom-ctcss-board.kicad_pcb')
    assert bottom_check['electrical_geometry_unchanged']
    bottom_artwork=geometry.artwork(folder/'native-exports/icom-ctcss-board-B_Silkscreen.gbo')
    from shapely.geometry import Point
    assert all(bottom_artwork.distance(Point(h['x'],h['y']))-h['diameter']/2>=.25 for h in data['holes'])
    checks['bottom_legend_minimum_hole_clearance_mm']=min(bottom_artwork.distance(Point(h['x'],h['y']))-h['diameter']/2 for h in data['holes'])
    checks['drag_spindle_speed_words']=0
    checks['final_hole_minimum_tool_tip_z_mm']=result['files']['50-bottom-holes.nc']['bounds_mm']['Z'][0]
    assert inventory['board_thickness_matches_stock'] and inventory['rule_area_count']==4
    assert inventory['jig_keepout_status'].startswith('PASS:')
    checks['jig_rule_areas']=inventory['rule_area_count']
    checks['native_thickness_mm']=inventory['saved_board_thickness_mm']
    assert checks['DRC_errors']==checks['unconnected']==checks['ERC_errors']==0
    manifest={'date':'2026-11-10','revision':'In-jig coating, bottom subsystem legend, two-face diamond drag and final floor-referenced holes',
              'source_sha256':sources,'konnect':'0.13.0',
              'freecad':reopened['freecad_version'],
              'geometry_packages':{name:version(name) for name in ['gerbonara','shapely','resvg-py']},
              'kicad':subprocess.check_output(['C:/Program Files/KiCad/10.0/bin/kicad-cli.exe','--version'],text=True).strip(),
              'checks':checks,
              'evidence_sha256':{name:digest(ROOT/'docs/verification'/name) for name in reports},
              'cam_source_sha256':digest(ROOT/'mechanical/pcb/icom-ctcss-pcb-cam.FCStd'),
              'cam_inputs_sha256':digest(folder/'cam-inputs.json'),
              'build_tools_sha256':{name:digest(ROOT/name) for name in ['tools/export-pcb-legends.py','tools/prepare-pcb-cam.py','tools/build-pcb-cam.py','tools/verify-pcb-cam.py','tools/check-final-board.py','tools/check-netlist.py','tools/post/makera_legacy_post.py']},
              'operator_docs_sha256':{name:digest(ROOT/name) for name in ['docs/pcb-fabrication-guide.md','docs/pcb-attempt-log.md','docs/images/pcb-trial-z-references.svg','docs/images/pcb-bottom-subsystems.svg','docs/images/pcb-bottom-subsystems.png','manufacturing/pcb/carvera-air/README.md']},
              'review_NC_sha256':{name:record['sha256'] for name,record in result['files'].items()},
              'preparation_status':'Native PCB and CAM trial preparation verified; physical trial pending; inventory preflight incomplete',
              'native_api_fallback':['Multiline bottom text and mirroring: Konnect output failed native loading; recovered original clean board and used PCB_TEXT API','Clean native legend plotting: Konnect exporter lacks footprint-field/drill-mark suppression options'],
              'historical_evidence_reuse':{'erc-complete.json':'Schematic is unchanged; original ERC run retained, not relabeled as a new run.',
                    'pcb-keepout-fill.json':'Historical controlled fill test; current native inventory and unchanged electrical geometry establish applicability.',
                    'pcb-mask-job.json':'Historical 0.20 mm mask addition record, superseded by current 0.05 mm trial paths.',
                    'pcb-cam-job-split.json':'Historical copper/hole split comparison, not current floor-referenced hole validation.'},
              'mask_tool_profile_sha256':digest(folder/'pcb-mask-removal.fctb'),
              'manufacturing_verdict':'Native and posted trial checks pass; no physical qualification or inventory-completeness claim',
              'open_items':['Physical hole fit, flip repeatability, tool/holder/bed-fixture clearance, protected breakthrough and surface mapping.',
                            'Coating products/layer counts/cures, interlayer adhesion, spring-tool pad exposure and intact copper.',
                            'Two-color diamond-drag contrast with intact base mask; actual pressure/line width, mechanical tool setting and 1/4 inch collet clearance.',
                            'Final sacrificial setup and floor-referenced bores, inventory coverage, assembly/radio acceptance.']}
    (ROOT/'docs/verification/pcb-revision.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()

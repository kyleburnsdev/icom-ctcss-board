"""Create B1's three-plate Bambu Studio project and verify native readback.

Run with ordinary Python after build-bench-holder.py. Uses installed X1C 0.4
profiles, one Generic PLA slot, no network/printer connection. The existing
enclosure packaging helper supplies STL placement and 3MF readback functions.
"""
from pathlib import Path
import importlib.util
import json
import hashlib
import subprocess
import zipfile
import xml.etree.ElementTree as ET
import base64
from collections import Counter, defaultdict
import re

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'manufacturing/bench-holder'
WORK=ROOT/'.agent-scratch/bench-holder-optimization/slicer'
EV=ROOT/'docs/verification/bench-holder'
STUDIO=Path('C:/Program Files/Bambu Studio')
PLATES={
    '01 - TEST FIT - interfaces': [('interfacecoupon',30,40,0),('mountcoupon',30,110,0),('insertcoupon',30,185,0)],
    '02 - FINAL - base': [('base',23,18,0)],
    '03 - FINAL - controls': [('controlpanel',23,35,0),('ledkeeper',30,155,0),
        ('pcbspacer-a',90,155,0),('pcbspacer-b',110,155,0),('pcbspacer-c',130,155,0),('pcbspacer-d',150,155,0)],
}
THREAD_BAND = {'min_z':8.8,'max_z':15.2,
               'range_params':{'layer_height':'0.12','top_shell_layers':'5','bottom_shell_layers':'5'}}


def verify_layer_strategy(archive,report):
    """Check the native range assignments and actual per-object outer-wall Z steps."""
    ranges=ET.fromstring(archive.read('Metadata/layer_config_ranges.xml'))
    ordered=[name for placements in PLATES.values() for name,_,_,_ in placements]
    native={}
    for obj in ranges.findall('object'):
        name=ordered[int(obj.attrib['id'])-1]
        assert name in ('base','mountcoupon')
        entries=obj.findall('range');assert len(entries)==1
        entry=entries[0]
        assert abs(float(entry.attrib['min_z'])-THREAD_BAND['min_z'])<1e-5
        assert abs(float(entry.attrib['max_z'])-THREAD_BAND['max_z'])<1e-5
        options={o.attrib['opt_key']:o.text for o in entry.findall('option')}
        assert options==THREAD_BAND['range_params']
        native[name]={'min_z':float(entry.attrib['min_z']),'max_z':float(entry.attrib['max_z']),'options':options}
    assert set(native)=={'base','mountcoupon'}
    checks=[]
    for number in range(1,4):
        plate_names=[o['name'] for o in json.loads(archive.read(f'Metadata/plate_{number}.json'))['bbox_objects']]
        names={'single':plate_names[0]} if len(plate_names)==1 else {}
        levels=defaultdict(set);current='single' if len(plate_names)==1 else None;height=None;feature=''
        for line in archive.read(f'Metadata/plate_{number}.gcode').decode().splitlines():
            if line.startswith('; Z_HEIGHT:'):height=round(float(line.split(':')[1]),4)
            if line.startswith('; FEATURE:'):feature=line.split(':',1)[1].strip()
            if line.startswith('; start printing object, unique label id:'):current=line.rsplit(':',1)[1].strip()
            if line.startswith('; stop printing object'):current=None
            if current and line.startswith('M624 '):
                mask=int.from_bytes(base64.b64decode(line.split()[1]),'little')
                if mask and mask.bit_count()==1:names[current]=plate_names[mask.bit_length()-1]
            if current and height is not None and feature=='Outer wall' and line.startswith(('G1 ','G2 ','G3 ')):
                values={k:float(v) for k,v in re.findall(r'([XYE])(-?\d*\.?\d+)',line.split(';')[0])}
                if values.get('E',0)>0 and any(k in values for k in 'XY'):levels[current].add(height)
        for key,values in levels.items():
            name=names[key];threaded=name in ('base_1','mountcoupon_1')
            regions={'below':[v for v in sorted(values) if .3<v<8.6],
                     'thread_band':[v for v in sorted(values) if 9.1<v<14.8],
                     'above':[v for v in sorted(values) if v>15.5]}
            measured={}
            for region,zz in regions.items():
                steps=Counter(round(b-a,3) for a,b in zip(zz,zz[1:]))
                expected=.12 if threaded and region=='thread_band' else .2
                assert all(abs(step/expected-round(step/expected))<.01 for step in steps),(name,region,steps)
                if region=='thread_band' and threaded:assert .12 in steps
                measured[region]={str(k):v for k,v in steps.items()}
            checks.append({'plate':number,'name':name,'outer_wall_layer_count':len(values),'steps_mm':measured})
    assert len(checks)==10
    report['native_thread_height_ranges']=native
    report['actual_object_layer_steps']=checks


def main():
    WORK.mkdir(parents=True,exist_ok=True)
    spec=importlib.util.spec_from_file_location('plate_helpers',ROOT/'tools/prepare-enclosure-plates.py')
    helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers)
    helpers.MESHES=OUT
    # arranged_plate's historical p1- prefix is avoided with a small adapter.
    original_mesh=helpers.mesh
    helpers.mesh=lambda path:original_mesh(path.with_name(path.name.removeprefix('p1-')))
    helpers.MESH_NAMES={f'pcbspacer-{s}':'pcbspacer' for s in 'abcd'}
    profiles={p.stem:p for p in (STUDIO/'resources/profiles/BBL').rglob('*.json')}
    def resolve(name):
        d=json.loads(profiles[name].read_text(encoding='utf-8'))
        result=resolve(d['inherits']) if d.get('inherits') else {}
        result.update(d);result.pop('inherits',None)
        return result
    settings={
        'machine':resolve('Bambu Lab X1 Carbon 0.4 nozzle'),
        # Retain the previous installed Fine profile's speed/cooling choices;
        # change layer height without silently adopting unrelated preset changes.
        'process':resolve('0.12mm Fine @BBL X1C'),
        'filament':resolve('Generic PLA'),
    }
    settings['process'].update(wall_loops='4',top_shell_layers='3',bottom_shell_layers='3',
        sparse_infill_density='15%',sparse_infill_pattern='gyroid',layer_height='0.2',
        enable_support='0',brim_width='5',brim_type='outer_only',
        print_settings_id='B1 bench holder - PLA - 0.20 mm - local thread bands',
        line_width='0.45',outer_wall_line_width='0.45',inner_wall_line_width='0.45',
        initial_layer_line_width='0.45',top_surface_line_width='0.45',
        sparse_infill_line_width='0.45',internal_solid_infill_line_width='0.45')
    settings['process']['name']='B1 bench holder - PLA - 0.20 mm - local thread bands'
    settings['process']['from']='User'
    for kind,data in settings.items():
        (WORK/(kind+'.json')).write_text(json.dumps(data,indent=2),encoding='utf-8')
    assembly={'plates':[]}
    report={'revision':'B1','file':'manufacturing/bench-holder/bench-holder-b1.3mf',
            'printer':'Bambu Lab X1 Carbon 0.4 nozzle','filament':'Generic PLA',
            'bed':'Textured PEI Plate','plates':[]}
    for number,(name,placements) in enumerate(PLATES.items(),1):
        folder=WORK/f'plate-{number}'
        records,objects=helpers.arranged_plate(folder,placements)
        for (object_name,_,_,_),obj in zip(placements,objects):
            if object_name in ('base','mountcoupon'):
                obj['height_ranges']=[THREAD_BAND]
        assembly['plates'].append({'plate_name':name,'need_arrange':False,
                                  'plate_params':{'print_sequence':'by layer'},'objects':objects})
        report['plates'].append({'id':number,'name':name,'placements':records})
    request=WORK/'assemble.json';request.write_text(json.dumps(assembly,indent=2),encoding='utf-8')
    filename='bench-holder-b1.3mf'
    command=[str(STUDIO/'bambu-studio.exe'),'--debug','2','--outputdir',str(WORK),
        '--load-settings',str(WORK/'machine.json')+';'+str(WORK/'process.json'),
        '--load-filaments',str(WORK/'filament.json'),'--curr-bed-type','Textured PEI Plate',
        '--load-assemble-list',str(request),'--slice','0','--export-3mf',filename]
    result=subprocess.run(command,cwd=WORK,capture_output=True,timeout=300)
    (WORK/'slicer.log').write_bytes(result.stdout+result.stderr)
    status=json.loads((WORK/'result.json').read_text())
    if result.returncode or status.get('return_code') or len(status.get('sliced_plates',[]))!=3:
        raise RuntimeError(status)
    final=OUT/filename;final.write_bytes((WORK/filename).read_bytes())
    with zipfile.ZipFile(final) as z:
        assert z.testzip() is None
        config=json.loads(z.read('Metadata/project_settings.config'))
        model=ET.fromstring(z.read('Metadata/model_settings.config'))
        assert len(model.findall('object'))==10
        assert len(model.findall('plate'))==3
        assert config['wall_loops']=='4' and config['layer_height']=='0.2'
        assert config['sparse_infill_density']=='15%' and config['enable_support']=='0'
        assert 'PLA' in str(config['filament_type'])
        for i,plate in enumerate(model.findall('plate'),1):
            meta={m.attrib['key']:m.attrib['value'] for m in plate.findall('metadata') if 'key' in m.attrib}
            assert meta['plater_name']==report['plates'][i-1]['name']
            assert f'Metadata/plate_{i}.gcode' in z.namelist()
        forbidden={'wall_loops','layer_height','nozzle_temperature','filament_type','sparse_infill_density'}
        assert not [m.attrib for node in model.findall('object')+model.findall('plate')
                    for m in node.findall('metadata') if m.attrib.get('key') in forbidden]
        report['embedded_settings']=config
    report['slice_result']=status
    report['sha256']=hashlib.sha256(final.read_bytes()).hexdigest()
    helpers.verify_saved_layout(final,report)
    with zipfile.ZipFile(final) as archive:verify_layer_strategy(archive,report)
    report.pop('shared_settings_no_object_or_plate_process_overrides',None)
    report['thread_height_ranges']={'base':THREAD_BAND,'mountcoupon':THREAD_BAND}
    (EV/'slicer.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(status,indent=2))


if __name__=='__main__':main()

"""Prepare and check the two-plate B2 rear-display Bambu Studio project; no printer access.

Run ordinary Python after the FreeCAD builder. Uses installed X1C 0.4 / Fine
and Generic PLA profiles plus the existing native slicer assembly/readback helper.
"""
from pathlib import Path
import importlib.util,json,subprocess,zipfile,hashlib,xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'manufacturing/bench-panel-b2'
WORK=ROOT/'.agent-scratch/panel-rear-display/slicer'
EV=ROOT/'docs/verification/bench-panel-b2'
STUDIO=Path('C:/Program Files/Bambu Studio')
PLATES={
 '01 - TEST FIT - rear display and threads':[
 ('displayfitcoupon',30,40,0),('threadfita',30,145,0),('threadfitb',60,145,0),('threadfitc',90,145,0),
 ('displaythumbscrew-test-a',145,45,0),('displaythumbscrew-test-b',145,75,0),('displaythumbscrew-test-c',145,105,0),('displaythumbscrew-test-d',145,135,0)],
 '02 - FINAL - replacement panel and clamps':[
 ('controlpanel',23,35,0),('displaythumbscrew-a',30,155,0),('displaythumbscrew-b',60,155,0),('displaythumbscrew-c',90,155,0),('displaythumbscrew-d',120,155,0)],
}


def main():
    WORK.mkdir(parents=True,exist_ok=True)
    spec=importlib.util.spec_from_file_location('plate_helpers',ROOT/'tools/prepare-enclosure-plates.py')
    h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    h.MESHES=OUT;h.MESH_NAMES={name:'displaythumbscrew' for rows in PLATES.values() for name,*_ in rows if name.startswith('displaythumbscrew')}
    original=h.mesh
    h.mesh=lambda path:original(path.with_name(path.name.removeprefix('p1-')))
    paths={p.stem:p for p in (STUDIO/'resources/profiles/BBL').rglob('*.json')}
    def resolve(name):
        d=json.loads(paths[name].read_text(encoding='utf-8'))
        result=resolve(d['inherits']) if d.get('inherits') else {}
        result.update(d);result.pop('inherits',None);return result
    settings={'machine':resolve('Bambu Lab X1 Carbon 0.4 nozzle'),
              'process':resolve('0.12mm Fine @BBL X1C'),'filament':resolve('Generic PLA')}
    process=settings['process']
    process.update(name='B2 rear display and printed clamps - PLA - 0.12 mm',from_='User')
    process.pop('from_',None);process['from']='User'
    process.update(print_settings_id=process['name'],layer_height='0.12',initial_layer_print_height='0.20',
        wall_loops='4',top_shell_layers='5',bottom_shell_layers='5',
        sparse_infill_density='30%',sparse_infill_pattern='gyroid',
        enable_support='0',brim_type='outer_only',brim_width='3',
        wall_generator='arachne',outer_wall_speed=['25','25'],inner_wall_speed=['40','40'],
        line_width='0.42',outer_wall_line_width='0.42',inner_wall_line_width='0.42',
        initial_layer_line_width='0.42',top_surface_line_width='0.42',
        sparse_infill_line_width='0.42',internal_solid_infill_line_width='0.42')
    for kind,data in settings.items():(WORK/(kind+'.json')).write_text(json.dumps(data,indent=2))
    assembly={'plates':[]};report={'revision':'B2','printer':'Bambu Lab X1 Carbon 0.4 nozzle',
        'filament':'Generic PLA - user selected existing setup','plates':[]}
    for i,(name,placements) in enumerate(PLATES.items(),1):
        records,objects=h.arranged_plate(WORK/f'plate-{i}',placements)
        assembly['plates'].append({'plate_name':name,'need_arrange':False,'objects':objects})
        report['plates'].append({'id':i,'name':name,'placements':records})
    req=WORK/'assembly.json';req.write_text(json.dumps(assembly,indent=2))
    command=[str(STUDIO/'bambu-studio.exe'),'--debug','2','--outputdir',str(WORK),
        '--load-settings',str(WORK/'machine.json')+';'+str(WORK/'process.json'),
        '--load-filaments',str(WORK/'filament.json'),'--curr-bed-type','Textured PEI Plate',
        '--load-assemble-list',str(req),'--slice','0','--export-3mf','bench-panel-b2.3mf']
    result=subprocess.run(command,cwd=WORK,capture_output=True,timeout=240)
    (WORK/'slicer.log').write_bytes(result.stdout+result.stderr)
    status=json.loads((WORK/'result.json').read_text())
    assert result.returncode==0 and status.get('return_code')==0,status
    assert len(status['sliced_plates'])==2,status
    final=OUT/'bench-panel-b2.3mf';final.write_bytes((WORK/final.name).read_bytes())
    with zipfile.ZipFile(final) as z:
        assert z.testzip() is None
        config=json.loads(z.read('Metadata/project_settings.config'))
        model=ET.fromstring(z.read('Metadata/model_settings.config'))
        assert len(model.findall('object'))==13 and len(model.findall('plate'))==2
        assert config['layer_height']=='0.12' and config['wall_loops']=='4'
        assert config['sparse_infill_density']=='30%' and config['enable_support']=='0'
        assert 'PLA' in str(config['filament_type'])
        for i,p in enumerate(model.findall('plate'),1):
            meta={m.attrib['key']:m.attrib['value'] for m in p.findall('metadata') if 'key' in m.attrib}
            assert meta['plater_name']==report['plates'][i-1]['name']
            assert f'Metadata/plate_{i}.gcode' in z.namelist()
        report['embedded_settings']=config
    h.verify_saved_layout(final,report)
    report['slice_result']=status;report['sha256']=hashlib.sha256(final.read_bytes()).hexdigest()
    report['file']=final.relative_to(ROOT).as_posix()
    (EV/'slicer-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(status,indent=2))

if __name__=='__main__':main()

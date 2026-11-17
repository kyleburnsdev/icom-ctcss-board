"""Prepare a one-object B2/L1 retest project, reusing existing thumb screws.

Run after prepare-bench-panel.py. Native Bambu CLI supplies project metadata and
G-code; the primary B2 and C1 projects retain their own full test plates.
"""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,zipfile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'.agent-scratch/lcd-fit-correction/quick-slicer'
OUT=ROOT/'manufacturing/lcd-fit'
EV=ROOT/'docs/verification/lcd-fit'
STUDIO=Path('C:/Program Files/Bambu Studio')

def main():
    WORK.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    spec=importlib.util.spec_from_file_location('plate_helpers',ROOT/'tools/prepare-enclosure-plates.py')
    h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    h.MESHES=ROOT/'manufacturing/bench-panel-b2';h.MESH_NAMES={}
    original=h.mesh;h.mesh=lambda p:original(p.with_name(p.name.removeprefix('p1-')))
    files={p.stem:p for p in (STUDIO/'resources/profiles/BBL').rglob('*.json')}
    def resolve(name):
        data=json.loads(files[name].read_text(encoding='utf-8'))
        result=resolve(data['inherits']) if data.get('inherits') else {}
        result.update(data);result.pop('inherits',None);return result
    settings={'machine':resolve('Bambu Lab X1 Carbon 0.4 nozzle'),
        'process':resolve('0.12mm Fine @BBL X1C'),'filament':resolve('Generic PLA')}
    p=settings['process'];p.update(name='L1 LCD coupon only - PLA - reuse B2 screws',**{'from':'User'})
    p.update(print_settings_id=p['name'],layer_height='0.12',initial_layer_print_height='0.20',
        wall_loops='4',top_shell_layers='5',bottom_shell_layers='5',sparse_infill_density='30%',
        sparse_infill_pattern='gyroid',enable_support='0',brim_type='outer_only',brim_width='3',
        wall_generator='arachne',outer_wall_speed=['25','25'],inner_wall_speed=['40','40'],
        line_width='0.42',outer_wall_line_width='0.42',inner_wall_line_width='0.42',
        initial_layer_line_width='0.42',top_surface_line_width='0.42',
        sparse_infill_line_width='0.42',internal_solid_infill_line_width='0.42')
    for key,value in settings.items():(WORK/(key+'.json')).write_text(json.dumps(value,indent=2))
    name='01 - RETEST - L1 LCD - reuse four B2 thumb screws'
    rows,objects=h.arranged_plate(WORK/'plate-1',[('displayfitcoupon',50,50,0)])
    req=WORK/'assembly.json';req.write_text(json.dumps({'plates':[{'plate_name':name,'need_arrange':False,'objects':objects}]},indent=2))
    cmd=[str(STUDIO/'bambu-studio.exe'),'--debug','2','--outputdir',str(WORK),
        '--load-settings',str(WORK/'machine.json')+';'+str(WORK/'process.json'),
        '--load-filaments',str(WORK/'filament.json'),'--curr-bed-type','Textured PEI Plate',
        '--load-assemble-list',str(req),'--slice','0','--export-3mf','lcd-fit-l1.3mf']
    proc=subprocess.run(cmd,cwd=WORK,capture_output=True,timeout=240)
    (WORK/'slicer.log').write_bytes(proc.stdout+proc.stderr)
    status=json.loads((WORK/'result.json').read_text())
    assert proc.returncode==0 and status['return_code']==0 and len(status['sliced_plates'])==1,status
    assert not status['sliced_plates'][0]['warning_message'],status
    final=OUT/'lcd-fit-l1.3mf';final.write_bytes((WORK/final.name).read_bytes())
    with zipfile.ZipFile(final) as z:
        assert z.testzip() is None
        meta=ET.fromstring(z.read('Metadata/model_settings.config'))
        assert len(meta.findall('plate'))==1 and len(meta.findall('object'))==1
        config=json.loads(z.read('Metadata/project_settings.config'))
        assert config['layer_height']=='0.12' and config['wall_loops']=='4'
    report={'interface_revision':'L1','plates':[{'id':1,'name':name,'placements':rows}],
        'source_mesh_sha256':hashlib.sha256((h.MESHES/'displayfitcoupon.stl').read_bytes()).hexdigest(),
        'primary_project_sha256':hashlib.sha256(final.read_bytes()).hexdigest(),
        'embedded_settings':config,'slice_result':status,'physical_acceptance':'retest pending'}
    h.verify_saved_layout(final,report)
    (EV/'quick-slicer-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'warning':status['sliced_plates'][0]['warning_message'],
        'minutes':status['sliced_plates'][0]['total_predication']/60,
        'grams':sum(f['total_used_g'] for f in status['sliced_plates'][0]['filaments'])}))

if __name__=='__main__':main()

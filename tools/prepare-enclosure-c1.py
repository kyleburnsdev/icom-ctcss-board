"""Prepare C1 with Bambu Studio's native multi-plate CLI; no printer access.

Run ordinary Python after export-enclosure-c1.py. Reuses the existing saved-layout
readback, but applies the actual 256 mm bed and 3 mm brim rather than P1's more
conservative packing box. Profiles come from the installed Bambu X1C/Generic PLA.
"""
from pathlib import Path
import importlib.util
import hashlib
import json
import math
import struct
import subprocess
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'manufacturing/enclosure-c1'
WORK=ROOT/'.agent-scratch/enclosure-c1/slicer'
EV=ROOT/'docs/verification/enclosure-c1'
STUDIO=Path('C:/Program Files/Bambu Studio')
PLATES={
 '01 - TEST FIT - radio LCD nubs inserts rails':[
  ('displayfitcoupon',25,35,0),('radiopatterncoupon',25,130,0),
  ('coverrailcoupon',150,35,0),('covertonguecoupon',185,35,0),
  ('nubandstrapcoupon',150,90,0),('insertpilotcoupon',150,135,0),
  ('pcbcornerstrap-test',155,175,0),
  *[(f'displayearclip-test-{i}',25+25*i,185,0) for i in range(4)]],
 '02 - FINAL - narrow base': [('base',50,8,0)],
 '03 - FINAL - panel cheeks and retainers':[
  ('controlpanel',25,35,0),('leftradiocheek',25,145,90),('rightradiocheek',120,145,90),
  ('ledkeeper',25,210,0),
  *[(f'pcbcornerstrap-{i}',80+32*i,215,0) for i in range(4)],
  *[(f'displayearclip-{i}',80+27*i,190,0) for i in range(4)]],
 '04 - FINAL - sliding cover and radio saddles':[
  ('slidingcover',25,35,0),('leftradiosaddle',190,35,0),('rightradiosaddle',25,200,90)]
}

def main():
    WORK.mkdir(parents=True,exist_ok=True)
    spec=importlib.util.spec_from_file_location('plate_helpers',ROOT/'tools/prepare-enclosure-plates.py')
    h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    paths={p.stem:p for p in (STUDIO/'resources/profiles/BBL').rglob('*.json')}
    def resolve(name):
        d=json.loads(paths[name].read_text(encoding='utf-8'))
        result=resolve(d['inherits']) if d.get('inherits') else {}
        result.update(d);result.pop('inherits',None);return result
    settings={'machine':resolve('Bambu Lab X1 Carbon 0.4 nozzle'),
              'process':resolve('0.20mm Standard @BBL X1C'),'filament':resolve('Generic PLA')}
    p=settings['process']
    p.update(name='C1 PLA fit prototype - 0.20 mm - 5 walls',**{'from':'User'})
    p.update(print_settings_id=p['name'],layer_height='0.20',initial_layer_print_height='0.20',
        wall_loops='5',top_shell_layers='6',bottom_shell_layers='6',
        sparse_infill_density='30%',sparse_infill_pattern='gyroid',
        enable_support='0',brim_type='outer_only',brim_width='3',
        wall_generator='arachne',outer_wall_speed=['40','40'],inner_wall_speed=['60','60'],
        line_width='0.45',outer_wall_line_width='0.45',inner_wall_line_width='0.45')
    for kind,data in settings.items():(WORK/(kind+'.json')).write_text(json.dumps(data,indent=2))
    assembly={'plates':[]};report={'revision':'C1','printer':'Bambu Lab X1 Carbon 0.4 nozzle',
        'filament':'Generic PLA; explicit user choice','bed':'Textured PEI Plate','plates':[]}
    for i,(name,rows) in enumerate(PLATES.items(),1):
        records,objects=[],[];folder=WORK/f'plate-{i}';folder.mkdir(exist_ok=True)
        for label,tx,ty,angle in rows:
            meshname=label.split('-')[0]
            vs,fs=h.mesh(OUT/'supporting/stl'/(meshname+'.stl'))
            ymax=max(v[1] for v in vs)
            vs=[(ymax-y+tx,x+ty,z) if angle==90 else (x+tx,y+ty,z) for x,y,z in vs]
            bb=[min(v[0] for v in vs),min(v[1] for v in vs),max(v[0] for v in vs),max(v[1] for v in vs)]
            brim=[bb[0]-3,bb[1]-3,bb[2]+3,bb[3]+3]
            assert min(brim[:2])>=5 and max(brim[2:])<=251,(label,brim)
            assert brim[0]>=18 or brim[1]>=28,(label,'X1 excluded corner')
            assert abs(min(v[2] for v in vs))<1e-5 and max(v[2] for v in vs)<256
            for r in records:
                other=r['brim_bounds_mm']
                assert brim[2]<=other[0] or other[2]<=brim[0] or brim[3]<=other[1] or other[3]<=brim[1],(label,r['name'])
            target=folder/(label+'.stl')
            with target.open('wb') as f:
                f.write(b'C1 print-oriented arranged mesh'.ljust(80,b' '));f.write(struct.pack('<I',len(fs)))
                for face in fs:
                    a,b,c=[vs[k] for k in face]
                    u=[b[k]-a[k] for k in range(3)];v=[c[k]-a[k] for k in range(3)]
                    n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
                    length=math.sqrt(sum(q*q for q in n));n=[q/length for q in n] if length else [0,0,0]
                    f.write(struct.pack('<12fH',*n,*a,*b,*c,0))
            records.append({'name':label,'bounds_mm':bb,'brim_bounds_mm':brim,'in_plane_rotation_deg':angle})
            objects.append({'path':str(target),'count':1,'filaments':[1],'pos_x':[0],'pos_y':[0],'pos_z':[0]})
        assembly['plates'].append({'plate_name':name,'need_arrange':False,'objects':objects})
        report['plates'].append({'id':i,'name':name,'placements':records})
    req=WORK/'assembly.json';req.write_text(json.dumps(assembly,indent=2))
    command=[str(STUDIO/'bambu-studio.exe'),'--debug','2','--outputdir',str(WORK),
        '--load-settings',str(WORK/'machine.json')+';'+str(WORK/'process.json'),
        '--load-filaments',str(WORK/'filament.json'),'--curr-bed-type','Textured PEI Plate',
        '--load-assemble-list',str(req),'--slice','0','--export-3mf','ctcss-c1.3mf']
    result=subprocess.run(command,cwd=WORK,capture_output=True,timeout=600)
    (WORK/'slicer.log').write_bytes(result.stdout+result.stderr)
    status=json.loads((WORK/'result.json').read_text())
    assert result.returncode==0 and status.get('return_code')==0,status
    assert len(status['sliced_plates'])==4,status
    final=OUT/'ctcss-c1.3mf';final.write_bytes((WORK/final.name).read_bytes())
    with zipfile.ZipFile(final) as z:
        assert z.testzip() is None
        config=json.loads(z.read('Metadata/project_settings.config'))
        model=ET.fromstring(z.read('Metadata/model_settings.config'))
        assert len(model.findall('object'))==sum(map(len,PLATES.values())) and len(model.findall('plate'))==4
        assert config['wall_loops']=='5' and config['layer_height']=='0.2' and config['enable_support']=='0'
        for i,plate in enumerate(model.findall('plate'),1):
            meta={m.attrib['key']:m.attrib['value'] for m in plate.findall('metadata') if 'key' in m.attrib}
            assert meta['plater_name']==report['plates'][i-1]['name']
            assert f'Metadata/plate_{i}.gcode' in z.namelist()
        report['embedded_settings']=config
    h.verify_saved_layout(final,report)
    report['slice_result']=status;report['sha256']=hashlib.sha256(final.read_bytes()).hexdigest()
    (EV/'slicer-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(status,indent=2))

if __name__=='__main__':main()

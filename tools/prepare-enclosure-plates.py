"""Build one native three-plate P1 enclosure 3MF using local Bambu Studio.

Run with ordinary Python from the repo root. No printer connection is made.
Uses only the standard library; Bambu Studio supplies the slicer/profiles.
"""
from pathlib import Path
import json
import struct
import math
import hashlib
import subprocess
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'manufacturing/enclosure'
MESHES = OUT / 'supporting/stl'
SCRATCH = ROOT / '.agent-scratch/enclosure-p1/plates'
EVIDENCE = ROOT / 'docs/verification/enclosure-p1'
STUDIO = Path('C:/Program Files/Bambu Studio')
PLATES = {
    '01-fascia-and-fit-coupons': [('fascia',25,20,0),('displayinsert',25,97,0),
        ('controlcoupon',25,169,0),('gxcoupon',112,169,0),('mountcoupon',161,169,0),
        ('shaftcoupon',25,218,0),('encoderknob',201,97,0),('ledkeeper',88,221,0),
        ('knobaccentring',201,143,0),('pcbwasher-fit',150,224,0),('wirekeeper-fit',170,205,0)],
    '02-base-and-retainers': [('base',25,35,0),('wirekeeper-a',25,15,0),
        ('wirekeeper-b',70,15,0),('pcbwasher-a',115,15,0),('pcbwasher-b',135,15,0),
        ('pcbwasher-c',155,15,0),('pcbwasher-d',175,15,0)],
    '03-cover': [('cover',25,35,0)],
}
MESH_NAMES = {'pcbwasher-fit':'pcbwasher','wirekeeper-fit':'wirekeeper','wirekeeper-a':'wirekeeper','wirekeeper-b':'wirekeeper',
              **{f'pcbwasher-{c}':'pcbwasher' for c in 'abcd'}}



def mesh(path):
    raw = path.read_bytes()
    count = struct.unpack_from('<I', raw, 80)[0]
    assert len(raw) == 84 + 50 * count, path
    vertices, triangles, ids = [], [], {}
    for i in range(count):
        face = []
        for j in range(3):
            xyz = struct.unpack_from('<3f', raw, 84 + i * 50 + 12 + j * 12)
            if xyz not in ids:
                ids[xyz] = len(vertices)
                vertices.append(xyz)
            face.append(ids[xyz])
        triangles.append(face)
    return vertices, triangles


def arranged_plate(work, placements):
    """Bake the existing print orientations and local XY positions into STLs."""
    records, objects = [], []
    work.mkdir(exist_ok=True)
    for name, tx, ty, angle in placements:
        vertices, faces = mesh(MESHES / f'p1-{MESH_NAMES.get(name,name)}.stl')
        max_y = max(v[1] for v in vertices)
        vertices = [(max_y-y+tx, x+ty, z) if angle == 90 else (x+tx, y+ty, z)
                    for x,y,z in vertices]
        bbox = [min(v[0] for v in vertices), min(v[1] for v in vertices),
                max(v[0] for v in vertices), max(v[1] for v in vertices)]
        expanded = [bbox[0]-5,bbox[1]-5,bbox[2]+5,bbox[3]+5]
        assert expanded[0]>=18 or expanded[1]>=28, (name,'X1 corner exclusion')
        assert expanded[0]>=10 and expanded[1]>=10 and expanded[2]<=246 and expanded[3]<=246, (name,bbox)
        assert abs(min(v[2] for v in vertices))<1e-5
        for other in records:
            bb=other['brim_bounds_mm']
            assert expanded[2]<=bb[0] or bb[2]<=expanded[0] or expanded[3]<=bb[1] or bb[3]<=expanded[1], (name,other)
        records.append({'name':name,'bounds_mm':bbox,'brim_bounds_mm':expanded,'in_plane_rotation_deg':angle})
        path=work/(name+'.stl')
        with path.open('wb') as f:
            f.write(b'CTCSS P1 arranged print mesh'.ljust(80,b' '))
            f.write(struct.pack('<I',len(faces)))
            for face in faces:
                a,b,c=[vertices[i] for i in face]
                u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
                n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
                length=math.sqrt(sum(x*x for x in n))
                normal=[x/length for x in n] if length else [0,0,0]
                f.write(struct.pack('<12fH',*normal,*a,*b,*c,0))
        objects.append({'path':str(path),'count':1,'filaments':[1],
                        'pos_x':[0],'pos_y':[0],'pos_z':[0]})
    return records,objects


def profiles():
    paths={p.stem:p for p in (STUDIO/'resources/profiles/BBL').rglob('*.json')}
    def resolve(name):
        d=json.loads(paths[name].read_text(encoding='utf-8'))
        out=resolve(d['inherits']) if d.get('inherits') else {}
        out.update(d)
        out.pop('inherits',None)
        return out
    for kind,name in [('machine','Bambu Lab X1 Carbon 0.4 nozzle'),
                      ('process','0.20mm Standard @BBL X1C'),('filament','Generic PETG')]:
        d=resolve(name)
        if kind=='process':
            d.update(wall_loops='5',top_shell_layers='6',bottom_shell_layers='6',
                     sparse_infill_density='20%',sparse_infill_pattern='gyroid',layer_height='0.2',
                     line_width='0.45',outer_wall_line_width='0.45',inner_wall_line_width='0.45',
                     initial_layer_line_width='0.45',top_surface_line_width='0.45',
                     sparse_infill_line_width='0.45',internal_solid_infill_line_width='0.45',
                     brim_width='5',brim_type='outer_only',enable_support='0')
        (SCRATCH/(kind+'.json')).write_text(json.dumps(d,indent=2),encoding='utf-8')


def verify_saved_layout(path, report):
    """Read the slicer's saved meshes/transforms, not the staging STLs."""
    ns={'c':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
    prod='{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}'
    def transform(v,s):
        if not s:return v
        m=[float(x) for x in s.split()];x,y,z=v
        return (x*m[0]+y*m[3]+z*m[6]+m[9],
                x*m[1]+y*m[4]+z*m[7]+m[10],
                x*m[2]+y*m[5]+z*m[8]+m[11])
    with zipfile.ZipFile(path) as z:
        docs={name:ET.fromstring(z.read(name)) for name in z.namelist() if name.endswith('.model')}
        objects={(file,o.attrib['id']):o for file,doc in docs.items() for o in doc.findall('c:resources/c:object',ns)}
        config=ET.fromstring(z.read('Metadata/model_settings.config'))
        names={o.attrib['id']:next(m.attrib['value'] for m in o.findall('metadata') if m.attrib.get('key')=='name') for o in config.findall('object')}
        build={o.attrib['objectid']:o for o in docs['3D/3dmodel.model'].findall('c:build/c:item',ns)}
        def points(file,oid,chain):
            obj=objects[file,oid]
            for v in obj.findall('c:mesh/c:vertices/c:vertex',ns):
                vec=tuple(float(v.attrib[k]) for k in 'xyz')
                for t in chain:vec=transform(vec,t)
                yield vec
            for c in obj.findall('c:components/c:component',ns):
                yield from points(c.attrib.get(prod+'path',file).lstrip('/'),c.attrib['objectid'],[c.attrib.get('transform')]+chain)
        for plate,expected in zip(config.findall('plate'),report['plates']):
            checks=[];origin=None
            for instance in plate.findall('model_instance'):
                meta={m.attrib['key']:m.attrib['value'] for m in instance.findall('metadata')}
                oid=meta['object_id'];name=names[oid].removesuffix('_1')
                bb_expected=next(p['bounds_mm'] for p in expected['placements'] if p['name']==name)
                pp=list(points('3D/3dmodel.model',oid,[build[oid].attrib.get('transform')]))
                bb=[min(v[0] for v in pp),min(v[1] for v in pp),max(v[0] for v in pp),max(v[1] for v in pp)]
                delta=[bb[0]-bb_expected[0],bb[1]-bb_expected[1]]
                if origin is None:origin=delta
                assert max(abs(a-b) for a,b in zip(delta,origin))<0.001,(name,delta,origin)
                local=[bb[0]-origin[0],bb[1]-origin[1],bb[2]-origin[0],bb[3]-origin[1]]
                assert max(abs(a-b) for a,b in zip(local,bb_expected))<0.001,(name,local,bb_expected)
                assert abs(min(v[2] for v in pp))<0.001
                checks.append({'name':name,'local_bounds_mm':local,'z_min_mm':min(v[2] for v in pp)})
            expected['saved_layout_readback']=checks
            expected['slicer_plate_origin_mm']=origin
        assert all(next(m.attrib['value'] for m in o.findall('metadata') if m.attrib.get('key')=='extruder')=='1' for o in config.findall('object'))
        forbidden={'wall_loops','layer_height','nozzle_temperature','filament_type','sparse_infill_density'}
        assert not [m.attrib for o in config.findall('object') for m in o.findall('metadata') if m.attrib.get('key') in forbidden]
        assert not [m.attrib for p in config.findall('plate') for m in p.findall('metadata') if m.attrib.get('key') in forbidden]
        report['shared_settings_no_object_or_plate_process_overrides']=True


def main():
    SCRATCH.mkdir(parents=True,exist_ok=True)
    profiles()
    assembly={'plates':[]}
    report={'revision':'P1','packaging':'single multi-plate project',
            'printer':'Bambu Lab X1 Carbon 0.4 nozzle','filament':'Generic PETG',
            'bed':'Textured PEI Plate','total_plate_count':3,'enclosure_plate_count':3,
            'packing':'5 mm brim allowance; X/Y10..246; X1 excluded corner avoided.',
            'plates':[]}
    for number,(label,placements) in enumerate(PLATES.items(),1):
        placed,objects=arranged_plate(SCRATCH/label,placements)
        assembly['plates'].append({'plate_name':label,'need_arrange':False,
                                   'plate_params':{'print_sequence':'by layer'},'objects':objects})
        report['plates'].append({'id':number,'name':label,'placements':placed})
    assembly_path=SCRATCH/'assemble.json'
    assembly_path.write_text(json.dumps(assembly,indent=2),encoding='utf-8')
    final=OUT/'p1-enclosure.3mf'
    command=[str(STUDIO/'bambu-studio.exe'),'--debug','2','--outputdir',str(SCRATCH),
             '--load-settings',str(SCRATCH/'machine.json')+';'+str(SCRATCH/'process.json'),
             '--load-filaments',str(SCRATCH/'filament.json'),
             '--curr-bed-type','Textured PEI Plate','--load-assemble-list',str(assembly_path),
             '--slice','0','--export-3mf',final.name]
    result=subprocess.run(command,cwd=SCRATCH,capture_output=True,timeout=240)
    status=json.loads((SCRATCH/'result.json').read_text())
    assert result.returncode==0 and status.get('return_code')==0 and (SCRATCH/final.name).exists(),status
    assert len(status['sliced_plates'])==3,status
    final.write_bytes((SCRATCH/final.name).read_bytes())
    with zipfile.ZipFile(final) as z:
        assert z.testzip() is None
        config=json.loads(z.read('Metadata/project_settings.config'))
        model=ET.fromstring(z.read('Metadata/model_settings.config'))
        plates=model.findall('plate')
        assert len(plates)==3 and len(model.findall('object'))==sum(map(len,PLATES.values()))
        assert config['wall_loops']=='5' and config['brim_width']=='5' and config['enable_support']=='0'
        for number,(plate,expected) in enumerate(zip(plates,report['plates']),1):
            meta={m.attrib['key']:m.attrib['value'] for m in plate.findall('metadata') if 'key' in m.attrib}
            assert int(meta['plater_id'])==number and meta['plater_name']==expected['name'],meta
            assert len(plate.findall('model_instance'))==len(expected['placements'])
            assert f'Metadata/plate_{number}.gcode' in z.namelist()
        report['embedded_settings']=config
    report['file']=str(final.relative_to(ROOT)).replace('\\','/')
    report['sha256']=hashlib.sha256(final.read_bytes()).hexdigest()
    report['slice_result']=status
    verify_saved_layout(final,report)
    (EVIDENCE/'multi-plate-checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('One native 3MF project: three plates, nineteen objects, three successful slices.',flush=True)
    return report


if __name__=='__main__':
    main()

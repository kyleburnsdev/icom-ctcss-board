"""Check the retained wiring snapshots and guide, or accept a fresh netlist.

Usage: python tools/check-wiring-guide.py [--netlist PATH]
Standard library only. Does not read or modify KiCad source graphs.
Source file hashes identify the revision; net connectivity comes from exports.
"""
from pathlib import Path
import argparse,csv,json,re,hashlib,shutil
root=Path(__file__).resolve().parents[1];out=root/'docs/verification/wiring-guide'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--netlist',type=Path)
args=parser.parse_args()
src=args.netlist or out/'schematic.net'
previous=out/'checks.json'
if previous.exists() and args.netlist is None:
    old=json.loads(previous.read_text())['sha256']
    for source in ('electronics/icom-ctcss-board.kicad_pcb','electronics/icom-ctcss-board.kicad_sch'):
        assert hashlib.sha256((root/source).read_bytes()).hexdigest()==old[source], (
            'Source changed: refresh Konnect pad readback and pass a fresh schematic --netlist',source)
if src.resolve() != (out/'schematic.net').resolve():
    shutil.copyfile(src,out/'schematic.net')
tokens=iter(re.findall(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+',src.read_text()))
def read(t=None):
    t=next(tokens) if t is None else t
    if t!='(': return json.loads(t) if t.startswith('"') else t
    r=[]
    for t in tokens:
        if t==')':return r
        r.append(read(t))
    raise ValueError('Unclosed netlist expression')
tree=read();nets=next(x for x in tree if isinstance(x,list) and x[0]=='nets')
pins={}
for net in nets[1:]:
    name=next(x[1] for x in net if isinstance(x,list) and x[0]=='name')
    for node in net:
        if isinstance(node,list) and node[0]=='node':
            f={x[0]:x[1] for x in node[1:] if isinstance(x,list)}
            pins[f['ref'],f['pin']]=name
headers=json.loads((out/'header-readback.json').read_text())['headers']
rows=list(csv.DictReader((root/'docs/reference/final-product-wire-list.csv').open()))
doc=(root/'docs/final-product-wiring-guide.md').read_text(encoding='utf-8')
count=0
for h in headers:
    assert h['source']=='file'
    for p in h['pads']:
        key=(h['reference'],p['number'])
        r=next(r for r in rows if (r['header'],r['pin'])==key)
        assert r['net']==p['net']==pins[key],(key,r['net'],p['net'],pins[key])
        assert '`'+r['wire_id']+'`' in doc
        count+=1
assert count==31
assert len({r['wire_id'] for r in rows})==32
assert sum(r['populated']=='yes' and r['header']!='Local' for r in rows)==30
assert next(r for r in rows if r['wire_id']=='J3-4')['populated']=='no'
assert next(r for r in rows if r['wire_id']=='ENC-GND-LINK')['destination']=='EC11 C to identified push-switch S2'
for p in '12348':assert pins['J1',p]==pins['J2',p]
assert pins['J1','5']!=pins['J2','5']
assert pins['J1','2']==pins['U1','24']!=pins['U1','21']==pins['J4','2']
for h,p in [('J1','6'),('J1','7'),('J2','6'),('J2','7'),('J6','2'),('J6','4')]:assert pins[h,p]=='GND'
for h,p,r,p2 in [('J6','1','R6','2'),('J6','3','R7','2')]:assert pins[h,p]==pins[r,p2]
def slug(s):
    s=s.lower().replace('`','')
    s=re.sub(r'[^\w\s-]','',s)
    return s.replace(' ','-')
links=0
for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',doc):
    if target.startswith(('https:','http:')):continue
    path,_,anchor=target.partition('#')
    dest=(root/'docs'/path) if path else root/'docs/final-product-wiring-guide.md'
    assert dest.exists(),target
    if anchor:
        headings=re.findall(r'^#+\s+(.+)$',dest.read_text(encoding='utf-8'),re.M)
        assert anchor in [slug(s) for s in headings],(target,[slug(s) for s in headings])
    links+=1
files=['electronics/icom-ctcss-board.kicad_pcb','electronics/icom-ctcss-board.kicad_sch',
       'firmware/icom_ctcss/config.h','docs/requirements/board-specification.md',
       'docs/implementation/component-sourcing-review.md','docs/final-product-wiring-guide.md',
       'docs/reference/final-product-wire-list.csv','docs/verification/wiring-guide/header-readback.json',
       'docs/verification/wiring-guide/schematic.net','tools/render-wiring-guide.py',
       'tools/check-wiring-guide.py','tools/render-wiring-hardware.py']
files += [p.relative_to(root).as_posix() for p in sorted((root/'docs/images/wiring').glob('*.png'))]
report=dict(date='2026-11-16',result='pass',header_positions_checked=count,
    populated_board_contacts=30,local_encoder_jumpers=1,csv_rows=32,
    local_guide_links_and_anchors_checked=links,figures=len(list((root/'docs/images/wiring').glob('*.png'))),
    checks=['All CSV header nets match retained Konnect saved-PCB pads and Eeschema exported netlist',
            'MIC/RADIO pass-through and intercepted PTT checked',
            'RAW versus regulated VCC and LED series-resistor nets checked',
            'Every row represented in guide; J3-4 empty; local encoder jumper included',
            'Guide local links and anchors resolve'],
    tool='Eeschema 10.0.0 netlist export via Konnect; Python documentation checks; Pillow 12.0.0',
    physical_checks='Not run: harness construction, adapter mapping, encoder contacts, power/radio/mechanical acceptance',
    sha256={f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in files})
(out/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))

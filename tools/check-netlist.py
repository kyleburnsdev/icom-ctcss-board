"""Check the completed schematic's exported netlist, never KiCad source files."""
import json
import re
from pathlib import Path

path = Path(__file__).resolve().parents[1] / 'docs' / 'verification' / 'schematic-complete.net'
tokens = iter(re.findall(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+', path.read_text()))

def read(first=None):
    token = next(tokens) if first is None else first
    if token != '(':
        return json.loads(token) if token.startswith('"') else token
    result = []
    for token in tokens:
        if token == ')':
            return result
        result.append(read(token))
    raise ValueError('Unclosed expression')

tree = read()
nets = next(x for x in tree if isinstance(x, list) and x[0] == 'nets')
by_pin = {}
for net in nets[1:]:
    name = next(x[1] for x in net if isinstance(x, list) and x[0] == 'name')
    for node in net:
        if isinstance(node, list) and node[0] == 'node':
            fields = {x[0]: x[1] for x in node[1:] if isinstance(x, list)}
            by_pin[fields['ref'], fields['pin']] = name

checks = 0
def same(*pins):
    global checks
    actual = {by_pin[p] for p in pins}
    assert len(actual) == 1, (pins, actual)
    checks += 1

for pin in ('1', '2', '3', '4', '8'):
    same(('J1', pin), ('J2', pin))
same(('J1', '6'), ('J1', '7'), ('J2', '6'), ('J2', '7'), ('Q1', '1'))
assert by_pin['J1', '5'] != by_pin['J2', '5']
checks += 1
same(('J1', '5'), ('R8', '1'))
same(('R8', '2'), ('R9', '2'), ('TP7', '1'))
same(('Q1', '3'), ('J2', '5'), ('TP8', '1'))
same(('Q1', '2'), ('R10', '2'), ('R11', '1'))
same(('R1', '2'), ('R2', '1'), ('C1', '1'))
same(('R2', '2'), ('R3', '1'), ('C2', '1'), ('TP5', '1'))
same(('R3', '2'), ('R4', '1'))
same(('C3', '2'), ('R5', '1'))
same(('R5', '2'), ('J1', '1'), ('J2', '1'), ('TP6', '1'))
same(('R6', '2'), ('J6', '1'))
same(('R7', '2'), ('J6', '3'))
same(('J6', '2'), ('J6', '4'), ('J1', '6'))
same(('J5', '2'), ('J1', '6'))
for reference, expected in (('J5', {'1','2'}), ('J6', {'1','2','3','4'})):
    assert {pin for ref,pin in by_pin if ref==reference}==expected
    assert by_pin[reference,'1'] != by_pin[reference,'2']
    checks += 1
for resistor, pin in (('R12', '1'), ('R13', '2'), ('R14', '3')):
    same((resistor, '2'), ('J3', pin))
same(('R15', '2'), ('J5', '1'))
same(('RV1', '3'), ('R3', '2'), ('R4', '1'))
same(('RV1', '1'), ('Q1', '1'))
same(('RV1', '2'), ('C3', '1'))
for pin, other in {
    '3': ('J1', '6'), '4': ('J1', '6'), '23': ('J1', '6'),
    '5': ('J4', '3'), '6': ('J4', '4'),
    '7': ('J3', '1'), '8': ('J3', '2'), '9': ('J3', '3'),
    '10': ('R8', '2'), '11': ('R10', '1'), '12': ('R1', '1'),
    '13': ('J5', '1'), '18': ('R6', '1'),
    '19': ('R7', '1'), '21': ('J4', '2'), '24': ('J1', '2'),
}.items():
    same(('U1', pin), other)
same(('C4', '1'), ('U1', '24'))
same(('C5', '1'), ('C6', '1'), ('U1', '21'))
assert by_pin['U1', '21'] != by_pin['U1', '24']
checks += 1
for pin in ('1', '2', '14', '15', '16', '17', '20', '22'):
    name = by_pin['U1', pin]
    assert name.startswith('unconnected-'), (pin, name)
    checks += 1
components = next(x for x in tree if isinstance(x, list) and x[0] == 'components')
assert len(components) - 1 == 38
references = {next(x[1] for x in c if isinstance(x, list) and x[0] == 'ref') for c in components[1:]}
assert 'R16' not in references
assert not any('OFFSET' in name for name in by_pin.values())
assert sum(name == by_pin['U1','17'] for name in by_pin.values()) == 1
checks += 3
assert all(next(x[1] for x in c if isinstance(x, list) and x[0] == 'footprint').startswith('CTCSS_THT:') for c in components[1:])
checks += 2
print(f'PASS: {checks} assertions; 38 components, complete U1/RV1, A0 unused, CNC footprints assigned.')

"""Build face-readable, positive color SVG/PDF trial art; no transfer mirroring.

Requires gerbonara, shapely, reportlab, pypdf, resvg-py.
Read tools/README.md for the native metadata export prerequisite.
"""
import hashlib
import json
from collections import defaultdict
from pathlib import Path
import re

from gerbonara import GerberFile
from gerbonara.utils import MM
from shapely.geometry import Polygon, box, Point, LineString
from shapely.ops import unary_union
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor
from reportlab.graphics.svgpath import SvgPath
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, DictionaryObject
import resvg_py

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'manufacturing/pcb/sublimation'
EXPORTS = ROOT / 'manufacturing/pcb/carvera-air/native-exports'
META = ROOT / 'docs/verification/sublimation-board-metadata.json'
COLORS = {'neutral': '#263445', 'power': '#b43a12', 'ground': '#175c9c',
          'logic': '#14733f', 'analog': '#7438a4', 'status': '#9b285c'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def category(text):
    t = text.upper()
    if t.startswith(('CONTROL /', 'PTT IN /', 'PTT OUT /', 'UI /')):
        return 'logic'
    if 'GND' in t or 'SHLD' in t:
        return 'ground'
    if any(v in t for v in ('+5V', '+8V', 'POWER', '8V INPUT', 'C4 ', 'C5 ', 'C6 ')):
        return 'power'
    if any(v in t for v in ('MIX', 'AUDIO', 'FILTER', 'LEVEL', 'VOLTAGE', 'R1 ', 'R2 ', 'R3 ', 'R4 ', 'R5 ', 'C1 ', 'C2 ', 'C3 ', 'RV1 ')) or re.search(r'\bMIC\b', t):
        return 'analog'
    if any(v in t for v in ('LED', 'STATUS')):
        return 'status'
    if any(v in t for v in ('PTT', 'BYP', 'CONTROL', 'UI ', 'ENCODER', 'SDA', 'SCL', 'CLK')) or re.search(r'\bD\d+\b', t):
        return 'logic'
    return 'neutral'


def geometry(path):
    result = Polygon()
    dark = []
    for obj in GerberFile.open(path).objects:
        for prim in obj.to_primitives(unit=MM):
            p = prim.to_arc_poly().approximate_arcs(max_error=0.002)
            poly = Polygon([(x-50, -y-50) for x, y in p.outline])
            if not poly.is_valid:
                raise ValueError('Invalid exported geometry')
            if prim.polarity_dark:
                dark.append(poly)
            else:
                result = unary_union([result, *dark]).difference(poly)
                dark = []
    return unary_union([result, *dark])


def polygon_path(shape):
    polygons = [shape] if shape.geom_type == 'Polygon' else list(getattr(shape, 'geoms', []))
    return ' '.join('M'+' L'.join(f'{x:.5f},{y:.5f}' for x, y in ring.coords)+' Z'
                    for p in polygons if p.geom_type == 'Polygon' and not p.is_empty
                    for ring in [p.exterior, *p.interiors])


def svg_document(width, height, shapes):
    paths = '\n'.join(f'<g id="{name}"><title>{name}</title><path d="{polygon_path(shape)}" fill="{color}" fill-rule="evenodd"/></g>'
                      for name, color, shape in shapes if not shape.is_empty)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}mm" height="{height}mm" viewBox="0 0 {width} {height}">\n'
            '<title>Positive sublimation artwork - printer handles transfer mirroring</title>\n'+paths+'\n</svg>\n')


def pdf_document(path, width, height, shapes, title):
    c = canvas.Canvas(str(path), pagesize=letter, invariant=1)
    c.setTitle(title+' / UNMIRRORED / white mask')
    c.setAuthor('icom-ctcss-board')
    c.scale(mm, mm)
    cx, cy = letter[0]/mm/2, letter[1]/mm/2
    ox, oy = cx-width/2, cy-height/2
    c.setFont('Helvetica-Bold', 13/mm)
    c.drawCentredString(cx, 263, title)
    c.setFont('Helvetica', 9/mm)
    c.drawCentredString(cx, 256, 'POSITIVE / UNMIRRORED FILE / printer performs transfer mirror')
    c.drawCentredString(cx, 250, 'Letter / Actual size 100% / no Fit / one transfer per sheet')
    # SVG y-down to PDF y-up conversion only; no transfer reflection.
    d = Drawing(width, height)
    for _, color, shape in shapes:
        if not shape.is_empty:
            item = SvgPath(polygon_path(shape), fillColor=HexColor(color), strokeColor=None)
            item.fillMode = 0  # even-odd: preserve enclosed counters
            d.add(item)
    c.saveState()
    c.translate(ox, oy+height)
    c.scale(1, -1)
    renderPDF.draw(d, c, 0, 0)
    c.restoreState()
    c.setStrokeColor(HexColor('#263445'))
    c.setLineWidth(0.15)
    for x in (ox, ox+width):
        for y in (oy, oy+height):
            sx, sy = (-1 if x == ox else 1), (-1 if y == oy else 1)
            c.line(x+sx, y, x+sx*4, y)
            c.line(x, y+sy, x, y+sy*4)
    c.setFont('Helvetica', 9/mm)
    c.drawCentredString(cx, oy-9, f'{width:.2f} x {height:.2f} mm between corner tick centers')
    c.drawCentredString(cx, 24, 'Trim away page labels and crop marks before pressing. White = white mask.')
    c.drawCentredString(cx, 18, 'Trial only: qualify dye uptake, coating adhesion and heat cycle on a coupon first.')
    c.showPage()
    c.save()
    writer = PdfWriter()
    writer.clone_document_from_reader(PdfReader(path))
    writer._root_object[NameObject('/ViewerPreferences')] = DictionaryObject({NameObject('/PrintScaling'): NameObject('/None')})
    with path.open('wb') as f:
        writer.write(f)


def coupon():
    """Small independent process coupon: no assembly pinout claims."""
    shapes = []
    for i, (name, color) in enumerate(COLORS.items()):
        shapes.append((name+'-swatch', color, box(3+i*8, 3, 9+i*8, 9)))
        for j, w in enumerate((0.10, 0.15, 0.20, 0.30)):
            shapes.append((f'{name}-line-{w}', color, box(3+i*8, 12+j*2, 9+i*8, 12+j*2+w)))
    # Asymmetric F and L are immediately recognizable if reversed.
    shapes += [('orientation-F', COLORS['neutral'], unary_union([box(4, 22, 5, 34), box(4, 22, 12, 23), box(4, 27, 10, 28)])),
               ('orientation-L', COLORS['power'], unary_union([box(16, 22, 17, 34), box(16, 33, 24, 34)])),
               ('white-knockout', COLORS['analog'], box(29, 22, 39, 34).difference(box(31, 24, 37, 32))),
               ('gray-patch', '#808080', box(43, 22, 51, 34))]
    return shapes


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    meta = json.loads(META.read_text())
    manifest = json.loads((EXPORTS/'manifest.json').read_text())
    for rel, expected in manifest['source_sha256'].items():
        if digest(ROOT/rel) != expected:
            raise ValueError('Stale native exports: '+rel)
    if meta['board_sha256'] != digest(ROOT/'electronics/icom-ctcss-board.kicad_pcb'):
        raise ValueError('Stale native text metadata')
    if digest(ROOT/meta['top_plot']['path']) != meta['top_plot']['sha256']:
        raise ValueError('Changed sublimation top plot')
    for name, expected in manifest['files'].items():
        if digest(EXPORTS/name) != expected:
            raise ValueError('Changed export: '+name)
    evidence = {'status': 'Digital trial artwork; no physical qualification',
                'transfer_mirror_applied': False, 'printer_transfer_mirror': 'automatic, user supplied',
                'palette': COLORS, 'board_sha256': meta['board_sha256'],
                'native_exports_manifest_sha256': digest(EXPORTS/'manifest.json'),
                'metadata_sha256': digest(META),
                'subtitle_override': meta['subtitle_override'],
                'test_point_guide': meta['test_point_guide'],
                'silkscreen_faces': ['top'], 'bottom_legend': 'none', 'faces': {}}
    face, layer = 'top', 'F.Silkscreen'
    whole = geometry(ROOT/meta['top_plot']['path'])
    remaining = whole
    colored = defaultdict(list)
    for text in meta['texts']:
        if text['layer'] != layer:
            continue
        region = box(*text['bounds']).buffer(0.015)
        part = remaining.intersection(region)
        colored[category(text['text'])].append(part)
        remaining = remaining.difference(region)
    colored['neutral'].append(remaining)
    exclusions = []
    for pad in meta['pads']:
        x, y = pad['center']
        if pad['reference'] in ('H5', 'H6', 'H7', 'H8'):
            exclusions.append(Point(x, y).buffer(max(pad['drill_mm'])/2+1, quad_segs=32))
    exclusion = unary_union(exclusions)
    groups = []
    final = Polygon()
    for name, color in COLORS.items():
        shape = unary_union(colored[name]).difference(exclusion).intersection(box(0, 0, 100, 150))
        final = final.union(shape)
        groups.append((name, color, shape))
    if final.intersection(exclusion).area > 1e-7:
        raise ValueError('Ink in excluded pad/registration area')
    frame = box(*meta['test_point_guide_bounds']).buffer(0.65, join_style=2)
    border = frame.boundary.buffer(0.06, join_style=2)
    if border.intersects(whole) or frame.intersects(exclusion):
        raise ValueError('Test-point guide frame overlaps legend/keepout')
    for pad in meta['pads']:
        if frame.intersects(box(*pad['bounds'])):
            raise ValueError('Test-point guide overlaps pad: '+pad['reference'])
    envelopes = ROOT/'docs/verification/final-board-inventory.json'
    body_clearances = {}
    for body in json.loads(envelopes.read_text())['body_envelopes']:
        bounds = [v-50 for v in body['bounds']]
        if frame.intersects(box(*bounds)):
            raise ValueError('Test-point guide covered by body: '+body['reference'])
        body_clearances[body['reference']] = frame.distance(box(*bounds))
    evidence['guide_layout'] = {
        'portrait_bounds_mm': list(frame.bounds),
        'body_envelopes_sha256': digest(envelopes),
        'minimum_selected_body_clearance_mm': min(body_clearances.values()),
        'pad_and_jig_clearance': 'no overlap',
        'font_height_mm': 0.8, 'row_pitch_mm': 1.45,
    }
    groups.append(('test-point-guide-frame', COLORS['neutral'], border))
    w, h = 100, 150
    (OUT/f'{face}-color.svg').write_text(svg_document(w, h, groups), encoding='utf-8')
    pdf_document(OUT/f'{face}-color-letter.pdf', w, h, groups, f'CTCSS / {face.upper()} COLOR LEGEND')
    preview = svg_document(w, h, groups).replace(f'width="{w}mm" height="{h}mm"', f'width="{w*10}" height="{h*10}"')
    preview = preview.replace('</title>', '</title><rect width="100%" height="100%" fill="white"/>', 1)
    (ROOT/f'docs/images/pcb-sublimation-{face}.png').write_bytes(resvg_py.svg_to_bytes(svg_string=preview))
    evidence['faces'][face] = {'size_mm': [w, h], 'native_legend_ink_area_mm2': round(final.area, 8),
                              'total_printed_ink_area_mm2': round(unary_union([g[2] for g in groups]).area, 8),
                              'excluded_ink_area_mm2': round(final.intersection(exclusion).area, 8),
                              'removed_ink_area_mm2': round(max(0, whole.area-final.area), 8),
                              'j1_pin1_face_mm': [40, 130]}
    shapes = coupon()
    (OUT/'transfer-coupon.svg').write_text(svg_document(54, 38, shapes), encoding='utf-8')
    pdf_document(OUT/'transfer-coupon-letter.pdf', 54, 38, shapes, 'CTCSS / WHITE MASK TRANSFER COUPON')
    evidence['files'] = {name: digest(OUT/name) for name in
                         ('top-color.svg', 'top-color-letter.pdf',
                          'transfer-coupon.svg', 'transfer-coupon-letter.pdf')}
    evidence['generator_sha256'] = digest(Path(__file__))
    (ROOT/'docs/verification/pcb-sublimation.json').write_text(json.dumps(evidence, indent=2)+'\n', encoding='utf-8')
    print('Created top legend and coupon SVG/PDF pairs and one top preview. No transfer mirroring.')


if __name__ == '__main__':
    main()

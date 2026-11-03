"""Generate a folded, double-layer negative legend PDF (reportlab and pypdf).

Run from any directory: python tools/create-legend-print-test.py
Uses the existing native SVG export; never changes KiCad sources.
"""
from pathlib import Path
import hashlib
import xml.etree.ElementTree as ET

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import white
from reportlab.graphics import renderPDF
from reportlab.graphics.svgpath import SvgPath
from reportlab.graphics.shapes import Drawing
from pypdf import PdfReader, PdfWriter
from pypdf.generic import DictionaryObject, NameObject

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'manufacturing/pcb/carvera-air/native-exports/icom-ctcss-board-top-legend.svg'
OUTPUT = ROOT / 'manufacturing/pcb/carvera-air/print-masks/top-legend-negative-100x150mm.pdf'

# Millimetres, measured from the Letter page's lower-left. The rotated field
# is 150 x 100; both fields and all targets reflect about the same fold axis.
MASK_X = (letter[0] / mm - 150) / 2
MASK_Y = 40.0
FOLD_Y = 143.0


def draw_mask(c, drawing):
    """Draw the original 100 x 150 mm field in its native print orientation."""
    c.saveState()
    clip = c.beginPath()
    clip.rect(0, 0, 100, 150)
    c.clipPath(clip, stroke=0, fill=0)
    c.setFillColorRGB(0, 0, 0)
    c.rect(0, 0, 100, 150, stroke=0, fill=1)
    c.translate(-50, 200)
    renderPDF.draw(drawing, c, 0, 0)
    c.restoreState()


def draw_copy(c, drawing, mirrored=False):
    c.saveState()
    if mirrored:
        c.translate(0, 2 * FOLD_Y)
        c.scale(1, -1)
    c.translate(MASK_X, MASK_Y)
    # Clockwise 90 degrees: original (u,v) -> page (x+v,y+100-u).
    c.saveState()
    c.translate(0, 100)
    c.rotate(-90)
    draw_mask(c, drawing)
    c.restoreState()
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(0.15)
    for xx in (0, 150):
        for yy in (0, 100):
            sx, sy = (-1 if xx == 0 else 1), (-1 if yy == 0 else 1)
            c.line(xx + sx, yy, xx + sx * 3, yy)
            # Keep marks within the 3 mm half-gap at the fold.
            c.line(xx, yy + sy, xx, yy + sy * 2)
    for index, (xx, yy) in enumerate(((-5, 7), (155, 7), (-5, 93), (155, 93))):
        c.circle(xx, yy, 1.3, stroke=1, fill=0)
        if index == 0:
            c.circle(xx, yy, 2, stroke=1, fill=0)
        c.line(xx - 2.5, yy, xx + 2.5, yy)
        c.line(xx, yy - 2.5, xx, yy + 2.5)
    c.restoreState()


def main():
    svg = ET.parse(SOURCE).getroot()
    # This exporter uses a vertical reflection. Fail on a changed coordinate
    # contract rather than silently producing a displaced or mirrored mask.
    assert svg.attrib['viewBox'] == '50 -200 100 150'
    group = list(svg)
    assert len(group) == 1
    assert group[0].attrib['transform'] == 'translate(50.0 -50.0) scale(1 -1) translate(-50.0 200.0)'
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=letter, pageCompression=1)
    c.setTitle('CTCSS top legend - folded double-layer negative - 100 x 150 mm')
    c.setAuthor('icom-ctcss-board')
    c.setSubject('Two rotated vector masks reflected across a fold; print at actual size')
    x, y = MASK_X, MASK_Y
    c.scale(mm, mm)
    c.setFont('Helvetica-Bold', 13 / mm)
    c.drawCentredString(letter[0] / mm / 2, 268, 'TOP LEGEND / FOLD TO DOUBLE')
    c.setFont('Helvetica', 9 / mm)
    c.drawCentredString(letter[0] / mm / 2, 262, 'Letter / 100% Actual size / no Fit / no printer mirroring / simplex')
    # SVG viewport + group reflection, converted to PDF's upward Y axis:
    # PDF local (x, y) = (source x - 50, source y + 200).
    drawing = Drawing(100, 150)
    for elem in group[0]:
        assert elem.tag.endswith('path') and elem.attrib['fill'] == 'none'
        assert elem.attrib['stroke'] == 'black'
        shape = SvgPath(elem.attrib['d'], fillColor=None, strokeColor=white,
                        strokeWidth=float(elem.attrib['stroke-width']),
                        strokeLineCap=1, strokeLineJoin=1)
        drawing.add(shape)
    draw_copy(c, drawing)
    draw_copy(c, drawing, mirrored=True)

    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)
    c.setLineWidth(0.15)
    c.setDash(1, 1.5)
    c.rect(x - 10, 32, 170, 222, stroke=1, fill=0)
    c.setDash(3, 1)
    c.line(x - 10, FOLD_Y, x + 160, FOLD_Y)
    c.setDash()
    c.setFont('Helvetica-Bold', 7 / mm)
    c.drawCentredString(x + 75, 249, 'B / MIRRORED COPY - fold down onto A, toner faces together')
    c.drawCentredString(x + 75, 35, 'A / BASE COPY - keep flat; match all four targets before creasing')
    c.setFont('Helvetica', 6 / mm)
    c.drawCentredString(x + 75, FOLD_Y + 0.7, 'FOLD - DO NOT CUT')

    # Independent dimension references: measure between tick centres.
    c.line(x, 27, x + 150, 27)
    for xx in (x, x + 150):
        c.line(xx, 25.5, xx, 28.5)
    c.setFont('Helvetica', 7 / mm)
    c.drawCentredString(x + 75, 23, '150.00 mm between tick centres / dotted outer trim: 170 x 222 mm')
    c.line(x - 15, y, x - 15, y + 100)
    for yy in (y, y + 100):
        c.line(x - 16.5, yy, x - 13.5, yy)
    c.saveState()
    c.translate(x - 18, y + 50)
    c.rotate(90)
    c.drawCentredString(0, 0, '100.00 mm between tick centres')
    c.restoreState()
    c.setFont('Helvetica', 7 / mm)
    for line, yy in zip([
        'BLACK = block UV / WHITE = clear film. Measure both axes before trimming.',
        'Fold B onto A; align targets and fine text, then tape margins. Keep the hinge intact.',
        'Two-layer exposure experiment; opacity, print scale and exposure need trial acceptance.',
        'Source: native top-legend SVG / SHA256 ' + hashlib.sha256(SOURCE.read_bytes()).hexdigest()[:16],
    ], [18, 14, 10, 6]):
        c.drawCentredString(letter[0] / mm / 2, yy, line)
    c.showPage()
    c.save()
    reader = PdfReader(OUTPUT)
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    writer._root_object[NameObject('/ViewerPreferences')] = DictionaryObject({NameObject('/PrintScaling'): NameObject('/None')})
    with OUTPUT.open('wb') as stream:
        writer.write(stream)
    result = PdfReader(OUTPUT)
    assert len(result.pages) == 1
    assert tuple(float(v) for v in result.pages[0].mediabox) == (0, 0, 612, 792)
    print(f'Created {OUTPUT}; 2 x {len(list(group[0]))} white vector paths; '
          'two 150 x 100 mm fields, reflected about y=143 mm.')


if __name__ == '__main__':
    main()

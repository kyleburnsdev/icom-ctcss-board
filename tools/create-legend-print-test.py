"""Generate the unmirrored negative legend PDF. Requires reportlab and pypdf.

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
    c.setTitle('CTCSS top legend - negative - 100 x 150 mm - unmirrored')
    c.setAuthor('icom-ctcss-board')
    c.setSubject('Paper scaling test; black blocks UV, white transmits UV on clear film')
    x = (letter[0] / mm - 100) / 2
    y = 65.0
    c.scale(mm, mm)
    c.setFont('Helvetica-Bold', 13 / mm)
    c.drawCentredString(letter[0] / mm / 2, 252, 'TOP LEGEND / NEGATIVE MASK')
    c.setFont('Helvetica', 9 / mm)
    c.drawCentredString(letter[0] / mm / 2, 245, '100 x 150 mm artwork - no mirror - Letter paper')
    c.drawCentredString(letter[0] / mm / 2, 239, 'Print Actual size / 100%. Disable Fit and driver scaling.')

    c.saveState()
    c.translate(x, y)
    clip = c.beginPath()
    clip.rect(0, 0, 100, 150)
    c.clipPath(clip, stroke=0, fill=0)
    c.setFillColorRGB(0, 0, 0)
    c.rect(0, 0, 100, 150, stroke=0, fill=1)
    # SVG viewport + group reflection, converted to PDF's upward Y axis:
    # PDF local (x, y) = (source x - 50, source y + 200).
    c.translate(-50, 200)
    drawing = Drawing(100, 150)
    for elem in group[0]:
        assert elem.tag.endswith('path') and elem.attrib['fill'] == 'none'
        assert elem.attrib['stroke'] == 'black'
        shape = SvgPath(elem.attrib['d'], fillColor=None, strokeColor=white,
                        strokeWidth=float(elem.attrib['stroke-width']),
                        strokeLineCap=1, strokeLineJoin=1)
        drawing.add(shape)
    renderPDF.draw(drawing, c, 0, 0)
    c.restoreState()

    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)
    c.setLineWidth(0.15)
    # Crop marks lie on the exact edge extensions; none enter the mask.
    for xx in (x, x + 100):
        for yy in (y, y + 150):
            sx = -1 if xx == x else 1
            sy = -1 if yy == y else 1
            c.line(xx + sx * 2, yy, xx + sx * 8, yy)
            c.line(xx, yy + sy * 2, xx, yy + sy * 8)
    # Mid-edge alignment ticks, also entirely outside the mask.
    for xx in (x, x + 100):
        sx = -1 if xx == x else 1
        c.line(xx + sx * 2, y + 75, xx + sx * 6, y + 75)
    for yy in (y, y + 150):
        sy = -1 if yy == y else 1
        c.line(x + 50, yy + sy * 2, x + 50, yy + sy * 6)

    # Independent dimension references: measure between tick centres.
    c.line(x, y - 13, x + 100, y - 13)
    for xx in (x, x + 100):
        c.line(xx, y - 15, xx, y - 11)
    c.setFont('Helvetica', 9 / mm)
    c.drawCentredString(x + 50, y - 19, '100.00 mm between tick centres')
    c.line(x - 13, y, x - 13, y + 150)
    for yy in (y, y + 150):
        c.line(x - 15, yy, x - 11, yy)
    c.saveState()
    c.translate(x - 19, y + 75)
    c.rotate(90)
    c.drawCentredString(0, 0, '150.00 mm between tick centres')
    c.restoreState()
    c.setFont('Helvetica', 8 / mm)
    for line, yy in zip([
        'BLACK = leave uncured. WHITE = cure (clear / unprinted on transparency).',
        'Measure both references before trimming. Crop marks define the exact rectangle.',
        'Paper scaling test only; printer accuracy and exposure process are not qualified.',
        'Source: native top-legend SVG / SHA256 ' + hashlib.sha256(SOURCE.read_bytes()).hexdigest()[:16],
    ], [35, 30, 25, 20]):
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
    print(f'Created {OUTPUT}; {len(list(group[0]))} white vector paths; exact 100 x 150 mm field.')


if __name__ == '__main__':
    main()

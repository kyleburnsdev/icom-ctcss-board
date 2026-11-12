"""Export sublimation text metadata/art with KiCad Python; never save the board.

Konnect does not expose board-text bounding boxes needed for semantic coloring.
"""
import hashlib
import json
from pathlib import Path

import pcbnew

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'electronics/icom-ctcss-board.kicad_pcb'
board = pcbnew.LoadBoard(str(SOURCE))
if board is None:
    raise RuntimeError('Cannot load saved board')

# The color artwork has a finished-board subtitle rather than the machining
# note retained in the original monochrome source. Use KiCad's text renderer
# to preserve the native font, centering and stroke geometry in this derivative.
old_subtitle = 'SELECTABLE CTCSS | 5V PRO MICRO | CNC B.Cu ONLY'
new_subtitle = 'SELECTABLE CTCSS | 5V PRO MICRO'
matches = [d for d in board.GetDrawings() if isinstance(d, pcbnew.PCB_TEXT)
           and d.GetLayer() == pcbnew.F_SilkS and d.GetText() == old_subtitle]
if len(matches) != 1:
    raise RuntimeError('Expected exactly one original top subtitle')
matches[0].SetText(new_subtitle)

# The sublimation design has no bottom silkscreen. The old monochrome board
# remains the historical machining source; omit its backside notes entirely
# from this derivative and the associated metadata.
bottom_items = [d for d in board.GetDrawings() if d.GetLayer() == pcbnew.B_SilkS]
for item in bottom_items:
    board.Remove(item)

# Put useful bench guidance in the open space above the Pro Micro, replacing
# the decorative waveform. Keep the point IDs and nets bound to this revision.
test_point_rows = [
    ('TP1', 'GND', 'TP1 GND - PROBE RETURN'),
    ('TP2', '+8V', 'TP2 RAW - +8V INPUT'),
    ('TP3', '+5V', 'TP3 VCC - +5V RAIL'),
    ('TP4', '/PWM_D9', 'TP4 PWM - RAW D9'),
    ('TP5', '/FILTER_2', 'TP5 FILTER - SMOOTH TONE'),
    ('TP6', '/MIC_AUDIO', 'TP6 MIX - MIC + TONE'),
    ('TP7', '/PTT_SENSE_D7', 'TP7 SENSE - LOW = PTT'),
    ('TP8', '/RADIO_PTT', 'TP8 PTT OUT - LOW = KEYED'),
]
for ref, net, _ in test_point_rows:
    pads = [p for f in board.GetFootprints() if f.GetReference() == ref for p in f.Pads()]
    if len(pads) != 1 or pads[0].GetNetname() != net:
        raise RuntimeError('Test-point assignment changed: '+ref)


def add_legend_text(text, x, y, size=0.8):
    item = pcbnew.PCB_TEXT(board)
    item.SetText(text)
    item.SetLayer(pcbnew.F_SilkS)
    item.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x+50), pcbnew.FromMM(y+50)))
    item.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(size), pcbnew.FromMM(size)))
    item.SetTextThickness(pcbnew.FromMM(0.12))
    item.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
    board.Add(item)
    return item


legend_items = [add_legend_text('TEST POINT GUIDE', 41, 20, 0.9)]
for index, (_, _, label) in enumerate(test_point_rows):
    legend_items.append(add_legend_text(label, 41, 22+index*1.45))
export_dir = ROOT / 'manufacturing/pcb/sublimation/source'
export_dir.mkdir(parents=True, exist_ok=True)
plot = pcbnew.PLOT_CONTROLLER(board)
options = plot.GetPlotOptions()
options.SetOutputDirectory(str(export_dir))
options.SetPlotReference(False)
options.SetPlotValue(False)
options.SetDrillMarksType(pcbnew.DRILL_MARKS_NO_DRILL_SHAPE)
options.SetUseAuxOrigin(False)
options.SetMirror(False)
plot.SetLayer(pcbnew.F_SilkS)
if not plot.OpenPlotfile('sublimation-top', pcbnew.PLOT_FORMAT_GERBER,
                         'Finished-board subtitle; positive unmirrored artwork'):
    raise RuntimeError('Cannot open sublimation plot')
top_plot = Path(plot.GetPlotFileName())
if not plot.PlotLayer():
    raise RuntimeError('Cannot plot sublimation top legend')
plot.ClosePlot()


def bounds(item):
    b = item.GetBoundingBox()
    return [b.GetX()/1e6-50, b.GetY()/1e6-50,
            b.GetRight()/1e6-50, b.GetBottom()/1e6-50]


data = {
    'board_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'kicad_version': pcbnew.GetBuildVersion(),
    'subtitle_override': {'original': old_subtitle, 'printed': new_subtitle},
    'silkscreen_faces': ['top'],
    'omitted_historical_bottom_items': len(bottom_items),
    'test_point_guide': [{'reference': ref, 'net': net, 'printed': label}
                         for ref, net, label in test_point_rows],
    'test_point_guide_bounds': [min(bounds(t)[0] for t in legend_items),
                              min(bounds(t)[1] for t in legend_items),
                              max(bounds(t)[2] for t in legend_items),
                              max(bounds(t)[3] for t in legend_items)],
    'top_plot': {'path': top_plot.relative_to(ROOT).as_posix(),
                 'sha256': hashlib.sha256(top_plot.read_bytes()).hexdigest()},
    'coordinate_frame': 'Top portrait: x=Kx-50, y=Ky-50; mm; y down',
    'texts': [{'text': d.GetText(), 'layer': d.GetLayerName(), 'bounds': bounds(d)}
              for d in board.GetDrawings() if isinstance(d, pcbnew.PCB_TEXT)
              and d.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS)],
    'pads': [{'reference': f.GetReference(), 'number': p.GetNumber(),
              'net': p.GetNetname(), 'bounds': bounds(p),
              'center': [p.GetPosition().x/1e6-50, p.GetPosition().y/1e6-50],
              'drill_mm': [p.GetDrillSize().x/1e6, p.GetDrillSize().y/1e6]}
             for f in board.GetFootprints() for p in f.Pads()],
}
out = ROOT / 'docs/verification/sublimation-board-metadata.json'
out.write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')
print(f'Read {len(data["texts"])} texts and {len(data["pads"])} pads; PCB unchanged')

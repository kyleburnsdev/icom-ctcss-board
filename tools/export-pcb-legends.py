"""Export clean native legends with KiCad's bundled Python, without source writes.

Konnect export_gerber has no switch to omit duplicate footprint references/values.
Use this native plotting API for that unsupported option after normal exports.
"""
from pathlib import Path
import pcbnew

root=Path(__file__).resolve().parents[1]
board=pcbnew.LoadBoard(str(root/'electronics/icom-ctcss-board.kicad_pcb'))
if board is None:
    raise RuntimeError('KiCad could not load the saved board')
plot=pcbnew.PLOT_CONTROLLER(board)
options=plot.GetPlotOptions()
options.SetOutputDirectory(str(root/'manufacturing/pcb/carvera-air/native-exports'))
options.SetPlotReference(False)
options.SetPlotValue(False)
options.SetDrillMarksType(pcbnew.DRILL_MARKS_NO_DRILL_SHAPE)
options.SetUseAuxOrigin(False)
options.SetMirror(False)
options.SetUseGerberProtelExtensions(True)
for layer,suffix in [(pcbnew.F_SilkS,'F_Silkscreen'),(pcbnew.B_SilkS,'B_Silkscreen')]:
    plot.SetLayer(layer)
    if not plot.OpenPlotfile(suffix,pcbnew.PLOT_FORMAT_GERBER,'Positive legend; no duplicate footprint fields or drill marks'):
        raise RuntimeError('Could not open native plot: '+suffix)
    if not plot.PlotLayer():
        raise RuntimeError('Could not plot: '+suffix)
    plot.ClosePlot()
print('Exported native F.SilkS / B.SilkS legends without modifying sources.')

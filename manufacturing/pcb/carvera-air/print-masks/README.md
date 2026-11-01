# Negative legend paper scaling test

[Print the PDF](top-legend-negative-100x150mm.pdf) on Letter paper. The artwork
rectangle is exactly **100 x 150 mm** in the PDF. Black means leave uncured;
white means cure (unprinted, transparent film in a later exposure test).
The existing top-legend SVG is inverted in colour only, without mirroring.

| Step | Material / holding | Action / next check |
| --- | --- | --- |
| Print | Letter paper in printer | Actual size / 100%; disable Fit and driver scaling |
| Measure | Cooled sheet flat on bench | Measure horizontal 100 mm and vertical 150 mm tick-centre spans |
| Trim | Sheet on cutting mat | Use external corner marks to trim the 100 x 150 mm rectangle |

Use a ruler or calipers, straightedge, cutting mat and knife or paper trimmer.
The PDF itself illustrates the trim lines through external crop marks and
provides independent dimension references. Mid-edge ticks help alignment.
Measure before trimming so the references remain available. Check both axes;
record actual measurements. If correction is needed, the scale multiplier is
intended length divided by measured length. A single percentage works only
when both axes require the same correction. Do not call the physical print
dimensionally accepted merely because the print dialog says 100%.

This is a scaling test, not a qualified exposure process or replacement of the
current machining instructions. Paper is sufficient for this test. A future
transparency must be measured separately after printing and cooling.

Generated with [the reusable script](../../../../tools/create-legend-print-test.py)
using Python, ReportLab and pypdf. It uses
[the existing native SVG](../native-exports/icom-ctcss-board-top-legend.svg).
The PDF source hash is printed in its footer. Verified: one Letter page,
100 x 150 mm vector field, 1,141 white source paths, external trim marks,
and visually inspected rendered page. Printer scaling has not yet been measured.

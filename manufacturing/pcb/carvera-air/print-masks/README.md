# Folded double-layer negative legend mask

[Print the mask PDF](top-legend-negative-100x150mm.pdf), then follow the
[illustrated printing, folding and exposure guide](../../../../docs/folded-mask-guide.md).

One Letter page contains two exact **150 x 100 mm** fields: the existing
100 x 150 mm legend rotated clockwise, plus its reflection across the fold.
Four paired targets, a fold line, outer trim boundary and independent
100/150 mm measurement references are included. Retain **170 x 222 mm** of
film, folding to **170 x 111 mm**. Black blocks UV; white is unprinted film.
Print Actual size / 100%, simplex, without Fit or printer mirroring.

The user reported that the single toner layer did not sufficiently block UV.
This is the next two-layer exposure experiment; opacity and exposure settings
have not yet been physically accepted.

Regenerate with `python tools/create-legend-print-test.py` from the repository
root (Python, ReportLab and pypdf). The [generator](../../../../tools/create-legend-print-test.py)
uses the [native legend SVG](../native-exports/icom-ctcss-board-top-legend.svg)
without changing the PCB. See the guide for current verification and physical checks.

# PCB CAM source

Open `icom-ctcss-pcb-cam.FCStd` in FreeCAD 1.1.1. Native jobs contain preparation
pockets, independent bottom isolation and hole jobs, and top laser-hatch bands with editable tool
controllers. ManufacturingGeometry holds Gerber-derived geometry; the setup
summary records the process; cell B15 supplies laser power to the dedicated
post, while laser feed is set in the native tool controller. Mark fully UV-cured
white mask at provisional 5% power and 500 mm/min, one pass at 0.05 mm hatch.
Qualify the cleaned first full board; no separate legend coupon.

Use the [manufacturing instructions](../../manufacturing/pcb/carvera-air/README.md).
CAD/CAM migration checks pass, including enforced PCB rule areas and matching
1.5 mm native thickness. Physical machining/setup acceptance remains pending.
Review NC is delivered separately.

The hole job can be repeated after both coating stages, before assembly, using
the original pre-isolation copper G54 datum and protected breakthrough. Do not
capture any subsequent work zero. It excludes registration holes. Job 20 opens
111 bottom pads using the Makera spring-loaded mask remover before initial
electrical drilling. Its Z−0.20 mm is spring-tool overtravel below known copper,
not intended copper removal. Physical preload/removal qualification is pending.

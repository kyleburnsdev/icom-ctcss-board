# PCB implementation

The saved board is 100 × 150 mm: KiCad X50–150, Y50–200 mm. There are
38 circuit parts, 111 electrical pads, 242 B.Cu track segments, no routing vias
or jumpers, and no copper pours. Ordinary tracks are 0.5 mm; power/ground buses
are 1 mm; design clearance is 0.5 mm. These dimensions remain first-board CNC
targets; coupon checks establish the physical milling process.

Physical stock, saved KiCad thickness and the FreeCAD CAM model all use 1.5 mm.

## Mechanical interfaces

H1–H4 are enclosure mounts: 4 mm NPTH at (56,56), (144,56), (144,194),
(56,194) mm. Their placement and the board outline preserve the enclosure interface.
H5–H8 are separate jig registration holes. Their coordinates, finished fits and
single face transform are specified in the [manufacturing workflow](pcb-jig-and-freecad-cam.md).

The new holes have 1 mm body-clearance allowances represented by courtyards on
both faces. Native inventory finds a minimum 2.46 mm from a jig-hole edge to a
selected component-body envelope. This is nominal CAD geometry, not measured
pin fit or holder clearance. Four footprint-owned rule areas enforce exclusion
of tracks, vias, pads, copper fills and other footprints on both copper layers.
The saved library definitions retain the same areas. Native API creation was
used only for these unsupported Konnect operations and the thickness setting.
The [controlled zone-fill check](../verification/pcb-keepout-fill.json) confirms
the reserved region stays free of copper after refill.

## Electrical layout

All physical copper is on the bottom. KiCad's normalized THT pads include virtual
F.Cu lands; the selected manufacturing export excludes F.Cu. Every hole is
physically unplated, including holes in the CAD PTH drill file.

Ground uses buses and branches. The filter/divider/trimmer branch and LCD/UI
trunk reach the PTT/radio-ground junction separately upstream; some PTT return
remains shared. The jig migration changes no electrical components or tracks.
J5 is BYPASS/GND; J6 provides PTT LED+/GND/BYPASS LED+/GND. U1 A0 is unused.

The module/socket envelope is 37 × 18.24 mm including 3 mm socket strips.
Minimum selected-body spacing is 2.14 mm; C4/C5 to the module allowance is
2.38 mm. The Q1 footprint matches the selected factory-formed 2N3904TAR.
Capacitor envelopes follow the [sourcing review](component-sourcing-review.md).
Actual socket, cable and populated assembly fits remain prototype checks.

## Current evidence

[PCB inventory](../verification/final-board-inventory.json),
[DRC](../verification/final-drc.json) and the
[revision manifest](../verification/pcb-revision.json) identify the saved design.
DRC reports zero errors and zero unconnected items, retaining 115 warnings:
38 circuit-footprint library comparisons, 35 footprint-field/artwork overlaps,
and 42 schematic metadata/mechanical parity warnings. Jig footprints are marked
board-only. No new jig-hole or relocated legend warning remains.

Use the [assembly drawing](../reference/assembly-top.svg),
[bottom view](../reference/copper-bottom.svg) and
[manufacturing package](../../manufacturing/pcb/carvera-air/README.md).
Drawings are references, not machine toolpaths. The saved FreeCAD jobs and
review NC have separate CAM checks and pending physical acceptance.

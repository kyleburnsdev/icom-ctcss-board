# PCB jig and FreeCAD CAM workflow

Implementation verified 2026-10-29. The saved PCB includes all four jig holes
and enforced all-copper keepouts; native KiCad thickness and FreeCAD CAM both
use 1.5 mm. Editable CAM jobs use **Robust MCP Server**. Native sources, current
exports and posted review NC have revision-specific checks. Physical setup and
process qualification remain open; review NC is not released machine work.

Konnect is preferred for supported operations. Footprint keepouts and board
thickness used KiCad's native API because Konnect provides no writers for them,
under the user's standing fallback rule. Both saved board and project libraries
retain the keepouts. Native readback, DRC and a controlled fill check verify them.

## Board and enclosure interfaces

Keep the 100 × 150 mm finished PCB, 1.5 mm single-sided stock, B.Cu-only routing,
through-hole assembly, no jumpers or pours, and the four existing corner
mounting holes. The 150 × 100 mm blank fits the jig's intended interface.
Two-face registration benefits bottom milling and top coating/legend work;
it does not require a second copper layer.

Keep the enclosure's existing supports and corner mounting interface. Add the
jig holes separately rather than moving enclosure mounts. Recheck underside
support, screw/washer clearance and component envelopes against the revised PCB;
do not regenerate the enclosure or print project unless that review finds a change.

## PCB jig interface

H5–H8 are independent NPTH registration holes with courtyards and footprint-owned
keepout rule areas. H1–H4 remain enclosure mounts. The four rule areas exclude
tracks, vias, pads, copper fills and other footprints on F.Cu and B.Cu. P1–P4 below name fixture positions, not electrical connectors.

The mapping preserves the existing native KiCad orientation. For KiCad
coordinates K in mm, panel-local top-view coordinates are
**x = Ky − 50, y = Kx − 50**. Native Gerber has Y upward, so its equivalent is
**x = −GerberY − 50, y = GerberX − 50**. Recheck the actual export origin before
using this equation on regenerated artwork.

| Position | Panel x,y mm | KiCad Kx,Ky mm | Nominal finished hole for measured 4.000 mm pin |
| --- | --- | --- | --- |
| P1 / H5 | 20,20 | 70,70 | 4.03 mm |
| P2 / H6 | 130,20 | 70,180 | 4.03 mm |
| P3 / H7 | 20,70 | 120,70 | 4.12 mm |
| P4 / H8 | 130,70 | 120,180 | 4.12 mm |

Specify P1/P2 at measured pin diameter +0.02 to +0.04 mm and P3/P4 at
+0.10 to +0.15 mm. Record the measured pins and qualified finished-hole process;
nominal tool diameter alone is not acceptance. Start with 1 mm clearance beyond
the hole edge for copper and component bodies, increasing it for cutter reach
or access. Include explicit copper-zone exclusions even though this board has
no pours. Leave vertical access for the setup-only 4 × 20 mm PCB pins.

The [current native inventory](../verification/final-board-inventory.json)
verifies all eight mechanical holes and nominal selected-body clearance. The
new jig-hole edges clear those envelopes by at least 2.46 mm. The geometry
preparation also checks ideal isolation cutter sweep against merged copper.
Perform machining on an unpopulated board; all four PCB pins are withdrawn
before cutting. Holder and remaining fixture projections require a separate
collision review. Enclosure mounts and outline are unchanged.

The full-size circuit needs no smaller-board carrier or separation tabs by
default. If a later revision shrinks the circuit, retain the complete 150 × 100 mm
carrier and all four registration holes until every registered operation is done.
Separate carrier boundary, finished circuit outline and final separation paths.

## Coordinate and setup contract

The jig pocket is 150.20 × 100.20 mm. Panel-to-jig mapping is
**Jx = x + 0.10, Jy = y + 0.10**; J origin is pocket lower-left / Anchor 1 work XY0.
Do not add wall offsets or substitute firmware homing coordinates.

Flip about the Y-parallel midline: **x′ = 150 − x, y′ = y**;
in jig coordinates **Jx′ = 150.20 − Jx, Jy′ = Jy**. Do not rotate the blank
180 degrees or flip about X. Apply the face transform once in FreeCAD setup
geometry; keep native exports unmirrored. Verify all four centers and an
asymmetric circuit feature, such as J1 pin 1, on both faces. Only native, unmirrored exports are maintained. Transformed geometry exists
inside the FreeCAD setup; reference bottom-view SVGs are not CAM inputs.

## Current trial CAM — 2026-11-10

The [fabrication guide](../pcb-fabrication-guide.md) is the operator procedure.
The [package README](../../manufacturing/pcb/carvera-air/README.md) gives native
settings and regeneration. This candidate supersedes the earlier all-operations
copper datum, early drilling and laser legend sequence for the next attempt.

| Native job | Reference and purpose |
| --- | --- |
| Job00_RegistrationPreparation | Independent copper-top setup on sacrificial wasteboard; skip for accepted prepared blank |
| Job10_BottomCopper | Exposed bottom copper Z0 + thorough height map; isolate only |
| Job20_BottomMaskRemoval | Same undisturbed bond, copper Z0 and map after all bottom coats; no intervening probing except tool-length setting |
| Job25_BottomLegend | Optional execution; if skipped, proceed from pad clearing directly to the flip. If used: new finished-mask Z0; nonrotating diamond drag reveals base color through contrasting outer coats |
| Job40_TopLegend | After Y-axis flip and in-jig coating/curing; new top mask-surface Z0; nonrotating diamond drag |
| Job50_BottomHoles | After both faces; new aluminium-floor Z0 with board removed, sacrificial backing, bottom-up remount; no height map |

All coating/curing stays in the jig; keep seating unchanged through each face's
pad clearing. Only tool-length setting is allowed between copper mapping and
pad clearing, preserving that zero/map. Copper mapping is disabled for mask-
referenced legends and floor-referenced holes. Keep jig XY unchanged.

Use conservative first passes for pad clearing and both legends. Native
SetupSummary exposes initial 0.05 mm overtravel/preload and independent repeat
offsets: MaskPassOffset, BottomDragPassOffset and TopDragPassOffset. After
cleaning/inspection, lower only the applicable operation offset slightly,
recompute/export/recheck and repeat if needed. Spring compression changes
pressure; it is not a guaranteed removal depth. Do not overwrite saved datums.

The final hole job models 1 mm underside support and 0.15 mm breakthrough:
PCB underside +1.00, copper plane +2.50, minimum tip +0.85 mm above aluminium
floor zero. All posted hole motion must stay positive; no copper height map is
used. The 0.8 mm corn bit interpolates 111 electrical holes and four enclosure
mounts. Registration holes are excluded. No perimeter cut is needed on this
finished-size full-board blank. Adapt support settings if materially different;
do not turn this hobby setup into an unnecessary tolerance-analysis exercise.

The source remains mechanical/pcb/icom-ctcss-pcb-cam.FCStd, generated with native
FreeCAD operations through Robust MCP Server. ManufacturingGeometry stores
artwork-derived wires; SetupSummary gives settings and source hashes. T6 uses
the owned 6.35 mm shank / selected 90° diamond tip, spindle off. Reference
length and line width describe a matching WidgetWorks model, not measured owned
tool geometry. Diamond contact uses manual/mechanical setting, not electrical
tip probing. See the guide for tools, settings provenance and clearance checks.

## Current verification and physical acceptance

[Bottom legend verification](../verification/pcb-bottom-legend.json) records
native mirrored multiline text and unchanged electrical geometry. Konnect's
multiline writer produced a file KiCad could not load; the clean original board
was recovered and text was added with KiCad's native PCB_TEXT API. No live editor
or unrelated saved board changes were present. Clean native legend plotting also
uses the native API because Konnect export does not expose footprint-field and
drill-mark suppression. Source/library rules and thickness remain intact.

The [revision manifest](../verification/pcb-revision.json) identifies current
native/readback/posted checks and distinguishes historical evidence reuse.
Older mask-addition, job-split and controlled-fill reports keep their original
scope and dates; they are not new validation of this trial's depths or legends.
The unchanged schematic's ERC/netlist evidence remains applicable. Native
geometry and DRC checks do not establish physical coating removal or fixture fit.

Use the [attempt log](../pcb-attempt-log.md) to capture coat/cure details,
pressure adjustments, usable pad exposure, interlayer adhesion, readable
contrasting legends with retained base mask, hole fit and electrical checks.
The inventory helper report has incomplete stock/capability coverage and is not
a stock-completeness pass. No machine was operated or physical trial accepted.
Keep the workflow local until successful results justify skill-library promotion.

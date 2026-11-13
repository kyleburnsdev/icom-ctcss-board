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

## Machining and heat-transfer sequence

Use the [fabrication guide](../pcb-fabrication-guide.md) at the machine and the
[manufacturing package](../../manufacturing/pcb/carvera-air/README.md) for files
and settings. Heat transfer is the top-legend process. Laser transparency has
produced a sharp, clean transfer with easy alignment; sublimation is untested.

| Native job / action | Reference and purpose |
| --- | --- |
| Job00_RegistrationPreparation | Independent copper-top setup on sacrificial wasteboard; skip accepted prepared holes |
| Job10_BottomCopper | Exposed bottom copper Z0 + thorough map; isolate |
| Job20_BottomMaskRemoval | Same bond, copper Z0/map after bottom coats; only datum-preserving tool-length setting between mapping and clearing |
| Job50_BottomHoles | Before first flip: release, zero aluminium floor, add backing and remount bottom up; no map |
| Flip, coat/cure top, then heat transfer | Coat in jig; release for separate press; align transparency to drilled holes |
| Conditional repeat of Job50_BottomHoles | After front-side work only if holes are obstructed; restore floor setup/backing, no map |

Pre-flip drilling is the user's proposed sequence, not a completed machine run.
Its purpose is to provide holes for transparency alignment. The successful
transfer test does not establish the complete fabrication sequence.

Coating/curing stays in the jig. Keep bottom seating unchanged through pad
clearing; only datum-preserving tool-length setting is allowed after copper
mapping. Complete pad clearing before drilling; do not run its spring tip over
open electrical holes. SetupSummary provides MaskOvertravel = 0.05 mm and
MaskPassOffset = 0 initially. Clean/inspect before lowering only that operation
offset, recomputing and rechecking. Spring pressure is not a known removal depth.

For each hole setup, the selected 1 mm support and 0.15 mm breakthrough give
PCB underside +1.00 mm, copper +2.50 mm and tip +0.85 mm relative to aluminium
floor zero. Every hole move must stay above zero; use no copper map. The
0.8 mm corn bit interpolates 111 electrical holes and four enclosure mounts,
excluding the four jig holes. Clean/deburr before the first flip. A changed
support height requires CAM updates and output checks.

On the top face, keep holes clear while coating, then release/clean the PCB.
Only the board goes to the separate press. After transfer, inspect holes and
skip cleanup if clear; otherwise restore the same floor-referenced contract
for the repeat hole pass. No routine perimeter cut is needed on finished stock.

## Verification and physical acceptance

Use Robust MCP Server for the native FreeCAD source
`mechanical/pcb/icom-ctcss-pcb-cam.FCStd`. Preserve source identity and unsaved
work before any change. Verify native operations, posted motion, floor limits
and fixture clearance against the actual jobs being run. Native/planar checks
do not establish physical pad exposure, coating behavior or hole fit.

Use the [attempt log](../pcb-attempt-log.md) for transfer conditions/results,
pre-flip drilling and any cleanup, pad exposure, coating adhesion, hole fit and
electrical checks. The inventory report has incomplete stock/capability coverage;
it is not a stock-completeness pass. Keep generalized skill-library updates
separate from this workspace-local process.

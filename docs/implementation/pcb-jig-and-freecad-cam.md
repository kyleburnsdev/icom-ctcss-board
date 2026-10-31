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

## Jobs maintained through Robust MCP Server

Updated 2026-10-31: copper isolation and the repeatable electrical/enclosure-hole
cycle are independent native jobs/programs. The [split comparison](../verification/pcb-cam-job-split.json)
checks their cutting moves against the preceding combined program; maximum
sampled coordinate difference is under 0.000012 mm from native/post rounding.
Bottom mask removal now has a native job and reviewed NC using Makera's
spring-loaded 0.3 mm tool. The current product specifications take precedence
over the retained older OEM profile's RPM/shank discrepancies; see the package.

User-established datum strategy: establish copper G54 Z0 before trace cutting
and retain it for ALL subsequent operations. Do not capture a new work zero
on coating, after tool changes or after remounting/flipping. Reproduce original
seating; express any required height/focus correction as an explicit operation
offset relative to this datum. Tool-length calibration preserves the work zero.
Job 20 commands −0.20 mm below known copper into spring compliance; actual
compression also includes coating thickness. This is not intended copper removal.

Editable source: `mechanical/pcb/icom-ctcss-pcb-cam.FCStd`. Native CAM operations
and tool controllers are generated by `tools/build-pcb-cam.py` from the current
Gerber-derived `cam-inputs.json`; `tools/prepare-pcb-cam.py` prepares that input.
Review milling outputs live in `manufacturing/pcb/carvera-air/review-nc/`.
The [package README](../../manufacturing/pcb/carvera-air/README.md) gives setup
and regeneration instructions. Laser hatch bands are separate native engraving
operations because FreeCAD’s nearest-neighbour wire ordering becomes expensive
for the complete 24,000-segment hatch in one operation.

| Stage | Required result |
| --- | --- |
| Registration preparation | A separate first job making all four jig holes in one setup. Specify independent initial datum/restraint and sacrificial breakthrough protection; the unmade holes cannot locate this job. Deburr both faces and accept spacing and slip fit before production. |
| Bottom copper | Register on all four pins, seat/cure the painter's-tape/CA bond, withdraw all four PCB pins, check no movement, probe/height-map exposed copper, then isolate retained merged copper boundaries. Inspect swept cutter area at pad/track junctions and narrow gaps. |
| Bottom mask and pad opening (job 20) | Inspect exposed copper, apply/cure bottom UV mask, then clear all 111 pad regions with Makera's spring tool before electrical holes exist. Retain original copper Z0. Current Makera references: 6,000 RPM, 400/200 mm/min feed/plunge, 0.2 mm spring-tool overtravel. Preserve >=0.10 mm mask at pad edges with conservative cutter-envelope compensation and 0.12 mm fill pitch. Qualify preload and intact copper. |
| Electrical holes (independent job 30) | Initially drill/interpolate the current electrical holes and enclosure mounts after bottom pad opening, then deburr/check electrically. Repeat this separate bottom-frame program only if needed after BOTH coatings, before assembly. Retain original pre-isolation copper G54 Z0, reproduce seating/re-register after remounting, and protect breakthrough and finished coating. Exclude all jig holes. |
| Top coating/legend | After bottom inspection, flip about Y and repeat register/bond/withdraw/check. Apply white UV solder mask and fully UV-cure it, then laser-mark the dark legend. Initial full-board trial: 5% power, 500 mm/min, 0.05 mm hatch, one pass. Confirm firmware/focus behavior and inspect readability, retention and coating integrity after IPA cleaning. No separate legend coupon. |
| Final separation | Only if needed; last registration-dependent stage, with retention and protected breakthrough. No routine perimeter cut on an already finished-size full-board blank. |

Combine operations/tool changes only while the bonded setup remains undisturbed.
Create separate programs across flips, remounting or coating stages requiring
changed setup. Successive jobs on an undisturbed blank do not require rebonding.
PCB pins are removed before machining; bed locator pins remain installed.
Include their protrusion, screw heads and any clamps in collision checks.

The aluminium floor is not a spoilboard. Reconcile protective layers, the
1.50 mm pocket depth, 1.5 mm board and measured adhesive stack with actual Z and
pin engagement. Keep tape/CA clear of sockets and the jig's push-off/vent mouths
at (37.5,50), (75,50), (112.5,50). Those ports are fixture features, not PCB holes.
Retain the measured original copper G54 Z0 across remounts/flips; reproduce the
original support height rather than capturing a new face zero. Apply an explicit
operation height/focus offset if needed, without changing the work datum.

## Verification and physical acceptance

Saved native board/library readback verifies four footprint-owned rule areas on
both copper layers, all five exclusion flags and at least 1 mm beyond every
hole edge. Each area is a circumscribed 64-sided polygon, preserving the full
circular allowance. The keepout moves with its owning hole and does not reject
that mechanical footprint itself. A controlled native fill experiment excludes
all 64 sampled points in the reserved ring; its control fills all 64.

DRC after refill reports zero errors and zero unconnected items. Saved FreeCAD
jobs reopen; posted review NC checks cover modes, tool changes, the ideal planar
cutter sweep and laser power gating. See the
[current revision manifest](../verification/pcb-revision.json).

Before machining, qualify tool/holder/fixture clearance and the physical Z stack.
Copper-top Z0 and a -1.65 mm path on 1.5 mm stock need 0.15 mm sacrificial
penetration plus tolerance; the cutter may never enter the aluminium floor.
Protective layers change seating and pin engagement. Qualify registration fit,
flip repeatability, surface mapping and isolation/drill fits on representative
material. The V-bit settings remain coupon candidates. Qualify dark laser marking
on fully UV-cured white mask using the first full board, after IPA cleaning;
adjust the next board from that result. CAM geometry is not a physical process qualification.

No machine operation or physical acceptance has been performed. Bottom mask
removal is supplied as a separate native job/program; spring preload and clean
mask removal without copper damage still need physical qualification.
Copper isolation and holes are separate programs. The independent hole program
permits a final clearing cycle after both coatings; it repeats full-depth bores
and enclosure mounts, not registration holes. Firmware and electrical simulation
work retain their separate scope.

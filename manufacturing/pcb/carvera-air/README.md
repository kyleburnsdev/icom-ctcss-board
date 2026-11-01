# Carvera Air PCB manufacturing

For one board's electronic components and module sockets, use the [DigiKey upload CSV](../digikey-board-parts.csv) and [purchasing notes](../../../docs/digikey-board-parts.md).

For the laser-printer scaling trial, use the [negative legend PDF and print instructions](print-masks/README.md).

**Start with the [PCB fabrication guide](../../../docs/pcb-fabrication-guide.md)**
for the illustrated machine/workbench sequence, tools, optional registration
preparation, original copper-zero strategy, coating/flip steps and final hole
clearing. This README holds package contents and engineering/regeneration detail.

Editable source: [FreeCAD CAM project](../../../mechanical/pcb/icom-ctcss-pcb-cam.FCStd).
Use **Robust MCP Server** for FreeCAD CAM and Konnect for KiCad. The
[workflow](../../../docs/implementation/pcb-jig-and-freecad-cam.md) defines the jig interface.

**CAD/CAM migration verified; physical process qualification pending.** Four
footprint-owned keepouts enforce copper/placement exclusions, and native KiCad
thickness matches the 1.5 mm stock and CAM model. Required operations unsupported
by Konnect used KiCad's native API under the standing user fallback rule.

Actual fixture/holder clearance, protective Z stack, height mapping, hole fit and
milling qualification remain acceptance work. Verify the physical setup before
running `review-nc/`; qualify the legend on the first full board after IPA cleaning.

## Deliverables

| File | Purpose |
| --- | --- |
| `native-exports/` | Current unmirrored B.Cu, F.SilkS, outline and drills, with source/export hashes |
| `cam-inputs.json` | Merged copper, isolation centerlines, hole geometry and positive legend hatches in the top panel frame |
| [Registration drawing](registration.svg) | Full blank, eight mechanical holes, finished jig fits and flip |
| `review-nc/00-registration-preparation.nc` | Separate first setup: clear all four jig holes in one mounting |
| `review-nc/10-bottom-copper.nc` | Bottom copper isolation only |
| `review-nc/20-bottom-mask-removal.nc` | Makera spring-tool pad clearing after bottom coating, before electrical drilling |
| `review-nc/30-bottom-holes.nc` | Independent 111 electrical bores and four enclosure mounts; optional repeat after both coatings |
| `review-nc/40-top-legend-laser.nc` | Dark legend marking on fully UV-cured white mask; first full-board trial |
| `pcb-corn-0.8mm.fctb` | Pinned OEM tool reference used by the FreeCAD tool controllers |
| `pcb-mask-removal.fctb` | Unmodified OEM mask-tool reference; corrections below apply in native controllers |

All physical copper is B.Cu. All 119 holes are unplated, including electrical
drills labeled PTH by KiCad. H1–H4 are 4 mm enclosure mounts; H5/H6 are 4.03 mm
and H7/H8 4.12 mm nominal finished registration holes for measured 4.000 mm pins.

## Setup 00: prepare registration holes

Mount the finished-size 150 × 100 × 1.5 mm blank on a flat sacrificial wasteboard,
with the aluminium jig absent. Establish independent straight-edge XY datums:
X0 Y0 is the blank's panel lower-left. Bond the blank with tape/CA or a qualified
equivalent. Set G54 Z0 on its actual copper top. The program uses absolute
millimeters, 15 mm clearance and Z−1.65 mm, entering sacrificial material by
nominally 0.15 mm. Account for board thickness/flatness and holder clearance.
No perimeter trim is needed on this finished-size blank.

T3: 0.8 mm corn bit, 12,000 RPM, 500 mm/min feed, 100 mm/min plunge, 0.3 mm
stepdown and 40% stepover. These candidate settings use the retained OEM tool
baseline and require a coupon. Full pocket clearing avoids loose plugs. Native
CAM's ideal swept diameters are about 4.026/4.116 mm; qualify actual finished fit.
Deburr both faces. For measured 4.000 mm pins, accept P1/P2 at 4.02–4.04 mm and
P3/P4 at 4.10–4.15 mm, with correct 110 × 50 mm spacing and burr-free slip fit.
Never force a binding board onto pins.

## Setup 10: registered bottom face

Pocket lower-left / Anchor 1 is G54 XY0; panel-to-jig adds 0.10 mm to X and Y.
Register on all four PCB pins, seat/cure the painter's-tape/CA bond, withdraw
all four PCB pins, and check no movement. Bed locator pins stay installed.
Probe/height-map exposed copper after removing PCB pins; confirm copper-top Z0.
Successive operations on an undisturbed bond retain the setup.

The aluminium floor is not a spoilboard. A −1.65 mm through-cut requires
protected breakthrough beneath the 1.5 mm PCB. Protective layers change pocket
seating, adhesive height, pin engagement and Z clearance. Accept the complete
physical stack first. Keep adhesive clear of sockets/vents and include bed pins,
screws, clamps and holders in collision review.

T2: owned 30° V-bit, 0.2 mm tip; candidate 0.10 mm depth, 100 mm/min feed,
30 mm/min plunge, 12,000 RPM. Centerlines are 0.15 mm outside merged retained
copper; ideal width is 0.25359 mm. Posted planar sweep is checked against copper.
Actual runout, height variation and depth remain coupon inputs.

## Setup 20: bottom solder mask and pad opening

After copper isolation, inspect/clean the channels and check continuity/shorts
while the copper is exposed. Apply bottom UV solder mask, keep the four jig
holes clear, and fully cure it. Run job 20 **before initial electrical/enclosure
drilling**, while there are no open electrical holes for the spring tip to enter.

T4 is the Makera spring-loaded UV solder-mask remover, 0.3 mm tip, 30°, 3.175 mm
shank, approximately 50 mm long. The [current Makera specifications](https://www.makera.com/products/uv-solder-mask-removal-tool-1-8-shank)
give 6,000 RPM, 400 mm/min feed, 200 mm/min plunge and 0.2 mm DOC. The retained
[OEM FreeCAD profile](https://github.com/MakeraInc/CarveraProfiles/blob/de08a657bdc9c230a094dbdba792acd70bfcdf32/CAM_Post_Processors/Freecad/Tools/Bit/Makera_UV_Solder_Mask_Removal_Tool_PCB.fctb)
instead contains 8,000 RPM and a 6 mm shank. The native controller uses the
current product's 6,000 RPM / 3.175 mm values, retaining the OEM file unchanged
(SHA-256 `6fca74d1a97d0a2bab82c889a79912df22450e3b78d54df3a14839787d92e6d5`).

**Retain the G54 copper Z0 established before trace cutting. Do not capture a
new work zero for pad clearing, drilling, the flip or legend.** Tool-length
calibration must preserve that work datum. The mask program commands Z−0.20 mm
relative to known copper: this is spring-tool overtravel, not intended copper
removal. Actual spring compression also includes coating thickness. Qualify
preload and mask removal with intact copper; do not substitute a rigid V-bit.
After any remount, reproduce the original seating/adhesive stack rather than
zeroing on the new surface. Any required height/focus correction is an explicit
operation offset relative to the original datum, never a new G54 zero.

Paths use all 111 pad flashes from current B.Cu artwork, excluding tracks.
Opening regions are inset by 0.10 mm; centerlines compensate for a conservative
0.40718 mm V envelope at 0.2 mm travel, with 0.12 mm fill pitch. The nominal
0.3 mm spring-tip contact leaves additional edge mask. Check complete usable
soldering area, retained pad rims and absence of copper lifting after cleaning.

## Setup 30: independent bottom holes

Run `30-bottom-holes.nc` initially after bottom pad opening for drilling,
deburring and electrical inspection. After bottom mask/pad opening and top coating/legend are
both finished, inspect every hole. If coating has blocked holes, the same
independent program can be run again from the bottom before fitting components.
It repeats the complete 115-hole bore/mount cycle; it is not a reduced-depth
scraping pass. It never recuts the four registration holes. Keep those holes
clear throughout coating so remounting retains the original datum.

After a remount, register/bond/withdraw all four PCB pins and check alignment,
including J1 pin 1. Retain the **original pre-isolation copper-top G54 Z0**;
do not capture a new zero on either copper or mask. Reproduce original seating
and account for coating in the support stack without redefining the datum. Protect
the completed top coating from bond/release damage and provide sacrificial
breakthrough beneath it. Inspect pad edges for lifting/chipping, clean debris,
check lead fit, and repeat continuity/short checks after any clearing cycle.
An undisturbed bond needs no extra registration just for a program/tool change.

T3 interpolates 46 × 0.9 mm holes at 55 mm/min and 0.01 mm/revolution pitch,
then 65 × 1.1 mm holes at 135 mm/min and 0.03 mm/revolution. Both pitches give
1.823° ramps, within the OEM reference's 2° limit. Four 4 mm enclosure mounts
are cleared afterward. Qualify lead fit and tool entry behavior. This program
requests T3 only; changing feed controllers does not change the physical tool.

## Setup 40: top coating and legend

Pass bottom isolation/continuity and drilled-hole inspection, clean/deburr, then flip about Y:
x′=150−x, y′=y. Register, bond, withdraw all PCB pins and check seating again.
J1 pin 1 checks orientation: jig top (130.10,40.10), bottom (20.10,40.10) mm.
Apply a thin, uniform white UV solder-mask coating, keeping holes clear, and
fully cure it under the UV lamp according to its product instructions. Laser-mark
the cured white surface directly to produce the dark legend.

Install/focus the Air laser on the actual coated face at the programmed Z0 plane
while retaining the original copper G54 zero. Adjust optical focus without
resetting the work datum; reproduce seating after the flip. The separate
review program uses M321/M322 mode selection, explicit S0 on rapids, entries and
Z moves, and positive power only during nonzero XY feeds. First-board trial:
**5% power, 500 mm/min, 0.05 mm hatch pitch, one pass**. These agent-selected
settings reduce nominal power/feed by a factor of 20 from the previous saved
20%/100 mm/min job; they are not a physically validated marking recipe.
Confirm installed firmware's mode/power/focus behavior. Use the full board as
the test piece; no separate legend coupon is required. Clean with IPA and inspect
the actual labels for readability, sharp edges and retention. Reject loose soot,
smearing, blistering, flaking, broad discolored halos or exposed substrate.
Record settings and the cleaned result, then adjust the next board as needed.
Use the enclosed laser process and specified eye protection. Complete the final
hole inspection/clearing after both face coatings, not between them. No routine
perimeter-separation job is needed on this finished-size blank.

## Regeneration and verification

Export selected layers/drills through Konnect. The clean F.SilkS plot excludes
native footprint reference/value fields and retains board-level labels; KiCad CLI
provides `--exclude-refdes --exclude-value`. Run `python tools/prepare-pcb-cam.py`
with gerbonara 1.6.3 / Shapely 2.2. Load `tools/build-pcb-cam.py` through Robust
MCP Server `execute_python`, call `build(root)` and advance its generator once per
stage. Preserve native edits first; the builder refuses an open `CTCSS_PCB_CAM`.
The setup sheet is descriptive; edit native operation/controller properties to
change settings, then regenerate/recheck dependent geometry.

Call `export_milling(root)` and `export_laser(root)` in that module, then run
`inspect_saved(root)` after preserving/closing the project, then
`python tools/verify-pcb-cam.py`. Inspect the reopened native tree and paths.
[Revision](../../../docs/verification/pcb-revision.json),
[geometry](../../../docs/verification/pcb-cam-geometry.json),
[jobs](../../../docs/verification/pcb-cam-jobs.json) and
[posted-motion checks](../../../docs/verification/pcb-posted-motion.json)
state the verified scope. No upload, machine connection or cutting occurs.
The [pad-opening view](../../../docs/verification/pcb-mask-paths.png) shows the
ten editable pad-region operations; [native addition evidence](../../../docs/verification/pcb-mask-job.json)
records unchanged preceding toolpaths. Posted checks cover all 111 inset pad
regions, zero conservative sweep outside them, all 115 electrical/enclosure
holes, and absence of work-zero reset commands.

Milling uses the pinned [OEM FreeCAD post](https://github.com/MakeraInc/CarveraProfiles/blob/de08a657bdc9c230a094dbdba792acd70bfcdf32/CAM_Post_Processors/Freecad/1.1PostProcessor/makera_legacy_post.py),
retained with its LGPL notice under `tools/post/`. The project supplies G54,
two-second spin-up and a non-homing ending. Laser translation follows the
[OEM firmware](https://github.com/MakeraInc/CarveraFirmware/blob/6e12557cfa5eff446bb5fe014354eaa03abf0caa/src/modules/tools/laser/Laser.cpp)
and [Air manual](https://wiki.makera.com/en/Air/Manual). The
[OEM corn-bit definition](https://github.com/MakeraInc/CarveraProfiles/blob/de08a657bdc9c230a094dbdba792acd70bfcdf32/CAM_Post_Processors/Freecad/Tools/Bit/Makera_TiN_Coating_Corn_Bit_0.8_5.5mm_PCB.fctb)
is retained beside the outputs.

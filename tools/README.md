# Engineering tools

## Populated-board learning guide

Regenerate the November 16 illustrated guide from retained evidence with
`python tools/build-populated-board-learning-guide.py`, followed by
`./tools/build-populated-board-learning-guide.ps1`. The Python stage requires
NumPy, Matplotlib and Pillow; the PowerShell stage requires installed Microsoft
Word and creates its own invisible instance. No instruments are accessed.
Outputs are the PDF and editable DOCX under `docs/learning/`; the 13 figure
sources and PNGs are under `docs/images/populated-board-learning/`.
Render the final PDF to page images and inspect every page after changes.

Run these commands from the repository root. They are maintained project tools; agent-only scripts and intermediate outputs belong in ignored `.agent-scratch/`.

The temporary holder uses `build-bench-holder.py` with FreeCAD 1.1's bundled
Python and its `bench-holder-threads.py` native helix helper. Ordinary Python
`prepare-bench-holder.py` prepares the three-plate Bambu Studio 3MF using installed
X1C/Generic PLA profiles and the existing enclosure plate helpers. No printer
connection is made. `inspect-bench-holder.py` uses the installed Robust MCP
XML-RPC bridge for native assembly presentation/checks; it refuses to replace
live documents. `render-bench-holder.py`, run with FreeCAD's bundled Python
(matplotlib/Pillow), draws the guide and actual G-code layer sheets. See the
[native model notes](../mechanical/bench-holder/README.md) for commands and
[operator guide](../docs/bench-holder-guide.md) for printing and testing.

- `python tools/check-netlist.py`: checks the final exported netlist in `docs/verification/schematic-complete.net`. Uses the Python standard library.
- `python tools/tone-response.py`: runs the illustrative tone-chain model. Uses the Python standard library; see `docs/implementation/tone-response.md` for limitations.
- `python tools/check-final-board.py`: reads the saved PCB and refreshes `docs/verification/final-board-inventory.json`. Requires KiCad's Python environment with `pcbnew`. It does not save or change the PCB.

Generated reports describe the source revision used to generate them. Regeneration requires appropriate review before treating outputs as accepted manufacturing evidence.

## PCB CAM

### Sublimation color trial

1. With the intended PCB saved, run read-only metadata export using KiCad 10's
   bundled Python (Konnect has no board-text bounding-box reader):
   `& 'C:/Program Files/KiCad/10.0/bin/python.exe' tools/export-sublimation-metadata.py`.
   This writes `docs/verification/sublimation-board-metadata.json` and a native
   top-legend Gerber under `manufacturing/pcb/sublimation/source/`, never the PCB.
   The in-memory sublimation derivative replaces the machining subtitle with
   `SELECTABLE CTCSS | 5V PRO MICRO`, retaining KiCad's font and centering.
   It also adds the eight-point bench guide to this derivative, asserting each
   point's saved net assignment. The color generator checks its frame against
   pads, jig exclusions and the selected body envelopes before exporting.
2. Run `python tools/create-sublimation-artwork.py`. Dependencies: gerbonara,
   Shapely, reportlab, pypdf and resvg-py. It validates existing native export
   hashes against PCB/project/libraries and refuses stale inputs; refresh the
   native exports/manifest via the established process after a PCB change.
3. Inspect the top and coupon SVG/PDF pairs in `manufacturing/pcb/sublimation/`,
   white-backed top preview in `docs/images/` and `docs/verification/pcb-sublimation.json`.
   Print PDFs Actual size / 100%. No transfer mirroring is applied: the printer
   automatically mirrors. The transfer artwork is top only.

SVGs use millimeters and named color groups. Generator changes are the maintained
source for repeated exports; direct artwork edits are overwritten. No native
KiCad/CAM/NC file is modified. Use the [guide](../docs/pcb-fabrication-guide.md)
for coupon acceptance and the fabrication sequence.

### Native machining work

Use FreeCAD 1.1.1 through Robust MCP Server for editable CAM work. Preserve
unsaved work and exact source identity before mutation or regeneration.
The [machining package](../manufacturing/pcb/carvera-air/README.md) identifies
the selected programs: registration preparation, bottom isolation, bottom pad
clearing and circuit/enclosure holes. The [jig contract](../docs/implementation/pcb-jig-and-freecad-cam.md)
gives coordinate transforms and datum requirements.

Preserve original copper zero/map through pad clearing. Then drill on
sacrificial backing with aluminium-floor Z0 before the first flip. Coat/cure
top in the jig, release for the chosen heat transfer, and inspect holes. A
repeat hole pass is conditional on obstruction and uses the restored floor
setup with no copper map. Do not run pad clearing over open electrical holes.

After CAM changes, recompute and save native operations, inspect/reopen the
source, export the selected programs with the pinned mill post, and check
actual posted paths, tool changes, cutter sweep and floor limits before a
machine run. Checks must match the exact jobs/settings and saved source.
The revised pre-flip drilling sequence has not yet been physically run.

## Enclosure builder

`build-enclosure.py` runs inside FreeCAD 1.1.1 using Part Design, Sketcher, Spreadsheet, Draft, Mesh/MeshPart and bundled Netgen. Invoke through FreeCAD MCP `execute_python`. Preserve intentional edits before regenerating; the builder refuses an already-open `CTCSS_Enclosure_P1`.

Load once, retaining the namespace/generator between MCP calls:

```python
from pathlib import Path
root = Path("C:/src/personal-repos/icom-ctcss-board")
App._enclosure_namespace = {"__name__": "enclosure_builder"}
exec(compile((root / "tools/build-enclosure.py").read_text(encoding="utf-8-sig"),
             "build-enclosure.py", "exec"), App._enclosure_namespace)
App._enclosure_build = App._enclosure_namespace["build"](root)
_result_ = next(App._enclosure_build)
```

Call `_result_ = next(App._enclosure_build)` again for each stage until the CAD report is returned. Staging keeps individual geometry commands short. The final stage checks intersections and saves the FCStd. Run the independent export generator next:

```python
App._enclosure_export = App._enclosure_namespace["export"](root)
_result_ = next(App._enclosure_export)
```

Advance once per mesh, then once more to export STEP (catch `StopIteration` after completion). The lettered surround's Netgen mesh and STEP export can exceed an MCP response timeout; execution can continue in FreeCAD. Check the written report/file and UI before retrying a timed-out stage; do not advance/rebuild while its work is still running. `export(root, names=[...])` refreshes selected meshes while preserving other mesh records, then exports the complete STEP assembly.

Outputs: editable `mechanical/enclosure/icom-ctcss-enclosure.FCStd`, thirteen Z=0 print-oriented STLs beneath `manufacturing/enclosure/supporting/stl/`, assembly STEP beneath `supporting/step/`, and CAD/mesh reports under `docs/verification/enclosure-p1/`. The saved source uses native features and does not depend on the builder or scratch. Windows Stencil (`C:/Windows/Fonts/STENCIL.TTF`) supplies through-cut legends; Arial Bold supplies MIC/RADIO engraving. Fonts are required to regenerate lettering; saved geometry displays without them.

[Implementation notes](../docs/implementation/enclosure-p1.md) describe the model tree and coordinated layout editing. Geometry validation is tied to the generated revision.

## Prepared enclosure print project

Run `python tools/prepare-enclosure-plates.py` after mesh export. Uses Python's standard library and installed Bambu Studio at `C:/Program Files/Bambu Studio`; resolves its inherited X1 Carbon 0.4 mm / Generic PETG profiles, applies the enclosure settings and uses native `--load-assemble-list` packaging. It does not connect to a printer.

The primary output is `manufacturing/enclosure/p1-enclosure.3mf`: three named plates, nineteen instances, embedded shared settings and all three sliced toolpaths. All objects use slot 1 with no individual process overrides. The script checks ZIP integrity, plate order, counts, profiles, saved geometry/transforms, brim/exclusion reservations, bed faces and slice success. Evidence goes to `docs/verification/enclosure-p1/multi-plate-checks.json`; raw resolved profiles, arranged meshes and logs go to `.agent-scratch/enclosure-p1/plates/`. The final project has no scratch dependency.

Profile resolution/export follow the [Bambu CLI documentation](https://github.com/bambulab/BambuStudio/wiki/Command-Line-Usage) and [native plate-assembly implementation](https://github.com/bambulab/BambuStudio/blob/master/src/BambuStudio.cpp).
## Firmware build and test tools

`python tools/build-firmware-learning-guide.py` rebuilds the self-contained
[November 13 learning guide](../docs/learning/firmware-testing-field-guide-2026-11-13.pdf)
from retained repository evidence. Requires Python, ReportLab and Pillow; it never
accesses hardware. Original screen pixels are embedded unchanged, with PDF vector
annotations. The PDF goes in `docs/learning/`; build QA metadata goes in
`.agent-scratch/firmware-learning-guide/`. Visually review a rendered rebuild before
replacing the accepted document and its provenance manifest.

`build-firmware.ps1` builds the Arduino Pro Micro and/or CubeMX-generated
NUCLEO-F767ZI projects without flashing. `test-firmware.ps1` runs native C++
control/journal, actual tone ISR with a host register model, PWM-capture and display-model tests. `phase1-test.py` uses pyserial 3.5 to
run USB-only or wired bench checks and writes timestamped, source-hashed JSON.
Dependencies, commands and protocols are in the [firmware README](../firmware/README.md);
physical connections are in the [phase-one guide](../docs/implementation/firmware-phase1-guide.md).
Builds, temporary reports and captures belong in `.agent-scratch/firmware/`.

`usb-diagnostics-test.py --pro COM_PORT --output NEW_REPORT.json` checks bench
firmware parser rejection/recovery, fragmented commands, 200 STATUS requests and
a bounded stalled-reader burst. Requires pyserial 3.5, idle Arduino with signal
pins disconnected (passive probes allowed), exclusive serial ownership and a
new report path. It issues no valid SAVE, HANG, programming or stimulus command.
Nonzero exit means failure/incomplete evidence; JSON retains raw replies and
source hashes. It measures USB state/recovery, not electrical output timing.
The November 13 live robustness sequence passed. See the
[bench setup and scope procedure](bench/README.md) for `check-idle-pwm.py`,
dependencies, exact wiring, limits, evidence, recovery and offline evaluator tests.

The native suite also compiles `sketch_test.cpp`, including the unchanged Arduino
sketch and actual control/tone/storage/display modules. Nine host executions
cover PTT/bypass and faults through simulated hardware interfaces. No physical
connections are required. The model and its limits are described in the
[verification campaign](../docs/implementation/firmware-verification-plan.md).

## Wiring illustrations and schedule

Run `python tools/render-wiring-guide.py` from the repository root (Python 3.10+,
Pillow; Windows Arial fonts). It regenerates the seven PNG figures in
`docs/images/wiring/` and the marked wire tables in
`docs/final-product-wiring-guide.md` from the checked-in
`docs/reference/final-product-wire-list.csv` and
`docs/verification/wiring-guide/header-readback.json`. It does not edit KiCad.
After a hardware revision, refresh the pad readback through Konnect and compare
the wire schedule against a new schematic netlist before regenerating/reviewing.
Run `python tools/check-wiring-guide.py` (standard library only) to verify retained
CSV/PCB/schematic-export agreement, guide table coverage and local links. Pass
`--netlist PATH` to promote a fresh schematic export into the evidence package.
It records source hashes but does not query the current live board; refresh the
Konnect pad readback after a hardware change. Neither tool modifies KiCad files.

Run `python tools/render-wiring-hardware.py` (Python 3.10+, numpy, matplotlib)
for the two additional perspective hardware illustrations. These show GX16
bodies/pins/sockets/solder cups and the user-confirmed EC11 opposing 3/2 solder
tabs, with connector and wire callouts. Geometry is illustrative, not dimensional
CAD; the flat pinout sheets remain the contact-view references. Both generators
are needed to regenerate all nine figures; neither uses downloaded photos.

## EC11 nut with integrated washer

With B1 open and the N1 nut document closed in FreeCAD, execute the module
`tools/build-ec11-flange-nut.py` and call `main()` through Robust MCP's
`execute_python`. It uses native constrained sketches, Pads/Pockets, Groove and
SubtractiveHelix and exports FCStd, print-oriented STL and STEP. Existing B1
is read only. Constants own regeneration; custom dimension properties are
documentation of those inputs, not live drivers for every feature.

Run `python tools/prepare-ec11-flange-nut.py` using installed Bambu Studio X1C
0.4 / Fine / Generic PLA profiles; then `python tools/render-ec11-nut-guide.py`
(matplotlib) for the dimensioned stack and actual G-code layer inspections.
No printer connection occurs. Final files are in `manufacturing/ec11-flange-nut/`;
verification is in `docs/verification/ec11-flange-nut/`. See the
[fitting guide](../docs/ec11-flange-nut-guide.md) before printing.

## B2 rear-display replacement panel

The native builder `tools/build-bench-panel.py` runs through Robust MCP in
FreeCAD 1.1. It checkpoints the saved B1 file as a whole, loads through FreeCAD,
and builds a separate `mechanical/bench-holder/bench-panel-b2.FCStd`. B1 and its
live document remain untouched. Close only B2 before regeneration. Constants
own layout; constrained sketches, pads, pockets and native coarse helix features
remain editable. The thumb screws are custom 5 mm / 1 mm pitch, not standard M5.

Run `python tools/prepare-bench-panel.py` for the two-plate Bambu Studio project,
then `& 'C:/Program Files/FreeCAD 1.1/bin/python.exe' tools/render-bench-panel.py`
for the dimensioned assembly drawing and actual G-code layer views. The latter
uses bundled matplotlib. No printer connection is made. See
[the B2 guide](../docs/bench-panel-b2-guide.md) and
[package](../manufacturing/bench-panel-b2/README.md).

## C1 narrow enclosure and radio cradle

Run `main()` from `tools/build-enclosure-c1.py` through FreeCAD 1.1 Robust MCP
with the exact C1 document closed. It builds a separate native model using the
maintained B1 Sketcher/Pad/Pocket helpers; B1/B2/P1 sources remain untouched.
Run `main()` from `tools/export-enclosure-c1.py` through the same bridge to check
all installed printed instances, reference envelopes and sampled cover travel,
export print-oriented meshes/assembly STEP and verify native saved readback.
The exporter reads the saved native hole positions and preserves manual edits;
it does not normalize geometry or modify other documents.

Then run `python tools/prepare-enclosure-c1.py` with installed Bambu Studio for
the four-plate, shared Generic PLA/X1C 0.4/0.20 mm project. No printer is accessed.
Run `& 'C:/Program Files/FreeCAD 1.1/bin/python.exe' tools/render-enclosure-c1.py`
for the dimensioned guide schematics; FreeCAD's bundled Python supplies matplotlib.
Native CAD views are saved through the bridge. See the [C1 guide](../docs/enclosure-c1-guide.md)
and [mounting evidence](../docs/reference/ic229h-mounting.md). Inputs/constants own
regeneration; preserve manual C1 edits before rebuilding. Physical acceptance
and the inventory record gaps are separate from CAD/slicer checks.

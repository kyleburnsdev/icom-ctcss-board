# Engineering tools

Run these commands from the repository root. They are maintained project tools; agent-only scripts and intermediate outputs belong in ignored `.agent-scratch/`.

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

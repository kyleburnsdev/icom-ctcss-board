# Engineering tools

Run these commands from the repository root. They are maintained project tools; agent-only scripts and intermediate outputs belong in ignored `.agent-scratch/`.

- `python tools/check-netlist.py`: checks the final exported netlist in `docs/verification/schematic-complete.net`. Uses the Python standard library.
- `python tools/tone-response.py`: runs the illustrative tone-chain model. Uses the Python standard library; see `docs/implementation/tone-response.md` for limitations.
- `python tools/create-legend-print-test.py`: generates a Letter PDF with two rotated 150 x 100 mm negative-legend copies reflected across a fold, plus targets, trim and scale references. Requires ReportLab and pypdf; see the [folding guide](../docs/folded-mask-guide.md).
- `python tools/check-final-board.py`: reads the saved PCB and refreshes `docs/verification/final-board-inventory.json`. Requires KiCad's Python environment with `pcbnew`. It does not save or change the PCB.

Generated reports describe the source revision used to generate them. Regeneration requires appropriate review before treating outputs as accepted manufacturing evidence.

## PCB CAM

- `export-pcb-legends.py`: run with KiCad's bundled Python after normal Konnect
  Gerber/drill export. Uses native PLOT_CONTROLLER to export F.SilkS/B.SilkS
  without duplicate footprint fields or drill marks, options Konnect does not
  expose. Reads the saved board and never saves/modifies sources.
- `python tools/prepare-pcb-cam.py`: merge current unmirrored Gerbers, generate
  isolation/pad paths and separate positive top/bottom drag hatches, check all
  119 holes and export registration/assembly drawings and the bottom subsystem
  illustration. Requires gerbonara 1.6.3, Shapely 2.2 and resvg-py. FreeCAD applies
  the one face transform.
- `build-pcb-cam.py`: run inside FreeCAD 1.1.1 through Robust MCP Server
  `execute_python`. Preserve/close any existing PCB CAM, load the module in a
  retained namespace, call `build(root)` and advance once per stage. Outputs the
  native project in mechanical/pcb; each native job/controller remains editable.
- `export_milling(root)`: export all six current review programs with the pinned
  OEM post. Drag exports replace OEM M3 S0 with M5, strip cached spindle-speed
  words from moves and reject unexpected spindle starts. Native geometry/motion
  is unchanged by that post correction.
- Save/close, then `inspect_saved(root)` to reopen/read back operations/settings.
- `python tools/verify-pcb-cam.py`: independently check sources and posted modes,
  tool changes, copper sweep, 111 pad openings, positive-legend drag centerlines,
  spindle-off behavior and all-positive floor-referenced hole motion. Refreshes
  exact-revision manifests. Requires gerbonara/Shapely and KiCad CLI.

Example loading through Robust MCP Server execute_python:

```python
from pathlib import Path
root = Path("C:/src/personal-repos/icom-ctcss-board")
App._pcb_namespace = {"__name__": "pcb_builder"}
exec(compile((root / "tools/build-pcb-cam.py").read_text(),
             "build-pcb-cam.py", "exec"), App._pcb_namespace)
App._pcb_build = App._pcb_namespace["build"](root)
_result_ = next(App._pcb_build)
```

Advance `next(App._pcb_build)` once per stage to completion; then call
`App._pcb_namespace["export_milling"](root)`. Preserve/close the saved document
before `inspect_saved(root)`. Do not retry a timed-out mutation until its state
is inspected. These tools do not connect to the machine.

Order: bottom isolate/map; in-jig coats/cures; pad clearing on original copper
zero/map; bottom drag; flip/in-jig coats/cures/top drag; final sacrificial-backed
holes on new floor zero. No probing except tool-length setting between copper
mapping and pad clearing. Initial spring settings are 0.05 mm; native independent
repeat-pass offsets preserve saved surface datums. See the
[fabrication guide](../docs/pcb-fabrication-guide.md) for settings and acceptance.

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

`build-firmware.ps1` builds the Arduino Pro Micro and/or CubeMX-generated
NUCLEO-F767ZI projects without flashing. `test-firmware.ps1` runs native C++
control/journal, PWM-capture and display-model tests. `phase1-test.py` uses pyserial 3.5 to
run USB-only or wired bench checks and writes timestamped, source-hashed JSON.
Dependencies, commands and protocols are in the [firmware README](../firmware/README.md);
physical connections are in the [phase-one guide](../docs/implementation/firmware-phase1-guide.md).
Builds, temporary reports and captures belong in `.agent-scratch/firmware/`.

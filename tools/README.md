# Engineering tools

Run these commands from the repository root. They are maintained project tools; agent-only scripts and intermediate outputs belong in ignored `.agent-scratch/`.

- `python tools/check-netlist.py`: checks the final exported netlist in `docs/verification/schematic-complete.net`. Uses the Python standard library.
- `python tools/tone-response.py`: runs the illustrative tone-chain model. Uses the Python standard library; see `docs/implementation/tone-response.md` for limitations.
- `python tools/create-legend-print-test.py`: generates the unmirrored 100 x 150 mm negative-legend PDF with external crop marks and measurement references. Requires ReportLab and pypdf; see the [print instructions](../manufacturing/pcb/carvera-air/print-masks/README.md).
- `python tools/check-final-board.py`: reads the saved PCB and refreshes `docs/verification/final-board-inventory.json`. Requires KiCad's Python environment with `pcbnew`. It does not save or change the PCB.

Generated reports describe the source revision used to generate them. Regeneration requires appropriate review before treating outputs as accepted manufacturing evidence.

## PCB CAM

- `python tools/prepare-pcb-cam.py`: merges current native Gerber copper, creates
  isolation offsets, pad-only mask-clearing paths and positive legend hatches, checks all 119 holes, and exports
  the registration/assembly drawings. Requires gerbonara 1.6.3 and Shapely 2.2.
- `build-pcb-cam.py`: runs inside FreeCAD 1.1.1 through Robust MCP Server
  `execute_python`. Load it into a retained namespace, call `build(root)` and
  advance the returned generator once per stage. The native document is saved
  under `mechanical/pcb/`; intentional existing edits must be preserved first.
  Call `export_milling(root)` / `export_laser(root)` for review NC.
- Preserve and close the native project, then call `inspect_saved(root)` from
  that module to reopen/check saved paths and source identities. Native paths
  use installed FreeCAD proxies; the saved project has no scratch dependency.
- `python tools/verify-pcb-cam.py`: verifies current input identities, posted
  ideal cutter sweep, mask-tool containment in 111 inset pad regions, absence of
  work-zero reset commands, laser power gating, modes and tool changes; checks source
  DRC/ERC and the reopened CAM identity; runs the circuit netlist assertions;
  refreshes PCB/export manifests. Requires gerbonara/Shapely and the KiCad CLI.

See [PCB setup and acceptance](../manufacturing/pcb/carvera-air/README.md).
The pinned OEM FreeCAD milling post under `tools/post/` retains its LGPL license;
laser translation is separate. These scripts do not connect to a machine.

Production order is copper isolation, bottom mask/cure/pad opening, initial
electrical/enclosure holes, top coating/legend, then hole clearing if needed.
Every program retains the copper G54 Z0 established before trace cutting.
The mask job uses the spring-loaded Makera tool, never a rigid substitute;
Z−0.20 mm is spring-tool overtravel below copper, not intended copper removal.

The board inventory uses selected maximum capacitor body envelopes and a conservative module/socket allowance. It verifies four enclosure mounts and four independent jig holes, reports selected-body clearances and records the saved board hash. It verifies all four footprint-owned keepouts, their layers/exclusion flags and the 1.5 mm native thickness. See the [FreeCAD CAM migration](../docs/implementation/pcb-jig-and-freecad-cam.md).

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

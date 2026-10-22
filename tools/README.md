# Engineering tools

Run these commands from the repository root. They are maintained project tools; agent-only scripts and intermediate outputs belong in ignored `.agent-scratch/`.

- `python tools/check-netlist.py`: checks the final exported netlist in `docs/verification/schematic-complete.net`. Uses the Python standard library.
- `python tools/tone-response.py`: runs the illustrative tone-chain model. Uses the Python standard library; see `docs/implementation/tone-response.md` for limitations.
- `python tools/check-final-board.py`: reads the saved PCB and refreshes `docs/verification/final-board-inventory.json`. Requires KiCad's Python environment with `pcbnew`. It does not save or change the PCB.
- `python tools/export-landscape-registration.py`: regenerates the landscape manufacturing geometry and manifest under `manufacturing/pcb/carvera-air/landscape-y-flip/`. Requires `gerbonara` and the existing manufacturing exports. This writes deliverables; run only when intentionally refreshing that package.

Generated reports describe the source revision used to generate them. Regeneration requires appropriate review before treating outputs as accepted manufacturing evidence.

The board inventory uses the selected maximum capacitor body envelopes and a conservative module/socket allowance. Refresh it before the landscape exporter, which uses its track/pad count to cross-check exported copper. The exporter preserves existing user `.mkc` projects; it does not rebuild their imports or toolpaths. Reimport revised geometry and validate CAM separately.

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

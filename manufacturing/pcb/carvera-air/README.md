# Carvera Air PCB manufacturing

**Start with the [illustrated fabrication guide](../../../docs/pcb-fabrication-guide.md).**
It gives the chronological setups, tools, surface references and inspection steps.
Use the [attempt log](../../../docs/pcb-attempt-log.md) at the machine.

This package implements the **2026-11-10 in-jig coating and two-color diamond-drag
candidate**. Physical results are pending. NC is for review/controller preview;
no machine operation is claimed. The generalized skill library remains unchanged.

## Current files

| File | Purpose / reference |
| --- | --- |
| [Native FreeCAD CAM](../../../mechanical/pcb/icom-ctcss-pcb-cam.FCStd) | Six editable jobs, native operations/controllers and a settings spreadsheet |
| `native-exports/` | Unmirrored B.Cu, F.SilkS, B.SilkS, outline and drills; one face transform in FreeCAD |
| `cam-inputs.json` | Merged copper, isolation/pad paths, separate positive top/bottom legend hatches and all 119 holes |
| [Registration drawing](registration.svg) | Four jig holes, fit requirements, frame and flip |
| [00-registration-preparation.nc](review-nc/00-registration-preparation.nc) | Only for an unprepared blank, independent sacrificial setup |
| [10-bottom-copper.nc](review-nc/10-bottom-copper.nc) | Isolation with exposed-copper Z0 and initial map |
| [20-bottom-mask-removal.nc](review-nc/20-bottom-mask-removal.nc) | 111 pads after all bottom coats; same copper zero/map, only tool-length setting in between |
| [25-bottom-legend-drag.nc](review-nc/25-bottom-legend-drag.nc) | Optional bottom subsystem explanations; if used, new outer-mask Z0, spindle off |
| [40-top-legend-drag.nc](review-nc/40-top-legend-drag.nc) | Existing top assembly/pin labels; new outer-mask Z0, spindle off |
| [50-bottom-holes.nc](review-nc/50-bottom-holes.nc) | 111 electrical bores + four enclosure mounts after both faces; floor Z0, sacrificial backing, no map |
| `pcb-mask-removal.fctb` | Historical OEM tool reference; current native controller uses corrected shank/RPM and lighter trial overtravel |

No perimeter program is needed for the finished-size full-board blank. Old file 30
and the laser file 40 are superseded; they are not part of this attempt.

## Settings and deliberate datum changes

All coating and curing stay in the jig. Preserve the bond, original copper Z0
and original copper height map from isolation through pad clearing. No surface
probing or remapping is allowed in that interval, only tool-length setting that
preserves the work datum. For each legend, set a new finished-mask surface Z0
after pad clearing; disable the copper map. Preserve jig XY through every setup.

Running file 25 is optional. If omitting it, skip contrasting bottom coats and
the bottom drag setup/Z setting; proceed from accepted pad clearing directly to
the top-face flip. Keep the protective bottom coating and pad clearing. Artwork,
CAM jobs, top-legend and final-hole steps are unchanged.

For final holes, remove the board, zero at the aluminium floor, add sacrificial
backing and register/bond bottom up again. Remove PCB pins before machining.
The default PCB underside is +1.00 mm, its copper plane +2.50 mm and final tip
depth +0.85 mm. Every posted motion must stay above floor zero. A materially
different support height requires updating CAM and checking the resulting NC.

In native **SetupSummary**:

| Alias | Default | Meaning |
| --- | ---: | --- |
| `BoardThickness` | 1.5 mm | Established PCB thickness |
| `SupportHeight` | 1.0 mm | Selected final PCB underside height above aluminium floor |
| `Breakthrough` | 0.15 mm | Final floor-referenced Z = support height − breakthrough |
| `MaskOvertravel` | 0.05 mm | Conservative initial pad-tool spring overtravel below copper |
| `MaskPassOffset` | 0 mm | Lower slightly only after inspecting pad clearing |
| `DragPreload` | 0.05 mm | Conservative initial spring preload below outer-mask surface |
| `BottomDragPassOffset` / `TopDragPassOffset` | 0 / 0 mm | Independent repeat-pass adjustments; leave each at zero for its first pass |
| `DragFeed` / `DragPlunge` | 300 / 100 mm/min | Selected trial speeds; spindle remains off |
| `MaskRPM` / `MaskFeed` / `MaskPlunge` | 6000 / 400 / 200 | Makera reference speeds |

Prefer too little removal on both spring-tool processes. Clean/inspect, then
lower the appropriate operation offset slightly, recompute/export/recheck and
repeat if needed. Do not move the saved surface datum or automate increasing
passes. A command changes spring pressure, not a guaranteed removal depth.

T6 uses the owned ¼-inch shank / selected 90° diamond tip. Use a matching collet,
manual/mechanical surface contact and actual tool-length setting; diamond is not
an electrical probe. Reference length/line width in the native tool are from a
matching WidgetWorks model, not measurements of the owned tool. See the guide
for settings provenance and the actual clearance/inspection procedure.

## Regeneration

1. Save and verify the exact board through Konnect/native KiCad. Preserve all
   unsaved editor work. Export B.Cu, F.SilkS, B.SilkS, Edge.Cuts and drills with
   Konnect. Then run **KiCad's bundled Python** on
   [export-pcb-legends.py](../../../tools/export-pcb-legends.py) to omit duplicate
   footprint fields and drill marks, an option Konnect's exporter does not expose.
2. Run `python tools/prepare-pcb-cam.py` from the repository root. Requires
   gerbonara 1.6.3, Shapely 2.2 and resvg-py for the derived bottom illustration.
   Keep its source hashes and review geometry.
3. Preserve and close existing PCB CAM. Through **Robust MCP Server**
   `execute_python`, load [build-pcb-cam.py](../../../tools/build-pcb-cam.py)
   into a retained namespace and advance `build(root)` once per stage. The
   resulting jobs use FreeCAD's native Engrave, Helix and PocketShape operations.
4. Call `export_milling(root)` for all six review files. This uses the pinned
   OEM mill post. For drag jobs it replaces OEM `M3 S0` with `M5` and removes
   cached spindle-speed words from moves, leaving native motion intact;
   unexpected spindle-start values cause refusal.
5. Save/close and call `inspect_saved(root)` to reopen/read back native paths.
   Run `python tools/verify-pcb-cam.py` for final posted-path/source checks.
   Refresh the illustrations and guide if geometry, settings or sequence changed.

Native parameters remain editable in FreeCAD. After a setting change, recompute,
save, export and verify affected jobs; do not hand-edit toolpaths or NC depths.

## Evidence and remaining acceptance

- [Current revision manifest](../../../docs/verification/pcb-revision.json),
  [native readback](../../../docs/verification/pcb-cam-reopen.json),
  [posted motion](../../../docs/verification/pcb-posted-motion.json).
- [Bottom text/native geometry check](../../../docs/verification/pcb-bottom-legend.json),
  [bottom artwork](../../../docs/images/pcb-bottom-subsystems.png),
  [jig/coordinate contract](../../../docs/implementation/pcb-jig-and-freecad-cam.md).
- Inventory helper preflight is incomplete: detailed stock/consumable entries,
  tool count and usable process/envelope records are missing. This does not
  change the established project equipment facts or claim a stock outage; it
  does prevent calling the package inventory-qualified. See its separately
  recorded [coverage](../../../docs/verification/pcb-inventory-preflight.json).

The trial must establish pad exposure without copper damage, mask adhesion and
readable contrasting legends with intact base coating. Controller preview, actual
holder/fixture clearance, floor protection, fit and physical trial acceptance are
separate from the recorded native/planar checks. No machine was connected or run.

For electronic parts, see the [DigiKey CSV](../digikey-board-parts.csv) and
[purchasing notes](../../../docs/digikey-board-parts.md). The
[folded-transparency guide](../../../docs/folded-mask-guide.md) records an earlier
experiment; it is not a step in this candidate.

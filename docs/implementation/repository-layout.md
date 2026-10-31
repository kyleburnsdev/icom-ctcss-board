# Repository layout

Editable KiCad sources, library tables and required libraries live together in `electronics/`. `${KIPRJMOD}/libraries/...` references continue to resolve relative to the project. FreeCAD sources belong in `mechanical/enclosure/`, and Arduino sources in `firmware/`.

The PCB manufacturing package lives in `manufacturing/pcb/carvera-air/`.
Current unmirrored portrait exports in `native-exports/` support the
[jig and FreeCAD CAM workflow](pcb-jig-and-freecad-cam.md). Editable PCB CAM sources
live in `mechanical/pcb/`; review NC/setup sheets live in the manufacturing
package. FreeCAD CAM is controlled through Robust MCP Server; KiCad through Konnect.

## Enclosure manufacturing output

`manufacturing/enclosure/` presents the primary multi-plate `p1-enclosure.3mf` beside its `README.md`. Supporting STEP interchange files live in `supporting/step/`; individual part/coupon STL meshes live in `supporting/stl/`. The 3MF project is self-contained. Editable FreeCAD source remains in `mechanical/enclosure/`, and verification records remain in `docs/verification/enclosure-p1/`.

The enclosure export tools preserve this hierarchy on regeneration. Relocation of the supporting assets preserved their bytes; verification-record paths and documentation links were updated without changing the recorded geometry or slice results.

## Current PCB manufacturing sources

FreeCAD CAM sources are in `mechanical/pcb/`; native selected-layer exports,
Gerber-derived planar inputs and review NC are in `manufacturing/pcb/carvera-air/`.
Current PCB manifests and checks are in `docs/verification/`. Superseded PCB
manufacturing exports and reports belong in Git history, not parallel packages.

Reusable scripts belong in `tools/`; temporary work belongs in ignored `.agent-scratch/`. Keep local preferences, automatic backups, caches and editor history out of version control.

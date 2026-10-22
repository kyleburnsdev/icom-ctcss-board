# Repository layout

Editable KiCad sources, library tables and required libraries live together in `electronics/`. `${KIPRJMOD}/libraries/...` references continue to resolve relative to the project. FreeCAD sources belong in `mechanical/enclosure/`, and Arduino sources in `firmware/`.

The PCB manufacturing package lives in `manufacturing/pcb/carvera-air/`. Original portrait exports and their manifest are in `native-exports/`. The transformed landscape package, its manifest and the Makera Studio project remain together in `landscape-y-flip/`. Native exports must not be mixed with the transformed imports. The package README describes machining orientation and process constraints.

## Enclosure manufacturing output

`manufacturing/enclosure/` presents the primary multi-plate `p1-enclosure.3mf` beside its `README.md`. Supporting STEP interchange files live in `supporting/step/`; individual part/coupon STL meshes live in `supporting/stl/`. The 3MF project is self-contained. Editable FreeCAD source remains in `mechanical/enclosure/`, and verification records remain in `docs/verification/enclosure-p1/`.

The enclosure export tools preserve this hierarchy on regeneration. Relocation of the supporting assets preserved their bytes; verification-record paths and documentation links were updated without changing the recorded geometry or slice results.

## Relocation verification — 2026-10-21

The KiCad project, schematic, PCB, library tables, libraries, CAM archive, geometry exports and existing manifests were relocated without changing their bytes. Documentation and maintained tool paths were updated separately. No new ERC, DRC or manufacturing acceptance is implied by this relocation.

Existing evidence files and manifests retain their recorded paths, source basenames, revision descriptions and hashes as historical provenance. In the native export manifest, `landscape-y-flip/manifest.json` now means the sibling `../landscape-y-flip/manifest.json`; source design basenames resolve under `electronics/`. The original landscape manifest predates the added CAM project and does not attest to that archive.

Makera Studio's archive passed ZIP integrity inspection. On 2026-10-21, the project owner verified that the relocated CAM project opened correctly in Makera Studio with its layers intact. This completes the opening and layer-preservation check. For publication, CAM import-name metadata was made relative; embedded geometry is unchanged. After metadata cleanup, the project owner successfully reopened the sanitized archive in Makera Studio and confirmed that its layers looked correct on 2026-10-21. Toolpaths and machining settings remain subject to the manufacturing checks documented in the package README.

Reusable scripts belong in `tools/`; temporary work belongs in ignored `.agent-scratch/`. Keep local preferences, automatic backups, caches and editor history out of version control.

Relocation checks passed: library targets exist, local Markdown links resolve, manufacturing hashes match, maintained Python tools parse, and all 61 exported-netlist assertions pass. Only the two manufacturing READMEs changed among relocated files.

## Documentation cleanup — 2026-10-21

Build references now live in `docs/reference/`; retained revision-specific checks and source hashes live in `docs/verification/`. The former `docs/implementation/evidence/` catch-all was removed. Duplicate renders, historical checkpoints, raw tool readbacks, diagnostic XML, downloaded manufacturer PDFs/page extracts and seller-image copies are no longer maintained. Accepted pin maps, manufacturer links and seller-source notes preserve design decisions and provenance. Obsolete development artifacts are excluded from the initial public snapshot. CAD and manufacturing sources were unchanged.

Cleanup checks passed: all local documentation links resolve, reviewed source hashes match the current hardware, retained exports/check records match their committed contents allowing Git line-ending conversion, and all 61 netlist assertions pass.

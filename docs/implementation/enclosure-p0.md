# P0.1 enclosure implementation — historical

Superseded by [P1](enclosure-p1.md). The [P0.1 native baseline](../../mechanical/enclosure/revisions/p01-enclosure.FCStd) and the evidence below describe the previous geometry. Manufacturing now delivers P1.

Implemented on 2026-10-22 through the FreeCAD MCP server using FreeCAD 1.1.1. The model uses native Part primitives, constrained Sketcher roof profiles, boolean features, chamfers, Draft lettering and a Spreadsheet parameter sheet. It requires the standard Part, Sketcher, Draft and Mesh modules; no third-party workbench or Python feature proxy is needed to reopen it.

The body is 180 × 150 × 65 mm, with the existing PCB flat on insulating standoffs. The removable operator lid carries the LCD, encoder, bypass toggle and two 5 mm LEDs. Two rear GX16-8 bulkheads have reinforced open-top nut cradles. The front wall is closed; programming is performed before assembly or with the lid removed. A detachable LCD cradle and two LED keepers make the panel serviceable.

| Artifact | Location |
| --- | --- |
| Primary manufacturing build | `p01-enclosure.3mf` (historical export) |
| Supporting STEP assembly | `p0-enclosure-assembly.step` (historical export) |
| Supporting individual meshes | [STL assets](../../manufacturing/enclosure/supporting/stl/) |
| Editable assembly | [p01-enclosure.FCStd](../../mechanical/enclosure/revisions/p01-enclosure.FCStd) |
| Primary 3MF build and assembly instructions | [Fabrication package](../../manufacturing/enclosure/README.md) |
| Dimensioned layout | [Layout drawing](../verification/enclosure-p0/layout.svg) |
| Rear label orientation | [Rear exterior](../verification/enclosure-p0/rear-labels.png) |
| Prepared 3MF plates and layer checks | [Plate results](../verification/enclosure-p0/multi-plate-checks.json) |
| Assembly view | [Assembled enclosure](../verification/enclosure-p0/assembled.png) |
| Base construction view | [Base interior](../verification/enclosure-p0/base-interior.png) |
| Operator panel construction view | [Lid underside](../verification/enclosure-p0/lid-underside.png) |
| Native geometry and exported mesh checks | [CAD checks](../verification/enclosure-p0/cad-checks.json) |
| Defaults, corrections and prototype evidence | [Decision register](../requirements/enclosure-decision-register.md) |

## Editing and regeneration

`PrintedParts` contains the five assembly parts. `InstalledEnvelopes` contains the PCB, sockets/module, component allocations and visual hardware; exclude these reference objects from fabrication. `FitCoupons` contains five independent test pieces. `Construction` preserves the native feature tree. Editing does not depend on temporary files.

Dimensions are held in the `Parameters` sheet and in the named native construction features. Spreadsheet aliases drive the case shell, key openings and fastening dimensions; supporting geometry has editable native dimensions. Coordinate/layout changes require moving their corresponding mounts, legends, coupons and reference envelopes together and repeating the CAD checks. Use millimeters for the sheet's numerical entries.

The maintained [FreeCAD builder](../../tools/build-enclosure.py) reconstructs this baseline and exports the assembly, meshes and CAD report. Run it through FreeCAD MCP as described in [tools documentation](../../tools/README.md). It refuses to overwrite an open document with the same name. Save edits before closing or rebuilding. The builder uses Windows Arial Bold for the engraved legends; the saved native shapes do not require the font to display.

## Verification

The ten exported enclosure/coupon meshes were reopened after writing. Each has a valid single-solid BRep, a closed mesh with no detected non-manifold edges or self-intersections, and bed-level coordinates. The lid and LCD coupon use the bundled Netgen mesher; the remaining parts use OCC tessellation. The five assembly parts have zero mutual intersection volume; the PCB does not intersect the base. The modeled carrier allocation has 1.15 mm clearance to the LCD/backpack allocation and both GX16 rear envelopes. Mesh dimensions, triangle counts, volumes and build-space calculations are recorded in the JSON report.

The assembly coordinate transform and four board holes follow the electronics implementation record. Printed geometry was added around the existing board; no KiCad files, hole positions or electrical interfaces were changed. The register holds revision-specific physical and slicer acceptance status.

The rear text reads upright from outside: RADIO is on the viewer’s left and MICROPHONE on the viewer’s right. Connector identities and coordinates are preserved. The prepared `3MF project` (historical export) contains three plates: fit coupons first, then base, then lid/retainers. Its geometry, shared profiles and all three sliced toolpaths are embedded. Filament and process changes apply globally so coupon printing is part of the normal workflow.

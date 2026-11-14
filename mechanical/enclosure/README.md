# Enclosure

**Current direction — 2026-11-13:** the actual design will use the Grove LCD RGB
Backlight V4.0. Keep this P1 enclosure as a reference until the working assembled
PCB's as-built is available, then revise the case around that assembly rather
than each interim change. P1's earlier LCD window and mounts do not establish
Grove fit. See the [decision register](../../docs/requirements/enclosure-decision-register.md#display-and-enclosure-sequencing--user-decision-2026-11-13).

Open [icom-ctcss-enclosure.FCStd](icom-ctcss-enclosure.FCStd) in FreeCAD 1.1.1. P1 uses native Part Design bodies, constrained Sketcher profiles, Draft lettering and a Spreadsheet; no third-party workbench is required.

- [P1 design, views and verification](../../docs/implementation/enclosure-p1.md)
- [Primary 3MF build and assembly instructions](../../manufacturing/enclosure/README.md)
- [Requirements](../../docs/requirements/enclosure-specification.md)
- [Decision and prototype register](../../docs/requirements/enclosure-decision-register.md)
- [Reproducible builder](../../tools/build-enclosure.py)

The saved model retains installation coordinates. Print-oriented meshes are supporting assets beneath the primary build. `revisions/p01-enclosure.FCStd` preserves the previous native baseline.

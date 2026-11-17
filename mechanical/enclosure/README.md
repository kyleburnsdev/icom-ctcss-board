# Enclosure

**Current direction — 2026-11-17:** [C1](c1/README.md) evolves the printed B1/B2
bench concept into a 156 × 240 mm PLA enclosure/radio cradle. It uses the Grove
V4.0, removes the PTT-test button, rotates the unchanged PCB 90°, substitutes
nubs and insert-fastened corner straps, and adds a captured sliding cover with
a 12° radio support. Start with the [C1 package](../../manufacturing/enclosure-c1/README.md)
and [illustrated guide](../../docs/enclosure-c1-guide.md). C1 is a prototype;
physical fit/load/temperature acceptance remains pending. P1 below is retained
as an earlier reference and does not establish Grove or C1 fit.

Open [icom-ctcss-enclosure.FCStd](icom-ctcss-enclosure.FCStd) in FreeCAD 1.1.1. P1 uses native Part Design bodies, constrained Sketcher profiles, Draft lettering and a Spreadsheet; no third-party workbench is required.

- [P1 design, views and verification](../../docs/implementation/enclosure-p1.md)
- [Primary 3MF build and assembly instructions](../../manufacturing/enclosure/README.md)
- [Requirements](../../docs/requirements/enclosure-specification.md)
- [Decision and prototype register](../../docs/requirements/enclosure-decision-register.md)
- [Reproducible builder](../../tools/build-enclosure.py)

The saved model retains installation coordinates. Print-oriented meshes are supporting assets beneath the primary build. `revisions/p01-enclosure.FCStd` preserves the previous native baseline.

# B1 temporary assembled-board bench holder

| Requirement | Acceptance |
| --- | --- |
| BH-01 | Retain the unchanged PCB with four nylon M3 screws at its existing enclosure mounts |
| BH-02 | Keep 12 mm between PCB underside and floor; 10 mm under 2 mm lead tails; no blind PCB screw floor |
| BH-03 | Hold the control face at 30°, secured by four M3 screws and M3 × D5 × L4 inserts |
| BH-04 | Provide readable physical labels for all eight mounted components |
| BH-05 | Support radio-free 8 V power and a normally-open PTT button; preserve probe/USB/trimmer access |
| BH-06 | Fit every oriented part and brim within the X1C bed/exclusions; isolate fit tests in the same primary 3MF |
| BH-07 | Deliver native source, print project and illustrated assembly/test procedure; distinguish digital checks from physical acceptance |

The authoritative editable source is [bench-holder-b1.FCStd](bench-holder-b1.FCStd).
Print from the [prepared 3MF](../../manufacturing/bench-holder/bench-holder-b1.3mf),
following the [illustrated guide](../../docs/bench-holder-guide.md).

The 210 × 220 mm insulating base holds the unchanged 150 × 100 mm PCB on four
12 mm-high supports. Nylon M3 × 0.5 screws enter 6 mm of modeled thread at Z9–15,
with 3.4 mm clearance bores below, so a
blind screw floor cannot prevent clamping. Two integral side rails support a
210 × 90 mm control face at 30° above horizontal. Four M3 × 8 screws enter the
user's M3 × D5 × L4 heat-set inserts, normal to that face. All eight panel
components have raised labels.

The model tree separates production parts, fit coupons, simplified reference
envelopes and editable label text profiles. Geometry uses constrained Sketcher,
Pad, Pocket and **native SubtractiveHelix** history. Each PCB screw thread has
an editable 60° flank sketch, 0.5 mm pitch and 6 mm height. Native Pockets form
the core and lower clearance bore. The generator controls layout; native sketch
constraints, helix pitch/height, pad lengths and text profiles are also editable
in FreeCAD. Rebuilding overwrites this source, so preserve manual edits.

Rebuild using FreeCAD 1.1's bundled Python:

```powershell
& 'C:/Program Files/FreeCAD 1.1/bin/python.exe' tools/build-bench-holder.py
python tools/prepare-bench-holder.py
```

Close the exact holder document before rebuilding; do not rebuild over a live
document or unsaved changes. To save the assembly display and native image,
start FreeCAD 1.1 with its installed Robust MCP bridge, leave no documents open,
then run `python tools/inspect-bench-holder.py`. It opens this exact source and
refuses to replace live documents. Render drawings/layer evidence afterward with
`& 'C:/Program Files/FreeCAD 1.1/bin/python.exe' tools/render-bench-holder.py`.

Assembly coordinates remain in the FCStd and STEP. Only STL print copies undo
the control-panel rotation and translate onto Z0. The PCB coordinate transform
is X = 175 − board-local Y, Y = 105 + board-local X. The 30° panel placement
is a rotation about its local X axis followed by translation to front Z30.
The optional PCB spacer source represents one of four copies in the 3MF.

No final-enclosure, KiCad or firmware source is modified. Native CAD, meshes and
slicing verify digital geometry; the coupon and installed-assembly checks in
the guide remain physical acceptance steps.

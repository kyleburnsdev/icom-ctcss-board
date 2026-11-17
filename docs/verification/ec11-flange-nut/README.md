# EC11 flange nut N1 verification

2026-11-16. Accessory for B1's actual encoder mounting interface. The original
holder source and its three-plate 3MF were not modified. No printer was operated.

- [CAD checks](cad-checks.json): native FreeCAD 1.1.1 construction through Robust
  MCP; actual live/saved B1 encoder bore radius 3.6 mm, seat radius 10 mm and
  pocket depth 1.5 mm read back. B1's source hash is retained. Six valid single
  solids, fully constrained profiles and native right-hand SubtractiveHelix
  features; the saved source reopened successfully.
- [Native view](native-model.png): conventional body trees with flange pad,
  hex pad, core pocket, entry grooves, helix and notch pockets. Three nuts and
  independent A/B/C ring coupons. The actual B1 panel-seat crop under NutB is
  a reference excluded from exports. NutB/seat intersection is zero.
- Six STL files read back through native Mesh: all closed solids, flat face at
  Z0, bounds under 14 × 14 × 3 mm. Native Part export supplies corresponding STEP.
- [Slicer checks](slicer-checks.json): Bambu Studio **2.8.2.61**, two named plates,
  three objects per plate, embedded machine/material/process and toolpaths,
  archive integrity and saved transforms. Both slice warning strings empty.
- GUI reopen observed both plates, Generic PLA, X1C 0.4, four walls and 30%
  gyroid; Quality displayed layer and initial-layer heights **0.12 / 0.12 mm**.
  The file was opened as a project. No loaded user project was saved over.
- [Layer checks](layer-checks.json): 19 coupon layers to Z2.28 (2.25 mm mesh
  rounded by the slicer), 25 nut layers to Z3.00. All three bores retain varying-
  radius outer-wall contours in the thread band. [Coupon paths](toolpaths-plate-1.png)
  and [nut paths](toolpaths-plate-2.png) were visually inspected at first layer,
  washer transition and thread layers for continuity and unsupported features.
  No support structures are generated.
- [Illustrated fitting guide](../../ec11-flange-nut-guide.md): native model and
  dimensioned seat/stack drawing inspected for readable labels and orientation.

Inventory [request](inventory-request.yaml) / [preflight](inventory-preflight.json)
retain input hashes and findings. The authoritative store has no Generic PLA
entry and incomplete machine quantity/process/material/envelope metadata, so
this is not a passed inventory preflight. The user explicitly selected PLA with
the existing X1C setup; the 256 mm build volume is established. Those inputs
govern this package. No stock quantity was invented, reserved or decremented.

**Physical acceptance pending:** exact generic encoder pitch, ring choice,
3 mm exposed bushing reach, full-nut engagement, hand clamp retention and knob/
button clearance. The radial allowances are FDM trials, not certified fits.
The [Bourns drawing](https://www.bourns.com/docs/product-datasheets/pec11r.pdf)
supports the selected M7 × 0.75 trial pitch, not the exact WWZMDiB identity.
No physical print or mounting result is claimed.

Rebuild: open B1 in FreeCAD, close the N1 document, invoke `main()` from
[build-ec11-flange-nut.py](../../../tools/build-ec11-flange-nut.py) through
Robust MCP `execute_python`; then run ordinary Python
`tools/prepare-ec11-flange-nut.py` and `tools/render-ec11-nut-guide.py`.
Generator constants own regeneration inputs; native feature edits remain
available. Recheck geometry, saved/reopened CAD and slicing after edits.

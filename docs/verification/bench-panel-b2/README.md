# B2 rear-display panel verification

**Current LCD interface: L1.** The original coupon failed physical size/alignment;
the digital checks below now cover the corrected geometry. See the
[failure record](../lcd-fit/failed-coupon-2026-11-17.json) and
[L1 correction](../../lcd-fit-correction.md). L1 physical acceptance is still pending.

Scope: a digitally prepared replacement panel and printed display fasteners.
Physical print, screw retention, module fit and seated visibility are unrun.

- [Native CAD checks](cad-checks.json): named native sketch/Pad/Pocket/helix
  features, closed single-solid meshes, source and mesh hashes, protected base
  interface comparison, display/plug allowance intersections with base and panel.
- [Slicer checks](slicer-checks.json): real Bambu Studio two-plate slicing,
  settings, names, object counts, bed seating, saved-layout readback, estimates.
- [Layer review](layer-checks.json), [coupon plate](slice-1.png) and
  [replacement-panel plate](slice-2.png): actual extrusion at the first layer,
  engraving closure, front recess roofs, rear posts and threaded sockets.
  Both slices returned success with empty warning messages. The saved project
  reopened and re-sliced through native Bambu Studio with both named plates,
  X1C 0.4 / Generic PLA, 0.12 mm layers and 0.20 mm first layer; all warnings empty.
- [Illustrated operator guide](../../bench-panel-b2-guide.md): coupon acceptance,
  printing, clean-up, hardware transfer and internal harness routing.

Manufacturer XY dimensions are from page 23 of the linked JHD1313 V4 drawing.
L1 uses **40 mm hole rows**, viewing-area bottom **16.34 mm above PCB bottom**,
and **9.43 mm supports** from the user's **9.13 mm front projection** plus a
selected 0.30 mm gap. Six ears are modeled for clearance. Coarse thread clearances
and the cable allowance remain selected defaults; the actual module/cable coupon
check remains necessary. CAD envelope clearance
is not a measurement of an assembled cable or a physical fit acceptance.

The [inventory preflight](inventory-preflight.json) was rerun against the authoritative workstation store using
the existing B1 input. It retains the recorded unknown quantities and missing
machine capability metadata described in the [B1 disposition](../bench-holder/README.md#inventory-findings-and-disposition).
Existing user-established PLA/printer/control facts are carried forward. No
new purchased hardware is selected: the user's requested custom fasteners are
printed from the existing PLA setup. No inventory stock was changed or reserved.

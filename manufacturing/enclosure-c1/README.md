# C1 narrow enclosure / radio cradle — PLA fit prototype

**Current LCD interface: L1**, correcting the failed original B2-derived geometry.
The updated panel/coupon use 40 mm hole rows and 9.43 mm supports from the
user's 9.13 mm measurement. Print the L1 test plate first;
[correction and physical retest checks](../../docs/lcd-fit-correction.md).

Start with the [illustrated fabrication and assembly guide](../../docs/enclosure-c1-guide.md).

- **Primary print project:** [ctcss-c1.3mf](ctcss-c1.3mf). Open as a project in Bambu Studio. Four plates: independent interfaces, base, panel/retainers/cheeks, cover/saddles.
- **Print first:** plate **01 - TEST FIT - L1 LCD radio nubs inserts rails**.
- [Editable C1 FreeCAD model](../../mechanical/enclosure/c1/ctcss-c1.FCStd).
- [Assembly STEP](supporting/step/ctcss-c1-assembly.step); [individual print-oriented meshes](supporting/stl/).
- [Current CAD/export/slicer evidence](../../docs/verification/enclosure-c1/).

156 × 240 mm base; 156 × 90 mm, 30° panel; PCB rotated 90° relative to B1;
PTT-test button removed; locating nubs, relieved corner straps, captured sliding
cover and 12° radio cradle. Use PLA, X1C 0.4 mm / textured PEI, 0.20 mm layers,
five walls, six top/bottom layers, 30% gyroid, 3 mm brim, supports off.

Bambu Studio 2.8.2.61 estimates about **25 h 33 min / 603 g** including coupons:
plate 01 **2 h 22 min / 55 g**, base **13 h 28 min / 316 g**, panel set
**2 h 50 min / 74 g**, cover set **6 h 53 min / 158 g**. All final slice/reopen
warning strings are empty. Actual print time and use remain machine results.

All 24 enclosure screws are M3 × 8 socket-head cap screws, into D5 × L4 inserts.
The radio retains its OEM M4 × 8 interface; see [mounting documentation](../../docs/reference/ic229h-mounting.md).
Allow 32 inserts including all fit trials. M3 screw stock is user-confirmed;
insert counts and radio bolts remain a kit check. The store preflight remains
failed for missing quantity/capability records, separately from the geometry and
the user's PLA choice.

No physical C1 fit, sustained radio load or PLA temperature acceptance has been
performed. Do not skip the guide's coupon and unpowered installation checks.

# C1 — bench-derived narrow enclosure

**LCD interface L1:** the panel/coupon now read the shared
[Grove definition](../../interfaces/grove-lcd-v4.json), including the corrected
40 mm row spacing/window datum and 9.43 mm seat depth from the user's 9.13 mm
measurement. Print the new LCD coupon before a full panel. The base, cover,
saddles, cheeks and main-PCB straps are geometrically unchanged by L1.

Open [ctcss-c1.FCStd](ctcss-c1.FCStd) in FreeCAD 1.1. The new design preserves
the earlier B1/B2/P1 sources and their live documents. See the
[illustrated guide](../../../docs/enclosure-c1-guide.md) and
[prepared print package](../../../manufacturing/enclosure-c1/README.md).

The model separates enclosure parts, independent fit coupons, editable text
profiles and reference envelopes. Native Sketcher/Pad/Pocket features define the
parts; App Links repeat straps and LCD clips. A simplified radio, display,
board/component allocations and connector envelopes are reference objects,
excluded from printing. Assembly coordinates are retained; STL copies alone are
oriented for printing and normalized to bed Z0.

Layout is owned by [build-enclosure-c1.py](../../../tools/build-enclosure-c1.py).
It uses the maintained B1 native-sketch builder, but does not load or alter B1.
Run `main()` through Robust MCP with only the exact C1 document closed; preserve
any manual C1 edits before regeneration. Then run the native
[exporter](../../../tools/export-enclosure-c1.py) through Robust MCP and
`python tools/prepare-enclosure-c1.py` using installed Bambu Studio.

User inputs: PLA, ample M3 × 8 SHCS stock, no PTT-test button, board rotated 90°,
nubs/corner straps, sliding radio support; radio holes 39/88 mm from faceplate
flat and 20 mm above bottom. Selected design defaults: 156 × 240 footprint,
30° panel / 12° radio angles, 0.3 mm sliding clearances, 3.6 mm PCB nubs,
4.6 × 5.5 mm insert pilots, profile in the guide. The radio bolt size follows
the documented Icom part-number match; its allowable insertion is not inferred.

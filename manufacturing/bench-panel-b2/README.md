# B2 replacement control panel

**Open [bench-panel-b2.3mf](bench-panel-b2.3mf) as a project and print plate 01
first.** Follow the [illustrated printing and assembly guide](../../docs/bench-panel-b2-guide.md).

The LCD sits behind a screen-only window; the Grove connector and harness stay
inside. Four **printed coarse-thread thumb screws** clamp its mounting ears onto
integral rear supports. No purchased display fasteners are required. These are
custom 5 mm × 1 mm threads, not standard M5 screws.

This is a replacement for the removable B1 panel. **Reuse the existing B1 base,
panel screws, inserts, LED keeper, controls and main-PCB supports.** The panel's
210 × 90 mm outline, 3 mm skin, 30° installed placement and four base holes stay
unchanged. The display shifts 3 mm right for rear PCB-to-rail clearance. Labels
are engraved so the panel prints front down with the rear supports up.

| Plate | Contents | Slicer estimate |
| --- | --- | --- |
| 01 - TEST FIT - rear display and threads | Independent full display interface coupon, three thread trials, four trial thumb screws | 2 h 22 min / 22.2 g |
| 02 - FINAL - replacement panel and clamps | One replacement panel and four thumb screws | 3 h 39 min / 50.1 g |

Four accepted test screws can be reused; the production duplicates are optional.
The project embeds installed X1C 0.4 / Generic PLA / Textured PEI settings:
0.12 mm layers, 0.20 mm first layer, four walls, five top/bottom layers,
30% gyroid, 3 mm outer brim, supports off. See the guide for inspection gates.

Editable [FreeCAD source](../../mechanical/bench-holder/bench-panel-b2.FCStd),
[assembly STEP](bench-panel-b2-assembly.step), print-oriented
[panel](controlpanel.stl), [thumb screw](displaythumbscrew.stl),
[display coupon](displayfitcoupon.stl) and thread trials
[A](threadfita.stl), [B](threadfitb.stl), [C](threadfitc.stl) are supplied.

CAD and slicing evidence: [verification](../../docs/verification/bench-panel-b2/README.md).
Physical printed fit, retention and seated viewing acceptance remain to be run.

# N1 EC11 nut with integrated washer

**Open [ec11-flange-nut-n1.3mf](ec11-flange-nut-n1.3mf) as a Bambu Studio project.
Print plate 01 first.** Follow the [illustrated print and installation guide](../../docs/ec11-flange-nut-guide.md).

For the existing B1 bench holder's encoder: M7 × 0.75 right-hand thread,
14 mm integrated washer, 11 mm hex, 3 mm overall height. The washer fits the
20 mm recessed seat and covers the 7.2 mm opening on the 1.5 mm land. No loose
washer is required. The holder's CAD and original three-plate print project
remain the same; this is a separate small accessory print project.

| Plate | Contents | Slicer estimate |
| --- | --- | --- |
| 01 — TEST FIT | A/B/C independent thread rings; one/two/three identification notches | 9 min 31 s / 1.10 g |
| 02 — FINAL | Matching A/B/C flanged nuts; **install one**, retain alternatives as spares | 11 min 3 s / 1.01 g |

A/B/C have +0.05/+0.10/+0.15 mm **radial** thread allowance, respectively.
Print all three test rings, choose the snug freely turning fit, then use the
matching nut. These are fit alternatives for the same M7 × 0.75 thread, not
different thread pitches. Physical thread and clamping acceptance remain to be run.

Saved settings: X1 Carbon 0.4 mm nozzle, Generic PLA, Textured PEI, 0.12 mm
layers including first layer, 0.42 mm widths, four walls, five top/bottom layers,
30% gyroid, Arachne, supports off, 3 mm outside brim, 220 °C nozzle / 55 °C bed.
Flat flange face on the bed; thread axis vertical. Select the loaded PLA in
the printer workflow. All settings and both named plates are embedded;
the project was reopened in Bambu Studio 2.8.2.61 to check its effective settings.
No printer connection or print was performed.

Editable source: [ec11-flange-nut-n1.FCStd](../../mechanical/bench-holder/ec11-flange-nut-n1.FCStd).
Each part has conventional constrained profiles, pads, a bore, lead-in groove,
native SubtractiveHelix and identification pockets. The cropped B1 panel seat
is a labelled reference excluded from exports. The maintained builder is
[build-ec11-flange-nut.py](../../tools/build-ec11-flange-nut.py).

Print-oriented STL / STEP pairs:

| Variant | Fit ring | Flanged nut |
| --- | --- | --- |
| A — 1 notch | [STL](coupona.stl) / [STEP](coupona.step) | [STL](nuta.stl) / [STEP](nuta.step) |
| B — 2 notches | [STL](couponb.stl) / [STEP](couponb.step) | [STL](nutb.stl) / [STEP](nutb.step) |
| C — 3 notches | [STL](couponc.stl) / [STEP](couponc.step) | [STL](nutc.stl) / [STEP](nutc.step) |

[Verification evidence](../../docs/verification/ec11-flange-nut/README.md) separates
CAD, mesh, slicer, inventory records and the pending physical acceptance.

# B1 temporary bench holder

**Print [bench-holder-b1.3mf](bench-holder-b1.3mf), starting with plate 01.**
Follow the [illustrated fabrication, assembly and radio-free test guide](../../docs/bench-holder-guide.md).

The labeled control face sits at 30°. Four M3 screws enter the user's M3 × D5 ×
L4 heat-set inserts; four nylon M3 screws secure the PCB in the upper 6 mm of
thread, with open 3.4 mm clearance bores below. The 12 mm PCB supports leave 10 mm nominal floor clearance below the
existing 2 mm trimmed-lead allowance. No blind PCB screw-hole floor can stop
clamping. Inspect actual leads and screw tips as directed in the guide.

| Plate | Contents | Slicer estimate |
| --- | --- | --- |
| 01 - TEST FIT - interfaces | Hardware bore, PCB/LCD mount and angled insert coupons | 1 h 22 min / 38.7 g |
| 02 - FINAL - base | One 210 × 220 × 75 mm base | 4 h 6 min / 147.6 g |
| 03 - FINAL - controls | Labeled panel, LED keeper, four optional 2 mm PCB spacers | 1 h 19 min / 40.8 g |

Approximately **6 h 47 min / 227 g PLA total**, including coupons and brim:
about **1 h 41 min (20%) faster** than the previous full-height fine-layer package.
Installed X1C 0.4 mm / Generic PLA / Textured PEI settings are saved: **0.20 mm
default layers**, with **0.12 mm only at Z8.8–15.2 on the base and PCB mount
coupon**. Four walls, 0.6 mm skins (3 coarse / 5 fine layers), 15% gyroid,
5 mm outer brim, supports off,
220 °C nozzle and 55 °C bed. Open as a project to retain settings and plate names.
Select the actual loaded PLA in the printer workflow before printing.

The print orientations are already saved. The panel lies flat for printing;
the base rails establish its assembled angle. The 4.6 mm production insert
pilot is a trial default: accept the coupon first, changing/rebuilding the
base if the 4.4 or 4.8 mm trial works better. No physical print/fit is claimed.

Editable source: [FreeCAD B1](../../mechanical/bench-holder/bench-holder-b1.FCStd),
with [model/rebuild notes](../../mechanical/bench-holder/README.md).
[Assembly STEP](bench-holder-b1.step) preserves the base/panel/keeper positions.
STLs are individual print copies: [base](base.stl), [panel](controlpanel.stl),
[keeper](ledkeeper.stl), [optional spacer](pcbspacer.stl),
[interface coupon](interfacecoupon.stl), [mount coupon](mountcoupon.stl),
[insert coupon](insertcoupon.stl).

Current native, mesh, slicer and GUI evidence is in the
[verification record](../../docs/verification/bench-holder/README.md).
The radio and hand microphone remain disconnected during this bench setup.

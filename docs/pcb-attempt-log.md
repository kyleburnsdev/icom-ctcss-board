# White-mask sublimation trial log

Prepared 2026-11-12 on `feature/sublimation-silkscreen`. **No physical run yet.**
Use the [guide](pcb-fabrication-guide.md); retain earlier work in the
[diamond-drag log](pcb-diamond-drag-attempt-log.md).

| Input / outcome | Actual setting or result |
| --- | --- |
| Date / board ID / artwork manifest hash | Not run; `verification/pcb-sublimation.json` |
| Printer / ink | User: converted Epson E-15000 / Cosmos Ink sublimation ink |
| Mask | User: Mechanic, white foundation; exact code not recorded |
| Paper / driver / color profile | Not recorded |
| Transfer mirroring | Printer automatic; file/application mirror OFF |
| Coupon / bottom / top coats and cure per coat | Not recorded |
| Press | User-directed assumption: generic 12 × 12-inch clamshell T-shirt press; make/model unspecified |
| Support / release sheets / heat tape / cold closure check | Not recorded; setup not run |
| Selected first printed test | T1: 185 °C / 365 °F, 60 s, light pressure, warm peel about 40–50 °C; not run |
| Actual temperature / dwell / pressure / peel / cooling | Not recorded; distinguish setpoint from measured temperature |
| Pad material / thickness / size / installed or extra | Not recorded |
| Top/bottom blowout paper / optional PTFE cover | Not recorded; fresh paper each cycle |
| Pressure knob mark / turns / cold corner-contact check | Not recorded |
| Transfer drying time / tape width / tab or edge-strip pattern | Not recorded |
| Peel delay / approximate temperature / paper or mask sticking | Not recorded |
| Printed scale X / Y | Not measured |
| F L orientation / six colors / white knockout | Not inspected |
| 0.10 / 0.15 / 0.20 / 0.30 mm lines / native board-text sample | Not inspected |
| Dye uptake / adhesion / paper release / ghosting / warping | Not inspected |
| Unprinted bottom after single heat cycle / support sticking / softening | Not inspected |
| Accepted coupon recipe and decision | Not accepted |
| Copper zero/map retained through pad clearing | Not run |
| Pad overtravel / offsets / count / exposure | CAM 0.05 mm / zero offset; not run |
| Top transfer / registration error | Not run |
| Bottom legend | Removed; no bottom print or transfer setup |
| Both faces after final cycle / pad residue / solderability witness | Not inspected |
| Backing / minimum drilling Z | CAM 1.00 mm support / +0.85 mm; not run |
| 119 holes / lead fit / deburring / coating integrity | Not inspected |
| Continuity/isolation before coating and after holes | Not measured |
| Photos / failures / changed variable / next action | None recorded |

Use a fresh row set per changed coupon. Preserve failures; distinguish digital
checks, transfers, machine runs and electrical measurements.

## Coupon series

Run only as far as needed. Each row uses fresh, room-temperature coated scrap
and fresh paper. Keep light pressure/warm peel unless the test changes that one
variable. See the [complete application procedure](pcb-fabrication-guide.md#1-qualify-the-transfer-on-scrap).

| ID | Selected setting | Actual setting / observations / photo | Accept / next change |
| --- | --- | --- | --- |
| H0 | Heat-only: 185 °C / 60 s / light; inspect after cooling | Not run | Pending |
| T1 | Print: 185 °C / 60 s / light / warm peel 40–50 °C | Not run | Pending |
| T2 | If uniformly weak: 195 °C / 60 s, otherwise same | Not run | Pending |
| T3 | If improving but weak: 195 °C / 90 s, otherwise same | Not run | Pending |
| T4 | Optional last check: 200 °C / 90 s, only with sound coating | Not run | Pending |
| P | Best temperature/time, change light → medium only for uneven contact | Not run | Pending |
| C | Best thermal recipe, change warm → cold peel 20–30 °C | Not run | Pending |
| H | Best thermal recipe, hot peel within about 5 s if warranted and mask sound | Not run | Pending |
| Full board | Accepted coupon recipe, same pad/paper/cover/pressure; inspect center/corners | Not run | Pending |

# Independent design review

**Current sourcing revision (2026-10-22):** see [sourcing verification](../verification/sourcing-revision.json). Fresh ERC: 0 errors/0 warnings; DRC: 0 errors/0 unconnected, 115 retained warnings (38 library comparisons, 35 silk/field overlaps, 42 metadata/mechanical parity). All 111 electrical pads match the schematic in an independent read-only review; 61 netlist assertions pass. There are 242 B.Cu tracks, no vias/zones and minimum calculated body gap 2.14mm. Current reports and drawings were regenerated; the older narrative/results below are historical where they differ.

Reviewed 2026-10-20 against [the board specification](../requirements/board-specification.md). The reviewer did not build or modify the schematic, footprints, PCB, or project configuration. This report evaluates the saved prototype design; it does not approve machining, radio connection, or powered operation.

**Verdict: NEEDS ATTENTION — review warnings before manufacturing.** The automatic full-review coverage is complete: all six requested audits completed, one schematic file/sheet instance, 43 resolved schematic symbols, 42 board footprints, and no coverage diagnostics. Physical part fit, machine capability, radio interfaces and regulator performance remain unverified acceptance items. No confirmed electrical short, missing required route, or copper clearance error was found.

## Evidence collected independently

The [review summary](../verification/review-summary.json) retains the source SHA-256 hashes, netlist assertion count and ground-geometry conclusions from the 2026-10-20 OFF/A0 cleanup review after R16 removal, the J5 two-pin change and final A0 NC legend correction. The original review operations were read-only. Raw tool transcripts and superseded inspection artifacts were removed from the maintained tree during documentation cleanup; prior raw records are excluded from the public snapshot. This is historical verification, not a new CAD review.

| Check | Result |
|---|---|
| Schematic short detection | 0 detected shorts |
| ERC | 0 errors, 0 warnings |
| Exported netlist assertions | 61 passed; 38 functional components |
| PCB DRC | 0 errors; 0 unconnected items; 114 warnings |
| Full review | Complete coverage; 118 warnings including the 114 DRC warnings |
| Schematic/BOM coverage | 43 resolved symbols, including power symbols; no unresolved symbols; BOM-health audit has no findings |

The exported netlist checker was rerun, rather than accepting its historical result. It verifies direct microphone/audio/power pass-through, intercepted PTT, Q1 pin order, filter/divider/trimmer/mixer order, all used module contacts, eight intentional unused contacts, separate RAW/VCC rails, UI nets and all functional footprint assignments. Regenerated cleanup schematic, top assembly and mirrored bottom-copper PNGs were inspected after export: J5 has two contacts, R16/OFF labels are absent, A0 is marked NC, J6 retains its LED/ground pairs, and no required route or component is visibly lost. They agree with the functional blocks and show no wire links or obstructed discrete parts beneath the module. The regenerated monochrome assembly SVG/PNG was re-inspected and provides clear black-on-white labels; the former pale-yellow contrast issue is resolved.

The historical board inventory reported 241 B.Cu track segments, 0 vias, 0 copper zones, 111 electrical pads, and 38 functional components plus four mounting holes. Tracks use 0.5/1.0 mm widths. The 100×150 mm outline and four 4 mm NPTH holes at 6 mm corner insets meet the mechanical geometry requirement. The conservative body-envelope check reserves 37×18.24 mm for module/socket coverage and reports a minimum adjacent-body gap of 2.14 mm; C4/C5 clear that envelope by 2.18 mm. These are nominal geometric results, not an actual socket/header/USB-cable fit test.

## Current UI headers and OFF/A0 cleanup

Live IPC pad readback from the 2026-10-20 review agrees with the current exported netlist:

| Header | Pin 1 | Pin 2 | Pin 3 | Pin 4 |
|---|---|---|---|---|
| J5 bypass, 1×2 | BYPASS/D10 | GND | — | — |
| J6 LEDs, 1×4 | PTT LED anode via R6 | GND | BYPASS LED anode via R7 | GND |

Both use 2.54 mm pitch, 2.0 mm pads and 1.1 mm drills; pin 1 is square. Each off-board switch or LED has an adjacent ground contact, permitting separate two-wire connections without a shared-ground cable splice. The grounds remain common on the board. J5's previous three/four-pin cable orders are superseded and must not be used. R16 is absent from the board inventory, the OFFSET net has zero trace segments, and U1 pad 17 is now `unconnected-(U1-A0-Pad17)` with an explicit schematic no-connect evidenced by zero ERC findings and the exported-netlist assertions. J6 remains unchanged. The bypass-only revision removes the offset function; it does not implement firmware behavior.

## DRC findings requiring explicit disposition

| Warning group | Count | Interpretation and action |
|---|---:|---|
| Library footprint mismatch | 38 | Every functional placed footprint differs from its library representation. Native KiCad normalizes THT copper layer sets, so the live source cannot be described as having only B.Cu pad lands. Preserve the measured pad/drill/numbering evidence and inspect the exact fabrication layers; do not dismiss this warning as proof of identical libraries. A library refresh alone did not remove it. |
| Footprint-owned silkscreen overlap | 34 | Native reference fields touch their own footprint artwork. Readable external board labels provide assembly references/values, but the original field overlaps remain. They do not affect bottom-copper machining. If a printed silkscreen is commissioned, repair or deliberately exclude those fields and inspect a fresh plot. |
| Schematic parity | 42 | 38 Description/custom-field differences or omissions, plus four expected extra mechanical mounting-hole footprints. These are not 42 net mismatches. Retain BOM/assembly documentation as the part-selection authority; avoid copying incomplete PCB metadata into a purchasing BOM. |

No warning was suppressed or waived by the user. The presence of readable supplemental labels does not make the CAD silkscreen warning-free. Following the user's Carvera Air laser-process clarification, the manufacturing F.SilkS export deliberately excludes native reference/value fields while retaining the external readable labels and footprint artwork. The Gerber-derived clean legend preview was separately inspected; see the [manufacturing instructions](../../manufacturing/pcb/carvera-air/README.md). Physical UV coating/exposure/cleaning capability remains a coupon check. This export update does not change the reviewed electrical design.

## Electrical and manufacturing risks still open

**Resolved layout finding — analog/UI ground branches:** the initial review found LCD/encoder return current passing through part of the analog return. The design owner removed the R4-to-UI-trunk link and added a separate 1.0 mm analog return from RV1 toward the Q1/PTT ground junction near the radio header. The initial correction query found 79 ground segments; the cleanup review summarized in the [verification record](../verification/review-summary.json) found 78 after the right UI-ground bus and bypass-header revisions. Independent segment-distance connectivity analysis, including full 1.0 mm copper widths, shows the analog cluster and UI cluster remain separate upstream of the PTT/radio junction (21 versus 43 segments wholly above Y=177 mm, minimum edge gap 2.9318 mm). The deleted link has not been recreated by thick-trace overlap. Both branches remain electrically connected through the intended common ground near the radio/PTT section; DRC from that review reports zero unconnected items. This resolves the avoidable LCD/LED current sharing in the analog branch. It is not a galvanically isolated or ideal star ground: PTT and common connector return impedance remain, and bench noise checks are still necessary.

1. **LCD I²C pull-ups:** the full audit finds no board-side SDA/SCL pull-up resistors. This is intentional only if the actual 5 V LCD backpack supplies suitable pull-ups. Verify their presence, resistance and voltage before operation. If absent, return the design for a documented Konnect change and fresh review; MCU internal pull-ups alone are not evidence of satisfactory bus operation.
2. **Supply capacity, stability and heating:** the audit flags both rails for lacking its generic ≥10 µF bulk-capacitance threshold. C6 is an intentional 4.7 µF film capacitor on +5V, with 100 nF local RAW/VCC capacitors; module-internal capacitance is not modeled as carrier-board parts. The specification does not require 10 µF, so the heuristic is not by itself a value error. Nevertheless, module regulator identity, required output capacitance, microphone-port current and load-step behavior are unproven. The 200 mA branch allocation implies approximately 0.6 W LDO dissipation from 8 V; measure full-load temperature/current and rail transients before radio use.
3. **Radio/PTT/audio acceptance:** actual cable functions, available current, PTT open voltage/sink current, saturation/reset release, microphone bias/loading and tone deviation are still bench checks. The 5 mA PTT design target is provisional. The specified 100 kΩ mixing resistor strongly reduces tone into low input impedance; the illustrative AC model cannot prove adequate deviation. Keep the minimum-level starting procedure and do not connect the radio before interface checks.
4. **Physical parts and access:** verify the actual module and two 1×12 female socket strips against a 1:1 drawing, then check USB plug access and enclosure/cable clearance. Buy the exact current supplier-linked parts in the [sourcing review](component-sourcing-review.md); generic package names do not establish drop-in fit. Confirm socket/header pin dimensions and all drill sizes before milling.
5. **CNC acceptance:** 0.5 mm isolation and enlarged pads are conservative design targets, not a validated process. Copper weight, actual drills, flatness/runout, depth, feeds and material behavior remain unknown. Prove a test coupon, inspect the CAM toolpath and verify registration/mirroring before cutting the circuit board. No reviewed machine G-code is delivered.

Native THT pads include virtual F.Cu lands as well as B.Cu lands. The physical single-sided requirement is met only by exporting and machining **B.Cu alone**, together with the outline and both drill files. Do not fabricate an all-layer/default/IPC-2581 copper set. The CAD PTH drill filename does not require plated holes: every hole in this CNC blank is unplated. Validate the final restricted package separately from the mirrored visual preview.

The user accepted 8 V to RAW for this revision; additional voltage conditioning and firmware are outside scope. This acceptance does not establish the clone's USB/RAW backfeed behavior. Follow the documented power-disconnection procedure and [staged assembly/bring-up checklist](assembly-and-bring-up.md). Machining and powered-radio acceptance remain pending those checks.

# Accepted physical maps for completed schematic

This supersedes the module/trimmer omissions in the first checkpoint. All library and schematic writes used Konnect. Module nominal geometry was explicitly approved by the user: 2.54 mm pitch and 15.24 mm row spacing, preferred over approximate physical measurements. The actual clone/socket/cable envelope remains a placement allowance, not a new pin-map blocker.

## U1 Teyleten Robot USB-C Pro Micro, 5 V / 16 MHz

Source: exact seller listing [B0B6HYLC44](https://www.amazon.com/dp/B0B6HYLC44), seller photos PT01/PT02 and actual user module photo; [source notes](../reference/teyleten-source-notes.md). No manufacturer dimensioned datasheet/revision exists in the provided evidence. User approved the nominal [Biacco42 footprint](promicro-library.md), commit 96404fc297aa4b3009f8e2e2b69e1c1abed35538. The incorrect seller ATmega328P circuit was rejected.

The **24-row lead/function/pad/X/Y table in [promicro-library.md](promicro-library.md)** is the acceptance table. Every row is component/top view: USB toward negative X, contacts 1–12 progress +X on +Y row, 13–24 return −X on −Y row. Physical lead = symbol pin = footprint pad number in every row. All grounds are three separate physical contacts (3,4,23); no duplicate pad numbers, no hidden shield/contact, no mechanical-only pad. Counts: 24 physical contacts, 24 symbol pins, 24 electrical pads.

Symbol: `CTCSS:Teyleten_ProMicro_5V`. Names follow the table's Arduino logical names. Pin types: 3/4/23 GND power_in; 24 RAW power_in; 21 regulated VCC power_out; 22 RST input; remaining 18 I/O bidirectional. This models the accepted radio-to-RAW powering use; it does not prove onboard USB/regulator behavior. Source symbol's reversed RAW/VCC power types were not copied.

Final footprint `CTCSS_THT:ProMicro_CNC_BCu` is a CNC derivative of `Biacco42_ProMicro:ProMicro`: same 24 centers/numbering, same square pad 1 and USB outline; pads increased from 1.6 to 2.0 mm, drills retained at 1.1 mm, copper only B.Cu. Annular ring 0.45 mm; adjacent circle pad gap 0.54 mm. Two female socket strips mount on top; solder joints are on bottom.

Acceptance: symbol queried back (all 24 names/numbers/types), source and CNC footprint queried back (all pads, sizes/drills/layers), disposable symbols and footprints placed in `.agent-scratch/implementation/evidence/scratch/`. Rendered schematic and top-view board detail were inspected: 12 contacts per row, square pad 1 at USB end of +Y row, numbering direction consistent with table, USB projection −X. Scratch schematic instances read back using Konnect. Konnect's saved-file `get_component_pads` fails to find the modern property-format U1 despite the saved render showing it; therefore independent **Konnect IPC-2581 export** `pinmap-board.xml` and `cnc-pinmap-board.xml` establishes actual Component U1/U2, package 24 pins and pad locations. The accepted map above retains the conclusion; temporary exports and raw readbacks are no longer maintained. This is a documented tool-reader limitation, not a missing placement. Geometry and electrical map accepted under user nominal approval; socket insertion/cable clearance remains assembly/bench verification.

## RV1 Bourns 3296W-1-103LF

Primary source [Bourns 3296 datasheet](https://www.bourns.com/docs/product-datasheets/3296.pdf), consulted 20 October 2026, page 1 product-dimensions 3296W and electrical diagram. No explicit document revision printed on page 1; source retrieval date identifies this copy. Alternate official URL resolved the earlier 403. Symbol `Device:R_Potentiometer`, final footprint `CTCSS_THT:RV_3296W_CNC` derived from KiCad's Bourns 3296W vertical footprint.

| Physical lead | Function | Symbol pin/name/type | Pad | Local X/Y mm | View/direction | Source |
|---|---|---|---|---|---|---|
| 1 | CCW end | 1 / 1 / passive | 1 | 0 / 0 | Component top view, adjuster toward +X/+Y corner, rightmost lead | p1 3296W terminal/end view and CW diagram |
| 2 | Wiper | 2 / 2 / passive | 2 | -2.54 / 0 | Same top view, middle lead | same |
| 3 | CW end | 3 / 3 / passive | 3 | -5.08 / 0 | Same top view, leftmost lead | same |

The datasheet terminal-end drawing shows 3,2,1 downward; translating to component top view and rotating gives 3 left, 2 middle, 1 right, with screw near lead 1. Symbol numbering and footprint local pad coordinates queried back. Three physical leads, three symbol pins, three electrical pads; zero duplicates/mechanical pads. Pads 2.0 mm, drills 0.9 mm, B.Cu/B.Mask; 0.55 mm annular ring and 0.54 mm minimum adjacent pad gap. Disposable source RV1 and CNC RV2 board render plus schematic inspected; IPC-2581 instance readback confirms pads. Accepted. Connect 3 to DIVIDER, 1 to GND, 2 to coupling capacitor so clockwise increases tone; start fully CCW.

## Q1 onsemi 2N3904RLRAG (factory formed leads)

This replaces straight-lead 2N3904G solely to provide generous CNC pad spacing. Primary source [onsemi 2N3903/D](https://www.onsemi.com/download/data-sheet/pdf/2n3903-d.pdf), August 2021 Rev.9, page 3 exact 2N3904RLRAG tape/reel ordering; page 1 bent-lead perspective; PDF pages 7–8 CASE29-11 issueAM drawing/style1. Use the linked manufacturer source; downloaded copies and page renders are no longer maintained.

| Physical lead | Function | Symbol pin/name/type | Pad | Local X/Y mm | View/direction | Evidence |
|---|---|---|---|---|---|---|
| 1 | Emitter | 1 / E / passive | 1 | 0 / 0 | Component top view, flat face +Y, leftmost | p1 bent-lead perspective, p7 bent-lead geometry, p8 style1 |
| 2 | Base | 2 / B / input | 2 | 2.54 / 0 | Same top view, middle | same |
| 3 | Collector | 3 / C / passive | 3 | 5.08 / 0 | Same top view, rightmost | same |

Symbol `Transistor_BJT:2N3904`; footprint `CTCSS_THT:Q_TO92_Formed_CNC`, derived from `Package_TO_SOT_THT:TO-92_Inline_Wide`. Datasheet bent-lead pitch G=2.40–2.80 mm encompasses 2.54 mm nominal. Three physical leads/symbol pins/pads; zero duplicate or mechanical pads. Exact source suffix is important: do not buy straight-lead bulk 2N3904G for this footprint without a separately reviewed lead-forming process. CNC pads 2.0 mm/drills 0.9 mm, 0.55 mm annular ring, 0.54 mm adjacent pad gap; pad1 square. Source symbol, wide source footprint and final CNC variant queried back. Disposable Q2 board placement/export/render and IPC-2581 readback inspected: square leftmost E pad, B middle, C right, flat edge down in top view. Accepted. The superseded narrow package is described in [the historical pin-map notes](transistor-pin-map.md).

The electrical 5 mA sink design target is provisional; measure actual radio PTT voltage/current and verify saturation/default release. Physical map acceptance does not establish radio electrical compatibility.

## C3 and C6 unpolarized film capacitors

Primary source [WIMA main catalogue 2026](https://www.wima.de/wp-content/uploads/media/WIMA_Main_Catalogue_2026.pdf), edition 03.26, pages 34–35. C3 `MKS2C041001F00KSSD`, 1uF/63V, 10%, bulk, 6−2mm leads: body7.2×5×10mm, pitch5mm, wire0.5mm. C6 `MKS2C044701O00KSSD`, 4.7uF/63V: body7.2×11×18mm, pitch5mm. The 4.7uF film bulk selection replaces the tentative 10uF part; no specification fixes bulk capacitance. Both are symmetric two-lead unpolarized parts: symbol `Device:C` pin1/passive maps pad1 at0/0, pin2/passive maps pad2 at5/0; either physical lead can be1. Two leads/pins/pads, zero duplicate/mechanical features. Final CNC footprints use2mm pads/.9mm drills; source stock outlines and5mm centers retained. No polarity reversal ambiguity exists. Loaded response and regulator transient performance still require bench checks.

# Enclosure requirements

Baseline: prototype P1, 2026-10-22. Use the dimensions and construction below for enclosure development. Maintain parameter decisions and prototype findings in the [enclosure decision register](enclosure-decision-register.md); keep unresolved-value tracking exclusively in that register.

## Purpose and operating context

House the Icom IC-229H selectable CTCSS interface board and bring its user controls, indications, microphone input and radio connection to the outside. Protect the electronics, support everyday operation and cable handling, and allow straightforward assembly, programming, calibration and repair by a beginner.

The unit adds selectable CTCSS to the microphone audio path and forwards microphone PTT through the MCU. The encoder and LCD select tones; 151.4 Hz is the initial fallback, not a fixed tone. Bypass disables tone while retaining firmware PTT forwarding. The unit remains powered with the radio: there is no OFF switch, OFFSET control or mechanical/unpowered PTT bypass.

Electrical and UI authority: [board specification](board-specification.md), [accepted firmware baseline](firmware-specification.md), [assembly instructions](../implementation/assembly-and-bring-up.md), and [component sourcing review](../implementation/component-sourcing-review.md). This specification does not authorize changes to those interfaces or the PCB.

## Design approach

**Maintain a bias toward printing what we can and only fall back to purchased materials with clear justification.** This is an established user-provided design principle.

Evaluate integrated printed features first, then separate printed parts, before adding purchased mechanical items. For each purchased mechanical BOM item, record the specific functional reason a printed solution is unsuitable or materially worse, such as required grip/compliance, wear resistance, precision, temperature performance or repeated fastening. Convenience or carryover from an earlier BOM is not sufficient justification.

Apply this principle within the existing requirements for strength, electrical insulation, clearance, printability, assembly and service. Include required printed parts and representative fit tests in the shared multi-plate 3MF workflow. Record item-specific print-versus-buy decisions and their evidence in the decision register.

## Established inputs

| Item | Requirement / current project input |
| --- | --- |
| Carrier PCB | 100 × 150 mm rectangular board, 1.5 mm substrate; top-mounted THT parts and bottom copper/solder joints |
| Board mounting | Four 4 mm NPTH holes, centers 6 mm from adjacent edges; hole spacing 88 × 138 mm |
| MCU | Socketed Teyleten USB-C Pro Micro, 5 V / 16 MHz; preserve module removal and connected USB cable clearance |
| Display | 1602, 16 columns × 2 rows, I²C; current selected purchase is DFRobot DFR0063 with backpack |
| Selection control | Already-owned WWZMDiB EC11 encoder with push switch and knob; support rotation, short presses and 750 ms long presses |
| Bypass | One maintained toggle; current selected part is E-Switch 100SP1T1B1M1REH, wired closed-to-ground for bypass |
| Indicators | Two **5 mm LEDs**, confirmed by the user: PTT and bypass. Current selections are red Kingbright WP7113ID and green WP7113GD |
| External radio interfaces | Two already-owned **standard GX16-8 bulkhead adapters**, confirmed by the user: microphone-side and radio-side |
| Power | Radio nominal 8 V through the existing microphone/radio wiring; no separate power inlet or power switch is required |
| Fabrication | Default FDM/FFF. Every individual printed part must fit the established **256 × 256 × 256 mm** build volume in its intended print orientation, including space for brim/supports and excluded bed areas |

The [PCB implementation record](../implementation/pcb-layout.md) gives the KiCad outline as X=50–150, Y=50–200 mm. Its four enclosure-mount centers are (56,56), (144,56), (144,194), (56,194) mm. In a board-local frame with the same axes and origin at (50,50), these become (6,6), (94,6), (94,144), (6,144) mm. A CAD rotation must transform the board and holes together; the panel CAM frame is not the assembly coordinate frame. The separate H5–H8 jig holes are not enclosure mounts; preserve the existing support interface.

## Functional and mechanical requirements

| ID | Requirement |
| --- | --- |
| ENC-01 | Fully retain the board and all external elements. Prevent fingers, loose hardware and cable movement from reaching exposed conductors during normal closed-case use. |
| ENC-02 | Mount the PCB using all four existing holes, without bending it, relocating holes or changing electrical clearances. Keep bosses, washers and fasteners clear of copper, solder joints and component bodies. |
| ENC-03 | Provide positive clearance below every solder joint and trimmed lead, including tolerances and board deflection. Support the PCB at mounting holes; do not rest its bottom copper on the case floor. |
| ENC-04 | Account for the complete populated height: sockets, module, USB shell, capacitors, vertical headers, mating housings, wires and bends. C6 alone has a documented maximum body height of 12.5 mm above the board; it is not the complete assembly-height limit. |
| ENC-05 | Present the full LCD character area through a readable opening, retain the display independently of its wiring, and protect its glass, backpack and solder connections. Avoid bezel interference with first/last characters and viewing angle. |
| ENC-06 | Secure the encoder against rotation and axial movement. Provide knob/finger clearance for rotation and deliberate pressing, including a sustained press, without contacting adjacent controls or flexing the panel noticeably. |
| ENC-07 | Secure the bypass switch, make both positions identifiable, and keep its travel clear of the case, knob and cables. Label positions according to the actual installed contact orientation. |
| ENC-08 | Mount and retain both 5 mm LEDs with insulated leads and visible labels. Use 5.2 mm lens bores with internal flange capture and a screw-retained keeper; insulate the leads. |
| ENC-09 | Provide two GX16-8 bulkhead mounting positions. Accommodate body, flange/nut/washer, anti-rotation features where present, rear terminations, insulation, mating connector shells and coupling-ring/tool access. Prevent mating torque from twisting wiring or loosening the bulkhead. |
| ENC-10 | Label the two external connections clearly as MIC and RADIO. Preserve adapter identity, key orientation and pin numbering through assembly. The GX16-8 identity is established; conductor mapping and shielding follow the existing electrical acceptance procedure. |
| ENC-11 | Transfer connector insertion, withdrawal, mating torque and cable pulls into the enclosure structure rather than the PCB headers or solder joints. Strain-relieve internal harnesses and keep them out of closure seams and screw paths. |
| ENC-12 | Preserve all eight required adapter connections and microphone shielding. Route sensitive audio wiring away from PWM, LCD and switching harnesses as practical; avoid adding unnecessary audio cable length. Do not introduce an undocumented shield/chassis connection. |
| ENC-13 | Keep the enclosure walls closed around USB. Flash the MCU before assembly; service programming uses lid removal and internal USB access or removal of the socketed Pro Micro. |
| ENC-14 | Preserve the current power-handling procedure: disconnect radio/RAW power before USB connection, and USB before applying radio/RAW power, until module power-path acceptance permits otherwise. Disconnect radio power before service programming. |
| ENC-15 | Permit RV1 tone-level adjustment with the assembly retained and the necessary radio/test connections attached. Lid removal is acceptable for this service operation; a permanent external calibration hole is not required. Keep tool access clear and avoid accidental contact with nearby conductors. |
| ENC-16 | Allow opening, inspection, header disconnection, module extraction and board removal with ordinary tools. Keep the removable cover independent of the UI; provide a defined header-disconnect sequence and enough harness slack for fascia removal. |
| ENC-17 | Retain replaceable parts with accessible mechanical fasteners. Provide reusable enclosure joints suitable for repeated service; do not default to glue, brittle clips or thin printed load-bearing threads. Insulate unused toggle terminals and exposed LED/connector terminations. |
| ENC-18 | Use legible, durable panel identification. Label the indicators PTT and BYPASS; PTT means commanded radio PTT, not confirmed RF transmission. No separate power indicator is required. |
| ENC-19 | Provide stable support during encoder rotation, pressing and cable handling. Use four 12 mm-diameter, 3 mm-high nonslip feet, positioned near the base corners. |
| ENC-20 | Evaluate regulator and LCD-backlight heating in the closed enclosure at full intended load. Add ventilation only as needed from the thermal evaluation and intended environment; a printed plastic case does not establish RF shielding or environmental sealing. |

## P1 construction baseline

The IC-229H companion uses a dark, low rectangular case, a rounded front fascia, recessed contrasting display surround, a large ribbed left knob with a thin accent band, aligned small status legends and a front microphone connection. Keep the top plain and the radio lead at the rear. These are geometry and separate printed parts; contrasting filament is optional.

- Use a 200 × 195 × 68 mm body, excluding feet, knob and plugs. Walls, floor and top cover are 3 mm; the front fascia is 4 mm with local mounting lands. Use rounded 4 mm outer corners and hidden underside/rear attachment screws.
- Place the unchanged PCB at X25–175, Y55–155, underside Z9.35. Map board-local coordinates as X=175−board Y, Y=55+board X. Its holes are (31,61), (169,61), (31,149), (169,149). Integrate 6.35 mm insulating supports into the floor; use M3 captive nuts, M3 × 8 screws and printed 7.8 OD × 3.4 ID × 1 mm washers. Keep trimmed underside leads within 2 mm, leaving 4.35 mm to the floor.
- Allocate 25 mm above the board's Z10.85 component surface. Keep RV1's 10 mm vertical tool corridor and 15 mm module extraction allowance accessible with the cover removed. Keep all external walls closed around USB.
- Put the LCD window at X56–128, Z26.5–51.5 on the front. The surround face is recessed 1.2 mm behind the fascia. Allocate X51–133, Y5.2–30.2, Z20–58 for the LCD/backpack; its 75 × 31 hole rectangle has centers X54.5/129.5, Z23.5/54.5. Four printed posts support the LCD at Y10.2, with M2.5 × 6 screws and captive nuts. Two M3 × 12 screws retain the surround from inside; growing ramps support their ears in the front-face-down orientation.
- Put the encoder at front (X24,Z36), with a 7.2 bore and 1.5 mm bushing land. Allocate a 20 × 25 × 20 rear body; printed side guides provide 0.3 mm lateral clearance. Use a printed 30 mm nominal ribbed knob, 6.2 shaft socket, split collar and tangential M3 × 16 clamp bolt. A separate 1.6 mm C-shaped accent band seats in the rear groove with 0.15 radial and 0.2 mm axial clearance per side.
- Put the toggle at (159,39), with a 6.5 bore, 1.5 mounting land and 15 × 25 × 15 rear allocation. Identify tone-enabled as PL and bypass as BYP. Keep the wired contact orientation aligned with those legends.
- Put PTT and BYPASS LEDs at (156,56)/(181,56), using 5.2 bores and 7 mm flange seats 1.6 deep. A keyed printed bridge captures both flanges with 0.3 axial clearance and 4.5 lead passages; one M3 × 8 screw and captive nut retain it.
- Put MIC at front (181,23), RADIO at rear (40,49). Use 16.2 bores, 2 mm grip lands, 20.5 across-flat captive nut seats and 26 mm-diameter reinforcement. The upright rear bore has a printable roof and gusset. Allocate 24 diameter × 30 inward for each connector; reserve 45 outward plus 30 cable-bend allowance. From the front face the front plug/bend reaches Y−75; the rear reaches Y270.
- Fasten the fascia from below with two M3 × 8 screws. Fasten the cover with two M3 × 8 underside screws and two M3 × 10 rear screws. All use captive M3 nuts. Use 5.7 across-flat × 2.6-deep M3 seats and 3.4 bores; rear cover seats are open-front. The cover's segmented 2 mm locating rails have 0.3 mm lateral clearance per side.
- Use 200 mm UI harnesses, 260 mm microphone harness and 200 mm radio harness. Include 75 mm service loops where a panel disconnects. Two reusable printed harness bridges at X70/145,Y42 replace cable ties; each uses two M3 × 8 screws and captive nuts. Keep audio/shield wiring together, 15 mm bend radii and 5 mm clearance from seams and screw paths.
- Use four compliant 12 diameter × 3 mm feet at XY(15,24), (185,24), (15,180), (185,180), clear of the underside fasteners. Keep the case unvented, using PETG for indoor desktop operation at 10–35 °C.
- Use 3.8 mm stencil PTT/BYPASS and PL/BYP legends, 4.5 mm CTCSS and 3.5 mm recessed MIC/RADIO. Through-cut stencil contours keep counters attached to the surround. The surround and knob band are separate printable color accents.

## Print and CAD requirements

1. Maintain editable, parameterized FreeCAD source in `mechanical/enclosure/icom-ctcss-enclosure.FCStd`, in millimeters, with meaningful part/feature names. Preserve assembly coordinates and document the FreeCAD version and dependencies.
2. Parameterize PCB clearances, standoff height, wall/panel thickness, connector and control cutouts, hardware pockets and fit allowances. Identify whether each fit allowance is per-side/radial or total/diametral.
3. Use PETG for the indoor desktop operating envelope above. Evaluate sustained screw preload, connector loads, impact and closed-case temperature during prototype testing.
4. Use a 0.4 mm nozzle, 0.45 mm extrusion width, 0.2 mm layers, five perimeters, six top/bottom layers and 20% gyroid infill. Use 3 mm walls, floor and lid; locally reinforce cable mounts and bosses. Slice with the printer’s PETG profile and these geometry settings.
5. Print the base floor-down and the cover exterior-face-down, with its internal supports facing upward; print the fascia, display surround and knob front-face-down. Use recessed lettering on the bed face instead of raised relief. Give removable retainers a broad flat bed face. Arrange extrusion paths and structural ribs/fillets to carry connector torque, cable pulls, encoder presses and screw loads while limiting layer-peeling forces. Use downward chamfers where useful and avoid abrupt stressed roots.
6. Prefer support-free geometry; roughly 45° from vertical is an initial overhang heuristic, not a verified printer limit. Address horizontal-hole roofs, bridges and isolated islands. Any required supports must be removable without damaging critical fits.
7. Provide stable bed faces and account for warping and first-layer expansion at mating edges. Check each oriented bounding box against 256 mm limits with process margins; split oversized parts into alignable, mechanically suitable pieces if necessary.
8. Export separate closed, manifold print meshes already oriented with their bed faces at Z=0 and no negative-Z geometry. Keep the primary 3MF build and README at the root of `manufacturing/enclosure/`, with individual meshes under `supporting/stl/` and STEP interchange under `supporting/step/`; keep rationale and acceptance evidence in `docs/`. Provide one multi-plate 3MF project containing fascia/fit pieces, base/retainers, and cover in that order, sharing global filament/process settings.
9. Print representative coupons for critical holes, LED retention, panel hardware and enclosure joints before a full case. Inspect a slice with the intended printer/material profile for bed fit, thin features, unsupported regions, continuous walls/skins, supports and time/material estimates.

## Component procurement

Any additional required purchased enclosure parts must meet the project's Amazon/Mouser/DigiKey sourcing requirement and have their mechanical dimensions incorporated in the CAD and mechanical BOM.

## Acceptance and deliverables

Before design release, deliver a dimensioned assembly/layout view, parameterized CAD, individual print-oriented meshes, mechanical BOM, panel labels, print instructions and assembly/service sequence. Record the complete installed envelope, hardware/tool access and harness routing, including a safe lid-opening path.

Keep acceptance tied to the exact revision:

- **CAD:** check board/hole alignment, underside and component clearance, control travel, display visibility, both mated GX16-8 plugs, internal USB service access, wiring bends, fastener access and removal paths. Check all oriented part dimensions and mesh integrity.
- **Slicer:** inspect the intended profile for support and toolpath continuity, bed fit and process margins. Record orientation, bed face, material/profile, estimated time and material.
- **Prototype:** check actual board fit and retention, connector torque/cable handling, control feel, LED retention, lid closure without pinching and repeated service access. Test full-load heating and radio/audio operation with the enclosure closed.

Record revision-specific CAD, slicer and physical acceptance results in the decision register. Historical electronics checks do not establish enclosure fit or closed-case performance.

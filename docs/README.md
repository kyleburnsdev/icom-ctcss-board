# Icom IC-229H selectable CTCSS/PL interface

**Carrier-board sourcing revision complete (2026-10-22):** obsolete Q1/C3 selections and the unavailable C6 selection have been replaced, with exact supplier-linked parts for all 38 BOM instances. See the [purchasing list and remaining product acceptance](implementation/component-sourcing-review.md). Radio/microphone adapters are already owned; physical manufacturing/radio acceptance and firmware remain open; this is a buildable carrier-board design, not a released product.

**Control cleanup complete:** J5 is a two-pin bypass connector. The obsolete OFF/A0 switch circuit and R16 have been removed; A0 is intentionally unused. The board stays powered with the radio. The BOM and manufacturing files reflect this revision.

This project adds a firmware-generated, user-selectable CTCSS/PL tone to the microphone audio path of an Icom IC-229H. Microphone audio passes through the board, while the Pro Micro reads microphone PTT and drives the radio's PTT through an NPN transistor. An off-board encoder, LCD, one bypass switch and two LEDs provide the user interface. **151.4 Hz is one required supported tone, not a fixed operating frequency.**

The carrier board is 100 × 150 mm, with top-mounted through-hole components and a socketed 5 V / 16 MHz USB-C Pro Micro. It uses bottom copper only, with no routing vias, wire jumpers or copper pours. Manufacturing targets the Makera Carvera Air with PCB kit and laser accessory on 1.5 mm single-sided copper-clad stock. The top legend is laser-marked dark onto fully UV-cured white solder mask and qualified on the first full board after IPA cleaning.

The schematic and routed PCB prototype are complete. **Firmware and physical manufacturing/radio acceptance remain outstanding.** The jig/CAM migration, including enforced keepouts and 1.5 mm native thickness, is verified. Recorded hardware checks report zero ERC errors/warnings, zero DRC errors or unrouted connections, and 61 passing connectivity assertions. The [design review](implementation/design-review.md) documents the remaining warnings and bench checks.

## Components for one board

This grouped list totals **38 schematic component instances**, matching the [reference-by-reference BOM](reference/bom.csv). Connector and test-point rows are grouped by physical part even though their signal labels differ. Quantities do not include spares or the additional items in the next section.

| Component | Quantity | Board references | Required part / fit |
| --- | ---: | --- | --- |
| 330 Ω resistor | 2 | R6, R7 | Axial DIN0204 body, 3.6 × 1.6 mm; 5.08 mm lead pitch |
| 1 kΩ resistor | 2 | R4, R8 | Same axial body and pitch |
| 3.3 kΩ resistor | 2 | R1, R2 | Same axial body and pitch |
| 4.7 kΩ resistor | 1 | R10 | Same axial body and pitch |
| 10 kΩ resistor | 6 | R3, R9, R12–R15 | Same axial body and pitch |
| 100 kΩ resistor | 2 | R5, R11 | Same axial body and pitch |
| 100 nF nonpolar capacitor | 4 | C1, C2, C4, C5 | Vishay **K104K15X7RF5TL2**, 50 V; 2.5 mm pitch; maximum 4 × 2.6 mm body |
| 1 µF / 63 V nonpolar film capacitor | 1 | C3 | KEMET **R82DC4100AA60J**; 5 mm pitch; maximum 7.5 × 5.1 × 10.1 mm body |
| 4.7 µF / 63 V nonpolar film capacitor | 1 | C6 | TDK **B32522C0475J000**; 15 mm pitch; maximum 18 × 7 × 12.5 mm body |
| 10 kΩ trimmer | 1 | RV1 | Bourns **3296W-1-103LF**; top adjustment |
| NPN transistor, factory-formed leads | 1 | Q1 | onsemi **2N3904TAR**, 2.54 mm formed-lead pitch; do not substitute the straight-lead suffix without footprint review |
| Vertical 1×8 male header | 2 | J1, J2 | 2.54 mm pitch; microphone/radio cable adapters |
| Vertical 1×5 male header | 1 | J3 | 2.54 mm pitch; encoder |
| Vertical 1×4 male header | 2 | J4, J6 | 2.54 mm pitch; LCD and LEDs |
| Vertical 1×2 male header | 1 | J5 | 2.54 mm pitch; bypass switch |
| Through-hole test connection | 8 | TP1–TP8 | Fit the 1.1 mm holes and 3 mm lands; use solderable pins/wire loops within the reviewed envelope |
| USB-C Pro Micro module | 1 | U1 | Teyleten Robot ATmega32U4, **5 V / 16 MHz**; nominal 2.54 mm pitch and 15.24 mm between socket rows |

There are **15 fixed resistors and 6 capacitors** in the table. The compact resistor/capacitor body sizes are intentional: check actual purchased parts against the [footprint details](implementation/footprint-review.md), not just their electrical values. Exact manufacturer numbers, quantities and purchase links are in the [BOM](reference/bom.csv); accessory selections are in the [sourcing review](implementation/component-sourcing-review.md).

## Additional parts needed to complete the project

These are outside the 38-instance schematic BOM. Socket, UI and harness selections are listed in the [sourcing review](implementation/component-sourcing-review.md). Radio adapters are already owned; the [P1 enclosure package](../manufacturing/enclosure/README.md) supplies the case and mechanical assembly.

| Item | Quantity | Notes |
| --- | ---: | --- |
| 1×12 female socket strip | 2 | 2.54 mm pitch for U1; body no wider than the assumed 3 mm; pins must fit 1.1 mm holes |
| 1×12 male module header strip | 2, if needed | Only if the Pro Micro does not already have compatible soldered pins |
| 5 V I²C LCD with backpack | 1 | Confirm its connector order, SDA/SCL pull-ups and actual backlight current |
| Quadrature encoder with push switch | 1 | Connect CLK, DT, SW, +5V and GND according to J3; verify the actual device interface |
| On/off toggle switch | 1 | Bypass only; OFF/OFFSET has been removed from the intended controls |
| Bare indicator LED | 2 | PTT and bypass; board-mounted 330 Ω resistors are already included |
| Microphone/radio cable adapter | 2 | Already owned: one microphone-side and one radio-side adapter; verify mating, shielding and pin mapping |
| Cable wire and mating contacts/housings | 1 set | For J1–J6: two 8-position, one 5-position, two 4-position and one 2-position board interfaces. J5/J6 each carry two independent two-wire pairs; no return-wire splice is needed |
| Insulating standoff/fastener set | 4 | For 4 mm mounting holes; check washer clearance and enclosure fit |
| Enclosure / panel | 1, as required | Allow for the module USB cable, 12.5 mm-high C6, UI controls, headers and wiring |
| 1.5 mm single-sided copper-clad blank | 1 | Finished board is 150 × 100 mm; allow stock/fixture margins if the chosen CAM setup needs them |
| Sacrificial coupon material | At least 1 piece | Prove milling, drill fit and registration; qualify legend marking on the first full circuit board |

The module mounts in the two socket strips; do not solder it permanently to the carrier board. All selected carrier-board capacitors are nonpolarized.

## Equipment, consumables and unfinished work

For fabrication, use the Carvera Air/PCB kit, the available 30°/0.2 mm-tip or 60°/0.1 mm-tip V-bit, suitable **0.9 mm, 1.1 mm and 4 mm** drilling capability, and the registration/hold-down setup. Exact copper thickness, isolation depth, feeds and tool capability still need a coupon check. For the top legend, have white UV solder mask, a flood-curing UV source, the laser accessory and IPA for cleaning. Fully UV-cure the white coating before laser marking; evaluate retention and coating integrity after cleaning the first full board.

Assembly and bring-up require soldering tools and consumables, a multimeter, a current-limited bench supply and a suitable USB cable. Tone/noise and radio-deviation acceptance require appropriate measurement equipment and test firmware. Verify the actual radio cable pinout, microphone-port current capacity, module regulator heating, PTT voltage/current and tone injection level before normal radio operation.

Firmware still needs to implement the selectable tone table, waveform/PWM generation, encoder/LCD UI, PTT forwarding, bypass, LEDs and input handling. There is no offset or separate OFF function. Bypass is firmware-controlled tone disabling with PTT forwarding; it is not a mechanical pass-through when the MCU is unpowered. Until the module's power isolation is verified, disconnect RAW/radio power before connecting USB and disconnect USB before applying RAW power.

## Where to go next

| Task | Instructions / artifact |
| --- | --- |
| Understand requirements and scope | [Board specification](requirements/board-specification.md) |
| Plan the enclosure and external interfaces | [Enclosure requirements](requirements/enclosure-specification.md) |
| Iterate on firmware behavior | [Firmware requirements baseline](requirements/firmware-specification.md); PCB pin assignments and electrical behavior are fixed constraints |
| Inspect the circuit | [Schematic PDF](reference/schematic-complete.pdf) and [circuit notes](implementation/schematic-complete.md) |
| Open the editable design | [KiCad project](../electronics/icom-ctcss-board.kicad_pro) |
| Match parts to references and packages | [Detailed BOM CSV](reference/bom.csv), [footprint review](implementation/footprint-review.md), [physical pin maps](implementation/physical-pin-maps.md) |
| Find parts on the board | [Top assembly drawing](reference/assembly-top.svg) |
| Prepare Carvera manufacturing jobs | [Manufacturing overview](../manufacturing/pcb/carvera-air/README.md) |
| Implement jig registration and FreeCAD CAM | [Migration plan and Robust MCP Server job contract](implementation/pcb-jig-and-freecad-cam.md) |
| Assemble and connect the UI | [Assembly and bring-up](implementation/assembly-and-bring-up.md), including the [J5/J6 wiring table](implementation/assembly-and-bring-up.md#j5j6-cable-wiring) |
| Review remaining acceptance work | [Acceptance checklist](implementation/acceptance-checklist.md) and [independent design review](implementation/design-review.md) |
| Understand tone-frequency response | [Tone-chain model and limitations](implementation/tone-response.md) |
| Review electrical simulation before the prototype | [LTspice validation and service-manual PTT analysis](implementation/ltspice-validation.md) |
| Browse implementation notes and verification | [Implementation index](implementation/README.md) |

Use the **current two-pin J5 / four-pin J6 files** together. Older three-pin header layouts and intermediate routing/checkpoint artifacts are isolated in ignored `.agent-scratch/` and are not the current manufacturing set. The supplied manufacturing files are geometry for CAM review, not approved CNC/laser G-code.

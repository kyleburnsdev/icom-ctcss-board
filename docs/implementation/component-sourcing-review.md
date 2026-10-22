# Component sourcing and purchasing review

Reviewed 2026-10-22. **Carrier-board component sourcing is closed:** every one of the 38 schematic instances has an exact manufacturer/part number and approved-source purchase link in the [BOM](../reference/bom.csv). The replacements are incorporated into the schematic, libraries, routed PCB, assembly drawings and manufacturing exports. The user confirmed that the radio/microphone adapters are already owned; no adapter purchase is required for this build. **Whole-product release remains incomplete:** mechanical integration, physical acceptance and firmware remain open.

The [procurement requirement](../requirements/board-specification.md#component-procurement-requirement) applies to every required purchase. Availability is a dated observation, not reserved inventory; recheck cart quantity and shipping at purchase. No orders were placed. DigiKey selections below were listed active, in stock and available in quantity one; use cut tape where offered. U1 is the existing user-owned module and its Amazon listing has an enabled main ordering/cart control; destination-specific checkout inventory was not established.

## Incorporated replacements

| Part | Previous selection | Incorporated selection and fit |
| --- | --- | --- |
| Q1 | Obsolete onsemi 2N3904RLRAG | onsemi **2N3904TAR**, same E1/B2/C3, factory-formed 2.54mm leads; existing 0.9mm drills and body envelope retained. |
| C3 | Obsolete WIMA MKS2C041001F00KSSD | KEMET **R82DC4100AA60J**, nonpolar 1uF/63V/5%, same 5mm pitch; body artwork enlarged to maximum 7.5×5.1×10.1mm. |
| C6 | Unverified purchasing source for WIMA MKS2C044701O00KSSD | TDK **B32522C0475J000**, nonpolar 4.7uF/63V/5%; new 15mm-pitch footprint, 1.1mm drills and 18×7×12.5mm maximum body. C6/TP3 routing and placement updated. |
| C1/C2/C4/C5 | Unspecified 100nF in an unrealistically small generic envelope | Vishay **K104K15X7RF5TL2**, 100nF/50V X7R/10%, 2.5mm pitch; artwork updated to maximum 4×2.6mm body. C4/C5 repositioned. |

Primary geometry evidence: [onsemi 2N3904/D](https://www.onsemi.com/pdf/datasheet/2n3904-d.pdf), Rev.3 October 2024, CASE135AR drawing PDF p8; [KEMET exact-part specification](https://search.kemet.com/component-documentation/download/specsheet/R82DC4100AA60J); [TDK exact-part production specification](https://product.tdk.com/en/search/capacitor/film/rfi_general/info?part_no=B32522C0475J000); [Vishay K series](https://www.vishay.com/docs/45171/kseries.pdf), Rev.05Sep2025. Capacitor electrical values and nonpolar construction are preserved. C3 tolerance improves from 10% to 5%; filter capacitors remain X7R and require loaded tone calibration.

All resistors are selected Vishay MRS16, 1%, 0.4W, maximum 3.6×1.6mm body; form their axial leads with a tool to the 5.08mm footprint. The [manufacturer drawing](https://www.vishay.com/docs/28724/mrs16m25.pdf), document28724, p3, permits minimum 5mm mounting pitch. Headers/test posts use the Würth 6130xx11121 series, 0.64mm square pins and manufacturer-recommended 1.10mm holes; [8-position drawing](https://www.we-online.com/components/products/datasheet/61300811121.pdf). Verify actual insertion on the coupon. RV1 remains the [Bourns 3296W](https://www.bourns.com/docs/product-datasheets/3296.pdf). See [physical pin maps](physical-pin-maps.md) for exact lead-to-pad checks.

## Carrier-board order list

Quantities are for one populated board, without spares. U1's Amazon package contains multiple modules; only one is used. Each link is the exact selected purchase page; the BOM also records supplier SKU and assembly notes.

| References | Quantity | Manufacturer / MPN | Purchase |
| --- | ---: | --- | --- |
| C1, C2, C4, C5 | 4 | Vishay **K104K15X7RF5TL2** | [BC1084CT-ND](https://www.digikey.com/en/products/detail/vishay-beyschlag-draloric-bc-components/K104K15X7RF5TL2/286538) |
| C3 | 1 | KEMET **R82DC4100AA60J** | [399-5860-ND](https://www.digikey.com/en/products/detail/kemet/R82DC4100AA60J/2571295) |
| C6 | 1 | TDK **B32522C0475J000** | [495-1131-ND](https://www.digikey.com/en/products/detail/tdk-electronics-inc/B32522C0475J000/592709) |
| J1, J2 | 2 | Wurth Elektronik **61300811121** | [732-5321-ND](https://www.digikey.com/en/products/detail/w%C3%BCrth-elektronik/61300811121/4846839) |
| J3 | 1 | Wurth Elektronik **61300511121** | [732-5319-ND](https://www.digikey.com/en/products/detail/w%C3%BCrth-elektronik/61300511121/4846831) |
| J4, J6 | 2 | Wurth Elektronik **61300411121** | [732-5317-ND](https://www.digikey.com/en/products/detail/w%C3%BCrth-elektronik/61300411121/4846827) |
| J5 | 1 | Wurth Elektronik **61300211121** | [732-5315-ND](https://www.digikey.com/en/products/detail/w%C3%BCrth-elektronik/61300211121/4846823) |
| Q1 | 1 | onsemi **2N3904TAR** | [2N3904TARCT-ND](https://www.digikey.com/en/products/detail/onsemi/2N3904TAR/4213831) |
| R1, R2 | 2 | Vishay **MRS16000C3301FCT00** | [BC3934CT-ND](https://www.digikey.com/en/products/detail/vishay-beyschlag-draloric-bc-components/MRS16000C3301FCT00/7351364) |
| R3, R9, R12, R13, R14, R15 | 6 | Vishay **MRS16000C1002FCT00** | [BC3918CT-ND](https://www.digikey.com/en/products/detail/vishay-beyschlag-draloric-bc-components/MRS16000C1002FCT00/5063734) |
| R4, R8 | 2 | Vishay **MRS16000C1001FCT00** | [BC3915CT-ND](https://www.digikey.com/en/products/detail/vishay-beyschlag-draloric-bc-components/MRS16000C1001FCT00/5063732) |
| R5, R11 | 2 | Vishay **MRS16000C1003FCT00** | [BC3921CT-ND](https://www.digikey.com/en/products/detail/vishay-beyschlag-draloric-bc-components/MRS16000C1003FCT00/7351351) |
| R6, R7 | 2 | Vishay **MRS16000C3300FCT00** | [BC3933CT-ND](https://www.digikey.com/en/products/detail/vishay-beyschlag-draloric-bc-components/MRS16000C3300FCT00/7351363) |
| R10 | 1 | Vishay **MRS16000C4701FCT00** | [BC3940CT-ND](https://www.digikey.com/en/products/detail/vishay-beyschlag-draloric-bc-components/MRS16000C4701FCT00/5063896) |
| RV1 | 1 | Bourns **3296W-1-103LF** | [3296W-103LF-ND](https://www.digikey.com/en/products/detail/bourns-inc/3296W-1-103LF/1088045) |
| TP1, TP2, TP3, TP4, TP5, TP6, TP7, TP8 | 8 | Wurth Elektronik **61300111121** | [732-5314-ND](https://www.digikey.com/en/products/detail/w%C3%BCrth-elektronik/61300111121/4846821) |
| U1 | 1 | Teyleten Robot **USB-C Pro Micro 5V 16MHz** | [B0B6HYLC44](https://www.amazon.com/dp/B0B6HYLC44) |

Observed DigiKey stock at research: Q1 582, C3 20,626, C6 9,142, 100nF 216,889, RV1 at least 37,214. Resistor stock ranged from 139 (4.7k) to 13,630 (1k); all required quantities were covered. Header/test-post stock exceeded 40,000 for each selected length. These observations establish project-quantity availability on the review date, not continuing supply guarantees.

## Additional selected purchases

These items are outside the 38-instance schematic BOM. Stock observations are from approved supplier pages on the review date. The [P0 enclosure package](../../manufacturing/enclosure/README.md) defines panel geometry, hardware and cable lengths.

| Item | Quantity | Selected purchase / interface |
| --- | ---: | --- |
| Module sockets | 2 | [Würth 61301211821](https://www.digikey.com/en/products/detail/w%C3%BCrth-elektronik/61301211821/16608531), 1×12, 2.54mm; stock6,879. [Manufacturer drawing](https://www.we-online.com/components/products/datasheet/61301211821.pdf): maximum body width2.7mm within 3mm allowance; 8.5mm body height. Dry-fit module, pins and USB plug before soldering. |
| Module male strips, if absent | 2 | [Würth 61301211121](https://www.digikey.com/en/products/detail/w%C3%BCrth-elektronik/61301211121/4846844), 1×12, stock7,198. Do not double-order if included with U1. |
| LCD/backpack | 1 | [DFRobot DFR0063](https://www.digikey.com/en/products/detail/dfrobot/DFR0063/7597121), 16×2, 5V, stock126. [Manufacturer documentation/schematic](https://wiki.dfrobot.com/dfr0063/) specifies I2C, default address0x20 and PCA8574 backpack with 10k SDA/SCL pull-ups. Wire by GND/VCC/SDA/SCL labels to J4; verify actual connector order and backlight load before powering. |
| Encoder with switch | 1 | Use the user's already-owned [WWZMDiB EC11, Amazon B0C6Q67V97](https://www.amazon.com/dp/B0C6Q67V97), subject to the contact-identification checks below. No encoder purchase required for this build. [Bourns PEC11R-4215F-S0024](https://www.digikey.com/en/products/detail/bourns-inc/PEC11R-4215F-S0024/4499665) remains the documented purchase fallback (observed stock12,293); its exact pin order, detent count and mechanical drawing must not be attributed to the generic EC11. |
| Bypass toggle | 1 | [E-Switch 100SP1T1B1M1REH](https://www.digikey.com/en/products/detail/e-switch/100SP1T1B1M1REH/378820), stock1,208, maintained SPDT gold low-level contacts. Use common and one throw across J5; insulate unused throw. Confirm continuity before connection. |
| PTT LED, red | 1 | [Kingbright WP7113ID](https://www.digikey.com/en/products/detail/kingbright/WP7113ID/1747663), stock139,924. Anode to J6 pin1; cathode to pin2. Board already includes330ohm. |
| Bypass LED, green | 1 | [Kingbright WP7113GD](https://www.digikey.com/en/products/detail/kingbright/WP7113GD/1747662), stock79,006. Anode to J6 pin3; cathode to pin4. Board already includes330ohm. |
| 8-position harness housings | 2 | [Harwin M20-1060800](https://www.digikey.com/en/products/detail/harwin-inc/M20-1060800/3728198), stock4,916, J1/J2. |
| 5-position harness housing | 1 | [Harwin M20-1060500](https://www.digikey.com/en/products/detail/harwin-inc/M20-1060500/3728194), stock873, J3. |
| 4-position harness housings | 3 | [Harwin M20-1060400](https://www.digikey.com/en/products/detail/harwin-inc/M20-1060400/3728193), stock38,857, J4/J6 and LCD far end if needed. |
| 2-position harness housing | 1 | [Harwin M20-1060200](https://www.digikey.com/en/products/detail/harwin-inc/M20-1060200/3728191), stock34,667, J5. |
| Female crimp contacts | 35 plus spares | [Harwin M20-1160042](https://www.digikey.com/en/products/detail/harwin-inc/M20-1160042/3728123), stock246,426, cut tape,22–30AWG. 31 board-side positions plus4 LCD positions; encoder +5V may be empty. [Manufacturer housing compatibility](https://www.harwin.com/products/M20-1060500). Use appropriate crimp tooling and perform pull/continuity tests. Housings are unkeyed: mark pin1 and strain-relieve. |
| Insulating standoffs | 4 | [Keystone 1902A](https://www.digikey.com/en/products/detail/keystone-electronics/1902A/61864), nylon,4-40 female/female,6.35mm high and6.35mm hex, stock65,352. Fit within the 8mm reserved mounting envelope; verify screw/head/washer retention over the 4mm board holes and enclosure attachment. |

## Already-owned EC11 encoder substitution

The user identified the existing encoders as WWZMDiB EC11 from Amazon ASIN B0C6Q67V97. The seller describes a bare five-pin rotary encoder with push button and knob; it does not provide a trustworthy exact terminal map, detent/transition specification or dimensioned manufacturer drawing. The seller's reset-to-zero wording describes possible software behavior, not an internal counting/reset function.

This is an off-board passive-contact encoder connected by a harness, so using it does not change the carrier PCB, BOM instances, drill files or CAM geometry. Accept it for this build after identifying the actual contacts with a meter, with power disconnected:

| Identified encoder contact | Carrier connection |
| --- | --- |
| Quadrature output A | J3 pin1 CLK / D4 |
| Quadrature output B | J3 pin2 DT / D5 |
| Quadrature common C | J3 pin5 GND |
| One push-switch terminal | J3 pin3 SW / D6 |
| Other push-switch terminal | J3 pin5 GND, joined to C in the harness |
| No encoder connection | J3 pin4 +5V: leave unpopulated/insulated |

Do not equate the encoder's five physical pins with the five J3 positions or wire them straight across. Identify the isolated normally-open switch pair by continuity when pressed; identify common and the two alternating contact outputs while slowly rotating. Typical three-terminal/two-terminal grouping is only a clue, not accepted pin numbering. Board R12–R14 already supply 10k pull-ups, so the bare encoder needs no +5V connection or additional pull-ups. Mechanical mounting tabs are not signal pins.

During bring-up, verify released SW is high and pressed SW is low, both rotation channels switch cleanly between high/low, clockwise increases the UI selection, and each detent gives the intended step count. Set firmware direction, transitions per detent and debounce for the actual encoder; the Bourns 24-detent specification does not establish the generic part's behavior. Confirm panel thread, shaft/knob fit and harness strain relief separately. The Amazon page currently shows no featured offer; ownership establishes availability for this build, while the Bourns fallback remains the researched purchasing option for future builds.

## Unresolved whole-product items

**Radio/microphone adapters are already owned**, confirmed by the user on 2026-10-22; the purchase-source blocker is closed for this build. Before connection, verify that both ends mate the actual radio/microphone, carry the required eight conductors, preserve microphone shielding and match the accepted pin map by continuity testing. Ownership does not establish those electrical checks. For repeat builds requiring new adapters, an approved-source compatible replacement pair still needs qualification; generic GX16/aviation descriptions do not establish mating/thread/key compatibility. Previously researched Amazon CESS B01MTSNNUB, B00H5764LA and B0125YRWKE remain rejected/unverified candidates, not purchase recommendations.

The [P0 enclosure package](../../manufacturing/enclosure/README.md) defines cable lengths and the mechanical fastener set. Enclosure fit and procurement decisions are maintained in the [enclosure register](../requirements/enclosure-decision-register.md). Fabrication tooling, copper stock and UV coatings remain the documented machine/process acceptance inputs.

## Verification of this revision

The [package-fit inspection render](../reference/sourcing-package-fit.png) shows the selected small capacitor, C3, C6 and Q1 footprints on a disposable inspection board. It is package evidence, not the final assembly layout.

Fresh [verification record](../verification/sourcing-revision.json): ERC0/0; DRC0errors/0unconnected with115 retained warnings;61 exported-netlist assertions pass; independent source IPC-2581 comparison matches all111 electrical pads. Native inventory:242 B.Cu tracks,0vias,0zones,38 parts+4mounts. Body clearance check uses selected maximum capacitor envelopes: minimum2.14mm overall, C4/C5 to module/socket allowance2.38mm, C6 to TP3 2.6926mm. Manufacturer pin/package drawings, disposable placement render/IPC readback and final assembly/copper/legend/schematic renders were inspected. Physical tolerances still require actual fit testing.

Exports now contain46 holes at0.9mm,65 at1.1mm and4 mounting holes at4mm. Landscape registration checks all353 copper objects and6,961 legend objects. **Existing Studio .mkc is older user work: reimport revised geometry and regenerate toolpaths.** No current G-code or machining acceptance is claimed. Coupon/drill/registration, load/regulator heating, PTT saturation/default release, microphone noise/deviation and firmware remain acceptance work. Earlier 2026-10-20 review-summary.json remains historical and must not validate this revision.

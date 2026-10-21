# Icom IC-229H CTCSS Tone Generator — Board Specification

## Purpose

Build an inline microphone interface for the Icom IC-229H that adds an MCU-generated, user-selectable CTCSS/PL tone to microphone audio and intercepts PTT. **151.4 Hz must be supported; it is not a fixed operating frequency.** The firmware requirements now select it as the first-use/invalid-settings fallback, while valid saved selections take precedence. Firmware selects other PL tones through the encoder/LCD UI. These are subaudible tone frequencies, not repeater RF frequencies. The PWM carrier is nominally **10 kHz** and is distinct from the selected tone frequency.

This document defines the board requirements. Remaining design decisions and validation tasks are listed under Open verification items.

**Control revision:** OFF has been removed altogether; there is no OFFSET feature. The interface stays powered with the radio, and bypass disables tone while retaining PTT forwarding. J5 is BYPASS/GND only, R16 is removed, and U1 A0 is intentionally unused. The PCB, BOM and manufacturing files reflect this cleanup. See the [firmware baseline](firmware-specification.md).

## Mechanical and fabrication requirements

- Fabrication target: **CNC isolation milling on 1.5 mm single-sided copper-clad stock**. This is the user's first board; prioritize generous isolation gaps, robust pads, accessible drilling, and forgiving assembly over compactness. Cutter geometry, available drill sizes, copper weight, and milling tolerances must be recorded before toolpath/fabrication acceptance.
- Maximum rectangular PCB size: **100 mm × 150 mm**. The initial layout target is the full permitted size.
- **Single-sided copper: bottom copper (B.Cu) only.** No top traces, inner copper, or routing vias.
- Ground uses dedicated bus tracks and branches; **no solid ground plane or copper pours**.
- All board-mounted parts are **through-hole**, including connectors, passives, adjustment trimmer, and PTT driver.
- The Arduino Pro Micro is an assembled module mounted through standard THT socket headers. Its onboard components are the exception to the THT requirement.
- Four corner mounting holes, **4 mm drill, non-plated**. Place centers 6 mm from the two adjacent edges.
- CAM setup: the **150 mm edge lies along machine X**, with 100 mm along Y. Flip about Y so left/right exchange. Use a common full-board coordinate frame for all operations and registration views containing all four mounting holes. In lower-left CNC XY, centers are (6,6), (144,6), (6,94), (144,94) mm; bottom transform is X′=150−X, Y′=Y. Keep guides separate from process artwork and identify files where the flip has already been applied.
- Components mount on the top side, with readable top silkscreen.
- Manufacturing equipment: Makera Carvera Air with PCB kit and laser accessory. Include top F.SilkS artwork for the user's two-color UV solder-mask process: flood-cure the background, selectively laser-cure the contrasting legend, then clean away uncured material. Supply top legend separately from bottom copper; actual exposure and cleaning settings require a coupon.
- Manufacturing order: complete bottom copper isolation, drilling, deburring and bare-board electrical checks before applying top solder-mask/legend coatings. Keep the supporting top substrate bare and flat during isolation milling; retain registration through the Y-axis flip and subsequent top coating/UV/laser operations.
- Use bottom copper only in fabrication output, including THT pads.
- Route without jumpers. If routing proves to require wire links, stop and review that change before adding them.

## Power architecture

- MCU module: **Teyleten Robot Type-C Pro Micro, ATmega32U4, 5 V / 16 MHz**, with USB-C.
- Purchase listing title: `Teyleten Robot Type-C Pro Micro Atmega32U4 5V 16MHz Module Board Micro USB Pro Micro Development Board Micro Controller 3pc` (Amazon).
- Module features: four 10-bit ADC channels, twelve digital I/Os including five PWM-capable pins, and hardware RX/TX serial.
- Power the module directly from the radio's nominal **8 V supply through RAW**. Suitability of this input voltage is accepted for this revision; voltage-conditioning changes are outside the current scope.
- The module includes seller-specified PTC fuse and diode protection.
- Provide clearance for the **USB-C connector** and a connected cable.
- KiCad module footprint source: project-local `Biacco42_ProMicro:ProMicro`, adapted from the public Biacco42 ProMicro library with its pad centers preserved. The implementation uses `CTCSS_THT:ProMicro_CNC_BCu`, its enlarged-land CNC derivative. See [library provenance and integration checks](../implementation/promicro-library.md). Actual USB-C clone/socket fit and machining remain physical verification items.
- Incoming microphone power at J_MIC_IN pin 2 passes to J_RADIO_OUT pin 2 and branches directly to MCU **RAW**.
- MCU **VCC** provides the nominal regulated **5 V rail** for the LCD backpack, encoder, input pull-ups, and status LED circuits.
- All grounds share the routed ground bus.
- Add THT 100 nF local decoupling and THT bulk capacitance.
- Size the power budget for the MCU, LCD backlight, encoder, pull-ups, and LEDs.

## Microphone and radio connectors

J_MIC_IN and J_RADIO_OUT are vertical 1×8, 2.54 mm THT headers:

`Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical`

These headers connect to microphone/radio cable adapters. Label adapter connections by the radio connector pin numbers.

| Pin | Function | Required connection |
| --- | --- | --- |
| 1 | Microphone audio | Direct MIC_IN → RADIO_OUT audio path, with processed tone injected in parallel |
| 2 | Nominal +8 V microphone power | Direct pass-through, branch to MCU RAW |
| 3 | Up/Down | Direct pass-through |
| 4 | Squelch/Spare, designation pending radio verification | Direct pass-through |
| 5 | PTT | Intercepted: microphone switch to MCU sense; transistor pulls radio PTT low |
| 6 | PTT ground | Both headers to common GND |
| 7 | Shield/ground | Both headers to common GND |
| 8 | Function not yet established | Direct pass-through |

Pins 6 and 7 share common GND.

## MCU pin allocation

The table uses **Arduino logical pin names**. Map these to the KiCad symbol pins and physical header pads.

| Function | Logical pin |
| --- | --- |
| LCD SDA | D2 |
| LCD SCL | D3 |
| Encoder CLK | D4 |
| Encoder DT | D5 |
| Encoder SW | D6 |
| Microphone PTT sense | D7 |
| Radio PTT driver | D8 |
| Tone PWM | D9 |
| Bypass toggle | D10 |
| Unused | A0; intentionally unconnected |
| PTT active LED | A1, used as digital output |
| Bypass LED | A2, used as digital output |

Use D7 for PTT sense because D2 is SDA on the ATmega32U4 Pro Micro. D2/D3 are reserved for the LCD I²C bus.

## PTT sense and output

- The microphone PTT input is active low: the switch closes pin 5 to ground.
- Connect microphone PTT to D7 through a small series resistor and provide an external pull-up to 5 V.
- Drive radio PTT with a **THT NPN open-collector stage**: collector to J_RADIO_OUT pin 5, emitter to GND, base driven from D8 through a resistor.
- Add a base-to-emitter/ground pull-down so the transistor defaults off during MCU reset.
- Size the transistor and resistors for the radio PTT voltage and sink current.
- During reset or loss of MCU drive, the default state must be **PTT released**.

## Tone generation, filtering, and mixing

Required signal order:

`D9 PWM → R1 → FILTER_1 → R2 → FILTER_2 → R3 → DIVIDER → level adjustment → DC-blocking capacitor → R5 → microphone audio`

- C1 connects FILTER_1 to GND.
- C2 connects FILTER_2 to GND.
- R4 connects DIVIDER to GND.
- Microphone audio remains directly connected between header pin 1 connections. The tone chain is a parallel injection branch, not a series audio filter.

| Reference | Required value/function |
| --- | --- |
| R1 | **3.3 kΩ**, first filter series resistor |
| R2 | **3.3 kΩ**, second filter series resistor |
| C1 | **100 nF**, first filter shunt capacitor |
| C2 | **100 nF**, second filter shunt capacitor |
| R3 | **10 kΩ**, divider upper resistor |
| R4 | **1 kΩ**, divider lower resistor |
| R5 | **100 kΩ**, tone isolation/mixing resistor |
| RV1 | 10 kΩ Bourns 3296W-1-103LF; CW end to DIVIDER, CCW end to GND, wiper to C3 |
| C3 / C_TONE | 1 µF nonpolar WIMA MKS2C041001F00KSSD, 63 V, 5 mm pitch |

R1/R2 use 3.3 kΩ to limit attenuation at 151.4 Hz. Each isolated 3.3 kΩ / 100 nF section has a nominal corner near **482 Hz**. The two passive sections, divider, trimmer, and radio load interact; this figure is not the complete chain's cutoff.

The 10 kΩ / 1 kΩ divider gives **1/11 voltage** when unloaded, rather than exactly 1/10. R5 and radio input loading cause additional attenuation. Provide enough tone amplitude and adjustment range to set the required radio deviation.

Passive footprints:

- Resistors: `Resistor_THT:R_Axial_DIN0204_L3.6mm_D1.6mm_P5.08mm_Horizontal`.
- C1/C2: `Capacitor_THT:C_Disc_D3.0mm_W2.0mm_P2.50mm`.

Select THT footprints for the coupling capacitor, supply capacitors, and trimmer to match the selected parts.

## Off-board user interface

All UI connectors use vertical 2.54 mm THT headers. The implemented board pin order is below; verify the off-board device wiring against it before cable assembly. J5/J6 provide one ground contact per device so no external ground splice is required.

| Connector | Implemented pin order |
| --- | --- |
| J_UI_ENCODER, 1×5 | 1 CLK/D4; 2 DT/D5; 3 SW/D6; 4 +5V; 5 GND |
| J_UI_LCD, 1×4 | 1 GND; 2 +5V; 3 SDA/D2; 4 SCL/D3 |
| J5 / J_BYPASS, 1×2 | 1 BYPASS/D10; 2 GND |
| J6 / J_UI_LEDS, 1×4 | 1 PTT LED anode via R6; 2 PTT LED cathode/GND; 3 BYPASS LED anode via R7; 4 BYPASS LED cathode/GND |

- R6 and R7 are **330 Ω** THT current-limiting resistors.
- LED outputs source current to off-board LED anodes through R6/R7; LED cathodes return to the header GND.
- The bypass switch closes to GND with R15 pull-up. R12–R14 provide encoder pull-ups.
- Use one wire per header contact: J5 pins 1–2 serve the bypass switch; J6 pins 1–2 serve the PTT LED and 3–4 the bypass LED. Join the returns on the PCB, not in external Y-splices.

## Functional behavior and firmware interface

- Tone frequency is user-selectable in firmware through the encoder/LCD UI. Include **151.4 Hz** among the supported tones; the accepted tone range and 50 presets are defined in the [firmware baseline](firmware-specification.md). Nominal PWM carrier: **10 kHz**, independently configured from the synthesized tone frequency.
- Generate the tone using the Pro Micro PWM output and the specified analog filter.
- Forward microphone PTT through firmware to the transistor-controlled radio PTT output.
- **Bypass means tone disabled while PTT is forwarded by firmware.** It depends on MCU power and functioning firmware; do not add a relay or mechanical bypass.
- PTT-active indication reflects commanded radio PTT; bypass indication reflects the bypass state.
- Tone timing, PTT sequencing, encoder behavior, LCD content, frequency selection range and persistence follow the separate [firmware baseline](firmware-specification.md). No OFF/OFFSET control is present.
- Deliverable scope: schematic and PCB design. Firmware implementation is outside this specification.

## PCB placement and routing strategy

- Prioritize easy component identification, placement, hand soldering, and rework over compactness. Use the available board area to provide working room.
- Place microphone and radio headers adjacent and identically oriented so direct pass-through tracks can run in parallel.
- Place PTT circuitry near the intercepted pin 5 connections.
- Group filter, divider, level adjustment, coupling, and injection components near the microphone audio path.
- Keep PWM source routing and UI switching paths away from the sensitive audio branch.
- Put UI headers on accessible edges and the Pro Micro where sockets and USB access remain practical.
- Route a dedicated ground bus with short branches. Arrange analog returns so LCD and LED return currents do not share the sensitive audio return branch unnecessarily.
- Solve crossings by placement, rotation, and permissible UI header pin ordering; no top-copper escape routes.
- Size trace widths and clearances for the fabrication process and circuit currents.

## Beginner-friendly assembly

- Use top-side horizontal THT resistors and accessible THT capacitors. Avoid upright resistors, stacked parts, and components hidden beneath the Pro Micro.
- Keep each functional block visually distinct. Arrange repeated parts in consistent orientations and align connector pin-1 ends wherever routing permits.
- Provide at least **2 mm between adjacent component bodies**, including socket bodies. Increase spacing at connectors, the trimmer, and large parts to leave room for fingers, tweezers, and removal tools.
- Choose footprints to match the actual lead spacing and body size. Prefer parts that drop into their holes without bending leads against the body or forcing them into place.
- For new footprint selections, prefer generous annular rings and solder pads over minimum-size library pads. Review the specified compact resistor and capacitor footprints for hand-soldering access; use larger THT alternatives when needed, preserving values and circuit function.
- Size finished holes for easy insertion of the selected leads and header pins. Ensure adjacent pads retain enough clearance to avoid solder bridges. Record hole and pad dimensions during footprint review.
- Keep every bottom-side solder joint accessible to an ordinary soldering-iron tip. Avoid tracks squeezed between header pads when a route around the connector is practical.
- Mount the Pro Micro in **two THT female socket strips** so it can be replaced. Keep the module outline, USB-C end, and insertion orientation visible on the board; label both socket rows by function.
- Provide clear polarity and orientation marks for the transistor, polarized capacitors, module, and connectors. Show transistor lead functions beside its footprint and mark capacitor positive terminals explicitly.
- Place each component reference and value where it remains readable after assembly. Keep text out from under component bodies, socket strips, and connector housings.
- Identify connector pin 1 with both a pad-shape distinction and a visible silkscreen mark. Print each pin's function beside its position, including **+8V**, **+5V**, and **GND** rather than relying on wire colors.
- Mark the tone trimmer's adjustment point and direction of increasing tone level. Keep its screw accessible with the module and cables installed.
- Provide labeled, THT-accessible test points for **GND, +8V, +5V, PWM, filtered tone, tone injection, microphone PTT sense, and radio PTT**. Place a GND test connection where a meter or oscilloscope ground clip can attach without shorting adjacent conductors.
- Provide an assembly drawing and BOM with references, values, polarity, and lead spacing. Order the assembly instructions from low-profile parts through sockets and headers, inserting the Pro Micro after soldering and inspection.
- Include a staged bring-up checklist: inspect joints and bridges, check power-to-ground resistance for shorts, and verify polarity and socket wiring before inserting the Pro Micro. With power off, insert the module in the marked orientation. Use a current-limited bench supply to check RAW and the module-generated +5V rail before connecting the radio and off-board UI.

## Educational silkscreen

Provide readable references, values, connector pin functions, pin-1 marks, transistor orientation, module orientation, and adjustment instructions. Include block labels such as:

- `8-PIN PASS-THROUGH`
- `PTT SENSE` and `PTT DRIVER`
- `RC FILTER`
- `VOLTAGE DIVIDER`
- `TONE LEVEL` and `AUDIO MIX`
- `5V PRO MICRO — 8V INPUT TO RAW`

Keep labels clear of pads, holes, component bodies, and sockets. Ensure connector functions remain identifiable after assembly. Pin labels must match the final netlist and physical header order.

## Implementation workflow and acceptance evidence

1. Inspect the existing project and preserve unrelated work.
2. Capture the complete annotated schematic, power symbols, functional notes, and verified module/discrete pin mappings.
3. Assign and verify all THT footprints, including socket compatibility and exact transistor lead order.
4. Export and inspect connectivity; run ERC and resolve or document justified findings. Render and visually review the schematic.
5. Synchronize the verified schematic to the PCB using a reviewed dry run.
6. Create the rectangular outline and four mounting holes; place all components and complete bottom-only routing and ground buses.
7. Add and visually inspect the educational silkscreen.
8. Save, run DRC, and verify no shorts, clearance failures, or unrouted required connections remain. Independently confirm no top/inner traces, routing vias, or copper pours, and confirm dimensions, mounting holes, and THT technology.
9. Deliver the editable KiCad project with reviewable schematic/layout outputs and an explicit list of remaining bench checks. Fabrication readiness requires completion of the electrical and physical checks.

Assembly acceptance also requires a top/bottom visual review of component spacing, soldering-iron access, readable populated-board labels, socket orientation, test-point access, and the assembly drawing/BOM. Resolve soldering-access problems through placement and footprint changes before reducing spacing to finish routing.

All KiCad design modifications must use Konnect MCP tools under the installed Konnect workflow. Do not edit serialized KiCad files directly.

## Open verification items

| Item | Required evidence or decision |
| --- | --- |
| Radio/microphone wiring | Exact IC-229H documentation and actual microphone/cable pin mapping, especially pins 4, 6, 7, and 8 |
| Microphone-port power | Check available current against the total board and UI load. |
| Module | Check header pin mapping and footprint fit. Define the USB/radio powering procedure. |
| PTT | Switch behavior, radio voltage/current, transistor selection and package map, resistor sizing |
| Tone chain | Loaded response, amplitude consistency and achievable radio deviation across the selected tone table, including 151.4 Hz; 10 kHz carrier rejection, trimmer range and coupling capacitor sizing |
| Audio | Radio input impedance/bias, microphone loading, injection level, audible noise and distortion |
| UI | Final header order, actual encoder/LCD interfaces, pull-ups and LED current |
| Fabrication | Copper thickness, material, trace/clearance limits, bottom-only copper manufacturing process and drill requirements |
| Mechanics | Socket/header fit, USB access, enclosure/cables, washer/standoff clearance |

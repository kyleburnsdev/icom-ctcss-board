# Completed schematic capture

The saved project schematic contains **38 annotated components**, all assigned to the bottom-only CNC footprints in `electronics/libraries/CTCSS_THT.pretty`. U1 and RV1 are now present; the earlier partial checkpoint is historical. The custom module symbol is in `electronics/libraries/CTCSS.kicad_sym`, registered project-locally. All KiCad source changes used Konnect.

## Implemented circuit

Tone frequency is user-selectable in the future encoder/LCD firmware. The 151.4 Hz requirement is a supported-tone check, not a fixed-frequency hardware setting. The RC chain has a broad response; see the [frequency examples](tone-response.md#selectable-tone-frequencies). No component or firmware implementation locks this design to 151.4 Hz.

J1/J2 are microphone/radio adapters, with direct pins1/2/3/4/8 pass-through and common ground6/7. Pin5 is intercepted: J1 drives D7 through1k R8, with10k R9 pull-up. D8 drives factory-formed onsemi2N3904TAR through4.7k R10, with100k R11 base pull-down; collector drives radio PTT and emitter goes toGND. Radio PTT is released on reset/high-impedance drive.

D9 drives the specified3.3k/100nF two-stage filter,10k/1k divider and10k Bourns3296W-1-103LF level control. RV1 pin3(CW) is DIVIDER, pin1(CCW) GND and pin2 wiper drives1uF C3, then100k R5 to the direct microphone audio path. Clockwise increases tone; start fully CCW. C3 is nonpolar KEMET R82DC4100AA60J. C4/C5 provide100nF RAW/VCC decoupling; C6 is nonpolar4.7uF/63V TDK B32522C0475J000 bulk capacitance.

UI headers follow the specification's cable order. R12–R15 provide10k encoder/toggle input pull-ups;330Ω R6/R7 source current to off-board LEDs. SDA=D2 and SCL=D3. LCD backpack pull-ups must be present and checked; none are duplicated on this board. Eight labeled THT test points expose ground, supplies, PWM, filtered tone, injection, PTT sense and radio PTT.

All24 module header contacts map to the user-approved nominal Biacco42 geometry. Pin24 RAW is power input, pin21 VCC regulated output; three distinct GND contacts are connected. Eight unused contacts (TX/RX/MOSI/MISO/SCK/A0/A3/RST) have explicit no-connect marks. The module itself contains its reset circuitry. External supply flags apply only to incoming radio+8V andGND; no fake+5V source was added. [Accepted physical maps](physical-pin-maps.md) and [CNC footprint review](footprint-review.md) contain exact sources, counts, geometry and disposable validation.

## Verification

- The schematic was visually inspected at 4096 px, with continuous filter chain, visible level-control stage, all module pins and clear block notes; the retained [PDF](../reference/schematic-complete.pdf) provides the readable circuit reference.
- [PDF](../reference/schematic-complete.pdf), [netlist](../verification/schematic-complete.net), and [BOM CSV](../reference/bom.csv) were exported from saved state. Duplicate renders and raw library readbacks are no longer maintained.
- [ERC](../verification/erc-complete.json): **zero errors and zero warnings**, KiCad10.0.0 via Konnect.
- Existing-pin and wire-endpoint checks: zero unconnected unmarked pins, zero floating endpoints.
- `python tools/check-netlist.py` checks pass-through/interception, filter/divider/trimmer/mixer, Q1 leads, all used U1 contacts, separateRAW/VCC, eight unused contacts, all38 footprint assignments and UI nets from the exported netlist.

Schematic and library mutations were frozen and handed back before root PCB synchronization. PCB layout/CAM/assembly checks and bench electrical acceptance remain separate work; see [acceptance checklist](acceptance-checklist.md) and [assembly/bring-up](assembly-and-bring-up.md).

## Power and bench assumptions

Reserve an initial engineering budget of50mA for module,100mA forLCD/backlight,5mA for encoder,30.3mA for bothLED paths (conservative5V/330Ω with zero LED forward drop),2.5mA for five active10k pull-ups, and0.9mA for transistor drive: approximately189mA, rounded to a**200mA+5V branch allocation**. These are design allocations, not measured demands or confirmed module capability. The actual LCD/backlight and module must be measured; neither regulator identity nor radio port current limit is established. An LDO supplying200mA from8V to5V dissipates about0.6W before quiescent losses, so thermal/current validation is essential. Incoming8V current also includes the microphone pass-through load. Do not claim this budget is accepted by the radio or clone regulator.

Only radio-toRAW suitability was accepted for this revision; no extra voltage conditioning was introduced. Disconnect radio power before USB programming, and unplugUSB before radio-powered operation, until the actual module's USB/VCC/RAW isolation is verified. Check4.7uF bulk adequacy and rail transients underLCD/backlight switching; selection is a starting implementation value, not measured stability evidence.

PTT5mA sink target is provisional. Measure radio voltage/current and verify saturation and reset release. Loaded tone gain/deviation remains dependent on radio input bias/impedance and actual PWM waveform; [the linear response model](tone-response.md) is illustrative. Verify microphone loading, carrier noise, deviation and audible behavior on the real radio. No firmware was implemented.

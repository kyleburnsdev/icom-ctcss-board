# Assembly and bring-up procedure

Use the [final BOM](../reference/bom.csv) and [top assembly drawing](../reference/assembly-top.svg); do not assemble from an earlier checkpoint. Radio cable mapping, available port current, and tone deviation remain bench acceptance items.

Supplement the circuit BOM with two 1×12, 2.54 mm female socket strips (15.24 mm between row centers), compatible module male pins if needed, external cable mates, and four suitable insulating standoffs/fasteners for 4 mm holes. Select sockets no wider than the assumed 3 mm body and confirm their pins fit the 1.1 mm holes. Reserve hardware within a 4 mm radius of each mounting-hole center; verify the actual washers against copper and components. External LCD, encoder, switches and LEDs are off-board accessories. Verify their ratings and connector orders before purchase/assembly. All selected board capacitors are nonpolarized; no electrolytic polarity assumption applies.

## CNC board inspection

Follow the [manufacturing order](pcb-jig-and-freecad-cam.md#jobs-maintained-through-robust-mcp-server): isolate bottom copper and inspect exposed channels/continuity, apply and cure bottom mask, open pads with the Makera spring tool, then drill and deburr **before top coating is applied**. Keep the top support surface bare and flat throughout precision isolation milling. Retain the copper G54 Z0 established before trace cutting for all subsequent programs; do not capture a new work zero on a coating or after remounting/flipping.

1. Check the final bottom-copper preview against the top-side assembly drawing. Confirm the CAM transform for bottom-side machining before cutting: exported board coordinates are not permission to mirror an arbitrary number of times. Check registration using an asymmetric pin-1 feature and mounting-hole coordinates.
2. On the milled board, inspect every isolation channel for copper whiskers and bridges. Remove chips and burrs without cutting traces or lifting pads. Inspect the compact socket/header gaps under magnification.
3. Check actual drill sizes and hole registration on sacrificial material before the circuit board. Holes are unplated: a trace or pad on the top side cannot provide connectivity.
4. Check bare-board continuity against the final netlist. Each net should be continuous end-to-end, with no connection to neighboring nets. Verify both +8V and +5V are isolated from GND and from each other while the module is absent. Through the eventual resistive signal paths, a nonzero resistance may be intended; use the schematic to distinguish it from a copper short.

After those checks pass, flip about Y, re-register, and apply the top legend using the [dedicated Gerber/SVG and white-mask marking instructions](../../manufacturing/pcb/carvera-air/README.md#setup-40-top-coating-and-legend). Fully UV-cure the white coating before laser marking. Use the first full board as the marking test piece; inspect legibility, retention and coating integrity after IPA cleaning, then adjust the next board if needed. The assembly drawing includes F.Fab details and must not replace the legend marking artwork. Keep holes clear and orientation marks readable. Retain locating features until both sides are finished; after final release/cleaning, repeat continuity and short checks before fitting parts.

After both face coatings and bottom pad opening are complete, inspect all holes.
If coating obstructs them, use the [independent bottom-hole program](../../manufacturing/pcb/carvera-air/README.md#setup-30-independent-bottom-holes)
before fitting parts. Re-register after remounting, withdraw all PCB pins,
retain the original pre-isolation copper G54 Z0, reproduce original seating,
and protect breakthrough and the finished top coating. Do not capture a new zero.
Clean debris, inspect pad integrity, check lead fit, and repeat continuity/short
checks. Keep jig registration holes clear; the clearing program excludes them.
The pad-opening job runs before initial electrical holes; do not run its spring
tip across already-open electrical holes.

## Assembly order

### J5/J6 cable wiring

Each device gets its own two-wire pair, with one wire per contact and no external Y-splice. Identify pin 1 from the component-side drawing/mark; cable mating views can reverse the apparent order.

| Device | Header pair | Wiring |
| --- | --- | --- |
| Bypass toggle | J5 pins 1–2 | Switch between pin 1 (D10) and pin 2 (GND) |
| PTT indicator | J6 pins 1–2 | LED anode (+) to pin 1; cathode (−) to pin 2 |
| Bypass indicator | J6 pins 3–4 | LED anode (+) to pin 3; cathode (−) to pin 4 |

The J5 bypass input already has the R15 10 kΩ pull-up: open reads HIGH, closed reads LOW. No external +5V wire is needed. J6 already has the R6/R7 330 Ω series resistors for bare LEDs. The two ground contacts on J6 are joined on the board. The LEDs and bypass switch behavior require firmware. J5 has only two contacts; there is no OFF/OFFSET switch.

This revision uses a two-pin J5 and four-pin J6. Use the current PCB, drilling/legend files, BOM and cable map together. Earlier three-pin layouts and the superseded four-pin J5 OFF/A0 layout are historical; do not mix their manufacturing files with this revision.

1. Fit the horizontal resistors, verifying reference and value against the BOM.
2. Fit small nonpolar capacitors, then the larger film capacitors and trimmer. Match the trimmer's marked pin order and adjustment direction to the drawing.
3. Fit the exact specified transistor suffix in its marked E/B/C orientation. A different TO-92 part is not automatically pin-compatible. Use the selected formed-lead part instead of bending leads against the body.
4. Fit the test points, cable headers, and two female Pro Micro socket strips. Use the module or a mechanical alignment fixture only to align cold sockets; remove the module before soldering. Keep sockets square and fully seated.
5. Inspect every bottom-side joint. Check solder bridges, wetting and lifted pads. No solder should be relied upon to join an interrupted milled track accidentally.

## Before installing the module

With USB, bench supply, radio and UI cables disconnected:

1. Verify the two microphone/radio header pin-1 marks and all pass-through connections. Confirm PTT pin 5 is intercepted rather than shorted between headers.
2. Verify GND at header pins 6/7 and every ground test connection.
3. Verify +8V reaches RAW only, and the +5V net reaches VCC and the specified UI pins. Check socket row orientation against the final physical pin map.
4. Measure resistance from each supply to GND and check for shorts. Allow meter readings to settle as capacitors charge; do not apply a universal resistance threshold to a populated circuit.
5. Confirm that no test firmware, external cable or socket orientation can drive the radio PTT transistor inadvertently during the first power test.

## First power and functional tests

1. With all power off, insert the module in the marked orientation. Leave the radio and off-board UI disconnected. Use a current-limited bench supply at the accepted RAW input voltage, starting with a limit appropriate to the module alone. If it current-limits or a part heats unexpectedly, disconnect and investigate.
2. Verify RAW voltage at TP2 and regulated +5V at TP3 relative to TP1. Record supply current and regulator temperature; a correct unloaded voltage does not establish the LCD/backlight power budget.
3. Power off before adding each UI cable. Verify its connector order first. Confirm the LCD backpack supplies suitable SDA/SCL pull-ups to +5V; this PCB does not duplicate them. A backpack without pull-ups requires a reviewed correction before use. Repeat rail/current/temperature checks under the full intended load.
4. Use suitable test firmware to verify active-low microphone PTT sense, commanded radio PTT output, reset release, and bypass behavior before connecting the radio. Firmware is a separate deliverable; these checks remain pending without it.
5. Connect the radio only after verifying the actual cable pinout, PTT open-circuit voltage/sink current, and available microphone-port current. Set the tone trimmer to minimum initially. Set the required deviation with appropriate radio test equipment, checking microphone audio and residual PWM noise.

## USB/radio power handling

Until the exact clone power path has been verified, disconnect radio/bench RAW power before connecting USB for programming, and disconnect USB before applying RAW power. Never rely on the unrelated seller ATmega328P schematic as evidence for this module's protection or backfeed behavior. Power down before inserting/removing the module or changing UI wiring.

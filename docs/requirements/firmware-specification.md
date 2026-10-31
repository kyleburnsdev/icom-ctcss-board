# CTCSS/PL firmware requirements — version-one baseline

**Status: version-one baseline accepted by the user on 2026-10-20; implementation has not started.** The consolidated UI flow and engineering defaults below are agreed requirements. Hardware identification and physical acceptance remain outstanding; PCB cleanup is complete; acceptance of this baseline does not mean those checks have passed.

**Completed control change:** OFF is removed altogether. The interface stays powered with the radio so microphone PTT forwarding remains available. There is no OFF switch, OFFSET feature, software power-off or sleep substitute. J5 is now BYPASS/GND only, R16 and the A0 switch wiring are removed, and U1 A0 is intentionally unused. The BOM and manufacturing files reflect this cleanup.

## Purpose and authority

Provide user-selectable CTCSS/PL tone generation and microphone PTT forwarding for the Icom IC-229H interface board. The encoder/LCD select and display operating settings; one bypass toggle and two LEDs provide the additional controls/indications described below.

The [board specification](board-specification.md), [saved schematic/netlist](../verification/schematic-complete.net), and [J5/J6 wiring](../implementation/assembly-and-bring-up.md#j5j6-cable-wiring) are hardware constraints. Firmware must conform to their pin allocation, polarity, wiring and analog signal path. A firmware convenience does not authorize changing the PCB. Any hardware conflict must be reported and resolved explicitly before implementation.

The original board deliverable excluded firmware. This document starts the separate firmware scope; it does not replace the hardware requirements or imply that outstanding physical checks have passed.

## Firmware technology stack

**Decision accepted on 2026-10-21:** Implement the firmware as a standard Arduino sketch (`.ino`), using the Arduino programming model with `setup()` and `loop()` and an Arduino-compatible core/board definition for the actual ATmega32U4 Pro Micro **5 V / 16 MHz** module.

This choice supports the project's educational purpose, matches the Arduino-compatible hardware, and keeps the implementation accessible to readers familiar with ordinary Arduino sketches. The current requirements and plausible future extensions are expected to fit this approach; they do not justify a more complex framework at this stage.

Keep the sketch readable and organized, with supporting C/C++ files where useful. Use standard Arduino APIs and libraries where they meet the requirements; documented AVR timer/register code and interrupt handlers may be used where waveform timing or other hardware constraints require them. The sketch structure must still meet the response, persistence and fault-handling requirements below.

The firmware approach is settled. Exact core/board package and library versions, build/upload instructions, timer allocation and LCD driver remain implementation choices to verify and document against the actual module and peripherals.

## Confirmed hardware constraints

### MCU and pin allocation

Target U1 is the Teyleten USB-C Pro Micro, ATmega32U4, **5 V / 16 MHz**. Arduino logical pin names below are not physical socket-pad numbers. Do not assume an Uno/Nano pin map or silently substitute another Pro Micro voltage/clock variant.

| Function | Arduino name | U1 socket pad | Electrical behavior / connection |
| --- | --- | ---: | --- |
| LCD SDA | D2 | 5 | J4 pin 3; I²C SDA |
| LCD SCL | D3 | 6 | J4 pin 4; I²C SCL |
| Encoder CLK | D4 | 7 | J3 pin 1; external 10 kΩ pull-up |
| Encoder DT | D5 | 8 | J3 pin 2; external 10 kΩ pull-up |
| Encoder push switch | D6 | 9 | J3 pin 3; external 10 kΩ pull-up; switch closes to GND |
| Microphone PTT sense | D7 | 10 | Active LOW; 1 kΩ series resistor and external 10 kΩ pull-up |
| Radio PTT drive | D8 | 11 | HIGH drives Q1 on and pulls radio PTT to GND; LOW releases it |
| Tone PWM | D9 | 12 | Drives the fixed analog reconstruction/injection chain |
| Bypass toggle | D10 | 13 | J5 pin 1, return pin 2; external 10 kΩ pull-up; closed reads LOW |
| Intentionally unused | A0 | 17 | Unconnected/NC; no switch connection or pull-up. Do not use it as a firmware control |
| PTT LED | A1 as digital output | 18 | HIGH illuminates LED via R6/J6 pin 1; cathode returns at J6 pin 2 |
| Bypass LED | A2 as digital output | 19 | HIGH illuminates LED via R7/J6 pin 3; cathode returns at J6 pin 4 |

J3 also supplies +5V on pin 4 and GND on pin 5. J4 supplies GND on pin 1 and +5V on pin 2. The LCD backpack must provide suitable SDA/SCL pull-ups; firmware cannot assume an absent pull-up network has been supplied by the carrier board.

The selected display format is **1602: 16 columns × 2 rows**. Use the PCB's I²C connection; the actual backpack/controller mapping, I²C address and backlight current still require identification. The format alone does not establish those details.

TX/RX, MOSI/MISO/SCK, A0, A3 and RST are intentionally unused by the carrier circuit. There is no authorization to repurpose connected pins or add required wires to unused pins. USB programming/diagnostics must not require those spare header contacts.

### Analog and radio interface

- **HW-01:** Generate tone on D9 only. Its fixed path is two 3.3 kΩ/100 nF low-pass sections, the 10 kΩ/1 kΩ divider, 10 kΩ level trimmer, 1 µF DC-blocking capacitor and 100 kΩ mixing resistor into the direct microphone audio path.
- **HW-02:** The PWM carrier is nominally 10 kHz, distinct from the selected subaudible tone frequency. Verify achievable timer mode, resolution and update timing for the actual 16 MHz target before committing to a waveform implementation. Do not let a library default silently change the carrier or use a square-wave tone as a substitute for reconstructed sine generation.
- **HW-03:** Support selectable tones, including 151.4 Hz, through both manual entry and a common-preset menu. Use 67.0–254.1 Hz inclusive with one decimal place for manual entry. This range is selected from published amateur-radio CTCSS tables; it does not itself prove radio deviation or hardware performance at the endpoints. No component selects a fixed tone.
- **HW-04:** RV1 provides manual overall amplitude adjustment. There is no MCU control of that trimmer, microphone gain or radio deviation. Frequency-dependent waveform amplitude compensation is possible only within available digital/analog headroom and must be validated against the real load.
- **HW-05:** Microphone audio and connector pins 1/2/3/4/8 pass through in hardware. PTT pin 5 is intercepted and requires functioning firmware to reach the radio.
- **HW-06:** Bypass means tone disabled while microphone PTT is still forwarded by firmware. It is not an unpowered or mechanical bypass.
- **HW-07:** Reset/high-impedance D8 is released by the hardware base pull-down. Firmware must not deliberately key the radio during boot, reset recovery or initialization. Bootloader behavior still needs physical verification.
- **HW-08:** The PTT LED indicates the firmware's PTT command. There is no radio-transmit feedback input, so it cannot certify actual RF transmission.
- **HW-09:** No interface power switch or frequency-offset control is required. The unit stays powered from the radio during operation. A0 is unconnected; do not implement a function for it. There is no firmware connection for controlling the radio’s RF transmit offset.
- **HW-10:** The PCB does not provide rail-voltage, transistor-current, tone-amplitude or RF-deviation feedback. Firmware must not claim to measure or automatically guarantee these quantities.

The [tone-response model](../implementation/tone-response.md) shows a broad but non-flat response. It is illustrative, not radio acceptance evidence. Test the agreed tone table for level, distortion, PWM residue, microphone loading and radio deviation.

**Implementation evidence (2026-10-25):** [LTspice keying analysis](../implementation/ltspice-validation.md#tone-enabledisable-transient-firmware-action) shows that stopping D9 LOW shifts the filter's DC level and produces a coupling-capacitor transient. The engineering recommendation is to retain a 50% idle PWM duty and ramp modulation about that center. This informs the pending waveform implementation; it does not change the agreed command-response budget or establish bench acceptance of idle carrier and switching clicks.

## Confirmed functional intent

| ID | Requirement |
| --- | --- |
| FN-01 | Provide an encoder/LCD menu with manual tone entry and common preset selection. For manual entry, rotation edits the current digit; a short press cycles through the four numeric digits and a Cancel item, skipping the fixed decimal point. Long press on a digit saves a valid frequency and returns to the menu; long press on Cancel discards edits and returns without saving. |
| FN-02 | 151.4 Hz is included as a supported tone and is the first-use/invalid-settings fallback. A valid saved setting takes precedence; 151.4 Hz is not a fixed operating frequency. |
| FN-03 | Read active-low microphone PTT and drive the active-high D8 transistor control to forward it during normal operation. |
| FN-04 | In bypass, suppress tone but retain firmware PTT forwarding. Changes to the bypass switch take effect during an active transmission without releasing radio PTT, subject only to bounded input qualification. |
| FN-05 | PTT indication reflects commanded radio PTT; bypass indication reflects bypass state. |
| FN-06 | J5 is a two-pin BYPASS/GND connector; J6 retains its four-pin PTT LED+/GND/BYPASS LED+/GND map. Preserve one wire per contact with no return-wire splice. |
| FN-07 | Forward microphone PTT and generate the selected tone until release. In bypass, forward PTT without tone. Do not generate a continuous idle tone. Transition timing follows the accepted 25 ms response budget and keying sequence below. |
| FN-08 | Remove OFF entirely. Stay powered with the radio; provide no firmware OFF, OFFSET or sleep control. Bypass is the powered tone-disable mode and continues to forward PTT. |
| FN-09 | Fit the menu and operating information on a 1602 display: 16 characters per row, two rows. |
| FN-10 | Restore the last saved valid tone after a power cycle. If settings are missing, corrupt or outside the allowed range, use 151.4 Hz. Loading the fallback does not bypass the startup release-before-rearm requirement. |
| FN-11 | Latch the tone frequency for each transmission and keep it unchanged until microphone PTT is released. A tone saved during transmission is pending and becomes the active selection after release; unsaved digit edits never change the transmitted tone. If bypass is enabled then disabled during that transmission, resume the latched frequency, not a pending saved frequency. |
| FN-12 | On power-up or any reset, keep radio PTT released until the microphone PTT input has been observed released and a new press occurs. A button held through startup/reset must not automatically key the radio, including in bypass. |
| FN-13 | If only the LCD/I²C display fails, continue PTT forwarding and the last valid tone selection, respecting bypass and the per-transmission frequency latch. A display failure alone must not unkey the radio, enable idle tone, apply a pending frequency early or block PTT handling. Do not accept invisible menu edits while the display is unavailable. |
| FN-14 | Preset selection offers all 50 listed frequencies in ascending order. Rotate to highlight a value; short press saves it and returns to the menu. Browsing alone never changes the saved or transmitted tone. The same pending-until-release rule applies if saved during PTT. |

## Tone range and agreed presets

Manual entry accepts **67.0–254.1 Hz inclusive in 0.1 Hz steps**, displayed as `067.0` through `254.1` with a fixed decimal point. The user delegated the range to typical amateur-repeater PL practice; one decimal place is the design choice matching published tone tables. Manual values need not belong to the preset list. Out-of-range intermediate digit combinations must not be committed or transmitted; invalid-entry feedback is specified below. Cancel discards the edit buffer without modifying saved, pending or transmitted frequency. Entry resolution is not a guarantee of measured frequency accuracy.

Range authority: the [Kenwood TM-281A manual](https://www.kenwood.com/usa/Support/pdf/TM-281A_Manual.pdf) lists 42 tones spanning 67.0–254.1 Hz. For a broader preset menu, the [Yaesu FT-450 CAT reference, Table 1, printed page 5](https://public2024.yaesu.com/Files/4CB893D7-1018-01AF-FA97E9E9AD48B50C/FT-450_CAT_Operation_Reference_Book.pdf?ts=4%2F12%2F2026+9%3A40%3A26+AM) publishes the following 50-tone chart. Sources checked 2026-10-20. These are tone-frequency choices, not regional repeater-use statistics or a promise that a particular repeater accepts every entry.

Agreed preset menu: all 50 entries, ascending by frequency, displayed in Hz rather than manufacturer-specific tone-code numbers:

```text
67.0, 69.3, 71.9, 74.4, 77.0, 79.7, 82.5, 85.4, 88.5, 91.5,
94.8, 97.4, 100.0, 103.5, 107.2, 110.9, 114.8, 118.8, 123.0, 127.3,
131.8, 136.5, 141.3, 146.2, 151.4, 156.7, 159.8, 162.2, 165.5, 167.9,
171.3, 173.8, 177.3, 179.9, 183.5, 186.2, 189.9, 192.8, 196.6, 199.5,
203.5, 206.5, 210.7, 218.1, 225.7, 229.1, 233.6, 241.8, 250.3, 254.1
```

## Operating behavior baseline

The following decisions form the accepted version-one baseline. Outstanding device identification and validation are explicitly identified.

| Decision | Version-one behavior | Status |
| --- | --- | --- |
| Tone selection modes | Menu offers manual digit-by-digit entry and common presets | Confirmed |
| Manual entry | 67.0–254.1 Hz, 0.1 Hz steps; rotate to edit digit; short press cycles digits plus Cancel; long press saves on a digit or discards on Cancel | Confirmed; feedback and 750 ms long press specified below |
| Preset table | Published 50-tone list above, ascending; rotate to browse, short press saves/returns | Confirmed |
| Display | 1602 (16×2) showing active tone, bypass and PTT state as described below. Backpack address/mapping require identification | UI confirmed; hardware identification outstanding |
| Power control | No separate OFF switch; interface remains powered with radio. The unused A0/J5/R16 control hardware is removed | Confirmed; PCB cleanup complete |
| Tone duty | Selected tone only during PTT when not bypassed; no tone while idle or bypassed | Confirmed |
| Keying sequence | Start PTT and tone enable from the same qualified press; stop both on release, with no deliberate tail. Verify filter settling and clicks | Confirmed; bench validation outstanding |
| Changes during PTT | Saved frequency changes wait until PTT release. Bypass immediately stops/resumes tone without unkeying the radio; resumption uses the same latched transmission frequency | Confirmed; command response within 25 ms including qualification |
| Bypass switch polarity | Closed-to-GND means bypass enabled; open means disabled | Confirmed |
| Encoder direction | Clockwise selects the next higher tone; actual encoder transition direction is a device setting | Confirmed |
| Power-up setting | Restore the last saved valid tone; use 151.4 Hz if missing/invalid. Physical bypass switch determines bypass state | Confirmed |
| Saving settings | Save only explicit changes; validate durable storage before saved feedback, preserve responsive PTT and recover prior or complete new data after interrupted writes | Confirmed |
| PTT held at boot/reset | Stay released until the operator releases PTT and presses it again, in both normal and bypass operation | Confirmed |
| LCD/I²C failure | Continue PTT and the last valid tone, respecting bypass and the transmission latch. Disable invisible menu editing and avoid indefinite bus waits; recovery mechanics to be designed | Operating policy confirmed; technical recovery details open |
| Watchdog recovery | Use a bootloader-compatible watchdog targeting recovery within one second; every reset uses release-before-rearm | Confirmed; actual module compatibility and timing require validation |
| Calibration | Start with one documented digital amplitude setting alongside RV1; measure range-wide deviation before considering per-tone compensation | Confirmed initial approach; bench evidence outstanding |
| USB | Programming and optional diagnostics only, with no wait for a serial host during standalone startup | Confirmed |

In particular, a software hang while D8 is HIGH can leave the output commanded on until reset. The base pull-down handles reset/high impedance, not arbitrary running-code failure. Define recovery and test it rather than promising unconditional fail-safe release.

## Consolidated UI flow

The following navigation, editor gestures and screen wording are accepted for version one:

1. Home shows the active tone plus receive/transmit and bypass status. Short press opens a menu with Presets, Manual and Back; rotation moves the menu highlight and short press selects it. Back returns home.
2. Presets opens at the saved value if present in the table, otherwise the nearest table entry (tie goes to the lower frequency). Rotation browses; short press saves/returns to the menu. Long press exits to the menu without saving, providing a way out after merely browsing.
3. Manual opens with a separate copy of the saved frequency, including a leading zero below 100 Hz. Rotation wraps the selected digit 0–9 without carrying into other digits. Short presses cycle hundreds → tens → units → tenths → Cancel → hundreds. The decimal point is fixed.
4. Long press on a numeric digit saves only a valid in-range entry; otherwise remain in the editor and show `Range 067-254.1` without changing any committed value. Long press on Cancel discards the edit buffer and returns to the menu. A recognized long press must never also generate a short-press event on release.
5. A save while transmitting updates the saved/next selection; the current transmission retains its latched frequency. Home shows current TX frequency and the pending next frequency. Cancel never undoes a previously completed save.

Accepted 16×2 screen examples (each block is two rows; cursor/highlight treatment is separate):

Home, idle:

```text
Tone 151.4 Hz
RX  Tone enabled
```

Manual digit editing (selected digit visibly marked by the LCD cursor):

```text
Manual 151.4 Hz
Hold=Save
```

Manual Cancel item:

```text
Manual 151.4 Hz
>Cancel  Hold=OK
```

Transmission with a saved pending change:

```text
TX 151.4 Hz
Next 100.0 Hz
```

Startup while PTT is held:

```text
Release PTT
To enable TX
```

If editing during PTT, keep a TX indicator visible on the editor's second row. The hardware PTT/bypass LEDs continue to indicate commands independently of which menu screen is displayed.

## Engineering defaults

These defaults were accepted by the user for version one. They are implementation and acceptance targets; measured performance remains to be demonstrated.

| Item | Accepted version-one default |
| --- | --- |
| Encoder long press | 750 ms; one action per press, without repeating saves while held |
| Bypass / encoder direction | Closed switch means bypass enabled; clockwise increases digit/preset/menu position; encoder direction configurable for actual wiring |
| Input response | PTT press/release and bypass command changes within 25 ms of a stable physical input transition, including input qualification, even during menu, display-fault and settings-save work. Analog filter decay is measured separately |
| Keying sequence | Start radio PTT and tone enable from the same qualified press event when not bypassed; stop both on qualified release, with no deliberate transmit tail. Any ramping must remain within the input-response budget and be checked for clicks |
| Display | Refresh changed content within 200 ms under normal operation; do not redraw the entire LCD continuously or block PTT/tone timing |
| Tone accuracy | Measured reconstructed tone within ±0.1 Hz across the accepted range; demonstrate at low/middle/high frequencies and account for actual module clock accuracy. Entry resolution alone is not evidence |
| Saving | Only explicit saves commit settings; never write on digit/preset browsing. Complete a validated durable save before presenting it as saved, while keeping PTT/waveform timing responsive. An interrupted write must recover either the prior valid setting or the complete new setting, never partial data |
| Watchdog | Enable a bootloader-compatible watchdog with a target maximum one-second stalled-firmware recovery; prove reset/release behavior on the actual module. A display-only failure must not cause repeated watchdog resets |
| Tone amplitude | Start with one documented digital amplitude setting and the physical RV1 adjustment; measure range-wide deviation before deciding whether per-tone compensation is needed |
| USB | No startup wait for a serial host; programming and optional diagnostics only. USB connection/reset must not assert PTT or override the release-before-rearm rule |

The LCD backpack address/controller mapping and actual encoder detent/transition behavior remain hardware-identification inputs. Keep them configurable; do not infer them solely from “1602.”

## State model and remaining fault policy

Use these cases to guide implementation and acceptance. The other-peripheral/waveform-fault policy remains to be defined; no behavior is claimed as implemented.

| State | Radio PTT | Tone | Indications |
| --- | --- | --- | --- |
| Boot / recovery | Released | Inactive | No transmit indication; reflect toggle state after valid sampling |
| Awaiting microphone release after boot/reset | Released, even if microphone is held | Disabled | Do not indicate commanded transmission; Show the release-PTT prompt above |
| Ready, microphone released | Released | Disabled | Active selection shown; bypass LED follows agreed bypass state |
| Microphone pressed, normal | Asserted after agreed qualification/sequence | Selected tone until release | PTT LED on |
| Microphone pressed, bypass | Asserted | Disabled | PTT and bypass LEDs on |
| Bypass enabled while microphone held | Remains asserted | Stop selected tone after bounded switch qualification | PTT LED stays on; bypass LED turns on |
| Bypass disabled while microphone held | Remains asserted | Resume the transmission's latched frequency; do not apply a pending saved frequency | PTT LED stays on; bypass LED turns off |
| Release | Released within agreed latency | Stop under agreed sequencing | PTT LED off |
| Display-only fault | Continue normal qualified microphone PTT forwarding | Last valid selection when keyed and not bypassed; retain any current transmission latch | PTT/bypass LEDs continue; no unseen menu changes |
| Other peripheral/waveform fault | Policy still to define by fault class | Policy still to define by fault class | Do not treat all faults as equivalent to display loss |

## Measurable acceptance criteria and outstanding checks

Accepted firmware targets are ±0.1 Hz tone accuracy, 25 ms maximum PTT/bypass command response including qualification, 750 ms long press, 200 ms changed-content display refresh and a target maximum one-second watchdog recovery. Verify actual encoder behavior and qualification against the response budget. Allowable amplitude/deviation variation, waveform distortion and carrier residue still need numerical bench acceptance limits. Distinguish firmware measurements from radio/load-dependent measurements.

The Arduino sketch implementation must keep tone timing and PTT handling independent of slow display updates, encoder/UI processing and settings persistence. Timer/resource choices must preserve required D9 waveform generation and D2/D3 I²C operation. Exact Arduino core/board package, library and build-tool versions, timer allocation and LCD driver will be chosen after requirements/device identification and checked against the MCU rather than assumed from another Arduino board.

## Required acceptance scenarios

1. Confirm every configured pin and active level against the cleaned-up netlist; demonstrate the three intended device pairs: one bypass switch on J5 and two LEDs on J6.
2. Observe startup/reset/programming with a disconnected radio or suitable test load: no unintended PTT assertion.
3. Exercise PTT press/release, held-at-startup/reset, contact bounce and UI activity; measure maximum latency under load. A held button must never assert radio PTT after startup/reset until a release followed by a new press is observed. Repeat with bypass enabled.
4. Select several tones, including 151.4 Hz and the agreed range endpoints; measure D9 carrier and reconstructed tone frequency/level at the test points.
5. Verify bypass both before and during PTT: toggling it stops/resumes tone without interrupting radio PTT, and LEDs follow the commanded states. Save a different frequency while transmitting, toggle bypass on/off, and verify the resumed tone is still the original latched frequency until microphone release.
6. Verify menu navigation, manual digit editing and preset selection; verify bounds, decimal handling and agreed apply/cancel behavior. Verify no obsolete OFF/OFFSET control is exposed and that the cleaned-up hardware leaves A0 unused.
7. Disconnect/stall the LCD while idle and while keyed: PTT remains responsive, the latched tone stays correct, bypass still works and no invisible edits are committed. Exercise malformed/missing saved settings: select 151.4 Hz and retain startup release-before-rearm. Display recovery must not itself assert PTT or apply an unconfirmed edit.
8. Check settings persistence, reset and power-cycle behavior, including avoidance of excessive nonvolatile writes.
   Include saving a new frequency during PTT: the current transmission stays on its original frequency, the saved selection applies only after release, and a subsequent power cycle restores the saved value.
9. On the actual radio, verify deviation across the tone list, residual carrier/audio noise, microphone behavior and keying/release transients.

Hardware prerequisites remain in the [assembly/bring-up procedure](../implementation/assembly-and-bring-up.md): verify cable pinout, available power, regulator heating and PTT electrical limits. Do not connect USB and RAW/radio power together until the clone's power path is verified. Firmware does not remove those prerequisites.

## Implementation boundary and next steps

The user accepted the consolidated UI flow and engineering defaults as the version-one baseline on 2026-10-20 and the Arduino sketch approach on 2026-10-21. Requirements alignment is complete for those behaviors and the firmware approach. Next, identify the actual LCD backpack/encoder, use the cleaned-up PCB constraints, and choose/verify the Arduino core/board package, libraries, build/upload tooling, timer allocation and display driver against these constraints. Define the remaining fault policy and radio-dependent acceptance limits before implementation acceptance. PCB cleanup is complete; firmware implementation has not started.

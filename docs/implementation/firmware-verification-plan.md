# Arduino verification campaign

Start with the breadboard-mounted **5 V / 16 MHz Pro Micro**, USB only, with
all signal pins disconnected. The radio, carrier, RAW supply, LCD and encoder
stay disconnected through the initial USB checks. This plan extends the
[illustrated phase-one procedure](firmware-phase1-guide.md); use that procedure
for exact wiring, resistor values, power order and shutdown.

The goal is evidence that the Arduino meets the
[accepted firmware requirements](../requirements/firmware-specification.md),
followed by evidence that its real interfaces work with the solution. A host
test pass, a USB reply, a measured pin and a working radio establish different
things. Preserve that distinction in every report.

## Sequence and gates

| Stage | Hardware and run | Acceptance before advancing |
| --- | --- | --- |
| A. Software | Host C++ tests; production, bench and display-enabled AVR builds | Current sources pass; identify remaining model limitations |
| B. Bare Arduino | USB only; `phase1-test.py --mode usb` without `--standin` | Correct device/build identity; saves survive watchdog reset; original setting restored |
| C. Passive observation | Meter, Rigol, Saleae; no stimulus board initially | Correct supply/output levels; idle D9 midpoint PWM; no D8 assertion during observed startup/reset |
| D. Repeatable inputs | Qualified F767ZI fixture and four dividers; `--mode wired` | PTT/bypass/latching, waveform and watchdog checks pass; independent captures show no extra pulses |
| E. Stress and recovery | Same fixture, then identified actual encoder/LCD | Timing holds during activity/faults; startup interlock and durable settings survive applicable resets/power interruptions |
| F. Final firmware | Production build with actual display configuration | Physical behavior repeated without bench commands; standalone USB power with no serial host works |
| G. Solution integration | Carrier power, transistor/load, filter, controls, then microphone/radio | Electrical, audio and radio checks in assembly guide pass |

If the current, identified build has already passed a stage under the same
setup, retain that evidence and skip repeating it unless a relevant change
invalidates it. The November 2 USB results are historical, not a new live test.
Stage C adds measurement probes; stage D adds the fixture. Neither requires
connecting the solution's electronic components.

## Equipment roles

| Bench item supplied by user | Intended use |
| --- | --- |
| NUCLEO-F767ZI | Existing open-drain input stimulus, PWM capture and output observer; use its checked-in Release firmware |
| Saleae Logic 8 | Independent simultaneous record of PTT stimulus, PTT command, PWM, both LED commands and bypass; later encoder/button or I²C |
| Rigol DS1202Z-E | Analog pin levels/edges, supply startup, PWM details, reset release and later reconstructed audio |
| XDM125 multimeter | VCC, idle/high output and fixture-divider voltage checks; identify exact reported model before automation (inventory lists XDM1251) |
| KA3005P | Later controlled power/power-cycle work after a single power path is established; unused during USB-only bring-up |
| NUCLEO-H743ZI2 | Reserve for a specific independent stimulus/observer need; no H743 test firmware is currently delivered |

Windows discovery on November 13 found the Saleae and Rigol USB devices and
the supply's matching serial USB identity. A read-only Rigol query returned
DS1202Z-E, firmware 00.06.04. No Arduino or ST-Link serial device was present
at that check. Presence is not a DUT measurement. No supply commands were sent.

The Saleae uses Logic 2 automation on this workstation; the installed sigrok
path does not acquire this Logic 8 model. Retain native `.sal` plus raw CSV.
For the Rigol retain waveform data, scaling preamble, settings and an explanatory
view. Project-owned automation must accompany any new recurring measurement
before it is handed off as a human-run automated procedure. Existing inventory
helpers establish workstation connectivity, not Arduino acceptance.

## A. Software evidence

Run [test-firmware.ps1](../../tools/test-firmware.ps1) in a configured C++
developer shell; [build-firmware.ps1](../../tools/build-firmware.ps1) builds
without programming. Commands and tool versions are in the
[firmware README](../../firmware/README.md).

Current checks include:

- Control/interlock/debounce/rollover and UI tests, all 50 presets, 2,816 modeled
  torn-write cases and single-bit record corruption.
- All 65,536 numerical inputs for range validation, all 10,000 manual editor
  values, all 1,872 allowed values through pending-save/bypass/TX latching, and
  all 65,536 eight-event microphone/bypass sequences after reset.
- Execution of the actual `tone.cpp` ISR and setter against a host register
  model at all 1,872 settings. Check nominal-clock frequency, duty bounds,
  midpoint idle, bounded attack, completed release, timer configuration fault
  detection and stop behavior. The model does not simulate AVR execution time,
  interrupt priorities, atomicity, timer buffering, USB or physical clock error.
- Independent synthetic tests of the F767ZI PWM estimator, including missed
  edges and timer rollover; display transaction/fault/recovery model tests.
- Actual sketch integration: the unchanged `.ino` setup/loop, control, tone ISR,
  asynchronous storage service and display driver execute together against host
  GPIO/USB/EEPROM/Wire models. Nine executions cover normal/held/bypass/both-held
  startup, millis wrap, unavailable LCD, no serial host at startup, EEPROM
  readback failure and a separate display-disabled build. PTT/bypass inputs are
  simulated at `digitalRead`; assertions check real loop output writes, modeled
  PWM, durable/pending settings, rejected concurrent saves, display loss/recovery,
  suppressed invisible gestures, USB backpressure/absence, timer fault and
  active-PTT release/no-watchdog-feed during the upload request.

This integration harness separates stimulus from logic without adding a USB
keying override or alternate PTT control path to the deployed firmware. Later
NUCLEO stimulus exercises the existing physical input path; it does not require
rewriting the control state machine. The model advances time in 100 µs steps
and completes modeled EEPROM writes after 3.4 ms. Those are model choices,
not instruction/interrupt timing, EEPROM electrical qualification or pin latency.
Bootloader/reset behavior remains a physical test. Display NACK/offline state is
discovered on an attempted transaction; unchanged content does not create a
continuous display-presence heartbeat.

An AVR build checks compilation/linking and static memory use, not worst-case
stack use or interrupt deadline compliance. Physical captures under load must
cover those effects. Host journal tests do not execute the EEPROM peripheral's
byte-launch sequence or qualify brownout behavior.

## B–D. First bench session

1. Connect only the Arduino USB data cable and rediscover its port. Confirm
   `STATUS` identity and released PTT. Record board identity and the image/hash
   actually programmed; do not infer flash contents from matching source files.
2. Use the phase-one guide to build/program if needed, then run:

   ```powershell
   python tools/phase1-test.py --pro COM_PORT --mode usb --output .agent-scratch/firmware/usb-current.json
   ```

   Replace `COM_PORT` with the discovered port. This temporarily saves four
   settings and intentionally resets the bench firmware; it restores the original
   setting. It needs `bench=1`, not a production image. Keep signal wires absent.
3. Before attaching probes, agree the lead/channel map. With power off attach
   common ground and securely accessible probes. For startup observation, provide
   the phase-one fixture's defined pull-down/sense load on D8: an unloaded
   high-impedance reset pin is not proof of a driven HIGH or LOW. Scope ground
   goes to common GND. Do not attach the supply to USB-powered VCC/RAW.
4. Check VCC and D8/A1 idle levels; inspect D9 for nominal 10 kHz, approximately
   50% idle duty. Save startup/reset observations with the trigger and prehistory
   showing the event. USB enumeration timing is not PTT timing.
5. With both boards unpowered, assemble the
   [illustrated fixture](firmware-phase1-guide.md#2-wire-with-both-usb-cables-unplugged).
   Follow its resistance/continuity, power-order and divided-level acceptance
   before `ARM` or a wired run. Use the F767ZI pin map exactly; H743 connectors
   are not substitutes. Do not join board power rails.
6. Run the existing wired runner. Its low/middle/high checks are the initial
   gate, not the entire campaign below. It polls some outputs and can miss
   short glitches; simultaneous retained Saleae records supply that evidence.
7. Finish with `STOP`, verify `armed=0 drive=0`, restore original tone, remove
   stimulus wires before powering boards down. If the host stops, use `STOP`
   and verify release; the fixture also has an arm lease/watchdog. Retain failures.

## D–F. Extended acceptance matrix

The repeat counts/windows below are selected campaign defaults, not previously
measured results. Add automation in bounded batches as each acquisition path is
qualified. Do not run USB-only fixture mode once its drive wires are attached.

| Check | Procedure and evidence | Required result |
| --- | --- | --- |
| Frequency coverage | All 50 presets physically, plus non-preset 67.1, 100.1, 151.5 and 254.0 Hz; at least 3 s valid PWM record per setting after settling; repeat endpoints/midrange after warm-up | Encoded frequency within ±0.1 Hz, no capture errors; reconstructed audio acceptance follows at stage G |
| Time reference | Compare NUCLEO estimates with independent Saleae/scope records; record each timebase specification/calibration status and estimator/window uncertainty | Require `abs(error) + uncertainty <= 0.1 Hz` for an unambiguous pass; boundary overlap is inconclusive; do not average away oscillator error |
| PTT timing | Initially 20 press/release pairs; then 1,000 pairs in bounded batches, distributed across normal/bypass and background loads | Each stable press/release acted on within 25 ms; D8/A1 agree; no extra pulses; retain worst case |
| Bypass timing | Toggle while keyed, including a different saved pending tone; capture bypass, A2, D8 and D9 | Change within 25 ms; D8 never drops; midpoint while bypassed; same latched tone resumes; pending value applies after release |
| Contact bounce | Existing 1 ms bounce pattern plus varied short pulse trains and just-below/at/above 5 ms stable intervals | Reject subqualification disturbances; respond to stable final state within 25 ms; inspect every unintended intermediate output transition |
| Background load | Repeat timing during repeated STATUS traffic, a stalled host reader, malformed/overlong commands, settings writes and later normal LCD/UI activity | No unintended keying, missed carrier periods, timing violation or loss of durable saved selection; recovery to valid commands |
| Watchdog | Key then HANG on bench build, both bypass states; capture D7/D8/D9 and maintain fixture lease | D8 release within 1 s; no rekey while held; release then new press required; saved tone intact |
| Startup/reset/upload | Ten cold starts and ten resets per held/released PTT × bypass state; observe ordinary upload and USB connect/disconnect separately | No unintended D8 assertion; held input cannot key until release/new press; no need for an open serial terminal |
| Persistence | Save endpoints/non-presets, reset/power-cycle; confirm same-value save does not create a new write using implementation/electrical evidence as available | Last completed valid save restored; missing/corrupt records fall back to 151.4 Hz; interlock remains active |
| Interrupted save | First establish board power path, bootloader/fuse/BOD behavior and safe reset conditions; interrupt real writes at swept delays in a dedicated test | Prior valid value or complete new value only; maintain separate evidence from modeled torn bytes; do not use USB-connected supply cycling as a power cut |
| Real UI | Identify LCD address/mapping and encoder; all presets, each manual digit, range errors, Cancel, short/750 ms long press, browsing during TX | Matches FN-01/09/11/14; no browsing writes; no long+short double action; normal changed content within 200 ms |
| Display faults | Identified display build; unplug/NACK and held-low SCL/SDA faults during RX/TX, bypass and pending save; restore | PTT/tone/latch continue correctly; no invisible edits; recovery home without unconfirmed save or rekey |
| Soak | Selected one-hour mixed activity run after shorter checks pass; periodic saves without continuous EEPROM wear; retain counters and trace windows | No resets/faults, stuck output, capture loss or out-of-budget event in observed windows; unobserved intervals are not glitch-free evidence |
| Production regression | Flash verified final production/display configuration; repeat startup, pin timing, bypass/latching through UI, unplugged serial host and display faults | Same required operating behavior; SAVE/HANG absent; record exact final image and configuration |

Use a selected starting rate of **25 MS/s digital** for the six main Saleae
signals (PTT input, bypass input, D8, D9, A1, A2); use the qualified fixture's
divided sense nodes for outputs. Confirm actual supported settings and voltage
range before capture. At this rate one sample is nominally 40 ns; that is
resolution, not absolute timebase accuracy. Long stress captures may use lower
rates for event timing, with separate high-rate PWM records. Document which
claim each record supports; ensure storage and acquisition completeness.

Keep latency referenced to the observed stable input edge, including debounce.
For watchdog release, reference an observed stimulus/marker and document the
uncertainty in when the firmware actually entered HANG. Host command timing
alone is a conservative bound only when its transport/order is established.

## G. Integration boundary

Follow [assembly and bring-up](assembly-and-bring-up.md) after the bare-Arduino
gate. Add the actual power path, then Q1 with a suitable dummy PTT load, then
the reconstruction filter, identified display/encoder, and microphone/radio.
At each addition repeat the affected digital regressions. Use the supply only
with a documented current limit and one established power path; capture rails
and D8 during power changes. No automated brownout sweep is authorized by a
generic instrument-connectivity check.

Measure filtered frequency, amplitude versus tone, distortion, idle carrier,
keying clicks, PTT sink/load behavior and microphone interaction. Agree numerical
analog/deviation limits against the intended radio before calling integration
accepted; digital firmware tests cannot establish them. Radio deviation and
actual repeater operation remain distinct from dummy-load tests.

## Records and disposition

Use fresh scratch run directories. Promote accepted current-revision evidence
to `docs/verification/firmware-phase1/` with a concise readable result, raw-data
location, source and flashed-image hashes, versions, exact wiring/channel map,
probe/threshold/rate/trigger settings, stimulus, expected/observed values,
uncertainty and cleanup readback. Retain failing attempts and their disposition.
For large native captures, document retained local paths if they are not stored
in Git. Never put a final required dependency solely in scratch.

Classify each criterion as **pass**, **fail**, **inconclusive** or **not run**.
Missing/partial captures cannot pass. A source/model defect is fixed and its
affected checks repeated; a fixture/instrument failure calls for setup repair,
not relaxed DUT limits. Record physical acceptance separately from offline
test-tool verification.

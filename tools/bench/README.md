# Firmware bench tools

The project-local `rigol_scope.py` is adapted from the workstation inventory's
tested DS1202Z-E helper (`tooling/rigol-ds1202z-e-digital-oscilloscope/scope_control.py`).
It is included here so project verification does not depend on that private
checkout. Its docstring points here. The project adds a tested state-preservation
fix: avoid reissuing STOP to an already stopped single acquisition, which changes
SING to AUTO on this firmware. No inventory records or workstation configuration
are modified.

## Set up

From the repository root, use Python 3.12:

```powershell
python -m venv .agent-scratch/firmware/bench-venv
.agent-scratch/firmware/bench-venv/Scripts/python.exe -m pip install -r tools/bench/requirements.txt
```

The November 13 hardware run used the already-installed inventory Python 3.12
environment with the pinned PyVISA/PyUSB packages. The Rigol uses its existing
WinUSB driver, USB VID 1AB1/PID 0517, model DS1202Z-E firmware 00.06.04. The helper
requires exactly one matching USB device and checks the returned model. Close
other VISA/sigrok/scope clients; it uses an advisory Windows ownership lock.
Do not replace a working USB driver as part of a routine run.

## Idle PWM

1. USB-power the identified 5 V / 16 MHz Pro Micro, idle with PTT released.
   Leave signal inputs disconnected. Keep RAW and the bench supply disconnected.
2. With Arduino USB unplugged, connect physical ×10 CH1 probe tip to **D9** and
   ground clip to **GND**, then reconnect USB. Both probe attenuation and channel
   attenuation must be ×10. Do not connect scope ground to a signal or VCC.
3. Do not run while changing wires or during another acquisition you need to
   preserve. The tool replaces the acquisition buffer. It refuses an already
   armed single acquisition and restores relevant settings, not old samples.
4. Run with a fresh destination:

   ```powershell
   .agent-scratch/firmware/bench-venv/Scripts/python.exe tools/check-idle-pwm.py --output .agent-scratch/firmware/idle-pwm-RUN_ID
   ```

   Replace RUN_ID. This sets CH1 ×10, 1 V/div, offset −2.5 V, DC coupling,
   2 ms/div, normal acquisition, CH1 rising trigger at 2.5 V and 1.2 Mpoint memory.
   It disables CH2. Channel changes must settle before memory selection;
   readback enforces the requested depth. Expect roughly 10–20 seconds including
   settings/transfer/restoration. No Arduino or supply command is sent.
5. Accept only exit 0 plus `result.json` with `passed=true` and
   `settings_restored=true`, and `capture/capture.json` with `restored=true`.
   Raw BYTE samples, preamble, before/after settings, SHA-256 and screenshot
   remain in the run directory. The screenshot is taken after the raw capture
   helper has resumed acquisition; it is explanatory, not the exact raw buffer.

Selected coarse screening limits are carrier 10 kHz ±1%, every measured period
98–102 µs, every measured duty 48–52%, LOW plateau −0.3–0.5 V and HIGH plateau
4–5.5 V, no ADC clipping, at least 100 complete cycles and sample spacing ≤1 µs.
Plateaus use the 10th/90th percentile codes, not overshoot extrema. These limits
are for bare-module idle screening, not calibrated timing/voltage limits or
proof of supply voltage, edge quality, modulated tone accuracy or safety.
Inspect the waveform and measure VCC separately when the plateau is unexpected.
The November 13 user's VCC reading was approximately 4.38 V. The recorded
coarse PWM pass therefore does not qualify the 16 MHz MCU supply envelope:
Microchip specifies at least 4.5 V at 16 MHz. The user explicitly authorized
continuing at the measured low rail, accepting possible rework. Conditional
bench testing continues; correct the supply and repeat affected physical checks
before claiming nominal-supply acceptance.

The November 13 accepted run returned 1,200,000 points at 40 ns/sample (48 ms).
Memory length is derived from actual preamble, not the visible time span. A
two-level midpoint threshold gives rising/falling edges; whole-period averages
give frequency. Absolute timebase accuracy remains a separate input. The
display and plotted traces are not a claim about every event outside this window.

Nonzero exit means DUT screening failed or acquisition was inconclusive; inspect
`result.json` and retained raw files. Do not silently retry into the same directory.
On interruption/transport loss, reconnect exclusively, query status, restore the
recorded settings explicitly (RUN before memory-depth changes), then restore
original trigger sweep and run/stop state. Verify readback. Do not reset the
scope or automatically clear diagnostics. Failed November 13 attempts identified
the asynchronous channel/depth dependency; one explicit `*CLS` recovery was
recorded after an error-query timeout. The corrected tool does not auto-clear it.

## USB protocol robustness

```powershell
.agent-scratch/firmware/bench-venv/Scripts/python.exe tools/usb-diagnostics-test.py --pro COM_PORT --output .agent-scratch/firmware/usb-robustness-RUN_ID.json
```

Replace the explicit discovered Arduino port and RUN_ID. Requires bench=1,
idle healthy firmware, exclusive serial ownership and signal inputs disconnected;
passive probes may remain. It rejects malformed/overlong commands, checks
fragmentation/CRLF, executes 200 STATUS commands and a 16-command burst with a
0.5 s stalled reader. It issues no valid SAVE/HANG/reset/flash command. A new
JSON report is required; exit 0 and `passed=true` indicate USB state/recovery
acceptance, not electrical timing. No physical cleanup is required beyond
closing the port; verify the reported final state. Hardware path passed on
COM14 on November 13.

## Offline checks

```powershell
python tools/bench/test_idle_pwm.py -v
```

Seven tests cover accepted data, wrong frequency/duty/level, clipping, static
input and incomplete data. They never connect to an instrument. They qualify
the evaluator, separately from the retained real Arduino measurements.

## Concurrent USB and PWM

Add `--pro-stress COM_PORT` to the idle-PWM command. This opens the explicitly
selected Arduino port, confirms healthy idle bench firmware, continuously requests
STATUS during the complete scope capture call, then closes the port. It sends
no saves, resets or stimulus. The worker has a 20 s budget and 2 s reply timeout;
it requires at least ten unchanged replies. Counts/raw replies and host overlap
timestamps are recorded in `result.json`. November 13 hardware execution passed
with 541 replies. The scope record is a finite window inside that traffic interval.

## Minimal NUCLEO-driven tone sequence

This mode uses the already-programmed F767ZI Release fixture. Do not substitute
an H743 board/pinout. No radio, RAW supply, LCD or encoder is connected.
For exact connector orientation consult the
[illustrated full fixture](../../docs/implementation/firmware-phase1-guide.md#2-wire-with-both-usb-cables-unplugged).
The minimal variant needs two 1 kΩ series resistors, two 10 kΩ pull-ups and
jumpers. Workshop inventory lists ten Vishay MRS16000C1001FCT00 1 kΩ resistors
and thirty MRS16000C1002FCT00 10 kΩ resistors; this setup uses two of each.

With **both USB cables unplugged**, connect:

| F767ZI contact | Connection | Arduino contact |
| --- | --- | --- |
| GND, CN10 pin 5 | Direct common ground | GND |
| PF12 / NUCLEO D8, CN7 pin 20 | Through 1 kΩ | Arduino D7 / PTT input |
| PF13 / NUCLEO D7, CN10 pin 2 | Through 1 kΩ | Arduino D10 / bypass input |

For each of the two Arduino input nodes:

```text
NUCLEO open-drain pin ---- 1 kΩ ----+---- Arduino input
                                  |
                                10 kΩ
                                  |
                              Arduino VCC
```

The pull-ups go to **Arduino VCC**, never a NUCLEO power rail. Leave Arduino
D8 and all other outputs disconnected except D9→scope CH1. Check common-ground
continuity and resistor values while unpowered. Connect NUCLEO USB first, then
Arduino USB with the fixture stopped/released. Do not add a manual PTT jumper.
These pins sink LOW or release; a push-pull 3.3 V HIGH is not the intended interface.
Keep both boards powered while the drive wires are attached.

After wiring confirmation, use the project venv:

```powershell
.agent-scratch/firmware/bench-venv/Scripts/python.exe tools/nucleo-tone-test.py --pro COM_PORT --standin FIXTURE_PORT --output .agent-scratch/firmware/nucleo-tone-RUN_ID
```

The orchestrator verifies both identities, releases all inputs, remembers the
saved tone, and tests 151.4 Hz, bypass midpoint, a pending 100.0 Hz save while
keyed, resumption of latched 151.4 Hz, and a fresh transmission at 100.0 Hz.
It refreshes the fixture's five-second lease throughout each scope subprocess.
Expect several minutes for three long tone captures plus one idle capture.
It issues STOP/readback and restores the original tone on handled completion
or failure. New output directories prevent overwriting prior evidence.

Tone mode (`check-idle-pwm.py --tone-hz VALUE`) selects 0.5 s/div and 12 Mpoints,
requiring at least 3 s at ≥1 MS/s. It derives tone frequency from interpolated
midpoint crossings of measured PWM duty, with hysteretic rearm. It checks the
encoded tone against ±0.1 Hz on the nominal scope timebase, carrier continuity
and duty modulation. Scope calibration/timebase uncertainty and reconstruction
filter/radio behavior remain separate. `--tone-hz` and `--pro-stress` cannot be
combined in this revision. Run `python tools/bench/test_tone_measurement.py -v`
for six offline tests (three good frequencies plus wrong/missing/static/weak/
incomplete waveform cases).

The minimal fixture has **no independent D8/LED feedback**. USB tx/bypass state
and scope PWM checks must not be reported as electrical PTT latency, LED or
reset-release acceptance. Add the full four-divider feedback fixture for those.
Do not run the earlier USB-only fixture tests with these drive wires attached.
The November 13 minimal-fixture sequence passed on actual hardware, together
with endpoint measurements and held-PTT watchdog checks. See
[retained results](../../docs/verification/firmware-phase1/2026-11-13/nucleo-minimal/README.md).
Add `--tones 670 2541` for an endpoint-only sweep (tenths of Hz), or use
`--held-reset` for physical PTT held through watchdog recovery in both bypass
states. These modes cannot be combined. Held-reset mode requires observed USB
disappearance/recovery, checks unarmed/released command state while the physical
input remains held, captures midpoint D9 PWM, then verifies release/new-press
rearm. It maintains the fixture lease throughout. Its USB recovery times do
not measure electrical D8 release. Original setting and released inputs are
restored on handled completion/failure.

If interrupted, STOP the F767 and verify `armed=0 drive=0`; confirm Arduino
`tx=0` and restore the recorded original tone. On a killed scope subprocess,
restore its recorded settings using the recovery procedure above. Host loss
should expire the fixture lease; the independent fixture watchdog releases
outputs on a fixture stall. Neither substitutes for checking the final state.
Remove drive wires before powering down the NUCLEO.

## Offline sketch integration and deferred recovery tests

`tools/test-firmware.ps1` now runs the real Arduino sketch setup/loop and actual
control, tone, storage and display modules against host hardware models. It
requires no connected devices. The host test build uses C++14 for the Windows
STL; the AVR build remains unchanged. Run from a Visual Studio developer shell:

```powershell
./tools/test-firmware.ps1 -Compiler cl
```

The sketch model removes AVR section/naked attributes, substitutes GPIO/USB/
EEPROM/Wire hardware and uses the existing fake single-threaded atomic/PROGMEM
interfaces. It advances time in 100 µs steps and completes each modeled EEPROM
byte after 3.4 ms. Narrow AVR-address pointer casts and host-vs-AVR printf type
differences have narrowly scoped warning allowances; these do not change the
deployed source. Native adapter warnings otherwise remain errors. No instruction
timing, interrupt scheduling, real watchdog reset, bootloader, electrical levels
or peripheral programming-timing qualification follows from a pass.

Nine executions cover normal, held PTT, bypass, both held, timer wrap, missing
display, standalone/no serial host startup, EEPROM readback corruption, and a
separate display-disabled build. The actual loop must forward PTT, reject brief
input glitches, preserve PTT during bypass, retain a transmission's frequency
through pending saves, reject concurrent saves, avoid same-value EEPROM writes,
continue across display failure and stalled/absent USB, stop on timer faults,
and release active PTT/stop watchdog feeds for a 1200-baud upload request.
The display model detects NACK on an attempted transaction; there is no claim
of an immediate electrical disconnect heartbeat. Physical stimulus wiring is
deferred at the user's request.

For a later USB-only recovery session, the prepared command is:

```powershell
.agent-scratch/firmware/bench-venv/Scripts/python.exe tools/usb-watchdog-test.py --pro COM_PORT --cycles 5 --output .agent-scratch/firmware/watchdog-RUN_ID.json
```

This requires bench firmware, radio/driven inputs disconnected, and exclusive
Arduino port ownership. It sends HANG up to ten times (five by default), requires
observed USB disappearance and return within bounded waits, and checks saved/
active settings and released PTT state without issuing saves. It does not
measure D8 release time. Reports preserve failures and never overwrite a prior
file. If interrupted after HANG, allow the watchdog/re-enumeration, rediscover
the port and query STATUS; no persistent drive or changed setting is intended.
The November 13 attempted repeated run could not start because the Arduino
was no longer enumerating; **this new repeated hardware path is unqualified**.
Four offline mocked verdict tests pass, including rejection when disappearance
is unobserved, settings change, or the device is absent:

```powershell
python tools/bench/test_usb_watchdog.py -v
```

## Physical D7/D8 timing

Use `check-ptt-timing.py` with the minimal F767 drive fixture and **CH1=D7,
CH2=D8**, both probes physically/channel-configured ×10, both grounds Arduino
GND. Keep radio and external supply disconnected. Change probe connections with
Arduino USB unplugged first, then NUCLEO USB; reconnect NUCLEO first. Close
other serial/scope clients. This tool replaces the scope buffer and restores
changed settings with readback; it refuses an already armed single acquisition.

```powershell
.agent-scratch/firmware/bench-venv/Scripts/python.exe tools/check-ptt-timing.py --pro COM_PORT --standin FIXTURE_PORT --pairs 3 --output NEW_DIRECTORY
```

It captures press/release in both bypass states, 0.8 s after arming. Settings:
dual channels at 1 V/div, offset −2.5 V, DC coupling, 10 ms/div, 600 kpoints,
normal acquisition, CH1 edge trigger at 2 V. Actual successful records are
120 ms at 200 ns/sample. Both channels are read from the same stopped buffer.
Exactly one output edge is required, with no extra pulses and delay 0–25 ms.
The threshold is each channel's measured LOW/HIGH midpoint. Data, metadata,
raw logs and result JSON are retained in a new directory. Accept exit 0 only
with `passed=true`, `scope_restored=true`, and released cleanup states.

`--save-before-edge` alternates settings and confirms save busy immediately
before each stimulus; it restores the original setting afterward. `--bounce`
uses eight 1 ms toggles and measures from the final stable edge, requiring one
output transition; it may be combined with save-active testing. Pair count is
1–20 per bypass state. The actual bounds and finite tested counts are in the
[physical results](../../docs/verification/firmware-phase1/2026-11-13/ptt-electrical/README.md).

`--watchdog` is a separate mode. It uses 0.5 s/div, CH2 falling trigger and a
3.5 s pretrigger-fill wait with fixture keepalive. A captured short D7 marker
finishes before HANG is sent. Marker→D8 LOW is therefore a conservative release
upper bound, accepted only within 1 s, with no rekey while held. The 6 s paired
records sample at 10 µs; USB disappearance/recovery and release/new-press rearm
are checked separately. This is not an exact timestamp for executing HANG.

Handled exits STOP/read back the fixture and verify Arduino released state;
save-active mode restores the initial tone. After interruption, send STOP and
verify armed=0/drive=0, allow Arduino USB recovery and verify tx=0. An interrupted
scope transfer needs explicit restoration from recorded `scope_before`; closing
ports does not restore settings. Do not treat a timeout or partial channel as
DUT acceptance. The user's low-supply limitation remains in force.

Offline evaluator and run-state tests (no instruments accessed):

```powershell
python tools/bench/test_ptt_measurement.py -v
python tools/bench/test_watchdog_measurement.py -v
python tools/bench/test_scope_run_state.py -v
```

## Mixed UI and PTT stress

[check-ui-ptt-stress.py](../check-ui-ptt-stress.py) uses the original five fixture
drives, a Grove V4 display, CH1=D7 and CH2=D8 at ×10, with common ground and no
radio/bench supply. Encoder A must be on D4, not reassigned to SCL. Begin at the
freshly reset home screen, with the default Presets menu selection. Merely
returning home from a prior UI session does not reset its remembered menu item.

```powershell
.agent-scratch/firmware/bench-venv/Scripts/python.exe tools/check-ui-ptt-stress.py --pro COM_PORT --standin FIXTURE_PORT --batches 10 --output NEW_DIRECTORY
```

Ten batches produce 80 press/release pairs, 80 accepted forward detents and two
background saves during held TX. Bypass alternates by batch. Editing is gated
while EEPROM is busy; the runner waits for save completion before counted
rotation. It checks the latched active tone during saves, then saves the browsed
preset through a physical button gesture and compares it with the independently
counted preset index. This temporarily writes settings; original saved tone is
restored through bench SAVE, inputs released and scope settings restored.
Home is expected after successful UI cleanup; failures may leave a different
screen, so reset before another run. No cold power cycle is performed.

Each batch retains paired 600 kpoint channels at 10 µs/sample over six seconds.
Three seconds of prehistory are filled before the first real D7 trigger. All
eight pairs must fit the posttrigger record and leave at least 50 ms afterward.
The evaluator uses a physical 2 V threshold and checks every edge, with a 25 ms
limit and no extra output pulses. Sample resolution is 20 µs for an edge-pair
bound, not absolute timebase calibration. D9, LEDs and actual I²C waveforms are
not observed. Ten records establish 60 seconds of captured windows, not
continuous glitch-free evidence across transfers or a one-hour soak.

Offline evaluator: `python tools/bench/test_ptt_stress_measurement.py -v`.
On interruption STOP the fixture/read back armed=0/drive=0, restore original tone,
check idle/display/fault status and restore scope from `scope_before`. A timeout,
missing edge, extra pulse, count mismatch or incomplete cleanup cannot pass.

## Display bus fault qualification

For the subsequent Grove bus-fault campaign, follow the
[illustrated display fault procedure](../../docs/implementation/display-bus-fault-test.md).
It temporarily reassigns encoder A to SCL through the existing 1 kΩ and uses
the XDM1251 read-only DCV helper to qualify released/clamped/released voltage.
`qualify-display-clamp.py` must pass before `check-ptt-timing.py --display-fault
--fault-qualification RESULT_JSON` may be used. Do not use ordinary encoder
gestures while that drive is connected to SCL. Restore the endpoint to D4 before
using `exercise-ui-input.py` again. The seven offline qualifier tests are
`python tools/bench/test_display_clamp.py -v`; they never open hardware.

`bench/xdm1251.py` is the project-owned copy of the already-qualified read-only
inventory helper (`tooling/owon-xdm1251-digital-multimeter/serial_control.py`).
It identifies exact model/firmware and checks DCV/math state. Its query rate is
not the displayed conversion rate; mode/range/rate are never changed by it.
The fault test's electrical limits and settling policy belong to the project
qualifier, not to the generic meter helper.

## Physical D10/D9 bypass timing

Production builds are supported with 151.4 Hz already selected through the UI;
ordinary PTT/bypass timing sends no bench commands. `--save-before-edge` and
PTT `--watchdog` remain bench-only, with offline production guards covering
their rejection. Bypass `--serial-closed` requires production and closes the
Arduino port before keying and throughout captures, reopening only for cleanup.
USB remains connected; do not interpret this as data-host electrical removal.

For a long measurement of the already selected tone on production firmware,
use `nucleo-tone-test.py --current-only --scope-channel 2` when D9 is on CH2.
It sends no SAVE/HANG, closes Arduino serial during capture, refreshes the
NUCLEO lease and verifies released/unchanged state afterward. The scope child
`check-idle-pwm.py --channel 2 --tone-hz FREQUENCY` does not drive inputs itself;
use the parent to hold PTT safely. See the
[qualified production procedure](../../docs/verification/firmware-phase1/2026-11-13/grove-ui/production/README.md).

Use `check-bypass-timing.py` with **CH1=D10, CH2=D9**, both ×10 probes with
grounds on Arduino GND, and the unchanged minimal F767 input-drive fixture.
Keep radio and bench supply disconnected. Move probes with both boards unpowered
(Arduino unplugged first); reconnect NUCLEO first. This setup differs from the
D7/D8 PTT timing command above.

```powershell
.agent-scratch/firmware/bench-venv/Scripts/python.exe tools/check-bypass-timing.py --pro COM_PORT --standin FIXTURE_PORT --pairs 3 --output NEW_DIRECTORY
```

It temporarily selects/key-latches 151.4 Hz, captures bypass enable/release from
actual input edges, and verifies carrier continuity, midpoint suppression and
modulation return within the 25 ms budget. Midpoint tolerance is ±0.5 duty
percentage point; the additional span metric uses 20–80% duty thresholds, not
exact nominal peak amplitude. These are raw digital PWM checks, excluding the
analog filter/radio. The actual paired records are 600 kpoints/channel at 200 ns,
120 ms, with no forced trigger. `--save-before-edge` confirms save busy before
each stimulus and durable completion afterward. Original tone and released
inputs are restored, along with scope settings. All captures/results are kept
under a new directory; no earlier run is overwritten.

The tool uses the same scope setup/trigger/cleanup strategy as PTT timing.
After interruption, STOP/read back the fixture, verify Arduino tx=0, restore its
recorded original tone, and restore any interrupted scope settings explicitly.
Accept only successful JSON plus cleanup readback. Seven offline tests run with
`python tools/bench/test_bypass_measurement.py -v`. The
[physical result and definitions](../../docs/verification/firmware-phase1/2026-11-13/bypass-electrical/README.md)
identify the tested envelope and remaining gates.

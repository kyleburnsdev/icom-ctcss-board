# Grove display-bus fault test

This temporarily reuses the F767 encoder-A open-drain drive as an SCL clamp.
The Grove V4 bench image stays installed. No firmware or power-path change is
required. Keep radio and bench supply disconnected. Use the existing breadboard,
1 kΩ series resistor, 10 kΩ input pull-ups, Rigol ×10 probes, XDM1251 and USB
connections. The physical EC11 remains disconnected.

| Stage | Connections / action | Acceptance before next stage |
| --- | --- | --- |
| Prepare, unpowered | Move encoder-A drive endpoint D4→D3; meter red on D3/SCL | Confirm diagram below; other wires unchanged |
| Power fixture | NUCLEO CN1 only; STOP/readback | armed=0, drive=0 |
| Power DUT | Arduino USB | lcd=1, tx=0, fault=0; original tone retained |
| Qualify clamp | Read-only DMM queries; brief ENCA sink | Released SCL 3.5–5.25 V; clamped −0.1–0.8 V; display offline then recovered |
| Test PTT | Retain CH1=D7, CH2=D8; qualified clamp asserted | Physical edges within 25 ms; no extra pulses; saved selection preserved |
| Recover | STOP releases clamp and all contacts | LCD returns online within three seconds; idle healthy status |
| Restore, unpowered | Return clamp endpoint D3→D4 | Encoder emulation restored; keep actual display SCL wire on D3 |

## 1. Prepare the wiring

1. STOP the fixture and verify released inputs. Unplug Arduino USB first,
   then NUCLEO USB. Keep the PSU disconnected.
2. Identify the existing **PF15 / NUCLEO D2, CN10 pin 12 → 1 kΩ → Arduino D4**
   encoder-A drive. Move **only its Arduino endpoint from D4 to D3/SCL**.
   Retain its series resistor. Do not move the display's existing SCL wire.
3. Leave D4's separate 10 kΩ pull-up connected to Arduino VCC; D4 now remains
   HIGH without a fixture drive. Do not move this pull-up to SCL. Leave encoder B,
   button, PTT and bypass wiring unchanged.
4. Keep Rigol CH1=D7 and CH2=D8, physical/channel ×10, grounds Arduino GND.
5. Meter: black lead COM, red lead voltage/ohms jack, DC volts and math/relative
   off. Black tip Arduino GND, red tip Arduino D3/SCL. Secure both tips; keep
   the red tip away from adjacent D2 and power contacts. No resistance mode.

Schematic view; Arduino D3 and NUCLEO D2 are labels on different boards:

```text
Grove SCL --------------------+---- Arduino D3 / SCL
                              |
NUCLEO PF15 / D2 --- 1 kΩ -----+---- Meter red (voltage jack)
      CN10 pin 12

Arduino VCC ------- 10 kΩ ---------- Arduino D4 (no drive attached)

Arduino GND ----------------------- Meter black (COM)
     |
NUCLEO GND -------- Grove GND ------- Scope grounds

Unchanged: CH1 tip -> Arduino D7, CH2 tip -> Arduino D8
```

6. Reconnect **only NUCLEO CN1 USB**. Verify identity/STOP/status before Arduino
   power. Then reconnect Arduino USB and require healthy idle lcd=1 status.

## 2. Qualify SCL electrically

Use the existing [bench requirements](../../tools/bench/requirements.txt), exclusive
ownership of each port, and a new output directory. Rediscover device identities;
the previously observed ports were Arduino COM14, ST-Link COM5, XDM1251 COM15.

```powershell
.agent-scratch/firmware/bench-venv/Scripts/python.exe tools/qualify-display-clamp.py --pro COM14 --standin COM5 --meter COM15 --output NEW_CLAMP_DIRECTORY
```

The tool never changes meter mode/range/math/rate. It checks exact OWON XDM1251
firmware V1.0.1.0.4 and existing DCV mode, then reads released/clamped/released
levels. It allows 1.5 s settling and retains three displayed-value polls per
state; those are not independent conversions or edge timing. The fixture lease
is refreshed while clamped. Toggling bypass forces a changed display frame,
so an unchanged home screen cannot hide the fault from the transaction-driven
driver. The clamp must hold the bus LOW and take the driver offline while PTT
stays released and saved tone is preserved. Release must restore SCL HIGH and
the display online. Read the entire report; accept only exit zero and passed=true.

The 1 kΩ resistor bounds current to approximately 5.25 mA if the bus were held
at 5.25 V by a strong source (calculated, ignoring GPIO drop). The actual bus
pull-up resistance is not established by the available Grove documentation.
The measured LOW gate above qualifies the actual setup; a failure stops the
dependent test rather than silently accepting an ineffective fault. This does
not qualify LOW voltage at every instant; a scope bus capture can add that.

## 3. Measure PTT under the qualified fault

```powershell
.agent-scratch/firmware/bench-venv/Scripts/python.exe tools/check-ptt-timing.py --pro COM14 --standin COM5 --pairs 3 --display-fault --fault-qualification NEW_CLAMP_DIRECTORY/result.json --output NEW_FAULT_PTT_DIRECTORY
```

The report must come from this wiring session. The tool asserts ENCA as SCL
clamp, forces display traffic and confirms lcd=0 before running both bypass
states. It sends short/long/short button gestures while offline and requires
no durable setting change. Encoder A is reassigned, so this setup does **not**
claim a physical full-detent invisible-rotation test. No gesture-based save
is intended. Existing `--save-before-edge` and `--bounce` may be selected in
separate runs after baseline passes. Do not combine with watchdog mode.

The scope retains actual D7→D8 timing including qualification, with paired
600,000-point records at 200 ns/sample, 120 ms. Exactly one D8 transition is
required, within 25 ms of the stable input edge. Encoder A's drive bit must
remain asserted through acquisition. PTT output is scope-loaded; D9 tone
continuity and loaded radio behavior are not observed in this connection map.

## 4. Recover and restore

Normal cleanup STOPs the fixture, checks armed=0/drive=0, restores original tone
if save mode was used, requires lcd=1 within three seconds, and restores scope
settings/run state. Its former acquisition buffer is replaced. Confirm the
visible home screen after recovery; an online I²C response alone cannot prove
correct LCD pixels.

On interruption, send STOP and verify armed=0/drive=0; the five-second arm lease
also releases the fixture after host loss. Check Arduino tx=0, bypass=0, busy=0,
fault=0, lcd=1 and original saved tone. Restore scope from the retained
`scope_before` report if acquisition was interrupted. Preserve failures.

To restore encoder A, unplug Arduino first, then NUCLEO. Move only the added
clamp's Arduino endpoint from D3 back to D4, retaining its 1 kΩ. Leave the Grove
SCL wire on D3 and D4 pull-up in place. Disconnect the meter tips or return them
to the intended voltage measurement points. Power NUCLEO first and verify STOP,
then Arduino. Record actual outcomes in the Grove verification directory;
prepared scripts and offline tests are not physical fault acceptance.

References: [Grove V4 protocol and revision information](https://wiki.seeedstudio.com/Grove-LCD_RGB_Backlight/),
the existing [fixture pin-map procedure](firmware-phase1-guide.md), and the
[current Grove verification record](../verification/firmware-phase1/2026-11-13/grove-ui/README.md).

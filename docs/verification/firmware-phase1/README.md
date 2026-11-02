# Firmware verification — 2026-11-02

**Implemented, built and USB-tested; wired phase-one acceptance is pending.**
The user connected both boards for programming/USB tests and chose to wire
the fixture later. No inter-board signal wires, reconstructed audio, radio,
logic analyzer or oscilloscope were used during these recorded runs.

The [source/build manifest](manifest.json) identifies this uncommitted source
snapshot and build artifacts by SHA-256. [USB results](usb-results.json)
record the actual serial checks and source hashes, and [host-test output](host-tests.txt)
records the native tests. Use the [setup guide](../../implementation/firmware-phase1-guide.md)
to continue. No commit/push was made.

## Checks actually performed

| Check | Result / scope |
| --- | --- |
| PCB pin mapping | Matched U1's exported netlist to fixed firmware pins and SparkFun Pro Micro variant; existing 61 netlist assertions pass; A0 unused |
| Pro Micro bench compile/link | Pass: 11,470 bytes flash, 829 bytes static RAM; 1,731 bytes remain for stack/local use |
| Pro Micro production, display disabled | Pass: 10,536 bytes flash, 764 bytes static RAM |
| Pro Micro production, configured 0x27 PCF8574 display | Pass: 14,256 bytes flash, 1,364 bytes static RAM; 1,196 bytes remain; actual display not identified/tested |
| STM32 Release compile/link | Pass: 17,784 bytes flash, 6,128-byte linker RAM allocation (includes reserved heap/stack) |
| STM32 Debug compile/link | Pass: 28,372 bytes flash, 6,152-byte linker RAM allocation |
| Native control/journal tests | Pass: startup interlock, bypass/TX latch, debounce, millis wrap, gestures, UI bounds/cancel, presets, 2,816 torn-write cases, single-bit corruption |
| Native PWM capture tests | Pass: all 50 presets using the checked-in DDS table, idle midpoint, 32-bit timer wrap, invalid/dropped edges; worst synthetic frequency error 0.004996 Hz |
| Native display transaction model | Pass: startup/home/TX/pending/Cancel text, one transaction per service, NACK/timeout-offline state and recovery; not electrical LCD evidence |
| CubeMX generation/regeneration | Pass: actual 6.16.1 generator + F7 1.17.3; application USER CODE hooks preserved when IWDG added |
| AVR programming | ATmega32U4 signature `0x1e9587`; Caterina reports v1.0; flash write/read verification; normal 1200-baud upload retested |
| STM32 programming | NUCLEO-F767ZI, device ID 0x451, revision Z, 2 MB flash; ST-Link write/read verification |
| Pro Micro USB settings | Saves 67.0, 151.4, 254.1, 100.0 Hz; `busy=0` and saved selection checked; watchdog reset retained 100.0 Hz; original 151.4 Hz restored |
| Pro Micro live scheduling diagnostic | Maximum observed main-loop gap during final USB save sequence: **2,068 µs**; not a pin-edge latency measurement |
| Pro Micro watchdog USB recovery | Device returned and reported saved value; host reconnection about **0.922 s**; not electrical D8 release time |
| NUCLEO USB scheduler | ARM/drive/BOUNCE completed; maximum reported bounce scheduling lateness **3 µs**, without wires; waveform edges not measured |
| NUCLEO host lease | After no commands for 5.2 s, `armed=0 drive=0`; this checks command state, not physical output levels |

The NUCLEO's floating inputs reported `sense=7` and one capture error with no
wiring. Those readings are deliberately excluded from acceptance; the four
divider lower legs establish defined inputs in the wired fixture. A wired
measurement resets capture statistics and must report zero errors.

Arduino `--warnings all` emits four pre-existing unused-parameter warnings
from Arduino AVR 1.8.6 `new.cpp`. Application code compiles without warnings.
Native tests use warnings as errors. STM32 application modules also use
`-Wextra -Werror`; normal generated/HAL sources retain generator flags.

## Changes discovered through validation

- LTO removed an unreferenced early watchdog hook; marking it `used` retained
  it in `.init3`, verified in the linked AVR disassembly and by reset status.
- Arduino's `Serial` boolean conversion adds a 10 ms delay. Replacing it with
  `Serial.dtr()` reduced the observed loop gap from roughly 10.3 ms to 2.060 ms
  in the corrected USB testing (2.068 ms maximum in the final recorded run).
- Feeding the application watchdog prevented the core's 1200-baud upload
  reset. The sketch now releases PTT and withholds feeds during that request;
  ordinary CLI upload works again. The temporary earlier image was recovered
  through its bench hang command and existing Caterina bootloader; no bootloader
  or fuse rewrite was needed.
- The initial CubeMX configuration selected the wrong PLL input implicitly.
  Explicit HSE selection and review of generated initialization established
  the intended 96 MHz clock tree before programming the test driver.

## Pending physical acceptance

1. Assemble/qualify the illustrated fixture, then run `--mode wired`.
2. Measure D8/PTT, bypass and LED latency ≤25 ms, including saves, USB traffic
   and LCD failure; inspect bounce for unintended intermediate pulses.
3. Measure actual PWM carrier and encoded tone ±0.1 Hz at range endpoints and
   midrange with a sufficiently accurate reference. Synthetic capture accuracy
   does not establish either board's oscillator accuracy.
4. Capture held-at-power-up/reset/programming behavior and electrical watchdog
   release within one second, in normal and bypass modes.
5. Identify/install the LCD backpack and encoder, check UI direction/detents,
   750 ms gestures, 200 ms refresh, unplugged/stuck-I²C operation and recovery.
6. Exercise interrupted EEPROM writes with real power removal within the
   permitted supply/BOD operating conditions. Host torn-byte tests are distinct.
7. On the assembled PCB, measure analog reconstruction, idle residue, clicks,
   level/distortion across the range, Q1 load and power behavior; later test
   microphone operation and radio deviation. No numerical analog acceptance
   limit has been invented by these digital tests.

## Reproducibility and retained local work

Tool versions: Arduino CLI 1.3.1; SparkFun AVR 1.1.13; Arduino AVR 1.8.6;
AVR GCC 7.3.0-atmel3.6.1-arduino7; CubeMX 6.16.1 / DB.6.0.161;
CubeF7 1.17.3; xPack Arm GCC 13.2.1-1.1; CMake 3.31.6-msvc6;
Ninja 1.12.1; STM32CubeProgrammer 2.21.0; Python 3.12; pyserial 3.5;
MSVC 19.44.35207 native tests.

The final board state is Pro Micro **bench** build, LCD disabled, saved tone
151.4 Hz, PTT released; NUCLEO Release build, stimuli released/disarmed.
Ports observed: COM10 and COM5 respectively; rediscover them on the next run.

Local build images/toolchain executables needed for the next wired session
remain in `.agent-scratch/firmware/`. The pre-programming NUCLEO flash backup
is retained there as `nucleo-before.bin` for recovery. These are local working
artifacts, not source dependencies or released manufacturing files. Final
evidence is copied here; temporary generator scripts/download archives and
superseded logs are removed. Rebuild commands use installed tools or explicit
paths and do not depend on those temporary generator scripts.

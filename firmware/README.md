# Firmware and radio stand-in

- [Pro Micro sketch](icom_ctcss/icom_ctcss.ino): 5 V / 16 MHz ATmega32U4;
  fixed PCB pins, DDS sine PWM, PTT interlock, bypass, 1602 UI and durable settings.
- [NUCLEO-F767ZI project](radio_standin/radio_standin.ioc): STM32CubeMX/HAL C,
  phase-one open-drain stimulus, PWM capture, PTT/LED observation and USB-host commands.
- **Start at the [illustrated phase-one test guide](../docs/implementation/firmware-phase1-guide.md).**
- [Architecture and fault policy](../docs/implementation/firmware-architecture.md),
  [verification record](../docs/verification/firmware-phase1/README.md),
  [accepted requirements](../docs/requirements/firmware-specification.md).

Implementation and USB testing are complete; wired timing, analog and radio
acceptance are separate steps. The unidentified LCD backpack is disabled by
default (`CTCSS_LCD_ADDRESS=0`). Its address/pin mapping and the actual encoder's
direction/detent setting must be selected before UI hardware acceptance.

## Tool versions and dependencies

| Tool | Checked version / configuration |
| --- | --- |
| Arduino CLI | 1.3.1 |
| Arduino AVR core | `arduino:avr@1.8.6` |
| SparkFun board package | `SparkFun:avr@1.1.13` |
| Pro Micro FQBN | `SparkFun:avr:promicro:cpu=16MHzatmega32U4` |
| AVR GCC / avrdude | 7.3.0-atmel3.6.1-arduino7 / 6.3.0-arduino17 (core dependencies) |
| Arduino libraries | Core-provided Wire 1.0; no third-party LCD/encoder/tone library |
| STM32CubeMX | 6.16.1; database DB.6.0.161 |
| STM32CubeF7 | 1.17.3; generated required HAL/CMSIS sources and licenses included |
| Arm GNU | 13.2.Rel1 (xPack 13.2.1-1.1 distribution used locally) |
| CMake / Ninja | CMake ≥3.22 and Ninja on PATH; exact run versions in verification |
| STM32CubeProgrammer | 2.21.0 |
| Python | 3.12, `pyserial==3.5` for hardware runner |
| Host C++ tests | C++11 compiler; MSVC 19.44 and Clang supported |

Install Arduino packages once:

```powershell
arduino-cli core update-index --additional-urls https://raw.githubusercontent.com/sparkfun/Arduino_Boards/main/IDE_Board_Manager/package_sparkfun_index.json
arduino-cli core install arduino:avr@1.8.6
arduino-cli core install SparkFun:avr@1.1.13 --additional-urls https://raw.githubusercontent.com/sparkfun/Arduino_Boards/main/IDE_Board_Manager/package_sparkfun_index.json
python -m pip install pyserial==3.5
```

The SparkFun board definition selects the Arduino AVR core and Pro Micro pin
variant. It does not establish a clone's power-path or bootloader identity.
This module's Caterina bootloader and ATmega32U4 signature were observed during
programming; neither the bootloader nor fuse settings was replaced.

## Build (from repository root)

```powershell
# Production: USB STATUS only, unidentified LCD disabled.
./tools/build-firmware.ps1 -Target ProMicro
# Bench: same control/waveform implementation, plus USB SAVE and HANG.
./tools/build-firmware.ps1 -Target ProMicro -Bench
# Identified PCF8574-compatible display example only; verify its mapping first.
./tools/build-firmware.ps1 -Target ProMicro -LcdAddress 0x27
# arm-none-eabi-gcc, CMake and Ninja must be on PATH.
./tools/build-firmware.ps1 -Target Standin -Configuration Release
./tools/build-firmware.ps1 -Target Standin -Configuration Debug
```

Pass `-ArduinoCli` / `-CMake` for non-PATH executables; tool installation paths
are local configuration. Build output is under `.agent-scratch/firmware/`,
including AVR HEX/ELF and STM32 ELF/HEX/BIN/map. No build implicitly flashes.
Display-enabled AVR builds have an address suffix (e.g. `avr-production-lcd0x27`)
so they cannot silently replace the default no-display image.
Release retains debug symbols; perform timing acceptance with Release.

For the STM32 project alone, open `radio_standin/` in a CMake-aware editor or
use its Debug/Release presets. The `.ioc` owns GPIO/peripheral/clock settings.
Regenerate with CubeMX 6.16.1 and STM32CubeF7 1.17.3. Custom calls are inside
`USER CODE` regions; application modules and the top-level CMake additions are
maintained separately. Regeneration was exercised with application hooks
present. Do not hand-maintain alternate pin/clock initialization.

## Program explicitly

List devices first and substitute the identified port/probe:

```powershell
python -m serial.tools.list_ports -v
arduino-cli upload --verify --fqbn SparkFun:avr:promicro:cpu=16MHzatmega32U4 --port COM10 --input-dir .agent-scratch/firmware/avr-bench
STM32_Programmer_CLI -l stlink
STM32_Programmer_CLI -c port=SWD sn=YOUR_STLINK_SERIAL mode=UR -w .agent-scratch/firmware/standin-Release/radio_standin.elf -v -rst
```

Use `avr-production` for the production image. Arduino's normal 1200-baud
touch is supported: the sketch releases PTT and stops feeding the reset
watchdog until Caterina takes over. If an unrelated/older sketch prevents
upload, use the module's reset-to-bootloader procedure and upload during its
boot window. Do not burn a replacement bootloader as a routine upload step.

## Run tests

In a Visual Studio developer shell with Clang, or with a configured GNU C++ compiler:

```powershell
./tools/test-firmware.ps1 -Compiler clang++
# Or in a Visual Studio developer shell: ./tools/test-firmware.ps1 -Compiler cl
python tools/phase1-test.py --pro COM10 --standin COM5 --mode usb --output .agent-scratch/firmware/usb-test.json
# Only after the guide's wiring/voltage checks:
python tools/phase1-test.py --pro COM10 --standin COM5 --mode wired --output .agent-scratch/firmware/wired-test.json
```

The USB-only mode drives fixture pins with **signal wires disconnected**. It
checks firmware command/scheduler/lease state, not electrical outputs. Both
modes temporarily write tone settings and restore the original selection.
Each report identifies source hashes. Preserve binary hashes for the images
actually flashed as well; source hashes alone cannot prove a device's contents.

## USB protocols (115200, 8-N-1, newline; no terminal echo required)

Pro Micro production accepts `STATUS`. Values `saved` and `active` are tenths
of Hz; `tx` means the commanded D8 state, not measured RF. `loop_us` is the
largest observed main-loop gap since reset. `reset` is MCUSR **after the
bootloader** and may be zero; it is not an authoritative reset-cause log.

Bench builds additionally accept `SAVE 1514` (explicit durable save; poll
`STATUS` for `busy=0 saved=1514`) and `HANG` (intentional watchdog test).
An initial `OK queued` is not durable-save confirmation. No USB command can
key PTT or bypass the release-before-rearm interlock.

| NUCLEO command | Action |
| --- | --- |
| `ID` | Protocol/phase/board/clock identity |
| `STATUS` | Arm, drive/sense bitmasks, measured PTT latency, poll gap, capture errors, bounce jitter |
| `ARM` | Release all stimuli, then allow drives with a five-second host lease |
| `STOP` | Release all stimuli, cancel bounce and measurement, disarm |
| `PTT 0` / `PTT 1` | Release / sink microphone PTT |
| `BYPASS 0` / `BYPASS 1` | Release / sink bypass switch |
| `BUTTON 0` / `BUTTON 1` | Release / sink optional encoder button |
| `ENCA 0/1`, `ENCB 0/1` | Optional encoder contact states (1 sinks LOW) |
| `BOUNCE 0` / `BOUNCE 1` | Eight 1 ms toggles, then stable released / pressed; logs scheduling lateness |
| `MEASURE 100` … `MEASURE 4000` | Window in ms; immediate `OK`, then one asynchronous `MEAS` result |

Commands during an arm lease refresh it. No response should be interpreted
as approval for a later phase's radio voltages: phase-one wiring is for bare
Pro Micro logic. Capture results report mHz/us; nonzero errors or insufficient
period count invalidate frequency acceptance. `sense` bits: PTT=1, PTT LED=2,
bypass LED=4. `drive` bits: PTT=1, bypass=2, button=4, A=8, B=16.

Keep direct register code confined to AVR Timer1/EEPROM and the STM32 capture
overrun flag check. HAL owns STM32 initialization and interrupt dispatch.

# PTT/bypass logic through the actual sketch

**Pass: nine host executions each with MSVC 19.44 and Clang 19.1.5.**
The user deferred fixture wiring and requested PTT/bypass logic testing with
physical triggering adapted later. These tests use the actual sketch and modules;
they do not add a USB PTT override or change the deployed control logic.

| Integration check | Observed in host model |
| --- | --- |
| Startup | No PTT with input held, including bypass; released input then fresh press required |
| Input qualification | Brief 4 ms disturbances rejected; stable input handled after qualification |
| PTT and indications | Actual sketch writes D8/A1 together; A2 follows bypass |
| Tone and bypass | Actual ISR samples modulate when keyed, settle to midpoint in bypass; PTT stays asserted |
| Save/latch | Real SAVE parser and asynchronous storage commit 100.0 Hz during 151.4 Hz TX; bypass release resumes measured modeled 151.4 Hz; next TX measures modeled 100.0 Hz |
| Save contention/wear | A second save during busy state is rejected; same-value save performs no byte launches |
| EEPROM readback fault | Injected corrupted payload prevents commit, preserves old selection and permits a later good save |
| Display loss/recovery | NACK on next attempted transaction takes display offline; PTT/tone/latch continue; invisible button/encoder gestures do not save; display recovers |
| USB | Stalled endpoint and absent serial host do not prevent logical PTT press/release; standalone startup succeeds |
| Timer fault | Corrupted owned timer configuration releases PTT and stops D9; fault remains latched |
| Upload request | Actual 1200-baud/no-DTR path releases an actively keyed PTT and stops watchdog feeds; continued held input cannot rekey |

Executions: normal; held PTT; bypass; both held; millis wrap at startup;
unavailable display; no serial host at startup; EEPROM readback fault; and a
separate build with the display disabled, matching the current bench configuration.
The existing module suites also pass, including all allowed tone values and
exhaustive input/range/latch checks.

[MSVC log](msvc-tests.txt), [Clang log](clang-tests.txt), and
[source/evidence manifest](manifest.json) identify the checked revision.
Reproduce using [test-firmware.ps1](../../../../../tools/test-firmware.ps1)
in a Visual Studio developer shell. The
[test source](../../../../../firmware/tests/sketch_test.cpp) includes the unchanged
`.ino` and links the actual control, tone, storage, journal and display modules.
Only its hardware boundaries are modeled. The host compiler uses C++14 for the
Windows STL; the Arduino compiler/build settings are unchanged.

The model advances time in 100 µs steps, supplies input levels at `digitalRead`,
executes the ISR, records GPIO writes, and completes modeled EEPROM bytes after
3.4 ms. Those choices are not measured AVR execution/interrupt timing, EEPROM
electrical programming timing, power-cut or pin-latency evidence. AVR attributes
and atomic/PROGMEM behavior are replaced for host execution. Narrow allowances
handle known host-vs-AVR address/printf types; the remaining host code uses
warnings as errors. Watchdog feeding/upload logic is tested; a real reset,
bootloader and output electrical behavior are not modeled.

Display detection is transaction-driven: unchanged content does not poll for
presence continuously. The test deliberately triggers a display update before
expecting NACK detection. This corrects an initial test expectation, without
requiring a firmware correction.

## Deferred physical work

The Arduino and NUCLEO were absent from serial enumeration when the additional
repeated USB recovery run was attempted; only COM11 (supply) appeared. The
[inconclusive report](watchdog-port-unavailable.json) contains no completed
cycles. No HANG or fixture drive command reached a device during this attempt.
This does not invalidate the earlier completed USB/watchdog run.

A repeatable USB watchdog runner is prepared and four mocked verdict tests
pass, but its new repeated hardware path remains unqualified. It requires an
observed USB disappearance before accepting recovery. The full
[bench procedure](../../../../../tools/bench/README.md) distinguishes this from
electrical D8 release timing. Physical NUCLEO stimulus, independent PTT/LED
timing and operation at a rated 16 MHz supply remain open. Continue conditional
testing at the user-accepted low rail when the bench session resumes.

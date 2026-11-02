# Firmware architecture and implementation decisions

This implements the [accepted baseline](../requirements/firmware-specification.md).
Use the [bench guide](firmware-phase1-guide.md) for physical setup, and the
[verification record](../verification/firmware-phase1/README.md) for evidence.

## Pro Micro

The conventional Arduino sketch owns `setup()` and `loop()`. Modules:

| Module | Responsibility and ownership |
| --- | --- |
| `control.cpp` | Pure control state, 50 presets, debounce, encoder and UI; host-testable |
| `tone.cpp` / `sine_table.h` | Timer1 ISR and D9 waveform; only ISR owns phase/envelope |
| `journal.cpp` | Versioned record encoding, CRC-16/CCITT-FALSE, sequence selection |
| `storage.cpp` | Asynchronous EEPROM writer and durable read-back verification |
| `display.cpp` | Configurable PCF8574/HD44780 1602 driver, bounded transactions and recovery |
| `icom_ctcss.ino` | Fixed pin wiring, scheduler, watchdog and bounded USB diagnostics |

Timer0 remains Arduino's millis/micros timebase. Timer1 fast PWM mode 14,
ICR1=1599, no prescaler: **16 MHz / 1600 = 10 kHz** on OC1A/PB5/D9.
Overflow computes the next buffered duty using a 32-bit phase accumulator
and 256 signed samples stored in flash. No Servo/tone/analogWrite library may
take Timer1. D2/D3 remain Wire/I²C. A0 is untouched.

Tone frequency is represented in tenths of Hz; phase increment is rounded
from `tone_tenths * 2^32 / 100000`, adjusted by `clockCorrectionPpm`. Entry
resolution and DDS quantization do not establish oscillator accuracy. For a
measured fast clock error of +400 ppm, set correction to +400 and remeasure.
Do not calibrate against an unqualified NUCLEO reference and claim traceability.

The initial digital peak is **600 counts about midpoint 800**, nominal duty
12.5–87.5%, with a 50-sample / **5 ms** linear envelope on enable/disable.
At 5 V, full-scale modulation corresponds to a 1.875 V peak average PWM
fundamental before filtering (calculated). RV1 is the physical level control.
Changing `tonePeakCounts` also requires regenerating the sine table using its
documented formula; a compile-time assertion prevents a silent mismatch.
No per-frequency amplitude compensation is enabled without measurements.

Idle/bypass retain 50% carrier duty, following the existing transient analysis.
Tone disable means zero sine modulation, not zero carrier. Starting PWM at
boot still changes the analog bias; release-before-rearm prevents startup TX,
but startup coupling and clicks require PCB/radio measurements.

The main loop qualifies PTT/bypass for **5 ms** and services their outputs
before storage, display and USB. Both inputs must have a qualified initial
sample before arming; initial held PTT never keys. Each new press latches the
saved tone. Durable saves during TX change only `saved`; resuming tone after
bypass uses `latched` until release. The 250 ms watchdog is fed only by the
main loop. Every application reset starts unarmed.

Button qualification is 15 ms and long press is 750 ms after its qualified
press. Encoder transition sequence/detent count are configurable. Invalid
diagonal transitions discard partial movement; only full configured detents
change the UI. Editing never writes EEPROM until an explicit save gesture.

EEPROM addresses **0–19** contain two 10-byte records: commit marker, schema,
16-bit sequence, 16-bit tone, two reserved zero bytes and CRC. The inactive
slot is invalidated first, body written one byte at a time with hardware
erase/write running asynchronously, marker written last, then every byte
read back. Only a verified record changes the application's saved selection.
Same-value saves do no writes. CRC detects corruption; the storage design
assumes documented EEPROM operation within supply limits. Firmware cannot
make out-of-spec brownout writes reliable. Physical power-cut/BOD acceptance
remains separate; the existing fuse settings were not changed.

Wire uses a 1.5 ms timeout with TWI reset. Each service call sends at most one
bounded I²C transaction, and PTT is handled before the next. Display init
delays are scheduled, never blocking delays; changed-character updates avoid
continuous clears. A 32-character frame needs at most 64 data/address
transactions plus cursor commands. Rendering begins every 50 ms and is
designed to fit the 200 ms update budget; physical confirmation is pending.
Missing ACK/timeouts discard invisible edits and retry initialization after
one second. A request already explicitly saved may finish while the display
is unavailable. Recovery returns to Home; held buttons are suppressed.

USB output checks `Serial.dtr()` and endpoint space, transmitting at most 16
bytes at a time. Arduino AVR 1.8.6's `Serial` boolean conversion inserts a
10 ms delay, so it is deliberately avoided. The sketch honors the core's
1200-baud/DTR-low Caterina request by releasing PTT and withholding watchdog
feeds. Startup `.init3` is marked `used` to survive LTO. Reset cause is sampled
after the bootloader, which may already have consumed MCUSR.

## Fault decisions

| Fault | Behavior |
| --- | --- |
| LCD NACK/bus timeout | Preserve PTT, bypass and current TX latch; stop invisible editing; recover display asynchronously |
| Invalid/missing EEPROM at boot | 151.4 Hz fallback, remain unarmed until release/new press |
| EEPROM write/read-back failure | Retain prior selection; show Save failed; no early pending application |
| Timer1 configuration corruption | Latch fault; release D8/A1; disconnect/stop timer and drive D9 LOW; reset required |
| Stalled application | Hardware watchdog resets; release-before-rearm on restart; actual electrical release target ≤1 s |
| USB programming reset | Release PTT, permit bootloader reset, then require release/new press |

The waveform fault check detects register configuration corruption, not
every possible electrical/timing error. Its stop-to-LOW can cause a bias
transient; PTT release takes priority in this fault class. The board has no
rail/current/audio/RF feedback, so firmware makes no claims about those.

## NUCLEO-F767ZI

CubeMX `.ioc` and generated `Core`, startup/linker and CMake files provide the
baseline. Only USER CODE hooks call `Standin_Init`, `Standin_Poll` and the
pre-HAL overcapture check. `standin.c` owns the command parser, stimulus state,
lease, measurements and UART callbacks. `pwm_capture.c` owns the host-testable
edge/period/duty-crossing algorithm. No RTOS, DMA or cache-managed buffers are
needed for this phase.

HSE bypass receives factory ST-Link **8 MHz MCO**; PLL M=4, N=96, P=2 gives
96 MHz SYSCLK. APB1=48 MHz, TIM2=96 MHz. Prescaler 95 yields a **1 MHz 32-bit
capture counter**, rollover every 4294.967296 s. Unsigned subtraction handles
wrap. USART3 PD8/PD9 uses ST-Link VCP at 115200. GPIO labels and exact header
contacts are in the guide; selected stimulus pins use open drain, initially
released, with no STM32 internal pulls.

IRQ path: `TIM2_IRQHandler` checks CC1OF **before** HAL clears/reads capture
state, then `HAL_TIM_IRQHandler` dispatches the capture callback. It reads
CCR1 and the current PA0 level, records period/high time and counts duty
crossings with 47/53 µs hysteresis. ISR work contains no division, formatting,
UART writes or allocation. At 10 kHz there are 20,000 edge interrupts/s;
missed-edge patterns, implausible periods/widths and overcapture invalidate
the window. This polling-of-level capture approach depends on servicing
edges before the next transition; validate with the analyzer under load.
No assertion of lossless capture rests solely on a clear overcapture flag.

Main copies the small statistics object with interrupts briefly masked,
then computes mHz outside the ISR. Windows are limited to 4 s to bound
accumulators. No signal is reported as frequency zero plus success: the
runner requires enough periods, zero errors and suitable duty excursion.
The supplied synthetic test uses all 50 actual waveform table entries and
timer wrap, and checks dropped-edge diagnostics; it is not a bench measurement.

USART RX interrupts feed a 256-byte ring; main consumes bounded chunks and
starts one interrupt-driven response at a time. Overlong lines/UART loss
release stimuli. The five-second host lease releases outputs if communication
stops. An independent LSI watchdog (prescaler 32, reload 1999, nominal 2 s)
recovers a stalled loop into the released state; LSI timing is approximate.
`BOUNCE` schedules eight 1 ms alternating transitions then holds the final
state. Its maximum lateness is reported, so a poorly timed run is not silently
accepted as a precisely timed source.

## Boundaries for later phases

The first fixture has no analog audio stimulus, RF path, simulated radio
power supply or radio-PTT electrical load. Add those as explicitly identified
phase modes with the appropriate interface circuitry; do not reuse these
bare-module wires on the radio connector. UI hardware identification, full
range measured frequency, analog level/distortion limits and radio deviation
are still physical acceptance items, as distinct from implemented behavior.

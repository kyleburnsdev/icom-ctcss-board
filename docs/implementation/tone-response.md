# Preliminary tone-chain estimate

Run `python tools/tone-response.py` from the repository root.
This standard-library nodal AC calculation evaluates the implemented R1–R5/C1/C2 network with the selected 10 kΩ trimmer across DIVIDER/GND, its wiper feeding a 1 µF coupling capacitor. Part/pin-map evidence is recorded separately. The calculation uses an ideal PWM source and an **illustrative** resistive equivalent radio/microphone load; the actual impedance, bias, and required injection amplitude are unknown.

## Selectable tone frequencies

No component fixes the generated frequency at 151.4 Hz. Firmware must synthesize the selected tone on D9; the RC network is a broad low-pass reconstruction filter, not a tuned tone oscillator or narrow band-pass. The nominal 10 kHz PWM carrier is separate from the selected tone frequency. No firmware has been implemented.

Example transfer magnitudes at maximum trimmer setting, using the illustrative 1 kΩ load:

| Tone Hz | Audio gain per volt of D9 AC fundamental | Relative to 151.4 Hz |
| --- | ---: | ---: |
| 67.0 | 0.0004955 | +0.89 dB |
| 100.0 | 0.0004796 | +0.60 dB |
| 151.4 | 0.0004474 | 0 dB |
| 203.5 | 0.0004102 | −0.75 dB |
| 254.1 | 0.0003739 | −1.56 dB |

This demonstrates broad response rather than a 151.4 Hz lock. It does not certify a complete tone table or radio deviation. Once the intended table is defined, check amplitude, distortion, PWM residue and radio deviation across it. A single analog trimmer sets overall level; firmware may compensate frequency-dependent amplitude within its available PWM range, but maximum output headroom and actual loading must be measured.

Maximum trimmer setting, output at the microphone audio net per volt of AC input at D9:

| Illustrative load | Gain at 151.4 Hz | Gain at 10 kHz |
| --- | --- | --- |
| 600 Ω | 0.0002695 | 0.000001136 |
| 1 kΩ | 0.0004474 | 0.000001887 |
| 2.2 kΩ | 0.0009727 | 0.000004102 |
| 10 kΩ | 0.0041105 | 0.000017334 |
| 100 kΩ | 0.0226872 | 0.000095662 |

The calculated carrier-to-tone transfer ratio is approximately −47.5 dB for these cases. This is a ratio of circuit transfer magnitudes, **not** a prediction of the output spectrum: PWM carrier and tone input amplitudes differ, and firmware waveform generation is outside this model.

The strong load dependence means the fixed 100 kΩ mixing resistor can substantially limit available tone amplitude. At a hypothetical 1 kΩ load, 1 V peak of tone fundamental at D9 gives about 0.447 mV peak at the audio node. Required radio deviation cannot be established from this number. Measure the actual port load and required injection level before accepting the adjustment range; do not revise specified R5 merely to improve this illustrative calculation.

The model excludes wiring coupling, capacitor tolerances/leakage, microphone nonlinearities, radio frequency response, source output resistance, and noise. Minimum trimmer setting grounds the wiper and ideally gives zero tone. Intermediate settings alter both division and source impedance, so adjustment need not produce a linear output-amplitude scale.

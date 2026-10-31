# LTspice verification package - 25 October 2026

Read the [findings and prototype decisions](../../implementation/ltspice-validation.md) first. These are simulations of the unchanged 22 October hardware sources; the [manifest](manifest.json) identifies the exact inputs. The radio PTT network is transcribed from the Icom service manual; tone-chain loads remain illustrative.

## Run the editable cases

Copy the `.cir` and `.inc` files together into a task directory under repository-root `.agent-scratch/`, then open each `.cir` in LTspice and run it. No additional model download is needed: the passive models are intrinsic, and the explicitly generic PTT transistor/diode models are defined in the decks. The original runs used LTspice 26.1.1 Windows, Normal solver, 27 degrees C; analysis directives and numerical options are inside each input.

Through MCP: inspect open designs, call `open_design` with the absolute copied path, call `start_simulation`, poll `is_simulation_running`, then read `get_spice_log`. Do not start a second run while the first is running. An externally changed file can differ from the document held open in LTspice: use `set_design_content` to update an open document, then check `get_design_content` before rerunning.

| Input | Purpose | Completed cases |
| --- | --- | ---: |
| [tone-ac.cir](tone-ac.cir) | All 50 presets plus 10 kHz; five loads and five ideal trimmer positions | 25 |
| [tone-corners.cir](tone-corners.cir) | All 512 passive tolerance endpoints; five loads; four frequencies | 2,560 |
| [tone-pwm.cir](tone-pwm.cir) | Illustrative switched PWM at three tones, after settling | 3 |
| [tone-pwm-fine.cir](tone-pwm-fine.cir) | Halved maximum timestep at 151.4 Hz | 1 |
| [tone-keying.cir](tone-keying.cir) | Two idle mean levels and three tones, averaged PWM | 6 |
| [ptt-radio.cir](ptt-radio.cir) | Service-manual PTT network and carrier-board driver | 6 |
| [ptt.cir](ptt.cir) | Separate provisional 5 mA margin test; generic transistor gain sensitivity | 6 |

The tone decks share [tone-network.inc](tone-network.inc). Nominal values are in [nominal.inc](nominal.inc); the corner deck defines its own values. [connectivity.json](connectivity.json) maps modeled components to the fresh KiCad export and records 61 passing assertions and 38 BOM-value matches. RV1 is split into two resistors with a 1 milliohm endpoint approximation; physical wiper/end resistance is excluded.

## Results and interpretation

- [results.json](results.json): numerical summary, selected criteria, and unresolved acceptance targets.
- [nominal-ac.csv](nominal-ac.csv): all 1,275 nominal AC points, indexed by load and trimmer fraction.
- [tolerance-corners.csv](tolerance-corners.csv): all 10,240 endpoint frequency points, indexed by load and corner number. Corner bits 0-8 select high/low values for R1, R2, R3, R4, R5, C1, C2, C3, RV1 total resistance, respectively.
- Each input has a matching `.log` with original solver output and applicable `.meas`/`.four` results. Logs retain original execution paths as provenance; the decks use relative includes and do not need those paths.
- [manifest.json](manifest.json): design/library/BOM/requirement hashes, tool versions, service-manual identity, warning counts and package hashes.
- [erc.json](erc.json), [drc.json](drc.json), [schematic.net](schematic.net): newly collected saved-design evidence; distinct from prior verification records.

For numeric waveform inspection through MCP, use `get_raw_info` to discover names, then `read_raw_waveforms` for a small selection or `export_raw_waveforms` for a SQLite export. The tone cases save `V(audio)`; AC data is complex. Exported transient x values in the delayed-start PWM run begin at zero rather than 1 s: analyze its last five periods relative to the exported final time. Use trapezoidal time weighting for adaptive samples. Raw/SQLite files are reproducible intermediates and are not maintained here.

The nominal AC results were independently compared with `tools/tone-response.py` (Python standard library). Figures were generated from MCP-exported SQLite values using NumPy 2.3.4 and Matplotlib 3.11.2, then visually inspected. They illustrate behavior; scalar/CSV values and exact input decks are the retained engineering evidence. Fundamental agreement passed a 0.1% check; small harmonic estimates did not establish timestep-independent THD. The generic PTT models do not establish semiconductor production limits, and neither test replaces physical wiring/bring-up checks.

# Q1 physical pin map

**Historical narrow-footprint acceptance, superseded by [physical-pin-maps.md](physical-pin-maps.md).** The final CNC design uses factory-formed onsemi **2N3904RLRAG**, 2.54mm pitch, larger pads/drills. Do not order this document's straight-lead 2N3904G for the final board.

Selected part: **onsemi 2N3904G**, straight-lead bulk TO-92, CASE 29, STYLE 1. Do not substitute another vendor or bent-lead suffix without review.

Primary source: [onsemi 2N3903/D, August 2021, revision 9](https://www.onsemi.com/download/data-sheet/pdf/2n3903-d.pdf), PDF pages 1, 3, 7 and 8. Package drawing 98ASB42022B, CASE 29-11, issue AM, dated 9 March 2007. Page 3 specifies 2N3904G bulk packaging. Use the linked manufacturer source; local datasheet copies and rendered extracts are no longer maintained.

Symbol `Transistor_BJT:2N3904`; footprint `Package_TO_SOT_THT:TO-92_Inline`.

| Physical lead | Function | Symbol pin / name / type | Pad | Footprint-local x/y mm | View and direction | Evidence |
|---|---|---|---|---|---|---|
| 1 | Emitter | 1 / E / passive | 1 | 0 / 0 | Component top view, flat face toward +Y, leftmost lead | p1 straight-lead perspective, p7 geometry, p8 style 1 |
| 2 | Base | 2 / B / input | 2 | 1.27 / 0 | Component top view, flat face toward +Y, middle lead | same |
| 3 | Collector | 3 / C / passive | 3 | 2.54 / 0 | Component top view, flat face toward +Y, rightmost lead | same |

The bottom/package-end drawing on p7 has its flat edge upward. Translating to the component top view reverses that edge to downward; the p1 numbered perspective establishes E-B-C left to right when facing the flat marked surface with leads downward. This agrees with the footprint flat edge at positive Y and pad 1 at left. No inferred universal TO-92 numbering was used.

Counts: three physical leads, three symbol pins, three electrical pads, zero duplicate pads, zero mechanical-only pads. Query-back found 1.27 mm pitch (datasheet straight-lead G = 1.15–1.39 mm), 0.75 mm round drills, pad 1 rectangular and pads 2/3 oval, all 1.05 × 1.50 mm. Datasheet lead section D max 0.533 mm and J max 0.50 mm implies about 0.731 mm maximum diagonal; hole clearance is therefore tight at worst-case lead tolerance. Enlarge holes/pads and spread footprint if necessary during hand-solder footprint review. No claim of easy insertion at all tolerances.

Acceptance evidence: library symbol and footprint queried; disposable schematic and closed-file board placed by Konnect in `.agent-scratch/implementation/evidence/scratch/`; instances read back with `list_schematic_components` and `get_component_pads` (source `file`). Schematic PNG, board SVG and board-detail PNG visually inspected: E=1, B=2, C=3; square pad 1 at left; flat edge down; three holes; courtyard/fab/silk intact. Physical electrical map accepted for schematic placement. Stock `*.Cu` pads require project bottom-only variants before PCB acceptance.

Electrical selection remains provisional until radio PTT voltage/current are measured. R10=4.7 kΩ and R11=100 kΩ provide approximately 0.87 mA base drive at 5 V / 0.85 V VBE, including pull-down current. Use an initial **5 mA maximum sink design target**, with voltage/current and saturation checked on the real radio; this is not a demonstrated radio requirement or a transistor rating. Reset/high-impedance D8 is pulled low by R11, releasing PTT.

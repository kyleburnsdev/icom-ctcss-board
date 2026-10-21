# CTCSS board implementation

The editable schematic and routed PCB prototype are complete. This is a design handoff with documented CAM and bench checks outstanding, not a declaration that the board is ready to mill or connect to the radio.

- [Schematic PDF](../reference/schematic-complete.pdf) and [circuit notes](schematic-complete.md)
- [Top assembly drawing](../reference/assembly-top.svg) and [bottom copper preview](../reference/copper-bottom.svg)
- [BOM CSV](../reference/bom.csv), [part/footprint details](footprint-review.md), and [assembly/bring-up procedure](assembly-and-bring-up.md)
- [J5/J6 wiring table](assembly-and-bring-up.md#j5j6-cable-wiring): each switch/LED has its own signal/ground pair; no external return splice
- [CNC geometry package and instructions](../../manufacturing/pcb/carvera-air/README.md)
- [150 × 100 mm landscape CAM set and Y-flip registration instructions](../../manufacturing/pcb/carvera-air/landscape-y-flip/README.md)
- [Top legend SVG for laser preparation](../../manufacturing/pcb/carvera-air/native-exports/icom-ctcss-board-top-legend.svg), with F.SilkS Gerber in the same package
- [Independent review](design-review.md), [layout evidence](pcb-layout.md), and [acceptance checklist](acceptance-checklist.md)

Verification: ERC zero errors/warnings; final DRC zero errors and zero unconnected items; 61 exported-netlist assertions pass. Native PCB inventory confirms 241 B.Cu segments, no routing vias or pours, 100 × 150 mm outline and four 4 mm mounting holes. The final DRC retains 114 documented non-electrical warnings, including original footprint text overlaps. The independent aggregate review also flags LCD pull-up and bulk-capacitance assumptions requiring physical checks.

The PCB uses enlarged CNC lands derived from the approved Biacco42 Pro Micro geometry. KiCad's normalized virtual top THT lands are excluded from the physical manufacturing package. Socket fit, USB cable/enclosure fit, actual drills/copper, a milling coupon, radio cable mapping, supply/thermal limits, PTT current and tone deviation remain outstanding. Firmware is outside this deliverable.

Intermediate routing candidates, historical checkpoints and disposable fixtures are isolated in ignored `.agent-scratch/`. They are not required project deliverables. Reusable engineering tools live in `tools/`.

- [Build reference index](../reference/README.md)
- [Revision-specific verification records](../verification/README.md)

- [Build reference index](../reference/README.md)
- [Revision-specific verification records](../verification/README.md)

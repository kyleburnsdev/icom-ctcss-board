# Build references

These exports let readers inspect and assemble the hardware without opening KiCad.

- [Schematic PDF](schematic-complete.pdf)
- [Reference-by-reference BOM](bom.csv)
- [Top assembly drawing](assembly-top.svg)
- [Mirrored bottom-copper preview](copper-bottom.svg)
- [Clean top-legend preview](top-legend-clean.svg)
- [Module seller-source notes and header transcription](teyleten-source-notes.md)

These are saved-design references, not machine toolpaths. Use the [manufacturing package](../../manufacturing/pcb/carvera-air/README.md) for CAM inputs and the [assembly instructions](../implementation/assembly-and-bring-up.md) for build checks. Source revision and verification limitations are recorded in the [verification index](../verification/README.md).

Keep one useful format per drawing. Refresh relevant references deliberately after design changes; disposable previews belong in `.agent-scratch/`.

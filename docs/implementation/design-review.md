# Hardware verification and remaining acceptance

Current PCB revision: 2026-10-29 jig-interface migration. The
[revision manifest](../verification/pcb-revision.json) identifies source files
and check scope. The circuit and routing are unchanged; H5–H8 registration holes,
their footprints/courtyards, setup notes and three relocated legend labels are new.

## Direct CAD evidence

DRC: zero errors, zero unconnected items, 115 retained warnings. Of these,
38 compare circuit footprints with their library copies, 35 concern existing
footprint fields/artwork, and 42 concern schematic metadata plus four enclosure
mechanical footprints. The four new jig footprints are board-only. No new hole
or relocated label warning remains. Warnings remain visible in
[the complete report](../verification/final-drc.json).

The [inventory](../verification/final-board-inventory.json) verifies 242 B.Cu
segments, 111 electrical pads, no vias/pours, four unchanged enclosure mounts
and four new jig holes. Selected component envelopes clear the new hole edges
by at least 2.46 mm. Physical copper output excludes virtual F.Cu THT lands.

The schematic/netlist and component choices are unchanged by this migration.
Use the [electrical simulation](ltspice-validation.md) for its explicitly
identified electrical model/revision and the [sourcing review](component-sourcing-review.md)
for dated procurement evidence. Neither establishes current PCB machining acceptance.

## Physical manufacturing acceptance remains open

CAD/CAM migration checks pass. The saved board and library footprints contain
four enforced keepouts, native thickness is 1.5 mm, and the native fill-control
experiment verifies exclusion. These operations used the authorized native API
fallback because Konnect does not implement their writers.

- Native job reopen and posted-NC checks pass. Complete protected through-cut
  setup, physical tool/holder/bed-pin collision review and actual surface-height
  compensation before machining.
- Qualify hole sizes/spacing/slip fit, flip repeatability, isolation depth/width,
  electrical hole fit and UV/laser settings on representative material.
- Verify purchased module/socket/USB and enclosure/cable access on a prototype.
- Complete current-limited power, USB/radio power isolation, supply/regulator
  temperature, PTT key/release/reset, audio/noise and tone-deviation checks in the
  [assembly procedure](assembly-and-bring-up.md).

The user accepts nominal 8 V to RAW for this revision. Firmware and physical
radio acceptance remain separate work. The [manufacturing workflow](pcb-jig-and-freecad-cam.md)
is the authority for machine setup and program boundaries.

# Current verification records

The [PCB revision manifest](pcb-revision.json) identifies the 2026-10-29 saved
board and current export/check hashes. Superseded PCB manufacturing manifests
and review summaries are removed; retrieve earlier revisions from Git history.

| Record | Scope |
| --- | --- |
| [DRC](final-drc.json) | Saved board: zero errors/unconnected, 115 retained warnings |
| [Inventory](final-board-inventory.json) | Copper restrictions, component envelopes, eight mechanical holes and nominal jig clearances |
| [CAM input geometry](pcb-cam-geometry.json) | Native export identities, merged copper, hole counts, ideal cutter sweep and legend hatch |
| [CAM jobs](pcb-cam-jobs.json) | Generated native operations and review milling output |
| [Saved CAM reopen](pcb-cam-reopen.json) | Saved native paths, operation states and asymmetric J1 position |
| [Posted motion](pcb-posted-motion.json) | Actual review NC modes, tool changes, cutter sweep and laser power gating |
| [Bottom native CAM view](pcb-cam-bottom.png) | Current saved bottom toolpaths; holder/fixture simulation excluded |
| [Exported circuit netlist](schematic-complete.net) | Circuit connectivity assertions; mechanical jig holes have no circuit nets |
| [ERC](erc-complete.json) | Unchanged schematic's electrical rule evidence |
| [LTspice package](ltspice/README.md) | Revision-specific electrical simulations, with their own inputs and limits |
| [Enclosure P1](enclosure-p1/release-manifest.json) | Existing enclosure CAD/mesh/slice revision; PCB mounting interface unchanged |

CAD/CAM migration checks pass: four footprint-owned all-copper keepouts and
native 1.5 mm thickness are verified. The
[controlled native fill check](pcb-keepout-fill.json) and
[native update record](pcb-native-update.json) document the supported-API
fallback and unchanged machining geometry. Physical fit, protected breakthrough,
collision checks, surface mapping and milling qualification remain pending.
The dark legend is marked on fully UV-cured white mask at provisional 5% power,
500 mm/min, 0.05 mm hatch and one pass. Qualify readability, retention and coating
integrity after IPA cleaning on the first full board; no separate legend coupon.
See the [workflow and status](../implementation/pcb-jig-and-freecad-cam.md).

The 2026-10-31 CAM update separates copper isolation from the repeatable
115-hole electrical/enclosure program. Job 20 and its NC now clear 111 bottom
pads using Makera's spring-loaded mask tool before initial electrical drilling.
The [mask addition record](pcb-mask-job.json) checks preservation of prior native
paths; posted-motion checks cover pad-only sweep containment and original copper
datum usage. The hole program can clear coating after both faces are finished,
before assembly, using the original pre-isolation copper G54 Z0 and protected
breakthrough. No subsequent work zero is captured; jig registration holes are
excluded from clearing. Spring preload, usable soldering area and intact copper
remain physical acceptance items.

Unchanged-circuit evidence remains tied to its original inputs and date. The jig
PCB revision must not be inferred from an earlier simulation's PCB hash or DRC.
No bench, machine or physical jig acceptance is implied by these CAD reports.

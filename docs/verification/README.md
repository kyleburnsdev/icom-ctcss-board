# Current verification records

The [PCB revision manifest](pcb-revision.json) identifies the 2026-11-10
in-jig coating / two-color diamond-drag candidate and current saved sources.
It distinguishes unchanged-circuit evidence from newly generated trial checks.

| Record | Scope |
| --- | --- |
| [Firmware phase one](firmware-phase1/README.md) | Pro Micro/NUCLEO builds, native tests, programming and USB-only checks; wired acceptance pending |
| [DRC](final-drc.json) | Saved board: zero errors/unconnected, 115 retained warnings |
| [Inventory](final-board-inventory.json) | Copper restrictions, component envelopes, eight mechanical holes and nominal jig clearances |
| [CAM input geometry](pcb-cam-geometry.json) | Native export identities, merged copper, hole counts, ideal cutter sweep and legend hatch |
| [CAM jobs](pcb-cam-jobs.json) | Generated native operations and review milling output |
| [Saved CAM reopen](pcb-cam-reopen.json) | Saved native paths, operation states and asymmetric J1 position |
| [Posted motion](pcb-posted-motion.json) | Actual review NC modes, tool changes, cutter sweep, drag spindle-off behavior and floor depth limit |
| [Bottom native CAM view](pcb-cam-bottom.png) | Current saved bottom toolpaths; holder/fixture simulation excluded |
| [Exported circuit netlist](schematic-complete.net) | Circuit connectivity assertions; mechanical jig holes have no circuit nets |
| [ERC](erc-complete.json) | Unchanged schematic's electrical rule evidence |
| [LTspice package](ltspice/README.md) | Revision-specific electrical simulations, with their own inputs and limits |
| [Enclosure P1](enclosure-p1/release-manifest.json) | Existing enclosure CAD/mesh/slice revision; PCB mounting interface unchanged |

The [bottom legend check](pcb-bottom-legend.json) records native multiline
text/mirroring and unchanged electrical geometry. The
[inventory preflight](pcb-inventory-preflight.json) is incomplete; inspect its
[declared requirements](pcb-inventory-preflight-input.json) and package coverage
notes rather than interpreting it as a stock outage or qualification pass.

Current jobs retain copper zero/map through in-jig coating and pad clearing,
then use separate mask-surface references for nonrotating drag legends and a
floor reference for final bores after both coatings. The posted checks cover
positive legend centerlines, no spindle starts in drag NC and positive Z for
every final-hole move. Physical removal, adhesion, contrast and fits remain
trial observations in the [attempt log](../pcb-attempt-log.md).

Historical pcb-mask-job.json (0.20 mm initial overtravel) and
pcb-cam-job-split.json predate this candidate. pcb-keepout-fill.json remains the
historical controlled-fill experiment, with applicability supported by current
native inventory and unchanged copper/rule geometry. None validates current
legend pressure or floor-referenced depths. The schematic is unchanged; ERC
and netlist evidence retain their original scope/date. No machine run is implied.

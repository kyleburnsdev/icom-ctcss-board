# Verification records

Use the [fabrication guide](../pcb-fabrication-guide.md) for the current process
and [attempt log](../pcb-attempt-log.md) for physical results. The user's laser
transparency test demonstrates sharp, clean heat transfer with easy alignment.
Sublimation and the revised pre-flip drilling sequence have not yet been tested.

| Record | Scope |
| --- | --- |
| [Sublimation artwork](pcb-sublimation.json) | Source identity and color artwork; digital evidence |
| [Sublimation print QA](pcb-sublimation-print-qa.json) | Dimensions, scaling and orientation; digital evidence |
| [Firmware phase one](firmware-phase1/README.md) | Builds, tests, programming and USB checks; wired acceptance pending |
| [DRC](final-drc.json) | Saved board: zero errors/unconnected, 115 retained warnings |
| [Board inventory](final-board-inventory.json) | Copper restrictions, envelopes, eight mechanical holes and jig clearances |
| [Circuit netlist](schematic-complete.net) | Connectivity assertions; jig holes have no circuit nets |
| [ERC](erc-complete.json) | Schematic electrical-rule evidence |
| [LTspice package](ltspice/README.md) | Revision-specific electrical simulations and limits |
| [Enclosure P1](enclosure-p1/release-manifest.json) | Enclosure CAD/mesh/slice revision |

The [inventory preflight](pcb-inventory-preflight.json) has incomplete coverage;
inspect its [requirements](pcb-inventory-preflight-input.json) rather than
interpreting it as a stock outage or qualification pass.

Machining retains copper zero/map through pad clearing. Drilling before the
first flip and conditional cleanup after top work use aluminium-floor Z0 with
backing and no copper map. CAM checks must match actual sources and programs;
they do not establish fixture clearance, pad exposure, coating adhesion, hole
fit or electrical acceptance. Record those physical checks in the attempt log.

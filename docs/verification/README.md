# Hardware verification records

**Current sourcing revision (2026-10-22):** see [sourcing verification](sourcing-revision.json). Fresh ERC: 0 errors/0 warnings; DRC: 0 errors/0 unconnected, 115 retained warnings (38 library comparisons, 35 silk/field overlaps, 42 metadata/mechanical parity). All 111 electrical pads match the schematic in an independent read-only review; 61 netlist assertions pass. There are 242 B.Cu tracks, no vias/zones and minimum calculated body gap 2.14mm. Current reports and drawings were regenerated; the older narrative/results below are historical where they differ.

The current ERC, DRC, inventory and netlist describe the 2026-10-22 sourcing revision. `review-summary.json` and the older ground-geometry narrative describe the 2026-10-20 bypass-only hardware cleanup.

| Record | Purpose |
| --- | --- |
| [Review summary](review-summary.json) | Reviewed source SHA-256 hashes, assertion count and ground-geometry conclusions |
| [Design review](../implementation/design-review.md) | Findings, warning disposition and outstanding physical checks |
| [ERC](erc-complete.json) | Recorded zero errors and warnings |
| [DRC](final-drc.json) | Recorded zero errors/unconnected items and 115 warnings |
| [Board inventory](final-board-inventory.json) | Saved PCB geometry and nominal body-clearance inventory |
| [Exported netlist](schematic-complete.net) | Input to the maintained connectivity checker |

The netlist checker was rerun after this cleanup: all 61 assertions pass. That checks the retained export; it does not establish that a later source edit matches it. The netlist source-location metadata uses a repository-relative path for publication.

Before relying on these records after a hardware change, compare the saved source hashes with `sourcing-revision.json` and regenerate affected exports/checks through Konnect. Retain the source revision, tool version, check scope and unresolved findings with new results. Raw tool transcripts, duplicate renders and intermediate checkpoints belong in `.agent-scratch/`, unless needed to explain a specific unresolved issue.

`tools/check-netlist.py` reads the retained netlist. `tools/check-final-board.py` refreshes the inventory using KiCad's Python environment. See [tool instructions](../../tools/README.md). Manufacturing and powered-radio acceptance remain governed by the [acceptance checklist](../implementation/acceptance-checklist.md).

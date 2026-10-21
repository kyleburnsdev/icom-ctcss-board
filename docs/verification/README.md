# Hardware verification records

These records describe the 2026-10-20 bypass-only hardware cleanup. They were reorganized on 2026-10-21; that relocation did not rerun ERC, DRC or the independent CAD review.

| Record | Purpose |
| --- | --- |
| [Review summary](review-summary.json) | Reviewed source SHA-256 hashes, assertion count and ground-geometry conclusions |
| [Design review](../implementation/design-review.md) | Findings, warning disposition and outstanding physical checks |
| [ERC](erc-complete.json) | Recorded zero errors and warnings |
| [DRC](final-drc.json) | Recorded zero errors/unconnected items and 114 warnings |
| [Board inventory](final-board-inventory.json) | Saved PCB geometry and nominal body-clearance inventory |
| [Exported netlist](schematic-complete.net) | Input to the maintained connectivity checker |

The netlist checker was rerun after this cleanup: all 61 assertions pass. That checks the retained export; it does not establish that a later source edit matches it. The netlist source-location metadata uses a repository-relative path for publication.

Before relying on these records after a hardware change, compare the saved source hashes with `review-summary.json` and regenerate affected exports/checks through Konnect. Retain the source revision, tool version, check scope and unresolved findings with new results. Raw tool transcripts, duplicate renders and intermediate checkpoints belong in `.agent-scratch/`, unless needed to explain a specific unresolved issue.

`tools/check-netlist.py` reads the retained netlist. `tools/check-final-board.py` refreshes the inventory using KiCad's Python environment. See [tool instructions](../../tools/README.md). Manufacturing and powered-radio acceptance remain governed by the [acceptance checklist](../implementation/acceptance-checklist.md).

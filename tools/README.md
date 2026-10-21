# Engineering tools

Run these commands from the repository root. They are maintained project tools; agent-only scripts and intermediate outputs belong in ignored `.agent-scratch/`.

- `python tools/check-netlist.py`: checks the final exported netlist in `docs/verification/schematic-complete.net`. Uses the Python standard library.
- `python tools/tone-response.py`: runs the illustrative tone-chain model. Uses the Python standard library; see `docs/implementation/tone-response.md` for limitations.
- `python tools/check-final-board.py`: reads the saved PCB and refreshes `docs/verification/final-board-inventory.json`. Requires KiCad's Python environment with `pcbnew`. It does not save or change the PCB.
- `python tools/export-landscape-registration.py`: regenerates the landscape manufacturing geometry and manifest under `manufacturing/pcb/carvera-air/landscape-y-flip/`. Requires `gerbonara` and the existing manufacturing exports. This writes deliverables; run only when intentionally refreshing that package.

Generated reports describe the source revision used to generate them. Regeneration requires appropriate review before treating outputs as accepted manufacturing evidence.

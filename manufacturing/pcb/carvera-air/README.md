# Carvera Air PCB manufacturing

**Start with the [illustrated fabrication guide](../../../docs/pcb-fabrication-guide.md).**
Record physical results in the [attempt log](../../../docs/pcb-attempt-log.md).
Use [laser transparency transfer](../../../docs/pcb-laser-transparency-guide.md)
or the [sublimation trial](../sublimation/README.md) for the top legend.
The transparency test produced a sharp, clean transfer with easy alignment;
sublimation is untested. Both use a separate supported press setup.

## Sequence and files

Start with a 150 × 100 × 1.5 mm single-sided blank, bottom copper up,
150 mm along machine X. Keep jig XY at pocket lower-left / Anchor 1 and
J=(x+0.10,y+0.10). Flip x′=150−x, y′=y about the Y-parallel midline.
Withdraw all four setup-only PCB pins before machining; bed locators stay fixed.

| Run / action | Holding and reference | Next check |
| --- | --- | --- |
| [00 registration preparation](review-nc/00-registration-preparation.nc), only if needed | Jig absent; sacrificial wasteboard; blank-corner XY / copper Z0 | Four accepted jig holes |
| [10 bottom copper](review-nc/10-bottom-copper.nc) | Registered tape/CA bond; original copper Z0 + thorough map | Continuity/isolation |
| Coat/cure bottom, then [20 pad clearing](review-nc/20-bottom-mask-removal.nc) | Undisturbed seating; original copper zero/map; only tool-length setting in between | 111 clean pad openings |
| [50 holes](review-nc/50-bottom-holes.nc), before first flip | Zero aluminium floor with board removed; add backing; remount bottom up; no map | 111 electrical holes + four enclosure mounts; clean/deburr |
| Flip, coat/cure top, release and heat transfer | Register/bond/remove pins for coating; separate supported press afterward | Align transparency using drilled holes; inspect transfer and bottom pads |
| Conditional repeat of 50 | Restore floor-referenced bottom-up setup with backing; no map | Clear obstructed circuit/mounting holes only; skip if already clear |

Program numbers identify files, not an obligation to drill last. The proposed
pre-flip drilling order has not yet been physically run. Review/controller
preview and actual setup acceptance remain necessary. No routine perimeter cut
is needed on the finished-size blank.

## Editable source and settings

- [FreeCAD CAM](../../../mechanical/pcb/icom-ctcss-pcb-cam.FCStd): native
  operations/controllers and SetupSummary parameters. Recompute, save, export
  and verify affected jobs after changes; do not hand-edit NC depths.
- `native-exports/` and `cam-inputs.json`: native exports and derived machining
  geometry. Keep exports unmirrored; apply the face transform once in FreeCAD.
- [Registration drawing](registration.svg): independent jig-hole preparation;
  enclosure mounts are separate.

| SetupSummary alias | Default | Meaning |
| --- | ---: | --- |
| `BoardThickness` | 1.5 mm | Established board thickness |
| `SupportHeight` | 1.0 mm | Selected PCB underside height above aluminium floor |
| `Breakthrough` | 0.15 mm | Tool tip = support height − breakthrough |
| `MaskOvertravel` | 0.05 mm | Selected initial pad-tool spring overtravel |
| `MaskPassOffset` | 0 mm | Lower slightly only after inspecting pad clearing |
| `MaskRPM` / `MaskFeed` / `MaskPlunge` | 6000 / 400 / 200 | RPM and mm/min; Makera reference speeds |

Preserve original copper Z0/map through bottom coating and pad clearing. Disable
start options that probe a new surface or replace the map. Tool-length setting
must preserve that datum. Clean/inspect before lowering MaskPassOffset and
repeating; spring pressure is not a guaranteed removal depth. Complete pad
clearing before drilling; do not run the spring tip across open electrical holes.

After pad clearing, release the board, zero the aluminium floor, add backing
and remount bottom up. Selected support gives underside +1.00 mm, copper +2.50 mm
and minimum tip +0.85 mm. Every posted motion must stay above floor zero. A
different support height requires CAM updates and output checks. Do not apply
the copper map or recut jig holes. Use the same contract for conditional cleanup.

## Verification and handoff

Follow the [jig/CAM contract](../../../docs/implementation/pcb-jig-and-freecad-cam.md)
and [engineering tools](../../../tools/README.md). Use Robust MCP Server for
FreeCAD CAM work and Konnect for supported KiCad work. Preserve unsaved work
and source identity. Accept protected breakthrough, holder clearance, pad
exposure without copper damage, mask adhesion, hole/lead fit and electrical
continuity/isolation before assembly. CAD checks and physical runs are separate.

The [inventory preflight](../../../docs/verification/pcb-inventory-preflight.json)
has incomplete coverage. For electronic parts, use the
[DigiKey CSV](../digikey-board-parts.csv) and
[purchasing notes](../../../docs/digikey-board-parts.md).

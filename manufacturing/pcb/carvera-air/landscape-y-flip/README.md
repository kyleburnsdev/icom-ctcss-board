# Carvera landscape setup — Y-axis flip

Use this directory as one consistent CAM set for the requested setup: **150 mm along machine X, 100 mm along machine Y**. Coordinates below are CNC XY, measured from the board's lower-left corner. SVGs show the same frame with their usual screen Y-down display.

| File | Operation / purpose |
| --- | --- |
| `top-legend.gto` / `top-legend.svg` | Top legend exposure artwork; landscape, unmirrored |
| `top-legend-REGISTERED.svg` | Top artwork plus four blue hole/crosshair guides and board-frame guide |
| `bottom-copper-Y-FLIPPED.gbl` | Bottom copper, **already mirrored for the physical Y-axis flip** |
| `bottom-copper-Y-FLIPPED-REGISTERED.svg` | Bottom copper plus the same four blue registration-hole guides |
| `registration-holes.drl` | Four 4 mm holes for initial registration; same coordinate set before/after the specified flip |
| `bottom-electrical-holes-Y-FLIPPED.drl` | 111 electrical holes, aligned to the already-flipped bottom copper |
| `board-outline.gm1` | 150 × 100 mm perimeter; rectangle is unchanged by the flip |
| `manifest.json` | Transforms, artifact hashes and coordinate checks |

**Blue guides are setup geometry, not toolpaths or exposure artwork.** In the registered SVGs they are grouped as `REGISTRATION_GUIDES_DO_NOT_MACHINE`, separate from `PROCESS_ARTWORK`. Disable/exclude that group when generating a laser or milling job. CAM programs may flatten SVG groups/colors on import; the clean top SVG/Gerber is supplied for exposure once registration is established. The guide circles represent the actual 4 mm hole diameters. The dashed rectangle indicates the board frame, not an additional perimeter cut.

## Registration geometry

Hole centers: **(6,6), (144,6), (6,94), (144,94) mm**. Pitch is **138 mm along X and 88 mm along Y**, with 6 mm center-to-edge offsets. All four holes have 4 mm nominal diameter.

| Physical hole identity | Top XY mm | After Y flip, XY mm |
| --- | --- | --- |
| H1 | 6, 6 | 144, 6 |
| H2 | 6, 94 | 144, 94 |
| H3 | 144, 94 | 6, 94 |
| H4 | 144, 6 | 6, 6 |

Flip the board so left and right exchange, keeping the same board-centered Y axis and frame. The coordinate rule is **X′ = 150 − X, Y′ = Y**. Its mirror line is X=75 mm; this is not a rotation through 180°. Do not mirror the `Y-FLIPPED` files again. Do not independently auto-center or fit each layer to its artwork extents. Original portrait KiCad exports in `../native-exports/` are provenance files and must not be mixed into this transformed CAM set.

The registration-hole pattern is symmetric: matching holes alone cannot detect an incorrect flip or a 180° orientation mistake. Use the asymmetric **J1 pin-1 square land** as a second check: top-frame XY=(130,40), bottom-frame XY=(20,40). Keep a physical orientation mark on stock/fixture or use the documented connector/module orientation as well. The module's USB end faces machine −Y in this chosen landscape rotation.

Drill and prove the registration-hole/fixture setup before relying on it for the other side. Re-establish the same board frame after the flip; use a coupon/dry run to check that the planned pin-1 land and electrical holes register. The exported hole coordinates are exactly symmetric. Actual repeatability still depends on hole/pin clearance, fixture accuracy and machine setup; nominal geometry does not guarantee perfect physical alignment. Keep the board supported/located until all side-dependent operations finish rather than freeing the outline early.

## Manufacturing order

1. **Start with uncoated stock, copper side up.** Support the bare top substrate on the flat fixture/spoilboard. Establish the 150 × 100 mm frame, orientation mark and bottom-side XY setup. Prove the registration-hole/fixture arrangement on a coupon.
2. **Drill the four registration holes.** Use `registration-holes.drl`; their coordinate set is identical on both sides. Remove drilling burrs/chips, reseat the board flat if disturbed, and establish the surface-height reference/leveling for isolation. Registration drilling must not leave debris or burrs affecting support or probing.
3. **Mill bottom copper isolation.** Use `bottom-copper-Y-FLIPPED.gbl` without another mirror. Complete the isolation passes while the supporting top surface is still bare and flat.
4. **Drill the 111 electrical holes.** Use `bottom-electrical-holes-Y-FLIPPED.drl`. J5 is a two-pin bypass header; J6 is a four-pin LED header with individual ground returns. R16 and the OFF/A0 circuit are removed. If an oversized blank needs perimeter machining, do that mechanical work now while retaining tabs or a fixture arrangement that preserves the board frame for the top operation. An already-sized blank may not require an outline cut. Do not release the board from its locating features yet.
5. **Deburr, clean and inspect the bare board.** Check isolation, copper bridges, hole fit, registration, net continuity and unwanted connections before spending time on the coatings. Resolve copper defects now. Protect the finished lands/traces during subsequent handling.
6. **Flip about Y and re-register top-side up.** Left/right exchange. Confirm the four holes and asymmetric orientation check. Support the finished copper side without damaging raised lands or loading unsupported traces; re-establish the laser's top-surface reference/focus for the actual coating setup. Do not carry the bottom milling Z reference into laser setup.
7. **Apply the top UV-mask legend.** Apply/flood-cure the background, apply the contrasting layer, selectively cure the clean top legend artwork, then clean off uncured material. Keep registration/electrical holes clear. The blue registration guides are setup aids and remain excluded from exposure/toolpaths.
8. **Finish and inspect.** Once both sides are complete, release retained tabs/fixture as appropriate, clean the edges and holes, inspect the legend and copper, and repeat bare-board continuity/short checks before assembly. Plan final separation so it does not require another copper-isolation setup against the coated top face.

This order keeps both top coating layers out of the support stack during precision trace milling. Any copper rework discovered after coating needs a separate support/leveling plan; do not simply resume the earlier isolation job with the coated face resting on the spoilboard.

These are geometry derivatives of the parent exports, not machine G-code. The [parent instructions](../README.md) still govern stock, tooling, coatings and process validation. The transformation script reads exported Gerber/drill files only; it does not alter KiCad sources. Rebuild from the repository root with `python tools/export-landscape-registration.py` (requires `gerbonara`).

## Makera Studio project

Open `ctcss-board-cam.mkc` in Makera Studio. Keep it alongside all imports in this directory. The archive passes ZIP integrity inspection. On 2026-10-21, the project owner verified that the relocated project opened correctly in Makera Studio with its layers intact. For publication, absolute import-name prefixes were removed from archive metadata; embedded `makera.bin` geometry remains unchanged. After metadata cleanup, the project owner successfully reopened the sanitized archive and confirmed that its layers looked correct on 2026-10-21. If Studio requests source files on another machine, select the matching files in this directory and save the project here. Confirm imported geometry, orientation, tools and job settings in Studio before machining.

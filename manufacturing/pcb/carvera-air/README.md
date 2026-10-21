# Single-sided CNC review package

**Control cleanup complete:** J5 is a two-pin BYPASS/GND connector; J6 retains four LED contacts. The OFF/A0 switch circuit and R16 are removed. These regenerated files, the BOM and the [wiring table](../../../docs/implementation/assembly-and-bring-up.md#j5j6-cable-wiring) describe the same revision. The unit remains powered with the radio.

**For the user's 150 mm X × 100 mm Y landscape setup and left/right Y-axis flip, use the [landscape CAM set](landscape-y-flip/README.md).** It includes registered top/bottom SVGs with all four mounting holes. Its bottom copper and electrical drills are already mirrored for that flip; do not mirror them again. The files listed below remain the original portrait exports and must not be mixed into that transformed set.

This is a geometry package for CAM review and a test coupon, **not approved machine G-code**. Target equipment is the user's **Makera Carvera Air with PCB kit and laser accessory**, using 1.5 mm single-sided copper-clad stock, components above and copper below. The top legend is included for the user's contrasting UV solder-mask process.

| File | Use |
| --- | --- |
| `native-exports/icom-ctcss-board-B_Cu.gbl` | The only physical copper layer |
| `native-exports/icom-ctcss-board-Edge_Cuts.gm1` | 100 × 150 mm board perimeter |
| `native-exports/icom-ctcss-board-PTH.drl` | 111 electrical holes: 48 at 0.9 mm, 63 at 1.1 mm |
| `native-exports/icom-ctcss-board-NPTH.drl` | Four 4 mm mounting holes |
| `native-exports/icom-ctcss-board-F_Silkscreen.gto` | Positive top legend artwork, plotted from F.SilkS |
| `native-exports/icom-ctcss-board-top-legend.svg` | Same legend converted from that Gerber; transparent 100 × 150 mm page for laser preparation |

**All holes are physically unplated**, including the CAD file named PTH. Use both drill files. Physical copper remains B.Cu only; the top legend is a separate coating/laser operation, not top copper. No F.Mask/B.Mask aperture layer is supplied: the full top background coat is defined by the physical board, and the contrasting legend by F.SilkS. KiCad's native through-hole representation includes virtual top lands; all-layer default plots and diagnostic IPC-2581 exports must not replace this selected-layer package.

Current connector revision: **two-pin J5 and four-pin J6**, providing individual signal/ground pairs for one bypass toggle and two LEDs. Use the [wiring table](../../../docs/implementation/assembly-and-bring-up.md#j5j6-cable-wiring). These files supersede the earlier three-pin layouts and the four-pin J5 OFF/A0 revision; do not mix old copper, drilling or legend files with this revision.

## Top legend and UV solder-mask process

Complete bottom copper isolation, all drilling, deburring and bare-board electrical inspection **before applying either top coating**. Keep the top substrate bare and flat while it supports the board during isolation milling. Then flip about Y, re-register, and carry out the coating/UV/laser sequence. The [landscape manufacturing order](landscape-y-flip/README.md#manufacturing-order) defines the setup and handling sequence. No further copper-isolation operation is planned after coating.

The user-defined sequence is: coat the top substrate with a background UV solder-mask color, flood-cure it, apply a contrasting color, selectively cure the legend with the laser, then clean away uncured material. Black strokes/areas in the SVG identify **legend material to retain**, not material to remove. The SVG has no opaque background, board-edge cutting line, fabrication-layer overlays or drill marks. Do not invert it into a full-board exposure unintentionally.

The top artwork is **unmirrored**, viewed from the component side. The SVG page is exactly 100 × 150 mm and preserves the board crop (KiCad X=50–150, Y=50–200); keep that full page and register it against the board/fixture. Gerber coordinates remain shared with the outline/drills. Do not auto-fit to artwork bounds or use the mirrored bottom preview to position the top legend. Verify scale, orientation and registration in the actual laser software before processing.

The manufacturing Gerber excludes native footprint reference/value fields (`--exclude-refdes --exclude-value`), which otherwise duplicate labels and account for the 34 footprint-owned overlap warnings. The larger board-level references, values, pin functions, socket map and block labels remain, together with F.SilkS footprint artwork. The saved CAD warnings remain documented; this is an explicit plot policy rather than a source-design warning suppression. The clean Gerber-derived [preview](../../../docs/reference/top-legend-clean.svg) was inspected separately from the assembly drawing.

Render SVG stroke widths as physical exposed areas; a centerline engraving import is not equivalent to the supplied stroke widths. Some footprint strokes are 0.12 mm wide, so prove the smallest lines/text, color contrast, coating adhesion, cleaning and registration on a coupon with the actual resin and laser. Wavelength compatibility, exposure/dose, speed/power and cleaning chemistry have not been established here. No laser settings or machine G-code are supplied.

## Bottom copper and drilling

The default Gerber job metadata is excluded: it carries generic two-layer/1.6 mm stackup and nominal rule values, which do not describe this 1.5 mm single-sided CNC blank. This README and the actual selected copper/outline/drill geometry define the review package.

Gerbers and drills use common absolute metric board coordinates. The mirrored [bottom preview](../../../docs/reference/copper-bottom.svg) is a viewing aid. Establish the correct bottom-side machining transform in CAM using an asymmetric pin-1 feature and the mounting holes; avoid mirroring twice. Keep drill/copper/outline registration together. Verify dimensions at 1:1 scale.

Design geometry: 0.5 mm minimum copper clearance; 0.5 mm signal and 1 mm power/ground tracks; 2 mm ordinary lands and 3 mm test-point lands. No routing vias, wire jumpers or pours. The selected Q1 is the factory-formed 2N3904RLRAG; straight-lead substitutes do not match its footprint.

Available cutters are 30°/0.2 mm-tip and 60°/0.1 mm-tip V-bits. Confirm actual 0.9/1.1/4 mm drilling capability, copper thickness, runout, flatness and hold-down. Establish depth, feeds, isolation passes and outline cutting on scrap; inspect copper removal, pads, hole fit and continuity. No cutting depth or feed is approved by this package. If a matching drill is unavailable, review interpolation and minimum feature capability before cutting.

Use the [assembly drawing](../../../docs/reference/assembly-top.svg), [BOM](../../../docs/reference/bom.csv), [assembly procedure](../../../docs/implementation/assembly-and-bring-up.md) and [acceptance checklist](../../../docs/implementation/acceptance-checklist.md). Use the dedicated top-legend files for laser preparation; the assembly drawing also includes fabrication details and is not the exposure artwork.

The [current export manifest](native-exports/manifest.json) records saved-source hashes, selected files, drill counts and validation scope for the bypass-only cleanup. The [landscape manifest](landscape-y-flip/manifest.json) records the transformed artifacts and registration checks.

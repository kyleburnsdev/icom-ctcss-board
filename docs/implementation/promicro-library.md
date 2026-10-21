# Biacco42 ProMicro library adoption

Selected by the user on 2026-10-20. Source: https://github.com/Biacco42/ProMicroKiCad, commit `96404fc297aa4b3009f8e2e2b69e1c1abed35538`. Unused upstream files are not redistributed. The required project adaptation remains in `electronics/libraries/Biacco42_ProMicro.pretty/`; its [license notice](../../electronics/libraries/LICENSE-ProMicro.txt) is retained. Retrieve the original files from the linked upstream commit. MIT attribution: copyright 2017 Biacco42, with attribution to Ricardo Band's 2015 teensy library as recorded in upstream LICENSE.

## Registered footprint

Use **`Biacco42_ProMicro:ProMicro`**. The project-local library URI is `${KIPRJMOD}/libraries/Biacco42_ProMicro.pretty`, verified by Konnect library listing.

Konnect refuses inspection of the upstream pre-KiCad-6 `(module ...)` format. A modern-format adaptation was therefore written exclusively through Konnect library tools. It preserves all 24 upstream pad numbers, coordinates, sizes (1.6 mm), drills (1.1 mm), square pad 1/circular remaining pads, and front/back outline segments. Upstream's obsolete pad-layer token F.SilkS was omitted from the pad layer set; pads use *.Cu and *.Mask. Konnect generated visible reference/value fields, a chamfered fab body and a courtyard; the courtyard was expanded to include the upstream USB projection. This is an adaptation of the selected public footprint, not a newly designed pin layout.

Readback confirmed **2.54 mm pitch**, **15.24 mm row spacing**, **27.94 mm first-to-last span**, and all 24 upstream pad geometries. The exported library preview was visually inspected for two rows, square pad 1, USB end, outlines and drill openings. Duplicate previews and raw readbacks are no longer maintained; the accepted map below and required project library retain the design information.

## Physical map to use for symbol integration

Footprint-local component/top view: USB projects toward **negative X**. Pad 1 is at the USB end of the +Y row. Pads 1–12 progress toward +X; pads 13–24 return toward −X on the −Y row. Rotating USB to the top places pad 1 on the left and pad 24 on the right. Functional assignments follow the upstream symbol, checked against the photographed module legends and seller-photo transcription; these are module header numbers, not MCU chip leads. VCC/RAW/RST obscured in the actual photo retain the stated seller-evidence limitation.

| Pad / intended symbol pin | Module function | Local X mm | Local Y mm |
| --- | --- | --- | --- |
| 1 | TX/D1 | -13.97 | 7.62 |
| 2 | RX/D0 | -11.43 | 7.62 |
| 3 | GND | -8.89 | 7.62 |
| 4 | GND | -6.35 | 7.62 |
| 5 | SDA/D2 | -3.81 | 7.62 |
| 6 | SCL/D3 | -1.27 | 7.62 |
| 7 | D4 | 1.27 | 7.62 |
| 8 | D5 | 3.81 | 7.62 |
| 9 | D6 | 6.35 | 7.62 |
| 10 | D7 | 8.89 | 7.62 |
| 11 | D8 | 11.43 | 7.62 |
| 12 | D9 | 13.97 | 7.62 |
| 13 | D10 | 13.97 | -7.62 |
| 14 | D16/MOSI | 11.43 | -7.62 |
| 15 | D14/MISO | 8.89 | -7.62 |
| 16 | D15/SCK | 6.35 | -7.62 |
| 17 | A0 | 3.81 | -7.62 |
| 18 | A1 | 1.27 | -7.62 |
| 19 | A2 | -1.27 | -7.62 |
| 20 | A3 | -3.81 | -7.62 |
| 21 | VCC | -6.35 | -7.62 |
| 22 | RST | -8.89 | -7.62 |
| 23 | GND | -11.43 | -7.62 |
| 24 | RAW | -13.97 | -7.62 |

Counts: 24 module header contacts, 24 unique footprint pads, three separate GND contacts (3,4,23), no duplicate pad numbers. The upstream symbol labels several pins with AVR port names; Arduino logical names above must be used when wiring. Its RAW pin is incorrectly typed power_out for our use and VCC is power_in; do not reuse that symbol unchanged as the regulator/source model for this project.

## Remaining integration checks

Final board caveat: KiCad normalizes THT lands to both copper sides despite the derivative's library layer request. The CNC package exports B.Cu only; see [native pad/export evidence](pcb-layout.md#native-tht-pad-representation). References below to bottom-only pads describe library intent and physical fabrication, not absence of virtual F.Cu lands in the saved board.

Integration is now complete in the saved schematic. U1 uses `CTCSS:Teyleten_ProMicro_5V` and `CTCSS_THT:ProMicro_CNC_BCu`, the bottom-only CNC derivative of this approved source. The derivative preserves all24 nominal centers and numbering, enlarges pads to2.0mm with1.1mm drills, and retains the source's square pad1/USB-end artwork. The original registered adaptation remains unchanged for provenance. See [accepted physical maps](physical-pin-maps.md) for all symbol types and disposable acceptance evidence.

The earlier `GetOpenDocuments (AS_UNHANDLED)` failure was traced to a closed PCB editor. With the root editor running, disposable closed-file board placement, rendering and independent IPC-2581 readback succeeded. The saved-file `get_component_pads` reader still fails to locate modern property-format U1 even though KiCad exports show it; acceptance therefore uses the exporter-derived Component/package/pad record, not a repeated placement or direct file edit. Source and CNC disposable renders have both been visually inspected.

The upstream outline is about30.48×17.78mm excludingUSB projection and does not represent the user's approximate37×18mm USB-C clone envelope. Preserve nominal pad centers, but expand assembly/USB keepouts during layout; do not treat this courtyard as a verified clone/socket/cable envelope. The CNC derivative's B.Cu-only2.0mm pads around1.1mm drills give0.45mm nominal annular rings and0.54mm adjacent copper gap. Actual socket pin fit, drill tolerance, cable access and hand-solder clearance remain physical acceptance checks. User approved nominal2.54mm pitch/15.24mm rows over imprecise measurements; do not re-block that accepted geometry.


A later manager/editor IPC collision also produced AS_UNHANDLED while the PCB editor was running. Gracefully closing the manager/editor and reopening the saved board directly restored exact-board IPC access. A healthy Ping alone does not prove GetOpenDocuments/PCB mutation support; check open_project against the full requested board path before writing.

# Teyleten module seller-image evidence

Retrieved 2026-10-20 from the [Teyleten Robot product listing](https://www.amazon.com/dp/B0B6HYLC44), ASIN B0B6HYLC44. The listing title matches the module named in the board specification. Seller images describe the advertised product; they do not prove the dimensions or wiring of a particular delivered board.

| Seller asset identifier (local copies removed) | Original seller asset | Observed use |
| --- | --- | --- |
| teyleten-seller-PT01.jpg | https://m.media-amazon.com/images/I/71OI8alz-9L._AC_SL1500_.jpg | Oblique top view with pin legends and USB-C connector |
| teyleten-seller-PT02.jpg | https://m.media-amazon.com/images/I/71wE4gRpLSL._AC_SL1500_.jpg | Opposite top view, useful for reading power/analog row |
| teyleten-seller-PT03.jpg | https://m.media-amazon.com/images/I/61NG9BSBoXL._AC_SL1500_.jpg | USB-C connector view |
| teyleten-seller-PT04.jpg | https://m.media-amazon.com/images/I/71pjPdXa1tL._AC_SL1500_.jpg | Bottom view; do not transpose its mirrored geometry into a top-view pad map |
| teyleten-seller-PT05.jpg | https://m.media-amazon.com/images/I/61cJSUs1uvL._AC_SL1500_.jpg | REJECTED: depicts an ATmega328P Pro Mini circuit, not the advertised ATmega32U4 Pro Micro |

## Header legend transcription

### Actual module measurements supplied by the user

On 2026-10-20, the user measured the available module with calipers and reported a board width of **18 mm**, length of **37 mm**, and **15 mm center-to-center header row spacing**. Measurement tolerance and whether the length excludes USB-C overhang were not specified. The breadboard fit supports a nominal 2.54 mm pin grid; six grid intervals would give 15.24 mm row spacing, consistent with an approximately 15 mm reading but not yet established as an exact measured value. First-to-last hole span, pad-to-edge offsets, and USB-C overhang remain unmeasured.

Initial Konnect lookup of `Module:Arduino_Pro_Micro` failed: it is absent from the installed KiCad 10 Module library. A registered-library search for `Pro_Micro` also returned no matches. The user subsequently selected the public Biacco42 footprint. It is now registered as `Biacco42_ProMicro:ProMicro`; see [adoption and verified nominal dimensions](../implementation/promicro-library.md). The user explicitly prefers nominal specification dimensions over their approximate measurements unless a gross discrepancy appears. The adopted 2.54 mm pitch and 15.24 mm row spacing are consistent with the breadboard fit and approximately 15 mm measurement.

The user also supplied the seller schematic shown in PT05 above. Inspection of that supplied image confirms U4 is labeled **ATMEGA328P-AU**, with a 17×2 header and a Pro Mini filename in the title block. It remains excluded as evidence for the specified ATmega32U4 USB-C module.

The user subsequently supplied a component-side photograph of the actual module, installed in a breadboard with USB at the bottom of the image. Visible legends include TX0/RX1, two GND positions, digital pins 2–9, VCC, A3–A0, and 15/14/16/10; the crystal is marked 16.000 MHz. Rotating this view 180 degrees to put USB at the top makes the visible header order consistent with the seller-photo transcription below. Some power/reset legends and the processor marking are obscured or insufficiently legible; the photograph alone does not independently establish those connections, the processor identity, or the 5 V variant. Perspective and solder coverage prevent a precision socket-spacing measurement from this image.

View: component/top side, USB-C connector at the top, looking down onto the module. Each table row advances away from USB. These are printed functional labels, not an accepted KiCad pad numbering scheme.

| Position from USB | Left header legend | Right header legend |
| --- | --- | --- |
| 1 | TX0 | RAW |
| 2 | RX1 | GND |
| 3 | GND | RST |
| 4 | GND | VCC |
| 5 | 2 | A3 |
| 6 | 3 | A2 |
| 7 | 4 | A1 |
| 8 | 5 | A0 |
| 9 | 6 | 15 |
| 10 | 7 | 14 |
| 11 | 8 | 16 |
| 12 | 9 | 10 |

The seller photos support the functional header order. They do not establish center-to-center row spacing, exact outline/USB overhang, maximum component height, regulator rating, or internal power-path topology. Do not infer a dimensioned mechanical drawing from perspective photographs. The unrelated seller schematic is excluded from electrical evidence, including power-path and USB backfeed reasoning.

Before fabrication, measure the actual module against the selected footprint and sockets, confirm the printed order, and check the USB cable envelope and powering procedure. Complete the accepted symbol-pin/footprint-pad map and rendered inspection separately.

# Third-party sources and required library notices

The root MIT license covers original project contributions. Required third-party library material retains its upstream terms.

## Required editable libraries

- Pro Micro adaptations derive from [Biacco42/ProMicroKiCad](https://github.com/Biacco42/ProMicroKiCad/tree/96404fc297aa4b3009f8e2e2b69e1c1abed35538), copyright 2017 Biacco42, incorporating work copyright 2015 Ricardo Band. The [MIT notice](../electronics/libraries/LICENSE-ProMicro.txt) is retained. Project adaptations modernize the footprint format and enlarge CNC pads; see [provenance and pin map](implementation/promicro-library.md). Unused upstream distributions are omitted.
- Other CNC footprint adaptations derive from the [KiCad community footprint libraries](https://gitlab.com/kicad/libraries/kicad-footprints). Their [library license and design exception](../electronics/libraries/LICENSE-KiCad.md) and [CC BY-SA 4.0 terms](https://creativecommons.org/licenses/by-sa/4.0/legalcode) are retained. The stock-derived footprint adaptations in `electronics/libraries/CTCSS_THT.pretty/`, excluding the Pro Micro footprint covered above, are distributed under those terms. Changes include larger pads/drills, selected layer requests and process-specific outlines; see [footprint details](implementation/footprint-review.md). The MIT license does not replace these library terms.

## External reference material

Manufacturer PDFs, extracted pages and seller-image copies are not included in the public snapshot. [Accepted physical maps](implementation/physical-pin-maps.md) link to the onsemi, Bourns and WIMA sources with document/page references. [Seller-source notes](reference/teyleten-source-notes.md) link to original image assets and preserve the accepted header transcription. Those external works retain their owners' rights.

# Third-party sources and required library notices

The root MIT license covers original project contributions. Required third-party library material retains its upstream terms.

## Required editable libraries

- Pro Micro adaptations derive from [Biacco42/ProMicroKiCad](https://github.com/Biacco42/ProMicroKiCad/tree/96404fc297aa4b3009f8e2e2b69e1c1abed35538), copyright 2017 Biacco42, incorporating work copyright 2015 Ricardo Band. The [MIT notice](../electronics/libraries/LICENSE-ProMicro.txt) is retained. Project adaptations modernize the footprint format and enlarge CNC pads; see [provenance and pin map](implementation/promicro-library.md). Unused upstream distributions are omitted.
- Other CNC footprint adaptations derive from the [KiCad community footprint libraries](https://gitlab.com/kicad/libraries/kicad-footprints). Their [library license and design exception](../electronics/libraries/LICENSE-KiCad.md) and [CC BY-SA 4.0 terms](https://creativecommons.org/licenses/by-sa/4.0/legalcode) are retained. The stock-derived footprint adaptations in `electronics/libraries/CTCSS_THT.pretty/`, excluding the Pro Micro footprint covered above, are distributed under those terms. Changes include larger pads/drills, selected layer requests and process-specific outlines; see [footprint details](implementation/footprint-review.md). The MIT license does not replace these library terms.

## External reference material

`tools/post/makera_legacy_post.py` is the unmodified OEM FreeCAD postprocessor
from MakeraInc/CarveraProfiles commit `de08a657bdc9c230a094dbdba792acd70bfcdf32`,
SHA-256 `a5a10005b6e40caf6563937c328f2e99da168805fc7f819948e72bf8c2c8b115`.
Its copyright/LGPL header is retained, with license text in
`tools/post/LICENSE-LGPL-2.1-or-later.txt`. This license is separate from the
project's MIT license. The retained OEM tool definition and source links are
documented in the [PCB manufacturing package](../manufacturing/pcb/carvera-air/README.md).

Manufacturer PDFs, extracted pages and seller-image copies are not included in the public snapshot. [Accepted physical maps](implementation/physical-pin-maps.md) link to the onsemi, Bourns, KEMET, TDK and Vishay sources with document/page references. [Seller-source notes](reference/teyleten-source-notes.md) link to original image assets and preserve the accepted header transcription. Those external works retain their owners' rights.

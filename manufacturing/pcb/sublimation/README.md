# White-mask sublimation experiment

**Start with the [illustrated guide](../../../docs/pcb-fabrication-guide.md)**
and [trial log](../../../docs/pcb-attempt-log.md).
Branch `feature/sublimation-silkscreen`; physical acceptance pending.

[Laser transparency transfer](../../../docs/pcb-laser-transparency-guide.md)
is a sibling press method with a user-reported sharp, clean result at
330 °F / 60 s / heavy pressure and a refrigerated cold peel. Its recipe and
printer orientation are separate from this sublimation trial.

| Print file | Editable source | Actual artwork field |
| --- | --- | --- |
| [Top / Letter PDF](top-color-letter.pdf) | [Top SVG](top-color.svg) | 100 × 150 mm portrait |
| [Coupon / Letter PDF](transfer-coupon-letter.pdf) | [Coupon SVG](transfer-coupon.svg) | 54 × 38 mm; six colors, fine lines, F L |

**Positive artwork. No transfer mirroring applied; your printer mirrors
automatically. File/application mirror OFF.** Print Actual size / 100%, no Fit,
Letter, simplex. Measure crop-mark spans on a proof, then trim page furniture
away. Transparent SVG regions expose the white mask. PDFs show the same ink.
The artwork is **top only**. Bottom subsystem notes duplicated information now
available on top and in the guide, so the bottom artwork and transfer step have
been removed. Leave bottom white mask and pad openings as prepared.

Printer/ink: user-supplied converted Epson E-15000 / Cosmos Ink. Foundation:
Mechanic white UV solder mask. Run the coupon first: **185 °C / 365 °F, 60 s,
light pressure, warm peel around 40–50 °C** is the selected starting experiment,
not a Mechanic-rated process. The [application procedure](../../../docs/pcb-fabrication-guide.md#flow-b-sublimation-untested-trial)
gives the press-stack drawing, heat-tape arrangement, temperature/dwell ladder,
pressure/peel comparisons and failure responses. Product-specific physical
acceptance remains open. See the
[equipment/process record](../../../docs/implementation/pcb-sublimation-trial.md).
Use the user's assumed **generic 12 × 12-inch clamshell T-shirt press**; its
nominal 304.8 × 304.8 mm platen accommodates this board. No exact model is needed
to proceed with coupon testing. Record the actual pressure-control position,
temperature and dwell used. Use one firm silicone lower support pad, fresh
blowout paper above/below the assembly, and an optional thin PTFE upper cover.
Keep ink directly against mask; tape edges against movement before heating.

Use [Carvera review outputs](../carvera-air/README.md) 00 if needed, 10, 20 and
50 with the guide's transitions. Retain copper zero/map through pad clearing; transfer off the jig
after top coating. Drill before the first flip using the floor datum so holes
can aid alignment; repeat only if obstructed after top work. The proposed order
is unrun. Native CAM is unchanged.

Named SVG groups retain existing text with color cues and a boxed guide to
TP1–TP8 above the Pro Micro. It replaces the decorative waveform and identifies
probe return, supply rails, raw PWM, filtered tone, audio mix and PTT input/output.
No invented polarity/tolerance/high-voltage claims or QR destinations.
The top subtitle is **SELECTABLE CTCSS | 5V PRO MICRO**; manufacturing notes are
kept in the documentation. `source/` holds the native KiCad-plotted top derivative,
including this subtitle change, without changing the original monochrome PCB.
KiCad remains authoritative for circuitry/placement; color art is a derivative.
[Regeneration](../../../tools/README.md) overwrites generated SVG/PDF files;
maintain intended changes in the generator. [Hash evidence](../../../docs/verification/pcb-sublimation.json).
[Print QA](../../../docs/verification/pcb-sublimation-print-qa.json) records
document dimensions, source identity and visual inspection.

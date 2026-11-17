# IC-229H mounting interface

Current enclosure: C1. Dimensions below are millimetres. The radio is the
IC-229H; do not substitute the shorter A/E chassis depth.

| Interface | Value | Basis |
| --- | --- | --- |
| Nominal radio body W × H × D | 140 × 40 × 155 | Icom instruction manual, specifications, printed page 43; excludes projections |
| First side-hole center behind faceplate flat | 39 | User measurement, 2026-11-17 |
| Second side-hole center behind the same flat | 88 | Calculated: 39 + user-supplied 49 center spacing |
| Side-hole height above chassis bottom | 20 | User measurement, 2026-11-17 |
| Pattern | Two holes on each side, same height | User description and supplied photos |
| OEM mounting bracket | MB-27; service part 8010005180 | Icom instruction manual unpacking list; service manual §5-2, item 52 |
| OEM radio mounting bolt | 8820000530, quantity four | IC-229A/E/H service manual §5-2, item 54 |
| Bolt size | M4 × 8, flange bolt | **Part-number inference:** another Icom service manual explicitly identifies 8820000530 as M4 × 8 |
| Maximum safe insertion depth | Not specified in the reviewed material | Must not be inferred from the 8 mm under-head bolt length |

The IC-229 manual's M5 × 12 and M5 × 16 accessory screws are **bracket-to-vehicle
hardware**, not evidence for M5 chassis threads. The manual's 5.5–6 mm mounting
drill suggestion likewise concerns mounting the bracket to its supporting surface.

## Documents reviewed

- [Icom's official IC-229A/E/H instruction-manual page](https://www.icomjapan.com/support/manual/2842/).
- [Icom America manual and support article](https://icomamericasupport.zendesk.com/hc/en-us/articles/35050324595348-IC229A-229H-Instruction-Manual-and-FAQs).
- [Icom-authored instruction-manual scan](https://www.radioamatore.info/attachments/1332_IC-229_user_manual.pdf): unpacking on printed page ii, mounting on page 7, dimensions on page 43. MB-27 and an angle-adjustable mounting arrangement are shown, without a dimensioned side-hole drawing.
- [Icom-authored service-manual scan](https://www.radiomanual.info/schemi/ICOM_VU/IC-229A_E_H_serv.pdf): §5-2 on printed page 5-1 (PDF page 12), exploded assembly/accessories on 5-2 (PDF page 13). The drawings are illustrations, not scale drawings of the hole pattern.
- [Icom IC-M803 service manual](https://www.radiomanual.info/schemi/Surplus_Civil/Icom_IC-M803_serv_2020.pdf): mechanical parts, chassis item MP3009, explicitly identifies **8820000530 — FLANGE BOLT M4 × 8 NI**.

No dimensioned manufacturer drawing establishing the 39/49/20 pattern was found.
Those dimensions remain the established user inputs, independent of the manual
search. The part-number match establishes a well-supported M4 × 8 design choice;
it does not establish an unused blind-thread depth or an arbitrary longer bolt.

## C1 application

Use M3 × 8 socket-head cap screws for enclosure joints. Retain the radio's OEM
M4 × 8 interface as a documented exception; M3 screws cannot engage its M4 thread.
C1 provides 4.4 mm clearance holes in 3 mm printed cheeks, with 0.3 mm clearance
between cheek and radio. An 8 mm bolt would project **4.7 mm** past that interface.
Trial the actual OEM bolt in an unpowered, supported radio; it must clamp the
cheek before bottoming. Add a suitable printed grip spacer or revise cheek
thickness if needed to reproduce the original bracket's exposed bolt length.
Do not force a bolt or use the bolt to pull a misaligned bracket into place.

The separate C1 radio-pattern coupon reproduces the 49 mm pitch and 39 mm front
datum; its hole centers are 15 mm from the coupon edge, **not** a chassis-height
datum. The drawing in the C1 guide carries the actual 20 mm chassis height.

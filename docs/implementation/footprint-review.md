# CNC footprint review

All 38 schematic components now use 12 project-local `CTCSS_THT` footprint types, written only through Konnect. The nominal pad centers/numbering come from the specified stock libraries and user-approved Biacco42 library. Pads were enlarged for single-sided CNC isolation milling. The project-local libraries preserve the actual pad centers, drills, sizes, layer sets and graphics; the retained [netlist](../verification/schematic-complete.net) records schematic footprint assignments. Raw readback transcripts are no longer maintained.

| Footprint / use | Pitch mm | Pad diameter mm | Drill mm | Nominal minimum annular ring mm | Adjacent pad copper gap mm |
|---|---:|---:|---:|---:|---:|
| R_P5.08_CNC / R1–R15 | 5.08 | 2.0 | 0.9 | 0.55 | 3.08 |
| C_Disc_P2.5_CNC / C1,C2,C4,C5 | 2.50 | 2.0 | 0.9 | 0.55 | 0.50 |
| C_Film1u_P5_CNC / C3 | 5.00 | 2.0 | 0.9 | 0.55 | 3.00 |
| C_Film4u7_P5_CNC / C6 | 5.00 | 2.0 | 0.9 | 0.55 | 3.00 |
| Q_TO92_Formed_CNC / Q1 | 2.54 | 2.0 | 0.9 | 0.55 | 0.54 |
| RV_3296W_CNC / RV1 | 2.54 | 2.0 | 0.9 | 0.55 | 0.54 |
| Header_1x02/04/05/08_CNC / J1–J6 | 2.54 | 2.0 | 1.1 | 0.45 | 0.54 |
| ProMicro_CNC_BCu / U1 | 2.54; rows15.24 | 2.0 | 1.1 | 0.45 | 0.54 |
| TP_CNC / TP1–TP8 | single | 3.0 | 1.1 | 0.95 | placement dependent |

Pad 1 is square, other pads circular. The listed ring is the minimum distance from a round drill to a square/circular copper edge. Library pad copper requests **B.Cu only**; B.Mask is CAD metadata and no physical soldermask is assumed. Native KiCad board readback nevertheless shows 111 normalized THT lands on both F.Cu and B.Cu. Only the explicitly selected bottom-copper export is authorized for this single-sided blank; see [layout/export caveat](pcb-layout.md#native-tht-pad-representation). Parts mount on top. KiCad places the electrical holes in a plated-drill category; CNC fabrication uses ordinary **unplated** drilled holes in the 1.5mm single-sided blank. Never infer physical plating or a second copper side from that category.

Supported source silk/fab/courtyard geometry is retained; the initial generated placeholder geometry was replaced through Konnect. Library 3D models were not copied; no 3D-fit claim is made. Pin-1 square pads and fab/socket orientation must also appear on the assembly drawing/physical top marking. The required Biacco42 adaptation and upstream license notice are retained; unused upstream copies are replaced by source links. Its final CNC derivative changes pad sizes/layers, not pin centers or numbering.

## Bodies and handling allowances

- Resistor bodies are the specified horizontal DIN0204 envelope, 3.6×1.6mm. Buy actual parts fitting that body/lead pitch; larger 1/4W bodies need a different footprint, not forced leads.
- C1/C2/C4/C5 use the specified 3×2mm disc envelope at2.5mm pitch. Buy 100nF parts rated at least25V that fit; the drill accepts leads up to the selected gauge with clearance. A larger purchased disc must be reviewed.
- C3 WIMA MKS2C041001F00KSSD:7.2×5mm body,10mm height,5mm pitch,0.5mm wire. C6 WIMA MKS2C044701O00KSSD:7.2×11mm body,18mm height,5mm pitch. Both unpolarized.
- Q1 is **factory-formed** onsemi2N3904RLRAG, not straight-lead bulk2N3904G.2.54mm pitch is within the manufacturer's bent-lead2.4–2.8mm range; max body about5.2×4.19mm. No beginner hand-forming against the body is required.
- RV1 Bourns3296W-1-103LF:9.53×4.83mm, top screw access near lead1; reserve screwdriver room.
- Headers are standard2.54mm single rows. The1.1mm drill nominally clears a0.64mm square pin's0.905mm diagonal. Module sockets require actual selected socket pin fit; keep two socket bodies and all populated parts at least2mm apart.
- U1 retains Biacco42 centers but reserve at least the user's approximate37×18mm clone outline, plus socket bodies and USB-C cable clearance. Source footprint outline is smaller and is not the final populated envelope.

The0.5mm gap is a geometric design target, not proof that a particular V-bit/depth produces clean isolation. User tools are30°/0.2mm and60°/0.1mm V-bits plus assorted drills. Confirm drill sizes, copper thickness, flatness, runout, depth and a test coupon before machining. CAM must preserve enlarged solder lands and avoid islands/copper slivers. First-board acceptance includes soldering-iron access, component-body spacing and external readable markings.

## Evidence and limitations

Library query-back confirms all12 types request only B.Cu copper pads; native board normalization is described above. Disposable module/RV/Q variants were rendered and inspected, with instance IPC-2581 readback; see [physical maps](physical-pin-maps.md). Root layout and assembly drawing are now complete; see [layout evidence](pcb-layout.md). Unplated-drill CAM review and physical fit remain outstanding. A clean schematic/ERC does not establish machining readiness.

J5 uses the 1x02 CNC variant for one bypass pair; J6 uses 1x04 for two LED pairs. Return contacts are tied on-board. Twelve project-local footprint types are used by the board; the unused 1x03 variant remains in the library.

## Bypass-only connector revision

J5 uses `Header_1x02_CNC`, retaining the first two accepted header positions and geometry: pin 1 at (0,0), square 2 mm land, BYPASS/D10; pin 2 at (0,2.54), round 2 mm land, GND. Both drills are 1.1 mm. The body is 2.54 × 5.08 mm, with a keyed/chamfered pin-1 fabrication outline and 0.5 mm courtyard allowance. This is the shortened two-position version of the accepted generic header, with no new mating-view numbering scheme. Library/component readback, rendered assembly/legend and live placed-pad readback during the [documented cleanup review](design-review.md) verified the two contacts, body/key orientation and net assignment. J6 remains four pins. R16 and the obsolete J5 pair are removed.

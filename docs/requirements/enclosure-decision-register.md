# Enclosure decision and prototype register

Baseline: P1, 2026-10-22. This is the **sole location** for working defaults awaiting final determination, fit uncertainties, alternatives and physical acceptance. The specification and manufacturing notes use these values directly.

Unless explicitly identified as user-provided, dimensions and load screens below are agent-selected defaults, not measurements of the owned hardware or certified ratings. Established inputs remain: the 100 × 150 × 1.5 board and its four existing 4 mm holes, owned GX16-8 bulkheads and EC11, 5 mm LEDs, accepted electrical/UI behavior, no external USB opening and 256³ individual-part build volume. These are not reopened by fit prototyping. All linear dimensions below are mm.

## Working values and validation

### Direction for the next iteration — user correction, 2026-10-22

The user clarified that “as few plates as practical” is an optimization preference, not a fixed three-plate requirement. P1's packing combined the quick sizing plate with assembly-critical production parts and mixed intended colors on that plate. Do not carry that arrangement forward as a design rule. The current P1 CAD, meshes, 3MF and manufacturing notes remain unchanged by this correction.

- Let fit testing, orientation, material/color grouping and assembly needs determine the plate count. Add plates when those needs justify them.
- Keep quick sizing coupons on a dedicated plate inside the same project, independently printable without assembly-critical production parts. Optional representative duplicates may accompany the coupons.
- Prefer plates containing one color/filament type when practical. Preserve the benefit of separately printed contrasting parts by grouping their plates accordingly.
- The printer has an AMS, as confirmed by the user. It can handle mixed-color/material plates when justified, with filament-change time and purge waste included in the tradeoff.
- Preserve consistent process settings where appropriate and test each production filament with representative coupons. A shared project/process does not mandate one filament slot for every plate.

This user direction supersedes any interpretation of ER-24 or the P1 packing rationale as prescribing three plates, assembly parts on the coupon plate, or a single filament slot for future revisions. P1's recorded counts and slot assignments describe that delivered revision only.

Status **P1** means use the value and complete its listed physical check. CAD and slicing do not establish physical acceptance. No P1 part has been physically printed or tested; supplier-linked fastening hardware/feet qualification remains open here.

| ID | Working value | How to solidify | Status |
| --- | --- | --- | --- |
| ER-01 | Indoor desktop, operator at Y=0; front UI, plain removable top; 10–35 °C ambient | Use alongside IC-229H; assess viewing, reach and cable approach | P1 |
| ER-02 | 200 × 195 × 68 body; 3 walls/floor/cover; 4 front panel; front bay to Y30.2, PCB starts Y55 | Full-case fit, panel stiffness, closure and tabletop footprint | P1 |
| ER-03 | PCB X25–175/Y55–155, underside Z9.35; X=175−boardY, Y=55+boardX | Existing hole transform checked in CAD; trial assembly and service access | P1 |
| ER-04 | Integrated PETG posts 6.35 high, OD7.5, 1 root fillet; M3 × 8 and captive nuts; printed washers 7.8 OD × 3.4 ID × 1 | Mount coupon plus washer; nut insertion, thread engagement, hole retention and copper clearance | P1 |
| ER-05 | 2 max underside leads, 4.35 floor clearance; 25 above PCB surface for carrier/headers | Populate board, inspect deflection, cable/header clearance and closure | P1 |
| ER-06 | Front LCD: 72 × 25 opening; 82 W × 25 depth × 38 H allocation, 75 × 31 holes, 2.8 bores; PCB rear support Y10.2 | Fit DFR0063 and backpack to full surround on plate 1; check visible characters, header access and M2.5 × 6 engagement | P1 |
| ER-07 | Encoder (24,36); bore7.2, land1.5; rear20 W ×25 depth ×20 H; body-guide clearance0.3/side; exposed shaft14; socket6.2; knob OD30 nominal | Fit owned EC11 to control coupon/full fascia; check bushing nut, antirotation, insertion depth, rotation and push travel | P1 |
| ER-08 | Toggle (159,39); bore6.5, land1.5; rear15 W ×25 depth ×15 H; PL/BYP legend positions | Fit chosen switch; check grip, travel and wired bypass position | P1 |
| ER-09 | 5 mm LEDs at (156,56)/(181,56); bores5.2, flange7 ×1.6 deep, keeper0.3 axial gap, lead passages4.5 | Fit control coupon and full fascia/keeper; retention, projection, lead insulation and keeper-key seating | P1 |
| ER-10 | Front MIC (181,23), rear RADIO (40,49); bore16.2, grip land2, nut AF20.5; rear body envelope24 diameter ×30 | Fit owned GX16-8 to coupon/fascia/base; nut loading, key orientation, grip, conductor termination and antirotation | P1 |
| ER-11 | GX16 plug24 diameter ×45 outward, plus30 cable bend; installed longitudinal envelope Y−75..270 | Mate plugs beside radio; inspect coupling access, front handling and rear cable bend | P1 |
| ER-13 | RV1 vertical tool corridor10 diameter; module extraction15 above module with cover removed | Trial calibration and module removal with installed harnesses; no external USB opening | P1 |
| ER-14 | UI200 incl75 service loops; MIC260; RADIO200; bends15; seam/screw exclusion5 | Mock up harness routes, panel disconnection, clamp grip and RF/audio behavior; shorten excess | P1 |
| ER-15 | Cover: two underside M3 ×8, two rear M3 ×10. Fascia: two underside M3 ×8. Surround: two M3 ×12. LED keeper: one M3 ×8. Harness bridges: four M3 ×8. Knob: one M3 ×16. LCD: four M2.5 ×6. M3 pocket AF5.7 ×2.6; M2.5 AF5.2 ×2.2 | Qualify supplier-linked ISO metric hardware; check captive loading, socket-key access, engagement, no bottoming and repeated service. Use M3 socket heads nominal5.5 diameter ×3 high; knob head clearance checked in CAD | P1 |
| ER-16 | Cover rails2 high; 0.3 lateral clearance/side; no axial bottoming ledge; fascia/insert recess0.3 lateral/side, front setback1.2 | Print plate 1 fits; check elephant foot, seams, slide-in access and closure on full case | P1 |
| ER-17 | Four purchased compliant feet12 diameter ×3; XY(15,24),(185,24),(15,180),(185,180) | Select adhesive/compliant feet; check encoder pushes, cable pulls, nonslip grip, attachment and underside screw access | P1 |
| ER-18 | PETG; X1 Carbon0.4 working profile; 0.45 widths; 0.2 layers; five walls; six top/bottom;20% gyroid;5 brim; supports off | Apply actual filament profile globally; inspect continuity/warping and closed-case heating; physical acceptance pending | P1 |
| ER-19 | Base floor-down; cover exterior-down; fascia/surround/knob front-down; keeper rear-down; other parts flat. Ramp roots1 wide and 7.2 deep; small nut roofs span5.2–5.7 | Review current sliced layers and bridge cooling; inspect full printed ramps, roofs, thread seats and lettering | P1 |
| ER-20 | Per part256³ established volume; XY planning10..246;5 brim/side; X1 excluded corner18 ×28. Base/cover allocations210 ×205; panel204 ×72 | Saved mesh bounds, prepared plate readback and extrusion limits; inspect actual brim/adhesion and excluded regions | P1 |
| ER-21 | Stencil PTT/BYPASS, PL/BYP3.8 high; CTCSS4.5; MIC/RADIO recessed3.5 high ×0.65 deep; grey surround and amber C-band | Print plate 1; check thin stencil bridges, first-layer legibility, viewing distance and switch-state orientation | P1 |
| ER-22 | Screen20 N axial cable pull,0.3 N·m bulkhead torque,100 enclosure open/close cycles | Agent-selected screening loads, not ratings. Protect electronics; inspect cracks, rotation, nut retention, panel flex and wire tension | P1 |
| ER-23 | Closed full-load run2 h at35 °C ambient; case≤45 °C; components within their operating ratings | Measure air/regulator/LCD/case temperatures, inspect creep and compare with component limits | P1 |
| ER-27 | IC-229H companion styling: dark rectangle, rounded fascia, recessed horizontal display, left ribbed knob, printed color inserts, front MIC and rear RADIO | Review P1 views beside the radio; adjust proportions and control feel from prototype | P1 |
| ER-28 | Printed C-band OD31.2/ID27.3 ×1.6, gap1.6; groove R13.5, radial clearance0.15, axial0.2/side; split-clamp collar6 deep | Fit shaft coupon 6.0/6.2/6.4, complete knob/band; assess band installation, creep, clamp force and push travel; cosmetic band may flex during installation | P1 |
| ER-12 | No external USB connector/opening; flash before assembly, service with cover removed or extract socketed Pro Micro | Established user decision; maintain RAW/USB power procedure | Closed — user decision |
| ER-24 | One multi-plate 3MF, coupons as ordinary first-plate workflow; shared global settings/slot1. P1: three plates, nineteen instances | Native plate/settings/geometry and toolpath readback | Closed — packaging policy; P1 slice evidence below |
| ER-25 | Print integrated feature → separate printed part → justified purchase | Established user-provided design principle, adopted in AGENTS.md | Closed — user decision |
| ER-26 | Printed PCB posts/washers, reusable harness bridges, knob/band and retention features replace purchased mechanical accessories | BOM review implemented; individual physical checks use ER-04/07/09/14/15/17/22/28 | Review complete — P1 geometry |

## Print-versus-buy decisions

| Item | P1 choice | Functional justification / check |
| --- | --- | --- |
| PCB standoffs | Integrated printed posts | PETG provides insulation and height without separate standoffs or underside PCB screws; washer/support fit uses ER-04 |
| PCB retaining washers | Printed, four production plus one fit copy | Broad insulating capture over existing 4 mm holes; ER-04 |
| Harness restraints | Printed reusable bridges, two production plus one fit copy | Screw-removable clamp, without disposable cable ties; ER-14/22 |
| Encoder knob and accent | Printed knob and C-band | Native clamp and replaceable cosmetic trim; ER-07/28 |
| LCD supports, GX nut cradles, LED keeper | Integrated/separate printed parts | Retain hardware without purchased bezel/standoffs/LED clips; ER-06/09/10 |
| M3 screws and hex nuts | Purchased, all joints | Metal thread wear/precision and repeatable service; thin printed threads are unsuitable for the small reusable joints. M3 ×8:13, ×10:2, ×12:2, ×16:1, nuts18. ER-15/22 |
| M2.5 screws and hex nuts | Purchased, LCD only | Fit selected LCD hole allocation with repeatable small threads; four M2.5 ×6 and four nuts. ER-06/15 |
| Compliant nonslip feet | Purchased, four | Grip and compliance under encoder pushes/cable handling; rigid PETG feet do not supply that function. No TPU capability is assumed. ER-17 |
| Heat-shrink insulation | Purchased, as needed | Conformal electrical insulation at LED/switch/GX terminations; rigid printed sleeves cannot seal/grip those individual joints equivalently. Electrical bring-up procedure applies |
| GX/encoder/toggle supplied nuts/washers | Retain the actual hardware's mounting hardware | Match threaded bushings and coupling surfaces; printed cradles restrain the nuts rather than replacing their threads. ER-07/08/10 |

## P1 verification and prototype record

Current CAD, mesh, slicing and readback evidence is in [enclosure-p1](../verification/enclosure-p1/). The model has thirteen installed printed instances made from nine unique production bodies, plus four coupon bodies. All sketches are fully constrained. The PCB/base intersection and all printed-part intersections are zero; allocated LCD/encoder/toggle/MIC/RADIO clearances to the carrier are 24.8/26/26/23/8.08 respectively.

Thirteen exported meshes are closed, manifold and free of detected self-intersections, with Z=0 bed faces. The surround uses Netgen because OCC tessellation produced intersecting triangles around lettering. The rear roof was changed from a rounded tangent approximation to a positively overlapping roof profile after mesh readback detected slivers at its bore junction.

Assembly review extended the support nut-loading slots through the post walls, added encoder body guides, moved the front feet clear of underside screws, and widened the knob collar/relocated its clamp bolt to clear a 5.5 diameter ×3 socket head. Display mounting ramps were widened to a 1 mm root after the slicer flagged the original sub-extrusion-width starts as floating cantilevers. These are adopted P1 corrections, not physical acceptance.

Final P1 slice: Bambu Studio 2.8.2.61, all three return codes zero and all warning strings empty after the ramp correction. Estimates: plate 1 2 h 38 min / 71.9 g; plate 2 5 h 52 min / 255.7 g; plate 3 3 h 59 min / 133.8 g; combined about 12 h 29 min / 461.5 g. Inspected bed skins, lettering, mounting ramps, posts, nut ceilings, rear roof and final columns in the current layer sheets. Native STEP readback contains all thirteen installed solids, including repeated linked washers/bridge. Physical acceptance remains governed by the open rows above.

Print plate 1 includes the full fascia/surround/knob/band/LED keeper, four coupons and fit copies of the PCB washer and harness bridge. Plate 2 contains base, two bridges and four washers; plate 3 contains cover. Keep global process/filament settings shared. The print project embeds its geometry, profiles and sliced paths and has no dependency on scratch. Final warning strings, time/material estimates and saved transforms are recorded in [multi-plate-checks.json](../verification/enclosure-p1/multi-plate-checks.json).

Physical sequence: print plate 1 using the chosen filament/settings; record the corresponding checks above; update geometry/global settings as needed, re-slice, then print plates 2/3. Record hardware supplier and actual printer/filament/profile with each result. Complete enclosure handling, repeated service, thermal and radio/audio tests after population.

| Revision/date | Check | Result / adopted change |
| --- | --- | --- |
| P1 / 2026-10-22 | FreeCAD native geometry, exported mesh readback and installed envelopes | CAD/mesh evidence at the links above; physical fits remain P1 |
| P1 / 2026-10-22 | Prepared shared three-plate project and layer review | Exact final metrics/warnings in the current slice evidence; physical checks remain P1 |

## Historical P0 / P0.1 record

The following evidence describes the former geometry and does not validate P1. Historical exported manufacturing paths mentioned below have been retired; the previous native baseline is [p01-enclosure.FCStd](../../mechanical/enclosure/revisions/p01-enclosure.FCStd).

### Historical prototype sequence and evidence

1. Capture exact hardware geometry and create parameterized P0 CAD using the working values. Check component interference, service paths and print-volume allocations.
2. Print coupons for GX16 bulkheads, EC11/toggle mounting, LEDs, LCD bezel/cradle and lid joints. Reuse a combined coupon where practical.
3. Record the coupon results below, revise affected rows and produce the complete case. Inspect slices before printing.
4. Populate and exercise the case; complete fit, service, mechanical handling, closed-case thermal and radio/audio tests. Record the actual printer/profile, revision and hardware used.

Historical evidence: P0.1 CAD and mesh checks are complete; see [CAD results](../verification/enclosure-p0/cad-checks.json), [assembly preview](../verification/enclosure-p0/assembled.png) and [layout drawing](../verification/enclosure-p0/layout.svg). All ten current exported parts/coupons are valid single solids and closed meshes with no detected non-manifold edges or self-intersections. The native document was reopened and checked. Five enclosure parts have zero mutual intersection volume. Board-to-base intersection is zero. The carrier allocation has 1.15 mm separation from the LCD and each GX16 rear envelope. Each mesh fits the 236 mm XY planning area with a 5 mm brim and the 256 mm Z constraint.

**Physical acceptance remains open here only.** No coupon or full enclosure has been physically printed/tested. New fastener/foot supplier qualification remains open; listed hardware is the working mechanical BOM. The GX16/EC11/LCD mounting defaults, retention, grip lengths and load/thermal screens still require the checks in the rows above.

**P0.1 slice and plate evidence:** Bambu Studio 2.8.2.61 sliced and exported the historical single three-plate project with X1 Carbon 0.4 mm, Generic PETG and Textured PEI Plate. The saved project embeds five perimeters, six top/bottom layers, 0.2 mm layers, 0.45 mm line widths, 20% gyroid, 5 mm brims and supports disabled. This profile is an agent-selected working default matching the locally selected printer profile; the established build volume remains 256 mm.

The single project contains a seven-piece coupon plate first (five coupons plus a reusable LCD cradle and one LED keeper), followed by the base and lid/retainers plates. The complete enclosure occupies two production plates; coupon printing uses the same project and global settings. Five-millimeter brim reservations fit inside X/Y10–246 mm; additional placement offsets avoid the X1's front-left 18 × 28 mm excluded rectangle. Readback of the final native 3MF resource/component/build transforms and plate assignments confirms exact object counts, placements and Z=0 bed faces. Model, profile and toolpath data are embedded; no scratch file is needed to open a project.

Slice estimates: base 6 h 14 min / 241.6 g; lid/retainers 2 h 46 min / 94.7 g; coupons 1 h 36 min / 43.4 g. The main enclosure total is about 9 h / 336.3 g. These are slicer estimates, not physical measurements. Return codes were zero, all three slice-warning strings were empty and no printer command was sent. Reviewed representative extrusion layers for skins, walls, lettering, bosses, bridges, nut pockets and roof openings: [base](../verification/enclosure-p0/slice-02-base.png), [lid/retainers](../verification/enclosure-p0/slice-03-lid-and-retainers.png), [coupons](../verification/enclosure-p0/slice-01-fit-coupons.png). Critical assembly fits and load/temperature tests remain the physical checks in ER-01–23. Saved metrics and file hashes are in [multi-plate-checks.json](../verification/enclosure-p0/multi-plate-checks.json).

**Resolved trial history:** P0's OrcaSlicer C++ exception and Bambu exit `0xFFFFFFC3` produced no slice. P0.1 resolved Bambu's own inherited machine/process/Generic PETG profiles rather than supplying mixed Orca profiles or the non-instantiable filament base. The initial plate position intersected the printer's excluded corner; shifting placements +10 X/+20 Y resolved the collision. Export using an absolute filename failed after slicing; using a filename relative to the dedicated output directory produced valid native projects, then the projects were promoted to manufacturing. The final project passes ZIP integrity, profile, geometry and toolpath-presence checks.

**P0.1 user review changes:** removed the USB opening, corridor and obsolete coupon. The closed wall is verified at the old opening center; initial programming is pre-assembly and service programming uses the removable lid/socketed module. Corrected the rear lettering frame to local X=−case X, local Y=+case Z, outward normal=+case Y and inspected the [rear exterior view](../verification/enclosure-p0/rear-labels.png). Connector identities and positions are unchanged. Native geometry and all ten current mesh exports were regenerated and checked.

P0 modeling corrections:

- Raised GX16 centers from Z40 to Z49: the original 24 mm-diameter rear envelope reached Z28 and overlapped the carrier's Z10.85–35.85 component allocation. It now starts at Z37, giving 1.15 mm separation.
- Changed M3 nut seats from 7 to 5.7 mm across flats, 2.6 mm deep: the original pocket would not restrain a nominal 5.5 mm-across-flats M3 nut. Used side-loading slots in base pillars and open-bottom pockets in lid bosses.
- Opened GX16 nut cages at the top for nut insertion and removed the rear lip above them. Circular bores retain their 16.2 mm passage and gain 45° printable roofs; the roof apex is Z60.46, below the Z62 lid underside.
- Historical P0, superseded by ER-12: set USB passage center to (X110, Z22.95) from the board transform and working socket/module stack; the front-wall opening has a 45° roof above the 16 × 10 clear passage. USB insertion corridor length to the module face is 41.5 mm.
- Used separate LCD cradle and LED keepers, with M3 × 10 cradle-to-lid screws, M2.5 × 6 LCD-to-cradle screws and M2.5 × 8 keeper screws. Added 0.3 mm outer bed-edge chamfers to base and lid.
- Removed axial lip-clearance language: the lip enters the open cavity without a bottoming ledge; the lid seats directly on the base wall. Raised rear labels were replaced by recessed labels to keep the body envelope at 180 × 150.
- Replaced OCC tessellation with Netgen for the lid and LCD coupon after the secondary mesh check detected intersecting triangles near engraving/clipped bosses. The final mesh readbacks have no detected intersections; the native geometry is retained.
- Native geometry and mesh validation do not establish exact assembled component fit. Main dimensions/openings are driven by the spreadsheet and native feature properties; coordinate changes require coordinated support, coupon and clearance review. Complete-layout regeneration uses the maintained FreeCAD builder.


| Revision / date | Register IDs | Evidence and result | Adopted change / finalization |
| --- | --- | --- | --- |
| P0 / 2026-10-22 | ER-01–23 | FreeCAD MCP build, eleven mesh readbacks, BRep validity and assembly intersection/envelope checks | CAD stage passed; dimensional fit and physical acceptance stay P0 |
| P0 / 2026-10-22 | ER-18–20 | OrcaSlicer/Bambu Studio CLI trials exited without slice output | Historical trial; resolved in P0.1 |
| P0.1 / 2026-10-22 | ER-12, ER-21 | Closed front wall and rear text corrected after user review; native model reopened | CAD/mesh stage passed; ER-12 decision closed |
| P0.1 / 2026-10-22 | ER-18–20 | One three-plate project sliced; coupons first, then base and lid/retainers; saved project transforms/settings checked; layer sheets inspected | Slice/packing stage passed; physical checks remain P0 |

Keep failed checks and adopted resolutions here. A changed parameter reopens only the affected checks and dependent geometry. Do not copy unresolved-item lists or repeated qualification language into the requirements, mechanical workspace, print notes or other project documents.

Working material retained in ignored `.agent-scratch/enclosure-p01/`: resolved slicer profiles, intermediate arranged geometry, native slice results, layer-inspection script, downloaded source inspection copies and generated backups/obsolete USB coupon. These are not project dependencies.

Multi-plate packaging update (2026-10-22): user requested that coupons remain inside the same project as an ordinary step when trying materials/settings. Replaced the three single-plate exports with one native Bambu Studio project using the slicer's plate-assembly interface. All three plates sliced successfully and have empty warning strings; placement/bed-face readbacks passed and no individual process overrides were found. Per-plate G-code and metadata are embedded. Previously exported single-plate files and their evidence are superseded and stored only in ignored scratch. CAD geometry is unchanged.

Retained working material for this packaging update is in `.agent-scratch/enclosure-p01-multiplate/`: resolved profiles, arranged STLs, native assembly request, raw slice result, layer-inspection script and superseded single-plate files/evidence. The delivered project is self-contained.


P1 working-file handoff: ignored `.agent-scratch/enclosure-p1/` retains intermediate meshes, arranged plate geometry, resolved slicer profiles/results and inspection/document-generation scripts. Automatic approval review rejected recursive cleanup with the stated reason “blocked by policy”; these files are not dependencies of the delivered CAD, 3MF or documentation. Automatic FreeCAD backups remain ignored.


### Bambu Studio opening discrepancy — user report, 2026-10-22

The user reports that opening the delivered 3MF in Bambu Studio did not show the settings previously reported by the agent. Direct inspection of P1's embedded `Metadata/project_settings.config` confirms wall_loops=5, sparse_infill_density=20%, sparse_infill_pattern=gyroid, top/bottom_shell_layers=6, layer_height=0.2, line_width=0.45, brim_width=5, supports disabled and ironing_type=no ironing. Its process preset identifier still reads `0.20mm Standard @BBL X1C`.

The embedded values do not establish that the user's Bambu Studio session adopted or displayed them. Cause remains unresolved; do not describe the end-to-end opening/settings workflow as verified. In a future packaging review, reproduce opening the delivered project in Bambu Studio and compare the effective process and object/plate overrides with the embedded configuration. Keep this separate from future part-specific print optimization. No current manufacturing output was changed in response to this report.

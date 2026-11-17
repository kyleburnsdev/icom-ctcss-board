# C1 digital verification

**Current LCD interface: L1, 2026-11-17.** C1 now corrects the B2-derived row
spacing/window datum and uses 9.43 mm supports from the user's 9.13 mm bezel
projection. The checks below cover L1; the original failed coupon is historical.
See the [L1 correction and retest](../../lcd-fit-correction.md).

This evidence covers the C1 PLA fit prototype. It does not establish physical
radio retention, fit, temperature performance or a completed machine print.

- [CAD and interface checks](cad-checks.json): preserved B1/B2 hashes, user radio pattern, selected fits, clear reference allocations, fully constrained native sketches.
- [Export/readback checks](export-checks.json): 16 closed unique print meshes, print transforms/bounds, all printed-instance intersections, sampled rearward cover travel, native saved-source readback and STEP checks.
- [Slicer/project readback](slicer-checks.json): four named plates, 27 objects, shared embedded PLA/X1C profiles, saved-layout transforms, slice results and project hash.
- [Actual extrusion layer sheets](layer-checks.json): [test interfaces](layers-1.png), [base](layers-2.png), [panel and retainers](layers-3.png), [cover and saddles](layers-4.png).
- [Inventory preflight](inventory-preflight.json) and [input](inventory-input.json): record gaps remain separate from geometry and current user inputs. Insert quantities, filament stock counts and complete printer capability records are missing; user selected PLA and confirmed ample M3 × 8 screws.
- [Package checks](package-checks.json): local links, file hashes, exact quantities, source/mesh/project identity and Bambu native project reopen.

All four final slice warning strings are empty. A first slice flagged the tongue
coupon as a floating cantilever when printed flange-down. The final coupon is
roof-down to match the production cover; the final slice/reopen warnings are empty.
The actual extrusion sheets were visually reviewed for bed skins, LCD supports,
insert/nub features, rail gussets/lips, corner straps, bracket holes and cover
tongues. Short bridges remain process features for the coupon tests, not a claim
that physical print quality has been accepted.

Cover-travel checking caught its saddle insert bosses passing too close to the
base's cover-lock posts. The current 9 mm-wide lock posts at X23.5/132.5 and the
9 mm-diameter cover bosses leave 0.5 mm lateral clearance during sliding. Rear
straps are clear. Sampled travel is Y+0/+10/+50/+100/+150/+165 mm; this is a CAD
check, not a measured sliding force.

Part.export in this FreeCAD build omitted App Link instances from a direct STEP
export. The maintained exporter therefore makes native shape snapshots for STEP
only; the editable source retains its Body histories and App Links. STEP readback
contains all 16 installed printed instances, with volume agreement within the
selected 0.01 mm³ exchange-readback tolerance.

Native references use the unchanged 100 × 150 × 1.5 PCB and its existing four
4 mm holes, Grove V4 drawing/B2 ear geometry, simplified connector/module
allocations and a 140 × 155 × 40 radio envelope. The [guide](../../enclosure-c1-guide.md)
requires actual mated cables, USB/trimmer access and radio bolt engagement before
power or loaded use. The [mounting note](../../reference/ic229h-mounting.md)
separates user dimensions from Icom parts evidence and unpublished thread depth.

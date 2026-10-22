# PCB implementation record

## Mechanical foundation

The rectangular board occupies X=50–150 mm and Y=50–200 mm in KiCad, giving **100 × 150 mm**. Konnect created four straight Edge.Cuts segments over live IPC. No pre-existing outline was present.

| Hole | Center X mm | Center Y mm | Drill | Technology |

| --- | --- | --- | --- | --- |

| H1 | 56 | 56 | 4 mm | NPTH |

| H2 | 144 | 56 | 4 mm | NPTH |

| H3 | 144 | 194 | 4 mm | NPTH |

| H4 | 56 | 194 | 4 mm | NPTH |

Every center is 6 mm from its two adjacent edges. Live component readback confirmed all four positions; H1 pad readback confirmed np_thru_hole and a 4 × 4 mm circular drill. The library mounting-hole pads list all copper layers as a clearance object, with pad diameter equal to drill diameter: this is not a plated annulus or routed top copper.

After saving, Konnect placement scoring proved a rectangular outline and reported no mechanical hard failures for these four objects. The historical mechanical-stage DRC completed with zero design-rule errors and 41 schematic-parity warnings because the circuit had not yet been synchronized. This stage result is not full-board DRC acceptance.

## Completed layout

The saved layout contains 38 circuit parts and four mounting holes. All 242 track segments are on B.Cu; there are no routing vias, jumpers, zones or copper pours. Signal tracks are 0.5 mm and power/ground tracks 1.0 mm, with 0.5 mm clearance. These widths use a provisional 200 mA board-load allocation and ordinary 1 oz copper as planning assumptions; actual copper weight, module regulator dissipation and radio-port current remain unverified.

See the [top assembly drawing](../reference/assembly-top.svg), [mirrored bottom copper view](../reference/copper-bottom.svg), and [independent native inventory](../verification/final-board-inventory.json). The body check uses selected component dimensions and a conservative 37 × 18.24 mm module/socket envelope, including 3 mm socket bodies. The minimum calculated body gap is 2.14 mm (Q1/R11); module-to-C4/C5 gaps are 2.38 mm. Actual purchased sockets, cable plug, enclosure and mounting hardware still require a dry fit. USB faces left with open board area to the edge. No other component occupies the module envelope.

The [final DRC](../verification/final-drc.json) reports **zero errors and zero unconnected items**. Its 115 warnings remain visible: 38 library-footprint comparisons, 35 original footprint reference/outline overlaps, and 38 schematic metadata differences plus four expected extra mechanical-hole parity warnings. They are not suppressed. Electrical net connectivity is independently checked by the exported netlist assertions. Larger external assembly labels supplement the original footprint fields; the CNC blank needs a separate physical marking process.

### Native THT pad representation

Library footprints request B.Cu-only lands, but KiCad normalizes saved through-hole pads to include F.Cu as well. Native inventory finds 111 bottom and 111 virtual top lands, with **no top tracks**. The physical single-sided requirement is enforced by the explicitly selected fabrication layers: [CNC review package](../../manufacturing/pcb/carvera-air/README.md) contains B.Cu as its only copper layer, plus Edge.Cuts, drills and a separate top-legend Gerber/SVG. Do not manufacture an all-layer default export or the diagnostic IPC-2581 file. Neither is the single-sided machining contract.

## CNC milling process target

The user selected CNC isolation milling on **1.5 mm single-sided copper-clad stock**, with first-board reliability prioritized. No plated-through connections, solder-mask registration, or industrial fine-gap capability may be assumed. Bottom pads must be solderable on their own. Through-hole drill paths and NPTH mounting holes need explicit CNC/tool capability review.

The implemented geometry uses 0.5 mm isolation clearance, 0.5 mm ordinary traces, 1.0 mm power/ground buses, and 2.0 mm socket/header pads with 1.1 mm drills. Individual drill dimensions, copper weight and a test cut remain necessary for milling acceptance. Routing goes around header rows. Q1 uses the documented factory-formed 2.54 mm-pitch onsemi 2N3904TAR, replacing the original closely spaced straight-lead option.

The user has a **30° V-bit with 0.2 mm tip**, a **60° V-bit with 0.1 mm tip**, and an assortment of PCB milling/drilling bits. Ideal effective cut width at penetration d is tip + 2d·tan(included angle/2). At d=0.10 mm, this gives approximately 0.254 mm and 0.215 mm respectively. Thus a 0.5 mm design gap leaves useful room for clearing multiple passes. These calculations do not establish a safe depth or machining capability: copper thickness, tip condition, runout, surface-height variation, stock hold-down and calibration remain real inputs. Verify isolation width and full copper removal on scrap before production. Individual available drills, particularly 1.1 mm and 4 mm, remain to be confirmed; holes may need reviewed interpolation if a matching drill is unavailable. Do not generate final CNC toolpaths from the ideal-width equation alone.

The approved Pro Micro public layout remains the pad-number/pitch source. Enlarging pad diameters for this process preserves its electrical map and header spacing; the derivative documents each change. The user has clarified that the Carvera Air includes the PCB kit and laser accessory. The manufacturing package now includes F.SilkS Gerber and a matching 100 × 150 mm SVG for a flood-cured background coat and contrasting selectively laser-cured UV solder-mask legend. See the [process and plot policy](../../manufacturing/pcb/carvera-air/README.md#top-legend-and-uv-solder-mask-process). Physical exposure/cleaning settings remain coupon checks.

## Analog ground return

The final layout separates the filter/divider/trimmer return from the LCD/UI trunk. C3 rotates to 270° and R10 reverses its pad orientation within its original body envelope, leaving a route beneath ordinary THT bodies. A 1 mm analog branch runs from RV1 around C3 to the Q1/PTT ground branch; the LCD/UI trunk reaches the radio header separately. The branches meet at the header ground connection, with a remaining shared PTT return segment. No wire link was added. Noise/reset/keying behavior still requires the documented bench test. See the dated independent review for geometric confirmation.


## Two-pin J5 and four-pin J6 revision

J5 now uses Header_1x02_CNC at its original pin-1 position (140,102), rotation 0: pin 1 BYPASS/D10, pin 2 GND. J6 retains Header_1x04_CNC with PTT LED+/GND/BYPASS LED+/GND. R16 and all 14 OFFSET/A0 track segments have been removed; U1 pad 17 is explicitly unused. Existing power/ground buses remain continuous, including the former R16 power-pad position, which is a through junction serving R15 rather than a dangling branch. The top legend removes the obsolete R16/OFF labels and marks A0 NC. Native inventory contains 111 electrical pads and 242 bottom track segments, with no vias or pours. Mounting-hole geometry, separated analog return and the landscape Y-flip contract are unchanged.

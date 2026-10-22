# Makera Studio toolpaths and board fabrication

**2026-10-22 sourcing revision:** C6 now has 15 mm pitch and 1.1 mm drills; TP3 moved. Use the regenerated copper, legend and drill exports together. The existing `ctcss-board-cam.mkc` is preserved user work from the earlier geometry: reimport the revised files, rebuild toolpaths and verify registration/drill counts before machining. It is not validated for this revision.

Make the board in two machine stages: complete the bottom copper and holes, then flip the board and laser-cure the top legend. Keep all operations for an unchanged stock setup in one NC file, including tool changes. End the file before cleaning underneath the board, reseating it, coating it or turning it over.

Use 1.5 mm single-sided copper-clad stock, 150 mm along machine X and 100 mm along machine Y. Components mount on the bare substrate side; copper faces down on the finished board. Use the current two-pin J5 / four-pin J6 files.

This procedure follows the [Makera CAM guide](https://wiki.makera.com/en/software/MakeraCAM_userguide), [Carvera Air manual](https://wiki.makera.com/en/Air/Manual) and [LED Light example](https://wiki.makera.com/en/Air/Manual/Air-LED-Light). Use the recipe below for the first attempt and adjust it from the results.

## Job files and order

Start with bare bottom copper for the first board. Add bottom solder mask using the separate section near the end when you want that finish.

| Order | Action | NC file |
| --- | --- | --- |
| 1 | Mount the blank copper-side up; probe and level it. | Setup only |
| 2 | Contour-isolate copper, drill the small electrical holes, pocket the larger electrical and registration holes, and trim the perimeter when using an oversized blank. | `10-ctcss-bottom-machine.nc` |
| 3 | Clean, deburr, check continuity, flip the board, apply and cure the top background, then apply the contrasting coat. | Manual work between files |
| 4 | Selectively cure the top legend with the laser. | `40-ctcss-top-legend.nc` |
| 5 | Wipe away uncured coating, remove tabs, finish edges and inspect. | Manual finish |

Step numbers leave room for the bottom-mask stage. Keep registration holes in step 10: install the locating pins after that file finishes, for use during the flip. Initial hold-down uses the blank's edges and tape, so it does not need pre-cut registration holes.

Save final Studio projects and numbered NC files under `manufacturing/pcb/carvera-air/`. Add a revision suffix when changing a job, such as `10-ctcss-bottom-machine-r02.nc`. Keep only the selected revision in the machine's active job folder. Put inspection notes and photos in `docs/verification/`.

## Open the project and check alignment

Open [ctcss-board-cam.mkc](../../manufacturing/pcb/carvera-air/landscape-y-flip/ctcss-board-cam.mkc) from the [landscape CAM package](../../manufacturing/pcb/carvera-air/landscape-y-flip/README.md). Keep the project beside its source imports. Inspect the existing layers before importing anything else so each object appears once.

For the sourcing revision, rebuild the imports before calculating paths:

1. Save a new revision of the existing Studio project, preserving the earlier project as a reference.
2. Remove the superseded copper, electrical-hole and legend imports from the new working revision, together with paths derived from them. Retain tool profiles and setup settings only after checking them against this guide.
3. Import the current `bottom-copper-Y-FLIPPED.gbl`, `bottom-electrical-holes-Y-FLIPPED.drl`, `registration-holes.drl`, `board-outline.gm1` and `top-legend.svg` from the same `landscape-y-flip/` directory. Replace any retained copies so there is exactly one of each geometry set.
4. Preserve their common origin, scale and orientation. Check the dimensions and asymmetric J1 pin-1 positions below; do not mirror the bottom files again.
5. Confirm C6 has two holes 15 mm apart, and count 46 electrical holes at 0.9 mm, 65 at 1.1 mm and four registration holes at 4 mm. Then create the paths in the sections below. Earlier toolpaths do not update merely because the source files on disk changed.

Use this board-local frame throughout:

| Feature | Position or dimension |
| --- | --- |
| Finished board | X=0–150 mm; Y=0–100 mm |
| XY zero | Lower-left corner of the finished board |
| Registration holes | (6,6), (144,6), (6,94), (144,94) mm |
| Registration hole diameter | 4 mm |
| Hole pitch | 138 mm X; 88 mm Y |
| J1 pin 1 in bottom machining view | (20,40) mm |
| J1 pin 1 in top view | (130,40) mm |

The bottom files are already mirrored for a left/right flip about Y. Leave their orientation unchanged. After machining, flip the physical board left/right: X′=150−X, Y′=Y. Use the orientation mark and J1 pin 1 to distinguish this from a 180° rotation.

Use these layers:

| Source file | Purpose |
| --- | --- |
| `bottom-copper-Y-FLIPPED.gbl` | Copper lands and traces to preserve. |
| `bottom-electrical-holes-Y-FLIPPED.drl` | 46 holes at 0.9 mm and 65 holes at 1.1 mm. |
| `registration-holes.drl` | Four 4 mm mounting/registration holes. |
| `board-outline.gm1` | Finished 150 × 100 mm rectangle. |
| `top-legend.svg` | Top legend artwork for laser exposure. |
| `*-REGISTERED.svg` | Alignment references; keep their blue guides out of toolpaths. |

Preserve the shared coordinates when importing. Move layers together rather than centering each on its own artwork. Use the table above to check the imported scale and position. Keep the portrait files in `native-exports/` out of this job.

## Set up the tools

Open **Setting → Tool Library** and use the Makera tool profiles below. Assign the same numbers in the library and in each operation. The Air uses those numbers to prompt for manual tool changes.

| Number | Tool | Work |
| --- | --- | --- |
| T2 | 30° V-bit with 0.2 mm tip | Fine copper isolation. |
| T3 | 0.8 mm corn bit | Prototype small-hole drilling, larger hole pockets and perimeter; optional broad copper clearing. Use for axial drilling only if the actual cutter supports plunging. |
| T5 | UV solder-mask removal tool | Pad openings in the bottom-mask workflow. |
| Laser | Carvera Air laser profile | Top legend curing. |

Select the **PCB material preset** for each cutter. Keep its spindle speed, feed and plunge settings for the first run. For T2, use 30° included angle and a 0.2 mm flat tip. For T5, use the spring-loaded solder-mask profile.

Use these first-run operation settings. Copper-cutting depths and laser power choices follow Makera's PCB recipe; the retained-WCS bottom-mask settings, stepover, stepdown, fill interval and tab dimensions are this project's choices.

| Operation | Settings |
| --- | --- |
| Copper isolation | **2D Contour**, T2 only; tool compensated into waste copper, no tabs or ramping. Start depth 0; end depth 0.05 mm below copper surface. Use the effective V-bit diameter at that depth, approximately 0.227 mm for the nominal 30°/0.2 mm-tip tool. Confirm the swept cut in preview and on a coupon. |
| Small-hole drilling — prototype deviation | Drilling path at the 46 nominal 0.9 mm hole centers with the existing 0.8 mm tool; resulting holes are approximately 0.8 mm, intentionally undersized. Start depth 0; final depth stock thickness + 0.3 mm (1.8 mm for this stock). Peck increment 0.3 mm; retract to a fixed height 1 mm above the starting surface between pecks; no bottom dwell. Use a drilling/plunge setting appropriate to the actual tool and PCB material, checked on the coupon. |
| Larger hole pockets | T3; Parallel pocket strategy; ramping off; 0.3 mm stepdown; final depth stock thickness + 0.3 mm, giving 1.8 mm for 1.5 mm stock. |
| Perimeter | T3; Outside contour; 0.3 mm stepdown; 1.8 mm final depth; four tabs, each 3 mm wide and 0.5 mm thick. |
| Bottom mask openings | T5; Parallel pocket strategy; retain bare-copper WCS; start depth −0.5 mm, end depth +0.1 mm, step-down 0.6 mm for one clearing pass; PCB preset feed and spindle settings. |
| Top legend | Laser Vector, Fill; speed 100 mm/min; 20% power for a light contrasting coat or 30% for a dark one; 508 LPI (0.05 mm line interval); one pass. |

Positive depth values are below the operation's Z reference. Bottom-mask depths retain the bare-copper reference: −0.5 mm is above bare copper and +0.1 mm is below it. Use a 10 mm safe height for spindle jobs and keep clamps below that travel plane. Laser focus and clearance are set separately in the laser section.

## Run a small first test

Cut a small sample on spare matching stock before the full board. Include a 0.5 mm gap, a 0.5 mm track, two 2 mm lands at 2.5 mm pitch, 0.9/1.1/4 mm holes and a small patch of the top legend. Use the same operation settings as the board.

Inspect the result and make these adjustments:

| Result | Adjustment |
| --- | --- |
| Copper remains across an isolation channel | Clean and reseat the sample, rerun leveling, and increase isolation depth from 0.05 to 0.07 mm. |
| Electrical holes are tight | For the 1.1 mm pockets, measure the holes, correct T3's effective diameter in the tool profile and regenerate the pockets. The prototype's 46 small holes are intentionally drilled approximately 0.8 mm; check actual lead fit, and open individual holes to 0.9 mm if needed rather than forcing leads. Keep the nominal 0.9/1.1 mm design diameters unchanged. |
| Cutter chatters or leaves ragged holes | Reduce feed by 25% and stepdown from 0.3 to 0.15 mm. |
| Registration pins bind | Deburr first, then enlarge the registration pockets in 0.02 mm diameter increments until the pins slide in without force. |
| Laser-cured strokes wash away | Increase exposure by reducing speed by 20%. |
| Legend strokes spread or the background discolors | Reduce exposure by increasing speed by 20%. |

Dry-fit an actual component lead and socket pin. Test the registration pins and perform one flip. Wipe the laser sample to judge the retained legend. Save the settings that give the best result and use them for the board.

## Define the bottom toolpaths

Create these paths in execution order. Export them together as `10-ctcss-bottom-machine.nc`.

| Order | Path name | Tool |
| --- | --- | --- |
| 1 | `11-copper-isolate` | T2 |
| 2 | `12-electrical-0p8-prototype-46holes` — drilling | T3 |
| 3 | `13-electrical-1p1-65holes` | T3 |
| 4 | `14-registration-4mm-4holes` | T3 |
| 5 | `15-perimeter` | T3; omit for a finished-size blank |

### Isolate copper with a 2D Contour and T2

The default operation is **2D Contour with the T2 engraving V-bit only**. Cut a narrow insulating channel around the wanted copper; leave the broad background copper in place. The earlier multi-tool pocket instructions described full-area copper removal, which is optional and is not needed merely to isolate the nets.

1. Work from `bottom-copper-Y-FLIPPED.gbl`, which represents positive copper to **keep**. Hide the outline, drill and legend layers while selecting isolation geometry.
2. Use the boundary of the **merged copper regions**: touching/overlapping trace strokes and pad flashes belonging to a connected region must form a single shape before its boundary is contoured. Do not contour each original trace stroke or pad separately: that can cut through their intended junctions. Preserve separate regions belonging to separate nets. If the import has intersecting outlines rather than merged regions, resolve those with the CAM geometry union/PCB import handling before generating the contour; inspect the result rather than assuming the import performed that union.
3. Create **2D Contour**, name it 11-copper-isolate, and select **T2 only**. For exterior boundaries of positive copper regions, use **Outside** so the cutter is compensated into unwanted copper. Do not use **On Vector**, which centers the cutter on the copper edge and removes part of the intended trace/land. Do not select the board rectangle for this operation.
4. Inspect any enclosed waste-copper areas separately. Their cut must also be on the waste side of the retained-copper boundary; a blanket Outside setting on every nested loop is not automatically correct. Do not add electrical drill circles to the isolation operation; those are pocketed later.
5. Set start depth 0 and end depth 0.05 mm, safe height 10 mm, no tabs, no ramping. Use the PCB feed/spindle preset as the coupon starting point. V-bit compensation must account for its width at cutting depth: nominal width = tip width + 2 × depth × tan(included angle/2), approximately 0.227 mm here. Check how the selected tool profile calculates this width; do not compensate it a second time manually.
6. Calculate and inspect the **swept cutter area**, not just its centerline. The cut must surround retained copper without crossing trace/pad junctions or reducing the specified 2 mm lands, 0.5 mm signal tracks or 1 mm power/ground tracks. Inspect C1/C2 pad gaps, Q1, both module rows and all narrow passages. Makera documents that intersecting paths can prevent Inside/Outside contour generation; an empty or missing path is not successful isolation.
7. Verify every distinct net is separated from the remaining background and other nets. One approximately 0.227 mm groove can electrically isolate a region even though the design reserves 0.5 mm between wanted copper shapes; it does **not** remove the entire 0.5 mm space. If more isolation width or soldering clearance is needed, add reviewed offset passes into waste copper or use the optional clearing method below. Prove the chosen groove width on the coupon and check shorts/continuity after milling.

Makera's [2D Contour documentation](https://wiki.makera.com/en/software/MakeraCAM_userguide) defines Inside, Outside and On Vector compensation. These instructions describe the required geometry/result; a contour is acceptable only when the imported merged boundaries and swept-area preview satisfy those checks. No Studio toolpath has been generated or validated by this documentation edit.

### Optional: remove broad background copper with a 2D Pocket

Use **2D Pocket** only if you deliberately want to remove the copper background over an area, rather than cut insulating outlines. Define the board boundary as the outer pocket boundary and the merged wanted-copper regions as protected islands; preserve enclosed wanted-copper shapes. The preview must remove the background and leave the complete tracks and pads intact.

T3 can rough the broad areas at the shallow copper-removal depth, while T2 can finish inaccessible narrow areas **if the CAM operation supports and correctly previews that remaining-material geometry**. Do not assume merely adding a second tool performs valid rest machining. Review the V-bit's depth-dependent width and the final swept areas. This alternative adds machining time and tool changes; omit 10-copper-clear entirely for the default contour-only workflow. Do not run a full-area pocket and the contour as overlapping unreviewed alternatives.

### Drill the small holes and pocket the larger electrical holes

**Initial prototype only, user-approved deviation:** select the centers of the 46 nominal 0.9 mm holes and create a **drilling path** with the existing 0.8 mm tool. Name it `12-electrical-0p8-prototype-46holes`. Do not attempt a 0.9 mm pocket with this tool; Studio rejects that narrow pocket. Drilling makes approximately 0.8 mm holes, not the design's 0.9 mm diameter. Keep the source drill files and tool's declared diameter unchanged. Confirm the actual cutter supports axial plunging; the drilling operation does not make a non-plunging cutter suitable for drilling.

Select the 65 nominal 1.1 mm holes separately and create a **2D Pocket** path with T3 using the larger-hole settings above. If the import supplies only centers, create 1.1 mm circles at those centers for the pocket operation. Do not include these holes in the 0.8 mm drilling selection.

For the small-hole **drilling** path, use the following prototype starting settings. These numeric peck/retract choices are project coupon settings, not a manufacturer-validated recipe for the unidentified 0.8 mm cutter:

| Drilling parameter | Starting setting |
| --- | --- |
| Start / final depth | 0 / 1.8 mm below the copper surface |
| Peck increment (depth per cut) | 0.3 mm: cumulative depths 0.3, 0.6, 0.9, 1.2, 1.5 and 1.8 mm |
| Retract strategy | Fixed Z Height, returning above the starting surface after each peck |
| Peck retract height | 1 mm above the copper surface, not 1 mm above the current hole bottom |
| Bottom dwell | 0 seconds, if the interface offers this field |
| Travel between holes | Retain the 10 mm safe height; the 1 mm peck retract does not replace clamp-clearance travel |
| Spindle / plunge feed | Use settings appropriate to the actual tool's axial-cutting capability and PCB stock; confirm on a few coupon holes before all 46. Do not assume a pocket feed is a drilling plunge feed. |

Makera's [2D Drilling documentation](https://wiki.makera.com/en/software/MakeraCAM_userguide) describes Fixed Z Height as retraction above Start Depth; Studio's field names may differ. Verify the preview shows six progressively deeper pecks per hole and a return above the surface between them. Pecking assists chip evacuation; it does not make a non-center-cutting corn bit suitable for axial drilling. Check the actual cutter's suitability before using this path. If chips pack, the tool heats or the cut sounds labored, stop and review the cutter/feed/extraction rather than adding dwell at the bottom.

Check the path counts: 46 undersized drilled holes and 65 larger pocketed holes. J5 has two holes, J6 has four, and the Pro Micro has two rows of twelve. C6 contributes two 1.1 mm holes at 15 mm pitch. All holes are unplated, including those categorized as PTH in the CAD exports. Check lead insertion on the coupon and before assembly, particularly Q1's formed rectangular leads; enlarge individual holes if necessary rather than forcing a component. Record this deviation with the prototype's fabrication notes; it is not a production drill-size change.

Keep ramping off for the 1.1 mm pockets. The small-hole drilling path plunges at the centers without pocket interpolation.

### Pocket registration holes

Select the four 4 mm circles and add another T3 pocket using the same 1.8 mm final depth. Cut these after the electrical holes. The registration pins go in after the entire bottom file finishes.

### Trim an oversized blank

For an oversized blank, select the finished board boundary and create a **2D Contour** path. Choose **Outside**, T3 and the perimeter settings above. Place one tab near the middle of each edge, away from clamps. The cutter center runs 0.4 mm outside the finished edge.

Run this path last. Leave its tabs attached until the laser work is complete, then remove them by hand. For a blank already at 150 × 100 mm, omit perimeter machining.

## Export the combined NC file

1. Save the Studio project and select the **Carvera Air** machine profile.
2. Arrange the bottom paths in the order listed above, using **Move Up/Move Down** or dragging.
3. Right-click **Paths** and choose **Save All Paths**, or open **Export** and check the paths belonging to step 10. Exclude the top laser paths.
4. Save the checked collection as `10-ctcss-bottom-machine.nc`.
5. Open that NC in the controller preview. Check the default sequence T2 → T3, all 115 holes and the final perimeter path when included.
6. Check the machine envelope against the blank and clamps, then upload the file.

Export the selected paths together. Studio writes the tool transitions into the file; the Air pauses for each tool change and continues with the next operation. Keep the stock clamped during those pauses.

Use the same export method for the other stages, selecting only that stage's paths. Flipping, coating, curing and reseating belong between NC files.

## Mount and machine the bottom

Use the [Air controller controls](https://wiki.makera.com/en/Air/Manual/Air-software) for the work origin, Scan Margin, Auto Z Probe and Auto Leveling.

1. Place a flat sacrificial board beneath the blank. Use an even layer of thin double-sided tape to support the bare substrate face, copper-side up. Add edge clamps outside the toolpaths. Mark the blank's orientation.
2. Set the board's lower-left XY origin from the fixture/anchor position. Enter the actual offset between the selected anchor and that corner. Keep the full cutter path and probe travel clear of the bracket and clamps.
3. Load `10-ctcss-bottom-machine.nc` and enable **Auto Vacuum**, **Scan Margin**, **Auto Z Probe** and **Auto Leveling**.
4. Use approximately 10 mm spacing for the leveling grid: a full 150 × 100 mm grid has 16 × 11 points. Position the grid on supported copper and keep its probe points away from clamps. Run this measurement before cutting holes.
5. Run the file. Install T2 and then T3 as prompted, allowing tool-length calibration after each change. Leave the board secured until the file ends.
6. Remove the board, clean away chips and deburr the holes. Keep the outline tabs attached.

Under magnification, inspect the narrow channels and the track necks at each land. Use a meter and the [assembly drawing](../reference/assembly-top.svg) to check intended continuity and unwanted bridges. Check +8V-to-GND, +5V-to-GND and adjacent header contacts, allowing for intentionally shared nets. Repair bridges and broken tracks now, before coating the top.

## Flip and coat the top

1. Clean the board and fixture. Flip the board left/right about Y and locate it on the registration pins. Secure it flat, supporting the finished copper without crushing lands or traces.
2. Check J1 pin 1 at top-frame (130,40) mm and the orientation mark. The four mounting holes are symmetric, so use this asymmetric feature to confirm the flip.
3. Apply a thin, even top background coat. Flood-cure it for the resin manufacturer's specified time. Keep the holes clear.
4. Return the board to the fixture and establish laser focus on the cured background. Use the laser module's focus spacer/reference.
5. Apply a thin contrasting coat and leave it uncured. Keep it out of direct UV light while preparing the exposure. Re-register after any removal from the fixture.

## Define and run the top legend

Select `top-legend.svg` and create a **Laser Vector** path named `40-top-legend`. Use **Fill** and the laser settings in the recipe table. Set the scan angle to 0° and leave the artwork unmirrored.

Set **LPI to 508**, equivalent to the specified 0.05 mm fill-line spacing: LPI = 25.4 / spacing in mm. If the field accepts only rounded presets, use 500 LPI (0.0508 mm spacing). LPI controls fill-line density; increasing it increases exposure per area at unchanged speed and power. Keep it fixed while adjusting the exposure recipe.

The positive artwork marks the coating to retain. Fill the exported stroke areas and preserve the open centers of letters. Exclude the blue registration guides, crosshairs and board-frame guides. Export only this path as `40-ctcss-top-legend.nc`.

Install and connect the Air laser module using the [tool kit instructions](https://wiki.makera.com/en/Air/Manual/toolkit). Seat it in its keyed orientation and keep the head from rotating. Set the focus at approximately 5 mm below the protective plate, using the module's reference. Keep clamps below the head's travel, wear the specified laser goggles and run with the enclosure closed.

Switch to laser mode and use the machine's laser XY offset. Keep the artwork in its existing board coordinates; apply the offset once through the machine. Establish the top focus independently of the bottom milling Z reference. Keep the contact probe away from the wet contrasting coat.

Load `40-ctcss-top-legend.nc`, check the frame against the board and run it. Wipe away uncured contrasting material with the resin-compatible cleaner used on the sample. Finish curing according to the resin instructions.

## Add bottom solder mask

Use this variation to coat the copper side as well. Keep the top coating/laser procedure unchanged.

| Stage | File | Contents |
| --- | --- | --- |
| 10 | `10-ctcss-bottom-isolation.nc` | T2 contour isolation only (optional clearing is a separate reviewed variation). |
| Manual | Apply and flood-cure bottom mask in place | Keep the board secured and retain the bare-copper WCS and leveling reference. |
| 20 | `20-ctcss-bottom-mask-holes.nc` | T5 pad opening, followed by T3 prototype 0.8 mm drilling, 1.1 mm electrical pockets, registration holes and perimeter. |
| Manual | Clean, inspect, flip and coat top | Follow the top preparation above. |
| 40 | `40-ctcss-top-legend.nc` | Top laser legend. |

Derive pad-opening shapes from the 111 bottom copper lands: 2 mm ordinary lands and 3 mm test-point lands, retaining square pin-1 shapes. Put them on a separate `bottom-mask-openings` layer in the existing flipped bottom frame. The package has no dedicated bottom-mask file, so create this layer in Studio. Keep the top legend separate.

Apply and flood-cure the bottom mask after step 10 **with the board remaining secured in place**. Retain the existing XY origin, bare-copper Z zero and surface-leveling reference. Do not re-zero or re-probe the coated surface before step 20. The Carvera Air's automatic tool-length measurement on tool change supplies the tool offset without resetting the WCS.

For the pad openings, create a T5 **2D Pocket** operation with **Parallel** strategy and these settings:

| Parameter | Setting |
| --- | --- |
| Z reference | Retained bare-copper WCS zero |
| Start depth | −0.5 mm: approach begins above the coating |
| End depth | +0.1 mm: nominal 0.1 mm spring engagement at exposed copper |
| Step-down | 0.6 mm, overriding the tool's 0.2 mm default |
| Clearing passes | One, at +0.1 mm end depth |
| Safe travel height | 10 mm |
| Feed and spindle | PCB preset for the spring-loaded mask-removal tool |

The 0.6 mm step-down spans the programmed approach from −0.5 to +0.1 mm; it is not 0.6 mm of spring compression. Check that the calculated pocket has one clearing level at +0.1 mm, with no intermediate clearing passes through air. The spring-loaded tool removes the coating while maintaining contact at the copper surface.

Add the T3 hole and perimeter operations after the mask pocket and export the complete T5 → T3 sequence as step 20. Those operations retain their existing depths from bare-copper zero. Keep the board secured throughout tool changes. Inspect the exposed lands after the file finishes and record any setting changes from the result before the next board.

An edge-located fixture handles coating removal and reseating without pre-cut holes. For a fixture that requires pins before isolation, export the four registration pockets as `05-ctcss-registration.nc`, cut them first, then deburr and install the pins. Remove those pockets from step 20 and re-probe the seated board before step 10.

## Finish the board

Remove perimeter tabs by hand and smooth the edges. Clear the holes, inspect the legend and dry-fit the socket strips and components. Repeat continuity and short checks after the final cleaning, then follow [assembly and bring-up](assembly-and-bring-up.md).

Save the Studio project, selected NC revisions and working settings together. Record changes beside the sample or board photos so the next board starts with the improved recipe.

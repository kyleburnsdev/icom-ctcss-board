# Makera Studio toolpaths and board fabrication

Make the board in two machine stages: complete the bottom copper and holes, then flip the board and laser-cure the top legend. Keep all operations for an unchanged stock setup in one NC file, including tool changes. End the file before cleaning underneath the board, reseating it, coating it or turning it over.

Use 1.5 mm single-sided copper-clad stock, 150 mm along machine X and 100 mm along machine Y. Components mount on the bare substrate side; copper faces down on the finished board. Use the current two-pin J5 / four-pin J6 files.

This procedure follows the [Makera CAM guide](https://wiki.makera.com/en/software/MakeraCAM_userguide), [Carvera Air manual](https://wiki.makera.com/en/Air/Manual) and [LED Light example](https://wiki.makera.com/en/Air/Manual/Air-LED-Light). Use the recipe below for the first attempt and adjust it from the results.

## Job files and order

Start with bare bottom copper for the first board. Add bottom solder mask using the separate section near the end when you want that finish.

| Order | Action | NC file |
| --- | --- | --- |
| 1 | Mount the blank copper-side up; probe and level it. | Setup only |
| 2 | Clear copper, finish isolation, pocket electrical and registration holes, and trim the perimeter when using an oversized blank. | `10-ctcss-bottom-machine.nc` |
| 3 | Clean, deburr, check continuity, flip the board, apply and cure the top background, then apply the contrasting coat. | Manual work between files |
| 4 | Selectively cure the top legend with the laser. | `40-ctcss-top-legend.nc` |
| 5 | Wipe away uncured coating, remove tabs, finish edges and inspect. | Manual finish |

Step numbers leave room for the bottom-mask stage. Keep registration holes in step 10: install the locating pins after that file finishes, for use during the flip. Initial hold-down uses the blank's edges and tape, so it does not need pre-cut registration holes.

Save final Studio projects and numbered NC files under `manufacturing/pcb/carvera-air/`. Add a revision suffix when changing a job, such as `10-ctcss-bottom-machine-r02.nc`. Keep only the selected revision in the machine's active job folder. Put inspection notes and photos in `docs/verification/`.

## Open the project and check alignment

Open [ctcss-board-cam.mkc](../../manufacturing/pcb/carvera-air/landscape-y-flip/ctcss-board-cam.mkc) from the [landscape CAM package](../../manufacturing/pcb/carvera-air/landscape-y-flip/README.md). Keep the project beside its source imports. Inspect the existing layers before importing anything else so each object appears once.

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
| `bottom-electrical-holes-Y-FLIPPED.drl` | 48 holes at 0.9 mm and 63 holes at 1.1 mm. |
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
| T3 | 0.8 mm corn bit | Broad copper clearing, hole pockets and perimeter. |
| T5 | UV solder-mask removal tool | Pad openings in the bottom-mask workflow. |
| Laser | Carvera Air laser profile | Top legend curing. |

Select the **PCB material preset** for each cutter. Keep its spindle speed, feed and plunge settings for the first run. For T2, use 30° included angle and a 0.2 mm flat tip. For T5, use the spring-loaded solder-mask profile.

Use these first-run operation settings. The depths and laser power choices follow Makera's PCB recipe; the stepover, stepdown, fill interval and tab dimensions are this project's starting choices.

| Operation | Settings |
| --- | --- |
| Copper clearing and isolation | Start depth 0; end depth 0.05 mm below copper surface. Tools in order: T3, then T2. Use 40% tool-diameter stepover. |
| Hole pockets | T3; Parallel pocket strategy; ramping off; 0.3 mm stepdown; final depth stock thickness + 0.3 mm, giving 1.8 mm for 1.5 mm stock. |
| Perimeter | T3; Outside contour; 0.3 mm stepdown; 1.8 mm final depth; four tabs, each 3 mm wide and 0.5 mm thick. |
| Bottom mask openings | T5; Parallel pocket strategy; 0.2 mm nominal engagement depth; PCB preset feed and spindle settings. |
| Top legend | Laser Vector, Fill; speed 100 mm/min; 20% power for a light contrasting coat or 30% for a dark one; 0.05 mm line interval; one pass. |

Depth values in this table are positive distances below the starting surface. Use a 10 mm safe height for spindle jobs and keep clamps below that travel plane. Laser focus and clearance are set separately in the laser section.

## Run a small first test

Cut a small sample on spare matching stock before the full board. Include a 0.5 mm gap, a 0.5 mm track, two 2 mm lands at 2.5 mm pitch, 0.9/1.1/4 mm holes and a small patch of the top legend. Use the same operation settings as the board.

Inspect the result and make these adjustments:

| Result | Adjustment |
| --- | --- |
| Copper remains across an isolation channel | Clean and reseat the sample, rerun leveling, and increase isolation depth from 0.05 to 0.07 mm. |
| Electrical holes are tight | Measure the holes, correct T3's effective diameter in the tool profile and regenerate the pockets. Keep the nominal 0.9/1.1 mm design diameters. |
| Cutter chatters or leaves ragged holes | Reduce feed by 25% and stepdown from 0.3 to 0.15 mm. |
| Registration pins bind | Deburr first, then enlarge the registration pockets in 0.02 mm diameter increments until the pins slide in without force. |
| Laser-cured strokes wash away | Increase exposure by reducing speed by 20%. |
| Legend strokes spread or the background discolors | Reduce exposure by increasing speed by 20%. |

Dry-fit an actual component lead and socket pin. Test the registration pins and perform one flip. Wipe the laser sample to judge the retained legend. Save the settings that give the best result and use them for the board.

## Define the bottom toolpaths

Create these paths in execution order. Export them together as `10-ctcss-bottom-machine.nc`.

| Order | Path name | Tool |
| --- | --- | --- |
| 1 | `10-copper-clear` | T3 |
| 2 | `11-copper-isolate` | T2 |
| 3 | `12-electrical-0p9-48holes` | T3 |
| 4 | `13-electrical-1p1-63holes` | T3 |
| 5 | `14-registration-4mm-4holes` | T3 |
| 6 | `15-perimeter` | T3; omit for a finished-size blank |

### Clear copper and finish isolation

Select the board boundary and the nested positive copper artwork for a **2D Pocket** operation. The pocket is the background surrounding the tracks and pads. In the preview, the tracks and pads remain as copper islands connected by their intended traces.

Add T3 first and T2 second to the pocket's tool list. T3 clears the broad areas; T2 finishes the narrow channels. Use the 0.05 mm depth and the material settings above. The actual board has 0.5 mm minimum gaps, so T2 handles the areas that T3 cannot enter.

Calculate the paths and inspect a close pair of capacitor pads and both Pro Micro socket rows. The 2 mm lands, 0.5 mm signal tracks and 1 mm power/ground tracks must remain intact. Check that the calculated pocket fills the background rather than the positive copper shapes.

Use the multi-tool pocket as one operation when Studio presents it that way; the two copper path names above describe its execution order. Keep both tools' output in the step 10 export.

### Pocket the electrical holes

Select the 0.9 mm drill circles and create a **2D Pocket** path using T3. Use the hole settings above. Repeat for the 1.1 mm circles.

When the drill import displays only centers, create circles of the required diameter at those centers before making the pockets. Use pocket operations, rather than a drilling operation that would produce the cutter's 0.8 mm diameter.

Check the path counts: 48 small holes and 63 larger holes. J5 has two holes, J6 has four, and the Pro Micro has two rows of twelve. All holes are unplated, including those categorized as PTH in the CAD exports.

Keep ramping off for these pockets. The 0.9 mm hole leaves only 0.05 mm of radial cutter-center travel; a large helical entry does not belong inside it.

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
5. Open that NC in the controller preview. Check the sequence T3 → T2 → T3, all 115 holes and the final perimeter path when included.
6. Check the machine envelope against the blank and clamps, then upload the file.

Export the selected paths together. Studio writes the tool transitions into the file; the Air pauses for each tool change and continues with the next operation. Keep the stock clamped during those pauses.

Use the same export method for the other stages, selecting only that stage's paths. Flipping, coating, curing and reseating belong between NC files.

## Mount and machine the bottom

Use the [Air controller controls](https://wiki.makera.com/en/Air/Manual/Air-software) for the work origin, Scan Margin, Auto Z Probe and Auto Leveling.

1. Place a flat sacrificial board beneath the blank. Use an even layer of thin double-sided tape to support the bare substrate face, copper-side up. Add edge clamps outside the toolpaths. Mark the blank's orientation.
2. Set the board's lower-left XY origin from the fixture/anchor position. Enter the actual offset between the selected anchor and that corner. Keep the full cutter path and probe travel clear of the bracket and clamps.
3. Load `10-ctcss-bottom-machine.nc` and enable **Auto Vacuum**, **Scan Margin**, **Auto Z Probe** and **Auto Leveling**.
4. Use approximately 10 mm spacing for the leveling grid: a full 150 × 100 mm grid has 16 × 11 points. Position the grid on supported copper and keep its probe points away from clamps. Run this measurement before cutting holes.
5. Run the file. Install T3, T2 and T3 again as prompted, allowing tool-length calibration after each change. Leave the board secured until the file ends.
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

The positive artwork marks the coating to retain. Fill the exported stroke areas and preserve the open centers of letters. Exclude the blue registration guides, crosshairs and board-frame guides. Export only this path as `40-ctcss-top-legend.nc`.

Install and connect the Air laser module using the [tool kit instructions](https://wiki.makera.com/en/Air/Manual/toolkit). Seat it in its keyed orientation and keep the head from rotating. Set the focus at approximately 5 mm below the protective plate, using the module's reference. Keep clamps below the head's travel, wear the specified laser goggles and run with the enclosure closed.

Switch to laser mode and use the machine's laser XY offset. Keep the artwork in its existing board coordinates; apply the offset once through the machine. Establish the top focus independently of the bottom milling Z reference. Keep the contact probe away from the wet contrasting coat.

Load `40-ctcss-top-legend.nc`, check the frame against the board and run it. Wipe away uncured contrasting material with the resin-compatible cleaner used on the sample. Finish curing according to the resin instructions.

## Add bottom solder mask

Use this variation to coat the copper side as well. Keep the top coating/laser procedure unchanged.

| Stage | File | Contents |
| --- | --- | --- |
| 10 | `10-ctcss-bottom-isolation.nc` | T3 copper clearing and T2 fine isolation. |
| Manual | Apply and flood-cure bottom mask | Keep the same edge datum for reseating. |
| 20 | `20-ctcss-bottom-mask-holes.nc` | T5 pad opening, followed by T3 electrical holes, registration holes and perimeter. |
| Manual | Clean, inspect, flip and coat top | Follow the top preparation above. |
| 40 | `40-ctcss-top-legend.nc` | Top laser legend. |

Derive pad-opening shapes from the 111 bottom copper lands: 2 mm ordinary lands and 3 mm test-point lands, retaining square pin-1 shapes. Put them on a separate `bottom-mask-openings` layer in the existing flipped bottom frame. The package has no dedicated bottom-mask file, so create this layer in Studio. Keep the top legend separate.

Apply and flood-cure the bottom mask after step 10. Reseat against the same edges, establish the coated surface reference, and level the surface before running step 20. Keep the leveling points on supported coated material.

For the pad openings, create a T5 **2D Pocket** operation with **Parallel** strategy and 0.2 mm nominal spring engagement. Use the PCB preset. Add the T3 hole and perimeter operations after it and export the complete T5 → T3 sequence as step 20. Inspect the exposed lands after the file finishes; remove any remaining mask before soldering.

An edge-located fixture handles coating removal and reseating without pre-cut holes. For a fixture that requires pins before isolation, export the four registration pockets as `05-ctcss-registration.nc`, cut them first, then deburr and install the pins. Remove those pockets from step 20 and re-probe the seated board before step 10.

## Finish the board

Remove perimeter tabs by hand and smooth the edges. Clear the holes, inspect the legend and dry-fit the socket strips and components. Repeat continuity and short checks after the final cleaning, then follow [assembly and bring-up](assembly-and-bring-up.md).

Save the Studio project, selected NC revisions and working settings together. Record changes beside the sample or board photos so the next board starts with the improved recipe.

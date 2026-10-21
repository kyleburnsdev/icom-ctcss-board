# Implementation acceptance checklist



Authority: [board specification](../requirements/board-specification.md).

Design evidence is linked in the [implementation index](README.md) and [independent review](design-review.md). Checked items record CAD/documentation evidence only. Unchecked combined items include physical acceptance that cannot be inferred from CAD.



## Schematic release to layout



- [x] Annotated schematic includes pass-through, RAW supply branch, MCU, UI, PTT sense/driver, tone chain, supply capacitors, and all eight required test connections.

- [x] Exported connectivity proves header pins 1/2/3/4/8 pass through; pins 6/7 share GND; microphone and radio PTT are separate nets.

- [x] Exact Pro Micro header map joins Arduino names, symbol pins, and footprint pads; clone fit and USB-C envelope are recorded separately from generic library compatibility.

- [x] Exact transistor package map joins datasheet leads, symbol pins, and footprint pads; reset pull-down and open-collector topology are verified.

- [x] Tone chain order and values match the specification; trimmer and coupling-capacitor choices have documented loaded-response calculations.

- [ ] Every populated board part has a reviewed THT footprint; Pro Micro socket compatibility and body clearances are recorded.

- [x] Direct KiCad ERC completes; findings are resolved or individually justified.

- [x] Rendered schematic is visually inspected for legibility, collisions, signal flow, and page boundaries.

- [x] PCB synchronization dry run is reviewed before applying its exact revision.



## PCB and fabrication



- [x] One 100 mm × 150 mm rectangular outline, independently measured.

- [x] Four 4 mm NPTH holes, each center 6 mm from adjacent edges.

- [ ] Actual standoff/washer clearance checked (4 mm hardware-radius allowance; hardware unselected).

- [x] Components mount above the board; footprint provides two 1×12 socket rows at 15.24 mm spacing.

- [ ] Actual female socket strips and module dry-fit successfully.

- [x] All required connections routed exclusively on B.Cu, with no routing vias, jumpers, inner/top tracks, or copper pours.

- [x] Ground uses dedicated buses/branches; independent width-aware review confirms analog and UI separation upstream of the PTT/radio junction.

- [x] Nominal selected-body spacing is at least 2 mm, including conservative socket/module envelope (minimum 2.14 mm).

- [ ] Purchased-part bodies, connector access and trimmer tool access physically checked.

- [ ] Actual pad/drill dimensions and lead fit recorded; bottom solder joints accessible without routing between header pads where avoidable.

- [x] CNC track/clearance geometry and provisional current/copper assumptions documented.

- [ ] Actual copper thickness/current demand and milling coupon validate those assumptions.

- [x] Direct DRC completes against saved, current design with no unresolved shorts, clearance failures, or required unrouted connections.

- [x] Independent inventory confirms copper restrictions and THT technology, including the virtual F.Cu lands introduced by native THT normalization. B.Cu-only physical output is separately constrained.

- [x] Fabrication package contains bottom copper only and explicitly states single-sided manufacturing/drill requirements.



## Assembly and bench acceptance



- [x] Top legend Gerber and matching full-board SVG exported and visually inspected; duplicate native reference/value fields excluded, readable board labels retained.
- [x] Landscape top/bottom registration views include four 4 mm mounting-hole guides at 138 × 88 mm pitch; Y-flipped copper/drill coordinates checked against every exported object.
- [ ] Actual fixture/flip repeatability, scale and asymmetric pin-1 alignment proven on the machine before machining/exposure.
- [ ] Physical populated-board markings remain readable after the Carvera Air UV-mask/laser process: references, values, pin functions, pin 1, transistor leads, capacitor polarity, module orientation, trimmer adjustment direction, and block names.

- [ ] Top and bottom visual reviews cover soldering access, socket insertion, USB-C cable clearance, enclosure, cables, and test-point access.

- [x] BOM and assembly drawing include lead spacing, polarity, socket details, and assembly order.

- [x] Bring-up instructions cover visual inspection, unpowered short checks, module orientation/insertion with power off, and current-limited supply tests before radio/UI connection.

- [ ] Actual radio/microphone cable mapping verified, especially pins 4/6/7/8.

- [ ] Radio supply capacity checked against measured MCU, LCD backlight, encoder, pull-up, and LED load; module thermal behavior checked.

- [ ] USB/radio power procedure defined and checked for unintended backfeeding.

- [ ] Radio PTT voltage/current measured; selected driver reliably keys and releases, including reset/power-loss tests.

- [ ] Loaded tone amplitude/range, 151.4 Hz response, carrier rejection, and achievable deviation checked on the actual radio.

- [ ] Microphone bias/loading, audio noise, and distortion checked with tone enabled and bypassed.

- [ ] UI cable order and actual LCD/encoder electrical interfaces verified.



Firmware is outside this deliverable. Hardware acceptance must identify any checks that require suitable test firmware and remain outstanding until that evidence exists.



The final CAD checks report ERC 0/0, DRC 0 errors/0 unconnected with 114 retained warnings, 61 netlist assertions passed, and no routing vias or pours. See the review for warning dispositions. Ground is routed as buses/branches; physical audio-noise performance remains unverified. Firmware is not supplied.


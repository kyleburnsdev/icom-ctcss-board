# Icom IC-229H selectable CTCSS interface

A Pro Micro based interface that adds selectable CTCSS tones to an Icom IC-229H microphone audio path, with PTT forwarding, an encoder, LCD, bypass control and status LEDs.

The schematic and routed PCB prototype are complete; assembly components have been ordered and the PCB is prepared for assembly. The first enclosure iteration is implemented in FreeCAD with print-oriented parts and fit coupons. Pro Micro firmware and a NUCLEO-F767ZI phase-one test driver are implemented, with build, host-test and USB verification. Begin breadboard testing with the [phase-one guide](docs/implementation/firmware-phase1-guide.md); wired timing, UI hardware and analog/radio acceptance remain outstanding. Manufacturing process evidence is recorded separately in the relevant packages.

| Area | Entry point |
| --- | --- |
| Requirements, parts and build instructions | [Project documentation](docs/README.md) |
| Electronics | [KiCad project](electronics/icom-ctcss-board.kicad_pro), with project-local libraries beside it |
| PCB manufacturing | [Carvera Air package](manufacturing/pcb/carvera-air/README.md) |
| Sublimation feature trial | [Color artwork and coupon](manufacturing/pcb/sublimation/README.md), [white-mask fabrication guide](docs/pcb-fabrication-guide.md) |
| PCB jig / FreeCAD CAM migration | [Required changes and job contract](docs/implementation/pcb-jig-and-freecad-cam.md) |
| Enclosure | [Mechanical workspace](mechanical/enclosure/README.md) |
| Arduino firmware | [Firmware workspace](firmware/README.md) |
| Engineering scripts | [Tools and dependencies](tools/README.md) |
| Repository layout and verification | [Layout notes](docs/implementation/repository-layout.md) |

Open the KiCad project from `electronics/` so its project-local symbol and footprint tables resolve. Keep each manufacturing package together when copying it to another machine.

Original project material is licensed under the [MIT license](LICENSE). Third-party material retains its own terms; see [third-party notices](docs/third-party-notices.md).

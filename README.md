# Icom IC-229H selectable CTCSS interface

A Pro Micro based interface that adds selectable CTCSS tones to an Icom IC-229H microphone audio path, with PTT forwarding, an encoder, LCD, bypass control and status LEDs.

The schematic and routed PCB prototype are complete. Firmware, enclosure design, physical manufacturing and radio acceptance remain outstanding. Manufacturing files are preparation material; machine settings and the physical process still require coupon validation.

| Area | Entry point |
| --- | --- |
| Requirements, parts and build instructions | [Project documentation](docs/README.md) |
| Electronics | [KiCad project](electronics/icom-ctcss-board.kicad_pro), with project-local libraries beside it |
| PCB manufacturing | [Carvera Air package](manufacturing/pcb/carvera-air/README.md) |
| Makera Studio CAM | [CAM project and supporting imports](manufacturing/pcb/carvera-air/landscape-y-flip/README.md) |
| Enclosure | [Mechanical workspace](mechanical/enclosure/README.md) |
| Arduino firmware | [Firmware workspace](firmware/README.md) |
| Engineering scripts | [Tools and dependencies](tools/README.md) |
| Repository layout and verification | [Layout notes](docs/implementation/repository-layout.md) |

Open the KiCad project from `electronics/` so its project-local symbol and footprint tables resolve. Keep each manufacturing package together when copying it to another machine.

Original project material is licensed under the [MIT license](LICENSE). Third-party material retains its own terms; see [third-party notices](docs/third-party-notices.md).

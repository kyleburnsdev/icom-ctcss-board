# PCB CAM source

Open [icom-ctcss-pcb-cam.FCStd](icom-ctcss-pcb-cam.FCStd) in FreeCAD 1.1.1.
Six native jobs implement prepared-hole setup, bottom isolation, bottom pad
clearing, bottom/top diamond-drag legends and final floor-referenced bores.
ManufacturingGeometry contains artwork-derived wires. SetupSummary contains
editable settings, independent repeat-pass offsets and source hashes.

Follow the [fabrication guide](../../docs/pcb-fabrication-guide.md) and
[package instructions](../../manufacturing/pcb/carvera-air/README.md).
All coating/curing stays in the jig. Preserve copper zero/map until pad clearing,
then use deliberate mask-surface references for legends and a floor reference
for the final sacrificial-backed hole setup. Spindle stays off for T6 drag jobs.

Initial spring overtravel/preload is 0.05 mm. Inspect before lowering only the
applicable operation offset; save/recompute/export/recheck after changes. The
nominal final underside +1.00 mm and breakthrough 0.15 mm give tip Z+0.85 mm.
No perimeter job is needed for this full-size blank. Physical trial acceptance
and inventory completeness are pending; native checks are not machine runs.

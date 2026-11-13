# PCB CAM source

Open [icom-ctcss-pcb-cam.FCStd](icom-ctcss-pcb-cam.FCStd) in FreeCAD 1.1.1.
Use Job00_RegistrationPreparation only for an unprepared blank, then
Job10_BottomCopper, Job20_BottomMaskRemoval and Job50_BottomHoles at the stages
in the [fabrication guide](../../docs/pcb-fabrication-guide.md).
Drill after bottom pad clearing and before the first flip so holes can help
align the top transparency. A repeat hole pass after top work is conditional
on obstruction. This revised order is a proposed, unrun sequence.

ManufacturingGeometry contains machining wires; SetupSummary contains
parameters and source hashes. Preserve original copper zero/map through pad
clearing. Drilling uses aluminium-floor Z0 and sacrificial backing, with no
copper map. Then flip and coat/cure top in the jig; release for heat transfer.
The same floor-referenced contract applies to conditional hole cleanup.

Initial pad-tool overtravel is 0.05 mm. Inspect before lowering MaskPassOffset;
save/recompute/export/recheck after changes. The selected underside +1.00 mm
and breakthrough 0.15 mm give tip Z+0.85 mm. No routine perimeter job is needed.
Native checks do not establish physical machining acceptance. See the
[package](../../manufacturing/pcb/carvera-air/README.md).

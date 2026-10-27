# ATS-TI1OP-521-C1-R1 KiCad footprint and STEP model

19 October 2026. Project-local CAD assets only: no production schematic, PCB, project or preference files were modified. The old 20 x 18 mm heatsink footprint is retained. This does not select or purchase a different heatsink for the project.

## Files and installation

- `TPA3126.pretty/Heatsink_ATS_ATS-TI1OP-521-C1-R1_50x13.9mm_H25mm_P40mm.kicad_mod`
- `TPA3126.3dshapes/ATS-TI1OP-521-C1-R1.step`

The footprint is already available through this project's `Custom` footprint library. Assign it to a Mechanical:Heatsink symbol when adopting this heatsink, or add it directly in the footprint chooser during a separately authorized layout step. The model link is `${KIPRJMOD}/TPA3126.3dshapes/ATS-TI1OP-521-C1-R1.step`, scale 1, zero rotation/offset. For another project, copy both folders beside its `.kicad_pro` and register the footprint library; the project-relative model path will then resolve.

## Geometry and references

Nominal body 50 x 13.9 x 25 mm. Long axis X, width Y, height Z. Origin is the heatsink's plan centre; nominal end mounting faces define Z=0. Two vertical #4-40 threaded mounting axes lie at X=-20 and +20 mm, Y=0; nominal blind-thread depth 6.5 mm. The footprint has unnumbered **3.2 mm NPTH clearance holes**, a deliberately selected PCB clearance for #4 screws rather than a manufacturer-prescribed PCB drill. Use #4-40 hardware; do not substitute M3 on the assumption the threads are interchangeable. Confirm screw length, PCB thickness, washers and thread engagement, with no bottoming in the blind holes.

TI Fig.39 and the ATS drawing show end feet at Z=0, central contact land at Z=1 mm and relieved sections at Z=3 mm. In X, the end-foot intervals are -25 to -15 and +15 to +25 mm; the central contact land is -5.5 to +5.5 mm (11 mm long). The two relieved gaps are 9.5 mm long. The 6.35 mm minimum foot width follows TI's section drawing. The taper shoulder width, fin thickness, fin-root height and radii are not fully dimensioned: this model uses an illustrative 9.525 mm shoulder, 2 mm fins and root plane Z=7 mm. Fin-root rounds are omitted. The finished outer envelope and published machining levels/locations are retained.

The STEP represents one physical extrusion as nine touching closed geometric subsolids. Screw holes are 48-sided smooth 2.845 mm major-diameter approximations, not a threaded helix or a tap-drill specification. This is a simplified mechanical reference model, not manufacturer machining CAD. All geometry uses millimetres. ATS's sheet prints `ATS-TI10P-521-C1-R1`, while distributor catalogues use `ATS-TI1OP-521-C1-R1`; the linked product/sheet and dimensions identify the requested part.

## Footprint layers and clearance

- F.Fab: nominal 50 x 13.9 mm body envelope.
- F.CrtYd: two conservative end-foot reservations, using the full maximum body width plus margin. Keep other components out of these mounting/fastener areas.
- Cmts.User: underside contact-region guides. Their transverse taper width is illustrative; use actual part dimensions to qualify close placements.
- Dwgs.User: full 53 x 16.9 mm manual assembly guide, centre mark and underside-height notes.

There is no solid courtyard across the middle: U1 must sit beneath the sink's contact land, and low parts may sit under the relieved gaps. The full-body drawing guide does not automatically enforce 3D component-height clearance. Keep exposed copper away from mounting metal unless deliberately grounded. No electrical pad/net is assigned to the heatsink.

**Important mounting-stack check:** the contact land is 1 mm above the nominal end-foot plane, while U1's published top height is 1.00-1.15 mm. Real interface material, part tolerances and preload therefore matter. The zero-offset STEP is a geometric datum, not a claim that the feet and IC can all be clamped to nominal planes without adjustment. Check the real assembly, set model Z if needed to match it, and do not bend the board or crush U1 to make the screws seat.

The relieved areas provide nominal 3 mm underside height above the foot plane, which is useful for the 1.35 mm maximum bootstrap-capacitor bodies. Check solder height and actual relief boundaries. This longer sink is **not a drop-in placement replacement** for the old 20 x 18 mm outline: its end mounting regions encroach on present L2 and DAC-side component positions when centred on the current U1. Placement needs a separate review; none was changed here.

## Verification and previews

KiCad 10.0.5 successfully parsed/exported the footprint, loaded and raytraced the STEP with U1 and four bootstrap capacitors on an isolated fixture, and re-exported the heatsink to STEP with all 9 solids. Model bounds are 50 x 13.9 x 25 mm; mounting axes and footprint holes agree on 40 mm pitch. Independent checks confirm every subsolid has a closed, consistently oriented shell and positive volume, millimetre units, the relative model path, and unchanged production files. See `geometry.json`, `shell-topology.json`, `validation.json` and `source-preservation.json`.

The isolated fixture DRC command aborted with exit 134 and produced no report. **DRC is not claimed to pass.** No production-board DRC was run. The fixture is a model-import/visualization aid, not a routed design or a qualified mounting assembly. `underside-exploded-preview.png` deliberately lifts the model by 7 mm to expose the underside; this is not the installed height. `assembly-preview.png` uses the footprint's nominal zero-offset datum.

No physical fit, screw, load/preload, thermal or enclosure tests were performed. Manufacturer thermal figures are airflow-dependent: 8.5 C/W at 200 LFM unducted, and 4.3 C/W at 800 LFM. Neither is a still-air sealed-compartment rating. MCP returned no matching stock record; no inventory was changed.

## Sources

- ATS manufacturer's sheet: https://www.qats.com/DataSheet/ATS-TI1OP-521-C1-R1
- Retrieved manufacturer-sheet mirror: https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/931/ATS-TI10P-521-C1-R1.pdf
- TI TPA3126D2 datasheet, section 11.3/Figure 39: https://www.ti.com/lit/ds/symlink/tpa3126d2.pdf

`build_ats.py` regenerates the model and footprint with standard Python. Its optional local test-fixture generation runs only if this project's production board is available and uses the current component footprints; the packaged fixture is already provided for inspection. Paths inside the fixture resolve to the original project for this local verification and should be updated if relocating it. The reusable production footprint itself has a relative model link.

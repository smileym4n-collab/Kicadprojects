# L1 horizontal air-core inductor visual model

STEP model based on the supplied photograph and the current L1 footprint. Coil axis runs between pins 1 and 2, parallel to the PCB.

The existing footprint is preserved: pad 1 (-6,-6), pad 2 (6,-6) mm, 12 mm pitch, 2.3 mm drills. STEP coordinates use X=footprint X, Y=-footprint Y and Z=0 at PCB top. Leads extend 3 mm below PCB top.

Illustrative winding: 10 turns, 1.1 mm wire, 1.2 mm pitch, 11.6 mm mean diameter; outer diameter 12.7 mm, maximum height 13.65 mm. These dimensions are assumptions for visual representation, not measured part dimensions or a calculation guaranteeing 0.95 uH. Verify against the physical inductor before checking enclosure clearance or fabrication fit.

To use in the existing project: copy the included YamahaSalvage.3dshapes folder to the project root. In L1 footprint properties, add ${KIPRJMOD}/YamahaSalvage.3dshapes/L_AirCore_0u95H_P12_Horizontal.step with scale 1,1,1 and zero rotation/offset. A matching footprint with this model reference is included for reuse. Existing project design files have not been edited.

Validation: smooth STEP reimport and solid validity checks; isolated KiCad board render for visual alignment. See validation.json and preview.png. This is mechanical visualisation only, not electrical or fabrication qualification.

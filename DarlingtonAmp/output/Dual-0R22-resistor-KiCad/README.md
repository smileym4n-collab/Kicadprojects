# Dual 0R22 emitter resistor 3D model

Custom approximate ceramic resistor model for R1 and R23 using the existing `YamahaSalvage:R_Dual_Power_L31_W5_H18_P10` footprint.

- Body: 31 × 5 × 18 mm, as confirmed by the user; chamfered ceramic casing.
- Pin centres at PCB surface: X = -10, 0, +10 mm; Y = 0. Matches 10 mm adjacent pitch.
- Leads: nominal 1 mm diameter, matching the footprint description; 1.3 mm holes.
- Body bottom: 3 mm above PCB, assumed mounting height. Leads extend 3 mm below PCB top.
- Outer lead bends and surface marking are illustrative. The photograph is a style reference, not a dimensioned manufacturer drawing for this 31 mm part.
- No power rating is asserted by the marking. Confirm actual part dimensions, lead forming, mounting height and thermal clearance on the bench.

## Install

Copy `YamahaSalvage.3dshapes` into the target project directory. In PCB Editor, open R1 / R23 Properties → 3D Models and add:

`${KIPRJMOD}/YamahaSalvage.3dshapes/R_Dual_0R22_L31_W5_H18_P10.step`

Use scale 1, rotation 0°, and offset 0 mm on all axes. Both footprints use the same model.

The included `.kicad_mod` is a copy of the existing project footprint with only the model reference added. It can replace the library footprint if desired; an existing board instance still needs its model assigned or updated from the library. Production board, schematic and project files were left unchanged.

This is a visual/mechanical aid, not manufacturer-certified geometry or thermal/layout qualification.

## Validation

Pad centres were checked against the saved R1 and R23 instances in DarlingtonAmpDual and R1 in DarlingtonAmp. KiCad 10 imported and rendered the STEP successfully; the final image was visually inspected. A STEP export of the isolated test assembly also retained the component solids. The model uses faceted planar surfaces with 32-sided lead sections. This verifies CAD placement, not real-part fit or thermal suitability.

# Standard KiCad footprint revision — 25 October 2026

20 placements converted from custom footprints to installed standard KiCad footprints:

| References | Standard footprint |
|---|---|
| QOUT1/QOUT2/QSINK1/QSINK2 | Package_TO_SOT_THT:TO-3P-3_Vertical |
| Q6/Q7/Q8/Q9/Q10 | Package_TO_SOT_THT:TO-220F-3_Vertical |
| R5/R10/R12/R13/R14/R17/R18/R24/R32/R33/R34 | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal |

58 of 62 assigned footprints now come from standard KiCad libraries. Selected MPNs, resistor power ratings, values, transistor pin numbering and inventory fields are unchanged. The resistor footprint's generic 0.25 W description is a geometric family description; selected TE LR1 parts remain rated 0.6 W. The TO-220F footprint provides the insulated-package envelope and 2.54 mm pin pitch for the Toshiba drivers; the standard TO-3P pattern uses 5.45 mm pitch. Confirm real lead fit and heatsink/assembly clearances before fabrication as usual.

Only two custom footprint types remain in active use:

- MC34629, three connectors: retains the verified 1.0 mm hole recommendation, locking-wall outline and manufacturer pin-1 convention. A generic 2.54 mm pin-header outline is too small for the shrouded body; the checked Molex footprint is not an exact drawing/numbering match. No connector series substitution was made.
- MCGPR50V478M22X41, one capacitor: 22 mm radial wire-leaded body on 10 mm pitch. The installed standard 22 mm/10 mm options are snap-in footprints, so the radial footprint was retained.

The three unused custom footprint files were moved out of the active library; their copies remain in the before/ backup. The 11 existing unassigned-package gaps remain unchanged. The current BOM in review/inventory-2026-10-25/assignments.csv is synchronized.

The latest saved file again lacked the Q5 mirror-reference junction. The previously authorized junction fix was restored at (170.18,154.94) mm. Apart from that junction, only the 20 footprint fields and their assignment-note fields changed. Other component objects, wiring, inventory selections, PCB, project and preferences are preserved. Reload the schematic in KiCad before saving an already-open older copy.

Final ERC: zero errors and warnings. The independent footprint/preservation verification and the 189 inventory checks pass. No PCB layout was performed.

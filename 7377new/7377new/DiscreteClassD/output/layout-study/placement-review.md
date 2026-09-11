# DiscreteClassD placement study

Created 9 September 2026. This is an **unrouted placement suggestion**, not a finished layout or a fabrication release. The study is based on the saved production PCB captured at the start of this task.

## Delivered files

- `../../DiscreteClassD-layout-study.kicad_pcb`: separate editable study board.
- `DiscreteClassD-layout-study.pdf`: native KiCad drawing, including Edge.Cuts, F.Fab, F.SilkS, footprint pad outlines/numbers, User.Drawings and User.Comments. A3, nominal 2:1; print at actual size to retain that scale.
- `DiscreteClassD-layout-study.svg`: native vector export of the same layers.
- `DiscreteClassD-layout-study.png`: 300 dpi rendering of the placement PDF.
- `DiscreteClassD-connectivity-study.pdf`: two pages of selected signal connectivity and enlarged power-stage connections. These are straight airwires between actual pad centres, with simplified footprint bounds; they are not routed paths or a complete KiCad ratsnest.
- `placement-coordinates.csv`: every footprint position, measured from the original outline's top-left corner, with rotation.
- `local-distances.json`, `study-drc.json`, `verification.json`: measurements and verification evidence.

## Board and floorplan

The original **100 x 100 mm** outline is retained exactly, from KiCad coordinates **(114.757, 51.473) to (214.757, 151.473) mm**. The existing four copper layers and embedded board setup are retained. All parts remain on their original side.

Coordinates below are millimetres from the outline's top-left corner, with Y increasing downward. Component coordinates are footprint origins; radial capacitor body centres are offset from their pad-1 origins.

| Section | Position and purpose |
|---|---|
| Stereo input | J1 at (47.5, 6), on the upper edge. C40 and C45 flank the input buffer. |
| Shared input buffer | U1 at (50, 19). It is one dual OPA1656 package carrying both input paths. |
| Shared PWM comparator | U8 at (50, 30). The existing dual TLV3602 contains both channel comparators. |
| VREF and oscillator | U3 at (49, 41), U7 at (59, 40), with their surrounding timing, divider and bypass parts. This area is above the bridge row, rather than at the centre of the switching-power corridor. |
| Filtered analogue supply | R43 at (36, 34), C50 at (36, 39), C51 at (40, 38), beside the analogue block. |
| Left control | U4 at (25, 29), U5 at (22, 39); the inverter and dead-time parts lead toward the left drivers. |
| Right control | U9 at (75, 29), U10 at (78, 39); broadly mirrored relative to the left logic. |
| Left bridges | Q5/Q6 at X=12; Q7/Q8 at X=28; high-side Y=61.1 and low-side Y=66.9. U2/U6 are immediately to their left. |
| Right bridges | Q105/Q106 at X=72; Q107/Q108 at X=88, at the same Y coordinates. U102/U106 repeat the same geometry. |
| Output filters | L6 at (20, 71.5), L106 at (80, 71.5). C15/C115 are just below the inductor outputs at Y=78. |
| Speaker outputs | J15/J115 at (18, 94)/(78, 94), close to the lower edge. Zobels, output capacitors and output test points are on the clean side. |
| Regulators | U11 at (43, 62), U12 at (58, 62), inside the central thermal-reserve area above the bulk capacitors. |
| Bulk storage | C17/C20 body centres approximately (42.5, 80.5)/(57.5, 80.5). Both existing 1000 uF footprints are preserved. |
| Power entry | J16 at (48, 94), below the bulk capacitors. The notes indicate a central split into two +24 V distribution corridors. No power copper was created. |

The side-by-side stereo power blocks keep both switching stages away from the upper input area. They are translated copies, separated by 60 mm, so matching MOSFETs and gate drivers have the same orientation and local geometry. This is approximate architectural symmetry, not a literal geometric reflection of each footprint. A literal reflection would reverse package handedness; neither channel has been flipped to the other board face.

## Local placement assessment

All distances below are **straight pad-centre to pad-centre distances**, not track lengths, copper-edge gaps, loop inductances or claims of high-frequency performance. Actual routing may be longer. The right channel has the same measurements as the left.

| Connection | Distance |
|---|---:|
| Gate resistor output to either MOSFET gate | 1.84 mm |
| Driver HO to series resistor input | 3.06 mm |
| Driver LO to series resistor input | 2.17 mm |
| HB / HS to bootstrap capacitor terminals | 2.00 / 2.41 mm |
| VDD / VSS to driver 100 nF terminals | 2.31 / 2.80 mm |
| Driver HS to high-side source | 6.54 mm |
| Driver VSS to low-side source | 6.57 mm |
| High-side source to low-side drain | 4.30 mm |
| 100 nF PVDD capacitor to high drain / low source | 6.01 / 6.59 mm |
| 1 uF PVDD capacitor to high drain / low source | 6.91 / 9.84 mm |
| 10 uF PVDD capacitor to high drain / low source | 10.46 / 14.15 mm |
| Bridge A high source / low drain to inductor input | 10.44 / 8.48 mm |
| Bridge B high source / low drain to inductor input | 7.70 / 4.94 mm |

**The gate resistors and bootstrap parts are locally placed, but this study does not fully meet the requested extremely tight PVDD and Kelvin-loop goals.** The approximately 6.5 mm source-reference connections, up to 9.84 mm 1 uF return reach, and unequal A/B switch-node reach remain placement compromises. Do not copy those local arrangements blindly. Refine the transistor/capacitor/driver cluster and check actual return geometry before routing the production board.

The original outline, all existing footprints and optional networks were retained. This constrained the choice of local arrangements. The inductor is tucked between and below the two bridge cells, with its clean outputs facing the output capacitor and speaker connector. No large switch-node copper is proposed. The 330 nF capacitors remain differential; neither speaker terminal is assigned to GND.

The optional diode/alternate-resistor networks are grouped above each driver cell. They are the most difficult parts to accommodate without crowding the active gate paths. Their alternate paths are not optimised; if those DNP parts are populated, move them into a compact network near the relevant gate resistor. Existing test points and snubber footprints also consume meaningful space. Their location and probe-stub capacitance need manual review.

## Annotations and future layers

User.Drawings/User.Comments carry the quiet-area boundary, switching-node advisory boundaries, local PVDD-loop and driver-loop boxes, central regulator reserve, and supply-distribution guidance. They are drawing annotations only: **no real copper zones, pours, routing or enforced keepouts were added**.

The intended future layer roles remain L1 components/critical routing, L2 largely continuous GND, L3 supply distribution and L4 slower signals. Any L2 void should match only the eventual switch-node copper footprint, after checking return paths. The advisory rectangles are not a prescription to remove whole rectangular areas of the ground plane. Do not introduce an analogue/digital ground split.

## Existing issues and manual review before copying

1. **Regulator package and exposed pads:** U11/U12 values say `TPS7A4901DGNR`, while their footprint ID is `Custom:TPS7A4901DRBR`. The supplied TI datasheet distinguishes DGN HVSSOP from DRB VSON. The preserved footprint includes pad 9 on GND, while pads 10-13 have no assigned net; pad 13 is the large central pad. Its overlap with the differently numbered small pads causes the reported internal clearance/mask findings. Resolve the actual orderable package, land pattern and thermal-pad mapping in a separately authorised design correction.
2. **Analogue supply discrepancy:** the saved PCB powers both OPA1656 packages from `+12V_A`, consistent with the requested filtered branch. The on-disk AGENTS.md text says `+12V_GD`. This study preserves the PCB assignments and does not adjudicate that discrepancy.
3. **Bulk capacitor dimensions:** both existing footprints are 12.5 mm diameter, 5 mm pitch. Values only say 1000 uF. Confirm the actual 1000 uF / 35 V parts' diameter, height and lead pitch; no substitution or footprint resizing was made.
4. **Regulator heat:** the central rectangle reserves routing/thermal area; it does not establish adequate copper area or temperature rise. U12 input capacitor C25 is farther from its regulator than ideal because of the adjacent right driver cell. Review that placement along with regulator dissipation and local bypass returns.
5. **Power loops and outputs:** review the measured local distances above, ensure low-side power returns do not share narrow gate-driver return paths, minimise SW copper, and validate both CSAD winding connections/polarity and the selected capacitor packages against the physical parts.
6. **Mechanical access:** connectors face a common lower edge, with J1 opposite them. Check enclosure openings, mating connector bodies, capacitor height, inductor height, soldering access and mounting requirements. No mounting holes or mechanical hardware were invented.
7. **Live schematic saves:** the three active schematic files were saved externally during the task, with contents matching their initial autosaves. This agent did not write them. The production PCB remained unchanged; the study retains the captured PCB net assignments. Check schematic/PCB parity against your desired saved revision before copying placements.

The supplied DMN6070SY pin-out drawing and UCC27301A pin-function text were consulted for layout orientation. The study preserves the existing G/D/S pad assignments, driver numbering, all footprints and all pad nets. This is not a new symbol, land-pattern or complete electrical qualification.

## Verification and limits

- **196 footprints preserved**, including values, identifiers, physical pad/footprint geometry and all existing pad net assignments. Geometry was compared after normalising position and rotation.
- Original Edge.Cuts, layer configuration and embedded PCB setup are unchanged.
- The production PCB SHA-256 still matches the starting snapshot. Production `.kicad_pro`, symbol library and library tables also match their starting hashes.
- Only the separate study omits the captured board's **139 track/via objects and 8 zones**. Original routing and zones remain in the production PCB and the source snapshot.
- Study DRC, KiCad 10.0.5 with the standalone study/default project rules: **zero courtyard overlaps, zero inter-footprint shorts and zero copper-to-edge clearance errors**.
- DRC is **not clean**: 260 findings remain: 18 internal footprint clearance findings, 8 internal regulator mask-bridge findings, 196 small reference-text findings, 25 silkscreen-over-copper and 13 silkscreen-overlap findings. There are **367 unconnected items**, expected for the unrouted study. No errors were suppressed and no rules were relaxed.
- No schematic changes, ERC, routing, final pours, fabrication exports, simulations, bench tests or thermal tests were performed. The PDFs were rendered and visually inspected.

Stop point: placement study and review drawings only. Use this as a floorplan to inspect and adapt manually.

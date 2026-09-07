Completed only local MOSFET decoupling and switch-node routing in the existing DiscreteClassD.kicad_pcb. The PCB is saved and reopened in KiCad. No schematic or project-rule changes.

All 23 added track segments are F.Cu. No vias or new copper zones were used. The previous SW_B pour was replaced by tracks. Existing OUT_A, OUT_B and Net-(C16-Pad1) zones are exactly preserved, including their fill data. Existing four 0.2 mm HB_A/HB_B segments are exactly preserved. There is currently no inner- or bottom-layer ground-plane copper beneath either switching node; no keepout was added.

Widths used:
- SW_A and SW_B: 0.8 mm short source-pad exits; 1.2 mm MOSFET interconnections; 1.5 mm connections into L6.
- +24V: 1.5 mm local capacitor-bank connections and A drain connection; 1.0 mm short B drain-pad approach.
- PGND: 1.5 mm capacitor-bank connections; 1.2 mm local return links; 1.0 mm source-pad approaches.
The short 0.8 mm exits accommodate the SOT-89 source-pad clearance. These dimensions describe the routing; DRC does not establish a continuous-current or thermal rating.

Local current loops (pin 1 = gate, pin 2 = drain, pin 3 = source; pin assignments unchanged):
- A: C10/C11/C12 pad 1 -> local +24V copper -> Q5 drain (2) -> Q5 source (3) -> SW_A -> Q6 drain (2) -> Q6 source (3) -> local PGND copper -> C10/C11/C12 pad 2. C10 is the closest 100 nF capacitor, C11 the immediately adjacent 1 uF, C12 the outer 10 uF.
- B: C4/C5/C6 pad 1 -> local +24V copper -> Q7 drain (2) -> Q7 source (3) -> SW_B -> Q8 drain (2) -> Q8 source (3) -> local PGND copper -> C4/C5/C6 pad 2. C4 is the closest 100 nF capacitor, C5 the immediately adjacent 1 uF, C6 the outer 10 uF.
These describe the high-frequency commutation loops, not simultaneous commanded conduction of both MOSFETs. Neither return uses driver VSS or analogue ground. The two banks remain separate local copper clusters; generic supply distribution was not routed.

Switch-node geometry:
- SW_A joins Q5 source to the right-hand part of Q6 drain, then directly diagonally into L6 pad 1. The drain-to-inductor segment is 3.158 mm centreline; the total added SW_A track length is 6.896 mm, including lengths inside pads.
- SW_B exits Q7 source through a short neck, passes diagonally to the right of Q8 gate into Q8 drain, then directly diagonally into L6 pad 4. The drain-to-inductor segment is 3.529 mm centreline; the total added SW_B track length is 8.476 mm, including lengths inside pads.
- Both are separate top-layer paths immediately beside the MOSFETs and inductor. Neither passes beneath drivers, logic or analogue circuitry. No switch-node pour remains.

Placement changes (board coordinates in mm):
| Part | Before x,y,rotation | After x,y,rotation | Translation |
|---|---|---|---|
| Q5 | 175.895,83.947,0 deg | 175.895,83.947,180 deg | 0 mm |
| C6 | 184.4925,60.198,0 deg | 167.0055,69.5575,-90 deg | 19.834 mm |
| C12 | 159.512,92.456,90 deg | 167.0055,82.423,90 deg | 12.523 mm |
Q5 rotation brings its source toward Q6 drain. C6 and C12 are now adjacent to their 1 uF capacitors. Q5 reference/value positions were retained and C12 value text repositioned to avoid new overlaps. No other footprint changed, and L6 remained fixed.

Verification:
- KiCad 10.0.5 DRC with all severities, all track errors and zone refill: 8 existing clearance errors, 126 existing warnings, 72 unconnected items. No errors were suppressed and no rules/exclusions were changed.
- The 134 clearance/text/silkscreen violations match the baseline by type, severity and affected UUIDs. The eight clearance errors are six adjacent-pin pairs on IC1 and two on U4, all with 0.150 mm actual clearance against 0.200 mm required. The warnings comprise 61 text thickness, 61 text height and four silkscreen-over-copper warnings.
- Unconnected items decreased from 86 to 72. Other branches of SW_A/SW_B and global +24V/PGND distribution remain unrouted by scope.
- KiCad connectivity traversal confirms all six capacitor positive/negative terminals reach the intended high-side drain/low-side source, and both high-side sources reach the corresponding low-side drain and L6 input. See connectivity.json.
- All component values and pad net assignments were compared with the live baseline and are unchanged. All unmodified footprints, unrelated tracks and zones are preserved. Schematic hashes are unchanged.
- The existing DMN6070SY pin arrangement was checked against the manufacturer's top-view pinout: https://www.diodes.com/datasheet/download/DMN6070SY.pdf . No MOSFET pin mapping was changed.

Files: before.json and after.json contain the full DRC results; added-tracks.json lists every added segment, width and endpoint; power-detail.pdf/png show the local top copper; backups/live-before.kicad_pcb is the exact saved starting board.

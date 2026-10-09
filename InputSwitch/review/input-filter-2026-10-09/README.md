# RECOM input filter — schematic change, 9 October 2026

Implemented the authorized Murata single-stage input filter in Power.kicad_sch. PCB/project and other schematic sheets are byte-identical to source/ backups.

- Added L1, 4.7 uH, Murata 1239AS-H-4R7M=P2; stock ID193, 10 available, zero reserved.
- C2 changed from 10 uF to nominal 22 uF/25 V; C11 added, same Samsung CL31A226KAHNNNE (3216 metric). Stock ID202, 19 available, zero reserved; two required total.
- Retained C1 100 uF upstream, existing protection and all output capacitors.
- Only U1 VIN moves from +12V to BUCK_VIN_FILTERED. Relay/trigger supply stays upstream on +12V.
- Added InputSwitch.pretty/L_Murata_DFE252012C.kicad_mod: manufacturer's 0.8 x 2.0 mm pads, centres +/-1.0 mm, inner gap 1.2 mm. Nonpolar; body 2.5 x 2.0 mm. Source: Murata DFE252012C drawing.

Netlist comparison: the sole existing pin-net change is U1.1. New connections are L1.1 to +12V, L1.2/C11.1/U1.1 to filtered VIN, C11.2 to GND. ERC before/after has the identical three pre-existing power-source errors (#PWR20009, U1.1, U5.8); no new errors. Render inspected, including horizontal L1 labels. No suppression added.

Engineering limits: based on RECOM's Class A nominal reference network; no Class B stage or EMC certification claimed. Murata maximum DCR 0.24 ohm: at 0.6 A, drop 0.144 V, loss 0.0864 W; at 0.8 A, drop 0.192 V, loss 0.154 W. Thermal rating 1.3 A at 40 C rise and inductance-drop rating 1.5 A are reference-condition ratings, not permission to operate at those currents in every enclosure. Filter is in the 12 V input branch, not the 5 V/2 A output. Ideal nominal 4.7 uH/22 uF resonance is about 15.7 kHz; this calculation alone does not validate damping or converter/filter interaction. Samsung effective capacitance falls under DC bias. Existing source bulk and winding losses are retained; startup ringing/inrush and stability have not been simulated or measured. Do not claim guaranteed startup or acoustic/EMC performance.

PCB handover: update PCB from schematic; place L1 near U1 input and C11 immediately across U1 pins1/2, with short GND return. C2 stays upstream of L1; preserve C1 and relay supply branching. Use the new local footprint. Route/refill and rerun DRC/parity before regenerating manufacturing files. The current PCB intentionally does not yet include this change.

Sources:
- https://recom-power.com/pdf/Innoline/R-78K-2.0.pdf (page6)
- https://www.murata.com/~/media/webrenewal/products/inductor/chip/tokoproducts/wirewoundmetalalloychiptype/m_dfe252012c.ashx
- https://media.digikey.com/pdf/Data%20Sheets/Samsung%20PDFs/CL31A226KAHNNNE_Spec.pdf

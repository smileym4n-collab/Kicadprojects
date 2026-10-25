# Purchase list — stereo Rev 0.1

Read `README.md` and the unresolved verification items before ordering a PCB. Stock was queried read-only on 25 October 2026; no reservations, quantity edits or purchase records were made. `BOM.csv` is the complete 130-part stereo assembly list, with stock IDs, quantities and footprints. All selected stock records report zero reserved quantity. This does not reserve them against later use.

| Quantity | Item | Purpose / choice |
|---:|---|---|
| 2 minimum | Infineon **IRF540NPBF**, TO-220 | N-channel outputs; not in inventory. Buying 4 provides two characterization/spare devices. |
| 2 | Nexperia **BZX79-C4V3**, DO-35, 500 mW | 4.3 V bias-spreader Zeners. Stocked 5.1 V parts are not a direct substitution. |
| 2 | Vishay **BAT46-TR**, 100 V Schottky, DO-35 | VAS anti-saturation clamp; the stocked 40 V 1N5819 is deliberately not used. |
| 2 | KEMET **C315C331J5G5TA**, 330 pF, 50 V, 5%, C0G, radial 2.54 mm | Final dominant-pole compensation; no suitable 330 pF stock found. |
| 2 | TE **LR1F130R**, 130 Ω, 0.6 W, 1% metal film | Bias-range resistors R114/R214; no suitable 130 Ω stock found. |
| 4 | TE **ROX2SJ10R**, 10 Ω, 2 W metal oxide | Two Zobels and two coil damping resistors; suitably flameproof, low-inductance construction. |
| 2 | Phoenix Contact **1715734**, MKDS 1,5/3-5,08 | Per-channel +V/GND/−V input, 5.08 mm pitch. |
| 2 | Phoenix Contact **1715721**, MKDS 1,5/2-5,08 | Per-channel speaker/protection output, 5.08 mm pitch. |
| 2 if owned pots do not fit | Bourns **3296W-1-202LF**, 2 kΩ, 25 turn | Stock ID 529 has 19 generic 2 kΩ pots; exact body and pin arrangement are unverified. |

Inventory supplies two of the twelve IRF9540N (ID 257), BC546/BC556, BD139/BD140, ordinary metal-film resistors, four 0R33/5 W source resistors, capacitors and signal diodes. Existing IRFZ44N are deliberately unused. Two 220 pF input C0G capacitors use **2012 metric** SMD packages; this small exception to through-hole construction uses appropriate stock without awkward parallel combinations.

Also check workshop supplies: approximately 0.8 m total of 1 mm diameter enamelled copper for two air coils; ten small tinned wire test loops; two 2.54 mm shorting shunts; insulated heatsink mounting hardware for the output MOSFETs and bias sensors; thermal compound. Drivers need insulation too if mounted on the same sink. A contact temperature probe is required for thermal qualification; it was not included in the listed test equipment. Coils and wire loops are fabrication items, not inferred stock.

Exact power-resistor dimensions and generic pot fit are layout hold points. The 0R33 inventory part is MCKNP05SJ033KAA9, quantity 6, required 4; do not order its PCB footprint before measuring one. The selected roomy 2 W/5 W resistor footprint also needs a physical check against the supplied ROX body/lead formation.

IRF540NPBF was listed in stock at [Farnell UK](https://uk.farnell.com/infineon/irf540npbf/mosfet-n-ch-100v-33a-to-220ab/dp/8648298) during this design session. Check current price and stock when ordering. Use DigiKey UK, Mouser UK, Farnell or CPC for genuine semiconductors; stock count is not a guarantee of future availability. No purchases have been made.

PSU reservoir capacitors/transformer are outside this amplifier BOM. The calculations assume 4,700 µF per rail; use at least 35 V ratings if subsequently selecting them. The existing local 220 µF capacitors are rated 35 V. Heatsinks are owned, but their thermal resistance has not been established.

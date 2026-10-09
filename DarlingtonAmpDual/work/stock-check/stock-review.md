# Mono amplifier stock review — 6 October 2026

Compared the currently saved schematic with live Electronic Parts Inventory. No inventory or circuit edits made. Counts below are database quantities; suitable rows report zero reserved quantity. Salvage quantities were not supplied.

## Exact electrical stock

| Circuit | Required | Inventory stock | Location / qualification |
|---|---:|---|---|
| Q11 2SD2390 | 1 | 20, recorded D2390 (#447) | Darlington Transistor Drawer; confirm full body marking |
| Q12 2SB1560 | 1 | 22, recorded B1560 (#448) | Darlington Transistor Drawer; confirm full body marking |
| Q8 2SA1837 | 1 | 6 (#587), TO-220 | PNP Driver drawer; inventory incorrectly describes NPN |
| Q10 2SC4793 | 1 | 6 (#586), TO-220 | NPN Driver drawer |
| Q9 BD139 | 1 | 12 ST (#148), SOT-32 | NPN Transistor drawer; verify exact ST pin mapping against present symbol/footprint before fitting |
| R2,R10 22k | 2 | 98 LR1F22K (#276), THT 600mW | Parts drawer 2 |
| R3–R7,R12,R13 100R | 7 | 41 LR1F100R (#150), THT 600mW | Parts drawer 2 |
| R8 330R | 1 | 19 LR1F330R (#290), THT 600mW | Parts drawer 2 |
| R14,R15 2k2 | 2 | 18 LR1F2K2 (#268), THT 600mW | Parts drawer 2 |
| R16 680R | 1 | 99 LR1F680R (#291), THT 600mW | Parts drawer 2 |
| C2 220uF/50V bipolar | 1 | 3 Nichicon UES1H221MHM (#501), radial THT | Parts Drawer 2; footprint still unassigned |

Verify actual resistor dimensions against assigned footprints; electrical inventory match does not establish mechanical fit.

## Owned candidates / physical checks

- R1 dual 0R22 and L505 0.95uH are user-confirmed salvage, not in inventory. One of each suffices. Power rating and coil current/temperature remain bench checks. Current saved L1 still says 0.82uH and has no footprint assigned.
- C5,C7,C9 need three 100nF/100V capacitors. Inventory #403 has 18 Kemet THT film capacitors (7 x 2 mm), Parts Drawer 2. Suitable electrical candidates; exact lead pitch/dielectric not recorded. C7/C9 currently use ceramic-disc footprints, so film substitution requires footprint review.
- C10 needs one 100nF/50V. Inventory #406 has 92 THT film parts rated 63V, Parts Drawer 2; alternatively #157 has 129 Kemet 100nF/50V MLCC in 3216 metric. Neither establishes fit to the currently assigned disc footprint.
- RV1: four generic 5k multiturn pots (#533), stored at Pootentiometers; 2.54 mm pitch noted. Confirm actual geometry, pin mapping and travel before adopting the Bourns 3296W footprint and fail-low wiper connection.
- C6,C8 specify 220uF/63V: no matching stock found. Ten Panasonic EEUFR1H221B 220uF/50V (#576) exist, but are a proposed rating change, not an exact BOM match. Keep 63V for the buy list unless the rail tolerance/transients and physical footprint are reviewed.
- Optional C1: three 2.2uF/63V film parts (#417), Parts drawer 2, dimensions 7.5 x 7 mm; DNP so no purchase required. Check footprint if fitted.
- Other owned emitter alternatives: 21 cement 0R33/5W (#289), plus six wirewound 0R33/5W (#288). Not needed when using the salvaged dual 0R22.

## Buy / no exact matching stock found

| Part | Quantity | Notes |
|---|---:|---|
| 33R THT resistors | 2 | R17,R18; 1% metal film, at least 0.25W |
| 68k THT resistor | 1 | R9; 1%, at least 0.5W; approximately 0.07W at nominal rails |
| 1k15 THT resistor | 1 | R11; 1% metal film |
| 10R non-inductive power resistors | 2 | R21,R22; at least 2W. Stock has eleven 5W wirewound (#284) and two 5W cement (#546), but non-inductive construction is unverified. 600mW metal-film stock is below specified power rating. |
| 100pF C0G/NP0, 100V, THT | 1 | C4. Owned #197 is 100pF/50V in 2012 metric, not the specified voltage/package. |
| 220uF/63V radial electrolytic | 2 | C6,C8; verify package dimensions before order |
| KSC1845 | 5 | Q1,Q2,Q5,Q6,Q7; exact stock absent; salvage option below |
| KSA992 | 2 | Q3,Q4; exact stock absent; salvage option below |
| J2 JST-XH 2-way input header plus mating connection | 1 set | Exact matching stock absent. Owned MC34629 is 2.54 mm, not the fitted JST-XH 2.50 mm footprint. |
| TE 62409-1 spade terminals | 4 | J4–J7; exact stock absent; physical salvage may cover these |

Optional C3 10pF C0G/100V is DNP and need not be bought for initial assembly. Test points are bare PCB pads, not compulsory purchased hardware. Main heatsink, insulators and fasteners require physical stock confirmation; no mechanical/thermal qualification performed.

## Previously mentioned salvaged transistors

- A970 / C2240: potential replacements for KSA992 / KSC1845 respectively, after quantity, exact marking, gain-group, matching, condition and pin/footprint review. Need five NPN and two PNP for the unchanged topology; single example of each type is insufficient. Do not silently substitute.
- A1145 / C2705: useful high-voltage spares; not needed with the stocked 2SA1837/2SC4793.
- A1015 / C1815: retain as general-purpose spares; not blanket replacements in this +/-35V amplifier. C1815 appearing twice in the user's list does not establish a quantity.

This is stock reconciliation, not a new electrical or PCB sign-off. Search returned caps at limits of 100, so targeted searches were used for critical values. Search filters did not consistently normalize capacitor units; free-text checks and category records were cross-checked.

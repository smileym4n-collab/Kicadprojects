> Standard footprint update, 25 October 2026: 20 custom assignments were replaced with standard KiCad footprints; 58 standard and 4 custom assignments remain. See [current footprint choices](../standard-footprints-2026-10-25/README.md). Earlier custom-envelope descriptions below are historical.

> ERC repair, 25 October 2026: the Q5 collector/common-base junction is now restored. Current ERC is 0 errors, 0 warnings; inventory/footprint assignments are preserved. See [repair verification](../erc-fix-2026-10-25/verification.txt). Earlier baseline-error statements below are historical.

# Inventory assignment — one mono Class-A channel, 25 October 2026

**45 schematic components matched to available stock; 62 of 73 non-power-symbol items have footprints.** There are 11 deliberate footprint gaps. The user chose to finish the generic 1k trimmer and unmarked ballast resistors. Other gaps need an exact purchased part/package. The inventory was read only: nothing was reserved, deducted or changed.

See [assignments.csv](assignments.csv) for every reference, MPN, inventory ID, quantity, location, footprint and unresolved item. [inventory-evidence.json](inventory-evidence.json) preserves the connector responses. Existing component values, identities, positions, wiring and pin numbers were retained, except the explicitly documented rating updates below. No PCB layout work was performed.

## Stocked selections

Quantities below are available after existing reservations; required quantity is for **one** mono channel. They are not physical-count verification.

| References | Manufacturer part | Inventory ID | Need / available | Location |
|---|---|---:|---:|---|
| C1 | MKS2C042201K00KSSD | 417 | 1 / 3 | Parts Drawer 2 |
| C2 | CL21C101JBANNNC | 197 | 1 / 100 | SMD Parts |
| C3 | R82DC3100DQ50J | 406 | 1 / 92 | Parts Drawer 2 |
| C7, C9 | C1206C104K5RACTU | 157 | 2 / 139 | SMD Parts |
| C8 | EEUFR1V102 | 338 | 1 / 7 | Parts Drawer 2 |
| C10 | MCGPR50V478M22X41 | 167 | 1 / 8 | Fat Caps Zone |
| D1, D2 | 1N4148 | 138 | 2 / 63 | Parts drawer 2 |
| J1, J2, J3 | MC34629 | 126 | 3 / 40 | Parts drawer 1 |
| Q6, Q8, Q9, Q10 | 2SC4793 | 586 | 4 / 6 | NPN Driver drawer |
| Q7 | 2SA1837 | 587 | 1 / 6 | PNP Driver drawer |
| QOUT1, QOUT2, QSINK1, QSINK2 | 2SC5198 | 141 | 4 / 20 | Audio NPN Transistor drawer |
| R1 | RR1220P-223-D | 511 | 1 / 50 | SMD Parts |
| R3, R4, R6, R7, R8, R11, R22, R23, R26 | RR1220P-101-D | 209 | 9 / 26 | SMD Parts |
| R5 | LR1F270R | 92 | 1 / 42 | Parts drawer 2 |
| R10 | LR1F18K | 275 | 1 / 22 | Parts drawer 2 |
| R12 | LR1F470R | 153 | 1 / 9 | Parts drawer 2 |
| R13, R14, R17, R18 | LR1F10R | 283 | 4 / 60 | Parts drawer 2 |
| R24, R34 | LR1F10K | 272 | 2 / 67 | Parts drawer 2 |
| R25 | RMCF0805FT3K30 | 373 | 1 / 50 | SMD Parts |
| R27, R31 | RR1220P-102-D | 224 | 2 / 42 | SMD Parts |
| R32, R33 | LR1F2K2 | 268 | 2 / 28 | Parts drawer 2 |

## Ratings and construction decisions

- C7 and C9 use the stocked KEMET 100nF X7R part in **3216 metric**. Their rating changes from provisional 63 V to 50 V. C7 sees the nominal 40 V rail (80% of rated voltage); this selection assumes the external supply, including tolerance/ripple, stays below 50 V. C9 sees the approximately 20 V reference.
- C8 uses owned Panasonic FR 1000u/35 V, replacing the provisional 50 V rating on the approximately 20 V reference. Manufacturer body is diameter12.5 x height20 mm, 5mm lead pitch. It is not a substitute for the 40 V supply capacitor C6.
- C10 uses owned Multicomp MCGPR50V478M22X41, 4700u/50 V, diameter22 x height41 mm nominal, 10mm radial **wire** lead pitch. Its positive terminal remains PRE_CAP; negative remains SPK_OUT. The prior snap-in footprint was replaced with a project-local radial footprint. Allow sleeve/case and height tolerances plus mechanical support during subsequent layout; this is a large component.
- C1 uses owned WIMA MKS2 PET film, 2u2/63 V, 7.2 x 7.2 x 13mm with 5mm lead pitch. C3 uses owned KEMET PET film, 100n/63 V, 7.2 x 2.5 x 6.5mm with 5mm pitch. Both retain the original film technology and capacitance.
- Susumu RR1220 thin-film parts are **2012 metric**, 0.1 W. Nine 100R references use 9 of 26 available. Their calculated small-signal dissipation is appropriate; they were not used in the high-power paths.
- TE LR1 metal-film parts are rated 0.6 W, with a selected 10.16mm formed-lead mounting pitch and allowance for a maximum 6.8 x diameter2.5mm body. R24 uses one of these because its estimated 0.15 W dissipation exceeds the available small SMD resistor ratings. R32/R33 each dissipate approximately 0.182 W at 40 V, below the 0.6 W stock rating. R10 is now labelled 0.6 W to match its selected part; its resistance remains 18k.
- The four 10R base stoppers use the stocked 0.6 W metal-film parts. The power damping/Zobel resistors were not replaced with ordinary wirewound inventory whose HF inductance is unspecified.
- J1/J2/J3 use MC34629, **2.54mm**, rated 3 A and 250 V. The nominal supply draw is approximately 2 A plus front-end current; speaker RMS current is approximately 1.37 A at 15 W/8 ohm. Keep connectors away from power-device heat. The mating MC34481 housings are in inventory; verify suitable crimp contacts and wire. This is not a 2.50mm JST-XH footprint or mating arrangement.
- The inventory calls 2SA1837 an “NPN driver”; its Toshiba datasheet confirms **PNP**, consistent with the existing Q7 symbol. No inventory record was edited. Power and driver transistor types were retained.

## Parts still to finish

| References | Status | What remains |
|---|---|---|
| Q1–Q3 | KSA992 not found in inventory | Specified type retained; onsemi KSA992FTA is recorded as an unconfirmed purchase/stock-check target. TO-92 inline footprint added from manufacturer 1E/2C/3B mapping. Confirm owned lead form before assembly. |
| Q4–Q5 | KSC1845 not found in inventory | Specified type retained; onsemi KSC1845FTA is an unconfirmed target. Same TO-92 mapping/lead-form condition. |
| R9 | No exact 82R stock | 2012 metric footprint provision only; select >=0.125 W part. TUNE retained. |
| R30 | No exact 19k stock | 2012 metric footprint provision only; select suitable thin-film feedback part. Gain-setting value unchanged. |
| C5 | Optional 10p C0G not found | 2012 metric footprint only; remains DNP/TUNE. |
| C4 | 470u/50 V bipolar not available | Footprint blank until an exact bipolar part is selected. Owned low-voltage polarized capacitors are not suitable substitutions. |
| C6 | 470u/63 V not available | Footprint blank. The inventory’s 470u/100 V record has zero physical stock; lower-voltage stock is unsuitable for the 40 V rail. |
| R15/R16/R19/R20 | User to assign | Four independent 0R22/5 W ballast resistors. Inventory lists only one unmarked 10% single resistor and unknown three-lead dual parts; neither was claimed as four verified parts. |
| R21 | No 0R27/5 W match | Footprint blank until exact sense resistor is selected. |
| R28/R29 | No verified low-inductance 10R >=3 W match | Footprints blank. Ordinary 5 W wirewound stock was not assumed non-inductive. |
| RV1 | User to assign | Generic inventory525 has three 1k multiturn trimmers, but package/body/wiper mapping is unverified; footprint blank as requested. |
| L1 | No 0.82uH >=4 A match | Footprint blank; unrelated inductors/ferrites were not substituted. |

The nine retained test points use bare plated through-hole test pads and consume no inventory component.

## Footprints and verification

Project-local footprints are in `ClassA_Inventory.pretty`, registered in `fp-lib-table`; native KiCad SVG/PNG previews are in `footprint-previews/`.

- MC34629: manufacturer 2.54mm pitch, 1.0mm holes, pin1 on the right when looking down with the locking wall at -Y. Pads preserve the schematic connector pin/net order.
- Toshiba 2SC5198: 1B/2C/3E, 5.45mm pitch, generous 1.6mm lead holes. Toshiba 2SC4793/2SA1837: 1B/2C/3E, 2.54mm pitch, 1.4mm holes. These local transistor footprints intentionally use **conservative symmetric body envelopes** covering the full maximum thickness on both sides of the lead row. Their pin patterns are verified; their rectangles are clearance envelopes, not exact body offsets or 3D models. Final heatsink/assembly positioning remains a separate layout task.
- TO-92 inline, diode, film/ceramic/reference-capacitor and bare test-pad footprints use installed KiCad libraries. Every assigned footprint resolves, and pad-number sets match the symbol pin-number sets.

**189 assignment/preservation checks passed.** Before/after exported named nets and pin sets are identical; wire/junction/label objects, component UUIDs, placements, transistor library definitions and symbol pin mappings are unchanged. Board, project and preferences SHA-256 hashes match the start of this work. Five custom footprints parse and export with native KiCad; rendered schematic and footprint previews were inspected.

**ERC baseline and final both have 1 error, 0 warnings:** Q4 base input not driven. The live saved schematic has its common Q4/Q5 base net disconnected from the Q5 reference collector. This was preserved and reported rather than silently changing circuitry during a parts-assignment task. It needs correction before treating the amplifier schematic as electrically complete. Previous historical clean ERC reports do not describe this current file. No new ERC errors were introduced.

These checks do not establish PCB, stability, hot SOA, thermal, protection or bench qualification.

## Primary technical sources

- [Toshiba 2SC5198 datasheet](https://toshiba.semicon-storage.com/info/2SC5198_datasheet_en_20131101.pdf?did=20663&prodName=2SC5198), [2SC4793](https://media.digikey.com/pdf/Data%20Sheets/Toshiba%20PDFs/2SC4793_Rev2006.pdf), [2SA1837](https://media.digikey.com/pdf/Data%20Sheets/Toshiba%20PDFs/2SA1837.pdf).
- [onsemi KSC1845](https://www.onsemi.com/download/data-sheet/pdf/ksc1845-d.pdf), [KSA992](https://www.onsemi.com/download/data-sheet/pdf/ksa992-d.pdf), [1N4148 family](https://www.onsemi.com/pdf/datasheet/1n914-d.pdf).
- [Multicomp MC34629 drawing/rating](https://www.farnell.com/datasheets/1751313.pdf), [Multicomp output-capacitor specification](https://uk.farnell.com/multicomp-pro/mcgpr50v478m22x41/cap-4700-f-50v-20/dp/1902903), [MCGPR manufacturer catalogue](https://www.farnell.com/datasheets/1441582.pdf).
- [Panasonic EEUFR1V102 dimensions/rating](https://na.industrial.panasonic.com/products/capacitors/aluminum-electrolytic-capacitors/series/83367/model/83808), [WIMA MKS2 manufacturer table](https://www.wima.de/wp-content/uploads/media/e_WIMA_MKS_2.pdf), [KEMET exact C3 manufacturer specification](https://www.tme.eu/Document/5fd094902f75426a888c075202e383dc/Datasheet-R82DC3100DQ50J.pdf).
- [TE LR manufacturer datasheet](https://docs.rs-online.com/92a4/0900766b81560e47.pdf), [Susumu manufacturer RR series specification](https://www.mouser.com/datasheet/2/392/n_e_all-3104089.pdf), [Samsung exact C2 specification](https://product.samsungsem.com/mlcc/CL21C101JBANNN.do).

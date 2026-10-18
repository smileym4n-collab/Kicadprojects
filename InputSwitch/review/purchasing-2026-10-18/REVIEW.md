# InputSwitch purchasing review — 18 October 2026

Basis: **one complete PCB**, minimum quantities without spares, as confirmed by the user. External power supply, mains relay, front-panel parts and enclosure wiring are excluded from the order. No inventory has been reserved or consumed and no order has been placed.

**Purchasing result: 11 DigiKey order lines, plus two 30R preload resistors requiring a separate supplier.** Stock covers the four G6K relays, MCU, both drivers, both LM358s, both isolated converters, input-filter inductor and most passives. Conditional physical checks remain for a few incompletely described stock items.

## DigiKey order list

Manufacturer identities, order codes and product listings were checked online during this review. The retrieved listings show stock, but some pages are cached and some UK pages did not load; equivalent DigiKey regional listings were used where necessary. This is not a reserved-stock or price quotation. Use cut tape rather than full reels for the listed SMD quantities.

| References | Qty | Manufacturer part number | DigiKey order code | Specification |
|---|---:|---|---|---|
| U1 | 1 | R-78K5.0-2.0 | [945-R-78K5.0-2.0-ND](https://www.digikey.co.uk/en/products/detail/recom-power/R-78K5-0-2-0/18093049) | RECOM 5 V / 2 A SIP3 |
| U6, U8 | 2 | VO617A-3 | [VO617A-3-ND](https://www.digikey.co.uk/en/products/detail/vishay-semiconductor-opto-division/VO617A-3/2811965) | Vishay DIP-4, CTR group 3 |
| U9 | 1 | SN74LVC1G04DBVR | [296-11599-1-ND](https://www.digikey.co.uk/en/products/detail/texas-instruments/SN74LVC1G04DBVR/385716) | TI SOT-23-5; cut tape |
| D1 | 1 | SS14-E3/61T | [SS14-E3/61TGICT-ND](https://www.digikey.co.uk/en/products/detail/vishay-general-semiconductor-diodes-division/SS14-E3-61T/1091538) | Vishay 1 A / 40 V SMA; cut tape |
| D2 | 1 | SMBJ13A | [SMBJ13ALFCT-ND](https://www.digikey.co.uk/en/products/detail/littelfuse-inc/SMBJ13A/285974) | Littelfuse unidirectional 13 V TVS, SMB; cut tape |
| C1 | 1 | 35ZLJ100M6.3X11 | [1189-2268-ND](https://www.digikey.co.uk/en/products/detail/rubycon/35ZLJ100M6-3X11/3563164) | Rubycon ZLJ 100 uF / 35 V, 6.3 mm diameter, 2.5 mm pitch |
| C23, C25, C43, C45 | 4 | EEU-FR1V330 | [P14434-ND](https://www.digikey.co.uk/en/products/detail/panasonic-electronic-components/EEU-FR1V330/2433568) | Panasonic FR 33 uF / 35 V, 5 mm diameter; form 2 mm leads to 2.5 mm PCB pitch |
| R13, R49 | 2 | RC0805FR-072M2L | [311-2.20MCRCT-ND](https://www.digikey.co.uk/en/products/detail/yageo/RC0805FR-072M2L/727677) | Yageo 2M2, 1%, 0.125 W, 2012 metric; cut tape |
| R23, R43 | 2 | RT0805FRE07470KL | [13-RT0805FRE07470KLCT-ND](https://www.digikey.co.uk/en/products/detail/yageo/RT0805FRE07470KL/1079269) | Yageo 470k, 1%, thin-film, 0.125 W, 2012 metric; cut tape |
| F2 holder | 1 | 0031.8201 | [486-1258-ND](https://www.digikey.co.uk/en/products/detail/schurter-inc/0031-8201/669925) | Schurter OGN 5 x 20 mm holder, 22.5 mm pin pitch |
| F2 fuse | 1 | 0218001.MXP | [F1745-ND](https://www.digikey.co.uk/en/products/detail/littelfuse-inc/0218001-MXP/777598) | Littelfuse T1A, slow blow, 5 x 20 mm |

C1 deliberately retains the earlier 35 V requirement. The stocked 100 uF capacitors are 16 V or 25 V, so they are not counted toward that requirement. The chosen Rubycon is the required 6.3 mm body / 2.5 mm pitch; several apparently similar Panasonic 100 uF / 35 V parts have larger bodies or different pitch.

The 33 uF Panasonic parts are rated 35 V rather than the earlier minimum 16 V, fit the 5 mm body provision, and have 2 mm straight-lead spacing. Form the leads gently to the board's 2.5 mm pitch before insertion, avoiding force on the seals. Their specified maximum seated height is 12.5 mm; allow enclosure clearance.

## Separate supplier: do not omit these

| References | Qty | Exact manufacturer part number | Requirement / source |
|---|---:|---|---|
| R20, R40 | 2 | **PR03000203009FAC00** | Vishay PR03, 30R, 3 W, 1%, copper leads, axial. [Mouser listing](https://www.mouser.co.uk/ProductDetail/Vishay-BC-Components/PR03000203009FAC00). |

I could not verify a DigiKey listing/order code for this exact 1% part. Do not use a guessed DigiKey code. The JAC00 variant is 5%, not the specified 1%. Manufacturer ordering data confirms wire code 2 is copper and F is 1%. [Vishay datasheet](https://www.vishay.com/docs/28729/pr010203.pdf).

The PR03 axial leads must be formed to 25.4 mm PCB pitch. Its coated body may extend to 19.5 mm length although the nominal DIN footprint identifier says 17 mm. The earlier accepted design uses this series; check body/end clearance during assembly. Raise the resistors above the board, clear of capacitors and wiring: nominal dissipation is 5²/30 = **0.83 W each**, rising to 1.2 W at 6 V. Enclosure temperature still requires measurement.

## Use from inventory

Available quantities below are physical quantity minus reserved quantity; the selected records reported zero reserved. These records are not a physical recount. Package and value matching was performed explicitly; similarly named parts in other packages were not counted.

| References | Need | Inventory ID | Available | Selected stock / location |
|---|---:|---:|---:|---|
| K1–K4 | 4 | 420 | 5 | Omron G6K-2PY DC5, through-hole; location unrecorded |
| U2 | 1 | 80 | 6 | ATtiny412 SOIC-8; SMD Parts |
| U3, U4 | 2 | 121 | 8 | ST ULN2003A SOIC-16; SMD Parts. Do not use DIP-16 stock ID120 |
| U5, U7 | 2 | 389 | 2 | TI LM358 DIP-8; Opamp drawer. Uses all recorded stock |
| U5/U7 sockets | 2 | 178 | 21 | Turned-pin DIP-8 sockets; DIP sockets drawer |
| U10, U11 | 2 | 416 | 3 | Mean Well SPU03L-05 SIP7; Voltage regulator drawer |
| Q2, Q3 | 2 | 452 | 117 | onsemi BC549 TO-92; verify C-B-E lead order/orientation |
| D21, D22, D41, D42 | 4 | 138 | 63 | Through-hole 1N4148; Parts drawer 2. SMD 1N4148W stock is not used |
| L1 | 1 | 193 | 6 | Murata 1239AS-H-4R7M=P2, 2520 metric; SMD Parts |
| C2, C11 | 2 | 202 | 19 | Samsung CL31A226KAHNNNE, 22 uF / 25 V, 3216 metric; SMD Parts |
| C4, C5, C7, C9, C22, C42 | 6 | 157 | 129 | Kemet C1206C104K5RACTU, 100 nF / 50 V, 3216 metric; SMD Parts |
| C6 | 1 | 181 | 50 | Samsung CL31B105KBHNFNE, 1 uF / 50 V, 3216 metric; SMD Parts |
| C8 | 1 | 188 | 9 | Samsung 2.2 uF / 25 V, 2012 metric; exact MPN not recorded |
| C10, C20, C40 | 3 | 135 | 50 | Taiyo Yuden TMK316B7106KL-TD, 10 uF / 25 V, X7R, 3216 metric; SMD Parts |
| C3, C21, C41 | 3 | 95 | 50 | Panasonic EEUFR1E470H, 47 uF / 25 V; Parts drawer 2 |
| C24, C44 | 2 | 406 | 92 | Kemet 100 nF / 63 V film, noted 7 x 2 mm; Parts Drawer 2; confirm 5 mm lead pitch |
| R1, R26, R33, R34, R46, R53, R54 | 7 | 224 | 42 | 1k thin-film, 0.5%, 2012 metric; SMD Parts |
| R2, R3, R4, R5, R10 | 5 | 504 | 100 | RMCF0805FT47K0, 47k, 1%, 0.125 W, 2012 metric; SMD Parts |
| R6, R9, R11, R12, R24, R25, R28, R31, R44, R45, R48, R51 | 12 | 242 | 70 | 100k thin-film, 0.5%, 2012 metric; SMD Parts |
| R7, R8, R30, R50 | 4 | 493 | 100 | RMCF0805FT4K70, 4k7, 1%, 0.125 W, 2012 metric; SMD Parts |
| R21, R41 | 2 | 209 | 26 | 100R thin-film, 2012 metric; power/tolerance/MPN not recorded: check reel |
| R22, R42 | 2 | 373 | 50 | RMCF0805FT3K30, 3k3, 1%, 0.125 W, 2012 metric; SMD Parts |
| R27, R47 | 2 | 232 | 46 | 10k thin-film, 0.5%, 2012 metric; SMD Parts |
| R32, R52 | 2 | 561 | 100 | RMCF0805FT390R, 390R, 1%, 2012 metric; SMD Parts |
| J1–J7, J10–J13 | 11 | 126 | 40 | MC34629 two-way Multicomp headers; Parts drawer 1; fit accepted in prior review |
| J8, J9 | 2 | 127 | 40 | MC34631 three-way Multicomp headers; Parts drawer 1; fit accepted in prior review |
| Two-way mating housings | 11 | 128 | 40 | MC34481; Parts drawer 1 |
| Three-way mating housings | 2 | 129 | 40 | MC34483; Parts drawer 1 |

C10/C20/C40 are on the +5 V rail in the fresh netlist; the stocked 25 V X7R parts have ample voltage margin. The old report suggested 50 V, but the saved schematic specifies only 10uF and the circuit does not need 50 V here. Stock ID505 is a 50 V alternative but uses a different dielectric code; it has not been silently substituted.

C2/C11 use the existing specified X5R 25 V part. Do not substitute the 10 V 22 uF stock on this 12 V input. Effective ceramic capacitance under DC bias remains below nominal and converter startup/filter behaviour remains a bench check.

For R21/R41, confirm at least 0.125 W and the intended tolerance from the stock label. If identification fails, two [Yageo RC0805FR-07100RL, DigiKey 311-100CRCT-ND](https://www.digikey.co.uk/en/products/detail/yageo/RC0805FR-07100RL/727543) provide a documented 100R / 1% / 0.125 W replacement. This conditional purchase is excluded from the main list.

For the film capacitors, the inventory does not identify a full MPN or dielectric. Confirm the two physical pieces have 5 mm pitch and the intended film construction before counting them as assembly-ready. No replacement has been selected without that check.

The Multicomp header fit was explicitly accepted in the 18 October fabrication follow-up. They remain 2.54 mm parts against JST-XH 2.50 mm footprint identifiers. Use the Multicomp mating family throughout; do not mix JST housings with Multicomp headers. **28 crimp contacts** are needed for one mating harness per connector; no matching loose-contact stock record was found. Confirm whether the housings already contain contacts or whether completed harnesses exist before purchasing contacts.

## Project checks and limits

- Fresh XML netlist exported from the current saved hierarchy; 107 schematic components including four mounting holes. All pin-to-net assignments match the 17 October reviewed netlist: zero changes.
- Fresh ERC: **3 errors**, all power-input-not-driven declarations: control GND (#PWR20009), U1 VIN and U5 V+. These remain documented and accepted in the previous review; ERC is not clean.
- Fresh DRC with zone refill and schematic parity: **0 unconnected items, 0 parity discrepancies, 0 non-excluded violations**. Eight excluded warnings remain: U1 library footprint mismatch, two text thickness, one silk overlap and four silk-over-copper. The library mismatch reflects the board's deliberate 1.3 mm U1 holes.
- Saved-board inspection confirms all four G6Ks use the corrected local footprint and U1 has 1.3 mm drills. The U1 value is R-78K5.0-2.0 despite its older R78B footprint/symbol identifiers; order the current value above, not the obsolete parts-list recommendation.
- F2 is the Schurter 0031.8201 holder in the saved schematic/board, with pads 22.5 mm apart and the central mechanical hole present. Do not order the Bulgin holder from the older report. F2's abbreviated 1A value is interpreted as the established **T1A** requirement.
- No schematic, PCB, library or project settings were edited. Hash comparison after review verifies source preservation. Existing scripts that hard-code old netlists were not used as proof of the present design.
- This is a procurement and current-CAD consistency review, building on the existing electrical/layout reviews. No simulation, firmware verification, bench, thermal or EMC qualification was performed. DRC uses the project's existing enabled/disabled rules and exclusions.

## External build items: outside the PCB list

The following still need physical-stock and mechanical decisions before a complete enclosure shopping list is possible:

- Regulated isolated 12 V adapter and matching DC inlet/cable.
- External Omron G7L-2A-T DC12 relay, mounting/wiring and suitable insulated terminations; no G7L inventory record was found.
- SPDT ON-ON front switch, two front-panel indicators, six RCA sockets if not already installed, shielded audio harnesses.
- Matching Multicomp crimp contacts or existing terminated leads, four M4 standoffs/fasteners, enclosure and wiring lengths.

The new inventory LED hits are SMD devices; they are not assumed to be suitable front-panel indicators. Other stocked mains/power relay models have not been treated as replacements for the specified G7L.

## Evidence and manufacturer references

- Local evidence: netlist.xml, erc.json, drc.json, source-hashes.json, inventory-snapshot.json and digikey-order-list.json in this directory.
- [RECOM R-78K-2.0](https://recom-power.com/pdf/Innoline/R-78K-2.0.pdf)
- [TI SN74LVC1G04](https://www.ti.com/lit/ds/symlink/sn74lvc1g04.pdf)
- [Vishay VO617A](https://www.vishay.com/docs/83430/vo617a.pdf)
- [Vishay SS14](https://www.vishay.com/docs/88746/ss12.pdf)
- [Littelfuse SMBJ](https://m.littelfuse.com/~/media/electronics/datasheets/tvs_diodes/littelfuse_tvs_diode_smbj_datasheet.pdf.pdf)
- [Schurter OGN](https://us.schurter.com/en/datasheet/typ_OGN.pdf)
- [Panasonic FR](https://industrial.panasonic.com/cdbs/www-data/pdf/RDF0000/ABA0000C1259.pdf)
- [Rubycon ZLJ](https://www.rubycon.co.jp/wp-content/uploads/catalog-aluminum/ZLJ.pdf) (manufacturer PDF fetch was blocked; exact product dimensions/rating independently checked against DigiKey's listing).
- [Yageo RC](https://yageogroup.com/content/datasheet/asset/file/PYU-RC_GROUP_51_ROHS_L)
- [Yageo RT](https://yageogroup.com/content/datasheet/asset/file/PYU-RT_1-TO-0-01_ROHS_L)


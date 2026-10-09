# InputSwitch parts needed

Inventory was checked live during this review. No stock was reserved or consumed and no orders were placed. Quantities listed as available are inventory records, not physical inspection. Match package and suffix exactly before assembly.

## Main purchases not found in inventory

| Qty | Part | Purpose / package |
|---:|---|---|
| 2 | Vishay **VO617A-3** | Detector optocouplers; standard DIP-4, 7.62 mm row spacing. |
| 1 | RECOM **R-78B5.0-2.0** | 12 V to 5 V buck module, SIP3, 2 A. Larger body than original 500 mA module; correct footprint assigned. |
| 1 | TI **SN74LVC1G04DBVR** | Source-LED inverter, DBV / SOT-23-5. |
| 2 | Vishay **PR03, 30R, 3W, 1%, copper leads** | Flameproof preload resistors; DIN0617, 25.4 mm formed pitch. Confirm exact suffix; 3 W rating requires copper-lead version. |
| 1 | Vishay **SS14** | Reverse-polarity blocking diode, SMA. No inventory hit in the initial search. |
| 1 | Littelfuse **SMBJ13A** | Unidirectional input TVS, SMB. |
| 1 | Omron **G7L-2A-T DC12** | External mains relay; no inventory record found. Omit purchase if already physically owned. |

**No isolated converters or 5.1 V reference zeners need to be bought.** Use two owned SPU03L-05 modules; one remains spare. Inventory ID416 is labelled “SPI03L-05”; the user identified the physical units as SPU03L-05. The inventory record was not edited.

Supplier references: [VO617A-3 at DigiKey UK](https://www.digikey.co.uk/en/products/detail/vishay-semiconductor-opto-division/VO617A-3/2811965), [R-78B5.0-2.0 at DigiKey](https://www.digikey.com/en/products/detail/recom-power/R-78B5-0-2-0/6677084), [R-78B manufacturer](https://recom-power.com/en/rec-p-R-78B5.0-2.0.html), [PR03 manufacturer specification](https://www.vishay.com/docs/28729/pr010203.pdf). Confirm current UK stock, exact suffix and price before ordering. No suitable 30R power resistor was found in the inventory search; 330R and 0R33 records are not substitutes.

## Reuse from recorded stock

| Need | Inventory record | Recorded stock | Package / location |
|---:|---|---:|---|
| 3 | G6K-2P-Y, 5 V, ID 420 | 4, none reserved | Through-hole; location not recorded |
| 1 | ATtiny412, ID 80 | 6, none reserved | SOIC-8; SMD Parts |
| 2 | ULN2003A, ID 121 | 7, none reserved | ST SOIC-16; SMD Parts |
| 2 | SPU03L-05 (recorded SPI03L-05), ID 416 | 3, none reserved | SIP7; Voltage regulator drawer |
| 2 | LM358, ID 389 | 2, none reserved | TI DIP-8; Opamp drawer |
| 2 | BC549, ID 452 | 117, none reserved | TO-92; manufacturer/location not recorded |
| 4 | 1N4148, ID 138 | 63, none reserved | Through-hole; Parts drawer 2 |

The five DIP-16 ULN2003As (ID 120, Mixed ICs drawer) are not the package assigned in this schematic. Use the SOIC-16 stock above unless a package change is approved. Check the physical G6K markings really say DC5 and the BC549 lead order is C-B-E before assembly. The two LM358s use the entire recorded unreserved quantity. Five unreserved MCP6002 DIP-8 devices were also found (ID13, Opamps drawer); no op-amp substitution is necessary. See [suitability review](SPU03-LM358-REVIEW.md).

## Other build items

- Six two-pin JST XH headers for audio and two more for DC input/G7L coil; two three-pin JST XH headers for UPDI and toggle, with matching housings/crimps.
- SPDT ON-ON front toggle, two suitable indicator LEDs, six isolated RCA sockets or existing system harnesses, shielded audio wiring.
- Regulated isolated 12 V wall adapter, preferably ±2%, at least 1 A; suitable DC inlet/cable.
- T1A 5 x 20 mm fuse and holder. **Holder provision needs mechanical confirmation:** the assigned FX0457 library footprint and Bulgin's conflicting online orientation descriptions need comparison with the actual part/drawing before purchase/layout.
- Three test-point pins/pads and existing mounting hardware.
- Passives listed below; check drawer stock by exact value/rating before buying. SMD resistors and ceramics are **2012 metric**. The two 30R preload resistors are through-hole, 3 W, 1%; mount with ventilation and clearance from capacitors. They dissipate approximately 0.83 W each at nominal voltage. Use 1% resistors; thin-film in detector gain/threshold networks is sensible. No precision parts are needed in utility pull-downs or LED feeds.
- Main input capacitor C1: 100 µF / 35 V, 6.3 mm body, 2.5 mm lead spacing provision. Other radial electrolytics currently use 5 mm body / 2.5 mm pitch provisions. Confirm exact bought capacitor dimensions. C24/C44 are detector-branch film capacitors; their 5 mm pitch / body provision also needs an exact-part fit check.

The following grouped BOM is generated from the final exported netlist, so quantities and references correspond to the schematic. It is an assembly planning BOM, not an order-ready manufacturer-part-number BOM.

| Qty | Value / part | References | Package / provision |
|---:|---|---|---|
| 1 | +12V | TP1 | TestPoint_THTPad_D2.0mm_Drill1.0mm |
| 1 | +5V | TP2 | TestPoint_THTPad_D2.0mm_Drill1.0mm |
| 2 | 100R | R21, R41 | 2012 metric |
| 8 | 100k | R24, R25, R28, R31, R44, R45, R48, R51 | 2012 metric |
| 6 | 100n / 50V | C22, C4, C42, C5, C7, C9 | 2012 metric |
| 2 | 100n FILM / 50V | C24, C44 | C_Rect_L7.0mm_W2.0mm_P5.00mm |
| 1 | 100u / 35V | C1 | CP_Radial_D6.3mm_P2.50mm |
| 2 | 10k | R27, R47 | 2012 metric |
| 3 | 10u / 50V X7R | C2, C20, C40 | 2012 metric |
| 1 | 12V DC INPUT | J7 | JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical |
| 4 | 1N4148 | D21, D22, D41, D42 | D_DO-35_SOD27_P7.62mm_Horizontal |
| 7 | 1k | R1, R26, R33, R34, R46, R53, R54 | 2012 metric |
| 1 | 1u / 25V | C6 | 2012 metric |
| 2 | 2M2 | R29, R49 | 2012 metric |
| 1 | 2u2 / 25V | C8 | 2012 metric |
| 2 | 30R / 3W / 1% | R20, R40 | R_Axial_DIN0617_L17.0mm_D6.0mm_P25.40mm_Horizontal |
| 4 | 33u / 16V | C23, C25, C43, C45 | CP_Radial_D5.0mm_P2.50mm |
| 2 | 390R | R32, R52 | 2012 metric |
| 2 | 3k3 | R22, R42 | 2012 metric |
| 2 | 470k | R23, R43 | 2012 metric |
| 5 | 47k | R10, R2, R3, R4, R5 | 2012 metric |
| 1 | 47u / 16V | C3 | CP_Radial_D5.0mm_P2.50mm |
| 2 | 47u / 25V | C21, C41 | CP_Radial_D5.0mm_P2.50mm |
| 4 | 4k7 | R30, R50, R7, R8 | 2012 metric |
| 1 | ATtiny412-SS | U2 | SOIC-8_3.9x4.9mm_P1.27mm |
| 1 | AV | D3 | LED_D3.0mm |
| 1 | AV L | J2 | JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical |
| 1 | AV R | J4 | JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical |
| 2 | BC549 | Q2, Q3 | TO-92_Inline |
| 3 | G6K-2P-Y DC5 | K1, K2, K3 | Relay_DPDT_Omron_G6K-2P-Y |
| 1 | G7L COIL ONLY | J10 | JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical |
| 1 | GND | TP3 | TestPoint_THTPad_D2.0mm_Drill1.0mm |
| 2 | LM358N | U5, U7 | DIP-8_W7.62mm |
| 4 | M4 | H1, H2, H3, H4 | MountingHole_4.3mm_M4 |
| 1 | P3A L | J5 | JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical |
| 1 | P3A R | J6 | JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical |
| 1 | R-78B5.0-2.0 | U1 | R78B_2A_SIP3 |
| 1 | REFERENCE | D4 | LED_D3.0mm |
| 1 | REFERENCE L | J1 | JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical |
| 1 | REFERENCE R | J3 | JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical |
| 1 | SMBJ13A | D2 | D_SMB |
| 1 | SN74LVC1G04DBV | U9 | SOT-23-5 |
| 1 | SPDT: REF / COM / AV | J9 | JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical |
| 2 | SPU03L-05 | U10, U11 | SPU03L_05_SIP7 |
| 1 | SS14 | D1 | D_SMA |
| 1 | T1A | F1 | Fuseholder_Cylinder-5x20mm_Bulgin_FX0457_Horizontal_Closed |
| 1 | ULN2003A (12V COIL) | U4 | SOIC-16_3.9x9.9mm_P1.27mm |
| 1 | ULN2003A (5V COILS) | U3 | SOIC-16_3.9x9.9mm_P1.27mm |
| 1 | UPDI / +5V / GND | J8 | JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical |
| 2 | VO617A-3 | U6, U8 | DIP-4_W7.62mm |

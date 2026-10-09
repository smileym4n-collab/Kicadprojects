# InputSwitch parts needed

Inventory was checked live during this review. No stock was reserved or consumed and no orders were placed. Quantities listed as available are inventory records, not physical inspection. Match package and suffix exactly before assembly.

## Main purchases not found in inventory

| Qty | Part | Purpose / package |
|---:|---|---|
| 2 | RECOM **R12P12S/P** | Independent 12 V to isolated 12 V supplies; standard SIP7 pinout, populated pins 1/2/5/7. Do not buy /X2 for this footprint. |
| 2 | Vishay **VO617A-3** | Detector optocouplers; standard DIP-4, 7.62 mm row spacing. |
| 1 | RECOM **R-78E5.0-0.5** | 12 V to 5 V buck module, SIP3, 500 mA. |
| 1 | TI **SN74LVC1G04DBVR** | Source-LED inverter, DBV / SOT-23-5. |
| 2 | Vishay **BZX55C5V1** | 5.1 V detector references, DO-35. |
| 1 | Vishay **SS14** | Reverse-polarity blocking diode, SMA. No inventory hit in the initial search. |
| 1 | Littelfuse **SMBJ13A** | Unidirectional input TVS, SMB. |
| 1 | Omron **G7L-2A-T DC12** | External mains relay; no inventory record found. Omit purchase if already physically owned. |

The isolated modules are the principal extra parts required by the two-channel isolation decision. The inventory's three “SPI03L-05” modules were **not substituted**: their model text and linked SPU03 datasheet are inconsistent and their suitability was not established.

Supplier listings: [R12P12S/P at Mouser](https://www.mouser.com/en/ProductDetail/RECOM-Power/R12P12S-P?qs=%252BHKxvJ84kqpWc%2FKh9uyiWw%3D%3D), [VO617A-3 at DigiKey UK](https://www.digikey.co.uk/en/products/detail/vishay-semiconductor-opto-division/VO617A-3/2811965), [R-78E5.0-0.5 manufacturer page](https://recom-power.com/en/products/switching-regulators/switching-regulators-sip/rec-p-R-78E5.0-0.5.html). These establish catalogue presence, not guaranteed current UK stock, price or lead time. Confirm availability before ordering; /P and /P/X2 are not interchangeable.

## Reuse from recorded stock

| Need | Inventory record | Recorded stock | Package / location |
|---:|---|---:|---|
| 3 | G6K-2P-Y, 5 V, ID 420 | 4, none reserved | Through-hole; location not recorded |
| 1 | ATtiny412, ID 80 | 6, none reserved | SOIC-8; SMD Parts |
| 2 | ULN2003A, ID 121 | 7, none reserved | ST SOIC-16; SMD Parts |
| 2 | LM358, ID 389 | 2, none reserved | TI DIP-8; Opamp drawer |
| 2 | BC549, ID 452 | 117, none reserved | TO-92; manufacturer/location not recorded |
| 4 | 1N4148, ID 138 | 63, none reserved | Through-hole; Parts drawer 2 |

The five DIP-16 ULN2003As (ID 120, Mixed ICs drawer) are not the package assigned in this schematic. Use the SOIC-16 stock above unless a package change is approved. Check the physical G6K markings really say DC5 and the BC549 lead order is C-B-E before assembly. The two LM358s use the entire recorded unreserved quantity.

## Other build items

- Six two-pin JST XH headers for audio and two more for DC input/G7L coil; two three-pin JST XH headers for UPDI and toggle, with matching housings/crimps.
- SPDT ON-ON front toggle, two suitable indicator LEDs, six isolated RCA sockets or existing system harnesses, shielded audio wiring.
- Regulated isolated 12 V wall adapter, preferably ±2%, at least 0.5 A; suitable DC inlet/cable.
- T500mA 5 x 20 mm fuse and holder. **Holder provision needs mechanical confirmation:** the assigned FX0457 library footprint and Bulgin's conflicting online orientation descriptions need comparison with the actual part/drawing before purchase/layout.
- Three test-point pins/pads and existing mounting hardware.
- Passives listed below; check drawer stock by exact value/rating before buying. SMD resistors and ceramics are **2012 metric**. The two 1k2 preload resistors are through-hole, at least 0.5 W. Use 1% resistors; thin-film in detector gain/threshold networks is sensible. No precision parts are needed in utility pull-downs or LED feeds.
- Main input capacitor C1: 100 µF / 35 V, 6.3 mm body, 2.5 mm lead spacing provision. Other radial electrolytics currently use 5 mm body / 2.5 mm pitch provisions. Confirm exact bought capacitor dimensions. C24/C44 are detector-branch film capacitors; their 5 mm pitch / body provision also needs an exact-part fit check.

The following grouped BOM is generated from the final exported netlist, so quantities and references correspond to the schematic. It is an assembly planning BOM, not an order-ready manufacturer-part-number BOM.

| Qty | Value / part | References | Package / provision |
|---:|---|---|---|
| 1 | +12V | TP1 | TestPoint_THTPad_D2.0mm_Drill1.0mm |
| 1 | +5V | TP2 | TestPoint_THTPad_D2.0mm_Drill1.0mm |
| 2 | 100R | R21, R41 | 2012 metric |
| 8 | 100k | R23, R25, R28, R31, R43, R45, R48, R51 | 2012 metric |
| 6 | 100n / 50V | C4, C5, C7, C9, C22, C42 | 2012 metric |
| 2 | 100n FILM / 50V | C24, C44 | C_Rect_L7.0mm_W2.0mm_P5.00mm |
| 1 | 100u / 35V | C1 | CP_Radial_D6.3mm_P2.50mm |
| 4 | 10k | R27, R30, R47, R50 | 2012 metric |
| 3 | 10u / 50V X7R | C2, C20, C40 | 2012 metric |
| 1 | 12V DC INPUT | J7 | JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical |
| 2 | 1M | R29, R49 | 2012 metric |
| 4 | 1N4148 | D21, D22, D41, D42 | D_DO-35_SOD27_P7.62mm_Horizontal |
| 5 | 1k | R1, R26, R33, R46, R53 | 2012 metric |
| 2 | 1k2 | R22, R42 | 2012 metric |
| 2 | 1k2 / 0.5W | R20, R40 | R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal |
| 2 | 1k8 | R32, R52 | 2012 metric |
| 1 | 1u / 25V | C6 | 2012 metric |
| 1 | 2u2 / 25V | C8 | 2012 metric |
| 4 | 33u / 16V | C23, C25, C43, C45 | CP_Radial_D5.0mm_P2.50mm |
| 2 | 470k | R24, R44 | 2012 metric |
| 5 | 47k | R2, R3, R4, R5, R10 | 2012 metric |
| 1 | 47u / 16V | C3 | CP_Radial_D5.0mm_P2.50mm |
| 2 | 47u / 25V | C21, C41 | CP_Radial_D5.0mm_P2.50mm |
| 2 | 4k7 | R7, R8 | 2012 metric |
| 1 | ATtiny412-SS | U2 | SOIC-8_3.9x4.9mm_P1.27mm |
| 1 | AV | D3 | LED_D3.0mm |
| 1 | AV L | J2 | JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical |
| 1 | AV R | J4 | JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical |
| 2 | BC549 | Q2, Q3 | TO-92_Inline |
| 2 | BZX55C5V1 | D20, D40 | D_DO-35_SOD27_P7.62mm_Horizontal |
| 3 | G6K-2P-Y DC5 | K1, K2, K3 | Relay_DPDT_Omron_G6K-2P-Y |
| 1 | G7L COIL ONLY | J10 | JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical |
| 1 | GND | TP3 | TestPoint_THTPad_D2.0mm_Drill1.0mm |
| 2 | LM358N | U5, U7 | DIP-8_W7.62mm |
| 4 | M4 | H1, H2, H3, H4 | MountingHole_4.3mm_M4 |
| 1 | P3A L | J5 | JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical |
| 1 | P3A R | J6 | JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical |
| 1 | R-78E5.0-0.5 | U1 | Converter_DCDC_RECOM_R-78E-0.5_THT |
| 2 | R12P12S/P | U10, U11 | R12P12S_P_SIP7 |
| 1 | REFERENCE | D4 | LED_D3.0mm |
| 1 | REFERENCE L | J1 | JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical |
| 1 | REFERENCE R | J3 | JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical |
| 1 | SMBJ13A | D2 | D_SMB |
| 1 | SN74LVC1G04DBV | U9 | SOT-23-5 |
| 1 | SPDT: REF / COM / AV | J9 | JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical |
| 1 | SS14 | D1 | D_SMA |
| 1 | T500mA | F1 | Fuseholder_Cylinder-5x20mm_Bulgin_FX0457_Horizontal_Closed |
| 1 | ULN2003A (12V COIL) | U4 | SOIC-16_3.9x9.9mm_P1.27mm |
| 1 | ULN2003A (5V COILS) | U3 | SOIC-16_3.9x9.9mm_P1.27mm |
| 1 | UPDI / +5V / GND | J8 | JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical |
| 2 | VO617A-3 | U6, U8 | DIP-4_W7.62mm |

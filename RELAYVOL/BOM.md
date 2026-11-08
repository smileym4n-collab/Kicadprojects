# RELAYVOL bill of materials

Quantities are for one stereo board. The default build leaves K8 and its driver unpopulated. Close JP1 and JP2 for that build.

| References | Qty | Build | Value | MPN or specification | KiCad footprint |
|---|---:|---|---|---|---|
| C1 | 1 | Fit | 220u / 35V | 35ZLH220MEFC8X11.5 · Rubycon ZLH radial electrolytic | `Capacitor_THT:CP_Radial_D8.0mm_P3.50mm` |
| C2, C3, C4, C6 | 4 | Fit | 100n | MC0603B104K500CT · X7R, 50 V, 1608 metric | `Capacitor_SMD:C_0603_1608Metric` |
| C5 | 1 | Fit | 4u7 / 25V | CL21A475KAQNNNE · X5R, 25 V, 2012 metric | `Capacitor_SMD:C_0805_2012Metric` |
| D1, D2, D3, D4, D5, D6, D7 | 7 | Fit | 1N4148W | 1N4148W · Fast switching diode, SOD-123 | `Diode_SMD:D_SOD-123` |
| D8 | 1 | Optional | 1N4148W | 1N4148W · Fast switching diode, SOD-123 | `Diode_SMD:D_SOD-123` |
| J1 | 1 | Fit | 5 V DC | B2B-XH-A(LF)(SN) · Through-hole header | `Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical` |
| J2 | 1 | Fit | VOLUME | Through-hole header | `Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical` |
| J3 | 1 | Fit | UPDI | Through-hole header | `Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical` |
| J4 | 1 | Fit | LEFT IN | Through-hole header | `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical` |
| J5 | 1 | Fit | RIGHT IN | Through-hole header | `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical` |
| J6 | 1 | Fit | LEFT OUT | Through-hole header | `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical` |
| J7 | 1 | Fit | RIGHT OUT | Through-hole header | `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical` |
| K1, K2, K3, K4, K5, K6, K7 | 7 | Fit | G6K-2P DC5 | G6K-2P DC5 · Omron DPDT non-latching, through-hole | `Relay_THT:Relay_DPDT_Omron_G6K-2P` |
| K8 | 1 | Optional | G6K-2P DC5 | G6K-2P DC5 · Omron DPDT non-latching, through-hole | `Relay_THT:Relay_DPDT_Omron_G6K-2P` |
| Q1, Q2, Q3, Q4, Q5, Q6, Q7 | 7 | Fit | 2N7002K | 2N7002K · G/S/D = 1/2/3, SOT-23 | `Package_TO_SOT_SMD:SOT-23` |
| Q8 | 1 | Optional | 2N7002K | 2N7002K · G/S/D = 1/2/3, SOT-23 | `Package_TO_SOT_SMD:SOT-23` |
| R1, R15 | 2 | Fit | 562R | ERA-6AEB5620V · 0.1% thin-film, 2012 metric | `Resistor_SMD:R_0805_2012Metric` |
| R2, R16 | 2 | Fit | 169k | RT0805BRD07169KL · 0.1% thin-film, 2012 metric | `Resistor_SMD:R_0805_2012Metric` |
| R3, R17 | 2 | Fit | 1k10 | RT0805BRD071K1L · 0.1% thin-film, 2012 metric | `Resistor_SMD:R_0805_2012Metric` |
| R4, R18 | 2 | Fit | 80k6 | ERA-6AEB8062V · 0.1% thin-film, 2012 metric | `Resistor_SMD:R_0805_2012Metric` |
| R5, R19 | 2 | Fit | 2k05 | RT0805BRD072K05L · 0.1% thin-film, 2012 metric | `Resistor_SMD:R_0805_2012Metric` |
| R6, R20 | 2 | Fit | 38k3 | ERA-6AEB3832V · 0.1% thin-film, 2012 metric | `Resistor_SMD:R_0805_2012Metric` |
| R7, R21 | 2 | Fit | 3k65 | RG2012P-3651-B-T5 · 0.1% thin-film, 2012 metric | `Resistor_SMD:R_0805_2012Metric` |
| R8, R22 | 2 | Fit | 16k5 | RG2012P-1652-B-T5 · 0.1% thin-film, 2012 metric | `Resistor_SMD:R_0805_2012Metric` |
| R9, R23 | 2 | Fit | 6k04 | ERA-6AEB6041V · 0.1% thin-film, 2012 metric | `Resistor_SMD:R_0805_2012Metric` |
| R10, R24 | 2 | Fit | 6k65 | ERA-6AEB6651V · 0.1% thin-film, 2012 metric | `Resistor_SMD:R_0805_2012Metric` |
| R11, R25 | 2 | Fit | 8k45 | ERA-6AEB8451V · 0.1% thin-film, 2012 metric | `Resistor_SMD:R_0805_2012Metric` |
| R12, R26 | 2 | Fit | 1k91 | RT0805BRD071K91L · 0.1% thin-film, 2012 metric | `Resistor_SMD:R_0805_2012Metric` |
| R13, R27 | 2 | Fit | 9k76 | ERA-6AEB9761V · 0.1% thin-film, 2012 metric | `Resistor_SMD:R_0805_2012Metric` |
| R14, R28 | 2 | Fit | 255R | RG2012P-2550-B-T5 · 0.1% thin-film, 2012 metric | `Resistor_SMD:R_0805_2012Metric` |
| R29, R30 | 2 | Fit | 10k TERM | RG2012P-103-B-T5 · 0.1% thin-film, 2012 metric; replace to suit amplifier input | `Resistor_SMD:R_0805_2012Metric` |
| R31, R33, R35, R37, R39, R41, R43 | 7 | Fit | 330R | RC0603FR-10330RL · 1%, 1608 metric | `Resistor_SMD:R_0603_1608Metric` |
| R32, R34, R36, R38, R40, R42, R44 | 7 | Fit | 100k | RT0805DRE07100KL · 0.5%, 2012 metric | `Resistor_SMD:R_0805_2012Metric` |
| R45 | 1 | Optional | 330R | RC0603FR-10330RL · 1%, 1608 metric | `Resistor_SMD:R_0603_1608Metric` |
| R46 | 1 | Optional | 100k | RT0805DRE07100KL · 0.5%, 2012 metric | `Resistor_SMD:R_0805_2012Metric` |
| R47 | 1 | Fit | 1k | RC0603FR-101KL · 1%, 1608 metric | `Resistor_SMD:R_0603_1608Metric` |
| R48 | 1 | Fit | 1M | RC0603FR-101ML · 1%, 1608 metric, unplugged-wiper pulldown | `Resistor_SMD:R_0603_1608Metric` |
| U1 | 1 | Fit | ATtiny1616-SN | ATTINY1616-SN · Wide SOIC-20, approved footprint | `Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm` |

## Copper features

| References | Qty | Function | KiCad footprint |
|---|---:|---|---|
| JP1, JP2 | 2 | Open solder jumpers. Bridge both only with K8 absent. | `Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm` |
| NT1 | 1 | Copper net tie between GND and GNDA | `NetTie:NetTie-2_SMD_Pad2.0mm` |
| TP1, TP2 | 2 | +5 V and GND probe pads | `TestPoint:TestPoint_Pad_D2.0mm` |

## Off-board parts

| Qty | Item | Specification |
|---:|---|---|
| 1 | Volume pot | 10 kΩ linear, single-gang, e.g. Bourns PTV09A-4020F-B103 |
| 1 | Regulated power source | 5.0 V DC, 0.5 A or greater. Board-side J1 polarity is 1 +5 V, 2 GND. |
| 1 | J1 mating housing | JST XHP-2 with two SXH-001T-P0.6 terminals for suitable wire, or a matching pre-crimped lead |
| 2 | Mating 1×3 connectors | 2.54 mm sockets or leads for J2 and J3, according to the pot and programmer harnesses |
| 4 | Mating 1×2 connectors | 2.54 mm sockets or leads for the four audio headers |

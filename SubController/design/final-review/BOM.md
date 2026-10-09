# Final schematic BOM — revision B, 8 October 2026

226 component references, including test-point pads. Generated from the final KiCad netlist. Inventory was read live; nothing was reserved or decremented. Stock markings/package checks remain as stated below.

## Inventory allocation

| ID | Exact recorded part | Required / stock | Buy shortage | Location |
|---:|---|---:|---:|---|
| 87 | RR1220P-471-D | 1 / 15 | 0 | SMD Parts |
| 88 | 0805N103J500CT | 2 / 38 | 0 | SMD Parts |
| 95 | EEUFR1E470H | 3 / 50 | 0 | Parts drawer 2 |
| 109 | 7805 | 1 / 17 | 0 | Voltage Regulator drawer |
| 124 | 1N4007 | 3 / 62 | 0 | Parts drawer 2 |
| 157 | C1206C104K5RACTU | 18 / 129 | 0 | SMD Parts |
| 181 | CL31B105KBHNFNE | 16 / 50 | 0 | SMD Parts |
| 197 | CL21C101JBANNNC | 5 / 100 | 0 | SMD Parts |
| 209 | 100R Thin Film | 2 / 26 | 0 | SMD Parts |
| 220 | 680R Thin Film | 1 / 39 | 0 | SMD Parts |
| 224 | 1K Thin Film | 1 / 42 | 0 | SMD Parts |
| 235 | 15K Thin Film | 4 / 22 | 0 | SMD Parts |
| 242 | 100K Thin Film | 3 / 70 | 0 | SMD Parts |
| 294 | ATTiny1614 | 1 / 4 | 0 | SMD Parts |
| 375 | 10K Thin Film | 34 / 50 | 0 | SMD Parts |
| 376 | 47K Thin Film | 13 / 30 | 0 | SMD Parts |
| 414 | 220n Film | 11 / 8 | 3 | Parts Drawer 2 |
| 461 | BC337 | 9 / 19 | 0 | not recorded |
| 493 | RMCF0805FT4K70 | 4 / 100 | 0 | SMD Parts |
| 500 | TPS7A3901 | 1 / 2 | 0 | SMD Parts |
| 503 | RMCF0805FT2K20 | 2 / 100 | 0 | SMD Parts |
| 505 | CL31A106KBHNNNE | 6 / 10 | 0 | SMD Parts |
| 510 | 1N4148W | 3 / 85 | 0 | Parts drawer 2 |
| 511 | RR1220P-223-D | 5 / 50 | 0 | SMD Parts |
| 588 | LM339 | 1 / 2 | 0 | SMD Parts |
| 595 | CS3310 | 1 / 5 | 0 | not recorded |
| 615 | 4570 | 6 / 22 | 0 | SMD Parts |
| 616 | AGN2004H | 5 / 6 | 0 | not recorded |

## Complete grouped BOM

| References | Value | Qty | Status / inventory | Footprint | Qualification |
|---|---|---:|---|---|---|
| C1, C2, C62, C64, C65 | 100p C0G / 50V | 5 | OWNED / 197 | `Capacitor_SMD:C_0805_2012Metric` | 50V C0G, 2012 metric. Match C1/C64 and C2/C65 within 2%; C62 compensation. |
| C3, C4, C7, C8, C17, C18 | 100nF | 6 | OWNED / 157 | `Capacitor_SMD:C_1206_3216Metric` | 50V X7R supply bypass, 3216 metric. |
| C5, C6, C9, C10, C19, C20 | 1uF | 6 | OWNED / 181 | `Capacitor_SMD:C_1206_3216Metric` | 50V X7R supply bypass, 3216 metric. |
| C11, C12, C13, C14, C16 | 220n FILM / 63V | 5 | OWNED / 414 | `Capacitor_THT:C_Rect_L7.2mm_W2.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2` | 63V 5% film, body <=7.2x2.5mm, pitch5mm; measure stock lead pitch/dielectric. Buy shortage as KEMET 82DC3220AA60J (legacy R82DC3220AA60J), polyester film; select matching pairs. |
| C21, C22, C23, C25, C26, C33, C34, C37, C38, C41, C52, C59 | 100n / 50V | 12 | OWNED / 157 | `Capacitor_SMD:C_1206_3216Metric` | 50V X7R supply bypass, 3216 metric. |
| C24, C29, C30 | 220n FILM | 3 | OWNED / 414 | `SubController:Film_7.2x2.5mm_P5.00mm` | 63V 5% film, body <=7.2x2.5mm, pitch5mm; measure stock lead pitch/dielectric. Buy shortage as KEMET 82DC3220AA60J (legacy R82DC3220AA60J), polyester film; select matching pairs. |
| C27, C28, C35, C36, C39, C40, C50, C53, C54, C55 | 1u / 50V | 10 | OWNED / 181 | `Capacitor_SMD:C_1206_3216Metric` | 50V X7R supply bypass, 3216 metric. |
| C31, C32 | 220n FILM | 2 | SHORTAGE / BUY / 414 | `SubController:Film_7.2x2.5mm_P5.00mm` | 63V 5% film, body <=7.2x2.5mm, pitch5mm; measure stock lead pitch/dielectric. Buy shortage as KEMET 82DC3220AA60J (legacy R82DC3220AA60J), polyester film; select matching pairs. |
| C44, C45, C51 | 47u / 25V FR | 3 | OWNED / 95 | `Capacitor_THT:CP_Radial_D5.0mm_P2.50mm` | 25V Panasonic FR; verify formed lead spacing against 2.5mm footprint. |
| C46, C47, C48, C49, C57, C58 | 10u / 50V X5R | 6 | OWNED / 505 | `Capacitor_SMD:C_1206_3216Metric` | 50V X5R, 3216 metric; supply use only. Verify effective capacitance at 15V against regulator requirement. |
| C56 | 220n FILM / 63V | 1 | SHORTAGE / BUY / 414 | `Capacitor_THT:C_Rect_L7.2mm_W2.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2` | 63V 5% film, body <=7.2x2.5mm, pitch5mm; measure stock lead pitch/dielectric. Buy shortage as KEMET 82DC3220AA60J (legacy R82DC3220AA60J), polyester film; select matching pairs. |
| C60, C61 | 10n C0G / 50V | 2 | OWNED / 88 | `Capacitor_SMD:C_0805_2012Metric` | 50V C0G, 2012 metric; TPS feed-forward. |
| C63 | 10u / 50V BIPOLAR | 1 | NEW / SOURCE | `SubController:C_NP_Radial_D8.0mm_P3.50mm` | Nichicon UES1H100MPM; 10uF 50V bipolar; diameter8mm height11.5mm pitch3.5mm. |
| D1, D5, D6 | 1N4148W | 3 | OWNED / 510 | `Diode_SMD:D_SOD-123` |  |
| D2, D3, D4 | 1N4007 | 3 | OWNED / 124 | `Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal` |  |
| D7 | BAT54A-7-F | 1 | NEW / SOURCE | `Package_TO_SOT_SMD:SOT-23` | Diodes BAT54A-7-F common-anode dual Schottky: pins1/2 cathodes,3 common anode. |
| J1 | REF LEFT | 1 | MECHANICAL / SOURCE | `Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical` | Preserved connector family. Fit exact matching housing: JST-XH2.50mm is not Multicomp2.54mm. Headers/jumpers and panel controls must be checked separately. |
| J2 | REF RIGHT | 1 | MECHANICAL / SOURCE | `Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical` | Preserved connector family. Fit exact matching housing: JST-XH2.50mm is not Multicomp2.54mm. Headers/jumpers and panel controls must be checked separately. |
| J3 | MARANTZ LFE | 1 | MECHANICAL / SOURCE | `Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical` | Preserved connector family. Fit exact matching housing: JST-XH2.50mm is not Multicomp2.54mm. Headers/jumpers and panel controls must be checked separately. |
| J4 | SLOPE: 1-2=12 / 2-3=24 | 1 | MECHANICAL / SOURCE | `Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical` | Preserved connector family. Fit exact matching housing: JST-XH2.50mm is not Multicomp2.54mm. Headers/jumpers and panel controls must be checked separately. |
| J9 | PANEL PHASE 50k LINEAR | 1 | MECHANICAL / SOURCE | `Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical` | Preserved connector family. Fit exact matching housing: JST-XH2.50mm is not Multicomp2.54mm. Headers/jumpers and panel controls must be checked separately. |
| J10 | PHASE BYPASS / ALLPASS | 1 | MECHANICAL / SOURCE | `Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical` | Preserved connector family. Fit exact matching housing: JST-XH2.50mm is not Multicomp2.54mm. Headers/jumpers and panel controls must be checked separately. |
| J11 | HP BANK 1: 15/20/25 | 1 | MECHANICAL / SOURCE | `Connector_PinHeader_2.54mm:PinHeader_2x03_P2.54mm_Vertical` | Preserved connector family. Fit exact matching housing: JST-XH2.50mm is not Multicomp2.54mm. Headers/jumpers and panel controls must be checked separately. |
| J12 | HP BANK 2: 15/20/25 | 1 | MECHANICAL / SOURCE | `Connector_PinHeader_2.54mm:PinHeader_2x03_P2.54mm_Vertical` | Preserved connector family. Fit exact matching housing: JST-XH2.50mm is not Multicomp2.54mm. Headers/jumpers and panel controls must be checked separately. |
| J13 | AV HP: BYPASS / FILTER | 1 | MECHANICAL / SOURCE | `Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical` | Preserved connector family. Fit exact matching housing: JST-XH2.50mm is not Multicomp2.54mm. Headers/jumpers and panel controls must be checked separately. |
| J14 | COMMON HP: BYPASS / MODE | 1 | MECHANICAL / SOURCE | `Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical` | Preserved connector family. Fit exact matching housing: JST-XH2.50mm is not Multicomp2.54mm. Headers/jumpers and panel controls must be checked separately. |
| J15 | POLARITY 0 / 180 | 1 | MECHANICAL / SOURCE | `Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical` | Preserved connector family. Fit exact matching housing: JST-XH2.50mm is not Multicomp2.54mm. Headers/jumpers and panel controls must be checked separately. |
| J16 | P68 SIGNAL / SENSE | 1 | MECHANICAL / SOURCE | `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical` | Preserved connector family. Fit exact matching housing: JST-XH2.50mm is not Multicomp2.54mm. Headers/jumpers and panel controls must be checked separately. |
| J17 | UPDI / +5R / GND | 1 | MECHANICAL / SOURCE | `Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical` | Preserved connector family. Fit exact matching housing: JST-XH2.50mm is not Multicomp2.54mm. Headers/jumpers and panel controls must be checked separately. |
| J18 | REF LEVEL | 1 | MECHANICAL / SOURCE | `Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical` | Preserved connector family. Fit exact matching housing: JST-XH2.50mm is not Multicomp2.54mm. Headers/jumpers and panel controls must be checked separately. |
| J19 | LFE LEVEL | 1 | MECHANICAL / SOURCE | `Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical` | Preserved connector family. Fit exact matching housing: JST-XH2.50mm is not Multicomp2.54mm. Headers/jumpers and panel controls must be checked separately. |
| J20 | ISOLATED TRIGGER 12V | 1 | MECHANICAL / SOURCE | `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical` | Preserved connector family. Fit exact matching housing: JST-XH2.50mm is not Multicomp2.54mm. Headers/jumpers and panel controls must be checked separately. |
| J21 | +15V / GND / -15V | 1 | MECHANICAL / SOURCE | `Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical` | Preserved connector family. Fit exact matching housing: JST-XH2.50mm is not Multicomp2.54mm. Headers/jumpers and panel controls must be checked separately. |
| J22 | EARLY PSU POWER-FAIL | 1 | MECHANICAL / SOURCE | `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical` | Preserved connector family. Fit exact matching housing: JST-XH2.50mm is not Multicomp2.54mm. Headers/jumpers and panel controls must be checked separately. |
| J23 | RUN LED: PIN1 A / PIN2 K | 1 | MECHANICAL / SOURCE | `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical` | Preserved connector family. Fit exact matching housing: JST-XH2.50mm is not Multicomp2.54mm. Headers/jumpers and panel controls must be checked separately. |
| J24 | AUTO / REF(open) / AV | 1 | MECHANICAL / SOURCE | `Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical` | Preserved connector family. Fit exact matching housing: JST-XH2.50mm is not Multicomp2.54mm. Headers/jumpers and panel controls must be checked separately. |
| J25 | LP: FILTER / BYPASS | 1 | MECHANICAL / SOURCE | `Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical` | Preserved connector family. Fit exact matching housing: JST-XH2.50mm is not Multicomp2.54mm. Headers/jumpers and panel controls must be checked separately. |
| J26 | FORCE MUTE (FIT SHUNT) | 1 | MECHANICAL / SOURCE | `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical` | Preserved connector family. Fit exact matching housing: JST-XH2.50mm is not Multicomp2.54mm. Headers/jumpers and panel controls must be checked separately. |
| K1, K2, K3, K4, K5 | AGN2004H | 5 | OWNED / 616 | `Custom:Relay_DPDT_Panasonic_AGN2004H` | AGN2004H rated4.5V; user specifies5V. Existing user footprint and STEP copied exactly. Coil1+/8-, NC2/7 COM3/6 NO4/5. |
| Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9 | BC337 (stock) | 9 | OWNED / 461 | `Package_TO_SOT_THT:TO-92_Inline` | BC337 manufacturer not recorded; verify physical C1/B2/E3 and collector saturation. |
| R1, R2, R3, R4, R119, R120, R121, R122 | 47k / 0.1% | 8 | OWNED / 376 | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks. |
| R5, R6 | 22K | 2 | OWNED / 511 | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks. |
| R7, R8, R9 | 10K | 3 | OWNED / 375 | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks. |
| R10, R17, R24, R31 | 4k27 | 4 | NEW / SOURCE | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks. |
| R38 | 20k | 1 | NEW / SOURCE | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks. |
| R39, R40, R41, R50, R51, R59, R60, R61, R62, R64, R65, R66, R68, R69, R71, R72, R97, R98, R99, R103 | 10k | 20 | OWNED / 375 | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks. |
| R42 | 2k2 | 1 | OWNED / 503 | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks. |
| R43, R67, R70, R73, R102 | 47k | 5 | OWNED / 376 | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks. |
| R44 | 16k9 | 1 | NEW / SOURCE | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks. |
| R45 | 12k7 | 1 | NEW / SOURCE | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks. |
| R46 | 10k2 | 1 | NEW / SOURCE | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks. |
| R47 | 34k | 1 | NEW / SOURCE | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks. |
| R48 | 25k5 | 1 | NEW / SOURCE | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks. |
| R49 | 20k5 | 1 | NEW / SOURCE | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks. |
| R52, R75, R76, R106, R107, R109, R110, R111, R114 | 10k / 0.1% | 9 | OWNED / 375 | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks. |
| R53, R89, R113 | 20k / 0.1% | 3 | NEW / SOURCE | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks. |
| R54, R93 | 100R | 2 | OWNED / 209 | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; stock tolerance must be checked, utility value not precision-critical. |
| R55 | 22k | 1 | OWNED / 511 | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks. |
| R63 | 2k2 / 0.125W | 1 | OWNED / 503 | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks. |
| R74 | 680R | 1 | OWNED / 220 | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks. |
| R83 | 100k / 1% | 1 | OWNED / 242 | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks. |
| R84, R88 | 10k / 1% | 2 | OWNED / 375 | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks. |
| R85 | 15k / 0.1% | 1 | NEW / SOURCE | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks. |
| R86 | 180k / 0.1% | 1 | NEW / SOURCE | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks. |
| R87 | 24k / 1% | 1 | NEW / SOURCE | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks. |
| R90 | 86k6 / 0.1% | 1 | NEW / SOURCE | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks. |
| R91 | 470R | 1 | OWNED / 87 | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks. |
| R92, R94 | 100k | 2 | OWNED / 242 | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks. |
| R95 | 1k | 1 | OWNED / 224 | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks. |
| R96, R100, R101, R104 | 4k7 | 4 | OWNED / 493 | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks. |
| R105, R108 | 22k / 0.5% | 2 | OWNED / 511 | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks. |
| R112 | 2k2 / 0.25W | 1 | NEW / SOURCE | `Resistor_SMD:R_0805_2012Metric` | 2012 metric 0.25W required: 113mW sustained worst injection-limiter calculation. |
| R115, R116, R117, R118 | 15k | 4 | OWNED / 235 | `Resistor_SMD:R_0805_2012Metric` | 2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks. |
| RV1 | PTD904-2015K-B203 | 1 | PROJECT RECORD / VERIFY | `SubController:PTD904_2015K_B203_Horizontal` | Prior project record reports2 owned; not in live inventory. Need1 PTD904-2015K-B203, four20k linear gangs. Measure tracking before layout. |
| TP1 | +15V | 1 | PCB PAD | `TestPoint:TestPoint_Pad_D1.5mm` | No purchased part. |
| TP2 | -15V | 1 | PCB PAD | `TestPoint:TestPoint_Pad_D1.5mm` | No purchased part. |
| TP3 | +5A | 1 | PCB PAD | `TestPoint:TestPoint_Pad_D1.5mm` | No purchased part. |
| TP4 | -5A | 1 | PCB PAD | `TestPoint:TestPoint_Pad_D1.5mm` | No purchased part. |
| TP5 | +5R | 1 | PCB PAD | `TestPoint:TestPoint_Pad_D1.5mm` | No purchased part. |
| TP6 | RUN_HW | 1 | PCB PAD | `TestPoint:TestPoint_Pad_D1.5mm` | No purchased part. |
| TP7 | GND | 1 | PCB PAD | `TestPoint:TestPoint_Pad_D1.5mm` | No purchased part. |
| TP8 | BUF_L | 1 | PCB PAD | `TestPoint:TestPoint_Pad_D1.5mm` | No purchased part. |
| TP9 | BUF_R | 1 | PCB PAD | `TestPoint:TestPoint_Pad_D1.5mm` | No purchased part. |
| TP10 | MONO | 1 | PCB PAD | `TestPoint:TestPoint_Pad_D1.5mm` | No purchased part. |
| TP11 | LP_SLOPE | 1 | PCB PAD | `TestPoint:TestPoint_Pad_D1.5mm` | No purchased part. |
| TP12 | PHASE_OUT | 1 | PCB PAD | `TestPoint:TestPoint_Pad_D1.5mm` | No purchased part. |
| TP13 | HP_OUT | 1 | PCB PAD | `TestPoint:TestPoint_Pad_D1.5mm` | No purchased part. |
| TP14 | AMP_OUT | 1 | PCB PAD | `TestPoint:TestPoint_Pad_D1.5mm` | No purchased part. |
| TP15 | TRIGGER_N | 1 | PCB PAD | `TestPoint:TestPoint_Pad_D1.5mm` | No purchased part. |
| TP16 | AV_ENABLE | 1 | PCB PAD | `TestPoint:TestPoint_Pad_D1.5mm` | No purchased part. |
| TP17 | RUN_REQUEST | 1 | PCB PAD | `TestPoint:TestPoint_Pad_D1.5mm` | No purchased part. |
| TP18 | RAIL_GOOD | 1 | PCB PAD | `TestPoint:TestPoint_Pad_D1.5mm` | No purchased part. |
| U1, U2, U3, U4, U5, U6 | uPC4570G2 | 6 | OWNED / 615 | `SubController:SOP-8_uPC4570G2_4.4x5.2mm_P1.27mm` | Salvaged 4570; electrical review uses NEC/Renesas uPC4570G2. Inventory says JRC; user physical identity/package check pending. |
| U7 | CS3310 | 1 | OWNED / 595 | `Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm` | Stock SMD suffix unconfirmed; wide SOIC16 assumed. User will verify physical package. |
| U8 | ATtiny1614-SS | 1 | OWNED / 294 | `Package_SO:SOIC-14_3.9x8.7mm_P1.27mm` | Microchip ATtiny1614-SS, SOIC14, direct GPIO. |
| U10 | VO617A-3 | 1 | NEW / SOURCE | `Package_DIP:DIP-4_W7.62mm` | Vishay VO617A-3, DIP4 7.62mm; buy one. |
| U11 | TPS7A3901 | 1 | OWNED / 500 | `SubController:TPS7A3901_DSC0010J_WSON10` | TI TPS7A3901DSCR/DSCT, WSON10 DSC0010J; EP11 GND, thermal vias. |
| U13 | 7805 (Diodes stock) | 1 | OWNED / 109 | `Package_TO_SOT_THT:TO-220-3_Vertical` | Diodes stock generic 7805; verify exact marking, pin1 IN/2 GND/3 OUT. Heatsink mandatory. |
| U14 | LM4040A25IDBZR | 1 | NEW / SOURCE | `Package_TO_SOT_SMD:SOT-23` | TI LM4040A25IDBZR SOT23; buy one. |
| U15 | LM339 | 1 | OWNED / 588 | `Package_SO:SOIC-14_3.9x8.7mm_P1.27mm` | Inventory lacks manufacturer; standard LM339 SOIC14, verify markings. |

## Additional assembly items

- U13 heatsink and mounting hardware: effective junction-to-ambient <=20 °C/W at 2.7W, target board ambient <=50 °C. Leave physical clearance during layout; do not rely on a bare TO-220.
- One external 50k linear phase pot; two quadrature encoders with dry contacts; panel mode switch optional; jumper shunts.
- Insulated RCA sockets and wiring; connector mating housings/contacts; separately regulated shared-return ±15V supply rated at least +350mA / −100mA.
- P68 speaker-protection and early-power-fail interface remain system requirements. No mains components have been designed here.

The unavailable exact part number for salvaged/loose stock is a recorded limitation, not an invented manufacturer identification.

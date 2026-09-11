# Stereo schematic draft — pending engineering decisions

The working project schematic, original PowerOutput.kicad_sch, PCB, and project settings are unchanged. The proposed stereo schematic is staged in this folder and exported as stereo-draft.pdf. **This is not a completed or build-ready schematic.**

## Decisions required

1. **OPA1656 power:** The requested +5 V supply permits input common-mode voltages only up to V+ − 2.25 V, about 2.751 V. The requested input followers reach about 2.997 V at 2 Vrms. This exceeds the specified operating range. The proposed correction is to power both OPA1656 packages from +12V_GD, retaining a 2.5 V reference and 5 V comparator/logic supply. The draft deliberately uses an undriven OPA_SUPPLY_PENDING net until this change is authorized. Keeping +5 V would reduce the symmetric input limit to approximately 1.01 Vrms and ideal output capability to approximately 9 W/channel for this carrier; it would not satisfy the 30 W target. TI OPA1656 datasheet table 6.5 is the source of this limit.
2. **MOSFET choice:** The actual saved sheet uses Q5–Q8 DMN6070SY with a generic G/D/S symbol and SOT-89-3 footprint. AGENTS.md specifies DMTH6016LPS. The draft preserves the saved DMN6070SY provisionally. Select the intended part before finalizing. The saved DMN6070SY physical pin mapping still needs visual verification against the manufacturer's package diagram if retained. No MOSFET substitution has been applied.

AGENTS.md states: “Do not substitute components or alter circuit topology without being asked.” The op-amp rail change also departs from the explicit +5V_A allocation in the request. These are engineering decisions, not an ERC suppression or software approval requirement.

## Verification performed

- Original baseline ERC: 72 violations (65 errors, 7 warnings).
- Latest draft ERC: **1 error, 0 warnings, no exclusions added**. The error is `power_pin_not_driven` at U1 pin 8 on OPA_SUPPLY_PENDING. U3 shares this intentionally unresolved supply. See erc.json for the complete report.
- Independent KiCad XML netlist comparison: all 203 intended main-sheet pin assignments pass. All 53 inherited physical components per output sheet match the original power-stage netlist, allowing only the specified control-net remapping and global PGND/power naming. The left/right output sheets match electrically after reference/channel renaming. See connectivity-check.json.
- PDF exported successfully, with one A1 control sheet and two A3 power sheets. Rendered pages inspected.
- PCB, original output sheet, .kicad_pro, and .kicad_prl SHA-256 checks all pass against the preserved baseline. No PCB work was performed.
- No simulation, hardware timing, audio measurements, thermal validation, or fabrication sign-off has been performed.

## IC count and allocation

**14 IC packages**: 4 UCC27301ADRCR, 2 TPS7A4901DGNR, 2 OPA1656ID, 2 TLV3602DGKR, 2 SN74LVC1G04DBVR, and 2 SN74LVC2G17DBVR. Additionally, 8 discrete MOSFETs.

| Device | Section A | Section B | Supply |
|---|---|---|---|
| U1 OPA1656 | LEFT follower: 3 IN+, 2 IN−, 1 OUT | RIGHT follower: 5 IN+, 6 IN−, 7 OUT | Pin 8 pending; pin 4 PGND |
| U3 OPA1656 | VREF buffer: 3 IN+, 2 IN−, 1 OUT | Integrator: 5 IN+, 6 IN−, 7 OUT | Pin 8 pending; pin 4 PGND |
| U7 TLV3602 | Oscillator: 1 IN+, 2 IN−, 7 OUT | LEFT PWM: 4 IN+, 3 IN−, 6 OUT | 8 +5V_A, 5 PGND |
| U8 TLV3602 | RIGHT PWM: 1 IN+, 2 IN−, 7 OUT | Spare: 4 IN+ PGND, 3 IN− VREF, 6 OUT NC | 8 +5V_A, 5 PGND |

The spare comparator has a defined LOW state once VREF settles. This is an application of the datasheet's input limits and truth table; the datasheet does not contain a special unused-channel prescription. During rail startup its output is irrelevant because it is unconnected.

U4/U5 form the LEFT inverter/Schmitt logic; U9/U10 form RIGHT. U2/U6 drive LEFT and U102/U106 drive RIGHT. U11 regulates +12V_GD, U12 regulates +5V_A.

## Regulators

Both regulators use a project-local copy of the user's **TPS7A4901DGNR** symbol, redrawn for readability with physical numbers unchanged and electrical pin types corrected from generic passive types. TI pin mapping: 1 OUT, 2 FB, 3 NC, 4 GND, 5 EN, 6 NR/SS, 7 DNC, 8 IN; exposed pad is represented as pad 9 in KiCad. Pins 4 and 9 connect to PGND. EN connects to IN/+24 V. Pins 3 and 7 are deliberately unconnected. DNC is not connected to any net.

Use VFB = **1.185 V**, not the different NR/SS reference value, for the feedback calculation:

| Rail | Upper resistor | Lower resistor | Nominal calculated output |
|---|---:|---:|---:|
| +12V_GD | 91.2 kΩ, 0.1% | 10 kΩ, 0.1% | **11.9922 V** |
| +5V_A | 32.2 kΩ, 0.1% | 10 kΩ, 0.1% | **5.0007 V** |

Vout = 1.185 × (1 + Rtop/Rbottom). Divider current is 118.5 µA, comfortably above the required 5 µA minimum. Actual output includes regulator accuracy, resistor tolerance, and feedback bias current. An early commentary incorrectly gave 12.0006 V for the first divider; 11.9922 V is the corrected result.

Each regulator has 10 µF/50 V X7R input capacitance, 10 µF/25 V X7R output capacitance, 10 nF NR/SS-to-PGND, and 10 nF feed-forward across its upper resistor. The effective input/output capacitance must remain ≥2.2 µF and ESR <0.2 Ω after DC bias and temperature; exact ceramic MPNs are not selected. The DGN footprint is KiCad HVSSOP-8-1EP_3x3mm_P0.65mm_EP1.57x1.89mm. Final footprint/package mechanical review remains part of component release.

Two shared Panasonic FR EEUFR1V102, 1000 µF/35 V capacitors are at main power entry. These are radial THT bulk capacitors, preserving the existing selected part; ordinary new R/C passives use metric SMD footprints. The original C17 and J14 are moved into the draft main sheet, not duplicated per output channel.

Each TPS7A4901 is limited to 150 mA and dissipates approximately (24 − Vout) × Iout. At 100 mA, the 12 V regulator dissipates about 1.20 W; at 40 mA, the 5 V regulator dissipates about 0.76 W. These are examples, not verified operating currents. Gate-driver rail budgeting must include 8 × Qg × f, four driver operating currents, and any op-amp current if the rail change is accepted. Nominal Qg at 10 V suggests about 39.7 mA for DMN6070SY or 54.9 mA for DMTH6016LPS gate charging alone at 403.7 kHz; 12 V drive requires a revised Qg estimate. Thermal/current validation remains outstanding.

## Reference and oscillator

The shared 10 kΩ/10 kΩ divider yields nominal 2.50035 V. Raw VREF has 10 µF and 100 nF bypassing. U3A buffers it as a follower. Large bypass capacitors are on the raw divider rather than directly loading the follower output.

The suggested original threshold arrangement is incompatible with directly driving an inverting integrator: triangle at the comparator's negative input, with output-derived thresholds at its positive input, has the wrong overall sign for this integrator loop. The corrected self-running arrangement uses **10 kΩ from TRIANGLE_400K to comparator IN+, 49.9 kΩ from OSC_SQUARE to IN+, and IN− = VREF**. The integrator uses the specified 3.09 kΩ square-wave input resistor and 1 nF C0G feedback capacitor, with its positive input at VREF. This is the requested mathematical correction to the initial oscillator values/topology, without adding an IC or duplicating the carrier.

At a comparator transition:

Vtriangle = VREF + (10k / 49.9k) × (VREF − Vsquare).

Assuming symmetric ideal 0 to 5.0007 V comparator swing:

- Lower triangle threshold: **1.999278 V**.
- Upper triangle threshold: **3.001422 V**.
- Triangle amplitude: **1.002144 Vpp**.
- Integrator slope magnitude: 2.50035 / (3090 × 1 nF) = **0.809175 V/µs**.
- Frequency: 49.9k / (4 × 10k × 3.09k × 1 nF) = **403.7217 kHz**.

Using 40.2 kΩ in this corrected non-inverting Schmitt topology would instead give about 325.243 kHz and 1.244 Vpp; this is why 49.9 kΩ was used. Comparator intrinsic hysteresis, actual high/low voltage, delay, resistor/capacitor tolerance, finite op-amp dynamics, and startup alter these ideal values. The integrator's input common mode remains at VREF even as its output moves through the triangle range. Startup and waveform shape have not been simulated or measured.

## Input paths and PWM

Both paths are identical: 220 nF film coupling, 47 kΩ series, 10 kΩ to VREF, 100 pF C0G to VREF, unity OPA1656 follower, and 100 Ω series isolation into the PWM comparator. Midband attenuation is **10/57 = 0.1754386 (−15.118 dB)**. The input high-pass corner is about **12.6918 Hz**, assuming negligible source impedance. The RF pole is about **193 kHz**, using (47k || 10k) and 100 pF; the full circuit also includes op-amp input/parasitic capacitance.

2 Vrms produces approximately 0.350877 Vrms or 0.496215 Vpk about VREF. This is near full modulation of the nominal 1.002 Vpp triangle. Ideal lossless BTL calculations give about 35.3 W/8 Ω at that input and about 1.84 Vrms input for 30 W. These calculations do not establish real output power, distortion, clipping margin, or bootstrap refresh margin. The OPA1656 supply issue above must be resolved first.

AUDIO_L/R drives comparator IN+, TRIANGLE_400K drives IN−. PWM_L/R is HIGH when audio exceeds triangle.

## Dead time and enable

Each channel has one inverter and two non-inverting Schmitt buffer sections. Inverter pins are 1 NC, 2 A, 3 PGND, 4 Y, 5 +5V_A. Dual-buffer pins are 1 1A, 6 1Y, 3 2A, 4 2Y, 2 PGND, 5 +5V_A. These physical maps match TI's specified DBV packages.

Each 330 Ω timing resistor is paralleled by a 1N4148W with **cathode (KiCad pin 1) at source logic and anode (pin 2) at the capacitor/Schmitt input**. A 100 pF C0G capacitor goes from that input to PGND. The capacitor charges through the resistor when the source rises; when the source falls, the diode conducts from the charged capacitor into the source's low output. This makes the rising edge delayed and the falling edge faster.

Nominal RC time constant is **33 ns**; the ideal delay to a 2.5 V threshold from a 5 V step is **22.87 ns**. TI specifies VT+ ranges of 1.9–3.1 V at 4.5 V and 2.2–3.7 V at 5.5 V. Applying each threshold range at its respective supply gives approximately **18.1–38.5 ns** and **16.9–36.9 ns**, respectively, before driver resistance, parasitics, and propagation delays. This is not a guaranteed dead-time range. Inverter skew makes the two commutations asymmetric; diode turn-off behavior, Schmitt propagation delay, UCC27301A mismatch, MOSFET turn-off and gate resistance also matter. The 20–30 ns goal is explicitly marked **DEAD TIME TUNE**, not final.

ENABLE_L and ENABLE_R each have 10 kΩ to PGND, an optional **DNP 1 kΩ** to +5V_A, and a test point. Fitting that option gives about 4.55 V ignoring small enable-input currents. Both channels default disabled. No MCU/protection/feedback/volume circuitry was added.

## Hierarchical wiring

| Main signal | Sheet port | LEFT driver pins | RIGHT driver pins |
|---|---|---|---|
| L_DRIVE_P / R_DRIVE_P | DRIVE_P | U2.7 HI and U6.8 LI | U102.7 HI and U106.8 LI |
| L_DRIVE_N / R_DRIVE_N | DRIVE_N | U2.8 LI and U6.7 HI | U102.8 LI and U106.7 HI |
| ENABLE_L / ENABLE_R | ENABLE | U2.6 and U6.6 | U102.6 and U106.6 |

Both sheets share only global +24V, +12V_GD, and PGND power nets plus their three named control ports. Switch nodes, gate/bootstrap signals, filter nets, and speaker outputs remain local. J15 is LEFT SPEAKER and J115 is RIGHT SPEAKER. The existing local decoupling, LC filter, Zobel, DNP snubbers/diodes, and DNP 1 nF output-to-PGND capacitors remain intact in both copies. HB power flags model the actual internal UCC27301A bootstrap charging diode; they do not hide an unpowered external supply.

## Component inventory

The draft has **193 physical components**, including **30 DNP**: 14 ICs, 8 MOSFETs, 53 resistors, 67 capacitors, 12 diodes, 2 coupled inductors, 4 connectors, and 33 test points. Power flags are excluded from these totals. Section units of a package are counted once. Exact inventory follows, including existing/reused parts and all added draft parts; no working-project BOM or PCB has been changed.

| Reference | Value | Sheet | Status | Population | Footprint |
|---|---|---|---|---|---|
| C1 | 100n / 25V | LEFT | Preserved left stage | Fit | Capacitor_SMD:C_0805_2012Metric |
| C2 | 100nF | LEFT | Preserved left stage | Fit | Capacitor_SMD:C_0805_2012Metric |
| C3 | 4.7uF | LEFT | Preserved left stage | Fit | Capacitor_SMD:C_0805_2012Metric |
| C4 | 100nF | LEFT | Preserved left stage | Fit | Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder |
| C5 | 1uF | LEFT | Preserved left stage | Fit | Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder |
| C6 | 10uF | LEFT | Preserved left stage | Fit | Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder |
| C7 | 100n / 25V | LEFT | Preserved left stage | Fit | Capacitor_SMD:C_0805_2012Metric |
| C8 | 100nF | LEFT | Preserved left stage | Fit | Capacitor_SMD:C_0805_2012Metric |
| C9 | 4.7uF | LEFT | Preserved left stage | Fit | Capacitor_SMD:C_0805_2012Metric |
| C10 | 100nF | LEFT | Preserved left stage | Fit | Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder |
| C11 | 1uF | LEFT | Preserved left stage | Fit | Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder |
| C12 | 10uF | LEFT | Preserved left stage | Fit | Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder |
| C13 | 330p DNP | LEFT | Preserved left stage | DNP | Capacitor_SMD:C_0805_2012Metric |
| C14 | 330p DNP | LEFT | Preserved left stage | DNP | Capacitor_SMD:C_0805_2012Metric |
| C15 | 330n | LEFT | Preserved left stage | Fit | Capacitor_THT:C_Rect_L7.2mm_W3.0mm_P5.00mm_FKS2_FKP2_MKS2_MKP2 |
| C16 | 100n / 100V | LEFT | Preserved left stage | Fit | Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder |
| C17 | 1000u / 35V FR | Main | Existing / rewired | Fit | Capacitor_THT:CP_Radial_D12.5mm_P5.00mm |
| C18 | 1nF | LEFT | Preserved left stage | DNP | Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder |
| C19 | 1nF | LEFT | Preserved left stage | DNP | Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder |
| C20 | 1000u / 35V FR | Main | Added in draft | Fit | Capacitor_THT:CP_Radial_D12.5mm_P5.00mm |
| C21 | 10u / 50V | Main | Added in draft | Fit | Capacitor_SMD:C_1210_3225Metric |
| C22 | 10n C0G | Main | Added in draft | Fit | Capacitor_SMD:C_0805_2012Metric |
| C23 | 10n C0G | Main | Added in draft | Fit | Capacitor_SMD:C_0805_2012Metric |
| C24 | 10u / 25V | Main | Added in draft | Fit | Capacitor_SMD:C_1210_3225Metric |
| C25 | 10u / 50V | Main | Added in draft | Fit | Capacitor_SMD:C_1210_3225Metric |
| C26 | 10n C0G | Main | Added in draft | Fit | Capacitor_SMD:C_0805_2012Metric |
| C27 | 10n C0G | Main | Added in draft | Fit | Capacitor_SMD:C_0805_2012Metric |
| C28 | 10u / 25V | Main | Added in draft | Fit | Capacitor_SMD:C_1210_3225Metric |
| C29 | 10u / 16V | Main | Added in draft | Fit | Capacitor_SMD:C_0805_2012Metric |
| C30 | 100n / 16V | Main | Added in draft | Fit | Capacitor_SMD:C_0805_2012Metric |
| C31 | 1n C0G / 1% | Main | Added in draft | Fit | Capacitor_SMD:C_0805_2012Metric |
| C32 | 100n / 25V | Main | Added in draft | Fit | Capacitor_SMD:C_0805_2012Metric |
| C33 | 4u7 / 25V | Main | Added in draft | Fit | Capacitor_SMD:C_0805_2012Metric |
| C34 | 100n / 25V | Main | Added in draft | Fit | Capacitor_SMD:C_0805_2012Metric |
| C35 | 4u7 / 25V | Main | Added in draft | Fit | Capacitor_SMD:C_0805_2012Metric |
| C36 | 100n / 25V | Main | Added in draft | Fit | Capacitor_SMD:C_0805_2012Metric |
| C37 | 100n / 25V | Main | Added in draft | Fit | Capacitor_SMD:C_0805_2012Metric |
| C38 | 100n / 25V | Main | Added in draft | Fit | Capacitor_SMD:C_0805_2012Metric |
| C39 | 100n / 25V | Main | Added in draft | Fit | Capacitor_SMD:C_0805_2012Metric |
| C40 | 220n FILM | Main | Added in draft | Fit | Capacitor_SMD:C_2220_5750Metric |
| C41 | 100p C0G | Main | Added in draft | Fit | Capacitor_SMD:C_0805_2012Metric |
| C42 | 100p C0G | Main | Added in draft | Fit | Capacitor_SMD:C_0805_2012Metric |
| C43 | 100p C0G | Main | Added in draft | Fit | Capacitor_SMD:C_0805_2012Metric |
| C44 | 100n / 25V | Main | Added in draft | Fit | Capacitor_SMD:C_0805_2012Metric |
| C45 | 220n FILM | Main | Added in draft | Fit | Capacitor_SMD:C_2220_5750Metric |
| C46 | 100p C0G | Main | Added in draft | Fit | Capacitor_SMD:C_0805_2012Metric |
| C47 | 100p C0G | Main | Added in draft | Fit | Capacitor_SMD:C_0805_2012Metric |
| C48 | 100p C0G | Main | Added in draft | Fit | Capacitor_SMD:C_0805_2012Metric |
| C49 | 100n / 25V | Main | Added in draft | Fit | Capacitor_SMD:C_0805_2012Metric |
| C101 | 100n / 25V | RIGHT | Added: right copy | Fit | Capacitor_SMD:C_0805_2012Metric |
| C102 | 100nF | RIGHT | Added: right copy | Fit | Capacitor_SMD:C_0805_2012Metric |
| C103 | 4.7uF | RIGHT | Added: right copy | Fit | Capacitor_SMD:C_0805_2012Metric |
| C104 | 100nF | RIGHT | Added: right copy | Fit | Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder |
| C105 | 1uF | RIGHT | Added: right copy | Fit | Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder |
| C106 | 10uF | RIGHT | Added: right copy | Fit | Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder |
| C107 | 100n / 25V | RIGHT | Added: right copy | Fit | Capacitor_SMD:C_0805_2012Metric |
| C108 | 100nF | RIGHT | Added: right copy | Fit | Capacitor_SMD:C_0805_2012Metric |
| C109 | 4.7uF | RIGHT | Added: right copy | Fit | Capacitor_SMD:C_0805_2012Metric |
| C110 | 100nF | RIGHT | Added: right copy | Fit | Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder |
| C111 | 1uF | RIGHT | Added: right copy | Fit | Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder |
| C112 | 10uF | RIGHT | Added: right copy | Fit | Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder |
| C113 | 330p DNP | RIGHT | Added: right copy | DNP | Capacitor_SMD:C_0805_2012Metric |
| C114 | 330p DNP | RIGHT | Added: right copy | DNP | Capacitor_SMD:C_0805_2012Metric |
| C115 | 330n | RIGHT | Added: right copy | Fit | Capacitor_THT:C_Rect_L7.2mm_W3.0mm_P5.00mm_FKS2_FKP2_MKS2_MKP2 |
| C116 | 100n / 100V | RIGHT | Added: right copy | Fit | Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder |
| C118 | 1nF | RIGHT | Added: right copy | DNP | Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder |
| C119 | 1nF | RIGHT | Added: right copy | DNP | Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder |
| D1 | DNP diode | LEFT | Preserved left stage | DNP | Diode_SMD:D_SOD-123 |
| D2 | DNP diode | LEFT | Preserved left stage | DNP | Diode_SMD:D_SOD-123 |
| D3 | DNP diode | LEFT | Preserved left stage | DNP | Diode_SMD:D_SOD-123 |
| D4 | DNP diode | LEFT | Preserved left stage | DNP | Diode_SMD:D_SOD-123 |
| D20 | 1N4148W | Main | Added in draft | Fit | Diode_SMD:D_SOD-123 |
| D21 | 1N4148W | Main | Added in draft | Fit | Diode_SMD:D_SOD-123 |
| D22 | 1N4148W | Main | Added in draft | Fit | Diode_SMD:D_SOD-123 |
| D23 | 1N4148W | Main | Added in draft | Fit | Diode_SMD:D_SOD-123 |
| D101 | DNP diode | RIGHT | Added: right copy | DNP | Diode_SMD:D_SOD-123 |
| D102 | DNP diode | RIGHT | Added: right copy | DNP | Diode_SMD:D_SOD-123 |
| D103 | DNP diode | RIGHT | Added: right copy | DNP | Diode_SMD:D_SOD-123 |
| D104 | DNP diode | RIGHT | Added: right copy | DNP | Diode_SMD:D_SOD-123 |
| J1 | STEREO LINE INPUT | Main | Existing / rewired | Fit | Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical |
| J14 | 24V INPUT | Main | Existing / rewired | Fit | DiscreteClassD:Power_Input_2_SMD |
| J15 | LEFT SPEAKER | LEFT | Preserved left stage | Fit | Connector_Molex:Molex_KK-396_A-41791-0002_1x02_P3.96mm_Vertical |
| J115 | RIGHT SPEAKER | RIGHT | Added: right copy | Fit | Connector_Molex:Molex_KK-396_A-41791-0002_1x02_P3.96mm_Vertical |
| L6 | CSAD0660-100M | LEFT | Preserved left stage | Fit | DiscreteClassD:CSAD0660-100M |
| L106 | CSAD0660-100M | RIGHT | Added: right copy | Fit | DiscreteClassD:CSAD0660-100M |
| Q5 | DMN6070SY | LEFT | Preserved left stage | Fit | Package_TO_SOT_SMD:SOT-89-3 |
| Q6 | DMN6070SY | LEFT | Preserved left stage | Fit | Package_TO_SOT_SMD:SOT-89-3 |
| Q7 | DMN6070SY | LEFT | Preserved left stage | Fit | Package_TO_SOT_SMD:SOT-89-3 |
| Q8 | DMN6070SY | LEFT | Preserved left stage | Fit | Package_TO_SOT_SMD:SOT-89-3 |
| Q105 | DMN6070SY | RIGHT | Added: right copy | Fit | Package_TO_SOT_SMD:SOT-89-3 |
| Q106 | DMN6070SY | RIGHT | Added: right copy | Fit | Package_TO_SOT_SMD:SOT-89-3 |
| Q107 | DMN6070SY | RIGHT | Added: right copy | Fit | Package_TO_SOT_SMD:SOT-89-3 |
| Q108 | DMN6070SY | RIGHT | Added: right copy | Fit | Package_TO_SOT_SMD:SOT-89-3 |
| R1 | 10R | LEFT | Preserved left stage | Fit | Resistor_SMD:R_0805_2012Metric |
| R2 | 47k | LEFT | Preserved left stage | Fit | Resistor_SMD:R_0805_2012Metric |
| R3 | 10R DNP | LEFT | Preserved left stage | DNP | Resistor_SMD:R_0805_2012Metric |
| R4 | 10R | LEFT | Preserved left stage | Fit | Resistor_SMD:R_0805_2012Metric |
| R5 | 47k | LEFT | Preserved left stage | Fit | Resistor_SMD:R_0805_2012Metric |
| R6 | 10R DNP | LEFT | Preserved left stage | DNP | Resistor_SMD:R_0805_2012Metric |
| R7 | 10R | LEFT | Preserved left stage | Fit | Resistor_SMD:R_0805_2012Metric |
| R8 | 47k | LEFT | Preserved left stage | Fit | Resistor_SMD:R_0805_2012Metric |
| R9 | 10R DNP | LEFT | Preserved left stage | DNP | Resistor_SMD:R_0805_2012Metric |
| R10 | 10R | LEFT | Preserved left stage | Fit | Resistor_SMD:R_0805_2012Metric |
| R11 | 47k | LEFT | Preserved left stage | Fit | Resistor_SMD:R_0805_2012Metric |
| R12 | 10R DNP | LEFT | Preserved left stage | DNP | Resistor_SMD:R_0805_2012Metric |
| R13 | 10R DNP | LEFT | Preserved left stage | DNP | Resistor_SMD:R_1206_3216Metric |
| R14 | 10R DNP | LEFT | Preserved left stage | DNP | Resistor_SMD:R_1206_3216Metric |
| R15 | 10R / 1W | LEFT | Preserved left stage | Fit | Resistor_SMD:R_2512_6332Metric |
| R20 | 91k2 / 0.1% | Main | Added in draft | Fit | Resistor_SMD:R_0805_2012Metric |
| R21 | 10k / 0.1% | Main | Added in draft | Fit | Resistor_SMD:R_0805_2012Metric |
| R22 | 32k2 / 0.1% | Main | Added in draft | Fit | Resistor_SMD:R_0805_2012Metric |
| R23 | 10k / 0.1% | Main | Added in draft | Fit | Resistor_SMD:R_0805_2012Metric |
| R24 | 10k | Main | Added in draft | Fit | Resistor_SMD:R_0805_2012Metric |
| R25 | 10k | Main | Added in draft | Fit | Resistor_SMD:R_0805_2012Metric |
| R26 | 10k / 0.1% | Main | Added in draft | Fit | Resistor_SMD:R_0805_2012Metric |
| R27 | 49k9 / 0.1% | Main | Added in draft | Fit | Resistor_SMD:R_0805_2012Metric |
| R28 | 3k09 / 0.1% | Main | Added in draft | Fit | Resistor_SMD:R_0805_2012Metric |
| R29 | 47k | Main | Added in draft | Fit | Resistor_SMD:R_0805_2012Metric |
| R30 | 10k | Main | Added in draft | Fit | Resistor_SMD:R_0805_2012Metric |
| R31 | 100R | Main | Added in draft | Fit | Resistor_SMD:R_0805_2012Metric |
| R32 | 330R | Main | Added in draft | Fit | Resistor_SMD:R_0805_2012Metric |
| R33 | 330R | Main | Added in draft | Fit | Resistor_SMD:R_0805_2012Metric |
| R34 | 10k | Main | Added in draft | Fit | Resistor_SMD:R_0805_2012Metric |
| R35 | 1k DNP | Main | Added in draft | DNP | Resistor_SMD:R_0805_2012Metric |
| R36 | 47k | Main | Added in draft | Fit | Resistor_SMD:R_0805_2012Metric |
| R37 | 10k | Main | Added in draft | Fit | Resistor_SMD:R_0805_2012Metric |
| R38 | 100R | Main | Added in draft | Fit | Resistor_SMD:R_0805_2012Metric |
| R39 | 330R | Main | Added in draft | Fit | Resistor_SMD:R_0805_2012Metric |
| R40 | 330R | Main | Added in draft | Fit | Resistor_SMD:R_0805_2012Metric |
| R41 | 10k | Main | Added in draft | Fit | Resistor_SMD:R_0805_2012Metric |
| R42 | 1k DNP | Main | Added in draft | DNP | Resistor_SMD:R_0805_2012Metric |
| R101 | 10R | RIGHT | Added: right copy | Fit | Resistor_SMD:R_0805_2012Metric |
| R102 | 47k | RIGHT | Added: right copy | Fit | Resistor_SMD:R_0805_2012Metric |
| R103 | 10R DNP | RIGHT | Added: right copy | DNP | Resistor_SMD:R_0805_2012Metric |
| R104 | 10R | RIGHT | Added: right copy | Fit | Resistor_SMD:R_0805_2012Metric |
| R105 | 47k | RIGHT | Added: right copy | Fit | Resistor_SMD:R_0805_2012Metric |
| R106 | 10R DNP | RIGHT | Added: right copy | DNP | Resistor_SMD:R_0805_2012Metric |
| R107 | 10R | RIGHT | Added: right copy | Fit | Resistor_SMD:R_0805_2012Metric |
| R108 | 47k | RIGHT | Added: right copy | Fit | Resistor_SMD:R_0805_2012Metric |
| R109 | 10R DNP | RIGHT | Added: right copy | DNP | Resistor_SMD:R_0805_2012Metric |
| R110 | 10R | RIGHT | Added: right copy | Fit | Resistor_SMD:R_0805_2012Metric |
| R111 | 47k | RIGHT | Added: right copy | Fit | Resistor_SMD:R_0805_2012Metric |
| R112 | 10R DNP | RIGHT | Added: right copy | DNP | Resistor_SMD:R_0805_2012Metric |
| R113 | 10R DNP | RIGHT | Added: right copy | DNP | Resistor_SMD:R_1206_3216Metric |
| R114 | 10R DNP | RIGHT | Added: right copy | DNP | Resistor_SMD:R_1206_3216Metric |
| R115 | 10R / 1W | RIGHT | Added: right copy | Fit | Resistor_SMD:R_2512_6332Metric |
| TP1 | SW_A | LEFT | Preserved left stage | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP2 | HO_A | LEFT | Preserved left stage | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP3 | LO_A | LEFT | Preserved left stage | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP4 | SW_B | LEFT | Preserved left stage | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP5 | HO_B | LEFT | Preserved left stage | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP6 | LO_B | LEFT | Preserved left stage | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP7 | OUT_A | LEFT | Preserved left stage | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP8 | OUT_B | LEFT | Preserved left stage | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP9 | +24V | Main | Existing / rewired | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP10 | +12V_GD | Main | Existing / rewired | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP11 | PGND | Main | Existing / rewired | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP20 | +5V_A | Main | Added in draft | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP21 | VREF_2V5 | Main | Added in draft | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP22 | OSC_SQUARE | Main | Added in draft | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP23 | TRIANGLE_400K | Main | Added in draft | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP24 | AUDIO_L | Main | Added in draft | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP25 | PWM_L | Main | Added in draft | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP26 | L_DRIVE_P | Main | Added in draft | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP27 | L_DRIVE_N | Main | Added in draft | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP28 | ENABLE_L | Main | Added in draft | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP29 | AUDIO_R | Main | Added in draft | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP30 | PWM_R | Main | Added in draft | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP31 | R_DRIVE_P | Main | Added in draft | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP32 | R_DRIVE_N | Main | Added in draft | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP33 | ENABLE_R | Main | Added in draft | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP101 | SW_A | RIGHT | Added: right copy | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP102 | HO_A | RIGHT | Added: right copy | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP103 | LO_A | RIGHT | Added: right copy | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP104 | SW_B | RIGHT | Added: right copy | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP105 | HO_B | RIGHT | Added: right copy | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP106 | LO_B | RIGHT | Added: right copy | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP107 | OUT_A | RIGHT | Added: right copy | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| TP108 | OUT_B | RIGHT | Added: right copy | Fit | TestPoint:TestPoint_Pad_D1.5mm |
| U1 | OPA1656ID | Main | Existing / rewired | Fit | Package_SO:SOIC-8_3.9x4.9mm_P1.27mm |
| U2 | UCC27301ADRCR | LEFT | Preserved left stage | Fit | Package_SON:VSON-10-1EP_3x3mm_P0.5mm_EP1.65x2.4mm |
| U3 | OPA1656ID | Main | Existing / rewired | Fit | Package_SO:SOIC-8_3.9x4.9mm_P1.27mm |
| U4 | SN74LVC1G04DBVR | Main | Existing / rewired | Fit | Package_TO_SOT_SMD:SOT-23-5 |
| U5 | SN74LVC2G17DBVR | Main | Existing / rewired | Fit | Package_TO_SOT_SMD:SOT-23-6 |
| U6 | UCC27301ADRCR | LEFT | Preserved left stage | Fit | Package_SON:VSON-10-1EP_3x3mm_P0.5mm_EP1.65x2.4mm |
| U7 | TLV3602DGKR | Main | Added in draft | Fit | Package_SO:VSSOP-8_3x3mm_P0.65mm |
| U8 | TLV3602DGKR | Main | Added in draft | Fit | Package_SO:VSSOP-8_3x3mm_P0.65mm |
| U9 | SN74LVC1G04DBVR | Main | Added in draft | Fit | Package_TO_SOT_SMD:SOT-23-5 |
| U10 | SN74LVC2G17DBVR | Main | Added in draft | Fit | Package_TO_SOT_SMD:SOT-23-6 |
| U11 | TPS7A4901DGNR | Main | Added in draft | Fit | Package_SO:HVSSOP-8-1EP_3x3mm_P0.65mm_EP1.57x1.89mm |
| U12 | TPS7A4901DGNR | Main | Added in draft | Fit | Package_SO:HVSSOP-8-1EP_3x3mm_P0.65mm_EP1.57x1.89mm |
| U102 | UCC27301ADRCR | RIGHT | Added: right copy | Fit | Package_SON:VSON-10-1EP_3x3mm_P0.5mm_EP1.65x2.4mm |
| U106 | UCC27301ADRCR | RIGHT | Added: right copy | Fit | Package_SON:VSON-10-1EP_3x3mm_P0.5mm_EP1.65x2.4mm |

## Sources and remaining limits

- [TI TPS7A49 datasheet](https://www.ti.com/lit/ds/symlink/tps7a49.pdf): pin table, feedback voltage, capacitors, current rating.
- [TI OPA1656 datasheet](https://www.ti.com/lit/ds/symlink/opa1656.pdf): dual pin map, supply and input common-mode range.
- [TI TLV3602 datasheet](https://www.ti.com/lit/ds/symlink/tlv3602.pdf): dual pin map, supply/input limits, push-pull outputs.
- [TI SN74LVC1G04 datasheet](https://www.ti.com/lit/ds/symlink/sn74lvc1g04.pdf) and [SN74LVC2G17 datasheet](https://www.ti.com/lit/ds/symlink/sn74lvc2g17.pdf): pin maps and Schmitt thresholds.
- [Diodes 1N4148W datasheet](https://www.diodes.com/datasheet/download/1N4148W.pdf): fast switching diode, SOD-123 package. Symbol pin 1 is cathode, matching KiCad SOD-123 pad 1 convention.
- [Diodes DMN6070SY datasheet](https://www.diodes.com/datasheet/download/DMN6070SY.pdf): saved MOSFET characteristics. Physical package pin map still requires completion of verification if selected.
- Supplied `sources/ucc27301a.pdf`, `sources/DMTH6016LPS.pdf`, and `sources/CSAD0660.pdf` support existing output-stage parts; the original stage pin assignment was preserved, rather than silently redesigned.

No TPS7A4901 physical pin-number uncertainty was found. The user's alternative DRB custom symbol contains additional exposed-pad contact numbers; it was not used or assumed interchangeable with DGN. The DGN copy uses the verified mapping above. The two engineering decisions at the beginning remain unresolved. The completed schematic, final ERC and final PDF must be issued after those decisions and verification of the selected MOSFET map. Exact film/filter capacitor parts, effective ceramic capacitance, thermal design, output power, oscillator startup, bootstrap behavior, and final dead time remain hardware/component-release checks.

## Resume implementation

The generator is saved here as `build_stereo.py`; it uses the preserved baseline and writes to `stereo-draft` when invoked with `--draft`. Do not run it on a subsequently manually edited design. Accepted supply choices are `--opa-rail +12V_GD` or `--opa-rail +5V_A`; accepted MOSFET choices are `--mosfet DMN6070SY` or `--mosfet DMTH6016LPS`. The default OPA_SUPPLY_PENDING is deliberately incomplete. Before applying a final choice, verify the selected MOSFET datasheet pins, revise the text for that decision, and re-run ERC, independent netlist verification and PDF inspection. This report describes the pending draft, not an approved final design.

# Mono Class-A — 40 V single-supply revision, 2026-10-06

The output stage remains two upper 2SC5198 emitter followers over two independently controlled 2SC5198 current sinks. The external supply is now J3 pin 1 +40 V, pin 2 GND. This is an amplifier schematic only; the PCB and project settings were preserved. The live user-edited schematic was backed up in `before-single-supply/`, and its retained component UUIDs, placement and footprints were checked.

## Changes

- Former +20 V rail becomes +40 V; former -20 V rail becomes GND. AMP_OUT and PRE_CAP rest at approximately 20 V DC.
- R32/R33, each 2k2 / 0.5 W / 1%, form VREF_20V. C8 is now 1000u / 50 V and C9 100n / 63 V, both from VREF to GND. VREF serves input and feedback references only; speaker and current-sink currents return to GND.
- R1 returns to VREF. Input coupling C1 remains 2u2 film / 63 V. The former DC-bypass resistor R2 and its local wiring were removed so a ground-referenced source cannot bypass the necessary level separation.
- C4 feedback return moves to VREF; its value is now 470u / 50 V bipolar. Audio gain remains 20 V/V, with DC gain approximately unity about VREF.
- C6/C7 are the local 40 V supply bypass: 470u / 63 V and 100n / 63 V. R10 changes from 9k1 to 18k to retain approximately 2 mA diode-reference bias when returning to supply GND.
- C10 is a polarized 4700u / 50 V speaker coupling capacitor after the existing inductor/damping network. Its positive terminal faces the amplifier. Feedback and Zobel remain before the coupling capacitor. R34, 10k, defines the disconnected speaker-side DC potential and provides capacitor discharge through the amplifier when powered.
- Restored the intended Q5 collector-to-common-mirror-base connection. The saved baseline had one ERC input-not-driven error at Q4 base; this link also restores the discrete current mirror's diode-connected reference transistor.

## First-pass calculations

- Divider current: 40/4400 = 9.09 mA. Each divider resistor dissipates 0.182 W. Reference Thevenin resistance is 1.1k; 1000u gives about 1.1 s reference settling time constant. Input bias current and resistor tolerance produce a small midpoint deviation; measure TP16.
- Speaker high-pass corner: 1/(2*pi*8*4700u) = 4.23 Hz. A 10k bleed has negligible effect on an 8-ohm load. Unloaded output-capacitor discharge through the bleed is approximately 47 s while the amplifier output can provide a return; powered-off decay depends on rail/reference decay and device conduction.
- Set sink current to approximately 2 A total: 220 mV across each R19/R20 and approximately 540 mV across shared R21. Thermal tracking, device spread and sharing remain bench requirements. Sink sensing, ballast and adjustment values are unchanged.
- Output-stage idle rail power remains approximately 40 V * 2 A = 80 W, around 19–20 W per power device plus resistor losses. Driver/front-end and reference-divider power are additional.
- Estimated 8-ohm output remains approximately 12–15 W at a stiff 40 V supply. At 15 W the speaker demand is 15.49 V peak / 1.94 A peak; upper bank current peaks near 3.94 A. Conservative beta=35 requires roughly 113 mA output base drive. Driver/VAS headroom remains the same as the previous translated ±20 V circuit. These are estimates, not measured ratings.
- Supply, signal and power transistor pin mappings remain as previously verified. C10 positive at PRE_CAP and negative at SPK_OUT is verified against the exported netlist. Supply electrolytic and reference capacitor polarities and ratings were checked. The feedback capacitor is explicitly bipolar.

## Verification and limits

Baseline ERC: 1 error, 0 warnings. Final ERC: 0 errors, 0 warnings. All 52 connectivity/pin/preservation checks pass; the board, project and preferences match the start-of-revision hashes. Existing retained component UUIDs, positions and footprints were preserved except the explicitly converted two-pin J3. The final KiCad PDF was rendered and inspected.

Compensation, 10-ohm base stoppers, current setting and output inductance remain TUNE/TBC. Verify startup/shutdown thump, reference settling, output-capacitor charging/reverse transients, hot DC SOA, thermal current sharing and load stability before layout/build qualification. No simulation, bench qualification, heatsink design, PSU design or PCB work was performed.

Manufacturer pin/rating references remain in the archived engineering note and the project transistor symbols: Toshiba 2SC5198, 2SC4793, 2SA1837; onsemi KSC1845 and KSA992. No transistor or footprint substitutions were made.

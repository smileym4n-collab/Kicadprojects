# InputSwitch schematic review - 1 October 2026

The requested controller is implemented as five schematic sheets. KiCad 10.0.5 ERC reports **0 errors and 0 warnings**. Independent netlist checks pass **151 assertions**, including contact states and isolation, and **101 component footprint references** resolve with complete numbered-pad parity.

This is a schematic implementation and static review, not a fabrication or bench sign-off. The retained ULN2003A/5 V G6K combination has unresolved pickup margin. The PCB and project settings are byte-for-byte unchanged; the existing PCB does not represent this new circuit.

## Review of the starting circuit

The starting schematic had 37 ERC errors and one warning. Most were the unconnected MCU/relays or undriven supply declarations. These are recorded in `original-2026-10-01/baseline-erc.txt`.

Comparison with [ESP P239, Figure 1](https://sound-au.com/project239.htm):

| Original project block | Finding and disposition |
|---|---|
| U1A, R7 100k, R6 1k, C5 33u | Useful AC gain stage, nominal gain 101 and unity DC gain. Retained in principle, independently for L and R. |
| R1/R2 10k and C2 47n | Original stereo summing tap: loads both sources and can cancel opposite-phase signals. Replaced by separate high-impedance sensing taps. |
| D4 5.1 V, R9 2k2, C8 33u | Useful bias/reference principle. Recreated separately on isolated rails. |
| U1B, R13 10k, R12 100k | Useful threshold detection principle. Retained with modest comparator hysteresis and an isolated logic interface. |
| R5 10 Ω between GNDD and GND | A real conductive audio/control connection. Removed; not an isolation barrier. |
| D2, R3, C6, R8, Q1 | Long analogue timer and MOSFET relay drive removed. MCU performs qualification and timeout. |
| Q2, C7, R10/R11, D5 | Analogue lockout removed; firmware must provide post-switch and post-power-off blanking. |
| Existing K1 and mains connector J5 | Removed from the low-voltage schematic. New J10 carries only G7L coil connections. |
| Original R4 560 Ω | Was in series with the relay coil supply. This is not P239's indicator branch and would reduce coil voltage substantially. Removed. |
| Original K2/K3/K4 | Unwired symbols labelled DC3. Inventory reports DC5 parts. New K1/K2/K3 specify G6K-2P-Y DC5. |

## Final circuit

**Audio:** J1 Reference L, J2 AV L, J3 Reference R, J4 AV R, J5 P3A L, J6 P3A R. Every audio connector uses pin 1 signal, pin 2 its own return. All remain JST XH board connectors with external isolated RCAs and short shielded leads. There is no amplifier, capacitor, resistor or analogue switch in series with the through audio path.

K1 and K2 use one pole each for signal and one for return. The project-local relay symbol separates contacts and coil for readability while preserving the original manufacturer pin numbering. [Omron's G6K drawing](https://omronfs.omron.com/en_US/ecb/products/pdf/en-g6k.pdf) establishes:

| Relay pins | Function |
|---|---|
| 1 / 8 | Coil positive / low-side drive |
| 3 / 6 | Pole commons |
| 2 / 7 | Normally closed: Reference on K1/K2; selected signal on K3 |
| 4 / 5 | Normally open: AV on K1/K2; output's own return on K3 |

K3 disconnects each selected signal before shorting the P3A input to its corresponding return. It never deliberately shorts the source output. All coils off gives Reference pass-through, with the mains command off.

**Power:** external isolated regulated 12 V, preferably within ±2%, at least 0.5 A. J7 pin 1 positive, pin 2 control GND. T500mA fuse, SS14 reverse blocking diode, SMBJ13A transient clamp, input bulk and bypass capacitors; [R-78E5.0-0.5 buck module](https://recom-power.com/pdf/Innoline/R-78E-0.5.pdf) generates 5 V. TP1/TP2/TP3 expose protected 12 V, 5 V and GND. Three nominal relay coils total about 63 mA at full rated coil voltage; allow 100 mA on 5 V. Allow roughly 0.3 A input overall with margin for startup; actual isolated-module low-load losses need measurement.

U3 and U4 are both **ULN2003A**, as explicitly requested after the drive-margin review. Their COM connections are +5 V and +12 V respectively. K1/K2 share only MCU input control; their output channels are separate. Spare driver inputs are grounded and genuinely unused outputs carry no-connect markers. [ST ULN2003A datasheet](https://www.st.com/resource/en/datasheet/uln2001.pdf).

**MCU and front panel:** [ATtiny412 SOIC-8 pinout](https://ww1.microchip.com/downloads/en/DeviceDoc/ATtiny212-412-DataSheet-DS40001911B.pdf) checked against the schematic. A single [SN74LVC1G04DBV](https://www.ti.com/lit/ds/symlink/sn74lvc1g04.pdf) derives the Reference LED from the source command; AV LED uses that command directly. LED currents are limited by 4k7 resistors. These indicate commands, not verified contact positions.

| Physical pin | Port | Assignment |
|---|---|---|
| 1 / 8 | VDD / GND | 5 V / control GND |
| 6 | PA0 | UPDI only; J8 pin 1 |
| 4 | PA1 | SOURCE_AV: 0 Reference, 1 AV |
| 5 | PA2 | MUTE: 1 energises K3 |
| 7 | PA3 | AUDIO_PRESENT_N: low means recent audio |
| 2 | PA6 | P3A_ON: 1 energises G7L |
| 3 | PA7 | TOGGLE_AV: 0 Reference, 1 AV |

J8 pins 1/2/3 are UPDI/target 5 V/GND. Use target-powered programming; do not back-power the board through J8. J9 pins 1/2/3 go to Reference throw/common/AV throw. R2 pulls an open cable toward Reference. R1/C7 filter edges; firmware still debounces for at least 20 ms. GPIO pulldowns hold selector, mute and mains commands low through reset.

## Isolated sensing and calculations

Each channel has its own [R12P12S/P isolated converter](https://recom-power.com/pdf/Econoline/RxxPxx.pdf), LM358 and [VO617A-3 optocoupler](https://www.vishay.com/docs/83430/vo617a.pdf). The module is the standard /P pinout, **not /X2**: 1 input+, 2 input-, 5 isolated return, 7 output+. No pin 6. The local footprint follows the standard pin positions and body envelope; perform the usual physical fit check before layout approval.

Each isolated return connects only to its own selected audio return. No intentional capacitor bridges the isolation barrier. Real modules and optocouplers have small parasitic capacitance, so galvanic isolation does not imply zero RF/common-mode coupling.

The 1k2 / 0.5 W module preload provides about 10 mA at 12 V. A 100 Ω / 47 µF RC filter supplies the amplifier/reference; its pole is 33.9 Hz. Zener reference and gain-bypass capacitors are local to that audio domain. Preload dissipation is nominally 0.12 W; allow more for the unregulated output rise. Total output capacitance is below the converter's published limit.

The sensing tap is 100 nF film, 100 kΩ series, 470 kΩ bias. Nominal input impedance is approximately 570 kΩ, with a 2.79 Hz coupling pole. Amplifier AC gain is 101 with a 4.82 Hz gain-bypass pole; including input attenuation gives 83.3 midband gain. Comparator threshold with feedback gives approximately **4.3 mVrms nominal** activation. LM358 bias/offset, zener voltage, bandwidth and saturation recovery affect this. This is a calculated starting point; qualify actual sensitivity across the audio band. At 2 Vrms the detector intentionally clips, outside the through path. When unpowered, input clamping can reduce the sensing-branch impedance toward 100 kΩ; the passive bypass is therefore not a completely unloaded wire.

BC549 switches each optocoupler LED at roughly 5-7 mA nominal. The optocoupler outputs combine through separate 1 kΩ resistors into R10/C8 and PA3, with approximately 103 ms nominal release time constant. This is a recent-audio envelope, not the ten-minute timer. A single click may assert it briefly; only firmware persistence qualification rejects that event. Independent channels avoid L/R cancellation.

## Remaining limits and decisions

1. **G6K pickup margin is not guaranteed.** A standard DC5 G6K must operate by 4.0 V at 23°C. ULN2003A is a Darlington driver with a significant saturation drop. A conservative 1.1 V screening drop leaves 3.9 V even from exactly 5 V, before regulator tolerance or temperature. The datasheet does not give a production maximum specifically at the roughly 20 mA coil current. This does not prove that your relays will fail, but clean ERC cannot qualify them. Both ULN2003A devices were retained at your instruction; test pickup at low supply and elevated coil temperature. This remains an electrical sign-off blocker.
2. **Two independent selector relays cannot guarantee source-return isolation throughout a transition if the P3A joins L/R returns externally.** A temporary K1=AV/K2=Reference state can bridge the source grounds through that shared return. Static states are isolated; this transition is reproduced by the connectivity test. Muting signals cannot prevent it. Strict all-times isolation would require an approved change to the return-switching arrangement. Keep external RCA shells insulated and audit existing earth/HDMI/preamp connections too.
3. **Unpowered Reference bypass trades away fail-muted behaviour.** When controller power collapses K3 releases. The P3A may still contain stored energy, or be manually powered, so pop-free shutdown is not guaranteed. There is no hardware power-fail hold-up/sequencer in this revision.
4. **Supply protection is limited.** The TVS limits large transients; it does not clamp within the isolated converters' 10.8-13.2 V recommended range or provide sustained overvoltage cutoff. Verify the protected 12 V rail under load. Use the specified regulated adapter. Fuse nuisance blowing/inrush, converter ripple injection and EMC remain bench/layout checks.
5. **Assembly details remain to be finalised before PCB work.** All symbol-to-footprint numbered pads match, but that is not a complete dimensional BOM audit. Confirm stocked transistor manufacturer/pinout, actual film/electrolytic body sizes, fuse-holder mechanical drawing and connector harness orientation against purchased parts. The Bulgin FX0457 online orientation descriptions are inconsistent; its provisioned footprint is not a mechanical release. No PCB placement, routing or DRC was performed.
6. **G7L and mains assembly are external.** J10 contains only coil supply and low-side return. [G7L-2A-T DC12](https://assets.omron.com/m/174e816c78be0fba/original/G7L-Datasheet.pdf) is about 158 mA at rated 12 V, with nominal 75 Ω coil. Allow ULN drop, hot pickup voltage and diode-slowed release in testing. Transformer inrush/contact life, fusing, shrouds, strain relief and protective earth need a separate chassis review. No speaker outputs are switched.

## Firmware contract, not implemented here

On reset initialise P3A_ON low, assert MUTE promptly, debounce the toggle and select the requested source while muted. Enable brownout detection (4.2 V setting) and watchdog. Ignore detector startup settling, then qualify roughly 500 ms of sustained recent audio. Use envelope/pulse persistence rather than assuming the detector must stay continuously low for every waveform.

Source change: mute, wait 75 ms, change K1/K2, wait 150 ms, release mute only if the amplifier state permits it. Power-on: mute before mains, energise G7L, wait approximately 2 s, then release mute. Power-off: ten minutes without qualified audio, mute, wait 200 ms, release G7L. Add a configurable post-off lockout (start with P239's approximately ten-second intent) and reset detection qualification after every source/power transition. Confirm all timings on the real amplifier. Firmware and bench tests have not been performed.

## Files and verification

Changed: `InputSwitch.kicad_sch`. Added: `Power.kicad_sch`, `Control.kicad_sch`, `Detector_L.kicad_sch`, `Detector_R.kicad_sch`, local symbol/footprint libraries and tables, review/parts documents, verification helpers and PDF export. Existing mounting-hole symbols remain represented; their PCB placements are untouched.

Preserved byte-for-byte: `InputSwitch.kicad_pcb` and `InputSwitch.kicad_pro`. Original files and hashes are in `review/original-2026-10-01/`. No ERC exclusions or project check settings were added. No-connect markers are restricted to unused ULN outputs and the inverter's internally unconnected pin.

Evidence: `final-erc.txt`, `final-netlist.xml`, `connectivity-checks.json`, `footprint-pad-checks.json`, and `output/pdf/InputSwitch-schematic.pdf`. All five exported pages were visually reviewed. Schematic connectivity checked; calculations performed; no circuit simulation, firmware validation, layout verification, bench or thermal validation, or production approval.

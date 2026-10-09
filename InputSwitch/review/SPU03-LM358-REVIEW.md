# SPU03 conversion and LM358 suitability — 1 October 2026

The schematic now uses two owned Mean Well SPU03L-05 modules, one per detector. U5/U7 remain LM358N in DIP-8. U6/U8 remain VO617A-3 optical interfaces. The audio and control sheets, PCB and project settings were preserved byte-for-byte relative to `pre-spu03-2026-10-01/`. That snapshot is the preservation baseline for this change; the PCB had already changed since the earlier original snapshot.

## Implemented changes

| References | Final selection / purpose |
|---|---|
| U10, U11 | SPU03L-05, supplied from control +5V; independently isolated nominal 5V outputs |
| R20, R40 | 30R, 3W, 1%, flameproof preload, approximately 167mA and 0.83W each at 5V |
| R21/R41, C21/C41 | Retained 100R / 47u supply filters, nominal 33.9Hz pole |
| R22/R42, new R34/R54 | 3k3 / 1k local bias divider, approximately 1.1V; replaces D20/D40 5.1V zeners |
| R23/R43, R24/R44 | 470k series / 100k bias, approximately 570k sensing impedance |
| R29, R49 | 2M2 hysteresis; reduced positive feedback preserves silent-state release margin at lower voltage |
| R30, R50 | 4k7 transistor base drive |
| R32, R52 | 390R optocoupler LED feed |
| U1 | RECOM R-78B5.0-2.0, 5V / 2A buck with its correct larger footprint |
| F1 / external adapter | T1A fuse; isolated regulated 12V adapter rated at least 1A |

## VERIFIED OK — LM358 retained

The [TI LM358 datasheet](https://www.ti.com/lit/ds/symlink/lm358.pdf) and [TI application guidance, sections 5 and 6](https://www.ti.com/lit/an/sloa277b/sloa277b.pdf) support low-voltage operation with adequate input/output headroom. It is not rail-to-rail. TI explicitly explains that, in this device's comparator configuration, common-mode is determined by the **less positive input**. The fixed low threshold therefore keeps the comparator in a valid operating region even when the amplifier output saturates high. This is why an additional output attenuator is unnecessary.

The design acceptance window is isolated raw supply 4–6V, filtered supply 3.6–6V, audio up to 2Vrms sine / 2.83V peak, and the stocked LM358's 0–70°C ambient range. These are design/test limits, not a claim that the unregulated converter guarantees them under all conditions.

Calculations using resistor tolerance and explicit offset/bias allowances give an amplifier input range of approximately 0.25–1.41V at the lowest filtered supply, versus the conservative upper common-mode limit of 1.6V. Comparator threshold margin is over 0.81V. Worst screened silent-state release margin is about 22mV after offset allowances; no static latch is predicted. DC gain remains one, so amplifier input offset is not multiplied by 101 at DC.

The revised midband gain from the audio connector is 17.7. Nominal trigger is about **4.2mVrms**; the simplified DC tolerance screen spans about 1.5–7mVrms before gain tolerance, bandwidth and recovery effects. Input coupling pole remains 2.79Hz; gain-bypass pole is 4.82Hz. This is suitable for a quiet-audio presence detector, not a calibrated level meter. Legacy LM358 limits are mostly characterised at supplies of 5V and above; operation below that is supported by TI guidance but the exact sensitivity is still a bench measurement.

BC549 provides the optocoupler LED current rather than loading the LM358 directly. LED current is roughly 9mA nominal and approximately 5–13mA over the screening window, dependent on LED/transistor drops. Collector loads on the control side remain very small. LM358 saturation recovery and slew rate can reduce sensitivity to high-frequency-only tones; test across the audio band. Firmware qualification, startup blanking and the 103ms envelope remain necessary.

## Inventory comparison

Live inventory records: LM358 ID389, two DIP-8, unreserved, Opamp drawer; MCP6002 ID13, five DIP-8, unreserved, Opamps drawer; TLV9362 ID24, seven SOIC-8, unreserved, SMD Parts. No stock was reserved or consumed.

[MCP6002](https://ww1.microchip.com/downloads/en/DeviceDoc/MCP6001-1R-1U-2-4-1-MHz-Low-Power-Op-Amp-DS20001733L.pdf) is a credible low-voltage alternative, with rail-to-rail input/output and low bias current. Its operating supply ceiling is 6V and it offers less overvoltage margin on an unregulated supply. Its comparator/saturation behaviour would also need qualification. [TLV9362](https://www.ti.com/lit/ds/symlink/tlv9362.pdf) is a faster SOIC option; changing package/device is unnecessary here. Neither alternative was substituted. Keeping the LM358s avoids an unnecessary part change while meeting this detector's intended function.

## IMPORTANT — module loading, power and heat

[Mean Well SPU03 datasheet](https://www.meanwell.com/Upload/PDF/SPU03/SPU03-SPEC.PDF): SPU03L-05 is **5V input only**, unregulated nominal 5V output, 600mA capacity. The output-current range begins at 60mA, but load regulation is characterised from 20% load. The preloads keep the modules above 120mA within the design window, including the screening tolerance/temperature allowance. They are on the raw outputs, not behind the 100R filters. Input pins are 1+/2−; isolated output pins 7+/5−. The local footprint uses the published pin spacing and body size. Confirm body alignment against an owned module before PCB release, since the horizontal body-to-pin offset is not explicitly dimensioned.

The pair of preload resistors dissipates **1.67W nominal**, up to about 2.49W in the conservative voltage/tolerance screen. Select Vishay PR03 copper-lead 3W, 30R, 1% or an explicitly checked equivalent. The provision is 17mm × 6mm body envelope, 25.4mm lead pitch; PR03 maximum body is 16.7mm × 5.2mm. [PR03 datasheet](https://www.vishay.com/docs/28729/pr010203.pdf). At its stated 60K/W thermal resistance, the nominal 0.83W suggests around 50°C rise; this depends strongly on mounting. Keep clear of electrolytics, allow ventilation and measure enclosed temperatures. The larger wattage rating does not eliminate heat.

The original 500mA buck is inadequate for the conservative load budget. [R-78B5.0-2.0](https://recom-power.com/pdf/Innoline/R-78B-2.0.pdf) supplies 2A with 6.5–32V input, pins 1 input / 2 GND / 3 output. A project-local footprint follows its 11.5 × 8.5mm body, 2.54mm pin pitch and 1.2mm edge-to-pin offset; height is 17.5mm. The bundled library used a different 2.0mm edge offset, so it was not assigned. External capacitance is comfortably below its 820uF limit. The existing input bulk and local bypassing remain; EMC compliance of the assembled board is not claimed.

Allow **1.1A on 5V** and approximately **0.8A at the protected 12V input** for planning. This includes two module no-load losses, preload/detector demand, control loads and the G7L coil, with conservative conversion-loss assumptions. Mean Well does not supply a guaranteed low-load current curve, so these are estimates, not certified maxima. The 2A buck provides margin; use a 12V adapter of at least 1A and check startup/inrush, T1A fuse behaviour, SS14 temperature and rail droop. Actual standby power exceeds the 1.67W resistor dissipation because of converter and controller losses.

## Checks and remaining bench work

- KiCad ERC: **0 errors, 0 warnings**, with no added exclusions.
- **157 connectivity assertions** passed, including domain separation, contact states and UPDI.
- **42 value/electrical screening assertions** passed; these include 34 component-selection checks and eight operating-margin/budget checks.
- **101 footprint references** resolved with numbered-pad parity. Power and detector PDF pages visually reviewed.
- Source preservation checked against the pre-change snapshot. No PCB layout or firmware work.

Before calling the hardware proven, measure both raw/filtered isolated rails, minimum-load behaviour, startup and silent settling; test detection at 20Hz, 100Hz, 1kHz, 10kHz and 20kHz; check 2Vrms overload recovery; confirm no false triggers from relay/converter switching; and measure supply current and hot resistor/module temperatures inside the enclosure.

Existing blockers remain: ULN2003A/G6K pickup margin, temporary external return bridging during staggered selector relay movement, and unpowered pass-through not guaranteeing a muted power failure. Clean ERC does not resolve them. No circuit simulation, bench/thermal qualification or fabrication approval is claimed.

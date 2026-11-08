# RELAYVOL

Open [RELAYVOL.kicad_pro](RELAYVOL.kicad_pro) in KiCad 10 and open its schematic. Keep [RELAYVOL.kicad_sym](RELAYVOL.kicad_sym) and [sym-lib-table](sym-lib-table) beside the project. The project-local symbol divides each physical G6K relay into a left contact, a right contact and a coil. All three units share one footprint and reference designator.

The schematic is for a 5 V proof-of-concept attenuator. The 128 settled relay states were calculated and the schematic passed ERC and a pin-by-pin netlist audit. Hardware verification is pending.

- [Bill of materials](BOM.md)
- [Purchasing and stock](PURCHASING.md)
- [Resistor calculations, 128-state truth table and loading results](ATTENUATION.md)
- [KiCad 10.0.5 ERC report](ERC.rpt)

## Passive audio path

K1 to K7 switch 0.5, 1, 2, 4, 8, 16 and 32 dB pads, respectively. Each pole's COM is the stage output. With the coil off, COM touches NC and connects the shunt resistor from output to GNDA. The signal then passes through the series resistor. With the coil on, COM touches NO, connecting the stage input straight to the stage output and disconnecting the shunt. The same mechanism switches both channels. The only common audio connection is the return.

For a target loss A in dB, the voltage ratio is `k = 10^(−A/20)`. With downstream load Z = 10 kΩ, the ideal values are `Rseries = Z × (1 − k)` and `Rshunt = Z × k / (1 − k)`. These make each inserted stage look like 10 kΩ to the preceding stage. The fitted E96 pairs use one 0.1% thin-film resistor per position. The rounded values change the nominal step sizes.

For bench use, fit R29 and R30 as 10 kΩ and use a high-impedance instrument. For a known amplifier input resistance Ramp above 10 kΩ, choose a single resistor per channel using `Rterm = 1 / (1 / 10000 − 1 / Ramp)`, with resistances in ohms. With 47 kΩ inputs the exact value is 12.7027 kΩ. Use 12.7 kΩ, 0.1%, which gives an effective 9.9983 kΩ load. A 10 kΩ amplifier already provides the termination. An amplifier below 10 kΩ cannot reach a 10 kΩ effective load by adding a parallel resistor. Include any measuring instrument that remains connected in parallel when calculating the load.

Use a low-impedance, DC-free or AC-coupled source. At 2 Vrms into approximately 10 kΩ, total resistive dissipation is about 0.4 mW per channel. The 0.125 W thin-film parts have ample power margin. The highest calculated output resistance is about 3.30 kΩ at the bench load, so source impedance and cable or amplifier capacitance should be included when measuring frequency response. Omron's low-level contact reference condition is 10 µA at 10 mV DC. Some contacts can see less current at low signal levels and high attenuation. Check low-level continuity, noise, switching artefacts and channel separation on the prototype. [Omron G6K datasheet](https://components.omron.com/us-en/system/files/2026-05/datasheet_pdf/K106-E1.pdf)

## Assembly options and connectors

| Reference | Pin 1 | Pin 2 | Pin 3 |
|---|---|---|---|
| J1 power | Regulated +5 V | GND | — |
| J2 volume pot | +5 V, clockwise end | Wiper | GND, anticlockwise end |
| J3 UPDI | UPDI data | Target +5 V sense | GND |
| J4 left input | Left signal | GNDA | — |
| J5 right input | Right signal | GNDA | — |
| J6 left output | Left signal | GNDA | — |
| J7 right output | Right signal | GNDA | — |

| Build | Fit | JP1 and JP2 | Output at reset |
|---|---|---|---|
| Initial prototype | K1–K7 and their drivers | Bridge both | Ladder at maximum attenuation |
| With mute | K1–K8 and all drivers, including Q8, D8, R45 and R46 | Leave both open | J6/J7 signal pins grounded by K8 |

With K8 fitted, low on MUTE_CTRL grounds the outputs and high passes the ladder signal. R29/R30 are on the ladder side of K8, so grounding the outputs leaves the ladders terminated. The amplifier's parallel load joins them when K8 passes audio. If the jumpers are bridged with K8 fitted, K8 can ground the ladder outputs directly. Use one assembly option per board.

## MCU and volume input

U1 uses the user-approved wide SOIC-20 footprint, 7.5 × 12.8 mm nominal body and 1.27 mm lead pitch. Verify the physical package against the footprint before assembly. The stock record identified as SSOP-20 remains a separate package question. The following map uses the documented leaded ATtiny1616 pinout. [Microchip ATtiny1616 datasheet and package drawings](https://ww1.microchip.com/downloads/en/DeviceDoc/ATtiny1614-16-17-DataSheet-DS40002204A.pdf)

| Pin | Port | Function |
|---:|---|---|
| 1 | VDD | +5 V, C4 and C5 at the MCU |
| 2 | PA4 | RELAY_0_5DB, K1 |
| 3 | PA5 | RELAY_1DB, K2 |
| 4 | PA6 | RELAY_2DB, K3 |
| 5 | PA7 | RELAY_4DB, K4 |
| 6, 7 | PB5, PB4 | Unused |
| 8 | PB3 | MUTE_CTRL, optional K8 |
| 9 | PB2 | RELAY_32DB, K7 |
| 10 | PB1 | RELAY_16DB, K6 |
| 11 | PB0 | RELAY_8DB, K5 |
| 12–15 | PC0–PC3 | Unused |
| 16 | PA0/UPDI | J3 pin 1 |
| 17 | PA1/ADC0 AIN1 | VOL_ADC |
| 18, 19 | PA2, PA3 | Unused |
| 20 | GND | Digital return |

Use the internal oscillator and retain PA0 in UPDI mode. Use target-voltage sense on J3 pin 2 with the board powered from J1. R47 and C3 give a time constant of roughly 0.10–0.35 ms, including the wiper source resistance of a 10 kΩ pot. R48 pulls VOL_ADC low if the pot is disconnected. The ADC input is intended for the short internal wiring of a passive pot powered from J2. R47 limits transient injection and C3 filters the input. The header is a 0–5 V interface.

Use ADC0 with VDD as reference so slow supply changes track the pot voltage. Average ADC readings, add hysteresis around the 127 thresholds, and qualify state changes to limit chatter. The desired attenuation index is 127 at the anticlockwise end and 0 at the clockwise end. Gate pulldowns hold the relays off while the MCU pins are inputs. Initialise output latches low before enabling output direction. With K8 fitted, keep it off through startup and attenuation changes. Measure pickup, release and bounce with the flyback diodes fitted before setting the mute timing. Binary carries can change several contacts on one adjacent volume step.

## Coil supply and grounding

J1 takes regulated 5.0 V DC. Allow 0.5 A or more at the source and check the voltage at TP1 under an all-on relay load. The coil rating is 237 Ω and 21.1 mA typical at 23 °C. Seven coils draw approximately 148 mA and eight approximately 169 mA. At 5.25 V and −10% coil resistance, eight coils alone draw about 197 mA. The standard relay's must-operate limit is 4.0 V at 23 °C. C1 provides 220 µF bulk. C2 bypasses the incoming rail, C6 bypasses the local relay rail and C4/C5 decouple U1. [Omron G6K datasheet](https://components.omron.com/us-en/system/files/2026-05/datasheet_pdf/K106-E1.pdf)

Each 2N7002K is a low-side switch with a 330 Ω gate resistor and 100 kΩ gate pulldown. SOT-23 pins 1/2/3 are gate/source/drain. The stocked Multicomp Pro part is rated for 60 V VDS, ±20 V VGS and 300 mA continuous at 25 °C. Its published on-resistance table specifies 10 V drive. Its lower-gate-voltage data are typical, so verify pull-in and drain drop at 4.75 V supply and with warmed coils. For a same-pinout procurement option, Diodes Inc. specifies a maximum of 3 Ω at 4.5 V gate drive, equivalent to about 63 mV and 1.3 mW at 21.1 mA using that limit. D1–D8 use SOD-123 pin 1 cathode to +5 V and pin 2 anode to drain. Initial flyback current is approximately the preceding coil current. [Stock MOSFET datasheet](https://www.farnell.com/datasheets/4495380.pdf) · [Diodes Inc. 2N7002K](https://www.diodes.com/assets/datasheets/ds30896.pdf) · [1N4148W SOD-123 datasheet](https://www.vishay.com/docs/86356/1n4148w.pdf)

For layout, return the drivers and supply bypass currents to J1 ground without sharing their route with audio return currents. Join GNDA to GND at NT1 near the supply return. Check any additional connection between these returns through the enclosure, source, amplifier or programmer. TP1 and TP2 expose +5 V and GND.

## Pin and footprint verification

| Part | Verified assignment |
|---|---|
| K1–K8 | Pin 1 coil positive, 8 coil negative. Left COM/NC/NO 3/2/4. Right COM/NC/NO 6/7/5. Standard G6K-2P hole pattern has 5.08 mm row separation, 2.54 mm pitch along each row and eight 0.85 mm holes. |
| Stock G6K-2P-Y | Same electrical pin functions. Its intermediate pins lie at 3.2 and 5.4 mm from the end-pin datum and its end-pin spacing is 7.6 mm. This differs from the standard G6K-2P pattern. |
| U1 | KiCad ATtiny1616-S symbol and matching wide SOIC-20 footprint, pad 1 VDD and pad 20 GND. No exposed pad. |
| Q1–Q8 / D1–D8 | KiCad 2N7002K SOT-23 and 1N4148W SOD-123 symbols and matching footprints. |
| C1 | Rubycon ZLH, 8 mm body diameter, 3.50 mm pitch, pin 1 positive. |
| J1 / J2–J7 | JST XH 2.50 mm power input, and single-row 2.54 mm through-hole headers for control and audio. |
| Resistors and ceramics | 1608 and 2012 metric footprints, as itemised in the BOM. |

Sources for the mechanical assignments include [Omron G6K datasheet](https://components.omron.com/us-en/system/files/2026-05/datasheet_pdf/K106-E1.pdf), [JST XH series drawing](https://order.jst-mfg.com/InternetShop/app/pdf_show.php?kbn=1&key=eXH.pdf), [Rubycon C1 part data](https://www.digikey.com/en/products/detail/rubycon/35ZLH220MEFC8X11-5/3563385) and [Samsung C5 component data](https://product.samsungsem.com/mlcc/CL21A475KAQNNN.do).

## Validation

KiCad 10.0.5 reports 0 errors and 0 warnings with the project defaults. An independent comparison of the exported netlist verified the exact node membership of 70 nets, including the eight intentionally unused MCU pins. The audit matched all 256 physical pins to pads across 91 footprints and checked the five DNP references. The analogue model uses the values exported from this schematic. The PCB and physical operating behaviour remain to be verified on a prototype.

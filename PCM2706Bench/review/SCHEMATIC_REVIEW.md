# PCM2706Bench schematic review - 27 October 2026

The schematic has been corrected and checked against TI's PCM2706C datasheet, including all 32 IC pins. It is suitable for proceeding with the remaining assembly decisions and a PCB update/review. It is **not yet fabrication approved**: the supplied WH148 potentiometer has a user-confirmed first-gang direction but unverified second-gang direction and physical fit, J5 has conflicting part metadata, and component ratings/crystal details remain unspecified. No bench, thermal, USB-compliance or PCB-layout verification has been performed.

## Changes made

| Item | Original finding | Saved correction |
|---|---|---|
| R4, USB pull-up | 1k5 pulled up the D-minus path, giving the wrong USB speed identification | Connected to the D-plus path between R11 and IC2 pin 1; supplied from VDD |
| IC1 internal supplies | All four internal supply outputs were joined by the `3V3` labels | Four separate nets: VCCP/C11, VDD/C12, VCCL/C13 and VCCR/C14, following TI's bus-powered arrangement |
| RV1 | Signal on 1/4 and ground on 3/6; reversed relative to the conventional endpoint assignment | Ground on 1/4, signal on 3/6, wipers 2/5 to J4; no symbol pin numbers changed |
| RV1 value | `10K LOG` did not describe the user's B-taper kit | `10k LINEAR (B)`; use the B10k device from the kit |
| FSEL | Undefined while a break-before-make toggle is between contacts, or when disconnected | Added R17, 100k to VDD, defaulting to analogue operation |
| IC1 FUNC3/DIN, pin 4 | Left open with internal pulldown | Explicit ground connection: no play/pause command in analogue mode and zero serial data into the internal DAC in I2S mode |
| Unused pins | Seven unmarked open pins caused ERC errors | Marked unused HID0/1/2, SSPND, CK and DT appropriately; FUNC3 grounded as above |
| Shield annotation | Modified GND power symbols named SHIELD caused a power-driver ERC error | Replaced those two symbols with ordinary SHIELD net labels; preserved the bead and separate shield net |
| Stray label | Dangling AMPVCC outside the page | Removed |
| Documentation | Mode, connector and pot conventions were not explicit | Added notes directly on the sheet, including the measured WH148 first-gang direction and remaining fit/second-gang checks |

Only the schematic was changed. Project settings, PCB file, existing footprint assignments and all embedded symbol pin mappings were preserved. Baseline schematic/project copies and hashes are under `baseline/`.

R17 uses a 2012 metric footprint. A suitable existing utility resistor is inventory item 241, KOA Speer RK73B2ATTE104J, 100k, 5%, 0.25W; the inventory lookup returned 77 available and zero reserved. Nothing has been reserved or deducted. Its approximate dissipation with FSEL held low is 0.11mW at 3.3V.

## Mode switch and output wiring

Use a **break-before-make SPDT ON-ON switch**, with common connected to **J1 pin 2**. A make-before-break switch would momentarily short VDD to ground.

| Switch connection | FSEL | Intended use |
|---|---|---|
| J1 2 to 1 | LOW | I2S output to an external DAC |
| J1 2 to 3 | HIGH | Internal DAC analogue output to an amplifier |
| Switch disconnected/between contacts | Pulled HIGH by R17 | Default analogue mode |

FSEL selects the digital pin functions; it is not a physical analogue output disconnect. Grounded DIN is intended to produce zero samples at the internal DAC in I2S mode. Switching transients are not qualified. Stop playback and mute the connected amplifier before changing mode; reconnect USB if a host/device fails to recover.

J5: **1 MCLK/SYSCK, 2 BCLK, 3 DATA, 4 LRCK, 5 GND, 6 GND**. In analogue mode, the DATA pin becomes S/PDIF and the clock pins become HID inputs. The header is usable as an I2S source only with FSEL LOW. It supplies no power to the DAC under test. Use a common ground, compatible 3.3V logic, a separately powered DAC, and short wiring. The external DAC must accept source-driven clocks; do not connect another clock master to these outputs. Long bench leads and load capacitance require signal-integrity checks; 22-ohm source resistors are already provided.

J4: **1 RIGHT, 2 GND, 3 LEFT**. RV1 controls only these analogue outputs. The I2S stream does not pass through the potentiometer.

The source supports 16-bit samples at 32, 44.1 and 48kHz, with BCLK = 64fs and MCLK = 256fs. At 48kHz these are 3.072MHz and 12.288MHz. The analogue full-scale output is approximately 1.8V peak-to-peak, or 0.64Vrms for a sine wave; it is not a 2Vrms source. Some amplifiers will therefore not reach their full rated output. Measure and calibrate the actual maximum level on the assembled unit.

## Potentiometer: required physical check

The supplied part was identified by the user as a Swpeet generic WH148 six-pin **B-taper linear** potentiometer. No authoritative drawing for that specific supplied part is available. The Alps RK163 footprint currently assigned in KiCad is **not proof that this WH148 fits or follows the same physical pad order**.

The saved schematic defines:

- Pins 1 and 4: anticlockwise ends, grounded.
- Pins 2 and 5: wipers, to the output connector.
- Pins 3 and 6: clockwise ends, fed by C22 and C21 respectively.

Before soldering, disconnect the pot completely. Looking from the knob/shaft end, turn fully anticlockwise. Identify each gang's middle/wiper terminal and the outer terminal that measures nearly zero ohms to it. That outer terminal must go to **GND**. The other outer terminal takes the capacitor-fed signal. At full clockwise, the wiper must read nearly zero ohms to the signal end. Repeat for both gangs. Verify approximately 10k between the two outer terminals, and no electrical connection between gangs. This functional check avoids ambiguity from front/rear views or mirrored lug layouts.

Measure pad spacing, gang spacing, body clearance, shaft position and hole size against the footprint, or wire the panel pot using the verified functional connections. The user subsequently measured resistance between pins 1 and 2 with the shaft facing them and reported that resistance increases clockwise. This confirms pin 1 as the anticlockwise end relative to the wiper, so the revised first-gang wiring gives clockwise volume increase. No further electrical change is needed. Repeat the same check on the second gang (schematic pins 4/5/6), and check near-zero wiper-to-ground resistance at full anticlockwise. Physical footprint fit remains **unverified**.

Linear taper is electrically usable for this bench attenuator but does not give a logarithmic volume law. With a high-impedance load, half travel is about -6dB. With a 10k amplifier input, half travel is about -8dB. End-stop residual resistance means minimum volume is not necessarily a perfect electrical mute.

## Other findings and build gates

- **J5 procurement conflict:** the assigned footprint is JST XH, 2.50mm pitch, while the manufacturer fields say Multicomp Pro MC34635, a 2.54mm header. Resolve which physical connector will be used before PCB release. Neither the connector series nor footprint was changed by guesswork.
- **J3:** despite its custom library name `USBC`, the actual footprint description is `UJ2-B-HR-G-TH-3`, with four contacts and two shield pads numbered 5. It is a USB-B footprint, consistent with the user's clarification. Its contact numbering agrees with the referenced Same Sky drawing. Fit to the specific supplied USB-B connector still needs verification.
- **IC1:** symbol pin numbers/functions agree with the PCM2706C PJT pin table. The assigned custom footprint has 32 pads on 0.8mm pitch, consistent with the TQFP package; no exposed pad is specified. This was not a complete land-pattern/manufacturing review.
- **Power/controls:** PSEL and TEST are HIGH, HOST is LOW (100mA bus-power configuration), VBUS goes only to USB 5V, and all five IC ground pins go to GND. No external active load is supplied from the internal regulator outputs. Each supply has its existing 1u capacitor, and VCOM has C1 10u, positive toward VCOM.
- **Crystal:** 12MHz with 1M feedback and two 18p capacitors is a conventional arrangement. The exact crystal MPN, load capacitance, tolerance and ESR were not supplied. With equal 18p capacitors, effective load is approximately 9p plus stray capacitance, not 18p. Select/check against the actual crystal specification and confirm startup/frequency on the board.
- **Capacitors:** voltage ratings and exact technologies were not specified. Confirm C1 polarity, and use genuine nonpolar parts for the existing unpolarized C21/C22 implementation. Check all ratings and mechanical fit. Supply ceramics may use X7R/X5R; crystal capacitors should use C0G/NP0. Preserve suitable existing parts rather than purchasing from this report alone.
- **Analogue network:** the 16-ohm/22n shunt networks follow the type shown by TI. They are not series output low-pass filters. A 10u coupling capacitor feeding the 10k pot gives about 1.59Hz high-pass corner unloaded; at maximum volume with a 10k amplifier input the effective load is 5k and the corner is about 3.18Hz. Retained values are suitable for ordinary audio testing. Verify actual low-frequency response and cable-load behaviour.
- **Output impedance:** the passive pot can present up to about 2.5k source resistance. Long capacitive cables may affect high-frequency response; no output buffer was added.
- **FB1:** existing shield bead retained. Its exact part, impedance and fit are unspecified; this review does not establish an EMI result.
- **Testability:** supply/coupling capacitor pads, J1/J4/J5 and R12-R15 provide accessible checks. No new clock test stubs were added. Confirm that component placement allows access.
- **PCB boundary:** no placement, routing, decoupling-loop, crystal-layout, USB pair, ground-return or DRC review was done. The PCB has not been updated to these schematic changes, including R17 and swapped pot nets. Do not fabricate from the existing PCB on the strength of this review.
- Existing root CSV/XLSX/XML exports predate this review and refer to an older design; use the fresh `final/netlist.xml` and `final/components.csv` for this schematic revision.

## Verification and accepted warnings

KiCad 10.0.5 ERC: **0 errors, 2 warnings, no new exclusions**. Baseline was 9 errors and 2 warnings. The project already ignores footprint-filter, single-global-label, four-way-junction and simulation-model checks; those settings were not changed.

The remaining warnings are existing `lib_symbol_mismatch` findings:

1. RV1's cached dual-pot symbol differs in property placement/simulation metadata from the installed Device library; the pin map and graphic geometry agree.
2. J3's cached USB_B symbol uses shield pin **5**, matching both shield pads of the assigned custom footprint. The installed standard symbol uses **SH**. Blindly updating the symbol would break that mapping, so it was retained and the warning is documented.

IC1 and IC2's imported symbols declare their pins passive. ERC alone therefore cannot prove correct power or signal direction. The separate verification script checks explicit expected nets, every IC1 pin, internal USBLC6 channel continuity, header wiring, pot wiring, pin-map preservation, and unchanged PCB/project hashes: **104 checks passed**. Final PDF was rendered and visually inspected.

Re-run after future edits:

```sh
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli sch export netlist --format kicadxml -o review/final/netlist.xml PCM2706Bench.kicad_sch
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli sch erc --format json --severity-all -o review/final/erc.json PCM2706Bench.kicad_sch
python3 scripts/verify_schematic.py
```

Assembly/bench qualification still includes USB enumeration and suspend/resume, all sample rates, both switch states, second-gang pot direction/end stops and gang tracking, actual analogue level/DC/transients, clock waveform at the receiving DAC, and operation into the intended amplifier load. Simulation, bench and thermal tests have not been performed.

## Sources

- [TI PCM2706C datasheet SBFS036B](https://www.ti.com/lit/ds/symlink/pcm2706c.pdf): pin tables, sections 9.3/9.5, timing diagrams and Figure 36.
- [TI PCM2706/7EVM-U guide SLEU116](https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/6/PCM2706-Users-guide-sleu116.pdf): bus-power jumper settings and circuit drawing corroborate separate internal supply outputs.
- [ST USBLC6-2 datasheet](https://www.st.com/resource/en/datasheet/usblc6-2.pdf): protected channels 1-6 and 3-4, GND 2, VBUS 5.
- [Alps potentiometer catalogue](https://tech.alpsalpine.com/assets/catalog/product-catalog-rv-all.en.pdf), RK163 drawings: reference for the assigned footprint, not evidence for the Amazon WH148.
- [Same Sky USB-B drawing](https://www.sameskydevices.com/product/resource/uj2-b-hr-g-th.pdf): J3 contact order.
- [Multicomp Pro MC34635 product data](https://www.newark.com/multicomp-pro/mc34635/header-square-pin-2-54mm-6way/dp/46P5353): J5 part-number/pitch conflict.

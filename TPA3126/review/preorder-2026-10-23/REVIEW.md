> **Follow-up — 23 October 2026:** The user is addressing U1 grounding and has checked the heatsink/C21. The other identified schematic/BOM/note issues are addressed in [the correction report](../revisions/preorder-corrections-2026-10-23/README.md). This review below is the preserved pre-correction snapshot, not the current unresolved-item list.

# TPA3126 pre-order review — 23 October 2026

**Disposition: do not release this revision for PCB fabrication or a complete parts order yet.** The core circuit is coherent and the PCB matches its schematic, but the local amplifier ground returns, several BOM/footprint conflicts, and the channel/connector documentation need attention. Heatsink assembly clearance remains unverified.

This was a read-only review of all five saved schematic sheets and the saved four-layer PCB. No production schematic, PCB, project setting, library table or symbol library was changed. SHA-256 preservation results are in [preservation.json](preservation.json); reviewed inputs are identified by [source-hashes.json](source-hashes.json). Zone refill and GUI DRC were performed on an isolated review copy. This is a prototype readiness review, not bench, thermal, acoustic or EMC qualification.

## 1. Items to resolve before ordering

### 1.1 Improve U1 power-ground connections before fabrication

U1 pads 22 and 28 each have only **one thermal spoke**, below the zone's minimum of two. Both violations already have DRC exclusions. U1 pad 25 is also a power-ground return. The nearest GND through-via distances measured from these pads are:

| U1 pad | Location, mm | Nearest GND via distance |
|---|---|---:|
| 28 | 146.685, 119.171 | 6.30 mm |
| 25 | 146.685, 121.121 | 8.16 mm |
| 22 | 146.685, 123.071 | 7.02 mm |

There is connected front-layer GND copper under U1, so these pads are **not electrically unconnected**. However, the single-spoke connections and remote plane vias are a poor choice for the Class-D switching-current return. I recommend short, robust local GND connections and GND vias immediately beside these power-ground pads, with C33/C34 return paths arranged as a compact local supply loop. Do not accept the existing exclusions as evidence of adequate high-frequency grounding. This is about switching-current return impedance; the DAD package has its thermal pad on top.

Evidence: [amplifier detail](amplifier-detail.png), [GUI DRC](gui-drc.rpt), [measurements](layout-measurements.json). TI's TPA3126D2 layout guidance calls for compact supply/ground loops and local PVCC bypassing.

### 1.2 Correct the BOM/footprint conflicts before buying parts

The PCB and schematic agree with each other, but the following assigned manufacturer parts do not agree with their footprints or values. A netlist/DRC pass cannot detect these purchasing errors.

| References | Schematic value / assigned package | Assigned MPN | Problem / disposition |
|---|---|---|---|
| C28 | 1u, 2012 metric | CL31B105KBHNFNE | This MPN is 3216 metric. Choose a suitable 2012 part or change the footprint deliberately. |
| C30, C31, C33, C34 | 100n, 1608 metric | C1206C104K5RACTU | This MPN is 3216 metric. The confirmed inventory stock does not fit the assigned footprint. |
| C56, C57 | 1n, 1608 metric | C1206C104K5RACTU | This is a **100n** part in 3216 metric: wrong value and package. Specify the intended 1n part. |
| C45 | 10u, 3216 metric | GRM32ER71H106KA12L | This MPN is 3225 metric. Its own assembly note also says 3225. Select a matching, adequately rated part and check DC-bias capacitance, or restore the appropriate footprint. |
| C21 | 47u, radial 10 mm diameter / 20 mm height / 5 mm pitch | None | Record the intended **Nichicon UES1H470MPM, 47u / 50 V bipolar**. Do not fit an ordinary polarized electrolytic in this BTL speaker lead. Envelope is compatible; speaker-current heating still needs qualification. |
| C32, C54, C59, C60 | 10n, 2012 metric | None | Specify dielectric and voltage rating; C0G/NP0 at least 50 V is a sensible target for these output RC branches. |
| R6, R20, R34, R40 | 3R3, 2012 metric | None | Select a real resistor with appropriate continuous/pulse rating; qualify dissipation with switching residue present. |

These are not instructions to enlarge all footprints. A correctly selected smaller part may be the better resolution, especially under the heatsink. No replacement MPN was silently selected in this review.

C37–C40 are currently **Panasonic ECW-FE2W684J, 680n, polypropylene, 450 V DC, 15 mm pitch**. Their assigned 18 × 7 mm / 15 mm-pitch footprint is consistent with the recorded 17.5 × 7 × 12.5 mm body. The formerly discussed WIMA parts are not the currently assigned BOM parts.

A fresh [current BOM](current-bom.csv) is included as an audit of saved fields, **not an approved shopping list**. Older project purchasing lists contain removed or renumbered parts and must be reconciled before ordering. Live distributor availability was not established for a complete current cart.

### 1.3 Resolve the DAC channel contract and stale wiring notes

The saved schematic and PCB actually implement:

| PCM5122 output | Analogue path | Amplifier bridge / output |
|---|---|---|
| OUTL, U2 pin 6 | R2 → TWEETER_AUDIO → R14/R15 → C6 → LINP | Left bridge → L3 → C21 → **J17 tweeter** |
| OUTR, U2 pin 7 | R3 → WOOFER_AUDIO → R12/R13 → C1 → RINP | Right bridge → L2 → **J16 woofer** |

This can work electrically, but it reverses the original requirement **DAC left = woofer / right = tweeter** and contradicts existing schematic prose. Either deliberately retain the actual routing and document/configure firmware as left=tweeter, right=woofer, or restore the originally specified channel assignment. Do not connect a tweeter while assuming the old DSP channel mapping.

Also correct these stale notes:

- **J2 pin 2 is now MODEBTN**, not the volume pot's ground. Pot wiper is pin 3, high end pin 4, low end a GND pin such as pin 1 or 5. An old note still says pot low end goes to pin 2.
- C21 is now the onboard 47u tweeter series capacitor. Notes referring to an external “C54=47u at J18” are obsolete; J18 is absent and C54 is now a 10n output RC capacitor.
- R20 is now a fitted 3R3 output RC resistor, not the old DNP PLIMIT resistor. Do not follow the old R20 DNP instruction.

### 1.4 Confirm the ATS heatsink mounting stack before mechanical release

HS1 is centered nearly on U1 and has two 3.2 mm NPTH holes at **40 mm pitch**, at (142.803, 101.541) and (142.803, 141.541) mm. The nominal heatsink plan envelope is **50 × 13.9 mm**, rotated along the board's Y axis. The intended part is ATS-TI1OP-521-C1-R1.

However, the board copy of HS1 has lost its full body/courtyard graphics; it largely represents holes and center marks. DRC therefore does not validate the full heatsink envelope or component height beneath it. C25/C26 project about **0.77 mm inside the full-width heatsink envelope** near its shoulder. That is not proof of a collision: the underside relief/taper matters. The transverse shoulder geometry in the generated 3D model was illustrative because the source drawing did not fully dimension it.

The source drawing's central underside height is nominally 1 mm; U1 body height is approximately 1.00–1.15 mm, before TIM and tolerances. Confirm the real contact, relief and mounting preload with the actual sink or a sufficiently detailed drawing. Do not force both mounting feet flat in a way that overloads the IC. Use appropriate hardware for the heatsink's mounting arrangement; 3.2 mm PCB holes alone do not define the fastener/thread stack.

The upper exposed pad is electrically associated with GND; the heatsink must not touch leads or other conductors. A suitable thermal interface is still required. Final insulation/attachment choice must follow TI's package and actual assembly requirements. The commonly quoted 8.5 °C/W heatsink figure is at **200 LFM airflow**, not a still-air enclosure guarantee.

## 2. Schematic review: what checks out

All hierarchical sheets were inspected. A fresh netlist was used for pin/net tracing, and significant IC pin mappings were compared with the official documentation and current symbol/footprint mapping. [119 connectivity assertions](connectivity.json) pass for the actual current circuit. This does not erase the channel contract discrepancy described above.

### Power and regulation

The intended power tree is coherent:

**12–16 V input → fuse → reverse-polarity P-MOSFET → protected PVDD → amplifier**

**PVDD → LMR51430XFDDCR buck, approximately 4.30 V → TLV1117LV33 ESP32 3.3 V**

**4.30 V → 2R2 RC input filtering → TPS7A2033 DAC 3.3 V**

The fuse, P-MOSFET orientation, gate zener and TVS polarity are consistent. U3's XF suffix selects the intended FPWM version; do not order another suffix solely from the generic “LMR51430” value. The buck divider is 100k/16k2, and the inductor is SRP6030WA-6R8M. The LDO pinouts and feedback/decoupling connections are consistent.

The ESP LDO dissipates approximately 0.25 W at 250 mA, 0.50 W at 500 mA, and 1 W at 1 A, using a 1 V drop. Its board tab presently has limited copper spreading. Continuous high-current thermal capability is not established: more output-net copper around its tab would improve margin. Wi-Fi peak current and 3.3 V droop need bench verification; a 3 A buck rating does not make the downstream LDO a guaranteed continuous 1 A supply on this layout.

At 2 × 15 W, a plausible amplifier dissipation envelope is 3.3–5.3 W at 90–85% efficiency, plus control electronics and regulator loss. A regulated **16 V / 3 A** source provides a sensible starting margin. This does not imply 15 W/channel at 12 V, or qualification of the enclosure thermals.

### DAC and analogue interface

PCM5122 remains the selected DAC. Its digital/analogue/charge-pump supplies, CAPP/CAPM and VNEG capacitors, LDOO decoupling and ground connections are consistent. MODE straps select register-controlled operation, ADR straps select **7-bit I²C address 0x4C**, and SCK is grounded for BCK-PLL / MCLK-less operation. The DAC has an ESP-controlled XSMT signal.

TPA3126D2 single-ended input coupling is coherent: matching 1u coupling capacitors, positive-leg attenuation and approximately matched negative-leg source impedance. R12/R13 and R14/R15 are 1k2/1k5, with the DAC's 470-ohm series resistor included. Nominal attenuation is approximately **0.466**; 2 Vrms full-scale DAC output becomes about 0.93 Vrms at the amplifier input. The 820-ohm reference-leg resistors approximate the positive leg's approximately 790-ohm source resistance.

At 20 dB gain, 15 W into 4 ohms requires approximately **0.775 Vrms input**, 7.75 Vrms speaker output, 10.95 V peak and 1.94 Arms. This is attainable in principle at 16 V, subject to distortion and losses. Full-scale DAC output is still above that input level: the pad reduces gain/headroom risk but does not impose a precise 15 W ceiling. An approximately −2 dBFS DSP setting is only an initial nominal calibration point; tolerances, EQ, source level and limiter behavior must be measured.

### Amplifier configuration and output filters

- TPA3126D2 DAD pin mapping, PVCC and GND connections, stereo BTL arrangement and 220n bootstrap capacitors are consistent.
- Gain is **20 dB**; oscillator is **400 kHz master**, hybrid modulation setting as wired. SYNC is intentionally unused.
- Output filter windings are **10u each**, in two CSAD0660-100M packages, with 680n shunts as wired. Physical winding pairs 1–2 and 4–3 are preserved. Neither speaker terminal is grounded.
- The current Codaca datasheet lists 10u ±20%, **47 milliohms typical / 55 milliohms maximum DCR**, 6.5 A typical current at 30% inductance reduction, and 3.5 A typical current at 40 °C temperature rise. The listed package height is **4.2 mm maximum**, not the taller figure in an older project memory. Nominal inductance alone is not a protection guarantee.
- A simple half-bridge estimate at 16 V / 400 kHz gives about 1 App winding ripple at 10u, or 1.25 App at the −20% tolerance limit. Added to the 2.74 A sine peak at 15 W, this remains below the typical 6.5 A saturation test point. This is a nominal operating estimate, not short-circuit/fault qualification or a model of unspecified interwinding coupling.
- Four 10n/3R3 series RC branches are **after the inductors**, one on each filtered output. The tweeter positive branch is before C21. They are electrically separate from the main LC shunt capacitors. The previous 330p/18-ohm switching-node networks are absent.
- PLIMIT is referenced from ESP 3.3 V through R19=10k, with C29=1u; the old lower divider resistor is absent. A simplified datasheet model gives approximately **19 W nominal** into 4 ohms. This is not precision power regulation, and clipped waveform power can exceed a sine-wave estimate. It cannot replace independent woofer excursion protection, tweeter high-pass filtering and per-channel DSP limits.
- JP1 correctly bypasses C21. Leave it open for the intended tweeter fail-safe; close only for deliberate bypass/stereo use. 47u with an ideal 4-ohm load gives approximately **847 Hz** high-pass corner. Real tweeter impedance and DSP crossover interaction require measurement.

### Startup, GPIOs and controls

Hardware defaults remain appropriate: R25 holds SDZ low, R29 holds MUTE high, and R32 holds DAC XSMT low during MCU reset. GPIO-controlled outputs and FAULTZ pull-up are present. These defaults support quiet startup but do not prove zero pops on abrupt power removal or firmware failure.

Firmware should keep the amplifier shut down/muted while rails settle, configure the DAC muted, start valid DSP/I²S, release XSMT, enable SDZ, allow the amplifier startup interval, release MUTE, then ramp volume. Mute/shut down promptly on faults or loss of valid audio. Check hard power-off behavior on the bench; VIN sensing alone is not a guaranteed early-warning power-fail system.

| Function | GPIO | Review |
|---|---:|---|
| Wi-Fi LED | 32 | Retained |
| Bluetooth LED | 33 | Retained |
| I²S LRCK / BCK / DATA | 25 / 26 / 13 | Retained |
| I²C SCL / SDA | 19 / 21 | Retained |
| Amplifier SDZ / MUTE | 27 / 23 | Valid free output GPIOs |
| Amplifier FAULTZ | 35 | Input-only GPIO is appropriate; external pull-up present |
| DAC XSMT | 18 | Valid output |
| VIN sense | 36 | ADC1 input |
| Volume | 34 | ADC1 input, R39/R41/C58 verified |
| Mode button | 22 | Module pin 36, 10k external pull-up R35, active-low switch to GND |

The exact module remains **ESP32-WROVER-IE-N16R8**. The proven firmware GPIOs are preserved; flash/PSRAM reservations and boot restrictions do not conflict with GPIO22. GPIO22 is not a boot strapping pin. Implement button debounce in firmware.

R39=10k and R41=22k limit nominal volume-wiper full scale to **2.269 V**; C58=100n filters the ADC node, and a disconnected wiper has a defined low state. The divider is present in both schematic and PCB. C58 is nearer J2 than the ADC; moving it close to the ADC would reduce pickup along the approximately 35 mm ADC trace, but this is an improvement rather than a demonstrated functional blocker.

Current J2: **1 GND, 2 MODEBTN, 3 pot wiper, 4 3.3 V, 5 GND, 6 BT LED positive drive, 7 GND, 8 Wi-Fi LED positive drive**. LED drives have 1k series resistors. UART J3 is 1 GND, 2 RX, 3 TX, 4 ESP 3.3 V; avoid back-powering from a powered programming adapter. EN/BOOT buttons and pull-ups are retained.

## 3. PCB review

The saved board is **100.000 × 86.487 mm**, with four copper layers and a nominal 1.6 mm stack. Minimum routed width is 0.2 mm; ordinary signals are typically 0.3 mm, and power routing uses wider tracks/zones. Vias are 0.6 mm diameter / 0.3 mm drill. These dimensions are compatible with ordinary JLCPCB four-layer capability; fabrication outputs still need final upload inspection.

Positive findings:

- L2/In1.Cu provides an essentially continuous GND reference. There is no arbitrary analogue/digital ground split.
- Power input/buck, DAC analogue circuitry and Class-D output stage are spatially separated.
- Buck input capacitors, bootstrap capacitor, inductor and output capacitors form a compact power section. Feedback is on the quieter side.
- Bootstrap components are close to U1, output windings are near the amplifier, filtered outputs use broad copper, and the dual-inductor pin routing matches the schematic.
- The output capacitors and RC branches are on the correct side of the inductors.
- Speaker polarity and independent BTL connections are preserved.

Additional improvements/limits:

- Correct the U1 ground returns described in section 1.1. Local PVCC decoupling effectiveness depends on the return loop, not just capacitor proximity.
- Some I²S routing is on B.Cu, with sparse In2.Cu above it and the solid In1 GND plane across the thick core. Existing source resistors help. A nearby continuous ground reference on the signal's adjacent layer, or moving critical clocks to routing adjacent to In1, would improve return geometry. Current operation/EMI is unproven, not proven defective.
- U4 needs thermal testing and could benefit from more output-net copper for heat spreading.
- The IE module uses an **external antenna**. Confirm the coax/antenna arrangement, distance from heatsink/metal, and Wi-Fi performance under amplifier load; a PCB-antenna keepout drawing is not a substitute for this module's actual RF assembly.
- IC2/IC3 courtyards overlap about 0.507 mm, but the nominal 6 × 6 mm switch bodies have approximately 1.493 mm clearance. The existing courtyard exclusion can be reasonable if the actual actuator/assembly envelope is confirmed.
- Mounting-hole library mismatch warnings reflect board-vs-library differences and remain unresolved as library warnings; they are not open circuits. HS1's footprint exists in the local files, but the GUI still reported a library-resolution warning. Do not infer that warning means the two physical holes are absent.
- The sink footprint lacks its full courtyard. Missing-courtyard checking is globally ignored in this project, so a mechanically clean DRC cannot be inferred.
- Bottom silkscreen says “TDA3126”; correct to “TPA3126” when revising artwork.

Images: [front routing](front-routing.png), [top render](board-top.png), [L2 ground](layers/In1_Cu.png), [L3](layers/In2_Cu.png), [bottom](layers/B_Cu.png). Missing 3D models and illustrative heatsink geometry mean the render is not a complete collision check.

## 4. Actual verification results

| Check | Actual result |
|---|---|
| KiCad 10.0.5 CLI ERC | **0 errors, 28 warnings**, all endpoint-off-grid warnings |
| Fresh exported schematic connectivity assertions | **119 passed** for actual current topology; original L/R contract check is explicitly false |
| Independent schematic-to-board comparison | **356 schematic pins / 356 distinct numbered PCB pads**, no missing/extra pins, no genuine net mismatches, no value/footprint assignment mismatches |
| KiCad CLI DRC with refill/parity request | **Aborted, exit 134; no usable report. Not a pass.** |
| KiCad PCB Editor GUI DRC on isolated review copy, with zone refill | **0 unconnected pads; 9 existing excluded findings; no unexcluded errors/warnings** |
| Native GUI schematic parity | Not run; independent comparison above is supplemental |
| Production source preservation | All recorded production file hashes unchanged |

The nine excluded DRC findings are **four errors and five warnings**:

1. IC2/IC3 courtyard overlap, error.
2. U1 pad 22 one-spoke thermal connection, error.
3. U1 pad 28 one-spoke thermal connection, error.
4. U2 pad 20/SCK-to-GND one-spoke thermal connection, error. This is a low-current strap, less critical than U1; either improve it or document acceptance.
5–8. H1–H4 footprint/library mismatches, warnings.
9. HS1 footprint not found in the GUI's resolved Custom library, warning.

Ignored checks include missing courtyard, track endpoint not centered on via, tuning profile geometry, footprint filter mismatch and component-type/pad mismatch. Existing exclusions/settings were not altered. See [native GUI report](gui-drc.rpt), [ERC JSON](erc.json), [pin comparison](parity.json) and [connectivity JSON](connectivity.json). This is not an unconditional “clean DRC” result.

## 5. Inventory spot check for the order

These quantities were returned by the actual read-only inventory MCP on 23 October 2026. All listed records report zero reserved quantity. This is a targeted critical-parts check, not a completed full-BOM stock allocation. Inventory does not prove recovered IC condition or substitute for physical confirmation.

| Component | Manufacturer part / recorded model | Required | Confirmed physical inventory | Purchase disposition |
|---|---|---:|---:|---|
| U1 amplifier | TPA3126, salvaged; schematic TPA3126D2DADR | 1 | 1 | No, if recovered marking/condition confirmed |
| U2 DAC | PCM5122; schematic PCM5122PWR | 1 | **0** | **Yes**, unless separately owned but unrecorded |
| IC5 module | ESP32-WROVER-IE-N16R8 | 1 | 1 | No |
| U3 buck | LMR51430XFDDCR | 1 | 1 | No; additional 10 on order are not counted as owned |
| IC4 DAC LDO | TPS7A2033PDBVR | 1 | 15 | No |
| L2/L3 | CSAD0660-100M | 2 | 2 | No |
| L1 | SRP6030WA-6R8M | 1 | 5 | No |
| R41 | RR1220P-223-D, 22k | 1 | 50 | No |
| C28 assigned part | CL31B105KBHNFNE | 1 | 50 | **Package conflict: do not order/assemble from current fields** |
| C30/C31/C33/C34 assigned part | C1206C104K5RACTU | 4 | 139 | **Package conflict**; same MPN is also wrongly assigned to C56/C57 |
| Bootstrap capacitors | Samsung 220n / 25 V X7R, 2012 metric, inventory ID 84 | 4 | 48 | Suitable package/value stock confirmed; match actual reel/MPN |

The inventory's WROVER record links a WROOM datasheet; that link was not used as authority. No inventory record was modified or reserved. Raw replies: [inventory.json](inventory.json).

## 6. Release and first-build gates

Before PCB release: resolve the U1 return geometry; choose one unambiguous channel contract; correct the J2/obsolete component notes; settle the footprint/MPN conflicts; confirm heatsink clearance/stack; refill and rerun DRC on the final production board. Regenerate Gerbers and separate plated/non-plated drill files from that final save, then inspect the fabricator's board/slot/drill preview. No final fabrication archive was generated or approved in this review.

Before a complete parts order: reconcile the current BOM with actual packages and ratings, the missing PCM5122 stock, the selected bipolar C21, output RC component ratings and current distributor availability. The current BOM CSV deliberately exposes incomplete fields rather than inventing replacements.

After assembly: current-limited initial power-up, rail and Wi-Fi transient tests, DAC I²C/I²S verification, muted startup/hard-off/reset tests, low-level channel identification into dummy loads, output stability/ripple/RC and inductor temperature, 16 V power/distortion calibration, fault recovery, then enclosure thermal/RF/EMI checks. Connect the tweeter only after channel mapping and per-channel filtering/limits have been confirmed. Test driver protection for each intended speaker system: a reusable board cannot impose one safe crossover/excursion limit for every driver/enclosure.

## Sources

Current source files and measurements are primary evidence for the as-built connectivity/layout findings. Manufacturer sources used for electrical and mechanical interpretation:

- [TI TPA3126D2 datasheet](https://www.ti.com/lit/ds/symlink/tpa3126d2.pdf)
- [TI TPA3126D2 EVM user guide](https://www.ti.com/lit/pdf/slou506)
- [TI PCM5122 datasheet](https://www.ti.com/lit/ds/symlink/pcm5122.pdf)
- [Espressif ESP32-WROVER-E / WROVER-IE datasheet](https://documentation.espressif.com/esp32-wrover-e_esp32-wrover-ie_datasheet_en.pdf)
- [Codaca CSAD0660 datasheet](https://www.codaca.com/Private/pdf/CSAD0660.pdf)
- [TI LMR51430](https://www.ti.com/lit/ds/symlink/lmr51430.pdf), [TLV1117LV](https://www.ti.com/lit/ds/symlink/tlv1117lv.pdf), [TPS7A20](https://www.ti.com/lit/ds/symlink/tps7a20.pdf)
- [Diodes DMP4015SK3](https://www.diodes.com/assets/Datasheets/DMP4015SK3.pdf)
- [JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities/)

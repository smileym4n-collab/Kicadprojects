# PCM1704 / DF1704 DAC ("Reference Series DAC-3"): Performance Review

Date: 2026-10-17. This review covers the working-tree state of `PCM1704.kicad_sch` and `PCM1704.kicad_pcb` (KiCad 10.0.5). That state includes changes not yet committed since `6d8d627`. **No design files were changed.**

| State | Status |
|---|---|
| Schematic checked against datasheets | **Yes**, for the PCM1704, DF1704, OPA1611/OPA1612 and LM317/LM337. **LT3042/LT3094 partly**: analog.com blocked scripted downloads (see §5). |
| Layout reviewed | **Yes.** I checked placement, stack-up, every net's layer use, decoupling distances, return paths and the clock routes. |
| KiCad ERC | 7 errors (all ATtiny pins left unconnected without no-connect flags) and 18 warnings (off-grid points, plus a cosmetic symbol/library mismatch). |
| KiCad DRC | 1 live error (a 0.17 mm clearance) and 6 excluded items. Nothing is unrouted. |
| Simulated / bench-tested / thermally tested | **No.** |

Sources:

- PCM1704: Burr-Brown/TI SBAS097 (PDS-1454C).
- DF1704: TI SBAS099A.
- OPA1611/OPA1612: TI SBOS450.
- PGFB guidance: the ADI DC2624A (LT3094) eval-board notes.

---

## 0. Summary

The circuit follows the Burr-Brown reference design closely, and it does so correctly. The pinouts, rail arrangement, reference-pin capacitors, I/V scaling and filter maths all check out. The analogue chain layout is good: it is compact and symmetric, entirely on F.Cu, and over a solid In1 ground plane.

The things most likely to limit the PCM1704s are **clocking and the DAC's own support-pin layout**, not the op-amps:

1. **(High)** The DF1704→PCM1704 BCLK, WCLK and DATA lines run mostly on B.Cu/In2. Those layers have no adjacent plane, the lines run parallel to each other, and BCLK/WCLK are T-split.
2. **(High)** The REF DC and SERVO DC capacitors return to −5 V through the shared −5 V supply trunk instead of directly to each DAC's pin 20. The trunk is routed *through their pads*.
3. **(High)** The XMOS master clock enters unbuffered and travels about 23 mm of trace to XTI. The XMOS board can also drive the DF1704 inputs while this board is unpowered. The fixed J5 pinout gives SCK the worst return path. H3 has the receive-buffer plan.
4. **(Medium)** The output is DC-coupled with no offset control and no mute. The PCM1704's bipolar-zero error alone allows up to ±57 mV of output offset.

---

## 1. Verified correct (keep as is)

**PCM1704 (U1, U2)**

- **Pinout:** matches SBAS097 p.3 pin-for-pin.
- **Footprint:** `SO-20_5.3x12.6mm_P1.27mm` matches TI's package addendum (NS, 5.3 mm SOP). *Measure the salvaged parts with calipers before ordering.* The lead span should be about 7.8 mm, not the 10.3 mm of a wide SOIC-20.
- **Word length and polarity:** 20BIT (pin 9) and INVERT (pin 10) are tied to DGND, which is logic H for these pins. That gives 24-bit, non-inverted (Tables II and III).
- **Supply rails:** +V<sub>CC</sub>/+V<sub>DD</sub> share one rail and −V<sub>CC</sub>/−V<sub>DD</sub> share one rail, as the datasheet requires ("tie together at a single point"). This also satisfies the ±0.1 V supply-difference absolute maximum.
- **Support-pin capacitors:**
  - REF DC 47 µF and SERVO DC 47 µF go to −V<sub>CC</sub>.
  - BPO DC 100 µF goes to AGND.
  - Values, return nodes and polarities match Figs. 3 and 5.

**DF1704 (U3)**

- **Mode:** software mode (MODE = H). The hardware-only pins (3–5, 15–20, 27) are strapped to GND.
- **Clock and reset:** XTI is driven from SCKIN, and XTO/CLKO are left open. RST is held low by R75 until the MCU releases it.
- **Series resistors:** R79–R82 sit at the driver, which is correct.
- **Bit clock:** BCKO is 256 f<sub>S</sub> at 256/512 f<sub>S</sub> system clocks. That is 24.576 MHz at 96 kHz, which just meets the PCM1704's 40 ns minimum BCLK period.

**Channel mapping**

- DOR → U1 → U4 → U8B → U9B → OUT_R → J1 pin 1.
- DOL → U2 → U5 → U8A → U9A → OUT_L → J1 pin 3.
- The silkscreen "L G R" is correct.
- Absolute polarity is preserved: the I/V and MFB stages each invert, so the two inversions cancel.

**I/V stage**

- OPA1611 with 2.37 kΩ ∥ 47 pF gives ±1.2 mA × 2.37 kΩ = 2.844 V peak = **2.011 Vrms**.
- The 47 pF sets a pole at 1.43 MHz.
- This is essentially Fig. 5 (OPA627, 2.5 kΩ, 47 pF).
- Noise gain is 1 + 2.37 k/1 k (DAC R<sub>OUT</sub>) = 3.4, so OPA1611 voltage noise contributes about 3.7 nV/√Hz. The 2.37 kΩ resistor contributes 6.2 nV/√Hz. Both are below what the DAC is specified for.

**Post filter**

- The MFB stage has f<sub>0</sub> = 39.9 kHz and Q = 0.999. The RC pole is at 39.86 kHz. Together they make a 3rd-order Butterworth.
- Response is −0.07 dB at 20 kHz and about −57 dB at 352.8 kHz, the first image at 8 × 44.1 kHz. Sinc roll-off adds more on top.
- Both MFB and I/V hold their non-inverting inputs at ground, so there is no common-mode distortion in either stage.

**Op-amp pinouts:** U4/U5 (single) and U8/U9 (dual) are correct.

**Power**

- **Set points:** LM317 = +8.02 V and LM337 = −8.02 V (240 Ω / 1.3 kΩ). LT3042 = +4.99 V and LT3094 = −4.99 V (49.9 kΩ × 100 µA).
- **Diode polarities:** D5–D8 are all correct for output→input discharge and ADJ-capacitor protection.
- **Rail separation:** one LT3042 supplies only the DACs (+5 V), and a second supplies the DF1704 and MCU (+5VDF).
- **Unused LT pins:** PGFB is tied to IN, which disables power-good and fast-start as intended, per ADI. ILIM is tied to GND.

**Layout fundamentals**

- In1 is an unbroken GND plane, with 358 GND vias.
- Each PCM1704 is oriented with its digital pin row facing the DF1704 and its analogue pin row facing the I/V stage.
- J1 (output) is on the top edge, away from J2 (power) and J5 (I²S). Any loop current between the source board and the PSU therefore stays at the bottom edge, away from the analogue section.
- The I²S input traces from J5 to U3 are on F.Cu over In1.

---

## 2. Findings, ranked by expected effect on DAC performance

### H1 — DF1704→PCM1704 clock/data routing has no close reference plane (layout)

| Net | F.Cu | In2 | B.Cu | Vias |
|---|---|---|---|---|
| U1-BCLK (to both DACs) | 5.9 mm | 20.8 mm | 19.9 mm | 3 |
| U1-WCLK (to both DACs) | 6.0 mm | — | 40.0 mm | 3 |
| U1-DATA | 4.1 mm | 16.3 mm | — | 2 |
| U2-DATA | 9.1 mm | — | 20.3 mm | 2 |

- **No close plane:** In2 and B.Cu carry no plane. With the 0.1 / 1.24 / 0.1 mm stack, the nearest reference for these tracks is In1, about 1.3 mm away.
- **Parallel runs:** BCLK runs 19.5 mm alongside U2-DATA (B.Cu) and 15 mm alongside U1-DATA (In2), at 0.6 mm centre spacing. WCLK runs about 10 mm alongside BCLK.
- **Coupling estimate:** the usual crosstalk rule of thumb is 1/(1+(D/H)²). With D = 0.6 mm and H ≈ 1.3 mm it gives about 0.8. The same pair on F.Cu over In1 (H = 0.1 mm) gives about 0.03. So the coupling here is roughly **30× stronger** than it would be on F.Cu.
- **Why it matters for this DAC:** the PCM1704 output changes on the 2nd BCLK rising edge after WCLK falls (SBAS097 p.7). The BCLK/WCLK edge timing *is* the conversion clock. Crosstalk from DATA onto BCLK is therefore data-dependent, i.e. signal-correlated, jitter.
- **Edge margin:** at 24.576 MHz BCLK (96 kHz) there is no spare period, so ringing from the BCLK and WCLK T-splits also needs margin.
- **DRC error at the source:** the one live DRC error is here. The U2-DATA arc passes 0.17 mm from R79 pad 2 (BCLK) near (133.8, 115.1) mm.

**Recommendations**

1. Give these four lines a solid reference along their whole length. Either:
   - route them on F.Cu over In1 where space allows (between U3 and the DAC decoupling row, y ≈ 104–118 mm), or
   - pour stitched GND on In2 and B.Cu and run the lines on B.Cu over that In2 fill.
2. Keep DATA at least 3 track-heights away from BCLK and WCLK.
3. Use one series resistor per DAC for BCLK and for WCLK (point-to-point, not T). This adds 2 × 1608 metric resistors.
4. DF1704 SBAS099A suggests 50–100 Ω as the *starting point* for these series resistors; the board has 22 Ω. Tune with a scope on the PCM1704 pins, using a short ground spring, after re-routing.

### H2 — REF DC / SERVO DC capacitors return through the shared −5 V trunk (layout)

Datasheet Figs. 3 and 5 return the REF and SERVO capacitors to the −V<sub>CC</sub> pin itself. On this board the −5 V route is:

**LT3094** → C29/C30 → via (164.0, 85.8) → In2 trace → **C16(−)** (U1 SERVO) → In2 → junction (141.0, 88.6)

From the junction, two branches leave:

- **To U1:** **C15(−)** (U1 REF) → F.Cu → C99 → U1 pin 20 → U1 pin 4.
- **To U2:** In2 → **C14(−)** (U2 SERVO) → **C13(−)** (U2 REF) → F.Cu → C100 → U2 pin 20 → U2 pin 4.

Problems with this:

- **Cap pads used as vias:** the through-hole pads of C13–C16 act as the layer transitions for the supply. The −5 V net has only one real via.
- **Shared current:** the supply current of both DACs (30 mA typical / 45 mA max each, including the −V<sub>DD</sub> logic current and the signal current of up to ±1.2 mA) flows between each capacitor's negative terminal and the pin 20 it is meant to reference.
- **Crosstalk path:** U2's (left-channel) supply current passes through U1's SERVO capacitor node.
- **Size of the effect:**
  - The shared path is several tens of mΩ of trace, so the signal current gives tens of µV between the capacitor and the pin.
  - SBAS097 does not specify how well these pins reject that voltage. Treat it as a *likely* contributor to L→R crosstalk and low-level distortion, not a proven one.
  - It is cheap to fix.

**Recommendations**

1. Connect each REF and SERVO capacitor's negative lead to its own DAC's pin 20 with a short, dedicated F.Cu trace that carries no supply current.
2. Feed −5 V to each DAC as a separate branch from the LT3094 output capacitors (a star), arriving at the pin 20 / C99 (C100) node, not via the capacitor pads.
3. Move C15/C13 (REF, now 5.5–5.7 mm from pin 19) and C17/C18 (BPO, 6.1 mm and 8.4 mm) closer to their pins if the re-route allows.
4. Apply the same discipline to +5 V: the pin 11 capacitors (C7/C97, C6/C98) should be the first thing the feed meets.

### H3 — Master clock input from the XMOS XU208 (constraints fixed 2026-10-17)

**Fixed constraints**

- J5 is fed by an XMOS XU208 USB-to-I²S board, which stays I²S master.
- J5's position and pinout cannot change: 1 SCK, 2 BCK, 3 DATA, 4 LRCK, 5 GND, 6 GND.
- The DAC-as-clock-master option is therefore off the table.

**What matters:** the DF1704 times its outputs (BCKO/WCKO, the PCM1704 conversion clock) from XTI only. So SCK's edge at XTI sets the conversion timing. BCK, LRCK and DATA only need to meet the DF1704's setup/hold times.

**Problems in the current arrangement**

- **Unbuffered SCK:** SCK travels about 23 mm of board trace from J5 straight into XTI, with no receive buffer.
- **Worst return path:** in the cable, SCK is the conductor furthest from either GND pin.
- **Termination:** R28–R31 sit at the receiving end. Series resistors only terminate at the *driver*.
- **Power-off back-powering (new finding):**
  - The XMOS board drives the DF1704 inputs through only 22 Ω.
  - If the XMOS board is powered (from USB) while this board is off, that breaks the DF1704's −0.3 V … V<sub>DD</sub> + 0.3 V input rating (±10 mA abs max).
  - It can also back-power +5VDF through the input clamps.

**Recommended changes on this board**

1. **Receive buffer beside U3, on a new 3.3 V rail.** The parts were checked against TI/Nexperia datasheets, and all are in inventory.
   - **SCK:** SN74LVC1G17, a Schmitt buffer, 2 in stock. At V<sub>CC</sub> = 3 V its thresholds are V<sub>T+</sub> 1.48–1.92 V and V<sub>T−</sub> 0.89–1.2 V. That suits a 3.3 V input, and the hysteresis rides through ringing on the cable-driven edge.
   - **BCK, LRCK, DATA:** 74LVC125APW, 3 in stock. It is rated for V<sub>CC</sub> 1.65–3.6 V, with V<sub>IH</sub> 2.0 V / V<sub>IL</sub> 0.8 V and no hysteresis. Tie the spare gate's input to GND and its OE pin high (disabled).
   - **3.3 V supply:** TPS7A2033 (V<sub>IN</sub> ≤ 6.0 V, so feed it from +5VDF, not +8 V), 14 in stock. Put a local 100 nF at each buffer.
   - **Outputs:** they drive the DF1704's TTL-level inputs (V<sub>IH</sub> 2.0 V) over a few mm of F.Cu. Provide a 22–33 Ω series footprint at each output.
   - **Inputs:** add weak pull-downs (about 100 kΩ, provisional) so the inputs are defined when the XMOS board is off or unplugged.
   - **Power-off protection:** both LVC parts are I<sub>OFF</sub>-rated (≤10–20 µA with 5.5 V on an input at V<sub>CC</sub> = 0), which removes the back-powering path above.
2. **Parts not used, and why:**
   - The 74LVC125A is not rated for operation at 5 V.
   - The LVC1G17 at 4.5–5.5 V has V<sub>T+</sub> up to 2.74–3.33 V, which is too close to a 3.3 V swing.
   - The SN74AHCT125 would run from +5VDF, but it has no I<sub>OFF</sub> rating, and the stocked part is DIP.
3. **Termination:** leave R28–R31 fitted (22 Ω or 0 Ω). Add a DNP RC-termination footprint on SCK at the buffer input in case the scope shows ringing; set values after measuring. Confirm the XMOS board has series resistors at its own drivers.

**Cable (no PCB change):** twist the SCK wire (pin 1) with the pin 6 GND wire, and BCK (pin 2) with pin 5 GND, along the cable run. Keep the cable as short as practical.

**DF1704 limits the XMOS set-up must respect**

- **Sample rates:** f<sub>S</sub> 32–96 kHz only. Disable 176.4/192 kHz and above, and DSD/DoP, in the XU208 firmware/driver.
- **MCLK ratio:** must be 256/384/512/768 f<sub>S</sub>, and 768 f<sub>S</sub> is not allowed at 96 kHz.
  - 22.5792/24.576 MHz MCLK gives 512 f<sub>S</sub> at 44.1/48 kHz and 256 f<sub>S</sub> at 88.2/96 kHz. Both are fine.
  - 45.1584/49.152 MHz MCLK would be 1024 f<sub>S</sub> at 44.1/48 kHz, which is not supported. **Check which oscillators the XU208 board uses.**
- **BCK and format:** BCK of 64 f<sub>S</sub> is supported. The MCU sets the DF1704 to I²S, 24-bit.
- **Rate changes:** the XMOS board switches MCLK oscillators on a rate-family change, and the DF1704 re-syncs. Mute around this (see M2). Feeding buffered LRCK to a spare MCU pin would give clock-loss and rate-change detection.

**Ground loop:** if the XU208 board is powered from USB through the StreamerIsolater, its ground meets this board only at J5, so there is no loop. If it shares the J2 supply, there is a loop through J5 GND. That loop already stays at the bottom edge, away from the analogue section.

### M1 — DC offset and channel balance (schematic)

**What the datasheet allows**

- **Bipolar-zero error** is ±0.5 % FSR typical and ±1 % maximum. With FSR = 2.4 mA that is ±12 µA / ±24 µA, giving **±28 mV typical / ±57 mV maximum** at the I/V output, and the same at J1.
- **Op-amp contributions** are about 3 mV worst case: V<sub>OS</sub> × noise gain plus I<sub>B</sub> × R.
- **Gain error** is ±1 % typical and ±3 % maximum. Channel balance can therefore differ by several tenths of a dB even with 0.1 % feedback resistors.

**Why it matters here:** the schematic notes a PGA2310 downstream. DC at a PGA2310 input turns each gain step into a DC step, which is heard as a click.

**Options, after measuring the salvaged parts first (§4)**

- **(a)** Accept it if the preamp input is AC-coupled.
- **(b)** Add a DC servo per channel: an integrator, e.g. a spare OPA1612 half or an OPA1641, sensing OUT_x and injecting into the I/V summing node.
  - The injection resistor needs to be ≤ 13 V / 24 µA ≈ 540 kΩ (e.g. 330–470 kΩ). Its noise current at the I/V output is about 0.4 nV/√Hz, which is negligible.
  - Set the corner well below 1 Hz.
  - These values are provisional.
- **(c)** Provide a film output coupling capacitor footprint (bypassable).

Option (b) keeps the DC-coupled path.

### M2 — No output mute; power-up/down transients (schematic)

**The problem**

- ±15 V reaches the op-amps immediately.
- The DAC rails soft-start over about 235 ms (49.9 kΩ × 4.7 µF on SET).
- J1 is DC-coupled, so the I/V output sees whatever the DACs do while their rails ramp. The schematic notes already list this as outstanding.

**Suggestion:** an MCU-driven mute, e.g. a small signal relay or shunt after R62/R63.

- It would engage at power-up and release after DF1704 reset release plus settling.
- It would re-engage when ±5 V or the clock is lost. That requires rail monitoring: PA5–PA7 and PB0–PB3 are free, and the LT3042/3094 PG pins are currently unused.
- Provisioning it as DNP footprints in Rev 1 is fine.

### M3 — LM337 stability capacitors are far from U10 (layout)

- The LM337 needs 1 µF solid tantalum or ≥25 µF aluminium at its output for stability. The schematic note says "Place at U10 OUT".
- As placed, C90 (1 µF) is **18 mm** from U10 pin 3 and C19 (47 µF) is **27 mm** away.
- **Move both next to U10 pin 3.**
- The LM317 side (C71 at 13 mm, C22 at 39 mm) is less critical, because the LM317 does not need an output capacitor for stability.

### M4 — No test points (layout)

Suggested test points:

- **Rails:** +8 V, −8 V, +5 V, −5 V and +5VDF, each with a nearby GND loop.
- **DC checks:** each DAC's REF, SERVO and BPO pins. Use small pads; these are high-impedance nodes, so measure DC only.
- **Clocks:** BCLK and WCLK at one DAC. Use a small pad with an adjacent GND pad for a probe spring.
- **Control:** DF_RST.
- **Audio:** each I/V output, for offset measurement.

### M5 — ±5 V distribution impedance (layout; lower priority than H2)

- +5 V and −5 V travel 40–70 mm on 0.4 mm In2 traces, with the regulators sensing (OUTS) at the regulator.
- The local 100 nF + 4.7 µF at each pin covers the HF.
- **When fixing H2,** widen these feeds or pour them as In2 copper islands under the DAC area. If inner layers are JLC's 0.5 oz default, 0.4 mm is about 2.5 mΩ/mm.

### M6 — MCU activity on +5VDF next to the DF1704 (firmware)

- The ATtiny1614 shares +5VDF with the DF1704 and sits about 25 mm from it.
- **After configuring the DF1704, put the MCU into power-down sleep** (wake on pin change if needed), so that no MCU clock activity runs during playback.

---

## 3. Low priority / housekeeping

- **Op-amp bulk decoupling:** each op-amp rail has only 100 nF locally. The nearest bulk (C44/C45) is about 60 mm away, so the quality of the external ±15 V reaches the op-amps directly. A 10–22 µF per rail at the op-amp cluster is cheap insurance. TI's minimum (0.1 µF at the pins) is met.
- **MFB input impedance:** 768 Ω, together with R<sub>F</sub>, loads the OPA1611 at about 580 Ω (4.9 mA peak). That is within its ratings. Scaling R66–R68/R70–R72 up and C77/C78/C80/C81 down by the same factor would reduce the load with negligible noise cost (re-check f<sub>0</sub> and Q).
- **LT3042 exposed pad:** the EP is GND and has no vias. Add 4–5 vias to In1 for a low-impedance ground; dissipation is ≤0.1 W, so this is not a thermal problem. The LT3094 EP is IN (−8 V) on a 124 mm² F.Cu pour; at about 0.2 W that is adequate.
- **BOM part specs:** the value fields carry no part specifications. Add:
  - **C0G** for C75–C82.
  - **0.1 % thin-film** for R60/R61 (thin-film, at least, for R66–R73).
  - **MLCC voltage ratings**, allowing for DC-bias derating: 22 µF on +8 V needs ≥16 V.
  - **Low-leakage electrolytics, with voltage rating,** for C13–C18. Leakage current flows into high-impedance reference nodes.
- **Smaller DAC-pin decouplers:** the 100 nF parts at the DAC pins are 3216 metric. Your newer 1608 metric standard part would shorten those loops.
- **Schematic notes out of date:**
  - The channel headers are swapped: the U1 chain is labelled "L" but produces OUT_R.
  - The preregulator note says 110 Ω / 590 Ω and 11.4 mA; the actual values are 240 Ω / 1.3 kΩ and 5.2 mA.
  - "D1–D4" should be D5–D8, and "C107" should be C19.
  - The R79–R82 note says "0R" but the parts are 22 Ω.
  - R75 is "10K" while R76 is "10k".
- **ERC cleanup:**
  - Add no-connect flags to (or bring out to pads) PA5–PA7 and PB0–PB3.
  - The `lib_symbol_mismatch` on U1/U2 is cosmetic. I compared all 20 pins and the pin maps are identical, so *Update symbols from library* is safe.
- **DF1704 RST pull-up:** its internal pull-up value is not specified. With R75 = 10 kΩ, confirm that DF_RST reads ≤0.8 V while the ATtiny is un-programmed or held in reset.
- **Stale fab outputs:** `production/` is dated 2026-09-28. Regenerate it before ordering.

---

## 4. Suggested bring-up measurements (in order)

1. **Rails and LT3094 temperature:** check ±8 V, +5 V, −5 V and +5VDF.
2. **Support-pin DC voltages:** measure REF, SERVO and BPO on each DAC. This confirms the electrolytic polarity and voltage margin.
3. **Output DC offset** per channel, before connecting the preamp. Expect up to ±57 mV worst case. This decides M1.
4. **BCLK/WCLK at the PCM1704 pins** with a ground spring: look for monotonic edges and no ringing near threshold, then tune the series resistors.
5. **I/V output settling:** check for ringing (this validates the 47 pF compensation, since the DAC's output capacitance is not specified).
6. **THD+N, noise floor and L→R crosstalk.** Measure crosstalk before and after the H2 fix to see whether it mattered.
7. **Power-on and power-off transients** at J1.

## 5. Not verified in this review

- **LT3042 (`Custom:LT3042`, DFN-10) and LT3094 (DFN-12) pin maps and land patterns.** analog.com refused scripted downloads.
  - The symbols are internally consistent.
  - The LT3094 PGFB→IN tie matches ADI's eval-board guidance.
  - Re-check both "Pin Functions" pages and confirm that the parts you have are the DD (DFN) variants.
- **PCM1704 speed grade (U / U-J / U-K) and package width** of the salvaged chips.
- **PCM1704 output capacitance:** not given in SBAS097, so the I/V phase margin is estimated, not calculated.
- **The I²S source board's drive strength and termination.**

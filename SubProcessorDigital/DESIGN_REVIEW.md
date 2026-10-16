# P68 Subwoofer DSP Controller — Engineering Review and Schematic Completion (Rev A)

Date: 2026-10-14. Applies to the KiCad 10 project `SubProcessorDigital` (6 sheets).

| State | Status |
|---|---|
| Schematic complete, connectivity verified | **Yes.** Every pin's connection was cross-checked against the intended design (591 pins / 147 nets) and every symbol pin was matched to a footprint pad. |
| KiCad ERC | **0 errors, 0 warnings, no exclusions added** (the 4 rule categories ignored by your original project settings are unchanged). |
| PCB layout | **Not started.** The existing `.kicad_pcb` holds the *old* netlist's footprints, unplaced. Run *Update PCB from Schematic* (F8) first. |
| KiCad DRC | **Not run.** It would be meaningless before placement and routing. |
| Simulated / bench-tested / thermally tested | **No.** |
| Fabrication-ready | **No.** See section 9. |

The previous state is preserved in git commit `aa2581f` ("SubProcessorDigital: snapshot before agent engineering review and completion").

---

## 1. Findings in the existing design

### Critical (would have stopped the board working, or defeated protection)

1. **Wrong TPS3850 variant.** `TPS3850G12QDRCRQ1` monitors a **1.2 V** rail with a ±4 % window (TI SBVS301B §11.1.1). Connected to 3.3 V, SENSE is permanently above the over-voltage threshold, so RESET would be held low forever.
2. **PROTECT sheet not connected to anything.** Its sheet symbol had no pins. WDI, RESET and WDO went nowhere, and the relay driver base was on a floating label (`AMP_ENABLE`).
3. **No flyback diode on the output-relay coil.** Q1 would avalanche every time the relay released.
4. **No hardware qualification of the relay.** One ESP32 GPIO stuck high would have kept the P68 connected.
5. **Input switching not implemented.** J1/J2 were unconnected, there were no input relays, and the `IN-LEFT`/`IN-RIGHT` labels were dangling.
6. **Net-name typos split power nets.** The DAC decoupling capacitors (C66/C69/C70/C71) were on `3V3-DAC` and the I²C pull-ups on `3V3-ESP` (hyphen instead of underscore). Both were isolated nets, so the DAC had only 1 µF on its supply and the I²C bus had no pull-ups.
7. **PCM1863 clock inputs floating.** SCKI and XI were both unconnected, and XI is OR-ed with SCKI internally (SLAS831D §9.3.9.4.1, register SCK_XI_SEL default = "SCK or XTAL"). The automatic clock detection, which needs SCK *halted* to enter BCK-PLL mode (Table 15), would have been unreliable.
8. **USB symbol and footprint mismatch.** A `USB_B` symbol was on a `Custom:USBC` footprint.
9. **J6 symbol and footprint mismatch.** A DIN41612 symbol (pins a1…b10) was on an IDC footprint (pads 1…20), so no nets would have reached the PCB.
10. **Three footprints had no library nickname** (`ESP32S3WROOM1UN16R8`, `SOP50P640X120-30N`, `DRC0010R`). The custom `DRC0010R` footprint also had thermal-via pads named "V" with no net, which DRC flags against the GND exposed pad.

### Important

- **Buck input capacitance too low:** 2 × 1 µF, against TI's requirement of ≥4.7 µF X7R rated ≈2×V<sub>IN</sub> plus 100 nF at the pins (SLUSEF4A §9.2.2.6).
- **PCM1863 decoupling below the datasheet:**
  - LDO pin: 2.2 µF, but TI specifies 0.1 µF + 10 µF.
  - AVDD and DVDD: no 10 µF.
  - VREF: 2.2 µF, but TI specifies 1 µF.
- **XSMT had no pull-down,** so the DAC mute state was undefined while the ESP32 was in reset.
- **ESP32 module:** the schematic used the **N16R8**. Modules with octal PSRAM (R8) are rated to **65 °C ambient**, whereas the **N8 is rated to 85 °C** (Espressif WROOM-1U datasheet v1.8, Table 1-2).
- **ESP32 3.3 V regulator:** the AMS1117 symbol was used where the stocked part is the TS1117B. Same pinout, but TS1117B requires 10 µF MLCC on input and output.
- **No reverse-polarity protection** on a header that also carries −15 V.
- **VBUS divider (10 k/10 k)** back-fed ≈0.4 mA into the ESP32 when the board is unpowered and USB is plugged in.
- **DAC full scale vs P68 sensitivity:** 2.1 Vrms full scale against the P68's 1.3 Vrms full-power sensitivity at ±56 V rails (ESP Project 68). A full-scale firmware error would drive the P68 about 4 dB into clipping.

### Retained because they were already correct

- **LMR51430XFDDCR (500 kHz forced-PWM)** with 6.8 µH, 2 × 22 µF and a 100 k/13.7 k divider, exactly as in TI Table 9-1. FPWM avoids audio-band PFM bursts at light load.
- **TPS7A2033 LDOs.**
- **PCM5102A hardware straps:** FLT = 1 (low-latency), DEMP = 0, FMT = 0 (I²S), SCK = GND (BCK-PLL).
- **TI's ADC input network:** 10 µF + 100 Ω + 10 nF.
- **AGN2004H relays** with 16 Ω coil resistors.
- **Output relay arrangement:** NC → 1 k → GND, plus 100 k on COM.
- **Other parts:** USBLC6-2SC6, EN/BOOT buttons, and the I²S pin choices (IO7/9/10/11/38).

---

## 2. Changes made, with justification

The sheet structure is preserved (root, POWER, AUDIO-IN, ADCESPDAC, PROTECT), and **CONTROL** is added. Existing reference designators and symbol UUIDs are kept where the part remains. Supply rails are now global power symbols (`+15V`, `+5V`, `+3V3_ESP`, `+3V3_DAC`, `+3V3_A_ADC`, `+3V3_D_ADC`, `+3V3_UI`). Signals between sheets use hierarchical pins.

### POWER sheet

| Change | Why |
|---|---|
| **F1** C1F 3 A (inventory) and **D1** 1N5819 (inventory) in series with +15 V | Protects against a −15/+15 V harness swap and against harness faults. D1 drops ≈0.35 V at 0.18 A (≈60 mW). |
| C99/C100 → **10 µF/50 V X7R 3216** (Samsung CL31A106KBHNNNE, inventory), **C109 100 nF/50 V** added at VIN | Meets TI's input capacitor requirement. |
| C33/C34 specified as **22 µF/25 V** (CL31A226KAHNNNE, inventory) | TI's Table 9-1 assumes 25 V parts (DC-bias derating). |
| **R23/C110** and **R24/C111** (4R7 + 22 µF) RC pre-filters ahead of the DAC and ADC-analogue LDOs | f<sub>c</sub> ≈ 1.5 kHz, about 50 dB extra rejection at 500 kHz, with no ferrite beads. Drop is <0.1 V at 20 mA. |
| U6 → **TS1117BCW33** (inventory) with 10 µF in and out | Matches the stock part and its datasheet requirement. |
| **U8 TPS7A2033 → +3V3_UI** for the daughterboard | A ribbon-cable short or ESD event cannot pull down the ESP32 rail (TPS7A20 current limit is 160 mA). |
| **U15 AP2205-50Y-13 (SOT-89, 24 V max) from +15V → +5V_UI** on J6 pin 20, with 1 µF in, 1 µF + 10 µF out | Clean 5 V for a 5 V display (its own level shifter): no buck ripple or relay steps, and a ribbon fault cannot pull down the main +5V. Dissipation 10 V × I: keep the display ≤50 mA (0.5 W). The module's ESP32-side I²C pull-ups must go to 3.3 V (or be removed). J6 pin 1 remains +3V3_UI. |
| Test points on every rail and two GNDs | Bench measurement. |

### AUDIO-IN sheet (new circuitry)

- **K2** (AGN2004H) switches the signal poles. Each ADC channel COM is fed from PRE_L/PRE_R (NC) or LFE (NO). In LFE mode the same LFE signal goes to both channels.
- **K3** (AGN2004H) switches the source ground. COM = board GND, NC = PRE_GND, NO = LFE_GND, with both poles in parallel.
- **Only the selected source's hot and ground touch the board.** The unselected source is fully open-circuit, so there is no high-impedance leakage path for Class-II/Y-capacitor ground currents.
- **R25/R26 4k7 thin-film** sit between relay COM and the ADC input chain. With the PCM1863's 10 kΩ input this gives −3.3 dB (full scale 3.1 Vrms). They also limit ESD-diode current to <2 mA at 10 Vrms; TI's absolute limit is 5 mA. Alternatives: 0 Ω for 2.1 Vrms full scale, or 10 k for 4.2 Vrms.
- **Bleed resistors R7/R8 (100 k) stay on the ADC side, referenced to board GND,** so no resistor bridges an unselected source to GND. During relay transfer, the COM node is held via R25/R26 → R7/R8.
- **Drivers:** BC546 (inventory), 1 k base resistor, 16 Ω coil resistor, and a 1N4148W across each coil with correct polarity (pin 1 + on this polarised GN coil).
- **R31 100 k** pulls INPUT_SEL low, which keeps ESP32 strap GPIO45 low at reset. If it were high, VDD_SPI would switch to 1.8 V and the flash would not boot.

### ADCESPDAC sheet

**ADC (PCM1863)**

- XI tied to DGND.
- SCKI held low by R33 100 k (BCK-PLL slave mode). R32 22R is a DNP option to feed ESP32 MCLK (IO9) if BCK-PLL mode proves unsatisfactory.
- LDO pin: **10 µF + 100 nF**. AVDD and DVDD: **100 nF + 10 µF**. VREF: **1 µF**.
- C3/C4 specified **C0G**, since TI asks for film-type.
- R3/R4 specified thin-film.
- DOUT has a 22R source-termination resistor (R37).

**DAC (PCM5102A)**

- Each supply pin has its own 100 nF + 10 µF.
- XSMT pull-down R40 100 k.
- OUTR left open, which the datasheet permits. Unused R14/C26 removed.
- **Output-level trim R38 2 k / R39 6k8 (thin film).** Into the P68's 22 kΩ this gives **1.42 Vrms full scale**, just above the P68's 1.3 Vrms full power at ±56 V. Load on the DAC is 7.7 kΩ against a 1 kΩ minimum, and the source impedance is 1.7 kΩ. If your P68 runs ±70 V rails (2.0 Vrms needed), fit R38 = 0 Ω and leave R39 unfitted.

**Output relay K1**

- Pole A is unchanged: NO = filtered DAC, NC → R19 1 k → GND, COM → J5 with R20 100 k.
- Pole B is new: relay-state feedback to IO3 (R41 pull-up).
- The coil now has a flyback diode D4.
- The coil is now switched by **two BC546 in series**: Q1 driven by the fault latch, Q4 driven by the AUDIO_READY level. This is a hardware AND that also survives a single shorted transistor.

**ESP32**

- Value changed to **ESP32-S3-WROOM-1U-N8** (inventory). Same footprint and pinout.
- IO35–37 left unused, so the N8R8 also fits.
- 3V3 decoupling is 22 µF + 100 nF, per Espressif.
- C5 reduced to 100 nF. R44 470 Ω limits the TPS3850 RESET sink current, which drives EN.

**USB**

- Correct USB-B footprint (On Shore USB-B1HSxx). Stock `USB_B` symbol, whose shield pin matches the footprint.
- 0 Ω placeholders on D±, per Espressif.
- Shield → 1 MΩ ∥ 4.7 nF/100 V.
- VBUS sense divider changed to 100 k/100 k, which cuts back-feed to ≈25 µA.

**I²S**

- 22 Ω source terminations at the ESP32 (R34/R35/R36).
- I²C1 is kept separate from the ADC's I²C0, so a display or ribbon fault cannot lock up ADC control.

### PROTECT sheet (rebuilt)

- **U7 TPS3850H01DRCR**, the adjustable (0.4 V), under-voltage-only variant. The 22 k/3k3 divider trips at **3.07 V**: above the ESP32-S3 minimum of 3.0 V, and 165 mV below TS1117B's worst-case minimum of 3.235 V. A G33 variant would trip at 3.168 V, only ≈66 mV from the rail minimum, so LDO load transients risk false resets.
  - Watchdog: SET0 = 0, SET1 = 1, CWD = 10 k gives a window of 10.35 ms (max lower) to 165.8 ms (min upper). CRST open gives a 200 ms reset/WDO pulse.
  - WDI has a 100 k pull-down, so no edges occur while the GPIO is high-Z.
  - **RESET → ESP32 EN. WDO → FAULT_N only.** The ESP32 boots for longer than any useful window, so tying WDO to EN would cause a reset loop.
- **Rail supervisors (TPS3808).** The SENSE input is independent of VDD, so a *dead* rail is still reported as a fault.
  - **U9 G01** monitors +15 V at 11.3 V (270 k/10 k + 10 nF) for early power-fail warning.
  - **U10–U12 G33** monitor the DAC, ADC-A and ADC-D rails at 3.07 V.
  - All outputs are open-drain on **FAULT_N** (10 k pull-up). The symbol pin type was corrected to open-collector to match the datasheet.
- **D5 1N4148W** makes a TPS3850 supply reset also pull FAULT_N low (≈0.6 V, below the 74AUP V<sub>IL</sub> of 0.9 V).
- **U13 SN74AUP1G74 fault latch** (Schmitt inputs, so slow open-drain edges are fine):
  - CLR = FAULT_N, D = 1, CLK = AUDIO_READY, Q → Q1.
  - Q becomes 1 only on an AUDIO_READY *rising edge* while FAULT_N is high.
  - **A stuck-high GPIO produces no new edge, so after any fault the relay stays open** until firmware deliberately drops and re-raises AUDIO_READY.

### CONTROL sheet (new)

- **J6, 2×10 shrouded IDC.** Pinout (ribbon order): 1 +3V3_UI, 2 GND, 3 SDA, 4 GND, 5 SCL, 6 GND, 7 E1A, 8 E1B, 9 E1SW, 10 GND, 11 E2A, 12 E2B, 13 E2SW, 14 GND, 15 E3A, 16 E3B, 17 E3SW, 18 GND, 19 LED, 20 **+5V_UI** (for a 5 V display; see below). Each I²C wire is flanked by grounds.
- **Encoder conditioning on the main board,** using Bourns' recommended PEC11R filter: 10 k pull-up, 10 k series, 10 nF. With the daughterboard unplugged, all inputs sit at defined idle-high levels.
- **I²C1:** 100 Ω series resistors plus 4k7 pull-ups to +3V3_ESP.
- **12 V trigger:**
  - J7 → 4k7 → **Vishay TCMT1107** optocoupler (CTR 80–160 % at 5 mA, 3750 Vrms). LED current is ≈2.3 mA at 12 V.
  - 1N4148W reverse clamp (LED V<sub>R</sub> max 6 V) and a 10 k LED shunt for noise immunity.
  - Collector has a 10 k pull-up and 10 nF to GND, feeding IO47.
  - The trigger side has **no** connection to board GND.
- **Status LED and UART:** status LED on IO46, with a 1 k feed to the front panel via the ribbon. UART0 debug header J8.
- **Four M3 mounting holes,** unconnected.

### Libraries

- New **project-local library `SPD`**: `SubProcessorDigital.kicad_sym`, `SubProcessorDigital.pretty`, plus `sym-lib-table` and `fp-lib-table`. It holds the custom symbols and the five custom footprints actually used. This removes the dependency on `~/Downloads/Custom.pretty` and the unconfigured `SubController` library.
- The TPS3850 now uses KiCad's stock `VSON-10-1EP_3x3mm_P0.5mm_EP1.65x2.4mm`, which matches TI's DRC0010J land pattern: 2.4 × 1.65 mm exposed pad, 0.5 mm pitch.

---

## 3. Engineering assessment

### Source switching and ground isolation

- **What's connected in each mode:** in each mode exactly one source ground is bonded to board GND, through K3 near the ADC. The other source is open-circuit on both hot and ground.
- **Switching sequence** (firmware): ramp down → XSMT low → AUDIO_READY low (K1 opens) → switch K2/K3 → wait ≥200 ms for C1/C2 settling and ADC fade-in → load preset → re-arm → XSMT high → ramp up.
- **Relay timing:** K2 and K3 are break-before-make with ≤4 ms operate/release times. During the transfer the ADC sees ≤ a few mV from source DC offsets, and the output is already disconnected.
- **Input impedance seen by each source:** ≈13.9 kΩ (4.7 k + 100 k ∥ 10.1 k). Fine for any solid-state preamp; check if your preamp is valve-based with high output impedance.
- **Low-frequency corner:** 10 µF with ≈10 kΩ gives 1.6 Hz.
- **DC bias on C1/C2:** ≈1.65 V (ADC inputs bias to AVDD/2), so the bipolar electrolytic is appropriate.

### Clocking

- **Configuration:** the ESP32-S3 is I²S0 full-duplex master (BCK 3.072 MHz = 64 fs, LRCK 48 kHz). The PCM1863 runs as a slave in BCK-PLL mode (SCKI held static) and the PCM5102A uses its internal BCK-PLL. ADC and DAC are therefore synchronous by construction.
- **Jitter:** ESP32-S3 fractional dividers add deterministic jitter. For a ≤200 Hz output, the jitter-induced error is negligible (≈−118 dB at 100 Hz for ~2 ns rms).
- **Fallbacks if measurement disagrees:** fit R32 to feed MCLK (256 fs). Alternatively, a future revision can make the PCM1863 master from a crystal.

### Latency (fixed part only; excludes the intended group delay of crossover, high-pass and all-pass filters)

**Latency ≈ (10 ADC + 3.5 DAC) samples + N (RX block) + D·N (TX queue)**

| DMA frame size N | TX descriptors D | Estimate |
|---|---|---|
| 32 | 2 | ≈110 samples = **2.3 ms** |
| 16 | 2 | ≈62 samples = **1.3 ms** |

Both meet the 1–3 ms target. **Measure** with a loop-back pulse (scope on TP11–TP17).

Phase alignment cannot make the subwoofer *earlier*. The all-pass and polarity controls can only add delay or phase lag, so the main-speaker path cannot be compensated. State this in the UI.

### DSP capacity at 48 kHz

The signal is summed to mono first, then processed through ≈16 biquads (LR4/LR8 low-pass, 2–4th-order high-pass, 6 PEQ, 2 all-pass) plus delay, volume and limiter. That is ≈500–700 cycles/sample with ESP-DSP f32 biquads, or ≈25–35 M cycles/s: about 15 % of one 240 MHz core. Comfortable. Keep the audio task and buffers in internal RAM (no PSRAM needed, which supports choosing the N8).

### Protection — fault matrix

| Fault | Detected by | Hardware action | Recovery |
|---|---|---|---|
| +15 V loss / brown-out | U9 (< 11.3 V) | FAULT_N ↓ → latch cleared → K1 opens. C6 holds +5 V ≈18 ms at full load; K1 releases in ≤4 ms (+ diode-extended decay, measure) | Automatic latch hold-off; firmware must re-arm |
| 3.3 V ESP rail UV | U7 RESET | ESP32 held in reset, latch cleared (via D5), AUDIO_READY ↓ (R53) | After 200 ms; firmware re-arms |
| DAC / ADC-A / ADC-D rail UV or dead | U10 / U11 / U12 | Latch cleared | Firmware reads IO42, logs, re-arms when good |
| Firmware hang / stalled audio task | U7 watchdog (no WDI kick in 165.8 ms) | WDO 200 ms pulse → latch cleared | ESP32 internal WDTs reset the CPU; re-arm after boot |
| Runaway fast loop | U7 window (kick < 10.35 ms) | As above | As above |
| GPIO stuck high (AUDIO_READY) | No new rising edge after any fault | K1 stays open | Hardware repair |
| One relay driver transistor shorted | Other series transistor still switches | K1 still controllable | Flag via IO3 relay-sense mismatch |
| Board unpowered | — | K1 de-energised → P68 input grounded via 1 k | — |
| Clock loss (I²S) | PCM5102A clock-halt auto-mute; DMA stall stops WDI kicks | Soft mute, then latch clear | Firmware |
| Corrupted / large audio | **Not caught by hardware** | Firmware limiter; R38/R39 limit FS to ≈1.4 Vrms | — |

### Power budget and dissipation (estimates, verify on the bench)

| Item | Load | Dissipation |
|---|---|---|
| +5 V total (ESP32 ≤250 mA peak, ADC 25 mA, DAC 20 mA, UI ≤30 mA, relays 3 × 29 mA) | ≈0.45 A peak | Buck input ≈0.18 A at 15 V |
| U6 TS1117B (ESP32) | 0.1–0.25 A | 0.17–0.43 W. Give the SOT-223 tab ≥2 cm² of copper. **Thermal check needed** |
| U1 / U4 / U5 / U8 TPS7A2033 | 10–30 mA | ≤50 mW each |
| D1 1N5819 | 0.18 A | ≈60 mW |
| 16 Ω coil resistors | 29 mA | 13 mW (125 mW part) |

**Relay coil margin:** coil voltage is ≈4.2–4.35 V, against a must-operate of 3.38 V at 20 °C. At 70 °C ambient, coil resistance rises about 20 %, and the drive current is still ≈24 mA against ≈23.3 mA pick-up current. **Margin is thin above about 60 °C ambient.** If the controller will run that hot, fit 0 Ω in place of R22/R27/R29: the coil then sees ≈103 % of nominal, well within the 150 % maximum.

### GPIO map (ESP32-S3)

| GPIO | Function |
|---|---|
| IO1 | DAC_XSMT |
| IO2 | WDI (watchdog kick) |
| IO3 | Output-relay sense (input) |
| IO4 / IO5 / IO6 | ENC1 A / B / SW |
| IO7 | I²S DIN (from ADC) |
| IO8 | ENC2 SW |
| IO9 | MCLK (optional) |
| IO10 | BCK |
| IO11 | LRCK |
| IO12 / IO13 | I²C0 SDA / SCL (ADC) |
| IO14 / IO21 | I²C1 SDA / SCL (UI) |
| IO15 / IO18 | ENC2 A / B |
| IO16 | AUDIO_READY |
| IO17 | VBUS sense |
| IO19 / IO20 | USB D− / D+ |
| IO38 | I²S DOUT (to DAC) |
| IO39 / IO40 / IO41 | ENC3 A / B / SW |
| IO42 | FAULT_N (input) |
| IO43 / IO44 | UART0 TX / RX |
| IO45 | INPUT_SEL (strap: low at reset) |
| IO46 | STATUS_LED (strap) |
| IO47 | MODE_TRIG_N |
| IO48 | ADC_INT |
| IO35–37 | Unused (PSRAM on R8 parts) |
| IO0 | BOOT |

---

## 4. Unresolved concerns (decisions or checks for you)

1. **USB-B part.** The inventory lists an unlabelled "USB-B header". The footprint is the On Shore **USB-B1HSW6**; check your part against it, or buy the OST part.
2. **PCM5102 vs PCM5102A.** Inventory says "PCM5102". Pinout and strapping are identical; confirm the marking.
3. **Output-level trim (R38 series, R39 = 6k8 shunt to GND) — an attenuator so the DAC's 2.1 Vrms full scale cannot drive the P68 hard into clipping.** P68 gain is 23; its full-power input is ≈1.3 Vrms at ±56 V and ≈2.0 Vrms at ±70 V (ESP), scaling roughly with rail voltage. Values below give a full scale ≈5–10 % above full power (into the P68's 22 kΩ, with R13 470 Ω). All are standard 2012 metric thin-film parts; keep R39 = 6k8.

   | P68 rails | Full-power input (approx.) | R38 | Resulting DAC full scale |
   |---|---|---|---|
   | ±35 V | 0.81 Vrms | 6k8 | 0.88 Vrms |
   | ±40 V | 0.93 Vrms | 5k6 | 0.97 Vrms |
   | ±45 V | 1.04 Vrms | 3k9 | 1.14 Vrms |
   | ±50 V | 1.16 Vrms | 3k3 | 1.22 Vrms |
   | ±56 V (fitted) | 1.30 Vrms | 2k2 or 2k (stock) | 1.39 / 1.42 Vrms |
   | ±63 V | 1.62 Vrms | 560R | 1.75 Vrms |
   | ±70 V | 2.0 Vrms | 0R, R39 DNP | 2.1 Vrms |

   Intermediate rails: pick the next row up (lower rail = larger R38). The full-power figures are estimates; confirm by measuring the P68's clipping input level on your build. The firmware limiter should still set the working ceiling.
4. **The +15 V source.** If it is unregulated or sags below ≈12 V under load, raise the U9 trip point by reducing R51.
5. **No spares.** The inventory has **one** ESP32-S3-WROOM-1U-N8 and **one** LMR51430XFDDCR. Buy spares, or use the N8R8 as fallback (it fits, but only to 65 °C).
6. **USB ground loop.** Accepted: USB is for configuration only; run the Mac on battery when connected to avoid any loop.
7. **BCK-PLL clock quality** (PCM1863 slave) is untested. R32 provides the MCLK fallback.
8. **Relay release time with a plain diode clamp** has not been measured. If muting needs to be faster, consider a diode + 12 V zener clamp (BC546 V<sub>CEO</sub> = 65 V).
9. **Through-hole parts** (BC546, AGN2004H, 1N5819, C1/C2/C6, connectors) suit hand assembly; JLCPCB charges extra for through-hole assembly.
10. **Daughterboard display pull-ups:** many OLED modules include their own I²C pull-ups. Combined with R56/R57 the bus is ≈2.4 kΩ, which is fine.
11. **Stale 3D model paths** in the custom footprints (cosmetic only).

---

## 5. Bill of materials

The full grouped BOM is generated from the schematic: `SubProcessorDigital-BOM.csv` (99 lines, 212 placed parts; R32 is DNP).

### 5.1 Confirmed in inventory (quantity needed / in stock)

**ICs, modules and electromechanical**

| Part | Use | Need / stock |
|---|---|---|
| ESP32-S3-WROOM-1U-N8 | IC1 | 1 / 1 |
| PCM5102 (confirm "A") | U2 | 1 / 2 |
| LMR51430XFDDCR | U3 | 1 / 1 |
| TPS7A2033 | U1, U4, U5, U8 | 4 / 14 |
| TS1117B (3.3 V, SOT-223) | U6 | 1 / 11 |
| USBLC6-2SC6 | IC3 | 1 / 7 |
| Panasonic AGN2004H | K1–K3 | 3 / 6 |
| ST BC546 | Q1–Q4 | 4 / 36 |
| onsemi 1N4148W | D2–D5, D7 | 5 / 67 |
| Diotec 1N5819 | D1 | 1 / 13 |
| Kingbright KP-2012EC red LED | D6 | 1 / 10 |
| Bel C1F 3 A fuse | F1 | 1 / 21 |
| Same Sky TS02-66-50 buttons | IC4, IC5 | 2 / 16 |
| Bourns SRP6030WA-6R8M | L3 | 1 / 5 |

| Multicomp MC34631 3-way header (fits the 1×3 2.54 mm footprint) | J8 | 1 / 40 |

**Capacitors**

| Part | Use | Need / stock |
|---|---|---|
| KEMET C1206C104K5RACTU 100 nF/50 V, 3216 metric | — | 18 / 129 |
| Samsung CL31B105KBHNFNE 1 µF/50 V, 3216 | — | 10 / 50 |
| Samsung CL21A106KOQNNNF 10 µF/16 V, 2012 | — | 7 / 32 |
| Samsung CL31A106KBHNNNE 10 µF/50 V, 3216 | C99, C100 | 2 / 10 |
| Taiyo Yuden TMK316B7106KL 10 µF/25 V, 3216 | C107, C108 | 2 / 50 |
| Samsung CL31A226KAHNNNE 22 µF/25 V, 3216 | — | 5 / 19 |
| Samsung CL21B225KPFNNNE 2.2 µF, 2012 | C18, C20 | 2 / 63 |
| Walsin 0805N103J500CT 10 nF C0G, 2012 | — | 12 / 38 |
| Walsin 0805B103K500CT 10 nF, 2012 | C119 | 1 / 30 |
| Walsin 0805N272J500CT 2.7 nF C0G | C25 | 1 / 14 |
| Walsin 0805N472J101CT 4.7 nF/100 V C0G | C117 | 1 / 9 |
| Panasonic EEUFR1V102 1000 µF/35 V (FR) | C6 | 1 / 12 |
| Nichicon UES1H100MPM 10 µF bipolar | C1, C2 | 2 / 10 |

**Resistors (all 2012 metric)**

| Value | Type | Need |
|---|---|---|
| 10 k | KOA 5 % | 25 |
| 10 k | 0.1 % thin | 2 |
| 100 k | thick | 9 |
| 100 k | thin 0.5 % | 3 |
| 4k7 | Stackpole 1 % | 5 |
| 4k7 | Yageo 0.1 % thin | 2 |
| 1 k | thick | 6 |
| 22R | — | 4 (+1 DNP) |
| 16R | Stackpole | 3 |
| 4R7 | — | 2 |
| 100R | thin | 2 |
| 100R | thick | 2 |
| 470R | Susumu thin | 1 |
| 470R | thick | 1 |
| 2 k | Susumu thin | 1 |
| 6k8 | Susumu thin | 1 |
| 22 k | Susumu thin | 1 |
| 3k3 | — | 1 |
| 13k7 | — | 1 |
| 270 k | — | 1 |
| 1 M | thin | 1 |
| 680R | thin | 1 |
| 0R | — | 2 |

No values are made from series or parallel combinations.

### 5.2 To purchase (suggested suppliers: DigiKey UK, Mouser UK, Farnell/CPC)

| Qty | Part | Use |
|---|---|---|
| 1 (+1 spare) | TI **PCM1863QDBTRQ1** (Mouser 595-PCM1863QDBTRQ1), or commercial-grade PCM1863DBTR | IC2 ADC |
| 1 (+1) | TI **TPS3850H01DRCR** | U7 supervisor/watchdog |
| 1 | TI **TPS3808G01DBVR** | U9 +15 V monitor |
| 3 | TI **TPS3808G33DBVR** | U10–U12 rail monitors |
| 1 (+1) | TI **SN74AUP1G74DCUR** | U13 fault latch |
| 1 | Vishay **VO617A-3** (DIP-4, being purchased) | U14 trigger opto |
| 1 | On Shore **USB-B1HSW6** (unless your stocked USB-B matches) | J3 |
| 1 | 2×10 2.54 mm shrouded box header, e.g. Würth 61202021621 | J6 |
| 2 + 3 | JST **B3B-XH-A** (J1, J4) and **B2B-XH-A** (J2, J5, J7), plus XHP-3/XHP-2 housings and SXH-001T-P0.6 crimps | Connectors |
| Spares | ESP32-S3-WROOM-1U-N8, LMR51430XFDDCR | Only one of each in stock |
| Optional | ADuM4160-based USB isolator (external dongle) | Listening with a Mac attached |
| 4 | M3 spacers and screws | Mounting |

---

## 6. Footprints and part numbers (key items)

| Ref | Part | Footprint | Package (metric) |
|---|---|---|---|
| IC1 | ESP32-S3-WROOM-1U-N8 | `SPD:ESP32S3WROOM1UN16R8` (common to all WROOM-1U) | 18 × 19.2 mm module |
| IC2 | PCM1863QDBTRQ1 | `SPD:SOP50P640X120-30N` | TSSOP-30, 0.5 mm pitch |
| U2 | PCM5102APWR | `Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm` | TSSOP-20 |
| U3 | LMR51430XFDDCR | `Package_TO_SOT_SMD:SOT-23-6` | SOT-23-THIN-6 (DDC) |
| U1/U4/U5/U8 | TPS7A2033PDBVR | `Package_TO_SOT_SMD:SOT-23-5` | SOT-23-5 |
| U6 | TS1117BCW33 | `Package_TO_SOT_SMD:SOT-223-3_TabPin2` | SOT-223 |
| U7 | TPS3850H01DRCR | `Package_SON:VSON-10-1EP_3x3mm_P0.5mm_EP1.65x2.4mm` | VSON-10 (DRC0010J) |
| U9–U12 | TPS3808Gxx DBVR | `Package_TO_SOT_SMD:SOT-23-6` | SOT-23-6 |
| U13 | SN74AUP1G74DCUR | `Package_SO:VSSOP-8_2.3x2mm_P0.5mm` | VSSOP-8 (DCU) |
| U14 | VO617A-3 | `Package_DIP:DIP-4_W7.62mm` | DIP-4 through-hole |
| K1–K3 | AGN2004H | `SPD:Relay_DPDT_Panasonic_AGN2004H` | Verified against Panasonic pattern: 3.2 mm rows, 3.2/2.2/2.2 mm pitch |
| L3 | SRP6030WA-6R8M | `SPD:SRP6030WA-6R8M` | 6.6 × 7.1 mm |
| Q1–Q4 | BC546 | `Package_TO_SOT_THT:TO-92_Wide` | TO-92 (C-B-E) |
| J3 | USB-B | `Connector_USB:USB_B_OST_USB-B1HSxx_Horizontal` | Through-hole |
| J6 | 2×10 header | `Connector_IDC:IDC-Header_2x10_P2.54mm_Vertical` | Shrouded |
| Passives | — | 2012 metric (R, small C), 3216 metric (100 nF/1 µF/10–22 µF stock parts) | — |

---

## 7. ERC / DRC results

- **ERC:** 0 errors, 0 warnings, 0 exclusions (KiCad 10.0.5 `kicad-cli sch erc --severity-all`). Problems were fixed at source rather than suppressed:
  - Open-drain supervisor outputs are now typed open-collector.
  - PWR_FLAGs added on the RC-filtered LDO inputs.
  - Project-local library resolves all symbols.
- **Connectivity verification:** the KiCad netlist matches the recorded design intent for all 591 pins in 147 nets. Each net was also reviewed by hand.
- **Footprint check:** every symbol pin has a matching footprint pad, and there are no orphan pads.
- **DRC:** not applicable yet (no layout).

---

## 8. Commissioning and fault-injection tests

1. **Bare-board power (no ICs except regulators, current-limited bench supply at 15 V / 200 mA):**
   - Check the rails at TP1–TP7.
   - Check the buck switch node (500 kHz, no PFM) and the +5 V ripple.
   - Reverse the supply: D1 must block.
2. **Supervisors:**
   - Sweep +15 V down: FAULT_N (TP18) should fall at ≈11.3 V.
   - Pull each 3.3 V LDO down through a resistor until it trips: FAULT_N ≈3.07 V; for +3V3_ESP, SUP_RST_N/EN (TP19/TP24).
   - Short each LDO output to GND (current-limited): the corresponding monitor must report it.
3. **Latch logic (ESP32 fitted, test firmware):**
   - AUDIO_READY edge → TP20 high → K1 closes; IO3 reads low.
   - Hold AUDIO_READY high and stop WDI: within ≤224 ms WDO pulses, TP20 falls, K1 opens and **stays open**.
   - Kick WDI faster than 10 ms: the window fault must also open K1.
   - Short TP21 to 3V3 (stuck GPIO) and inject a fault: K1 must stay open.
4. **Power-down thump test:** P68 connected to a dummy load and scope. Pull the +15 V plug while playing; there must be no transient at the P68 input (TP17). Repeat by switching off the source mains.
5. **Input switching:**
   - Measure the ground isolation: PRE_GND ↔ LFE_GND resistance must be ≥ MΩ in both modes, with the board powered and unpowered.
   - Check mode-change pops at the P68 (should be none: muted).
6. **ADC/DAC performance:**
   - Noise floor and THD at 1 kHz and 50 Hz.
   - Confirm BCK-PLL lock (PCM1863 registers 0x72/0x75).
   - Clipping at ≈3.1 Vrms input.
7. **Latency:** pulse into the preamp input, scope TP11-referenced I²S and the P68 input. Record the fixed latency for N = 16 and N = 32.
8. **Thermal:** 1 hour at maximum activity (CPU 240 MHz, all relays on). Measure U6, U3, L3 and relay coil temperatures.
9. **Trigger input:** 0 / 5 / 12 / 15 V and reverse polarity on J7. Check the MODE_TRIG_N thresholds and confirm isolation (≥ MΩ to GND).

---

## 9. Remaining work before ordering PCBs

1. Open the project in KiCad. Confirm the project library tables (SPD) load, then run **Update PCB from Schematic** (F8) with "delete footprints with no symbol" and "replace footprints with changed lib ID".
2. Choose the stack-up. **A 4-layer board is recommended** (L1 components/critical routing, L2 continuous GND, L3 power, L4 slow signals); the existing file is 2-layer.
3. **Floorplan:**
   - Inputs and relays K2/K3 at one edge → ADC → ESP32 (module edge, no antenna keep-out needed for the 1U) → DAC → K1/J5 at the opposite edge.
   - Buck converter in a corner, away from the ADC and inputs.
   - Trigger opto at the board edge with ≥2 mm clearance.
4. **Layout rules:**
   - C109 at U3 VIN/GND; compact SW node; FB away from L3.
   - Decoupling at the pins.
   - Short I²S runs with 22R terminations at the ESP32.
   - Relay coil return currents kept out of the ADC ground area.
   - TS1117B tab copper.
5. Run DRC, check the 3D view, review the board against this document, then generate Gerbers and BOM/CPL for JLCPCB.
6. Order the purchase list (5.2), including spares.

## 10. Firmware requirements implied by the hardware

- **Keep IO45 low at boot** (R31 provides this) and never drive IO46 high during download mode.
- **Mute/unmute sequences:**
  - Startup: configure the PCM1863 over I²C: SCK_XI_SEL = SCK only, slave mode, low-latency IIR, inputs VINL1/VINR1, single-ended.
  - Start I²S full duplex.
  - Start kicking WDI from the audio task only after verifying DMA timing and sane ADC data.
  - Read FAULT_N (IO42) = 1.
  - Rising edge on AUDIO_READY; confirm IO3 is low within 10 ms.
  - After 20 ms, XSMT high; then ramp the volume.
- **Mode change:** follow the 8-step sequence in the brief, using AUDIO_READY low as step 3.
- **Limiter and DC/subsonic high-pass are mandatory.** Hardware cannot catch corrupted samples.
- **Wi-Fi/BT disabled.** The audio task is pinned to one core at high priority with buffers in internal RAM; non-blocking I²C, UI and flash work runs on the other core.

## 11. Datasheets and references used

- TI PCM1863 — SLAS831D (Mar 2018): pin table, full-scale/impedance, clocking (Table 5, Table 15), input filter (§10.1.5), power-up.
- TI PCM5102A — SLAS859C (May 2015): pin table, XSMT timing, filter latency, application circuit, power-down.
- TI TPS3850 — SBVS301B (Sep 2021): variants (§11.1.1), timing table (§6.6), divider table 8-6, DRC0010J land pattern.
- TI TPS3808 — SBVS050N: thresholds (Table 4-1), DBV pinout, SENSE vs VDD.
- TI SN74AUP1G74 — SCES644D: Schmitt inputs, DCU pinout, function table.
- TI LMR51430 — SLUSEF4A: device comparison (XF = 500 kHz FPWM), V<sub>FB</sub> 0.6 V, Table 9-1, input capacitor guidance.
- TI TPS7A20 — SBVS338H: ROC, C<sub>OUT</sub> range, PSRR, DBV pinout.
- Taiwan Semiconductor TS1117B — I2405: pinout, 10 µF MLCC, dropout.
- Espressif ESP32-S3-WROOM-1/1U datasheet v1.8: variants and temperature, pin table, strapping pins, peripheral schematic.
- Panasonic GN relays — ASCTB13E (2026): AGN2004H coil data, timing, PCB pattern, pinout.
- Vishay TCMT110x — doc 83510: pinout, CTR groups, ratings.
- Bourns PEC11R: suggested filter circuit. Bourns SRP6030WA: ratings and land pattern.
- ESP Project 68 (sound-au.com/project68.htm): 22 kΩ input, gain 23, 1.3 Vrms full power at ±56 V.

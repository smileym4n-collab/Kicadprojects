# ESPUSBI2S rev 2 — design notes

Status: **schematic drawn and ERC-checked; footprints created. Not simulated, PCB not updated, nothing bench tested.**
The original working design is preserved in Git commit `74e3b2c` (and the existing `ESPUSBI2S.kicad_pcb` is untouched and now out of step with the schematic).

Files

| File | Content |
|---|---|
| `ESPUSBI2S.kicad_sch` | Stand-alone board: connectors only + the block |
| `USB_AUDIO_UAC2.kicad_sch` | Reusable parent sheet |
| `USB_INTERFACE` / `ESP32_UAC2` / `AUDIO_CLOCK` / `OUTPUT_INTERFACE` `.kicad_sch` | The four functional sheets |
| `ESPUSBI2S.kicad_sym`, `ESPUSBI2S.pretty/` | Project-local symbols and footprints |
| `docs/ESPUSBI2S_rev2_schematic.pdf` | Plot of all six sheets |
| `docs/BOM_rev2.csv` | BOM with MPNs and both population columns |
| `docs/ERC_rev2.rpt` | ERC report |

---

## 1. GPIO mapping, old vs new

Source of truth: the original schematic (netlist of commit `74e3b2c`) and the firmware in `~/Documents/GitHub/ESP32S3I2S`.

| Function | GPIO | WROOM-1U pin (old) | PICO-1 pin (new) | Changed? |
|---|---:|---:|---:|---|
| I2S BCLK | 4 | 4 | 9 | no |
| I2S LRCK | 5 | 5 | 10 | no |
| I2S DATA | 6 | 6 | 11 | no |
| Oscillator select (LOW = 22.5792 MHz) | 7 | 7 | 12 | no |
| I2C SDA (COMM header) | 8 | 12 | 13 | no |
| I2C SCL (COMM header) | 9 | 17 | 14 | no |
| ATtiny status UART TX | 10 | 18 | 15 | no |
| VBUS detect (active HIGH) | 13 | 21 | 18 | no |
| External MCLK input | 15 | 8 | 21 (pad name `XTAL_32K_P`) | no |
| MUTE (active HIGH) | 16 → **35** | 9 | 40 | **yes** |
| F3 | 17 → **36** | 10 | 41 | **yes** |
| F2 | 18 → **37** | 11 | 42 | **yes** |
| F1 | 38 | 31 | 43 | no |
| F0 | 39 | 32 | 44 (pad name `MTCK`) | no |
| USB D− | 19 | 13 | 25 | no |
| USB D+ | 20 | 14 | 26 | no |
| BOOT | 0 | 27 | 5 | no |
| U0TXD / U0RXD | 43 / 44 | 37 / 36 | 49 / 50 | no |
| EN / CHIP_PU | — | 3 | 4 | no |

Three GPIO numbers change (MUTE, F3, F2); everything else is identical. Every PICO-1 pad number was taken from Table 2-1 of the PICO-1 datasheet v1.2, not from the QFN or WROOM numbering.

**Why MUTE/F3/F2 moved to GPIO35/36/37.** The firmware defaults (`Kconfig.projbuild`, `Pinout.MD`) already put them there; the original PCB used GPIO16/17/18 only because GPIO35-37 are taken by the octal PSRAM on its N16R8 module. On the PICO-1-N8R2 (quad PSRAM) GPIO35-37 are free, and they are the better choice:

- Espressif's power-up glitch table lists a ~60 us glitch on GPIO16 and GPIO17 (low) and GPIO18 (low and high). GPIO35-39 are not in that table, so MUTE cannot dip and F2 cannot pulse at power-up.
- The new board then runs the firmware's default pin configuration with no changes.

Consequences: the existing WROOM board keeps needing its 16/17/18 override, and an N8R8 version of the PICO-1 must never be substituted (octal PSRAM takes GPIO33-37). GPIO16/17/18 are now unconnected spares.

Sample-rate code F3..F0 (from firmware, unchanged): 0001 = 44.1 kHz, 0010 = 48 kHz, 0011 = 88.2 kHz, 0100 = 96 kHz, 0000 = inactive/muted.

Connector pin-outs are unchanged: J1 (GND, GND, LRCK, DATA, BCLK, MCLK), J2 (RX, TX, 3V3, F0, F1, F2, F3, MUTE, GND, GND), J3 (GND, +5 V), J5 (GND, D−, D+, CC, CC, VBUS), J6 (GND, SDA, SCL, UART).

---

## 2. Component change summary

| Was | Now | Reason |
|---|---|---|
| ESP32-S3-WROOM-1U-N16R8 | ESP32-S3-PICO-1-N8R2 | requested |
| 74LVC1G157GW + 5PB1102PGGK | Si53307-B-GM | requested |
| ASE-series oscillators | ASELJ-E-22.5792MHZ-L-R-T, ASELJ-E-24.576MHZ-L-R-T | requested |
| LD1117S33 (one rail for everything) | AP7361C-33SP-13 (`3V3_MCU`), TPS7A2033PDBVR (`3V3_CLK`), TPS7A2033PDBVR (`3V3_ISO`) | requested |
| — | ISOUSB211DPR + 0R bypass + ground bridge | requested |
| 100k/100k VBUS divider straight into GPIO13 | Config A: ISOUSB211 `V1OK`. Config B: 33k/47k divider + 74LVC1G17 | see §6 |
| C8 220 µF on 3V3 | removed | 22 µF MLCC specified for the AP7361C output; nothing on the new rail needs the reservoir |
| HandSolder passive footprints | standard 1608 / 2012 / 3216 metric footprints | compact board; same packages |

Additions that were not in the original and not explicitly requested — please confirm or strike:

1. **MUTE pull-up 2k2 to 3V3_MCU** (R40). The original had none, so MUTE was pulled low by the LED during reset, i.e. un-muted. With the LED and its 2k2 fitted the header sits at about 2.6 V in reset; without the LED it is 3.3 V.
2. **10k pull-downs on F0–F3** (R42/44/46/48), so the code is 0000 during reset instead of floating at an LED forward voltage.
3. **499R in U0TXD** (R20), per the Espressif guideline.
4. **22R at each oscillator output** (R24/R26), the `Rs` in Si5330x Fig. 2.2. Marked tune.
5. **SFOUT strap footprints to GND** (R34/R36, DNP), so the output drive strength can be changed on the bench.
6. **74LVC1G17** in the non-isolated VBUS detector (one in stock, low stock).

Decisions that differ from the starting values in the brief:

- **MCLK series resistors are 33R, not 22R.** Si5330x Table 2.7 recommends 33R for the 12/18/24 mA LVCMOS settings (0R for 6 mA). The straps select 12 mA (SFOUT = 1,1), which is the setting the datasheet's LVCMOS jitter figures are specified at.
- **One shared VDD/2 divider (1k/1k + 100n) biases both CLK0b and CLK1b.** Fig. 2.2 shows one divider per input. A shared, bypassed reference is how the family's own VREF pin is used, but it is a deviation; splitting it costs two resistors and a capacitor.
- **No ferrite bead in VBUS** (TI shows one as optional).
- **USB D+/D− capacitor footprints to ground at the MCU are not provided** (Espressif suggests reserving them; the original board works without).

---

## 3. Population tables

Config A = isolated (as drawn). Config B = non-isolated. Never mix the two link sets.

| Parts | Function | A (isolated) | B (non-isolated) |
|---|---|---|---|
| U1 | ISOUSB211DPR | FIT | DNP |
| C2, C3 | VBUS1/VCC1 decoupling 4u7, 100n | FIT | DNP |
| C4 | V3P3V1 100n | FIT | DNP |
| C5–C10 | V1P8V1 2u2/100n/10n ×2 | FIT | DNP |
| C11, C12 | VBUS2/V3P3V2/VCC2 100n, 1u | FIT | DNP |
| C15–C20 | V1P8V2 10n/100n/2u2 ×2 | FIT | DNP |
| U3, C13, C14 | 3V3_ISO regulator, 10u out, 4u7 in | FIT | DNP |
| R1, R2 | 0R links, connector → UD−/UD+ | FIT | DNP |
| R3, R4 | 0R links, DD−/DD+ → MCU | FIT | DNP |
| R11 | 0R, V1OK → VBUS_DET | FIT | DNP |
| R5, R6 | 0R bypass links, connector end | DNP | FIT |
| R7, R8 | 0R bypass links, MCU end | DNP | FIT |
| R9, R10 | 0R ground bridge GND_USB ↔ GND | DNP | FIT |
| R13, R14, C21 | VBUS divider 33k / 47k, 10n | DNP | FIT |
| U4, C22 | 74LVC1G17 + 100n | DNP | FIT |
| R15 | 0R, buffer → VBUS_DET | DNP | FIT |
| U2, C1, R12 | USBLC6-2SC6, VBUS 100n, VBUS_DET pull-down 100k | FIT | FIT |
| R34, R36 | SFOUT strap-low options | DNP | DNP |
| everything else | | FIT | FIT |

USB VBUS is not connected to the local 5 V rail in either configuration.

ISOUSB211 pin configuration (Fig. 8-6, checked pin by pin): VBUS1 + VCC1 = USB VBUS; V3P3V1 = internal LDO output, 100n; V1P8V1 pins 4 and 11 joined, 2u2 + 100n + 10n at each; VBUS2 + V3P3V2 + VCC2 = 3V3_ISO; V1P8V2 pins 25 and 18 joined, same decoupling; CDPENZ1 → V3P3V1 and CDPENZ2 → 3V3_ISO (charging-port advertising off); EQ10/EQ11 → GND_USB, EQ20/EQ21 → GND (no equalisation, short traces); V2OK unused; NC pins open.

---

## 4. Regulator current and thermal calculations

Input taken as 5.25 V worst case, 5.0 V typical.

### 3V3_CLK — TPS7A2033PDBVR (RθJA 187 °C/W, JEDEC board)

| Load | Typ | Max / bound | Source |
|---|---:|---:|---|
| Si53307 core IDD | 65 mA | 100 mA | Table 3.3 |
| Si53307 LVCMOS outputs (Q0, Q0b, Q1, Q1b all toggle) | ~5 mA | 80 mA | Datasheet gives 20 mA per output at 200 MHz/5 pF; ~5 mA is a C·V·f estimate at 24.576 MHz with ~15 pF |
| 2 × ASELJ | 10 mA | 20 mA | 5 typ / 10 max each at 3.3 V |
| VDD/2 divider, pull-ups | 2 mA | 2 mA | |
| **Total** | **~82 mA** | **~202 mA** | |

- Typical: (5.0 − 3.3) × 0.082 = 0.14 W → +26 °C.
- Upper bound: (5.25 − 3.3) × 0.202 = 0.39 W → +74 °C. That is Tj ≈ 99 °C at 25 °C ambient and ≈ 124 °C at 50 °C, against a 125 °C limit.
- **Flag:** inside the 300 mA rating, but the bound has no thermal margin in a warm enclosure. The bound uses the 200 MHz output figure, which overstates a 24.576 MHz clock several-fold; a more realistic maximum (100 + 8 + 20 + 2 = 130 mA) gives 0.25 W, +47 °C. Measure the rail current and regulator temperature on the first board. Both oscillators running continuously is included.
- Capacitors: 10 µF/10 V X7R 2012 derates to roughly 6–7 µF at 3.3 V; the device needs ≥ 0.47 µF effective and accepts up to 200 µF. 4.7 µF/16 V 2012 at 5 V is roughly 3 µF effective against a recommended ≥ 0.47 µF. Check the actual DC-bias curve of the parts bought.

### 3V3_ISO — TPS7A2033PDBVR (config A only)

- Full-speed operation: ≤ 15.3 mA (V3P3V2) + 0.55 mA (VCC2) ≈ 16 mA → 0.03 W, +6 °C.
- If the link ever ran high-speed: 13.5 + 96 = 110 mA → 0.21 W, +40 °C. The ESP32-S3 is full-speed only, so this is not expected.
- ISOUSB211 itself at full speed: about 16 mA from VBUS and 16 mA from 3V3_ISO, roughly 0.14 W, +6 °C at 44 °C/W.

### 3V3_MCU — AP7361C-33SP-13 (θJA 100 °C/W on the datasheet test board)

- ESP32-S3 with the radio never started: datasheet Table 3-8 gives up to about 56 mA at 80 MHz; I did not extract the 240 MHz rows, so I have assumed ≤ 110 mA. LEDs, pull-ups and the buffer add about 6 mA.
- 120 mA: (5.25 − 3.3) × 0.12 = 0.23 W → +23 °C.
- If firmware ever enabled Wi-Fi, peaks of about 350 mA are still inside the 1 A rating.
- Output capacitor 22 µF/16 V X7R 3216 (EMK316BB7226ML-T): expect roughly half at 3.3 V; the regulator needs ≥ 2.2 µF.
- **Flag:** the datasheet does not state in words that the SO-8EP exposed pad is ground. The U-DFN drawing labels it GND and the thermal note refers to vias to the ground plane, so the pad is connected to GND.

---

## 5. Clocking

- Y1 22.5792 MHz → CLK0, Y2 24.576 MHz → CLK1. `CLK_SEL` LOW = CLK0, with a 10k pull-down: same polarity as the original (GPIO7 LOW = 22.5792 MHz), so `AUDIO_OSC_SELECT_INVERT` stays off.
- Q0 → 33R → ESP32 GPIO15 (external MCLK in). Q1 → 33R → J1 pin 6. Outputs are not paralleled. Q0b and Q1b are left open as the datasheet requires; in LVCMOS mode they still toggle.
- OE is pulled up (always enabled). Oscillator OE pins are pulled up with 10k (always running).
- The mux is glitchless, but its output stops low for up to three cycles of the new clock while switching, and `CLK_SEL` must not be toggled faster than 1/250 of the slower input. The firmware's existing mute → switch → 500 ms settle → reconfigure sequence covers this.
- Test pads: both oscillator outputs (after their series resistor), selected MCLK, CLK_SEL, 3V3_CLK. The pads on the oscillator lines add capacitance to clock nets; keep them small and adjacent in layout, or omit after bring-up.

---

## 6. VBUS detection

GPIO thresholds (PICO-1 datasheet): VIH ≥ 0.75 × VDD, VIL ≤ 0.25 × VDD.

**The original 100k/100k divider is marginal.** It gives 2.5 V at 5.0 V and 2.2 V at 4.4 V, against a VIH of 2.48 V at VDD = 3.3 V. It works on the bench because real thresholds sit near mid-rail, but it is not guaranteed.

Config A — `V1OK`:
- High only when VBUS1 is above its UVLO (rising threshold 4.0 V, falling 3.6 V per the table) and the side-1 1.8 V rail is up. Push-pull, VOH ≥ V3P3V2 − 0.2 V at 3 mA, powered from 3V3_ISO, which comes up and goes down with 3V3_MCU, so there is no back-feed path.
- When side 1 is unpowered the DD± pins go high-impedance, so the MCU also sees the bus disappear.
- Conclusion: V1OK is suitable and no optocoupler is fitted. **Not specified by TI:** V1OK response time and behaviour during a slow VBUS ramp. Verify attach/detach on the bench before deleting the option of an opto from your mind entirely.

Config B — divider + Schmitt buffer:
- 33k/47k (ratio 0.588): 4.35 V → 2.56 V, 5.5 V → 3.23 V at the buffer input.
- SN74LVC1G17 at 3 V: VT+ 1.48–1.92 V, VT− 0.89–1.2 V. Referred to VBUS: detects present by about 3.3–3.6 V rising, releases by about 1.5–2.0 V falling.
- The buffer has Ioff and 5.5 V-tolerant inputs, so nothing is injected into 3V3_MCU when local power is off. The MCU sees a clean logic level.
- The divider returns to local GND, which is correct only because the ground bridge is fitted in this configuration. R13 (33k) is the part that physically bridges the barrier gap; it is DNP when isolated.
- A plain divider straight into GPIO13 would also work and saves the IC, at the cost of about 60 µA into the unpowered MCU rail. Say if you would rather have that.

Both sources are active HIGH on the same net, selected by R11 or R15. R12 (100k) holds the line low if neither is fitted.

---

## 7. Footprints and symbols created

| Item | Basis | Notes |
|---|---|---|
| `ESP32-S3-PICO-1_LGA-56-1EP_7x7mm_P0.4mm` | Datasheet Fig. 6-1: e 0.4, b 0.20, L 0.325, EP 4.0 × 4.0 | Lands 0.20 × 0.65 mm with 0.2 mm toe outside the body; 3 × 3 paste windows (62 %); four 0.3 mm ground vias. **Espressif publishes no land pattern in this datasheet — the land extension is my choice.** |
| `Si53307_QFN-16-1EP_3x3mm_P0.5mm_EP1.8x1.8mm` | Datasheet Table 7.1 exactly | 2 × 2 paste openings of 0.65 mm on 0.9 mm pitch as specified |
| `Abracon_ASELJ_3.2x2.5mm` | Recommended land pattern: 1.2 × 1.0 pads, 2.2 × 1.6 pitch | Pin 1 OE, 2 GND, 3 OUT, 4 Vdd |
| `ISOUSB211_DP0028A_SSOP-28_7.5x10.3mm_P0.65mm` | TI DP0028A-C02, IPC-7351 standard pattern: 2.0 × 0.45, 9.3 mm row centres | Differs from your existing `Custom:ISOUSB211` (2.0 × 0.40 at 8.93 mm). TI also shows an 8.2 mm-clearance variant with 1.65 mm pads. |
| `TS026650BK100SCRD` | Copied unchanged from your `Custom.pretty` | No longer used on the schematic (switches removed, see §12); left in the project library |
| AP7361C | Stock `Package_SO:Diodes_SO-8EP` | Pins 1 OUT, 2 EN, 4 GND, 8 IN, pad 9 |

Symbols use the manufacturer's pin numbers and names; pins are grouped by function for readable wiring.

---

## 8. ERC

`kicad-cli sch erc --severity-all`: **0 errors, 1 warning.**

- `lib_symbol_mismatch` on J4: the `USB_B` symbol embedded in the original schematic has a numbered shield pin (5) to suit the `Custom:USBC` footprint and so differs from the stock library. Inherited from the original, left as it was, not excluded.

Three things were fixed rather than suppressed during the work: PWR_FLAGs that clashed with the connector's power-output pins, a duplicated net name on the MUTE/F lines (the output sheet now taps those nets instead of passing them through), and a dependency on the global `Custom` symbol library.

A clean ERC says the drawing is consistent. It does not say the hardware works.

---

## 9. Firmware changes needed

None of the application code needs rewriting. Configuration only:

1. Pin configuration: none for the new board - the Kconfig defaults (MUTE 35, F3 36, F2 37, F1 38, F0 39) match it. The existing WROOM board still needs 16/17/18 for MUTE/F3/F2, so keep that as a separate board profile.
2. New board profile for the PICO-1-N8R2: 8 MB quad flash; PSRAM either disabled or configured as 2 MB quad SPI (not octal). Remove the octal-PSRAM pin-conflict guard for this profile, or make it conditional.
3. The radio must never be initialised (LNA_IN is open).
4. VBUS detect, oscillator-select polarity, I2S pins, external-MCLK configuration, UART0 and the ATtiny UART are unchanged.
5. With the new MUTE pull-up the DAC is muted from power-on until firmware drives the pin; the firmware already drives it HIGH first, so behaviour only improves.

Checked against the firmware source: external MCLK via `I2S_CLK_SRC_EXTERNAL` on GPIO15, 32-bit Philips slots, feedback endpoint (FIFO-count method), four sample rates. Whether the feedback is accurate enough for bit-perfect playback over long runs is a firmware measurement, not something the schematic can show.

---

## 10. Outstanding questions and verification tasks

Decisions for you:

1. ~~MUTE/F3/F2 pin choice~~ - decided: GPIO35/36/37 (see section 1).
2. Keep the six additions listed in §2?
3. Shared or separate VDD/2 dividers for CLK0b/CLK1b?
4. 74LVC1G17 detector, or a plain divider, for config B?
5. Keep the five LEDs on a 40 × 30 mm target? (The tactile switches have been removed, see §12.)
6. ISOUSB211 land pattern: TI standard (as drawn) or your existing proven footprint?

To verify before ordering:

7. PICO-1 land pattern against an Espressif reference design or module footprint.
8. AP7361C SO-8EP exposed-pad potential, with Diodes or by continuity on a part.
9. ESP32-S3 240 MHz supply current from Table 3-8.
10. DC-bias curves of the chosen 4.7 µF, 10 µF and 2.2 µF parts.
11. Availability of ASELJ-E-22.5792MHZ-L-R-T; the datasheet lists 24.576 MHz in its jitter table but not 22.5792 MHz explicitly.
12. ISOUSB211 stock is zero in the inventory.

To measure on the first board:

13. 3V3_CLK current and regulator temperature (§4).
14. MCLK edges at the ESP32 pin and at the DAC with 33R; try the 6 mA / 0R option if overshoot or EMI is a problem.
15. Spur at the unselected oscillator frequency on MCLK (both oscillators run continuously).
16. V1OK timing on attach, detach and host suspend.
17. Enumeration in both configurations, and with local power applied before and after USB.
18. MUTE level at the DAC during reset with your XMOS-side input loading.

Layout items carried forward (not started): 90 Ω pair geometry on the JLCPCB stack-up, barrier gap on all four layers under U1, where R5/R6 and R13 straddle the gap, ground-bridge position next to the USB pair, decoupling placement for the 1.8 V pins (TI recommends 1005-metric parts on the top layer without vias; 1608 are drawn), thermal copper for U6 and U7, shield/chassis strategy.

---

## 11. Inventory pass (2026-11-15)

Part fields were edited in place (Value, Footprint, MPN, Description only); wiring and your own edits (J5, R51, R52 removed) are untouched. Because footprints changed, run **Update PCB from Schematic** again.

From stock:

| Value | Refs (count) | Stock part | Package | In stock | Change from previous draft |
|---|---|---|---|---:|---|
| 100n | 20 | MC0603B104K500CT, X7R 50 V | 1608 | 961 | none |
| 10n | C7 C10 C15 C18 C21 (5) | 0805B103K500CT, X7R 50 V | 2012 | 13 | 1608 → 2012 |
| 2u2 | C5 C8 C17 C20 (4) | CL21B225KPFNNNE, X7R 10 V | 2012 | 54 | 1608 → 2012 |
| 1u | C12 C29 C31 C34 C37 (5) | C0805C105K3RACTU, X7R 25 V | 2012 | 87 | 1608 → 2012 |
| 4u7 | C2 C14 C32 (3) | CL21A475KAQNNNE, **X5R** 25 V | 2012 | 37 | X7R → X5R |
| 10u | C13 C23 C25 C33 (4) | TMK316B7106KL-TD, X7R 25 V | 3216 | 43 | 2012 → 3216 |
| 220u | C42 | EEUFR1C221B, Panasonic FR 16 V | 6.3 mm radial | 10 | none |
| 22R | 9 | RK73B1JTTD220J, 5 % | 1608 | 139 | R29/R30 were 33R |
| 10k | 12 | RC0603FR-0710KL | 1608 | 53 | none |
| 1k | R27 R28 | RC0603FR-101KL | 1608 | 99 | none |
| 2k2 | 6 | RC0603JR-072K2L, 5 % | 1608 | 37 | none |
| 1M | R50 | RC0603FR-101ML | 1608 | 90 | none |
| 470R | R20 | ASC0805-470RFT5 | 2012 | 86 | was 499R 1608 |
| 33k / 47k / 100k | R13 / R14 / R12 | MCWR08X3302FTL / RMCF0805FT47K0 / RK73B2ATTE104J | 2012 | 100 / 93 / 44 | 1608 → 2012 |
| Red LED | D1–D5 | Kingbright KP-2012EC | 2012 | 9 | part now named |
| TPS7A2033PDBVR | U3 U7 | — | SOT-23-5 | 6 | none |
| USBLC6-2SC6 | U2 | — | SOT-23-6 | 5 | none |
| 74LVC1G17 | U4 (config B only) | — | SOT-23-5 | 1 | none |

Still to buy: ESP32-S3-PICO-1-N8R2, Si53307-B-GM, both ASELJ oscillators, AP7361C-33SP-13, ISOUSB211DPR (stock is 0), EMK316BB7226ML-T (22 µF). JST XH connectors and plain pin headers are not tracked in the inventory.

Points to note:

- **MCLK series resistors are now 22R** (your original starting value, in stock) instead of the 33R Skyworks tabulates for the 12 mA drive setting; there is no SMD 33R in stock. Both are bench-tune values. If the edges ring, 33R is the first thing to try. This supersedes the 33R statements in sections 2 and 5.
- **U0TXD resistor is 470R** rather than Espressif's suggested 499R. The difference is immaterial.
- **4.7 µF parts are X5R, not X7R.** They are regulator-input and VBUS bulk capacitors, where X5R is fine. Effective capacitance at 5 V is roughly half; the TPS7A20 needs 0.47 µF.
- **10 µF moved to 3216 X7R 25 V**, which holds its capacitance at 3.3 V far better than a 2012 part. This improves the regulator-output margins in section 4.
- **ISOUSB211 1.8 V decoupling is now 2012 for the 2.2 µF and 10 nF** (100 nF stays 1608). TI recommends the smallest practical parts placed on the top layer without vias, so this makes placement around pins 3/4, 11/12, 17/18 and 25/26 harder. Put the 100 nF closest to each pin.
- **0R links are KOA RK73Z2ATTD, 2012, from stock (64 held, 16 positions)**, changed from the 1608 RC0603JR-070RL in the brief at your request. This applies to the USB path links, the ground bridge, the VBUS_DET source links and the SFOUT straps. The larger pads add a little stub capacitance on D+/D-, which is harmless at full speed.
- **22 µF stays as the agreed EMK316BB7226ML-T.** In stock you have GRM21BR61A226ME51K (22 µF X5R 10 V, 2012, 39 pcs), or two TMK316B7106KL-TD in parallel would do the job from stock.
- **The red LEDs will be dim.** KP-2012EC is specified at 20 mA; with 2k2 it runs at about 0.6 mA. Lower the LED resistors only on the F lines if you want more light; on MUTE the 2k2 values set the reset-state level.

## 12. RESET and BOOT switches removed

SW1 (RESET) and SW2 (BOOT) are deleted to save board area (2 × 6 × 6 mm tactile switches).

- **BOOT** is now J7, a 2-pin 2.54 mm header between GPIO0 and GND (same net as TP5). Fit a shunt, apply power, and the chip starts in ROM download mode; flash over USB, remove the shunt, power-cycle.
- **RESET** is a power cycle. The CHIP_PU network (R16 10k, C31 1u) is unchanged and TP4 remains on CHIP_PU, so it can still be shorted to GND on the bench.
- A blank chip needs no jumper: the ROM enables USB Serial/JTAG and esptool enters download mode over USB.
- In the isolated build the ESP is powered from the local 5 V input, so "power cycle" means that supply, not the USB cable.
- GPIO0 keeps its 10k pull-up (R17). J7 must not be left shunted in normal use.
- No firmware change. Not bench tested.

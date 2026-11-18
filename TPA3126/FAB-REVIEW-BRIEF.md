# TPA3126 board: fabrication-readiness review brief

**For:** a Claude session on a machine with KiCad 10 installed.
**Task:** review the whole TPA3126 design (schematic **and** PCB) and decide whether it is ready to order. Report findings; do not fix them.
**Design state:** the latest `TPA3126` commit on `main`. This includes the Rev C note, title-block and part-field update of 18 Nov 2026, which sits on top of the owner's `a67670d`. Run `git log -3 -- TPA3126` first and note the commit you reviewed.
**Prepared by:** the Claude session that did the firmware port and first-board bring-up (ESP32SnapAudioClient repo, branch `tpa3126`).

Start the session in the `Kicadprojects` folder and tell Claude:

> Read TPA3126/FAB-REVIEW-BRIEF.md and carry out the review it describes.

---

## 1. Ground rules

1. **Read-only.** Do not edit any `.kicad_sch`, `.kicad_pcb`, `.kicad_pro`, `.kicad_sym`, footprint or library file. Do not open the project in the KiCad GUI and save it. The owner makes every change.
2. **Do not run anything in `review/scripts/`.** These are historical editing scripts, not a build pipeline (see `review/README.md`).
3. Write all output to `review/fab-readiness-2026-11-18/` (create it):
   - `REPORT.md`: the verdict and findings (format in section 9)
   - `erc.json`, `drc.json`, `netlist.xml`, `bom.csv`: raw tool output
   - Gerber/drill test exports go to a temporary folder outside the repo. Do not commit them.
4. Commit nothing unless the owner asks.
5. The owner's hardware rule: no bodge wires or patched copper. Any fix must be a schematic/PCB change for this order.
6. Mark each finding as **verified** (you checked the file, tool output or datasheet) or **suspected**. Quote the evidence.

## 2. Tools

`kicad-cli` is usually at `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`. Run `kicad-cli version`, and `--help` for each subcommand, because flags differ between versions. Run from `TPA3126/`:

```bash
kicad-cli sch erc --format json --severity-all -o review/fab-readiness-2026-11-18/erc.json TPA3126.kicad_sch
kicad-cli pcb drc --schematic-parity --severity-all --format json -o review/fab-readiness-2026-11-18/drc.json TPA3126.kicad_pcb
kicad-cli sch export netlist --format kicadxml -o review/fab-readiness-2026-11-18/netlist.xml TPA3126.kicad_sch
kicad-cli sch export bom -o review/fab-readiness-2026-11-18/bom.csv TPA3126.kicad_sch
kicad-cli pcb export gerbers -o /tmp/tpa3126-gerbers/ TPA3126.kicad_pcb
kicad-cli pcb export drill -o /tmp/tpa3126-gerbers/ TPA3126.kicad_pcb
```

**Datasheets** are in `review/datasheets/`; the `.txt` copies are searchable. These are not there yet, so fetch them:
- DMP4025LSD: https://www.diodes.com/datasheet/download/DMP4025LSD.pdf. Pinout: 1 S1, 2 G1, 3 S2, 4 G2, 5-6 D2, 7-8 D1. VGS ±20 V, VDS −40 V.
- SMBJ20A (Littelfuse)
- 1N4740A

Do not trust the old `review/REVIEW-REPORT.md`, `PURCHASING-LIST.md` or `INVENTORY-USAGE.md`. They describe earlier revisions.

## 3. What the board is

An ESP32-WROVER-IE-N16R8 Snapcast/Bluetooth speaker endpoint:
- I2S drives a PCM5122 DAC (I2C control), which feeds a TPA3126D2 stereo BTL class-D amp.
- The DSP does an active crossover: LEFT is the tweeter (J17), RIGHT is the woofer (J16).

**Power:** DC in, 19 V maximum.
- Input path: fuse, then a back-to-back dual P-FET (reverse block, soft start, switch to GND turns it on), giving PVDD.
- PVDD feeds the TPA3126 directly.
- PVDD also feeds the LMR51430 buck (`5V_PRE`), then the TLV1117LV33 LDO (`3V3-ESP`), plus the DAC's own LDO (IC4).

**The first PCB of this design was built and brought up.** Its failures drive most of the checks in section 6.

## 4. Decisions that are final (do not report these as defects)

- **TPA3126:**
  - MODSEL tied to GND (Hybrid modulation).
  - AM0/AM1/AM2 tied to GND (400 kHz).
  - GAIN/SLV R18 5.6k to GND (master, 20 dB).
  - SYNC (pin 16) unconnected.
- **PLIMIT (U1 pin 6) tied directly to GVDD (pin 7):** no power limit. This is the TI datasheet method. The old 3V3 → R19 → PLIMIT feed was removed deliberately.
- **19 V maximum input:** SMBJ20A TVS, 20 V stand-off.
- **DMP4025LSD-13** is "not recommended for new design". Accepted: it is stocked at Digi-Key.
- 1N4740A gate zener in through-hole DO-41: it is in the owner's inventory.
- The ESP32 GPIO assignments in section 5 are fixed by the firmware.
- **The PCM5122 circuit is unchanged from the first board.** There it acknowledged at I2C 0x4C after a solder rework and configured correctly.
- **R24 = 13k7 on purpose:** `5V_PRE` = 0.6 × (1 + 100k/13k7) ≈ 4.98 V. U3 did not start with the original 16k2 (4.30 V). Do check that every load on `5V_PRE` is within its input limit at 5.0 V plus tolerance: U4 TLV1117LV33, the DAC LDO IC4, and the 5V_PRE capacitors.
- **U4's MPN fields disagree** (`TLV1117LV33DCYR` vs `TS1117B`). The owner knows which part they will fit. Ignore this.
- **J1 pin 10 (PWR_SW):** sits near PVDD (up to 19 V) when the switch is open, on the same connector as 3V3 logic. Accepted: the connector is keyed.
- **No always-on jumper:** the board needs the J1 harness switch to power on. Intended.
- **Blank MPNs:** C29, C46, C48, R23, R24 and R27 have their MPN fields deliberately blank. The old MPNs were the wrong package for the footprints. List them under "MPN to choose" in the BOM section, not as defects. Do check the value, footprint and voltage rating noted in each part's Assembly_Note.
- **Firmware** still warns above 16.5 V (`SUPPLY_MAX_V`). It will be changed later and is out of scope here.

## 5. Firmware contract: these must match exactly

Source: `ESP32SnapAudioClient/include/board_config.h` (branch `tpa3126`). Module pin numbers are ESP32-WROVER pads. Check each row in the schematic **and** in the PCB pad nets.

| Function | GPIO | WROVER pin | Net (current schematic) | Board-side expectation |
|---|---|---|---|---|
| I2S BCK | 26 | 11 | BCK via R5 22R | to PCM5122 BCK |
| I2S LRCK | 25 | 10 | LRCK via R4 22R | to PCM5122 LRCK |
| I2S DATA | 13 | 16 | DATA via R9 22R | to PCM5122 DIN |
| DAC SDA | 21 | 33 | SDA | R33 4k7 pull-up to 3V3-ESP |
| DAC SCL | 19 | 31 | SCL | R31 4k7 pull-up to 3V3-ESP |
| DAC XSMT | 18 | 30 | DAC_XSMT | R32 10k pull-down (DAC muted at reset) |
| Amp SDZ | 27 | 12 | AMP_ENABLE → AMP_SDZ | 10k series + 100 nF, 100k pull-down (amp off at reset) |
| Amp MUTE | 23 | 37 | AMP_MUTE_CMD → AMP_MUTE | 10k series + 100 nF, R29 100k pull-up (muted at reset) |
| Amp FAULTZ | 35 | 7 | AMP_FAULT_N | R30 100k pull-up (input-only pin) |
| PVDD sense | 36 | 4 | VIN_SENSE | R27 100k / R28 10k (÷11): 19 V gives 1.73 V |
| Volume pot | 34 | 6 | VOL-ADC | R39 10k / R41 22k divider, C58 100 nF |
| Mode button | 22 | 36 | MODE BTN | active low, R35 10k pull-up |
| Wi-Fi LED | 32 | 8 | WIFI_LED via R8 1k | active high, off-board via J1 |
| BT LED | 33 | 9 | BT_LED via R7 1k | active high, off-board via J1 |
| Boot / reset | 0 / EN | 25 / 3 | GPIO0, EN | R11/R10 10k pull-ups, EN 1 µF; buttons IC3/IC2 |
| UART | TX0/RX0 | 35/34 | TX, RX | J4 PROG: **GND, RX, TX only, no 3V3** |

Also check: GPIO12 (pin 14, a strapping pin that sets flash voltage) and GPIO2/GPIO15 are not pulled to a level that breaks boot. WROVER pins 17–22 and 27–28 must stay unconnected: they are the flash/PSRAM lines.

## 6. Lessons from the first board: confirm each one is fixed

| # | First-board problem | What to verify now |
|---|---|---|
| 1 | GVDD (U1 pin 7) collapsed to 0.7–0.8 V. PLIMIT was fed from 3V3, above GVDD+0.3 V abs max. | PLIMIT pin 6 connects only to GVDD. Nothing else is on the GVDD net except C28 (1 µF X7R) and pins 6/7. |
| 2 | C28 (GVDD) was 17 mm from U1. | C28 within ~3 mm of pin 7, GND side to pin 9 / PowerPAD with a short return. Report the distance. |
| 3 | PVCC decoupling far from the pins | C33/C34 (100 nF) and bulk caps beside the PVCC pin pairs 17-19 and 31-32. Report the distances. |
| 4 | Film input caps C1/C2/C5/C6 melted during rework near U1/heatsink | Distance from the input caps to U1 and to the HS1 footprint/keep-out |
| 5 | DAC I2C failed: SDA/SCL held at 0.3–1 V. Cause: solder residue at U2, aggravated by SCL running 35 mm beside LRCK. | I2C (SDA/SCL) is on B.Cu, I2S (BCK/LRCK/DATA) on the bottom inner layer, top inner layer is solid GND. Check spacing between I2C and I2S traces; no I2C trace parallel to I2S over a split or void. Report the worst-case parallel run and gap. |
| 6 | A serial adapter back-powered the 3V3 rail and the DAC through the PROG header | J4 has no 3V3 pin (confirmed in the current netlist: GND/RX/TX). |
| 7 | GND-tied amp pins | The owner's rule: pins tied to GND stay tied in copper. Check MODSEL, AM0-2 and pin 9 go straight to the ground plane. |

## 7. Power entry: expected circuit

This was designed in the bring-up session and pasted from `Kicadprojects/PowerIn/PowerIn.kicad_sch`. The references changed when it was pasted.

| Net | Should contain |
|---|---|
| J3 pin 1 → F1 pin 1 | DC +, T3.15A time-delay fuse |
| VIN_F | F1 pin 2, Q2 pins 7, 8 (D1) |
| VS | Q2 pin 1 (S1), Q2 pin 3 (S2), R36 100k, D3 1N4740A **cathode**, D4 SMBJ20A **cathode**, C29 100 nF |
| GATE | Q2 pin 2 (G1), Q2 pin 4 (G2), R36, D3 anode, R19 47k, D5 1N4148W **cathode**, R37 1M |
| NSS | D5 anode, R37, C43 220 nF |
| PVDD | Q2 pins 5, 6 (D2), C43, all PVDD loads |
| PWR_SW | R19 and J1 pin 10. A switch to GND turns the board on. |

**Values:** R36 100k, R19 47k, R37 1M, C43 220 nF 50 V X7R, D3 10 V zener, D4 SMBJ20A, D5 1N4148W.

**How it works:**
- Closing the switch pulls GATE low through R19. D3 clamps the gate to 10 V.
- C43 through D5 gives an output ramp of roughly 13–15 ms. Inrush is about 1 A into roughly 680 µF at 19 V.
- D5 blocks the C43 feedback path at turn-off, so the FETs switch off fast.

**Check:**
- Q2 drain copper is sized for about 3 A.
- D4 is close to Q2 with a short GND return.
- C43/D5/R37 are close to Q2 pin 4.
- Q2 SOIC-8 thermal: about 0.1 W per FET at 2 A. Each FET is 25 mΩ max.
- PVDD voltage ratings at 19 V plus surge: the SMBJ20A clamps at 32.4 V at full pulse current.
  - The 220 µF electrolytics are 35 V. Confirm C35/C36/C47.
  - Every ceramic on PVDD/VS must be 50 V. Check MPNs, not just values.
  - TPA3126 is 26 V recommended max, 30 V abs max.
  - LMR51430 is 36 V max.

## 8. Full checklist

### Schematic (every sheet)
- ERC: 0 errors. Explain every warning or mark it harmless.
- Every component has a footprint. The footprint package matches the MPN's package. Look for 0603 MPNs on 0805/1206 footprints and the reverse.
- Value matches MPN, e.g. resistor value against the value encoded in the part number.
- Voltage rating for the net each capacitor sits on, with derating: X5R/X7R DC-bias where it matters (C45, C49, C50, C43).
- No floating inputs. Check unconnected pins against datasheets, including on U2 (PCM5122), U1 pin 16, IC4 and IC5.
- PCM5122: confirm the mode/address pins give I2C at address **0x4C**, as the firmware expects. Confirm the SCK input is grounded (3-wire I2S, BCK PLL).
- The TPA3126 pin-by-pin connections match the datasheet's typical application:
  - bootstrap caps C24-C27 (220 nF)
  - output LC filter (L2/L3 10 µH)
  - snubbers
  - input coupling and the input pad (R12-R17)
  - the AVCC (pin 17) connection
- Hierarchical sheet pins and labels: no single-ended nets created by typos (e.g. `AMP_MUTE` vs `AMP_MUTE_CMD`, `AMP_ENABLE` vs `AMP_SDZ`). Trace these through the root sheet.
- **Documentation.** Notes and title blocks were updated to Rev C on 18 Nov 2026:
  - title blocks: "Pre-order C", 2026-11-18
  - root: 19 V / 5.0 V
  - Amp: PLIMIT to GVDD, 15 W DSP-limited
  - Power: power-entry notes use Q2/D3/D4/D5/C43/R19/R36/R37; U3 note says 13k7 = 4.98 V; TLV1117 dissipation at 5 V in
  - ESP32: J1 10-pin system connector, J4 PROG GND/RX/TX

  Check that every note's references, values and pin numbers match the design. Report anything still wrong.

### PCB
- DRC with schematic parity: 0 errors, 0 unconnected items. The footprints and nets match the schematic.
- Board updated from the current schematic: no leftover footprints from removed parts (old Q1 DPAK, D1/D2/R22, R19/C29 on PLIMIT, old J2/JP1 if removed).
- The 18 Nov field edits (blank MPNs, new notes) were made in the schematic only. PCB footprint fields may still show the old MPNs until the owner runs Tools → Update PCB from Schematic. Note it; it is not blocking, and nets and footprints are unaffected.
- **L2/L3:** `review/README.md` notes a winding swap whose pad-net assignments were to be updated "during a future PCB update". Verify the L2/L3 pad nets now match the schematic. Check that each winding pair puts an OUT pin and its speaker connector on the same winding.
- **TPA3126 PowerPAD:** U1 is the DAD HTSSOP-32 PowerPAD-up package. Check the heatsink HS1 mounting and the thermal pad treatment against the datasheet layout guidance.
- **Track widths for current:**
  - PVDD path J3 → F1 → Q2 → bulk caps → U1 PVCC: about 3 A peak.
  - Speaker outputs through L2/L3 to J16/J17.
  - GND returns.
- **Switching loops:**
  - Buck U3: input cap C45/C46 tight to VIN/GND; SW node small.
  - Amp: PVCC caps tight to the pins.
- Mounting holes, connector placement and courtesy clearances. HS1 clearance was confirmed by the owner (see the HS1 Assembly_Note).
- Silkscreen: polarity marks on electrolytics, diodes, TVS and connectors. J3 pin 1 = +. J1 pin numbering visible.
- Fab outputs generate without errors: Gerbers for all copper layers, mask, silk, Edge.Cuts, and drill. Layer count and stack-up are as intended: 4 layers, In1 = GND.
- Manufacturer constraints: minimum track/space/drill in the board setup vs a typical 4-layer service (e.g. JLCPCB or PCBWay standard). Note any feature below 0.127 mm or 0.3 mm drill.

### BOM
- Every fitted part has an MPN, apart from the six deliberately blank ones in section 4. List those separately with value, package and rating so the owner can choose parts. Flag MPNs that are obsolete or not orderable, except the accepted DMP4025LSD.
- Check that each MPN's package matches the footprint, across every sheet, not just the six already fixed.
- Through-hole vs SMD consistent with the footprints.

## 9. Earlier findings and how they were resolved (18 Nov 2026)

These came from a file-level pre-check by the bring-up session. Do not re-report them unless the fix itself is wrong.

| # | Finding | Resolution |
|---|---|---|
| 1 | R24 13k7 value vs 16k2 MPN | 13k7 is intended (5V_PRE ~4.98 V). MPN blanked. See section 4. |
| 2 | Footprint vs MPN package mismatch: C29, C46, C48 (1206), R23, R24, R27 (0805) | MPNs blanked, footprints kept. Assembly_Note gives value/package/rating. |
| 3 | U4 MPN fields disagree | Owner will choose. Ignore. |
| 4 | PWR_SW near PVDD on J1 pin 10 | Accepted: keyed connector. |
| 5 | No always-on jumper | Intended. |
| 6 | Stale notes and title blocks | Updated to Rev C. Verify them (section 8). |
| 7 | Firmware SUPPLY_MAX_V 16.5 V | Firmware change later. Out of scope. |

The 18 Nov update changed only text notes, title blocks and part fields. Connectivity was compared before and after on every sheet and is identical.

## 10. Report format (`review/fab-readiness-2026-11-18/REPORT.md`)

1. **Verdict:** READY / READY AFTER FIXES / NOT READY, in one paragraph.
2. **Blocking:** must change before ordering. For each: sheet or layer, reference/pin/net, evidence (tool output line, file excerpt or datasheet quote with page), suggested fix.
3. **Should fix:** low cost, worth doing in this order.
4. **Notes / cosmetic**
5. **Checked and OK:** short list, so the owner can see coverage. Include the section 5 contract table with a ✓ per row and the section 6 lessons with measurements.
6. **Tool summary:** ERC/DRC counts, kicad-cli version, commit reviewed.

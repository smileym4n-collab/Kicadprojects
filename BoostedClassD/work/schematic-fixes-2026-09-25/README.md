# Schematic corrections — 25 September 2026

The four hierarchical schematic sheets were edited in place. The PCB and `.kicad_pro` are byte-for-byte identical to the backup. The user's existing TAS grounding fixes and charger settings (R17 300R, R18 13k) were preserved. No PCB update, routing, footprint replacement, or firmware edit was performed.

## Implemented

- TAS2320 U2 and TAS2120 U3 IOVDD now use ESP3V3; their core VDD stays at 1.8 V. C22/C24 follow IOVDD; C21/C23 remain on core VDD.
- Corrected TAS symbol pin 22/23 names to GND without changing numbering. Preserved the user's existing ground connections and I2C-mode pin 16 grounding. Corrected electrical pin types against datasheet functions and stored project-local symbol copies. R9's existing custom shunt symbol was copied locally, with its numbering and footprint unchanged.
- Separate SDZ controls on GPIO27 (U2) and GPIO33 (U3), with 100k pulldowns. Unused amplifier IRQ/SDOUT pins and U2 NC pin 13 explicitly marked unused.
- 24k address resistors: U3 to ground gives 7-bit 0x49; U2 to IOVDD gives 0x4A. INA236B with A0 grounded remains 0x48; verify the actual INA236 suffix before purchase. TAS global address 0x40 remains a firmware consideration.
- ATtiny U5, C8 and button pullup R13 now use always-on BQ-SYS upstream of Q1. The buck-boost and amplifiers remain on switched SYS. This crosses the hierarchy through an explicit BQ-SYS sheet connection.
- Q2/Q3 isolate the higher-voltage ATtiny play/shutdown outputs from ESP32 GPIO34/35. Existing R14/R15 pull the collectors to ESP3V3. ATtiny HIGH now asserts an active-LOW ESP input.
- Q4 adds the requested shutdown acknowledgement: ESP32 GPIO14 HIGH pulls ATtiny PA3/ACK_N LOW. Existing TP1 now monitors ACK_N. The collector pullup is to the ATtiny's own always-on supply.
- INA236 ALERT is connected through both sheet boundaries to GPIO32, with a 4k7 pullup to ESP3V3.
- Q5 converts open-drain charger STAT2 into a sourcing charge-LED driver; J1 pin 7 remains LED positive and pin 8 remains ground. Existing R19 2k2 retained. GPIO23's status LED now has R34 1k in series; J2 pin 6 unchanged.
- C32 adds 10u local ESP32 bulk decoupling. C26/C27 changed from nominal 1u to 4u7 / 25 V X7R, subject to verifying at least 1u effective capacitance. Amplifier capacitor voltage/dielectric requirements are shown in schematic notes/fields.
- J6 provides ATtiny UPDI access: pin 1 target voltage reference/BQ-SYS, pin 2 UPDI, pin 3 ground. Do not use this header to externally power the board without evaluating backfeed.
- Cleaned dangling sheet stubs, unused pins and page boundaries. No ERC exclusions were added. Power flags identify external input/ground and Q1's switched output, rather than masking floating connections.

## Added physical components

All added resistors and C32 use 2012 metric footprints. Existing R14, R15 and R19 are reused.

| References | Quantity | Value / part | Function |
|---|---:|---|---|
| Q2–Q4 | 3 | onsemi MMBT3904LT1G, SOT-23 | Two requests and shutdown acknowledgement |
| Q5 | 1 | onsemi MMBT3906LT1G, SOT-23 | Charge LED source driver |
| R22, R23 | 2 | 100k, 1% | SDZ pulldowns |
| R24, R25 | 2 | 24k, 1% | TAS address selection |
| R26, R28, R30, R35 | 4 | 22k, 1% | Transistor base current limiting |
| R27, R29, R31, R36 | 4 | 100k, 1% | Base-emitter bias resistors |
| R32 | 1 | 10k, 1% | ATtiny acknowledgement pullup |
| R33 | 1 | 4k7, 1% | INA ALERT pullup |
| R34 | 1 | 1k, 1% | Status LED limiting |
| C32 | 1 | 10u / 10 V X7R | ESP32 bulk decoupling |
| J6 | 1 | 1x3, 2.54 mm vertical header | UPDI programming |

Total: **21 new parts** (4 transistors, 15 resistors, 1 capacitor, 1 header). New transistor pinout verified against onsemi: 1 base, 2 emitter, 3 collector. No inventory was available to establish whether purchases are needed.

## Firmware contract

| Function | ESP32 | ATtiny412 | Assertion |
|---|---|---|---|
| Play/pause request | GPIO34, module pin 6 | PA1, pin 4 | ATtiny HIGH gives ESP LOW |
| Shutdown request | GPIO35, module pin 7 | PA2, pin 5 | ATtiny HIGH gives ESP LOW |
| Shutdown acknowledged | GPIO14, module pin 13 | PA3, pin 7 | ESP HIGH gives ATtiny LOW |
| TAS2320 SDZ | GPIO27, module pin 12 | — | LOW shuts down U2 |
| TAS2120 SDZ | GPIO33, module pin 9 | — | LOW shuts down U3 |
| INA236 ALERT | GPIO32, module pin 8 | — | Active LOW |
| Q1 power control | — | PA7, pin 3 | LOW holds system power ON; release HIGH to turn OFF |
| Power button | — | PA6, pin 2 | Active LOW |
| UPDI | — | PA0, pin 6 | Programmer data |

At startup, keep request outputs inactive and GPIO14 LOW. Keep both amplifiers in shutdown until supplies are valid. Follow TI's shared-boost sequence: release secondary U2 before primary U3; configure shared-boost roles, current limit, serial-audio channels and mute state; observe the documented clock/startup timing before playback. The independent SDZ controls make this possible but do not implement firmware.

On shutdown, ATtiny requests shutdown while holding Q1 ON. ESP32 mutes/stops the amplifiers, lowers both SDZ controls, completes persistent writes and asserts GPIO14 HIGH. ATtiny observes ACK_N LOW and releases Q1, with a bounded timeout for an unresponsive ESP32. Clear stale acknowledgement before accepting another cycle. Firmware, sleep current, brownout and switch bounce still require implementation/bench validation.

## Unresolved design limits — not fixed by a clean ERC

1. **7 Ah cell versus charger timer:** R17 300R sets nominal 1 A charge and R18 13k selects 1.1 A input limit / 4.2 V. The confirmed source can provide 5 V / 1.1 A. The BQ25185 has a nominal 360-minute charge safety timer. A 7 Ah recharge already needs roughly seven hours of ideal constant 1 A before taper; a full recharge from deep discharge therefore cannot be relied upon with this charger/timer combination. Thermal regulation and system consumption also affect charging. The charger was retained and the limitation annotated; solving it properly requires a separate charger-selection decision, not a resistor-only fix or timer bypass. The exact pouch cell must support 4.2 V charging and 1 A charge current.
2. **L1/L2 exact parts remain unspecified:** L1 needs appropriate RMS capability and saturation margin above the converter's maximum current requirement (at least 3.35 A plus margin). L2 must match the configured boost peak current including tolerance, loss and thermal limits. Generic 1uH values and existing footprints are not evidence of suitability.
3. **R9 physical shunt remains unverified:** 20 mOhm is preserved, as is its custom four-terminal footprint. Exact manufacturer part and force/sense pad mapping are still needed. A local symbol copy does not verify the physical footprint.
4. **Battery and current-path limits remain:** confirm protected pack, suitable external NTC (10k, beta 3435 K), wiring, connector and fuse ratings against actual peak battery current. Existing 3 A paths can constrain attainable audio output. These were not silently uprated or redesigned.
5. **Capacitor ratings are procurement requirements:** verify manufacturer DC-bias curves and package fit, especially boost PVDD capacitors and charger capacitors. Nominal values alone do not establish effective capacitance.
6. **PCB and hardware remain separate work:** none of these schematic changes has been transferred to the PCB. Preserve/recheck the user's point-1 PCB fix when updating later. No new layout, DRC, simulation, EMI, acoustic, bench, or thermal validation is claimed.

## Verification and artifacts

- `erc.json`: full hierarchical ERC, **0 errors, 0 warnings**, no new exclusions.
- `connectivity-checks.json`: **53 passing checks**, including exact transistor interfaces, SDZ isolation, hierarchy, power domains, new footprints, unchanged PCB/project settings, preservation of other original terminal relationships and no unintended net mergers.
- `before.xml`, `after.xml`: hierarchical netlists.
- `verify_connections.py`: repeatable checks against exported netlists.
- `schematic-review.pdf`: all four revised sheets; rendered drawings visually inspected.
- `backup/` and `baseline-hashes.json`: original saved design before this edit.

Changed design files: `BoostedClassD.kicad_sch`, `ESP32.kicad_sch`, `Amplifiers.kicad_sch`, `CHGPOWER.kicad_sch`. Added `BoostedClassD.kicad_sym` and `sym-lib-table`. No git commit was made; the installed system git is blocked by the unaccepted Xcode licence, so the saved backup and hashes provide change control.

## Datasheet references

- [TI TAS2120](https://www.ti.com/lit/ds/symlink/tas2120.pdf): pin functions, IOVDD, address selection, shared-boost operation.
- [TI TAS2320](https://www.ti.com/lit/ds/symlink/tas2320.pdf): pin functions, address selection, shared-boost operation.
- [TI BQ25185](https://www.ti.com/lit/ds/symlink/bq25185.pdf): resistor settings, capacitor requirements, STAT outputs and charge safety timer.
- [onsemi MMBT3904](https://www.onsemi.com/pdf/datasheet/mmbt3904lt1-d.pdf) and [MMBT3906](https://www.onsemi.com/download/data-sheet/pdf/mmbt3906lt1-d.pdf): package pin numbering and electrical limits.

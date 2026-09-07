# DiscreteClassD power/output stage review

Completed 7 September 2026 using KiCad 10.0.5. Open `DiscreteClassD.kicad_pro`, then the **Power output stage** hierarchical sheet. The output stage is on `PowerOutput.kicad_sch` (A3, sheet 2). The exported PDF includes both sheets.

## Scope and preservation

- Read project `AGENTS.md` before editing. Original schematic and project settings are preserved in `output/verification/DiscreteClassD.before-output-stage.*`.
- Reused U2, Q1, Q2, C1, L6, J14 and J15, retaining their UUIDs. The starting file contained only one driver and two MOSFETs; added U6, Q3 and Q4 to complete the requested BTL stage.
- The original Q1/Q2 values said **DMTH6016LPSQ** although the request specifies **DMTH6016LPS**. All four now explicitly specify the requested non-Q DMTH6016LPS. No other MOSFET type was selected.
- Corrected output-stage symbol electrical types and restored physical MOSFET pin numbering. The original driver numbers were already correct; its pins were all incorrectly typed as inputs. Its NC pin is now NC and has a legitimate no-connect marker.
- All nine unrelated symbol instances (U1/U3 multi-unit op amps, U4, U5, IC1), their positions/properties, and the original root embedded libraries remain unchanged. U1/U3 were already outside the A4 drawing boundary, some at negative Y, so they remain clipped from the root PDF. No audio, oscillator, PWM, dead-time, feedback or protection circuitry was designed.
- `DiscreteClassD.kicad_pro` is byte-for-byte unchanged. No ERC rules or exclusions were added. `DiscreteClassD.kicad_pcb` was not modified; no PCB placement/routing/update-from-schematic was performed.

## Datasheet evidence

- [TI UCC27301A official datasheet](https://www.ti.com/lit/ds/symlink/ucc27301a.pdf), SLUSEY5: printed pages 3–4, DRC pin table and exposed-pad note; application/layout sections. Local copy: `sources/ucc27301a.pdf`.
- [Diodes DMTH6016LPS official datasheet](https://www.diodes.com/datasheet/download/DMTH6016LPS.pdf), DS38436 Rev. 5-2, August 2026: page 1 pin configuration; page 7 package and pad layout. Local copy: `sources/DMTH6016LPS.pdf`.
- [Codaca CSAD0660 official datasheet](https://www.codaca.com/Private/pdf/CSAD0660.pdf), revised 2020-07-14: page 1 winding schematic and land pattern. Local copy: `sources/CSAD0660.pdf`.
- [Panasonic EEUFR1V102 specification](https://na.industrial.panasonic.com/products/capacitors/aluminum-electrolytic-capacitors/series/83367/model/83808): 1000uF, 35V FR, 12.5mm diameter, 20mm height, 5mm lead spacing.

## Driver pin-number / pin-name connections

The EP is represented as pad **11** in KiCad; TI calls it the thermal pad rather than an eleventh numbered lead. NC is intentionally unconnected. EN remains available and is not tied high. The DRC driver's internal pull-down disables it while EN is floating.

| DRC pin | Pin name | U2: bridge A | U6: bridge B |
|---|---|---|---|
| 1 | VDD | +12V_GD; C2/C3 to PGND | +12V_GD; C8/C9 to PGND |
| 2 | NC | No connection | No connection |
| 3 | HB | HB_A; C1 to SW_A | HB_B; C7 to SW_B |
| 4 | HO | HO_A → R1 → Q1 gate | HO_B → R7 → Q3 gate |
| 5 | HS | SW_A, Kelvin to Q1 source | SW_B, Kelvin to Q3 source |
| 6 | EN | EN_A, reserved | EN_B, reserved |
| 7 | HI | HI_A, reserved | HI_B, reserved |
| 8 | LI | LI_A, reserved | LI_B, reserved |
| 9 | VSS | PGND, Kelvin to Q2 source | PGND, Kelvin to Q4 source |
| 10 | LO | LO_A → R4 → Q2 gate | LO_B → R10 → Q4 gate |
| EP / 11 | Thermal pad | PGND | PGND |

## MOSFET pin-number / pin-name connections

For **each device**, pins **1, 2 and 3 are source**, pin **4 is gate**, and pins **5, 6, 7 and 8 are drain**. The exposed drain metal is part of the drain; the project footprint assigns its central copper to pad 5, not to a fictitious extra lead. All source and drain lead numbers are present in the symbol/netlist, with stacked secondary pins hidden only graphically.

| MOSFET | Role | Pins 1, 2, 3: S | Pin 4: G | Pins 5, 6, 7, 8 and exposed drain: D |
|---|---|---|---|---|
| Q1 | A high side | SW_A | GH_A, via R1 from U2.4 | +24V |
| Q2 | A low side | PGND | GL_A, via R4 from U2.10 | SW_A |
| Q3 | B high side | SW_B | GH_B, via R7 from U6.4 | +24V |
| Q4 | B low side | PGND | GL_B, via R10 from U6.10 | SW_B |

## Every network and component value

Each gate has its own 10-ohm series resistor and 47-kohm gate-source resistor, both 2012 metric (0805). Optional parallel branches comprise a diode and a separate initial 10-ohm resistor. The diode cathode faces the driver, so population would provide a lower-resistance turn-off path. These diode part numbers remain to be selected for speed, pulse current and at least 30V reverse rating; SOD-123 land patterns are provided.

| MOSFET | Main series path | Gate-source resistor | Optional DNP path, gate to driver |
|---|---|---|---|
| Q1 | HO_A → R1 10R → GH_A | R2 47k: GH_A–SW_A | GH_A → R3 10R → D1 anode; D1 cathode → HO_A |
| Q2 | LO_A → R4 10R → GL_A | R5 47k: GL_A–PGND | GL_A → R6 10R → D2 anode; D2 cathode → LO_A |
| Q3 | HO_B → R7 10R → GH_B | R8 47k: GH_B–SW_B | GH_B → R9 10R → D3 anode; D3 cathode → HO_B |
| Q4 | LO_B → R10 10R → GL_B | R11 47k: GL_B–PGND | GL_B → R12 10R → D4 anode; D4 cathode → LO_B |

| Parts | Value / rating | Connection | Package / requirement |
|---|---|---|---|
| C1 / C7 | 100nF / 25V X7R | HB_A–SW_A / HB_B–SW_B | 2012 metric, directly at HB/HS |
| C2 / C8 | 100nF / 25V X7R | +12V_GD–PGND | 2012 metric, directly at VDD/VSS |
| C3 / C9 | 4.7uF / 25V X7R | +12V_GD–PGND | 2012 metric, close to respective driver |
| C4 / C10 | 100nF / 50V X7R | +24V–PGND | 2012 metric, local to respective bridge |
| C5 / C11 | 1uF / 50V X7R | +24V–PGND | 3216 metric, local to respective bridge |
| C6 / C12 | 10uF / 50V X7R | +24V–PGND | 3225 metric, local to respective bridge |
| C17 | 1000uF / 35V Panasonic FR | Positive to +24V; negative to PGND | EEUFR1V102; radial 12.5mm / 5mm pitch |
| L6 winding 1 | 10uH | Pin 1 SW_A → pin 2 OUT_A | One Codaca CSAD0660-100M |
| L6 winding 2 | 10uH | Pin 4 SW_B → pin 3 OUT_B | Same physical dual device |
| C15 | 330nF / 100V requirement | OUT_A–OUT_B | Low-loss C0G or SMD film; provisional 5750 metric |
| R15 + C16 | 10R / 1W + 100nF / 100V | OUT_A → R15 → C16 → OUT_B | Non-inductive 6332 metric resistor; C0G/SMD film, provisional 3225 metric capacitor |
| R13 + C13 | 10R + 330pF / 100V | SW_A → R13 → C13 → PGND | Both DNP; 3216 metric resistor, 2012 metric C0G capacitor |
| R14 + C14 | 10R + 330pF / 100V | SW_B → R14 → C14 → PGND | Both DNP; same packages as bridge A |
| J14 | 24V power entry | Pin 1 +24V; pin 2 PGND | SMD solder-wire pads |
| J16 | Driver supply entry | Pin 1 +12V_GD; pin 2 PGND | SMD solder-wire pads |
| J15 | Differential speaker | Pin 1 OUT_A; pin 2 OUT_B | SMD solder-wire pads; no PGND terminal |

The driver uses its integrated bootstrap diode; no external bootstrap diodes were added. D1–D4 belong exclusively to the optional gate-resistor branches.

**Test points:** TP1 SW_A; TP2 HO_A; TP3 LO_A; TP4 SW_B; TP5 HO_B; TP6 LO_B; TP7 OUT_A; TP8 OUT_B; TP9 +24V; TP10 +12V_GD; TP11 PGND. HO test points are on floating high-side outputs: their gate-drive reference is HS, not PGND.

DNP and excluded from the default assembly BOM: **D1–D4, R3, R6, R9, R12, R13, R14, C13, C14**. The default `output-stage-bom.csv` contains the remaining 45 symbols (including PCB solder pads and test points); those bare copper features are not purchase items.

Full pin-by-pin output-stage connectivity, including the unnamed series junctions, is in `verification/all-output-connections.md`, extracted from the KiCad XML netlist.

## Libraries and footprint decisions

Custom symbols are in `DiscreteClassD.kicad_sym`, and custom footprints are in `DiscreteClassD.pretty`, referenced by project-local library tables.

- UCC27301ADRCR uses the standard KiCad VSON-10 footprint with 1.65 × 2.4mm exposed pad, checked against TI's DRC drawing.
- MOSFET footprint geometry was copied from the existing custom footprint and its generic 1=G / 2=D / 3=S pad scheme was restored to the physical 1–8 numbering. The geometry matches the dimensions on the supplied official package drawing; final PCB manufacture still requires normal footprint/assembly review.
- The existing Codaca footprint had 2.6 × 2.65mm pads centered at X=±2.6, Y=±1.625. Corrected the local copy to **2.65 × 2.6mm pads at X=±1.625, Y=±2.6**, matching the manufacturer's recommended land pattern. Top-view numbering: 1 upper left, 2 lower left, 3 lower right, 4 upper right; the datasheet package underside view is mirrored.
- Reused connector references/symbols J14 and J15, but changed their original Molex through-hole footprint assignments to SMD solder-wire pads to honor the requested single through-hole exception. No particular SMD connector MPN was invented. Mechanical wire retention/strain relief remains a later PCB/enclosure decision.
- C17 is the sole through-hole footprint in the output-stage selection.

## Assumptions and remaining engineering decisions

The user-specified component values are starting values, not measured performance guarantees. With ideal 20uH differential series inductance and 330nF across the speaker, the simple uncoupled LC estimate is **61.95kHz**. Actual behavior must account for winding interaction, load, parasitics, modulation and feedback. A 30W sine into 8 ohms requires **15.49Vrms, 21.91Vpeak, 1.94Arms and 2.74Apeak**; ideal modulation is 0.913 at 24V, before losses. The Codaca datasheet specifies 3.5A temperature-rise current and 6.5A saturation current under its stated conditions; switching ripple and actual temperature still need checking.

- The requested 100nF bootstrap capacitors are retained. A nominal 17nC MOSFET gate charge alone gives about 0.17V charge-related droop on 100nF; this is only a first estimate, excluding driver consumption and capacitor DC-bias effects. Bootstrap recharge and maximum duty limits must be considered with the later PWM design.
- Select exact ceramic MPNs by **effective capacitance at 12V/24V bias**, temperature, ripple and package. The displayed nominal values and voltage ratings are not an assertion that every part in the chosen package will meet those conditions.
- C15 remains one 330nF schematic component, as requested. Its low-loss dielectric requirement and provisional footprint are explicit. Exact stock parts, any parallel-capacitor realization, and allowable ripple/heating remain to be decided. C16 also needs an exact low-loss MPN. No X7R substitution was made for either filter/Zobel capacitor requirement.
- The optional gate diodes and snubbers need measurement-based selection/tuning. R15 is initially 1W and non-inductive; verify its dissipation with both audio and switching residue.
- EN_A/EN_B and all four HI/LI inputs are reserved, separate nets. No permanent enable connection or common bridge logic connection was added. +5V_A is documented as the future logic rail; no power-stage component needs it yet.
- The layout constraints listed in the user request are on the output sheet. Kelvin returns and small physical loops are PCB routing requirements, not something a schematic net label can enforce by itself.

## ERC: all remaining findings

Final KiCad ERC: **69 messages: 63 errors, 6 warnings**. Baseline had 77 messages. No exclusions were added, no PWR_FLAG symbols were used to silence checks, and all reported connectivity mistakes introduced during editing were corrected and rechecked.

| Area / device | Remaining errors | Explanation |
|---|---:|---|
| IC1 | 8 | All eight existing comparator pins unconnected |
| U4 | 7 | Four unconnected pins; one undriven input; two undriven power pins |
| U5 | 10 | Six unconnected pins; two undriven inputs; two undriven power pins |
| U1 | 14 | Eight unconnected pins; four undriven inputs; two undriven power pins |
| U3 | 14 | Same categories as U1 |
| U2 | 6 | HI pin 7, LI pin 8 and EN pin 6 undriven; VDD pin 1, VSS pin 9 and HB pin 3 lack an ERC power-output source |
| U6 | 4 | HI pin 7, LI pin 8 and EN pin 6 undriven; HB pin 3 lacks an ERC power-output source |
| **Total** | **63** | 53 untouched-circuit errors plus 10 output-stage errors |

The six warnings are `isolated_pin_label` on **HI_A, LI_A, EN_A, HI_B, LI_B, EN_B**. Each is intentionally connected only to its driver's input, pending later control circuitry.

The VDD/PGND source errors are reported once on the shared supply nets, hence appear under U2 rather than again for U6. They connect to external supply entry pads, which are passive. Each HB connects to its bootstrap capacitor and the IC's internal diode; that internal diode is not represented as an ERC power-output pin. These messages remain visible rather than being suppressed.

The original project already ignored four check classes: single global labels, four-way junctions, SPICE model issues, and footprint-filter mismatches. Those settings were retained verbatim. `erc-all.json` was also generated with all available severities, including exclusions; its 69 findings match the text report. The unchanged project settings do not amount to a claim that the entire amplifier is ERC-clean.

See `verification/erc-after.rpt` for every message with symbol/pin and exact coordinates.

## Verification performed

- KiCad parsed the root and child sheets, exported the full two-page PDF and XML netlist, and opened the updated project in the desktop application.
- Compared **131 named pin/net assignments** against the exported netlist; checked **seven isolated series junctions**; confirmed no gate-resistor bypasses and no speaker-to-PGND or bridge-to-bridge short.
- Checked all 12 DNP/exclude-from-BOM states, all physical MOSFET pad numbers, preserved unrelated symbols and unchanged project/ERC settings.
- Rendered and visually inspected both PDF pages; note the pre-existing off-page op amps described above.
- No simulation or hardware test was run. PCB file SHA-256: `0ea777a22eed996e67c99aa18140e19ea676b045cca790eb3b3bb58bedd6239c`.

Stop point: power/output-stage schematic only. Later stages remain unconnected.

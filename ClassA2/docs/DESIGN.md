# ClassA2 Rev A — design notes

Hiraga-inspired complementary Class-A power amplifier, one mono channel per board (two boards for stereo). **Schematic only — not released for PCB.** Everything here is a calculation or a simulation with author-approximate models (see [SIMULATION.md](SIMULATION.md)). None of it has been bench tested.

Status:

| Stage | State |
|---|---|
| Schematic | ERC 0 errors / 0 warnings. Netlist cross-checked against the SPICE deck: connectivity and values. |
| Simulated | DC, AC, loop gain, transient, THD, power-cycling, gain spread, thermal bias. Approximate models. |
| Layout | Not started (user) |
| Bench tested / thermally tested | No |

---

## 1. Hiraga *Le Monstre*: what the original does

Sources: the translated *l'Audiophile* articles on the Class-A Amplifier Site ([no. 27](https://sound-au.com/tcaas/monster27.htm), [no. 29](https://sound-au.com/tcaas/monster29.htm)), a builder's page ([qrp.gr](http://qrp.gr/page/audio/monstre/monstre.htm)), and builder reports on diyAudio. The schematic itself is an image I could not read as text. Items marked *(interpretation)* are my reading of the described component relationships, not a verified copy of the original circuit.

- **Three stages, push-pull throughout.** A complementary input stage drives a complementary driver, which drives one complementary output pair. In the later version, the input stage is a JFET/BJT cascode (2SK170/2SJ74 with 2SC1775/2SA872), the drivers are 2SB716/2SD756, and the outputs are 2SD844/2SB754. The article calls the output arrangement a "reversed Darlington", which is a complementary feedback pair (CFP, Sziklai).
- **Low supply, large standing current.** The rails are about ±12–14 V from lead-acid batteries or large capacitor banks. Hiraga specified about 0.6–0.8 A of bias, which gives about 8 W of pure Class A, roughly constant from 7 to 20 Ω.
- **Bias set by resistors in the input-stage load, without a dedicated thermal-tracking element.** A summary of the circuit gives "voltage across the 1 kΩ drain resistor = driver VBE + Iq × 1 Ω emitter resistor". *(Interpretation)* The input-stage current through that resistor sets the drive to each CFP, so Iq depends on the input-device current and the driver VBE. That is consistent with builders reporting bias moving "about 100 mV and maybe more" as the heatsink warms, and with fans being added to hold it.
- **Modest global feedback.** The feedback resistor is a single 220 Ω. Builders measured about 26 dB of gain, and Hiraga suggests 4.7–10 nF across the feedback resistor if the amplifier oscillates. The article claims stability into 1 µF and more than 4 MHz bandwidth. I have not verified these claims.
- **Offset balance** comes from a 100 Ω trimmer between the input-device sources.

Principles kept in ClassA2:

- direct-coupled complementary push-pull;
- one CFP output pair at about 0.7 A;
- low rails;
- a minimal stage count;
- a single feedback loop of moderate depth;
- an input-pair balance trimmer.

Changes, made for electrical reasons:

- **Bias is set by a VBE multiplier that tracks the drivers.** This removes the dependence on input-stage current and on output-device temperature.
- **Inventory BJTs replace the JFETs.** Neither 2SK170 nor 2SJ74 is in stock, and both are obsolete.
- **The CFP is used as a follower, not as a rail-referenced stage.** That gives a lower open-loop output impedance and a well-defined Iq.

## 2. Architecture options considered

| Option | For | Against | Decision |
|---|---|---|---|
| A. Close Le Monstre copy with BJTs: complementary input → resistor-loaded drive → CFP | Fewest parts, closest to the original | Iq depends on input current and driver VBE with no thermal tracking (the original's known weakness); offset depends on NPN/PNP VBE matching; poor open-loop output impedance | Rejected |
| B. ESP P3A style: one LTP, current mirror, CCS-loaded VAS, EF2 | Well known | Explicitly excluded by the brief; not symmetrical | Rejected |
| C. **Complementary LTPs → push-pull VAS → VBE multiplier → CFP output** | Symmetrical, DC-coupled, defined currents everywhere, CFP gives thermal bias stability and about 0.5 V more swing than an EF2 at these low rails | 13 transistors, more than Le Monstre | **Chosen** |
| D. Option C with an EF2/EF3 (Darlington) output | Classic, easy to stabilise | Bias must track four junctions on the heatsink; Iq varies with output-device temperature; about 0.5 V less swing | Rejected |

## 3. Circuit, stage by stage

Reference designators match `ClassA2.kicad_sch` and `simulation/amp.cir`.

**Input (J1, C1, R1, R2, C2).**
- C1 (2u2 PET) and R1 (47k) set the input impedance (about 46 kΩ) and a 1.54 Hz high-pass.
- R2 (1k) and C2 (470p C0G) form a 339 kHz RF filter (−0.016 dB at 20 kHz).
- R1 equals the feedback resistor R26, so the residual base currents of the two input pairs (about 1 µA) give almost no offset.

**Input stage (Q1/Q2 2SC2240-GR, Q3/Q4 2SA970-BL).**
- Two complementary long-tailed pairs share the input node and the feedback node (FB).
- Each pair runs at about 2 mA from a tail current source: Q5 (BC546) or Q6 (BC556). Each source is referenced to two 1N4148s (D1/D2, D3/D4), which are fed in series by one shared resistor, R5 (27k).
- 220 Ω emitter degeneration (R6/R7, R11/R12) lowers gm and gives about 11 V/µs of slew with 100 pF Miller capacitors.
- Only the signal-side collector of each pair drives the VAS. The feedback-side collectors go straight to the filtered rail, which adds less than 1 mV of offset.

**Offset trim (RV2 500R, R30 220R).**
- RV2's track runs from E1 to E2, with its wiper fed to the tail through R30. This is Hiraga's balance trimmer, made fail-safe.
- If the wiper goes open, R6/R7 still carry the tail and the offset returns to its untrimmed value.
- Trim range in simulation: +17 to −47 mV around the untrimmed −15 mV.

**VAS (Q7 2SA1145-Y, Q8 2SC2705-Y).**
- Push-pull common-emitter stage, each side at about 5.5 mA.
- The current is set by the input-pair half-current through R9/R14 (1k3) against VBE plus R16/R17 (100R).
- C5/C6 (100p C0G) provide Miller compensation; their value sets the loop crossover at about 200 kHz.

**Bias generator (Q9 BD139, R18 1k, R19 470R, RV1 500R, C7 1µ).**
- A VBE multiplier between the driver bases. Q9 is mounted on the main heatsink beside the drivers.
- RV1 is a rheostat in the base–emitter leg:
  - **more resistance = less bias**;
  - an open wiper gives the full 500 Ω, which is minimum bias (about 75 mA);
  - RV1 = 0 is limited by R19 to about 0.94 A.
- C7 ties the two driver bases together at audio and higher frequencies.

**Output stage (CFP pairs).**
- Upper half: Q10 BD139 drives Q12 2SA1941. Lower half: Q11 BD140 drives Q13 2SC5198.
- The output-device emitters sit on the rails. Their collectors and tabs are EP and EN, which return to OUT through R22/R25 (0R33 / 5 W).
- R21/R24 (100R) are the output base–emitter resistors. R20/R23 (51R) are driver base stoppers.
- Iq ≈ (V_bias/2 − VBE(driver)) / 0.33 Ω, so it depends almost only on the drivers' VBE. In simulation:
  - output-device temperature: +0.35 mA/K;
  - driver temperature: +5.2 mA/K;
  - sensor temperature: −7.5 mA/K.

**Feedback (R26 47k, R27 3k, C9 220µ NP).**
- Gain 1 + 47/3 = 16.7 (24.4 dB).
- C9 makes the DC gain unity, so output offset ≈ input-stage offset. Its corner is 0.24 Hz.
- C8 is a DNP footprint for a phase-lead capacitor across R26, in case bench tests need it.

**Output network.**
- Zobel R28 (10R / 2W metal oxide) with C10 (100n).
- Isolation coil L1 (1.5 µH air core) in parallel with R29 (2R7 / 1W).
- The coil is necessary: without it the model oscillates at 1.9 MHz into a 100 nF open load.

**Supply.**
- J2 brings in +V/GND/−V. C11/C13 (1000µ) and C12/C14 (100n film) are local decoupling at the output pair.
- R3/C3 and R4/C4 (10R + 220µ, 72 Hz) give the front end its own filtered rails, +VF/−VF.
- There is one GND net; its returns are described in section 8.

## 4. Component selection rationale

| Position | Part | Why |
|---|---|---|
| Q12/Q13 | 2SA1941/2SC5198 (in stock 19/20) | Requested; 100 W, 140 V, fT 30 MHz; ≥6× DC-SOA margin at 10.6 W / 15 V. Toshiba lists them **Not Recommended for New Design**; acceptable because they are in stock, but replacements would be 2SA1943/2SC5200 (also stocked, TO-3P(L), different footprint). |
| Q10/Q11 | BD139/BD140 | Stocked, 80 V, 12.5 W, TO-126 bolts to the heatsink for driver/sensor tracking. 2SC4793/2SA1837 would be faster but only 6 each are stocked and the ClassA project uses them. |
| Q9 | BD139 | Same package/thermal path as the drivers it tracks. |
| Q7/Q8 | 2SA1145-Y/2SC2705-Y (salvaged, 12 each) | 150 V, Cob 1.8–2.5 pF: low Early/Cob nonlinearity for a VAS. Obsolete; BC556/BC546 are an electrical fallback (65 V, higher Cob, different pinout). |
| Q1–Q4 | 2SC2240-GR / 2SA970-BL | Low-noise, 120 V complementary audio pairs, stocked. Obsolete (salvaged). Gain ranks differ (GR 200–400 vs BL 350–700); the offset effect is covered by RV2. |
| Q5/Q6 | BC546/BC556 | Tail CCS only; 65 V. |
| R22/R25 | Yageo SQP500JB-0R33 | 5 W cement; idle dissipation 0.16 W keeps their drift low. 23 stocked; ClassA uses 4. |
| Small resistors | TE LR1 0.6 W 1 % metal film | Stocked; every position dissipates below 0.04 W. |
| C1 | WIMA MKS2 2.2 µF PET | Stocked DC block. With the 47k load, the signal voltage across it at 20 Hz is less than 8 % of the input. PP film is an optional upgrade. |
| C5/C6, C2 | 2012 metric C0G (stock) | C0G is required in the compensation and filter positions; 2012 metric SMD from stock (through-hole C0G is a drop-in at layout). C5/C6 can see up to about 32 V at clipping; 50 V rating. |
| C9 | Nichicon UES1H221MHM 220 µF bipolar (on order, 2) | Sees only the offset (mV); bipolar avoids reverse-bias concerns. |
| C11/C13 | Panasonic FR 1000 µF 35 V | Low-impedance local reservoir at the output pair; 35 V vs 20.3 V worst no-load rail. |
| R28 | Stackpole RSMF2 10R 2W metal oxide (on order) | Non-inductive Zobel resistor; do not use the stocked wirewound 10R. |

## 5. Power supply (12-0-12 VAC, ~100 VA, both channels)

Assumptions:

- The transformer is uncharacterised. Its regulation is taken as 8 % or 12 %, and the winding resistance is referred to each secondary.
- UK mains is 230 V, from −6 % to +10 % (216–253 V).
- A centre-tapped bridge feeds the reservoirs. Each rail path conducts through one diode per half-cycle.
- The load is the two channels' standing current, 2 × 0.708 A ≈ 1.42 A per rail. In Class A the average rail current does not change with signal.

Simulated (`simulation/psu.py`):

| Reservoir per rail | Mains | Loaded rail avg | Valley | Ripple p-p |
|---|---|---|---|---|
| 10,000 µF | 216 V | 14.55–14.67 V | 14.06–14.20 V | 0.94–0.98 V |
| 10,000 µF | 230 V | 15.63–15.78 V | 15.13–15.30 V | 0.95–0.99 V |
| 10,000 µF | 253 V | 17.40–17.60 V | 16.90–17.12 V | 0.96–1.00 V |
| 22,000 µF | 230 V | 15.66–15.80 V | 15.44–15.59 V | 0.43–0.45 V |
| No load (bias collapsed) | 253 V | **20.3 V peak** | | |

Hand checks:

- No-load peak: 12 V × (1 + reg) × √2 × 1.1 − 0.7 ≈ 19.5–20.3 V.
- Ripple: ΔV ≈ I/(f·C) = 1.42/(100 × 10 mF) = 1.4 V. That conservative formula is above the simulated 1.0 V because the diodes conduct for part of each cycle.

Transformer loading:

- RMS secondary current is 2.6–2.8 A against a 4.17 A rating, which is 63–67 %. The supply delivers 59–75 VA, and copper loss is about 40–45 % of the rated loss.
- **It is suitable for continuous Class A**, though it will run warm. Measure its temperature after 2 h in the enclosure.

Idle power:

- DC: 43 W (48 W at high mains).
- Bridge: about 2.6 W. Transformer: about 4–7 W.
- **Total: roughly 50–55 W from the mains for stereo at idle.** About 44 W of that is heat on the two channel heatsinks.

PSU recommendations (off-board, not part of this schematic):

- **Reservoirs:** use at least 10,000 µF per rail, shared between the channels. 15,000–22,000 µF per rail halves the ripple; your two stocked 15,000 µF / 63 V HEC caps would work.
- **Bridge:** at least 6 A, mounted to the chassis (the stocked D5SBA20 qualifies).
- **Mains side:** a slow-blow mains fuse (about T1A for 100 VA; confirm against the transformer's inrush data), a protective-earth bond to the chassis, and correct creepage on the primary wiring.
- **Rail voltage:** the rails do not compromise the design. Swing at 1 % THD is 10.3 W at low mains and 12 W nominal, both above the Class-A limit. No change to the transformer is needed.

## 6. Bias, thermal and SOA

Target: **Iq = 0.70 A per channel when warm**, which is 231 mV across R22 (TP5–TP4) and across R25 (TP4–TP6).
- 2 × Iq gives a peak current of 1.40 A.
- **The Class-A limit is 2·Iq²·R_L = 7.8 W into 8 Ω.** In simulation, the device current stays above 20 mA up to 7.5 W.
- Above that, the stage runs Class AB up to clipping.

Bias stability (simulation):

| Quantity | Result |
|---|---|
| Heatsink 25 → 65 °C, fixed RV1 (sensor and drivers track the sink) | 0.738 → 0.657 A (−2.0 mA/K, falling: safe direction) |
| Rails 14.0 → 20.2 V | 0.687 → 0.722 A |
| Output hFE 55 → 160 | 0.662 → 0.713 A |
| Driver hFE 40 → 250 | 0.756 → 0.687 A |
| RV1 0 → 500 Ω | 0.94 → 0.075 A |

The VBE multiplier ratio (about 2.75) slightly over-compensates the two driver junctions, so Iq falls a little as the heatsink warms. **Set the bias when the amplifier is warm.**

Dissipation per channel at idle, ±15.6 V (simulation):

| Device | Dissipation |
|---|---|
| Q12, Q13 | 10.55 W each |
| Q10, Q11 | 0.17 W each |
| Q7, Q8 | 0.08 W each |
| R22, R25 | 0.16 W each |
| Rail power | 2 × 15.6 V × 0.708 A = 22.1 W |

Output-device dissipation falls with signal (`results/device_dissipation.json`):

| Output into 8 Ω | Q12/Q13 each |
|---|---|
| 0 W | 10.55 W |
| 3.75 W | 8.7 W |
| 7.5 W | 6.8 W |
| 12 W | 5.3 W |

Into 4 Ω at 10 W it is 7.8 W. **Idle is the thermal worst case.**

Heatsink: about 21.5 W per channel is on the sink (Q10–Q13 and Q9).

| Parameter | Value |
|---|---|
| Rth(j-c), 2SC5198/2SA1941 | 1.25 K/W (from Pc = 100 W at Tc = 25 °C, Tj(max) = 150 °C) |
| Rth(c-s) | about 0.5 K/W (mica + grease) or about 1.0 K/W (silicone pad) |
| Design point | 30 °C inside the enclosure, sink ≤ 55 °C |
| **Required** | **Rth(s-a) ≤ 25/21.5 ≈ 1.1 K/W per channel** (≤ 0.55 K/W for one shared stereo sink) |
| Resulting Tj | 55 + 10.55 × (1.25 + 0.5) ≈ 74 °C (≈ 79 °C with a pad) |
| BD139/BD140 Tj | sink + about 2.5 K (Rth(j-c) 10 K/W at 0.17 W) |

A 1.5 K/W sink would still keep Tj ≤ 86 °C, but the sink would be uncomfortably hot to touch (about 62 °C), and bias would fall by about 30 mA.

DC SOA:
- **Idle:** 15.4 V at 0.69 A is far inside the DC SOA. Pc at Tc = 70 °C is 64 W, and the DC limit at 15 V is power-limited, not second-breakdown-limited.
- **Highest VCE:** about 2 × rail (31 V nominal, 41 V at the high-mains no-load rail), reached near zero current. All parts are rated at least 80 V (VAS and outputs at least 140 V).
- **Fault, RV1 short:** about 0.94 A gives 14.5 W per device. That is survivable on the specified sink, but the sink runs about 20 K hotter.
- **No output short-circuit protection**, as specified. A shorted output with the real PSU will destroy the outputs. Use a current-limited supply for bring-up.

Resistor ratings:

| Resistor | Dissipation | Rating |
|---|---|---|
| R22/R25 | ≤ 0.5 W average at 12 W out | 5 W |
| R28 | about 0.12 W at 20 kHz / 10 W | 2 W; sustained full-power HF testing above about 50 kHz will exceed it |
| R29 | < 0.1 W at 20 kHz full power | 1 W |
| All others | < 0.04 W | 0.5–0.6 W |

## 7. Stability

Simulated loop gain, using voltage injection at OUT:
- Crossover at 171–215 kHz, phase margin 82–95° and gain margin 23–25 dB at 5.7–9 MHz.
- That holds for every load tested: 4 Ω, 8 Ω, open, and 100 nF–10 µF with or without 8 Ω.
- Loop gain is 44 dB at 1 kHz and 20 dB at 20 kHz.

Square waves (10 kHz) are clean into resistive loads. The overshoot into large capacitors is the L1/R29 network resonating with the load capacitance, not the loop. This is normal for an output coil.

**The CFP local loops are not captured by the injection method.** The transient test found a 1.9 MHz oscillation into 100 nF with L1 removed. That is why L1 is mandatory, and why the bench check for oscillation at EP/EN (section 9 of [BENCH_TEST.md](BENCH_TEST.md)) matters.

## 8. Notes for your layout

These are not layout instructions, only the schematic intent.

- **Heatsink:** Q9, Q10 and Q11 go on the main heatsink, next to Q12/Q13, all insulated. **The tabs of Q12/Q13 are at EP/EN (near OUT), not at a rail.** Short leads from the drivers to Q12/Q13. R20/R23 go at the driver bases.
- **Decoupling:** C11/C12 at the Q12 emitter, C13/C14 at the Q13 emitter. The Zobel and L1 go at the board output. C3/C4 go at the front end.
- **Grounding:**
  - one GND net, with return currents controlled by placement;
  - the input ground (J1 screen, R1, C2, C9) goes to one point;
  - the power ground (C11–C14, C10, J3 return) goes to another;
  - join them at J2 pin 2;
  - keep the R26/R27/C9 feedback return off the output-current path.
- **Trimmers:** keep RV1/RV2 accessible. TP4, TP5 and TP6 must be reachable with the amplifier powered.

## 9. Open items and uncertainties

1. **2SC2705/2SA1145 pinout:** E-C-B is taken from a second-source datasheet, not Toshiba's. Confirm with a meter (diode test) before fitting. The salvaged parts' gain ranks are also unverified.
2. **Device models are approximations.** Absolute THD, exact margins and the startup transient need bench confirmation.
3. **The transformer's regulation and temperature rise are unknown.** Measure the rails loaded and unloaded.
4. **Offset:** −15 mV simulated untrimmed, −12 to −22 mV across the gain spread. Real values depend on VBE matching. RV2 covers ±30 mV around untrimmed. Match Q1/Q2 and Q3/Q4.
5. **Power-up transient:** about 0.7 V at the output, settling over about 3 s. External speaker protection with a delay of at least 3 s is assumed.
6. **2SC2240-GR stock:** 7 are in stock and this design needs 4 for stereo. DarlingtonAmp/DarlingtonAmpDual also use 2SC2240, so the allocation is your call.
7. **L1 is self-wound.** The footprint is a placeholder; fit it to the actual coil at layout.
8. **Toshiba lifecycle:** the outputs are NRND, and the small-signal Toshiba parts are obsolete. This is fine for a stocked build; not ideal for reproduction.

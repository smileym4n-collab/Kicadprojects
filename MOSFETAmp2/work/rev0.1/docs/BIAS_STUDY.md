# Bias temperature compensation study — 25 October 2026

**Status: simulation study and proposal only. The schematic, BOM, PCB and other documents still describe the Rev 0.1 network (variant A). Nothing here is bench-verified.** MOSFET temperature behaviour is *imposed* in every simulation, because no available model reproduces it. Treat all numbers as development evidence.

Scripts: `simulation/bias_study.py` (static corners, thermal scenarios, rails, open wiper) and `simulation/bias_dynamic.py` (k selection, distortion, clipping burst, loop gain). Results: `simulation/results_bias/` (`bias_study_infineon.json`, `bias_study_authored.json`, `bias_dynamic_infineon.json`, decks and logs). Run sequentially from any directory, using the same Python environment as `run.py`.

## 1. Why the Rev 0.1 network fails

Spread = VZ (4.3 V, fixed, on the PCB) + k·VBE(Q108 on the heatsink). Only the multiplier ratio k can absorb device spread, and k also sets the temperature coefficient. Low-threshold MOSFETs need little spread, so k falls towards 1.5 and the sensor provides only about −3 mV/K. High-threshold MOSFETs push k up to about 9 and over-compensate. The MOSFET VGS slope at 50 mA, however, is roughly the same whatever the threshold. The required compensation is fixed while the network's compensation follows the trim setting. That is a structural fault, not a tuning problem.

A rough estimate of the required slope comes from the datasheet Fig. 3 typical transfer curves (25 °C and 175 °C), extrapolated with a square law from the zero-temperature-coefficient crossing. It gives about −4.7 mV/K per device at 50 mA for both the IRF540N and the IRF9540N. These are typical curves, not guaranteed data; the real value must be measured (Section 6).

## 2. Models

Genuine Infineon SPICE models were obtained this session: `simulation/models/infineon/irf540n.spi` and `irf9540npbf.spi`, with provenance in `simulation/models/README.md`. They are MODPEX Level-1 fits with a nonlinear Cgd network. At 50 mA they give VGS ≈ 3.61 V (N) and 3.86 V (P), close to the authored models' 3.47/3.89 V. The N model's KP is 112 A/V² against the authored 20, which makes bias about 1.5× more sensitive to spread: about 0.6 mA per mV. **They do not model threshold temperature coefficient, subthreshold behaviour, spread or SOA.** The study therefore imposes:

- spread: the datasheet VGS(th) window of 2–4 V, applied as a gate series source relative to the model VTO. Corners: nominal, 2 V/2 V, 4 V/4 V, N 2 V/P 4 V and N 4 V/P 2 V;
- temperature: threshold slope of −3.0, −4.7 or −6.0 mV/K per device, plus KP ∝ T^−1.5;
- sensor (Q108) temperature TS and board temperature TB (drivers, current-source reference, LED, Zener, diodes, current sink) set separately.

The authored models were re-run as a cross-check; conclusions are the same.

## 3. Variants compared

| | Spread arrangement | Adjustment | Temperature coefficient |
|---|---|---|---|
| **A** (Rev 0.1) | 4.3 V Zener + BD139 multiplier, 1k / 47k ∥ (130R + 2k) | 2k rheostat changes k | Varies with device threshold and trim |
| **P** | Select-on-test BZX79 (2V4–6V8) + multiplier, 2k7 / 1k2 ∥ (820R + 2k) | Zener chosen from measured VGS; 2k narrows k (≈4.2–6.5) | Varies with trim and Zener value |
| **B** (proposed) | 2 × 1N4148 (PCB) + BD139 multiplier with **fixed** 3k9/1k0 (k ≈ 4.9) + BC546 current sink drawing I = (V_LED − VBE)/(RE + RV) from the multiplier base | Offset = 3k9 × I, set by select-on-test RE plus a small trim rheostat | Fixed by two resistors, independent of device threshold and trim |

Variant B in detail (proposed references are descriptive, not yet assigned):

- BP → two 1N4148 in series → Q108 collector. The diodes sit on the PCB and track the two driver VBEs (model −1.79 mV/K each against −1.99 mV/K per driver).
- Q108 BD139 on the heatsink. R12 = 3k9 from collector to base and R13 = 1k0 from base to emitter (BN). k = 4.9, giving about −9.4 mV/K at the sensor; the model BD139 VBE slope is −1.93 mV/K at 4 mA.
- Current sink: BC546 collector to the Q108 base, emitter → RE (select-on-test) → RV (rheostat, wiper tied to one end) → −V. Base at a red LED from base to −V.
- LED fed with about 1 mA from a BC556 whose base is on the existing two-diode TREF reference, with 680 R to +V. This keeps LED current nearly rail-independent, using the same structure as the existing Q105/Q107 current sources.
- The offset current comes from the active-load current (normally under 1.5 mA of the ~6 mA) and returns to −V. C103 (100 nF BP–BN) is retained.
- The LED/VBE pair largely cancels in temperature, so the offset has a small board-temperature coefficient (assumed LED slope −1.8 mV/K; real red LEDs vary, typically −1.5 to −2.5 mV/K).

## 4. Results (Infineon models, ±15 V, calibrated to 50 mA cold in each corner)

P-device idle current in mA at **−4.7 mV/K per device**. Scenario temperatures are the amounts above a 27 °C ambient.

| Variant / corner | Selected part, trim | Warm idle: sink +20, die +22, board +10 | Hot idle: sink +40, die +42, board +15 | After burst: sink +20, die +29 | Burst start: die +15, sensor cold | Ambient +15 (all) | Board only +15 |
|---|---|---:|---:|---:|---:|---:|---:|
| A nominal | 32 Ω of 2k | 34.4 | 13.2 | 61.6 | 120.8 | 39.1 | 65.4 |
| A 4 V/4 V | 4 Ω of 2k | 18.4 | 0.1 | 41.5 | 120.7 | 23.3 | 56.9 |
| A N 2 V/P 4 V | 134 Ω of 2k | 75.2 | 83.5 | 108.4 | 120.9 | 73.7 | 72.9 |
| A 2 V/2 V | **cannot reach 50 mA** (Infineon); authored models: 50 → **228 mA** hot | | | | | | |
| P nominal | 5V6, 1.1k of 2k | 73.8 | 82.4 | 106.8 | 120.7 | 70.0 | 67.3 |
| P 2 V/2 V | **cannot reach 50 mA** (would need a Zener below 2.4 V) | | | | | | |
| **B nominal** | RE 1k0, 128 Ω of 200R | **51.0** | **46.2** | 81.1 | 120.7 | 40.7 | 41.5 |
| **B 2 V/2 V** | RE 5k1, 1.18k of 2k | **54.2** | **51.4** | 84.8 | 120.7 | 44.3 | 44.3 |
| **B 4 V/4 V** | RE 820R, 144 Ω of 200R | **50.3** | **45.0** | 80.2 | 120.6 | 39.8 | 40.7 |
| **B N 2 V/P 4 V** | RE 1k5, 184 Ω of 500R | **52.6** | **48.7** | 83.0 | 120.8 | 42.5 | 43.0 |

The full −3.0 / −4.7 / −6.0 mV/K tables, the N 4 V/P 2 V corner and the authored-model cross-check are in the JSON files. Key observations:

- **B removes the threshold dependence.** At any given scenario, B's current varies by at most about ±4 mA across all five datasheet corners, in both model sets. A varies by over 80 mA, and P cannot cover the full window.
- **The slope must still match.** At B's default k = 4.9, a −3 mV/K device gives 3.6 mA hot (over-compensated: bias collapses, which is safe but causes crossover distortion). A −6 mV/K device gives 98 mA hot (under-compensated: bounded at these imposed temperatures, but too high). Because k is now set by two fixed resistors, it can be chosen once the slope has been measured. Selection table (nominal pair, holding 50 mA from cold to sink +40 K):

  | Measured slope per device | −3.0 | −4.0 | −4.7 | −5.5 | −6.0 | −7.0 mV/K |
  |---|---:|---:|---:|---:|---:|---:|
  | R13 (R12 = 3k9) | 2k0 | 1k3 | 1k0 | 820R | 750R | 620R |
  | k | 2.9 | 4.0 | 4.8 | 5.7 | 6.2 | 7.4 |

- **Die-to-sensor lag is common to all variants.** It shows as about 80 mA just after a burst and about 120 mA at burst start with a cold sensor, at −4.7 mV/K. It depends on the mechanical coupling of Q108 and on source resistance, not on the spreader topology. It is a transient; it settles as the die temperature approaches the sink temperature.
- **Board temperature:** B slightly over-compensates (+15 K on the board → 41–44 mA), the safe direction. A and P under-compensate (57–73 mA), because their Zener does not track the drivers.
- **Rail sensitivity is common to all variants and still open:** about 37–42 mA at 12.5 V and 66–77 mA at 20.6 V when calibrated at ±15 V. B is no worse than A. The individual mechanisms (active-load current versus rail, MOSFET λ, driver Early effect) have not yet been separated. This matters for a final PSU with ±10% mains variation and needs attention before release.
- **Open wiper:** about 0.02–0.03 mA in every B corner, so it fails low. With RE unfitted the offset current is zero and bias is about zero, which gives a safe first power-up without J101.
- **Dynamic checks** (Infineon models, nominal pair, 8 Ω, ±15 V):

  | | A | B |
  |---|---:|---:|
  | 1 kHz, 5.26 Vpk out, THD (2–10) | 0.0083% | 0.0086% |
  | 20 kHz, 5.26 Vpk out, THD (2–10) | 0.173% | 0.176% |
  | Loop phase margin, 8 Ω / reactive load | 78.6° / 70.5° | 78.5° / 70.4° |
  | Spread minimum during hard clipping | 4.55 V | 6.87 V |
  | Spread deviation within 500 µs after clipping | 2.5 mV | 1.2 mV |

  B's current sink is referenced about 1.15 V above −V. Its compliance held through hard negative clipping in this test. The Infineon-model margins are close to the earlier authored-model results (79° and 68°).

## 5. Failure modes of B (single faults)

| Fault | Effect | Comparison with A |
|---|---|---|
| RV wiper or track open | Offset current → 0, bias ≈ 0 (fail-low) | Same as A |
| RE open or unfitted | Bias ≈ 0 (fail-low) | — |
| LED open | Sink transistor saturates and starves the Q108 base; spread opens; **fail-high** | New series-type failure |
| BC546 sink C–E short | Q108 base pulled to −V; **fail-high** | New |
| Either series 1N4148 open, Q108 open, R12 open | Spread opens; **fail-high** | A has the same class (Zener, Q108, R112 open) |
| BC556 LED feed open | LED current only from leakage; offset collapses; fail-low | — |

B adds two fail-high single faults (LED open, sink short) to the class A already has. As before, protection against these relies on supervised bring-up, bench current limiting and the external speaker-protection board. This should be weighed when deciding. A parallel resistor across the LED does not cure the LED-open case, because the base would still be driven high.

## 6. What must be measured (not simulated)

1. **VGS at 50 mA, at two temperatures, for each MOSFET to be used.** This gives both the select-on-test value and the slope that sets k. A fixture is proposed below; it needs a contact temperature measurement, which has not yet been confirmed as available.
2. Real red-LED Vf slope (typically −1.5 to −2.5 mV/K) and the actual BD139 VBE slope only matter to second order; B's board coefficient was robust in simulation. They can be checked in-circuit during warm-up.
3. Q108's thermal coupling and lag on the actual heatsink (warm-up and post-burst behaviour).
4. Rail sensitivity on the real circuit.

### Proposed VGS / slope fixture (low risk, about 0.2 W)

- Mount one MOSFET, insulated as in the amplifier, on a spare heatsink. Bolt a power resistor (for example 10 Ω / 10 W) next to it as a heater, driven from the second EL302RD output. Clamp a thermocouple (or other contact probe) to the MOSFET tab next to the package.
- N device: drain to the bench supply positive output, with the supply in current limit at **50 mA** and voltage limit about 10 V. Gate tied to drain through 1 kΩ, source to 0 V, and a 10 V Zener plus 47 kΩ from gate to source as in the amplifier. The device then sits at VDS = VGS ≈ 3.5–4 V and about 0.2 W.
- P device: same, with polarity reversed.
- Measure VGS at the device pins with the DMM. Record at ambient, then with the heater raising the tab to about 40, 55 and 70 °C, waiting for stability at each step. Slope = ΔVGS/ΔT, which selects R13 from the table above.
- Stop if VGS drifts continuously at constant temperature or the tab exceeds 80 °C.

### Proposed commissioning with B

1. Fit R13 from the measured slope (default 1k0). **Leave RE unfitted.**
2. Power up current-limited: bias should be about zero, since spread = diodes + k·VBE.
3. Measure the spread S0 between BP and BN and the voltage across the RE footprint position (LED − VBE ≈ 1.15 V).
4. Required spread S = VGS_N + VGS_P (from the fixture, at 50 mA) + VBE(Q109) + VEB(Q110) + 33 mV. Required current I = (S − S0)/3k9. RE ≈ 1.15 V/I. Fit **one E24 value above** that (lower bias). Choose the trim pot by RE: 200R for RE up to 1k3, 500R up to 3k3, 2k above. All three are stocked generic multiturn parts; fit quality and pinout still need confirming.
5. Trim upwards from maximum resistance (minimum bias) to 50 mA warm, as in the existing bench procedure.

## 7. Parts implications (provisional, not yet in the BOM)

Per channel versus A: remove the BZX79-C4V3 and the 130 Ω; add 2 × 1N4148 (stock 63), 1 × BC546 (stock 36, 6 already allocated), 1 × BC556 (stock 20, 8 already allocated), 1 red LED, 680 R, 3k9, select-on-test RE and a sized trim. A stocked red LED exists only as SMD 2012 metric (Kingbright KP-2012EC, 10 pcs); a through-hole red LED would be a small purchase. The purchased BZX79-C4V3 would no longer be needed. Inventory was read only.

## 8. Recommendation and decision needed

Adopt **variant B** for Rev 0.2, subject to your approval. It is the only variant here that fixes the temperature coefficient independently of device threshold and trim, covers the whole datasheet threshold window, keeps fail-low open-wiper behaviour, and leaves distortion and loop margin unchanged in simulation. Its costs are five extra small parts per channel, a select-on-test resistor, and two new fail-high single faults. Variant P was investigated and is not recommended.

Not yet done, pending a decision:

- updating `channel.cir`, `tools/build_schematic.py`, the KiCad schematic, BOM, purchase list, DESIGN/BENCH/LAYOUT documents, and rerunning the full `run.py`/`extended.py`/`supplement.py` suite and ERC/netlist verification;
- separating the rail-sensitivity mechanisms;
- the hot-SOA question (blocker C), which this study does not address.

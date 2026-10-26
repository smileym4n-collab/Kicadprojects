# ClassA2 Rev A — bias adjustment and bench commissioning

Expected values below come from simulation at ±15.6 V (see [SIMULATION.md](SIMULATION.md)). Treat them as guides: real devices differ.

**Do not connect a loudspeaker until every step in section 4 has passed.** There is no output short-circuit protection.

## 1. Before soldering

- [ ] Check the pinout of every salvaged transistor with a meter (diode test), against the symbol notes:

  | Parts | Package | Pinout |
  |---|---|---|
  | 2SC2240 / 2SA970 | TO-92 2-5F1B | E-C-B |
  | **2SC2705 / 2SA1145** | TO-92MOD | E-C-B, from a second-source sheet: **confirm** |
  | BD139 / BD140 | — | E-C-B |
  | BC546 / BC556 | — | C-B-E |
  | 2SC5198 / 2SA1941 | — | B-C-E |

- [ ] Match Q1/Q2 (2SC2240-GR) and Q3/Q4 (2SA970-BL) within about 2 mV VBE at 1 mA, and hFE within 10 %. Mount each pair touching (thermally coupled).
- [ ] Check the trimmer direction on the actual part with a meter: which way of turning increases R(pin 1–pin 2)?

## 2. Before first power

- [ ] Q12/Q13 insulated from the heatsink: more than 20 MΩ, tab to heatsink. **The tabs are at EP/EN, near OUT.**
- [ ] Q9, Q10, Q11 bolted to the main heatsink (insulated) next to Q12/Q13, with thermal compound.
- [ ] **RV1 (bias) set to maximum resistance.** With power off, the resistance from the R19/RV1 junction to VBN (the Q9 emitter) should read about 500 Ω. This is the minimum-bias setting, about 75 mA in simulation.
- [ ] RV2 (offset) centred: pin 2 to pin 1 and pin 2 to pin 3 should each read about 250 Ω.
- [ ] Electrolytic polarity:
  - C11 + to +V;
  - C13 + to GND;
  - C3 + to +VF;
  - C4 + to GND.
  - C9 is bipolar.
- [ ] No short from +V, −V, +VF or −VF to GND or to each other (measure resistance both ways).

## 3. First power — current-limited bench supply, 8 Ω dummy load (≥ 20 W), input shorted

1. Set the supply to ±15 V with a **150 mA** current limit per rail, and switch on.
2. Expect a rail current of about 0.09 A per rail (front end about 11 mA plus minimum Iq). If either rail hits the limit, switch off and investigate.
3. Measure (black probe on TP3/GND):

   | Point | Expected |
   |---|---|
   | +VF / −VF | ≈ +15.4 / −15.4 V |
   | Across R8 / R13 (tail currents) | ≈ 0.52 / 0.54 V (≈ 1.95 / 2.0 mA) |
   | Across R16 / R17 (VAS currents) | ≈ 0.55 V each (≈ 5.5 mA) |
   | Q9 C–E (bias spreader) | ≈ 1.23 V at minimum bias |
   | TP4 (OUT) | within ±50 mV |
   | TP5 − TP4 and TP4 − TP6 | ≈ 25 mV each (≈ 75 mA) |

4. Scope OUT, TP5 and TP6 (≥ 100 MHz bandwidth, ground spring on the probe). There should be **no oscillation at any frequency**. Re-check with 8 Ω ∥ 1 µF and with 2.2 µF across the load.

## 4. Bias adjustment (Iq = 0.70 A per channel)

Measure the drop across both emitter resistors: TP5 − TP4 (R22) and TP4 − TP6 (R25). **0.70 A gives 231 mV across each 0.33 Ω.**

1. Raise the current limit to 1.0 A per rail.
2. Turn RV1 slowly toward lower resistance, which **raises** bias. Stop at 100 mV (0.3 A). Wait 5 minutes and check the heatsink temperature and that both drops match within about 10 %.
3. Continue to about 230 mV. Watch both rail currents; they should be ≈ Iq + 11 mA and equal.
4. Run the amplifier for at least 60 minutes in its final mechanical arrangement (enclosure, real heatsink).
   - In simulation, bias **falls** by about 2 mA per °C of heatsink rise, so expect it to drop by roughly 40–60 mA when warm.
   - Re-trim to 231 mV when warm.
   - If the bias **rises** as the heatsink warms, switch off. Q9 is not thermally coupled correctly.
5. Rails from the real supply (12-0-12 VAC PSU) will be 14–17.6 V depending on mains. Re-check Iq on the real PSU after warm-up.
6. **Offset:** adjust RV2 for TP4 within ±5 mV when warm. Then re-check it after 30 more minutes. The target is ±25 mV after settling under any condition.
7. Record the final drops, rail voltages, heatsink temperature and ambient for each channel.

## 5. Commissioning checklist (8 Ω dummy load)

| # | Test | Pass criterion / expectation (simulation) |
|---|---|---|
| 1 | Gain at 1 kHz, 1 V out | 24.4 dB ±0.3 dB (16.6 V/V) |
| 2 | Response 20 Hz–20 kHz | within ±0.2 dB (sim −0.03 dB at 20 Hz, −0.07 dB at 20 kHz) |
| 3 | 10 kHz square, 2 V pk into 8 Ω / open | no overshoot or ringing (sim < 0.1 %) |
| 4 | Same into 8 Ω ∥ 1 µF and open ∥ 2.2 µF | damped LC ringing only (sim 32 % and 57 % overshoot), no sustained oscillation |
| 5 | Scan for parasitic oscillation at idle and at 1 W, 7.5 W, clipping | none, including with capacitive loads |
| 6 | Clipping into 8 Ω at 1 kHz | symmetrical, clean recovery, no sticking or burst oscillation. Sim: about 12 W at nominal rails, 10 W at low mains |
| 7 | Class-A limit | scope the voltage across R22 and R25 at 1 kHz: neither may fall to 0 V below about 7.5 W out |
| 8 | THD at 1 W and 5 W, 1 kHz | record (model estimate 0.002–0.004 %; hardware will differ) |
| 9 | Output noise, input shorted, 20 Hz–20 kHz | record (model 22 µV) |
| 10 | Heatsink and transformer after 2 h idle | heatsink ≤ 55 °C at 25–30 °C ambient (with Rth(s-a) ≤ 1.1 K/W per channel); transformer temperature within its rating |
| 11 | Offset drift, cold → warm | stays within ±25 mV |
| 12 | Power-on / power-off transient at OUT (no speaker) | sim about ±0.7 V slow excursion; confirm the speaker protection delay is ≥ 3 s |
| 13 | Rail sensitivity (variac, if available) | Iq at 216 V / 253 V mains within about ±30 mA of nominal |
| 14 | Both channels | repeat 1–13; record per-channel Iq and offset |

If ringing or oscillation appears:
- first check the probe grounding and layout;
- the next options are fitting C8 (10–22 pF C0G) or raising R20/R23 to 100 Ω;
- re-run test 3 afterwards;
- do not reduce C5/C6 without repeating the stability checks.

# SubAmp schematic and PCB review - 18 October 2026

**Decision: NOT READY for fabrication/assembly sign-off.** The circuit is recognisably ESP Project 68, and the saved PCB connectivity matches the saved schematic. There are definite capacitor rating errors, unresolved resistor ratings, a thermal mounting question, and layout/stability work to resolve. No schematic, PCB or project settings were changed.

Scope: saved `SubAmp.kicad_sch`, `SubAmp.kicad_pcb`, and `SubAmp.kicad_pro`; KiCad 10.0.5. User specifies 4 or 8 ohms, normally +/-35 V, with +/-56 V as an absolute maximum. Power transistors are intended to lie flat, tab down, with a large shared heatsink secured through their mounting holes. Actual heatsink section, thermal resistance, insulation, copper weight, capacitor BOM and resistor BOM were not supplied.

## 1. Findings requiring resolution

### High: capacitor voltage ratings

- **C3 and C6:** the previously discussed 220 pF / 50 V parts are unsuitable at +/-56 V. Each sees roughly one rail at idle and can approach the full rail-to-rail voltage on opposite output peaks. Even +/-35 V can produce nearly 70 V across them. Retain C0G/NP0 and 220 pF; 200-250 V or higher is a conservative choice, with 500 V also suitable.
- **C8 and C9:** the recorded part `C1206C104K5RACTU` is 100 nF, X7R, **50 V**, 3216 metric. They connect directly from each supply rail to GND. They exceed their continuous rating at 56 V; use suitably rated replacements, preferably 100 V, and verify effective capacitance under DC bias. They are within their voltage rating at 35 V. [KEMET specification](https://search.kemet.com/component-documentation/download/specsheet/C1206C104K5RACTU)
- **C12 and C13:** 100 uF directly across the rails, with correct polarity, but no voltage rating/part number is specified. Require at least 63 V for a genuinely bounded 56 V supply; 80/100 V offers greater margin if it fits. The 8 mm body / 2.5 mm pitch footprint must match the selected part.
- **C5:** bootstrap capacitor, positive to OUT, correct for normal operation. Approximately 28 V DC at 56 V rails and 17.5 V at 35 V rails, with ripple and startup stress. Specify the actual part; 63 V is a sensible choice. It does not normally see 112 V.
- **C7:** Zobel capacitor sees output voltage; use an appropriately rated film part, at least 100 V DC for this design. C10 bridges signal and power ground, C11 bridges the two bias diodes; neither normally sees a supply rail. Their exact parts/rating still need recording.

### High: R10, R11 and R22 ratings are not established

R10/R11 are both 3k3, but have DIN0207 body footprints (6.3 x 2.5 mm, 10.16 mm pitch), and no wattage is stated. A footprint does not prove the installed resistor's power rating.

The bootstrap midpoint is approximately halfway between output and the negative rail. At idle, each resistor therefore has approximately half one rail across it:

| Condition | Approximate R10 dissipation | Approximate R11 dissipation |
|---|---:|---:|
| +/-35 V, idle | 0.093 W | 0.093 W |
| +/-56 V, idle | 0.238 W | 0.238 W |
| +/-56 V, 35 Vrms output, effective bootstrap action | 0.238 W | 0.609 W |

Last row uses `P_R11 ~= ((Vrail/2)^2 + Vout_rms^2)/3300`. Diode drops, ripple and loading change these estimates slightly. **Specify 1 W parts for both and verify physical fit.** A standard 0.25 W part has almost no idle margin at 56 V; R11 can exceed it substantially during output.

**R22** is the 10 ohm Zobel resistor, also assigned DIN0207. Specify at least the reference design's 1 W rating, with a suitable flameproof/pulse-capable part and matching footprint. This branch has little low-frequency dissipation but substantial high-frequency loading; do not qualify it using subwoofer frequency alone. For illustration, 30 Vrms at 20 kHz into the 10 ohm / 100 nF series branch dissipates about 1.4 W in R22. This is a stress illustration, not an expected sustained subwoofer signal.

R16-R21 have larger power-resistor footprints, but their wattages are also absent. Specify 5 W minimum as a starting point and check actual body/pitch. The 0R33 resistors can dissipate roughly 3 W each at 50 V peak into 4 ohms, assuming approximate equal sharing between two main devices per polarity and neglecting the helper contribution. Reactive loading and clipping need separate assessment.

### High: tab-down heatsink assembly is unresolved

The electrical collector-tab connections matter:

| Devices | Tab/collector net |
|---|---|
| Q7 | Positive-side internal drive node, shared with Q5 emitter and Q9/Q11 bases |
| Q8 | Negative-side internal drive node, shared with Q6 emitter and Q10/Q12 bases |
| Q9, Q11 | VCC |
| Q10, Q12 | VEE |

These tabs **must not be connected together by a common heatsink or metal fixings**. Use appropriate insulating thermal interfaces and insulated mounting hardware, and check isolation after tightening. Q4-Q6 also have electrically live collector tabs. [Toshiba 2SC5200 drawing](https://toshiba.semicon-storage.com/info/2SC5200_datasheet_en_20160107.pdf?did=20668&prodName=2SC5200), [onsemi MJE15032/33](https://www.onsemi.com/pdf/datasheet/mje15032-d.pdf)

If the proposed stack is transistor tab -> FR4 -> heatsink, it is **not an adequate thermal arrangement**. Bolts through the holes do not provide the required heat path. The tabs need thermal contact with the heatsink through an appropriate insulating pad, using a mechanically compatible arrangement such as mounting on the heatsink-facing board side or an intentionally designed interface. Do not choose that arrangement without checking lead orientation and clearance to board copper.

The six large footprints use 5.45 mm lead pitch, 1.5 mm lead drills, and 3.3 mm non-plated mounting holes. Toshiba specifies B-C-E and 5.45 mm pitch, which agree electrically. The generic TO-264 footprint is not automatically wrong: its broad dimensions are similar to the Toshiba 26 mm body. However its 25.08 mm mounting-hole-to-lead-row distance assumes formed leads. Verify a real part and insulating hardware against a 1:1 print before assembly. No complete mechanical stack or physical fit is verified.

Q4-Q6 require a suitable driver heatsink; a large sink for Q7-Q12 does not establish their cooling. D2/D3 must track driver temperature through deliberate thermal contact. The diode placement beside the driver line is compatible with arranging this, but the assembly must make it happen. [ESP thermal guidance](https://sound-au.com/project68.htm)

### Medium/high: local driver loops are unnecessarily spread out

Q5 is at (51.054, 139.294) mm and Q7's lead row is at x=91.885 mm. Q6 is at x=51.054 mm and Q8's lead row is also at x=91.885 mm. Each complementary feedback pair therefore spans roughly **40 mm**, with about **51/58 mm of total routing** on their respective collector/base-drive nets. These are active local feedback loops, not simply slow speaker wiring.

The shared base-drive nets to the main output transistors contain approximately **135 mm of routed track per polarity**, plus associated copper. These are total net lengths, not an assertion that every base has a 135 mm source-to-pin route. Long shared paths can introduce inductance and unequal drive. Move the driver/helper pairs closer if revising placement, and make the branches to parallel devices compact and reasonably symmetric. Do not add arbitrary compensation or base resistors solely on this review: validate with measured ringing/stability first.

C3 and C6 themselves are placed close to their respective TO-220 devices, which is good. Correct capacitance and local placement do not establish overall loop stability with the substituted power devices and this PCB.

## 2. Schematic observations

The main signal path, differential input stage, current sink, PNP voltage amplifier, bootstrap, complementary feedback helper pairs, output emitter resistors and Zobel connect coherently. Fresh netlist comparison found **no mismatched net assignments on numbered PCB pads**.

- MPSA42 symbol mapping is E=1, B=2, C=3, consistent with the specified family; MJE15032/33 and Toshiba power devices use B=1, C=2, E=3. No obvious swapped base/emitter connection was found. Check actual manufacturer's parts during assembly, especially because manufacturer and MPN fields are reversed in several BOM entries. [Diotec MPSA42](https://diotec.com/tl_files/diotec/files/pdf/datasheets/mpsa42.pdf)
- C1 is recorded as a Nichicon UES bipolar part, appropriate for input coupling. C4's positive terminal is on the R9 side; C5's positive terminal is OUT. Rail electrolytic polarities are correct. C4 normally has only small DC bias, whose exact sign depends on device offsets.
- AC gain is approximately `1 + 22k/1k = 23` (27.2 dB); DC gain is approximately unity. Input coupling is around 0.7 Hz using 10 uF and 23 kohms; the feedback transition is about 1.6 Hz using 100 uF and 1 kohm. R1/C2 provide RF filtering around 0.75 MHz for a low-impedance source, rather than a subwoofer crossover. These are first-order estimates including the relevant local resistances, not a simulation.
- SGND and GND are intentionally linked through R23 (10 ohm) in parallel with C10 (100 nF), matching the reference concept. This is a deliberate audio ground arrangement; do not replace it with an arbitrary ground-plane merge. J6.1 is SGND; J6.2 is input. J1 is signal output; speaker return must use the power-supply/power-ground system, not J6.1 or R23.
- Q1 current is roughly 2 mA for a conventional green LED. LED colour/type must be recorded: the symbol only says LED. Q1 dissipates roughly 0.1 W at 56 V; input-pair devices roughly 0.05 W each. No obvious voltage-rating problem was found for the MPSA42 or MJE15032/33 devices.
- Departures from the published Figure 1 include 2SA1943/2SC5200 power transistors, R16/R17=3R9 rather than 3R3, bipolar C1, and an added 100 nF C11 across D2/D3. The 3R9 value makes the main devices begin contributing at somewhat lower helper current (roughly 0.18 A rather than 0.21 A using 0.7 V). These are not identified as automatic faults, but reference performance/stability cannot simply be assumed.
- Toshiba rates these power devices at 230 V and 150 W at a 25 C case; voltage margin is adequate for 112 V rail-to-rail operation. Hot safe operating area and reactive-load capability remain unverified. Toshiba lists 2SA1943 as not recommended for new designs; this does not by itself prevent reuse of genuine suitable stock. [2SA1943 status](https://toshiba.semicon-storage.com/us/semiconductor/product/bipolar-transistors/detail.2SA1943.html), [2SA1943 datasheet](https://toshiba.semicon-storage.com/info/docget.jsp?did=20427&prodName=2SA1943)
- No onboard supply fuses, short-circuit limiting, thermal shutdown or DC speaker disconnect are present. Rail fuses must be provided externally. DC speaker protection is a system-level decision to resolve; no protection was added. This topology must not be treated as short-circuit tolerant. [ESP](https://sound-au.com/project68.htm)

## 3. PCB observations

Board is approximately **170.36 x 67 mm**, two copper layers, 1.6 mm thick. Positives include broad output/emitter copper, separated input and power regions, paired main output devices with individual emitter resistors, rail bypass components, and no net-assignment mismatch.

- **Feedback pickup:** R12.1 at (40.132,119.126) reaches the output copper near R16.2 at (72.39,116.84) through about 33.6 mm of 1 mm track. J1 is near x=141 mm. Thus feedback is taken from the helper end of the distributed output collection bus, not directly from the output connector. Consider a deliberate Kelvin pickup from the common output collection point when revising layout; preserve a quiet reference path. This is a distortion/grounding concern, not a proven oscillation fault.
- **Sensitive node extent:** Q3-base net includes about 36.6 mm of routing to R12 and C4. Keep the inverting input/feedback junction compact and away from the driver and high-current routes; C4 placement contributes a long branch.
- **Return geometry:** power GND uses a relatively narrow perimeter route, not a continuous plane. Keep speaker current out of the signal-ground link and do not assume the narrow GND route is suitable as the speaker-return path. C12/C13 are useful local reservoirs, but small-signal rail bypass at Q4 is physically remote; verify rail ringing with the actual PSU leads before adding/repositioning parts.
- **Current capacity:** main rail tracks include 3.5 mm sections and large output zones, but copper weight is unspecified. No current/temperature-rise qualification is claimed. At 4 ohms, 30 V peak means 7.5 A peak; 50 V peak means 12.5 A. Check necks, pad entries, connectors and actual copper thickness against those currents. Thin signal traces are not the principal issue here.
- **Clearance:** project default track clearance is 0.2 mm, while zones commonly specify 0.5 mm. A manufacturing DRC pass at these rules is not a dedicated 112 V spacing qualification. Review the minimum spacing specifically between opposing rail/drive nets and exposed metalwork; no claim of a regulatory violation is made from the default alone.
- **Serviceability:** component values are visible, but reference designators are generally absent from silkscreen. Add references and explicit +V/-V markings when revising. Test access can use resistor/pin pads, but defined rail/GND/output checkpoints would make commissioning easier.
- **Mechanical support:** only the power-transistor mounting holes are present; confirm PCB support, connector insertion forces and heatsink mass do not load transistor leads. A heatsink supported by the chassis should not hang from FR4/lead joints.

## 4. Load and thermal envelope

For an ideal Class-B stage, maximum total output-stage heat with a sine wave into a resistive load is approximately `2*Vrail^2/(pi^2*Rload)`, reached below clipping. This is a thermal planning estimate, not a transistor SOA check or measured dissipation:

| Rails | 4 ohms | 8 ohms |
|---|---:|---:|
| +/-35 V | 62 W | 31 W |
| +/-56 V | 159 W | 79 W |

Include driver losses, insulating-pad thermal resistance, enclosure temperature and margin. A sink permitting only 40 C rise at 159 W needs roughly 0.25 C/W sink-to-ambient before allocating additional losses. Description as 'big' cannot establish that rating.

Normal +/-35 V operation is substantially easier thermally. At +/-56 V into 4 ohms, the two main Toshiba devices per polarity require a hot-SOA/reactive-load review; their headline 150 W rating is not sufficient evidence. No blanket approval for sustained high power into 4 ohms is given.

At +/-35 V, even an ideal lossless stage cannot exceed about 153 W into 4 ohms or 77 W into 8 ohms. Real output is lower because of voltage losses and supply sag. The board's 300 W label therefore does not describe normal +/-35 V operation.

## 5. Verification status and next gate

- Fresh ERC: **230 findings: 2 errors, 228 warnings**. Errors are undriven power-input declarations on SGND/GND; external connector power needs correct ERC documentation. Warnings comprise 215 off-grid endpoints and 13 library-symbol mismatches (4 spade connectors and 9 generic transistor instances). The netlist is connected, so off-grid warnings are not evidence of 215 open circuits. Review library differences before updating symbols; do not overwrite custom mappings indiscriminately.
- Saved-fill CLI DRC: **0 violations, 0 unconnected pads**. No DRC exclusions are stored. Several checks are globally ignored, including missing courtyard, footprint filters/type, via-centre and tuning geometry checks. See `DRC-saved-fill.rpt`.
- Both `--refill-zones --schematic-parity` and a separate `--refill-zones` CLI attempt aborted with **exit 134**, without reports. **Freshly refilled DRC remains unverified**. Run refill and DRC in the GUI before fabrication. No board was saved by these commands.
- Independent numbered-pad-to-fresh-schematic-net comparison: **0 mismatches**. This checks net assignments, while the ordinary DRC checks saved-fill physical connectivity; neither substitutes for successful refilled DRC.
- Not simulated, bench tested, thermally tested, EMI tested or mechanically qualified. The preliminary 3D render did not load the transistor models, so it was not used to certify the heatsink assembly.

Before ordering: resolve voltage/wattage BOM entries and fit, establish the direct insulated heatsink interface and driver thermal tracking, consider compacting driver/feedback routing, then obtain a successful refilled GUI DRC. Before connecting a speaker: use current-limited startup, check DC offset and idle current, inspect both local driver loops/output for oscillation, and test sine/square-wave response into dummy loads with representative cable capacitance. Confirm bias/temperature after warm-up and under sustained load before increasing to the maximum rails. A low-frequency application still requires checking for high-frequency parasitic oscillation.

## Evidence and preservation

Review renders: `schematic.png`, `top-copper.png`, `bottom-copper.png`, `silkscreen.png`. Raw checks: `ERC.rpt`, `DRC-saved-fill.rpt`.

SHA-256 values verified unchanged during review:

```
SubAmp.kicad_sch 880274cbd0f7d8924f1fad9bc15b86bd935ae0f593f5f97278c3e70044b50fbe
SubAmp.kicad_pcb 570500681c628fcff10907af471ed5fe758ab5ed5f7642527f868b515402e8e2
SubAmp.kicad_pro 99eb448358337e1d72fc9c02cab50240fc3ac3da7adf65778888254217d956ed
```

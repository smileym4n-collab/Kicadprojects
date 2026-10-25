# MOSFETAmp2 — self-contained Codex handoff

Prepared: 25 October 2026, Europe/London.

Continue the amplifier design from the existing project. This document supplies the brief, decisions, work completed, failed qualification case and tools needed to resume without the previous conversation. Read the actual files before modifying them; this is a handoff, not a hardware release.

> **Update, 25 Oct 2026 (second session):** Blocker A has been studied and blocker B partly resolved. See `docs/BIAS_STUDY.md`. Genuine Infineon MODPEX models for both MOSFETs are now in `simulation/models/infineon/` (they still have no thermal or subthreshold behaviour). Variant B, which keeps the multiplier ratio fixed and sets the offset with an LED-referenced current sink plus a select-on-test RE, holds bias independently of threshold across the full 2–4 V datasheet window in simulation. It awaits user approval before the schematic, SPICE baseline, BOM and documents are changed. ERC was rerun on the current project settings (0 violations, scratch copy only); the project-file difference is KiCad settings only, with no exclusions. `tools/final_verify.py` and the manifest were not touched.

> **Update, 25 Oct 2026 (second session, continued):** With the user's approval, variant B is now implemented as **Rev 0.2**: `channel.cir`, `tools/build_schematic.py` and the KiCad sheets, the verifier, the BOM (140 parts), the purchase list and DESIGN/SIMULATION/BENCH/LAYOUT/README. The full simulation suite was rerun on the Infineon models (`MOSFET_MODELS=authored` gives the Rev 0.1 approximations). ERC: 0/0. Connectivity: 302 checks PASS. Rev 0.1 sources, documents and results are archived in `work/rev0.1/`. `tools/final_verify.py` was updated for Rev 0.2 (see its header). Sections 4–9 below describe Rev 0.1 and are historical where they conflict with `docs/`.

**Current disposition (Rev 0.2): experimental candidate; NOT ready for PCB fabrication. Open items: measured MOSFET VGS slope and select-on-test values, bias rail sensitivity, Q108 β and LED-slope sensitivities, hot linear-mode SOA, and all bench/thermal/layout work.**

## 1. Workspace and working rules

- Project: `/Users/tomwatson/Documents/GitHub/Kicadprojects/MOSFETAmp2`.
- Read applicable `AGENTS.md`, including `/Users/tomwatson/Documents/GitHub/Kicadprojects/AGENTS.md`. The user supplied the general electronics rules in the previous conversation; the parent file is present.
- The user values conservative, understandable, buildable and measurable hardware. ERC alone is not validation.
- Explain meaningful circuit/part/topology changes. Do not silently substitute devices, alter pin numbers or change the PCB.
- Use inventory MCP read-only. Never reserve/deduct stock or create purchase records.
- Preserve unrelated Git work. The project sits within a parent Git workspace; inspect its state before committing or making broad changes.
- No subagents/delegation were requested. Do not start separate tasks or send external messages without authorization.
- Use metric SMD package descriptions. Manufacturer/library identifiers containing imperial names may remain unchanged.
- Scope of the latest request was creating this handoff. No circuit changes were made while preparing it.

## 2. User brief and accepted clarifications

Design a useful, inexpensive stereo analogue Class-AB audio amplifier with:

- Two identical channels, one complementary **IRF540N/IRF9540N output pair per channel**.
- Prefer fully discrete BJT differential input, VAS and drivers; conventional single global negative-feedback loop.
- DC-coupled signal path preferred; approximately 20–26 dB gain and 22–47 kΩ input impedance.
- Through-hole preferred, standard inexpensive values, suitable owned components first.
- No MCU/DSP, no unnecessary regulators, no unnecessarily complicated circuitry.
- Normal load 8 Ω. Investigate 5–10 W/channel, but accept lower power when justified by gate-drive headroom. Assess 4 Ω without claiming support prematurely.
- Initial supply: TTI EL302RD dual-output current-limited bench supply, approximately ±12 to ±15 V, one channel at a time.
- Possible final supply: approximately 100 VA, 12-0-12 VAC transformer with external bridge/reservoir PCB. Amplifier accepts +V/GND/−V with local decoupling. No mains circuitry on amplifier PCB.
- Separate speaker-protection PCB is already owned; do not add an onboard speaker relay/protection system.
- **Explicit later instruction: no output short-circuit protection is required.** Output current-limit transistors were removed. Do not reintroduce them automatically. Gate clamps, source resistors, bias safeguards, Zobel and output coil remain appropriate.
- User subsequently clarified that **no transformer or reservoir capacitors are fixed yet**, and accepted conservative assumptions: 230 V primary, 10% transformer regulation and 4,700 µF per rail.
- User will do PCB layout. Assign footprints and give guidance; do not route the board.
- Owned equipment: EL302RD, Hanmatek DOS1102 scope, multimeter, 4 Ω/8 Ω high-power dummy load and audio generator. Heatsinks, mica washers, compound and hardware are owned, but heatsink specifications are unknown. Contact temperature measurement capability is not confirmed.
- No speakers during initial testing.

Required eventual deliverables: connected KiCad 10 stereo project, SPICE files/results, stock-versus-required BOM, purchase list, calculations/assumptions, unresolved verification items, layout guidance, bench procedure and README. Files exist for all these categories, but electrical qualification is incomplete.

## 3. Completed work and file map

The initial project had an empty schematic/PCB. Originals were backed up to `work/original/`.

| File/directory | Contents |
|---|---|
| `README.md` | Candidate architecture, status and document index |
| `MOSFETAmp2.kicad_pro` | KiCad project |
| `MOSFETAmp2.kicad_sch` | Root sheet, separate channel power/input/output connectors |
| `Channel.kicad_sch` | Reusable channel instantiated as LEFT and RIGHT |
| `MOSFETAmp2.kicad_sym`, `sym-lib-table` | Project-local symbols with explicit physical pin numbering |
| `MOSFETAmp2.pretty/`, `fp-lib-table` | Local air-coil and KEMET C315 capacitor footprints |
| `MOSFETAmp2.kicad_pcb` | Original empty PCB, preserved; no placement/routing |
| `BOM.csv` | Current 130-component stereo BOM, manufacturers, footprints, stock IDs/quantities and purchases |
| `inventory/` | Read-only MCP snapshots and selection/query evidence |
| `docs/DESIGN.md` | Topology, gate headroom, bias, PSU, thermal/SOA calculations and source links |
| `docs/SIMULATION.md` | Actual simulation tables, limitations and release gates |
| `docs/Schematic.pdf` | Three-page schematic review export |
| `docs/PURCHASE_LIST.md` | Current candidate purchases; bias-related entries may change |
| `docs/LAYOUT.md` | Two-layer layout and mechanical guidance |
| `docs/BENCH_TEST.md` | Conditional development bring-up procedure; read the bias failure warning first |
| `docs/plots/` | Six sets of actual-result plots, PNG/PDF |
| `docs/IRF540N.pdf`, `docs/IRF9540N.pdf` | Downloaded manufacturer datasheets |
| `simulation/channel.cir` | Current single-channel SPICE circuit |
| `simulation/models/devices.lib`, `simulation/models/README.md` | Models and explicit provenance/limitations |
| `simulation/results/` | Generated decks, logs, compressed numeric traces and three summary JSON files |
| `tools/build_schematic.py` | Deterministic schematic/library generator |
| `tools/verify_netlist.py` | Independent exported-KiCad pin/net graph checks against SPICE |
| `tools/make_bom.py` | BOM generation from exported XML and inventory snapshots |
| `tools/plot_results.py`, `tools/report_results.py` | Figures/report generated from saved simulation data |
| `tools/final_verify.py` | Consistency checks and hash manifest; contains revision-specific assertions |
| `work/stereo.xml`, `work/ERC.rpt` | Exported netlist and last recorded ERC |
| `work/connectivity_verification.json`, `work/verification_manifest.json` | Recorded verification evidence |
| `tools/ngspice/` | Locally compiled ngspice 47, macOS arm64, licensing/source notes |

**Generator warning:** rerunning `tools/build_schematic.py` overwrites generated schematic/symbol files. Keep it consistent with manual schematic changes, or deliberately retire/update it. It does not synthesize the SPICE circuit automatically.

## 4. Current circuit — candidate, not a fixed requirement

LEFT references are in the 100 series; RIGHT is generally the same reference +100. SPICE numbering omits this channel offset, e.g. Q8 is Q108/Q208.

- Q101/Q102: BC556 PNP differential pair, approximately 1 mA each; 100 Ω emitter degeneration.
- Q103/Q104: BC546 NPN current mirror.
- Q105: BC556 tail source, approximately 2 mA, using a two-diode reference and 330 Ω emitter resistor.
- Q115: BC546 buffer feeding Q106 BD139 VAS.
- Q107: BC556 active VAS load, approximately 6 mA, 100 Ω emitter resistor.
- D107 1N4148 + D108 BAT46: VAS anti-saturation clamp.
- Q109/Q110: BD139/BD140 emitter-follower gate drivers.
- Q111/Q112: IRF540N/IRF9540N complementary source followers.
- R119/R120: 0R33/5 W source resistors.
- R117/R118: 100 Ω gate stoppers; 47 kΩ G–S bleeds and BZX85C10 gate-source clamps.
- R103/R104: 22 kΩ/2.2 kΩ feedback divider, gain 11 from B1. Input 1 kΩ series + 22 kΩ shunt gives external gain about 10.52, **20.44 dB**, input about **23 kΩ**.
- C101: 220 pF C0G input filter, stocked 2012 metric SMD.
- C102: **330 pF C0G/50 V**, purchased radial KEMET C315C331J5G5TA. Increased from an early 220 pF candidate to improve reactive/parasitic stability margin.
- Zobel: 10 Ω/2 W + 100 nF film in series, OUT to GND.
- Output: approximately 0.7 µH air coil with parallel 10 Ω/2 W damper, **outside global feedback**. Feedback senses OUT before the coil; SPK is after it.
- Per-channel bypass: 220 µF/35 V and 100 nF/63 V from each rail to GND. Negative-rail electrolytic positive terminal goes to GND.
- GND is one common net; channel ± rails have separate connectors for independent bring-up.

Physical pins verified in the design mapping: BC546/556 C1/B2/E3; ST BD139/140 E1/C2/B3; IRF540N/9540N G1/D2/S3, drain tab live. Confirm actual owned-part manufacturer/package before assembly. Electrically insulate output tabs and bias-sensor collector tabs from a common heatsink.

### Current bias network

D109 BZX79-C4V3 is in series with Q108 BD139 VBE multiplier, with Q108 thermally attached/insulated to the output heatsink.

- R112 = 1 kΩ collector-to-base.
- R113 = 47 kΩ base-to-emitter.
- R114 = 130 Ω in series with RV101, 2 kΩ multiturn, as another base-emitter branch.
- RV101 pins 2 and 3 tied together: maximum measured resistance is minimum bias. Open wiper/track failures reduce nominal spread; shorted-pot/sensor failures are not covered.
- C103 = 100 nF across BP–BN.
- J101 shorts **BP to BN** for an output-off first-power check. This is a bias commissioning link, not output short-circuit protection.
- Approximate spread: `VZ + VBE × (1 + 1k / [47k || (130 + RV)]) + IB × 1k`.
- Nominal simulated spread ≈8.59 V; 50 mA P-device idle at ±15 V requires RV≈37.7 Ω in the authored models. **Never copy this as a construction setting.** It uses only about half a turn of a 25-turn 2 kΩ track, which is another practical reason to improve the adjustment.
- 16.5 mV per 0R33 corresponds to 50 mA. TP101–TP102 measures N current; TP102–TP103 measures P current; corresponding RIGHT points are TP201–203.
- Minimum spread ≈5.38 V, open adjustment branch ≈5.09 V. Zero-resistance trimmer endpoint produces about 0.63 A in the nominal model: full adjustment range is not a safe blind sweep.

## 5. Main blockers — distinguish demonstrated model failure from missing evidence

### A. Bias compensation needs redesign or substantially better justification

This is the main engineering task for the next agent, not something to offload to the user through repeated trimming or lucky part selection.

The current network couples DC bias adjustment to thermal compensation. Lower-threshold devices need a smaller DC spread, which produces a smaller VBE multiplier ratio and too little temperature compensation.

In `simulation/supplement.py`:

- Low-threshold case: `VTON=2`, `VTOP=-2`, `RV=2000`, sensor/drivers 27 °C → **48.8 mA**.
- Same case at imposed MOSFET temperature 75 °C, sensor/drivers also 75 °C, threshold magnitudes reduced by 4 mV/K and KP scaled by `(348.15/300.15)^−1.5` → **262.5 mA**.

**Important qualification:** these are author-imposed sensitivity assumptions in simplified models, not measured devices, calibrated manufacturer electrothermal results or a demonstrated physical thermal runaway. They expose a compensation weakness that the current design has not resolved. Do not repeat the number as a guaranteed real-device outcome.

For the nominal higher-threshold models, tracked temperature gives about 50 mA at 27 °C and 32 mA at 75 °C; leaving sensor/drivers cold while MOSFETs are imposed hot gives about 227 mA. At 75 °C, imposing 2/4/6 mV/K threshold slopes gives approximately 0.08/32/108 mA. Therefore one apparently good nominal-temperature plot is not enough.

Investigate conventional bias arrangements that give adequate, preferably independently controllable, DC spread and temperature compensation, with safe initial setting, useful trim resolution and fail-low open-wiper behaviour. Keep complexity justified. Do not assume merely lowering idle current, increasing the heatsink or thermally clamping Q108 fixes the failed corner. Any redesign needs cold/warm/device-spread/thermal-lag checks before being replicated as a qualified stereo design.

### B. Manufacturer models were not successfully obtained

Official MOSFET model download attempts returned empty responses or 403/404 errors. Do not claim these models are manufacturer supplied:

- MOSFETs: **authored Level-1 approximations**, VTO 3.4/−3.77 V, KP 20/7.07 A/V², fixed lumped Cgs/Cgd, simple body diodes/series resistances.
- BD139/BD140, BAT46 and Zeners: authored approximations.
- BC546B/BC556B: nominal NXP models copied from installed LTspice, not measurements/models of the owned ST/onsemi stock.
- MOSFET intrinsic `TEMP=27` is fixed deliberately. Temperature sensitivity is imposed using VTO/KP, with sensor/driver temperatures varied separately. Global `.temp` is not a substitute.
- No self-heating, die hotspots, qualified SOA or realistic full nonlinear gate-charge model.

Seek official usable models and/or actual device characterization. Verify subcircuit pin order before substitution. Even an official switching model may not validate low-current thermal behaviour or SOA. Do not tune invented parameters to obtain attractive distortion figures.

### C. Hot linear-mode SOA remains unknown

Manufacturer PDFs reviewed give 100 µs/1 ms/10 ms single-pulse SOA curves at case 25 °C; no guaranteed hot DC operating envelope was established. A 20 Hz half-cycle is 25 ms and conduction is repetitive. Headline switching current, RDS(on), wattage and whole-die thermal impedance do not establish hotspot immunity.

At the assumed ±21 V ceiling and 8 Ω, resistive instantaneous loss is roughly 13.2 W at about 1.26 A/10.5 V VDS; off-device voltage can approach 42 V. Reactive loads can combine larger VDS/current. Whole-die thermal-only derating factors are about 0.667 at case 75 °C and 0.50 at 100 °C, but these are not guaranteed hot-SOA multipliers.

This is a missing-evidence issue, not a demonstrated SOA violation. Obtain manufacturer guidance where possible and define conservative experimental load/temperature limits. No 4 Ω rating or output-short rating is supported. Do not reintroduce output current limiting against the user's explicit preference.

### D. Bench/mechanical facts still needed

- Actual MOSFET VGS-versus-temperature at relevant fixed currents; prepare a controlled current-limited fixture/procedure before asking the user to perform measurements.
- Heatsink model/dimensions, mounting/enclosure and real thermal resistance. A shared-sink analytical target was ≤1.5 K/W under a conservative high-rail stereo heat assumption; it is not a verified owned-sink specification.
- Confirm contact thermometer/thermocouple availability.
- Generic 2 kΩ pot body, pinout and turn count; exact power-resistor dimensions; actual air-coil L/DCR/formed footprint.
- Actual PSU rail extremes/ripple once a transformer/capacitors are selected.
- Real DC offset, HF stability, distortion/noise, clipping recovery, warm-up and signal-to-idle behaviour.

## 6. Inventory and sourcing already done

MCP inventory was successfully queried read-only. Saved records are in `inventory/`; refresh live availability before a final BOM. No quantities were modified, parts reserved or purchases made. Selected records reported zero reserved quantity at query time.

| Part / stock ID | Available then | Current stereo requirement |
|---|---:|---:|
| IRF9540N, 257 | 12 | 2 |
| IRF540N | 0 | 2 minimum, purchase |
| IRFZ44N, 258 | 9 | 0; deliberately unused |
| BC546, 254 | 36 | 6 |
| BC556, 462 | 20 | 8 |
| BD139, 148 | 13 | 6 |
| BD140, 149 | 22 | 2 |
| 0R33/5 W MCKNP05SJ033KAA9, 288 | 6 | 4 |
| 2 kΩ generic multiturn, 529 | 19 | 2 conditional on fit/pinout |
| 220 pF C0G/50 V, 2012 metric, 198 | 20 | 2 |
| KEMET R82DC3100DQ50J, 100 nF/63 V film, 406 | 92 | 8 |
| Rubycon 35ZLH220MEFC8X11.5, 220 µF/35 V, 366 | 19 | 4 |
| 1N4148, 138 | 63 | 10 |
| BZX85C10, 251 | 8 | 4 |
| MC34629 two-pin headers, 126 | 40 | 4 |

Ordinary TE 0.6 W metal-film resistor stock covers the other selected values; see BOM/snapshots for exact IDs and aggregate quantities. Avoid awkward series/parallel combinations just to avoid buying a cheap standard value.

Current candidate purchase list: 2 IRF540NPBF, 2 BZX79-C4V3, 2 BAT46-TR, 2 C315C331J5G5TA 330 pF, 2 LR1F130R, 4 ROX2SJ10R 10 Ω/2 W, 2 Phoenix 1715734 three-way power connectors, 2 Phoenix 1715721 two-way outputs, and optionally 2 Bourns 3296W-1-202LF if generic pots do not qualify. Bias-related selections are provisional pending redesign.

BAT46 replaced stocked 40 V 1N5819 to improve reverse-voltage margin against the possible 42 V bus. Output coils are hand-wound candidates, approximately 12 turns of 1 mm enamelled copper on an 8 mm mandrel; measure them. Ten wire-loop test points and two bias shorting shunts need workshop supplies confirmed.

Preferred purchasing: DigiKey UK, Mouser UK, Farnell or CPC; genuine manufacturer parts. Board assumption is inexpensive two-layer JLCPCB. Do not rely on previously observed distributor prices/stock remaining current.

## 7. Recorded simulation results — development evidence only

The tests cover OP, idle current/offset, 20 Hz/1 kHz/20 kHz sine, clipping sweeps, AC response, approximate harmonic distortion, square waves, reactive/capacitive loads, approximate loop gain, temperature/tolerance sensitivity, ideal rail ramps and supply extremes. All use the limitations above.

| Stiff rails / 8 Ω | Fundamental Vpk at last tested point below 0.1% model THD | Power |
|---|---:|---:|
| ±12 V | 5.68 V | 2.02 W |
| ±15 V | 8.45 V | 4.47 W |
| ±16 V | 9.44 V | 5.57 W |
| ±18 V | 11.29 V | 7.96 W |
| ±20.5 V | 13.63 V | 11.61 W |
| ±21 V | 14.12 V | 12.46 W |

High-rail rows are stress/feasibility cases, not supported continuous stereo power ratings. The likely final project is around 5 W/channel, subject to actual rail valleys and device drive. Gate headroom consumes roughly 6–7 V per rail; do not force a 10 W claim from ±15 V.

At ±15 V/nominal 50 mA: simulated offset ≈6.54 mV, rail currents ≈62 mA each, idle input power ≈1.87 W/channel. At 1.73 W/8 Ω, approximate THD(2–10) is 0.005% at 1 kHz and 0.104% at 20 kHz; these are not hardware specifications. Slew estimates are about +5.97/−5.20 V/µs. Gain relative to 1 kHz is about −0.011 dB at 20 kHz.

Approximate first-crossing phase margins: 79° at 8 Ω; 68° with severe 100 nF/reactive loads; 66° with selected parasitics. Voltage injection uses `−V(FB)/V(FBI)` at Q101's feedback input. It is not a full two-injection/Tian proof; high-frequency feedthrough/finite impedances make the ratio unreliable at very high frequencies. Open 100 nF loading shows significant post-coil ringing. No measured PCB stability is established.

Ideal rail-ramp simulations show approximately 0.34 V symmetric and 1.06 V asymmetric startup excursions; external speaker protection/muting needs real testing.

## 8. PSU and thermal assumptions

Approved calculation assumptions: 12-0-12 VAC full-load secondary, 230 V primary, 100 VA, 10% no-load regulation, 4,700 µF/rail, 50 Hz. Bridge across 24 VAC with centre tap as GND: approximately one effective diode drop per rail, two across the bus.

- Low scenario: 216 V mains, full-load secondary factor 1.00, diode 1 V, 0.9 A/rail, capacitors at −20% → about 14.94 V charging peak and 12.55 V ripple valley; wiring could reduce valley further.
- Nominal scenario: 230 V, factor 1.07, diode 0.85 V, 0.75 A/rail → about 17.31 V peak, 16.51 V average, 15.71 V valley.
- High/no-load scenario: 253 V, factor 1.10, diode 0.55 V → about 19.98 V; illustrative +3% secondary tolerance raises it to about 20.60 V.
- ±21 V is an assumed design ceiling, **not an electrically/thermally qualified rating**. Actual transformer/capacitor data must replace these assumptions later. Use ≥35 V electrolytics for the anticipated supply.

MOSFET data reviewed: 100 V VDS magnitude, ±20 V VGS, Tj max 175 °C, RθJC 1.15 K/W N and 1.1 K/W P. Headline case-25 °C dissipation is not a usable audio rating. See `docs/DESIGN.md` for loss equations and detailed caveats.

## 9. Validation state and fresh handoff finding

Last electrical verification recorded:

- KiCad **10.0.5**, ERC **0 errors / 0 warnings** at the then-current project settings.
- **278** independent connectivity checks, **130** components, **280** connected pins.
- Footprint files exist and contain the expected numbered pads; two local footprints also parsed/exported using KiCad CLI. This does not prove mechanical fit.
- PCB remained byte-for-byte identical to its empty original. No layout/DRC/bench/thermal release.
- 104 simulation logs checked. `rv_0.log` records zero-ohm coercion to 1 pΩ and a failed dynamic-gmin attempt followed by successful true-gmin convergence; no transient timestep failure was reported. This endpoint is not a precise physical wiper-contact model.

**Fresh check while writing this handoff:** all files listed in the recorded SHA256 manifest still match **except `MOSFETAmp2.kicad_pro`**. The PCB and schematic sources still match. The project JSON now contains additional board defaults, schematic/BOM/annotation settings, an ERC section and a populated top-level-sheet entry; `erc_exclusions` is empty. This looks consistent with KiCad initializing/saving project settings, but the origin was not established.

Do not restore the project file over current work just to satisfy a checksum. Review its JSON diff against `work/original/MOSFETAmp2.kicad_pro` and rerun ERC with the current settings. **`tools/final_verify.py` currently asserts byte-for-byte project-file preservation and will fail that guard** until this legitimate/settings-only difference is handled deliberately. Its earlier `original_project_and_pcb_preserved=true` claim is historical, not a claim about the current project file.

The verifier also hardcodes the current 130-part count, 330 pF compensation and absence of former limiter references. A justified redesign may require reviewing/updating those assertions; do not mistake them for immutable electrical requirements or weaken them merely to obtain a pass.

## 10. Tools, reproduction and update workflow

KiCad CLI:

```sh
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli --version
```

ngspice 47 executable: `tools/ngspice/bin/ngspice` (macOS arm64). Licensing/source provenance are in `tools/ngspice/COPYING` and `SOURCE.md`. Set `NGSPICE` to another compatible executable if needed. Native component models do not require external OSDI devices.

Python requirements: `simulation/requirements.txt` (`numpy`, `scipy`, `matplotlib`); use an appropriate environment. The previous run used bundled Python at:

`/Users/tomwatson/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3`

with temporary libraries under `/private/tmp/mosfet-python`, set through `PYTHONPATH`; `MPLCONFIGDIR=/private/tmp/mosfet-mpl`. Check these paths still exist; temporary dependencies are not a durable project prerequisite.

Run simulation scripts **sequentially**, as later scripts read earlier summaries and output filenames are reused:

```sh
python3 simulation/run.py
python3 simulation/extended.py
python3 simulation/supplement.py
python3 tools/plot_results.py
python3 tools/report_results.py
```

`run.py` changes working directory to `simulation/` when imported. Individual generated decks expect that working directory for includes. Data loader accepts `.txt` or losslessly compressed `.txt.gz`; fresh `.txt` takes precedence. Current saved traces are compressed; reruns create uncompressed files. Avoid parallel runs against the same results directory and preserve old evidence when comparing revisions.

After an actual electrical revision, keep SPICE, generator, KiCad, model provenance, BOM and written results consistent. Then export/check:

```sh
python3 tools/build_schematic.py
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli sch export netlist --format kicadxml -o work/stereo.xml MOSFETAmp2.kicad_sch
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli sch erc -o work/ERC.rpt MOSFETAmp2.kicad_sch
python3 tools/verify_netlist.py
python3 tools/make_bom.py
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli sch export pdf -o docs/Schematic.pdf MOSFETAmp2.kicad_sch
```

Resolve the project-settings preservation guard described above before using `tools/final_verify.py` to refresh the manifest. The pin/net verifier does not constitute a full numerical SPICE-versus-schematic value audit; check values and device models separately. Visually inspect regenerated schematic pages after edits. Do not suppress genuine ERC issues or overwrite the user's PCB.

## 11. Recommended resumption order

1. Read this handoff, applicable AGENTS, `docs/DESIGN.md`, `docs/SIMULATION.md`, model provenance and `simulation/channel.cir`. Inspect current Git/project state and the project-settings-only hash difference.
2. Address the bias architecture first. Treat the current schematic as a candidate that may need revision; explain and justify changes. Assess both temperature slope and adjustment/failure behaviour across realistic device spread.
3. Seek better manufacturer models. Identify which remaining facts require measurements rather than more simulation. Prepare a practical low-risk characterization fixture/table if actual VGS/temperature data are needed.
4. Re-evaluate headroom, SOA/thermals, recovery and feedback stability under any revised circuit. Keep 8 Ω and low-rail commissioning as the initial scope; output short-circuit protection remains omitted.
5. Only after satisfactory electrical evidence, update the stereo implementation, inventory-based BOM, purchases, calculations and bench/layout documents, rerun checks and state exactly what remains unverified.

The user has offered to help resolve blockers. The most useful outstanding inputs are genuine model archives, heatsink details and confirmation of contact temperature measurement capability. They have not yet supplied those. The final transformer/capacitors remain intentionally unfixed. Avoid transferring responsibility for the unresolved bias design to the user.

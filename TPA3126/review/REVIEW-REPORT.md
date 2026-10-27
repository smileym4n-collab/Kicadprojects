> **Current update — 23 October 2026:** See [pre-order corrections](revisions/preorder-corrections-2026-10-23/README.md), [current purchasing list](PURCHASING-LIST.md) and [current inventory table](INVENTORY-USAGE.md). The material below describes an earlier revision; old schematic ZIPs are historical. Current working schematic PDF has been regenerated. Do not replay legacy design scripts against the current project.

# ESP32-WROVER / PCM5122 / TPA3126D2 schematic review

19 October 2026 - one board - schematic completion only.

**Status: revised for 2 x 15 W into 4 ohms at 16 V; schematic for review. Latest KiCad 10.0.5 ERC: 0 errors, 31 pre-existing off-grid warnings.** No PCB edits were performed by the agent; a concurrent external PCB save prevents a byte-for-byte preservation claim for this turn. Project settings and local preferences retain their revision-baseline hashes. This is not PCB, acoustic, thermal or production qualification. PLIMIT calibration, the salvaged amplifier/heatsink and the external UES capacitor require bench verification.

Open `TPA3126.kicad_pro` and its top schematic. The five-sheet plotted review is [TPA3126-schematic.pdf](TPA3126-schematic.pdf). Detailed [inventory usage](INVENTORY-USAGE.md), [purchasing list](PURCHASING-LIST.md), [BOM metadata](bom-and-inventory.json), [netlist](validation/final.xml), [ERC evidence](validation/final-erc.json), [418 passing checks plus one external preservation record](validation/connectivity-checks.json) and [calculations](validation/calculations.json) accompany this report. The original files and SHA-256 hashes are in `original/`.

## A. Schematic completion

All five original sheets were inspected before editing. The PCM5122 power/charge pump, I2C mode straps, output RC filters, ESP32 programming buttons, proven signal GPIOs and most of the power circuit were reusable. The amplifier had only its inputs and grounds connected. Missing sheet ports, undriven controls, dangling legacy TPA3220 signals, missing LEDs/UART connector, incomplete supplies and off-grid endpoints were corrected.

- Completed every TPA3126D2 connection: supplies, bypassing, four bootstraps, two stereo BTL filters, gain/mode straps, limiter, shutdown/mute/fault circuitry, connectors and diagnostic pads.
- Retained the installed amplifier symbol's physical pin numbering. Changed its electrical pin types to match this circuit, including open-drain FAULTZ and master SYNC output.
- Retained DAC circuitry, 470R/2n7 C0G output filters and four 1u film amplifier coupling footprints. Added source attenuation and matched negative-input reference impedances.
- Connected I2C, DAC mute, amplifier controls and input-voltage sensing through the existing hierarchy. Removed obsolete OTW/reset interfaces that do not describe this amplifier.
- Added a real six-pin UART header, I2C pull-ups, mode LEDs and local ESP32 bulk decoupling.
- Retained the existing buck plus two-LDO power topology, with a lower intermediate voltage and a more suitable transient clamp.
- Added a bypassable external capacitor loop for CH2. C54 is an external assembly item, excluded from PCB placement.
- Preserved existing non-power component UUIDs. No IC, firmware GPIO, amplifier class, digital/analogue architecture or main ground system was replaced.

The top level and amplifier use A3 drawing sheets for readability; the hierarchy and filenames remain intact. All ordinary ground symbols resolve to the same **GND** net. Quiet and switching returns are a placement/routing requirement, not artificial isolated ground domains.

## B. Significant changes and footprint decisions

Latest revision: input pad and PLIMIT changed for the requested 2 x 15 W target at 16 V. See [15W-POWER-REVISION.md](15W-POWER-REVISION.md) for calculations, inventory checks and current validation. The previously approved Panasonic C37-C40 selection is retained.

| References | Final selection / change | Reason |
|---|---|---|
| U1 | TPA3126D2DADR; standard KiCad `Texas_DAD0032A_HTSSOP-32_6.1x11mm_P0.65mm_TopEP3.71x3.81mm` | Correct top-PowerPAD package, 32 leads, no bottom exposed-pad solder land. The original custom land was shorter than the standard footprint. No pin numbers changed. |
| C1/C2/C5/C6 | Retained 1u film, 63 V, original 7.2 x 5 mm / 5 mm pitch footprint | Appropriate AC coupling for low gain; no need for larger coupling capacitance in a protected small-driver system. Owned Kemet parts need their pitch checked; named WIMA fallback fits. |
| R12/R14, R13/R15, R16/R17 | 1k2 series, 1k5 shunt, 820R source-ground reference | Supports 15 W target while approximately balancing AC source impedances. New pad resistors are 1%; owned references remain 0.5%. |
| R18 | 5k6 to GND; upper gain resistor absent | Minimum 20 dB, master mode. |
| R19/R20/C29 | 10k from 3V3-ESP, R20 DNP, C29 1u | Filtered external PLIMIT reference gives headroom for 15 W; calibrated DSP sets application limits. |
| C24-C27 | 220n / 25 V X7R, 2012 metric | Correct bootstrap capacitors. |
| C28/C32/C33/C34/C35/C36 | 1u GVDD/AVCC, 100n PVCC, two 220u / 35 V Rubycon ZLH reservoirs | Completes local amplifier bypassing. Final PCB must distribute these locally at the appropriate pins. |
| L2/L3 | Two owned CSAD0660-100M packages | Four 10u windings, one package per bridge. |
| C37-C40 | Four 680n / 450 V DC, 5% Panasonic ECW-FE2W684J polypropylene capacitors | TI shunt-to-GND filter topology, one capacitor per leg. Assigned 18 x 7 mm / 15 mm pitch footprints for the 17.5 x 7 x 12.5 mm Panasonic body; 1.2 mm holes accommodate its 0.8 mm leads. These were absent in the incomplete amplifier sheet. |
| C41-C44 / R35-R38 | 330p C0G / 18R, all **DNP** | TI-based tuning provision; no claimed optimized snubber and no inherited TPA3220 values. 18R candidates are 125 mW; validate pulse stress before fitting. |
| C54 / J18 | External UES1H470MPM, 47u / 50 V bipolar, plus capacitor-loop header | User-requested fail-safe with stereo bypass. Current/temperature qualification remains necessary. |
| R21/R25/C30 | 10k series, 100k pull-down, 100n | SDZ is low without a driven GPIO. |
| R26/R29/C31 | 10k series, 100k pull-up to ESP 3.3 V, 100n | MUTE is high without a driven GPIO; RC limits command slew. |
| R30 | 100k pull-up to ESP 3.3 V | FAULTZ open-drain level compatible with ESP GPIO35. |
| R24 | **13k7 -> 16k2 / 1%**; R23 remains 100k | Intermediate rail changes from 4.98 V to 4.304 V, improving LDO dissipation while allowing worst-case dropout. |
| D2 | **SMAJ18A -> Littelfuse SMBJ16A**, `Diode_SMD:D_SMB` | 26 V rated pulse clamp provides more margin below the amplifier's 30 V absolute maximum. Unidirectional symbol: cathode on PVDD, anode GND. |
| C47 | 220u / 35 V Rubycon ZLH, 8 mm diameter / 3.5 mm pitch | Input bulk reservoir after reverse protection. |
| C55 | 22u / 25 V, 3216 metric | Local ESP32 transient reservoir, in addition to C3 100n. |
| C7/C10 | 10u / 50 V and 22u / 25 V Nichicon UFW; 5 mm diameter / 2 mm pitch | Correct footprints for the specifically identified owned electrolytics. Values retained. |
| J1/J16/J17 | Molex 09-65-2028; `Molex_KK-396_5273-02A_1x02_P3.96mm_Vertical` | Matches confirmed stock part, including body; retains 3.96 mm connector family/pitch. |
| F2 | Littelfuse 39613150000, T3.15A / 125 V, retained TE5 footprint | Specifies an actual time-delay fuse. 395-series fuses themselves are fast-acting; their TE5 body footprint is compatible. |
| U2 cached symbol | Mode-qualified PCM5122 I2C/VREF electrical types | ADR1/ADR2 are inputs in this mode; VCOM is the specified ground reference in VREF mode. Physical pin map retained, no No-ERC markers. |

All required nonstandard symbol/footprint dependencies are project-local. Imported module exposed-ground segments numbered 39-47 remain connected to GND; these are CAD segmentation of the common exposed ground region, not additional numbered manufacturer signal terminals.

## C. Inventory usage

The full required table, including every fitted passive and DNP alternatives, is [INVENTORY-USAGE.md](INVENTORY-USAGE.md). It uses live MCP results rather than assumptions. Key allocations:

| Component | Manufacturer part number | Quantity required | Inventory quantity confirmed | Purchase required |
|---|---|---:|---:|---|
| Amplifier | TPA3126D2DADR (record TPA3126) | 1 | 1 | No, salvaged part requires inspection |
| DAC | PCM5122PWR | 1 | 0 | Yes unless physically present but unlogged |
| ESP32 | ESP32-WROVER-IE-N16R8 | 1 | 1 | No |
| Buck | LMR51430XFDDCR | 1 | 1 | No |
| ESP32 LDO | TLV1117LV33DCYR | 1 | No matching record | Yes |
| DAC LDO | TPS7A2033PDBVR | 1 | 14 | No |
| Dual inductors | CSAD0660-100M | 2 | 2, reserved 0 | No |
| Buck inductor | SRP6030WA-6R8M | 1 | 5 | No |
| Reverse FET | DMP4015SK3 | 1 | 3 | No |
| 220u / 35 V reservoirs | 35ZLH220MEFC8X11.5 | 3 | 19 | No |
| Bootstrap capacitors | CL21B224KAFNNNE | 4 | 48 | No |
| Output film capacitors | ECW-FE2W684J | 4 | No matching record | Yes |
| External tweeter capacitor | UES1H470MPM | 1 | No matching record | Yes |
| Molex power/speaker headers | 09-65-2028 | 3 | 16 | No |
| UART header | MC34635 | 1 | 10 | No |
| Capacitor loop header | MC34629 | 1 | 40 | No |
| Wi-Fi / BT LEDs | KP-2012LSGC / KP-2012EC | 1 each | 1 / 10 | No |

Unidentified generic inventory parts are recorded by inventory ID and verified value/package/tolerance; no manufacturer identity has been invented. In particular, a stocked 2012 resistor is not treated as a replacement for an inherited 1608 footprint. Nothing was reserved or deducted from inventory. Prices and distributor stock are not guaranteed by this review.

## D. Power supply report

**J1 -> F2 -> reverse P-FET Q1 -> PVDD (12-16 V) -> amplifier directly.** D1 clamps gate-source voltage; D2 absorbs bounded input transients. C47 is input bulk; C35/C36 are local amplifier reservoirs. This is not protection against a sustained wrong-voltage supply.

**PVDD -> U3/L1 -> 4V_PRE = 4.304 V -> U4 -> 3V3-ESP**, and **4V_PRE -> R1/C7/C8 -> IC4 -> DAC 3.3 V**. There is no required 5 V peripheral rail. U3 remains a 500 kHz forced-PWM 3 A converter, not its PFM variant. L1 ripple is 0.93 A p-p at 16 V nominal; approximately 1.3 A p-p at conservative inductance/frequency corners. With a 1.1 A design transient budget, peak inductor current is about 1.75 A, well below normal rated current; converter short-circuit limiting still requires bench checks.

Use 0.25 A average and 0.5 A peak as planning figures for ESP32 operation, with a **1 A rail/transient design envelope**, not a guaranteed measured firmware load. Budget 50 mA for the DAC rail and a few mA for LEDs/control. At 4.304 V, the ESP LDO dissipates about 0.25 W at 0.25 A, 0.50 W at 0.5 A and 1.00 W at 1 A. The 1 A envelope is a transient/electrical capability; continuous operation there needs adequate copper and thermal validation. DAC LDO dissipation at 50 mA is roughly 0.045 W after R1.

With 1% divider resistors and the buck's 1.5% reference allowance, 4V_PRE is about **4.167-4.444 V** before ripple/transients. The lower corner exceeds 3.3495 V + the TLV1117LV33's 700 mV maximum 1 A dropout by about 117 mV; 500 mA operation has more practical margin. Measure rail undershoot at Wi-Fi bursts and maximum temperature. Do not substitute an ordinary 1117 variant whose dropout/stability differs. C52 is ceramic, as required for TLV1117LV stability.

At 2 x 15 W output and 85-90% amplifier efficiency, amplifier input is 33.3-35.3 W and amplifier heat is 3.3-5.3 W. Add roughly 1-3 W for radio/regulators, giving approximately 2.15-2.4 A at 16 V. A regulated **16 V, 3 A** external supply is a sensible starting point; verify transients and inrush. Output must derate at lower supply voltages. F2 and the connector remain subject to actual adapter/inrush checks. Q1 conduction loss at 2 A using 11 milliohms is 44 mW at the datasheet test temperature, rising when hot.

VIN_SENSE is PVDD/11 on ADC1 GPIO36: 1.09-1.45 V over the specified operating range. Firmware should detect a falling input early enough to mute before dropout; ADC threshold, filtering and real hold-up must be measured. There is no independent supply-loss supervisor or hard watchdog added.

## E. ESP32 pinout and firmware contract

Exact retained module: **ESP32-WROVER-IE-N16R8**, 16 MB flash / 8 MB PSRAM, external antenna. All seven proven assignments are unchanged.

| Function | GPIO | Module pin | Status / default |
|---|---:|---:|---|
| Wi-Fi LED | 32 | 8 | Retained; active high through R8 |
| Bluetooth LED | 33 | 9 | Retained; active high through R7 |
| I2S LRCK | 25 | 10 | Retained; R4 22R source damping |
| I2S BCK | 26 | 11 | Retained; R5 22R source damping |
| I2S DATA | 13 | 16 | Retained; R9 22R source damping |
| I2C SCL | 19 | 31 | Retained; 4k7 pull-up |
| I2C SDA | 21 | 33 | Retained; 4k7 pull-up |
| Amplifier enable / SDZ command | 27 | 12 | Added; HIGH enables, external LOW default |
| Amplifier MUTE command | 23 | 37 | Added; HIGH mutes, external HIGH default |
| Amplifier FAULTZ | 35 | 7 | Added; input-only GPIO is appropriate; 100k external pull-up |
| DAC XSMT | 18 | 30 | Added; LOW mutes; existing 10k pull-down |
| PVDD sense | 36 | 4 | Completed inherited provision; ADC1 input only |
| UART TX / RX | 1 / 3 | 35 / 34 | Programming UART retained |
| BOOT | 0 | 25 | 10k pull-up, momentary to GND |
| EN/reset | EN | 3 | 10k pull-up, 1u, momentary to GND |

GPIO18/23/27 are output-capable, non-strapping pins in this module. GPIO35/36 support input use only. None of the additions uses flash GPIO6-11, PSRAM GPIO16/17, or strapping GPIO0/2/5/12/15. Existing GPIO13 is a JTAG-capable pin but is retained for its proven I2S function. Unused module NC pads remain unconnected.

J2 pinout: **1 GND, 2 ESP RX, 3 ESP TX, 4 EN, 5 GPIO0, 6 3V3 reference**. Cross the adapter TX/RX. Use 3.3 V logic and power the board from J1; do not feed adapter power into pin 6. There is no USB-UART circuit.

DAC: I2C **0x4C**, MODE1 low, MODE2 high, both address pins low; SCK grounded. Use 64fs BCK/32-bit I2S slots and PLL referenced to BCK. Initialize both digital-volume registers muted, retain normal clock-error handling and **VREF mode (P1 R1 OSEL=0)**, then ramp both channels together for master volume. Hardware grounding of VCOM assumes VREF mode; do not change to VCOM mode.

Recommended sequence: stabilize rails; boot with SDZ low/MUTE high/XSMT low; configure DAC and DSP while muted; start valid I2S; enable SDZ; wait at least 50 ms; release DAC and amplifier mute; ramp volume from silence. Shutdown reverses this, allowing at least 150/fs + 0.2 ms for DAC soft mute before power loss. At 48 kHz this is about 3.33 ms. On fault, mute/shut down and diagnose before deliberately cycling SDZ. Do not automatically retry a persistent fault.

## F. Amplifier, filters and protection

### Level and input arrangement

Gain is 20 dB nominal (10 V/V), master mode. Before limiting or external attenuation, an ideal 16 V BTL rail could support 11.31 Vrms / 32 W into 4 ohms; with 0.29 ohm series loss, a simple model gives about 10.55 Vrms / 27.8 W. These are ceilings, not measured low-distortion output specifications. Corresponding unpadded sensitivity is about 1.06-1.13 Vrms. At 12 V the same lossy model gives about 7.91 Vrms / 15.65 W.

DAC full scale is approximately 2.1 Vrms. With retained 470R plus the revised **1k2/1k5 pad**, nominal attenuation is **0.4658 (-6.64 dB)**. Full scale requests **9.78 Vrms / 23.9 W** before clipping/PLIMIT. This provides tolerance headroom for the **15 W / 4-ohm target (7.75 Vrms)**. It is not a passive 15 W cap. Retain 20 dB gain and calibrate independent DSP limits at the output connectors; nominal -2.03 dBFS is only an initial calculation. Amplifier gain is specified 19-21 dB and DAC gain error up to +/-6%; load/filter response also matters. Begin bench firmware well below the calculated limit.

Each unused differential input is **AC referenced through an equal 1u capacitor**, with 820R on the source side. Do not directly ground the amplifier input pin: it carries internal DC bias. Positive source impedance is about 790 ohms and negative reference 820 ohms, giving external source RC time constants near 0.8 ms. Input high-pass corners are approximately 3 Hz, far below the eventual driver crossover. The datasheet gives differing 50k/60k input figures; calculations conservatively use 50k with its stated tolerance. Retained 470R/2n7 DAC filtering is about 125 kHz unloaded and slightly altered by the input pad.

### PWM and output filters

MODSEL low selects hybrid modulation. AM2/AM1/AM0 = 000 selects 400 kHz nominal (376-424 kHz specified range). SYNC is an unused master output, intentionally no-connect. Both channels remain independent BTL bridges. The original convenient channel order is explicit: **DAC LEFT -> amplifier RIGHT -> J16 woofer/CH1; DAC RIGHT -> amplifier LEFT -> J17 tweeter/CH2**.

Each bridge has two 10u windings and **680n from each filtered leg to GND**. Differential equivalents are 20u and 340n, giving a natural frequency of **61.0 kHz**, not the 43 kHz obtained by wrongly treating one 680n as the differential capacitor. For a resistive 4-ohm load Q is about 0.522 and the calculated 20 kHz attenuation about 0.8 dB. Real driver impedance and tolerances change this; measure electrical response and include it in DSP/acoustic development.

Worst-case simple per-leg ripple estimate at 16 V, L=8u and 376 kHz is **1.33 A p-p / 0.384 A RMS**. At 15 W into 4 ohms, audio current is 1.94 A RMS; RSS including that ripple is 1.97 A, with peak approximately 3.40 A. Actual hybrid-mode waveforms need measurement. Film capacitor HF ripple voltage is approximately 0.65 V p-p at this conservative corner; at a 7.75 Vrms differential / 20 kHz sine, each shunt capacitor carries about 0.331 A RMS of audio current. Panasonic's permissible-current graph shows approximately 2.6 A RMS at 200 kHz for the 680n / 15 mm pitch version. This provides substantial current margin, but the published current curve stops before the 376-424 kHz switching band; verify temperature/ripple with the actual switching waveform, near the LC resonance and with open/real loads. Do not infer a 400 kHz AC voltage rating from its 450 V DC marking. DNP snubbers remain unqualified until waveforms/EMI are measured.

### Codaca verification

Inventory confirms **CSAD0660-100M**, quantity 2, reserved 0. The manufacturer drawing shows windings **1-2 and 4-3**. The retained footprint has 1/2 on one side and 4/3 on the other in top view; both are used as series inductors, never as a common-mode choke. The drawing depicts separate winding/core structures without polarity dots; no flux cancellation or defined coupling coefficient is assumed. The manufacturer does not publish a guaranteed mutual-coupling limit, so "perfectly uncoupled" is not claimed.

Per the manufacturer's table: 10u +/-20%, DCR **47 milliohms typical / 55 milliohms maximum per winding**, **3.5 A thermal current** at a 40 C rise, **6.5 A typical saturation current at 30% inductance reduction**, 125 C maximum including self-heating. The current-related curves are typical 25 C data. They comfortably cover the proposed normal output envelope but do not guarantee minimum inductance at all fault/temperature corners.

TI requires at least 1u remaining under a short circuit. Codaca's typical 100M curve remains several uH near TI's approximately 7.5 A typical trip point, suggesting suitability; this is **not a guaranteed worst-case fault qualification**, particularly with temperature and simultaneous winding heating. Before release, obtain a guaranteed hot L-vs-I limit or perform controlled current-limited short-circuit validation. Verify continuity 1-2 / 4-3 on the actual stock and check winding independence with an LCR meter before assembly. Estimated copper loss at 15 W is about 0.43 W per dual package using maximum DCR and the ripple estimate; core loss is additional.

### PLIMIT and driver limits

R19 now feeds PLIMIT from regulated **3V3-ESP through 10k**; R20 is DNP and C29 remains 1u (10 ms RC). TI permits an external reference. Nominal 3.3 V avoids the large GVDD tolerance of the old divider. The TI peak virtual-rail model gives approximately **18.9 W unclipped into 4 ohms**, or 18.4-19.5 W for the +/-1.5% reference allowance alone, with 0.29 ohm total series loss. Illustrative 0.5 ohm hot loss gives 17.2 W nominal. This leaves headroom above 15 W; it is not an accurately guaranteed watt cap. TI Table 3's Vrms label/example remains inconsistent with the peak-rail equation. Calibrate the real onset and do not infer an RMS or excursion limiter from peak clipping.

Use a differential probe or suitable isolated measurement system across BTL outputs. Never attach an earthed oscilloscope ground clip to either speaker terminal. Measure clipping, THD and severe-clipping RMS power at 12 and 16 V with dummy loads, individually and together. Set independent DSP limits to the application and calibrated 15 W maximum. At 12 V, 2 x 15 W clean output is not guaranteed; use VIN_SENSE and measured supply-aware derating.

The SB10PGC21-4's **20 W rating uses a 200 Hz, 12 dB/octave Butterworth high-pass test condition**; it is not a broadband bass rating. Its 4.5 mm peak-to-peak linear travel is only +/-2.25 mm. Using its listed low-frequency compliance, force factor and DC resistance gives roughly 0.77 mm/V static displacement in free air, illustrating why a few watts of bass can exceed travel. No universally safe woofer high-pass can be specified without the enclosure and SPL target.

The tweeter's thermal rating similarly does not authorize low-frequency drive. PLIMIT is common to both channels and is a voltage clipper, not independent driver/excursion/thermal protection. The amplifier's own DC detection is slow enough that it cannot replace the external tweeter capacitor or DSP protection. Valid I2S carrying incorrect crossover data or full-scale noise will not be detected as an I2S clock fault.

### External UES capacitor and stereo use

C54 is **Nichicon UES1H470MPM**, bipolar 47u / 50 V, +/-20%, 10 mm diameter x 20 mm length, 5 mm pitch. It connects across **J18 pins 1-2** in the CH2 positive lead, after the LC filter. Do not connect either pin to GND. For stereo, unplug the capacitor harness and install an insulated shorting link/shunt rated at least 3 A. With neither capacitor nor link fitted, CH2 positive is open. Change the configuration only while unpowered; the stereo firmware must also use appropriate stereo processing.

A nominal 4-ohm approximation gives **847 Hz**, -0.33 dB and about 16 degrees phase shift at 3 kHz. With 3.2-ohm DC resistance the pole estimate is 1.06 kHz. Actual impedance near resonance invalidates a purely resistive acoustic prediction. Include the cap in crossover measurements; this first-order safeguard is not a passive crossover.

**UES qualification limitation:** the manufacturer describes this as an audio small-signal bipolar series and does not provide a continuous speaker-current rating on its series sheet. Its voltage/capacitance fit is verified; sustained speaker-level ripple capability is not. Measure capacitor voltage, current, ESR and temperature with the intended high-pass programme before adoption. If heating or loss is excessive, retain J18 and use a qualified external speaker-crossover capacitor after user review. The 10u UES parts in inventory are not combined to approximate 47u.

### Heatsink

TPA3126D2's exposed pad is on **top**, with specified junction-to-top thermal resistance about 1.2 C/W. TI permits grounding it (preferred) or leaving it floating. Electrical insulation is not required merely because the grounded pad contacts a grounded sink; insulation is required if the mounting could contact another potential. Do not trust anodizing as electrical insulation and never connect the sink to PVDD. Use a thin suitable nonconductive thermal adhesive/interface or mechanically restrained contact, avoiding conductive adhesive and pin shorts.

The salvaged **20 x 18 x 10 mm** sink has no known thermal resistance. Its dimensions alone cannot qualify it; it is substantially smaller than TI's continuous-power EVM sink. Reserve at least the full sink envelope plus assembly clearance, preferably about 24 x 22 mm, and its height above the package. Check underside overhang clearance from every lead, component and trace, coax access and mechanical retention.

At 30 W total audio output, 85-90% amplifier efficiency implies about **3.3-5.3 W heat**. This is a planning range, not measured efficiency. The requested ATS-TI1OP-521-C1-R1 CAD asset is available but has not been selected/placed by this revision. Its 8.5 C/W rating is at 200 LFM forced airflow, not natural convection; enclosed operation needs testing. With 50 C compartment air, 1 W dissipation, a 2 C/W interface and assumed sink values of 30/50/80 C/W, estimated junction temperatures are approximately **83/103/133 C**. At 2 W they become **116/156/216 C**. This demonstrates sensitivity to the unknown sink and enclosure. The absolute junction limit is 150 C; target below 125 C and do not use thermal shutdown as normal control. Measure case/air temperatures under both-channel sine tests and representative high-crest-factor music before enclosure installation.

## G. KiCad validation and intentional dispositions

- Baseline KiCad 10.0.5 ERC: **272 findings**. Earlier completion ERC: **0 findings**. Latest 15 W revision ERC: **0 errors, 31 off-grid warnings**, also present with the same identities in its pre-change snapshot; `--severity-all` was used.
- No ERC exclusions exist and none were added. No No-ERC markers were used. True no-connect markers document unused GPIOs, NC pads and master SYNC.
- Power flags remain where legitimate supply paths cross passive elements: protected external input, GND, buck output after L1 and DAC LDO input after R1. The DAC's actual LDO output is typed as a power output.
- This power revision leaves the current project ERC configuration unchanged. Its pre-existing disabled checks are single-global-label, four-way-junction, simulation-model and footprint-filter checks; the report does not imply those optional checks ran.
- **418 checks pass, with one separate external preservation-change record:** complete IC pin dispositions, hierarchy-derived connectivity, bootstrap matching, preserved GPIOs, channel routing, independent BTL terminals, cap-loop separation, regulator/protection polarity, assigned footprint pad sets, retained physical pin mappings/UUIDs and protected project/settings checks. The concurrently saved PCB is explicitly marked CHANGED_DURING_RUN rather than preserved.
- KiCad's schematic loader/netlist exporter and PDF plotter loaded all five sheets successfully. No GUI save was used. The PDF was visually inspected; all project-local libraries resolve.
- No PCB DRC was run because no board change was authorized. Existing PCB connectivity is stale relative to the completed schematic.

## H. Subsequent PCB design notes

Historical envelope asset: project-local `Custom:Heatsink_20x18x10mm_TopMount_Clearance24x22mm`. F.Fab shows the 20 x 18 mm sink body and Dwgs.User shows a 24 x 22 mm assembly guide. The current saved schematic has no HS1 instance. Consider the later ATS asset and clearance reviews during future placement; no pads, holes or copper keepout are inferred. The guide is manual, not DRC-enforced. Height 10 mm is above the package/interface. See [HEATSINK-FOOTPRINT.md](HEATSINK-FOOTPRINT.md).

Use a maximum 100 x 100 mm four-layer board; no placement/routing has been performed. Suggested stack: L1 components/critical loops, L2 continuous GND, L3 power distribution, L4 slow control. Do not cut a general analogue/digital ground split.

Keep PVCC bypass loops at both IC supply ends short and tied to the corresponding GND pins. Put AVCC/GVDD and bootstrap capacitors at their pins, not together as the drawing's visual bank. Keep each bootstrap loop and switching-node copper compact. Inductors go near the amplifier; keep both legs symmetric and carry filtered speaker pairs together. Connect the shunt capacitors with short local returns, not through the DAC ground corridor. Snubbers, if fitted, return locally to amplifier GND. Avoid oversized switching copper and unnecessary capacitive overlap under switch nodes while maintaining the primary ground reference elsewhere.

Route each DAC signal and its source-side ground reference together to its input coupling pair. Keep them away from the buck SW node, inductors and speaker wiring. Put the quiet DAC LDO/charge-pump caps locally; do not share analogue return necks with amplifier/buck currents. Source 22R resistors belong at ESP32 pins; route BCK/LRCK/DATA above uninterrupted ground. Keep I2C short; choose 100 kHz if bus capacitance makes 400 kHz rise-time compliance marginal.

Reserve the complete heatsink volume before any placement. Keep its conductive overhang away from IC leads and capacitors. Place headers so J18's capacitor/link function and floating speaker terminals can be labelled clearly. J2 needs explicit pin-1 and 3.3 V logic/reference markings. The IE module uses an external antenna; plan coax routing/connector access and an external antenna environment clear of metal, sink and switching circuits. Do not apply PCB-antenna assumptions from a WROOM/E module to the IE connector variant.

## I. Review gates and unresolved risks

1. **Bench calibrate PLIMIT and the real full-scale/output-level envelope** before connecting drivers. Resolve the TI example inconsistency by measurement or TI clarification; do not claim a precise hardware watt limit from this report.
2. **Verify the salvaged IC and small heatsink** electrically, mechanically and thermally; no sink resistance or hot-compartment test is available.
3. **Validate Codaca hot/fault behavior and winding identification.** Published typical curves are not a guaranteed minimum-inductance fault specification or coupling limit.
4. **Qualify UES at speaker current**, as above, with its bypass option. Its suitability for continuous high-current use is not established by its 50 V rating.
5. **Select driver-specific crossover, high-pass and limiter settings** for each enclosure/application. The board deliberately has no fixed acoustic alignment. Loss of clocks is muted by the DAC; incorrect valid audio needs firmware/DSP safeguards. Hardware defaults do not detect a running but malfunctioning application with valid clocks.
6. **Complete footprint/assembly checks on actual stock**, particularly generic film-cap lead pitch, R2/R3 tolerance, the module exposed-ground segmentation, connector mating parts, and heatsink overhang. A pad-number check is not fabrication qualification.
7. **Measure supply transients, power-off pops, RF/audio interference, LC response, open-load ringing and temperatures** during the subsequent prototype phase. Confirm fuse/inrush/TVS coordination for the actual adapter and cables.
8. **Review/update the PCB only in a future explicitly authorized task.** Then run DRC, parity, thermal/mechanical and manufacturing checks before ordering. Passing this schematic ERC does not release the inherited board.

## Primary documentation

- [TI TPA3126D2 datasheet, SLOS942](https://www.ti.com/lit/ds/symlink/tpa3126d2.pdf), including pin table, gain table, bootstrap guidance, PLIMIT model, filter, DAD package and thermal data.
- [TI TPA3126D2 EVM, SLOU506](https://www.ti.com/lit/pdf/slou506). The EVM/typical diagrams pair BSPL with OUTPL and BSNL with OUTNL; the pin-table prose swaps those left names. This schematic follows the matching-name diagrams, not that prose typo.
- [TI PCM5122 datasheet, SLAS763C](https://www.ti.com/lit/ds/symlink/pcm5122.pdf).
- [Espressif ESP32-WROVER-E/IE module datasheet v2.4](https://documentation.espressif.com/esp32-wrover-e_esp32-wrover-ie_datasheet_en.pdf), and [ESP32 schematic guidance](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/schematic-checklist.html).
- [Codaca CSAD0660 manufacturer PDF](https://www.codaca.com/Private/pdf/CSAD0660.pdf).
- [LMR51430](https://www.ti.com/lit/ds/symlink/lmr51430.pdf), [TLV1117LV](https://www.ti.com/lit/ds/symlink/tlv1117lv.pdf), [TPS7A20](https://www.ti.com/lit/ds/symlink/tps7a20.pdf), [DMP4015SK3](https://www.diodes.com/assets/Datasheets/DMP4015SK3.pdf), [Bourns SRP6030WA](https://www.bourns.com/docs/product-datasheets/srp6030wa.pdf).
- [WIMA MKP2](https://www.wima.de/en/our-product-range/metallized-capacitors/mkp-2/), [WIMA MKS2](https://www.wima.de/en/our-product-range/metallized-capacitors/mks-2/), [Nichicon UES1H470MPM](https://www.nichicon.com/en-us/part/ues1h470mpm/5425/), [Same Sky TS02](https://www.sameskydevices.com/product/resource/ts02.pdf), [Molex 09-65-2028](https://www.molex.com/en-us/products/part-detail/09652028).
- [SB Acoustics SB10PGC21-4](https://sbacoustics.com/wp-content/uploads/2020/02/3in-SB10PGC21-4.pdf), [Dayton ND25FA-4 manufacturer specifications](https://www.daytonaudio.com/product/1196/nd25fa-4-1-soft-dome-neodymium-tweeter-4-ohm).
- [Littelfuse 396 fuse](https://www.littelfuse.com/assetdocs/littelfuse-fuse-396-datasheet?assetguid=28004c2f-992c-4d86-8a35-f495c62803a6). [Littelfuse SMBJ manufacturer-indexed sheet](https://www.littelfuse.com/~/media/electronics/datasheets/tvs_diodes/littelfuse_tvs_diode_smbj_datasheet.pdf.pdf). Direct SMBJ PDF endpoints were unavailable; SMBJ16A 16 V standoff / 26 V pulse clamp and SMB package were cross-checked against manufacturer-indexed data and distributor records. Recheck the current manufacturer sheet before procurement; this is not a claim of successful local retrieval.

Locally retrieved manufacturer PDFs are in `datasheets/`. The Dayton PDF download returned an HTML access response; its manufacturer web specifications were accessible. Retrieval failures are not presented as successful document downloads.

- [Panasonic ECW-F(E) catalog](https://industrial.panasonic.com/cdbs/www-data/pdf/RDI0000/ast-ind-152809.pdf), [Panasonic current/temperature performance curves](https://mediap.industry.panasonic.eu/assets/imported/industrial.panasonic.com/cdbs/www-data/pdf/RDI0000/ABD0000COS38.pdf), [DigiKey UK purchasing page](https://www.digikey.co.uk/en/products/detail/panasonic-electronic-components/ECW-FE2W684J/5881196).

## Capacitor revision validation

The workspace had intervening KiCad saves after the initial completion report (19:18 on 19 October 2026). Its PCB/project hashes therefore differ from the initial originals. This revision preserves that newer user state; it does not restore older files. `revisions/panasonic-output-caps/protected-hashes.json` records the pre-revision snapshot. A fresh netlist comparison confirms every electrical connection is unchanged by this capacitor substitution. The 405-check script was rerun with `--preservation-baseline review/revisions/panasonic-output-caps/protected-hashes.json`; original symbol pin maps and component UUID checks still use the original schematic files.

## Heatsink footprint revision validation

HS1 and its explanatory text/cache are the only additions to Amp.kicad_sch in this revision. All original circuit content and net connections are unchanged. The new footprint loads/exports through KiCad 10.0.5, and its 20 x 18 mm F.Fab rectangle and 24 x 22 mm Dwgs.User guide were checked numerically. No pads, drill holes, copper keepouts or collision-producing F.CrtYd were added. ERC remains zero findings and the updated connectivity/package suite passes 407 checks. Protected files are checked against `revisions/heatsink-envelope/protected-hashes.json`.

## Output-inductor winding-order revision

At the user's request the complete windings within L2 and L3 were exchanged to remove crossed PCB connections. The inductor instances are mirrored vertically in the schematic; physical symbol/footprint numbering and winding pairs 1-2 / 4-3 are unchanged.

| Amplifier output | Inductor input | Filtered output |
|---|---|---|
| U1 pin 29, woofer positive | L2 pin 4 | L2 pin 3 -> C37 / J16 pin 1 |
| U1 pin 27, woofer negative | L2 pin 1 | L2 pin 2 -> C38 / J16 pin 2 |
| U1 pin 23, tweeter positive | L3 pin 4 | L3 pin 3 -> C39 / J18 pin 1 |
| U1 pin 21, tweeter negative | L3 pin 1 | L3 pin 2 -> C40 / J17 pin 2 |

L2 remains the woofer bridge and L3 the tweeter bridge. Speaker polarity, bootstrap-to-output pairing, values, footprints and all other electrical connections are unchanged. The PCB is not edited; a future schematic-to-PCB update is needed to apply the new pad-net assignments.

Latest winding revision: actual ERC reports zero violations and 405 current checks pass using `--preservation-baseline review/revisions/output-winding-swap/protected-hashes.json`. The saved amplifier sheet at the start of this revision no longer contained HS1 following intervening user saves; the heatsink footprint remains in the project library. This winding-only revision preserves that current state and does not reinsert unrelated schematic content.

## Current PCB heatsink-clearance review

A later read-only inspection of the current saved placement finds C24-C27 beneath a centred flat heatsink. Their 1.25 +/-0.10 mm bodies are too tall to assume safe clearance over a 1.00-1.15 mm IC. A proposed 5 mm left offset retains full top-pad coverage, gives approximately 1.0 mm to those capacitor bodies and 3.1 mm to C10 in plan view, and avoids moving the bootstrap components. This proposal is not applied to the PCB and needs actual mounting/tilt/retention verification. Remaining amplifier bypass parts are not placed locally. See [HEATSINK-CLEARANCE-REVIEW.md](HEATSINK-CLEARANCE-REVIEW.md) for bounds, sources, illustrations and limitations.

## Latest 15 W revision validation

See [15W-POWER-REVISION.md](15W-POWER-REVISION.md). Only R19 pin 1 changes net membership (GVDD to 3V3-ESP); all other electrical connections remain identical in fresh netlists. Six resistor instances and two notes changed. No PCB edits were performed by the agent; concurrent external saves affected the PCB and top-level schematic, and are preserved. Actual final ERC has 0 errors and 31 pre-existing capacitor-bank grid warnings. These have not been suppressed or described as a clean ERC.

Current user-added C56/C57 carry inconsistent inherited part metadata (1n / 1608 metric versus a 100n / 3216 metric MPN). This power-only revision preserves their source; resolve their actual selections before procurement.

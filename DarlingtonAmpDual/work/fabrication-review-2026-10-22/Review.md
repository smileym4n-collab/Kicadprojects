# DarlingtonAmpDual fabrication review — 22 October 2026

**READY FOR FIRST PROTOTYPE FABRICATION.** The present PCB passes a fresh native KiCad DRC with zone refill and schematic parity enabled. I found no electrical connectivity, copper-clearance, drill or outline blocker. This decision includes the user's confirmed assembly method: Q11–Q14 and Q9 mount **below** the board, leads bent upward into the pads, with their tab faces against the heatsink and fasteners through the existing NPTH holes. The user has successfully used this construction on multiple projects. A top-side rendering of the library footprints does not represent that assembly.

This is a saved-file schematic/PCB review, not simulation or measured amplifier qualification. Approval is for an initial prototype; sustained 4 Ω operation, hot current sharing, bias tracking and capacitive-load stability remain bench qualifications. No circuit, board, library or project-setting changes were made.

**Checks and evidence**

| Check | Current result |
|---|---|
| KiCad version | 10.0.5 |
| Fresh schematic ERC, all severities | 0 violations; `erc.json` |
| Native GUI PCB DRC, refill enabled | 0 violations; `native-drc.rpt` |
| Native GUI unconnected items | 0 |
| Native GUI schematic parity | 0 |
| Individual DRC exclusions | None in the project |
| Independent fresh netlist comparison | All 123 numbered PCB pads match the schematic; no value/footprint differences |
| Intentionally absent component | C3: schematic explicitly sets `on_board no`, `dnp yes` |
| Outline | One closed rectangle, 81.153 × 98.933 mm |
| Board | Two copper layers; nominal thickness 1.6 mm |
| Routing | 172 straight segments + 81 arcs; all explicit routes 1.0 mm wide; 21 copper zones; no vias |
| Holes | 121 plated holes, 5 NPTH holes; no slots |
| Minimum calculated circular-drill PTH annulus | 0.320 mm, using the smallest pad dimension |
| Saved source preservation | SHA-256 checks of PCB, schematic, project and both library tables passed |

The project retains five ignored DRC test categories: missing courtyards, track endpoints not centred on vias, tuning-profile geometries, footprint-filter mismatches and footprint component-type mismatches. I changed none of these settings. There are no vias or tuned routes here; the ignored footprint checks mean the clean DRC is supplemented by the package/pad inspection described below. Electrical clearance, shorts, unconnected items, edge clearance, courtyard overlap, holes and mask-bridge checks are enabled. Default net clearance is 0.20 mm; board-edge copper clearance is 0.50 mm.

The command-line DRC crashed with exit 134 and produced no report. The successful DRC result above is from the GUI, with both refill and schematic parity visibly checked, and its native report was saved. A command-line Gerber export requesting automatic zone refill also crashed. Ordinary saved-state Gerber and separate PTH/NPTH drill exports succeeded; they are isolated in `gerbers-review-only/`. Those plots are review evidence, **not a released order package**: regenerate the final upload from a refilled and saved PCB and inspect the fabricator's preview. No files were uploaded or ordered.

**PCB layout findings**

1. **Output-stage connections and local base stoppers pass.** R17/R19 are independently fed by DRIVE_N; R18/R20 are independently fed by DRIVE_P. Each resistor feeds only its own output base. Resistor-to-base pad separations are approximately 5.24, 5.27, 4.48 and 4.48 mm respectively. The longer common drive branches terminate at these individual stoppers. There is no cascaded base-stopper connection.

2. **Emitter ballast and output collection pass.** Q11.3 → R1.3, Q12.3 → R1.1, Q13.3 → R23.3 and Q14.3 → R23.1. Both dual-resistor centre terminals join AMP_OUT. The individual emitter paths use broad back-copper pours rather than the 1 mm small-signal routing. Feedback R10 and Zobel C5 connect before L1; J4 and the far side of R22 connect after L1. R22 is across L1, as intended. No connection has been inferred solely from a net label: pad assignments and native routing connectivity were checked separately.

3. **Power routing is credible for the initial 8 Ω prototype.** Both output pairs receive the correct collector rails through broad pours. The positive rail runs on the right/front and the negative rail on the left/back. The common speaker-output path is poured copper, with both J4 holes connected. I found no isolated 1 mm track forced to carry the entire speaker current. At a representative 31 V peak output, load current is 3.88 A peak into 8 Ω or 7.75 A peak into 4 Ω. Select the fabrication copper weight deliberately; these observations do not establish a measured temperature-rise rating for the pours or salvaged coil.

4. **The grounding arrangement is usable with deliberate external wiring.** C6/C7, C8/C9, the Zobel return and J7 meet in the upper power-ground region. The input and feedback-capacitor returns reach it via the outer/bottom ground copper. The speaker return is external: take it to the intended power-ground/star connection, not through the input cable/J2 ground. Likewise, avoid routing reservoir charging or chassis currents through the quiet input return. The saved note calling J2 pin 2 the ground/star is obsolete: J2.1 is GND and J2.2 is INPUT; the power-ground terminal is J7.

5. **Compensation placement is good; decoupling locality is the main refinement.** C4 is close to Q8 and its DRIVE_N connection. However, C7/C9 sit beside the upper output pair. Their relevant rail pads are about 42 mm in a straight line from Q11/Q12 collector pads; the actual return loops are longer. No separate local rail-to-ground bypass pair is fitted beside the lower outputs/VAS. This is not evidence of oscillation and is not a demonstrated fabrication blocker. It is the first layout refinement I would consider if commissioning reveals HF rail movement or ringing; local bypass placement should be considered before treating this as a production layout. No capacitors or routes were added during review.

6. **No visible component overlap or edge-fit blocker was found in the footprint outlines.** The body and courtyard check passed under the existing rules. All component reference designators are hidden on the PCB; values alone make troubleshooting harder, especially for the repeated 100 Ω, 33 Ω and 2k2 parts. Adding visible references would improve assembly/serviceability but is not required to manufacture this prototype. The supplied copper PNGs add reference labels for review; they are not manufacturing plots.

**Underside assembly and package checks**

The mounting concern is closed by the user's explicit underside construction. Fit the devices in their intended orientation with leads rising into the existing pad order; underside mounting does not itself require changing the electrical pin numbers. Do not mirror the lead order as an additional operation. Use the actual device lead form and a 1:1 board print during assembly preparation.

| Device | PCB electrical pad order | Relevant physical checks |
|---|---|---|
| Q11/Q13, 2SD2390 | 1 B, 2 C, 3 E | 5.45 mm pitch, 1.50 mm lead holes; 3.40 mm NPTH |
| Q12/Q14, 2SB1560 | 1 B, 2 C, 3 E | Same PCB geometry as NPN partners |
| Q9, BD139 | 1 E, 2 C, 3 B | 2.28 mm pitch, 1.00 mm lead holes; 3.20 mm NPTH; onsemi pin map checked |
| Q8/Q10, 2SA1837/2SC4793 | 1 B, 2 C, 3 E | Manufacturer drawing has nominal 2.54 mm lead pitch, consistent with assigned pad pitch |
| Q1/Q2/Q5/Q6/Q7, 2SC2240 | 1 E, 2 C, 3 B | Manufacturer TO-92 drawing checked; board uses a spread 2.54 mm lead form |
| Q3/Q4, 2SA970 | 1 E, 2 C, 3 B | Manufacturer TO-92 drawing checked; board uses a spread 2.54 mm lead form |
| J4–J7, TE 62409-1 footprints | Both pads on the same terminal net | PCB uses 1.43 mm holes; TE specifies a nominal 1.40 mm PCB hole |
| R1/R23, salvaged dual emitter resistor | Pins 1–2 and 2–3 are separate 0R22 sections | 10 mm adjacent pitch; 1.30 mm holes; confirm the actual salvage leads/body |
| L1, salvaged L505 | AMP_OUT → SPK_OUT | 12 mm lead pitch, 2.30 mm holes; coil current/temperature requires measurement |

Output mounting-hole centres in KiCad front-view coordinates, mm:

| Device | X | Y |
|---|---:|---:|
| Q13 | 250.444 | 27.432 |
| Q14 | 198.120 | 27.432 |
| Q11 | 250.444 | 56.388 |
| Q12 | 198.120 | 56.388 |
| Q9 | 224.536 | 77.738 |

Use the established insulating pads/shoulder washers and suitable support in this construction: output collector/tab nodes are on opposite rails, and Q9's collector is DRIVE_N. NPTH holes alone do not insulate a metal transistor tab or screw. Accommodate the different Q9/output-package thicknesses so tightening does not bow the PCB or strain the leads. Support the board while inserting/removing the FASTON receptacles. There are no independent board-mounting holes beyond the five transistor holes; that is consistent with the user's stated mounting scheme rather than an omitted mounting requirement.

The 3D render is illustrative only: it shows the library's default mounting orientation, some models are unavailable, R23 has no attached model, and R1/L1 use absolute model paths into the neighbouring DarlingtonAmp project. It is not an underside assembly or complete collision verification.

**Schematic and assembly notes**

The fresh schematic check agrees with the validated topology. Rail polarity and output collector/emitter connections are correct. C6 positive goes to +35 V and negative to GND; C8 positive goes to GND and negative to −35 V. C2 is explicitly bipolar. RV1 pins 2 and 3 are tied to DRIVE_P and R16 goes to pin 1, preserving the intended wiper arrangement. C3 is intentionally absent from the PCB, rather than an unrouted missing part. C1 is now fitted as an input coupling capacitor; the older note stating that a direct input link is fitted no longer describes the saved circuit. With 22k and 2.2 µF, its nominal high-pass corner is approximately 3.29 Hz. Midband feedback gain is 1 + 22k/1k15 = 20.13; the nominal C2/R11 low-frequency corner is approximately 0.629 Hz.

Keep the following in the assembly specification; none requires a topology change:

- C4: the saved value specifies 100 pF / 100 V, which addresses the voltage concern. Specify C0G/NP0 explicitly for the installed 2012 metric part. C4 can see much more than one rail voltage during signal swing.
- C6/C8: saved values omit their voltage rating. Use parts rated above the maximum actual rail, including high-mains/no-load behaviour, that fit the 10 mm body / 5 mm lead pitch. 63 V is the conservative assembly choice discussed previously; an existing 50 V part requires an actual maximum-rail check.
- C5/C7/C9/C10: record the installed dielectric, voltage rating and physical fit. C5 is the Zobel capacitor, not a supply bypass.
- R21/R22: record power rating and construction; use appropriately rated low-inductance parts fitting the 15.24 mm pitch footprints. Verify the salvaged R1/R23 section ratings and L1 wire/temperature capability.
- Correct the stale TP1/TP2/TP3 bias instructions. For each NPN section measure R1/R23 pin 3 relative to pin 2; for each PNP section measure pin 2 relative to pin 1. An 80–100 mA provisional target corresponds to 17.6–22 mV across each 0R22 section. Measure all four sections separately.
- Output transistor values no longer consistently carry the same optional-branch markings as R19/R20/R23. Specify the actual assembly variant. The complete optional branch is Q13, Q14, R19, R20 and R23; partial omission is not the single-pair variant.
- The schematic's output network still extends beyond the printed A3 sheet. The fresh netlist includes it and PCB parity passes, but the clipped PDF should not be the sole wiring/assembly reference.

At ±35 V the proposed 80–100 mA bias dissipates approximately 2.8–3.5 W in each output device at idle, or 11.2–14 W across four devices. Ideal equal-sharing Class-B worst-case resistive signal dissipation is approximately 7.76 W/device into 8 Ω and 15.5 W/device into 4 Ω with two pairs. These figures do not include all Class-AB/reactive-load losses or prove a heatsink/SOA rating. No protection was added: the saved circuit has no onboard DC speaker protection, output current limiting or thermal shutdown. Use the intended external system protection and current-limited commissioning procedure.

**Release boundary**

The PCB is suitable to send for an initial prototype using the user's established underside heatsink assembly. Before uploading the order, refill and save the final PCB, export fresh Gerbers and both drill files from that same saved state, and check the fabricator preview for the correct 81.153 × 98.933 mm outline and five unplated mounting holes. Do not reuse a similarly named older DarlingtonAmp export folder.

Commissioning still needs DC offset/startup checks, all four bias currents cold and hot, output current sharing, clipping recovery, square-wave/capacitive-load stability, heatsink/coil/copper temperatures and intended external protection checks. These are prototype tests, not reasons to claim an otherwise clean PCB has failed fabrication rules. Production readiness and sustained 4 Ω capability are not established by this review.

Manufacturer references: [Sanken 2SD2390](https://www.semicon.sanken-ele.co.jp/sk_content/2sd2390_ds_en.pdf), [Sanken 2SB1560](https://www.semicon.sanken-ele.co.jp/sk_content/2sb1560_ds_en.pdf), [onsemi BD139](https://www.onsemi.com/download/data-sheet/pdf/bd139-d.pdf), [ST BD139](https://www.st.com/resource/en/datasheet/bd139.pdf), [TE 62409-1](https://www.te.com/en/product-62409-1.html). The Toshiba manufacturer PDFs already saved in this project were visually inspected for the small-signal and VAS transistor package drawings.

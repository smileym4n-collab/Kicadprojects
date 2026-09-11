# Stereo schematic cleanup — 8 September 2026

The three active schematic sheets have been redrawn with visible local wiring. The stereo architecture, hierarchical sheet identities, and every original physical component are preserved. The project now has 194 physical components, up from 190. The current schematic was backed up in `../pre-cleanup-20260908` before editing.

## Electrical changes

| Reference | Change |
|---|---|
| R29, R36 | Audio input series resistance: 47k → 51k |
| R43, new | 4.7 Ω between +12V_GD and +12V_A |
| C50, new | 22 µF / 25 V from +12V_A to GND |
| C51, new | 100 nF / 25 V from +12V_A to GND |
| TP34, new | Test point with value +12V_A |

Both OPA1656 packages, U1 and U3, have pin 8 on +12V_A and pin 4 on GND. Their existing local 100 nF + 4.7 µF bypass pairs, C32/C33 and C34/C35, are retained and moved electrically to +12V_A. UCC27301A devices U2, U6, U102 and U106 retain +12V_GD on pin 1; none is supplied by +12V_A. A PWR_FLAG models the powered rail after R43, since ERC does not propagate a power-output pin through a passive resistor. This is not an ERC exclusion.

R30/R37 remain 10k to VREF_2V5. C40/C45 remain 220 nF; C41/C46 remain 100 pF. All other existing component values are unchanged, including the DMN6070SY MOSFET values and regulator dividers.

Nominal resistive input attenuation is 10k / (51k + 10k) = **0.163934426** (−15.7066 dB). A 2 Vrms input produces **0.327868852 Vrms / 0.463676578 Vpk** about VREF_2V5. This is the nominal divider result, excluding frequency-dependent coupling/RF effects and tolerances.

## Ground and local wiring

PGND has been replaced by GND in every current root-level `.kicad_sch` file, including the unreferenced legacy `PowerOutput.kicad_sch`. The latter received ground cleanup only; its wires and original component positions were preserved. Historical backups retain their original content.

There is one ground net, GND, and no PGND or AGND net. Active sheets use 69 standard `power:GND` symbols. Regulator, analogue, logic and power-stage returns share this net. Both speaker terminals of each channel remain floating; neither connector pin is on GND. The power-stage Kelvin-return annotations remain.

Regulator input/enable, feedback and noise-reduction circuits; VREF; oscillator; input buffers; dead-time RC/diode paths; gate resistors/pulldowns; bootstrap networks; bypass banks; half bridges; coupled inductors and differential outputs now have visible local wires. The main sheet uses A1 for readable spacing; output sheets use A3.

Remaining labels are functional boundaries or useful node names:

- Main: LEFT_IN, RIGHT_IN, AUDIO_L/R, PWM_L/R, L_DRIVE_P/N, R_DRIVE_P/N, ENABLE_L/R, VREF_2V5, OSC_SQUARE and TRIANGLE_400K, plus supply labels and hierarchical ports.
- Each output sheet: DRIVE_P, DRIVE_N and ENABLE link the retained hierarchical ports to both drivers. SW_A/B and OUT_A/B identify switch/output nodes. OUT_A/B also connect the separately drawn optional DNP output capacitors.

None of the discouraged local L/R_BIAS, AC, BUFFER, DT, OSC_SUM, INTEGRATOR_SUM, FB or NR labels remains in the active design. No such labels were technically necessary within the local blocks.

## TPS7A4901 package check — mismatch requires manual resolution

Both U11 and U12 currently have:

- Part value and manufacturer part number: **TPS7A4901DGNR**.
- Symbol: **DiscreteClassD:TPS7A4901DGNR**, representing DGN, 8-pin HVSSOP PowerPAD, nominal 3 × 3 mm body.
- Actual assigned footprint: **Custom:TPS7A4901DRBR**. This is a DRB/VSON-style footprint, not the DGN footprint implied by the part value.

The footprint resolves through the existing global library table to `/Users/tomwatson/Downloads/Custom.pretty/TPS7A4901DRBR.kicad_mod`. Its description is `VSON (8)**`, with a 3 × 3 mm fabrication outline. The project-local footprint table and all assignments have been left unchanged.

TI's [TPS7A49 datasheet, page 4](https://www.ti.com/lit/ds/symlink/tps7a49.pdf#page=4) confirms the same electrical functions for pins 1–8 in DGN and DRB:

| Pin | Function |
|---|---|
| 1 | OUT |
| 2 | FB |
| 3 | NC |
| 4 | GND |
| 5 | EN |
| 6 | NR/SS |
| 7 | DNC |
| 8 | IN |

Thus the signal/power pin numbering is compatible with TPS7A4901DRBR, but the land patterns differ. There is also an exposed-pad mapping mismatch: the present symbol exposes only pin 9 (EP, on GND); the assigned custom footprint has additional copper pads 9–13, with the central 1.5 × 1.75 mm exposed pad numbered **13**. The symbol provides no pins 10–13, so its EP9 connection does not establish a net assignment for the central pad13. This was inspected in the library, not corrected or applied to the PCB.

The project therefore does not establish one consistent intended package, nor can it identify the physical inventory. Verify the inventory part suffix and reconcile the value, symbol and exposed-pad mapping in a separately authorized package change. The current mismatch is annotated beneath both regulators in the PDF. No footprint or PCB change was made.

## Additional connection repairs

Two genuine pre-existing breaks in the right dead-time networks were repaired during the explicitly requested connection cleanup:

- R39 pin 2 / U10 pin 1 reconnected to D22 pin 2 / C47 pin 1.
- R40 pin 2 / U10 pin 3 reconnected to D23 pin 2 / C48 pin 1.

This restores each intended diode/resistor/timing-capacitor node. Apart from these repairs, the ground merge and the requested analogue rail changes, the complete pin-to-net partition matches the pre-edit backup. No other unintended electrical changes were found.

## Verification

KiCad 10.0.5 schematic ERC, including error, warning and exclusion severities, reports **0 errors, 0 warnings and 0 excluded violations**. No new suppression was added. Four existing project-level ignored check categories remain unchanged: single global label, four-way junction, SPICE model issue and footprint-filter mismatch. ERC success is under those existing settings and does not resolve the package mapping issue above.

`connectivity-check.json` records the full net-group comparison, component/value checks, ground cleanup, supplies, speaker isolation and preserved-file hashes. Original component identities, symbol selections, DNP states and footprint assignments passed comparison. The PCB, project settings, local preferences, footprint table, symbol table and custom symbol library match the pre-cleanup backup byte-for-byte. No footprint geometry was edited.

The complete active three-page schematic was exported to `../../pdf/DiscreteClassD-stereo-cleanup.pdf`; all pages were rendered and visually reviewed. The unreferenced historical sheet is not part of the active hierarchy or PDF. This verification covers schematic connectivity and presentation, not PCB synchronization or hardware performance.

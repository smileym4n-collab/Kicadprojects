# PCM2706Bench fabrication review - 27 October 2026

**READY FOR ONE-OFF PROTOTYPE FABRICATION.**

The current schematic and PCB implement the intended USB-to-I2S/analogue bench source. I found no electrical connection, routing, copper-clearance or board-outline fault requiring a redesign before this one-off build. This decision uses the user's confirmation that the actual WH148 fits the PCB hole pattern and that J5 will be a JST XH 2.50mm connector. Operation still needs normal first-build testing; this is not a claim of bench-proven hardware or USB compliance.

No source schematic, PCB or project settings were changed during this review. A separate copy was opened in KiCad, refilled, checked and saved under `source/`. Its footprints, tracks, vias, board outline and filled zones are identical to the source when compared by UUID; saving only changed object ordering. Source hashes were checked again after the review.

## Evidence

| Check | Result |
|---|---|
| Schematic ERC, KiCad 10.0.5 | 0 errors, 2 existing library-symbol mismatch warnings |
| Native GUI DRC after zone refill | 0 errors, 0 unconnected pads; 1 active cosmetic warning and 2 excluded cosmetic warnings |
| Schematic-to-PCB connectivity | All 111 unique numbered schematic pins match the PCB pad-net groups |
| Components | All 32 schematic components present; values and footprint assignments agree |
| PCB pad count | 112 numbered pad instances, 111 unique reference/pin pairs; J3 shield pad 5 occurs twice intentionally |
| PCB-only items | One logo footprint, with no electrical pads |
| Duplicate vias | None |
| Copper and outline inspection | Front/back copper, component placement and top render inspected |
| Outline | One closed rectangle, 47.498 x 60.452mm |
| Layer stack | Two copper layers, board thickness 1.6mm |
| Routing | 131 segments at 0.40mm, 11 at 0.20mm; default clearance 0.20mm |
| Vias | 76 through vias, 0.30mm drill |
| Fabrication export | Front/back copper, masks and silkscreen, outline, PTH/NPTH drills and Gerber job generated |
| Drill inspection | 112 plated holes: 76 vias and 36 component holes; no NPTH holes required by this design |

The command-line DRC crashed with exit 134 and no report. It was not treated as a pass. The successful native GUI result is saved in `source/GUI-DRC.rpt`. Native GUI schematic parity was not run in the standalone editor; the independent pin-net comparison above provides the separate parity evidence. See `audit.py`, `audit.json` and `audit-summary.txt`.

The project has five pre-existing ignored DRC tests: missing courtyard, off-centre track/via endpoints, tuning-profile geometry, symbol footprint filters and footprint component-type mismatch. These settings were preserved. Relevant package/pad types and physical placement were separately inspected; neither ignored checks nor a clean DRC establishes mechanical fit to an unspecified replacement part.

## Functional review

- IC1 is the PCM2706C with the correct 32-pin PJT package pin assignments. Its pin-1 marker is at the upper-right corner in this PCB orientation; take care to align the real device.
- USB-B pin 1 supplies IC1 VBUS pin 24. USB D+/D- polarity is correct through IC2; R11/R10 are the corresponding series resistors. The 1k5 pull-up R4 is on D+, supplied from VDD. USBLC6 channels are correctly paired 1-6 and 3-4, with pin 2 grounded and pin 5 at VBUS.
- PSEL and TEST are HIGH; HOST is LOW for the 100mA bus-powered configuration. IC1's four internally generated supply outputs remain separate, with their own local 1u capacitors. VCOM has C1, positive toward IC1. No external active circuit is powered from the internal supplies.
- IC1 supply-pad to capacitor-pad distances are approximately 2.22mm (VCCP/C11), 2.24mm (VCCL/C13), 2.35mm (VCCR/C14), and 4.25mm (VDD/C12), measured as straight-line distances. These are adequate for this low-power bench prototype; the routes and nearby ground connections were inspected.
- The 12MHz crystal has the 1M feedback resistor and two 18p load capacitors. XTI/XTO copper lengths, including branches, are approximately 13.1/12.8mm. R16 is on the underside near the crystal. The arrangement is reasonable for a one-off build; moving the crystal network is not required on the evidence available. Exact crystal load capacitance/ESR was not supplied, so oscillator startup and USB enumeration remain first-power checks.
- USB routes are short at this full-speed device's data rate. The D+ pull-up branch and unequal route lengths are not reasons to redesign this one-off board. No claim of controlled impedance or USB certification is made.
- J1's pin 2 is the FSEL common; pin 1 is ground/I2S, pin 3 is VDD/analogue. R17 defaults FSEL HIGH while the switch is open. Use a break-before-make SPDT ON-ON switch to avoid momentarily joining VDD to ground. Stop playback and mute the connected amplifier while changing mode.
- I2S pin assignments, 22-ohm source resistors and J5 silkscreen agree. The ground planes are connected by stitching vias, and the I2S routes have an opposing ground reference. The longest output copper is about 48.3mm. This is acceptable for the board; keep the external I2S connection very short and use a common ground. Power the DAC separately and ensure it accepts 3.3V I2S with source-driven clocks.
- The analogue path is correct: IC1 right through C22 to RV1 pin 3; left through C21 to pin 6. Pins 1/4 are grounded, and wipers 2/5 go to J4 right/left respectively. The user's measurement of increasing R(1-2) clockwise confirms the first gang's direction. Check both end stops/gangs during assembly.
- The 10k linear pot is appropriate as a simple bench level control. It does not affect I2S data. The 10u coupling capacitors and retained 16-ohm/22n shunt networks are reasonable for ordinary line-level testing. Full-scale analogue output is roughly 0.64Vrms; an amplifier expecting 2Vrms may not reach full power.
- Supply currents and dissipation are low. Using the datasheet's maximum line-mode dissipation and package thermal resistance gives an approximate 11-degree C junction rise in its reference thermal conditions, with no indication that this bench board needs a heatsink. Actual assembled temperature has not been measured.

These operating conditions and pin functions were checked against [TI's PCM2706C datasheet](https://www.ti.com/lit/ds/symlink/pcm2706c.pdf) and [ST's USBLC6-2 datasheet](https://www.st.com/resource/en/datasheet/usblc6-2.pdf). The board's 0.20mm tracks/spacing and 0.30mm through drills are within ordinary [JLCPCB fabrication capabilities](https://jlcpcb.com/capabilities/pcb-capabilities/); order standard 1oz copper.

## Accepted cosmetic findings

1. R16 reference text is mirrored on the front layer, at approximately (127.917, 106.884)mm. This cannot prevent operation; R16 itself is correctly on B.Cu. Its reference can be identified from the placement drawing.
2. Two RV1 shaft-outline silkscreen lines extend across the right board edge, at approximately (171.771, 125.666) and (171.771, 132.906)mm. These are existing exclusions. The expected shaft/bushing extends beyond the edge; clipped outline ink is harmless.
3. The schematic's existing RV1 library warning concerns cached symbol metadata. The USB-B symbol warning preserves shield pin 5 to match the custom footprint. Neither changes the verified pin mapping.

There is no need to change the board solely to clear these cosmetic findings for this build.

## Assembly notes that matter

- **Pot fit:** the user physically checked the two rows 5mm apart, with 5mm pin spacing and 1.2mm holes. This closes the previous footprint-fit blocker. The Alps library name does not identify the supplied pot manufacturer; use the physically checked WH148.
- **J5:** the user confirmed JST XH 2.50mm, matching the board. The schematic's old MC34635 manufacturer field is stale and describes a 2.54mm header. Ignore that field when ordering; fit the JST XH connector shown. No footprint change is required.
- Fit the intended USB-B connector matching the custom UJ2-B-HR-G-TH-style footprint. Do not substitute a different USB-B footprint based only on connector type.
- Fit a suitable fundamental-mode 12MHz crystal. Use C0G/NP0 for C3/C4; check the actual crystal specification against the two 18p capacitors. Supply capacitors may use X7R/X5R. Use suitable voltage ratings: at least 10V for the USB VBUS capacitor and comfortable margin above 3.3V elsewhere.
- C1 is polarized, positive toward VCOM. C21/C22 are drawn unpolarized: use appropriate nonpolar coupling capacitors; if using conventional polarized electrolytics instead, verify the change and orient positive toward the DAC. Do not fit arbitrary polarized parts solely from the generic 3D pictures.
- R16 must be fitted on the underside. Check resistor values carefully around R4 (1k5) and R17 (100k).
- The PCB has no separate mounting holes. Provide appropriate insulating support/panel mounting; avoid stressing the USB connector or pot solder joints.

## First power-up

1. Inspect soldering, especially IC1/IC2 bridges, and check USB 5V-to-GND resistance with power disconnected. Set analogue level fully anticlockwise.
2. Connect USB without a DAC/amplifier attached. Confirm enumeration and approximately 3.3V at each of VCCP, VDD, VCCL and VCCR. Confirm no abnormal heating.
3. Play a modest test tone. Verify left/right analogue output, low DC after coupling, and clockwise volume increase on both channels. Then connect the amplifier with its input/mute set conservatively.
4. Stop playback, select I2S, and check LRCK/BCLK/MCLK before connecting the separately powered DAC. At 48kHz, expect 48kHz LRCK, 3.072MHz BCLK and 12.288MHz MCLK.

## Fabrication package

`PCM2706Bench-fabrication-2026-10-27.zip` contains the seven Gerber layers, PTH/NPTH drill files and Gerber job file from the verified copy. The NPTH file is intentionally empty. No solder paste layers are required for this hand-assembled build. Review the fabricator upload preview to confirm the 47.498 x 60.452mm outline, both copper layers and all plated holes before payment.

Copper/placement previews are in `exports/front.png`, `exports/back.png` and `exports/top-3d.png`. These are generated from the same board geometry as the Gerbers. The Gerber outline coordinates, layer declarations and Excellon drill output were inspected; a fabricator-rendered upload preview has not been performed here.

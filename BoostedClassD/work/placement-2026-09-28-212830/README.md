# BoostedClassD component placement pass

Applied to `BoostedClassD.kicad_pcb`. This is an unrouted placement starting point, not a fabrication-ready or measured-performance design.

## Backup and scope

The `backup/` directory contains the original PCB, hierarchical schematics, project settings, local symbol library and library table. `baseline-hashes.json` records their SHA-256 hashes. Restore the PCB alone to reverse this placement pass; do not overwrite newer project settings accidentally.

85 of 101 footprints were moved. The board outline, four copper layers, mounting holes H1–H4 and connectors J1–J5 retain their original geometry and placement. J6 is placed at the upper left for programming access. All component values, footprint identities, pad geometry, pad assignments and hierarchical net connections were preserved. No BOM components were added or substituted; Q2–Q5 remain the existing bipolar devices.

424 existing tracks/vias/arcs and 12 copper zones were removed from the working PCB because they no longer match the placement. They are preserved in the backup. No routing, new planes or thermal vias were added.

## Placement rationale

- Charger input, battery path, shunt and current monitor are grouped near the power connector. Charger capacitors sit around their corresponding pins; the shunt still needs proper Kelvin routing.
- The TPS631000 inductor is aligned with its switch pins, with input/output capacitors local and feedback resistors on the opposite side.
- The amplifiers are grouped toward the speaker connector. Local supply and GREG capacitors surround the ICs, with L2 close to the boost switch pin. The amplifier centres are 14.5 mm apart to shorten shared-boost distribution.
- Output filtering is between the amplifiers and speaker connector. Control circuitry occupies the centre; ESP32 decoupling and source resistors are near the relevant module pins.
- The existing external-antenna ESP32 module position is retained. Keep the antenna cable and antenna clear of switching circuitry in the enclosure.

The supplied TAS2120 layout guidance (pages 103–104), TPS631000 layout guidance (page 18) and BQ25185 layout guidance informed this pass. Placement alone cannot establish performance; routing determines the actual current-loop geometry.

## Verification

`placement-validation.json` records seven passed checks: preserved footprints and pads; fixed connector/hole positions; unchanged outline; retained four layers with obsolete routing removed; no component courtyard bounding-box overlaps; all pads inside the outline; and all PCB pad nets matching the exported hierarchical schematic netlist. For footprints without courtyards, the check used footprint bounds; decorative logos were excluded from component overlap checks. Existing mounting-hole courtyards can extend beyond the board edge.

Measured straight-line pad-centre separations include U3 SW to L2 at 2.20 mm, U1 to L1 at 2.81 mm, charger SYS to C25 at 2.30 mm, and amplifier PVDD to local capacitors at 2.05 mm. These are not routed loop lengths.

The final KiCad DRC completed with **11 violations, 244 unconnected items and 8 schematic-parity issues**. Unconnected items are expected for this unrouted board. The remaining violations comprise:

- Two existing R9 internal pad-clearance issues: 0.15–0.16 mm versus the configured 0.20 mm rule. Verify its exact part and land pattern before deciding how to resolve these.
- Four existing library-footprint mismatches: IC2, U2, U3 and R9. Do not blindly update these custom footprints from the library.
- Four existing R9 silkscreen-over-pad issues, plus one C29 reference overlap with C9 copper introduced during label placement. Final silkscreen cleanup remains necessary.
- Eight value-parity warnings for C28–C31 and R22–R25, also reproduced on the original backup. Stored PCB values and exported netlist values match; investigate the checker discrepancy before fabrication.

No DRC exclusions were added. Existing project rule settings were used. Standalone connector legends and title text were moved to F.Fab to avoid clashes; restore useful connector labels on final silkscreen during finishing.

All hierarchical schematic files, the local symbol library and library table match the initial hashes. Project settings changed externally during this task; the latest version was captured in `project-settings-at-apply.kicad_pro` and preserved byte-for-byte during application. `final-hashes.json` records the final state and these checks.

## Remaining engineering work

1. Resolve the R9 land pattern, custom library mismatches and parity warnings before routing release.
2. Review amplifier capacitor packages. The retained 2012/3216 metric parts impose longer loops than TI’s small-package guidance (0603 metric for specified local bypass parts). No package substitutions were made.
3. Verify exact L1/L2 saturation current, RMS current and loss against the intended operating conditions; placement does not resolve component-rating uncertainty.
4. Route compact boost and regulator loops, direct local decoupling returns, controlled shared-boost distribution, short source-terminated digital lines and Kelvin shunt connections. Keep feedback and control nets away from switching nodes.
5. Implement a largely continuous ground reference and appropriate exposed-pad copper/thermal vias. Check charger dissipation and enclosure temperatures. Do not enlarge switching-node copper unnecessarily.
6. Finish silkscreen, connector identification and mechanical/service clearance, then refill zones and run full DRC and schematic parity again.
7. Existing charging limitation remains: approximately 1 A charging with the nominal 360-minute timer cannot guarantee a full charge of a 7 Ah cell. Confirm battery protection and charging behaviour separately.
8. Validate firmware sequencing, startup/shutdown, thermal behaviour, output performance and EMI on hardware. None were bench-tested by this task.

## Review files

- `placement-review.png` / `placement-review.svg`: front copper, silkscreen, courtyards and outline.
- `assembly-review.svg`: front fabrication view including retained legends.
- `drc-final.json`: full final DRC output.
- `drc-baseline-parity.json`: original-board comparison with the same check options.
- `placement-validation.json`: preservation checks, movements and pad distances.
- `placement-candidate.kicad_pcb`: copy of the final main PCB.

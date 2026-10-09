# Smaller amplifier passives — completed 5 October 2026

Applied to `BoostedClassD.kicad_pcb` and the hierarchical `Amplifiers.kicad_sch` sheet. The pre-change project is in `backup/`, with SHA-256 hashes in `baseline-hashes.json`. The verified full project is in `review/`.

## Changes

- C13–C24 now use standard reflow **0603 metric (0.6 × 0.3 mm)** capacitor footprints. These replace the oversized hand-solder lands used previously. No components were added; capacitance values and all circuit connections are unchanged.
- C13/C14 PVDD high-frequency bypass, C17/C18 GREG and C15/C16 DREG moved nearer their IC pins. C19 VBAT bypass also moved inward. Other replaced capacitors retain their original power-pad anchors, with smaller bodies/lands and repaired connections.
- GREG capacitor returns have a separate bottom-layer route back to the respective PVDD pin. Local In2 copper-pour keepouts around their outer return vias prevent accidental connection to the PVDD distribution plane before that star point. These keepouts do not interrupt the In1 ground plane. The IC end uses one via; it is not a zero-inductance connection or a claim of exact EVM geometry.
- Reworked local PVDD distribution and reservoir connections, added direct ground returns, and moved U2's negative-output layer transition out from inside the IC fanout. That output still uses paired vias and a bottom-layer section. The other amplifier output routes were retained.
- Bulk C9–C12, inductors, resistors, connectors, IC footprints, mounting holes, outline and four-layer arrangement remain unchanged. This is a local amplifier redesign, not a whole-board miniaturisation.
- Each new capacitor has a local 0.15 mm clearance override for its standard reflow land pattern (0.18 mm copper-pad gap). The global 0.20 mm rule and project settings are unchanged. This is an explicit fine-pitch package requirement; no DRC errors were excluded or suppressed.
- Hidden sourcing/rating fields match between schematic and PCB. Small-part identifiers remain available on the fabrication/assembly layer; see `amplifier-closeup.png`.

## Selected parts

| References | Value/rating | Samsung part | JLC/LCSC code |
|---|---|---|---|
| C13, C14, C17, C18 | 100 nF, 25 V, X5R, ±10% | CL03A104KA3NNNC | C307379 |
| C15, C16, C19, C20 | 1 µF, 10 V, X5R, ±20% | CL03A105MP3NSNC | C170153 |
| C21, C22, C23, C24 | 2.2 µF, 10 V, X5R, ±20% | CL03A225MP3CRNC | C318539 |

All are 0603 metric, non-polarised MLCCs. Manufacturer pages confirm dimensions, ratings and production status. The 1 µF and 2.2 µF selections match TI's TAS2120EVM BOM types; the 100 nF selection supplies the recommended 25 V rating for PVDD. Existing generic capacitor rating fields have been updated to these X5R selections. DC-biased effective capacitance and ESL have not been independently characterised; nominal capacitance must not be interpreted as guaranteed effective capacitance. Bulk PVDD capacitance was not reduced.

A search of the connected inventory for CL03 returned no matches. These are proposed new purchases, not allocations of owned stock. JLC lists all three for **Standard PCBA only**. Catalogue availability is not reserved stock; confirm exact BOM matching/availability at ordering. `small-capacitors-BOM.csv` covers only these twelve parts, not the full assembly BOM.

Sources checked:
- [TI layout guidelines, especially sections 3.2 and 3.3](https://www.ti.com/lit/an/slaaem7/slaaem7.pdf)
- [TI TAS2120EVM BOM, page 21](https://www.ti.com/lit/ug/slau936/slau936.pdf)
- [Samsung 100 nF](https://product.samsungsem.com/mlcc/CL03A104KA3NNN.do), [1 µF](https://product.samsungsem.com/mlcc/CL03A105MP3NSN.do), [2.2 µF](https://product.samsungsem.com/mlcc/CL03A225MP3CRN.do)
- [JLC C307379](https://jlcpcb.com/partdetail/291053-CL03A104KA3NNNC/C307379), [C170153](https://jlcpcb.com/partdetail/CL03A105MP3NSNC/C170153), [C318539](https://jlcpcb.com/partdetail/299668-CL03A225MP3CRNC/C318539)
- [JLC assembly capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities)

## Assembly choice

JLC Standard assembly is recommended for the amplifier ICs and these tiny capacitors. Its published requirements include rails, fiducials and a minimum 70 × 70 mm assembly size. This board is about 83 × 58 mm, so the order needs an appropriate assembly panel/rails. The finished-board outline has not been enlarged, and a production panel has not been generated. Have JLC review stencil apertures and paste volume for the mix of small capacitors and larger power-component pads.

A stencil and temperature-controlled hot plate can assemble parts smaller than a soldering iron comfortably allows. However, 0603 metric placement, bridging/tombstoning inspection and QFN rework need magnification and suitable tools. A stencil alone does not make this an easy first home-reflow board. For home assembly, use the final paste layers, paste suitable for fine apertures, a measured board-temperature profile consistent with the paste/component specifications, and inspect under magnification before powering. Install heat-sensitive/through-hole items afterwards as appropriate. A controlled reflow oven is generally easier to profile consistently than an improvised hot plate.

## Verification and remaining work

`validation.json`, `erc-baseline.json`, `erc-final.json`, `drc-final.json` and the before/after hierarchical netlists contain the evidence.

- All 101 footprint identities, values, hierarchical paths and numbered-pad nets preserved.
- Only C13–C24 footprint sizes/positions changed; all other component positions and pad geometry preserved.
- Every numbered PCB pad matches the hierarchical schematic netlist; all schematic net connections and values unchanged.
- All added tracks/vias retain their intended net after refill.
- DRC: **11 existing findings, 9 existing unconnected items, 0 parity issues**. Violation descriptions and unrouted-net list match the prior completed routing baseline. No new findings.
- Existing DRC findings: R9 pad clearances (2), R34/J2 courtyard overlap (1), existing library-footprint mismatches (4), R9 silkscreen warnings (4).
- ERC: **one existing error**, C32 pin 1 unconnected in `/ESP32-ATTINY/`; zero new errors. That user-modified circuit was preserved.
- Nine remaining opens are outside the new local capacitor loops: charger GND, a 3.3 V branch, two USB5V connections, main switched SYS feed to the amplifier supply, three BQ-SYS branches and UPDI.
- Visual front-copper/assembly review completed. This pass does not qualify current/thermal margins of the complete board, EMI, audio performance, firmware startup/shutdown or the supply system. Existing long VDD/IOVDD distribution and the boost-inductor geometry have not been fully re-optimised.

The board is **not fabrication-ready** while those existing connections/errors remain. No Gerber/stencil order, purchase, upload or assembly order was submitted.

Reopen/reload the PCB and amplifier schematic from disk in KiCad; do not save an older already-open editor copy over the updated files.

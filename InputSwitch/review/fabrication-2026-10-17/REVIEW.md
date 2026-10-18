# InputSwitch final fabrication review — 17 October 2026

**Verdict: HOLD the PCB order for the relay and connector footprint issues below.** No schematic, PCB or project settings were modified. Current source files match the captured review copies byte-for-byte. The PCB autosave is identical to the saved PCB.

## Address before ordering

1. **K1–K3 relay hole positions differ from the specified relay drawing.** Their embedded `Relay_THT:Relay_DPDT_Omron_G6K-2P-Y` footprints put pins 2 and 7 at 3.0 mm from the coil row. Omron specifies **3.2 mm** for G6K-2P-Y; the remaining contact rows are 5.4 and 7.6 mm. These three footprints should use the verified project-local geometry already used by K4, followed by reconnecting the moved pads and rerunning DRC. The 0.85 mm holes may accommodate some misalignment, but relying on that is unnecessary assembly risk. This is separate from the accepted ULN2003A drive choice.
2. **J1–J13 are JST-XH 2.50 mm footprints, whereas your declared stock is Multicomp 2.54 mm.** J8/J9 are three-pin; the remaining eleven are two-pin. Use drawing-verified footprints for the actual stocked headers, or deliberately purchase matching JST headers and housings. A small pitch difference is not evidence of mechanical interchangeability, particularly for the housing/courtyard. This review has not re-counted stock.
3. **Three ERC source-declaration errors remain:** control GND (#PWR20009), U1 pin 1 (BUCK_VIN_FILTERED), and U5 pin 8 (ISO_L_QUIET). The feeds exist in the netlist; these errors do not indicate open PCB traces. Mark the legitimately supplied nets with appropriate PWR_FLAG declarations after tracing their sources. Do not disable the ERC rule. This is schematic housekeeping rather than a copper redesign.

## Smaller improvements

- **U1 holes:** current drills are 1.2 mm; RECOM recommends 1.3 mm. Matching its recommended drawing would remove a remaining mechanical uncertainty. This is not a demonstrated insertion failure.
- **Silkscreen:** one active overlap warning concerns “Reference” / “Series”. Two text-thickness warnings and four F2 silk-over-mask warnings are excluded. Fine script strokes may reproduce poorly; fuse-holder silk may be clipped. These are cosmetic, not electrical failures.
- **C2/C11 ratings:** their displayed values now say only 22uF, replacing 22u / 25V. Preserve the intended 25 V ceramic specification in the assembly BOM. Do not select parts from capacitance alone; effective capacitance falls with DC bias.
- **L1 lands:** the assigned generic 2520 metric footprint now uses 1.25 × 2.2 mm pads on 2.15 mm centres, rather than the earlier manufacturer-pattern footprint. Its larger pads overlap the intended terminal lands; no obvious fit obstruction was identified, but it is not the exact Murata recommended pattern. Prefer the existing manufacturer-pattern footprint if revising this area; otherwise retain this as an assembly-process difference.
- C11 is roughly 8.9 mm centre-to-U1 VIN pin. Moving it directly beside VIN/GND would shorten the input bypass loop if revising this area. Existing placement is not identified as a fabrication blocker.

## Checks completed and evidence

- Fresh KiCad ERC, PCB DRC with zone refill and schematic parity, and XML netlist export. The initial sandboxed DRC process aborted; the rerun outside that sandbox completed and produced the report used here.
- **DRC: zero unconnected items, zero schematic/PCB parity discrepancies, no reported electrical clearance or short violations.** Seven listed violations comprise one active silkscreen overlap and six excluded cosmetic warnings described above. Missing-courtyard and footprint-filter/type checks are disabled in the existing project settings, so DRC is not a complete package certification.
- Every current netlist pin-to-net assignment matches the verified 9 October post-filter netlist. Component differences are value formatting for C2/C11/L1, generic L1 footprint selection, and DIP socket footprints for U5/U7.
- All four copper-layer plots inspected. Separate control-GND and selected-return regions remain deliberate. No new unintended ground-domain connection was found in connectivity checks. External P3A common grounds still join L/R returns as previously discussed.
- K1/K2 select source signal and return. Energizing K3 disconnects source signals and shorts each P3A input to its selected return. K4 switches protected +12 V to J13.1; J13.2 is control GND.
- ULN2003A clamp/common and emitter nets remain +5 V/GND for U3 and +12 V/GND for U4. Unused driver inputs remain grounded. J10 is the external power-relay coil connection, not a mains connector.
- Converter, LM358, optocoupler, MCU, transistor and diode connections retain the established pin assignments. SPU03 inputs use +5 V/control GND; each output and detector use their own selected return. Detector optocoupler transistor sides use control GND.
- L1 is in series with the RECOM input only. C2 is upstream and C11 downstream, both to control GND; the external 12 V relay branches remain upstream. The intended Murata 4.7 uH part has 0.24 ohm maximum DCR: at 0.6 A, approximately 0.144 V drop and 0.086 W copper loss. This is a calculation, not a measured current or startup qualification.
- Board has four copper layers and 1.6 mm specified thickness. Actual track widths are 0.4/1.0 mm; vias are 0.6/0.3 mm or 1.0/0.5 mm diameter/drill. Default net clearance is 0.2 mm and copper-to-edge minimum is 0.5 mm. DRC did not report outline or drill violations under the configured rules.

## Assembly and qualification limits

- Retain R20/R40 at 30R, 3 W, 1% flameproof as specified: approximately 0.83 W each at 5 V, or 1.2 W at 6 V. Raise them above the PCB and provide enclosure heat clearance. Enclosure temperature has not been established.
- F2 should be the specified T1A despite its abbreviated 1A value. Use the intended regulated 12 V wall supply and preserve capacitor voltage ratings.
- R32/R52 are currently 390R, not 330R. Their expected LED-path dissipation remains comfortably below 0.125 W at the discussed isolated-supply voltages.
- The accepted ULN2003A relay-driver choice is retained, not re-raised as a blocker.
- Firmware sequencing, actual bought transistor pinout/package, enclosure hardware fit, converter startup/filter damping, EMC and measured audio noise are not proven by these CAD checks. Relay mute defaults and click suppression still depend on the complete system and firmware.
- No final Gerber/drill ZIP has been approved. After corrections, save/refill, rerun ERC/DRC, regenerate all four copper layers, mask, silkscreen, outline and drill files, then inspect the resulting manufacturing preview. This review is not a bench-tested or production-qualified guarantee.

## Sources and review files

- [Omron G6K drawing, page 6](https://omronfs.omron.com/en_US/ecb/products/pdf/en-g6k.pdf)
- [RECOM R-78K-2.0 drawing and input-filter guidance](https://recom-power.com/pdf/Innoline/R-78K-2.0.pdf)
- [Murata DFE252012C specifications and lands](https://www.murata.com/~/media/webrenewal/products/inductor/chip/tokoproducts/wirewoundmetalalloychiptype/m_dfe252012c.ashx)

Evidence: `erc.json`, `drc.json`, `netlist.xml`, `inspection.txt`, `layers.pdf`, `layer-0.png` through `layer-3.png`, and unchanged source snapshots in `source/`.

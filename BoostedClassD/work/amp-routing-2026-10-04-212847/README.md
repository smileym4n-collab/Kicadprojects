# TAS2120 / TAS2320 local routing pass

Applied to `BoostedClassD.kicad_pcb` on 4 October 2026. Original project files and PCB are preserved in `backup/`, with `baseline-hashes.json`. The changes improve and complete local amplifier connectivity; the board remains unfinished and is not fabrication-ready.

## What changed

- Brought C12, C13 and C18 back inside the outline beside U2 (TAS2320). These are the only footprints moved. Values, packages, pad shapes, pad assignments and schematic connections were preserved.
- Connected U2 GREG, PVDD bypass/bulk capacitors and VBAT/sense pins. Added an inner-layer shared PVDD connection to the U3 boost reservoir and a supply link between the local amplifier sections.
- Routed both U2 outputs to their existing ferrite beads. OUTP stays on front copper; OUTN uses a short front escape and paired 0.6 mm / 0.3 mm drill vias at each end of a 0.5 mm back-layer route. The layer change resolves the output ordering without crossing the power-pin fanout on the front.
- Replaced the U3 output escape tracks/arcs to remove its existing clearance violation. These remain 0.2 mm where the existing capacitor arrangement limits space; they have not been certified for the final current/temperature rise.
- Added local ground returns at C12/C13/C14, C19/C20 and amplifier ground pins. Replaced one redundant existing PVDD via to make room for the C14 return. The previous C14 starved-thermal warning is resolved.
- Connected amplifier IOVDD branches to the existing ESP3V3 distribution on the inner power layer.
- Retained the current boost-inductor placement and SW copper, digital signal routing, connectors and the rest of the board. Refilling necessarily updates zone fill geometry around the new routing.

110 track/via items were added and 14 were removed (13 U3 output-route items and one local PVDD via). There are 742 tracks/arcs/vias in the resulting PCB. No schematic or BOM components were added or substituted. No rule exclusions or project settings were changed.

## Verification

| Check | Before | After |
|---|---:|---:|
| DRC violations | 13 | 11 |
| Missing connections | 24 | 9 |
| Schematic-parity issues | 0 | 0 |

All 11 remaining violation identities were already present in the original board. No new shorts, track-clearance errors, dangling vias, courtyard overlaps or silkscreen violations remain from this pass. Remaining violations are two intrinsic R9 pad-clearance errors, the R34/J2 courtyard overlap, four library-footprint mismatches (IC2, U2, U3 and R9), and four R9 silkscreen-over-pad warnings.

The zones were refilled and saved before verification. An independent comparison verified footprint identities, values, pad geometry and pad nets; only the three specified capacitor moves; retained routing endpoints/layers/nets; all newly added net assignments after refill; current hierarchical netlist parity; and preserved outline/four-layer count. All schematic files, local symbol/library-table files and project settings remain byte-identical to the backup. The main PCB was checked again after application. See `validation.json`, `final-hashes.json` and `drc-final.json`.

## Work still required

The nine open connections are:

1. IC1 ground pins 4–5.
2. The INA236-area ESP3V3 branch to the rest of ESP3V3.
3. F2 USB5V to IC1 input.
4. C26 input bypass to IC1 input.
5. Main switched SYS feed from Q1 to the amplifier/local regulator supply network.
6. BQ-SYS feed to J6.
7. BQ-SYS connection between ATtiny supply and the LED/control area.
8. BQ-SYS connection between charger and the control area.
9. J6 UPDI connection to U5.

The amplifier SYS feed is a high-current distribution route, not a small signal; size its copper and parallel vias for the combined amplifier and regulator demand. It is intentionally left open rather than represented by a token narrow connection.

### Performance limitations requiring review

TI recommends very small local bypass packages and a direct GREG-capacitor return to the device PVDD pin. The retained 2012/3216 metric footprints constrain the loops. In particular, GREG capacitor returns still share local PVDD copper with bypass circuitry, so this pass does not fully implement TI's preferred dedicated return geometry. Smaller local bypass/GREG footprints and a further local placement revision would be preferable before a performance-focused fabrication release. No package changes were assumed or made.

The existing U3 boost/SW layout and full amplifier ground/thermal design have not been optimised or signed off by this pass. Existing local SW and supply zones were preserved. Review switch-node area, BGND/PGND connections, via capacity, copper weight, boost inductor rating, effective capacitor values, EMI and enclosure temperature before manufacture. The new shared PVDD connection needs the same current/thermal review as the rest of the power distribution.

The current netlist also identifies C32 pad 1 as unconnected. This was preserved; its intended ESP32 bulk-decoupling connection should be reviewed separately.

Datasheet basis: TI TAS2120, SLASFC6A, layout guidance on pages 103–104 (`tas2120.pdf` in the project; https://www.ti.com/lit/ds/symlink/tas2120.pdf). This is connectivity/clearance-checked routing work, not measured audio, EMI, thermal or production validation.

## Review artifacts

- `after.png` and `after.svg`: final front copper/silkscreen view.
- `back-copper.svg`: back copper including the new OUTN route.
- `before.svg`: original front copper view.
- `routing-candidate.kicad_pcb`: copy of the applied board.
- `drc-baseline.json` / `drc-final.json`: complete reports.
- `backup/`: original PCB and project sources. Restore only the PCB to undo this routing pass.

If the PCB editor was already open, reload the PCB from disk before editing further so an older in-memory copy does not overwrite these changes.

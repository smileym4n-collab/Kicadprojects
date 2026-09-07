# Requested power-loop routing: stopped at placement limit

AGENTS.md was read first. No PCB, schematic, component value, net assignment, pin mapping, placement, trace, via, zone, or DRC setting was changed. Only this report and the DRC JSON were created.

The user instructed: if movement larger than about 2 mm is needed, stop and report it. The existing capacitor placements require such movement to achieve the specified very small local decoupling loops.

## Two different board states

`DiscreteClassD.kicad_pcb` is the saved 16:43 board. `_autosave-DiscreteClassD.kicad_pcb` is a newer 16:58 state with changed capacitor footprints/values and substantial placement changes. Neither was overwritten, recovered or saved over the other.

The active power MOSFET references in these files are Q5/Q6 (A) and Q7/Q8 (B), not the Q1-Q4 references from the earlier schematic task. The saved file labels them Q_NMOS_GDS with SOT-89-3 footprints; the autosave labels them DMN6070SY. AGENTS.md still specifies DMTH6016LPS. These discrepancies were recorded, not corrected or treated as authorization to replace devices. Distances below use the existing pad net assignments, not an assumed physical package pinout.

## Measured obstacle

Distances are straight-line **pad-centre to pad-centre**, not routed trace lengths. Actual routes would generally be longer. Positive terminal is capacitor pad 1; negative terminal is pad 2. High-side drain and low-side source are identified from the board's existing net assignments.

| Board state | Capacitor | Bridge used for measurement | Cap + to high-side drain | Cap - to low-side source |
|---|---|---|---:|---:|
| Saved | C4, 100nF | A: Q5/Q6 | 63.97 mm | 62.72 mm |
| Saved | C5, 1uF | A: Q5/Q6 | 68.38 mm | 66.62 mm |
| Saved | C6, 10uF | A: Q5/Q6 | 74.95 mm | 73.77 mm |
| Saved | C10, 100nF | B: Q7/Q8 | 25.56 mm | 18.77 mm |
| Saved | C11, 1uF | B: Q7/Q8 | 37.58 mm | 30.62 mm |
| Saved | C12, 10uF | B: Q7/Q8 | 32.85 mm | 25.57 mm |
| Autosave | C4, 100nF | Nearest bridge B | 2.23 mm | 4.13 mm |
| Autosave | C5, 1uF | Nearest bridge B | 4.64 mm | 5.76 mm |
| Autosave | C10, 100nF | Nearest bridge A | 2.20 mm | 2.17 mm |
| Autosave | C11, 1uF | Nearest bridge A | 4.61 mm | 4.55 mm |
| Autosave | C6, 10uF | Nearest bridge B | 11.83 mm | 18.84 mm |
| Autosave | C12, 10uF | Nearest bridge A | 17.67 mm | 17.86 mm |

C4-C6 in the saved board are outside its right-hand outline (board X maximum 214.757 mm). Even the newer autosave requires relocation beyond 2 mm for its remote 10uF capacitors to become local to the MOSFET power loops. Moving the capacitors and MOSFETs each by 2 mm would still leave the longest connections much too long for the requested local arrangement. No exact alternative placement was chosen or applied.

## Routing and geometry status

- Added trace widths: **none**.
- Added or modified copper zones: **none**.
- Vias added: **0**.
- Component movement: **0 mm**, all components.
- Existing board has four 0.2 mm F.Cu segments on HB_A/HB_B; these were left untouched.
- Existing zones are all on F.Cu: SW_B, OUT_A, OUT_B and the Zobel junction net `Net-(C16-Pad1)`. They were preserved, including the existing SW_B polygon. No filtered-output or Zobel routing was added or modified.
- SW_A would need to connect the existing Q5 source/Q6 drain junction to L6 pad 1. On the saved board those pad-centre distances to L6 are 6.75 / 8.70 mm; on the autosave they are 10.11 / 6.38 mm. No SW_A route was added.
- SW_B uses Q7 source/Q8 drain and L6 pad 4. Their pad-centre distances to L6 are 7.93 / 6.33 mm in both files. Its existing F.Cu zone was not changed. No claim is made that all its intended endpoints are already DRC-connected.
- No ground plane or keepout was added or modified beneath switching nodes.

The required local current path for each bridge remains: local capacitor positive terminal -> high-side drain -> high-side MOSFET -> SW junction -> low-side MOSFET -> low-side source -> the same capacitor's negative terminal. No such capacitor loop was routed during this task. The eventual return must connect directly to the low-side source, independently of gate-driver VSS and analogue-ground routing.

## DRC of the unchanged saved PCB

KiCad 10.0.5 command: `kicad-cli pcb drc --severity-all --all-track-errors --refill-zones --format json`. No `--save-board` was passed: zones were refilled for checking in memory only. The sandboxed DRC process aborted; the same check outside the sandbox completed successfully.

- **8 clearance errors**.
- **115 warnings**: 55 text thickness, 55 text height, 1 silkscreen overlap, 4 silkscreen-over-copper.
- **86 unconnected items**, reported separately by KiCad.
- Total: 123 violations plus 86 unconnected items.
- No DRC suppression/exclusion or project settings were changed. Existing ignored checks are listed below.
- DRC was run on the saved PCB, not on the differing autosave. Schematic-parity checking was not requested or performed.

- Existing ignored check: {'description': 'Footprint has no courtyard defined', 'key': 'missing_courtyard'}
- Existing ignored check: {'description': 'Track endpoint not centered on via', 'key': 'track_not_centered_on_via'}
- Existing ignored check: {'description': 'Tuning profile track geometries', 'key': 'tuning_profile_track_geometries'}
- Existing ignored check: {'description': "Footprint doesn't match symbol's footprint filters", 'key': 'footprint_filters_mismatch'}
- Existing ignored check: {'description': "Footprint component type doesn't match footprint pads", 'key': 'footprint_type_mismatch'}

### Clearance errors

- Clearance violation ( clearance 0.2000 mm; actual 0.1500 mm)
  - Pad 1 [unconnected-(IC1-IN1+-Pad1)] of IC1 on F.Cu; {'x': 275.7545, 'y': 88.115}
  - Pad 2 [unconnected-(IC1-IN1--Pad2)] of IC1 on F.Cu; {'x': 275.7545, 'y': 88.765}
- Clearance violation ( clearance 0.2000 mm; actual 0.1500 mm)
  - Pad 1 [unconnected-(U4-NC-Pad1)] of U4 on F.Cu; {'x': 275.1745, 'y': 97.17}
  - Pad 2 [unconnected-(U4-Pad2)] of U4 on F.Cu; {'x': 275.1745, 'y': 97.67}
- Clearance violation ( clearance 0.2000 mm; actual 0.1500 mm)
  - Pad 2 [unconnected-(IC1-IN1--Pad2)] of IC1 on F.Cu; {'x': 275.7545, 'y': 88.765}
  - Pad 3 [unconnected-(IC1-IN2--Pad3)] of IC1 on F.Cu; {'x': 275.7545, 'y': 89.415}
- Clearance violation ( clearance 0.2000 mm; actual 0.1500 mm)
  - Pad 3 [unconnected-(IC1-IN2--Pad3)] of IC1 on F.Cu; {'x': 275.7545, 'y': 89.415}
  - Pad 4 [unconnected-(IC1-IN2+-Pad4)] of IC1 on F.Cu; {'x': 275.7545, 'y': 90.065}
- Clearance violation ( clearance 0.2000 mm; actual 0.1500 mm)
  - Pad 2 [unconnected-(U4-Pad2)] of U4 on F.Cu; {'x': 275.1745, 'y': 97.67}
  - Pad 3 [unconnected-(U4-GND-Pad3)] of U4 on F.Cu; {'x': 275.1745, 'y': 98.17}
- Clearance violation ( clearance 0.2000 mm; actual 0.1500 mm)
  - Pad 5 [unconnected-(IC1-V--Pad5)] of IC1 on F.Cu; {'x': 279.9795, 'y': 90.065}
  - Pad 6 [unconnected-(IC1-OUT2-Pad6)] of IC1 on F.Cu; {'x': 279.9795, 'y': 89.415}
- Clearance violation ( clearance 0.2000 mm; actual 0.1500 mm)
  - Pad 6 [unconnected-(IC1-OUT2-Pad6)] of IC1 on F.Cu; {'x': 279.9795, 'y': 89.415}
  - Pad 7 [unconnected-(IC1-OUT1-Pad7)] of IC1 on F.Cu; {'x': 279.9795, 'y': 88.765}
- Clearance violation ( clearance 0.2000 mm; actual 0.1500 mm)
  - Pad 7 [unconnected-(IC1-OUT1-Pad7)] of IC1 on F.Cu; {'x': 279.9795, 'y': 88.765}
  - Pad 8 [unconnected-(IC1-V+-Pad8)] of IC1 on F.Cu; {'x': 279.9795, 'y': 88.115}

Full details: `drc-existing-pcb.json` in this directory.

## File integrity

SHA-256 before/after inspection and DRC:

- Saved PCB: `a65994bda7fdbd8bad9e062e3943cc52babb92c06ea2ef83cbd0c3792036252d`
- Autosave PCB: `8e477c01080ca9dc1231a7f87240aa7dce463c322d139a05fa87967b2c30ee9e`

Both hashes were unchanged. Routing remains pending the intended board state being saved and the local decoupling placement being brought within routing distance, or a revised movement allowance. No other routing was started.

# Subwoofer source trigger — schematic only

Added to `Control.kicad_sch` on 7 October 2026. The user will place and route the PCB. `InputSwitch.kicad_pcb`, project/settings files, all other schematic sheets, symbol library and library tables are byte-identical to the preserved source snapshot. Temporary PCB work was reverted and is not a deliverable. No fabrication outputs were regenerated.

## Operation and external wiring

| InputSwitch | Connect to SubController | Function |
| --- | --- | --- |
| J13 pin 1 | J20 pin 1 | Switched protected 12 V positive |
| J13 pin 2 | J20 pin 2 | Trigger return, InputSwitch control GND |

With the sub selector in AUTO, Marantz/source AV energizes K4 and applies the trigger. Preamp/source REF, MCU reset, or loss of InputSwitch power opens the trigger contact. K4 follows `SOURCE_AV`, independently of the audio mute and P3A mains-relay command. The existing firmware output and R3 reset pull-down are reused; no additional MCU pin or firmware behavior is required.

The trigger uses the protected `+12V` rail after the existing fuse and reverse-polarity diode. The voltage is therefore slightly below the adapter voltage. With approximately 11.5–12 V and an assumed 1.2 V optocoupler LED drop, the sub's user-confirmed 2k2 resistor gives approximately 4.7–4.9 mA. Its resistor dissipation is approximately 48–53 mW. These are calculations using the interface information supplied by the user, not measurements or an independent SubController review. No subwoofer resistor change is needed.

No second optocoupler is added. The isolation boundary is the optocoupler at the subwoofer. J13 pin 2 is control GND here and must go only to the sub's isolated trigger return, not its audio/board GND. The whole trigger output is not floating relative to InputSwitch: it intentionally uses this box's protected supply.

## Added parts and driver connection

- K4: Omron G6K-2P-Y DC5, matching the existing relay type. Coil pin 1 to +5V, pin 8 to `K4_LOW`; U3 channel 4 has input pin 4 on `SOURCE_AV` and output pin 13 on `K4_LOW`. U3's existing COM pin 9 at +5V provides coil clamping. Outputs are not paralleled.
- K4 contact pin 4 (NO) to +12V; pin 3 (COM) to J13 pin 1. NC pin 2 is unused. The second pole, pins 5/6/7, is explicitly unused. Pin mapping comes from [Omron's G6K datasheet](https://omronfs.omron.com/en_US/ecb/products/pdf/en-g6k.pdf); driver pin mapping from [ST's ULN2003A datasheet](https://www.st.com/resource/en/datasheet/uln2001.pdf).
- J13: two-pin JST-XH header, assigned the same series and 2.50 mm pitch footprint as the existing two-pin board headers. Use its matching housing; the stocked 2.54 mm Multicomp parts are not interchangeable.
- Inventory queried live: G6K-2P-Y, ID 420, THT, 5 V, quantity 4, reserved 0; storage location is not recorded. This covers three existing relays plus K4, subject to physical stock/marking confirmation. Inventory was not consumed or reserved.

One added nominal coil consumes 21.1 mA on 5 V (about 0.106 W at rated voltage), plus approximately 5 mA on the trigger supply while AV is selected. Existing supply capacity is sufficient for this increment. The previously accepted ULN2003A/5V G6K pickup-margin limitation still needs bench confirmation; this change does not qualify relay operation or firmware sequencing.

K4 is assigned `InputSwitch:Relay_DPDT_Omron_G6K-2P-Y_Datasheet`. This new project-local footprint uses the Omron drawing's 3.2 mm NC-pin distance from the coil end; the installed stock footprint uses 3.0 mm. Only the new K4 footprint is corrected; K1–K3 assignments and geometry remain untouched. The row separation is 5.08 mm, COM distance 5.4 mm, and NO distance 7.6 mm. `scripts/build_g6k_trigger_footprint.py` generates this footprint without loading a PCB.

## Verification and handover

- Exported KiCad netlist confirms the new positive/return pin mapping and the shared selection command.
- 508 checks pass: existing pin nets remain unchanged except the repurposed U3 pins 4/13; all retained Control-sheet objects are unchanged; unrelated root files match their backups; the unused contacts are open; and the existing reset pull-down remains connected.
- ERC: the same three pre-existing `power_pin_not_driven` errors on #PWR20009, U1 pin 1, and U5 pin 8. No new errors or warnings; no exclusions or rule changes added.
- KiCad SVG render visually reviewed for the new control block. `control-after.png` and `trigger-detail.png` show it.
- The PCB is restored to its original version and intentionally has no K4/J13. Layout, routing, schematic/PCB parity and DRC for this addition remain the user's next stage. No bench or thermal testing performed.

Backups are in `source/`; hashes and checks are in `hashes-before.json`, `hashes-after.json` and `verification.json`. `scripts/add_subwoofer_trigger.py` reproduces the scoped schematic addition from that snapshot; it does not run the old full-project generator.

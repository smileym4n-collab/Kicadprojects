# InputSwitch pre-order review — 9 October 2026

## Decision: hold the PCB order for footprint decisions

Reviewed the saved PCB and schematics, and separately checked the newer PCB autosave. No production design files were edited. The newer autosave has identical footprints, tracks, arcs and vias; one AV_L_SIGNAL zone differs internally, with the same boundary coordinates. A final saved revision and regenerated manufacturing files are still needed.

## IMPORTANT — address before ordering

1. **K1–K3 mechanical footprint mismatch.** The embedded footprints locate pads 2/7 at 3.0 mm from coil pads 1/8. Omron specifies 3.2 mm for G6K-2P-Y; COM and NO positions are 5.4 and 7.6 mm. The 0.85 mm holes do not justify assuming that the wrong centres fit across tolerances. K4 already uses the project-local corrected footprint `InputSwitch:Relay_DPDT_Omron_G6K-2P-Y_Datasheet`. Use that geometry for K1–K3, reconnect the moved pads and rerun DRC/parity. This is a mechanical issue, separate from the accepted ULN2003A driver choice.
2. **J1–J13 are still JST-XH 2.50 mm.** Your declared stock is Multicomp 2.54 mm. Decide between fitting matching JST headers/housings or changing the footprints to drawing-verified Multicomp geometry. Neither the stock statement nor a small pitch difference proves mechanical compatibility. J8/J9 are three-pin; the other eleven are two-pin.
3. **Three schematic ERC errors remain.** Power-input-not-driven on #PWR20009 (control GND), U1.1 (+12V) and U5.8 (ISO_L_QUIET). These are source-declaration issues, not evidence of open PCB traces. Add legitimate PWR_FLAG declarations after confirming the feeds, rather than disabling ERC checks.

## VERIFIED OK within this review

- Saved-board DRC with refill and schematic parity: zero unconnected items, zero parity discrepancies, zero non-excluded violations. Four previously excluded F2 silkscreen/mask warnings remain.
- Newer autosave checked in isolation: zero unconnected items and zero parity discrepancies. Additional missing-library warnings arise solely from the review copy lacking the project library table (U1, U10, U11 and K4); the production-location DRC does not have them.
- All four copper layers visually inspected. The earlier local capacitor moves, added C10, wider converter power branch and local ground domains remain present. The previous AUDIO_PRESENT_N routing correction and removal of the overlap beneath U10 remain in place.
- K1/K2 net assignments select both signal and return; K3 disconnects the source signals and shorts P3A inputs to their selected returns when energized. No unexpected net assignment was found in these relay connections.
- U3 inputs 1/3/4 are SOURCE_AV, outputs 16/14/13 feed K1/K2/K4 respectively; input 2/output 15 controls mute K3. COM9 is +5V, emitter8 is GND. Unused inputs are grounded.
- New K4 trigger routing matches the schematic: coil1 +5V, coil8 K4_LOW; NO4 protected +12V, COM3 J13.1; J13.2 GND. Unused contacts are explicitly unused. K4 follows source selection independently of mute.
- U4 COM9 is +12V, emitter8 GND, input1 P3A_ON and output16 G7L_LOW. J10 carries external relay coil power, not mains.
- SPU03 input pins 1/2 are +5V/control GND, output 7/5 are isolated positive/selected return. LM358 pins8/4 are corresponding quiet rail/selected return. Optocoupler transistor returns are control GND.
- D1 cathode and D2 cathode connect to protected +12V. C1/C3 positive pads connect to +12V/+5V respectively. Q2/Q3 schematic-to-pad mapping is collector1, base2, emitter3; actual bought transistor manufacturer/package pinout remains an assembly check.
- U2 supply, UPDI, source, mute, power command and detector input net assignments remain consistent with the established design.

## Assembly and remaining limits

- Keep R20/R40 at 30 ohm, 3 W, 1% flameproof; dissipation is about 0.83 W each at 5 V, 1.2 W at 6 V. Raised mounting and enclosure heat clearance still matter.
- F2 purchasing requirement is T1A, despite the abbreviated 1A component value. Retain capacitor voltage ratings in the assembly BOM.
- U1 footprint has 1.2 mm drills. RECOM's current drawing recommends 1.3 mm holes for its 0.64 mm nominal square pins. This is not a demonstrated fit failure, but matching the recommended hole size would remove another assembly uncertainty before fabrication.
- Most reference designators remain hidden on silkscreen. Adding key IC/diode/connector references helps assembly but is not an electrical blocker.
- Retain the accepted ULN2003A/G6K design decision; it is not raised again as a blocker.
- Firmware sequencing, measured audio noise, converter startup, thermal behaviour, actual transistor/connector stock, enclosure washers/standoffs and complete manufacturer-by-manufacturer package certification are not established by this review. No production-ready or guaranteed-first-build claim is made.
- No final Gerber/drill package was approved. After footprint decisions and saving/refilling, regenerate manufacturing files from the final revision and inspect the fabrication preview before payment.

## Sources and evidence

- Omron G6K datasheet, page 6, G6K-2P-Y bottom-view mounting drawing: https://omronfs.omron.com/en_US/ecb/products/pdf/en-g6k.pdf
- RECOM mechanical drawing (previously inspected in this chat): https://recom-power.com/pdf/Innoline/R-78K-2.0.pdf
- Current evidence in this folder: erc.json, drc.json, netlist.xml, layers.pdf, layer-0.png through layer-3.png, source/ and autosave-check/.

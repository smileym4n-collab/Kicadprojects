# InputSwitch follow-up layout review

Reviewed saved files dated 3 October 2026, 23:27. Read-only review against the previous findings; production files were not edited. ULN2003A with 5 V G6Ks is an accepted user decision and is not treated as an outstanding blocker.

## Result

Most requested layout corrections are implemented. Two copper-layout refinements and the existing three schematic power-source declarations remain. This review verifies the changes and current rule checks; it does not establish measured noise, thermal performance, firmware operation or production qualification.

## Corrected

- C9 is now beside U9: approximately 2.2 mm from capacitor centre to VCC pin 5, versus about 36 mm previously.
- C40 is now beside U11: about 4.9 mm centre to input pin 1, versus about 40 mm previously. Its supply pad is connected by a short local track. C20 remains beside U10, about 4.8 mm centre to input pin 1.
- C10, 10 uF, has been added across +5V/GND near U1. This implements the additional output ceramic recommendation. Its positive pad is about 8 mm from U1 output; closer would be preferable if convenient, but the capacitor is in the local regulator area.
- U10/U11 now have a dedicated 1 mm +5V branch from U1 on In2.Cu, independent of the narrow MCU feed. Short local capacitor connections remain 0.4 mm.
- Control GND and both selected returns now have F.Cu/In1.Cu zones. The main detector regions use their own selected-return copper, with no copper DC short between domains reported by DRC.
- LM358 bypass capacitors are slightly closer, approximately 4.6–4.7 mm centre to supply pin.
- AUDIO_PRESENT_N no longer crosses the left detector's central circuitry; the right-edge branch is also outside the right detector plane.

## Remaining layout refinements

### 1. AUDIO_PRESENT_N still passes under the right detector

The left optocoupler branch on In2.Cu runs diagonally from approximately (130.683,139.700) to (135.890,144.907), then vertically at x=135.890 to y=173.228. Part of this lies beneath the right detector's SEL_R_RETURN plane, including (135.890,148.000) and (135.890,152.000), verified against refilled copper.

Move this branch into the gap between the detector islands, on the control side of U6, then around the lower perimeter. Keep it clear of both detector return regions on other layers, preferably alongside a control-GND return. The signal is slow and filtered: this is a coupling/layout refinement, not evidence of audible noise or a DC short.

### 2. Control GND overlaps the left selected return beneath U10

The In1.Cu control-GND strip feeding the right-hand module crosses underneath the F.Cu SEL_L_RETURN tongue linking the left detector to its preload. Refilled copper confirms SEL_L_RETURN on F.Cu and GND on In1.Cu at (107–109,160) mm. This small overlap adds inter-domain capacitance; it does not short the grounds.

If preserving the intended clean separation, reshape the control-GND corridor and/or selected-return connection to remove this overlap. Simply cutting the control-GND strip would interrupt its return path: reroute it deliberately, then refill and recheck. No wholesale extra ground pours are needed.

## Schematic and assembly details still open

- ERC still reports power-input-not-driven on #PWR20009 (GND), U1 pin 1 (+12V) and U5 pin 8 (ISO_L_QUIET). These are the same three source-declaration issues as before. Verify the intended feeds and add appropriate PWR_FLAG declarations; do not blanket-suppress them.
- F2 value is still `1A`, while the sheet note specifies T1A. Make the purchasing/assembly value explicit.
- R20/R40 still have `30R` values. Sheet notes specify 3 W flameproof; retain the full 30 ohm, 3 W, 1% requirement in the assembly BOM.
- Most component references are still hidden from top silkscreen. Adding key references remains useful for assembly/service, not an electrical blocker.
- Preload spacing and enclosure thermal behaviour remain assembly considerations; keep the previously recommended raised mounting. No thermal test or enclosure-clearance validation was performed.

## Checks and evidence

- Production-location DRC with zone refill and schematic parity: zero unconnected items, zero parity findings, zero non-excluded violations. Four existing excluded F2 silkscreen/mask warnings remain.
- ERC: three errors listed above, unchanged.
- Copper inspected on all four layers. An isolated copy was additionally refilled and saved for checking actual filled polygons. That copy reports three missing local-library configuration warnings for U1/U10/U11 because the project-local library table was not copied; these are review-copy artefacts, absent from the production-location DRC.
- Source hashes before and after review match. No production schematic, PCB or settings edits.
- Evidence: drc.json, erc.json, geometry.txt, layers.pdf, source-hashes.txt and refilled/ in this folder. The source/ folder preserves the reviewed snapshot.

This follow-up supersedes the previous report's status for the corrected items and the accepted relay-driver choice. Inventory was not queried again in this follow-up.

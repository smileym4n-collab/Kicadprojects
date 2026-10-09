# InputSwitch PCB review and stock check

03 October 2026. One board. Read-only review of the saved 100 x 100 mm, four-layer PCB: 104 footprints including two logos, 315 straight track segments plus arcs, 24 vias. This is a pre-fabrication review, not acoustic, firmware or thermal qualification.

## Verdict

The overall arrangement is good: audio connectors and relays are at the top, two compact detector sections below them, control electronics to the left, and the isolated converters/preloads at the bottom. Routing is electrically complete under the current design rules. I would make the supply-layout corrections below before ordering boards. The ULN2003A relay pickup margin still prevents a claim of guaranteed first-build operation.

## Verification results

- DRC with zone refill and schematic parity: zero non-excluded violations, zero unconnected items and zero schematic-parity findings. Four excluded warnings are fuse-holder F2 silkscreen segments touching its solder-mask openings. These are cosmetic; do not interpret them as copper faults.
- DRC settings use 0.20 mm default net clearance, 0.20 mm minimum track width, 0.50 mm copper-to-edge clearance and 0.30 mm minimum through-hole drill. Some checks, including missing courtyard, are disabled in the existing project. No settings or exclusions were changed.
- Independent comparison of multi-pad net membership: no mismatches against the latest saved schematic. U3 input/output channel assignments now correctly pair source control with K1/K2 and mute with K3.
- ERC: three errors remain, all power-input-not-driven: GND power symbol #PWR20009, U1 pin 1 (+12V) and U5 pin 8 (ISO_L_QUIET). Netlist tracing shows the intended feeds through the external connector/diode/filter. Restore appropriate source declarations after confirming these paths; do not suppress the errors indiscriminately.
- The first DRC attempts crashed at macOS application registration inside the sandbox. The same read-only DRC succeeded outside it. DRC did not save/refill the production board file on disk.
- The schematic was saved during this review, resolving initial differences in U3 pin assignments and U1/C40 properties. The latest netlist and ERC were regenerated. PCB and project-settings hashes remain identical to the initial snapshot. No production file was edited by this review.

## CRITICAL - unresolved design margin

**U3 / K1-K3: 5 V G6K coils driven by ULN2003A.** The G6K must-operate threshold is 80% of rated coil voltage at the specified reference conditions: 4.0 V for a 5 V coil. A conservative 1.1 V Darlington-drop screen leaves 3.9 V from a nominal 5.0 V rail, before rail tolerance, wiring loss and coil heating. The 1.1 V figure is a screening assumption, not a guaranteed maximum at this coil current. This does not prove failure, but it cannot support a guaranteed-pickup claim. A larger-current 5 V regulator does not remove the drop. Your requirement to retain ULN2003A is respected; a driver/coil solution with guaranteed operating margin still needs an explicit design decision. Do not raise the shared 5 V rail casually: it also powers logic and SPU03 inputs.

## IMPORTANT - changes before fabrication

**1. Put C40 beside U11; return C9 to U9.** C40 (10 uF) is currently beside C20/U10, approximately 40 mm from U11 input pin 1. C9 (100 nF) is beside U11, approximately 36 mm from U9 VCC pin 5. Move C40 across U11 pins 1/2 with short connections. Move C9 immediately beside U9 pins 5/3. Keep C20 at U10. Adding a separate 100 nF at each SPU03 input is a useful optional provision using existing stock; it does not replace the 10 uF capacitors.

**2. Give the converters their own power branch.** The +5 V feed to U10/U11 traverses long 0.4 mm tracks through the MCU/control supply route before reaching the modules; the modules are then daisy-chained. Route a wider dedicated feed from U1/C3 to C20/C40 and the modules, with a nearby control-GND return. Branch the MCU supply separately near the regulator output. A roughly 1 mm feed is a sensible starting point where space permits, with short pad neck-downs; final width depends on copper thickness and the current budget. This reduces common supply impedance and converter-current injection into the logic supply.

**3. Improve U1 output bypassing.** C3 supplies 47 uF bulk storage and C4 is 100 nF, but the board has no local 10 uF ceramic directly across U1 output/GND. RECOM characterises output ripple with a 10 uF low-ESR MLCC. Add that provision near pins 3/2 using stock, retaining C3. This is a recommendation to approach the published ripple test setup, not a claim that the module cannot operate without it. Keep C2 close to pins 1/2 as the input ceramic. The module's full EMC filter is not implemented, so board-level EMC performance is unverified.

**4. Keep AUDIO_PRESENT_N outside the detector islands.** It crosses under the left detector on In1.Cu around y=143 mm and under the right detector on B.Cu around y=140-143 mm. This is control-domain wiring overlapping isolated audio-return copper. It creates capacitive coupling, not a DC ground short; C8 also slows this node, so it is not automatically an audible-noise fault. For the cleanest layout, route it with control GND around the lower/outside perimeter rather than under U5/U7 and their local returns. Preserve the copper gaps across each optocoupler and between SPU03 primary/secondary pins on every layer.

**5. Finish the schematic and BOM annotations.** Restore the three legitimate power-source declarations, retain explicit 3 W / 1% on R20/R40 in the assembly BOM, retain voltage ratings on capacitors, and specify F2 as the intended time-delay 1 A fuse rather than simply '1A'. The PCB abbreviates several component values; purchase from the full requirements, not silkscreen alone.

## IMPROVEMENTS - worthwhile while placement is still editable

- C22/C42 are about 5.6 mm from LM358 pin 8 by centre-to-pin distance; their actual supply trace is roughly 6 mm. These are reasonably local, but can be tucked closer to pin 8, with a broad local-return connection. Do not confuse this optional refinement with the much larger C40/C9 displacement.
- R25/R45 feedback and the sensing/clamp networks are compact. Avoid making the pin-3 sensing node or pin-2 feedback node larger while rerouting. Keep the longer sensing run before R23/R43 (470k).
- Preloads are well away from the electrolytics, but their nominal body edges are only about 2.7 mm from the SPU03 case edges. Each dissipates about 0.83 W at 5 V, 1.2 W at 6 V. Mount the resistors about 5 mm above the PCB and increase separation from the modules if enclosure space allows. Heat and enclosure air temperature remain unqualified.
- Inner layers currently contain sparse signal/power tracks, not continuous reference planes. This is not a DRC fault. If retaining four layers, use deliberate control-GND copper in the control region and local selected-return copper where useful; never flood control GND beneath the isolated detector regions or bridge the domains.
- Most component references are absent from the top silkscreen. Add at least IC, connector, diode and key resistor references for assembly/service, and retain clear pin-1/polarity markings.
- Check washer/standoff envelopes around H1-H4 and clearance above the bottom-edge power resistors in the enclosure. Copper-edge DRC does not verify mounting hardware or vertical clearances.

## VERIFIED OK within this review

- The selected-return domains remain distinct in the netlist: SEL_L_RETURN, SEL_R_RETURN and control GND are not tied by copper connectivity. The P3A can still join L/R externally as previously discussed.
- SPU03 input pins 1/2 go to +5V/control GND; output pins 7/5 go to the corresponding isolated supply/selected return. Optocoupler LED and transistor sides have the intended domains.
- R20/R40 connect across raw isolated outputs; R21/R41 and C21/C41 filter the LM358 rails. High preload current is not routed through the 100-ohm filters.
- U3 COM pin 9 is +5V; U4 COM pin 9 is +12V; both emitters pin 8 are control GND. D1 cathode faces protected +12V and D2 cathode is on +12V.
- The primary audio path still uses relay contacts only. The four added 100k resistors connect each source signal to its own return. The selected source sees about 85k from 100k in parallel with the approximately 570k detector input, before the P3A input load.
- Both LM358 supply pin mappings and the optocoupler pin mappings agree with their intended circuit roles. No mains routing is present on this control PCB; J10 is coil drive only.

## Order list - no matching stock record found

Quantities below are fitted quantities for ONE board. Buy a few spare small passives if useful. 'No record' means no suitable entry found in the connected inventory, not proof that your physical drawers are empty. This is a shortage list, not a placed order or a live priced basket.

| Qty | Part / requirement | References | Package / purchasing note |
| --- | --- | --- | --- |
| 1 | RECOM R-78K5.0-2.0 | U1 | Standard upright SIP3; no L suffix. Fits current local footprint. |
| 2 | Vishay VO617A-3 | U6, U8 | Standard DIP-4, 7.62 mm row spacing; avoid SMD or wider-row suffixes. |
| 1 | TI SN74LVC1G04DBVR | U9 | SOT-23-5 / DBV. |
| 1 | SS14 | D1 | SMA / DO-214AC, e.g. Vishay SS14-E3/61T. |
| 1 | SMBJ13A | D2 | Unidirectional TVS, SMB / DO-214AA; do not buy SMBJ13CA. |
| 2 | Vishay PR03000203009FAC00 | R20, R40 | 30 ohm, 3 W, 1%, axial copper-lead PR03; form leads to 25.4 mm pitch. |
| 2 | 390 ohm, 1%, >=0.125 W | R32, R52 | 2012 metric. |
| 2 | 470k, 1%, >=0.125 W | R23, R43 | 2012 metric; thin-film preferred. |
| 2 | 2M2, 1%, >=0.125 W | R13, R49 | 2012 metric; thin-film preferred. Left reference is now R13, not R29. |
| 4 | 33 uF, >=16 V, reputable radial electrolytic | C23, C25, C43, C45 | Board allows 5 mm body / 2.50 mm pitch; verify exact orderable part dimensions before buying. |
| 1 | 100 uF, 35 V radial electrolytic | C1 | Board allows 6.3 mm body / 2.50 mm pitch. Stock has 16/25 V parts, not the specified 35 V part. |
| 1 | Schurter 0031.8201 fuse holder | F2 hardware | Footprint names this 5 x 20 mm holder; confirm bought drawing against footprint. |
| 1 | T1A time-delay fuse, 5 x 20 mm | F2 fuse | Separate from holder; choose voltage/breaking rating suitable for the 12 V adapter circuit. |
| 10 | JST B2B-XH-A vertical headers | J1-J7, J10-J12 | 2 positions, 2.50 mm pitch; finish suffix per supplier. |
| 2 | JST B3B-XH-A vertical headers | J8, J9 | 3 positions, 2.50 mm pitch. |
| 10 + 2 | JST XHP-2 + XHP-3 mating housings | Harnesses | If not already owned; J8 housing only if making a programming lead. |
| 26 minimum | Compatible XH crimp contacts | Harnesses | Select SXH contact version for actual wire gauge; allow spares. |

The stocked Multicomp MC34629/MC34631 headers and MC34481/MC34483 housings are a 2.54 mm family. They are not verified substitutes for these JST-XH footprints or housings; do not mix them in the order.

## Existing stock to use

All listed records show zero reserved quantity at lookup. Quantities are database stock, not physically counted. Manufacturer/package identities are stronger evidence than generic passive entries; notes below identify outstanding checks.

| Need | Part / value | Available (inventory ID) | References / location / confidence |
| --- | --- | --- | --- |
| 3 | Omron G6K-2P-Y, 5 V | 4 (#420) | K1-K3; location not recorded. Exact family/package matches; pickup margin remains unresolved. |
| 2 | SPU03L-05 | 3 (#416) | U10/U11, Voltage regulator drawer. Inventory typo SPI03L-05; your earlier confirmation identifies SPU03L-05. |
| 2 | ULN2003A SOIC-16 | 7 (#121) | U3/U4, SMD Parts. Do not use DIP-16 stock for this board. |
| 1 | ATtiny412 SOIC-8 | 6 (#80) | U2, SMD Parts. Firmware must be programmed. |
| 2 | LM358 DIP-8 | 2 (#389) | U5/U7, Opamp drawer. Uses all recorded stock. |
| 2 | BC549 TO-92 | 117 (#452) | Q2/Q3, location not recorded. Verify actual manufacturer pinout and form leads for TO-92_Wide. |
| 4 | 1N4148 axial | 63 (#138) | D21/D22/D41/D42, Parts drawer 2. Not the SOD123 1N4148W stock. |
| 12 | 100k thin-film, 0.5%, 2012 | 70 (#242) | All 100k resistors, SMD Parts. Prefer this to the 5% thick-film stock for detector values. |
| 7 | 1k thin-film, 0.5%, 2012 | 42 (#224) | R1/R26/R33/R34/R46/R53/R54, SMD Parts. |
| 2 | 3k3, 1%, 2012 | 50 (#373) | R22/R42, SMD Parts. RMCF0805FT3K30. |
| 4 | 4k7, 1%, 2012 | 100 (#493) | R7/R8/R30/R50, SMD Parts. RMCF0805FT4K70. |
| 2 | 10k thin-film, 0.5%, 2012 | 46 (#232) | R27/R47, SMD Parts. |
| 5 | 47k, 1%, 2012 | 100 (#504) | R2-R5/R10, SMD Parts. RMCF0805FT47K0. |
| 2 | 100 ohm thin-film, 2012 | 26 (#209) | R21/R41, SMD Parts. Tolerance/power not recorded; check label (target 1%, >=0.125 W). |
| 6 | 100 nF 50 V X7R, 3216 | 129 (#157) | C4/C5/C7/C9/C22/C42, SMD Parts. Kemet C1206C104K5RACTU. Additional bypass proposals can use this stock. |
| 3 | 10 uF 50 V MLCC, 3216 | 10 (#505) | C2/C20/C40, SMD Parts. Samsung CL31A106KBHNNNE. One additional U1 output ceramic would bring use to four. |
| 1 | 1 uF 50 V MLCC, 3216 | 50 (#181) | C6, SMD Parts. Samsung CL31B105KBHNFNE. |
| 1 | 2.2 uF 10 V MLCC, 2012 | 63 (#182) | C8, SMD Parts. Samsung CL21B225KPFNNNE; actual timing varies with capacitance tolerance/DC bias. |
| 3 | 47 uF 25 V Panasonic FR | 50 (#95) | C3/C21/C41, Parts drawer 2. EEUFR1E470H; 5 mm body and formed 2.5 mm pitch match board provision. |
| 2 | 100 nF film, 63 V, 7 x 2 mm | 92 (#406) | C24/C44, Parts Drawer 2. Generic entry: check 5 mm lead pitch and dielectric/marking; 7 x 2 mm body fits the 7 x 2.5 mm provision. |
| optional 2 | DIP-8 turned-pin sockets | 33 (#178) | U5/U7, DIP sockets. Check resulting height beneath enclosure. |

## External items / physical-stock check

No matching inventory entry was found for the specified Omron G7L-2A-T DC12, the SPDT ON-ON selector, the two indicator LEDs or a regulated 12 V adapter. These may already be part of your system; check before ordering. J10 carries the G7L coil only. Include the appropriate relay terminals, wiring, insulated RCA connectors, short shielded audio leads and four M4 mounting sets. The mains assembly remains external and is not qualified by this PCB review. No alternative relay is approved by this stock check.

## Recommended next action

Move C40 and C9; add local U1 output ceramic; separate module power routing; move AUDIO_PRESENT_N out of the detector areas; resolve relay pickup margin; restore the three ERC source declarations. Then refill, rerun ERC/DRC and regenerate BOM/Gerbers. Do not order a PCB from the current snapshot solely because the copper DRC passes.

## Evidence and primary references

- Local: drc.json, erc-latest.json, netlist-latest.xml, connectivity-and-bom.txt, pcb-parts.json and the inventory JSON snapshots beside this report.
- RECOM R-78K: https://recom-power.com/pdf/Innoline/R-78K-2.0.pdf
- Mean Well SPU03: https://www.meanwell.com/Upload/PDF/SPU03/SPU03-SPEC.PDF
- TI inverter bypass guidance, section 8.4: https://www.ti.com/lit/ds/symlink/sn74lvc1g04.pdf
- ST ULN2003A: https://www.st.com/resource/en/datasheet/uln2001.pdf
- Omron G6K: https://omronfs.omron.com/en_US/ecb/products/pdf/en-g6k.pdf
- Vishay VO617A: https://www.vishay.com/docs/83430/vo617a.pdf
- Vishay PR03: https://www.vishay.com/docs/28729/pr010203.pdf
- JST-XH mechanical family: https://www.jst-mfg.com/product/pdf/eng/eXH.pdf

No acoustic measurements, transient simulation, firmware review, full enclosure model check or complete manufacturer-by-manufacturer footprint certification was performed. Recommendations reduce identified risks; they do not constitute fabrication or production approval.

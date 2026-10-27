# Pre-order schematic corrections — 23 October 2026

The non-grounding items from the pre-order review have been addressed in the existing schematic. **The user is handling U1 grounding. The user has confirmed the heatsink and C21 have been checked.** This update does not modify the PCB or claim a new PCB DRC pass.

All component values, footprint assignments, wires, labels, hierarchical interfaces, pins and UUIDs are retained. Changes are limited to component identification/specification fields, prose notes and schematic revision/date. The current routed assignment is documented consistently: **PCM5122 OUTL → tweeter/J17; OUTR → woofer/J16.** Firmware must use that assignment; the earlier left=woofer requirement is superseded for this preserved routing.

## Completed changes

| References | Final part / specification | Reason |
|---|---|---|
| C28 | KEMET C0805C105K3RACTU, 1u / 25 V X7R, 2012 metric | Correct part for retained footprint; replaces incorrectly assigned 3216 part. GVDD decoupling voltage margin is ample. |
| C30/C31/C33/C34 | Multicomp Pro MC0603B104K500CT, 100n / 50 V X7R, 1608 metric | Correct package for existing footprints; same specified part as C46/C48/C53. |
| C56/C57 | Samsung CL10B102KB8NNNC, 1n / 50 V X7R, 1608 metric | Corrects wrong 100n MPN and package; value remains 1n. These are supply bypass capacitors. |
| C45 | Samsung CL31A106KBHNNNE, 10u / 50 V X5R, 3216 metric | Matches existing PCB footprint and confirmed stock. Replaces incompatible 3225 Murata MPN. X5R is suitable here; actual bias/load assessment below. |
| C32/C54/C59/C60 | Multicomp Pro MC0805N103F500CT, 10n / 50 V C0G/NP0, 2012 metric | Finalises the four fitted post-filter RC capacitors using owned stock. |
| R6/R20/R34/R40 | Vishay CRCW08053R30FKEAHP, 3R3 / 1% / 0.5 W P70, pulse-proof, 2012 metric | Finalises the four fitted RC resistors; footprints retained. Power rating depends on cooling; verify actual resistor temperatures. |
| C21 | Nichicon UES1H470MPM, 47u / 50 V bipolar, 10 × 20 mm / 5 mm pitch | Records the intended part and user's check; JP1 is the onboard stereo bypass. |
| C1/C2/C5/C6 | KEMET R82DC4100AA60J, 1u / 63 V / 5%, metallized polyester film | Replaces old WIMA fallback metadata with the exact confirmed owned part. Manufacturer dimensions 7.2 × 5 × 10 mm and 5 mm pitch match the retained footprint. Electrical value/type remain film coupling. |
| J2 | JST B8B-XH-A(LF)(SN), 8-way top-entry XH / 2.50 mm pitch | Adds exact part identification for the existing user-selected JST footprint; connector series and pinout unchanged. |
| HS1 | ATS-TI1OP-521-C1-R1 | Records the exact heatsink and user-confirmed fit check; enclosure thermal testing remains separate. |

Conflicting inherited `Manufacturer_Part_Number` / manufacturer fields were reconciled to the selected MPN for R24, C49/C50, C51/C52, C46/C48/C53, D1, D2, J1 and IC5. These changes do not substitute those parts. For example, R24 no longer carries the old 13k7 ordering code, and D2 no longer carries the old SMAJ18A ordering code.

## Notes and firmware contract

- DAC, amplifier and top-level notes now consistently say **left=tweeter/J17; right=woofer/J16**.
- J2 is **1 GND, 2 MODEBTN, 3 volume wiper, 4 3V3, 5 GND, 6 BT LED drive, 7 GND, 8 Wi-Fi LED drive**. Pot low end uses pin 1 or 5, not pin 2. GPIO22's active-low button and 10k pull-up are documented.
- The obsolete external C54/J18 capacitor harness instructions were removed. **C21 is onboard; JP1 open = tweeter capacitor active; JP1 linked = bypass for stereo.** Change the link with power off; neither speaker terminal is GND.
- The old “R20 DNP” instruction was removed. R20 is a fitted 3R3 output RC resistor; PLIMIT is R19/C29 with no lower divider resistor.
- Removed references to deleted C41–C44/R35–R38 snubbers. The four actual fitted 10n/3R3 post-filter RC branches are identified.
- The obsolete 20 × 18 × 10 mm heatsink instruction was replaced with the ATS part and the user's check. Top-pad/GND and thermal-test notes remain.
- Startup prose now states: valid muted DAC/I²S, release DAC XSMT, enable SDZ, wait at least 50 ms, release amplifier MUTE, then ramp volume. Hardware defaults are unchanged.

## C45 DC-bias and load assessment

A 50 V marking does not mean a 10u ceramic retains 10u at 16 V. The Samsung-authored characteristics curve for CL31A106KBHNNNE shows approximately **3u typical effective capacitance at 16 V**. This was visually checked from the manufacturer's plotted curve; see [characteristics sheet](C45-Samsung-characteristics.pdf) and [render](C45-Samsung-characteristics.png). The manufacturer product page confirms 10u / 50 V / X5R / 3216 metric.

TI recommends a nominal 4.7u or higher X5R/X7R input ceramic, with voltage rating preferably at least twice maximum VIN. C45 is nominal 10u / 50 V, with C46's local 100n and C47's input bulk retained. The buck supplies the low-voltage electronics, not the loudspeaker output power.

Using VOUT=4.304 V, fs=500 kHz and D=VOUT/VIN, the ideal capacitive input ripple estimate is `ΔVIN ≈ IOUT × D × (1−D) / (fs × CEFF)`:

- At 16 V, 1 A output and 3u effective capacitance: approximately **0.13 Vpp**.
- Using a conservative design scenario of 1.05 A output and only 1.5u effective capacitance: approximately **0.28 Vpp at 16 V**, or **0.32 Vpp at 12 V**. The 1.5u figure is an engineering margin scenario, not a manufacturer-guaranteed minimum.
- Maximum input-capacitor RMS current over 12–16 V at 1.05 A output is about **0.50 Arms**. The manufacturer's ripple-temperature curves indicate comfortable nominal capability at that current; temperature and tolerance still need hardware confirmation.

This is suitable for the actual ESP32 plus DAC load envelope with the retained bulk reservoir. It does not qualify 3 A continuous output from the buck or establish an arbitrary input-cable/transient environment. Check VIN ripple/overshoot and the 3.3 V rail during Wi-Fi bursts on the first board. No topology or PCB change was needed to resolve C45.

## Inventory and purchasing

The actual MCP inventory was refreshed for **all 40 inventory IDs used by the current BOM**, plus exact stock checks for unassigned purchase parts. No records were changed/reserved. See [inventory evidence](inventory.json), [additional exact checks](extra-stock.json), [inventory table](INVENTORY-USAGE.md), [current BOM CSV](BOM.csv) and [purchasing list](PURCHASING-LIST.md).

Relevant current quantities:

| Part | Required for this correction | Confirmed physical | Already on order |
|---|---:|---:|---:|
| C0805C105K3RACTU, C28 | 1 | 0 | 100 |
| MC0603B104K500CT, C30/C31/C33/C34 | 4, plus 3 elsewhere | 0 | 1000 |
| CL10B102KB8NNNC, C56/C57 | 2 | 100 | 0 |
| CL31A106KBHNNNE, C45 | 1 | 10 | 0 |
| MC0805N103F500CT, output RC caps | 4 | 10 | 0 |
| CRCW08053R30FKEAHP, output RC resistors | 4 | No matching record | Not confirmed |
| R82DC4100AA60J, input capacitors | 4 | 43 | 0 |
| PCM5122, U2 | 1 | **0** | 0 |

Do not order the on-order decouplers twice unless delivery requires it. “C21 checked” is recorded as the user's fit/specification confirmation, not invented MCP stock. The full shopping list separates missing physical stock, parts already on order and system/hardware items. Connector mating halves, antenna, heatsink fasteners/TIM and speaker wiring are separate from PCB electronic parts.

Vishay's selected resistor is listed by DigiKey as **541-3.30TCT-ND**, with stock shown during the 23 October lookup. This is a sourcing snapshot, not a reservation. Complete cart availability/prices were not verified for every pre-existing BOM part.

## Verification and remaining PCB work

- KiCad 10.0.5 successfully exported all five sheets, a fresh netlist and a new schematic PDF.
- **ERC: 0 errors, 28 warnings**, all the same off-grid warnings with unchanged item signatures.
- **119 connectivity assertions pass.** The complete set of pin-to-net memberships is unchanged from the reviewed board-matching schematic.
- All values, footprint assignments, electrical/graphical objects and component UUIDs are unchanged. Only symbol properties, notes and title blocks changed.
- **PCB, project and preference files are byte-for-byte unchanged** at completion; see [verification.json](verification.json).
- The schematic renders were checked for readable notes and spacing. [Current schematic PDF](TPA3126-schematic.pdf).

The earlier PCB DRC remains the last PCB result: zero unconnected pads, but existing exclusions including U1's ground thermals. No new DRC was run because this update made no PCB changes. The user is addressing U1 grounding; refill and run final DRC on that saved board before fabrication. Other previously reviewed exceptions and bench-qualification requirements remain documented in the [pre-order review](../../preorder-2026-10-23/REVIEW.md). The user's physical heatsink/C21 checks close the outstanding fit questions; they do not establish enclosure thermal performance or speaker-capacitor heating under programme material.

No change is required to PCB footprints or routes to apply these schematic metadata corrections. Synchronise component fields to the PCB if those fields are exported from it. Retain the user-selected routing. The optional “TDA3126” silkscreen typo correction and the earlier layout improvements can be made with the user's PCB update.

## References

- [KEMET C0805C105K3RACTU spec](https://search.kemet.com/component-documentation/download/specsheet/C0805C105K3RACTU)
- [Multicomp Pro 100n / 50 V product data](https://cpc.farnell.com/multicomp-pro/mc0603b104k500ct/mlcc-0603-x7r-50v-100nf/dp/CA06380)
- [Samsung 1n / 50 V part](https://product.samsungsem.com/mlcc/CL10B102KB8NNN.do)
- [Samsung 10u / 50 V part](https://product.samsungsem.com/mlcc/CL31A106KBHNNN.do); [Samsung-authored plotted characteristics, distributor mirror](https://www.allelcoelec.com/datasheets.f7/CL31A106KBHNNNE.pdf)
- [Multicomp Pro capacitor manufacturer sheet](https://www.farnell.com/datasheets/4417444.pdf)
- [Vishay CRCW-HP e3 datasheet](https://www.vishay.com/docs/20043/crcwhpe3.pdf); [selected resistor sourcing](https://www.digikey.com/en/products/detail/vishay-dale/CRCW08053R30FKEAHP/5326912)
- [KEMET R82DC4100AA60J spec](https://search.kemet.com/download/specsheet/R82DC4100AA60J)
- [JST XH manufacturer drawing](https://www.jst-mfg.com/product/pdf/eng/eXH.pdf)
- [TI LMR51430 input capacitor guidance](https://www.ti.com/lit/ds/symlink/lmr51430.pdf), section 9.2.2.6

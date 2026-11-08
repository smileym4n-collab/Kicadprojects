> **Current update — 23 October 2026:** See [pre-order corrections](revisions/preorder-corrections-2026-10-23/README.md), [current purchasing list](PURCHASING-LIST.md) and [current inventory table](INVENTORY-USAGE.md). The material below describes an earlier revision; old schematic ZIPs are historical. Current working schematic PDF has been regenerated. Do not replay legacy design scripts against the current project.

# Current PCB heatsink clearance review

19 October 2026. Read-only check of the current saved PCB. User confirms the salvaged 20 x 18 x 10 mm heatsink has a flat underside.

**Centred mounting conflicts with C24-C27. An approximately 5 mm left offset is feasible in plan view and preserves full thermal-pad coverage; verify physical mounting and tolerances.**

Assume the heatsink is centred on U1, 20 mm along PCB X and 18 mm along Y. U1 is at X148.6875, Y115.223 mm. The sink spans X138.6875-158.6875 and Y106.223-124.223 mm. Its 24 x 22 mm manual assembly guide spans X136.6875-160.6875 and Y104.223-126.223 mm. There is no HS1 instance on the saved PCB; the envelope was overlaid for this review only.

| Component | Current position / clearance | Finding |
|---|---|---|
| C24 | Centre X155.702, Y110.744 mm | Fully under flat sink |
| C25 | Centre X155.702, Y113.792 mm | Fully under flat sink |
| C26 | Centre X155.702, Y116.078 mm | Fully under flat sink |
| C27 | Centre X155.702, Y118.872 mm | Fully under flat sink |
| L2/L3 | Saved F.Fab left boundary X166.474 mm | 7.7865 mm horizontally from sink body; 5.7865 mm beyond assembly guide |
| C10 | Saved body right boundary X130.623772 mm | 8.0637 mm horizontally from sink body |
| C28/C32/C33/C34/C35/C36/R18 | Still in the unplaced area, beyond the board outline | Their final fit around the heatsink is not validated |

The bootstrap capacitors are Samsung CL21B224KAFNNNE, 2012 metric, 2.00 +/-0.10 by 1.25 +/-0.10 mm in plan and **1.25 +/-0.10 mm thick**. Their maximum body height is 1.35 mm before mounted solder height. TI DAD0032A specifies U1 seating-plane-to-top height **1.00-1.15 mm**. The capacitor and IC height ranges therefore overlap unfavourably, even before solder and assembly tolerance. A nominal 0.1 mm thermal bond would place the flat sink underside roughly 1.10-1.25 mm above the seating plane; that is not guaranteed to clear the capacitors. Do not let the sink rest on the capacitors or bend against their solder joints.

Rotating the sink through 90 degrees (18 mm along X, 20 mm along Y) still covers all four capacitor bodies, so rotation alone does not solve it. A 5 mm shift to the left does remove this overlap while retaining full thermal-pad coverage in plan view. The proposed sink centre is X143.6875, Y115.223 mm, with body bounds X133.6875-153.6875 and Y106.223-124.223 mm. The maximum top-pad envelope (approximately 4.11 x 4.36 mm) is fully inside that base. This leaves 1.0145 mm to the nominal capacitor bodies (about 0.9645 mm allowing their maximum body length), 3.0637 mm to the saved C10 body and 12.7865 mm to L2/L3. Actual component and placement tolerances, underside flatness, adhesive retention and tilt remain to be checked. The sink centre will no longer coincide with the IC centre; the original footprint must be positioned with this deliberate offset if the proposal is adopted.

## Practical next layout choices

**Simplest option: use the existing flat sink with an approximately 5 mm left offset, if the physical assembly confirms the calculated clearances.** This keeps the electrically important bootstrap capacitors close to U1 and does not require moving them or adding thermal interfaces. The original 24 x 22 mm guide would overlap the capacitors because its extra 2 mm margin exceeds the approximately 1 mm actual gap; it is a manual planning margin, not a mandatory electrical clearance. Check the real sink dimensions, capacitor positions and adhesive/retention before adopting the offset. Do not use the small top thermal pad as an unverified mechanical cantilever.

If centred mounting is required:

1. **Keep the flat sink and move local passives outside its plan envelope, or onto the underside with very short connections.** There is approximately 7.8 mm body-to-body space toward L2/L3 in this saved placement, so a top-side strip for the four bootstrap capacitors is geometrically plausible. To place a maximum 2.10 mm-long capacitor body at least 0.5 mm outside the right sink edge needs centre X >=160.2375 mm. Keeping its entire current 3.76 mm courtyard beyond the 24 x 22 guide needs centre X >=162.5675 mm. These are placement bounds, not a routed proposal. Re-evaluate short bootstrap loops and shared high-current paths before moving them; do not use unnecessarily long bootstrap wiring simply to avoid the sink.
2. **Alternatively, deliberately raise the heatsink using a correctly sized, retained thermal pedestal/spacer.** A real metal thermal contact path can create vertical space, but interface area, two bond lines, electrical potential, retention, tilt and the increased enclosure height need a separate mounting design. Do not substitute a thick generic thermal pad without checking its added thermal resistance. No spacer is selected or added here.

Wherever the flat base overhangs the PCB, treat the area as unavailable for these 1.35 mm-tall capacitors unless height is deliberately established. The offset option puts all four outside the actual base. Very low parts under the overhang still require measured worst-case vertical clearance. The flat sink also spans the amplifier leads, which need inspection for solder protrusions, conductive adhesive squeeze-out and tilt. The existing 2D guide is not a 3D collision check or DRC-enforced keepout.

The efficient next step is to agree a mounting approach, then perform a small placement study of amplifier bypassing and bootstraps. No placement or routing was changed in this review. No DRC was run because the board is unchanged; the identified failure is mechanical height clearance, not a reported DRC violation. Thermal adequacy remains a separate measurement requirement.

## Evidence

- [Centred placement conflict](heatsink-preview/Current-PCB-heatsink-clearance.svg)
- [Proposed 5 mm offset](heatsink-preview/Offset-PCB-heatsink-clearance.svg)
- [Numerical bounds and saved-board SHA-256](validation/heatsink-current-placement.json)
- [TI TPA3126D2 datasheet, DAD0032A package drawing](https://www.ti.com/lit/ds/slos942/slos942.pdf)
- [Samsung CL21B224KAFNNN family, including CL21B224KAFNNNE](https://product.samsungsem.com/mlcc/CL21B224KAFNNN.do)

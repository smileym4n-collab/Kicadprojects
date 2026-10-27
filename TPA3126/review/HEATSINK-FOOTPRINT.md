> **Current update — 23 October 2026:** See [pre-order corrections](revisions/preorder-corrections-2026-10-23/README.md), [current purchasing list](PURCHASING-LIST.md) and [current inventory table](INVENTORY-USAGE.md). The material below describes an earlier revision; old schematic ZIPs are historical. Current working schematic PDF has been regenerated. Do not replay legacy design scripts against the current project.

# Salvaged TPA3126D2 heatsink envelope

Footprint: `Custom:Heatsink_20x18x10mm_TopMount_Clearance24x22mm`
Schematic: HS1 on the amplifier sheet. It will be available during a future Update PCB from Schematic. This task does not modify the PCB.

- Origin: geometric centre; align it with U1's footprint origin when placing it later.
- F.Fab: actual plan envelope, 20 mm along X and 18 mm along Y.
- Dwgs.User: dashed 24 x 22 mm assembly-clearance guide, giving 2 mm around the body. This is a provisional placement margin, not an electrical-clearance standard.
- Height: 10 mm above the heatsink base. Add amplifier package height, adhesive/interface thickness and enclosure clearance to obtain required height above the PCB.
- No pads, drill holes, copper/mask/paste, inferred mounting hardware or detailed 3D fin model are included.
- There is deliberately no F.CrtYd: HS1 sits above U1, so a solid courtyard would create an intentional collision with the amplifier. The drawing-layer guide does not enforce DRC clearance. Check neighbouring components, heights and overhang manually.
- Rotate as needed to match the actual sink and IC orientation. Confirm that the flat contact area reaches the top thermal pad without contacting leads or other exposed potentials. Overall dimensions do not establish underside geometry, attachment strength or cooling performance.

The 20 x 18 x 10 mm dimensions are supplied by the user. This footprint is a mechanical planning aid and does not qualify the salvaged heatsink thermally.

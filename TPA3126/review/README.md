> **Current update — 23 October 2026:** See [pre-order corrections](revisions/preorder-corrections-2026-10-23/README.md), [current purchasing list](PURCHASING-LIST.md) and [current inventory table](INVENTORY-USAGE.md). The material below describes an earlier revision; old schematic ZIPs are historical. Current working schematic PDF has been regenerated. Do not replay legacy design scripts against the current project.

# Schematic review package

Open `TPA3126.kicad_sch` in KiCad 10 from the project root. The existing `.kicad_pro` settings are retained. Start with `REVIEW-REPORT.md` and `TPA3126-schematic.pdf`.

All five existing schematic sheets were completed in place. Original files are preserved in `original/`. The capacitor revision does not modify the PCB. This package does not qualify the current board for fabrication. The schematic-only ZIP deliberately omits the PCB.

J18: fit the external Nichicon UES1H470MPM capacitor harness for tweeter protection, or remove it and fit an insulated >=3 A shorting link for stereo. With neither fitted CH2 positive is open. Neither pin is ground. Change only with power removed.

Latest revision targets **2 x 15 W into 4 ohms at 16 V**. Start with `15W-POWER-REVISION.md`. Actual final ERC: **0 errors, 31 pre-existing off-grid warnings**. `validation/connectivity-checks.json` records 418 passing checks and one separate concurrent PCB preservation-change record. The agent made no PCB writes. Current verification command:

```
python3 review/scripts/verify.py --preservation-baseline review/revisions/15w-output/protected-hashes.json --record-external-changes
```

Other editing scripts are historical steps, not a build pipeline; do not rerun them to open/review the project.

Inventory snapshots are read-only MCP responses from 19 October 2026. No matching record means quantity unknown, distinct from an explicitly recorded zero. No stock was reserved or consumed. Purchasing quantities assume one board; offboard/mating/antenna items need physical checks.

This is ready for schematic review. Bench, acoustic, mechanical, thermal, layout and manufacturing qualification remain separate gates listed in the report.

The older heatsink envelope remains in the footprint library; no HS1 instance exists in the current saved amplifier sheet. See `HEATSINK-FOOTPRINT.md` and `heatsink-preview/Heatsink-U1-clearance.svg`. For current preservation checks use `--preservation-baseline review/revisions/heatsink-envelope/protected-hashes.json`.

Historical winding revision baseline: `review/revisions/output-winding-swap/protected-hashes.json`. L2/L3 complete windings have been swapped; update pad-net assignments during a future PCB update. See the final report for the exact pin table.

Latest scoped change, 22 October 2026: [volume potentiometer connection](VOLUME-POT-CONNECTION.md), J2 pins 2/3/4 and GPIO34 / ADC1_CH6. Current ERC evidence and preservation hashes are in revisions/volume-pot/. Older completion/BOM/review archives describe earlier saved states and have not been reconciled with all intervening user changes. The current schematic PDF includes this volume-input change.

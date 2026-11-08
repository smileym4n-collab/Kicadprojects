# Purchasing list - one board

No orders placed. Recheck supplier availability before ordering. Parts already present on the existing PCB, or in an unlogged kit, must be checked physically; they are not counted as owned here.

| References | Manufacturer part number | Quantity | Reason |
|---|---|---:|---|
| U2 | PCM5122PWR | 1 | MCP explicitly reports zero. Existing circuit does not establish ownership. |
| C37, C38, C39, C40 | MKP2D036801M00JSSD | 4 | WIMA 680n, 100 V, 5%, 7.2x8.5x14 mm, pitch 5 mm. |
| C54 | UES1H470MPM | 1 | External 47u / 50 V bipolar, 10x20 mm, 5 mm pitch. No matching MCP record. |
| C1, C2, C6, C5 | MKS2C041001F00JSSD | 4 | Stock is Kemet generic 1u / 63 V, body noted 7x5 mm. Check 5 mm pitch; WIMA MPN is a verified purchase fallback, not a claim about stock identity. |
| R35, R36, R37, R38 | RC0805FR-0718RL | 0 initially; 4 optional | DNP 18R snubber tuning resistors, 125 mW; pulse rating must be checked if populated. |
| F2 | 39613150000 | 1 | Time-delay TE5, 3.15 A / 125 V. Existing 395 footprint shares TE5 mechanical case. |
| R23, R27 | RC0603FR-07100KL | 2 | 100k / 1%, 1608; owned 2012 resistors do not match retained footprint. |
| R24 | RC0603FR-0716K2L | 1 | 16k2 / 1%, 1608; no matching MCP record. |
| C53, C48, C46 | MC0603B104K500CT | 3 | 100n / 50 V X7R, 1608 metric; exact inventory record has zero. |
| U4 | TLV1117LV33DCYR | 1 | No matching inventory record. Do not substitute TS1117B. |
| D2 | SMBJ16A | 1 | Littelfuse, unidirectional SMB. No matching MCP record. |
| C45 | GRM32ER71H106KA12L | 1 | 10u / 50 V X7R, 3225 metric, retain inherited footprint. Owned 3216 parts are not substituted. |

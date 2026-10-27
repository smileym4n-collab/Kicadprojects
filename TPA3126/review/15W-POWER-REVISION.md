> **Current update — 23 October 2026:** See [pre-order corrections](revisions/preorder-corrections-2026-10-23/README.md), [current purchasing list](PURCHASING-LIST.md) and [current inventory table](INVENTORY-USAGE.md). The material below describes an earlier revision; old schematic ZIPs are historical. Current working schematic PDF has been regenerated. Do not replay legacy design scripts against the current project.

# 2 x 15 W output target at 16 V

19 October 2026. Schematic revision only. Existing ICs, GPIOs, gain, output filters and component footprints retained. No PCB writes were performed by the agent.

The earlier approximately 5 W input pad and conservative PLIMIT divider were too restrictive for the requested board capability. The revised target is **15 W per channel into nominal 4 ohms at a regulated 16 V input**, subject to clipping, THD, supply and thermal measurements. This is board capability, not a universally safe driver setting.

| References | Previous | Revised | Reason |
|---|---|---|---|
| R12/R14 | 3k3 | 1k2, 1% | Increase available input level |
| R13/R15 | 1k | 1k5, 1% | Set pad attenuation with approximately matched source impedance |
| R16/R17 | 820R | Retained | Matches positive source impedance of approximately 790 ohms |
| R19 | 100k from GVDD | 10k from regulated 3V3-ESP | Filter an external PLIMIT reference without GVDD's large tolerance |
| R20 | 33k fitted | 33k DNP | Retain optional tuning footprint; remove old divider shunt |
| C29 | 1u | Retained | 10 ms PLIMIT RC filter |
| R18 | 5k6 / 20 dB gain | Retained | No higher gain required |

At 15 W into 4 ohms: 7.746 Vrms, 10.954 V peak, 1.936 Arms, 2.739 A peak. The two 1u coupling capacitors per channel remain equal. Including the DAC's 470R series resistor and nominal 50k amplifier input resistance, the new pad gain is 0.4658 (-6.64 dB). The approximate positive source resistance is 1k5 || (1k2 + 470R) = 790 ohms; retain 820R on the negative source reference. All amplifier input pins retain their internal DC bias through AC coupling.

Nominal 2.1 Vrms DAC full scale would request 9.78 Vrms / 23.9 W before limiting and clipping. This headroom accommodates the amplifier's specified 19-21 dB gain, DAC gain error (up to +/-6%) and filter/load losses. **The passive pad is not a 15 W hard cap.** A nominal initial digital ceiling is approximately -2.03 dBFS, then calibrate each channel to 7.75 Vrms across a 4-ohm dummy load at the speaker connector. Begin substantially lower. Check across the intended audio band: the LC filter attenuates high frequencies and real driver impedance differs from 4 ohms. Driver crossover, excursion and RMS/peak protection remain independent per channel; a tweeter must not receive broadband 15 W.

TI explicitly permits externally referenced PLIMIT. The existing regulated 3.3 V rail feeds R19/C29; no extra regulator/reference is needed. Its +/-1.5% reference allowance gives approximately 3.2505-3.3495 V. TI's peak virtual-rail model gives about 18.9 W unclipped nominal into 4 ohms with 0.29 ohm total bridge/winding resistance, or 18.4-19.5 W over that reference tolerance alone. With illustrative hot total series loss of 0.5 ohm the nominal estimate is 17.2 W. These estimates leave headroom above 15 W. They exclude PLIMIT transfer error, load variation and clipping distortion. TI's table/example inconsistency remains unresolved: do not claim a precise hardware watt limit. PLIMIT clips peaks; severe clipping can produce higher RMS power. DSP establishes the calibrated application limit.

At 12 V the simple rail-and-loss ceiling is only about 15.6 W before allowing supply sag, input protection drop, distortion and temperature. **2 x 15 W clean output is not guaranteed at 12 V.** Firmware should derate using VIN_SENSE and measured clipping at the lower input voltages.

At 30 W total output and assumed 85-90% amplifier efficiency, amplifier input is 33.3-35.3 W and amplifier dissipation is 3.3-5.3 W. Adding 1-3 W for radio/regulators gives approximately 34.3-38.3 W total (2.15-2.4 A at 16 V). A regulated 16 V / 3 A adapter is a sensible starting point; verify dynamic droop and fuse/inrush behavior. Existing regulators supply logic/DAC only and are unchanged.

Codaca winding current at 15 W including conservative switching ripple is about 1.97 Arms, with approximately 3.40 A peak including half the 1.33 A p-p ripple. This is below the published 3.5 A thermal rating and 6.5 A typical saturation point, but does not qualify hot fault behavior. Estimated copper loss is 0.43 W per dual package, with core loss additional. Each 680n shunt carries approximately 0.331 Arms of audio current for a 20 kHz / 15 W sine; qualify combined audio/switching ripple thermally. No output-filter changes are required by this calculation.

The ATS-TI1OP-521-C1-R1 CAD package remains available in the project library. It has not been placed or selected by this revision. Its 8.5 C/W figure is specified at 200 LFM forced airflow and must not be used as a natural-convection rating. Neither that sink nor the salvaged 20 x 18 x 10 mm sink has been qualified in the intended compartment. Verify junction-temperature margin with both channels loaded, expected ambient, mounting/interface and representative programme. Aim below 125 C; thermal shutdown is not normal control.

Inventory MCP confirmed R19's KOA RK73B2ATTD103J, quantity 100, reserved 0 (ID194); three total are required including R21/R26. No 1k2 match was returned. Owned 1k5 ID226 is 1608 metric and does not fit the retained 2012 metric footprints. Purchase two RMCF0805FT1K20 and two RMCF0805FT1K50, 1%, 125mW, 2012 metric. No inventory records changed. Evidence: inventory-power15.json. Existing BOM tables remain based on their prior inventory snapshot for unchanged components; newly user-added C56/C57 are listed as unverified rather than presumed stock. They show 1n / 1608 metric while inherited MPN C1206C104K5RACTU / ID157 identifies a different value/package; resolve this before ordering. Their source fields are preserved.

Validation: actual KiCad 10.0.5 ERC reports **0 errors, 31 warnings**, all pre-existing off-grid endpoints in the capacitor bank. The pre-revision ERC has the same warning identities; no warning exclusions added. 418 connectivity/value/package checks pass; a separate preservation record notes a concurrent external PCB save, so byte-for-byte PCB preservation across the whole turn cannot be claimed. The agent did not edit the PCB. The top-level schematic also received a concurrent external save. A fresh netlist comparison confirms the only electrical net-membership change is R19 pin 1 moving from GVDD to 3V3-ESP. Both source states contain 130 components. The plotted amplifier sheet was visually inspected.

Sources: [TI TPA3126D2 datasheet](https://www.ti.com/lit/ds/symlink/tpa3126d2.pdf), sections 6.5, 7.3.3 and 7.3.4; [TI PCM5122 datasheet](https://www.ti.com/lit/ds/symlink/pcm5122.pdf); [TI TLV1117LV](https://www.ti.com/lit/ds/symlink/tlv1117lv.pdf); [Codaca CSAD0660](https://www.codaca.com/Private/pdf/CSAD0660.pdf). Stackpole RMCF manufacturer catalog was indexed with 2012 metric / 125mW / 1% ordering data; direct manufacturer PDF retrieval redirected/failed. Recheck the current catalog and supplier stock at purchase; no successful local resistor-PDF download is claimed.

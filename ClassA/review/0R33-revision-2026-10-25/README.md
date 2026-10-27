# Yageo 0R33 ballast revision — 25 October 2026

R15, R16, R19 and R20 now specify **Yageo SQP500JB-0R33**, 0.33 ohm, 5 W, 5%. R25 changes from 3k3 to **470R**, using owned TT Electronics / Welwyn ASC0805-470RFT5, 2012 metric, 1%, 0.125 W (inventory 218: 86 available, SMD Parts). R21 remains 0R27/5 W. No new topology or pin mapping is introduced. The existing BOM JSON/CSV and schematic setup note are updated. The Yageo parts are user-selected; no inventory holding or reservation is claimed.

## Bias setting

The increased lower ballast resistance raises the effective sense coefficient from approximately 0.38 to 0.435 ohm. R25=3k3 cannot reliably reach the intended 2 A. R25=470R widens the adjustment while retaining the existing R27 open-wiper fallback.

The calculation includes the R22/R23 averaging-network load and R26/R27 paths, rather than treating RV1 as an unloaded divider. The original schematic's claimed 0.79 minimum ratio was incorrect: with 3k3 and the existing R27 path the unloaded Q10-base/sense ratio was approximately 0.875. With 470R it is approximately 0.521. At a fixed illustrative Q10 VBE=0.65 V and zero base-current load, the loaded DC network adjusts from about 1.55 to 3.02 A; 3k3 would top out around 1.79 A with the new ballasts. These are conditional network calculations, not guaranteed transistor operating points or thermal simulation. See bias-calculation.txt and the verifier for explicit assumptions/corners.

1. Start with RV1 wiper toward SENSE_AVG (minimum current), no speaker/load, and a current-limited supply. Do not retain the old trim setting after replacing resistors.
2. Adjust gradually toward approximately 330 mV across each R19/R20, corresponding to approximately 1 A per branch; confirm both branches. R21 should read approximately 540 mV at 2 A total (sensing-network current creates a small difference). Tolerances mean the actual individual drops/current will differ; use measured resistor values for precision. Do not force unequal branches to equal voltages with a common adjustment.
3. Recheck and adjust after thermal settling. The maximum setting can exceed 3 A, especially cold; maximum trim is not the target. Q10 must thermally track the sink heatsink as already specified.

At 1 A each ballast dissipates approximately 0.33 W. The output bank's signal-current peaks impose more than its idle dissipation; at roughly 2 A through an upper ballast, instantaneous dissipation is about 1.32 W. The 5 W rating has useful margin, subject to ambient-temperature derating and actual assembly conditions. Nominal idle amplifier power remains about 80 W at 40 V and 2 A.

## Footprint

Manufacturer drawing: [Yageo SQP/NSP datasheet, April 2026 V5](https://yageogroup.com/content/datasheet/asset/file/yageo-sqp_nsp_datasheet), page 3. SQP500 nominal body is 22 x 9.5 x 9 mm; maximum body 23.5 x 10.5 x 10 mm; leads 0.8 +/-0.05 mm. At this low resistance the SQP part is wirewound; it is not the non-inductive NSP series. The schematic no longer incorrectly calls these ballasts non-inductive. Their high-frequency effect still needs amplifier bench stability checks.

All four use project-local `ClassA_Inventory:Yageo_SQP500_L22.0mm_W9.5mm_P30.48mm`. Lead spacing is a selected **formed 30.48 mm pitch**, not a factory fixed pitch. Pads are 2.4 mm diameter with 1.2 mm holes; the courtyard covers the maximum body plus 0.5 mm. No polarity; pads 1 and 2 retain resistor-symbol numbering. No approximate 3D model is attached.

The closest installed standard box footprint, L25/W9, has a courtyard only 9.5 mm wide, below the Yageo's 10.5 mm maximum width. A matching local footprint avoids an undersized courtyard. The rest of the existing standard-footprint assignments are preserved. Check formed-lead fit and assembly clearance before PCB fabrication.

## Verification and scope

- Fresh ERC: **0 errors, 1 pre-existing warning**. The retained user-added L2 references `YamahaSalvage:L_Yamaha_L505_15x15mm_P12mm`, whose library is absent from the current configuration. This revision does not guess a replacement footprint or change the inductor.
- The saved baseline had again lost the Q5 collector/common-base junction. The previously authorized junction at (170.18,154.94) mm is restored; it is the only connectivity change. Reload the current schematic before saving an already-open older KiCad copy.
- `python3 scripts/verify_033_revision.py`: 105 scoped checks, including exact component/object preservation outside the specified edits, fresh netlist comparison, bias-network connectivity, footprint geometry, synchronized selected BOM rows and project/PCB/preferences hashes.
- `ClassA.pdf`, `ClassA.net`, `ERC.rpt`, `verification.txt`, `bias-calculation.txt` are the current revision artifacts. The before/ directory preserves the live user-edited starting point. Earlier verification scripts/reports describe their own historical revisions and are not current validation.
- Rendered schematic, enlarged setup note and KiCad-exported footprint preview visually checked: edited labels are readable, and body, pads and courtyard do not overlap. KiCad CLI independently reopened the saved schematic for ERC, netlist and PDF exports.
- No PCB changes, circuit simulation, bench, thermal or stability qualification performed. R21, RV1 and other existing unresolved component/package assignments remain unresolved.

R25 manufacturer specification: [TT Electronics ASC](https://www.ttelectronics.com/TTElectronics/media/ProductFiles/Datasheet/ASC.pdf).

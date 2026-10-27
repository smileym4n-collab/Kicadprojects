# PCB layout re-review — 24 October 2026

**Disposition: suitable direction for a first prototype, with three small DRC tidy-ups before releasing fabrication files.** I found no further substantial layout blocker in the current saved revision. Do not call the present board DRC-clean: it still has one active clearance error and two duplicate-via warnings. After these are corrected, refill/save, rerun DRC and generate fresh fabrication outputs.

This was a read-only review of the production files saved at approximately 11:31 on 24 October. All source hashes are preserved; see [preservation.json](preservation.json). Native GUI refill/DRC was performed only on an isolated copy. Nothing was placed, rerouted, removed or saved into the production PCB by this review.

## 1. Remaining fabrication tidy-ups

| Priority | Location | Finding | Action |
|---|---|---|---|
| Before order | DAC charge pump: F.Cu VNEG arc at **116.7450, 128.7208 mm**, near C14 pad 2 at **116.6020, 128.8315 mm** | Actual clearance **0.1980 mm**, project rule **0.2000 mm** | Move/reshape the VNEG arc slightly away from C14.2; keep a little margin rather than targeting the exact rule boundary. Recheck adjoining arc/track continuity. This is a tiny geometry correction, not a charge-pump topology problem. |
| Before order | **147.3200, 63.5000 mm** | Two identical GND vias occupy exactly the same point | Remove one duplicate, retaining one connected via. |
| Before order | **165.1000, 147.3200 mm** | Two identical GND vias occupy exactly the same point | Remove one duplicate, retaining one connected via. |

The duplicate pairs have matching 0.6 mm diameters / 0.3 mm drills and the same GND net. They are redundant objects, not a net short. These are easy pre-fabrication cleanups and should not be hidden with exclusions.

Exact native results: [GUI-DRC report](gui-drc.rpt).

## 2. U1 ground-return correction

The previous U1 power-ground concern is substantially improved and is no longer an ordering blocker in my assessment:

- Pads **22 and 28 now use solid zone connections**; their previous incomplete-thermal DRC errors disappear in a fresh zone refill/DRC.
- A local GND stitching array has been added under/near U1. Nearest GND through-via distances are now approximately **1.40 mm from pad 22, 1.89 mm from pad 25, and 1.50 mm from pad 28**, versus approximately 7.02 / 8.16 / 6.30 mm previously.
- The relevant local front copper joins the ground reference; the vias have the actual GND net. This is a physical return improvement, not just removal of a DRC marker.
- U1's footprint/library mismatch is consistent with the local ground-pad zone-connection edits. **All 32 pad geometries match the installed KiCad library footprint**, including pad types, sizes, positions, layers and shape settings. Do not replace the board footprint blindly and lose the intentional connection edits.

These vias improve switching-current return. They are not a bottom exposed-pad thermal array: the TPA3126D2 DAD package has its PowerPAD on top. TI's local decoupling/return guidance remains applicable. [TI datasheet, section 11.1](https://www.ti.com/lit/ds/symlink/tpa3126d2.pdf).

## 3. Whole-board assessment

Reviewed all four copper views and the main power, DAC and amplifier areas. The board remains **100.000 × 86.487 mm**, four layers. Routed tracks are at least **0.2 mm**; vias are **0.6 / 0.3 mm**. No outline defect is reported by native DRC.

Positive findings:

- **In1.Cu is a largely continuous GND plane**. There is no artificial analogue/digital ground split.
- DAC analogue circuitry remains separated from the buck and Class-D output section. Analogue traces have no newly discovered accidental switching-net connection.
- Buck input/boot/inductor/output placement is compact. Supply feedback remains on the quieter side of the power section.
- Amplifier ground stitching and local connections are improved. Bootstrap parts remain close to their correct output/boot pins.
- BTL output windings, shunt capacitors and post-filter RC branches retain the intended connectivity. Neither loudspeaker return is GND.
- PCM5122 **left → tweeter/J17**, **right → woofer/J16** remains consistent with the revised schematic notes. C21/JP1 remains in the tweeter positive lead, after the LC filter.
- Heatsink position/hole pitch are retained. The user's heatsink and C21 fit confirmations remain accepted; this review did not reopen those physical checks.

Previously documented first-build qualifications remain:

- U4's SOT-223 heat spreading is modest. Check its temperature and the 3.3 V rail under sustained Wi-Fi load. The 1 A IC rating is not a thermal guarantee on this PCB.
- I²S on the bottom layer has the solid In1 ground plane across the thicker core rather than an adjacent solid In2 plane. Existing source resistors help; check digital integrity/EMI on the prototype. This remains an improvement opportunity, not a demonstrated functional blocker.
- Verify the external antenna/coax arrangement of the WROVER-IE module under amplifier load and in the intended enclosure.
- Check amplifier/sink, inductor and output RC temperatures with representative programme material. Validate startup/reset/hard-off behavior and DSP channel limiting before connecting drivers.

No new substantial concern was identified in these areas that justifies another layout redesign before the first prototype. This is not an EMC, thermal, acoustic or production qualification.

## 4. Fresh consistency and ERC results

| Check | Result |
|---|---|
| KiCad 10.0.5 CLI ERC | **0 errors, 25 warnings**, all endpoint-off-grid |
| Independent schematic/PCB comparison | **360 schematic pins / 360 distinct numbered PCB pads; no missing/extra pins or net mismatches** |
| Value and assigned-footprint comparison | No differences between PCB and schematic |
| Focused functional connectivity checks | **119 pass** |
| Changes from the corrected 23 October circuit | Only **C41 and C42**, each 1u between PVDD and GND; all existing pin-net assignments retained |
| Production-file preservation | All checked files byte-for-byte unchanged during this review |

Evidence: [parity and changes](parity-and-changes.json), [connectivity checks](connectivity.json), [ERC JSON](erc.json), [source hashes](before-hashes.json).

C41/C42 are extra supply bypass capacitors in existing **3216 metric** footprints. Use **1u / 50 V X7R**, for example the owned **Samsung CL31B105KBHNFNE**. Actual MCP stock was refreshed on 24 October: **50 physical, zero reserved**. These are two additional fitted capacitors relative to the 23 October BOM; include them in assembly/BOM exports. Their saved schematic fields currently omit voltage and MPN, so do not buy unspecified low-voltage 1u ceramics from the bare value alone. The components are electrically connected to the correct supply and ground nets.

## 5. Fresh native DRC, including exceptions

CLI DRC again aborted with **exit 134** and no usable JSON report. It is not counted as a pass. The **PCB Editor GUI DRC successfully ran with “refill all zones” enabled** on the isolated snapshot.

Result: **11 findings, zero unconnected pads, zero reported footprint parity errors**. Native schematic-parity checking was not run; the independent 360-pin comparison above supplies separate consistency evidence.

Active findings:

- **1 error:** the 0.198 mm DAC clearance.
- **2 warnings:** duplicate via pairs at the coordinates in section 1.
- **1 warning:** HS1's Custom footprint was not resolved by the GUI library context. The local footprint file and board holes exist; the user's mechanical check remains accepted. This warning does not mean the heatsink holes are missing.
- **1 warning:** U1 differs from its library copy. Pad geometry has been independently checked; the local zone-connection settings are intentional.

Existing excluded findings:

- **IC2/IC3 courtyard overlap, error.** Nominal switch bodies were previously checked to have about 1.49 mm clearance; the conservative courtyard overlap is an assembly-envelope exception.
- **U2 pad 20 incomplete thermal, error.** This is SCK tied to GND for the MCLK-less DAC configuration. It has a connected spoke and is a low-current logic strap, not a power-ground return. I do not treat this as equivalent to the earlier U1 return problem. It remains an intentional exception unless tidied.
- **H1–H4 board/library footprint mismatches, four warnings.** Existing local mounting-hole definitions remain.

Ignored tests remain: missing courtyard, endpoint not centered on via, tuning-profile geometry, symbol footprint filters and component-type/pad mismatch. Existing exclusions/settings were not modified. Do not describe this as zero DRC findings.

## 6. Release decision

**After the three small active geometry/duplicate fixes and a satisfactory final DRC, I would proceed with a first prototype PCB order.** I found no other substantial schematic/layout blocker in this revision. Keep the intentional exceptions documented rather than hiding new violations.

Refill and save the final production board, regenerate Gerbers and separate PTH/NPTH drill files from that exact save, then inspect the fabricator's outline, layer order, holes and drill preview before paying. No fabrication archive or uploaded manufacturer preview was generated/approved by this review. The present design is a prototype to be measured; the previous bench startup, DSP, RF and thermal qualification tasks still apply.

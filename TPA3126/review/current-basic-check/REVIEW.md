**Historical review note:** the volume-divider finding below was subsequently resolved in the authorized volume-divider-restored revision (R39=10k, new R41=22k). Other findings in this snapshot are not automatically resolved.

# Current schematic: basic functional and channel review

22 October 2026. Review of all five current saved schematic sheets. No schematic, PCB or project settings were edited. Fresh KiCad netlist/ERC and plotted sheets were used; older reports were not treated as the current circuit.

**Verdict: the core circuit is electrically plausible, but the saved L/R assignment conflicts with the requested assignment and the volume-input change needs resolving. Do not connect the tweeter with the previous DSP channel assignment.** This is a schematic basics review, not a guarantee of operation, PCB qualification or bench validation.

## Actual audio routing

| Stage | Woofer / J16 | Tweeter / J17 |
|---|---|---|
| PCM5122 U2 output | **OUTR pin 7** | **OUTL pin 6** |
| DAC series resistor | R3, 470R | R2, 470R |
| DAC shunt capacitor | C19, 2n7 | C16, 2n7 |
| Hierarchical audio net | WOOFER_AUDIO | TWEETER_AUDIO |
| Input pad | R12 1k2 / R13 1k5 | R14 1k2 / R15 1k5 |
| Input coupling | C1 -> U1 RINP pin 4 | C6 -> U1 LINP pin 10 |
| Negative input reference | R16 / C2 -> RINN pin 5 | R17 / C5 -> LINN pin 11 |
| TPA bridge | RIGHT | LEFT |
| Positive output | U1 pin29 -> L2 pin4 -> L2 pin3 -> J16 pin1 | U1 pin23 -> L3 pin4 -> L3 pin3 -> C21 -> J17 pin1 |
| Negative output | U1 pin27 -> L2 pin1 -> L2 pin2 -> J16 pin2 | U1 pin21 -> L3 pin1 -> L3 pin2 -> J17 pin2 |

**Finding 1 — channel contract mismatch:** the agreed assignment was DAC LEFT = woofer and RIGHT = tweeter. The current saved circuit does the reverse. This originates on the DAC sheet: OUTL/R2 is labelled TWEETER_AUDIO; OUTR/R3 is labelled WOOFER_AUDIO. The amplifier sheet still maps its named woofer and tweeter inputs correctly to J16 and J17. The top-level, DAC and amplifier notes still claim the older mapping and are misleading.

Two electrically valid resolutions exist: restore OUTL -> WOOFER_AUDIO / OUTR -> TWEETER_AUDIO on the DAC sheet, preserving the original firmware contract; or intentionally retain this routing and change DSP/I2S channel assignment and all notes to LEFT=tweeter, RIGHT=woofer. Do not interchange the speaker harness alone: C21 protection belongs to J17. This review applies neither change.

**BTL polarity is correct:** positive and negative legs are consistent, the dual inductors use complete 4-3 and 1-2 windings, and neither speaker terminal is GND. The four 220n bootstraps are paired to the matching outputs: C24 pin29, C25 pin27, C26 pin23, C27 pin21. The difference between DAC channel names and amplifier bridge names is not itself an electrical fault.

## Volume input

**Finding 2 — previous ADC divider/pull-down removed:** GPIO34 / ADC1_CH6 remains the appropriate free input, and J2 pins 2=GND / 3=wiper / 4=3V3 remain connected correctly. But R39 is now **1k**, the original 22k ADC shunt is absent (reference R40 is now reused on the amplifier sheet), and C58 remains 100n to GND. This is a series RC filter, with almost no DC attenuation. Full travel reaches approximately 3.3 V, rather than the documented 2.27 V.

Because the pot is powered by the GPIO's own supply this is not inherently an overvoltage violation, but it exceeds the approximately 2.45 V upper bound of the published effective ADC measurement range at highest attenuation. The upper part of the control travel can lose useful accuracy/range. There is also no defined pull-down if the wiper wire disconnects; C58 may retain a previous reading until leakage changes it. The sheet's R39/R40/2.27 V note is now false. R39's MPN RK73B2ATTD103J still specifies 10k, conflicting with its 1k value.

Recommendation: restore the previously selected 10k R39 and 22k shunt R40 with C58, or deliberately select another divider that keeps the complete pot travel within the ADC range. Restore a defined open-wiper low state if that firmware behavior is desired. Firmware averaging, endpoint calibration, logarithmic volume mapping and independent DSP limiting remain required. No correction was applied during review.

## Other basics checked

- **Input/power:** J1 pin1 positive -> F2 -> PMOS drain; protected PMOS source feeds PVDD. Gate Zener polarity, TVS polarity and common GND are consistent. Buck feedback is 100k / 16k2, giving approximately 4.304 V nominal; SW, bootstrap and inductor connections are correct. This feeds the TLV1117LV33 ESP rail and TPS7A2033 DAC rail through the retained 2R2 RC input filter. The two 3.3 V positive rails remain distinct; all grounds share GND. No obvious power-rail short or unpowered principal IC pin was found.
- **DAC:** AVDD, CPVDD and DVDD are powered, CAPP/CAPM and VNEG capacitors connect correctly, LDOO is decoupled, and VCOM is grounded for the retained VREF configuration. MODE1 low / MODE2 high and both address pins low select I2C at 0x4C. SCK is grounded for BCK-derived PLL operation; firmware must configure that mode and suitable I2S clocks. I2C and I2S hierarchy connections reach the intended ESP pins.
- **ESP32:** proven GPIO32/33 LEDs, GPIO25 LRCK, GPIO26 BCK, GPIO13 DATA, GPIO19 SCL and GPIO21 SDA remain intact. Reserved flash/PSRAM pads remain unused. GPIO27 commands SDZ, GPIO23 commands MUTE, GPIO35 reads FAULTZ, GPIO18 drives DAC XSMT, GPIO36 senses input voltage and GPIO34 reads the pot. EN/BOOT circuitry and the separate J3 3.3 V UART connector are consistent. J3 pin4 is connected to the board 3.3 V rail; avoid powering it against an independently powered adapter output.
- **Amplifier/startup:** 20 dB gain, master 400 kHz mode, hybrid selection and all PVCC/AVCC/GND pins are consistent. SDZ has a hardware pull-down; MUTE has a pull-up; DAC XSMT has a pull-down. FAULTZ is pulled to ESP 3.3 V. R19 still filters the existing 3.3 V reference into PLIMIT; the old shunt resistor is absent. R20 is now reused as a 3R3 output-network resistor. No precise 15 W hard-limit guarantee is inferred; calibration and driver-specific DSP protection are still needed.
- **Output LC:** 10u per leg and 680n shunts remain correctly connected. The earlier switching-node snubbers have been removed. Four post-filter 10n/3R3 networks are now present and correctly wired: C54/R20 on woofer +, C32/R6 on woofer -, C60/R40 on tweeter + before C21, and C59/R34 on tweeter -. Each returns to GND through its series resistor. Their topology matches the TI EVM arrangement. Specify C0G/NP0 capacitors with at least 50 V rating and suitable resistor pulse/power ratings; values alone do not complete procurement qualification.

## Tweeter protection and part-selection findings

**C21 / JP1 topology is correct.** C21 is now an onboard 47u series capacitor in J17 positive; JP1 bridges exactly its two terminals. Keep JP1 open for tweeter protection. Close it only for intentional bypass/stereo use. The chosen two-pad test-point footprint requires an actual wire/link; it is not automatically shorted by a populated schematic symbol. Neither JP1 terminal is GND.

**C21 is not fully specified:** no MPN or voltage rating is present in the current source. It must be bipolar/non-polar for this location. If it is the previously requested Nichicon UES1H470MPM, record/verify 47u / 50V bipolar and fit in the 10 x 20 mm / 5 mm pitch envelope. Its speaker-current heating remains a bench qualification item. Old text still describes the former C54/J18 external capacitor loop (C54 is now a 10n output-network part) and should be updated to C21/JP1. The old 20 x 18 x 10 mm heatsink note also conflicts with the ATS heatsink footprint now assigned to HS1.

**Finding 3 — assembly/BOM inconsistencies:** these do not change the exported electrical nets, but can cause wrong parts to be assembled:

| References | Current discrepancy |
|---|---|
| R39 | Value 1k; MPN RK73B2ATTD103J specifies 10k |
| C28 | 1u value / 2012 metric footprint; CL31B105KBHNFNE MPN is 3216 metric |
| C30/C31/C33/C34 | 100n value / 1608 metric footprints; C1206C104K5RACTU MPN is 3216 metric |
| C56/C57 | 1n value / 1608 metric footprints; inherited C1206C104K5RACTU MPN specifies 100n / 3216 metric |
| C21 | 47u / 10 x 20 mm footprint but MPN, bipolar identity and voltage rating unspecified |
| C45 | Footprint changed to 3216 metric; retained GRM32ER71H106KA12L MPN is 3225 metric. Verify chosen 50 V part and effective capacitance or restore matching footprint. |
| C32/C54/C59/C60 and R6/R20/R34/R40 | New 10n / 3R3 networks have no exact parts specified; dielectric, voltage and resistor ratings remain to be selected. |

Select parts matching the chosen footprints and intended values before ordering. This review did not substitute parts or query new procurement stock.

The onboard D3/D4 LEDs have now been removed. J2 pin8 is the Wi-Fi LED anode drive through R8 1k from GPIO32; pin6 is the BT LED drive through R7 1k from GPIO33. J2 pins7/5 are their GND returns. These are appropriate connections for external LEDs; check physical LED polarity. J2 pins1/2 are also GND.

## Validation evidence and remaining gate

Actual KiCad 10.0.5 ERC: **0 errors, 28 warnings**, all endpoint_off_grid. A concurrent save during the review added the four output RC networks and removed onboard LEDs/test points; the final netlist, ERC and assertions were refreshed against that version. No findings were excluded or suppressed. The warnings concern off-grid endpoints; off-grid endpoints should be tidied before final schematic sign-off. ERC does not detect an L/R channel intention mismatch, excessive pot voltage for the ADC's characterized range, or MPN/package mismatches.

114 focused connectivity/pin-map assertions pass. These assert the actual saved connections and do not claim the channel contract passes. Evidence: current.xml, erc.json and checks.json. The DAC plot and refreshed amplifier plot were visually inspected in current-schematic.pdf. All five sheets loaded for export.

**Ready for further schematic correction/review; not yet ready to connect the drivers under the old DSP assumptions.** After resolving channel mapping, volume input and assembly metadata, initial tests should use a current-limited supply and dummy loads: verify all rails, boot/mute behavior, both channels with distinct test tones, speaker polarity, clipping at 16 V, pot travel and heatsink temperatures. Layout, EMI, acoustic alignment, hot/fault behavior and actual 15 W delivery were not validated here. No PCB DRC or PCB routing review was performed.

Output-network reference: [TI TPA3126D2 EVM Figure 4](https://www.ti.com/lit/pdf/slou506).

Primary references: [TI PCM5122](https://www.ti.com/lit/ds/symlink/pcm5122.pdf), [TI TPA3126D2](https://www.ti.com/lit/ds/symlink/tpa3126d2.pdf), [Espressif WROVER-E/IE module pin assignments and ADC range](https://documentation.espressif.com/esp32-wrover-e_esp32-wrover-ie_datasheet_en.pdf). Current netlist connectivity, rather than old sheet notes, determines the routing findings above.

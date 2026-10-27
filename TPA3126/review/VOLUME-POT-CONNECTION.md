> **Current update — 23 October 2026:** See [pre-order corrections](revisions/preorder-corrections-2026-10-23/README.md), [current purchasing list](PURCHASING-LIST.md) and [current inventory table](INVENTORY-USAGE.md). The material below describes an earlier revision; old schematic ZIPs are historical. Current working schematic PDF has been regenerated. Do not replay legacy design scripts against the current project.

# System connector volume potentiometer

22 October 2026. Scoped schematic change in ESP32.kicad_sch only; all other schematic sheets, PCB, project and preference files match the pre-change hashes in revisions/volume-pot/protected-hashes.json.

| J2 pin | Function |
|---|---|
| 2 | GND, potentiometer low end; existing connection retained |
| 3 | Potentiometer wiper -> R39 -> VOL-ADC -> GPIO34, module pin 6 |
| 4 | 3V3-ESP, potentiometer high end; existing connection retained |

A 10k linear potentiometer is recommended. Swapping only the two outer pot terminals reverses rotation sense. Potentiometer manufacturer's physical terminal numbering must be checked separately; J2 numbering above is authoritative for the board. The pot is a DC control input, not in the audio path. Existing LEDs and programming connector are unchanged.

GPIO34 is ADC1_CH6, input-only and previously no-connect. It is neither a strapping pin nor a flash/PSRAM reservation on the retained ESP32-WROVER-IE-N16R8. It has no internal pull-up/down. ADC1 is available while Wi-Fi runs; ADC2 is unsuitable for that role. All existing firmware GPIO assignments are retained. Firmware must add this new analogue input.

Added R39 = 10k series, R40 = 22k to GND, and C58 = 100n to GND, both shunts on the GPIO side. The ADC sees 3.3 x 22/(10+22) = 2.269 V at the high end, comfortably below the approximately 2.45 V upper end of the documented effective measurement range at highest attenuation. Using the 3.3 V rail's 1.5% allowance, R39 5% and R40 0.5%, the worst high-end estimate is 2.343 V. R40 pulls the ADC low if the wiper connection opens; this does not detect every possible harness fault. R39 limits current and isolates the cable; C58 supplies the ADC sampling charge and filters noise. With a 10k pot, the approximate RC time constant is 0.69-0.80 ms, or 2.2 ms with the wiper disconnected. The divider mildly loads the pot; firmware should calibrate endpoints and shape the volume law rather than assume an exact linear ADC response.

Firmware: use ADC1_CH6 / GPIO34 at the highest attenuation supported by the existing ESP-IDF version (historically 11 dB; naming may differ in newer APIs). Average/filter samples, provide a small deadband, calibrate the two travel endpoints, and map low/disconnected wiper to mute. Map pot position to a useful logarithmic volume law via the PCM5122 digital volume registers. Ramp volume changes; initialize muted. Retain independent per-driver DSP peak/RMS/excursion limits irrespective of the knob position. Firmware implementation is outside this schematic revision.

| Added component | MPN | Quantity required | MCP physical quantity / reserved | Purchase required |
|---|---|---:|---|---|
| R39, 10k / 5%, 2012 metric | KOA RK73B2ATTD103J | 1 additional | 100 / 0, ID194 | No |
| R40, 22k / 0.5%, 2012 metric | Susumu RR1220P-223-D | 1 | 50 / 0, ID511 | No; use owned stock |
| C58, 100n / 50V X7R, 3216 metric | Kemet C1206C104K5RACTU | 1 additional | 139 / 0, ID157 | No |

MCP queried on 22 October 2026; no inventory records were modified. Existing inventory allocations to other components still apply; these are incremental quantities, not additional inventory totals. The older RR series is selected because it is owned stock, not as a recommendation to purchase a legacy series. The 100n search field returned no match; exact MPN lookup and get_part confirmed C58. Evidence: inventory-volume-pot.json.

Validation: KiCad 10.0.5 loaded and exported all sheets. Actual ERC: **0 errors, 31 warnings**, all identical pre-existing off-grid warnings. The previous isolated VOL-ADC warning was resolved. Fresh netlist assertions confirm GPIO34 connects only to the new R39/R40/C58 node, J2 pin 3 connects only to R39, both pot outer-end nets are preserved, and every unrelated net membership is unchanged. The new footprints resolve and have matching pad numbers. The plotted ESP32 sheet was visually inspected. Detailed evidence: revisions/volume-pot/validation.json, after.xml and after-erc.json. No PCB update or routing was performed.

Layout guidance for a future authorized PCB update: put C58 beside GPIO34 with a short GND return; place R39 near the system-connector entry, keep pot wiring away from Class-D switching nodes and the RF feed, and carry a ground return alongside the wiper. Connect/disconnect the internal control harness with power off; no external overvoltage/ESD qualification is implied.

Primary references: [Espressif WROVER-E/IE datasheet, pin table and ADC characteristics](https://documentation.espressif.com/esp32-wrover-e_esp32-wrover-ie_datasheet_en.pdf), [Espressif ADC hardware guidance](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/schematic-checklist.html#adc), [KOA RK73B](https://www.koaspeer.com/pdfs/RK73B.pdf), [Susumu RR dimensions/ratings](https://www.susumu.co.jp/common/pdf/n_e_all.pdf).

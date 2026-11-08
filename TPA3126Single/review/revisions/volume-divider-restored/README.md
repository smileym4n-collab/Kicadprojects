# Volume ADC divider restored

22 October 2026. ESP32.kicad_sch only; PCB and every other production schematic/project/preference file are unchanged against before-hashes.json.

- R39: 1k -> 10k, KOA RK73B2ATTD103J, inventory ID194, existing 2012 metric footprint and UUID retained.
- R41: added 22k to GND from the GPIO side of R39. Susumu RR1220P-223-D, 0.5%, 2012 metric, matching assigned footprint.
- C58: existing 100n filter retained, with existing position and UUID.
- J2 remains 2=GND, 3=pot wiper, 4=3V3; ADC remains GPIO34 / ADC1_CH6.
- R40 is already used by the tweeter output RC network; it was not changed. The new ADC shunt is R41.
- Note updated to name R39/R41 correctly. No audio channel routing was altered.

Nominal maximum ADC voltage is 3.3 x 22/(10+22) = 2.269 V. With the previously budgeted 3.3V +/-1.5%, R39 +/-5% and R41 +/-0.5%, maximum is approximately 2.343 V. A disconnected wiper is pulled low by R41 with a nominal 2.2 ms discharge time constant through C58. A 10k linear pot is suitable. Retain maximum ADC attenuation, averaging/deadband, endpoint calibration and ramped DAC digital volume in firmware. Firmware implementation is not included.

MCP rechecked owned stock: ID194 quantity100, reserved0; ID511 quantity50, reserved0. One of each is required in this circuit. These are physical inventory totals, not additional allocations; no stock was reserved or changed. R39 now matches its existing MPN. R41 uses the owned older Susumu RR series; no purchase is needed.

Actual KiCad 10.0.5 ERC: 0 errors, 28 warnings, identical warning types/identities to the pre-change snapshot. No exclusions or No-ERC markers added. Fresh netlist assertions confirm the only new net memberships are R41.1 on VOL-ADC and R41.2 on GND; every existing connection is preserved. New footprint pads checked. The plotted ESP32 sheet was visually inspected. Evidence: after.xml, after-erc.json, validation.json and schematic.pdf.

For the user’s PCB update: change the fitted R39 value to10k, add R41=22k to GND on the GPIO side of R39, and retain C58 close to the ADC input. ADC scale and all unrelated routes still need appropriate PCB placement/DRC checks after that update.

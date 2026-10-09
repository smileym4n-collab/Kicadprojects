# Final-review controller contract — ATtiny1614, 8 October 2026

This supersedes the ATtiny412/MCP23008 contract. Firmware has NOT been implemented or bench-qualified. Audio remains analogue. Use the internal clock at 5 MHz, watchdog, and continuous brownout detection around 4.2 V. Preserve PA0/UPDI; never program its fuse as GPIO. Verify the selected BOD fuse encoding against the actual device pack.

| Function | Port | Physical pin |
|---|---|---:|
| +5R / GND | VDD / GND | 1 / 14 |
| Programmer | PA0 / UPDI | 10 |
| Inverted serial data / clock / chip select | PA1 / PA2 / PA3 | 11 / 12 / 13 |
| Reference encoder A / B | PA4 / PA5 | 2 / 3 |
| AV encoder A / B | PA6 / PA7 | 4 / 5 |
| Active-low mode request | PB3 | 6 |
| RAIL_GOOD input | PB2 | 7 |
| AV_ENABLE output | PB1 | 8 |
| RUN_REQUEST output | PB0 | 9 |

There is no I/O expander. Reset makes outputs high impedance: external pull-downs release K1–K5; K4 shorts P68 input to AMP_RETURN, and K5 grounds buffer inputs while disconnecting source signals. RUN_HW is a transistor base-drive node, not a logic output. Do not connect another digital load to it.

Serial collector pull-ups use +5A. Physical CS is high when PA3 is low. Physical data/clock are low when PA1/PA2 are high. Initialise these output latches BEFORE their direction bits. Use a 10 kHz serial clock: right byte zero followed by left byte, MSB first, data stable on physical rising clock edge; CS low for all 16 bits. Confirm with a scope. ZCEN is high.

Left codes: 0=mute; 1…191=attenuation in 0.5 dB steps; 192=unity. Reject 193…255, which request positive internal gain. Defaults after missing/invalid EEPROM: REF −30 dB (132), AV −12 dB (168). Store independent levels with version/magic/CRC and two alternating records. Save after two seconds without encoder activity. Decode full quadrature transitions; reject illegal transitions. Poll trigger and RAIL_GOOD at least every millisecond using a nonblocking state machine.

Startup, brownout or watchdog reset:

1. Set RUN_REQUEST=0 and AV_ENABLE=0 in the output latches before enabling their GPIO drivers. Set serial idle states. Write both CS bytes zero.
2. Require RAIL_GOOD continuously high for 500 ms; any fault restarts the timer. This is a collapse monitor, not a precision ±5 V compliance guarantee.
3. Read the requested mode; set AV_ENABLE. Keep RUN=0 for at least two seconds after valid rails/mode selection, allowing filter offsets and C63 to settle. CS hardware MUTE must remain asserted at least 2 ms for its calibration.
4. Check rails again, then set RUN=1. This closes K4 AND K5: the inputs connect and the output connects, but CS gain remains code0. Wait a further two seconds for input/filter settling; monitor rails throughout.
5. Ramp toward the validated stored level by at most 1 dB per 20 ms. Never jump directly to the stored value. For R38=10k commissioning gain option, revise stored calibration/default levels down 6 dB and enforce the lower input ceiling documented in the review.

Mode change:

1. Ramp down, write code0, then wait 25 ms for the CS zero-cross timeout.
2. RUN=0; wait at least 50 ms for K4/K5 release. Flyback diodes lengthen release relative to a bare-coil datasheet test.
3. Change AV_ENABLE; wait two seconds while muted. Then repeat startup steps 4–5.
4. Frequency, slope, phase bypass, polarity and HP jumpers are mechanical: change them muted until bench transients have been measured. Mode selection is AUTO (J24 1–2), forced REF (J24 open), forced AV (2–3).

Faults: any low RAIL_GOOD must immediately clear RUN_REQUEST in software. Hardware Q8/Q9 already clamps RUN_HW independently. Write code0 while supplies remain valid. Require the entire startup sequence before rearming. Never use only a fixed timer that can unmute during an active fault. J26 is an independent hard-mute shunt.

J22 accepts ONLY an open-collector/drain or isolated dry contact to local GND, with no injected voltage. An external early-power-fail signal must precede loss of valid analogue rails. K4/K5 remain mechanical devices: arbitrary instantaneous loss of either ±15 V rail cannot be guaranteed silent or free of brief input overdrive. Determine the required warning lead time by oscilloscope; start with at least 50 ms. The separate P68 speaker relay must also release before its power stage becomes uncontrolled. These system timings are mandatory commissioning items.

Test before connecting the woofer: no-firmware state; watchdog and brownout during both modes; all four sensed-rail faults; J22; J26; source present with processor off; trigger changes; serial polarity/bit order; corrupted EEPROM; each encoder; C63 charge/discharge; amplifier-first and processor-first start/stop. Use a dummy load and differential probes where needed. A grounded programmer or oscilloscope can defeat source isolation; disconnect it in normal use.

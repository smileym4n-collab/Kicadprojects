# Model provenance and limits

The installed LTspice library supplies the NXP BC546B/BC556B Gummel-Poon models copied into devices.lib with LTspice-only rating metadata removed. These are nominal models, not measurements of the stocked ST/onsemi parts or gain ranks.

Infineon datasheets were downloaded and visually checked. Public model downloads could not be obtained reliably (empty responses, 404/403); no inaccessible model was invented. The output models here are explicitly **author-created Level-1 approximations**, not manufacturer models. They approximate threshold, transconductance and lumped capacitances. BD139/BD140, BAT46 and Zener models are also engineering approximations. The BAT46 model uses 10 pF zero-bias capacitance and approximate low-current forward behaviour; leakage and temperature characteristics are not qualified. Thus numerical distortion, clipping, phase margin and temperature results are development evidence only. They do not validate the final hardware or justify final PCB release. Replace with verified manufacturer models and repeat, then measure the actual prototype.

The approximate MOSFETs do not model subthreshold detail, nonlinear gate charge accurately, die temperature, hotspots, SOA, secondary breakdown, self-heating, avalanche energy or production spread. MOSFET temperature sensitivity is separately imposed through VTON/VTOP and KPN/KPP; explicit TEMP=27 prevents double counting. Sensor/driver temperatures can be varied independently. Global `.temp` is not a substitute for this imposed mismatch study.

Typical gate capacitances are represented by fixed Cgs/Cgd and nonlinear body diode Cjo. This is insufficient to certify HF stability. Selected device lead/PCB inductance, source-resistor inductance, bypass ESL and bulk ESR are tested separately in supplement.py. They are assumed values, not extracted parasitics. This does not replace nonlinear manufacturer models or bench testing.

## Infineon manufacturer models (added 25 Oct 2026)

`infineon/irf540n.spi` and `infineon/irf9540npbf.spi` are genuine Infineon (Symmetry MODPEX "POWER MOS Model v1.0", SPICE3) subcircuits, downloaded from the Infineon "Power MOSFET simulation models" page assets:

| File | Source URL | SHA-256 (as downloaded) | Generated |
|---|---|---|---|
| irf540n.spi | https://www.infineon.com/assets/row/public/documents/24/50/irf540n.spi | 9d368875d0a3a3185827e83dde737e7fcd6b75947fd3bde36df497d1548c7e65 (CRLF; stored here with LF) | 5 Sep 2001 |
| irf9540npbf.spi | https://www.infineon.com/assets/row/public/documents/24/50/infineon-spice-file-irf9540npbf-sm-en.spi | 65d0a5551f452f6ad35322f19f120041244bcdee1c1d9b6ea3a20b7c0761669e | 15 Aug 2017 |
| irf540n.sin | https://www.infineon.com/assets/row/public/documents/24/50/irf540n.sin | 4ef3a201d48cce6718713ac004f4ce25bdb7fcc981bfff994c8cb81c695de9d9 | Saber format, kept for reference, not used |

Pin order is 1 = drain, 2 = gate, 3 = source in both, the same as the authored subcircuits. Both models are Level-1 cores (N: VTO 3.582 V, KP 112.25 A/V²; P: VTO −3.740 V, KP 6.905 A/V²) with series resistances, body diode and a nonlinear Cgd network. They are fitted to typical high-current data. They do **not** model threshold temperature coefficient, subthreshold conduction, production spread, hot linear SOA or self-heating; the irf540n.spi thermal RC subcircuit is a separate whole-die Zth network and is not connected. Their use is subject to Infineon's model terms of use. In `bias_study.py` and `bias_dynamic.py`, temperature behaviour is still imposed (threshold slope through a gate series source, KP scaled by T^−1.5); the authored models remain in `devices.lib` for comparison with the earlier results.

## Rev 0.2 model files

- `mosfets_infineon.lib` (default) holds the two Infineon subcircuits renamed MOSN/MOSP, with KP multiplied by `{KPS}`. Nothing else is changed.
- `mosfets_authored.lib` holds the Rev 0.1 authored approximations renamed MOSN/MOSP with the same interface. Select them with `MOSFET_MODELS=authored`.
- In both, threshold spread and temperature are applied by gate series sources `VTHN`/`VTHP` (parameters `DVN`/`DVP`) in `channel.cir`. These are simulation-only zero-volt sources; the netlist verifier treats GNI/GPI as GN/GP.
- `devices.lib` adds `LEDR`, an author-created red-LED approximation for the bias reference D113: about 1.85 V at 1 mA, dVf/dT about −1.8 mV/K, set by `LEDEG` (2.3). It is not a Kingbright model, and real red-LED slopes vary; −1.5 to −2.5 mV/K is tested in `supplement.py`.
- The BD139 model has XTB = 0, so its current gain does not vary with temperature. The Rev 0.2 bias network is more sensitive to Q108 β than Rev 0.1 (see `docs/DESIGN.md`).

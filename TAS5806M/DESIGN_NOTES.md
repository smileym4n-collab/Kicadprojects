# TAS5806M 1S Bluetooth Soundbar — Design Notes (Rev A)

Generated 2026-10-19 alongside the KiCad schematic in this folder.

**Status:** the schematic is drawn and its electrical rules check (ERC) is clean. The netlist was exported with kicad-cli and compared pin by pin with the design: 459 pins, 0 mismatches. Every symbol pin maps to a pad on its footprint.
**Not done:** no simulation, no PCB, no bench test, no thermal test. The boost loop compensation and Class-D filter come from calculation only.

## Contents
1. Files and sheet structure
2. Architecture and power tree
3. Engineering calculations
4. Pin assignments
5. Startup / shutdown state machine
6. BQ25895 configuration
7. TAS5806M configuration / register strategy
8. ATtiny412 power-controller firmware specification
9. PCB layout guidance (4-layer, 70 x 100 mm max)
10. BOM, stock and purchases
11. Decisions taken, deviations and unresolved items
12. Remaining risks
13. Pre-fabrication electrical review checklist
14. Safe first power-up test plan

---

## 1. Files and sheet structure

| File | Content |
|---|---|
| `TAS5806M.kicad_sch` | Root sheet: six sheet blocks, rail summary |
| `USB_Charger.kicad_sch` | J101 USB-C, D101 TVS1400, U102 TPD2E2U06, U101 BQ25895, J102 battery, F101, J103 NTC |
| `PVDD_Boost.kicad_sch` | U201 TPS61088-Q1, VSYS -> PVDD 9.3 V |
| `3V3_BuckBoost.kicad_sch` | U301 ISL91127IRAZ, VSYS -> +3V3 (switched) |
| `Power_Control.kicad_sch` | U401 TPS7A2033 (+3V3_AON), U402 ATtiny412, SW401 encoder, J401 UPDI |
| `ESP32.kicad_sch` | U501 ESP32-WROOM-32UE-N8R2, reset/boot, J501 programming, I2C pull-ups |
| `Amplifier.kicad_sch` | U601 TAS5806M, L601/L602 CSAD0660-100M, output caps, J601/J602 speakers |
| `Soundbar.kicad_sym` / `Soundbar.pretty` | Project library: custom symbols built from datasheet pin tables; footprints copied from your `Custom.pretty` (CSAD0660-100M, ESP32WROOM32UEN8R2, TS026650BK100SCRD) |
| `sym-lib-table`, `fp-lib-table` | Project library tables (`${KIPRJMOD}`) |
| `TAS5806M-BOM.csv` | Grouped BOM with manufacturer, MPN, stock/inventory id, notes |

Reference designators are numbered by sheet: 1xx charger, 2xx boost, 3xx 3V3, 4xx power control, 5xx ESP32, 6xx amplifier.
Signals between sheets use global labels. Rails use power symbols: `VBUS`, `VSYS`, `VBAT`, `PVDD`, `+3V3`, `+3V3_AON` and `GND`.
There is one GND net: no separate analogue/digital/power grounds.

## 2. Architecture and power tree

```
USB-C 5 V --TVS1400--> BQ25895 VBUS --(buck 1.5 MHz, power-path)--> VSYS 3.0-4.4 V
                                       |                               |-- TPS61088-Q1 boost (EN = ESP32 BOOST_EN) --> PVDD 9.3 V --> TAS5806M
1S 9 Ah cell --KK-396--F101 8 A--> VBAT --BATFET (11 mOhm)-------------|-- ISL91127 buck-boost (EN = ATtiny EN_3V3) --> +3V3 --> ESP32, TAS DVDD
                                                                       |-- TPS7A2033 LDO (always on) --> +3V3_AON --> ATtiny412
```

- **OFF state:** these stay powered: BQ25895 (BATFET on), TPS7A2033 and the ATtiny412 in power-down. Everything else is disabled.
  - TPS61088 EN is low, so PVDD sits at VSYS minus the body diode (the TPS61088 has no output disconnect).
  - TAS5806M PDN is low (shutdown, about 7 µA from PVDD).
  - ISL91127 is disabled (0.05 µA), so the ESP32 is unpowered.
- **Domains and back-feeding:**
  - The ESP32, TAS5806M, I²C pull-ups and encoder pull-ups are all on the switched +3V3 rail, so none of them can feed current into an unpowered part.
  - The ATtiny is on +3V3_AON. Its links to the ESP32 are a UART (PC_TX/PC_RX), each with a 1k series resistor.
    - The ATtiny drives its TX low whenever EN_3V3 is low (firmware rule).
    - PC_RX has a 100k pull-down on the ATtiny side.
  - BQ25895 INT (open-drain) goes only to the ATtiny, pulled up to +3V3_AON.
  - The ESP32 reads charger status over I²C instead.

## 3. Engineering calculations

All numbers come from `calc.py` (scratch), using datasheet equations. Sources: TAS5806M SLASEP9, TPS61088-Q1 SLVSE52A, BQ25895 SLUSC88C, ISL91127IR FN8859, the CSAD0660 datasheet, and the Peerless .sdrv file in Downloads.

### 3.1 Amplifier, speaker and PVDD choice
Driver (Peerless TA6FD00-04 .sdrv file): Re = 3.5 ohm, Le = 35 uH, Pe = 10 W, Xmax = 2.1 mm, Fs = 170 Hz.

| PVDD (V) | Vpk max into 4 ohm (V) | P_max theor. (W) | est. P @1% THD (W) | headroom over 5 W (dB) | > Pe 10 W? |
|---|---|---|---|---|---|
| 8.0 | 7.18 | 6.5 | 5.8 | 0.6 | no |
| 9.0 | 8.08 | 8.2 | 7.3 | 1.7 | no |
| 9.3 | 8.35 | 8.7 | 7.8 | 2.0 | no |
| 10.0 | 8.98 | 10.1 | 9.1 | 2.6 | no |
| 12.0 | 10.78 | 14.5 | 13.1 | 4.2 | yes |

TI Figure 19 (4 ohm, 1SPW, 4.7 uH+0.68 uF) reads ~6.3 W @1% at 8.5 V and ~9.5 W at 10.5 V, consistent with the table.
Chosen PVDD = 1.204 V x (1 + 316k/47k) = **9.30 V** (stocked 1% resistors).
5 W into 4 ohm: 4.47 Vrms, 6.32 Vpk, 1.12 Arms, 1.58 Apk.  Into Re = 3.5 ohm (impedance minimum): 1.81 Apk.
PVDD input power at 2 x 5 W continuous sine (eta_amp ~ 0.85 from TI Fig.22/23): **11.8 W** -> I_PVDD = 1.27 A.
TAS5806M dissipation 1.76 W -> dTj = 51 C with RthJA 29.0 C/W.
TAS5806M dissipation 1.76 W -> dTj = 42 C with RthJA 23.6 C/W.

Analog gain: 0 dBFS = 29.5 Vpk at AGAIN 0 dB. Rail-limited peak into 4 ohm ~ 8.4 V, so AGAIN = 0x15 (-10.5 dB -> 8.81 Vpk at 0 dBFS) places digital full scale just above the clip point: the whole digital range is usable and the idle noise is scaled down by the same 10.5 dB versus the 0 dB setting. 5 W (6.32 Vpk) then sits at -2.9 dBFS - this is the ESP32 limiter ceiling.

### 3.2 Output LC filter (per BTL channel)
Per leg: 10 uH + 0.68 uF to GND -> f0 = 61.0 kHz.  Differential equivalent: 20 uH, 0.34 uF.
Characteristic impedance 7.67 ohm; Q into 4 ohm = 0.52, into 8 ohm = 1.04.

| f (Hz) | |H| 4 ohm resistive (dB) | |H| driver model Re+Le (dB) | |H| open (dB) |
|---|---|---|---|
| 1000 | -0.20 | -0.25 | 0.00 |
| 10000 | -0.39 | -1.44 | 0.24 |
| 15000 | -0.62 | -1.96 | 0.54 |
| 20000 | -0.93 | -2.15 | 0.99 |
| 40000 | -2.91 | -0.71 | 4.87 |
| 61000 | -5.71 | 5.08 | 38.20 |
| 384000 | -32.13 | -31.60 | -31.73 |
| 768000 | -44.04 | -43.91 | -43.94 |

TI Table 53: <=12 V, 384 kHz, 1SPW/Hybrid needs >= 10 uH + 0.68 uF; at 768 kHz minimum is 384/768 x 10 = 5 uH. 10 uH satisfies both. Idle ripple (1SPW/Hybrid ~14% duty, 384 kHz): 0.29 App per leg.
Fsw 384 kHz: power-up peak (TI eq.1, theta=0.14) 0.34 A; clipping burst peak (TI eq.2) 2.42 A.
Fsw 768 kHz: power-up peak (TI eq.1, theta=0.14) 0.17 A; clipping burst peak (TI eq.2) 1.21 A.
Peak output current at an unlimited 8 W into 4 ohm: 2.83 A; into Re 3.5: 2.14 A. CSAD0660-100M: L(2 A) ~ 10.0 uH (curve), L(4 A) ~ 9.3 uH (>80% of 10 uH), Isat(-30%) 6.5 A, Irms 3.5 A; 5 W sine -> 1.2 Arms, copper loss 2 x 1.2^2 x 0.047 = 135 mW per channel.

### 3.3 TPS61088-Q1 boost (VSYS -> PVDD)
RFREQ 270k: fsw at VIN 3.0 V = 547 kHz
RFREQ 270k: fsw at VIN 3.6 V = 561 kHz
RFREQ 270k: fsw at VIN 4.2 V = 572 kHz

| case | VIN (V) | IOUT (A) | eta | IIN avg (A) | ripple pp (A, L-20%) | I_L peak (A) |
|---|---|---|---|---|---|---|
| 2x5 W sine, limiter on | 3.0 | 1.27 | 0.87 | 4.52 | 2.06 | 5.55 |
| 2x5 W sine, limiter on | 3.3 | 1.27 | 0.88 | 4.07 | 2.16 | 5.14 |
| 2x5 W sine, limiter on | 3.7 | 1.27 | 0.90 | 3.55 | 2.26 | 4.67 |
| 2x5 W sine, limiter on | 4.2 | 1.27 | 0.91 | 3.09 | 2.33 | 4.26 |
| limiter off, 2x8 W clip | 3.0 | 2.20 | 0.87 | 7.84 | 2.06 | 8.87 |
| limiter off, 2x8 W clip | 3.3 | 2.20 | 0.88 | 7.04 | 2.16 | 8.12 |
| limiter off, 2x8 W clip | 3.7 | 2.20 | 0.90 | 6.14 | 2.26 | 7.27 |
| limiter off, 2x8 W clip | 4.2 | 2.20 | 0.91 | 5.35 | 2.33 | 6.52 |
| idle hybrid | 3.0 | 0.03 | 0.87 | 0.09 | 2.06 | 1.12 |
| idle hybrid | 3.3 | 0.03 | 0.88 | 0.08 | 2.16 | 1.16 |
| idle hybrid | 3.7 | 0.03 | 0.90 | 0.07 | 2.26 | 1.20 |
| idle hybrid | 4.2 | 0.03 | 0.91 | 0.06 | 2.33 | 1.23 |

RILIM 68k (MODE floating = PFM, TI eq.3): ILIM typ = 8.09 A, worst-case min ~ 6.59 A (typ - 1.5 A), est. max ~ 9.2 A. 2 x 5 W at 3.0 V needs ~5.7 A peak -> OK; the limit caps unlimited overdrive at low battery.
If MODE is strapped to GND (FPWM, R205 fitted) the limit becomes 550000/R - 1.6 = 6.49 A typ: change RILIM to 56k.
Inductor Coilcraft XAL7030-222ME: 2.2 uH +/-20%, DCR 15.07 mOhm max, Isat 18 A, Irms 10 A (20 C rise) >> ILIM max; copper loss at 4.5 A avg = 0.31 W.
Soft start CSS 33 nF: tss = 1.204 x 33n / 5 uA = 7.9 ms; inrush to charge 270 uF by 5.8 V in tss: 0.20 A.
FB divider current 1.204/47k = 25.6 uA (>= 20 uA recommended).

Compensation (TI eq.18-20, output = 51 uF ceramic eff. || 220 uF/ESR 70 mOhm electrolytic): R5 = 100k, C5 = 10 nF, C8 chosen by numeric loop sweep below.

| VIN (V) | IOUT (A) | C8 | fc (kHz) | phase margin (deg) | gain margin (dB) |
|---|---|---|---|---|---|
| 3.0 | 1.27 | open | 7 | 110 | >40 |
| 3.0 | 2.20 | open | 7 | 106 | >40 |
| 3.6 | 1.27 | open | 9.23 | 116 | >40 |
| 3.6 | 2.20 | open | 9.33 | 112 | >40 |
| 4.2 | 1.27 | open | 12.4 | 121 | >40 |
| 4.2 | 2.20 | open | 12.4 | 117 | >40 |
| 3.0 | 1.27 | 47p | 6.76 | 98 | 13 |
| 3.0 | 2.20 | 47p | 6.76 | 94 | 8 |
| 3.6 | 1.27 | 47p | 8.71 | 101 | 14 |
| 3.6 | 2.20 | 47p | 8.71 | 97 | 10 |
| 4.2 | 1.27 | 47p | 11.1 | 102 | 15 |
| 4.2 | 2.20 | 47p | 11.1 | 98 | 11 |

Worst-case phase margin over VIN 3.0-4.2 V, IOUT 0.3-2.2 A is best with C8 = open (106 deg). Model limits: REA, ESL and capacitor DC-bias tolerance are not modelled - **verify with a load-step test on the bench** (0.2 -> 1.5 A, look for <= 1 overshoot ring).

### 3.4 Battery current and system budget
3V3 rail average while playing: ESP32 BT A2DP ~120 mA (bursts to ~500 mA), TAS DVDD 18 mA, misc 10 mA = 148 mA.

| condition | P_PVDD (W) | P_3V3 (W) | battery current at 3.0 / 3.3 / 3.7 / 4.2 V (A) |
|---|---|---|---|
| idle, hybrid mod. | 0.19 | 0.49 | 0.25 / 0.23 / 0.20 / 0.18 |
| typical music ~0.5 W/ch avg | 1.25 | 0.49 | 0.66 / 0.59 / 0.52 / 0.46 |
| 2 x 5 W continuous sine | 11.76 | 0.49 | 4.69 / 4.22 / 3.68 / 3.21 |

Cell energy ~33 Wh (9 Ah x 3.7 V). Runtime: idle (connected, silent) ~44 h; typical music ~17 h; continuous 2 x 5 W sine ~2.4 h.
BQ25895 BATFET: 6 A continuous / 9 A peak (1 s), 11 mOhm -> worst continuous case 4.7 A at 3.0 V is within rating; fuse 0451008.MRL (8 A, 7.7 mOhm).

### 3.5 BQ25895 charger
RILIM = 150 ohm: input-current ceiling 2.37 A typ (2.13 - 2.60 A over KILIM tolerance).
Charging 1.0 A at 4.2 V needs ~4.6 W in -> 0.91 A from 5 V.
Charging 1.5 A at 4.2 V needs ~6.8 W in -> 1.37 A from 5 V.
USB budget at 5 V: 3 A source = 15 W, 1.5 A source = 7.5 W, default = 2.5 W (500 mA). With playback + 1.5 A charge the BQ25895 prioritises SYS; charge current is reduced automatically (input DPM) and the battery supplements SYS when the load exceeds the input limit (supplement mode, BATFET ideal-diode).
TS cold (LTF 73.25%) -> 1.0 C
TS hot start (HTF 48.25%) -> 39.7 C
TS cut-off (TCO 44.75%) -> 44.5 C
NTC open: TS = RT2/(RT1+RT2) = 85.2% > 73.25% -> "cold" -> charging suspended (fail-safe). NTC shorted: TS = 0 -> "hot" -> suspended.

### 3.6 3.3 V rails
ISL91127IRAZ: VOUT = 0.8 x (1 + 1M/316k) = 3.332 V (FB 0.783-0.813 V -> 3.26-3.39 V). Inductor XFL4020-102ME 1 uH, Isat 4.5 A(-10%) vs 4.5 A switch limit. Output 2 x 22 uF.
ISL91127 at 0.5 A burst, VIN 3.0 V: eta ~ 92% -> 0.6 A from VSYS. Shutdown IQ 0.05 uA typ.
AON LDO TPS7A2033: IQ 6.5 uA typ; ATtiny412 power-down 0.1 uA typ (2 uA max at 25 C).

### 3.7 OFF-state budget (no USB, battery connected)
| item | typ (uA) | max (uA) |
|---|---|---|
| BQ25895 IBAT, BATFET on, HiZ, monitor off | 32.00 | 60.0 |
| TPS7A2033 IQ | 6.50 | 10.0 |
| ATtiny412 power-down (+WDT/BOD off) | 0.10 | 2.0 |
| pull-ups (BTN 100k idle, INT idle) | 0.00 | 0.1 |
| TPS61088 shutdown (EN low) VIN pin | 1.00 | 3.5 |
| TAS5806M PVDD shutdown (PDN low) | 7.20 | 10.0 |
| ISL91127 shutdown | 0.05 | 1.0 |
| 1N4148W / misc leakage | 0.10 | 1.0 |
| **total** | **47.0** | **87.6** |

9000 mAh / 47 uA = 22 years (typ) - self-discharge of the cell (~2-3 %/month) dominates. Ship mode (BATFET_DIS) reduces the BQ25895 draw to 12 uA typ and removes everything else.


### 3.8 PVDD choice: why 9.3 V
- 9.3 V gives 2 x 5 W with about 2 dB of headroom to clipping.
- The rail-limited maximum, about 7.8 W at 1 % THD+N, stays **below the driver's 10 W Pe**. The speakers are protected by the hardware even if the firmware limiter fails. At 12 V that limit would be about 13 W, above Pe.
- Lower PVDD also means lower Class-D switching loss and idle current, and a lower boost ratio, which gives better efficiency at low battery.
- The 316k/47k divider uses stocked 1 % resistors. Use 360k/56k to get 8.94 V if you prefer to sit nearer 9 V; the headroom drops to about 1.7 dB.
- **Distortion at 5 W:** read from the datasheet curves only (Fig. 11–19). At 1 W it is ≤ 0.03 %. At 5 W it is roughly 0.05–0.2 %, and the 1 % THD+N point is about 7.8 W. Bench measurement is required.

## 4. Pin assignments

### ESP32-WROOM-32UE-N8R2 (U501)
| Module pin | GPIO | Net | Dir | Notes |
|---|---|---|---|---|
| 3 | EN | ESP_EN | in | 10k/1u RC, RESET switch, J501-5 |
| 4 | GPIO36 (ADC1_CH0) | CC1_SENSE | in | USB-C CC1 voltage via 100k (10n reservoir) |
| 5 | GPIO39 (ADC1_CH3) | CC2_SENSE | in | CC2 |
| 6 | GPIO34 | ENC_A | in | external 10k pull-up + 10k/10n RC; use PCNT |
| 7 | GPIO35 | ENC_B | in | as above |
| 8 | GPIO32 | PC_TX | in (UART RX) | from ATtiny TXD, 115200 8N1 |
| 9 | GPIO33 | PC_RX | out (UART TX) | to ATtiny RXD |
| 10 | GPIO25 | I2S_LRCLK | out | 22R series |
| 11 | GPIO26 | I2S_BCLK | out | 22R series, 3.072 MHz |
| 12 | GPIO27 | I2S_DOUT | out | 22R series |
| 13 | GPIO14 | TP501 | – | spare/debug |
| 14 | GPIO12 | NC | – | strap: must be low at boot |
| 16 | GPIO13 | status LED (green, 1k) | out | |
| 23/24 | GPIO15/GPIO2 | NC | – | straps |
| 25 | GPIO0 | ESP_IO0 | in | BOOT switch, J501-6 |
| 26 | GPIO4 | BOOST_EN | out | 100k pull-down at TPS61088 |
| 27 | GPIO16 | 10k pull-up | – | PSRAM CS on N8R2 — never use |
| 28 | GPIO17 | TP502 | – | spare |
| 29 | GPIO5 | NC | – | strap |
| 30 | GPIO18 | AMP_FAULT_N | in | TAS5806M ADR/FAULT (after re-mapping) |
| 31 | GPIO19 | TP503 | – | spare |
| 33 | GPIO21 | I2C_SDA | bidir | 4k7 to +3V3 |
| 34/35 | RXD0/TXD0 | ESP_RXD0/TXD0 | – | J501 |
| 36 | GPIO22 | I2C_SCL | out | 4k7 to +3V3 |
| 37 | GPIO23 | AMP_PDN | out | 100k pull-down at TAS5806M |

ADC1 pins are used for CC sensing because ADC2 is unavailable while Bluetooth is running.

### ATtiny412-SS (U402)
| Pin | Port | Net | Function |
|---|---|---|---|
| 1 | VDD | +3V3_AON | 100n local |
| 2 | PA6 | PC_TX (via R403 1k) | USART0 TXD -> ESP32 |
| 3 | PA7 | PC_RX (via R404 1k, R405 100k pull-down) | USART0 RXD <- ESP32 |
| 4 | PA1 | EN_3V3 | ISL91127 enable (R302 100k pull-down) |
| 5 | PA2 | CHG_INT_N | BQ25895 INT, 10k pull-up; **fully asynchronous pin** — wakes from power-down on the 256 µs pulse |
| 6 | PA0 | UPDI | J401 |
| 7 | PA3 | BTN_N | 100k pull-up, D401 to BTN_RAW_N |
| 8 | GND | GND | |

### I²C bus (400 kHz, 4k7 pull-ups to +3V3)
| Device | 7-bit address |
|---|---|
| BQ25895 | 0x6A |
| TAS5806M (ADR 15k to DVDD) | 0x2D (8-bit write 0x5A) |

### Button node (BTN_RAW_N)
Encoder switch S1 to GND. The node connects directly to BQ25895 /QON (internal 200k pull-up to BAT) and to ATtiny PA3 through D401.
- Holding the button ≥ 1.25–2.25 s exits BQ ship mode.
- Holding ≥ 12–18 s with no VBUS gives a BQ25895 full system power cycle (BATFET_RST_EN default = 1). This is the hardware recovery path for a hung ATtiny.

## 5. Startup / shutdown state machine

```
            +-----------+  short press (50 ms..1.5 s, act on release)
   reset -->|  OFF      |------------------------------------------+
   (POR,    | ATtiny    |  CHG_INT edge & rate-limit OK             |
   BOD,WDT) | power-down|--------------------+                      |
            +-----------+                    v                      v
                 ^                    +-------------+       +---------------+
                 |  done/timeout 10 s | SERVICE     |       | BOOTING       |
                 +--------------------| EN_3V3 = 1  |       | EN_3V3 = 1    |
                 |                    | ESP: config |       | wait HELLO    |
                 |                    | BQ, no amp  |       | (timeout 5 s) |
                 |                    +-------------+       +-------+-------+
                 |                                                  | HELLO
                 |                                                  v
                 |   PWROFF_ACK or 8 s timeout              +---------------+
                 +------------------------------------------| RUN           |<-+
                 |                                          | heartbeat 500 ms |
                 |   +------------------+  hold >= 2 s       | (timeout 3 s)    |
                 +---| SHUTDOWN_REQ     |<------------------+---------------+
                     | ESP: soft mute,  |                      | heartbeat lost
                     | HiZ, PDN low,    |                      v
                     | BOOST_EN low,    |               +----------------+
                     | save NVS, BQ cfg |               | FAULT RECOVERY |
                     +------------------+               | EN_3V3 = 0 1 s |
                                                        | retry x3, then |
                                                        | OFF (latched)  |
                                                        +----------------+
```

**Power-on sequence (ESP32 firmware, in order):**
1. Boot. Send `HELLO` to the ATtiny.
2. Read the BQ25895 fault/status registers and apply the charger configuration (§6).
3. Keep AMP_PDN = 0 and BOOST_EN = 0. Check VBAT ≥ 3.3 V (BQ ADC). If VBAT is lower, show low-battery and request power-off.
4. Set BOOST_EN = 1. Wait 20 ms (soft start about 8 ms).
5. Set AMP_PDN = 1. Wait ≥ 5 ms (TI 9.5.3.1).
6. Start I²S BCLK/LRCLK, sending zeros.
7. Write register 0x03 = 0x02 (Hi-Z, DIS_DSP = 0 so the DSP starts).
8. Wait ≥ 5 ms. Write the configuration (§7) with volume muted. Write 0x03 = 0x03 (Play). Ramp the volume to the saved level.
9. Start the A2DP sink.

**Power-off (long press, low battery, or idle timeout):**
1. Ramp the digital volume down / set MUTE (0x03 bit 3).
2. Wait ≥ 6 ms (TI Fig. 69). Write 0x03 = 0x02 (Hi-Z).
3. Set AMP_PDN = 0, then BOOST_EN = 0.
4. Stop I²S. Save state to NVS.
5. Make sure the BQ watchdog is disabled and the charge settings are written.
6. Send `PWROFF_ACK`. The ATtiny then sets EN_3V3 = 0.

**Low-battery policy (ESP32):**
- Under load: limit volume below 3.4 V and shut down at 3.3 V.
- At rest: shut down at 3.2 V.
- Below 3.1 V at shutdown, set BATFET_DIS with BATFET_DLY = 1 (ship mode, 12 µA). Exit by plugging in USB or holding the button for about 2 s.

**Startup scenarios checked**

| Scenario | Behaviour |
|---|---|
| Battery only, button press | Normal sequence above. |
| USB inserted with the system OFF | BQ powers SYS from VBUS and charges with its current registers (defaults after POR: ICHG 2048 mA, IINLIM from BC1.2 detection, capped by ILIM at about 2.37 A). The INT pulse wakes the ATtiny, which runs a SERVICE boot so the ESP32 can read CC1/CC2, set IINLIM/ICHG, disable HVDCP and the watchdog, and power off again (≤ 2 s). |
| USB inserted while playing | ESP32 receives CHG_INT (relayed over UART) and re-applies IINLIM from the CC reading. Audio load above the input limit is supplemented by the battery (BATFET ideal diode). |
| Deeply discharged cell (< 3.0 V) | BQ pre-charges at 128 mA (2.2–3.0 V) or 100 mA (< 2.2 V). SYS is held at SYS_MIN 3.5 V from USB, so the ESP32 can run. Firmware must not enable the amplifier until VBAT > 3.4 V — there is no battery to supplement peaks. |
| No battery, USB only | BQ supports instant-on without a battery. TS reads "cold" (no NTC), so charging stays disabled. The system runs but is limited by IINLIM. Treat as bench mode: amplifier disabled or volume-capped by firmware. |
| Battery reversed | Not protected (see §11). The BQ25895 BAT pin and F101 would conduct through internal diodes; F101 should clear. **Check polarity before mating.** |

## 6. BQ25895 configuration (ESP32 writes these at every boot and SERVICE boot)

| Reg | Value | Meaning |
|---|---|---|
| REG02 | 0x71 (run) / 0x31 (service, off) | CONV_RATE = 1 (1 s continuous ADC) while running, BOOST_FREQ default, ICO on, **HVDCP_EN = 0, MAXC_EN = 0** (stays 5 V), AUTO_DPDM on. 0x31 = one-shot ADC. |
| REG00 | IINLIM from CC | EN_ILIM (bit 6) stays 1. CC voltage < 0.66 V -> USB default -> 500 mA (0x48). 0.66–1.23 V -> 1.5 A (0x5C). > 1.23 V -> 3.0 A (0x7A). Silicon is further capped by ILIM (2.37 A typ). Keep EN_ILIM = 1. Re-write after each D+/D- detection (IINLIM is overwritten by detection). |
| REG03 | 0x1A | OTG_CONFIG = 0 (belt and braces — the OTG pin is already tied low), CHG_CONFIG = 1, SYS_MIN 3.5 V |
| REG04 | 0x17 | ICHG 1472 mA (≈ 1.5 A). Use 0x10 for 1.0 A. |
| REG05 | 0x13 | IPRECHG 128 mA, ITERM 256 mA |
| REG06 | 0x5E | VREG 4.208 V (4.2 V cell), BATLOWV 3.0 V, VRECHG 100 mV |
| REG07 | 0x8D | EN_TERM, STAT on, **WATCHDOG disabled (00)**, safety timer on, 12 h |
| REG08 | 0x03 | No IR compensation, TREG 120 °C |
| REG09 | 0x44 | BATFET_RST_EN = 1 (keep the /QON hardware reset); BATFET_DIS only for ship mode |

- **Watchdog rationale:** if the watchdog expired it would restore the defaults, which charge at 2.048 A. That is still only 0.23 C for the 9 Ah cell and is limited by ILIM, so neither state is unsafe. Disabling the watchdog keeps the chosen 1.5 A.
- **Persistence:** register values survive until POR (battery removal) or REG_RST. Re-apply them at every boot.
- **CC thresholds:** measured at a 5.1k Rd (Type-C spec): Default 0.25–0.61 V, 1.5 A 0.70–1.16 V, 3.0 A 1.31–2.04 V. The ADC reads through 100k, so sample slowly with the 10n reservoir; the error is negligible. Use the higher of CC1/CC2 because only one is active.

## 7. TAS5806M configuration / register strategy

- **Clocking:** I²S Philips, 32-bit slots (64 fs), 48 kHz, no MCLK. 3-wire mode, PLL locked to SCLK (datasheet 9.3.2).
- **Base settings (Book 0, Page 0):**
  - `0x02 = 0x12`: FSW 384 kHz + Hybrid modulation (lowest idle current). Alternative: `0x02 = 0x01` (768 kHz, 1SPW).
    - Hybrid needs the PVDD value entered in PPC3 and the PPC3-generated coefficient set. If you are not using PPC3, use 1SPW at 768 kHz with `0x53 = 0x60` (175 kHz loop bandwidth).
    - At 384 kHz, `0x53` must select ≤ 120 kHz bandwidth: `0x53 = 0x40`.
  - `0x54 = 0x15`: AGAIN −10.5 dB → 0 dBFS ≈ 8.75 Vpk, just above the 9.3 V clip point. Minimum noise for the available swing.
  - `0x4C`: digital volume = master volume (0x30 = 0 dB; 0.5 dB steps). The encoder maps to this register through I²C.
  - `0x4E = 0x33`: default ramp. `0x03` bit 3 = soft mute.
  - DSP: keep EQ/DRC flat/bypassed (use the PPC3 "flat" process flow). Leave thermal foldback/AGL enabled as a safety net. All tonal EQ, high-pass and limiting run in the ESP32.
  - Optional EMI: `0x6B = 0x03`, `0x6C = 0x03` (spread spectrum, 25 %, at 384 kHz). Channel-to-channel phase shift: `0x53` bit 0.
  - FAULT pin: after init write `0x61 = 0x0B`, then `0x60 = 0x01`, so ADR/FAULT becomes FAULT (datasheet pin table). The ESP32 polls `0x70–0x72` on falling AMP_FAULT_N.
- **ESP32 limiter:** ceiling −2.8 dBFS (5 W into 4 Ω), with the high-pass at about 120 Hz for the 2" driver (Fs 170 Hz, Xmax 2.1 mm). This must be validated by measurement.
- Re-load the full configuration after any PDN low or PVDD < 3.5 V (datasheet section 11).

## 8. ATtiny412 power-controller firmware specification

**Clock and sleep:**
- 3.33 MHz main clock (OSC20M/6). Power-down sleep when OFF.
- Enable the RTC/PIT (OSCULP32K) only while in BOOTING/RUN/SERVICE.
- BOD: 1.8 V, sampled mode in sleep (fuse).
- WDT always on, 1 s period, cleared in the main loop. LOCKBIT not set (keeps UPDI usable).

**Pins:**
- PA3 BTN_N: internal pull-up off (external 100k), both-edges interrupt. 20 ms debounce.
- PA2 CHG_INT_N: falling edge (fully asynchronous pin).
- PA1 EN_3V3: output, default low.
- PA6 TX:
  - Configure as output low before EN_3V3 rises.
  - Enable the USART only after EN_3V3 = 1 and 50 ms.
  - Disable it again and drive low before EN_3V3 falls.
- PA7 RX: input (external 100k pull-down).

**Button:**

| Duration | OFF state | RUN state |
|---|---|---|
| 50 ms–1.5 s, acted on release | Power on | Forward `BTN_SHORT` (ESP32 may use it for play/pause) |
| ≥ 2 s | Ignore; after > 5 s, offer `MAINT` boot (no heartbeat timeout for 10 min — used for flashing on battery) | Send `SHUTDOWN_REQ`; force OFF if no `PWROFF_ACK` within 8 s |
| ≥ 12 s, no USB | BQ25895 hardware reset (not ATtiny firmware) | BQ25895 hardware reset (not ATtiny firmware) |

**UART protocol:**
- 115200 8N1 ASCII lines, each ending in `\n` with a checksum byte `*hh`.
- ATtiny → ESP32: `BOOT,<reason>` where reason is USER / SERVICE / MAINT / RECOVER; `BTN_SHORT`; `SHUTDOWN_REQ`; `CHG_INT`.
- ESP32 → ATtiny: `HELLO,<fwver>`; `HB` (every 500 ms); `PWROFF_ACK`; `SERVICE_DONE`; `REQ_SHUTDOWN` (ESP32-initiated, for low battery or idle).

**Watchdog and recovery:**
- No `HELLO` within 5 s, or no `HB` for 3 s in RUN: EN_3V3 = 0 for 1 s, then retry.
- After 3 consecutive failures, stay OFF until the next button press.
- An ESP32 brown-out (internal BOD) shows up as a lost heartbeat and is handled the same way.

**SERVICE boots:**
- Trigger: a CHG_INT falling edge while OFF.
- Ignore INT for 10 s after a SERVICE boot, and allow at most 6 SERVICE boots per hour. This prevents an INT ↔ config loop.
- Timeout: 10 s.

**Budget:** OFF ≈ 0.1 µA (power-down) + 6.5 µA LDO.

## 9. PCB layout guidance (4-layer, ≤ 70 x 100 mm)

**Stack-up (1.6 mm, JLCPCB JLC04161H-7628 or similar):**
- L1: components and critical power routing.
- L2: solid GND.
- L3: power pours (VSYS, PVDD, +3V3) plus slow signals.
- L4: GND / slow signals.
- Keep L2 unbroken under the TAS5806M, boost, BQ25895 and ESP32. No splits.

**Placement order:** connectors and edges → BQ25895 + inductor → boost → TAS5806M + filter → 3V3 → ESP32 → ATtiny/encoder. Suggested floor plan for 70 x 100:
- One short edge: USB-C (J101) and the battery KK-396 (J102). The BQ25895 sits within 15 mm.
- Centre: TPS61088 next to the BQ SYS output, with the PVDD bus going directly to the TAS5806M.
- Opposite short edge: TAS5806M with the filters and speaker connectors at the edge.
- Long edge, away from the boost and Class-D: the ESP32 module with its U.FL. Encoder wherever the enclosure needs it.

**BQ25895:**
- PMID cap (C103) and the 100n at PMID/PGND get the tightest loop.
- Keep the SW → L101 copper short, on L1 only.
- SYS caps C106/C107 near the inductor output and pins 15/16.
- REGN cap C110 at pin 22.
- Exposed pad with ≥ 9 vias to L2/L4.
- TS divider near the IC. Route the NTC lead from J103 as a quiet trace away from SW.

**TPS61088:**
- Input caps C206–C208 and output caps C209–C213 within 2 mm of VIN/VOUT/PGND.
- Minimise the VOUT–PGND hot loop: output ceramics directly at pins 14–16 to pad 21.
- Keep the SW node (pins 4–7) and L201 pad small; do not pour GND-plane copper on L1 directly under the SW island.
- FB divider and compensation at the AGND side, away from SW.
- RHL pad 21 gets many vias (≥ 12) for heat. Expect about 0.7 W at 2 x 5 W / 3.0 V.

**TAS5806M:**
- Follow TI's layout example (section 12): PVDD 0.1 µF + 22 µF at pins 6/7 and 32/33, each on the same layer as the IC.
- BST caps (0.22 µF) directly across the BST/OUT pins.
- PowerPAD fully soldered with a via array to L2/L4. RθJA ≈ 24–29 °C/W → about 1.8 W at 2 x 5 W continuous, about +50 °C rise.
- Copper area on L4 under the IC helps.
- Place CSAD0660 L601/L602 right at the OUT pins.
- 0.68 µF caps close to the inductor outputs, returning to GND with short vias. Speaker connectors after the 1 nF caps.
- Keep OUT traces wide enough for 2 A peak; the switch-node copper before the inductors stays compact.
- Silkscreen: "SPK L+ / L−, BTL – neither terminal is GND".

**ISL91127:** input/output caps at the pins, LX1/LX2 tight around L301, FB resistors at the FB pin with a GND guard (datasheet).

**ESP32:**
- Module at the board edge, U.FL accessible. The coax runs away from the boost and TAS outputs.
- 22 µF + 10 µF + 100 nF at pin 2.
- Pins 39–47 (EPAD) to GND with vias.
- I²S lines (BCLK 3.072 MHz) routed over continuous L2 GND, kept away from the encoder/CC traces; 22R at the ESP32 pins.

**Grounding:** one GND plane. Separate by placement: power stages in one zone, ESP32/encoder in another. No ferrite beads.

**Test points:**
- TP101–TP104 VBUS/VSYS/VBAT/GND
- TP201 PVDD, TP202 BOOST_EN
- TP301 +3V3, TP302 EN_3V3
- TP401 +3V3_AON
- TP501–503 spare GPIO
- TP601–603 BCLK/LRCLK/DOUT

Avoid adding probe pads on SW nodes; use the inductor pads for scope probing (high dV/dt — label them).

**Thermal:**
- Expected dissipation at 2 x 5 W / 3.3 V: TAS ≈ 1.8 W, TPS61088 ≈ 0.7 W, L201 ≈ 0.3 W, BQ (charging 1.5 A) ≈ 0.6 W.
- Keep the BQ and TPS61088 apart; they can both be hot while charging + playing.
- Validate in the enclosure.

**Antenna and EMI:**
- Spread-spectrum option on the TAS.
- Keep the speaker leads twisted.
- DNP common-mode caps are already effectively provided by the 1 nF C605/C606/C611/C612.

## 10. BOM, stock and purchases

The full grouped BOM is in `TAS5806M-BOM.csv` (77 lines). Each line has the inventory id where the part is stocked.

**From inventory (verified quantities):**

| Part | Inventory id | Note |
|---|---|---|
| ISL91127IRAZ-T7A | 732 | qty 1 — buy a spare |
| ESP32-WROOM-32UE-N8R2 | 83 | |
| ATtiny412 | 80 | |
| TPS7A2033PDBVR | 28 | |
| CSAD0660-100M | 520 | ×2 — uses all stock |
| Panasonic FR 220 µF/16 V | 581 | |
| KK-396 header | 722 | |
| MC34629/MC34631/MC34635 headers | 126/127/691 | |
| TS02 switches | 537 | |
| 1N4148W | 510 | |
| KP-2012EC / KP-2012LSGC LEDs | 640/639 | |

Plus stocked MLCCs (2012/3216) and resistors (2012/1608): see the BOM `Stock` column.

**To purchase (UK: DigiKey UK / Mouser UK / Farnell / CPC):**

| Qty | Value | MPN | Package | Reason |
|---|---|---|---|---|
| 1 (+1 spare) | BQ25895RTWR | TI BQ25895RTWR | WQFN-24 4x4 | Charger/power-path (specified) |
| 1 (+1) | TPS61088QRHLRQ1 | TI | VQFN-20 RHL | Boost; -Q1 because the TPS61088 commercial datasheet/page was unavailable — see §11 |
| 1 (+1) | TAS5806MDCPR | TI | HTSSOP-38 | Amplifier |
| 1 | TVS1400DRVR | TI | WSON-6 2x2 | VBUS surge/ESD, 14 V standoff (HVDCP-safe) |
| 1 | TPD2E2U06DCKR | TI | SC-70-3 | D+/D- ESD (stock USBLC6-2 has a 6 V VBUS pin that HVDCP 9/12 V would overstress) |
| 1 | USB4105-GF-A | GCT | USB-C 16P | Receptacle, 5 A |
| 1 | 0451008.MRL | Littelfuse | NANO2 6.1x2.7 | 8 A battery fuse |
| 2 | XFL4020-102MEB | Coilcraft | 4x4x2.1 | 1 µH for BQ25895 and ISL91127 |
| 1 | XAL7030-222MEB | Coilcraft | 7.5x7.2x3.1 | 2.2 µH boost |
| 4 | 0.68 µF 100 V X7R | KEMET C1210C684K1RACTU | 3225 metric | Class-D filter |
| 12 (+10) | 100 nF 50 V X7R | KEMET C0603C104M5RACTU | 1608 metric | Your standard decoupling part (stock 3216 would also work) |
| 7 (+10) | 1 µF 25 V X7R | Samsung CL21B105KAFNNNG | 2012 metric | Your standard |
| 1 | 47 nF 50 V X7R | Murata GRM188R71H473KA61D | 1608 | BQ BTST |
| 1 | 56 pF C0G | Murata GRM1885C1H560JA01D | 1608 | ISL feed-forward |
| 1 (DNP) | 47 pF C0G | Murata GRM1885C1H470JA01D | 1608 | Boost C8 tuning |
| 1 | 150 Ω 1 % | Yageo RC0805FR-07150RL | 2012 | BQ ILIM (stock 150R has no recorded tolerance) |
| 1 | 68 kΩ 1 % | Yageo RC0805FR-0768KL | 2012 | Boost ILIM |
| 1 | EC11E18244A5 | Alps Alpine | EC11E | Encoder + switch |
| 1 (DNP) | NCU18XH103F60RB | Murata | 1608 | Optional on-board NTC |
| 1 | 10k NTC with leads (if the pack has none) | e.g. TDK/EPCOS B57861S0103F040 (B 3988 — verify; a 103AT/B3435 bead is preferred) | – | Cell-mounted NTC on J103 |

## 11. Decisions taken, deviations and unresolved items

1. **TPS61088 → TPS61088QRHLRQ1 (needs your review).**
   - TI's TPS61088 product page and `symlink/tps61088.pdf` returned 404 on every attempt, and the mirrors were blocked.
   - All calculations use the verified TPS61088-Q1 datasheet (SLVSE52A): same RHL package and pinout.
   - If you fit TPS61088RHLR, re-check RILIM/RFREQ against its own datasheet. The Q1 lists higher RDS(on) (21/24 mΩ) than the search summary quoted for the commercial part (11/13 mΩ), so thermals would be better, not worse.
2. **Class-D filter capacitor dielectric.**
   - 0.68 µF / 100 V X7R in 3225 metric: the TI EVM value, used at about 9 % of its rating.
   - Film (Panasonic ECW-U1684KCV, PEN, 9.8 x 6.3 mm) would avoid X7R in the output path, but its SMD footprint isn't verified and it is large.
   - The TAS5806M feedback is taken before the LC filter, so the filter caps' linearity is not corrected. Their audio-band current is small (Xc = 234 Ω at 1 kHz).
3. **No reverse-polarity FET on the battery (your decision).**
   - Fitted: a polarised KK-396 connector plus F101.
   - A low-side N-MOSFET (gate to BAT+) would need Rds(on) ≤ 5 mΩ guaranteed at Vgs = 2.5–3 V. I did not verify a specific part.
   - I recommend adding one if the pack leads are hand-made.
4. **Power-path budget.** ILIM 150R fixes a hardware input ceiling of about 2.37 A. Firmware sets the actual IINLIM from the CC advertisement. With the system OFF, a 1.5 A-only Type-C charger that also shorts D+/D- (DCP) could be asked for up to 2.37 A until the ATtiny SERVICE boot reconfigures it (≤ 2 s). VINDPM/ICO protect against collapse.
5. **NTC unknown.** Fail-safe: no NTC means "cold", so charging stays inhibited. Fit either a 10k B3435 NTC bonded to the cell (J103) or RT101 on the board — never both. An on-board NTC measures the PCB, not the cell. The BQ25895 does not monitor TS during discharge (REGN is off without VBUS).
6. **Thermal protection of the cell during discharge** relies on the cell's own protection plus the BQ's 9 A BATFET OCP and F101. There is no discharge temperature cutoff — add a firmware limit on long sessions if the pack is enclosed with the amplifier.
7. **Boost output disconnect.** The TPS61088 has none, so in OFF state PVDD ≈ VSYS − 0.5 V. The amplifier is held in shutdown (7 µA). Add a high-side P-FET only if a true zero is needed.
8. **ESP32 back-feed via the CC-sense resistors:** ≤ 15 µA when USB is present and the system is OFF. Accepted and documented.
9. **Inductor footprints:**
   - XFL4020 uses the KiCad XAL4020 land pattern. Verify against Coilcraft document 745.
   - CSAD0660 uses your existing footprint, which matches Codaca's 2.6 x 2.65 mm pads, 1–2 / 4–3 windings.
   - Winding-to-winding coupling (k) is not specified. Measure L(1–2) with 4–3 open and shorted.
10. **Stocked header footprints:** the MC34629/31 friction-lock headers are drawn with the Molex KK-254 footprint. Verify against the Multicomp drawing.
11. **100 nF / 1 µF:** your 1608/2012 standard parts are specified for purchase. Stock 3216 parts are valid electrical fallbacks.
12. **HVDCP/MaxCharge** are enabled at BQ POR, so a QC charger could raise VBUS to 9/12 V before the first ESP32 configuration. Every VBUS part is rated for that: TVS1400 14 V, C105 25 V, BQ 14 V operating.

## 12. Remaining risks

- **Boost loop:** compensation is from the TI small-signal model with estimated capacitor derating. It needs load-step verification. C205 is provided as a DNP tuning position.
- **Hybrid modulation:** needs a PPC3-generated configuration. The datasheet register description alone may not set it up correctly; use 1SPW/768 kHz first.
- **Battery current:** about 4.7 A at 3.0 V for continuous full output. Unknown pack protection: if its OCP trips below about 6 A, reduce the limiter ceiling at low VBAT.
- **Thermal:** the TAS5806M at 2 x 5 W continuous (about 51 °C rise) inside an enclosure with the cell. The BQ25895 charging while the boost runs.
- **Encoder/button QON 12 s reset:** pressing during playback for > 12 s cuts power abruptly (by design).
- **Footprint verification items** in §11.9–10 and the DCP/RHL exposed-pad sizes (checked against the TI drawings, but confirm the paste design).

## 13. Pre-fabrication electrical review checklist

- [ ] Supply voltages:
  - [ ] PVDD 9.30 V (316k/47k)
  - [ ] +3V3 3.33 V (1M/316k)
  - [ ] +3V3_AON 3.3 V
  - [ ] VREG 4.208 V in firmware
- [ ] Every IC supply pin is decoupled at the pin (BQ PMID/SYS/BAT/REGN, TPS VIN/VOUT/VCC, ISL PVIN/VOUT, TAS PVDD×2/DVDD/AVDD/VR_DIG, ESP32 3V3, ATtiny VDD, LDO in/out).
- [ ] Exposed pads tied to GND: BQ pad 25, TPS pad 21, ISL pad 21, TAS pad 39, TVS pad 7, ESP32 39–47.
- [ ] Connector pinouts:
  - [ ] J102 (pin 1 BAT+)
  - [ ] J103 NTC
  - [ ] J601/J602 (pin 1 +)
  - [ ] J501 (1 GND … 6 IO0)
  - [ ] J401 (1 UPDI, 2 V, 3 GND)
  - [ ] USB-C A/B mapping
- [ ] Polarities:
  - [ ] D401 anode to PA3
  - [ ] LEDs D102 (K to STAT) and D501
  - [ ] C620 electrolytic + to PVDD
  - [ ] TVS1400 IN to VBUS
- [ ] Default states with the ESP32 unpowered:
  - [ ] BOOST_EN low (R204)
  - [ ] AMP_PDN low (R602)
  - [ ] EN_3V3 low (R302)
  - [ ] OTG = GND
  - [ ] /CE = GND
- [ ] Strapping pins: IO12 floating (low), IO0 pull-up, IO2/IO15/IO5 untouched. IO16 pulled up (PSRAM).
- [ ] Voltage ratings:
  - [ ] VBUS caps ≥ 25 V
  - [ ] PVDD caps 25 V (22 µF), 16 V (220 µF FR), 100 V (0.68 µF)
  - [ ] BST 0.22 µF 25 V
- [ ] Power ratings: F101 8 A; L201 Irms 10 A; CSAD Irms 3.5 A; 150R/68k signal-level only.
- [ ] Footprints match the ordered MPNs (§11.9–10). Verify the electrolytic diameter (FR 220 µF/16 V).
- [ ] ERC clean (it is at generation time) and DRC clean after layout. Re-run ERC after any edit.
- [ ] Antenna: U.FL position and coax route; no metal enclosure over the antenna.

## 14. Safe first power-up test plan

Use a bench supply with current limit instead of the cell for steps 1–6. Do not connect the speakers until step 8.

1. **Before any power:** visual and continuity checks.
   - Measure each rail to GND: VBUS, VSYS, VBAT, PVDD, +3V3, +3V3_AON. Each should read > 1 kΩ, not a short.
   - Confirm J102 pin 1 is BAT+.
   - Check the TAS/TPS/BQ thermal pads for solder voids (X-ray or a careful look).
2. **VBAT input only:** bench supply at 3.7 V, 100 mA limit, into J102.
   - Expect VSYS ≈ 3.7 V and +3V3_AON = 3.3 V.
   - Total current < 100 µA (ATtiny blank: EN_3V3 held low by R302).
3. **Program the ATtiny** through J401 (SerialUPDI). Measure the OFF current: expect about 40 µA (§3.7).
4. **3V3 rail:**
   - Short-press the button (or jumper EN_3V3 to +3V3_AON through 1k with the ATtiny blank). Expect +3V3 = 3.30–3.36 V.
   - Flash the ESP32 through J501 with a "hello + I²C scan" image. It should find 0x6A and 0x2D.
5. **Boost, no load:**
   - Raise the limit to 1 A. Firmware sets BOOST_EN = 1 with AMP_PDN = 0.
   - PVDD should be 9.2–9.4 V. Check the SW waveform at about 550 kHz (scope on the L201 pad).
   - Input current < 30 mA in PFM.
6. **Boost load step:** 9.3 V → 10 Ω electronic load stepping 0.2 ↔ 1.0 A. Look for ≤ 1 ring and no oscillation; adjust C205/R207 if needed. Check the VIN = 3.0 V corner.
7. **Charger:**
   - USB-C from a current-limited source. Verify BC1.2/CC detection, the IINLIM write and ICHG 1.5 A (REG12 ADC).
   - With the NTC absent, TS_FAULT must report COLD and there must be no charging.
   - Then fit the NTC. Check the TS temperature reads correctly at room temperature.
   - Let the BQ25895 die reach equilibrium and measure its temperature.
8. **Amplifier:**
   - Load each output with 4 Ω power resistors (≥ 10 W), not speakers.
   - Run the sequence in §5. Check the idle current at PVDD (hybrid/1SPW).
   - 1 kHz sine: check THD+N and that clipping occurs at about 7.5–8 W; verify the ESP32 limiter holds 5 W.
   - Check the PVDD ripple. Thermal soak at 2 x 5 W for 30 min.
9. **Speakers:** only after the limiter and high-pass are verified. Start at low volume.
10. **Battery:**
    - Connect the real cell (with its protection) only after steps 1–9.
    - Check the fuse/connector voltage drop at 4 A, low-battery shutdown, ship mode entry/exit, and the 12 s /QON reset.
11. **Firmware fault injection:**
    - Kill the ESP32 heartbeat: the ATtiny must cut +3V3 within 3 s.
    - Hang the ATtiny (debug build): the 12 s /QON reset must recover.
    - Pull USB during playback: no brown-out.

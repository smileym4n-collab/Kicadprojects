# RELAYVOL purchasing and stock

Quantities are for one stereo prototype. Supplier links identify the exact parts or their search results. Check cart availability before ordering. Inventory quantities are from the read-only lookup for this design.

## Purchase for the default build

| Qty | References | Item |
|---:|---|---|
| 7 | K1–K7 | Omron G6K-2P DC5, 5 V non-latching DPDT, standard through-hole pattern. [DigiKey UK](https://www.digikey.co.uk/en/products/detail/omron-electronics-inc-emc-div/G6K-2P-DC5/277852) |
| 2 | R1, R15 | 562 Ω Panasonic ERA-6AEB5620V. [DigiKey UK](https://www.digikey.co.uk/en/products/detail/panasonic-industry/ERA-6AEB5620V/2025641) |
| 2 | R2, R16 | 169 kΩ Yageo RT0805BRD07169KL. [DigiKey UK](https://www.digikey.co.uk/en/products/detail/yageo/RT0805BRD07169KL/6616992) |
| 2 | R3, R17 | 1.10 kΩ Yageo RT0805BRD071K1L. [DigiKey UK](https://www.digikey.co.uk/en/products/detail/yageo/RT0805BRD071K1L/5139256) |
| 2 | R4, R18 | 80.6 kΩ Panasonic ERA-6AEB8062V. [DigiKey UK](https://www.digikey.co.uk/en/products?keywords=ERA-6AEB8062V) |
| 2 | R5, R19 | 2.05 kΩ Yageo RT0805BRD072K05L. [DigiKey UK](https://www.digikey.co.uk/en/products/detail/yageo/RT0805BRD072K05L/6617028) |
| 2 | R6, R20 | 38.3 kΩ Panasonic ERA-6AEB3832V. [DigiKey UK](https://www.digikey.co.uk/en/products/detail/panasonic-industry/ERA-6AEB3832V/3075116) |
| 2 | R7, R21 | 3.65 kΩ Susumu RG2012P-3651-B-T5. [DigiKey UK](https://www.digikey.co.uk/en/products/detail/susumu/RG2012P-3651-B-T5/1267020) |
| 2 | R8, R22 | 16.5 kΩ Susumu RG2012P-1652-B-T5. [DigiKey UK](https://www.digikey.co.uk/en/products?keywords=RG2012P-1652-B-T5) |
| 2 | R9, R23 | 6.04 kΩ Panasonic ERA-6AEB6041V. [DigiKey UK](https://www.digikey.co.uk/en/products/detail/panasonic-industry/ERA-6AEB6041V/2025734) |
| 2 | R10, R24 | 6.65 kΩ Panasonic ERA-6AEB6651V. [DigiKey UK](https://www.digikey.co.uk/en/products/detail/panasonic-industry/ERA-6AEB6651V/2025738) |
| 2 | R11, R25 | 8.45 kΩ Panasonic ERA-6AEB8451V. [DigiKey UK](https://www.digikey.co.uk/en/products/detail/panasonic-industry/ERA-6AEB8451V/2025747) |
| 2 | R12, R26 | 1.91 kΩ Yageo RT0805BRD071K91L. [DigiKey UK](https://www.digikey.co.uk/en/products/detail/yageo/RT0805BRD071K91L/1075696) |
| 2 | R13, R27 | 9.76 kΩ Panasonic ERA-6AEB9761V. [DigiKey UK](https://www.digikey.co.uk/en/products/detail/panasonic-industry/ERA-6AEB9761V/2025753) |
| 2 | R14, R28 | 255 Ω Susumu RG2012P-2550-B-T5. [DigiKey UK](https://www.digikey.co.uk/en/products/detail/susumu/RG2012P-2550-B-T5/1266949) |

Each resistor above is one 2012 metric thin-film part, ±0.1%, rated 0.125 W. All fourteen ladder values have to be sourced in pairs. The stocked precision values listed in the brief do not match the chosen ladder values. The stocked G6K-2P-Y DC5 uses a different drill pattern, so seven standard G6K-2P DC5 relays are required. [Omron terminal and mounting drawings](https://components.omron.com/us-en/system/files/2026-05/datasheet_pdf/K106-E1.pdf)

## Purchase if needed for assembly or configuration

| Qty | When needed | Item |
|---:|---|---|
| 1 | Optional output muting | One more G6K-2P DC5 for K8. Its driver uses the stocked components below. [DigiKey UK](https://www.digikey.co.uk/en/products/detail/omron-electronics-inc-emc-div/G6K-2P-DC5/277852) |
| 2 | 47 kΩ amplifier inputs | 12.7 kΩ Panasonic ERA-6AEB1272V, 0.1%, 2012 metric, in place of R29/R30. [DigiKey UK](https://www.digikey.co.uk/en/products/detail/panasonic-industry/ERA-6AEB1272V/2025762) |
| 1 set | No matching parts on hand | J1 JST B2B-XH-A(LF)(SN), XHP-2 housing and two matching contacts or a pre-crimped pigtail. [JST XH](https://order.jst-mfg.com/InternetShop/app/pdf_show.php?kbn=1&key=eXH.pdf) |
| 2 × 3-pin and 4 × 2-pin | No matching parts on hand | Straight 2.54 mm single-row through-hole headers and mating leads for J2–J7. |
| 1 | No suitable panel control on hand | 10 kΩ linear single-gang pot and mounting hardware. Example Bourns PTV09A-4020F-B103. The inventory's generic 10 kΩ multiturn part is a different form factor. [Bourns data](https://www.bourns.com/docs/product-datasheets/PTV09.pdf) · [DigiKey UK](https://www.digikey.co.uk/en/products/detail/bourns-inc/PTV09A-4020F-B103/3534181) |
| 1 | No suitable external supply on hand | Regulated 5 V DC source rated at least 0.5 A with a correctly polarised lead. |

## Inventory parts used in the BOM

| Part | Fit now / with K8 | Available | Inventory ID |
|---|---:|---:|---:|
| ATtiny1616 wide SOIC-20 | 1 / 1 | 1 | 82 |
| 2N7002K SOT-23 | 7 / 8 | 18 | 332 |
| 1N4148W SOD-123 | 7 / 8 | 61 | 510 |
| RC0603FR-10330RL, 330 Ω | 7 / 8 | 99 | 217 |
| RT0805DRE07100KL, 100 kΩ | 7 / 8 | 67 | 242 |
| RC0603FR-101KL, 1 kΩ | 1 / 1 | 99 | 222 |
| RC0603FR-101ML, 1 MΩ | 1 / 1 | 90 | 246 |
| RG2012P-103-B-T5, 10 kΩ, 0.1% | 2 / 2 for bench termination | 50 | 375 |
| 35ZLH220MEFC8X11.5, 220 µF/35 V | 1 / 1 | 16 | 366 |
| MC0603B104K500CT, 100 nF/50 V | 4 / 4 | 961 | 698 |
| CL21A475KAQNNNE, 4.7 µF/25 V | 1 / 1 | 37 | 133 |

The SOIC record is the match for the schematic footprint. The four parts listed separately as SSOP-20 are outside the count above. The inventory remains read-only.

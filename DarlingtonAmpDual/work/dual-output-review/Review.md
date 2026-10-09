# Follow-up verification - corrected base drive

The saved schematic was re-exported after the user correction. R19.1 now connects directly to DRIVE_N alongside R17.1; R20.1 connects directly to DRIVE_P alongside R18.1. All four output bases have separate 33R stoppers from their shared drive nodes. This closes the connection finding below.

Corrected ERC: 0 violations. Exactly Q13/Q14/R19/R20/R23 remain asterisked. Omitting the complete branch preserves the original single-pair topology. The earlier capacitor specification, sheet presentation, bias documentation and bench/thermal qualifications remain outside this correction check. No source files changed by the reviewer.

---

# DarlingtonAmpDual schematic review - 9 October 2026

Read-only review of the saved DarlingtonAmpDual.kicad_sch. ERC: 0 violations. Schematic topology checked by exported netlist and rendered review. PCB, DRC, thermal assembly and actual component condition were not reviewed in this pass.

## Required connection correction

R19.1 is connected to Q11 base / R17.2. R20.1 is connected to Q12 base / R18.2. Thus R17/R18 feed both transistor inputs; the second transistor additionally sees R19/R20. This is an asymmetrical base drive arrangement rather than four separate stoppers from the shared drive nodes. It couples the two devices through the first resistor and can alter dynamic sharing/damping.

Move R19 pin 1 to DRIVE_N (R17 pin 1), and R20 pin 1 to DRIVE_P (R18 pin 1). Keep each 33R resistor close to its own transistor base on the PCB. No connection changes were made during this review.

## Checks that passed

- Q13 pin 2 goes to +35V; Q14 pin 2 goes to -35V.
- Q13 pin 3 goes only to R23 pin 3; Q14 pin 3 goes only to R23 pin 1.
- R23 pin 2 joins AMP_OUT, as does R1 pin 2. Each of the four transistors therefore has an individual 0R22 emitter section.
- Feedback and Zobel remain on AMP_OUT before the common output inductor; speaker output is after that inductor.
- Exactly five part values end in an asterisk: Q13, Q14, R19, R20, R23. Removing their nodes and ignoring empty nets reproduces the original single-pair 31-net topology exactly. Omit the complete branch, without jumpers.
- Existing front-end and bias reference connections are preserved.

## Assembly and documentation

An asterisk in Value is a human annotation, not an automatic BOM/DNP variant. Record a single-pair assembly list or use DNP flags on the appropriate components when generating that BOM. The current two-pair schematic should include a visible legend identifying the five optional parts.

The rendered sheet cuts off the output filter/connector beyond the right-hand page edge. Move those blocks into the sheet or enlarge it before generating build documents.

Bias notes refer to removed TP1/TP2/TP3. Update them for the present dual resistors: for NPN, measure red on R1/R23 pin 3 and black on pin 2; for PNP, red on pin 2 and black on pin 1. At 80-100mA per transistor, every section reads 17.6-22mV and two-pair idle output dissipation totals approximately 11.2-14W at +/-35V. This remains a provisional bias setting requiring distortion, drift and sharing checks. All outputs and Q9 need a verified common heatsink arrangement with electrical insulation and proper sensor coupling.

C4 says 100pF / 100V but does not identify C0G/NP0 dielectric in its Value. C6/C8 and C5/C7/C9 omit voltage ratings. Specify the installed ratings explicitly. 50V C6/C8 can be suitable when the actual maximum rails including no-load/high-mains peaks really stay within +/-35V; 63V provides more headroom. Voltage ratings do not prove mechanical footprint fit.

## Supply recommendation

Treat +/-35V as the recommended maximum actual rail voltage for both variants into 8 ohms at this design stage. Two output pairs improve current/thermal margin, not rail-voltage capability. Higher rails require another electrical/SOA/thermal assessment, not just a second pair.

For single-pair 4-ohm commissioning, start at +/-25V and do not treat that as a validated safe limit for arbitrary reactive speakers. Two pairs at +/-35V into 4 ohms are a conditional development target, subject to the base-drive correction, current sharing, hot SOA, VAS drive, stability, heatsink, coil and connector testing. No measured maximum-safe-supply rating is established for either build.

For a resistive sinusoidal load, worst-case ideal Class-B average transistor dissipation is Vrail^2/(pi^2 Rload Npairs). At 35V: single pair / 8ohm = 15.5W per transistor; single pair / 4ohm = 31.0W; double pair / 4ohm = 15.5W assuming equal sharing. Add allowance for quiescent losses. Reactive load current/phase can impose larger instantaneous SOA stress. Off-state output devices can approach twice the rail voltage, approximately 70V at +/-35V, irrespective of pair count.

The existing approximately 6mA VAS drive can be retained as a starting point, but doubled output loading requires square-wave and capacitive-load stability checks for both assembly variants. DC gain alone does not establish adequate dynamic drive.

Manufacturer reference: https://www.semicon.sanken-ele.co.jp/sk_content/2sd2390_ds_en.pdf and https://www.semicon.sanken-ele.co.jp/sk_content/2sb1560_ds_en.pdf. The output devices' 150V / 10A / 100W absolute ratings must not be interpreted as a build-level safe operating envelope.

No source schematic, PCB, project or libraries were modified.

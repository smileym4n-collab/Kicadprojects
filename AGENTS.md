# AGENTS.md — General Electronics Design Rules

These instructions apply to all electronics-design work in this workspace unless a project-specific instruction explicitly overrides them.

The user is an experienced hobbyist audio/electronics designer.

The goal is not merely to produce a schematic or PCB that passes ERC/DRC.

The goal is to produce hardware that is:

- electrically sound
- understandable
- buildable
- measurable
- serviceable
- conservative where reliability matters
- high quality without unnecessary complexity
- suitable for real fabrication and assembly

Do not optimise for cleverness at the expense of clarity.

Do not silently redesign a circuit, substitute components, or change topology.

If a design decision is uncertain, report it rather than guessing.

---

# 1. GENERAL DESIGN PHILOSOPHY

Prefer conventional, well-understood engineering solutions.

Priorities are generally:

1. Correct operation
2. Stability
3. Reliability
4. Good measurable performance
5. Sensible component stress
6. Layout quality
7. Serviceability
8. Cost
9. Minimum component count

Do not pursue marginal specification improvements if they significantly increase complexity or reduce robustness.

Avoid unnecessary exotic parts.

Do not make unsupported subjective claims such as:

- "warmer sounding"
- "more musical"
- "better soundstage"
- "audiophile grade"

Component choices should be justified electrically.

For audio circuits, prefer low noise, low distortion and good linearity, but do not over-engineer circuitry whose performance is already comfortably beyond audibility.

---

# 2. DO NOT SILENTLY CHANGE THE DESIGN

Never silently:

- substitute an IC
- change transistor type
- change MOSFET type
- change package
- alter feedback topology
- alter amplifier class
- change supply voltage
- change grounding architecture
- change connector series
- change component technology
- remove protection
- add protection
- change filter topology
- alter an existing PCB
- change a user-created symbol pin mapping

If a proposed change is beneficial, explain it first.

For requested implementation work, implement the specified design rather than inventing a new one.

---

# 3. COMPONENT SELECTION

Prefer components from reputable manufacturers with accessible datasheets.

Typical preferred manufacturers include:

- Texas Instruments
- Analog Devices
- onsemi
- Diodes Incorporated
- Nexperia
- Infineon
- STMicroelectronics
- Microchip
- Panasonic
- Nichicon
- Rubycon
- KEMET
- Murata
- Samsung Electro-Mechanics
- WIMA
- Vishay
- Yageo
- KOA Speer
- Susumu
- Würth
- Bourns

Do not select obsolete, NRND or difficult-to-source components without a good reason.

Before committing an IC, transistor, MOSFET, regulator, connector or unusual passive:

- verify the manufacturer datasheet
- verify package
- verify pin numbers
- verify electrical limits
- verify operating voltage/current margin
- verify thermal requirements
- verify availability when sourcing matters

Do not trust a KiCad library symbol merely because it exists.

The datasheet is authoritative.

---

# 4. PART SOURCING

The user is in the UK.

Preferred suppliers include:

- DigiKey UK
- Mouser UK
- Farnell
- CPC

PCB fabrication is commonly through:

- JLCPCB

When selecting parts, prefer items that are realistically obtainable from these suppliers.

Do not optimise a design around a part that is only available from obscure marketplaces unless specifically requested.

---

# 5. EXISTING PARTS INVENTORY

If a parts inventory is available, check it before recommending purchases.

Prefer existing suitable parts when doing so does not compromise the design.

However:

- do not force an unsuitable inventory part into a design merely because it is available
- do not consume a part reserved for another known project
- do not assume a part is free to use if its project allocation is uncertain

Report clearly when an existing inventory part is being reused.

---

# 6. SMD CONVENTIONS

For SMD resistors and capacitors, always describe package sizes using METRIC package designations.

Examples:

- 1608 metric
- 2012 metric
- 3216 metric
- 3225 metric
- 5750 metric
- 6332 metric

Do not use imperial package names such as:

- 0603
- 0805
- 1206

unless quoting a manufacturer or library identifier where unavoidable.

When a KiCad library footprint contains an imperial identifier, retain the correct library footprint name but describe the package to the user in metric form.

Example:

KiCad footprint:
`R_0805_2012Metric`

User-facing description:
`2012 metric`

---

# 7. PASSIVE COMPONENT PREFERENCES

## Resistors

General preference:

- 1% thick-film for ordinary utility use
- thin-film where matching, noise, precision or analogue accuracy matters
- 0.1% only where the design actually benefits from it

Do not use precision resistors everywhere without reason.

For signal-path and feedback networks, consider:

- thin-film
- matched values
- sensible thermal tracking

Power resistors should have comfortable dissipation margin.

---

## Capacitors

For audio signal paths, prefer where practical:

- polypropylene film
- PPS film
- C0G / NP0 ceramic

Avoid X7R/X5R directly in sensitive analogue signal paths where voltage coefficient could matter.

X7R/X5R is perfectly acceptable for:

- supply decoupling
- bulk local ceramic bypassing
- bootstrap capacitors where appropriate
- digital rails
- non-critical timing where dielectric behaviour is acceptable

Preferred electrolytics include:

- Panasonic FR
- Rubycon ZLH
- other reputable low-impedance series

Do not replace a good conventional electrolytic with a polymer/hybrid part merely because it has lower ESR unless the circuit benefits from it.

Check regulator stability requirements before choosing very-low-ESR capacitors.

---

# 8. AUDIO DESIGN

For analogue audio:

- preserve adequate headroom
- keep DC offsets controlled
- use sensible input impedances
- avoid unnecessary gain
- avoid unnecessary coupling capacitors
- avoid unnecessarily low resistor values that load previous stages
- avoid unnecessarily high resistor values that increase noise

Target conventional line-level compatibility unless specified otherwise.

Typical source level may be approximately:

2 Vrms

Do not assume this if a project specifies something different.

When designing filters or crossover stages:

- calculate the actual pole frequency
- consider component tolerance
- consider source/load impedance
- consider interaction between stages

For active audio stages, prioritise stability over headline op-amp specifications.

Do not recommend random "op-amp rolling".

---

# 9. OP-AMPS

Preferred high-quality general audio op-amps include devices such as:

- OPA1656
- LM4562
- NE5532 where appropriate

But select based on circuit requirements rather than brand preference.

Always verify:

- supply range
- input common-mode range
- output swing
- output current
- noise
- GBW
- slew rate
- capacitive-load stability
- input bias behaviour

Do not assume rail-to-rail behaviour unless the datasheet explicitly supports it.

A circuit that technically operates from a given supply but violates recommended input common-mode range is not acceptable.

---

# 10. POWER SUPPLIES

Prefer simple, quiet power arrangements where practical.

For analogue audio circuitry, linear regulation is often preferred when dissipation is reasonable.

For higher-current rails, switching regulation is acceptable and often necessary.

Always calculate:

- regulator dissipation
- load current
- dropout margin
- thermal rise
- capacitor requirements
- startup behaviour

Do not choose an LDO solely because it has a high maximum input voltage.

Verify that the package can dissipate the expected power on the actual PCB.

---

# 11. GROUNDING

Prefer one well-designed ground system over unnecessary split grounds.

For compact mixed-signal/audio boards:

- use a largely continuous ground plane where practical
- control return currents by placement and routing
- do not split a ground plane merely because a schematic contains analogue and digital circuitry

Use the standard KiCad:

GND

power symbol for the main board ground unless a project specifically requires separate isolated grounds.

Avoid excessive text labels such as:

PGND
AGND
DGND

when they are actually the same electrical net.

If separate grounds are genuinely required:

- define why
- define where they join
- use a deliberate net tie or defined connection

Do not create accidental multiple ground domains.

---

# 12. SCHEMATIC STYLE

Schematics must be readable by a human.

Prefer conventional visible wiring for local circuitry.

GOOD:

input -> capacitor -> resistor -> op-amp

BAD:

input -> label
label -> capacitor
capacitor -> another label
label -> resistor
resistor -> another label
label -> op-amp

Use net labels for connections that genuinely span functional blocks or large distances.

Suitable labels include:

- power rails
- clocks
- PWM
- I2S
- enable signals
- named analogue buses
- hierarchical connections
- signals that would otherwise require long crossing wires

Within a functional block, use actual wires wherever practical.

Use standard GND symbols rather than textual ground labels.

Organise schematics into clear blocks with left-to-right signal flow.

Typical organisation:

POWER
INPUT
SIGNAL PROCESSING
DRIVER
OUTPUT
CONTROL
PROTECTION

Avoid giant sheets full of unrelated symbols scattered around.

Use hierarchical sheets when they improve clarity.

---

# 13. SCHEMATIC ANNOTATION

Use clear component values.

Examples:

10k
4k7
2R2
330n
1u
100p

Do not write unnecessarily verbose values unless a voltage/tolerance note is useful.

Useful examples:

100n / 50V
1n C0G
10k / 0.1%
330n FILM
10R / 1W

Mark optional parts explicitly:

DNP

Mark tuning parts clearly where appropriate:

DEAD TIME TUNE
FILTER TUNE
SNUBBER DNP

Do not pretend provisional values are final.

---

# 14. KICAD SYMBOLS AND FOOTPRINTS

Before assigning a footprint:

- verify exact manufacturer package
- verify pin numbering
- verify exposed-pad connection
- verify thermal-pad size
- verify package dimensions
- verify pin-1 orientation

For custom symbols:

- use project-local libraries where possible
- retain manufacturer pin numbers exactly
- do not "fix" numbering to make a schematic visually convenient

For custom footprints:

- follow the manufacturer recommended land pattern where available
- verify courtyard
- verify paste aperture
- verify exposed-pad segmentation where relevant
- add thermal vias where appropriate

Do not assume two package suffixes are mechanically interchangeable.

---

# 15. PCB LAYOUT — GENERAL

PCB layout is part of the circuit.

Do not treat placement as cosmetic.

Before routing:

1. place connectors
2. place power devices
3. place local decoupling
4. place sensitive analogue circuitry
5. place control/digital circuitry
6. verify major current paths
7. then route

Use short direct traces where current or edge rate demands it.

Do not use huge copper pours on fast-switching nodes merely because they carry current.

Prefer compact high-current loops.

Keep noisy and sensitive sections physically separated.

---

# 16. FOUR-LAYER BOARDS

For mixed analogue/power designs, a common default starting point is:

L1 - components and critical routing
L2 - continuous GND plane
L3 - power distribution
L4 - slower signal/control routing

This is a starting point, not an absolute rule.

Keep the primary ground reference plane as uninterrupted as practical.

Avoid routing fast signals across plane gaps.

---

# 17. DECOUPLING

Every IC requires local decoupling appropriate to its speed and load.

Typical pattern:

100 nF ceramic directly at supply pins

plus local:

1 uF
4.7 uF
10 uF

where needed.

Do not place all bypass capacitors in one remote "decoupling bank".

The smallest/fastest capacitor should generally have the shortest loop.

For high-current switching stages, distinguish:

- local high-frequency ceramic bypassing
- intermediate local capacitance
- bulk reservoir capacitance

They serve different purposes.

---

# 18. CLASS-D / FAST SWITCHING DESIGN

Treat Class-D power stages as high-speed switching converters.

Critical items include:

- gate loop inductance
- driver placement
- bootstrap loop
- PVDD decoupling loop
- dead time
- switch-node area
- MOSFET capacitance
- reverse recovery
- output-filter placement
- ground return geometry

For each half bridge:

- place gate driver close to MOSFET pair
- place gate resistor close to MOSFET gate
- keep HO/HS loop short
- keep LO/VSS loop short
- Kelvin-reference driver return where practical
- keep local PVDD decoupling extremely close
- keep switch-node copper compact
- place output inductor close to switch node

Do not place large ground-plane copper directly beneath large high-dV/dt switch-node copper if avoiding it reduces parasitic capacitance.

Do not use enormous MOSFETs with unnecessary gate charge simply to minimise RDS(on).

For modest-power Class-D designs, switching behaviour may matter more than achieving extremely low conduction resistance.

---

# 19. MOSFET SELECTION

For switching applications consider:

- VDS margin
- RDS(on)
- total gate charge Qg
- Miller charge Qgd
- output capacitance
- reverse-recovery behaviour
- package thermal performance
- switching speed
- actual operating current

Do not choose purely by current rating.

For moderate-current high-frequency designs, a slightly higher RDS(on) device with much lower gate charge may be preferable.

Always verify the package pinout.

---

# 20. GATE DRIVERS

Use dedicated gate drivers when appropriate.

Check:

- source current
- sink current
- propagation delay
- propagation matching
- UVLO
- bootstrap requirements
- logic thresholds
- dead-time behaviour
- input interlock

Do not assume a gate driver automatically provides suitable dead time.

If dead time is externally generated, mark timing components as provisional until measured.

---

# 21. CLASS-D OUTPUT FILTERS

For BTL output filters:

- remember that the speaker is differential
- do not ground either speaker terminal
- calculate effective differential inductance/capacitance correctly
- use low-loss capacitors
- place the main differential filter capacitor close to the inductor output

A differential capacitor between BTL outputs is acceptable and often preferable.

A Zobel network performs a different function from the main LC capacitor.

Do not confuse the two.

Optional small common-mode capacitors to GND may be provided as DNP footprints where EMI tuning may later require them.

---

# 22. ANALOGUE / DIGITAL SEPARATION

Do not separate analogue and digital by arbitrary ground-plane cuts.

Instead:

- separate physically
- control return paths
- decouple locally
- route clocks away from analogue inputs
- keep switching nodes away from references and high-impedance nodes

Sensitive references such as:

VREF
DAC reference
ADC reference
op-amp virtual ground

should be treated as quiet analogue nets.

---

# 23. DIGITAL SIGNAL ROUTING

For fast digital signals such as:

I2S
SPI
clocks

consider:

- source termination
- short routes
- continuous ground reference
- minimal stubs
- avoiding analogue areas

Small series resistors near the driving device are often preferable to arbitrary filtering.

Do not add ferrite beads automatically.

The user generally prefers to avoid ferrite beads unless they solve a specific demonstrated problem.

---

# 24. AUDIO OUTPUT / SPEAKER CONNECTORS

For BTL amplifiers:

- neither speaker terminal is ground
- label outputs clearly
- prevent accidental ground assumptions in schematic and silkscreen

Use adequately rated connectors and copper.

---

# 25. MAINS SAFETY

The user operates from UK 230 V mains.

Any mains-powered design must treat safety as a primary requirement.

For mains circuitry:

- maintain suitable creepage
- maintain suitable clearance
- use correctly rated fuses
- use correctly rated switches/connectors
- use X/Y safety capacitors where required
- use appropriately rated MOVs/NTCs
- maintain protective-earth integrity where applicable
- clearly separate SELV and mains areas
- avoid copper under isolation gaps where inappropriate

Do not casually reduce creepage/clearance to save PCB space.

Mains safety takes priority over compactness.

---

# 26. THERMAL DESIGN

Calculate dissipation for:

- regulators
- MOSFETs
- BJTs
- rectifiers
- power resistors
- inductors

Do not rely only on datasheet headline wattage/current.

Consider:

- copper area
- exposed pads
- thermal vias
- ambient temperature
- enclosure conditions
- neighbouring heat sources

Flag components that require bench thermal validation.

---

# 27. PROTECTION

Do not automatically add elaborate protection to every prototype.

But always consider whether the design needs:

- overcurrent protection
- DC speaker protection
- thermal protection
- startup mute
- undervoltage behaviour
- reverse polarity protection
- fuse protection
- inrush limiting

For experimental Rev 1 circuits, provision/DNP footprints may be preferable to adding unnecessary complexity immediately.

---

# 28. TESTABILITY

Design for bench testing.

Add useful test points for important nodes such as:

- supply rails
- GND
- references
- clocks
- PWM
- driver outputs
- switching nodes
- filtered outputs
- enable lines
- fault lines

Do not add test points to extremely sensitive or high-frequency nodes if their pad/copper area would materially harm performance.

Clearly label hazardous/high-dV/dt test points.

---

# 29. MEASUREMENT-FIRST APPROACH

Where practical, design so uncertain parameters can be measured and tuned.

Examples:

- MOSFET gate resistance
- Class-D dead time
- RC snubbers
- output-filter damping
- amplifier bias
- feedback compensation

Use DNP footprints or selectable values where useful.

Do not claim final optimisation before bench measurements.

---

# 30. ERC / DRC

Always run ERC after significant schematic changes.

Always run DRC after significant PCB changes.

Do not suppress errors simply to produce a clean report.

If an ERC/DRC warning is intentionally accepted:

- explain why
- document it

Do not hide genuine problems with exclusions.

---

# 31. PCB ROUTING BY AGENT

Do not autoroute an entire analogue/audio/power board unless specifically requested.

For sensitive designs, route only well-defined sections when instructed.

Examples suitable for limited automated routing:

- local supply rails
- low-speed logic
- clearly defined point-to-point nets
- repetitive non-critical routing

Critical routes should be treated conservatively:

- Class-D switch nodes
- MOSFET gate loops
- current-sense paths
- analogue reference nodes
- high-gain feedback nodes
- crystal/clock loops
- mains isolation areas

If uncertain, stop and report rather than guessing.

---

# 32. GIT / CHANGE CONTROL

Before major automatic schematic or PCB changes:

- preserve the existing working design
- preferably commit the current state to Git

Do not make widespread formatting, symbol, footprint and topology changes in one uncontrolled step.

Keep changes scoped.

After significant work, report:

- what changed
- why it changed
- files modified
- any assumptions
- any unresolved issues

---

# 33. PROJECT-SPECIFIC RULES

A project-specific AGENTS.md may add:

- exact supply voltages
- exact IC selections
- fixed topology
- target power
- switching frequency
- connector requirements
- specific grounding rules
- special layout constraints
- PCB dimensions
- reserved inventory parts

Project-specific requirements override generic preferences where they conflict.

Do not infer project-specific requirements from unrelated previous projects.

---

# 34. WHEN SOMETHING IS UNCERTAIN

Stop and report uncertainty for things such as:

- ambiguous symbol pin mapping
- uncertain footprint
- unclear datasheet revision
- undocumented connector pinout
- conflicting manufacturer information
- uncertain polarity
- possible thermal violation
- questionable stability
- unclear existing schematic intent

Do not "make it work" by guessing.

---

# 35. FINAL REVIEW EXPECTATION

Before calling a design complete, review:

- every supply voltage
- every IC supply pin
- every exposed pad
- every ground connection
- every connector pin
- every MOSFET/transistor pin
- every diode polarity
- electrolytic polarity
- regulator feedback
- enable/reset pins
- unused inputs
- startup states
- local decoupling
- component voltage ratings
- component power ratings
- footprint/package match
- testability
- ERC/DRC status

A clean ERC/DRC report is necessary but is not proof that the hardware design is correct.

Always distinguish:

- schematic verified
- layout verified
- simulated
- bench tested
- thermally tested
- production ready

These are not equivalent states.

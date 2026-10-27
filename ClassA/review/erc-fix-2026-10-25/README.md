# Current-mirror ERC repair

Added one junction at (170.18, 154.94) mm: Q5 collector and Q2 collector now connect to the common Q4/Q5 bases, restoring the intended diode-connected reference transistor. No other schematic object, value, pin mapping, footprint or inventory field changed. PCB, project and preferences hashes are unchanged.

ERC: 1 error before, 0 errors/0 warnings after. Eight scoped checks pass; the 189 inventory/assignment checks also pass with only this authorized net merge permitted. This is a schematic repair, not bench or thermal qualification.

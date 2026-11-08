#!/usr/bin/env python3
"""Swap Y1 (HC49 2-pin) for Wurth 830108338809 3225 4-pad crystal."""
import re, sys, uuid
src, dst = sys.argv[1], sys.argv[2]
LIB = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Device.kicad_sym"
U = lambda: str(uuid.uuid4())
t = open(src).read()

def match(s, i):
    d, j = 0, i
    while True:
        c = s[j]
        if c == '"':
            j += 1
            while s[j] != '"':
                j += 2 if s[j] == '\\' else 1
        elif c == '(':
            d += 1
        elif c == ')':
            d -= 1
            if d == 0:
                return j
        j += 1

# 1. embed Device:Crystal_GND24, drop unused Device:Crystal
lib = open(LIB).read()
i = lib.find('\n\t(symbol "Crystal_GND24"\n') + 2
blk = lib[i:match(lib, i) + 1].replace('(symbol "Crystal_GND24"', '(symbol "Device:Crystal_GND24"', 1)
blk = "\n".join("\t" + l for l in blk.split("\n"))
ci = t.find('\t\t(symbol "Device:Crystal"\n')
assert ci > 0 and t.count('(lib_id "Device:Crystal")') == 1
ce = match(t, ci + 2)
t = t[:ci] + blk.lstrip("\n") + t[ce + 1:]

# 2. rewrite the Y1 instance
ri = t.find('(property "Reference" "Y1"')
s = t.rfind('\n\t(symbol\n', 0, ri) + 1
e = match(t, s + 1) + 1
old = t[s:e]
uid = re.search(r'\(uuid "([^"]+)"\)', old).group(1)
X, Y = 116.84, 162.56
assert '(at 116.84 162.56 0)' in old

def prop(name, val, x, y, ang=0, hide=True):
    h = "\n\t\t\t(hide yes)" if hide else ""
    return f'''\t\t(property "{name}" "{val}"
\t\t\t(at {x} {y} {ang}){h}
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
'''
new = f'''\t(symbol
\t\t(lib_id "Device:Crystal_GND24")
\t\t(at {X} {Y} 0)
\t\t(unit 1)
\t\t(body_style 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(in_pos_files yes)
\t\t(dnp no)
\t\t(uuid "{uid}")
'''
new += prop("Reference", "Y1", X, 162.814, 90, False)
new += prop("Value", "12MHz", X, 177.8, 0, False)
new += prop("Footprint", "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm", X, Y)
new += prop("Datasheet", "https://www.we-online.com/catalog/datasheet/830108338809.pdf", X, Y)
new += prop("Description", "12 MHz crystal, 12 pF CL, 120R ESR max, 100uW max drive, 3.2x2.5mm 4-pad (1,3 crystal; 2,4 GND/lid)", X, Y)
new += prop("Manufacturer", "Wurth Elektronik", X, Y)
new += prop("MPN", "830108338809", X, Y)
new += prop("Mouser Part Number", "710-830108338809", X, Y)
new += prop("Source", "ORDER (Mouser)", X, Y)
for n in "1234":
    new += f'\t\t(pin "{n}"\n\t\t\t(uuid "{U()}")\n\t\t)\n'
new += '''\t\t(instances
\t\t\t(project "2706ES9033"
\t\t\t\t(path "/38bf17a7-0851-4df1-8df7-1c8ac1c1974f"
\t\t\t\t\t(reference "Y1")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)'''
t = t[:s] + new + t[e:]

# 3. GND for pads 2/4: wire from (116.84,167.64) down to GND symbol at 170.18
n = max(int(x) for x in re.findall(r'"#PWR(\d+)"', t)) + 1
gref = f"#PWR{n:03d}"
gi = t.find('\t(symbol\n\t\t(lib_id "power:GND")')
ge = match(t, gi + 1) + 1
g = t[gi:ge]
m = re.search(r'\(at ([-\d.]+) ([-\d.]+) 0\)', g)
gx, gy = float(m.group(1)), float(m.group(2))
g = g.replace(f"(at {m.group(1)} {m.group(2)} ", "(at @X@ @Y@ ")
g = re.sub(r'\(at ([-\d.]+) ([-\d.]+) (\d+)\)', lambda mm: f"(at {round(float(mm.group(1)) - gx + X, 4):g} {round(float(mm.group(2)) - gy + 170.18, 4):g} {mm.group(3)})", g)
g = g.replace("(at @X@ @Y@ ", f"(at {X} 170.18 ")
g = re.sub(r'\(reference "#PWR\d+"\)', f'(reference "{gref}")', g)
g = re.sub(r'\(property "Reference" "#PWR\d+"', f'(property "Reference" "{gref}"', g)
g = re.sub(r'\(uuid "[^"]+"\)', lambda mm: f'(uuid "{U()}")', g)
wire = f'''\t(wire
\t\t(pts
\t\t\t(xy 116.84 167.64) (xy 116.84 170.18)
\t\t)
\t\t(stroke
\t\t\t(width 0)
\t\t\t(type default)
\t\t)
\t\t(uuid "{U()}")
\t)
'''
ins = t.rfind("\t(sheet_instances")
t = t[:ins] + g + "\n" + wire + t[ins:]
open(dst, "w").write(t)
print("ok", gref)

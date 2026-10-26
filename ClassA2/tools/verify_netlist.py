#!/usr/bin/env python3
"""Cross-check the KiCad netlist (exported by kicad-cli) against simulation/amp.cir.

Each schematic part carries a 'spice' map {pin number: SPICE node} (tools/parts.json, written by
build_schematic.py). This script checks that
  1. every SPICE element in amp.cir exists in the schematic with the same nodes (pin by pin), and
  2. the KiCad nets partition the pins exactly as the SPICE nodes do (no extra or missing joins).
Connectors/test points (not in the SPICE deck) are checked through their 'spice' maps only."""
import json, re, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
K = '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
NET = ROOT / 'work' / 'ClassA2.net'
subprocess.run([K, 'sch', 'export', 'netlist', '--format', 'kicadsexpr', '-o', str(NET), str(ROOT / 'ClassA2.kicad_sch')], check=True, capture_output=True)
txt = NET.read_text()
nets = {}
for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]*)"\)(.*?)\)\s*(?=\(net |\)\s*\)\s*$)', txt, re.S):
    nets[m.group(1)] = set(re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', m.group(2)))
if not nets:  # tolerate multi-line formatting
    for blk in re.split(r'\(net\s*\(code', txt)[1:]:
        name = re.search(r'\(name\s*"([^"]*)"', blk).group(1)
        nets[name] = set(re.findall(r'\(ref\s*"([^"]+)"\)\s*\(pin\s*"([^"]+)"\)', blk))
parts = json.loads((ROOT / 'tools' / 'parts.json').read_text())
pin2net = {p: n for n, ps in nets.items() for p in ps}
errors = []
# --- SPICE deck elements (top level of subckt AMP)
cir = (ROOT / 'simulation' / 'amp.cir').read_text()
body = cir[cir.index('.subckt'):cir.index('.ends')]
spice = {}
for line in body.splitlines()[1:]:
    line = line.split('*')[0].strip()
    if not line or line.startswith('+'): continue
    tok = line.split()
    spice[tok[0].upper()] = tok[1:]
# map SPICE element -> schematic part / pin order
order = {'Q': ['C', 'B', 'E'], 'R': ['1', '2'], 'C': ['1', '2'], 'D': ['A', 'K'], 'L': ['1', '2']}
checked = set()
for el, tok in spice.items():
    if el.startswith('RV2'):   # RV2a/RV2b model the trimmer track halves
        continue
    ref = el
    if el == 'RV1':
        ref = 'RV1'
    if ref not in parts:
        errors.append(f'{el}: in amp.cir but not in schematic'); continue
    p = parts[ref]
    sp = p['spice']
    kind = el[0] if el != 'RV1' else 'RV'
    if kind == 'RV':
        want = {'1': tok[0], '3': tok[1], '2': tok[1]}
    else:
        if kind == 'Q':
            nodes = dict(zip(['C', 'B', 'E'], tok[:3]))
            # schematic spice map is by pin number; invert through pin names from the part's lib symbol
            names = {'Transistor_BJT:Q_NPN_ECB': 'ECB', 'Transistor_BJT:Q_PNP_ECB': 'ECB', 'Transistor_BJT:Q_NPN_BCE': 'BCE',
                     'Transistor_BJT:Q_PNP_BCE': 'BCE', 'Transistor_BJT:Q_NPN_CBE': 'CBE', 'Transistor_BJT:Q_PNP_CBE': 'CBE'}[p['lib_id']]
            want = {str(i+1): nodes[c] for i, c in enumerate(names)}
        elif kind == 'D':
            want = {'2': tok[0], '1': tok[1]}       # Device:D pin 1 = K, 2 = A
        else:
            a, b = tok[0], tok[1]
            if set(sp.values()) == {a, b} and sp.get('1') == b and sp.get('2') == a:
                want = {'1': b, '2': a}             # two-terminal parts may be drawn either way round
            else:
                want = {'1': a, '2': b}
    if want != sp:
        errors.append(f'{el}: amp.cir nodes {want} != schematic map {sp}')
    checked.add(ref)
# RV2 track ends and wiper from RV2a/RV2b
a, b = spice['RV2A'], spice['RV2B']
want = {'3': a[0], '2': a[1], '1': b[1]}
if parts['RV2']['spice'] != want: errors.append(f"RV2: {want} != {parts['RV2']['spice']}")
checked.add('RV2')
for ref in parts:
    if ref not in checked and not ref.startswith(('J', 'TP')):
        errors.append(f'{ref}: in schematic but not in amp.cir')
# --- net partition check
groups = {}
for ref, p in parts.items():
    for pin, node in p['spice'].items():
        groups.setdefault(node, set()).add((ref, pin))
for node, pins in groups.items():
    kn = {pin2net.get(x, '<unconnected>') for x in pins}
    if len(kn) != 1:
        errors.append(f'SPICE node {node}: pins split across KiCad nets {sorted(kn)} -> {sorted(pins)}')
    else:
        n = kn.pop()
        extra = {x for x in nets.get(n, set()) if x[0] in parts} - pins
        if extra: errors.append(f'KiCad net {n} (SPICE {node}) has extra pins {sorted(extra)}')
rail_names = {'0': 'GND', 'VP': '+V', 'VN': '-V', 'VPF': '+VF', 'VNF': '-VF'}
for node, want in rail_names.items():
    got = {pin2net.get(x) for x in groups.get(node, [])}
    if got != {want}: errors.append(f'rail {node} expected net name {want}, got {got}')

# --- value cross-check (schematic Value field vs SPICE value)
PARAMS = dict(re.findall(r'(\w+)=([^\s]+)', body.splitlines()[0].split('params:')[1]))
def num(s):
    s = s.strip().split('/')[0].split()[0].replace('{', '').replace('}', '')
    s = PARAMS.get(s, s)
    m = re.fullmatch(r'(\d*)([RrKkMmUuNnPp]?)(\d*)', s)          # KiCad style: 4k7, 0R33, 2u2, 100p
    mult = dict(r=1, k=1e3, m=1e6, u=1e-6, n=1e-9, p=1e-12)
    if m and m.group(2) and (m.group(1) or m.group(3)):
        a, u, b = m.groups()
        return float((a or '0') + '.' + (b or '0')) * mult[u.lower()]
    m = re.fullmatch(r'([\d.]+)(meg|[kmunp])?', s.lower())
    if m:
        return float(m.group(1)) * dict(meg=1e6, k=1e3, m=1e-3, u=1e-6, n=1e-9, p=1e-12).get(m.group(2), 1)
    return None
for el, tok in spice.items():
    if el[0] not in 'RCL' or el.startswith('RV') or el not in parts: continue
    sv, kv = num(tok[2]), num(parts[el]['value'])
    if parts[el]['dnp']: continue
    if sv is None or kv is None or abs(sv - kv) > 0.011 * max(abs(sv), abs(kv)):
        errors.append(f"{el}: value mismatch schematic {parts[el]['value']!r} vs amp.cir {tok[2]!r}")
summary = dict(kicad_nets=len(nets), parts=len(parts), spice_elements=len(spice), errors=errors)
(ROOT / 'work' / 'netlist_check.json').write_text(json.dumps(summary, indent=1))
print(json.dumps(summary, indent=1))
sys.exit(1 if errors else 0)

#!/usr/bin/env python3
"""BOM.csv for ClassA2 Rev A from tools/parts.json (written by build_schematic.py). Quantities per channel and for stereo (x2)."""
import csv, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
parts = json.loads((ROOT / 'tools' / 'parts.json').read_text())
def metric(fp):
    m = re.search(r'_(\d{4})Metric', fp)
    return f'{m.group(1)} metric SMD' if m else ('THT' if fp else '')
def refkey(r):
    m = re.match(r'([A-Z]+)(\d+)', r); return (m.group(1), int(m.group(2)))
groups = {}
for ref, p in parts.items():
    if not p['inbom']: continue
    k = (p['lib_id'].split(':')[1].split('_')[0] if not p['lib_id'].startswith('Transistor') else 'Q', p['value'], p['mpn'], p['fp'], p['dnp'])
    groups.setdefault(k, []).append(ref)
rows = []
for k, refs in groups.items():
    refs.sort(key=refkey); p = parts[refs[0]]
    rows.append(dict(References=' '.join(refs), Qty_per_channel=0 if p['dnp'] else len(refs), Qty_stereo=0 if p['dnp'] else 2*len(refs),
                     Value=p['value'], Description=p['desc'], Manufacturer=p['mfr'], MPN=p['mpn'], Rating=p['rating'],
                     Package=metric(p['fp']), KiCad_footprint=p['fp'], Inventory=p['stock'], DNP='DNP' if p['dnp'] else '',
                     Notes=p['notes'], Datasheet=p['ds']))
rows.sort(key=lambda r: refkey(r['References'].split()[0]))
with open(ROOT / 'BOM.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(len(rows), 'lines,', sum(r['Qty_per_channel'] for r in rows), 'parts per channel')

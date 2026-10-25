#!/usr/bin/env python3
"""Generate stereo BOM from exported KiCad XML and read-only inventory snapshots."""
from pathlib import Path
import csv,json,xml.etree.ElementTree as ET,collections
P=Path(__file__).resolve().parents[1]
stock={}
def walk(o):
 if isinstance(o,dict):
  if 'inventory_id' in o and ('quantity' in o or 'physical_quantity' in o):stock[str(o['inventory_id'])]=o
  for v in o.values():walk(v)
 elif isinstance(o,list):
  for v in o:walk(v)
for f in ['raw_snapshot.json','detail_snapshot.json']:walk(json.loads((P/'inventory'/f).read_text()))
groups=collections.defaultdict(list)
for c in ET.parse(P/'work/stereo.xml').findall('components/comp'):
 fs={f.get('name'):f.text or '' for f in c.findall('fields/field')}
 if c.get('ref').startswith('RV'):fs['Inventory_ID']='529'
 k=(c.findtext('value'),fs.get('MPN',''),c.findtext('footprint'),fs.get('Inventory_ID',''))
 groups[k].append((c.get('ref'),fs.get('Design_note',''),c.findtext('datasheet') or ''))
rows=[]
for (value,mpn,fp,id),parts in sorted(groups.items(),key=lambda z:z[1][0][0]):
 item=stock.get(id,{})
 available=item.get('quantity','')
 n=len(parts);buy=max(0,n-int(available)) if available!='' else n
 status='STOCK' if available!='' and buy==0 else 'PURCHASE'
 note='; '.join(sorted(set(p[1] for p in parts if p[1])))
 if parts[0][0].startswith('RV'):
  status='CONDITIONAL STOCK';buy=n;note+='; Stock 529 generic pot: use only after body/pinout and fail-low wiring checks; otherwise buy exact MPN.'
 if parts[0][0].startswith('L'):
  status='WIND';buy=0;note+='; Wire stock unconfirmed; verify inductance before layout.'
 if parts[0][0].startswith('TP'):
  status='WIRE LOOP';buy=0;note+='; Ten soldered wire loops, wire stock unconfirmed.'
 if id=='288':note+='; Verify actual resistor length/diameter/lead pitch against assigned generous footprint.'
 rating=' / '.join(str(item.get(z,''))+((' W' if z=='power_rating' else '') if str(item.get(z,'')) and not str(item.get(z,'')).lower().endswith('w') else '') for z in ['voltage_rating','power_rating','tolerance'] if item.get(z,''))
 if not rating:
  rating={'C315C331J5G5TA':'50 V / 5%','LR1F130R':'0.6 W / 1%','ROX2SJ10R':'2 W / 5%','BZX79-C4V3':'500 mW / 5%','BAT46-TR':'100 V / 150 mA / 150 mW with specified lead cooling','3296W-1-202LF':'0.5 W at 70 C; derate above','1715734':'PCB connector; use within manufacturer rating','1715721':'PCB connector; use within manufacturer rating'}.get(mpn,'')
 if mpn.startswith('IRF'):note+='; Voltage/current/power inventory ratings are absolute/conditional switching ratings, not an audio SOA approval.'
 maker=item.get('manufacturer','')
 if not maker:maker={'C315C331J5G5TA':'KEMET','LR1F130R':'TE Connectivity','ROX2SJ10R':'TE Connectivity','BZX79-C4V3':'Nexperia','IRF540NPbF':'Infineon Technologies','BAT46-TR':'Vishay','1715734':'Phoenix Contact','1715721':'Phoenix Contact'}.get(mpn,'Workshop fabrication' if status in ['WIND','WIRE LOOP'] else '')
 if status=='CONDITIONAL STOCK':maker='Owned generic; Bourns if purchased'
 rows.append(dict(References=', '.join(p[0] for p in parts),Value=value,Manufacturer=maker,MPN=mpn,Required=n,Inventory_ID=id,Available=available,Reserved=item.get('reserved_quantity',''),Minimum_buy=buy,Status=status,Stock_package=item.get('package',''),Rating=rating,Footprint=fp,Datasheet=next((p[2] for p in parts if p[2]),item.get('datasheet_url','')),Notes=note.strip('; ')))
with (P/'BOM.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
with (P/'inventory/selected_stock.json').open('w') as f:json.dump({r['Inventory_ID']:stock.get(r['Inventory_ID'],{}) for r in rows if r['Inventory_ID']},f,indent=2)
print('BOM:',sum(r['Required'] for r in rows),'parts in',len(rows),'groups. Inventory unchanged.')

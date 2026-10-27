from pathlib import Path
import sys,json,csv,collections,hashlib,xml.etree.ElementTree as E,math
sys.path.insert(0,'review/scripts');from schlib import *
p=Path('review/revisions/preorder-corrections-2026-10-23')
invdata=json.loads((p/'inventory.json').read_text());inv={str(x['id']):x['part'] for x in invdata['parts']}
rows=[]
for fn in ['TPA3126','ESP32','DAC','Amp','Power']:
 for s in many(load(fn+'.kicad_sch'),'symbol'):
  ref=val(s,'Reference')
  if ref.startswith('#'):continue
  iid=val(s,'Inventory_ID') or '';stock=inv.get(iid);mpn=val(s,'MPN') or ''
  mech=ref.startswith(('H','TP')) or ref=='JP1'
  if mech:
   disposition='No electronic part; wire link optional' if ref=='JP1' else ('Physical fit checked by user; ownership not counted by MCP' if ref=='HS1' else 'No electronic part')
  elif stock:
   if stock.get('physical_quantity',0)>=1:disposition='Use confirmed inventory'
   elif stock.get('on_order_quantity',0)>=1:disposition='Await existing order; not physically in stock'
   else:disposition='Purchase required'
  else:disposition='Purchase unless separately held; no confirmed stock'
  if ref=='J3':disposition='Generic 1x4 straight 2.54 mm male header; physical stock check needed'
  rows.append({'reference':ref,'sheet':fn,'value':val(s,'Value'),'footprint':val(s,'Footprint') or '', 'manufacturer':val(s,'Manufacturer_Name') or (stock or {}).get('manufacturer',''),'mpn':mpn,'inventory_id':iid,'confirmed_physical_quantity':None if stock is None else stock.get('physical_quantity'),'reserved_quantity':None if stock is None else stock.get('reserved_quantity'),'on_order_quantity':None if stock is None else stock.get('on_order_quantity'),'dnp':str(get(s,'dnp')[1])=='yes','on_board':str(get(s,'on_board')[1])=='yes','voltage':val(s,'Voltage_Rating') or '', 'dielectric':val(s,'Dielectric') or '', 'power':val(s,'Power_Rating') or '', 'assembly_note':val(s,'Assembly_Note') or '', 'disposition':disposition})
rows.sort(key=lambda r:(re.sub(r'\d','',r['reference']),int(re.search(r'\d+',r['reference']).group() or 0)))
with (p/'BOM.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
result={'snapshot_date':'2026-10-23','scope':'Current fitted BOM after scoped pre-order schematic corrections','account_link':invdata['account_link'],'items':rows}
(p/'bom-and-inventory.json').write_text(json.dumps(result,indent=2)+'\n')
Path('review/bom-and-inventory.json').write_text(json.dumps(result,indent=2)+'\n')
groups=collections.defaultdict(list)
for r in rows:
 if r['reference'].startswith(('H','TP')) or r['reference']=='JP1':continue
 groups[(r['mpn'],r['inventory_id'],r['footprint'],r['value'].lower())].append(r)
lines=['# Current inventory usage — 23 October 2026','','Generated from the saved schematics after the pre-order corrections. MCP physical quantities are confirmed totals, not allocations. All queried reserved quantities are zero. On-order stock is shown separately. No inventory records were changed. Repeated stock totals are not additive.','','| References / value | MPN or stock identity | Required | Confirmed physical | On order | Disposition |','|---|---|---:|---:|---:|---|']
buy=['# Current purchasing list — 23 October 2026','','This list supersedes earlier lists containing J18, removed LEDs and old snubber references. It lists PCB electronic parts lacking confirmed physical stock, plus generic programming header J3. No order has been placed. Recheck cart availability at checkout.','','| References | Part | Required | Status |','|---|---|---:|---|']
for key,rs in groups.items():
 r=rs[0];refs=', '.join(x['reference'] for x in rs);mpn=r['mpn'] or ('Inventory ID '+r['inventory_id']+'; exact MPN unrecorded' if r['inventory_id'] else 'Generic 1x4 straight 2.54 mm male header');qty=len(rs)
 physical=r['confirmed_physical_quantity'];order=r['on_order_quantity'];status=r['disposition']
 lines.append(f"| {refs}: {r['value']} | {mpn} | {qty} | {'Not confirmed' if physical is None else physical} | {'Not queried' if order is None else order} | {status} |")
 if physical is None or physical<qty:buy.append(f'| {refs} | {mpn} | {qty} | {status} |')
lines+=['','C1/C2/C5/C6 now identify the exact owned KEMET R82DC4100AA60J, not a WIMA fallback. MCP confirms 43; manufacturer specifies 5 mm lead spacing and 7.2 x 5 x 10 mm body. C45 uses the owned Samsung CL31A106KBHNNNE; DC-bias/ripple assessment is documented in the correction report.','','HS1 heatsink and C21 fit were checked by the user. That confirmation is not an inventory count. Mounting holes/test pads need no electronic purchase; JP1 uses an optional short insulated wire link rated at least 3 A.']
buy+=['','C28 (100 on order) and C30/C31/C33/C34/C46/C48/C53 (1000 on order) need not be ordered twice; await receipt or confirm delivery. PCM5122 inventory is zero. C21 fit was checked by the user, but possession/quantity is not confirmed in MCP.','','Separate system items: suitable external antenna/coax, heatsink/TIM/fasteners, DC supply, volume pot/button/LEDs, speaker wiring, and connector mating housings/contacts. J2 is JST XH 8-way: matching XHP-8 housing and suitable SXH contacts; J1/J16/J17 use the retained Molex series. These are not silently counted as owned or added to a PCB-only parts order.','','Known selected output-RC purchase: CRCW08053R30FKEAHP (DigiKey 541-3.30TCT-ND), four required. The 10n C0G capacitors are confirmed inventory ID297. Supplier availability is a time-sensitive snapshot, not a guaranteed reservation.']
for path,content in [('INVENTORY-USAGE.md',lines),('PURCHASING-LIST.md',buy)]:
 (p/path).write_text('\n'.join(content)+'\n');Path('review',path).write_text('\n'.join(content)+'\n')
# Preserve all electrical objects and board boundaries.
h=json.loads((p/'before-hashes.json').read_text());checks={}
for fn in ['TPA3126','ESP32','DAC','Amp','Power']:
 old=load(p/'before'/(fn+'.kicad_sch'));new=load(fn+'.kicad_sch')
 def strip(n):return [x for x in n if not (isinstance(x,list) and x[0] in ['property','text','title_block'])]
 def canon(n):return [strip(x) if isinstance(x,list) and x[0]=='symbol' else x for x in strip(n)]
 assert canon(old)==canon(new),fn+' non-property object changed'
 checks[fn+' electrical/graphical objects retained']=True
 for r in many(new,'symbol'):
  oldr=next(x for x in many(old,'symbol') if get(x,'uuid')==get(r,'uuid'))
  assert val(oldr,'Footprint')==val(r,'Footprint')
  assert val(oldr,'Value')==val(r,'Value')
  if val(r,'MPN') and val(r,'Manufacturer_Part_Number'):assert val(r,'MPN')==val(r,'Manufacturer_Part_Number')
checks['all component values and footprint assignments unchanged']=True
for fn in ['TPA3126.kicad_pcb','TPA3126.kicad_pro','TPA3126.kicad_prl']:
 checks[fn+' unchanged']=hashlib.sha256(Path(fn).read_bytes()).hexdigest()==h[fn]
def nets(r):return {frozenset((n.get('ref'),n.get('pin')) for n in x.findall('node')) for x in r.findall('./nets/net')}
assert nets(E.parse('review/preorder-2026-10-23/schematic.xml'))==nets(E.parse(p/'after.xml'))
checks['complete netlist connectivity unchanged']=True
j=json.loads((p/'erc.json').read_text());v=[v for sh in j['sheets'] for v in sh['violations']]
def sig(j):return sorted((v['type'],v['severity'],tuple(sorted(x['uuid'] for x in v['items']))) for sh in j['sheets'] for v in sh['violations'])
assert sig(j)==sig(json.loads(Path('review/preorder-2026-10-23/erc.json').read_text()))
checks['ERC warning signatures unchanged']=True
ver={'checks':checks,'ERC_errors':sum(x['severity']=='error' for x in v),'ERC_warnings':sum(x['severity']=='warning' for x in v),'source_hashes_after':{str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in [*Path('.').glob('*.kicad_sch'),Path('TPA3126.kicad_pcb'),Path('TPA3126.kicad_pro'),Path('TPA3126.kicad_prl')]}}
(p/'verification.json').write_text(json.dumps(ver,indent=2)+'\n')
print('Generated current BOM, inventory/purchasing lists and verification:',len(rows),'components;',ver['ERC_errors'],'ERC errors;',ver['ERC_warnings'],'warnings')
print(json.dumps(checks,indent=2))

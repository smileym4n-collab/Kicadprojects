from schlib import *
import json
pool={}
for fn in Path('review').glob('inventory-*.json'):
 data=json.loads(fn.read_text())
 def walk(v):
  if isinstance(v,dict):
   if 'inventory_id' in v:pool[v['inventory_id']]=v
   for vv in v.values():walk(vv)
  elif isinstance(v,list):
   for vv in v:walk(vv)
 walk(data)
# BOM-to-inventory mappings are explicit, package-aware selections, not value-only substitutions.
mapping={}
def assign(refs,id,mpn=None,comment='',purchase='No'):
 for ref in refs.split(','):mapping[ref]={'inventory_id':id,'mpn':mpn,'comment':comment,'purchase':purchase}
assign('U1',734,'TPA3126D2DADR','Salvaged IC; inventory model TPA3126. Verify recovered part marking and solderability.')
assign('U2',491,'PCM5122PWR','MCP explicitly reports zero. Existing circuit does not establish ownership.','Yes')
assign('IC5',96,'ESP32-WROVER-IE-N16R8')
assign('U3',97,'LMR51430XFDDCR','Retain FPWM suffix XF; inventory quantity 1.')
assign('IC4',28,'TPS7A2033PDBVR')
assign('U4',None,'TLV1117LV33DCYR','No matching inventory record. Do not substitute TS1117B.','Yes')
assign('L1',329,'SRP6030WA-6R8M')
assign('L2,L3',520,'CSAD0660-100M','Two packages, two independent windings each. Inventory reserved quantity zero.')
assign('Q1',298,'DMP4015SK3-13')
assign('D1',495,'1N4740ATR')
assign('D2',None,'SMBJ16A','Littelfuse, unidirectional SMB. No matching MCP record.','Yes')
assign('D3',639,'KP-2012LSGC')
assign('D4',640,'KP-2012EC')
assign('IC2,IC3',537,'TS02-66-50-BK-100-SCR-D')
assign('J1,J16,J17',722,'09-65-2028','Exact stock series 5273 footprint assigned.')
assign('J2',691,'MC34635')
assign('J18',126,'MC34629','External cap loop; rated wire link or shunt for stereo, power off before changing.')
assign('F2',None,'39613150000','Time-delay TE5, 3.15 A / 125 V. Existing 395 footprint shares TE5 mechanical case.','Yes')
assign('C1,C2,C5,C6',132,'MKS2C041001F00JSSD','Stock is Kemet generic 1u / 63 V, body noted 7x5 mm. Check 5 mm pitch; WIMA MPN is a verified purchase fallback, not a claim about stock identity.','Conditional: only if stock pitch/type fails check')
assign('C3,C11,C15,C17,C22,C30,C31,C33,C34',157,'C1206C104K5RACTU')
assign('C4,C8,C9,C28,C29,C32',181,'CL31B105KBHNFNE')
assign('C7',426,'UFW1H100MDD')
assign('C10',442,'UFW1E220MDD')
assign('C12,C14',182,'CL21B225KPFNNNE','Charge pump MLCC; verify effective capacitance and ripple on bench.')
assign('C13,C20,C23,C51,C52',184,'CL21A106KOQNNNF')
assign('C16,C19',161,'0805N272J500CT')
assign('C18',135,'TMK316B7106KL-TD')
assign('C24,C25,C26,C27',84,'CL21B224KAFNNNE')
assign('C35,C36,C47',366,'35ZLH220MEFC8X11.5')
assign('C37,C38,C39,C40',None,'ECW-FE2W684J','Panasonic 680n, 450 V DC, 5% polypropylene; 17.5x7x12.5 mm, pitch 15 mm, leads 0.8 mm. DigiKey 10-ECW-FE2W684J-ND. No matching MCP inventory record.','Yes')
assign('C41,C42,C43,C44',569,'GMC21CG331J50NT','DNP tuning parts. No purchase for initial build.')
assign('C45',None,'GRM32ER71H106KA12L','10u / 50 V X7R, 3225 metric, retain inherited footprint. Owned 3216 parts are not substituted.','Yes')
assign('C46,C48,C53',698,'MC0603B104K500CT','100n / 50 V X7R, 1608 metric; exact inventory record has zero.','Yes')
assign('C49,C50,C55',202,'CL31A226KAHNNNE')
assign('C54',None,'UES1H470MPM','External 47u / 50 V bipolar, 10x20 mm, 5 mm pitch. No matching MCP record.','Yes')
assign('R1',335,'','Multicomp Pro 2R2, 1%, 2012; exact MPN not recorded.')
assign('R2,R3',218,'','470R, 2012; exact manufacturer/tolerance not recorded. Confirm <=5%.')
assign('R4,R5,R9',185,'RK73B1JTTD220J','22R damping resistors, 1608, 5%.')
assign('R7,R8',223,'','1k utility resistors, 2012, 5%; no exact manufacturer MPN recorded.')
assign('R10,R11,R22,R28,R32',231,'','10k, 1608, 1%; no exact manufacturer MPN recorded.')
assign('R12,R14',None,'RMCF0805FT1K20','1k2, 1%, 2012 metric. No matching inventory record.','Yes')
assign('R13,R15',None,'RMCF0805FT1K50','1k5, 1%, 2012 metric. Owned ID226 is 1608 and is not substituted.','Yes')
assign('R16,R17',221,'','820R thin film, 0.5%, 2012; no exact manufacturer MPN recorded.')
assign('R18',494,'RMCF0805FT5K60')
assign('R19',194,'RK73B2ATTD103J','10k, 5%, 2012 metric. PLIMIT RC filter from 3V3-ESP.')
assign('R20',333,'','33k, 1%, 2012; no exact manufacturer MPN recorded.')
assign('R21,R26',194,'RK73B2ATTD103J','10k utility control resistors, 2012, 5%.')
assign('R23,R27',None,'RC0603FR-07100KL','100k / 1%, 1608; owned 2012 resistors do not match retained footprint.','Yes')
assign('R24',None,'RC0603FR-0716K2L','16k2 / 1%, 1608; no matching MCP record.','Yes')
assign('R25,R29,R30',241,'','100k utility resistors, 2012, 5%; no exact manufacturer MPN recorded.')
assign('R31,R33',493,'RMCF0805FT4K70')
assign('R35,R36,R37,R38',None,'RC0805FR-0718RL','DNP 18R snubber tuning resistors, 125 mW; pulse rating must be checked if populated.','Optional DNP only')
# Metadata does not alter any electrical connections or reference identities.
allrows=[]
def setp(s,k,v):
 p=prop(s,k)
 if p:p[2]=str(v)
 else:s.append([S('property'),k,str(v),[S('at'),*get(s,'at')[1:3],S('0')],[S('effects'),[S('font'),[S('size'),S('1.27'),S('1.27')]],[S('hide'),S('yes')]]])
for fn in ['TPA3126','ESP32','DAC','Amp','Power']:
 n=load(fn+'.kicad_sch')
 for s in many(n,'symbol'):
  ref=val(s,'Reference');m=mapping.get(ref)
  if m:
   setp(s,'MPN',m['mpn'] or '')
   if m['inventory_id'] is not None:setp(s,'Inventory_ID',m['inventory_id'])
   if m['comment']:setp(s,'Assembly_Note',m['comment'])
  if ref and not ref.startswith('#'):
   row={'reference':ref,'sheet':fn,'value':val(s,'Value'),'footprint':val(s,'Footprint'),'mpn':val(s,'MPN') or '', 'dnp':get(s,'dnp')[1]=='yes','on_board':get(s,'on_board')[1]=='yes'}
   if m:row.update({k:v for k,v in m.items() if k!='mpn'});row['confirmed_inventory_quantity']=pool.get(m['inventory_id'],{}).get('quantity',None)
   allrows.append(row)
 save(fn+'.kicad_sch',n)
Path('review/bom-and-inventory.json').write_text(json.dumps({'snapshot_date':'2026-10-19','account_link':'link_6a9aaf0f76248191a402cfc531930bc3','items':allrows},indent=2))
# Grouped review table includes offboard capacitor, DNP quantities and all fitted passives.
groups={}
for r in allrows:
 if r['reference'].startswith(('H','TP')):continue
 key=(r.get('inventory_id'),r['mpn'],r.get('comment',''),r.get('purchase',''),r['dnp'],r['footprint'])
 groups.setdefault(key,[]).append(r)
lines=['# Inventory usage - one board','', 'Live MCP snapshot: 19 October 2026. Quantities are physical inventory totals, not reservations or purchase orders. All returned reserved quantities were zero. Each row counts distinct references; a shared inventory total is not summed twice. No inventory records were changed.','', '| Component / references | Manufacturer part number | Quantity required | Inventory quantity confirmed | Purchase required |','|---|---|---:|---:|---|']
purchase=['# Purchasing list - one board','', 'No orders placed. Recheck supplier availability before ordering. Parts already present on the existing PCB, or in an unlogged kit, must be checked physically; they are not counted as owned here.','', '| References | Manufacturer part number | Quantity | Reason |','|---|---|---:|---|']
for key,rs in groups.items():
 r=rs[0];refs=', '.join(x['reference'] for x in rs);qty=len(rs);dnp=r['dnp'];owned=r.get('confirmed_inventory_quantity','Not queried');iid=r.get('inventory_id');stock=str(owned)+f' (ID {iid})' if iid else 'No matching record'
 mpn=r['mpn'] or 'Not recorded; use specified inventory value/package'
 if iid==132:mpn='Kemet stock MPN unrecorded; WIMA '+r['mpn']+' fallback'
 lines.append(f"| {refs}: {r['value']} | {mpn} | {'0 fitted; '+str(qty)+' optional' if dnp else qty} | {stock} | {r.get('purchase','No')} |")
 if r.get('purchase','No')!='No':purchase.append(f"| {refs} | {r['mpn']} | {'0 initially; '+str(qty)+' optional' if dnp else qty} | {r.get('comment','')} |")
lines+=['', 'Generic stock with no manufacturer MPN remains identified by inventory ID, value, tolerance and package. This is deliberate; a purchase part number must not be misrepresented as the owned item. C1/C2/C5/C6 stock has a 7x5 mm body note, but lead spacing is not recorded; verify 5 mm pitch before assembly or buy the named WIMA fallback. R2/R3 stock tolerance is not recorded; verify <=5% or buy RC0805FR-07470RL.','', 'C54 is external and excluded from PCB placement. A stereo bypass requires a removable, insulated link across J18 rated for at least 3 A. Mating housings, crimp contacts, external antenna and heatsink attachment hardware need a physical stock check and are separate system items. Mounting holes and bare-copper test pads require no purchased electronic parts.']
Path('review/INVENTORY-USAGE.md').write_text('\n'.join(lines)+'\n');Path('review/PURCHASING-LIST.md').write_text('\n'.join(purchase)+'\n')

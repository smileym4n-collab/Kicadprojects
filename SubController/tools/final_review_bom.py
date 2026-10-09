"""Build the authoritative Markdown/JSON BOM from the final exported netlist."""
from pathlib import Path
from collections import defaultdict,Counter
import json,sys,re,shutil
from sexpr import parse,children,child
P=Path(__file__).resolve().parents[1];D=P/'design';O=D/'final-review'
a=parse((O/'final.net').read_text());stock={}
for e in json.loads((O/'inventory-confirmed.json').read_text()):
 s=e.get('value',{}).get('result',{}).get('structuredContent',{})
 if 'inventory_id' in s:stock[s['inventory_id']]=s
s=json.loads((O/'inventory-197.json').read_text());stock[197]=s
sort=lambda r:(re.match('[A-Z]+',r)[0],int(re.search(r'\d+',r)[0]))
rm={'1k':224,'47k':376,'10k':375,'2k2':503,'100R':209,'100k':242,'4k7':493,'680R':220,'15k':235,'470R':87,'22k':511}
um={'U1':615,'U2':615,'U3':615,'U4':615,'U5':615,'U6':615,'U7':595,'U8':294,'U11':500,'U13':109,'U15':588}
rows=[];need=Counter();used=Counter();groups=defaultdict(list)
for c in sorted(children(child(a,'components'),'comp'),key=lambda c:sort(str(child(c,'ref')[1]))):
 ref=str(child(c,'ref')[1]);v=str(child(c,'value')[1]);fp=str(child(c,'footprint')[1]);sid=None;status='NEW / SOURCE';note=''
 if re.fullmatch(r'R\d+',ref):
  val=v.split()[0].lower().replace('r','R');sid=rm.get(val)
  if '0.1%' in v and val not in ['10k','47k']:sid=None
  if ref=='R112':sid=None
  note='2012 metric; 1% maximum unless specified tighter; thin-film for signal/ratio/filter networks.'
  if ref=='R112':note='2012 metric 0.25W required: 113mW sustained worst injection-limiter calculation.'
  if ref in ['R54','R93']:note='2012 metric; stock tolerance must be checked, utility value not precision-critical.'
 elif ref.startswith('C'):
  sid=414 if 'FILM' in v else 197 if v.startswith('100p') else 88 if v.startswith('10n ') else 505 if v.startswith('10u ') else 95 if v.startswith('47u') else 157 if v.startswith('100n') else 181 if v.startswith('1u') else None
  if ref=='C63':sid=None;note='Nichicon UES1H100MPM; 10uF 50V bipolar; diameter8mm height11.5mm pitch3.5mm.'
  elif sid==414:note='63V 5% film, body <=7.2x2.5mm, pitch5mm; measure stock lead pitch/dielectric. Buy shortage as KEMET 82DC3220AA60J (legacy R82DC3220AA60J), polyester film; select matching pairs.'
  elif sid==197:note='50V C0G, 2012 metric. Match C1/C64 and C2/C65 within 2%; C62 compensation.'
  elif sid==505:note='50V X5R, 3216 metric; supply use only. Verify effective capacitance at 15V against regulator requirement.'
  elif sid in [157,181]:note='50V X7R supply bypass, 3216 metric.'
  elif sid==88:note='50V C0G, 2012 metric; TPS feed-forward.'
  elif sid==95:note='25V Panasonic FR; verify formed lead spacing against 2.5mm footprint.'
 elif ref.startswith('U'):
  sid=um.get(ref)
  note={'U7':'Stock SMD suffix unconfirmed; wide SOIC16 assumed. User will verify physical package.','U8':'Microchip ATtiny1614-SS, SOIC14, direct GPIO.','U10':'Vishay VO617A-3, DIP4 7.62mm; buy one.','U11':'TI TPS7A3901DSCR/DSCT, WSON10 DSC0010J; EP11 GND, thermal vias.','U13':'Diodes stock generic 7805; verify exact marking, pin1 IN/2 GND/3 OUT. Heatsink mandatory.','U14':'TI LM4040A25IDBZR SOT23; buy one.','U15':'Inventory lacks manufacturer; standard LM339 SOIC14, verify markings.'}.get(ref,'Salvaged 4570; electrical review uses NEC/Renesas uPC4570G2. Inventory says JRC; user physical identity/package check pending.')
 elif ref.startswith('K'):sid=616;note='AGN2004H rated4.5V; user specifies5V. Existing user footprint and STEP copied exactly. Coil1+/8-, NC2/7 COM3/6 NO4/5.'
 elif ref.startswith('Q'):sid=461;note='BC337 manufacturer not recorded; verify physical C1/B2/E3 and collector saturation.'
 elif ref.startswith('D'):
  sid=510 if v=='1N4148W' else 124 if v=='1N4007' else None
  if ref=='D7':note='Diodes BAT54A-7-F common-anode dual Schottky: pins1/2 cathodes,3 common anode.'
 elif ref=='RV1':status='PROJECT RECORD / VERIFY';note='Prior project record reports2 owned; not in live inventory. Need1 PTD904-2015K-B203, four20k linear gangs. Measure tracking before layout.'
 elif ref.startswith('J'):status='MECHANICAL / SOURCE';note='Preserved connector family. Fit exact matching housing: JST-XH2.50mm is not Multicomp2.54mm. Headers/jumpers and panel controls must be checked separately.'
 elif ref.startswith('TP'):status='PCB PAD';note='No purchased part.'
 if sid:
  assert sid in stock,(ref,sid)
  need[sid]+=1;s=stock[sid];available=s['physical_quantity']-s.get('reserved_quantity',0)
  if used[sid]<available:status='OWNED';used[sid]+=1
  else:status='SHORTAGE / BUY'
 row={'Reference':ref,'Value':v,'Footprint':fp,'Status':status,'Inventory_ID':sid,'Note':note}
 rows.append(row);groups[(v,fp,status,sid,note)].append(ref)
(O/'BOM.json').write_text(json.dumps(rows,indent=2)+'\n')
manifest=[{k:r[k] for k in ['Reference','Value','Footprint','Note']} for r in rows]
allocation=[{'inventory_id':i,'part':stock[i].get('model_number',stock[i].get('description','')),'required':need[i],'physical_stock':stock[i]['physical_quantity'],'reserved':stock[i].get('reserved_quantity',0),'allocated':used[i],'shortage':max(0,need[i]-used[i]),'location':stock[i].get('storage_location','not recorded')} for i in sorted(need)]
(O/'inventory-allocation.json').write_text(json.dumps(allocation,indent=2)+'\n')
text=['# Final schematic BOM — revision B, 8 October 2026','',f'{len(rows)} component references, including test-point pads. Generated from the final KiCad netlist. Inventory was read live; nothing was reserved or decremented. Stock markings/package checks remain as stated below.','', '## Inventory allocation','', '| ID | Exact recorded part | Required / stock | Buy shortage | Location |','|---:|---|---:|---:|---|']
for r in allocation:text.append(f"| {r['inventory_id']} | {r['part']} | {r['required']} / {r['physical_stock']} | {r['shortage']} | {r['location']} |")
text+=['','## Complete grouped BOM','', '| References | Value | Qty | Status / inventory | Footprint | Qualification |','|---|---|---:|---|---|---|']
for (v,fp,status,sid,note),refs in groups.items():text.append(f"| {', '.join(refs)} | {v} | {len(refs)} | {status}"+(f' / {sid}' if sid else '')+f' | `{fp}` | {note} |')
text+=['','## Additional assembly items','', '- U13 heatsink and mounting hardware: effective junction-to-ambient <=20 °C/W at 2.7W, target board ambient <=50 °C. Leave physical clearance during layout; do not rely on a bare TO-220.','- One external 50k linear phase pot; two quadrature encoders with dry contacts; panel mode switch optional; jumper shunts.','- Insulated RCA sockets and wiring; connector mating housings/contacts; separately regulated shared-return ±15V supply rated at least +350mA / −100mA.','- P68 speaker-protection and early-power-fail interface remain system requirements. No mains components have been designed here.','', 'The unavailable exact part number for salvaged/loose stock is a recorded limitation, not an invented manufacturer identification.','']
(O/'BOM.md').write_text('\n'.join(text))
purchases=['# New parts and physical-fit checks','', 'Purchase list from revision-B netlist; no orders placed.','', '| References | Value / part | Qty | Requirement |','|---|---|---:|---|']
for (v,fp,status,sid,note),refs in groups.items():
 if status in ['NEW / SOURCE','SHORTAGE / BUY','MECHANICAL / SOURCE']:purchases.append(f"| {', '.join(refs)} | {v} | {len(refs)} | {note} |")
purchases+=['','Also allow the U13 heatsink, phase pot, encoders, mating connectors and jumper shunts listed in BOM.md. Generic connector entries are fit checks, not an assertion that none are owned.','']
(O/'PURCHASES.md').write_text('\n'.join(purchases))
# Keep superseded deliverables out of the current-design path, with their content preserved.
hist=D/'historical-before-final-review';hist.mkdir(exist_ok=True)
for name in ['BOM.csv','PURCHASES.csv','component-manifest.json','inventory-allocation.json','block-diagram.pdf','response-plots.pdf','DESIGN-REVIEW.md','PRE-DRAWING-DECISIONS.md']:
 f=D/name
 if f.exists() and not (hist/name).exists():shutil.move(f,hist/name)
(D/'component-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(D/'inventory-allocation.json').write_text(json.dumps(allocation,indent=2)+'\n')
print(f'{len(rows)} references; {sum(used.values())} stock components allocated; film shortage {need[414]-used[414]}')

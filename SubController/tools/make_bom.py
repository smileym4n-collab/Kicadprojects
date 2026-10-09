from pathlib import Path
import json,csv,re,collections
P=Path(__file__).resolve().parents[1];snap=json.load(open(P/'design/source-data/inventory-snapshot.json'));stock={}
for c in snap['categories'].values():
 for p in c['items']:stock[p['inventory_id']]=p
for p in snap['capacitors']:stock[p['inventory_id']]=p
for p in json.load(open(P/'design/source-data/resistors-2012.json'))['items']:stock[p['inventory_id']]=p
for p in json.load(open(P/'design/source-data/selected-inventory.json')):stock[p['inventory_id']]=p
for p in json.load(open(P/'design/source-data/diodes.json'))['items']:stock[p['inventory_id']]=p
for p in snap['transistor']['items']:stock[p['inventory_id']]=p
extra=json.load(open(P/'design/source-data/tps7a3901-inventory.json'))
for p in [extra['regulator']]+extra['parts']:stock[p['inventory_id']]=p
stock.update({p['inventory_id']:p for p in extra.get('existing_user_parts',[])})
b=json.load(open(P/'design/component-manifest.json'));rows=[]
rmatch={'1k':224,'47k':376,'10k':375,'11k3':233,'2k2':503,'100R':209,'100k':242,'4k7':493,'680R':220,'15k':235,'470R':87}
uf={'U1':615,'U2':615,'U3':615,'U4':615,'U5':615,'U6':615,'U7':595,'U8':80,'U9':342,'U11':500,'U13':109,'U15':588}
for c in b:
 ref=c['Reference'];v=c['Value'];sid=None;status='PURCHASE';spec='';conf=''
 if ref=='RV1':
  status='OWNED / USER-CONFIRMED';spec='Bourns PTD904-2015K-B203; four 20k linear gangs, +/-20%; PCB-mounted exact local footprint.';conf='User reports two newly found parts; measure gang matching across travel. Not yet recorded in connected inventory snapshot.'
 elif ref.startswith('R'):
  val=v.split()[0].lower().replace('r','R');sid=rmatch.get(val)
  if '/ 0.1%' in v and val!='10k':sid=None
  if ref in ['R105','R108']:sid=511
  if ref in ['R5','R6'] and val=='22k':sid=511
  spec='2012 metric; '+('0.1% thin-film' if '/ 0.1%' in v else '1% thin-film preferred (owned tighter parts acceptable)')
  if ref in ['R105','R108']:spec='2012 metric; owned Susumu 22k 0.5% thin-film; TPS feedback upper arm'
  if sid==209:conf='Verify tolerance on owned stock; output isolation resistor does not require precision.'
  if sid==233:spec='2012 metric owned 1% thick-film; measure four values for tracking.'
 elif ref.startswith('C'):
  cv=v.lower().replace('nf','n').replace('uf','u').replace('pf','p')
  sid=406 if '100n film'==cv else 414 if '220n film'==cv else 157 if cv.startswith('100n') else 181 if cv.startswith('1u') else 95 if cv.startswith('47u') else None
  if ref in ['C46','C47','C48','C49','C57','C58']:sid=505
  if ref in ['C60','C61']:sid=88
  spec='Film, >=50V, measured/matched; 7.2 x 2.5mm body, provisional 5mm pitch' if 'FILM' in v else '2012 metric C0G, >=25V' if 'C0G' in v or ref in ['C1','C2'] else '3216 metric supply ceramic' if sid in [157,181] else 'Panasonic FR 25V, D5mm; formed lead pitch 2.50mm'
  if sid==505:spec='3216 metric; Samsung CL31A106KBHNNNE, 10uF 50V X5R; supply bypass only';conf='Two parallel per +/-15V input for DC-bias margin; one per +/-5V output. Verify effective capacitance on assembled board.'
  if sid==88:spec='2012 metric; Walsin 10nF 50V C0G 5%; regulator feed-forward'
 elif ref.startswith('U'):sid=uf.get(ref);spec='VO617A-3, through-hole DIP4, 7.62mm rows; user-selected common part for another board. No positive inventory record found.' if ref=='U10' else 'New LM4040A25IDBZR SOT23 reference' if ref=='U14' else ''
 elif ref.startswith('K'):sid=616 if v=='AGN2004H' else 420
 elif ref.startswith('Q'):sid=461;conf='Manufacturer absent; qualify physical C/B/E order and saturation before assembly.'
 elif ref.startswith('D'):sid=510 if v=='1N4148W' else 124
 elif ref.startswith('J'):
  if ref in ['J11','J12']:spec='New 2.54mm double-row header; high-pass selection'
  else:status='STOCK-PREFERRED / CHECK';spec='2.54mm pin header; owned MC34629 (2-pin) / MC34631 (3-pin), matching Multicomp housings. Confirm header length/packaging.'
  if c['Footprint'].startswith('Connector_JST:'):status='EXISTING USER SELECTION / CHECK';spec='JST-XH 2.50mm; preserve user-assigned footprint. Verify matching owned connector/housing; not interchangeable with 2.54mm Multicomp.'
 elif ref.startswith('TP'):status='PCB PAD';spec='No purchased component'
 if sid:
  item=stock.get(sid,{});status='OWNED';qty=item.get('physical_quantity','');reserved=item.get('reserved_quantity','');loc=item.get('storage_location','not recorded')
  if sid==615:conf='User confirms NEC uPC4570G2; inventory manufacturer/package label is inaccurate.'
  if sid==595:conf='SMD stock confirmed; exact CS3310-KS package suffix/body must be checked before layout.'
  if sid==500:spec='Owned TPS7A3901 WSON-10 DSC0010J; exact local TI land pattern; EP11=GND';conf='Solder exposed pad; provide GND thermal vias at layout. No inventory reservation changed.'
  if sid==616:spec='Existing user-selected Panasonic AGN2004H; 4.5V coil; custom footprint preserved';conf='Present in pre-change files; package/electrical qualification is outside this regulator update.'
 else:item={};qty=2 if ref=='RV1' else '';reserved='not recorded' if ref=='RV1' else '';loc='Collection (user report)' if ref=='RV1' else ''
 rows.append({**c,'Status':status,'Inventory_ID':sid or '', 'Stock_model':item.get('model_number',''),'Stock_quantity':qty,'Reserved_quantity':reserved,'Storage_location':loc,'Specification':spec,'Qualification_note':conf})
fields=list(rows[0]);
with (P/'design/BOM.csv').open('w') as f:w=csv.DictWriter(f,fields);w.writeheader();w.writerows(rows)
used=collections.Counter(r['Inventory_ID'] for r in rows if r['Inventory_ID'])
summary=[]
for sid,qty in used.items():
 p=stock[sid];assert qty<=p['physical_quantity']-p.get('reserved_quantity',0),(sid,qty)
 summary.append({'Inventory_ID':sid,'Part':p.get('model_number',p.get('description')),'Required':qty,'Stock':p['physical_quantity'],'Reserved':p.get('reserved_quantity',0),'Location':p.get('storage_location','not recorded')})
summary.append({'Inventory_ID':None,'Part':'PTD904-2015K-B203','Required':1,'Stock':2,'Reserved':'not recorded','Location':'Collection (user report)','Source':'Direct user confirmation; connected inventory has not been modified.'})
(P/'design/inventory-allocation.json').write_text(json.dumps(summary,indent=2)+'\n')
purchases=collections.defaultdict(list)
for r in rows:
 if r['Status']=='PURCHASE':purchases[(r['Value'],r['Specification'])].append(r['Reference'])
with (P/'design/PURCHASES.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['Quantity','Value_or_part','Specification','References'])
 for (v,spec),refs in purchases.items():w.writerow([len(refs),v,spec,' '.join(refs)])
 for qty,v,spec in [(3,'Insulated panel RCA','REF L / REF R / LFE; shell isolated from chassis'),(2,'Quadrature rotary encoder','Dry contacts; panel mounted, MCU debounce'),(1,'50k linear panel pot','Phase control only; stock multiturn may serve prototype'),(1,'RUN status LED','High-efficiency indicator; ~0.5mA via 4k7; panel mounted'),(8,'2.54mm shunt','Remaining slope/phase/HP/polarity/AUTO selectors'),(1,'AUTO / REF / AV panel switch (optional)','SPDT ON-OFF-ON; header J24'),(4,'Panel SPDT switches (optional)','Slope / allpass bypass / polarity / AV HP, otherwise use shunts'),(1,'U13 heatsink / insulated mount','Effective junction-to-ambient <=30C/W including interface')]:w.writerow([qty,v,spec,'Panel / assembly'])
print(f'{len(rows)} components: {sum(r["Status"]=="OWNED" for r in rows)} allocated to inventory plus one user-confirmed PTD904; no inventory reservations changed.')

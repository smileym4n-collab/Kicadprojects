"""Assign verified stocked parts/footprints without changing schematic connectivity."""
from pathlib import Path
if globals().get('__name__') == '__main__':
 raise SystemExit('Historical one-shot assignment: do not regenerate the current schematic. See assignments.csv and standard-footprints-2026-10-25/README.md for current footprint choices.')
import re,json,csv,uuid,copy,collections,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'review/inventory-2026-10-25';BEFORE=OUT/'before/ClassA.kicad_sch'
# Reuse only the lossless S-expression helpers, never either schematic generator.
ns={'__file__':str(ROOT/'scripts/convert_single_supply.py')}
exec((ROOT/'scripts/convert_single_supply.py').read_text().split("ns={'__file__'")[0],ns)
parse,dump,Atom=ns['parse'],ns['dump'],ns['Atom']
def kids(s,k):return [x for x in s if isinstance(x,list) and x and x[0]==k]
def fld(s,k):return kids(s,k)[0]
def props(s):return {p[1]:p[2] for p in kids(s,'property')}
def uid():return str(uuid.uuid4())
def q(v):return json.dumps(str(v))
stock=json.loads((OUT/'inventory-evidence.json').read_text())['queries'];parts={}
for d in stock.values():
 if isinstance(d,dict):
  for p in d.get('items',[]):parts[p['inventory_id']]=p
  if 'inventory_id' in d:parts[d['inventory_id']]=d
FPLIB=ROOT/'ClassA_Inventory.pretty';FPLIB.mkdir(exist_ok=True)
def rect(a,b,layer,w=.1):return f'(fp_rect (start {a[0]} {a[1]}) (end {b[0]} {b[1]}) (stroke (width {w}) (type default)) (fill none) (layer "{layer}"))'
def line(a,b,layer='F.SilkS',w=.12):return f'(fp_line (start {a[0]} {a[1]}) (end {b[0]} {b[1]}) (stroke (width {w}) (type default)) (layer "{layer}"))'
def pad(n,x,y,drill=1,size=1.8):return f'(pad "{n}" thru_hole {"rect" if n==1 else "circle"} (at {x} {y}) (size {size} {size}) (drill {drill}) (layers "*.Cu" "*.Mask"))'
def savefp(name,desc,geo,source=''):
 s=f'(footprint {q(name)} (version 20241229) (generator "pcbnew") (layer "F.Cu") (descr {q(desc+" Source: "+source)}) (attr through_hole) (property "Reference" "REF**" (at 0 -7 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15)))) (property "Value" {q(name)} (at 0 7 0) (layer "F.Fab") (effects (font (size 1 1) (thickness .15)))) '+''.join(geo)+')\n'
 (FPLIB/(name+'.kicad_mod')).write_text(s)
 return 'ClassA_Inventory:'+name
mc=savefp('Multicomp_MC34629_1x02_P2.54mm','MC34629 top view: pin1 right, locking wall -Y; 3A/250V; 1.0mm manufacturer-recommended holes; body 5.08x5.8mm',[
 rect((-3.81,-2.6),(1.27,3.2),'F.Fab'),rect((-4.35,-3.15),(1.8,3.75),'F.CrtYd',.05),
 line((-3.93,-2.72),(1.39,-2.72)),line((-3.93,3.32),(1.39,3.32)),line((-3.93,-2.72),(-3.93,3.32)),line((1.39,-2.72),(1.39,3.32)),line((-3.81,-1.8),(1.27,-1.8),'F.Fab'),pad(1,0,0),pad(2,-2.54,0)],'https://www.farnell.com/datasheets/1751313.pdf')
# Pin pitches/numbering follow manufacturer drawings. Symmetric full-thickness envelopes
# deliberately cover either body offset from the lead row; these are not exact 3D models.
def bjt(name,width,depth,pitch,drill,desc,source):
 mid=pitch;left=round(mid-width/2,3);right=round(mid+width/2,3)
 return savefp(name,desc+'; conservative body envelope extends full maximum thickness on BOTH sides of lead row; no exact body offset/3D claim',[
 rect((left,-depth),(right,depth),'F.Fab'),rect((left-.3,-depth-.3),(right+.3,depth+.3),'F.CrtYd',.05),
 line((left-.12,-depth-.12),(right+.12,-depth-.12)),line((left-.12,depth+.12),(right+.12,depth+.12)),line((left-.12,-depth-.12),(left-.12,depth+.12)),line((right+.12,-depth-.12),(right+.12,depth+.12)),
 pad(1,0,0,drill,2.5 if pitch>3 else 2),pad(2,pitch,0,drill,2.5 if pitch>3 else 2),pad(3,2*pitch,0,drill,2.5 if pitch>3 else 2)],source)
po=bjt('Toshiba_2SC5198_TO3PN_BCE_P5.45_Envelope',15.9,4.8,5.45,1.6,'2SC5198: 1B 2C 3E; collector tab live; nominal 5.45mm pitch; 1.6mm holes clear rectangular leads','https://toshiba.semicon-storage.com/info/2SC5198_datasheet_en_20131101.pdf?did=20663&prodName=2SC5198')
me=bjt('Toshiba_2_10R1A_BCE_P2.54_Envelope',10.3,4.7,2.54,1.4,'2SC4793 / 2SA1837 Toshiba 2-10R1A: 1B 2C 3E; 2.54mm pitch; generous lead holes','https://media.digikey.com/pdf/Data%20Sheets/Toshiba%20PDFs/2SC4793_Rev2006.pdf')
cap=savefp('Multicomp_MCGPR50V478M22X41_Radial_P10','4700u/50V, radial WIRE leads, 10mm pitch, 22mm nominal diameter (+0.5mm); body height 41mm nominal; not snap-in; roomy 1.3mm holes',[
 '(fp_circle (center 5 0) (end 16.25 0) (stroke (width .1) (type default)) (fill none) (layer "F.Fab"))',
 '(fp_circle (center 5 0) (end 16.37 0) (stroke (width .12) (type default)) (fill none) (layer "F.SilkS"))',
 '(fp_circle (center 5 0) (end 16.55 0) (stroke (width .05) (type default)) (fill none) (layer "F.CrtYd"))',
 line((-8,-1),(-8,1)),line((-9,0),(-7,0)),pad(1,0,0,1.3,2.6),pad(2,10,0,1.3,2.6)],'https://uk.farnell.com/multicomp-pro/mcgpr50v478m22x41/cap-4700-f-50v-20/dp/1902903')
lr=savefp('TE_LR1_L6.8mm_D2.5mm_P10.16mm','TE LR1 metal-film resistor: allow 6.8x2.5mm maximum body; 10.16mm user-formed lead pitch; 0.9mm holes',[
 rect((1.68,-1.25),(8.48,1.25),'F.Fab'),rect((1.56,-1.37),(8.6,1.37),'F.SilkS',.12),rect((-1.15,-1.65),(11.31,1.65),'F.CrtYd',.05),line((0,0),(1.68,0),'F.Fab'),line((8.48,0),(10.16,0),'F.Fab'),pad(1,0,0,.9,1.8),pad(2,10.16,0,.9,1.8)],'https://docs.rs-online.com/92a4/0900766b81560e47.pdf')
# No pre-existing fp-lib-table exists in this project; retain other entries if one is later added.
table=ROOT/'fp-lib-table'
if table.exists():
 t=table.read_text()
 if '(name "ClassA_Inventory")' not in t:
  t=t.rstrip();table.write_text(t[:-1]+' (lib (name "ClassA_Inventory") (type "KiCad") (uri "${KIPRJMOD}/ClassA_Inventory.pretty") (options "") (descr "Inventory verified footprints")))\n')
else:table.write_text('(fp_lib_table (version 7) (lib (name "ClassA_Inventory") (type "KiCad") (uri "${KIPRJMOD}/ClassA_Inventory.pretty") (options "") (descr "Inventory verified footprints")))\n')
RSM='Resistor_SMD:R_0805_2012Metric';CSM='Capacitor_SMD:C_0805_2012Metric';TO92='Package_TO_SOT_THT:TO-92_Inline';assign={}
def use(refs,i,fp,note='',value=None):
 for ref in refs.split():assign[ref]={'id':i,'fp':fp,'status':'IN STOCK','note':note,'value':value}
def pending(refs,fp='',status='PURCHASE REQUIRED',note=''):
 for ref in refs.split():assign[ref]={'id':None,'fp':fp,'status':status,'note':note}
use('QOUT1 QOUT2 QSINK1 QSINK2',141,po,'Manufacturer pins 1B 2C 3E; conservative body envelope; external heatsink/insulation still required.')
use('Q6 Q8 Q9 Q10',586,me,'Four required, six available. Datasheet 2-10R1A package; 1B 2C 3E.')
use('Q7',587,me,'Inventory description erroneously says NPN: manufacturer verifies 2SA1837 is PNP. No inventory data edited.')
pending('Q1 Q2 Q3',TO92,'NOT LISTED','Specified KSA992 retained; no inventory record found. Footprint follows onsemi 1E 2C 3B, inline 1.27mm pitch; verify actual lead form.')
pending('Q4 Q5',TO92,'NOT LISTED','Specified KSC1845 retained; no inventory record found. Footprint follows onsemi 1E 2C 3B, inline 1.27mm pitch; verify actual lead form.')
use('D1 D2',138,'Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal','onsemi 1N4148 DO-35; pad1=cathode, pad2=anode.')
use('C1',417,'Capacitor_THT:C_Rect_L7.2mm_W7.2mm_P5.00mm','WIMA MKS2 PET film, 7.2x7.2x13mm / 5mm pitch, 63V; owned part reused.')
use('C2',197,CSM,'100p C0G, 50V; VAS Miller capacitor / TUNE.')
use('C3',406,'Capacitor_THT:C_Rect_L7.2mm_W2.5mm_P5.00mm','KEMET PET film; 7.2x2.5x6.5mm, 5mm pitch; 63V.')
use('C7',157,'Capacitor_SMD:C_1206_3216Metric','50V stock part replaces provisional 63V bypass rating: 40V nominal supply is 80% of rated voltage. Verify external rail maximum remains below 50V.','100n / 50V')
use('C9',157,'Capacitor_SMD:C_1206_3216Metric','50V stock part on approximately 20V reference, replacing provisional 63V rating.','100n / 50V REF')
use('C8',338,'Capacitor_THT:CP_Radial_D12.5mm_P5.00mm','35V stock part on approximately 20V reference replaces provisional 50V rating; diameter12.5mm, height20mm, pitch5mm.','1000u / 35V REF')
use('C10',167,cap,'Positive terminal at PRE_CAP; 22mm body, 10mm radial lead pitch; corrected previous snap-in footprint.')
pending('C4',note='470u/50V BIPOLAR required. Owned 470u parts are polarized and only 10/16V; do not substitute.')
pending('C6',note='470u/63V local rail capacitor required. 100V matching inventory record 737 has zero physical stock; no suitable owned part confirmed.')
pending('C5',CSM,'DNP - FOOTPRINT ONLY','10p/50V C0G optional lead compensation; no exact stock match; remains DNP.')
use('R1',511,RSM,'22k thin-film 0.5%; inventory package 2012 metric; 0.1W series rating verified.')
use('R3 R4 R6 R7 R8 R11 R22 R23 R26',209,RSM,'100R thin-film 0.5%, 0.1W; nine needed, 26 available.')
use('R5',92,lr,'270R metal-film 1%, 0.6W; TUNE retained.')
pending('R9',RSM,note='82R unchanged, TUNE; no exact stock. Provision for ordinary 2012 metric resistor, >=0.125W; final MPN not assigned.')
use('R10',275,lr,'18k metal-film 1%, 0.6W; approximately 0.083W in circuit.','18k / 0.6W')
use('R12',153,lr,'470R metal-film 1%, 0.6W.')
use('R13 R14 R17 R18',283,lr,'10R metal-film 1%, 0.6W base stoppers; non-wirewound; TUNE retained.')
pending('R15 R16 R19 R20',status='USER TO ASSIGN',note='User will assign 0R22/5W ballast resistors/footprints. Only one unmarked 10% single resistor in inventory; dual three-lead parts not substituted. No inventory part claimed.')
pending('R21',note='0R27/5W common sense resistor; no exact inventory match. Select exact part/package before footprint assignment.')
use('R24 R34',272,lr,'10k metal-film 1%, 0.6W; R24 dissipates approximately 0.15W, so small 0.1/0.125W SMD stock rejected.')
use('R25',373,RSM,'3k3 thick-film 1%, 0.125W.')
use('R27 R31',224,RSM,'1k thin-film 0.5%, 0.1W.')
pending('R28 R29',note='10R >=3W low-inductance damping/Zobel resistors. Stock 5W MCKNP is ordinary wirewound with no non-inductive guarantee, so not forced into HF stability network. Final MPN/package required.')
pending('R30',RSM,note='19k thin-film feedback value unchanged, no exact inventory match. 2012 metric footprint provision only.')
use('R32 R33',268,lr,'2k2 metal-film 1%, 0.6W; estimated 0.182W each at 40V.')
pending('RV1',status='USER TO ASSIGN',note='Inventory525: generic 1k multiturn, available3, Potentiometers. User will assign actual package/wiper mapping; no MPN or footprint guessed.')
pending('L1',note='0.82uH >=4A output coil: no matching owned part. No unrelated 2.2/3.3uH inductor or ferrite substituted. Footprint depends on chosen coil.')
use('J1 J2 J3',126,mc,'MC34629 2.54mm 3A/250V header; three needed, 40 available. Mate with MC34481 stock housing; appropriate crimp contacts/wire required. Pin/net order retained.')
# Identify and replace only top-level placed-symbol expressions, retaining all other bytes.
source=BEFORE.read_text()
def spans(text):
 depth=0;start=None;quoted=False;esc=False
 for i,c in enumerate(text):
  if quoted:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c=='"':quoted=False
  elif c=='"':quoted=True
  elif c=='(':
   if depth==1:start=i
   depth+=1
  elif c==')':
   depth-=1
   if depth==1 and start is not None:yield start,i+1,text[start:i+1];start=None

def setprop(s,key,value):
 pp=next((p for p in kids(s,'property') if p[1]==key),None)
 if pp is not None:pp[2]=Atom(value,True);return
 at=fld(s,'at');s.append(parse(f'(property {q(key)} {q(value)} (at {at[1]} {at[2]} 0) (effects (font (size 1.0 1.0)) (hide yes)))'))
rows=[];patches=[]
for start,end,raw in spans(source):
 if not raw.startswith('(symbol') and not raw.startswith('(text'):continue
 s=parse(raw)
 if s[0]=='text' and 'ALL FOOTPRINTS UNASSIGNED' in str(s[1]):
  s[1]=Atom('Inventory/footprint assignments: see review/inventory-2026-10-25/README.md.\nBlank footprints are explicit purchase/user-assignment gaps. No PCB layout performed.',True);patches.append((start,end,dump(s)));continue
 if s[0]!='symbol' or not kids(s,'lib_id'):continue
 p=props(s);ref=str(p.get('Reference',''))
 if ref.startswith('#'):continue
 if ref.startswith('TP'):
  a={'id':None,'fp':'TestPoint:TestPoint_THTPad_D1.5mm_Drill0.7mm','status':'PCB FEATURE','note':'Bare plated test pad; no purchased component or stock claimed.'}
 else:
  assert ref in assign,ref;a=assign[ref]
 pp=parts.get(a['id'],{})
 if ref in ['Q1','Q2','Q3','Q4','Q5']:
  pp={'manufacturer':'onsemi','model_number':'KSA992FTA' if ref in ['Q1','Q2','Q3'] else 'KSC1845FTA'}
 setprop(s,'Footprint',a['fp'])
 if a.get('value'):setprop(s,'Value',a['value'])
 extra={'Manufacturer':pp.get('manufacturer',''),'MPN':pp.get('model_number',''),'Inventory_ID':str(a['id'] or ''),'Inventory_Available':str(pp.get('quantity','')),'Inventory_Location':pp.get('storage_location',''),'Assembly_Status':a['status'],'Assignment_Notes':a['note'],'Package':(pp.get('package','')+' metric' if pp.get('package') in ['1608','2012','3216'] else pp.get('package',''))}
 for key,value in extra.items():setprop(s,key,value)
 if pp.get('datasheet_url'):setprop(s,'Datasheet',pp['datasheet_url'])
 row={'Reference':ref,'Value':str(props(s)['Value']),'Footprint':a['fp'],'Manufacturer':pp.get('manufacturer',''),'MPN':pp.get('model_number',''),'Inventory_ID':a['id'] or '', 'Available':pp.get('quantity',''),'Location':pp.get('storage_location',''),'Status':a['status'],'Notes':a['note']}
 rows.append(row);patches.append((start,end,dump(s)))
for start,end,repl in reversed(patches):source=source[:start]+repl+source[end:]
(ROOT/'ClassA.kicad_sch').write_text(source)
rows.sort(key=lambda r:(re.sub(r'\d+','',r['Reference']),int(re.search(r'\d+',r['Reference'])[0])))
with (OUT/'assignments.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(OUT/'assignments.json').write_text(json.dumps(rows,indent=2))
counts=collections.Counter(r['Status'] for r in rows);print('Assignments:',dict(counts));print('Footprints assigned:',sum(bool(r['Footprint']) for r in rows),'of',len(rows));print('Unassigned footprints:',', '.join(r['Reference'] for r in rows if not r['Footprint']))

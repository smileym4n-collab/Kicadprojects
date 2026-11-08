"""Read-only assertions against this review's freshly exported netlist."""
from pathlib import Path
import xml.etree.ElementTree as E,json,hashlib,sys,math
sys.path.insert(0,'review/scripts');from schlib import load,many,val,get,pins
root=E.parse('review/revisions/preorder-corrections-2026-10-23/after.xml');nets={};checks=[]
for net in root.findall('./nets/net'):
 for p in net.findall('node'):nets[p.get('ref'),p.get('pin')]=net.get('name')
def eq(desc,*nodes):
 v=[nets.get((r,str(p))) for r,p in nodes];assert None not in v and len(set(v))==1,(desc,v);checks.append(desc)
def ne(desc,*nodes):
 v=[nets.get((r,str(p))) for r,p in nodes];assert None not in v and len(set(v))==len(v),(desc,v);checks.append(desc)
parts={}
for f in ['TPA3126','ESP32','DAC','Amp','Power']:
 n=load(f+'.kicad_sch')
 for s in many(n,'symbol'):parts[val(s,'Reference')]=s
# Trace the actual saved channel assignment, not the old prose.
eq('DAC OUTL pin6 -> R2.1',('U2',6),('R2',1));eq('DAC left filter -> tweeter pad',('R2',2),('C16',1),('R14',1));eq('Tweeter pad node',('R14',2),('R15',2),('C6',1));eq('Tweeter positive amp input',('C6',2),('U1',10))
eq('DAC OUTR pin7 -> R3.2',('U2',7),('R3',2));eq('DAC right filter -> woofer pad',('R3',1),('C19',1),('R12',1));eq('Woofer pad node',('R12',2),('R13',2),('C1',1));eq('Woofer positive amp input',('C1',2),('U1',4))
for pin,ref,pn in [(1,'J1',2),(2,'C30',1),(3,'R30',2),(4,'C1',2),(5,'C2',2),(6,'C29',1),(7,'C28',1),(8,'R18',1),(9,'J1',2),(10,'C6',2),(11,'C5',2),(12,'C31',1),(13,'J1',2),(14,'J1',2),(15,'J1',2),(17,'Q1',3),(18,'Q1',3),(19,'Q1',3),(20,'C27',1),(21,'L3',1),(22,'J1',2),(23,'L3',4),(24,'C26',1),(25,'J1',2),(26,'C25',1),(27,'L2',1),(28,'J1',2),(29,'L2',4),(30,'C24',1),(31,'Q1',3),(32,'Q1',3)]:eq('Amplifier pin '+str(pin),('U1',pin),(ref,pn))
assert nets['U1','16'].startswith('unconnected-');checks.append('SYNC intentional NC')
for c,p in [('C24',29),('C25',27),('C26',23),('C27',21)]:eq('Bootstrap '+c,(c,2),('U1',p))
eq('Woofer +',('L2',3),('C37',2),('J16',1));eq('Woofer -',('L2',2),('C38',1),('J16',2));eq('Tweeter + pre cap',('L3',3),('C39',2),('C21',1),('JP1',1));eq('Tweeter + post cap',('C21',2),('JP1',2),('J17',1));eq('Tweeter -',('L3',2),('C40',1),('J17',2));ne('Four speaker terminals floating and independent',('J16',1),('J16',2),('J17',1),('J17',2),('J1',2))
for p,r in [(10,'R4'),(11,'R5'),(16,'R9'),(8,'R8'),(9,'R7')]:eq('Preserved GPIO module pin '+str(p),('IC5',p),(r,2))
for p,r,dp in [(21,'R5',1),(22,'R9',1),(23,'R4',1),(11,'IC5',33),(12,'IC5',31),(25,'IC5',30)]:eq('DAC digital pin '+str(p),('U2',p),(r,dp))
for p in [3,9,10,16,17,20,24,27]:eq('DAC ground/strap '+str(p),('U2',p),('J1',2))
for p in [1,8,18,28]:eq('DAC 3.3V/strap '+str(p),('U2',p),('IC4',5))
eq('Charge pump CAPP',('U2',2),('C14',1));eq('Charge pump CAPM',('U2',4),('C14',2));eq('VNEG reservoir',('U2',5),('C12',1));eq('LDOO capacitors',('U2',26),('C15',1),('C18',1))
eq('Volume wiper series input',('J2',3),('R39',1));eq('Volume ADC',('IC5',6),('R39',2),('C58',1));eq('Volume/common ground',('J2',1),('J1',2));eq('Volume high end',('J2',4),('IC5',2))
eq('SDZ command GPIO27',('IC5',12),('R21',1));eq('MUTE command GPIO23',('IC5',37),('R26',1));eq('FAULT GPIO35',('IC5',7),('U1',3));eq('PLIMIT external reference',('R19',1),('IC5',2));ne('R20 is now output RC resistor, not PLIMIT shunt',('R20',1),('U1',6))
eq('Input fuse',('J1',1),('F2',1));eq('Reverse PMOS drain',('F2',2),('Q1',2));eq('Protected supply',('Q1',3),('D1',1),('D2',1),('U3',3),('U3',5));eq('Gate clamp',('Q1',1),('D1',2),('R22',1));eq('Buck SW',('U3',2),('C48',2),('L1',1));eq('Buck CB',('U3',6),('C48',1));eq('Pre rail',('L1',2),('R23',1),('U4',3),('R1',1));eq('Feedback',('U3',4),('R23',2),('R24',1));eq('ESP output',('U4',2),('IC5',2));eq('DAC LDO input',('R1',2),('IC4',1),('IC4',3));ne('Separate regulated positive rails',('Q1',3),('L1',2),('U4',2),('IC4',5),('J1',2))
# Added EVM-style post-filter series RC networks, on all four filtered legs.
for c,r,out in [('C54','R20',('J16',1)),('C32','R6',('J16',2)),('C60','R40',('L3',3)),('C59','R34',('J17',2))]:
 eq('Filtered RC feed '+c,(c,1),out);eq('Series RC junction '+c,(c,2),(r,1));eq('RC ground '+r,(r,2),('J1',2))
 assert val(parts[c],'Value')=='10nF' and val(parts[r],'Value')=='3R3'
eq('Restored ADC shunt',('R41',1),('IC5',6));eq('ADC shunt ground',('R41',2),('J1',2));eq('Mode button GPIO22',('IC5',36),('J2',2),('R35',1));eq('Mode pullup',('R35',2),('IC5',2));eq('Mode button ground',('J2',5),('J1',2))
# Original manufacturer physical pin-name maps retained.
for fn,ref in [('Amp','U1'),('DAC','U2'),('ESP32','IC5'),('Power','U3'),('Power','U4')]:
 if not Path('review/original/'+fn+'.kicad_sch').exists():continue
 old=load('review/original/'+fn+'.kicad_sch');cur=load(fn+'.kicad_sch');os=next((s for s in many(old,'symbol') if val(s,'Reference')==ref),None)
 if os:
  assert {p[:2] for p in pins(old,os)}=={p[:2] for p in pins(cur,parts[ref])};checks.append('Retained physical pin-name map '+ref)
j=json.loads(Path('review/revisions/preorder-corrections-2026-10-23/erc.json').read_text());v=[v for s in j['sheets'] for v in s['violations']];assert all(x['severity']=='warning' and x['type']=='endpoint_off_grid' for x in v)
result={'date':'2026-10-23','checks_passed':len(checks),'checks':checks,'ERC_errors':0,'ERC_warnings':len(v),'ERC_warning_types':['endpoint_off_grid'],'channel_assignment_matches_original_contract':False,'actual_channel_assignment':{'OUTL':'tweeter via TPA left bridge / J17','OUTR':'woofer via TPA right bridge / J16'},'volume_ADC_shunt_pulldown_present':True,'volume_R39_value':val(parts['R39'],'Value'),'design_file_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [*Path('.').glob('*.kicad_sch'),Path('TPA3126.kicad_pcb'),Path('TPA3126.kicad_pro')]}}
Path('review/revisions/preorder-corrections-2026-10-23/connectivity.json').write_text(json.dumps(result,indent=2));print('PASS:',len(checks),'basic connectivity checks. Findings require separate review; this is not a clean-design certificate.')

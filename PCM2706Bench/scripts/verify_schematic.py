"""Check freshly exported connectivity, all IC1 pins, pin-map preservation, and PCB/project hashes.
Run kicad-cli export netlist and ERC to review/final first.
"""
import hashlib,json,sys,xml.etree.ElementTree as E
from pathlib import Path
from schutil import parse,child,children,prop
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def check(cond,msg):
 assert cond,msg
 checks.append(msg)
r=E.parse(ROOT/'review/final/netlist.xml').getroot();nets={};names={};comps={c.attrib['ref']:c for c in r.findall('components/comp')}
for n in r.findall('nets/net'):
 pins=frozenset(x.attrib['ref']+'.'+x.attrib['pin']for x in n)
 for x in pins:nets[x]=pins;names[x]=n.attrib['name']
def same(*pins):check(all(nets[x]==nets[pins[0]]for x in pins),'Connected: '+', '.join(pins))
def exact(*pins):check(nets[pins[0]]==set(pins),'Exact net: '+', '.join(pins))
ground=['IC1.1','IC1.20','IC1.25','IC1.26','IC1.31','IC1.3','IC1.4','IC2.2','J3.4','J1.1','RV1.1','RV1.4','J4.2','J5.5','J5.6']
same(*ground)
for pin,cap in [('2','C11'),('21','C12'),('27','C13'),('30','C14')]:
 same('IC1.'+pin,cap+'.1');same('IC1.1',cap+'.2');check(comps[cap].findtext('value')=='1uF',cap+' is 1uF')
check(len({names['IC1.'+p]for p in ['2','21','27','30']})==4,'Four internal supply outputs are separate')
exact('IC1.2','C11.1');exact('IC1.27','C13.1');exact('IC1.30','C14.1')
exact('IC1.21','C12.1','IC1.10','IC1.16','J1.3','R4.1','R17.1')
exact('IC1.24','C16.1','J3.1','IC2.5');same('C16.2','IC1.1')
exact('IC1.9','J1.2','R17.2');check(comps['R17'].findtext('value')=='100k','FSEL has 100k default-high pullup')
check(nets['J1.1']!=nets['J1.3'],'Switch throws are ground and VDD on separate nets')
# USBLC6 internally joins 1-6 and 3-4; assert the two sides explicitly.
exact('IC1.23','R11.1');exact('R11.2','IC2.1','R4.2');exact('IC2.6','J3.3')
exact('IC1.22','R10.1');exact('R10.2','IC2.3');exact('IC2.4','J3.2')
check(comps['R4'].findtext('value')=='1K5','USB full-speed pullup is 1k5 on D+ path')
for chip,rs,head in [('17','R12','3'),('5','R13','4'),('18','R14','1'),('19','R15','2')]:
 exact('IC1.'+chip,rs+'.1');exact(rs+'.2','J5.'+head);check(comps[rs].findtext('value')=='22R',rs+' source termination is 22R')
exact('IC1.28','C21.1','C17.1');exact('IC1.29','C22.1','C15.1')
exact('C21.2','RV1.6');exact('C22.2','RV1.3');exact('RV1.2','J4.1');exact('RV1.5','J4.3')
check(comps['RV1'].findtext('value')=='10k LINEAR (B)','Pot annotation matches user B10k kit; first-gang direction confirmed by user measurement')
for c,rs in [('C17','R3'),('C15','R2')]:exact(c+'.2',rs+'.1');same(rs+'.2','IC1.1')
exact('IC1.32','C1.1');same('C1.2','IC1.1')
exact('IC1.12','C4.1','R16.1','Y1.1');exact('IC1.13','C3.1','R16.2','Y1.2');same('C3.2','C4.2','IC1.1')
for pin in ['6','7','8','11','14','15']:exact('IC1.'+pin)
check(all('IC1.'+str(p)in nets for p in range(1,33)),'All 32 IC1 pins accounted for')
exact('J3.5','FB1.2');same('FB1.1','IC1.1')
base=parse((ROOT/'review/baseline/PCM2706Bench.kicad_sch').read_text());final=parse((ROOT/'PCM2706Bench.kicad_sch').read_text())
def pinmaps(s):
 return {lib[1]:[(child(p,'number')[1],child(p,'name')[1],child(p,'at'),p[1:3])for u in children(lib,'symbol')for p in children(u,'pin')]for lib in children(child(s,'lib_symbols'),'symbol')}
check(pinmaps(base)==pinmaps(final),'Every embedded library symbol pin number, name, position and electrical type preserved')
for fname in ['PCM2706Bench.kicad_pro','PCM2706Bench.kicad_pcb']:
 lines=(ROOT/'review/baseline/source-sha256.txt').read_text().splitlines();h=next(x.split()[0]for x in lines if x.endswith(fname));check(hashlib.sha256((ROOT/fname).read_bytes()).hexdigest()==h,fname+' preserved byte-for-byte')
basecomps={x.attrib['ref']:x for x in E.parse(ROOT/'review/baseline/netlist.xml').getroot().findall('components/comp')}
check(set(comps)==set(basecomps)|{'R17'},'Only added component is R17; no original components removed')
for ref,c in basecomps.items():check(c.findtext('footprint')==comps[ref].findtext('footprint'),ref+' footprint assignment preserved')
erc=json.loads((ROOT/'review/final/erc.json').read_text());viol=[v for s in erc['sheets']for v in s['violations']]
check(not any(v['severity']=='error'for v in viol),'ERC has zero errors')
check(len(viol)==2 and all(v['type']=='lib_symbol_mismatch' and v['severity']=='warning'for v in viol),'Only two documented pre-existing library mismatch warnings remain')
print(json.dumps({'passed':len(checks),'checks':checks,'limitations':['WH148 second-gang direction, CCW end stops and mechanical fit require measurement','Component ratings/crystal load specification not supplied','PCB was not updated, reviewed or tested']},indent=2))

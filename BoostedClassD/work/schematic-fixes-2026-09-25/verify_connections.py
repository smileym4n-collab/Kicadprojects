"""Run after exporting after.xml with KiCad's hierarchical netlist exporter."""
import json,hashlib,pathlib,xml.etree.ElementTree as ET
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parent.parent
xml=ET.parse(HERE/'after.xml').getroot()
net={ (n.get('ref'),n.get('pin')): frozenset((p.get('ref'),p.get('pin')) for p in group.findall('node')) for group in xml.find('nets') for n in group.findall('node')}
checks=[]
def joined(title,*pins):
 ps=[tuple(p.split('.')) for p in pins];assert all(p in net[ps[0]] for p in ps),title;checks.append(title)
def separate(title,*pins):
 ps=[tuple(p.split('.')) for p in pins];assert len({net[p] for p in ps})==len(ps),title;checks.append(title)
def exact(title,*pins):
 ps=frozenset(tuple(p.split('.')) for p in pins);assert net[next(iter(ps))]==ps,(title,net[next(iter(ps))],ps);checks.append(title)
joined('Always-on tiny supply','IC1.1','Q1.2','U5.1','C8.1','R13.1','R32.1','J6.1','Q5.2','R36.1')
joined('Switched system supply','Q1.3','U1.4','U1.5','U2.15','U3.15','U4.1')
joined('3.3V IOVDD and local decoupling','U1.1','IC2.2','U2.5','U3.5','C22.1','C24.1','C32.1','R14.1','R15.1','R33.1','R25.2')
joined('1.8V core supplies and decoupling','U4.5','U2.24','U3.24','C21.1','C23.1')
separate('Ground, always-on, switched, 3.3V and 1.8V isolated','U5.8','U5.1','Q1.3','IC2.2','U2.24')
exact('Independent TAS2120 shutdown','IC2.9','U3.7','R22.1')
exact('Independent TAS2320 shutdown','IC2.12','U2.7','R23.1')
joined('Shutdown defaults low','R22.2','R23.2','U5.8')
exact('TAS2120 address resistor','U3.2','R24.1')
joined('TAS2120 address to ground','R24.2','U5.8')
exact('TAS2320 address resistor','U2.2','R25.1')
for ref in ['U2','U3']:
 for pin in ['12','16','21','22','23','25']:joined(ref+' ground/mode pin '+pin,ref+'.'+pin,'U5.8')
exact('Play request tiny side','U5.4','R26.1')
exact('Play request ESP side','IC2.6','Q2.3','R14.2')
exact('Off request tiny side','U5.5','R28.1')
exact('Off request ESP side','IC2.7','Q3.3','R15.2')
exact('Acknowledgement ESP side','IC2.13','R30.1')
exact('Acknowledgement tiny side','U5.7','Q4.3','R32.2','TP1.1')
for q,r,be in [('Q2','R26','R27'),('Q3','R28','R29'),('Q4','R30','R31')]:
 exact(q+' base bias',q+'.1',r+'.2',be+'.1');joined(q+' emitter and base return',q+'.2',be+'.2','U5.8')
exact('Charger status sink drives base resistor','IC1.3','R35.1')
exact('PNP base bias','Q5.1','R35.2','R36.2')
exact('PNP collector feeds LED resistor','Q5.3','R19.1')
exact('Charge LED connector positive preserved','R19.2','J1.7')
joined('Charge LED connector return preserved','J1.8','U5.8')
exact('Status LED resistor input','IC2.37','R34.1')
exact('Status LED resistor output','R34.2','J2.6')
exact('INA alert across hierarchy with pullup','IC5.8','IC2.8','R33.2')
exact('UPDI header data','U5.6','J6.2')
joined('UPDI header ground','J6.3','U5.8')
exact('Shared Class-H control retained','U2.1','U3.1')
joined('Boost PVDD shared','U3.18','U2.18','C10.1','C11.1','C12.1')
# Preserve every original terminal relationship except the five intentionally changed circuits.
bxml=ET.parse(HERE/'before.xml').getroot()
bnet={ (n.get('ref'),n.get('pin')): frozenset((p.get('ref'),p.get('pin')) for p in g.findall('node')) for g in bxml.find('nets') for n in g.findall('node')}
affected={'C8.1','U2.5','IC2.6','IC2.7','IC2.37','IC1.3'}
allowed={bnet[tuple(p.split('.'))] for p in affected}
for pin,old in bnet.items():
 if old not in allowed:assert old.issubset(net[pin]),('Unexpected disconnection',pin,old,net[pin])
checks.append('All other original pin relationships preserved')
# No altered topology between originally separate nets except the authorized supply moves and ALERT.
new_to_old={}
for pin,old in bnet.items():new_to_old.setdefault(net[pin],set()).add(old)
allowedmerges={net[('U5','1')],net[('U2','5')],net[('IC5','8')],net[('U3','7')],net[('U2','7')]}
for new,oldsets in new_to_old.items():
 if len(oldsets)>1:assert new in allowedmerges,('Unexpected merger',new)
checks.append('No unapproved mergers of original nets')
for f in ['BoostedClassD.kicad_pcb','BoostedClassD.kicad_pro']:
 assert (ROOT/f).read_bytes()==(HERE/'backup'/f).read_bytes(),f+' changed';checks.append(f+' byte-for-byte unchanged')
report=json.load(open(HERE/'erc.json'));assert not any(s['violations'] for s in report['sheets']);checks.append('Hierarchical ERC zero violations without new exclusions')
# Verify library footprint files assigned to every new component exist.
newrefs={f'R{i}' for i in range(22,37)}|{'Q2','Q3','Q4','Q5','C32','J6'}
for comp in xml.find('components'):
 if comp.get('ref') in newrefs:
  lib,name=comp.findtext('footprint').split(':');fp=pathlib.Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints')/(lib+'.pretty')/(name+'.kicad_mod');assert fp.exists(),fp
checks.append('All 21 new component footprints resolve')
(HERE/'connectivity-checks.json').write_text(json.dumps({'passed':len(checks),'checks':checks},indent=2)+'\n')
print(f'{len(checks)} checks passed')

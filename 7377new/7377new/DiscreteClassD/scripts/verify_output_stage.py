from pathlib import Path
import xml.etree.ElementTree as ET,json,sys,collections,hashlib
from sexp import *
root=Path(__file__).resolve().parents[1]; out=root/'output/verification'
r=ET.parse(out/'DiscreteClassD.xml').getroot(); actual={};nets={}
for net in r.findall('./nets/net'):
 name=net.get('name').split('/')[-1];nodes={(p.get('ref'),p.get('pin')) for p in net.findall('node')};nets[name]=nodes
 for key in nodes:actual[key]=name
expected=json.loads((out/'intended-connections.json').read_text()); bad=[];tested=0
for ref,ps in expected.items():
 for p,net in ps.items():
  if net.startswith(('ALT_','SNUB_')) or net=='ZOBEL':continue
  tested+=1
  if actual.get((ref,p))!=net:bad.append((ref,p,net,actual.get((ref,p))))
assert not bad,bad
# Check exact unnamed series branches, no unintended extra connections.
for refs in [('D1','2','R3','1'),('D2','2','R6','1'),('D3','2','R9','1'),('D4','2','R12','1'),('R13','2','C13','1'),('R14','2','C14','1'),('R15','2','C16','1')]:
 a,b,c,d=refs;assert actual[(a,b)]==actual[(c,d)];assert nets[actual[(a,b)]]=={(a,b),(c,d)}
# Critical nets must remain distinct: no gate resistor bypass or BTL short.
critical=['+24V','+12V_GD','PGND','SW_A','SW_B','OUT_A','OUT_B','HO_A','LO_A','HO_B','LO_B','GH_A','GL_A','GH_B','GL_B','HI_A','LI_A','HI_B','LI_B','EN_A','EN_B']
assert all(k in nets for k in critical)
assert len({actual[(ref,p)] for ref,p in [('J15','1'),('J15','2'),('J14','2')]})==3
sch=parse((root/'PowerOutput.kicad_sch').read_text()); syms=allof(sch,'symbol');byref={prop(s,'Reference')[2]:s for s in syms}
dnp={'D1','D2','D3','D4','R3','R6','R9','R12','R13','R14','C13','C14'}
assert {ref for ref,s in byref.items() if get(s,'dnp')[1]=='yes'}==dnp
assert all(get(byref[x],'in_bom')[1]=='no' for x in dnp)
assert len(byref)==57
# Footprint pads must cover every modeled semiconductor pin.
fp=parse((root/'DiscreteClassD.pretty/DMTH6016LPS_PowerDI5060-8.kicad_mod').read_text())
assert {p[1] for p in allof(fp,'pad')}==set('12345678')
for p in allof(fp,'pad'):
 x,y=map(float,get(p,'at')[1:3])
 if y>2:assert p[1]=={-1.905:'1',-.635:'2',.635:'3',1.905:'4'}[x]
 elif x in [-1.905,-.635,.635,1.905]:assert p[1]=={-1.905:'8',-.635:'7',.635:'6',1.905:'5'}[x]
 else:assert p[1]=='5'
fp=parse((root/'DiscreteClassD.pretty/CSAD0660-100M.kicad_mod').read_text())
assert {p[1] for p in allof(fp,'pad')}==set('1234')
# Exact semantic preservation of all unrelated pre-existing symbol instances and embedded library.
before=parse((out/'DiscreteClassD.before-output-stage.kicad_sch').read_text());after=parse((root/'DiscreteClassD.kicad_sch').read_text())
removed={'U2','Q1','Q2','C1','L6','J14','J15','#PWR01','#PWR02','#PWR03'}
preserved=[s for s in allof(before,'symbol') if prop(s,'Reference')[2] not in removed]
assert preserved==allof(after,'symbol')
assert get(before,'lib_symbols')==get(after,'lib_symbols')
assert (out/'DiscreteClassD.before-output-stage.kicad_pro').read_bytes()==(root/'DiscreteClassD.kicad_pro').read_bytes()
# Record actual nets and connections for review, including implicit package-pin groups.
rows=['| Component | Pin | Exported net |','|---|---|---|']
for ref in sorted(byref,key=lambda x:(x.rstrip('0123456789'),int(''.join(filter(str.isdigit,x))))):
 for (rr,p),net in sorted(actual.items(),key=lambda x:(x[0][0],int(x[0][1]))):
  if rr==ref:rows.append(f'| {ref} | {p} | {net} |')
(out/'all-output-connections.md').write_text('# All output-stage connections from KiCad netlist\n\n'+'\n'.join(rows)+'\n')
summary=f'''PASS: {tested} explicitly named pin-to-net assignments.
PASS: 7 isolated series-branch nets (DNP gate paths, snubbers, Zobel).
PASS: driver outputs, MOSFET gates, both switching nodes, and speaker terminals remain separate.
PASS: all 12 optional components are DNP and excluded from BOM.
PASS: MOSFET physical pads 1-8 match restored package numbering; central drain copper is pad 5.
PASS: {len(preserved)} unrelated symbol instances and original root embedded libraries unchanged.
PASS: original project settings byte-for-byte unchanged; no ERC exclusions added.
Output-stage symbols: 57. No simulation, PCB build, or hardware performance verification performed.
'''
(out/'connectivity-check.txt').write_text(summary);print(summary)

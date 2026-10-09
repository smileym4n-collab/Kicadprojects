from pathlib import Path
import re,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def parse(s):
 tokens=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',s);i=0
 def read():
  nonlocal i
  t=tokens[i];i+=1
  if t=='(':
   v=[]
   while tokens[i]!=')':v.append(read())
   i+=1;return v
  return json.loads(t) if t.startswith('"') else t
 return read()
def kids(s,k):return [x for x in s if isinstance(x,list) and x and x[0]==k]
def one(s,k):return kids(s,k)[0][1]
data=parse((ROOT/'review/ClassA.net').read_text());nets=kids(kids(data,'nets')[0],'net');lookup={};sets={}
for n in nets:
 name=one(n,'name');nodes={(one(x,'ref'),one(x,'pin')) for x in kids(n,'node')};sets[name]=nodes
 for node in nodes:lookup[node]=name
checks=[]
def same(*nodes):
 ns=[lookup.get(tuple(n)) for n in nodes];assert None not in ns and len(set(ns))==1,(nodes,ns);checks.append('same '+str(nodes))
def named(name,*nodes):
 for node in nodes:assert lookup.get(tuple(node)) in [name,'/'+name],(name,node,lookup.get(tuple(node)))
 checks.append(name+' '+str(nodes))
def separate(*nodes):
 ns=[lookup[tuple(n)] for n in nodes];assert len(set(ns))==len(ns),(nodes,ns);checks.append('separate '+str(nodes))
named('+40V',('J3','1'),('QOUT1','2'),('QOUT2','2'),('Q8','2'),('C6','1'),('C7','1'))
named('GND',('J3','2'),('R21','2'),('Q10','3'),('R8','2'),('R6','2'),('R7','2'),('C6','2'),('C7','2'),('C8','2'),('C9','2'),('R10','2'),('J1','2'),('J2','2'),('R29','2'),('R33','2'),('R34','2'))
named('VREF_20V',('R1','2'),('C4','2'),('C8','1'),('C9','1'),('R32','2'),('R33','1'),('TP16','1'))
named('+40V',('R32','1'))
named('AMP_OUT',('Q9','2'),('QSINK1','2'),('QSINK2','2'),('R15','2'),('R16','2'),('R30','1'),('L1','1'),('C3','1'))
named('PRE_CAP',('L1','2'),('R28','2'),('C10','1'))
named('SPK_OUT',('J2','1'),('C10','2'),('R34','1'),('TP12','1'))
separate(('C10','1'),('C10','2'),('L1','1'))
named('IN_PLUS',('Q1','3'),('R1','1'),('C1','2'));named('NFB',('Q2','3'),('R30','2'),('R31','1'))
named('VAS_B',('Q1','2'),('Q4','2'),('Q6','1'),('C2','1'));same(('Q2','2'),('Q5','2'),('Q5','3'),('Q4','3'))
named('VAS_OUT',('Q6','2'),('Q7','2'),('C2','2'),('R11','1'));same(('R11','2'),('Q8','1'))
named('UPPER_BASE',('Q8','3'),('R13','1'),('R14','1'),('R12','1'))
for qref,rbase,ballast in [('QOUT1','R13','R15'),('QOUT2','R14','R16'),('QSINK1','R17','R19'),('QSINK2','R18','R20')]:
 same((qref,'1'),(rbase,'2'));same((qref,'3'),(ballast,'1'));separate((qref,'1'),(qref,'2'),(qref,'3'));separate((ballast,'1'),(ballast,'2'))
named('SINK_BASE',('Q9','3'),('R17','1'),('R18','1'));named('SINK_CTRL',('Q10','2'),('Q9','1'),('R24','2'))
named('SINK_RETURN',('R19','2'),('R20','2'),('R21','1'));named('SENSE_AVG',('R22','1'),('R23','1'),('RV1','1'),('R27','1'))
same(('R22','2'),('QSINK1','3'));same(('R23','2'),('QSINK2','3'));same(('RV1','2'),('R26','1'));same(('R26','2'),('R27','2'),('Q10','1'));same(('RV1','3'),('R25','1'));separate(('RV1','1'),('RV1','2'),('RV1','3'))
named('P_BIAS',('Q3','3'),('Q7','1'),('D2','1'),('R10','1'));same(('D1','1'),('D2','2'));named('+40V',('D1','2'))
# Datasheet mapping is checked independently from the cached symbols.
sch=parse((ROOT/'ClassA.kicad_sch').read_text());libs=kids(kids(sch,'lib_symbols')[0],'symbol')
for lib in libs:
 if not lib[1].startswith('ClassA_Transistors:'):continue
 found={}
 for unit in kids(lib,'symbol'):
  for p in kids(unit,'pin'):found[one(p,'number')]=one(p,'name')
 expected={'1':'E','2':'C','3':'B'} if lib[1].split(':')[1] in ['KSC1845','KSA992'] else {'1':'B','2':'C','3':'E'}
 assert found==expected,(lib[1],found);checks.append('pins '+lib[1])
# Preserve the user's current component identities, placements and footprints.
before=parse((ROOT/'review/before-single-supply/ClassA.kicad_sch').read_text())
def byref(tree):return {one(x,'property'):x for x in []} # actual property-aware map below
def placed(tree):
 result={}
 for obj in kids(tree,'symbol'):
  props={p[1]:p[2] for p in kids(obj,'property')}
  result[props['Reference']]=(obj,props)
 return result
old=placed(before);cur=placed(sch)
for ref,(obj,props) in old.items():
 if ref=='R2' or ref.startswith('#'):continue
 assert ref in cur,ref
 now,fields=cur[ref]
 assert one(obj,'uuid')==one(now,'uuid'),ref
 assert fields.get('Footprint','')==props.get('Footprint',''),ref
 if ref!='J3':assert kids(obj,'at')==kids(now,'at'),ref
checks.append('existing component UUIDs, placement and footprints preserved except converted J3')
assert 'R2' not in cur
assert cur['C10'][1]['Value']=='4700u / 50V'
assert one(cur['J3'][0],'lib_id')=='Connector_Generic:Conn_01x02'
assert len(kids(cur['J3'][0],'pin'))==2
checks.append('mandatory input coupling; 4700u/50V polarized output cap; two-pin 40V supply')
# Preserve board and project state.
for line in (ROOT/'review/preserved-single-supply.sha256').read_text().splitlines():
 digest,name=line.split(None,1);assert hashlib.sha256((ROOT/name.strip()).read_bytes()).hexdigest()==digest,name
checks.append('PCB/project/preferences hashes unchanged')
report=f'{len(checks)} connectivity/pin/preservation checks passed.\n{len(nets)} exported nets. No simulation or bench validation.\n'
(ROOT/'review/connectivity.txt').write_text(report+'\n'.join(checks)+'\n')
print(report)
for n in nets:print(one(n,'name'), ' '.join(f'{r}.{p}' for r,p in sorted(sets[one(n,'name')]) if not r.startswith('#')))

from pathlib import Path
import xml.etree.ElementTree as ET,json,hashlib,sys,math,collections
ROOT=Path('/Users/tomwatson/Documents/GitHub/Kicadprojects/7377new/7377new/DiscreteClassD')
sys.path.insert(0,str(ROOT/'scripts'))
from sexp import *
B=ROOT/'output/verification/pre-cleanup-20260908'; O=ROOT/'output/verification/cleanup-20260908'
b=ET.parse(B/'netlist.xml').getroot(); a=ET.parse(O/'netlist.xml').getroot()
def nets(root):return {z.get('name'):{(n.get('ref'),n.get('pin')) for n in z.findall('node')} for z in root.findall('nets/net')}
def merge(n,p,q):
 k=next(k for k,v in n.items() if p in v);l=next(k for k,v in n.items() if q in v)
 assert k!=l,(p,q)
 n[k]|=n.pop(l)
bn=nets(b);an=nets(a)
bn['GND']|=bn.pop('PGND')
merge(bn,('R39','2'),('D22','2'));merge(bn,('R40','2'),('D23','2'))
shift={('U1','8'),('U3','8'),('C32','1'),('C33','1'),('C34','1'),('C35','1')}
assert shift<=bn['+12V_GD'];bn['+12V_GD']-=shift;bn['+12V_GD'].add(('R43','1'))
bn['+12V_A']=shift|{('R43','2'),('C50','1'),('C51','1'),('TP34','1')}
bn['GND']|={('C50','2'),('C51','2')}
expected={frozenset(v) for v in bn.values()};actual={frozenset(v) for v in an.values()}
missing=[sorted(v) for v in expected-actual];extra=[sorted(v) for v in actual-expected]
assert not missing and not extra,(missing,extra)
files=['DiscreteClassD.kicad_sch','PowerOutput_L.kicad_sch','PowerOutput_R.kicad_sch']
values=[];footprints=[];identity=[];new=[];groundcounts={};labels={};pin_tables={}
for f in files:
 old=parse((B/f).read_text());cur=parse((ROOT/f).read_text())
 def components(s):return {(prop(z,'Reference')[2],get(z,'unit')[1]):z for z in allof(s,'symbol') if not prop(z,'Reference')[2].startswith('#')}
 bc=components(old);ac=components(cur)
 assert bc.keys()<=ac.keys(),set(bc)-set(ac)
 new += [k for k in ac if k not in bc]
 for k,z in bc.items():
  v=ac[k]
  for field in ['uuid','lib_id','unit','dnp','in_bom','on_board']:
   if get(z,field)!=get(v,field):identity.append([f,k,field,get(z,field),get(v,field)])
  if prop(z,'Footprint')[2]!=prop(v,'Footprint')[2]:footprints.append([f,k])
  if prop(z,'Value')[2]!=prop(v,'Value')[2]:values.append([k[0],prop(z,'Value')[2],prop(v,'Value')[2]])
 text=(ROOT/f).read_text();assert 'PGND' not in text and 'AGND' not in text
 groundcounts[f]=sum(get(z,'lib_id')[1]=='power:GND' for z in allof(cur,'symbol'))
 labels[f]=sorted({z[1] for typ in ['label','hierarchical_label'] for z in allof(cur,typ)})
 assert not any(z[1]=='GND' for typ in ['label','global_label'] for z in allof(cur,typ))
 if f==files[0]:
  for r in ['U11','U12']:
   z=ac[(r,'1')];lib=next(x for x in allof(get(cur,'lib_symbols'),'symbol') if x[1]==get(z,'lib_id')[1])
   pin_tables[r]={'value':prop(z,'Value')[2],'library_id':get(z,'lib_id')[1],'footprint':prop(z,'Footprint')[2],'pins':{get(p,'number')[1]:get(p,'name')[1] for sub in allof(lib,'symbol') for p in allof(sub,'pin')}}
assert not identity and not footprints,(identity,footprints)
assert sorted(values)==[['R29','47k','51k'],['R36','47k','51k']],values
assert sorted(new)==[('C50','1'),('C51','1'),('R43','1'),('TP34','1')],new
for p in ROOT.glob('*.kicad_sch'):assert 'PGND' not in p.read_text() and 'AGND' not in p.read_text(),p
preservation={}
for l in (B/'untouched.sha256').read_text().splitlines():
 h,p=l.split(None,1);preservation[p]=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
for p in ['DiscreteClassD.kicad_sym','sym-lib-table']:preservation[p]=(ROOT/p).read_bytes()==(B/p).read_bytes()
assert all(preservation.values()),preservation
# Unreferenced legacy sheet changed only ground labels, names, and power-symbol cache.
lf='PowerOutput.kicad_sch';lc=parse((ROOT/lf).read_text());lb=parse((B/lf).read_text())
for typ in ['wire','junction','no_connect','sheet']:
 assert allof(lc,typ)==allof(lb,typ),(lf,typ)
lold={get(z,'uuid')[1]:z for z in allof(lb,'symbol')}
lnew={get(z,'uuid')[1]:z for z in allof(lc,'symbol')}
assert lold.keys()<=lnew.keys()
for u,z in lold.items():
 assert dump(z).replace('PGND','GND')==dump(lnew[u]),u
assert all(get(z,'lib_id')[1]=='power:GND' for u,z in lnew.items() if u not in lold)
erc=json.loads((O/'erc.json').read_text());be=json.loads((B/'erc.json').read_text())
assert erc['ignored_checks']==be['ignored_checks']
viol=[v for s in erc['sheets'] for v in s['violations']];assert not viol
# Directly verify supply and output boundaries as well as whole-net equivalence.
for r in ['U2','U6','U102','U106']:assert (r,'1') in an['+12V_GD']
assert {n for n in an if n in ['PGND','AGND']}==set()
for r in ['J15','J115']:
 for p in ['1','2']:assert (r,p) not in an['GND']
report={'passed':True,'baseline_physical_components':len(b.findall('components/comp')),'final_physical_components':len(a.findall('components/comp')),'expected_connectivity_matches':True,'unexpected_net_groups':extra,'missing_net_groups':missing,'original_symbols_and_footprints_preserved':True,'existing_value_changes':values,'new_components':[r for r,u in new],'ground_symbol_counts':groundcounts,'no_PGND_or_AGND_in_any_root_schematic':True,'legacy_sheet_only_ground_cleanup':True,'preserved_files_byte_for_byte':preservation,'ERC_violations':viol,'preexisting_ignored_checks_unchanged':erc['ignored_checks'],'remaining_local_and_hierarchical_labels':labels,'TPS7A4901':pin_tables,'nominal_attenuation':10/61,'nominal_output_Vrms_for_2Vrms':20/61,'nominal_output_Vpk_for_2Vrms':20/61*math.sqrt(2),'nominal_attenuation_dB':20*math.log10(10/61),'additional_electrical_repairs':['R39.2 and U10.1 reconnected to D22.2 and C47.1','R40.2 and U10.3 reconnected to D23.2 and C48.1']}
(O/'connectivity-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))

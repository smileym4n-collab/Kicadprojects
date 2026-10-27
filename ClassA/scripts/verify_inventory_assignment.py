from pathlib import Path
import re,json,hashlib,collections
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'review/inventory-2026-10-25'
ns={'__file__':str(ROOT/'scripts/convert_single_supply.py')};exec((ROOT/'scripts/convert_single_supply.py').read_text().split("ns={'__file__'")[0],ns);parse=ns['parse']
def kids(s,k):return [x for x in s if isinstance(x,list) and x and x[0]==k]
def fld(s,k):return kids(s,k)[0]
def one(s,k):return fld(s,k)[1]
def placed(s):return {str(next(p[2] for p in kids(x,'property') if p[1]=='Reference')):x for x in kids(s,'symbol')}
def props(s):return {p[1]:p[2] for p in kids(s,'property')}
checks=[]
FIX=ROOT/'review/erc-fix-2026-10-25'
fix=json.loads((FIX/'fix.json').read_text()) if (FIX/'fix.json').exists() else None
current_net=FIX/'ClassA.net' if fix else OUT/'ClassA.net'
before=parse((OUT/'before/ClassA.kicad_sch').read_text());after=parse((ROOT/'ClassA.kicad_sch').read_text());bp=placed(before);ap=placed(after)
assert bp.keys()==ap.keys();checks.append('All component references retained')
for tag in ['wire','junction','label','global_label','hierarchical_label','no_connect','lib_symbols']:
 if tag=='junction' and fix:
  j=kids(after,tag);added=[x for x in j if one(x,'uuid')==fix['junction_uuid']]
  assert len(added)==1 and list(map(float,fld(added[0],'at')[1:]))==fix['at']
  assert [x for x in j if x is not added[0]]==kids(before,tag)
  checks.append('Only documented Q5 mirror-reference junction added');continue
 assert kids(before,tag)==kids(after,tag),tag;checks.append('Unchanged '+tag)
allowed_values={'C7','C8','C9','R10'}
for ref,s in bp.items():
 t=ap[ref];p=props(s);p2=props(t)
 for tag in ['uuid','at','lib_id','unit','mirror','instances','pin','dnp','in_bom','on_board']:
  assert kids(s,tag)==kids(t,tag),(ref,tag)
 if ref not in allowed_values:assert p['Value']==p2['Value'],ref
 checks.append('Identity/placement/pin mapping '+ref)
def netsets(path):
 ns=kids(parse(path.read_text()),'nets')[0]
 return {str(one(n,'name')):{(str(one(p,'ref')),str(one(p,'pin'))) for p in kids(n,'node')} for n in kids(ns,'net')}
bn=netsets(OUT/'before/ClassA.net');an=netsets(current_net)
if fix:
 k1=next(k for k,v in bn.items() if ('Q4','3') in v);k2=next(k for k,v in bn.items() if ('Q5','2') in v)
 assert k1!=k2;merged=bn.pop(k1)|bn.pop(k2);k=next(k for k,v in an.items() if ('Q4','3') in v)
 assert an[k]==merged;an.pop(k)
assert bn==an;checks.append('Only documented mirror-reference net merge; other nets unchanged' if fix else 'Exported named net/pin sets identical before/after')
# Compare ERC finding bodies, allowing report timestamps to change.
def findings(path):return path.read_text().split('***** Sheet /',1)[1]
if fix:
 assert '** ERC messages: 0  Errors 0  Warnings 0' in (FIX/'ERC.rpt').read_text();checks.append('ERC now clean after separately authorized Q5 junction repair')
else:
 assert findings(OUT/'before/ERC.rpt')==findings(OUT/'ERC.rpt');checks.append('ERC unchanged: one pre-existing Q4-base error; no new warnings/errors')
for line in (OUT/'preserved.sha256').read_text().splitlines():
 digest,p=line.split(None,1);assert hashlib.sha256((ROOT/p.strip()).read_bytes()).hexdigest()==digest;checks.append('Hash preserved '+p)
# Resolve every nonempty footprint and check pad-number parity and holes.
rows=json.loads((OUT/'assignments.json').read_text());LIB=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints');cache={}
for row in rows:
 ref=row['Reference'];fp=row['Footprint']
 if not fp:continue
 lib,name=fp.split(':');path=(ROOT/'ClassA_Inventory.pretty' if lib=='ClassA_Inventory' else LIB/(lib+'.pretty'))/(name+'.kicad_mod')
 assert path.exists(),(ref,path)
 f=cache.setdefault(fp,parse(path.read_text()));pads=kids(f,'pad');padnums={str(p[1]) for p in pads if p[1]};spins={str(x[1]) for x in kids(ap[ref],'pin')}
 assert padnums==spins,(ref,padnums,spins)
 for p in pads:
  if p[2]=='thru_hole':
   size=[float(n) for n in fld(p,'size')[1:]];hole=float(one(p,'drill'));assert min(size)>hole,(ref,hole,size)
 checks.append('Footprint resolved and pad/pin parity '+ref)
# Confirm quantities are available for each selected MPN for this ONE mono channel.
counts=collections.Counter(r['Inventory_ID'] for r in rows if r['Status']=='IN STOCK')
for i,n in counts.items():
 r=next(r for r in rows if r['Inventory_ID']==i);assert int(r['Available'])>=n,(i,n,r['Available']);checks.append(f'Stock ID{i}: need {n}, available {r["Available"]}')
# Explicitly retained no-guess gaps and required output capacitor polarity.
assert props(ap['RV1'])['Footprint']==''
for ref in ['R15','R16','R19','R20','R21']:assert props(ap[ref])['Footprint']==''
assert ('C10','1') in netsets(current_net)['/PRE_CAP'];assert ('C10','2') in netsets(current_net)['/SPK_OUT']
checks.append('C10 polarity preserved; user-delegated parts remain unassigned')
for fp,n in [('Toshiba_2SC5198_TO3PN_BCE_P5.45_Envelope',3),('Toshiba_2_10R1A_BCE_P2.54_Envelope',3),('Multicomp_MC34629_1x02_P2.54mm',2),('Multicomp_MCGPR50V478M22X41_Radial_P10',2)]:
 aliases={'Toshiba_2SC5198_TO3PN_BCE_P5.45_Envelope':'Package_TO_SOT_THT:TO-3P-3_Vertical','Toshiba_2_10R1A_BCE_P2.54_Envelope':'Package_TO_SOT_THT:TO-220F-3_Vertical'}
 if fp in aliases:
  lib,name=aliases[fp].split(':');path=LIB/(lib+'.pretty')/(name+'.kicad_mod')
 else:path=ROOT/'ClassA_Inventory.pretty'/(fp+'.kicad_mod')
 f=parse(path.read_text());pads=kids(f,'pad');assert len(pads)==n
 xs=[float(fld(p,'at')[1]) for p in pads]
 if fp.startswith('Toshiba_2SC'):assert xs==[0,5.45,10.9]
 elif fp.startswith('Toshiba_2_'):assert xs==[0,2.54,5.08]
 elif fp.startswith('Multicomp_MC346'):assert xs==[0,-2.54]
 else:assert xs==[0,10]
 checks.append('Manufacturer lead pitch '+fp)
(OUT/'verification-after-erc-fix.txt' if fix else 'verification.txt').write_text(f'{len(checks)} assignment/preservation checks passed.\n'+ '\n'.join(checks)+'\n')
print(f'{len(checks)} assignment/preservation checks passed. {len(cache)} distinct footprints resolved. Part assignments preserved; net changes restricted to the separately documented mirror repair.')

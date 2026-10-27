from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'review/standard-footprints-2026-10-25'
ns={'__file__':str(ROOT/'scripts/convert_single_supply.py')};exec((ROOT/'scripts/convert_single_supply.py').read_text().split("ns={'__file__'")[0],ns);parse=ns['parse']
def kids(s,k):return [x for x in s if isinstance(x,list) and x and x[0]==k]
def fld(s,k):return kids(s,k)[0]
def one(s,k):return fld(s,k)[1]
def props(s):return {p[1]:p[2] for p in kids(s,'property')}
def placed(s):return {props(x)['Reference']:x for x in kids(s,'symbol')}
before=parse((OUT/'before/ClassA.kicad_sch').read_text());after=parse((ROOT/'ClassA.kicad_sch').read_text());change=json.loads((OUT/'changes.json').read_text());checks=[]
# Exactly the requested footprint/note fields plus the separately authorized Q5 junction.
normalized=parse((ROOT/'ClassA.kicad_sch').read_text());bp=placed(before);ap=placed(normalized)
assert bp.keys()==ap.keys()
for ref,s in ap.items():
 if ref in change['footprints']:
  for p in kids(s,'property'):
   if p[1] in ['Footprint','Assignment_Notes']:
    p[2]=next(x[2] for x in kids(bp[ref],'property') if x[1]==p[1])
 assert s==bp[ref],ref;checks.append('All other component fields/placement preserved '+ref)
if change['junction_restored']:
 marker=change['junction'];j=next(x for x in kids(normalized,'junction') if one(x,'uuid')==marker['junction_uuid']);assert list(map(float,fld(j,'at')[1:]))==marker['at'];normalized.remove(j)
assert normalized==before;checks.append('No other schematic object changes')
def nets(path):
 s=parse(path.read_text());return {str(one(n,'name')):{(str(one(x,'ref')),str(one(x,'pin'))) for x in kids(n,'node')} for n in kids(kids(s,'nets')[0],'net')}
b=nets(OUT/'before/ClassA.net');a=nets(OUT/'ClassA.net')
if change['junction_restored']:
 k1=next(k for k,v in b.items() if ('Q4','3') in v);k2=next(k for k,v in b.items() if ('Q5','2') in v);merged=b.pop(k1)|b.pop(k2);k=next(k for k,v in a.items() if ('Q4','3') in v);assert a.pop(k)==merged
assert a==b;checks.append('Only Q5 mirror junction net merge; all other connectivity preserved')
LIB=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints');std=custom=0
for ref,s in placed(after).items():
 fp=props(s).get('Footprint','')
 if not fp:continue
 lib,name=fp.split(':');p=(ROOT/'ClassA_Inventory.pretty' if lib=='ClassA_Inventory' else LIB/(lib+'.pretty'))/(name+'.kicad_mod');assert p.exists(),p
 f=parse(p.read_text());assert {x[1] for x in kids(f,'pad') if x[1]}=={x[1] for x in kids(s,'pin')},ref
 if lib=='ClassA_Inventory':custom+=1
 else:std+=1
 checks.append('Resolved footprint and pad parity '+ref)
for line in (OUT/'preserved.sha256').read_text().splitlines():
 digest,p=line.split(None,1);assert hashlib.sha256((ROOT/p.strip()).read_bytes()).hexdigest()==digest;checks.append('Preserved '+p)
assert '** ERC messages: 0  Errors 0  Warnings 0' in (OUT/'ERC.rpt').read_text();checks.append('ERC 0 errors / 0 warnings')
(OUT/'verification.txt').write_text(f'{len(checks)} checks passed. {std} standard and {custom} custom assigned footprints.\n'+'\n'.join(checks)+'\n');print(f'{len(checks)} checks passed; {std} standard footprints, {custom} custom. ERC clean.')

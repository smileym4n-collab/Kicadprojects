from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'review/erc-fix-2026-10-25'
ns={'__file__':str(ROOT/'scripts/convert_single_supply.py')};exec((ROOT/'scripts/convert_single_supply.py').read_text().split("ns={'__file__'")[0],ns);parse=ns['parse']
def kids(s,k):return [x for x in s if isinstance(x,list) and x and x[0]==k]
def one(s,k):return kids(s,k)[0][1]
before=parse((OUT/'before/ClassA.kicad_sch').read_text());after=parse((ROOT/'ClassA.kicad_sch').read_text());fix=json.loads((OUT/'fix.json').read_text());checks=[]
added=[x for x in kids(after,'junction') if str(one(x,'uuid'))==fix['junction_uuid']];assert len(added)==1
assert list(map(float,kids(added[0],'at')[0][1:]))==fix['at'];checks.append('One junction added at the intended crossing')
assert [x for x in after if x is not added[0]]==before;checks.append('Every other schematic object unchanged, including all component/footprint/inventory fields')
def nets(path):
 data=parse(path.read_text());return {str(one(n,'name')):{(str(one(x,'ref')),str(one(x,'pin'))) for x in kids(n,'node')} for n in kids(kids(data,'nets')[0],'net')}
b=nets(OUT/'before/ClassA.net');a=nets(OUT/'ClassA.net')
k1=next(k for k,v in b.items() if ('Q4','3') in v);k2=next(k for k,v in b.items() if ('Q5','2') in v);assert k1!=k2
joined=b.pop(k1)|b.pop(k2);assert joined=={('Q4','3'),('Q5','3'),('Q5','2'),('Q2','2')}
k=next(k for k,v in a.items() if ('Q4','3') in v);assert a[k]==joined;assert {x:y for x,y in a.items() if x!=k}==b
checks+=['Q5 collector joined to both mirror bases and Q2 collector','All other exported net/pin sets identical']
for line in (OUT/'preserved.sha256').read_text().splitlines():
 digest,p=line.split(None,1);assert hashlib.sha256((ROOT/p.strip()).read_bytes()).hexdigest()==digest;checks.append('Preserved '+p)
r=(OUT/'ERC.rpt').read_text();assert '** ERC messages: 0  Errors 0  Warnings 0' in r;checks.append('Final ERC: 0 errors, 0 warnings; no rule changes')
(OUT/'verification.txt').write_text(f'{len(checks)} scoped ERC-fix checks passed.\n'+'\n'.join(checks)+'\n');print(f'{len(checks)} scoped ERC-fix checks passed.')

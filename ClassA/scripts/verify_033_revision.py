"""Scoped preservation and loaded DC bias-network checks for the 0R33 revision.

The linear bias calculation fixes Q10 VBE/IB; it is not transistor simulation
or a guaranteed temperature/current range. Run fresh KiCad exports first.
"""
from pathlib import Path
import json,hashlib,itertools
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'review/0R33-revision-2026-10-25'
ns={'__file__':str(ROOT/'scripts/convert_single_supply.py')}
exec((ROOT/'scripts/convert_single_supply.py').read_text().split("ns={'__file__'")[0],ns)
parse,kids,fld=map(ns.get,['parse','kids','fld'])
def props(s):return {str(p[1]):str(p[2]) for p in kids(s,'property')}
def placed(s):return {props(x)['Reference']:x for x in kids(s,'symbol')}
def nets(p):
 s=parse(p.read_text());return {frozenset((str(fld(x,'ref')[1]),str(fld(x,'pin')[1])) for x in kids(n,'node')) for n in kids(fld(s,'nets'),'net')}
c=json.loads((OUT/'changes.json').read_text());checks=[]
b=parse((OUT/'before/ClassA.kicad_sch').read_text());a=parse((ROOT/'ClassA.kicad_sch').read_text())
bp,ap=placed(b),placed(a);assert bp.keys()==ap.keys()
for ref,s in ap.items():
 u=c['updates'].get(ref,{})
 for p in kids(s,'property'):
  if str(p[1]) in u:
   assert str(p[2])==u[str(p[1])],(ref,p[1]);p[2]=next(x[2] for x in kids(bp[ref],'property') if x[1]==p[1])
 assert s==bp[ref],ref;checks.append('All other fields/placement preserved '+ref)
for t in kids(a,'text'):
 if str(t[1])==c['new_text']:t[1]=ns['Atom'](c['old_text'],True);break
else:raise AssertionError('Missing setup note')
if c['junction_restored']:
 j=next(x for x in kids(a,'junction') if fld(x,'uuid')[1]==c['junction']['junction_uuid']);assert list(map(float,fld(j,'at')[1:]))==c['junction']['at'];a.remove(j)
assert a==b;checks.append('Only five components, setup note and authorized Q5 junction changed')
bn=nets(OUT/'before/ClassA.net');an=nets(OUT/'ClassA.net')
if c['junction_restored']:
 n1=next(x for x in bn if ('Q4','3') in x);n2=next(x for x in bn if ('Q5','2') in x);bn.remove(n1);bn.remove(n2);bn.add(n1|n2)
assert an==bn;checks.append('All nets preserved except intended Q5 mirror-base merge')
for group in [{('R19','2'),('R20','2'),('R21','1')},{('R22','1'),('R23','1'),('R27','1'),('RV1','1')},{('Q10','1'),('R26','2'),('R27','2')},{('RV1','3'),('R25','1')},{('R25','2'),('R21','2'),('Q10','3')}]:
 assert any(group<=n for n in an),group;checks.append('Bias-net endpoints '+str(sorted(group)))
for line in (OUT/'preserved.sha256').read_text().splitlines():
 digest,p=line.split(None,1);assert hashlib.sha256((ROOT/p.strip()).read_bytes()).hexdigest()==digest;checks.append('Preserved '+p)
fp=parse((ROOT/c['footprint']).read_text());pads=kids(fp,'pad');assert {p[1] for p in pads}=={'1','2'}
for p in pads:assert float(fld(p,'drill')[1])>=.85+.3
assert sorted(float(fld(p,'at')[1]) for p in pads)==[0,30.48]
cy=next(x for x in kids(fp,'fp_rect') if fld(x,'layer')[1]=='F.CrtYd');assert list(map(float,fld(cy,'start')[1:]))==[-1.7,-5.75];assert list(map(float,fld(cy,'end')[1:]))==[32.18,5.75]
assert (30.48-23.5)/2>3 and 5.75>=10.5/2+.5
checks.append('Two pads, 30.48mm formed pitch, lead-hole margin, max-body courtyard')
actual=placed(parse((ROOT/'ClassA.kicad_sch').read_text()));rows={r['Reference']:r for r in json.loads((ROOT/'review/inventory-2026-10-25/assignments.json').read_text())}
for ref in c['updates']:
 p=props(actual[ref]);r=rows[ref]
 for k in ['Value','Footprint','Manufacturer','MPN','Inventory_ID']:assert str(r[k])==p[k],(ref,k)
 checks.append('Synchronized BOM '+ref)
erc=(OUT/'ERC.rpt').read_text();assert '** ERC messages: 1  Errors 0  Warnings 1' in erc;assert "library 'YamahaSalvage'" in erc
checks.append('ERC: zero errors, one retained pre-existing YamahaSalvage warning')

# Linear KCL solve: matched sink emitters E -> Rb/2 -> common return T;
# E -> averaging pair Rav/2 -> SENSE_AVG S; S -> pot -> W -> R25 -> GND;
# S -> R27 -> B, W -> R26 -> B. B is fixed at Q10 VBE, with load IB.
# Unknowns E,T,S,W,total emitter current. Pot endpoint uses a negligible 1uOhm.
def solve(vbe,ib,t,r25=470,rb=.33,r21=.27,pot=1000):
 n=5;m=[[0.0]*(n+1) for _ in range(n)]
 def resistor(i,j,r):
  g=1/r;m[i][i]+=g
  if j is None:return
  m[j][j]+=g;m[i][j]-=g;m[j][i]-=g
 resistor(0,1,rb/2);resistor(1,None,r21);resistor(0,2,50)
 resistor(2,3,max(1e-6,t*pot));resistor(3,None,(1-t)*pot+r25)
 for i,r in [(2,1000),(3,100)]:m[i][i]+=1/r;m[i][n]+=vbe/r
 m[0][4]=-1;m[4][2]=1/1000;m[4][3]=1/100;m[4][n]=ib+vbe*(1/1000+1/100)
 for col in range(n):
  row=max(range(col,n),key=lambda r:abs(m[r][col]));m[col],m[row]=m[row],m[col]
  pivot=m[col][col];assert abs(pivot)>1e-12;m[col]=[x/pivot for x in m[col]]
  for r in range(n):
   if r==col:continue
   f=m[r][col];m[r]=[x-f*y for x,y in zip(m[r],m[col])]
 return [row[n] for row in m]
result=[]
for vb,ib in itertools.product([.55,.65,.75],[0,.00015]):
 lo=solve(vb,ib,0)[4];hi=solve(vb,ib,1)[4];assert lo<2<hi,(vb,ib,lo,hi)
 result.append(f'VBE {vb:.2f} V, IB {ib*1e6:.0f} uA: total emitter-current adjustment {lo:.3f} to {hi:.3f} A')
# Conservative component corners, not a guaranteed device/thermal envelope.
for vb,ib,pr,rr,br,cr in itertools.product([.55,.75],[0,.00015],[800,1200],[470*.99,470*1.01],[.33*.95,.33*1.05],[.27*.95,.27*1.05]):
 assert solve(vb,ib,0,rr,br,cr,pr)[4]<2<solve(vb,ib,1,rr,br,cr,pr)[4]
checks.append('2A is inside loaded DC trim range for stated VBE/IB and resistor/pot corners')
new=solve(.65,0,1)[4];old=solve(.65,0,1,r25=3300)[4]
assert new>2 and old<2
checks.append(f'At VBE0.65V/IB0, max trim rises from {old:.3f}A (3k3) to {new:.3f}A (470R)')
rw=1000*1100/2100;alpha=(1000*(470/(470+rw))+100)/1100
assert .52<alpha<.53
result+=['No-load minimum Q10-base/sense ratio: '+str(alpha),'These are DC network calculations, not SPICE, thermal or stability validation. Actual current is set by measured drops; resistor and branch mismatch alter targets. R21 current is slightly below emitter total due to sensing-network loading.']
(OUT/'bias-calculation.txt').write_text('\n'.join(result)+'\n')
(OUT/'verification.txt').write_text(str(len(checks))+' checks passed\n'+'\n'.join(checks)+'\n')
print(str(len(checks))+' checks passed; ERC 0 errors / 1 pre-existing warning.');print('\n'.join(result))

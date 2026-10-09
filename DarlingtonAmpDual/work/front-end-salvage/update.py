from pathlib import Path
import re, json, shutil, hashlib, copy
ROOT=Path.cwd();out=ROOT/'work/front-end-salvage';back=out/'backup';back.mkdir(exist_ok=True)
class Atom(str):pass
def parse(s):
 ts=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',s);i=0
 def walk():
  nonlocal i
  if ts[i]=='(':
   i+=1;a=[]
   while ts[i]!=')':a.append(walk())
   i+=1;return a
  t=ts[i];i+=1;return json.loads(t) if t.startswith('"') else Atom(t)
 return walk()
def dump(a):
 if isinstance(a,list):return '('+' '.join(dump(x) for x in a)+')'
 return str(a) if isinstance(a,Atom) else json.dumps(a)
def children(a,k):return [x for x in a if isinstance(x,list) and x and x[0]==k]
def prop(s,k):return next(x for x in children(s,'property') if x[1]==k)
files=['DarlingtonAmp.kicad_sch','DarlingtonAmp.kicad_sym','DarlingtonAmp.kicad_pro','DarlingtonAmp.kicad_pcb']
for f in files:shutil.copy2(ROOT/f,back/f)
fp='Package_TO_SOT_THT:TO-92_Inline'
assert (Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints')/'Package_TO_SOT_THT.pretty/TO-92_Inline.kicad_mod').exists()
mapping={'KSC1845':('2SC2240','https://www.taydaelectronics.com/datasheets/A-904.pdf','NPN'),'KSA992':('2SA970','https://kvazer.com/resources/prod_24895_2sa970pdf.pdf','PNP')}
libpath=ROOT/'DarlingtonAmp.kicad_sym';lib=libpath.read_text();ast=parse(lib);news=[]
for old,(new,ds,pol) in mapping.items():
 node=copy.deepcopy(next(s for s in children(ast,'symbol') if s[1]==old));node[1]=new
 for sub in children(node,'symbol'):sub[1]=sub[1].replace(old,new)
 prop(node,'Value')[2]=new;prop(node,'Footprint')[2]=fp;prop(node,'Datasheet')[2]=ds
 prop(node,'Description')[2]=f'Toshiba {pol} low-noise audio transistor, 120V 100mA 300mW; pins 1 E / 2 C / 3 B; salvaged, test and match before fitting'
 news.append(dump(node))
i=lib.rfind(')');libpath.write_text(lib[:i]+'\n'+'\n'.join(news)+'\n'+lib[i:])
sch=ROOT/'DarlingtonAmp.kicad_sch';s=sch.read_text()
for old,(new,ds,pol) in mapping.items():s=s.replace(old,new)
s=s.replace('https://www.onsemi.com/download/data-sheet/pdf/ksc1845-d.pdf',mapping['KSC1845'][1]).replace('https://www.onsemi.com/download/data-sheet/pdf/ksa992-d.pdf',mapping['KSA992'][1])
s=s.replace('Package_TO_SOT_THT:TO-92L_Wide',fp)
# Replace cached symbol definitions with the corresponding new local definitions,
# preserving their geometry and pin locations exactly.
def spans(text):
 depth=0;start=None;quoted=False;escaped=False
 for i,c in enumerate(text):
  if quoted:
   if escaped:escaped=False
   elif c=='\\':escaped=True
   elif c=='"':quoted=False
   continue
  if c=='"':quoted=True;continue
  if c=='(':
   if depth==2:start=i
   depth+=1
  elif c==')':
   depth-=1
   if depth==2 and start is not None:yield start,i+1;start=None
for start,end in reversed(list(spans(s))):
 block=s[start:end]
 for text in news:
  node=parse(text);new=node[1]
  if block.startswith('(symbol "DarlingtonAmp:'+new+'"'):
   node[1]='DarlingtonAmp:'+new;s=s[:start]+dump(node)+s[end:]
sch.write_text(s)
a=parse(s)
inst=children(a,'symbol')
for ref in ['Q1','Q2','Q5','Q6','Q7','Q3','Q4']:
 node=next(n for n in inst if prop(n,'Reference')[2]==ref)
 wanted='2SA970' if ref in ['Q3','Q4'] else '2SC2240'
 assert prop(node,'Value')[2]==wanted
 assert prop(node,'Footprint')[2]==fp
for f in ['DarlingtonAmp.kicad_pro','DarlingtonAmp.kicad_pcb']:
 assert (ROOT/f).read_bytes()==(back/f).read_bytes(),f
print('Updated seven transistor instances and cached/local symbols; PCB/project unchanged.')

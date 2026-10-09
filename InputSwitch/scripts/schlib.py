import re,json,copy,math,uuid
from pathlib import Path
class Atom(str):pass
def parse(s):
 ts=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',s); stack=[];root=None
 for t in ts:
  if t=='(':
   n=[]
   if stack: stack[-1].append(n)
   stack.append(n)
  elif t==')':
   root=stack.pop()
  else: stack[-1].append(json.loads(t) if t.startswith('"') else Atom(t))
 return root
def dump(x):
 if isinstance(x,list):return '('+' '.join(dump(i) for i in x)+')'
 if isinstance(x,Atom):return str(x)
 return json.dumps(x,ensure_ascii=False)
def child(n,k):return next((x for x in n if isinstance(x,list) and x and x[0]==k),None)
def kids(n,k):return [x for x in n if isinstance(x,list) and x and x[0]==k]
def val(n,k,d=None):
 c=child(n,k);return c[1] if c else d
def uid():return str(uuid.uuid4())
LIB=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols')
cache={}
def lib(name):
 group,key=name.split(':',1)
 if group not in cache:cache[group]=parse((LIB/(group+'.kicad_sym')).read_text())
 def flatten(key):
  s=copy.deepcopy(next(s for s in kids(cache[group],'symbol') if s[1]==key))
  ext=val(s,'extends')
  if ext:
   p=flatten(ext)
   own={x[1] for x in kids(s,'property')}
   s=[x for x in s if not(isinstance(x,list) and x[0]=='extends')]
   s+= [x for x in p[2:] if isinstance(x,list) and (x[0]=='symbol' or (x[0]=='property' and x[1] not in own))]
   for k in ['pin_names','pin_numbers']:
    if child(s,k) is None and child(p,k):s.append(copy.deepcopy(child(p,k)))
   for sub in kids(s,'symbol'):sub[1]=str(sub[1]).replace(ext+'_',key+'_',1)
  return s
 s=flatten(key);s[1]=name;return s
if __name__=='__main__':
 for n in ['MCU_Microchip_ATtiny:ATtiny412-SS','Transistor_Array:ULN2003A','Relay:G6K-2','Amplifier_Operational:LM358','Device:R','Device:C','Device:D','Transistor_BJT:BC549','Connector_Generic:Conn_01x02','Isolator:PC817','Regulator_Switching:R-78E5.0-0.5']:
  try:
   s=lib(n); print(n)
   for sub in kids(s,'symbol'):
    for p in kids(sub,'pin'): print(sub[1],val(p,'number'),val(p,'name'),child(p,'at')[1:])
  except Exception as e:print(e)

import re,json,copy,uuid,math
from pathlib import Path
class S(str): pass
def parse(s):
 ts=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',s); stack=[];root=None
 for t in ts:
  if t=='(': 
   a=[]
   if stack: stack[-1].append(a)
   else: root=a
   stack.append(a)
  elif t==')':stack.pop()
  else:stack[-1].append(json.loads(t) if t.startswith('"') else S(t))
 return root
def atom(x):
 if isinstance(x,S):return x
 return json.dumps(x,ensure_ascii=False)
def dump(x,ind=0):
 if not isinstance(x,list):return atom(x)
 if not any(isinstance(y,list) for y in x):return '('+' '.join(atom(y) for y in x)+')'
 out='('+' '.join(atom(y) for y in x if not isinstance(y,list))
 for y in x:
  if isinstance(y,list):out+='\n'+'\t'*(ind+1)+dump(y,ind+1)
 return out+'\n'+'\t'*ind+')'
def get(n,k):return next((x for x in n if isinstance(x,list) and x[0]==k),None)
def many(n,k):return [x for x in n if isinstance(x,list) and x[0]==k]
def prop(n,k):return next((x for x in many(n,'property') if x[1]==k),None)
def val(n,k):
 p=prop(n,k);return p[2] if p else None
def load(f):return parse(Path(f).read_text())
def save(f,n):Path(f).write_text(dump(n)+'\n')
def pins(n,s):
 lib=next(x for x in many(get(n,'lib_symbols'),'symbol') if x[1]==get(s,'lib_id')[1])
 res=[];at=get(s,'at');a=math.radians(float(at[3]));mx=get(s,'mirror')
 for unit in many(lib,'symbol'):
  for p in many(unit,'pin'):
   xy=get(p,'at');x,y=float(xy[1]),-float(xy[2])
   if mx and mx[1]=='x':y=-y
   if mx and mx[1]=='y':x=-x
   res.append((get(p,'number')[1],get(p,'name')[1],round(float(at[1])+x*math.cos(a)+y*math.sin(a),6),round(float(at[2])-x*math.sin(a)+y*math.cos(a),6),p[1]))
 return res
if __name__=='__main__':
 for f in Path('.').glob('*.kicad_sch'):
  n=load(f);print('\nFILE',f)
  for s in many(n,'symbol'):
   print(val(s,'Reference'),val(s,'Value'),get(s,'at'),pins(n,s))
  for k in ['sheet','hierarchical_label','label','text']:
   for x in many(n,k):print(k,dump(x))

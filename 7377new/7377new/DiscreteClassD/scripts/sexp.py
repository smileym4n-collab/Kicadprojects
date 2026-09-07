import re,json
class Q(str): pass
def parse(s):
 ts=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',s); stack=[]; root=None
 for t in ts:
  if t=='(':
   a=[]
   if stack: stack[-1].append(a)
   stack.append(a)
  elif t==')': root=stack.pop()
  else: stack[-1].append(Q(json.loads(t)) if t.startswith('"') else t)
 return root
def dump(a,level=0):
 if isinstance(a,Q): return json.dumps(str(a),ensure_ascii=False)
 if not isinstance(a,list): return str(a)
 if not any(isinstance(x,list) for x in a): return '('+' '.join(dump(x) for x in a)+')'
 return '('+' '.join(dump(x) for x in a if not isinstance(x,list))+''.join('\n'+'\t'*(level+1)+dump(x,level+1) for x in a if isinstance(x,list))+'\n'+'\t'*level+')'
def get(a,k): return next((x for x in a if isinstance(x,list) and x[0]==k),None)
def allof(a,k): return [x for x in a if isinstance(x,list) and x[0]==k]
def prop(a,k): return next((x for x in allof(a,'property') if x[1]==k),None)
if __name__=='__main__':
 from pathlib import Path
 a=parse(Path('DiscreteClassD.kicad_sch').read_text())
 for x in allof(a,'symbol'): print(prop(x,'Reference')[2],prop(x,'Value')[2],get(x,'at'),get(x,'unit'))

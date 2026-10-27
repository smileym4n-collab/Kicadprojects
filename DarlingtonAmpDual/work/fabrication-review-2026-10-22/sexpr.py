from pathlib import Path
import re,json,math,xml.etree.ElementTree as E
D=Path(__file__).parent

def parse(path):
 t=re.findall(r'"(?:\\.|[^"\\])*"|[^\s()]+|[()]',Path(path).read_text()); stack=[]; root=[]
 for a in t:
  if a=='(': n=[]; (stack[-1] if stack else root).append(n);stack.append(n)
  elif a==')':stack.pop()
  else:stack[-1].append(json.loads(a) if a.startswith('"') else a)
 return root[0]
def all(x,k):return [i for i in x if isinstance(i,list) and i and i[0]==k]
def one(x,k,default=None):return next(iter(all(x,k)),default)
def val(x,k,default=''):a=one(x,k);return a[1] if a else default

import re,json
from pathlib import Path

def parse(text):
 toks=list(re.finditer(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+',text));i=0
 def get():
  nonlocal i
  t=toks[i];i+=1
  if t[0]=='(':
   a=[]
   while toks[i][0]!=')':a.append(get())
   i+=1;return a
  return json.loads(t[0]) if t[0].startswith('"') else t[0]
 return get()
def children(a,key):return [x for x in a if isinstance(x,list) and x and x[0]==key]
def child(a,key):return next(iter(children(a,key)),None)
def prop(a,key):return next((x[2] for x in children(a,'property') if x[1]==key),None)
def topblocks(text):
 depth=0;start=None;quote=False;escape=False
 for i,c in enumerate(text):
  if quote:
   if escape:escape=False
   elif c=='\\':escape=True
   elif c=='"':quote=False
  elif c=='"':quote=True
  elif c=='(':
   if depth==1:start=i
   depth+=1
  elif c==')':
   depth-=1
   if depth==1 and start is not None:yield start,i+1,text[start:i+1]

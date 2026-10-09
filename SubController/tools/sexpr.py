import re, json
class Q(str): pass
def parse(s):
    toks=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',s)
    stack=[]; root=None
    for t in toks:
        if t=='(':
            a=[]
            if stack: stack[-1].append(a)
            stack.append(a)
        elif t==')':
            root=stack.pop()
        else: stack[-1].append(Q(json.loads(t)) if t.startswith('"') else t)
    return root
def dump(a):
    if isinstance(a,list): return '('+' '.join(dump(x) for x in a)+')'
    return json.dumps(str(a),ensure_ascii=False) if isinstance(a,Q) else str(a)
def children(a,key): return [x for x in a if isinstance(x,list) and x and x[0]==key]
def child(a,key): return next(iter(children(a,key)),None)

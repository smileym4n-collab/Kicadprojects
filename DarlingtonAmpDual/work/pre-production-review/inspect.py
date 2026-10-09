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
b=parse('DarlingtonAmp.kicad_pcb'); fps=[]; pads=[]
for f in all(b,'footprint'):
 props={p[1]:p[2] for p in all(f,'property')};a=one(f,'at');x,y=map(float,a[1:3]);rot=float(a[3]) if len(a)>3 else 0
 pp=[]
 for p in all(f,'pad'):
  at=one(p,'at');px,py=map(float,at[1:3]);r=math.radians(rot);xy=[x+px*math.cos(r)+py*math.sin(r),y-px*math.sin(r)+py*math.cos(r)]
  n=one(p,'net',['net','','']);z={'ref':props['Reference'],'pin':p[1],'xy':xy,'net':n[-1],'size':one(p,'size')[1:],'drill':one(p,'drill'),'type':p[2],'shape':p[3]};pp.append(z);pads.append(z)
 fps.append({'ref':props['Reference'],'value':props.get('Value'),'fp':f[1],'xy':[x,y],'rotation':rot,'pads':pp})
segs=[{'start':list(map(float,one(s,'start')[1:])),'end':list(map(float,one(s,'end')[1:])),'width':float(val(s,'width')),'layer':val(s,'layer'),'net':val(s,'net')} for s in all(b,'segment')]
for a in all(b,'arc'):
 st,mi,en=[tuple(map(float,one(a,k)[1:])) for k in ['start','mid','end']]
 ax,ay=st;bx,by=mi;cx,cy=en;dd=2*(ax*(by-cy)+bx*(cy-ay)+cx*(ay-by))
 ux=((ax*ax+ay*ay)*(by-cy)+(bx*bx+by*by)*(cy-ay)+(cx*cx+cy*cy)*(ay-by))/dd
 uy=((ax*ax+ay*ay)*(cx-bx)+(bx*bx+by*by)*(ax-cx)+(cx*cx+cy*cy)*(bx-ax))/dd
 aa,am,ae=[math.atan2(y-uy,x-ux) for x,y in [st,mi,en]]
 sweep=(ae-aa)%(2*math.pi)
 if (am-aa)%(2*math.pi)>sweep:sweep-=2*math.pi
 rad=math.hypot(ax-ux,ay-uy);nn=max(2,int(abs(sweep)*rad/.1));points=[(ux+rad*math.cos(aa+sweep*i/nn),uy+rad*math.sin(aa+sweep*i/nn)) for i in range(nn+1)]
 for u,v in zip(points,points[1:]):segs.append({'start':u,'end':v,'width':float(val(a,'width')),'layer':val(a,'layer'),'net':val(a,'net')})
nets={n[1]:n[2] for n in all(b,'net')}
for s in segs:s['net']=nets.get(s['net'],s['net'])
zones=[{'net':val(z,'net'),'layer':one(z,'layer') or one(z,'layers'),'connect':one(z,'connect_pads'),'fill':one(z,'fill'),'polygon':one(z,'polygon'),'filled_count':len(all(z,'filled_polygon'))} for z in all(b,'zone')]
out={'footprints':fps,'pads':pads,'segments':segs,'vias':all(b,'via'),'zones':zones,'edges':[g for k in ['gr_line','gr_arc','gr_rect'] for g in all(b,k) if val(g,'layer')=='Edge.Cuts'],'text':all(b,'gr_text')}
(D/'board.json').write_text(json.dumps(out,indent=2))
for f in fps:print(f['ref'],f['value'],f['fp'],f['xy'],f['rotation'],'; '.join(p['pin']+':'+p['net']+'@'+str([round(v,2) for v in p['xy']]) for p in f['pads']))
print('ZONES',zones); print('EDGES',out['edges']);print('VIAS',len(out['vias']));print('TEXT',out['text'])
r=E.parse(D/'netlist.xml'); expected={(c.get('ref'),c.get('pin')):n.get('name') for n in r.findall('./nets/net') for c in n.findall('node')}
diffs=[(p['ref'],p['pin'],p['net'],expected.get((p['ref'],p['pin']))) for p in pads if p['pin'] and p['net']!=expected.get((p['ref'],p['pin']))]
print('PARITY differences',diffs)
for net in sorted(set(s['net'] for s in segs)):
 ss=[s for s in segs if s['net']==net];print('TRACK',net,'widths',sorted(set(s['width'] for s in ss)),'length',round(sum(math.dist(s['start'],s['end']) for s in ss),2))

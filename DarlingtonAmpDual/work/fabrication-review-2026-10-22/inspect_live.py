from sexpr import *
from collections import Counter
b=parse('DarlingtonAmpDual.kicad_pcb'); s=parse('DarlingtonAmpDual.kicad_sch')
# KiCad 10 uses named net tokens directly in tracks and pads.
nets={n[1]:n[2] for n in all(b,'net') if len(n)>2}
def net(x):
 n=one(x,'net',['net','']);return nets.get(n[1],n[-1])
fps=[];pads=[]
for f in all(b,'footprint'):
 props={p[1]:p[2] for p in all(f,'property')};a=one(f,'at');x,y=map(float,a[1:3]);rot=float(a[3]) if len(a)>3 else 0
 pp=[]
 for p in all(f,'pad'):
  at=one(p,'at');px,py=map(float,at[1:3]);r=math.radians(rot);xy=[x+px*math.cos(r)+py*math.sin(r),y-px*math.sin(r)+py*math.cos(r)]
  z={'ref':props['Reference'],'pin':p[1],'xy':xy,'net':net(p),'size':one(p,'size')[1:],'drill':one(p,'drill'),'type':p[2],'shape':p[3],'angle':float(at[3]) if len(at)>3 else 0,'layers':one(p,'layers')[1:]};pp.append(z);pads.append(z)
 fps.append({'ref':props['Reference'],'value':props.get('Value'),'fp':f[1],'xy':[x,y],'rotation':rot,'pads':pp,'attrs':one(f,'attr'),'models':all(f,'model')})
segs=[]
for kind in ['segment','arc']:
 for t in all(b,kind):
  z={'kind':kind,'start':list(map(float,one(t,'start')[1:])),'end':list(map(float,one(t,'end')[1:])),'width':float(val(t,'width')),'layer':val(t,'layer'),'net':net(t),'uuid':val(t,'uuid')}
  if kind=='arc':z['mid']=list(map(float,one(t,'mid')[1:]))
  segs.append(z)
zones=[{'net':net(z),'layer':one(z,'layer') or one(z,'layers'),'connect':one(z,'connect_pads'),'fill':one(z,'fill'),'polygon':one(z,'polygon'),'filled_count':len(all(z,'filled_polygon'))} for z in all(b,'zone')]
edges=[g for k in ['gr_line','gr_arc','gr_rect'] for g in all(b,k) if val(g,'layer')=='Edge.Cuts']
r=E.parse(D/'netlist.xml');expected={(c.get('ref'),c.get('pin')):n.get('name') for n in r.findall('./nets/net') for c in n.findall('node')}
diffs=[(p['ref'],p['pin'],p['net'],expected.get((p['ref'],p['pin']))) for p in pads if p['pin'] and p['net']!=expected.get((p['ref'],p['pin']))]
missing=[(ref,pin,n) for (ref,pin),n in expected.items() if not any(p['ref']==ref and p['pin']==pin for p in pads)]
comps={c.get('ref'):{'value':c.findtext('value'),'fp':c.findtext('footprint')} for c in r.findall('./components/comp')}
fp_diffs=[(f['ref'],f['value'],comps.get(f['ref'])) for f in fps if f['ref'] in comps and (f['value']!=comps[f['ref']]['value'] or f['fp']!=comps[f['ref']]['fp'])]
out={'footprints':fps,'pads':pads,'segments':segs,'vias':all(b,'via'),'zones':zones,'edges':edges,'text':all(b,'gr_text'),'parity_diffs':diffs,'missing_pads':missing,'component_diffs':fp_diffs}
(D/'board.json').write_text(json.dumps(out,indent=2))
for f in sorted(fps,key=lambda f:(f['ref'][0],int(re.sub(r'\D','',f['ref']) or 0))):
 print(f['ref'],f['value'],f['fp'],[round(v,3) for v in f['xy']],f['rotation'],'; '.join(p['pin']+':'+p['net']+'@'+str([round(v,3) for v in p['xy']]) for p in f['pads']))
print('PARITY',diffs,'MISSING',missing,'COMPONENT DIFFS',fp_diffs)
print('COUNTS',len(fps),len(pads),len(segs),Counter((t['width'],t['layer']) for t in segs),'VIAS',len(out['vias']));print('ZONES',zones);print('EDGES',edges);print('TEXT',out['text'])
pro=json.loads(Path('DarlingtonAmpDual.kicad_pro').read_text());print('RULES',json.dumps(pro.get('board',{}),indent=2));print('NETCLASSES',json.dumps(pro.get('net_settings',{}),indent=2))

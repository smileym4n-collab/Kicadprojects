import sys,json,math,hashlib,xml.etree.ElementTree as E
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'));from schutil import *
D=Path(__file__).resolve().parent
b=parse((D/'source/PCM2706Bench.kicad_pcb').read_text());r=E.parse(D/'netlist.xml').getroot()
def norm(n):return n.replace('{slash}','/').replace('{backslash}','\\')
expected={};schemcomps={};actual={};pads=[];fps={}
for c in r.findall('components/comp'):schemcomps[c.attrib['ref']]=c
for n in r.findall('nets/net'):
 ns=frozenset(x.attrib['ref']+'.'+x.attrib['pin']for x in n)
 for x in ns:expected[x]=ns
for f in children(b,'footprint'):
 ref=prop(f,'Reference');fps[ref]=f;at=child(f,'at');ox,oy=map(float,at[1:3]);deg=float(at[3])if len(at)>3 else 0;ang=math.radians(deg)
 for p in children(f,'pad'):
  if not p[1]:continue
  n=child(p,'net');n=norm(n[-1])if n else '';key=ref+'.'+p[1]
  if key in actual:assert actual[key]==n
  actual[key]=n
  xy=child(p,'at');x,y=map(float,xy[1:3]);gx=ox+math.cos(ang)*x+math.sin(ang)*y;gy=oy-math.sin(ang)*x+math.cos(ang)*y
  pads.append({'key':key,'net':n,'xy':[round(gx,5),round(gy,5)],'layer':child(f,'layer')[1],'pad_type':p[2],'size':child(p,'size')[1:],'drill':child(p,'drill')[1:]if child(p,'drill')else None})
actualgroups=defaultdict(set)
for key,net in actual.items():actualgroups[net].add(key)
errors=[]
for key,net in expected.items():
 if key not in actual:errors.append({'missing_pad':key});continue
 aset=actualgroups[actual[key]]
 if aset!=net:errors.append({'pin':key,'expected':sorted(net),'board':sorted(aset)})
extras=sorted(set(actual)-set(expected));assert not errors,errors
component_mismatches=[]
for ref,c in schemcomps.items():
 f=fps.get(ref)
 if not f:component_mismatches.append([ref,'missing footprint']);continue
 if prop(f,'Value')!=c.findtext('value'):component_mismatches.append([ref,'value',prop(f,'Value'),c.findtext('value')])
 if f[1]!=c.findtext('footprint'):component_mismatches.append([ref,'footprint',f[1],c.findtext('footprint')])
assert not component_mismatches,component_mismatches
segments=[]
for s in children(b,'segment'):
 a=list(map(float,child(s,'start')[1:]));z=list(map(float,child(s,'end')[1:]));segments.append({'net':norm(child(s,'net')[-1]),'start':a,'end':z,'length':math.dist(a,z),'width':float(child(s,'width')[1]),'layer':child(s,'layer')[1]})
netlength=defaultdict(float)
for s in segments:netlength[s['net']]+=s['length']
vp=defaultdict(list)
for v in children(b,'via'):
 vp[tuple(child(v,'at')[1:])].append(v)
dups=[{'xy':k,'count':len(v)}for k,v in vp.items()if len(v)>1]
# Refilling the review copy must not change copper objects, footprints, net assignments, or outline.
orig=parse((ROOT/'PCM2706Bench.kicad_pcb').read_text());
def keyed(s,k):
 return {child(x,'uuid')[1]:x for x in children(s,k)}
preserved={k:keyed(orig,k)==keyed(b,k)for k in ['footprint','segment','arc','via','gr_rect','gr_line','gr_arc','zone']}
source_hashes={}
for line in (D/'source-sha256.txt').read_text().splitlines():
 h,name=line.split();source_hashes[name]=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h
out={'schematic_components':len(schemcomps),'board_footprints':len(fps),'numbered_pad_instances':len(pads),'unique_numbered_pads':len(actual),'schematic_pins':len(expected),'pad_net_parity_checks':len(expected),'net_parity_errors':errors,'extra_numbered_pads':extras,'component_value_footprint_mismatches':component_mismatches,'source_files_unchanged':source_hashes,'refill_geometry_preserved':preserved,'track_widths_mm':dict(Counter(s['width']for s in segments)),'vias':len(children(b,'via')),'duplicate_vias':dups,'drill_sizes_mm':dict(Counter(' '.join(child(v,'drill')[1:])for v in children(b,'via'))),'net_copper_length_mm':dict(sorted(netlength.items())),'pads':pads}
(D/'audit.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items()if k not in ['pads','net_copper_length_mm']},indent=2))
print('PIN LOCATIONS')
for p in pads:
 if p['key'].startswith(('IC1.','Y1.','C3.','C4.','C11.','C12.','C13.','C14.')):print(p['key'],p['xy'],p['net'])
print('USB LENGTHS',[(n,round(l,3))for n,l in netlength.items()if any(v in n for v in ['D+','D-','I/O'])])

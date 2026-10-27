from pathlib import Path
import json,sys,math,xml.etree.ElementTree as E,collections
sys.path.insert(0,'review/scripts');from schlib import *
p=Path('review/layout-review-2026-10-24');board=load('TPA3126.kicad_pcb');netnames={str(x[1]):str(x[2]) for x in many(board,'net')}
# KiCad 10 uses named net properties directly where present.
def net(n):
 x=get(n,'net');return str(x[2]) if x and len(x)>2 else netnames.get(str(x[1]),str(x[1])) if x else ''
root=E.parse(p/'schematic.xml');sn={};parts={}
for n in root.findall('./nets/net'):
 for x in n.findall('node'):sn[x.get('ref'),x.get('pin')]=n.get('name')
for x in root.findall('./components/comp'):parts[x.get('ref')]=x
pn={};fp={};geom={};gndvias=[]
for v in many(board,'via'):
 if net(v)=='GND':gndvias.append(tuple(float(x) for x in get(v,'at')[1:3]))
for f in many(board,'footprint'):
 r=val(f,'Reference');fp[r]=f;at=get(f,'at');a=math.radians(float(at[3]) if len(at)>3 else 0);fx,fy=map(float,at[1:3]);pads=[]
 for pad in many(f,'pad'):
  if not pad[1]:continue
  xy=get(pad,'at');px,py=map(float,xy[1:3]);x=fx+px*math.cos(a)+py*math.sin(a);y=fy-px*math.sin(a)+py*math.cos(a)
  pn[r,str(pad[1])]=net(pad)
  pads.append({'pin':str(pad[1]),'net':net(pad),'xy_mm':[x,y],'size_mm':list(map(float,get(pad,'size')[1:3])),'zone_connect':str(get(pad,'zone_connect'))})
 geom[r]={'xy_mm':[fx,fy],'rotation_deg':math.degrees(a),'pads':pads}
def norm(s):return s.replace('{slash}','/')
mis=[{'ref':r,'pin':pin,'sch':n,'pcb':pn.get((r,pin))} for (r,pin),n in sn.items() if norm(n)!=norm(pn.get((r,pin),''))]
missing=[list(x) for x in sn.keys()-pn.keys()];extra=[list(x) for x in pn.keys()-sn.keys()]
valuefp=[]
for r,c in parts.items():
 f=fp.get(r)
 if f is None:continue
 if c.findtext('value')!=val(f,'Value') or c.findtext('footprint')!=str(f[1]):valuefp.append({'ref':r,'sch_value':c.findtext('value'),'pcb_value':val(f,'Value'),'sch_fp':c.findtext('footprint'),'pcb_fp':str(f[1])})
old=E.parse('review/revisions/preorder-corrections-2026-10-23/after.xml');oldparts={x.get('ref'):x for x in old.findall('./components/comp')};oldn={}
for n in old.findall('./nets/net'):
 for x in n.findall('node'):oldn[x.get('ref'),x.get('pin')]=n.get('name')
diffs=[{'pin':list(k),'old':oldn.get(k),'new':sn.get(k)} for k in oldn.keys()|sn.keys() if oldn.get(k)!=sn.get(k)]
near=[]
for pp in geom['U1']['pads']:
 if pp['pin'] in ['22','25','28']:
  x,y=pp['xy_mm'];vs=sorted((math.hypot(x-vx,y-vy),(vx,vy)) for vx,vy in gndvias);near.append({'pin':pp['pin'],'xy_mm':[x,y],'nearest_GND_vias':[{'distance_mm':d,'xy_mm':xy} for d,xy in vs[:3]]})
report={'schematic_pins':len(sn),'pcb_pads':len(pn),'pad_net_mismatches':mis,'missing':missing,'extra':extra,'value_fp_mismatches':valuefp,'added_components':sorted(parts.keys()-oldparts.keys()),'removed_components':sorted(oldparts.keys()-parts.keys()),'schematic_net_changes':diffs,'U1_ground_vias':near,'GND_via_count':len(gndvias),'via_count':len(many(board,'via'))}
(p/'parity-and-changes.json').write_text(json.dumps(report,indent=2)+'\n');(p/'geometry.json').write_text(json.dumps(geom,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='schematic_net_changes'},indent=2));print('Net changes',len(diffs))

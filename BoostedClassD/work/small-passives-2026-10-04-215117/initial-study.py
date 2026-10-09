import pcbnew as p,pathlib,json,re,shutil
w=pathlib.Path(__file__).resolve().parent
a=p.LoadBoard(str(w/'backup/BoostedClassD.kicad_pcb')); old={f.GetReference():f for f in a.GetFootprints()};g=json.loads((w/'geometry.json').read_text())
refs={f'C{i}' for i in range(13,25)}
unique={'Net-(U2-GREG)','Net-(U3-GREG)','Net-(U2-DREG)','Net-(U3-DREG)','Net-(U2-OUTN)','Net-(U2-OUTP)','/Amplifiers/LEFT-','/Amplifiers/LEFT+'}
# Local power routing is rebuilt; digital signal fanout is retained.
def local(t):
 x,y=t['start'];xx,yy=t['end'];n=t['net'];front=t['layer']==p.F_Cu
 if n in unique:return True
 if n=='/Amplifiers/PVDD':return True
 if front and n in ['/Amplifiers/VDD1V8','/ESP3V3','/Amplifiers/SYS','GND']:
  if 136<x<148 and 83<y<114 and 136<xx<148 and 83<yy<114:return True
 return False
remove={t['uuid'] for t in g['tracks'] if local(t)}
# Delete old front PVDD shapes, keep the inner distribution plane.
rz={z['uuid'] for z in g['zones'] if z['net']=='/Amplifiers/PVDD' and p.F_Cu in z['layers']}
source=(w/'backup/BoostedClassD.kicad_pcb').read_text()
source=re.sub(r'\n\t\((?:segment|arc|via|zone|footprint)\s.*?\n\t\)',lambda m:'' if any(u in m.group() for u in remove|rz|{old[r].m_Uuid.AsString() for r in refs}) else m.group(),source,flags=re.S)
(w/'stripped.kicad_pcb').write_text(source);b=p.LoadBoard(str(w/'stripped.kicad_pcb'));nets={str(n.GetNetname()):n for n in b.GetNetsByNetcode().values()};f={x.GetReference():x for x in b.GetFootprints()}
pt=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y))
newnets={};fpids={}
def tr(n,ps,width=.2,layer=p.F_Cu):
 for x,y in zip(ps,ps[1:]):
  if x==y:continue
  t=p.PCB_TRACK(b);t.SetStart(pt(*x));t.SetEnd(pt(*y));t.SetWidth(p.FromMM(width));t.SetLayer(layer);t.SetNet(nets[n]);b.Add(t);newnets[t.m_Uuid.AsString()]=n
def via(n,x,y):
 v=p.PCB_VIA(b);v.SetPosition(pt(x,y));v.SetWidth(p.FromMM(.5));v.SetDrill(p.FromMM(.3));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(nets[n]);b.Add(v);newnets[v.m_Uuid.AsString()]=n
for r in sorted(refs):
 o=old[r];q=p.FootprintLoad('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Capacitor_SMD.pretty','C_0201_0603Metric');q.SetReference(r);q.SetValue(o.GetValue());q.SetFPID(p.LIB_ID('Capacitor_SMD','C_0201_0603Metric'));q.SetPath(o.GetPath());q.SetSheetname(o.GetSheetname());q.SetSheetfile(o.GetSheetfile());fpids[q.m_Uuid.AsString()]=o.m_Uuid.AsString();q.SetLocalClearance(p.FromMM(.15));q.SetPosition(o.GetPosition());q.SetOrientationDegrees(o.GetOrientationDegrees());b.Add(q)
 ns={d.GetNumber():d.GetNetname() for d in o.Pads() if d.GetNumber()}
 for d in q.Pads():
  if d.GetNumber():d.SetNet(nets[ns[d.GetNumber()]])
 q.Reference().SetTextSize(pt(.7,.7));q.Reference().SetTextThickness(p.FromMM(.12));q.Value().SetVisible(False);f[r]=q

def move(r,x,y,ang):
 f[r].SetPosition(pt(x,y));f[r].SetOrientationDegrees(ang);f[r].Reference().SetPosition(pt(x,y-.7));f[r].Reference().SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T))
def pad(r,num):
 q=next(d for d in f[r].Pads() if d.GetNumber()==str(num));return(p.ToMM(q.GetPosition().x),p.ToMM(q.GetPosition().y))
PV='/Amplifiers/PVDD';SYS='/Amplifiers/SYS';VD='/Amplifiers/VDD1V8';IO='/ESP3V3'
for u,cy,greg,pv,bat,dr,vd,io in [('U2',91.5,'C18','C13','C19','C15','C23','C24'),('U3',106,'C17','C14','C20','C16','C21','C22')]:
 move(greg,138.1,cy-.7,180);move(pv,136.9,cy+.2,180);move(bat,138.1,cy-2.1,180);move(dr,141.7336,cy+2.9,-90);move(vd,140.3,cy+3,-90);move(io,143.6,cy-.2,180)
 # Gate regulator: short top-layer lead and independent inner return to PVDD pin.
 tr(f'Net-({u}-GREG)',[pad(u,17),(138.72,cy-.2),pad(greg,1)])
 for x in [137.6,136.9]:via(PV,x,cy-1.65);tr(PV,[pad(greg,2),(x,cy-1.65)],.25)
 for yy in [cy+.3,cy+1.0]:via(PV,140.15,yy)
 tr(PV,[(137.6,cy-1.65),(139.4,cy-1.65),(140.15,cy-.9),(140.15,cy+.3),(140.15,cy+1)],.4,p.In2_Cu)
 tr(PV,[(136.9,cy-1.65),(137.6,cy-1.65)],.4,p.In2_Cu)
 tr(PV,[pad(u,18),(139.8,cy+.2),(140.15,cy+.3),(140.15,cy+1)],.2)
 # PVDD low-ESL cap is directly on the pin's separate front branch.
 tr(PV,[pad(u,18),pad(pv,1)],.2)
 for x in [137.3,136.5]:via(PV,x,cy+.9);tr(PV,[pad(pv,1),(137.3,cy+.9),(x,cy+.9)],.3)
 # Compact ground return; three vias from local bypass into ground reference.
 for x,y in [(135.9,cy+.2),(135.9,cy-.5),(135.2,cy+.2)]:via('GND',x,y);tr('GND',[pad(pv,2),(x,y)],.25)
 # Battery bypass directly beside VBAT/SNS pins.
 tr(SYS,[pad(u,15),(138.95,cy-1),pad(bat,1)],.2);tr(SYS,[pad(u,14),(138.95,cy-1.6),(138.95,cy-1)],.2)
 for x in [137.5,136.8]:via('GND',x,cy-2.9);tr('GND',[pad(bat,2),(x,cy-2.9)],.25)
 tr(SYS,[pad(bat,1),(138.42,cy-3.2)],.3);via(SYS,138.42,cy-3.2)
 tr(SYS,[(138.42,cy-3.2),(137.8,cy-3.2)],.4,p.In2_Cu)
 # DREG and 1.8-V caps, close to the bottom pins.
 tr(f'Net-({u}-DREG)',[pad(u,26),pad(dr,1)],.2)
 tr(VD,[pad(u,24),(140.9336,cy+2.2),pad(vd,1)],.2)
 for r in [dr,vd]:
  x,y=pad(r,2)
  for dx in [-.35,.35]:via('GND',x+dx,y+.65);tr('GND',[(x,y),(x+dx,y+.65)],.25)
 tr(VD,[pad(vd,1),(138.938,cy+3.5468)],.3);via(VD,138.938,cy+3.5468)
 # IOVDD cap, separate from the clock/address tracks.
 tr(IO,[pad(u,5),pad(io,1)],.2)
 x,y=pad(io,2)
 for yy in [cy-1.05,cy-1.75]:via('GND',x,yy);tr('GND',[(x,y),(x,yy)],.25)
 tr(IO,[pad(io,1),(144.4,cy-.2),(145.9,cy+.3)],.3);via(IO,145.9,cy+.3)
 # Ground pins use local direct returns; don't join via supply-cap ground stubs.
 for num,x,y in [(12,140.5336,cy-2.7),(16,139.9,cy-.9),(21,139.55,cy+2.25),(22,139.8,cy+2.7),(23,140.5336,cy+2.3),(25,141.3336,cy+2.3)]:
  via('GND',x,y);tr('GND',[pad(u,num),(x,y)],.2)
# Complete the retained inner rail branches at their original endpoints.
tr(VD,[(138.938,95.0468),(138.938,109.5468)],.4,p.In2_Cu)
tr(IO,[(145.9,91.8),(145.9,106.3),(145.9,103.55)],.4,p.In2_Cu)
tr(SYS,[(138.42,88.3),(136.9,88)],.4,p.In2_Cu)
tr(SYS,[(138.42,102.8),(135.4,99.9)],.4,p.In2_Cu)
# Bulk PVDD caps retain their size; give each a short connection to the inner rail.
for r in ['C10','C11','C12']:
 x,y=pad(r,1)
 for yy in [y-.4,y+.4]:via(PV,x-.9,yy);tr(PV,[(x,y),(x-.9,yy)],.45)
# Restore bulk/input connections where the previous local front routes were removed.
tr(SYS,[pad('C9',1),(135.4,99.9)],.6)
# Output routes will be refined after DRC. U3 maintains existing bead placement.
tr('/Amplifiers/LEFT-', [pad('U3',19),(138.8,106.6),(137.6,107.8),(133.0,107.8),pad('FB4',1)],.2)
tr('/Amplifiers/LEFT+', [pad('U3',20),(138.8,107.0),(137.5,108.3),(130.5,108.3),pad('FB3',1)],.2)
# U2 keeps its existing bead order initially, with a paired-via negative crossover.
tr('Net-(U2-OUTP)',[pad('U2',20),(138.8,92.5),(137.5,93.8),(131.7844,93.8),pad('FB1',1)],.2)
tr('Net-(U2-OUTN)',[pad('U2',19),(138.8,92.1),(137.8,93.1),(136.0,93.1)],.2)
for x,y in [(136,93.1),(135.3,93.1),(130.9,98.9),(131.6,98.9)]:via('Net-(U2-OUTN)',x,y)
tr('Net-(U2-OUTN)',[(136,93.1),(135.3,93.1)],.4)
tr('Net-(U2-OUTN)',[(136,93.1),(135.3,93.1),(132,96.4),(130.9,98.9),(131.6,98.9)],.5,p.B_Cu)
tr('Net-(U2-OUTN)',[pad('FB2',1),(130.9,98.9),(131.6,98.9)],.5)
# New pad clearance is local to these fine-pitch machine-assembled packages.
for r in refs:f[r].Reference().SetVisible(False)
p.SaveBoard(str(w/'candidate.kicad_pcb'),b)
s=(w/'candidate.kicad_pcb').read_text()
for new,original in fpids.items():s=s.replace(new,original)
(w/'candidate.kicad_pcb').write_text(s)
shutil.copy2(w/'backup/BoostedClassD.kicad_pro',w/'candidate.kicad_pro');(w/'expected-new-nets.json').write_text(json.dumps(newnets,indent=2));print('Written candidate',len(remove),'routes replaced')

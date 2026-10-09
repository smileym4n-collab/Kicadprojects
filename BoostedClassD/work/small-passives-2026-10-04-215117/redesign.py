import pcbnew as p,pathlib,json,re,shutil
w=pathlib.Path(__file__).resolve().parent
a=p.LoadBoard(str(w/'backup/BoostedClassD.kicad_pcb')); old={f.GetReference():f for f in a.GetFootprints()};g=json.loads((w/'geometry.json').read_text())
refs={f'C{i}' for i in range(13,25)}
unique={'Net-(U2-GREG)','Net-(U3-GREG)','Net-(U2-DREG)','Net-(U3-DREG)','Net-(U2-OUTN)','Net-(U2-OUTP)','/Amplifiers/LEFT-','/Amplifiers/LEFT+'}
# Local power routing is rebuilt; digital signal fanout is retained.
def local(t):
 n=t['net'];x,y=t['start'];xx,yy=t['end']
 if n=='/Amplifiers/SYS' and t['layer']==p.F_Cu and any(abs(z[0]-137.7336)<.00001 and abs(z[1]-87.2625)<.00001 for z in [t['start'],t['end']]):return True
 if n=='GND' and any(any(abs(z[0]-q['pos'][0])<.00001 and abs(z[1]-q['pos'][1])<.00001 for z in [t['start'],t['end']]) for r in ['C13','C14','C19'] for q in next(f for f in g['fps'] if f['ref']==r)['pads'] if q['n']=='2'):return True
 return (n=='/Amplifiers/PVDD' or n=='Net-(U2-OUTN)' or t['uuid'] in {'e1a7674a-ac2e-4640-a40c-bf39318341f5','210124ac-7baf-41f0-a4ba-8277defaa59e'}) or n in {'Net-(U2-GREG)','Net-(U3-GREG)','Net-(U2-DREG)','Net-(U3-DREG)'}
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
# Reuse verified route corridors, bringing the regulator and bypass pads inward.
for r in refs:
 o=old[r];op=next(d for d in o.Pads() if d.GetNumber()=='1');x,y=p.ToMM(op.GetPosition().x),p.ToMM(op.GetPosition().y)
 # Position the replacement's live pad at the previously routed live pad first.
 move(r,0,0,o.GetOrientationDegrees());dx,dy=pad(r,1);move(r,x-dx,y-dy,o.GetOrientationDegrees())
move('C19',138.63,88.65,180)
# Local regulated-supply capacitors move up their existing escape routes.
move('C15',141.7336,94.75,-90);move('C16',141.7336,109.25,-90)
# GREG capacitance now sits near the pin; dedicated bottom-layer PVDD return follows.
move('C18',138.1,90.3,180);move('C17',138.1,104.8,180)
# Main high-frequency PVDD capacitors move closer along their existing feed corridor.
move('C13',137.7,91.7,180);move('C14',137.7,106.2,180)
# 1.8-V caps move inward along the existing vertical escape without changing clock fanout.
# Other low-voltage caps retain the proven power-pad anchor, but lose the oversized lands.
# Move only existing trace endpoints which actually terminate at changed pads.
for r in refs:
 for num in ['1','2']:
  op=next(d for d in old[r].Pads() if d.GetNumber()==num);oldpos=op.GetPosition();newpos=pt(*pad(r,num))
  for t in b.GetTracks():
   if t.GetClass()=='PCB_VIA':continue
   if t.GetStart()==oldpos:t.SetStart(newpos)
   if t.GetEnd()==oldpos:t.SetEnd(newpos)
for u,cy,gr,pv,dr in [('U2',91.5,'C18','C13','C15'),('U3',106,'C17','C14','C16')]:
 tr(f'Net-({u}-GREG)',[pad(u,17),(138.6,cy-.2),pad(gr,1)],.2)
 tr(f'Net-({u}-DREG)',[pad(u,26),pad(dr,1)],.2)
 # Separate return from GREG to PVDD, not through reservoir-capacitor copper.
 for x in [136.8,136.1]:via(PV,x,cy-1.0);tr(PV,[pad(gr,2),(x,cy-1)],.25)
 via(PV,140.15,cy+.2)
 tr(PV,[(136.1,cy-1),(136.8,cy-1),(139.4,cy-1),(140.15,cy-.25),(140.15,cy+.2)],.35,p.B_Cu)
 tr(PV,[pad(u,18),(140.15,cy+.2)],.2)
 # Direct PVDD front-layer bypass.
 tr(PV,[pad(u,18),pad(pv,1)],.2)
 for r in [dr]:
  x,y=pad(r,2)
  for dx in [-1.05,-1.75]:
   yy=y+(1.8 if u=='U3' else 1.0);via('GND',x+dx,yy);tr('GND',[(x,y),(x,yy),(x+dx,yy)],.25)
# Main PVDD capacitors receive power through their own inner-plane feed.
for r,cy in [('C13',91.5),('C14',106)]:
 tr(PV,[pad(r,1),(138.02,cy-.5),(136.5,cy-.5)],.25);via(PV,136.5,cy-.5)
 for x in [136.5,135.8,135.1]:via('GND',x,cy+.2);tr('GND',[pad(r,2),(x,cy+.2)],.25)
# Preserve the separate GREG return through the plane by excluding only pour copper around its vias.
for cy in [91.5,106]:
 z=p.ZONE(b);z.SetIsRuleArea(True);z.SetLayer(p.In2_Cu);z.SetDoNotAllowZoneFills(True);z.SetDoNotAllowTracks(False);z.SetDoNotAllowVias(False);z.SetDoNotAllowPads(False);z.SetDoNotAllowFootprints(False);o=z.Outline();o.NewOutline()
 for x,y in [(135.6,cy-1.5),(137.3,cy-1.5),(137.3,cy-.55),(135.6,cy-.55)]:o.Append(p.FromMM(x),p.FromMM(y))
 b.Add(z)
for r in ['C10','C11','C12']:
 x,y=pad(r,1)
 for yy in [y-.4,y+.4]:via(PV,x-.9,yy);tr(PV,[(x,y),(x-.9,yy)],.45)
# Extend inner PVDD distribution just enough to include both primary reservoir capacitors.
for z in b.Zones():
 if z.GetNetname()==PV and not z.GetIsRuleArea():
  o=z.Outline();o.RemoveAllContours();o.NewOutline()
  for x,y in [(132.5,88.1),(137.4,88.1),(137.4,113.0),(132.5,113.0)]:o.Append(p.FromMM(x),p.FromMM(y))
# The negative output crosses layers outside the IC, freeing its internal fanout.
tr('Net-(U2-OUTN)',[pad('U2',19),(138.4,92.1),(137.5,93),(136,93),(135.3,93)],.2)
for x,y in [(136,93),(135.3,93),(130.9,98.9),(131.7,98.9)]:via('Net-(U2-OUTN)',x,y)
tr('Net-(U2-OUTN)',[(135.3,93),(136,93),(137.7,94.7),(137.7,96.5),(136.7,97.5),(132.3,97.5),(130.9,98.9),(131.7,98.9)],.5,p.B_Cu)
tr('Net-(U2-OUTN)',[pad('FB2',1),(130.9,98.9),(131.7,98.9)],.5)
tr(SYS,[(139.284,105.639329),(139.3,106.5),(145.034,112.234),(145.034,111.389329)],.3,p.In2_Cu)
tr(IO,[pad('C22',1),(144.9617,104.0),(145.9,103.8621)],.3)
tr(IO,[pad('C22',1),(144.7585,105.5116)],.2)
# Ground and IOVDD feed details at the now-smaller caps.
x,y=pad('C19',2)
for xx in [136.0,135.3]:via('GND',xx,y);tr('GND',[(x,y),(xx,y)],.25)
tr(SYS,[(136.9,88),(138.95,88),pad('C19',1),(138.95,88.4789)],.3)
for r in refs:f[r].Reference().SetVisible(False)
for r in ['U2','U3']:f[r].Value().SetVisible(False)
p.SaveBoard(str(w/'candidate.kicad_pcb'),b)
s=(w/'candidate.kicad_pcb').read_text()
for new,original in fpids.items():s=s.replace(new,original)
(w/'candidate.kicad_pcb').write_text(s)
shutil.copy2(w/'backup/BoostedClassD.kicad_pro',w/'candidate.kicad_pro');(w/'expected-new-nets.json').write_text(json.dumps(newnets,indent=2));print('Written candidate',len(remove),'routes replaced')

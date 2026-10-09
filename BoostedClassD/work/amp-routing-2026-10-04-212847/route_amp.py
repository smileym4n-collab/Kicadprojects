import pcbnew as p,pathlib,json,shutil
w=pathlib.Path(pathlib.Path('/private/tmp/amp-routing-path').read_text());source=(w/'backup/BoostedClassD.kicad_pcb').read_text()
# Remove only top-level route expressions for the one net to be repaired.
data=json.loads((w/'baseline-board.json').read_text());remove={t['uuid'] for t in data['tracks'] if t['net'] in ['/Amplifiers/LEFT-','/Amplifiers/LEFT+']}
remove.add('812ac655-3fd4-4c91-896a-c6e155838aba')
import re
source=re.sub(r'\n\t\((?:segment|arc|via)\n.*?\n\t\)',lambda m:'' if any(u in m.group() for u in remove) else m.group(),source,flags=re.S)
(w/'source-local-repair.kicad_pcb').write_text(source)
b=p.LoadBoard(str(w/'source-local-repair.kicad_pcb'))
pt=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y))
f={f.GetReference():f for f in b.GetFootprints()};nets={str(n.GetNetname()):n for n in b.GetNetsByNetcode().values()}
added=[]; expected_nets={}
def tr(net,points,width=.2,layer=p.F_Cu):
 for a,c in zip(points,points[1:]):
  if a==c:continue
  t=p.PCB_TRACK(b);t.SetStart(pt(*a));t.SetEnd(pt(*c));t.SetWidth(p.FromMM(width));t.SetLayer(layer);t.SetNet(nets[net]);b.Add(t);added.append(t.m_Uuid.AsString());expected_nets[t.m_Uuid.AsString()]=net
def via(net,x,y):
 v=p.PCB_VIA(b);v.SetPosition(pt(x,y));v.SetWidth(p.FromMM(.6));v.SetDrill(p.FromMM(.3));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(nets[net]);b.Add(v);added.append(v.m_Uuid.AsString());expected_nets[v.m_Uuid.AsString()]=net
def zone(net,points,layers,priority=8):
 z=p.ZONE(b);z.SetNet(nets[net]);ls=p.LSET()
 for l in layers:ls.AddLayer(l)
 z.SetLayerSet(ls);z.SetAssignedPriority(priority);z.SetLocalClearance(p.FromMM(.2));z.SetPadConnection(p.ZONE_CONNECTION_FULL);z.SetMinThickness(p.FromMM(.2));o=z.Outline();o.NewOutline()
 for q in points:o.Append(*[p.FromMM(a) for a in q])
 b.Add(z)
def mov(ref,x,y,angle):
 f[ref].SetPosition(pt(x,y));f[ref].SetOrientationDegrees(angle)
# Three parked capacitors go alongside the secondary amplifier.
for ref,y in [('C18',89.437),('C13',91.799),('C12',95.9)]:mov(ref,135.1788,y,180)
# Remove only the local OUTN arc run, and replace it with a clearance-safe escape.

tr('/Amplifiers/LEFT-',[(139.283601,106.599999),(138.5,106.599999),(137.6,107.5),(132.7108,107.5),(130.2652,105.0544)],.2)
tr('/Amplifiers/LEFT+',[(139.283601,107.000001),(138.7,107.000001),(137.65,108.05),(130.6916,108.05),(130.2328,108.5088)],.2)
# Secondary output: top-layer positive; negative uses two vias at either end.
tr('Net-(U2-OUTP)',[(139.283601,92.500001),(138.65,92.500001),(137.35,93.8)],.2)
tr('Net-(U2-OUTP)',[(137.35,93.8),(131.7844,93.8),(130.2328,95.3516)],.6)
tr('Net-(U2-OUTN)',[(139.283601,92.099999),(139.85,92.099999),(140.1,92.0)],.2)
tr('Net-(U2-OUTN)',[(140.1,92.0),(140.75,92.0)],.4)
for x,y in [(140.1,92),(140.75,92),(130.9,98.9),(131.7,98.9)]:via('Net-(U2-OUTN)',x,y)
tr('Net-(U2-OUTN)',[(140.1,92),(138.2,92),(137.7,92.5),(137.7,96.5),(136.7,97.5),(132.3,97.5),(130.9,98.9),(131.7,98.9)],.5,p.B_Cu)
tr('Net-(U2-OUTN)',[(130.2328,98.6536),(130.6536,98.6536),(130.9,98.9),(131.7,98.9)],.6)
# Local secondary gate-regulator capacitor and PVDD bypass.
tr('Net-(U2-GREG)',[(139.283601,91.3),(138.2,91.3),(138.2,90.8957),(136.7413,89.437),(136.7413,89.437)],.2)
tr('/Amplifiers/PVDD',[(139.283601,91.7),(137.9,91.7)],.2)
tr('/Amplifiers/PVDD',[(137.9,91.7),(136.8403,91.7),(136.7413,91.799)],.4)
# Local secondary PVDD shape plus inner-layer link to the primary boost reservoir.
zone('/Amplifiers/PVDD',[(132.5,88.1),(134.2,88.1),(134.2,90.4),(137.4,90.4),(137.4,97.5),(135.9,97.5),(135.9,90.9),(132.5,90.9)],[p.F_Cu])
zone('/Amplifiers/PVDD',[(132.5,88.1),(137.4,88.1),(137.4,111.9),(132.5,111.9)],[p.In2_Cu])
for x,y in [(133.0,88.4),(133.8,88.4),(135.65,91.3),(135.65,92.1),(135.65,95.5),(135.65,96.3)]:
 via('/Amplifiers/PVDD',x,y)
 anchor=(133.6163,89.437) if y<90 else ((136.7413,91.799) if y<94 else (136.7413,95.9))
 tr('/Amplifiers/PVDD',[anchor,(x,y)],.4)
# Restore secondary battery supply from its nearby bypass and the primary input node.
tr('/Amplifiers/SYS',[(139.283601,90.499999),(138.95,90.499999),(138.95,88.4789),(137.7336,87.2625)],.2)
tr('/Amplifiers/SYS',[(139.583603,89.900001),(138.95,89.900001)],.3)
for x,y in [(136.9,87.2),(136.9,88.0),(135.4,99.9),(134.6,99.9)]:via('/Amplifiers/SYS',x,y)
tr('/Amplifiers/SYS',[(136.9,88),(136.9,87.2),(137.7336,87.2625)],.6)
tr('/Amplifiers/SYS',[(135.4205,101.3),(135.4205,100.2),(135.4,99.9),(134.6,99.9)],.6)
tr('/Amplifiers/SYS',[(136.9,87.2),(136.9,88),(137.8,88.9),(137.8,99.0),(136.9,99.9),(135.4,99.9),(134.6,99.9)],.8,p.In2_Cu)
tr('Net-(U2-OUTN)',[(140.1,92),(140.75,92)],.4,p.B_Cu)
# Strong local return connections into the existing continuous ground plane.
for ref in ['C13','C12','C14']:
 a=next(a for a in f[ref].Pads() if a.GetNumber()=='2');x=p.ToMM(a.GetPosition().x);y=p.ToMM(a.GetPosition().y)
 for dy in [-.45,.45]:
  vx,vy=(x-1.15,y+dy) if ref!='C14' else (132.3,105.35+dy)
  via('GND',vx,vy);tr('GND',[(x,y),(vx,vy)],.3)
# Ground returns outside the signal fanout and bypass pads.
for x,y in [(140.5336,88.8),(139.7,88.8),(139,93.1),(139,93.9),(139.5,108.3),(140.3,108.7)]:via('GND',x,y)
tr('GND',[(140.5336,89.7),(140.5336,88.8),(139.7,88.8)],.2)
tr('GND',[(139.583603,93.100001),(139,93.1),(139,93.9)],.2)
tr('GND',[(139.583603,107.600001),(139.5,108.3),(140.3,108.7)],.2)
f['C20'].Value().SetPosition(pt(134,98.1));f['C20'].Value().SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T));f['C20'].Value().SetTextSize(pt(.8,.8))
# Complete the local amplifier IOVDD feed using the inner power layer.
for x,y in [(145.9,91.8),(145.9,103.55)]:via('/ESP3V3',x,y)
tr('/ESP3V3',[(144.8601,90.5764),(144.8601,90.7601),(145.9,91.8)],.3)
tr('/ESP3V3',[(144.9617,104.8004),(145.9,103.8621),(145.9,103.55)],.3)
tr('/ESP3V3',[(145.9,91.8),(145.9,103.55),(147.05,102.4),(158.5,102.4),(161.0,104.9),(162.1028,105.9688)],.4,p.In2_Cu)
# Local ground returns for the battery bypass capacitors.
for ref,points in [('C19',[(136.6,84.0),(136.6,84.8)]),('C20',[(135.8,98.6),(136.6,98.6)])]:
 a=next(a for a in f[ref].Pads() if a.GetNumber()=='2');anchor=(p.ToMM(a.GetPosition().x),p.ToMM(a.GetPosition().y))
 for v in points:via('GND',*v);tr('GND',[anchor,v],.4)
# Refill on a candidate only; preserve the existing project settings.
out=w/'routing-candidate.kicad_pcb';p.SaveBoard(str(out),b);shutil.copy2(w/'backup/BoostedClassD.kicad_pro',w/'routing-candidate.kicad_pro')
(w/'added-items.json').write_text(json.dumps(added,indent=2));(w/'expected-new-nets.json').write_text(json.dumps(expected_nets,indent=2))
print('Saved',out,'added tracks/vias',len(added))

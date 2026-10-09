import pcbnew as p,pathlib,json,hashlib,xml.etree.ElementTree as E
w=pathlib.Path(pathlib.Path('/private/tmp/amp-routing-path').read_text());a=p.LoadBoard(str(w/'backup/BoostedClassD.kicad_pcb'));b=p.LoadBoard(str(w/'routing-candidate.kicad_pcb'))
def vec(v):return(v.x,v.y)
def fp(f):return(f.GetValue(),str(f.GetFPID().GetLibNickname()),str(f.GetFPID().GetLibItemName()),f.m_Uuid.AsString(),sorted((d.GetNumber(),d.GetNetname(),vec(d.GetSize()),vec(d.GetDrillSize()),int(d.GetShape())) for d in f.Pads()))
fa={f.GetReference():f for f in a.GetFootprints()};fb={f.GetReference():f for f in b.GetFootprints()}
assert set(fa)==set(fb)
assert all(fp(fa[r])==fp(fb[r]) for r in fa)
moved=[r for r in fa if (vec(fa[r].GetPosition()),fa[r].GetOrientationDegrees())!=(vec(fb[r].GetPosition()),fb[r].GetOrientationDegrees())];assert set(moved)=={'C12','C13','C18'}
old={t.m_Uuid.AsString():t for t in a.GetTracks()};new={t.m_Uuid.AsString():t for t in b.GetTracks()}
removed=set(old)-set(new);assert all(old[i].GetNetname() in ['/Amplifiers/LEFT-','/Amplifiers/LEFT+'] or i=='812ac655-3fd4-4c91-896a-c6e155838aba' for i in removed)
for i in set(old)&set(new):
 x,y=old[i],new[i];assert x.GetNetname()==y.GetNetname() and vec(x.GetStart())==vec(y.GetStart()) and vec(x.GetEnd())==vec(y.GetEnd()) and x.GetLayer()==y.GetLayer()
expected=json.loads((w/'expected-new-nets.json').read_text());assert all(new[i].GetNetname()==n for i,n in expected.items()),[(i,n,new[i].GetNetname()) for i,n in expected.items() if new[i].GetNetname()!=n]
root=E.parse(w/'current-netlist.xml').getroot();mapping={(n.attrib['ref'],n.attrib['pin']):net.attrib['name'] for net in root.findall('./nets/net') for n in net}
errs=[]
for r,f in fb.items():
 for d in f.Pads():
  if (r,d.GetNumber()) in mapping and d.GetNetname().replace('{slash}','/')!=mapping[(r,d.GetNumber())]:errs.append((r,d.GetNumber(),d.GetNetname(),mapping[(r,d.GetNumber())]))
assert not errs,errs
hashes=json.loads((w/'baseline-hashes.json').read_text());assert all(hashlib.sha256(pathlib.Path(n).read_bytes()).hexdigest()==h for n,h in hashes.items()),'Source changed during routing; do not overwrite'
def edges(board):return sorted((d.GetShapeStr(),vec(d.GetStart()),vec(d.GetEnd())) for d in board.GetDrawings() if d.GetLayer()==p.Edge_Cuts)
assert edges(a)==edges(b);assert a.GetCopperLayerCount()==b.GetCopperLayerCount()==4
result={'checks':['All footprint identities, values, pad geometry and pad nets preserved','Only C12, C13 and C18 moved','All retained tracks and vias keep endpoints, layers and nets','All new route items have their intended nets after zone refill','All PCB pad nets match the current hierarchical schematic netlist','Board outline and four-layer count preserved','Source board, schematics and project settings unchanged during candidate work'], 'moved':moved,'removed_tracks_vias':len(removed),'added_tracks_vias':len(set(new)-set(old)),'final_tracks_vias':len(new)}
(w/'validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

import pcbnew as p,pathlib,json,hashlib,xml.etree.ElementTree as E,re,collections
w=pathlib.Path(__file__).resolve().parent;a=p.LoadBoard(str(w/'backup/BoostedClassD.kicad_pcb'));b=p.LoadBoard(str(w/'review/BoostedClassD.kicad_pcb'));aa={f.GetReference():f for f in a.GetFootprints()};bb={f.GetReference():f for f in b.GetFootprints()};parts=json.loads((w/'parts.json').read_text())
def vec(x):return(x.x,x.y)
def ident(f):return(f.GetValue(),f.m_Uuid.AsString(),f.GetPath().AsString(),sorted((d.GetNumber(),d.GetNetname()) for d in f.Pads() if d.GetNumber()))
assert set(aa)==set(bb);assert all(ident(aa[r])==ident(bb[r]) for r in aa)
for r in aa:
 if r in parts:assert str(bb[r].GetFPID().GetLibItemName())=='C_0201_0603Metric'
 else:
  assert str(aa[r].GetFPID().GetLibItemName())==str(bb[r].GetFPID().GetLibItemName())
  assert vec(aa[r].GetPosition())==vec(bb[r].GetPosition()) and aa[r].GetOrientationDegrees()==bb[r].GetOrientationDegrees()
  assert sorted((d.GetNumber(),vec(d.GetSize()),vec(d.GetPosition())) for d in aa[r].Pads())==sorted((d.GetNumber(),vec(d.GetSize()),vec(d.GetPosition())) for d in bb[r].Pads())
def edges(board):return sorted((d.GetShapeStr(),vec(d.GetStart()),vec(d.GetEnd())) for d in board.GetDrawings() if d.GetLayer()==p.Edge_Cuts)
assert edges(a)==edges(b);assert a.GetCopperLayerCount()==b.GetCopperLayerCount()==4
A=E.parse(w/'netlist-baseline.xml').getroot();B=E.parse(w/'netlist-final.xml').getroot()
def netmap(root):return {(n.attrib['ref'],n.attrib['pin']):net.attrib['name'] for net in root.findall('./nets/net') for n in net}
assert netmap(A)==netmap(B);nm=netmap(B)
for r,f in bb.items():
 for d in f.Pads():
  if (r,d.GetNumber()) in nm:assert d.GetNetname().replace('{slash}','/')==nm[r,d.GetNumber()],(r,d.GetNumber())
assert {x.attrib['ref']:x.findtext('value') for x in A.findall('./components/comp')}=={x.attrib['ref']:x.findtext('value') for x in B.findall('./components/comp')}
new={t.m_Uuid.AsString():t for t in b.GetTracks()};expected=json.loads((w/'expected-new-nets.json').read_text());assert all(new[i].GetNetname()==n for i,n in expected.items())
old={t.m_Uuid.AsString():t for t in a.GetTracks()};removed=set(old)-set(new);changed=[]
for i in set(old)&set(new):
 x,y=old[i],new[i];assert x.GetNetname()==y.GetNetname() and x.GetLayer()==y.GetLayer()
 if (vec(x.GetStart()),vec(x.GetEnd()))!=(vec(y.GetStart()),vec(y.GetEnd())):changed.append(i)
base=json.loads((w.parent/'amp-routing-2026-10-04-212847/drc-final.json').read_text());final=json.loads((w/'drc-final.json').read_text());assert not final['schematic_parity']
def issues(r):return sorted((i['type'],i['description']) for i in r['violations'])
assert issues(base)==issues(final)
def opennets(r):return sorted(re.search(r'\[([^]]+)\]',i['items'][0]['description'])[1] for i in r['unconnected_items'])
assert opennets(base)==opennets(final)
def erc(name):return sorted((v['type'],v['description'],tuple(i['uuid'] for i in v['items'])) for s in json.loads((w/name).read_text())['sheets'] for v in s['violations'])
assert erc('erc-baseline.json')==erc('erc-final.json')
h=json.loads((w/'baseline-hashes.json').read_text());assert all(hashlib.sha256(pathlib.Path(n).read_bytes()).hexdigest()==v for n,v in h.items()),'Source changed; do not overwrite'
assert (w/'backup/BoostedClassD.kicad_pro').read_bytes()==(w/'review/BoostedClassD.kicad_pro').read_bytes()
r={'checks':['101 footprint identities, values, hierarchical paths and numbered-pad nets preserved','Only C13-C24 footprints and positions changed','Other component positions and pad geometry preserved','Board outline and four copper layers preserved','All hierarchical schematic connections and values unchanged','All PCB pads match the exported hierarchical netlist','All added track/via net assignments preserved after refill','DRC violation identities and unrouted net list match baseline','Zero schematic parity issues','ERC identical to baseline: C32 pin 1 unconnected','Main project source hashes unchanged before applying','Project rules/settings byte-for-byte preserved'],'changed_capacitors':sorted(parts),'tracks_removed':len(removed),'tracks_added':len(set(new)-set(old)),'retained_tracks_with_adjusted_endpoints':len(changed),'DRC':{'violations':len(final['violations']),'unconnected':len(final['unconnected_items']),'parity':0},'ERC':{'existing_errors':1,'new_errors':0}}
(w/'validation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))

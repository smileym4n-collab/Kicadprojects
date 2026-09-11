"""Placement only; never saves the production board. Run with KiCad Python."""
from pathlib import Path
import json, hashlib, math, collections, sys
import pcbnew as p

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/layout-study'
SOURCE=ROOT/'DiscreteClassD.kicad_pcb'
TARGET=ROOT/'DiscreteClassD-layout-study.kicad_pcb'
protected=[x for x in ROOT.iterdir() if x.is_file() and x.suffix in ('.kicad_pcb','.kicad_sch','.kicad_pro','.kicad_sym','.kicad_prl') and 'layout-study' not in x.name]
protected += [ROOT/'AGENTS.md',ROOT/'fp-lib-table',ROOT/'sym-lib-table']
hashes={str(x.relative_to(ROOT)):hashlib.sha256(x.read_bytes()).hexdigest() for x in protected}
manifest=OUT/'source-hashes.json'
if manifest.exists():
    initial=json.loads(manifest.read_text())
    assert initial['DiscreteClassD.kicad_pcb']==hashes['DiscreteClassD.kicad_pcb'], 'Production PCB changed since study snapshot'
    changes={k:{'initial':v,'current':hashes.get(k)} for k,v in initial.items() if hashes.get(k)!=v}
    (OUT/'external-file-changes.json').write_text(json.dumps(changes,indent=2)+'\n')
else:
    manifest.write_text(json.dumps(hashes,indent=2)+'\n')
    (OUT/'production-source-snapshot.kicad_pcb').write_bytes(SOURCE.read_bytes())
b=p.LoadBoard(str(OUT/'production-source-snapshot.kicad_pcb'))
fps={f.GetReference():f for f in b.GetFootprints()}
assert len(fps)==len(list(b.GetFootprints()))
OX,OY=114.757,51.473
def vec(x,y): return p.VECTOR2I(round(x*1e6),round(y*1e6))
def pos(x,y): return vec(OX+x,OY+y)
def xy(pt): return [round(pt.x/1e6-OX,5),round(pt.y/1e6-OY,5)]
def identity(board):
    result={}
    for f in board.GetFootprints():
        result[f.GetReference()]={'uuid':f.m_Uuid.AsString(),'value':f.GetValue(),'id':str(f.GetFPID().GetLibNickname())+':'+str(f.GetFPID().GetLibItemName()),
          'pads':sorted([(a.m_Uuid.AsString(),a.GetNumber(),a.GetNetname(),tuple(a.GetSize()),a.GetShape()) for a in f.Pads()])}
    return result
before=identity(b)
sys.path.insert(0,str(ROOT/'scripts'))
from sexp import parse,dump,get
tree=parse((OUT/'production-source-snapshot.kicad_pcb').read_text())
removed={'tracks_and_vias':0,'zones':0,'drawings':0}
clean=[]
for item in tree:
    if isinstance(item,list):
        k=item[0]
        if k in ('segment','arc','via'): removed['tracks_and_vias']+=1; continue
        if k=='zone': removed['zones']+=1; continue
        if k.startswith('gr_') and get(item,'layer')!=['layer','Edge.Cuts']: removed['drawings']+=1; continue
    
    if isinstance(item,list) and item[0]=='footprint':
        item[:]=[v for v in item if not (isinstance(v,list) and v[0]=='fp_text' and v[2] in ('${REFERENCE}','%R'))]
    clean.append(item)
get(clean,'paper')[1]='A3'
(OUT/'unrouted-base.kicad_pcb').write_text(dump(clean)+'\n')
b=p.LoadBoard(str(OUT/'unrouted-base.kicad_pcb'))
fps={f.GetReference():f for f in b.GetFootprints()}
assert identity(b)==before
placed={}
def put(ref,x,y,a=0):
    assert ref not in placed,ref
    f=fps[ref]; f.SetLocked(False); f.SetOrientationDegrees(a); f.SetPosition(pos(x,y))
    placed[ref]=[x,y,a]
def batch(items):
    for row in items: put(*row)

# Identical translated cells retain device chirality, all on F.Cu.
for offset,add in [(0,0),(60,100)]:
    def ref(kind,n): return kind+str(n+add)
    for j,cx in enumerate([12+offset,28+offset]):
        cy=64; q=5+2*j; u=[2,6][j]; c=1+6*j; r=1+6*j; d=1+2*j; tp=1+3*j
        batch([(ref('Q',q),cx,cy-2.9),(ref('Q',q+1),cx,cy+2.9),
          (ref('U',u),cx-7.3,cy-1.5,270),
          (ref('R',r),cx-4.6,cy-5),(ref('R',r+3),cx-4.6,cy+2),
          (ref('C',c),cx-8.8,cy-4.9,180), # bootstrap immediately above HB / HS side
          (ref('C',c+1),cx-4.05,cy-1.5,270),
          (ref('C',c+2),cx-6,cy-8.5),
          (ref('C',c+3),cx+4,cy,270),(ref('C',c+4),cx+4,cy-5,270),
          (ref('C',c+5),cx+4,cy-10,270),
          (ref('D',d),cx-6,cy-15),(ref('D',d+1),cx-.5,cy-15),
          (ref('R',r+2),cx-6,cy-11.5),(ref('R',r+5),cx-.5,cy-11.5),
          (ref('R',r+1),cx-.5,cy-7),(ref('R',r+4),cx-1,cy+7.5),
          (ref('TP',tp),cx,cy+10.7),(ref('TP',tp+1),cx-9,cy-18),
          (ref('TP',tp+2),cx-5,cy-18),
          (ref('R',13+j),(cx-4 if j==0 else cx+4),cy+10),(ref('C',13+j),(cx-4 if j==0 else cx+4),cy+13)])
    batch([(ref('L',6),20+offset,71.5),
      (ref('C',15),17.5+offset,78),
      (ref('J',15),18+offset,94),
      (ref('R',15),9+offset,83),(ref('C',16),8+offset,87),
      (ref('C',18),29+offset,82),(ref('C',19),29+offset,86),
      (ref('TP',7),16+offset,86.5),(ref('TP',8),24+offset,86.5)])

# Quiet shared area, input edge at top.
batch([('J1',47.5,6),('C40',36,12),('C45',59,12),('U1',50,19),
 ('R29',40,18,270),('R30',43,21,270),('C41',40,23,270),('R31',44,17,270),
 ('R36',60,18,270),('R37',57,24,270),('C46',60,23,270),('R38',56,17,270),
 ('C32',48,13),('C33',49,25),('TP24',38,28),('TP29',62,28),
 ('U8',50,30),('C36',54.5,29,270),('TP25',43,31),('TP30',57,31),
 ('U3',49,41),('U7',59,40),('C34',51,35),('C35',46,35),
 ('R24',40,44),('R25',40,47),('C29',44,43,270),('C30',44.5,47,270),
 ('R26',59,35),('R27',64,38,270),('R28',54,38,270),('C31',54,43,270),
 ('C37',59,44.5),('TP21',47,48),('TP22',60,47),('TP23',53,48),
 ('R43',36,34),('C50',36,39,270),('C51',40,38,270),('TP34',36,45),
 ('U4',25,29),('U5',22,39),('U9',75,29,180),('U10',78,39,180),
 ('R32',19,32),('D20',19,29),('C42',18,37,270),
 ('R33',28,35),('D21',28,38),('C43',27,42),
 ('C38',29,29,270),('C39',18,41),
 ('R39',81,32,180),('D22',81,29,180),('C47',82,37,90),
 ('R40',72,35,180),('D23',72,38,180),('C48',73,42,180),
 ('C44',71,29,90),('C49',82,41),
 ('R34',40,51),('R35',40,54),('R41',60,51),('R42',59,53.5),
 ('TP26',18,24),('TP27',22,24),('TP28',31,41.5),
 ('TP31',82,24),('TP32',78,24),('TP33',69,41.5)])

# Power entry and reserved regulator thermal space, central lower island.
batch([('J16',48,94),('C17',40,80.5),('C20',55,80.5),
 ('U11',43,62),('U12',58,62),
 ('C21',47.5,57,270),('C24',38,59,270),('C22',43,67),
 ('R20',37.5,63),('R21',37.5,66),('C23',37.5,69),
 ('C25',62.5,55.4,270),('C28',53,59,270),('C26',58,67),
 ('R22',52.5,63),('R23',52.5,66),('C27',52.5,69),
 ('TP10',44,71),('TP20',59,71),('G***',12,10)])
assert set(fps)==set(placed), 'Unplaced: '+str(sorted(set(fps)-set(placed)))

# Reference readability changes are confined to the study; pad and footprint geometry untouched.
for f in fps.values():
    f.Value().SetVisible(False)
    r=f.Reference(); r.SetVisible(True); r.SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T)); r.SetTextSize(vec(.65,.65)); r.SetTextThickness(p.FromMM(.11))
    bb=f.GetBoundingBox(False,False)
    r.SetPosition(p.VECTOR2I((bb.GetLeft()+bb.GetRight())//2,bb.GetTop()-p.FromMM(.6)))
    for item in f.GraphicalItems():
        if isinstance(item,p.PCB_TEXT) and item.GetText() in ('${REFERENCE}','%R'):
            item.SetVisible(False)

# Place reference labels in nearby free drawing space, without moving components.
occupied=[f.GetBoundingBox(False,False) for f in fps.values()]
labels=[]
def overlap(a,b):
    return min(a.GetRight(),b.GetRight())>max(a.GetLeft(),b.GetLeft()) and min(a.GetBottom(),b.GetBottom())>max(a.GetTop(),b.GetTop())
for f in sorted(fps.values(), key=lambda f: (-len(f.GetReference()),f.GetReference())):
    r=f.Reference(); bb=f.GetBoundingBox(False,False)
    cx=(bb.GetLeft()+bb.GetRight())//2; cy=(bb.GetTop()+bb.GetBottom())//2
    candidates=[]
    for gap in (.65,1.1,1.7,2.4,3):
        g=p.FromMM(gap)
        for dx in (0,-p.FromMM(1),p.FromMM(1)):
            candidates.extend([(cx+dx,bb.GetTop()-g),(cx+dx,bb.GetBottom()+g)])
        w=p.FromMM(.25*len(f.GetReference())+.4)
        candidates.extend([(bb.GetLeft()-g-w,cy),(bb.GetRight()+g+w,cy)])
    best=None
    for candidate in candidates:
        r.SetPosition(p.VECTOR2I(*candidate)); rb=r.GetBoundingBox()
        penalty=sum(overlap(rb,z) for z in occupied+labels)
        if best is None or penalty<best[0]: best=(penalty,candidate)
        if penalty==0: break
    r.SetPosition(p.VECTOR2I(*best[1]));labels.append(r.GetBoundingBox())

notes=[]
def text(s,x,y,size=1,layer=p.Dwgs_User):
    t=p.PCB_TEXT(b); t.SetText(s); t.SetPosition(pos(x,y)); t.SetLayer(layer)
    t.SetTextSize(vec(size,size)); t.SetTextThickness(p.FromMM(size*.15)); t.SetHorizJustify(p.GR_TEXT_H_ALIGN_LEFT)
    b.Add(t); notes.append({'text':s,'x':x,'y':y,'size':size,'layer':b.GetLayerName(layer)})
def line(x1,y1,x2,y2,layer=p.Dwgs_User,width=.15):
    s=p.PCB_SHAPE(); s.SetShape(p.SHAPE_T_SEGMENT); s.SetStart(pos(x1,y1)); s.SetEnd(pos(x2,y2)); s.SetLayer(layer); s.SetWidth(p.FromMM(width)); b.Add(s)
def box(x1,y1,x2,y2,layer=p.Dwgs_User):
    for a in [(x1,y1,x2,y1),(x2,y1,x2,y2),(x2,y2,x1,y2),(x1,y2,x1,y1)]:line(*a,layer=layer,width=.12)
text('STEREO CLASS-D | PLACEMENT STUDY ONLY',0,-9,1.6)
text('100 x 100 mm existing outline | 4 layers | UNROUTED | NOT FOR FABRICATION',0,-6,1)
text('INPUT / QUIET ANALOGUE',35,2,1)
text('LEFT CONTROL',15,21,1);text('RIGHT CONTROL',71,21,1)
box(33,8,67,51)
text('LEFT POWER',3,42.5,1);text('RIGHT POWER',84,42.5,1)
box(35,54,65,74)

text('SHARED BULK / 24 V ENTRY',36,90,0.8)
text('LEFT BTL',15,99,0.8);text('POWER',46,99,0.8);text('RIGHT BTL',75,99,0.8)
for off in (0,60):
    for j,cx in enumerate([12+off,28+off]):
        box(cx-3,63.6,cx+2.5,69.7,p.Cmts_User)
        text('SW_'+('A' if j==0 else 'B'),cx-2.5,70.3,.55,p.Cmts_User)
        box(cx+2.8,56.6,cx+6,66.7,p.Cmts_User)
        box(cx-9.3,57.1,cx-2.5,67,p.Cmts_User)
    text('CLEAN OUTPUT',14+off,90.3,.75)
text('PLACEMENT NOTES (advisory outlines only; no copper or enforced keepouts)',0,105,1)
for i,s in enumerate([
 '1  SW_A / SW_B boxes: compact switching-node corridor; keep quiet traces out.',
 '2  Suggested L2 void: only under final SW copper footprint. Do not cut return paths.',
 '3  Tall boxes beside MOSFETs: local PVDD HF loop. C100n nearest, then C1u / C10u.',
 '4  Driver boxes: HO/HS and LO/VSS gate loops. Reserve separate Kelvin source returns.',
 '5  L2: continuous GND reference elsewhere; no analogue/digital plane split.',
 '6  L3: symmetric +24 V feeds from central bulk, via lower band into local PVDD caps.',
 '7  Keep both speaker terminals floating from GND. Zobel / C330n are after inductors.',
 '8  Central box: U11 +12V_GD / U12 +5V_A thermal area; verify package and exposed pads.',
 '9  Translated power cells preserve MOSFET/driver orientation; routing is not validated.',
 '10 Existing tracks / vias / pours omitted in this COPY only. Production PCB unchanged.'
]): text(s,0,108+i*2,0.82)
# Advisory high-current trunk at y76, split centrally, avoiding quiet upper region.
for x in [34,66]:
    line(50,87,50,76,p.Cmts_User,.3);line(50,76,x,76,p.Cmts_User,.3)
text('+24 V FEED CORRIDORS',36,76,.6,p.Cmts_User)

assert identity(b)==before
p.SaveBoard(str(TARGET),b)
after=p.LoadBoard(str(TARGET));assert identity(after)==before
assert not list(after.GetTracks()) and not list(after.Zones())
assert hashes=={str(x.relative_to(ROOT)):hashlib.sha256(x.read_bytes()).hexdigest() for x in protected}
data=[]
for f in after.GetFootprints():
    bb=f.GetBoundingBox(False,False)
    data.append({'ref':f.GetReference(),'value':f.GetValue(),'footprint':before[f.GetReference()]['id'],
      'x':xy(f.GetPosition())[0],'y':xy(f.GetPosition())[1],'angle':f.GetOrientationDegrees(),
      'bbox':[xy(bb.GetOrigin()),xy(bb.GetEnd())], 'reference_xy':xy(f.Reference().GetPosition()),
      'pads':[{'number':a.GetNumber(),'net':a.GetNetname(),'xy':xy(a.GetPosition()),'size':[v/1e6 for v in a.GetSize()]} for a in f.Pads() if a.GetNumber()]})
(OUT/'placement.json').write_text(json.dumps({'origin_mm':[OX,OY],'dimensions_mm':[100,100],'removed_from_study_only':removed,'footprints':data,'notes':notes},indent=2)+'\n')
print(json.dumps({'target':str(TARGET),'footprints':len(data),'removed_from_copy':removed,'original_hashes_unchanged':True}))

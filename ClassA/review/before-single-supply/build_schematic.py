from pathlib import Path
import re,uuid,math,json
ROOT=Path(__file__).resolve().parents[1]
LIB=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols')
def uid():return str(uuid.uuid4())
def q(s):return json.dumps(str(s))
def extract(text, name):
 start=text.index('(symbol '+q(name)); i=start; depth=0; quoted=False; escape=False
 while i<len(text):
  c=text[i]
  if quoted:
   if escape:escape=False
   elif c=='\\':escape=True
   elif c=='"':quoted=False
  elif c=='"':quoted=True
  elif c=='(':depth+=1
  elif c==')':
   depth-=1
   if depth==0:return text[start:i+1]
  i+=1
symbols={}; custom={}; pins={}
def addlib(lib,name,new=None,swap=False):
 s=extract((LIB/(lib+'.kicad_sym')).read_text(),name)
 if new:
  s=s.replace(q(name),q(new)).replace(name+'_',new+'_')
  if swap:
   s=re.sub(r'\(number "([13])"',lambda m:'(number "'+('3' if m[1]=='1' else '1')+'"',s)
   s=s.replace('1=B 2=C 3=E','3=B 2=C 1=E')
  custom[new]=s; lib='ClassA_Transistors';name=new
 key=lib+':'+name
 symbols[key]=s.replace('(symbol '+q(name),'(symbol '+q(key),1)
 pd={}
 for p in re.finditer(r'\(pin \w+ \w+\s*\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\).*?\(name "([^"]*)".*?\(number "([^"]+)"',s,re.S):
  pd[p[5]]=(float(p[1])/2.54,float(p[2])/2.54,p[4])
 pins[key]=pd
 return key
N=addlib('Transistor_BJT','Q_NPN_BCE','KSC1845',True)
P=addlib('Transistor_BJT','Q_PNP_BCE','KSA992',True)
MED=addlib('Transistor_BJT','Q_NPN_BCE','2SC4793')
PMED=addlib('Transistor_BJT','Q_PNP_BCE','2SA1837')
POW=addlib('Transistor_BJT','Q_NPN_BCE','2SC5198')
R=addlib('Device','R');C=addlib('Device','C');CP=addlib('Device','C_Polarized');D=addlib('Device','D');L=addlib('Device','L');POT=addlib('Device','R_Potentiometer');TP=addlib('Connector','TestPoint');GND=addlib('power','GND');FLAG=addlib('power','PWR_FLAG')
J2=addlib('Connector_Generic','Conn_01x02');J3=addlib('Connector_Generic','Conn_01x03')
parts=[];elements=[];wiresegs=[];comps={};root='4e4123de-272a-4a3b-9bad-d5ed095ac90d';g=2.54
def mm(x):return f'{x*g:.4f}'.rstrip('0').rstrip('.')
def inst(lib,ref,val,x,y,a=0,m=None,dnp=False,desc='',ds=''):
 u=uid(); pd={};rad=math.radians(a)
 for num,(lx,ly,name) in pins[lib].items():
  if m=='x':ly=-ly
  if m=='y':lx=-lx
  pd[num]=(round(x+lx*math.cos(rad)-ly*math.sin(rad),6),round(y-lx*math.sin(rad)-ly*math.cos(rad),6))
 s=f'(symbol (lib_id {q(lib)}) (at {mm(x)} {mm(y)} {a}) (unit 1) '+(f'(mirror {m}) ' if m else '')+f'(in_bom yes) (on_board yes) (dnp {"yes" if dnp else "no"}) (uuid {u})'
 # Keep text horizontal and deliberately offset from local wires.
 dx=3 if ref.startswith('Q') else 2
 for name,value,py,hidden in [('Reference',ref,y-1,False),('Value',val,y+1,False),('Footprint','',y,True),('Datasheet',ds,y,True),('Description',desc,y,True)]:
  fx=x+dx;fa=0
  if ref.startswith('#') and (name=='Reference' or lib==FLAG):hidden=True
  if ref=='J3' and name=='Value':fx=x-2;py=y+11
  if a%180==90:
   fx=x-1;fa=90
   if name=='Reference':py=y-2
   elif name=='Value':py=y+2
  if ref in ['R22','R23'] and name in ['Reference','Value']:
   py=y+2 if name=='Reference' else y+4
  s+=f' (property {q(name)} {q(value)} (at {mm(fx)} {mm(py)} {fa}) (effects (font (size 1.15 1.15)) (justify left)'+(' (hide yes)' if hidden else '')+'))'
 for num in pd:s+=f' (pin {q(num)} (uuid {uid()}))'
 s+=f' (instances (project "ClassA" (path "/{root}" (reference {q(ref)}) (unit 1)))))'
 parts.append(s);comps[ref]={'lib':lib,'value':val,'pins':pd,'desc':desc};return pd

def wire(*pts):
 for p1,p2 in zip(pts,pts[1:]):
  if p1==p2:continue
  assert p1[0]==p2[0] or p1[1]==p2[1],(p1,p2)
  wiresegs.append((p1,p2));elements.append(f'(wire (pts (xy {mm(p1[0])} {mm(p1[1])}) (xy {mm(p2[0])} {mm(p2[1])})) (stroke (width 0) (type default)) (uuid {uid()}))')
def label(name,p,a=0):elements.append(f'(label {q(name)} (at {mm(p[0])} {mm(p[1])} {a}) (effects (font (size 1.15 1.15)) (justify left bottom)) (uuid {uid()}))')
def text(s,x,y,size=1.4):elements.append(f'(text {q(s)} (at {mm(x)} {mm(y)} 0) (effects (font (size {size} {size})) (justify left top)) (uuid {uid()}))')
ng=0;nt=0;nf=0
def ground(p):
 global ng;ng+=1;inst(GND,f'#PWR{ng:03}','GND',*p)
def flag(p):
 global nf;nf+=1;inst(FLAG,f'#FLG{nf:03}','PWR_FLAG',*p)
def tp(name,p,offset=(0,-3)):
 global nt;nt+=1;t=(p[0]+offset[0],p[1]+offset[1]);inst(TP,f'TP{nt}',name,*t);wire(p,(t[0],p[1]),t)
def two(lib,ref,val,x,y,h=False,**kw):return inst(lib,ref,val,x,y,90 if h else 0,**kw)
def resistor(ref,val,p1,p2):
 assert p1[0]==p2[0] or p1[1]==p2[1]
 h=p1[1]==p2[1];x=round((p1[0]+p2[0]))/2;y=round((p1[1]+p2[1]))/2
 pp=two(R,ref,val,x,y,h)
 ends=sorted(pp.values(),key=lambda p:p[0] if h else p[1]); pts=sorted([p1,p2],key=lambda p:p[0] if h else p[1]);wire(pts[0],ends[0]);wire(ends[1],pts[1]);return pp
DS5198='https://toshiba.semicon-storage.com/info/2SC5198_datasheet_en_20131101.pdf?did=20663&prodName=2SC5198'
DS4793='https://media.digikey.com/pdf/Data%20Sheets/Toshiba%20PDFs/2SC4793_Rev2006.pdf'
DS1837='https://media.digikey.com/pdf/Data%20Sheets/Toshiba%20PDFs/2SA1837.pdf'
DSKSC='https://www.onsemi.com/download/data-sheet/pdf/ksc1845-d.pdf';DSKSA='https://www.onsemi.com/download/data-sheet/pdf/ksa992-d.pdf'
text('MONO SINGLE-ENDED CLASS-A  |  FIRST-PASS SCHEMATIC  |  8 ohm / 12-15 W target',12,8,2.2)
text('INPUT / DIFFERENTIAL PAIR',12,23,1.8);text('CURRENT MIRROR / VAS',75,23,1.8);text('UPPER SIGNAL DRIVER',116,23,1.8);text('NPN CLASS-A POWER STAGE',150,23,1.8);text('OUTPUT / SPEAKER',190,23,1.8)
# INPUT: default AC input; DNP jumper permits DC coupling.
j=inst(J2,'J1','INPUT',12,50);wire(j['1'],(16,50));label('INPUT',(16,50));tp('INPUT',(16,50))
c=two(C,'C1','2u2 FILM / 63V',25,50,True);wire((16,50),c['1']);wire(c['2'],(38,50));label('IN_PLUS',(38,50))
r=resistor('R1','22k / 1% thin-film',(38,50),(38,60));ground((38,60));wire(j['2'],(9,51),(9,61));ground((9,61));tp('SIGNAL_GND',(9,61),(-3,4))
r=resistor('R2','0R DC BYPASS / DNP',(20,43),(30,43));wire((20,50),(20,43));wire((30,43),(30,50));# actual DNP property below
# Differential PNP: input on active collector side, feedback on mirror reference side.
q1=inst(P,'Q1','KSA992 / MATCH',48,50,m='x',ds=DSKSA);q2=inst(P,'Q2','KSA992 / MATCH',68,50,a=180,ds=DSKSA)
wire((38,50),q1['3']);wire(q2['3'],(76,50),(76,71));label('NFB',(76,71));tp('NFB',(76,71),(3,0))
resistor('R3','100R',q1['1'],(49,40));resistor('R4','100R',q2['1'],(67,40));wire((49,40),(58,40),(67,40))
qt=inst(P,'Q3','KSA992 / TAIL',57,34,m='x',ds=DSKSA);wire(qt['2'],(58,40));resistor('R5','270R / TUNE',qt['1'],(58,28));label('+20V',(58,28));wire(qt['3'],(52,34));label('P_BIAS',(52,34))
# NPN current mirror at negative rail, active load on input-side collector.
qm1=inst(N,'Q4','KSC1845',48,67,ds=DSKSC);qm2=inst(N,'Q5','KSC1845',68,67,a=0,m='y',ds=DSKSC)
wire(q1['2'],(49,55),(49,65));wire(q2['2'],(67,56),(67,65));wire(qm1['3'],(44,67),(44,61),(58,61),(72,61),(72,67),qm2['3']);wire((67,61),(67,65))
resistor('R6','100R',qm1['1'],(49,76));resistor('R7','100R',qm2['1'],(67,76));wire((49,76),(67,76));label('-20V',(58,76))
# VAS and 8 mA PNP active load; reference is shared with tail.
qv=inst(MED,'Q6','2SC4793 / VAS',96,59,ds=DS4793);wire((49,55),(87,55),(87,59),qv['1']);label('VAS_B',(87,59));resistor('R8','100R',qv['3'],(97,76));label('-20V',(97,76))
ql=inst(PMED,'Q7','2SA1837 / VAS CCS',96,39,m='x',ds=DS1837);resistor('R9','82R / TUNE',ql['3'],(97,28));label('+20V',(97,28));wire(ql['1'],(91,39));label('P_BIAS',(91,39));wire(ql['2'],(97,47),qv['2']);label('VAS_OUT',(97,47))
c=two(C,'C2','100p C0G / TUNE',86,48,True);wire(c['1'],(82,48),(82,55));wire(c['2'],(97,48));
# Positive reference: two silicon junctions, 2 mA bias. KSA tail and VAS current decrease with heat.
resistor('R10','9k1 / 0.25W',(82,90),(82,105));ground((82,105))
d1=two(D,'D1','1N4148',82,80);d2=two(D,'D2','1N4148',82,86)
# Diodes horizontal by default, rotate90 for cathode downward.
# Replaced below by helpers using parsed pin positions.
# upper driver
qd=inst(MED,'Q8','2SC4793 / DRIVER',126,47,ds=DS4793);resistor('R11','100R',(110,47),qd['1']);wire((97,47),(110,47));wire(qd['2'],(127,28));label('+20V',(127,28));wire(qd['3'],(127,57),(140,57));label('UPPER_BASE',(140,57))
resistor('R12','470R', (137,57),(137,70));label('AMP_OUT',(137,70));
# Output transistors QOUT1/2: vertical emitter followers, all local connections visible.
a=inst(POW,'QOUT1','2SC5198',159,57,ds=DS5198);b=inst(POW,'QOUT2','2SC5198',178,57,ds=DS5198)
wire((160,28),(179,28));label('+20V',(160,28));wire(a['2'],(160,28));wire(b['2'],(179,28))
resistor('R13','10R / TUNE',(150,57),a['1']);resistor('R14','10R / TUNE',(169,57),b['1']);wire((140,57),(150,57));wire((150,57),(150,51),(169,51),(169,57))
resistor('R15','0R22 / 5W',a['3'],(160,76));resistor('R16','0R22 / 5W',b['3'],(179,76));wire((160,76),(179,76),(188,76));label('AMP_OUT',(188,76));tp('AMP_OUT',(188,76));tp('QOUT1_E',(160,60),(-4,0));tp('QOUT2_E',(179,60),(4,0))
# Lower sink transistors share collector node ONLY. Their drive is DC current regulation.
sa=inst(POW,'QSINK1','2SC5198',159,92,ds=DS5198);sb=inst(POW,'QSINK2','2SC5198',178,92,ds=DS5198);wire(sa['2'],(160,76));wire(sb['2'],(179,76))
resistor('R17','10R / TUNE',(150,92),sa['1']);resistor('R18','10R / TUNE',(169,92),sb['1']);wire((150,92),(150,87),(169,87),(169,92));label('SINK_BASE',(150,92))
resistor('R19','0R22 / 5W',sa['3'],(160,107));resistor('R20','0R22 / 5W',sb['3'],(179,107));wire((160,107),(170,107),(179,107));label('SINK_RETURN',(170,107));resistor('R21','0R27 / 5W',(170,107),(170,120));label('-20V',(170,120));tp('QSINK1_E',(160,94),(-4,0));tp('QSINK2_E',(179,94),(7,-4));tp('SINK_RETURN',(179,107),(6,0));tp('SINK_NEG_REF',(170,120),(4,0))
# Average individual emitter voltages then sense against negative rail. Req = .27 + .22/2.
resistor('R22','100R / 1%',(149,96),(160,96));resistor('R23','100R / 1%',(168,98),(179,98));wire((179,98),(179,96));label('SENSE_AVG',(149,96));label('SENSE_AVG',(168,98))
# Current-sink feedback placed beneath VAS/driver.
qsd=inst(MED,'Q9','2SC4793 / SINK DRIVER',130,96,ds=DS4793);wire(qsd['2'],(131,84));label('AMP_OUT',(131,84));wire(qsd['3'],(131,103));label('SINK_BASE',(131,103))
resistor('R24','10k / 0.5W',(120,80),(120,92));label('+20V',(120,80));wire((120,92),(124,92),(124,96),qsd['1']);label('SINK_CTRL',(120,92))
qs=inst(MED,'Q10','2SC4793 / SENSE',114,103,ds=DS4793);wire(qs['2'],(115,92),(120,92));wire(qs['3'],(115,120));label('-20V',(115,120));tp('CS_VBE',(110,103),(-2,-3))
# Pot 1 at upper end SENSE_AVG, 3 at lower end, wiper2 through100 to sense base.
pot=inst(POT,'RV1','1k MULTITURN / TUNE',96,103);resistor('R25','3k3',pot['3'],(96,120));label('-20V',(96,120));wire(pot['1'],(96,94));label('SENSE_AVG',(96,94));resistor('R26','100R',pot['2'],qs['1']);resistor('R27','1k FAIL-LOW',(110,94),(110,103));wire((110,94),(96,94));wire((110,103),qs['1'])
# Output stability network; feedback before series inductor.
ind=two(L,'L1','0.82uH / >=4A / TBC',201,76,True);wire((188,76),ind['1']);wire(ind['2'],(216,76));label('SPK_OUT',(216,76));tp('SPK_OUT',(211,76))
resistor('R28','10R / 3W',(196,68),(206,68));wire((196,68),(196,76));wire((206,68),(206,76));j=inst(J2,'J2','SPEAKER / 8 ohm',220,76);wire((216,76),j['1']);wire(j['2'],(214,77),(214,96));ground((214,96))
cz=two(C,'C3','100n FILM / 63V',192,87);wire((192,76),cz['1']);resistor('R29','10R / 3W',cz['2'],(192,104));ground((192,104))
# Feedback dc gain unity, ac gain20; electrolytic pole .34Hz. DC offset matching at unity.
resistor('R30','19k / 1% thin-film',(20,78),(33,78));label('AMP_OUT',(20,78));wire((33,78),(37,78));label('NFB',(37,78));resistor('R31','1k / 1% thin-film',(37,78),(37,90));cf=two(C,'C4','470u / 25V BP',37,96);wire((37,90),cf['1']);wire(cf['2'],(37,103));ground((37,103));text('C4: bipolar electrolytic. DC gain = 1.\nAC gain = 1 + 19k/1k = 20 (26 dB).\nQ1/Q2: match VBE and hFE; thermally couple.',12,111,1.35)
clead=two(C,'C5','10p C0G / DNP TUNE',26.5,71,True,dnp=True);wire(clead['1'],(20,71),(20,78));wire(clead['2'],(33,71),(33,78))
# Power connector and local decoupling, star is common GND.
text('EXTERNAL SPLIT SUPPLY / LOCAL DECOUPLING',12,133,1.8)
j=inst(J3,'J3','+20V / GND / -20V',17,143)
wire(j['1'],(23,142));label('+20V',(23,142));flag((23,142));wire(j['2'],(11,143),(11,152));ground((11,152));flag((11,152));wire(j['3'],(23,144),(23,153));label('-20V',(23,153));flag((23,153))
for ref,lib,val,x,neg in [('C6',CP,'470u / 35V',35,False),('C7',C,'100n / 50V',47,False),('C8',CP,'470u / 35V',60,True),('C9',C,'100n / 50V',72,True)]:
 c=two(lib,ref,val,x,146)
 if neg:
  wire(c['1'],(x,140));ground((x,140));wire(c['2'],(x,153));label('-20V',(x,153))
 else:
  wire(c['1'],(x,139));label('+20V',(x,139));wire(c['2'],(x,153));ground((x,153))
tp('+20V',(35,139),(-3,0));tp('-20V',(60,153),(-3,0));tp('POWER_STAR_GND',(11,152),(0,4))
text('GROUND: one GND net. Separate input/feedback returns from speaker/Zobel and rail-cap returns.\nJoin at J3 GND/local capacitor star. No ground-plane split implied. PSU reservoirs external.',12,159,1.25)
# Design notes are kept on sheet for bench use.
text('CURRENT SINK SETUP / THERMAL',93,133,1.8)
text('RV1 wiper toward SENSE_AVG = minimum current. Set unloaded and current limited.\nSet each R19/R20 to 220 mV (1.00 A each); R21 ~540 mV (2.00 A total).\nI = VBE(Q10) / [alpha x (0.27 + 0.22/2)]; alpha ~0.79 to 1.\nNominal range ~1.6-2.2 A; junction temperature/device spread: TBC.\nR27 pulls Q10 base toward full sense on open wiper: current decreases.\nThermally couple Q10 to lower-bank heatsink; hotter Q10 reduces current.\nQOUT1/2 and QSINK1/2 need substantial external heatsinking and\nelectrical isolation: Toshiba 2SC5198 collector tabs are electrically live.\nMatch parallel devices; each has its own non-inductive 0R22 ballast and 10R stopper.',93,138,1.3)
text('FIRST-PASS LIMITS / BENCH TBC',93,160,1.8)
text('Output-stage idle supply power ~80 W; ~19-20 W per power transistor.\n12 W: 13.86 Vpk / 1.73 Apk. 15 W: 15.49 Vpk / 1.94 Apk.\n2 A sink gives ideal resistive Class-A current ceiling ~16 W / 8 ohm.\nUpper bank peaks ~3.94 A; budget beta=35 => ~113 mA base drive.\nQ8/Q9 require thermal margin; Q6/Q7 ~8 mA, ~0.16 W each at idle.\nC2 100p, C5 DNP, stoppers and L1: bench stability/step response TUNE.\nWarm offset <50 mV is a target, not verified. Test startup/shutdown DC,\nrail sag, sink transient response and hot DC SOA before PCB layout.\nNo simulation, bench qualification, PSU design or PCB work in this revision.',93,165,1.25)
text('ALL FOOTPRINTS UNASSIGNED: exact owned package/lead-form verification required before PCB.\nPins: 2SC5198 / 2SC4793 / 2SA1837 = 1 B, 2 C, 3 E; KSC1845 / KSA992 = 1 E, 2 C, 3 B.',12,178,1.25)
# Correct D1/D2 orientation and wire reference after removing initial horizontal instances.
for ref in ['D1','D2']:
 idx=next(i for i,s in enumerate(parts) if f'(property "Reference" "{ref}"' in s);parts.pop(idx);comps.pop(ref)
d1=inst(D,'D1','1N4148',82,80,a=90);d2=inst(D,'D2','1N4148',82,86,a=90)
wire(d1['2'],(82,76));label('+20V',(82,76));wire(d1['1'],d2['2']);wire(d2['1'],(82,90));label('P_BIAS',(82,90))
# Explicit DC bypass DNP.
for i,s in enumerate(parts):
 if '(property "Reference" "R2"' in s:parts[i]=s.replace('(dnp no)','(dnp yes)')
# Insert visible junctions wherever >=3 wire branches terminate; add points at wire interiors.
points=set(p for seg in wiresegs for p in seg)
for p in points:
 count=0
 for a,b in wiresegs:
  if a==p or b==p:count+=1
  elif a[0]==b[0]==p[0] and min(a[1],b[1])<p[1]<max(a[1],b[1]):count+=2
  elif a[1]==b[1]==p[1] and min(a[0],b[0])<p[0]<max(a[0],b[0]):count+=2
 if count>=3:elements.append(f'(junction (at {mm(p[0])} {mm(p[1])}) (diameter 0) (color 0 0 0 0) (uuid {uid()}))')
# A2 exceeds notes area (y=188 grid=477); use custom landscape sheet.
sch=f'(kicad_sch (version 20260306) (generator "eeschema") (generator_version "10.0") (uuid {root}) (paper "User" 594 508) (title_block (title "Mono single-ended Class-A / 2SC5198") (date "2026-10-05") (rev "0.1 FIRST PASS")) (lib_symbols '+''.join(symbols.values())+') '+''.join(parts+elements)+f' (sheet_instances (path "/" (page "1"))) (embedded_fonts no))'
(ROOT/'ClassA.kicad_sch').write_text(sch)
(ROOT/'ClassA_Transistors.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor") '+''.join(custom.values())+')')
(ROOT/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "ClassA_Transistors") (type "KiCad") (uri "${KIPRJMOD}/ClassA_Transistors.kicad_sym") (options "") (descr "Datasheet pin mappings for owned transistors")))\n')
(ROOT/'review/components.json').write_text(json.dumps(comps,indent=2))
print('Generated',len(comps),'symbols;',len(wiresegs),'wires')

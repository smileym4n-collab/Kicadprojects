#!/usr/bin/env python3
"""Build connected stereo KiCad 10 sheets, retaining project and empty PCB.
All component nets are independently checked against simulation/channel.cir.
"""
from pathlib import Path
import uuid,math,json,re
ROOT=Path(__file__).resolve().parents[1]
def U(s): return str(uuid.uuid5(uuid.NAMESPACE_URL,'MOSFETAmp2/'+s))
RID='79fb2543-8f2c-4462-98ea-7c2d1baaa4ac'; CID=U('channel')
SID=[U('left'),U('right')]
def q(s): return json.dumps(str(s))
def eff(n=1,just=''): return f'(effects (font (size {n} {n})) {just})'
def prop(k,v,x=0,y=0,hide=False,angle=0,just=''):return f'(property {q(k)} {q(v)} (at {x} {y} {angle}) {eff(1,just)}'+(' (hide yes)' if hide else '')+')'
def line(x1,y1,x2,y2,w=.254): return f'(polyline (pts (xy {x1} {y1})(xy {x2} {y2})) (stroke (width {w})(type default))(fill(type none)))'
def pin(no,name,x,y,a,typ='passive'):return f'(pin {typ} line (at {x} {y} {a})(length 2.54)(name {q(name)} {eff()})(number {q(no)} {eff()}))'
LIB={}
def sym(name,pins,graphics,prefix):
    pp={str(n):(x,y)for n,_,x,y,_,*_ in pins}
    s=f'(symbol {q(name)} '+('(pin_numbers (hide yes))' if name in ['R','C','CP','D','DZ','DS','LED','RV','L','TP'] else '')+f' (pin_names (offset 0)(hide yes))(exclude_from_sim no)(in_bom yes)(on_board yes)'+prop('Reference',prefix)+prop('Value',name)+f'(symbol {q(name+"_0_1")} '+graphics+')'+f'(symbol {q(name+"_1_1")} '+''.join(pin(*p)for p in pins)+'))'
    s=s.replace('(length 2.54)','(length 3.175)') if name in ['C','CP'] else s
    LIB[name]=(s.replace('(symbol \"GND\"','(symbol \"GND\" (power)',1) if name=='GND' else s,pp,prefix)
sym('R',[(1,'~',0,3.81,270),(2,'~',0,-3.81,90)],'(rectangle(start -1.016 2.54)(end 1.016 -2.54)(stroke(width .254)(type default))(fill(type none)))','R')
sym('C',[(1,'~',0,3.81,270),(2,'~',0,-3.81,90)],line(-2,.635,2,.635)+line(-2,-.635,2,-.635),'C')
sym('CP',[(1,'+',0,3.81,270),(2,'-',0,-3.81,90)],line(-2,.635,2,.635)+line(-2,-.635,2,-.635)+line(-3,1,-3,3)+line(-4,2,-2,2),'C')
for pn in ['N','P']:
    for pack in ['CBE','ECB']:
        xy={'B':(-5.08,0,0),'C':(2.54,5.08 if pn=='N' else -5.08,270 if pn=='N' else 90),'E':(2.54,-5.08 if pn=='N' else 5.08,90 if pn=='N' else 270)}
        pins=[(i+1,n,*xy[n]) for i,n in enumerate(pack)]
        g=line(-2.54,0,0,0)+line(0,2,0,-2,.5)+line(0,1,2.54,2.54)+line(0,-1,2.54,-2.54)
        if pn=='N':g+=line(2.54,-2.54,.9,-2.1)+line(2.54,-2.54,2.1,-.9)
        else:g+=line(.4,1.2,.8,2.7)+line(.4,1.2,1.9,1.5)
        sym('Q_'+pn+'_'+pack,pins,g,'Q')
for pn in ['N','P']:
    sign=1 if pn=='N' else -1
    g=line(-2.54,0,-1.5,0)+line(-1.5,2,-1.5,-2)+line(-.5,2,-.5,-2,.5)+line(-.5,2,2.54,2)+line(-.5,-2,2.54,-2)+line(2.54,2,2.54,2.54)+line(2.54,-2,2.54,-2.54)
    g+=line(.2,.8,1.4,0)+line(1.4,0,.2,-.8) if pn=='N' else line(1.4,.8,.2,0)+line(.2,0,1.4,-.8)
    sym('MOS_'+pn,[(1,'G',-5.08,0,0),(2,'D',2.54,sign*5.08,270 if sign==1 else 90),(3,'S',2.54,-sign*5.08,90 if sign==1 else 270)],g,'Q')
for name in ['D','DZ','DS']:
    g=line(-1.27,2,-1.27,-2,.4)+line(-1.27,0,1.27,2)+line(1.27,2,1.27,-2)+line(1.27,-2,-1.27,0)
    if name=='DZ':g+=line(-1.27,2,-.5,2.5)+line(-1.27,-2,-2,-2.5)
    sym(name,[(1,'K',-3.81,0,0),(2,'A',3.81,0,180)],g,'D')
g=line(-1.27,2,-1.27,-2,.4)+line(-1.27,0,1.27,2)+line(1.27,2,1.27,-2)+line(1.27,-2,-1.27,0)+line(-.5,2.5,.7,3.7)+line(.7,3.7,.1,3.5)+line(.5,2.5,1.7,3.7)+line(1.7,3.7,1.1,3.5)
sym('LED',[(1,'K',-3.81,0,0),(2,'A',3.81,0,180)],g,'D')
sym('RV',[(1,'1',0,3.81,270),(2,'2',5.08,0,180),(3,'3',0,-3.81,90)],'(rectangle(start -1.016 2.54)(end 1.016 -2.54)(stroke(width .254)(type default))(fill(type none)))'+line(2.54,0,1,0)+line(1,0,1.8,.8)+line(1,0,1.8,-.8),'RV')
sym('L',[(1,'~',-5.08,0,0),(2,'~',5.08,0,180)],''.join(f'(arc(start {x} 0)(mid {x+.635} 1.27)(end {x+1.27} 0)(stroke(width .254)(type default))(fill(type none)))'for x in [-2.54,-1.27,0,1.27]),'L')
for n in [2,3]:
    pins=[(i+1,str(i+1),-5.08,-i*2.54,0)for i in range(n)]
    g=f'(rectangle(start -2.54 1.27)(end 0 {-2.54*(n-1)-1.27})(stroke(width .254)(type default))(fill(type none)))'
    sym('J'+str(n),pins,g,'J')
sym('TP',[(1,'1',0,-2.54,90)],'(circle(center 0 0)(radius 1)(stroke(width .254)(type default))(fill(type none)))','TP')
sym('GND',[(1,'GND',0,0,270,'power_in')],line(0,0,0,-1.27)+line(-2.54,-1.27,2.54,-1.27)+line(-1.5,-2,1.5,-2)+line(-.5,-2.7,.5,-2.7),'#PWR')
sym('PWR_FLAG',[(1,'pwr',0,0,90,'power_out')],line(0,0,0,2.54)+line(0,2.54,2.54,3.81)+line(2.54,3.81,0,5.08)+line(0,5.08,-2.54,3.81)+line(-2.54,3.81,0,2.54),'#FLG')

def standard_power(name):
    text=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/power.kicad_sym').read_text()
    start=text.index('(symbol "'+name+'"'); toks=list(re.finditer(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()]+',text[start:])); depth=0
    for t in toks:
        depth+=(t[0]=='(')-(t[0]==')')
        if depth==0:
            LIB[name]=(text[start:start+t.end()],{'1':(0,0)},'#PWR'if name=='GND'else'#FLG');break
standard_power('GND');standard_power('PWR_FLAG')
FPR='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal'
FPP='Resistor_THT:R_Axial_DIN0617_L17.0mm_D6.0mm_P30.48mm_Horizontal'
FPC='Capacitor_THT:C_Rect_L7.2mm_W2.5mm_P5.00mm'
FPD='Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal'
class Sheet:
 def __init__(self,name,uid,root=False):self.name=name;self.uid=uid;self.items=[];self.parts={};self.root=root;self.idx=0;self.junctions=set()
 def add(self,ref,kind,value,x,y,angle=0,mirror=False,fp='',mpn='',ds='',stock='',note='',nets=None,lab=None):
    u=U(self.name+'/'+ref);self.idx+=1
    pins=LIB[kind][1];a=math.radians(angle)
    def pos(pt):
      px,py=pt;px=-px if mirror else px
      return(round(x+px*math.cos(a)+py*math.sin(a),4),round(y+px*math.sin(a)-py*math.cos(a),4))
    ps={n:pos(p)for n,p in pins.items()}
    rbase=re.match(r'(\D+)(\d+)',ref)
    inst=''
    if self.root:inst=f'(path "/{RID}" (reference {q(ref)})(unit 1))'
    else:
      for i in range(2):
       rr=f'{rbase[1]}{int(rbase[2])+i*(10000 if ref.startswith('#') else 100)}'
       inst+=f'(path "/{RID}/{SID[i]}" (reference {q(rr)})(unit 1))'
    if kind=='L' or (kind in ['D','DZ','DS','LED'] and angle in [0,180]):
      props=prop('Reference',ref,x,y-3.81)+prop('Value',value,x,y+3.81)
    elif angle==0:
      px=x+3.81; py=y
      if kind.startswith('Q_') or kind.startswith('MOS_'):px=x-15.24 if mirror else x+7.62
      if kind=='RV':px=x+12.7
      dy=1.27 if kind in ['R','C','CP'] else 2.54
      props=prop('Reference',ref,px,py-dy,just='(justify left)')+prop('Value',value,px,py+(1.27 if kind in ['R','C','CP'] else 0),just='(justify left)')
    else:
      props=prop('Reference',ref,x,y-3.81,angle=((-angle)%360 if angle!=180 else 0))+prop('Value',value,x,y+3.81,angle=((-angle)%360 if angle!=180 else 0))
    if lab:la=(-angle)%360 if angle in (90,270) else 0;props=prop('Reference',ref,x+lab[0],y+lab[1]-1.27,angle=la,just='(justify left)')+prop('Value',value,x+lab[0],y+lab[1]+1.27,angle=la,just='(justify left)')
    props+=prop('Footprint',fp,x,y,True)+prop('Datasheet',ds,x,y,True)+prop('MPN',mpn,x,y,True)+prop('Inventory_ID',stock,x,y,True)+prop('Design_note',note,x,y,True)
    visible=kind not in ['GND','PWR_FLAG']
    if not visible: props=prop('Reference',ref,x,y,True)+prop('Value','GND' if kind=='GND' else 'PWR_FLAG',x,y+4,kind!='GND')
    self.items.append(f'(symbol (lib_id "{"power" if kind in ["GND","PWR_FLAG"] else "MOSFETAmp2"}:{kind}")(at {x} {y} {(-angle)%360})(unit 1)'+('(mirror y)' if mirror else '')+f'(in_bom {"yes" if visible else "no"})(on_board {"yes" if visible else "no"})(dnp no)(uuid {u})'+props+''.join(f'(pin {q(n)}(uuid {U(u+n)}))'for n in pins)+f'(instances(project "MOSFETAmp2" {inst})))')
    self.parts[ref]={'kind':kind,'value':value,'pins':ps,'footprint':fp,'mpn':mpn,'datasheet':ds,'stock_id':stock,'note':note,'nets':nets or {}}
    return ps
 def p(self,ref,n):return self.parts[ref]['pins'][str(n)]
 def wire(self,*pts):
    for a,b in zip(pts,pts[1:]):
      if a==b:continue
      self.idx+=1;self.items.append(f'(wire(pts(xy {a[0]} {a[1]})(xy {b[0]} {b[1]}))(stroke(width 0)(type default))(uuid {U(self.name+"/wire"+str(self.idx))}))')
 def dot(self,p):
    if p in self.junctions:return
    self.junctions.add(p);self.items.append(f'(junction(at {p[0]} {p[1]})(diameter 0)(color 0 0 0 0)(uuid {U(self.name+"/dot"+str(p))}))')
 def label(self,n,p,angle=0):self.items.append(f'(label {q(n)}(at {p[0]} {p[1]} {angle}) {eff(.95,"(justify left bottom)")}(uuid {U(self.name+"/label"+str(self.idx)+n+str(p))}))')
 def term(self,ref,pinno,node,at=None):
    p=self.p(ref,pinno);z=at or(p[0],p[1]+(4 if node=='GND' else -4))
    self.wire(p,z)
    if node=='GND':self.add('#PWR'+str((90000 if self.root else 10000)+self.idx),'GND','GND',*z)
    else:self.label(node,z)
 def txt(self,s,x,y,size=1.1):self.items.append(f'(text {q(s)}(at {x} {y} 0){eff(size,"(justify left top)")}(uuid {U(self.name+"/text"+s)}))')
 def hlabel(self,n,p,a,typ='passive'):self.items.append(f'(hierarchical_label {q(n)}(shape {typ})(at {p[0]} {p[1]} {a}){eff(1,"(justify left)")}(uuid {U(self.name+"/hlabel"+n)}))')
 def write(self,path,title):
    self.items=[re.sub(r'\((at|xy) ([-.0-9]+) ([-.0-9]+)',lambda m:f'({m[1]} {round(round(float(m[2])/1.27)*1.27,4)} {round(round(float(m[3])/1.27)*1.27,4)}',z)for z in self.items]
    lib=''.join(s.replace('(symbol '+q(k),'(symbol '+q(('power:' if k in ['GND','PWR_FLAG'] else 'MOSFETAmp2:')+k),1)for k,(s,_,__)in LIB.items())
    s=f'(kicad_sch(version 20260306)(generator "eeschema")(generator_version "10.0")(uuid {self.uid})(paper "A3")(title_block(title {q(title)})(date "2026-10-25")(rev "0.2 EXPERIMENTAL"))(lib_symbols {lib})'+''.join(self.items)
    if self.root:s+=f'(sheet_instances(path "/"(page "1")))'
    s+='(embedded_fonts no))';(ROOT/path).write_text(s)

S=Sheet('channel',CID)
Rvals={1:'1k',2:'22k',3:'22k',4:'2k2',5:'100R',6:'100R',7:'330R',8:'12k',9:'100R',10:'10k',11:'100R',12:'3k9',13:'1k SLOPE SEL',14:'1k SOT',15:'2k2',16:'2k2',17:'100R',18:'100R',19:'0R33 / 5W',20:'0R33 / 5W',21:'47k',22:'47k',23:'100R',24:'100R',25:'10R / 2W',26:'10R / 2W',27:'680R'}
Rstock={1:285,2:276,3:276,4:268,5:150,6:150,7:290,8:273,9:150,10:272,11:150,13:285,14:285,15:268,16:268,17:150,18:150,19:288,20:288,21:277,22:277,23:150,24:150,27:291}
RNOTE={13:'SLOPE SELECT: k = 1 + 3k9/R13. 1k0 default for about -4.7 mV/K per MOSFET; choose from measured VGS slope (docs/BIAS_STUDY.md table).',
 14:'SELECT ON TEST (RE): leave UNFITTED for first bias power-up (zero offset); fit one E24 step above the calculated value (docs/BIAS_STUDY.md). 1k0 is the nominal-model value.',
 12:'Fixed multiplier upper resistor; purchase LR1F3K9.',27:'LED reference feed, about 1 mA from TREF.'}
def R(n,x,y,h=False,**kw):return S.add('R'+str(100+n),'R',Rvals[n],x,y,90 if h else 0,fp=FPP if n in [19,20,25,26] else FPR,stock=Rstock.get(n,''),mpn='MCKNP05SJ033KAA9'if n in [19,20]else('ROX2SJ10R'if n in [25,26]else'LR1F'+Rvals[n].split()[0].upper()),ds='https://www.te.com/en/product-1625890-6.html'if n in [25,26]else'',note='Noninductive flameproof metal oxide; purchase'if n in [25,26]else RNOTE.get(n,''),**kw)
def C(n,x,y,h=False,**kw):
 val={1:'220p C0G',2:'330p C0G',3:'100n / 63V',4:'100n FILM / 63V',5:'220u / 35V',6:'220u / 35V',7:'100n / 63V',8:'100n / 63V'}[n]
 return S.add('C'+str(100+n),'CP'if n in [5,6]else'C',val,x,y,90 if h else 0,fp=('MOSFETAmp2:C_Radial_Kemet_C315_P2.54'if n==2 else'Capacitor_SMD:C_0805_2012Metric')if n in [1,2]else('Capacitor_THT:CP_Radial_D8.0mm_P3.50mm'if n in [5,6]else FPC),stock=(198 if n==1 else '')if n in [1,2]else(366 if n in [5,6]else 406),mpn=('C315C331J5G5TA'if n==2 else'0805N221J500CT')if n in [1,2]else('35ZLH220MEFC8X11.5'if n in [5,6]else'R82DC3100DQ50J'),ds='https://yageogroup.com/content/datasheet/asset/file/KEM_C1049_GOLDMAX_C0G'if n==2 else'',**kw)
def Q(n,x,y,mirror=False,**kw):
 pnp=n in [1,2,5,7,10,14,17];bd=n in [6,8,9,10];mos=n in [11,12]
 val=('IRF540N'if n==11 else'IRF9540N')if mos else(('BD140'if pnp else'BD139')if bd else('BC556'if pnp else'BC546'))
 kind='MOS_'+('N'if n==11 else'P')if mos else'Q_'+('P'if pnp else'N')+'_'+('ECB'if bd else'CBE')
 stock={ 'IRF540N':'','IRF9540N':257,'BD139':148,'BD140':149,'BC556':462,'BC546':254}[val]
 ds='https://www.infineon.com/assets/row/public/documents/24/49/infineon-'+val.lower()+'-datasheet-en.pdf'if mos else('https://www.st.com/resource/en/datasheet/bd135.pdf'if bd else('https://www.onsemi.com/pdf/datasheet/bc556bta-d.pdf'if pnp else'https://www.farnell.com/datasheets/2277528.pdf'))
 return S.add('Q'+str(100+n),kind,val,x,y,mirror=mirror,fp='Package_TO_SOT_THT:TO-220-3_Vertical'if mos else('Package_TO_SOT_THT:TO-126-3_Vertical'if bd else'Package_TO_SOT_THT:TO-92_Inline'),mpn=val+'PbF'if mos else val,ds=ds,stock=stock,note='INSULATE live drain tab'if mos else('Clamp to output heatsink; insulate collector tab'if n==8 else('Select matched VBE and hFE; thermal bond'if n in [1,2]else('Bias offset current sink; PCB, near D109/D112'if n==16 else('LED reference feed; PCB'if n==17 else'')))),**kw)
def D(n,x,y,a=0,**kw):
 if n==13:return S.add('D113','LED','LED RED',x,y,a,**kw,fp='LED_SMD:LED_0805_2012Metric',mpn='KP-2012EC',ds='https://www.farnell.com/datasheets/2628136.pdf',stock=640,note='Bias offset reference, about 1 mA. Stocked Kingbright KP-2012EC, 2012 metric SMD; verify cathode mark against pad 1.')
 v='BZX85C10'if n in [10,11]else('BAT46'if n==8 else'1N4148')
 return S.add('D'+str(100+n),'DZ'if n in [10,11]else('DS'if n==8 else'D'),v,x,y,a,fp=('Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal'if n in [10,11]else FPD),mpn='BAT46-TR'if n==8 else v,ds='https://www.vishay.com/docs/85662/bat46.pdf'if n==8 else'',stock=251 if n in [10,11]else(138 if n not in [8] else''),note='Driver VBE tracking; PCB beside Q109/Q110'if n in [9,12]else'',**kw)
def connect(r,n,*points):S.wire(S.p(r,n),*points)
def label(n,p):S.label(n,p)
def w(*p):S.wire(*p)
def dot(p):S.dot(p)
# Rev 0.2 layout: conventional amplifier drawing on a 2.54 mm grid (all coordinates below in grid units).
# +V rail along the top, -V rail along the bottom, signal left to right, OUT/feedback line across the middle.
g=lambda v:round(v*2.54,4)
def G(x,y):return(g(x),g(y))
def W(*pts):S.wire(*[p if isinstance(p,tuple) and len(p)==2 and not isinstance(p[0],str) else p for p in pts])
def pin(ref,n):return S.p(ref,n)
def gnd(x,y,up=False):S.add('#PWR'+str(10000+S.idx),'GND','GND',g(x),g(y),180 if up else 0)
def rlab(name,x,y):S.label(name,G(x,y))
def dots(*pts):
 for x,y in pts:S.dot(G(x,y))
YP,YN,YO=12,94,53   # +V rail, -V rail, OUT / feedback line
for x,t in [(8,'INPUT / DIFFERENTIAL PAIR'),(58,'VAS + ACTIVE LOAD'),(76,'THERMAL BIAS / PROGRAMMED OFFSET'),(106,'DRIVERS / OUTPUT PAIR'),(134,'OUTPUT / DECOUPLING')]:S.txt(t,g(x),g(5),1.3)
# Input network
S.hlabel('IN',G(8,YO),180,'input');R(1,g(14),g(YO),True);R(2,g(20),g(58));C(1,g(25),g(58))
W(G(8,YO),pin('R101',2));W(pin('R101',1),G(20,YO),G(25,YO),G(30,YO));dots((20,YO),(25,YO))
W(pin('R102',1),G(20,YO));W(pin('R102',2),G(20,62));gnd(20,62);W(pin('C101',1),G(25,YO));W(pin('C101',2),G(25,62));gnd(25,62)
rlab('B1',30,YO)
# Long-tailed pair, tail source and its two-diode reference
Q(2,g(36),g(YO));Q(1,g(50),g(YO),True,lab=(g(1),g(-4)));R(6,g(37),g(46));R(5,g(49),g(46));Q(5,g(42),g(26));R(7,g(43),g(18))
W(G(30,YO),pin('Q102',2));W(pin('Q102',3),pin('R106',2));W(pin('Q101',3),pin('R105',2))
W(pin('R106',1),G(37,42),G(43,42),G(49,42),pin('R105',1));dots((43,42));W(pin('Q105',1),G(43,42))
W(pin('Q105',3),pin('R107',2));W(pin('R107',1),G(43,YP))
D(2,g(30),g(17),270,lab=(g(3.5),0));D(1,g(30),g(22.5),270,lab=(g(3.5),0));R(8,g(30),g(30))
W(pin('D102',2),G(30,YP));W(pin('D102',1),pin('D101',2));W(pin('D101',1),G(30,26),pin('R108',1));W(G(30,26),pin('Q105',2));dots((30,26));rlab('TREF',33,26)
W(pin('R108',2),G(30,33.5));rlab('VN',30,33.5)
# Feedback divider: FB node right of Q101, R103 back along the OUT line
R(4,g(55),g(58));R(3,g(59),g(YO),True)
W(pin('Q101',2),G(55,YO),pin('R103',2));dots((55,YO));rlab('FB',53,YO);W(pin('R104',1),G(55,YO));W(pin('R104',2),G(55,62));gnd(55,62)
# Current mirror (Q103 diode-connected under Q101)
Q(4,g(38),g(80),True);Q(3,g(48),g(80))
W(pin('Q102',1),G(37,66),pin('Q104',1));W(pin('Q101',1),G(49,76),pin('Q103',1));W(pin('Q104',2),G(43,80),pin('Q103',2));W(G(49,76),G(43,76),G(43,80));dots((49,76),(43,80),(37,66))
W(pin('Q104',3),G(37,YN));W(pin('Q103',3),G(49,YN))
# VAS: Q115 buffer, Q106 VAS, Miller capacitor and anti-saturation clamp
C(2,g(67),g(58),True);D(7,g(63),g(62),180);D(8,g(69),g(62),180);Q(15,g(65),g(70));Q(6,g(73),g(76));R(10,g(66),g(82));R(9,g(74),g(84))
W(G(37,66),G(60,66));W(G(60,58),G(60,62),G(60,66),G(60,70),pin('Q115',2));dots((60,62),(60,66))
W(G(60,58),pin('C102',2));W(G(60,62),pin('D107',2));W(pin('D107',1),pin('D108',2));rlab('C2N',52,66)
W(pin('Q115',1),G(66,67));rlab('VP',66,67)
W(pin('Q115',3),G(66,76),pin('Q106',3));W(G(66,76),pin('R110',1));dots((66,76));W(pin('R110',2),G(66,YN))
W(pin('Q106',1),pin('R109',1));W(pin('R109',2),G(74,YN))
# Active load from +V
Q(7,g(73),g(22));R(11,g(74),g(16));W(pin('R111',1),G(74,YP));W(pin('R111',2),pin('Q107',3));W(pin('Q107',2),G(68,22));rlab('TREF',68,22)
# Bias spreader between BP (top) and BN (bottom)
D(9,g(74),g(30),270,lab=(g(3.5),0));D(12,g(74),g(35),270,lab=(g(3.5),0));Q(8,g(75),g(42),True,lab=(g(-4.5),g(0)));C(3,g(67),g(38))
R(12,g(80),g(41));R(13,g(80),g(48.5));Q(16,g(87),g(48),True,lab=(g(1),g(3)));R(14,g(86),g(57));Q(17,g(93),g(40),True,lab=(g(1),g(-4)))
S.add('RV101','RV','200R MULTITURN',g(86),g(63),fp='Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical',mpn='3296W-1-201LF',ds='https://www.bourns.com/docs/product-datasheets/3296.pdf',note='Wiper 2 tied to 3. Maximum 1-to-(2+3) resistance = minimum bias. Value sized to R114: 200R up to 1k3, 500R up to 3k3, 2k above. Stock generic fit unverified.',lab=(g(3),g(-1)))
D(13,g(92),g(58),270,lab=(g(3.5),0));R(27,g(92),g(33))
W(pin('Q107',1),G(74,26),G(74,27),pin('D109',2));W(pin('D109',1),pin('D112',2));W(pin('D112',1),G(74,38),pin('Q108',2))
W(G(74,27),G(67,27),pin('C103',1));W(pin('C103',2),G(67,48),G(74,48))
W(G(74,38),G(80,38),pin('R112',1));W(pin('R112',2),G(80,43),G(80,45),pin('R113',1));W(pin('Q108',3),G(77,43),G(80,43))
W(G(80,45),G(86,45),pin('Q116',1));W(pin('R113',2),G(80,51),G(74,51))
W(pin('Q108',1),G(74,48),G(74,51),G(74,58),G(74,62),G(74,71),pin('Q106',2))
W(G(74,58),pin('C102',1));W(pin('D108',1),G(74,62))
dots((74,26),(74,27),(74,38),(80,43),(80,45),(74,48),(74,51),(74,58),(74,62),(74,71))
W(pin('Q116',3),pin('R114',1));W(pin('R114',2),pin('RV101',1));W(pin('RV101',2),G(88,66),G(86,66),pin('RV101',3));W(G(86,66),G(86,68));rlab('VN',86,68);dots((86,66))
W(pin('R127',1),G(92,30.5));rlab('VP',92,30.5);W(pin('R127',2),pin('Q117',3));W(pin('Q117',2),G(97,40));rlab('TREF',97,40)
W(pin('Q117',1),G(92,48),pin('D113',2));W(G(92,48),pin('Q116',2));dots((92,48));W(pin('D113',1),G(92,62));rlab('VN',92,62)
S.add('J101','J2','BIAS SHORT - FIT FIRST',g(64),g(46),fp='Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical',mpn='MC34629',stock=126,lab=(g(-9),g(-2.5)))
W(pin('J101',1),G(59,46));rlab('BP',59,46);W(pin('J101',2),G(59,47));rlab('BN',59,47)
rlab('BP',84,26);rlab('BN',84,71)
# Drivers (BD139/BD140 emitter followers)
Q(9,g(107),g(26));Q(10,g(107),g(80));R(15,g(108),g(36.5));R(16,g(108),g(69.5));R(17,g(115),g(31),True);R(18,g(115),g(75),True)
W(G(74,26),pin('Q109',3));W(pin('Q109',2),G(108,YP));W(pin('Q110',2),G(108,YN))
W(G(74,71),G(103,71),G(103,80),pin('Q110',3))
W(pin('Q109',1),G(108,31),pin('R115',1));W(G(108,31),pin('R117',2));W(pin('R115',2),G(108,YO));W(pin('R116',1),G(108,YO))
W(pin('Q110',1),G(108,75),pin('R116',2));W(G(108,75),pin('R118',2));dots((108,31),(108,75))
# Output MOSFETs with gate stoppers, gate-source bleed resistors and clamps
Q(11,g(127),g(31));Q(12,g(127),g(75));R(19,g(128),g(43));R(20,g(128),g(62.5));R(21,g(120),g(35.5),lab=(g(-4.5),0));D(10,g(123),g(35.5),90);R(22,g(120),g(71),lab=(g(-4.5),0));D(11,g(123),g(71),90)
W(pin('R117',1),G(120,31),G(123,31),pin('Q111',1));W(G(120,31),pin('R121',1));W(G(123,31),pin('D110',1))
W(pin('R121',2),G(120,39),G(123,39),G(128,39));W(pin('D110',2),G(123,39));W(pin('Q111',3),G(128,39),G(128,40),pin('R119',1))
W(pin('R118',1),G(120,75),G(123,75),pin('Q112',1));W(G(120,75),pin('R122',2));W(G(123,75),pin('D111',2))
W(pin('R122',1),G(120,67),G(123,67),G(128,67));W(pin('D111',1),G(123,67));W(pin('R120',2),G(128,67),G(128,70),pin('Q112',3))
W(pin('Q111',2),G(128,YP));W(pin('Q112',2),G(128,YN))
W(pin('R119',2),G(128,YO),pin('R120',1))
dots((120,31),(123,31),(123,39),(128,39),(128,40),(120,75),(123,75),(123,67),(128,67),(128,70))
# OUT line: feedback from R103 runs across to the output node (crossings without dots are not connections)
W(pin('R103',1),G(108,YO),G(128,YO),G(132,YO),G(136,YO),G(139,YO));dots((108,YO),(128,YO),(132,YO),(136,YO),(139,YO));rlab('OUT',62,YO);rlab('OUT',129,YO)
for n,node,x,y,px,py in [(1,'SN',132,39,128,40),(2,'OUT',132,50,132,YO),(3,'SP',132,69,128,70)]:
 rr='TP'+str(100+n);S.add(rr,'TP',node,g(x),g(y),fp='TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm',lab=(g(1.5),g(-0.5)));W(pin(rr,1),G(px,py))
# Zobel and damped output coil (outside the feedback loop)
R(25,g(136),g(58.5));C(4,g(136),g(64.5));W(G(136,YO),pin('R125',1));W(pin('R125',2),pin('C104',1));W(pin('C104',2),G(136,69));gnd(136,69)
S.add('L101','L','0.7uH AIR / 3A',g(143),g(YO),fp='MOSFETAmp2:L_Air_0u7_12T',note='12 turns 1mm enamelled copper on 8mm mandrel; measure L and DCR')
R(26,g(143),g(49),True)
W(G(139,YO),pin('L101',1));W(G(139,YO),G(139,49),pin('R126',2));W(pin('R126',1),G(147,49),G(147,YO));W(pin('L101',2),G(147,YO),G(154,YO));dots((147,YO))
S.hlabel('SPK',G(154,YO),0,'output')
# Local decoupling and rail test points
for n,x,y in [(5,140,18),(7,146,18)]:C(n,g(x),g(y));W(pin('C'+str(100+n),1),G(x,YP));W(pin('C'+str(100+n),2),G(x,22));gnd(x,22)
for n,x,y in [(6,140,88),(8,146,88)]:C(n,g(x),g(y));W(pin('C'+str(100+n),1),G(x,84));gnd(x,84,True);W(pin('C'+str(100+n),2),G(x,YN))
S.add('TP104','TP','VP',g(151),g(8),fp='TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm',lab=(g(1.5),g(-0.5)));W(pin('TP104',1),G(151,YP))
S.add('TP105','TP','VN',g(151),g(97),fp='TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm',lab=(g(1.5),g(0.5)));W(pin('TP105',1),G(151,YN))
# Rails
vp=[30,43,74,108,128,140,146,151,156];vn=[37,49,66,74,108,128,140,146,151,156]
W(*[G(x,YP) for x in vp]);W(*[G(x,YN) for x in vn]);dots(*[(x,YP) for x in vp[1:-1]],*[(x,YN) for x in vn[1:-1]])
S.hlabel('VP',G(156,YP),0);S.label('VP',G(156,YP));S.hlabel('VN',G(156,YN),0);S.label('VN',G(156,YN))
# Input overload clamps (antiparallel, B1 to FB)
D(5,g(16),g(74));D(6,g(16),g(79),180)
W(pin('D105',1),G(12,74),G(12,76.5),G(12,79),pin('D106',2));W(pin('D105',2),G(20,74),G(20,76.5),G(20,79),pin('D106',1));W(G(12,76.5),G(9,76.5));W(G(20,76.5),G(23,76.5));rlab('FB',9,76.5);rlab('B1',23,76.5);dots((12,76.5),(20,76.5))
S.txt('Input overload clamps',g(8),g(70),1.0)
# Notes
S.txt('Q101/Q102: match VBE at 1 mA; bond flat faces.\nR101 + R102: input about 23k; gain 11 from B1,\nabout 10.52 (20.44 dB) at IN. DC coupled.\nC102 = 330p C0G 50V radial; D107 + D108\nprevent VAS saturation. VAS/load about 6 mA.',g(8),g(99),.95)
S.txt('BIAS: Q108 on heatsink beside its MOSFETs.\nk = 1 + 3k9/R113 (R113 = slope select).\nD109/D112 on PCB beside Q109/Q110.\nOffset = 3k9 x (V(D113) - VBE)/(R114 + RV101).\nR114 unfitted / RV101 max resistance = MIN BIAS.\nFit J101 for first power-up. See BIAS_STUDY.md.',g(42),g(99),.95)
S.txt('16.5 mV across each 0R33 = 50 mA (TP101-TP102, TP102-TP103).\nOUT is feedback sense BEFORE the coil.\nMOSFET drain tabs are live: INSULATE.\nGate Zeners: N K to gate; P K to source.\n8 ohm prototype; no short-circuit protection;\nexternal DC speaker protection required.',g(78),g(99),.95)
S.write('Channel.kicad_sch','Class-AB channel - experimental Rev 0.2')
# Top level: independent rail connectors permit one-channel bring-up.
T=Sheet('root',RID,True)
T.txt('MOSFETAmp2 - STEREO DISCRETE CLASS-AB',20,15,2.5)
T.txt('REV 0.2: SIMULATION DEVELOPMENT / NOT FABRICATION RELEASED\n8 ohm prototype; external current-limited +/-12 to +/-15 V first.\nNo mains circuitry. External DC speaker protection required. Read README and bench procedure.\nBIAS: fixed-ratio sensor + programmed offset; MOSFET VGS slope and SOA still need measurement.',20,28,1.3)
for i in range(2):
 x=100+i*180;y=100;sn='LEFT'if i==0 else'RIGHT';uid=SID[i]
 sheetpins=''.join(f'(pin {q(n)} {typ}(at {px} {py} {a}){eff()}(uuid {U(uid+n)}))'for n,typ,px,py,a in [('IN','input',x,y+20,180),('SPK','output',x+65,y+20,0),('VP','passive',x,y+10,180),('VN','passive',x,y+40,180)])
 T.items.append(f'(sheet(at {x} {y})(size {round(round((x+65)/1.27)*1.27-round(x/1.27)*1.27,4)} {round(round((y+55)/1.27)*1.27-round(y/1.27)*1.27,4)})(fields_autoplaced yes)(stroke(width .1524)(type solid))(fill(color 0 0 0 0))(uuid {uid})'+prop('Sheetname',sn,x,y-3)+prop('Sheetfile','Channel.kicad_sch',x,y+58)+sheetpins+f'(instances(project "MOSFETAmp2"(path "/{RID}"(page {q(str(i+2))}))))'+')')
 j=1+i
 T.add('J'+str(j),'J3','POWER '+sn,x-40,y-15,fp='TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal',mpn='1715734',ds='https://www.phoenixcontact.com/en-us/products/1715734',note='Pin1 +V, pin2 GND, pin3 -V. Verify purchased exact housing.')
 for no,n in [(1,'V'+sn+'P'),(3,'V'+sn+'N')]:
  p=T.p('J'+str(j),no);z=(x-55,y-25)if no==1 else(x-60,y);T.wire(p,(z[0],p[1]),z);T.label(n,z);T.add('#FLG'+str(j*10+no),'PWR_FLAG','PWR_FLAG',*z)
 T.term('J'+str(j),2,'GND',(x-55,y-12.46))
 T.txt('1: +V\n2: GND\n3: -V',x-35,y-7,1.0)
 for p,n in [((x,y+10),'V'+sn+'P'),((x,y+40),'V'+sn+'N')]:T.wire(p,(x-10,p[1]));T.label(n,(x-10,p[1]))
 T.add('J'+str(3+i),'J2','INPUT '+sn,x-40,y+30,fp='Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical',mpn='MC34629',stock=126)
 p=T.p('J'+str(3+i),1);T.wire(p,(p[0]-5,p[1]),(p[0]-5,y+20),(x,y+20));T.term('J'+str(3+i),2,'GND',(p[0],y+43))
 T.add('J'+str(5+i),'J2','TO PROTECTION '+sn,x+95,y+20,fp='TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal',mpn='1715721',ds='https://www.phoenixcontact.com/en-us/products/1715721')
 T.wire((x+65,y+20),T.p('J'+str(5+i),1));T.term('J'+str(5+i),2,'GND',(x+90,y+35))
T.add('#FLG99','PWR_FLAG','PWR_FLAG',30,230);T.add('#PWR99','GND','GND',30,230)
T.txt('Assembly gates\n1. Fit bias short J101/J201; leave R114/R214 unfitted; trimmers at MAXIMUM resistance.\n2. Verify live tab insulation and Q108/Q208 thermal contact.\n3. Connect supply GND to the junction of the two series bench outputs.\n4. Connect oscilloscope earth clips to board GND only.\n5. Use dummy loads; no speakers until DC protection and warm-up tests pass.',20,185,1.2)
T.txt('External PSU assumption envelope: roughly +/-12.5 V valley to +/-20.6 V peak.\nFinal transformer and capacitors not fixed. Recalculate and measure before use.\nSchematic connected and ERC checked separately from electrical/model/thermal validation.\nThe original empty PCB is retained. Layout is for the user; no routing supplied.',20,243,1.1)
T.write('MOSFETAmp2.kicad_sch','MOSFETAmp2 stereo Class-AB')
(ROOT/'MOSFETAmp2.kicad_sym').write_text('(kicad_symbol_lib(version 20241209)(generator "kicad_symbol_editor")'+''.join(s for s,_,__ in LIB.values())+')')
(ROOT/'sym-lib-table').write_text('(sym_lib_table\n (version 7)\n (lib (name "MOSFETAmp2")(type "KiCad")(uri "${KIPRJMOD}/MOSFETAmp2.kicad_sym")(options "")(descr "Project-local conventional symbols, datasheet pin numbers")))')
(ROOT/'work/component_manifest.json').write_text(json.dumps({'channel':S.parts,'root':T.parts},indent=2))
print('Generated',len(S.parts),'symbols per channel; root',len(T.parts))

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
 def add(self,ref,kind,value,x,y,angle=0,mirror=False,fp='',mpn='',ds='',stock='',note='',nets=None):
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
def R(n,x,y,h=False):return S.add('R'+str(100+n),'R',Rvals[n],x,y,90 if h else 0,fp=FPP if n in [19,20,25,26] else FPR,stock=Rstock.get(n,''),mpn='MCKNP05SJ033KAA9'if n in [19,20]else('ROX2SJ10R'if n in [25,26]else'LR1F'+Rvals[n].split()[0].upper()),ds='https://www.te.com/en/product-1625890-6.html'if n in [25,26]else'',note='Noninductive flameproof metal oxide; purchase'if n in [25,26]else RNOTE.get(n,''))
def C(n,x,y,h=False):
 val={1:'220p C0G',2:'330p C0G',3:'100n / 63V',4:'100n FILM / 63V',5:'220u / 35V',6:'220u / 35V',7:'100n / 63V',8:'100n / 63V'}[n]
 return S.add('C'+str(100+n),'CP'if n in [5,6]else'C',val,x,y,90 if h else 0,fp=('MOSFETAmp2:C_Radial_Kemet_C315_P2.54'if n==2 else'Capacitor_SMD:C_0805_2012Metric')if n in [1,2]else('Capacitor_THT:CP_Radial_D8.0mm_P3.50mm'if n in [5,6]else FPC),stock=(198 if n==1 else '')if n in [1,2]else(366 if n in [5,6]else 406),mpn=('C315C331J5G5TA'if n==2 else'0805N221J500CT')if n in [1,2]else('35ZLH220MEFC8X11.5'if n in [5,6]else'R82DC3100DQ50J'),ds='https://yageogroup.com/content/datasheet/asset/file/KEM_C1049_GOLDMAX_C0G'if n==2 else'')
def Q(n,x,y,mirror=False):
 pnp=n in [1,2,5,7,10,14,17];bd=n in [6,8,9,10];mos=n in [11,12]
 val=('IRF540N'if n==11 else'IRF9540N')if mos else(('BD140'if pnp else'BD139')if bd else('BC556'if pnp else'BC546'))
 kind='MOS_'+('N'if n==11 else'P')if mos else'Q_'+('P'if pnp else'N')+'_'+('ECB'if bd else'CBE')
 stock={ 'IRF540N':'','IRF9540N':257,'BD139':148,'BD140':149,'BC556':462,'BC546':254}[val]
 ds='https://www.infineon.com/assets/row/public/documents/24/49/infineon-'+val.lower()+'-datasheet-en.pdf'if mos else('https://www.st.com/resource/en/datasheet/bd135.pdf'if bd else('https://www.onsemi.com/pdf/datasheet/bc556bta-d.pdf'if pnp else'https://www.farnell.com/datasheets/2277528.pdf'))
 return S.add('Q'+str(100+n),kind,val,x,y,mirror=mirror,fp='Package_TO_SOT_THT:TO-220-3_Vertical'if mos else('Package_TO_SOT_THT:TO-126-3_Vertical'if bd else'Package_TO_SOT_THT:TO-92_Inline'),mpn=val+'PbF'if mos else val,ds=ds,stock=stock,note='INSULATE live drain tab'if mos else('Clamp to output heatsink; insulate collector tab'if n==8 else('Select matched VBE and hFE; thermal bond'if n in [1,2]else('Bias offset current sink; PCB, near D109/D112'if n==16 else('LED reference feed; PCB'if n==17 else'')))))
def D(n,x,y,a=0):
 if n==13:return S.add('D113','LED','LED RED',x,y,a,fp='LED_SMD:LED_0805_2012Metric',mpn='KP-2012EC',ds='https://www.farnell.com/datasheets/2628136.pdf',stock=640,note='Bias offset reference, about 1 mA. Stocked Kingbright KP-2012EC, 2012 metric SMD; verify cathode mark against pad 1.')
 v='BZX85C10'if n in [10,11]else('BAT46'if n==8 else'1N4148')
 return S.add('D'+str(100+n),'DZ'if n in [10,11]else('DS'if n==8 else'D'),v,x,y,a,fp=('Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal'if n in [10,11]else FPD),mpn='BAT46-TR'if n==8 else v,ds='https://www.vishay.com/docs/85662/bat46.pdf'if n==8 else'',stock=251 if n in [10,11]else(138 if n not in [8] else''),note='Driver VBE tracking; PCB beside Q109/Q110'if n in [9,12]else'')
def connect(r,n,*points):S.wire(S.p(r,n),*points)
def label(n,p):S.label(n,p)
def w(*p):S.wire(*p)
def dot(p):S.dot(p)
# Input and differential stage
S.txt('INPUT / DIFFERENTIAL PAIR + MIRROR',15,6,1.5)
R(1,30,60,True);R(2,45,75);C(1,60,75);R(3,30,95,True);R(4,45,115)
Q(1,80,95);Q(2,130,95);Q(3,80,130,True);Q(4,130,130);Q(5,100,45);R(5,82.54,80);R(6,132.54,80);R(7,102.54,30)
D(2,25,25,270);D(1,25,38,270);R(8,25,50)
S.hlabel('IN',(15,60),180,'input');w((15,60),S.p('R101',2));w(S.p('R101',1),(45,60),(60,60),(120,60),(120,95),S.p('Q102',2));dot((45,60));dot((60,60))
connect('R102',1,(45,60));S.term('R102',2,'GND',(45,90));connect('C101',1,(60,60));S.term('C101',2,'GND',(60,90));label('B1',(60,60))
S.term('R103',2,'OUT',(15,95));w(S.p('R103',1),(45,95),S.p('Q101',2));dot((45,95));connect('R104',1,(45,95));S.term('R104',2,'GND',(45,125));label('FB',(55,95))
w(S.p('Q101',3),S.p('R105',2));w(S.p('Q102',3),S.p('R106',2));w(S.p('R105',1),(82.54,70),(102.54,70),(132.54,70),S.p('R106',1));connect('Q105',1,(102.54,70));dot((102.54,70))
w(S.p('Q101',1),(82.54,110),(77.46,110),S.p('Q103',1));w(S.p('Q102',1),(132.54,110),S.p('Q104',1));dot((132.54,110));w((132.54,110),(145,110));label('C2N',(145,110))
w(S.p('Q103',2),(100,130),S.p('Q104',2));w((77.46,110),(77.46,115),(100,115),(100,130));dot((77.46,110));dot((100,130))
w(S.p('Q103',3),(77.46,145),(132.54,145),S.p('Q104',3));label('VN',(105,145))
w(S.p('R107',2),S.p('Q105',3));S.term('R107',1,'VP',(102.54,15));w(S.p('D102',1),S.p('D101',2));S.term('D102',2,'VP',(25,15));w(S.p('D101',1),(25,44),S.p('R108',1));S.term('R108',2,'VN',(25,56));w((25,44),(90,44),(90,45),S.p('Q105',2));dot((25,44));label('TREF',(65,44))
D(5,30,162);D(6,30,174,180)
w(S.p('D105',1),(20,162),(20,174),S.p('D106',2));w(S.p('D105',2),(40,162),(40,174),S.p('D106',1))
w((13,168),(20,168));dot((20,168));label('FB',(13,168));w((40,168),(45,168));dot((40,168));label('B1',(45,168))
S.txt('Q101/Q102: match at 1 mA; bond flat faces.\nR101 + R102: input about 23k.\nGain = 11 from B1; about 10.52 at IN.\nD105/D106 limit differential overload.',65,160,.95)
# VAS and source load
S.txt('BUFFERED VAS / DOMINANT POLE',165,6,1.5)
Q(15,175,95);Q(6,205,120);R(9,207.54,145);R(10,185,145);C(2,197,65,True);Q(7,245,45);R(11,247.54,30);D(7,174,78,180);D(8,191,78,180)
S.term('Q115',1,'VP',(177.54,50));S.term('Q115',2,'C2N',(160,95));w(S.p('Q115',3),(177.54,120),(185,120),S.p('Q106',3));dot((185,120));connect('R110',1,(185,120));S.term('R110',2,'VN',(185,160));w(S.p('Q106',1),S.p('R109',1));S.term('R109',2,'VN',(207.54,160));S.term('Q106',2,'BN',(207.54,85))
S.term('C102',2,'C2N',(185,65));S.term('C102',1,'BN',(211,65));S.term('D107',2,'C2N',(163,78));w(S.p('D107',1),(182,78),S.p('D108',2));S.term('D108',1,'BN',(201,78))
w(S.p('R111',2),S.p('Q107',3));S.term('R111',1,'VP',(247.54,15));S.term('Q107',2,'TREF',(229,45));S.term('Q107',1,'BP',(247.54,65))
S.txt('C102 = 330p C0G, 50V, radial 2.54mm.\nD107 + D108 prevent VAS saturation.\nNo rail bootstrapping or regulators.\nVAS/load current about 6 mA.',170,166,.95)
# Driver/output main current path
S.txt('DRIVERS / ONE COMPLEMENTARY PAIR',270,6,1.5)
Q(9,275,85);Q(10,275,175);Q(11,332,100);Q(12,332,160);R(17,300,100,True);R(18,300,160,True);R(19,334.54,118);R(20,334.54,142);R(15,285,120);R(16,285,142)
S.term('Q109',2,'VP',(277.54,55));S.term('Q110',2,'VN',(277.54,195));S.term('Q111',2,'VP',(334.54,55));S.term('Q112',2,'VN',(334.54,195));S.term('Q109',3,'BP',(264,85));S.term('Q110',3,'BN',(264,175))
w(S.p('Q109',1),(277.54,100),(285,100),S.p('R117',2));dot((285,100));w(S.p('R117',1),S.p('Q111',1));label('GN',(315,100));connect('R115',1,(285,100));S.term('R115',2,'OUT',(285,130))
w(S.p('Q110',1),(277.54,160),(285,160),S.p('R118',2));dot((285,160));w(S.p('R118',1),S.p('Q112',1));label('GP',(315,160));connect('R116',2,(285,160));S.term('R116',1,'OUT',(285,130))
w(S.p('Q111',3),(334.54,110),S.p('R119',1));label('SN',(334.54,110));w(S.p('R119',2),(334.54,130),S.p('R120',1));dot((334.54,130));w(S.p('R120',2),(334.54,150),S.p('Q112',3));label('SP',(334.54,150))
S.add('L101','L','0.7uH AIR / 3A',366,130,fp='MOSFETAmp2:L_Air_0u7_12T',note='12 turns 1mm enamelled copper on 8mm mandrel; measure L and DCR')
R(26,366,145,True);R(25,350,170);C(4,350,185)
w((334.54,130),(350,130),S.p('L101',1));dot((350,130));label('OUT',(344,130));w(S.p('L101',2),(385,130),(396,130));S.hlabel('SPK',(396,130),0,'output')
connect('R126',2,(350,145),(350,130));connect('R126',1,(385,145),(385,130));dot((385,130));connect('R125',1,(350,130));w(S.p('R125',2),S.p('C104',1));S.term('C104',2,'GND',(350,197))
for n,node,x,y in [(1,'SN',345,107),(2,'OUT',372,111),(3,'SP',345,154),(4,'VP',375,35),(5,'VN',395,35)]:
 rr='TP'+str(100+n);S.add(rr,'TP',node,x,y,fp='TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm');S.term(rr,1,node,(x,y+8))
S.txt('Measure 16.5 mV per 0R33 for 50 mA.\nOUT is feedback sense BEFORE the coil.\nMOSFET drain tabs are live: INSULATE.\n8 ohm prototype; no short-circuit protection.',275,202,.95)
# Limiter and gate clamps
S.txt('OPERATING LIMITS',15,191,1.3)
S.txt('8 ohm prototype; current-limited bench PSU first.\nNo output short-circuit protection is fitted.\nExternal DC speaker protection is required.\nGate clamps protect VGS; they do not establish SOA.\nRead the bias and warm-up procedure before power-up.',20,210,1.1)
for n,x,gn,sn,d in [(21,285,'GN','SN',10),(22,325,'SP','GP',11)]:
 R(n,x,232);D(d,x+15,232,90)
 for rr in ['R'+str(100+n),'D'+str(100+d)]:
  p1=S.p(rr,1);p2=S.p(rr,2);S.term(rr,1,gn,(p1[0],220));S.term(rr,2,sn,(p2[0],245))
S.txt('Gate-source Zeners\nN: K to gate, A to source\nP: K to source, A to gate',350,225,.95)
# Thermal bias spreader (Rev 0.2, docs/BIAS_STUDY.md variant B)
S.txt('THERMAL BIAS / PROGRAMMED OFFSET',165,191,1.2)
D(9,237.54,203,270);D(12,237.54,213,270);Q(8,235,228);R(12,222,226);R(13,222,239);Q(16,200,242);R(14,202.54,254)
S.add('RV101','RV','200R MULTITURN',202.54,266,fp='Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical',mpn='3296W-1-201LF',ds='https://www.bourns.com/docs/product-datasheets/3296.pdf',note='Wiper 2 tied to 3. Maximum 1-to-(2+3) resistance = minimum bias. Value sized to R114: 200R up to 1k3, 500R up to 3k3, 2k above. Stock generic fit unverified.')
D(13,185,252,270);Q(17,182.46,230);R(27,185,213);C(3,255,237)
S.term('D109',2,'BP',(237.54,195));w(S.p('D109',1),S.p('D112',2))
w(S.p('D112',1),(237.54,219),S.p('Q108',2));w((237.54,219),(222,219),S.p('R112',1));dot((237.54,219))
w(S.p('R112',2),(222,232),S.p('R113',1));w((222,232),(229.92,232),S.p('Q108',3));dot((222,232));w(S.p('Q116',1),(202.54,232),(222,232))
w(S.p('Q108',1),(237.54,270),(222,270),S.p('R113',2));label('BN',(228,270))
w(S.p('Q116',3),S.p('R114',1));w(S.p('R114',2),S.p('RV101',1))
w(S.p('RV101',2),(207.62,275),(202.54,275),S.p('RV101',3));dot((202.54,275));w((202.54,275),(185,275),S.p('D113',1));label('VN',(190,275))
w(S.p('Q116',2),(185,242),S.p('D113',2));w(S.p('Q117',1),(185,242));dot((185,242));label('BREF',(186,245))
w(S.p('R127',2),S.p('Q117',3));S.term('R127',1,'VP',(185,205));S.term('Q117',2,'TREF',(170,230))
S.term('C103',1,'BP',(255,225));S.term('C103',2,'BN',(255,250))
S.add('J101','J2','BIAS SHORT - FIT FIRST',165,197,fp='Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical',mpn='MC34629',stock=126)
S.term('J101',1,'BP',(150,197));S.term('J101',2,'BN',(150,199.54))
S.txt('Q108 on heatsink beside MOSFETs; ratio fixed by\nR112/R113 (R113 = slope select).\nD109/D112 track the drivers on the PCB.\nOffset = 3k9 x (V(D113) - VBE)/(R114 + RV101).\nR114 unfitted = zero offset = minimum bias.\nRV101 maximum resistance = minimum bias.',242,255,.9)
# Supply labels and local decoupling on separate root-level channel sheet ports
S.hlabel('VP',(396,55),0);S.label('VP',(396,55));S.hlabel('VN',(396,215),0);S.label('VN',(396,215))
for n,x,node in [(5,370,'VP'),(6,390,'VN'),(7,370,'VP'),(8,390,'VN')]:
 y=78 if n in [5,6]else 103;C(n,x,y)
 if n in [5,7]:S.term('C'+str(100+n),1,node,(x,y-7));S.term('C'+str(100+n),2,'GND',(x,y+7))
 else:S.term('C'+str(100+n),1,'GND',(x,y-7));S.term('C'+str(100+n),2,node,(x,y+7))
S.txt('Local bypass:\n220u / 35V each rail\n100n / 63V each rail\nC106 positive to GND',362,156,.9)
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

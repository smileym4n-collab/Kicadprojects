#!/usr/bin/env python3
"""Build the single-channel review schematic. No PCB operations."""
from pathlib import Path
import re, json, math, uuid, copy

ROOT = Path(__file__).resolve().parents[1]
LIB = Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols')
U = 1.27
ROOT_UUID = '1384b3cb-5bd6-4ffd-905a-aef8d0e311a3'
def uid(): return str(uuid.uuid4())
def q(s): return json.dumps(str(s), ensure_ascii=False)
def n(v): return f'{v:.6f}'.rstrip('0').rstrip('.') or '0'
def parse(s):
    ts=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',s); i=0
    def walk():
        nonlocal i
        if ts[i]=='(':
            i+=1;a=[]
            while ts[i]!=')':a.append(walk())
            i+=1;return a
        t=ts[i];i+=1
        return json.loads(t) if t.startswith('"') else Atom(t)
    return walk()
class Atom(str): pass
def dump(a):
    if isinstance(a,list): return '('+' '.join(dump(x) for x in a)+')'
    return str(a) if isinstance(a,Atom) else q(a)
def children(a,k): return [x for x in a if isinstance(x,list) and x and x[0]==k]
def child(a,k): return next(iter(children(a,k)),None)
cache={}
def get(lib,name):
    if lib not in cache:cache[lib]=parse((LIB/(lib+'.kicad_sym')).read_text())
    sym=copy.deepcopy(next(s for s in children(cache[lib],'symbol') if s[1]==name))
    ext=child(sym,'extends')
    if ext:
        base=get(lib,ext[1]);sym.remove(ext)
        for x in base[2:]:
            if isinstance(x,list) and x[0]=='symbol':sym.append(x)
            elif isinstance(x,list) and x[0] not in [v[0] for v in sym[2:] if isinstance(v,list)]:sym.append(x)
    return sym
defs={};custom={};items=[];components={};wires=[];labels=[]
def rename(sym,new,old=None):
    old=old or sym[1];sym[1]=new
    for s in children(sym,'symbol'):s[1]=s[1].replace(old,new)
    return sym
def make_trans(name,base,pnp=False,ds='',fp='',description=''):
    s=rename(get('Transistor_BJT',base),name)
    # PNP emitters face the positive rail; pin numbers retain manufacturer mapping.
    if pnp:
        def flip(a):
            if not isinstance(a,list):return
            if a and a[0] in ['xy','at','start','end','center'] and len(a)>=3:
                a[2]=Atom(n(-float(a[2])))
                if a[0]=='at' and len(a)>3:a[3]=Atom(n((-float(a[3]))%360))
            for x in a:flip(x)
        for g in children(s,'symbol'):flip(g)
    for p in children(s,'property'):
        if p[1]=='Value':p[2]=name
        if p[1]=='Datasheet':p[2]=ds
        if p[1]=='Footprint':p[2]=fp
        if p[1]=='Description':p[2]=description
    custom[name]=s
    defs['DarlingtonAmp:'+name]=copy.deepcopy(s);defs['DarlingtonAmp:'+name][1]='DarlingtonAmp:'+name

DS={
'KSC1845':'https://www.onsemi.com/download/data-sheet/pdf/ksc1845-d.pdf',
'KSA992':'https://www.onsemi.com/download/data-sheet/pdf/ksa992-d.pdf',
'2SC4793':'https://www.mouser.com/datasheet/2/408/toshiba_2SC4793-587292.pdf',
'2SA1837':'https://media.digikey.com/pdf/Data%20Sheets/Toshiba%20PDFs/2SA1837.pdf',
'BD139':'https://www.onsemi.com/download/data-sheet/pdf/bd139-d.pdf',
'2SD2390':'https://www.semicon.sanken-ele.co.jp/sk_content/2sd2390_ds_jp.pdf',
'2SB1560':'https://www.semicon.sanken-ele.co.jp/sk_content/2sb1560_ds_jp.pdf'}
for name,base,pnp,fp,desc in [
('KSC1845','Q_NPN_ECB',False,'','120V NPN, pins 1 E / 2 C / 3 B; leadform TBC before footprint'),
('KSA992','Q_PNP_ECB',True,'','120V PNP, pins 1 E / 2 C / 3 B; leadform TBC before footprint'),
('2SC4793','Q_NPN_BCE',False,'Package_TO_SOT_THT:TO-220-3_Vertical','230V NPN, Toshiba 2-10R1A, pins 1 B / 2 C / 3 E'),
('2SA1837','Q_PNP_BCE',True,'Package_TO_SOT_THT:TO-220-3_Vertical','230V PNP, Toshiba 2-10R1A, pins 1 B / 2 C / 3 E'),
('BD139','Q_NPN_ECB',False,'Package_TO_SOT_THT:TO-126-3_Vertical','onsemi BD13916STU, 80V NPN; 1 E / 2 C / 3 B. Heatsink sensor'),
('2SD2390','Q_NPN_Darlington_BCE',False,'Package_TO_SOT_THT:TO-3P-3_Vertical','Sanken 150V 10A NPN Darlington, 1 B / 2 C / 3 E, internal 70R'),
('2SB1560','Q_PNP_Darlington_BCE',True,'Package_TO_SOT_THT:TO-3P-3_Vertical','Sanken 150V 10A PNP Darlington, 1 B / 2 C / 3 E, internal 70R')]:
    make_trans(name,base,pnp,DS[name],fp,desc)

def prop(key,value,x,y,hide=False,align='left',size=1.05,angle=0):
    return f'(property {q(key)} {q(value)} (at {n(x)} {n(y)} {angle}) (effects (font (size {size} {size}))'+(f' (justify {align})' if align!='center' else '')+(' (hide yes)' if hide else '')+'))'
def sym(libid,ref,value,x,y,angle=0,mirror=None,fp=None,dnp=False,role='',pos=None):
    if libid not in defs:
        lib,name=libid.split(':');defs[libid]=get(lib,name);defs[libid][1]=libid
    d=defs[libid];X=x*U;Y=y*U;u=uid()
    props={p[1]:p[2] for p in children(d,'property')}
    if fp is None:fp=props.get('Footprint','')
    if pos is None:
        if ref.startswith('Q'):pos=(x+(11 if mirror=='y' else 5),y-1.7,'left')
        elif angle==90:pos=(x,y-4.5,'center')
        else:pos=(x+3,y-1.3,'left')
    px,py,al=pos
    if mirror=='y' and al=='left':al='right'
    ps=prop('Reference',ref,px*U,py*U,ref.startswith('#'),al,angle=angle)
    ps+=prop('Value',value,px*U,(py+2)*U,ref.startswith('#FLG') or ref.startswith('TP'),al,angle=angle)
    ps+=prop('Footprint',fp,X,Y,True)+prop('Datasheet',props.get('Datasheet',''),X,Y,True)
    if role:ps+=prop('Engineering',role,X,Y,True)
    if ref=='Q9':ps+=prop('Manufacturer','onsemi BD13916STU',X,Y,True)
    items.append(f'(symbol (lib_id {q(libid)}) (at {n(X)} {n(Y)} {angle}) (unit 1) '+(f'(mirror {mirror}) ' if mirror else '')+f'(in_bom {"no" if ref.startswith("#") else "yes"}) (on_board {"no" if ref.startswith("#") else "yes"}) (dnp {"yes" if dnp else "no"}) (uuid {u}) {ps} (instances (project "DarlingtonAmp" (path "/{ROOT_UUID}" (reference {q(ref)}) (unit 1)))))')
    pins={};a=math.radians(angle)
    for g in children(d,'symbol'):
        for p in children(g,'pin'):
            at=child(p,'at');xx,yy=float(at[1]),float(at[2])
            if mirror=='x':yy=-yy
            if mirror=='y':xx=-xx
            dx=xx*math.cos(a)-yy*math.sin(a);dy=-xx*math.sin(a)-yy*math.cos(a)
            pins[child(p,'number')[1]]=(round(x+dx/U,6),round(y+dy/U,6))
    components[ref]={'lib':libid,'value':value,'pins':pins,'fp':fp,'role':role,'dnp':dnp}
    return pins
def wire(*pts):
    for p1,p2 in zip(pts,pts[1:]):
        if p1==p2:continue
        assert p1[0]==p2[0] or p1[1]==p2[1],(p1,p2)
        wires.append((p1,p2))
def label(name,p,angle=0):
    labels.append((name,p))
    items.append(f'(label {q(name)} (at {n(p[0]*U)} {n(p[1]*U)} {angle}) (effects (font (size 1.05 1.05)) (justify left bottom)) (uuid {uid()}))')
def text(s,x,y,size=1.15):
    items.append(f'(text {q(s)} (at {n(x*U)} {n(y*U)} 0) (effects (font (size {size} {size})) (justify left top)) (uuid {uid()}))')
g=0
def ground(p):
    global g
    g+=1;sym('power:GND',f'#PWR{g:03}','GND',*p)
def netpin(ref,pin,net,dx=0,dy=0):
    p=components[ref]['pins'][str(pin)];end=(p[0]+dx,p[1]+dy);wire(p,end);label(net,end)
def R(ref,val,x,y,angle=0,role='',fp='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal',dnp=False):
    return sym('Device:R',ref,val,x,y,angle,fp=fp,role=role,dnp=dnp)
def C(ref,val,x,y,angle=0,role='',fp='',dnp=False,polar=False):
    return sym('Device:C_Polarized' if polar else 'Device:C',ref,val,x,y,angle,fp=fp,role=role,dnp=dnp)
def Q(ref,val,x,y,mirror=None,role=''):
    return sym('DarlingtonAmp:'+val,ref,val,x,y,mirror=mirror,role=role)
def TP(ref,net,x,y):
    p=sym('Connector:TestPoint',ref,net,x,y,fp='TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm',pos=(x+2,y-5,'left'))
    return p['1']

# One A3 sheet, signal flow left to right; supplies above and below.
text('ONE MONO CHANNEL - DISCRETE CLASS AB / +/-35 V',13,12,2.0)
text('REV A: FIRST SCHEMATIC FOR ENGINEERING REVIEW. 8 ohm target; 4 ohm capability needs SOA/thermal qualification.',13,17)
for t,x,y in [('INPUT',14,28),('DIFFERENTIAL / MIRROR',70,28),('VAS / CURRENT SINK',137,28),('BIAS SPREADER',183,28),('DARLINGTON OUTPUT',241,28),('OUTPUT NETWORK',281,28)]:text(t,x,y,1.35)

# Input: C1 optional film coupling, R1 default DC link, R2 defines input impedance.
j=sym('Connector_Generic:Conn_01x02','J1','INPUT / SIGNAL RETURN',20,75,mirror='y',fp='',pos=(14,64,'left'))
wire(j['1'],(31,75));label('INPUT',(26,75))
c=C('C1','2u2 / 63V FILM DNP',40,75,90,dnp=True,fp='Capacitor_THT:C_Rect_L18.0mm_W6.0mm_P15.00mm_FKS3_FKP3',role='Optional coupling; populate C1 only after removing R1; exact film MPN and body TBC')
wire((31,75),c['1']);wire(c['2'],(51,75))
r=R('R1','0R / DC LINK',40,65,90,role='Fitted by default; remove to use C1')
wire((31,75),(31,65),r['1']);wire(r['2'],(51,65),(51,75))
r=R('R2','22k / 1%',51,91,role='Input DC return; thin film preferred')
wire((51,75),r['1']);wire(r['2'],(51,106))
wire(j['2'],(26,77),(26,106),(51,106));ground((51,106))
r=R('R3','100R',62,75,90,role='Input base stopper')
wire((51,75),r['1'])

# Q1 collector drives PNP VAS; Q2 is the feedback leg of the mirror.
q1=Q('Q1','KSC1845',78,75,role='Non-inverting input; match VBE/hFE to Q2 at ~0.9mA')
q2=Q('Q2','KSC1845',107,75,mirror='y',role='Inverting feedback input')
wire(r['2'],q1['3'])
q3=Q('Q3','KSA992',78,50,role='Mirror output')
q4=Q('Q4','KSA992',107,50,mirror='y',role='Diode-connected mirror reference; match Q3/Q4')
r=R('R4','100R',80,41);wire((80,35),r['1']);wire(r['2'],q3['1'])
r=R('R5','100R',105,41);wire((105,35),r['1']);wire(r['2'],q4['1'])
wire((80,35),(105,35));label('+35V',(80,35))
wire(q3['2'],q1['2']);wire(q4['2'],q2['2'])
wire(q3['3'],(72,50),(72,60),(115,60),(115,50),q4['3'])
wire((105,55),(105,60));label('MIRROR_REF',(115,60))
r=R('R6','100R',80,88);wire(q1['1'],r['1']);wire(r['2'],(80,97))
r=R('R7','100R',105,88);wire(q2['1'],r['1']);wire(r['2'],(105,97))
wire((80,97),(93,97),(105,97))
q5=Q('Q5','KSC1845',91,110,role='Tail sink ~1.8mA; ~60mW at idle')
wire((93,97),q5['2']);netpin('Q5',3,'IREF',-4,0)
r=R('R8','330R / TUNE',93,123,role='Sets ~1.8mA tail; verify current on bench')
wire(q5['1'],r['1']);wire(r['2'],(93,134));label('-35V',(93,134))

# Feedback below the pair: gain 20.13; bipolar capacitor avoids ambiguous DC polarity.
r=R('R10','22k',114,117,90,role='Thin film 1%; feedback from AMP_OUT before L1')
wire(r['1'],(108,117),(108,104),(116,104),(116,75),q2['3']);label('NFB',(116,104))
wire(r['2'],(132,117));label('AMP_OUT',(132,117))
r=R('R11','1k15',108,141,role='Thin film 1%; audio gain = 1 + 22k/1k15 = 20.13')
wire((108,104),r['1'])
c=C('C2','220u / 50V BIPOLAR',108,156,role='DC gain unity; audio highpass corner ~0.63Hz; exact package TBC')
wire(r['2'],c['1']);wire(c['2'],(108,166));ground((108,166))
c=C('C3','10p C0G / 100V DNP',114,127,90,dnp=True,fp='Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm',role='Optional feedback lead compensation; TUNE only after stability testing')
wire(c['1'],(108,127),(108,117));wire(c['2'],(132,127),(132,117))
text('DC input link fitted. Zin ~22k.\nAudio gain 20.13 (26.1dB); DC gain 1.\nC2 is bipolar: no fixed DC polarity.\nQ1/Q2: match and thermally pair.',13,117)

# PNP VAS and NPN current sink; neither is a separate output driver.
q8=Q('Q8','2SA1837',153,58,role='PNP common-emitter VAS ~6mA; ~0.2W idle / <0.45W excursion estimate')
r=R('R12','100R',155,43);wire((155,35),r['1']);wire(r['2'],q8['3']);label('+35V',(155,35))
wire((80,67),(137,67),(137,58),q8['1']);label('VAS_IN',(137,67))
wire(q8['2'],(155,76),(237,76));label('DRIVE_N',(176,76))
c=C('C4','100p C0G / 100V',139,86,90,fp='Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm',role='Dominant Miller compensation; TUNE 68-100pF initial range')
wire(c['1'],(129,86),(129,67));wire(c['2'],(155,86),(155,76))
q10=Q('Q10','2SC4793',153,120,role='~6mA VAS current sink; ~0.2W idle / <0.45W at excursion')
wire(q10['2'],(155,112),(237,112));label('DRIVE_P',(176,112));netpin('Q10',1,'IREF',-4,0)
r=R('R13','100R / TUNE',155,128,role='Sets ~6mA VAS/sink current; verify 5-7mA bench')
wire(q10['3'],r['1']);wire(r['2'],(155,134));label('-35V',(155,134))
text('Direct Darlington drive; no driver pair.\nC4 TUNE: stability/load test required.\n~6mA VAS -> SR ceiling ~60V/us.\nDC operating point / clipping TBC.',136,141)

# Fail-low adjustable BD139 multiplier: fixed C-B, fixed B-E, adjustable shunt B-E.
q9=Q('Q9','BD139',213,95,role='Thermally couple to output heatsink; insulate collector tab. Manufacturer onsemi')
wire(q9['2'],(215,76));wire(q9['1'],(215,112))
r=R('R14','2k2',194,85,role='Fixed collector-base multiplier resistor')
wire(r['1'],(194,76));wire(r['2'],(194,95),q9['3'])
r=R('R15','2k2',194,103,role='Permanent base-emitter path; defines low bias with shunt absent')
wire((194,95),r['1']);wire(r['2'],(194,112))
r=R('R16','680R',181,99,role='Limits maximum bias when RV1 is at zero resistance')
wire((194,95),(181,95),r['1'])
rv=sym('Device:R_Potentiometer','RV1','5k / 25 TURN',181,108,fp='Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical',role='Bourns 3296W-1-502LF; wiper 2 tied to end 3; open wiper -> full 5k -> minimum bias',pos=(169,106,'left'))
wire(r['2'],rv['1']);wire(rv['3'],(181,112),(194,112),(215,112))
wire(rv['2'],(186,108),(186,112))
text('RV1: preset maximum resistance 1-3\n(wiper 2 tied to 3) for minimum bias.\nLost wiper -> LOW bias; track-open\nshunt -> lower still. R14/R15 failure\nis not made fail-safe.\nVspread ~1.6-3.4V + base-current term;\nactual Iq range / tracking TBC.',177,142)

# Exactly one Sanken complementary Darlington pair, each with 33R / 0R22.
qn=Q('Q11','2SD2390',255,76,role='QOUT_N; internal Darlington + 70R; external base stopper close to base')
qp=Q('Q12','2SB1560',255,112,role='QOUT_P; internal Darlington + 70R; external base stopper close to base')
r=R('R17','33R',244,76,90);wire((237,76),r['1']);wire(r['2'],qn['1'])
r=R('R18','33R',244,112,90);wire((237,112),r['1']);wire(r['2'],qp['1'])
wire(qn['2'],(257,35));label('+35V',(257,35))
wire(qp['2'],(257,134));label('-35V',(257,134))
r=R('R19','0R22 / 5W',257,88,fp='',role='Low-inductance power resistor; exact MPN/package TBC')
wire(qn['3'],r['1']);wire(r['2'],(257,96))
r=R('R20','0R22 / 5W',257,101,fp='',role='Low-inductance power resistor; exact MPN/package TBC')
wire(qp['3'],r['2']);wire(r['1'],(257,96))
wire((257,96),(280,96));label('AMP_OUT',(268,96))
pn=TP('TP1','BIAS_TEST_N',268,81);wire(pn,(268,81),(257,81));label('BIAS_TEST_N',(268,81))
pp=TP('TP2','BIAS_TEST_P',268,107);wire(pp,(268,107),(257,107));label('BIAS_TEST_P',(268,107))
po=TP('TP3','AMP_OUT',274,92);wire(po,(274,96))
text('BIAS TARGET: 80-100mA per device.\nN: TP1(+) to TP3(-): 17.6-22mV.\nP: TP3(+) to TP2(-): 17.6-22mV.\nBD139 on main heatsink; check warm drift.\nOutputs idle ~2.8-3.5W EACH.\nTO-3P: 1=B / 2=C / 3=E; tabs live.\n4 ohm SOA / cooling NOT qualified.',240,145)

# Zobel and output L//R, feedback is taken before inductor.
c=C('C5','100n / 100V FILM',282,109,fp='Capacitor_THT:C_Rect_L10.0mm_W4.0mm_P7.50mm_FKS3_FKP3',role='Zobel film capacitor; exact package TBC')
wire((280,96),(282,96),c['1'])
r=R('R21','10R / 2W',282,123,fp='',role='Zobel resistor, low inductance; pulse/thermal load TBC')
wire(c['2'],r['1']);wire(r['2'],(282,134));ground((282,134))
lp=sym('Device:L','L1','0.82u / >=8A TBC',299,96,90,fp='',role='Output stability air-core inductor; low DCR, exact coil footprint TBC',pos=(299,88,'center'))
wire((282,96),lp['1']);wire(lp['2'],(311,96))
r=R('R22','10R / 2W',299,108,90,fp='',role='Output inductor damping resistor, low inductance')
wire(r['1'],(290,108),(290,96));wire(r['2'],(309,108),(309,96))
j=sym('Connector_Generic:Conn_01x02','J3','SPEAKER',315,96,fp='',pos=(306,120,'left'))
wire((311,96),j['1']);label('SPK_OUT',(306,96))
wire(j['2'],(313,98),(313,134));ground((313,134))
ps=TP('TP4','SPK_OUT',310,88);wire(ps,(310,96))
text('Feedback / Zobel at AMP_OUT.\nSpeaker connector after L1.\nSpeaker return / Zobel return\nroute separately to local star.\nNominal ~30-31Vpk -> 56-60W/8R;\nrail sag / clipping must be measured.',281,145)

# Local supply connector and decoupling only. No PSU circuitry.
text('EXTERNAL POWER / LOCAL DECOUPLING',13,177,1.4)
j=sym('Connector_Generic:Conn_01x03','J2','EXTERNAL +/-35V',23,191,mirror='y',fp='',pos=(13,181,'left'))
wire(j['1'],(42,189),(100,189));label('+35V',(34,189))
wire(j['2'],(33,191),(33,204),(100,204));ground((33,204))
wire(j['3'],(30,193),(30,219),(100,219));label('-35V',(34,219))
fp_el='Capacitor_THT:CP_Radial_D10.0mm_P5.00mm'
c=C('C6','220u / 63V',48,197,polar=True,fp=fp_el,role='Positive rail local electrolytic; exact MPN/package TBC')
wire((48,189),c['1']);wire(c['2'],(48,204))
c=C('C7','100n / 100V',76,197,fp='Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm',role='Rail HF bypass close to Q11 collector; X7R acceptable')
wire((76,189),c['1']);wire(c['2'],(76,204))
c=C('C8','220u / 63V',48,211,polar=True,fp=fp_el,role='Negative rail local electrolytic: positive terminal to GND')
wire((48,204),c['1']);wire(c['2'],(48,219))
c=C('C9','100n / 100V',76,211,fp='Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm',role='Rail HF bypass close to Q12 collector')
wire((76,204),c['1']);wire(c['2'],(76,219))
for ref,net,x,y in [('TP5','+35V',100,189),('TP6','GND',100,204),('TP7','-35V',100,219)]:
    TP(ref,net,x,y);label(net,(x,y))
for i,(x,y) in enumerate([(42,189),(42,204),(42,219)],1):
    sym('power:PWR_FLAG',f'#FLG{i:03}','PWR_FLAG',x,y)
text('One electrical GND net. Local star/reference at J2 pin 2.\nInput + feedback returns form quiet branches to that point.\nSpeaker, Zobel and decoupling returns use separate power paths.\nGeneric connector and passive footprints are TBC before layout.\nJ2/J3: select >=10A rated terminals; no series chosen yet.',13,225)

# Two diode-connected KSC1845 reference transistors, near the tail/sink devices.
text('TAIL / VAS CURRENT REFERENCE',123,177,1.4)
r=R('R9','68k / 0.5W',139,190,role='~1mA reference from full 70V rail span; ~70mW / >=100V working rating',fp='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal')
wire(r['1'],(139,182));label('+35V',(139,182))
q6=Q('Q6','KSC1845',137,203,role='Diode-connected reference; thermal proximity to Q5')
wire(r['2'],q6['2']);wire(q6['3'],(131,203),(131,198),(139,198))
label('IREF',(139,198));q7=Q('Q7','KSC1845',137,217,role='Diode-connected reference ~1.2V above -35V')
wire(q6['1'],q7['2']);wire(q7['3'],(131,217),(131,212),(139,212))
wire(q7['1'],(139,228));label('-35V',(139,228))
c=C('C10','100n / 50V',157,211,fp='Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm',role='Current-reference filtering')
wire(c['1'],(157,198),(139,198));wire(c['2'],(157,228),(139,228))
text('IREF ~-33.8V. Tail ~1.8mA; VAS ~6mA.\nR8/R13 TUNE: diode and VBE spread matter.\nQ1/Q2 collectors ~+33V, emitters ~-0.7V.\nQ5 ~60mW; front-end VCEO rating 120V.\nMedium-power Q8/Q10 rated 230V.',122,229)

text('REVIEW / TUNE BEFORE LAYOUT',186,177,1.4)
text('C4 Miller (100p start), C3 lead (DNP), R8/R13 current, RV1 bias.\nCheck square-wave response with 8R / 4R / capacitive loads.\nCheck offset, startup, clipping recovery and heatsink bias tracking.\nNo DC protection, current limiting or thermal protection in Rev A.\nAt +/-35V a single pair is NOT signed off for sustained 4R use.\nWorst resistive Class-B dissipation ~15.5W/device (8R),\n~31W/device (4R), plus bias and reactive-load stress.\nSmall-signal leadforms and all exact passive/connector packages TBC.\nBD139 symbol uses onsemi ECB pin map; verify any stocked ST part\nindependently (ST legacy internal schematic numbering conflicts).',186,184)

# Deduplicate and split wires at actual pin/label intersections; junctions at branches.
points=set(p for w in wires for p in w)
points.update(p for c in components.values() for p in c['pins'].values())
points.update(p for _,p in labels)
segs=set()
for a,b in wires:
    along=[p for p in points if (a[0]==b[0]==p[0] and min(a[1],b[1])<=p[1]<=max(a[1],b[1])) or (a[1]==b[1]==p[1] and min(a[0],b[0])<=p[0]<=max(a[0],b[0]))]
    along=sorted(along,key=lambda p:(p[0],p[1]))
    for p1,p2 in zip(along,along[1:]):segs.add((p1,p2))
degree={}
for a,b in sorted(segs):
    items.append(f'(wire (pts (xy {n(a[0]*U)} {n(a[1]*U)}) (xy {n(b[0]*U)} {n(b[1]*U)})) (stroke (width 0) (type default)) (uuid {uid()}))')
    for p in [a,b]:degree[p]=degree.get(p,0)+1
for p,d in degree.items():
    if d>=3:items.append(f'(junction (at {n(p[0]*U)} {n(p[1]*U)}) (diameter 0) (color 0 0 0 0) (uuid {uid()}))')

def compact_lower(a):
    if not isinstance(a,list):return
    if a and a[0] in ['at','xy'] and len(a)>=3 and float(a[2])>=177*U:
        a[2]=Atom(n(float(a[2])-15*U))
    for x in a:compact_lower(x)
items=[parse(s) for s in items]
for a in items:compact_lower(a)
items=[dump(s) for s in items]
sch='(kicad_sch (version 20260306) (generator "eeschema") (generator_version "10.0") '+f'(uuid {ROOT_UUID}) (paper "A3") (title_block (title "DarlingtonAmp - Mono Class AB") (date "2026-10-05") (rev "A - REVIEW") (comment 1 "Schematic only. Stability, bias and 4 ohm SOA require bench review."))\n'
sch+='(lib_symbols\n'+'\n'.join(dump(s) for s in defs.values())+')\n'+'\n'.join(items)+f'\n(sheet_instances (path "/" (page "1"))) (embedded_fonts no))\n'
(ROOT/'DarlingtonAmp.kicad_sch').write_text(sch)
(ROOT/'DarlingtonAmp.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor")\n'+'\n'.join(dump(s) for s in custom.values())+'\n)\n')
(ROOT/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "DarlingtonAmp") (type "KiCad") (uri "${KIPRJMOD}/DarlingtonAmp.kicad_sym") (options "") (descr "Manufacturer pin maps for mono Darlington amplifier")))\n')
(ROOT/'work/review/component-intent.json').write_text(json.dumps(components,indent=2))
print(f'Generated {len(components)} symbols, {len(segs)} wire segments, one mono sheet.')

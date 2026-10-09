from schlib import *
from collections import defaultdict
ROOT=Path(__file__).resolve().parent.parent
ROOTID='6d54ed2e-2ae2-4573-a8b1-3b10bc28f7a1'
U=2.54
fmt=lambda n:f'{n:.4f}'.rstrip('0').rstrip('.')
q=lambda s:json.dumps(str(s))
custom={}
def rawsym(name,body,ref='U',desc='',fp='',ds=''):
 s=parse(f'''(symbol {q(name)} (pin_names (offset 0.508)) (in_bom yes) (on_board yes)
 (property "Reference" {q(ref)} (at 0 10.16 0) (effects (font (size 1.27 1.27))))
 (property "Value" {q(name.split(':')[-1])} (at 0 7.62 0) (effects (font (size 1.27 1.27))))
 (property "Footprint" {q(fp)} (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
 (property "Datasheet" {q(ds)} (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
 (property "Description" {q(desc)} (at 0 0 0) (effects (font (size 1.27 1.27)) hide)) {body})''')
 custom[name]=s;return s
def pin(num,name,x,y,a,typ='passive'):
 return f'(pin {typ} line (at {x} {y} {a}) (length 2.54) (name {q(name)} (effects (font (size 1.016 1.016)))) (number {q(num)} (effects (font (size 1.016 1.016)))))'
def line(pts):return '(polyline (pts '+' '.join(f'(xy {x} {y})' for x,y in pts)+') (stroke (width 0) (type default)) (fill (type none)))'
body=''
for unit,nc,com,no in [(1,2,3,4),(2,7,6,5)]:
 body+=f'(symbol "G6K_5V_{unit}_1" '+pin(nc,'NC',-10.16,2.54,0)+pin(no,'NO',-10.16,-2.54,0)+pin(com,'COM',10.16,0,180)+line([(-7.62,2.54),(-2.54,2.54)])+line([(-7.62,-2.54),(-2.54,-2.54)])+line([(7.62,0),(2.54,0),(-2.54,2.54)])+')'
body+='(symbol "G6K_5V_3_1" '+pin(1,'+',0,7.62,270)+pin(8,'-',0,-7.62,90)+'(rectangle (start -2.54 5.08) (end 2.54 -5.08) (stroke (width 0) (type default)) (fill (type background)))'+line([(-2.54,-5.08),(2.54,5.08)])+')'
rawsym('InputSwitch:G6K_5V',body,'K','G6K-2P-Y DC5; coil 1+,8-; NC 2/7; COM 3/6; NO 4/5. Pin numbering preserved.', 'Relay_THT:Relay_DPDT_Omron_G6K-2P-Y','https://omronfs.omron.com/en_US/ecb/products/pdf/en-g6k.pdf')
rawsym('InputSwitch:R12P12S_P','''(symbol "R12P12S_P_1_1" (rectangle (start -10.16 7.62) (end 10.16 -7.62) (stroke (width 0) (type default)) (fill (type background)))'''+pin(1,'VIN+',-12.7,5.08,0,'power_in')+pin(2,'VIN-',-12.7,-5.08,0,'power_in')+pin(7,'VOUT+',12.7,5.08,180,'power_out')+pin(5,'VOUT-',12.7,-5.08,180,'power_out')+')','U','12V to isolated 12V, 1W, /P continuous short-circuit protection; NOT /X2','', 'https://recom-power.com/pdf/Econoline/RxxPxx.pdf')
rawsym('InputSwitch:R78E5','(symbol "R78E5_1_1" (rectangle (start -7.62 5.08) (end 7.62 -5.08) (stroke (width 0) (type default)) (fill (type background)))'+pin(1,'VIN',-10.16,0,0,'power_in')+pin(3,'5V',10.16,0,180,'power_out')+pin(2,'GND',0,-7.62,90,'power_in')+')','U','RECOM R-78E5.0-0.5 buck module; 7-28V input; 500mA','Converter_DCDC:Converter_DCDC_RECOM_R-78E-0.5_THT','https://recom-power.com/pdf/Innoline/R-78E-0.5.pdf')
# The optocoupler pin numbering is identical to the standard four-pin phototransistor symbol.
s=lib('Isolator:PC817');s[1]='InputSwitch:VO617A_3'
for sub in kids(s,'symbol'):sub[1]=sub[1].replace('PC817','VO617A_3')
for p in kids(s,'property'):
 if p[1]=='Value':p[2]='VO617A-3'
 if p[1]=='Datasheet':p[2]='https://www.vishay.com/docs/83430/vo617a.pdf'
 if p[1]=='Footprint':p[2]='Package_DIP:DIP-4_W7.62mm'
custom[s[1]]=s
class Sheet:
 def __init__(self,name,title,page):
  self.name=name;self.title=title;self.page=page;self.uuid=ROOTID if page==1 else str(uuid.uuid5(uuid.NAMESPACE_URL,'InputSwitch/'+name));self.sid=str(uuid.uuid5(uuid.NAMESPACE_URL,'sheet/'+name));self.items=[];self.libs={};self.pins={};self.libfor={};self.refs=[];self.wires=[];self.pts=defaultdict(int)
 def add(self,libname,ref,value,x,y,rot=0,unit=1,fp=None,ds=None,prop=None):
  s=copy.deepcopy(custom[libname] if libname in custom else lib(libname));self.libs[libname]=s
  x*=U;y*=U;a=math.radians(rot); key=(ref,unit);pinmap={}
  for sub in kids(s,'symbol'):
   parts=sub[1].rsplit('_',2)
   if len(parts)<3 or int(parts[-2]) not in [0,unit]:continue
   for p in kids(sub,'pin'):
    at=child(p,'at');px,py=map(float,at[1:3]);rx=px*math.cos(a)-py*math.sin(a);ry=px*math.sin(a)+py*math.cos(a)
    pinmap[str(val(p,'number'))]=(round(x+rx,4),round(y-ry,4))
  self.pins[key]=pinmap;self.libfor[key]=libname
  props={p[1]:p[2] for p in kids(s,'property')};fp=props.get('Footprint','') if fp is None else fp;ds=props.get('Datasheet','') if ds is None else ds
  # Labels above component for ICs/horizontal passives, right of vertical passives.
  if libname.startswith('Device:') and rot==0 and libname.split(':')[-1] in ['R','C','C_Polarized','Fuse']:
   rx,ry=x+3.81,y-1.27;vx,vy=x+3.81,y+1.27;justify='(justify left)'
  else:
   miny=min([p[1] for p in pinmap.values()] or [y]);rx,ry=x,miny-5.08;vx,vy=x,miny-2.54;justify=''
  if libname.startswith('Device:D') or libname=='Device:LED':
   if rot%180==90:rx,ry,vx,vy=x+10.16,y-1.27,x+10.16,y+1.27;justify=''
  if libname=='Transistor_Array:ULN2003A':rx,ry,vx,vy=x,y-20.32,x,y-17.78
  if libname in ['InputSwitch:R78E5','InputSwitch:R12P12S_P']:rx,ry,vx,vy=x,y-15.24,x,y-12.7
  if prop:rx,ry,vx,vy=[v*U for v in prop]
  path='/'+ROOTID+('/'+self.sid if self.page!=1 else '')
  obj=f'''(symbol (lib_id {q(libname)}) (at {fmt(x)} {fmt(y)} {rot}) (unit {unit}) (in_bom yes) (on_board yes) (dnp no) (uuid {q(uid())})
 (property "Reference" {q(ref)} (at {fmt(rx)} {fmt(ry)} {rot%180}) (effects (font (size 1.016 1.016)) {justify}))
 (property "Value" {q(value)} (at {fmt(vx)} {fmt(vy)} {rot%180}) (effects (font (size 1.016 1.016)) {justify}))
 (property "Footprint" {q(fp)} (at {fmt(x)} {fmt(y)} 0) (effects (font (size 1.27 1.27)) hide))
 (property "Datasheet" {q(ds)} (at {fmt(x)} {fmt(y)} 0) (effects (font (size 1.27 1.27)) hide))
 (instances (project "InputSwitch" (path {q(path)} (reference {q(ref)}) (unit {unit})))))'''
  
  if libname.startswith('power:'):
   ob=parse(obj)
   for pr in kids(ob,'property'):
    if pr[1]=='Reference' or libname.endswith('PWR_FLAG'): child(pr,'effects').append(Atom('hide'))
    if pr[1]=='Value' and libname.endswith('GND'): child(pr,'at')[1:3]=[Atom(fmt(x)),Atom(fmt(y+3.81))]
   obj=dump(ob)
  self.items.append(obj);self.refs.append((ref,value,fp,ds));return key
 def p(self,k,n):return self.pins[k][str(n)]
 def w(self,*pts):
  for a,b in zip(pts,pts[1:]):
   a=tuple(round(v,4) for v in a);b=tuple(round(v,4) for v in b)
   if a==b:continue
   self.wires.append((a,b));self.pts[a]+=1;self.pts[b]+=1
   self.items.append(f'(wire (pts (xy {fmt(a[0])} {fmt(a[1])}) (xy {fmt(b[0])} {fmt(b[1])})) (stroke (width 0) (type default)) (uuid {q(uid())}))')
 def at(self,x,y):return (x*U,y*U)
 def label(self,name,p,global_=False,angle=0):
  typ='global_label' if global_ else 'label';extra='(shape bidirectional)' if global_ else ''
  self.items.append(f'({typ} {q(name)} {extra} (at {fmt(p[0])} {fmt(p[1])} {angle}) (effects (font (size 1.016 1.016)) (justify {"right" if angle==180 else "left"}{"" if global_ else " bottom"})) (uuid {q(uid())}))')
 def net(self,k,n,name,dx=4,dy=0,global_=True):
  a=self.p(k,n);b=(a[0]+dx*U,a[1]+dy*U);self.w(a,b);self.label(name,b,global_,180 if dx<0 else 0);return b
 def gnd(self,p):
  self.add('power:GND',f'#PWR{self.page}{len(self.items):04}', 'GND',p[0]/U,p[1]/U,fp='')
 def ground(self,k,n,dy=3):
  p=self.p(k,n);b=(p[0],p[1]+dy*U);self.w(p,b);self.gnd(b);return b
 def flag(self,p):self.add('power:PWR_FLAG',f'#FLG{self.page}{len(self.items):04}','PWR_FLAG',p[0]/U,p[1]/U,fp='')
 def nc(self,k,n):
  p=self.p(k,n);self.items.append(f'(no_connect (at {fmt(p[0])} {fmt(p[1])}) (uuid {q(uid())}))')
 def text(self,t,x,y,size=1.27):self.items.append(f'(text {q(t)} (at {fmt(x*U)} {fmt(y*U)} 0) (effects (font (size {size} {size})) (justify left top)) (uuid {q(uid())}))')
 def subsheet(self,s,x,y):
  self.items.append(f'''(sheet (at {fmt(x*U)} {fmt(y*U)}) (size 66.04 15.24) (fields_autoplaced yes) (stroke (width 0) (type default)) (fill (color 0 0 0 0)) (uuid {q(s.sid)})
(property "Sheetname" {q(s.title)} (at {fmt(x*U)} {fmt((y-1)*U)} 0) (effects (font (size 1.27 1.27)) (justify left bottom)))
(property "Sheetfile" {q(s.name+'.kicad_sch')} (at {fmt(x*U)} {fmt((y+7)*U)} 0) (effects (font (size 1.016 1.016)) (justify left top)))
(instances (project "InputSwitch" (path {q('/'+ROOTID)} (page {q(s.page)})))))''')
 def save(self):
  # Explicit junctions on branches; pins count as endpoints too.
  counts=dict(self.pts)
  for pm in self.pins.values():
   for p in pm.values():counts[p]=counts.get(p,0)+1
  junctions=[]
  for p,c in counts.items():
   if c>=3:junctions.append(f'(junction (at {fmt(p[0])} {fmt(p[1])}) (diameter 0) (color 0 0 0 0) (uuid {q(uid())}))')
  txt=f'''(kicad_sch (version 20250114) (generator "eeschema") (uuid {q(self.uuid)}) (paper "A3")
(title_block (title {q(self.title)}) (date "2026-10-01") (rev "A") (comment 1 "Low-voltage controller only. No mains on this PCB.") (comment 2 "ULN2003A/G6K pickup margin requires bench validation."))
(lib_symbols {' '.join(dump(s) for s in self.libs.values())})
'''+ '\n'.join(self.items+junctions)
  if self.page==1:txt+='\n(sheet_instances (path "/" (page "1")))'
  txt+='\n(embedded_fonts no))\n';(ROOT/(self.name+'.kicad_sch')).write_text(txt)
RFP='Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder'
CFP='Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder'
EFP='Capacitor_THT:CP_Radial_D5.0mm_P2.50mm'
DFP='Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal'
def r(s,ref,v,x,y,rot=0,fp=RFP):return s.add('Device:R',ref,v,x,y,rot,fp=fp)
def c(s,ref,v,x,y,rot=0,polar=False,fp=None):return s.add('Device:C_Polarized' if polar else 'Device:C',ref,v,x,y,rot,fp=fp or (EFP if polar else CFP))
def conn(s,ref,v,x,y,n=2,rot=180):return s.add(f'Connector_Generic:Conn_01x{n:02}',ref,v,x,y,rot,fp=f'Connector_JST:JST_XH_B{n}B-XH-A_1x{n:02}_P2.50mm_Vertical')
def caprail(s,ref,v,x,y,net,ground='GND',polar=False):
 k=c(s,ref,v,x,y,polar=polar,fp=('Capacitor_THT:CP_Radial_D6.3mm_P2.50mm' if ref=='C1' else None));s.net(k,1,net,0,-2)
 if ground=='GND':s.ground(k,2)
 else:s.net(k,2,ground,0,2)
 return k
# Root: relay contact path only.
a=Sheet('InputSwitch','Audio source selector and output mute',1)
a.text('CONTACTS ONLY IN THE THROUGH SIGNAL PATH',8,7,2)
a.text('K1/K2 OFF = REFERENCE. ON = AV. K3 OFF = PASS. ON = output shorted to its own return.\nAll RCA shells must be insulated from the enclosure. Keep each signal with its corresponding return.',8,12)
for ch,kref,y,jref in [('L','K1',30,1),('R','K2',66,3)]:
 sig=a.add('InputSwitch:G6K_5V',kref,'G6K-2P-Y DC5',47,y,unit=1)
 ret=a.add('InputSwitch:G6K_5V',kref,'G6K-2P-Y DC5',47,y+13,unit=2)
 jr=conn(a,f'J{jref}','REFERENCE '+ch,12,y-1)
 ja=conn(a,f'J{jref+1}','AV '+ch,12,y+5)
 # connectors at 180 have pin2 above pin1.
 a.w(a.p(jr,1),a.p(sig,2));a.label('REF_'+ch+'_SIGNAL',a.p(jr,1))
 p=a.p(jr,2);a.w(p,a.at(27,y-2),a.at(27,y+12),a.p(ret,7));a.label('REF_'+ch+'_RETURN',p)
 a.w(a.p(ja,1),a.at(34,y+5),a.at(34,y+1),a.p(sig,4));a.label('AV_'+ch+'_SIGNAL',a.p(ja,1))
 p=a.p(ja,2);a.w(p,a.at(23,y+4),a.at(23,y+16),a.at(38,y+16),a.at(38,y+14),a.p(ret,5));a.label('AV_'+ch+'_RETURN',p)
 a.net(sig,3,'SEL_'+ch+'_SIGNAL',6,0)
 a.net(ret,6,'SEL_'+ch+'_RETURN',6,0)
 mute=a.add('InputSwitch:G6K_5V','K3','G6K-2P-Y DC5',110,y,unit=1 if ch=='L' else 2)
 nc,co,no=(2,3,4) if ch=='L' else (7,6,5)
 a.net(mute,nc,'SEL_'+ch+'_SIGNAL',-8,0)
 jrout=conn(a,'J5' if ch=='L' else 'J6','P3A '+ch,143,y,rot=0)
 a.w(a.p(mute,co),a.p(jrout,1));a.label('P3A_'+ch+'_SIGNAL',a.at(125,y))
 p=a.p(mute,no);b=a.at(102,y+6);d=a.at(137,y+6)
 a.w(p,a.at(102,y+1),b,d,a.at(137,y+1),a.p(jrout,2));a.w(b,(b[0],b[1]+2*U));a.label('SEL_'+ch+'_RETURN',(b[0],b[1]+2*U),True)
 a.text(ch+' channel: no common GND',8,y+22)
a.text('Sensing taps are on SEL_* before K3. No permanent connection exists to inactive inputs.\nThe P3A may join its own L/R returns externally; this board does not join them.\nUnpowered pass-through is intentional: abrupt controller loss is not a guaranteed mute.',70,88)
power=Sheet('Power','12V input and 5V buck supply',2)
ctl=Sheet('Control','ATtiny412 and relay drivers',3)
dl=Sheet('Detector_L','Isolated left detector',4)
dr=Sheet('Detector_R','Isolated right detector',5)
for s,x in [(power,8),(ctl,46),(dl,84),(dr,122)]:a.subsheet(s,x,92)
# Supply
s=power;s.text('ISOLATED REGULATED 12V WALL ADAPTER: 12V +/-2%, >=0.5A',8,8,1.8)
s.text('DC input only. G7L mains contacts and all 230V wiring are chassis-mounted off-board.\nPE remains continuous and is never switched. Supply GND is the controller ground only.',8,13)
j=conn(s,'J7','12V DC INPUT',12,34)
f=s.add('Device:Fuse','F1','T500mA',29,34,90,fp='Fuse:Fuseholder_Cylinder-5x20mm_Bulgin_FX0457_Horizontal_Closed')
d=s.add('Device:D_Schottky','D1','SS14',44,34,180,fp='Diode_SMD:D_SMA',ds='https://www.vishay.com/docs/88746/ss12.pdf')
s.w(s.p(j,1),s.p(f,1));s.w(s.p(f,2),s.p(d,2));s.w(s.p(j,2),s.at(18,33),s.at(18,47));s.gnd(s.at(18,47))
s.net(d,1,'+12V',6,0);s.flag(s.p(d,1));s.flag(s.p(j,2))
tvs=s.add('Device:D_Zener','D2','SMBJ13A',61,43,270,fp='Diode_SMD:D_SMB',ds='https://m.littelfuse.com/~/media/electronics/datasheets/tvs_diodes/littelfuse_tvs_diode_smbj_datasheet.pdf.pdf')
s.net(tvs,1,'+12V',0,-3);s.ground(tvs,2)
caprail(s,'C1','100u / 35V',77,43,'+12V',polar=True)
caprail(s,'C2','10u / 50V X7R',94,43,'+12V')
u=s.add('InputSwitch:R78E5','U1','R-78E5.0-0.5',118,34)
s.net(u,1,'+12V',-6,0);s.net(u,3,'+5V',6,0);s.ground(u,2)
caprail(s,'C3','47u / 16V',139,43,'+5V',polar=True)
caprail(s,'C4','100n / 50V',153,43,'+5V')
s.text('D1 reverse-polarity blocking; F1 limits fault current; D2 clamps short input transients.\nNot a sustained-overvoltage disconnect. Use only the specified regulated adapter.\nSS14 drop reduces the coil/module feed slightly below the adapter voltage.',8,60)
s.text('5V supply: 500mA capacity; 3 relay coils total about 63mA nominal.\nAllow 100mA total 5V load, plus two isolated detector modules on 12V.\nR-78E total output capacitance must stay below 220uF.\nInput TVS/fuse coordination and ripple/EMI need bench/layout validation.',83,60)
for n,net,x in [(1,'+12V',25),(2,'+5V',50),(3,'GND',75)]:
 tp=s.add('Connector:TestPoint',f'TP{n}',net,x,85,fp='TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm')
 if net=='GND':s.ground(tp,1)
 else:s.net(tp,1,net,0,3)
s.text('NO PCB MAINS. Do not update the old PCB from this schematic until layout work is authorised.',8,100,1.5)
# Control
s=ctl;s.text('FIVE GPIOs; PA0 REMAINS UPDI',8,7,1.8)
u=s.add('MCU_Microchip_ATtiny:ATtiny412-SS','U2','ATtiny412-SS',29,29)
s.net(u,1,'+5V',0,-3);s.ground(u,8)
for n,net in [(6,'UPDI'),(4,'SOURCE_AV'),(5,'MUTE'),(7,'AUDIO_PRESENT_N'),(2,'P3A_ON'),(3,'TOGGLE_AV')]:s.net(u,n,net,7,0)
caprail(s,'C5','100n / 50V',10,25,'+5V');caprail(s,'C6','1u / 25V',10,41,'+5V')
j=conn(s,'J8','UPDI / +5V / GND',56,17,3,rot=0)
s.net(j,1,'UPDI',-4,0);s.net(j,2,'+5V',-4,0);s.ground(j,3)
s.text('J8 pin 1 UPDI; pin 2 target-voltage reference; pin 3 GND.\nProgrammer must not back-power the board. BOD 4.2V + watchdog in firmware.',8,51)
# Toggle connector and RC
j=conn(s,'J9','SPDT: REF / COM / AV',78,23,3,rot=180)
s.ground(j,1,3)
rr=r(s,'R1','1k',93,23,90);s.w(s.p(j,2),s.at(88,23),s.p(rr,1));s.net(j,3,'+5V',4,0)
node=s.at(103,23);s.w(s.p(rr,2),node);s.w(node,(node[0],node[1]-2*U));s.label('TOGGLE_AV',(node[0],node[1]-2*U),True)
rp=r(s,'R2','47k',103,32);s.w(node,s.p(rp,1));s.ground(rp,2)
cc=c(s,'C7','100n / 50V',118,32);s.w(node,s.at(118,23),s.p(cc,1));s.ground(cc,2)
s.text('Open/disconnected switch -> REFERENCE.\n100us contact-driven RC; 4.8ms with open switch.\nFirmware debounce >=20ms.',81,43)
# driver U3 and coils on same sheet
u3=s.add('Transistor_Array:ULN2003A','U3','ULN2003A (5V COILS)',48,75,fp='Package_SO:SOIC-16_3.9x9.9mm_P1.27mm',ds='https://www.st.com/resource/en/datasheet/uln2001.pdf')
s.net(u3,1,'SOURCE_AV',-2,0);s.net(u3,2,'SOURCE_AV',-2,0);s.net(u3,3,'MUTE',-2,0)
s.net(u3,9,'+5V',4,0);s.ground(u3,8)

for n in [4,5,6,7]:s.w(s.p(u3,n),s.at(41,75+(n-3)))
s.w(s.at(41,76),s.at(41,77),s.at(41,78),s.at(41,79),s.at(41,83));s.gnd(s.at(41,83))
for n in [13,12,11,10]:s.nc(u3,n)
for kref,net,x,out in [('K1','K1_LOW',72,16),('K2','K2_LOW',93,15),('K3','K3_LOW',114,14)]:
 k=s.add('InputSwitch:G6K_5V',kref,'G6K-2P-Y DC5',x,75,unit=3)
 s.net(k,1,'+5V',0,-3);s.net(k,8,net,0,3);s.net(u3,out,net,5,0)
# U4 12V driver block
u4=s.add('Transistor_Array:ULN2003A','U4','ULN2003A (12V COIL)',137,76,fp='Package_SO:SOIC-16_3.9x9.9mm_P1.27mm',ds='https://www.st.com/resource/en/datasheet/uln2001.pdf')
s.net(u4,1,'P3A_ON',-4,0);s.net(u4,9,'+12V',4,0);s.ground(u4,8)

for n in [2,3,4,5,6,7]:s.w(s.p(u4,n),s.at(130,76+(n-3)))
s.w(*[s.at(130,y) for y in range(75,83)]);s.gnd(s.at(130,82))
for n in [15,14,13,12,11,10]:s.nc(u4,n)
s.net(u4,16,'G7L_LOW',4,0)
j=conn(s,'J10','G7L COIL ONLY',144,94,2,rot=0);s.net(j,1,'+12V',-4,0);s.net(j,2,'G7L_LOW',-4,0)
s.text('G7L-2A-T DC12: J10 pin 1 coil+; pin 2 low-side.',105,88)
# default low GPIO pull-downs
for rr,net,x in [('R3','SOURCE_AV',12),('R4','MUTE',24),('R5','P3A_ON',33)]:
 k=r(s,rr,'47k',x,72);s.net(k,1,net,0,-4);s.ground(k,2)
s.text('Driver inputs tied low when MCU is reset.\nUnused ULN inputs grounded; outputs genuinely unused.\nNo parallel output channels.',8,87)
# A single logic inverter drives the Reference LED, preserving all five GPIOs.
inv=s.add('74xGxx:74LVC1G04','U9','SN74LVC1G04DBV',131,22,fp='Package_TO_SOT_SMD:SOT-23-5',ds='https://www.ti.com/lit/ds/symlink/sn74lvc1g04.pdf')
s.net(inv,2,'SOURCE_AV',-4,0);s.net(inv,4,'REFERENCE_LED',4,0);s.net(inv,5,'+5V',0,-3);s.ground(inv,3);s.nc(inv,1)
for ref,rr,net,x in [('D3','R7','SOURCE_AV',130),('D4','R8','REFERENCE_LED',151)]:
 res=r(s,rr,'4k7',x,37);s.net(res,1,net,0,-3)
 led=s.add('Device:LED',ref,'AV' if ref=='D3' else 'REFERENCE',x,46,90,fp='LED_THT:LED_D3.0mm');s.w(s.p(res,2),s.p(led,2));s.ground(led,1)
caprail(s,'C9','100n / 50V',114,15,'+5V')
s.text('LEDs indicate source COMMAND.\nThey do not verify relay contacts.',126,55)
# Detector wired OR active-low envelope at MCU side
rr=r(s,'R10','47k',91,100);s.net(rr,1,'+5V',0,-3);s.net(rr,2,'AUDIO_PRESENT_N',0,3)
cc=c(s,'C8','2u2 / 25V',109,100);s.net(cc,1,'AUDIO_PRESENT_N',0,-3);s.ground(cc,2)
s.text('Optocoupler wired-OR: LOW = recent audio. 103ms nominal release RC.\nFirmware must require 500ms persistence, then time 10min silence.\nBlank detection at startup, source changes and after power-off.\nDo not count a single edge/click as continuous audio.',8,100)
# Detector implementation below
for s,ch,base,ampref,opref,dcref,qref in [(dl,'L',20,'U5','U6','U10','Q2'),(dr,'R',40,'U7','U8','U11','Q3')]:
 rail='ISO_'+ch+'_12V';quiet='ISO_'+ch+'_QUIET';ret='SEL_'+ch+'_RETURN';bias='BIAS_'+ch;thr='THRESH_'+ch
 def R(i,v,x,y,rot=0,fp=RFP):return r(s,'R'+str(base+i),v,x,y,rot,fp)
 def C(i,v,x,y,rot=0,polar=False,fp=None):return c(s,'C'+str(base+i),v,x,y,rot,polar,fp)
 def retpin(k,n,dy=3):return s.net(k,n,ret,0,dy)
 s.text(ch+' CHANNEL - INDEPENDENT GALVANIC ISOLATION',8,7,1.8)
 s.text('Isolated return is tied ONLY to SEL_'+ch+'_RETURN, after its source-selection relay.\nNo detector wire, resistor, capacitor or shield connects this return to control GND or the other channel.',8,12)
 dc=s.add('InputSwitch:R12P12S_P',dcref,'R12P12S/P',30,31,fp='InputSwitch:R12P12S_P_SIP7')
 s.net(dc,1,'+12V',-6,0);s.ground(dc,2)
 s.net(dc,7,rail,5,0);s.net(dc,5,ret,5,0)
 caprail(s,'C'+str(base),'10u / 50V X7R',10,43,'+12V')
 preload=R(0,'1k2 / 0.5W',52,39,fp='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal');s.net(preload,1,rail,0,-4);retpin(preload,2)
 filt=R(1,'100R',71,29,90);s.net(filt,1,rail,-5,0);s.net(filt,2,quiet,5,0);s.flag(s.p(filt,2))
 caprail(s,'C'+str(base+1),'47u / 25V',86,40,quiet,ret,True)
 caprail(s,'C'+str(base+2),'100n / 50V',102,40,quiet,ret)
 pwr=s.add('Amplifier_Operational:LM358',ampref,'LM358N',117,39,unit=3,fp='Package_DIP:DIP-8_W7.62mm')
 s.net(pwr,8,quiet,0,-3);retpin(pwr,4)
 # zener reference and threshold divider, all in local isolated domain.
 rr=R(2,'1k2',140,28);s.net(rr,1,quiet,0,-3)
 z=s.add('Device:D_Zener','D'+str(base),'BZX55C5V1',140,40,270,fp=DFP,ds='https://www.vishay.com/docs/85604/bzx55.pdf')
 s.w(s.p(rr,2),s.p(z,1));s.label(bias,s.p(z,1));retpin(z,2)
 cc=C(3,'33u / 16V',153,40,polar=True);s.net(cc,1,bias,0,-3,False);retpin(cc,2)
 s.text('1k2 preload holds the isolated converter above 10% load.\n100R + 47u filters its switching ripple. No capacitor crosses isolation.\nModule input range 10.8-13.2V: verify at the protected +12V rail.',8,53)
 # audio branch: series coupling capacitor and resistor only in sensing tap.
 cc=C(4,'100n FILM / 50V',21,72,90,fp='Capacitor_THT:C_Rect_L7.0mm_W2.0mm_P5.00mm');s.net(cc,1,'SEL_'+ch+'_SIGNAL',-7,0)
 ri=R(3,'100k',34,72,90);s.w(s.p(cc,2),s.p(ri,1))
 ua=s.add('Amplifier_Operational:LM358',ampref,'LM358N',56,73,unit=1,fp='Package_DIP:DIP-8_W7.62mm')
 node=s.at(43,72);s.w(s.p(ri,2),node,s.p(ua,3))
 rb=R(4,'470k',43,65);s.net(rb,1,bias,0,-2,False);s.w(s.p(rb,2),node)
 # Feedback AC gain 101, DC gain one.
 fb=R(5,'100k',57,85,90);sn=s.at(48,74);out=s.at(66,73)
 s.w(s.p(ua,2),sn,s.at(48,85),s.p(fb,1));s.w(s.p(fb,2),s.at(66,85),out,s.p(ua,1))
 rg=R(6,'1k',48,94);s.w(s.at(48,85),s.p(rg,1));cg=C(5,'33u / 16V',48,103,polar=True);s.w(s.p(rg,2),s.p(cg,1));retpin(cg,2,2)
 # Comparator with modest positive feedback for a defined transition.
 ub=s.add('Amplifier_Operational:LM358',ampref,'LM358N',88,72,unit=2,fp='Package_DIP:DIP-8_W7.62mm')
 s.w(out,s.at(77,73),s.p(ub,6))
 rt=R(7,'10k',77,64);s.net(rt,1,bias,0,-3,False);tn=s.at(77,71);s.w(s.p(rt,2),tn,s.p(ub,5))
 rb2=R(8,'100k',77,91);s.w(tn,s.at(72,71),s.at(72,89.5),s.p(rb2,1));retpin(rb2,2)
 rh=R(9,'1M',89,57,90);s.w(s.p(rh,1),s.at(81,57),s.at(81,71),tn)
 cp=s.at(96,72);s.w(s.p(ub,7),cp,s.at(96,57),s.p(rh,2));s.label('DETECT_PULSE',cp)
 # BJT takes optocoupler LED current off the LM358 output.
 rr=R(10,'10k',106,72,90);s.w(cp,s.p(rr,1))
 qb=s.add('Transistor_BJT:BC549',qref,'BC549',116,72,fp='Package_TO_SOT_THT:TO-92_Inline',ds='https://www.onsemi.com/pdf/datasheet/bc550-d.pdf');s.w(s.p(rr,2),s.p(qb,2));retpin(qb,3)
 be=R(11,'100k',109,85);s.w(s.p(qb,2),s.at(112,72),s.at(112,82),s.at(109,82),s.p(be,1));retpin(be,2)
 op=s.add('InputSwitch:VO617A_3',opref,'VO617A-3',132,66,fp='Package_DIP:DIP-4_W7.62mm')
 ledres=R(12,'1k8',120,57);s.net(ledres,1,rail,0,-3);s.w(s.p(ledres,2),s.at(120,65),s.p(op,1))
 s.w(s.p(qb,1),s.at(117,67),s.p(op,2));s.ground(op,3,4)
 ro=R(13,'1k',146,65,90);s.w(s.p(op,4),s.p(ro,1));s.net(ro,2,'AUDIO_PRESENT_N',4,0)
 s.text('CONTROL SIDE',135,79,1.5)
 s.text('Optocoupler collector is the only\nlogic interface. Both channels\nwire-OR into one active-low input.',130,84)
 s.text('Nominal midband input impedance ~570k. AC gain ~101 x 470/570 = 83.3.\nNominal trigger ~4mVrms at 1kHz; tuning/bench value, not a guaranteed noise threshold.\nAt 2Vrms the detector saturates intentionally; it is outside the through audio path.\n100k limits loading when unpowered. Only ordinary SELV signals belong here.',62,98)
 # Input clamps protect the sensing amplifier; located on a separate annotated branch.
 for idx,upper in [(1,True),(2,False)]:
  dd=s.add('Device:D','D'+str(base+idx),'1N4148',12 if upper else 29,94,270,fp=DFP,ds='https://www.onsemi.com/pdf/datasheet/1n914-d.pdf')
  if upper:
   s.net(dd,1,quiet,0,-2);s.net(dd,2,'SENSE_INPUT',0,2,False)
  else:
   s.net(dd,1,'SENSE_INPUT',0,-2,False);retpin(dd,2)
 s.label('SENSE_INPUT',node)
 s.text('Branch clamps only;\nnever in the main audio path.',8,103)
for i,(x,y) in enumerate([(80,23),(90,23),(100,23),(110,23)],1):
 power.add('Mechanical:MountingHole',f'H{i}','M4',x,y,fp='MountingHole:MountingHole_4.3mm_M4')
# Save all five sheets and their explicit project-local symbol definitions.
for sh in [a,power,ctl,dl,dr]:sh.save()
syms=[]
for name,s in custom.items():
 s=copy.deepcopy(s);s[1]=name.split(':')[1];syms.append(dump(s))
(ROOT/'InputSwitch.kicad_sym').write_text('(kicad_symbol_lib (version 20250114) (generator "kicad_symbol_editor")\n'+'\n'.join(syms)+'\n)\n')
(ROOT/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "InputSwitch") (type "KiCad") (uri "${KIPRJMOD}/InputSwitch.kicad_sym") (options "") (descr "Verified controller-specific symbols")))\n')
# Schematic footprint provision only; no PCB layout or placement performed.
fpdir=ROOT/'InputSwitch.pretty';fpdir.mkdir(exist_ok=True)
fp='''(footprint "R12P12S_P_SIP7" (version 20250108) (generator "pcbnew") (layer "F.Cu") (attr through_hole)
(descr "RECOM R12P12S/P standard pinout, not /X2; datasheet RxxPxx rev 8-2024 p6")
(fp_text reference "REF**" (at 7.62 -4.5) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))
(fp_text value "R12P12S/P" (at 7.62 9.5) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))
(fp_rect (start -1.9 -2.4) (end 17.6 7.4) (stroke (width 0.1) (type default)) (fill none) (layer "F.Fab"))
(fp_rect (start -2.05 -2.55) (end 17.75 7.55) (stroke (width 0.12) (type default)) (fill none) (layer "F.SilkS"))
(fp_rect (start -2.65 -3.15) (end 18.35 8.15) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))
'''
for n,x in [(1,0),(2,2.54),(5,10.16),(7,15.24)]:fp+=f'(pad "{n}" thru_hole {"rect" if n==1 else "circle"} (at {x} 0) (size 1.8 1.8) (drill 1) (layers "*.Cu" "*.Mask"))\n'
fp+=')\n';(fpdir/'R12P12S_P_SIP7.kicad_mod').write_text(fp)
(ROOT/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "InputSwitch") (type "KiCad") (uri "${KIPRJMOD}/InputSwitch.pretty") (options "") (descr "Detector module footprint provision")))\n')
print('Generated five-sheet schematic.')

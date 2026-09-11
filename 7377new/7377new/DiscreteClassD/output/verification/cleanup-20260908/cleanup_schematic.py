from pathlib import Path
from copy import deepcopy as cp
import sys,uuid,math,re,json
ROOT=Path('/Users/tomwatson/Documents/GitHub/Kicadprojects/7377new/7377new/DiscreteClassD')
sys.path.insert(0,str(ROOT/'scripts'))
from sexp import *
BASE=ROOT/'output/verification/pre-cleanup-20260908'
SCALE=2.54
uid=lambda:Q(str(uuid.uuid4()))
def fmt(x):return str(round(float(x)*SCALE,6))
def effects(sz=1.27,just=None):
 e=['effects',['font',['size',str(sz),str(sz)]]]
 if just:e.append(['justify',*just.split()])
 return e
def propnew(n,v,x,y,hide=False):
 p=['property',Q(n),Q(v),['at',fmt(x),fmt(y),'0'],effects()]
 if hide:p.append(['hide','yes'])
 return p
libroot=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols')
cache={}
def load(id):
 if id not in cache:
  ns,name=id.split(':');a=parse((libroot/(ns+'.kicad_sym')).read_text());z=cp(next(s for s in allof(a,'symbol') if s[1]==name));z[1]=Q(id);cache[id]=z
 return cache[id]
def groundnames(a):
 for i,v in enumerate(a):
  if isinstance(v,list):groundnames(v)
  elif isinstance(v,Q):a[i]=Q(v.replace('PGND','GND'))
class Scene:
 def __init__(self,filename,pwrstart):
  self.filename=filename;old=parse((BASE/filename).read_text());self.old=old
  self.original={(prop(s,'Reference')[2],int(get(s,'unit')[1])):cp(s) for s in allof(old,'symbol')}
  self.a=[cp(v) for v in old if not(isinstance(v,list) and v[0] in ['symbol','wire','label','global_label','hierarchical_label','no_connect','junction','text','sheet','polyline','rectangle'])]
  for s in allof(get(old,'lib_symbols'),'symbol'):cache[s[1]]=cp(s)
  self.comps={};self.used=set();self.wires=[];self.pwr=pwrstart
  self.path=get(get(get(next(iter(self.original.values())),'instances'),'project'),'path')[1]
 def place(self,ref,x,y,angle=0,unit=1):
  k=(ref,unit);s=cp(self.original[k]);get(s,'at')[1:]=[fmt(x),fmt(y),str(angle)];get(s,'unit')[1]=str(unit)
  id=get(s,'lib_id')[1];self.used.add(id);self.comps[k]=s
  vertical=id in ['Device:R','Device:C','Device:C_Polarized'] and angle in [0,180]
  fx,fy=(x+2,y-1) if vertical else (x,y-4)
  if id.startswith('Amplifier_') or id.startswith('DiscreteClassD:TLV'):fy=y-5
  if id=='DiscreteClassD:UCC27301ADRCR':fy=y-14
  if id=='DiscreteClassD:TPS7A4901DGNR':fy=y-9
  if id.startswith('Transistor_FET:'):fx,fy=x+4,y-1
  if unit==3:fx,fy=x-3,y-1
  if id=='Connector:TestPoint':fx,fy=x+2,y-2
  if id=='74xGxx:74LVC1G04':fx,fy=x,y-11
  for n,pval in [('Reference',ref),('Value',None)]:
   p=prop(s,n);px=fx;py=fy+(1.8 if n=='Value' else 0)
   get(p,'at')[1:]=[fmt(px),fmt(py),str(angle) if angle in [90,270] else '0']
   p[:]=[v for v in p if not(isinstance(v,list) and v[0] in ['effects','hide'])]
   p.append(effects(1.15,'right' if unit==3 else 'left' if vertical or fx!=x else None))
  for p in allof(s,'property'):
   if p[1] not in ['Reference','Value']:
    get(p,'at')[1:]=[fmt(x),fmt(y),'0']
  self.a.append(s);return k
 def new(self,template,ref,val,x,y,angle=0,foot=None):
  s=cp(self.original[(template,1)]);get(s,'uuid')[1]=uid();prop(s,'Reference')[2]=Q(ref);prop(s,'Value')[2]=Q(val)
  if foot:prop(s,'Footprint')[2]=Q(foot)
  for n in ['Dielectric','Function','Requirement','MPN','Pin verification']:
   p=prop(s,n)
   if p:s.remove(p)
  inst=get(get(get(s,'instances'),'project'),'path');get(inst,'reference')[1]=Q(ref)
  self.original[(ref,1)]=s;return self.place(ref,x,y,angle)
 def pp(self,ref,n,unit=1):
  s=self.comps[(ref,unit)];x,y,ang=map(float,get(s,'at')[1:]);rad=math.radians(ang)
  for sub in allof(cache[get(s,'lib_id')[1]],'symbol'):
   if int(sub[1].split('_')[-2]) not in [0,unit]:continue
   for p in allof(sub,'pin'):
    if str(get(p,'number')[1])!=str(n):continue
    px,py=map(float,get(p,'at')[1:3]);return (round((x+px*math.cos(rad)-py*math.sin(rad))/SCALE,6),round((y-px*math.sin(rad)-py*math.cos(rad))/SCALE,6))
  raise KeyError((ref,n,unit))
 def w(self,*pts):
  for a,b in zip(pts,pts[1:]):
   a=tuple(round(v,6) for v in a);b=tuple(round(v,6) for v in b)
   if a==b:continue
   assert a[0]==b[0] or a[1]==b[1],(a,b)
   self.wires.append((a,b));self.a.append(['wire',['pts',['xy',*map(fmt,a)],['xy',*map(fmt,b)]],['stroke',['width','0'],['type','default']],['uuid',uid()]])
 def join(self,r1,p1,r2,p2,via=(),u1=1,u2=1):self.w(self.pp(r1,p1,u1),*via,self.pp(r2,p2,u2))
 def label(self,n,p,kind='label',right=False):
  if n=='GND':return self.gnd(p)
  a=[kind,Q(n)]
  if kind!='label':a.append(['shape','input' if kind=='hierarchical_label' else 'bidirectional'])
  a.extend([['at',*map(fmt,p),'0'],effects(1.15,'right bottom' if right and kind=='label' else 'left bottom' if kind=='label' else 'left'),['uuid',uid()]])
  if kind=='global_label':a.append(propnew('Intersheetrefs','${INTERSHEET_REFS}',*p,hide=True))
  self.a.append(a)
 def rail(self,n,p):self.label(n,p,'global_label')
 def gnd(self,p):
  self.pwr+=1;ref='#PWR'+str(self.pwr);id='power:GND';load(id);self.used.add(id)
  s=['symbol',['lib_id',Q(id)],['at',*map(fmt,p),'0'],['unit','1'],['in_bom','yes'],['on_board','yes'],['dnp','no'],['uuid',uid()],propnew('Reference',ref,p[0],p[1],True),propnew('Value','GND',p[0],p[1]+2.5),propnew('Footprint','',*p,True),propnew('Datasheet','',*p,True),['instances',['project',Q('DiscreteClassD'),['path',Q(self.path),['reference',Q(ref)],['unit','1']]]]]
  self.a.append(s)
 def groundpin(self,r,n,unit=1,length=2):
  p=self.pp(r,n,unit);q=(p[0],p[1]+length);self.w(p,q);self.gnd(q)
 def nc(self,r,n,unit=1):self.a.append(['no_connect',['at',*map(fmt,self.pp(r,n,unit))],['uuid',uid()]])
 def text(self,t,x,y,sz=1.4):self.a.append(['text',Q(t),['at',fmt(x),fmt(y),'0'],effects(sz,'left top'),['uuid',uid()]])
 def title(self,t,x,y):self.text(t,x,y,2.0)
 def tp(self,ref,x,y,p):self.place(ref,x,y);self.w((x,y),p)
 def flag(self,ref,n,x,y):
  if (ref,1) not in self.original:
   t=next(k for k in self.original if k[0].startswith('#FLG'));self.new(t[0],ref,'PWR_FLAG',x,y)
  else:self.place(ref,x,y)
  if n=='GND':self.gnd((x,y))
  else:self.rail(n,(x,y)) if n.startswith('+') else self.label(n,(x,y))
 def finish(self):
  # T junctions receive explicit dots; crossings without an endpoint stay separate.
  ends=set(p for seg in self.wires for p in seg);dots=set()
  for p in ends:
   degree=0
   for a,b in self.wires:
    if min(a[0],b[0])<=p[0]<=max(a[0],b[0]) and min(a[1],b[1])<=p[1]<=max(a[1],b[1]):degree+=1 if p in [a,b] else 2
   if degree>=3:dots.add(p)
  for p in dots:self.a.append(['junction',['at',*map(fmt,p)],['diameter','0'],['color','0','0','0','0'],['uuid',uid()]])
  get(self.a,'lib_symbols')[1:]=[cp(cache[id]) for id in sorted(self.used)]
  groundnames(self.a)
  (ROOT/self.filename).write_text(dump(self.a)+'\n')
def pair_ground(s,refs,xs,y,rail,bulk=False):
 for r,x in zip(refs,xs):s.place(r,x,y)
 top=y-4;bot=y+4
 for r,x in zip(refs,xs):s.w(s.pp(r,1),(x,top));s.w(s.pp(r,2),(x,bot))
 s.w((min(xs),top),(max(xs),top));s.w((min(xs),bot),(max(xs),bot));s.rail(rail,(min(xs),top));s.gnd((min(xs),bot))
def regulator(s,u,x,y,refs,rail,tp):
 ci,cn,cf,co,rt,rb=refs
 s.place(u,x,y);s.place(ci,x-16,y-1);s.place(cn,x-10,y+10);s.place(rt,x+17,y-1);s.place(rb,x+17,y+11);s.place(cf,x+27,y-1);s.place(co,x+37,y-1)
 # IN / EN and input bypass visibly share one bus.
 sy=y-3
 s.w((x-21,sy),s.pp(u,8));s.rail('+24V',(x-21,sy));s.w(s.pp(ci,1),(x-16,sy));s.groundpin(ci,2)
 s.w(s.pp(u,5),(x-8,y-1),(x-8,sy))
 s.w(s.pp(u,6),(x-10,y+3),(x-10,y+8.5),s.pp(cn,1));s.groundpin(cn,2)
 s.groundpin(u,4);s.groundpin(u,9);s.nc(u,3);s.nc(u,7)
 outy=y-7;fby=y+5
 s.w(s.pp(u,1),(x+9,sy),(x+9,outy),(x+40,outy));s.rail(rail,(x+40,outy))
 for r in [rt,cf,co]:p=s.pp(r,1);s.w(p,(p[0],outy))
 s.w(s.pp(u,2),(x+10,y),(x+10,fby),(x+27,fby))
 for r in [rt,cf]:p=s.pp(r,2);s.w(p,(p[0],fby))
 s.w(s.pp(rb,1),(x+17,fby));s.groundpin(rb,2);s.groundpin(co,2)
 s.tp(tp,x+34,outy-3,(x+34,outy))
 s.text('DGNR (DGN HVSSOP) value; DRBR footprint assigned.\nCustom:TPS7A4901DRBR unchanged; verify inventory.\nSymbol EP9 vs footprint pads 9-13 (centre 13): review.\n'+('91.2k / 10k: 11.9922 V' if rail=='+12V_GD' else '32.2k / 10k: 5.0007 V')+' nominal.',x-19,y+21,1.15)
def shared(s):
 s.title('2. SHARED VREF',10,60)
 s.place('R24',18,70);s.place('R25',18,84);s.rail('+5V_A',(18,66));s.w((18,66),s.pp('R24',1));s.join('R24',2,'R25',1);s.groundpin('R25',2)
 for r,x in [('C29',30),('C30',40)]:
  s.place(r,x,84);s.w(s.pp(r,1),(x,77));s.groundpin(r,2)
 s.w((18,77),(50,77));s.place('U3',53,78,unit=1);s.w((50,77),s.pp('U3',3))
 s.w(s.pp('U3',1),(61,78),(61,90),(47,90),(47,79),s.pp('U3',2));s.label('VREF_2V5',(61,78));s.tp('TP21',61,74,(61,78))
 s.title('3. SHARED 400 kHz OSCILLATOR',82,60)
 s.place('U7',112,78,unit=1);s.place('R26',94,77,90);s.place('R27',110,66,270)
 s.w((84,77),s.pp('R26',1));s.label('TRIANGLE_400K',(84,77),right=True)
 s.w(s.pp('R26',2),(103,77),s.pp('U7',1));s.w(s.pp('R27',1),(120,66),(120,78),s.pp('U7',7))
 s.w(s.pp('R27',2),(103,66),(103,77));s.w(s.pp('U7',2),(106,79));s.label('VREF_2V5',(106,79),right=True)
 # R27 pin 1 must be comparator OUT, pin 2 SUM: resistor is nonpolar; preserve numbering by rotation.
 # Reverse its orientation, then rewire its endpoints explicitly below during final topology check.
 s.place('R28',136,78,90);s.w((120,78),s.pp('R28',1));s.label('OSC_SQUARE',(122,78));s.tp('TP22',125,74,(125,78))
 s.place('U3',158,77,unit=2);s.w(s.pp('R28',2),(147,78),s.pp('U3',6,2));s.w(s.pp('U3',5,2),(151,76));s.label('VREF_2V5',(151,76),right=True)
 s.place('C31',158,66,90);s.w(s.pp('C31',1),(147,66),(147,78));s.w(s.pp('C31',2),(167,66),(167,77),s.pp('U3',7,2));s.label('TRIANGLE_400K',(167,77));s.tp('TP23',174,74,(174,77));s.w((167,77),(174,77))
 s.text('Non-inverting Schmitt + inverting integrator\n49.9k / 10k; 3.09k x 1nF: nominal 403.72 kHz\nTriangle approx. 1.999 to 3.001 V. Measure / tune.',91,91,1.15)
def powerunit(s,ref,idunit,x,y,vp,vm,rail,caps):
 s.place(ref,x,y,unit=idunit);pp=s.pp(ref,vp,idunit);top=y-6
 s.w(pp,(pp[0],top),(x+10*len(caps),top));s.rail(rail,(pp[0],top));s.groundpin(ref,vm,idunit)
 for i,c in enumerate(caps):
  cx=x+10+i*10;s.place(c,cx,y);s.w(s.pp(c,1),(cx,top));s.groundpin(c,2)
def channel(s,ch,y):
 isL=ch=='L';ins='U4' if isL else 'U9';buf='U5' if isL else 'U10';cmp='U7' if isL else 'U8';cu=2 if isL else 1;ou=1 if isL else 2
 cin,rf,rt,cr,ri=('C40','R29','R30','C41','R31') if isL else ('C45','R36','R37','C46','R38')
 tpa,tpp,tppos,tpneg,tpe=('TP24','TP25','TP26','TP27','TP28') if isL else ('TP29','TP30','TP31','TP32','TP33')
 rn,rp,dp,dn,capP,capN=('R33','R32','D20','D21','C42','C43') if isL else ('R40','R39','D22','D23','C47','C48')
 s.title(('4. LEFT' if isL else '5. RIGHT')+' INPUT / PWM / DEAD TIME',10,y-14)
 s.place(cin,21,y,90);s.place(rf,36,y,90);prop(s.comps[(rf,1)],'Value')[2]=Q('51k')
 s.w((12,y),s.pp(cin,1));s.label('LEFT_IN' if isL else 'RIGHT_IN',(12,y),right=True);s.join(cin,2,rf,1)
 s.place('U1',65,y+1,unit=ou);pnplus,pnminus,pnout=('3','2','1') if isL else ('5','6','7')
 s.w(s.pp(rf,2),s.pp('U1',pnplus,ou))
 for r,x in [(rt,45),(cr,54)]:s.place(r,x,y+10);s.w((x,y),s.pp(r,1));s.w(s.pp(r,2),(x,y+15))
 s.w((45,y+15),(54,y+15));s.label('VREF_2V5',(45,y+15),right=True)
 s.w(s.pp('U1',pnout,ou),(73,y+1),(73,y+13),(59,y+13),(59,y+2),s.pp('U1',pnminus,ou))
 s.place(ri,81,y+1,90);s.w((73,y+1),s.pp(ri,1));s.place(cmp,105,y+2,unit=cu)
 plus,minus,out=('4','3','6') if isL else ('1','2','7');s.w(s.pp(ri,2),s.pp(cmp,plus,cu));s.label('AUDIO_'+ch,(88,y+1));s.tp(tpa,91,y-3,(91,y+1))
 s.w(s.pp(cmp,minus,cu),(98,y+3));s.label('TRIANGLE_400K',(98,y+3),right=True)
 s.w(s.pp(cmp,out,cu),(125,y+2),(125,y));s.label('PWM_'+ch,(115,y+2));s.tp(tpp,119,y-2,(119,y+2))
 # Two complete RC/diode/Schmitt paths, directly wired.
 for unit,yy,r,d,c,tpn in [(1,y,rp,dp,capP,tppos),(2,y+23,rn,dn,capN,tpneg)]:
  s.place(r,147,yy,90);s.place(d,147,yy-6);s.place(c,161,yy+7);s.place(buf,181,yy,unit=unit)
  for nm,dy in [('Reference',2),('Value',3.8)]:get(prop(s.comps[(r,1)],nm),'at')[2]=fmt(yy+dy)
  s.w((137,yy),s.pp(r,1));s.w(s.pp(r,2),(161,yy),s.pp(buf,'1' if unit==1 else '3',unit));s.w((137,yy),(137,yy-6),s.pp(d,1));s.w(s.pp(d,2),(161,yy-6),(161,yy));s.w((161,yy),s.pp(c,1));s.groundpin(c,2)
  s.w(s.pp(buf,'6' if unit==1 else '4',unit),(203,yy));s.label(ch+'_DRIVE_'+('P' if unit==1 else 'N'),(192,yy));s.tp(tpn,197,yy-4,(197,yy))
 s.w((125,y),(137,y));s.place(ins,120,y+23);s.w(s.pp(ins,2),(111,y+23),(111,y+2));s.w(s.pp(ins,4),(137,y+23));s.nc(ins,1)
 s.w(s.pp(ins,5),(118,y+16));s.rail('+5V_A',(118,y+16));s.groundpin(ins,3)
 s.text('DEAD TIME TUNE: 330R / 100pF; diode K at source, A at RC node.\nDelayed rise, rapid fall. Final dead time requires gate measurements.',137,y+35,1.15)
 # Output sheet preserves UUID / instance; ports placed to accept direct drive wires.
 old=next(z for z in allof(s.old,'sheet') if prop(z,'Sheetname')[2]==('LEFT OUTPUT' if isL else 'RIGHT OUTPUT'))
 sh=cp(old);sx=225;sy=y-5;get(sh,'at')[1:]=[fmt(sx),fmt(sy)];get(sh,'size')[1:]=[fmt(69),fmt(40)]
 get(prop(sh,'Sheetname'),'at')[1:]=[fmt(sx),fmt(sy-2),'0'];get(prop(sh,'Sheetfile'),'at')[1:]=[fmt(sx),fmt(sy+42),'0']
 for p,dy in zip(allof(sh,'pin'),[5,28,35]):get(p,'at')[1:]=[fmt(sx),fmt(sy+dy),'180']
 s.a.append(sh);s.w((203,y),(225,y));s.w((203,y+23),(225,y+23))
 rpd,rpu=('R34','R35') if isL else ('R41','R42');s.place(rpd,214,y+39);s.place(rpu,214,y+21)
 s.w(s.pp(rpu,2),s.pp(rpd,1));s.w((214,y+30),(225,y+30));s.label('ENABLE_'+ch,(214,y+30),right=True);s.groundpin(rpd,2)
 s.w(s.pp(rpu,1),(214,y+17));s.rail('+5V_A',(214,y+17));s.tp(tpe,219,y+27,(219,y+30));s.text('10k: default disabled\n1k DNP: optional auto-enable',247,y+16,1.2)
 # Inverter local bypass directly tied to its supply and ground branch.
 cap='C44' if isL else 'C49';s.place(cap,104,y+26);s.w(s.pp(cap,1),(104,y+16),(118,y+16));s.groundpin(cap,2)
def main():
 s=Scene('DiscreteClassD.kicad_sch',200)
 s.title('1. POWER / REGULATORS',10,7)
 pair_ground(s,['C17','C20'],[13,24],25,'+24V')
 s.flag('#FLG01','+24V',13,39);s.flag('#FLG02','GND',24,39)
 regulator(s,'U11',53,28,['C21','C22','C23','C24','R20','R21'],'+12V_GD','TP10')
 regulator(s,'U12',136,28,['C25','C26','C27','C28','R22','R23'],'+5V_A','TP20')
 s.title('FILTERED ANALOGUE RAIL',195,7)
 s.new('R29','R43','4R7',214,20,90)
 s.new('C24','C50','22u / 25V',226,29,foot='Capacitor_SMD:C_1210_3225Metric');s.new('C24','C51','100n / 25V',239,29,foot='Capacitor_SMD:C_0805_2012Metric');s.new('TP20','TP34','+12V_A',246,17)
 s.w((201,20),s.pp('R43',1));s.rail('+12V_GD',(201,20));s.w(s.pp('R43',2),(246,20));s.rail('+12V_A',(246,20));s.w(s.pp('TP34',1),(246,20))
 for r,x in [('C50',226),('C51',239)]:s.w((x,20),s.pp(r,1));s.groundpin(r,2)
 s.flag('#FLG03','+12V_A',257,20)
 s.text('R43 feeds OPA1656 packages only.\n22uF + 100nF at filter; retain package bypass.\nUCC27301A devices stay on +12V_GD.',201,43,1.2)
 shared(s)
 s.title('IC SUPPLY PINS / LOCAL BYPASS',10,96)
 for args in [('U1',3,18,106,'8','4','+12V_A',['C32','C33']),('U3',3,61,106,'8','4','+12V_A',['C34','C35']),('U7',3,108,106,'8','5','+5V_A',['C36']),('U8',3,145,106,'8','5','+5V_A',['C37']),('U5',3,187,106,'5','2','+5V_A',['C38']),('U10',3,228,106,'5','2','+5V_A',['C39'])]:powerunit(s,*args)
 s.place('U8',280,77,unit=2);s.w(s.pp('U8',4,2),(270,76),(270,73));s.gnd((270,73));s.w(s.pp('U8',3,2),(272,78));s.label('VREF_2V5',(272,78),right=True);s.nc('U8',6,2);s.text('U8B spare: stable LOW after VREF settles.',259,89,1.2)
 s.place('J1',238,70);s.w(s.pp('J1',1),(232,69),(232,65));s.label('LEFT_IN',(232,65),right=True);s.w(s.pp('J1',3),(234,71),(234,76));s.label('RIGHT_IN',(234,76));s.w(s.pp('J1',2),(226,70),(226,73));s.gnd((226,73))
 channel(s,'L',131);channel(s,'R',180)
 # A1 provides room for conventional local wiring without reducing symbol scale.
 s.text('Input attenuation = 10k / (51k + 10k) = 0.163934; 2 Vrms -> 0.32787 Vrms / 0.463677 Vpk.\nOne board-wide GND. BTL speaker terminals remain floating. OPA1656 supply: filtered +12V_A.',10,225,1.2)
 get(s.a,'paper')[1]=Q('A1');s.finish()

def output(ch):
 s=Scene('PowerOutput_'+ch+'.kicad_sch',500 if ch=='L' else 800)
 def rr(ref):return re.sub(r'(\d+)$',lambda m:str(int(m[1])+100),ref) if ch=='R' else ref
 for side,ox,driver,hf,lf,offset in [('A',0,'U2','Q5','Q6',0),('B',80,'U6','Q7','Q8',6)]:
  X=lambda x:x+ox;u=rr(driver);qh=rr(hf);ql=rr(lf)
  s.title('HALF BRIDGE '+side,X(5),6)
  s.place(u,X(16),36);s.nc(u,2)
  s.w(s.pp(u,1),(X(16),26));s.rail('+12V_GD',(X(16),26))
  # Logic inputs retain the explicit cross-coupling; labels link to the three sheet ports.
  for pn,net in [('7','DRIVE_P' if side=='A' else 'DRIVE_N'),('8','DRIVE_N' if side=='A' else 'DRIVE_P'),('6','ENABLE')]:
   p=s.pp(u,pn);q=(X(8.5),p[1]);s.w(p,q);s.label(net,q,right=True)
  # VSS and exposed pad form a visible local ground return.
  s.w(s.pp(u,9),(X(16),46),(X(18),46),s.pp(u,11));s.gnd((X(16),46))
  s.place(qh,X(60),25);s.place(ql,X(60),50)
  s.w(s.pp(qh,2),(X(61),14));s.rail('+24V',(X(61),14));s.join(qh,3,ql,2);s.w(s.pp(ql,3),(X(61),61));s.gnd((X(61),61))
  s.label('SW_'+side,(X(61),36))
  # Bootstrap HB-HS visible between the driver and switch-node return.
  boot=rr('C1' if side=='A' else 'C7');s.place(boot,X(27),34)
  s.w(s.pp(u,3),(X(27),32),s.pp(boot,1));s.w(s.pp(boot,2),(X(27),36));s.w(s.pp(u,5),(X(61),36))
  for high,y,ridx,didx,tpidx in [(True,25,1+offset,1 if side=='A' else 3,2 if side=='A' else 5),(False,50,4+offset,2 if side=='A' else 4,3 if side=='A' else 6)]:
   r=rr('R'+str(ridx));pull=rr('R'+str(ridx+1));alt=rr('R'+str(ridx+2));d=rr('D'+str(didx));q=qh if high else ql;dp='4' if high else '10'
   s.place(r,X(40),y,90);s.place(pull,X(51),y+6);s.place(alt,X(46),y-7,90);s.place(d,X(37),y-7)
   # HO/LO -> local series resistor -> MOSFET gate. Cross HB once without junction.
   p=s.pp(u,dp);s.w(p,(X(23),p[1]),(X(23),y),s.pp(r,1));s.w(s.pp(r,2),s.pp(q,1))
   s.w((X(51),y),s.pp(pull,1))
   if high:s.w(s.pp(pull,2),(X(51),y+8),(X(61),y+8))
   else:s.w(s.pp(pull,2),(X(51),61),(X(61),61))
   # DNP faster turn-off branch preserved, including diode polarity and each pin number.
   s.w((X(30),y),(X(30),y-7),s.pp(d,1));s.join(d,2,alt,1);s.w(s.pp(alt,2),(X(54),y-7),(X(54),y))
   s.tp(rr('TP'+str(tpidx)),X(32),y-2,(X(32),y))
  # Existing switch-node RC snubber (DNP) wired vertically.
  snr=rr('R13' if side=='A' else 'R14');snc=rr('C13' if side=='A' else 'C14')
  s.place(snr,X(74),50);s.place(snc,X(74),59);s.w((X(61),40),(X(74),40),s.pp(snr,1));s.join(snr,2,snc,1);s.groundpin(snc,2)
  s.tp(rr('TP1' if side=='A' else 'TP4'),X(65),38,(X(65),40))
  # Local driver and 24 V ceramics form visibly wired parallel banks.
  cr=['C2','C3'] if side=='A' else ['C8','C9'];pair_ground(s,list(map(rr,cr)),[X(10),X(22)],70,'+12V_GD')
  cr=['C4','C5','C6'] if side=='A' else ['C10','C11','C12'];pair_ground(s,list(map(rr,cr)),[X(39),X(50),X(61)],70,'+24V')
  s.text('HS / VSS: Kelvin returns to respective MOSFET sources.\nKeep gate loops and local supply loops short.\nDNP diode K faces driver: optional faster turn-off path.',X(6),80,1.05)
  # HB flag is at the bootstrap node; represents the internal bootstrap diode source.
  fl=rr('#FLG11' if side=='A' else '#FLG12')
  s.place(fl,X(32),31);s.w((X(32),31),(X(32),29),(X(27),29),(X(27),32))
 # Both switch nodes connect with visible wires to the coupled output inductor.
 s.place(rr('L6'),80,94)
 s.w((61,36),(68,36),(68,93),s.pp(rr('L6'),1))
 s.w((141,36),(148,36),(148,86),(72,86),(72,95),s.pp(rr('L6'),4))
 s.title('DIFFERENTIAL OUTPUT',6,88)
 s.place(rr('C15'),94,99);s.place(rr('R15'),108,96);s.place(rr('C16'),108,103);s.place(rr('J15'),117,98)
 s.w(s.pp(rr('L6'),2),(112,93),(112,98),s.pp(rr('J15'),1));s.w(s.pp(rr('L6'),3),(86,95),(86,107),(114,107),(114,99),s.pp(rr('J15'),2))
 s.w((94,93),s.pp(rr('C15'),1));s.w(s.pp(rr('C15'),2),(94,107));s.w((108,93),s.pp(rr('R15'),1));s.join(rr('R15'),2,rr('C16'),1);s.w(s.pp(rr('C16'),2),(108,107))
 s.label('OUT_A',(88,93));s.label('OUT_B',(88,107));s.tp(rr('TP7'),92,90,(92,93));s.tp(rr('TP8'),88,104,(88,107))
 for r,net,x in [(rr('C18'),'OUT_A',44),(rr('C19'),'OUT_B',57)]:
  s.place(r,x,103);s.w(s.pp(r,1),(x,98));s.label(net,(x,98));s.groundpin(r,2)
 s.text('DNP output capacitors retained.\nNeither speaker terminal is grounded.',5,108,1.05)
 # Ports retained on the sheet with compact local stubs; control labels are shared by both drivers.
 for i,n in enumerate(['DRIVE_P','DRIVE_N','ENABLE']):
  p=(6,94+5*i);s.label(n,p,'hierarchical_label');s.w(p,(p[0]+11,p[1]));s.label(n,(p[0]+11,p[1]))
 s.text('HB power flags model internal UCC27301A bootstrap charging.\nGND is the single board-wide 0 V net; retain the Kelvin return layout intent.',6,110.5,1.0)
 get(s.a,'paper')[1]=Q('A3');s.finish()

def legacy_ground_cleanup():
 # Unreferenced historical sheet: ground naming only, no circuit redraw.
 s=Scene('PowerOutput.kicad_sch',1200)
 s.a=cp(s.old)
 s.used={get(z,'lib_id')[1] for z in allof(s.a,'symbol')}
 for kind in ['label','global_label']:
  for z in list(allof(s.a,kind)):
   if z[1]=='PGND':
    p=tuple(float(v)/SCALE for v in get(z,'at')[1:3])
    s.a.remove(z);s.gnd(p)
 s.finish()

if __name__=='__main__':
 main()
 for ch in ['L','R']:output(ch)
 legacy_ground_cleanup()

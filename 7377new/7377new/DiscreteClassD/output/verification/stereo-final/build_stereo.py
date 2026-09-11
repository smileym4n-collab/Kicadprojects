from pathlib import Path
from copy import deepcopy as cp
import sys, uuid, math, json, re, argparse
ROOT=Path('/Users/tomwatson/Documents/GitHub/Kicadprojects/7377new/7377new/DiscreteClassD')
sys.path.insert(0,str(ROOT/'scripts'))
from sexp import *
BASE=ROOT/'output/verification/pre-stereo-20260908'
oldroot=parse((BASE/'DiscreteClassD.kicad_sch').read_text())
oldpower=parse((BASE/'PowerOutput.kicad_sch').read_text())
rid=get(oldroot,'uuid')[1]
libroot=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols')
libs={s[1]:cp(s) for a in [oldroot,oldpower] for s in allof(get(a,'lib_symbols'),'symbol')}
local=parse((BASE/'DiscreteClassD.kicad_sym').read_text())
for s in allof(local,'symbol'):
 z=cp(s);z[1]=Q('DiscreteClassD:'+s[1]);libs[z[1]]=z
uid=lambda:Q(str(uuid.uuid4()))
def ef(size=1,just=None):
 z=['effects',['font',['size',str(size),str(size)]]]
 if just:z.append(['justify',*just.split()])
 return z
def pr(n,v,x=0,y=0,hide=False,size=1,just=None):
 z=['property',Q(n),Q(v),['at',str(x),str(y),'0'],ef(size,just)]
 if hide:z.append(['hide','yes'])
 return z
def libload(id):
 if id not in libs:
  ns,n=id.split(':');a=parse((libroot/(ns+'.kicad_sym')).read_text());z=cp(next(s for s in allof(a,'symbol') if s[1]==n))
  assert get(z,'extends') is None,id
  z[1]=Q(id);libs[id]=z
 return libs[id]
def pin(n,name,x,y,angle,typ='input'):
 return ['pin',typ,'line',['at',str(x),str(y),str(angle)],['length','2.54'],['name',Q(name),ef(.9)],['number',Q(n),ef(.9)]]
def rect(x1,y1,x2,y2):
 return ['rectangle',['start',str(x1),str(y1)],['end',str(x2),str(y2)],['stroke',['width','0.254'],['type','default']],['fill',['type','background']]]
# TPS7A4901DGN: preserve the verified user's pin numbers; redraw for readable wiring.
custom=parse(Path('/Users/tomwatson/Documents/KiCad/9.0/symbols/Custom.kicad_sym').read_text())
z=cp(next(s for s in allof(custom,'symbol') if s[1]=='TPS7A4901DGNR'))
assert {get(p,'number')[1]:get(p,'name')[1] for sub in allof(z,'symbol') for p in allof(sub,'pin')}=={'1':'OUT','2':'FB','3':'NC','4':'GND','5':'EN','6':'NR/SS','7':'DNC','8':'IN','9':'EP'}
z[1]=Q('DiscreteClassD:TPS7A4901DGNR');z[:]=[a for a in z if not(isinstance(a,list) and a[0]=='symbol')]
prop(z,'Datasheet')[2]=Q('https://www.ti.com/lit/ds/symlink/tps7a49.pdf')
prop(z,'Footprint')[2]=Q('Package_SO:HVSSOP-8-1EP_3x3mm_P0.65mm_EP1.57x1.89mm')
z.append(['symbol',Q('TPS7A4901DGNR_0_1'),rect(-10.16,12.7,10.16,-12.7)])
z.append(['symbol',Q('TPS7A4901DGNR_1_1'),pin('8','IN',-12.7,7.62,0,'power_in'),pin('5','EN',-12.7,2.54,0),pin('6','NR/SS',-12.7,-7.62,0,'passive'),pin('1','OUT',12.7,7.62,180,'power_out'),pin('2','FB',12.7,0,180),pin('3','NC',12.7,-7.62,180,'no_connect'),pin('7','DNC',12.7,-10.16,180,'no_connect'),pin('4','GND',-2.54,-15.24,90,'power_in'),pin('9','EP',2.54,-15.24,90,'power_in')])
libs[z[1]]=z
# Dual comparator sections follow TI table 5-2. Separate supply unit, same physical pins.
z=cp(libload('Amplifier_Operational:OPA1656ID'));z[1]=Q('DiscreteClassD:TLV3602DGKR')
for sub in allof(z,'symbol'):
 sub[1]=Q(sub[1].replace('OPA1656ID','TLV3602DGKR'))
 for p in allof(sub,'pin'):
  pn=get(p,'number')[1];get(p,'number')[1]=Q({'1':'7','2':'2','3':'1','5':'4','6':'3','7':'6','4':'5','8':'8'}[pn])
prop(z,'Value')[2]=Q('TLV3602DGKR');prop(z,'Datasheet')[2]=Q('https://www.ti.com/lit/ds/symlink/tlv3602.pdf');prop(z,'Footprint')[2]=Q('Package_SO:VSSOP-8_3x3mm_P0.65mm')
for name in ['Description','ki_keywords','ki_fp_filters']:
 p=prop(z,name)
 if p:z.remove(p)
z.append(pr('Description','Dual high-speed push-pull comparator; verified TI SNOSDB1E table 5-2',hide=True))
libs[z[1]]=z
class Sheet:
 def __init__(self,title,paper='A2',rootid=None,path=None):
  self.a=['kicad_sch',['version','20260306'],['generator',Q('eeschema')],['generator_version',Q('10.0')],['uuid',rootid or uid()],['paper',Q(paper)],['title_block',['title',Q(title)],['rev',Q('Stereo Rev 1')]],['lib_symbols']]
  self.path=path or '/'+rid;self.used=set();self.comps={};self.intent={}
 def add(self,id,ref,val,x,y,angle=0,unit=1,foot=None,dnp=False,extra=None):
  lib=libload(id);self.used.add(id)
  s=['symbol',['lib_id',Q(id)],['at',str(x),str(y),str(angle)],['unit',str(unit)],['in_bom','yes'],['on_board','yes'],['dnp','yes' if dnp else 'no'],['uuid',uid()]]
  vertical=id.startswith('Device:') and angle==0 and id!='Device:D'
  fx,fy=(x+3.81,y-1.27) if vertical else (x,y-10.16 if id.startswith(('Amplifier','DiscreteClassD:TLV')) else y-6.35)
  for n,v,px,py,h in [('Reference',ref,fx,fy,False),('Value',val,fx,fy+2.54,False),('Footprint',foot if foot is not None else str(prop(lib,'Footprint')[2]) if prop(lib,'Footprint') else '',x,y,True),('Datasheet',str(prop(lib,'Datasheet')[2]) if prop(lib,'Datasheet') else '',x,y,True)]:
   s.append(pr(n,v,px,py,h,1,'left' if vertical and not h else None))
  for n in ['Reference','Value']:
   if angle in [90,270]:get(prop(s,n),'at')[3]=str(angle)
  if unit==3:
   for n,dy in [('Reference',-2.54),('Value',0)]:
    pp=prop(s,n);get(pp,'at')[1:]=[str(x+5.08),str(y+dy),'0'];get(pp,'effects').append(['justify','left'])
  if id=='74xGxx:74LVC1G04':
   for n,dy in [('Reference',-20.32),('Value',-17.78)]:get(prop(s,n),'at')[1:]=[str(x),str(y+dy),'0']
  for n,v in (extra or {}).items():
   if prop(s,n):prop(s,n)[2]=Q(v)
   else:s.append(pr(n,v,x,y,True))
  s.append(['instances',['project',Q('DiscreteClassD'),['path',Q(self.path),['reference',Q(ref)],['unit',str(unit)]]]])
  self.a.append(s);self.comps[(ref,unit)]=s;self.intent.setdefault(ref,{})
  return (ref,unit)
 def pp(self,key):
  if isinstance(key,str):key=(key,1)
  s=self.comps[key];lib=libs[get(s,'lib_id')[1]];u=int(get(s,'unit')[1]);x,y,ang=map(float,get(s,'at')[1:]);r=math.radians(ang);res={}
  for sub in allof(lib,'symbol'):
   su=int(sub[1].split('_')[-2])
   if su not in [0,u]:continue
   for p in allof(sub,'pin'):
    px,py,pa=map(float,get(p,'at')[1:]);res[get(p,'number')[1]]=(round(x+px*math.cos(r)-py*math.sin(r),4),round(y-px*math.sin(r)-py*math.cos(r),4),(pa+ang)%360)
  return res
 def wire(self,p,q):
  p=tuple(round(float(t),4) for t in p[:2]);q=tuple(round(float(t),4) for t in q[:2])
  if p==q:return
  assert p[0]==q[0] or p[1]==q[1],(p,q)
  self.a.append(['wire',['pts',['xy',*map(str,p)],['xy',*map(str,q)]],['stroke',['width','0'],['type','default']],['uuid',uid()]])
 def label(self,n,p,kind='label',ang=0,just=None):
  z=[kind,Q(n)]
  if kind!='label':z.append(['shape','input' if kind=='hierarchical_label' else 'bidirectional'])
  z.extend([['at',*map(str,p[:2]),str(ang)],ef(1,just or ('left bottom' if kind=='label' else 'left')),['uuid',uid()]])
  if kind=='global_label':z.append(pr('Intersheetrefs','${INTERSHEET_REFS}',p[0],p[1],True))
  self.a.append(z)
 def net(self,key,pn,n,length=5.08):
  p=self.pp(key)[str(pn)];r=math.radians(p[2]);q=(round(p[0]-length*math.cos(r),4),round(p[1]+length*math.sin(r),4))
  kind='global_label' if n in ['+24V','+12V_GD','+5V_A','PGND'] else 'label'
  self.wire(p,q);self.label(n,q,kind,just='right bottom' if kind=='label' and p[2]==0 else None)
  ref=key if isinstance(key,str) else key[0];self.intent[ref][str(pn)]=n;return q
 def nc(self,key,pn):self.a.append(['no_connect',['at',*map(str,self.pp(key)[str(pn)][:2])],['uuid',uid()]])
 def dot(self,p):self.a.append(['junction',['at',*map(str,p[:2])],['diameter','0'],['color','0','0','0','0'],['uuid',uid()]])
 def text(self,t,x,y,size=1.27):self.a.append(['text',Q(t),['at',str(x),str(y),'0'],ef(size,'left top'),['uuid',uid()]])
 def section(self,t,x,y):self.text(t,x,y,1.8)
 def save(self,p):
  get(self.a,'lib_symbols')[1:]=[cp(libs[id]) for id in sorted(self.used)]
  p.write_text(dump(self.a)+'\n')
RFOOT='Resistor_SMD:R_0805_2012Metric';CFOOT='Capacitor_SMD:C_0805_2012Metric'
count={'R':19,'C':19,'TP':19}
def passive(s,kind,val,x,y,n1,n2,angle=0,ref=None,foot=None,dnp=False,extra=None):
 prefix='R' if kind=='R' else 'D' if kind=='D' else 'C'
 if not ref:count[prefix]=count.get(prefix,19)+1;ref=prefix+str(count[prefix])
 s.add('Device:'+kind,ref,val,x,y,angle,foot=foot or (RFOOT if prefix=='R' else 'Diode_SMD:D_SOD-123' if prefix=='D' else CFOOT),dnp=dnp,extra=extra)
 s.net(ref,'1',n1,2.54);s.net(ref,'2',n2,2.54);return ref
def tp(s,n,x,y,ref=None):
 if not ref:count['TP']+=1;ref='TP'+str(count['TP'])
 s.add('Connector:TestPoint',ref,n,x,y,foot='TestPoint:TestPoint_Pad_D1.5mm');s.net(ref,'1',n,2.54);return ref
def flag(s,n,x,y,ref):
 s.add('power:PWR_FLAG',ref,'PWR_FLAG',x,y);s.net(ref,'1',n,2.54)
def bypass(s,n,x,y,bulk=False):
 passive(s,'C','100n / 25V',x,y,n,'PGND',extra={'Dielectric':'X7R','Function':'Local IC package bypass'})
 if bulk:passive(s,'C','4u7 / 25V',x+20.32,y,n,'PGND',extra={'Dielectric':'X7R'})

def regulators(s):
 s.section('1. POWER / REGULATORS - SHARED',17.78,15.24)
 s.add('Connector:Conn_01x02_Socket','J14','24V INPUT',38.1,43.18,foot='DiscreteClassD:Power_Input_2_SMD')
 s.net('J14','1','+24V');s.net('J14','2','PGND')
 for ref,x in [('C17',68.58),('C20',101.6)]:
  passive(s,'C_Polarized','1000u / 35V FR',x,45.72,'+24V','PGND',ref=ref,foot='Capacitor_THT:CP_Radial_D12.5mm_P5.00mm',extra={'MPN':'EEUFR1V102','Manufacturer':'Panasonic','Function':'Shared supply bulk'})
 count['C']=20
 for n,x,ref in [('+24V',30.48,'TP9'),('PGND',76.2,'TP11')]:tp(s,n,x,78.74,ref)
 flag(s,'+24V',35.56,101.6,'#FLG01');flag(s,'PGND',86.36,101.6,'#FLG02')
 for u,ox,rail,top,bottom in [('U11',144.78,'+12V_GD','91k2 / 0.1%','10k / 0.1%'),('U12',365.76,'+5V_A','32k2 / 0.1%','10k / 0.1%')]:
  x=ox+48.26;y=50.8;s.add('DiscreteClassD:TPS7A4901DGNR',u,'TPS7A4901DGNR',x,y)
  for nm,yy in [('Reference',y-19.05),('Value',y-16.51)]:get(prop(s.comps[(u,1)],nm),'at')[1:]=[str(x),str(yy),'0']
  for pn,n in [('8','+24V'),('5','+24V'),('1',rail),('2',u+'_FB'),('6',u+'_NR'),('4','PGND')]:s.net(u,pn,n)
  pp=s.pp(u);end=(pp['4'][0],pp['4'][1]+5.08);ep=(pp['9'][0],end[1]);s.wire(pp['9'],ep);s.wire(ep,end);s.dot(end);s.intent[u]['9']='PGND'
  s.nc(u,'3');s.nc(u,'7')
  passive(s,'C','10u / 50V',ox,50.8,'+24V','PGND',foot='Capacitor_SMD:C_1210_3225Metric',extra={'Dielectric':'X7R','Requirement':'Effective C >=2.2uF at 24V; ESR <0.2 ohm'})
  passive(s,'C','10n C0G',ox+20.32,91.44,u+'_NR','PGND')
  passive(s,'R',top,ox+96.52,40.64,rail,u+'_FB')
  passive(s,'R',bottom,ox+96.52,68.58,u+'_FB','PGND')
  passive(s,'C','10n C0G',ox+132.08,40.64,rail,u+'_FB',extra={'Function':'Feed-forward across upper feedback resistor'})
  passive(s,'C','10u / 25V',ox+167.64,50.8,rail,'PGND',foot='Capacitor_SMD:C_1210_3225Metric',extra={'Dielectric':'X7R','Requirement':'Effective C >=2.2uF at rail voltage; ESR <0.2 ohm'})
  tp(s,rail,ox+124.46,93.98,'TP10' if rail=='+12V_GD' else None)
  s.text('Vout = 1.185 x (1 + Rtop/Rbottom)\n'+('11.9922 V nominal' if rail=='+12V_GD' else '5.0007 V nominal')+'; divider current 118.5 uA\nEN tied to IN; DNC pin 7 left open; EP to PGND.',ox+50.8,111.76,1.05)
 s.text('Both rails: 150 mA maximum; verify dissipation / thermal copper during PCB work.\nCapacitance values are nominal: verify effective value under DC bias.\nPGND is the single board-wide 0 V net.',17.78,119.38,1.05)

def shared(s,opa_rail):
 s.section('2. SHARED VREF',17.78,144.78)
 passive(s,'R','10k',25.4,170.18,'+5V_A','VREF_RAW')
 passive(s,'R','10k',25.4,198.12,'VREF_RAW','PGND')
 passive(s,'C','10u / 16V',60.96,190.5,'VREF_RAW','PGND')
 passive(s,'C','100n / 16V',88.9,190.5,'VREF_RAW','PGND')
 k=s.add('Amplifier_Operational:OPA1656ID','U3','OPA1656ID',134.62,175.26,unit=1)
 s.net(k,'3','VREF_RAW');s.net(k,'1','VREF_2V5')
 p=s.pp(k);s.wire(p['1'],(149.86,175.26));s.wire((149.86,175.26),(149.86,190.5));s.wire((149.86,190.5),(119.38,190.5));s.wire((119.38,190.5),(119.38,177.8));s.wire((119.38,177.8),p['2']);s.intent['U3']['2']='VREF_2V5'
 tp(s,'VREF_2V5',172.72,175.26)
 s.text('Divider bypass is on RAW node.\nNo large capacitor on buffer output.',111.76,200.66,1.05)
 s.section('3. SHARED 400 kHz OSCILLATOR',218.44,144.78)
 passive(s,'R','10k / 0.1%',236.22,167.64,'TRIANGLE_400K','OSC_SUM',angle=90)
 passive(s,'R','49k9 / 0.1%',274.32,198.12,'OSC_SQUARE','OSC_SUM',angle=90)
 k=s.add('DiscreteClassD:TLV3602DGKR','U7','TLV3602DGKR',307.34,170.18,unit=1)
 s.net(k,'1','OSC_SUM');s.net(k,'2','VREF_2V5');s.net(k,'7','OSC_SQUARE')
 passive(s,'R','3k09 / 0.1%',368.3,172.72,'OSC_SQUARE','INTEGRATOR_SUM',angle=90)
 k=s.add('Amplifier_Operational:OPA1656ID','U3','OPA1656ID',424.18,170.18,unit=2)
 s.net(k,'5','VREF_2V5');s.net(k,'6','INTEGRATOR_SUM');s.net(k,'7','TRIANGLE_400K')
 passive(s,'C','1n C0G / 1%',421.64,198.12,'INTEGRATOR_SUM','TRIANGLE_400K',angle=90)
 tp(s,'OSC_SQUARE',480.06,172.72);tp(s,'TRIANGLE_400K',533.4,172.72)
 s.text('Positive-feedback Schmitt: triangle -> 10k -> IN+; OUT -> 49k9 -> IN+; IN- = VREF.\nInverting integrator: square -> 3k09 -> IN-; 1nF from OUT to IN-; IN+ = VREF.\nIdeal 403.722 kHz; 1.9993 to 3.0014 V at nominal 5.0007 V rail. Tune / measure.',218.44,210.82,1.05)
 # Shared power units and associated local bypassing occupy a dedicated row.
 s.section('IC POWER / LOCAL BYPASS',17.78,228.6)
 for ref,id,x,unit,vp,vm,rail in [('U1','Amplifier_Operational:OPA1656ID',35.56,3,'8','4',opa_rail),('U3','Amplifier_Operational:OPA1656ID',119.38,3,'8','4',opa_rail),('U7','DiscreteClassD:TLV3602DGKR',203.2,3,'8','5','+5V_A'),('U8','DiscreteClassD:TLV3602DGKR',279.4,3,'8','5','+5V_A'),('U5','74xGxx:74LVC2G17',355.6,3,'5','2','+5V_A'),('U10','74xGxx:74LVC2G17',424.18,3,'5','2','+5V_A')]:
  k=s.add(id,ref,'OPA1656ID' if ref in ['U1','U3'] else 'TLV3602DGKR' if ref in ['U7','U8'] else 'SN74LVC2G17DBVR',x,259.08,unit=unit,foot='Package_TO_SOT_SMD:SOT-23-6' if ref in ['U5','U10'] else None)
  s.net(k,vp,rail,2.54);s.net(k,vm,'PGND',2.54);bypass(s,rail,x+22.86,259.08,ref in ['U1','U3'])
 k=s.add('DiscreteClassD:TLV3602DGKR','U8','TLV3602DGKR',528.32,259.08,unit=2)
 s.net(k,'4','PGND');s.net(k,'3','VREF_2V5');s.nc(k,'6')
 s.text('Spare U8B: IN+ = PGND, IN- = VREF; OUT unused.\nDefined LOW after VREF settles; inputs within rails.',480.06,281.94,1.0)

def channel(s,ch,ox,y):
 X=lambda x:round(x+ox,4)
 name='LEFT' if ch=='L' else 'RIGHT';inv='U4' if ch=='L' else 'U9';buf='U5' if ch=='L' else 'U10';cu='U7' if ch=='L' else 'U8';cunit=2 if ch=='L' else 1;ounit=1 if ch=='L' else 2
 s.section(('4. ' if ch=='L' else '5. ')+name+' INPUT + PWM + DEAD TIME',X(17.78),y)
 iy=y+27.94
 passive(s,'C','220n FILM',X(35.56),iy,ch+'EFT_IN' if ch=='L' else 'RIGHT_IN',ch+'_AC',angle=90,foot='Capacitor_SMD:C_2220_5750Metric',extra={'Dielectric':'Film','Requirement':'Provisional metric SMD land pattern; select actual 220n film MPN before PCB'})
 passive(s,'R','47k',X(76.2),iy,ch+'_AC',ch+'_BIAS',angle=90)
 passive(s,'R','10k',X(88.9),iy+20.32,ch+'_BIAS','VREF_2V5')
 passive(s,'C','100p C0G',X(119.38),iy+20.32,ch+'_BIAS','VREF_2V5')
 k=s.add('Amplifier_Operational:OPA1656ID','U1','OPA1656ID',X(139.7),iy+2.54,unit=ounit)
 plus,minus,out=('3','2','1') if ch=='L' else ('5','6','7')
 s.net(k,plus,ch+'_BIAS');s.net(k,out,ch+'_BUFFER')
 p=s.pp(k);yy=iy+12.7
 s.wire(p[out],(X(154.94),iy+2.54));s.wire((X(154.94),iy+2.54),(X(154.94),yy));s.wire((X(154.94),yy),(X(129.54),yy));s.wire((X(129.54),yy),(X(129.54),iy+5.08));s.wire((X(129.54),iy+5.08),p[minus]);s.intent['U1'][minus]=ch+'_BUFFER'
 passive(s,'R','100R',X(180.34),iy+2.54,ch+'_BUFFER','AUDIO_'+ch,angle=90)
 k=s.add('DiscreteClassD:TLV3602DGKR',cu,'TLV3602DGKR',X(238.76),iy+2.54,unit=cunit)
 plus,minus,out=('4','3','6') if cunit==2 else ('1','2','7')
 s.net(k,plus,'AUDIO_'+ch);s.net(k,minus,'TRIANGLE_400K');s.net(k,out,'PWM_'+ch)
 tp(s,'AUDIO_'+ch,X(180.34),iy+25.4);tp(s,'PWM_'+ch,X(251.46),iy+25.4)
 ly=iy+63.5
 k=s.add('74xGxx:74LVC1G04',inv,'SN74LVC1G04DBVR',X(43.18),ly+12.7,foot='Package_TO_SOT_SMD:SOT-23-5')
 s.net(k,'2','PWM_'+ch);s.net(k,'4','~{PWM_'+ch+'}');s.net(k,'5','+5V_A',2.54);s.net(k,'3','PGND',2.54);s.nc(k,'1')
 for unit,py,src,cn,op in [(1,ly,'PWM_'+ch,ch+'_DT_P',ch+'_DRIVE_P'),(2,ly+38.1,'~{PWM_'+ch+'}',ch+'_DT_N',ch+'_DRIVE_N')]:
  # Direct connections show diode cathode at source and anode at the RC node.
  count['R']+=1;rr='R'+str(count['R']);s.add('Device:R',rr,'330R',X(116.84),py,angle=90,foot=RFOOT,extra={'Function':'DEAD TIME TUNE'})
  for nm,dy in [('Reference',3.81),('Value',6.35)]:get(prop(s.comps[(rr,1)],nm),'at')[2]=str(py+dy)
  p=s.pp(rr);a=(X(99.06),py);b=(X(134.62),py);s.wire(a,p['1']);s.wire(p['2'],b);s.label(src,a);s.label(cn,b);s.intent[rr]={'1':src,'2':cn}
  count['D']=count.get('D',19)+1;dr='D'+str(count['D']);s.add('Device:D',dr,'1N4148W',X(116.84),py-10.16,foot='Diode_SMD:D_SOD-123',extra={'Datasheet':'https://www.diodes.com/datasheet/download/1N4148W.pdf','Function':'Fast discharge: K to source, A to Schmitt RC node'})
  p=s.pp(dr);s.wire(a,(a[0],py-10.16));s.wire((a[0],py-10.16),p['1']);s.wire(p['2'],(b[0],py-10.16));s.wire((b[0],py-10.16),b);s.dot(a);s.dot(b);s.intent[dr]={'1':src,'2':cn}
  passive(s,'C','100p C0G',X(144.78),py+12.7,cn,'PGND',extra={'Function':'DEAD TIME TUNE'})
  k=s.add('74xGxx:74LVC2G17',buf,'SN74LVC2G17DBVR',X(190.5),py,unit=unit,foot='Package_TO_SOT_SMD:SOT-23-6')
  s.net(k,'1' if unit==1 else '3',cn);s.net(k,'6' if unit==1 else '4',op)
  tp(s,op,X(234.95),py)
 s.text('DEAD TIME TUNE - 330R / 100pF, tau = 33 ns.\nDiode K at source, A at RC: slow rise / fast fall.\n20-30 ns is a tuning target, not a guaranteed dead time.',X(17.78),ly+60.96,1.05)
 # Default disabled; 1k pull-up option against 10k pulldown gives about 4.55 V when fitted.
 ey=ly+101.6
 passive(s,'R','10k',X(30.48),ey,'ENABLE_'+ch,'PGND')
 passive(s,'R','1k DNP',X(71.12),ey,'+5V_A','ENABLE_'+ch,dnp=True,extra={'Function':'Optional standalone enable pull-up'})
 tp(s,'ENABLE_'+ch,X(111.76),ey)
 bypass(s,'+5V_A',X(147.32),ey)
 s.text('Enable defaults LOW. Fit DNP 1k only for standalone enable.\n100n here belongs to '+inv+'; Schmitt package bypass is in IC POWER row.',X(17.78),ey+20.32,1.0)
 sid=uid();sx=X(198.12);sy=ly+78.74
 sh=['sheet',['at',str(sx),str(sy)],['size','73.66','33.02'],['stroke',['width','0.254'],['type','default']],['fill',['color','0','0','0','0']],['uuid',sid],pr('Sheetname',name+' OUTPUT',sx,sy-2.54),pr('Sheetfile','PowerOutput_'+ch+'.kicad_sch',sx,sy+35.56),['instances',['project',Q('DiscreteClassD'),['path',Q('/'+rid),['page',Q('2' if ch=='L' else '3')]]]]]
 for i,(n,net) in enumerate([('DRIVE_P',ch+'_DRIVE_P'),('DRIVE_N',ch+'_DRIVE_N'),('ENABLE','ENABLE_'+ch)]):
  py=sy+7.62+i*7.62;sh.append(['pin',Q(n),'input',['at',str(sx),str(py),'180'],ef(1),['uuid',uid()]])
  s.wire((sx-10.16,py),(sx,py));s.label(net,(sx-10.16,py))
 s.a.append(sh);return sid

def power_copy(ch,sid,mosfet,dest=ROOT):
 a=cp(oldpower);get(a,'uuid')[1]=uid();get(a,'title_block')[1:]=[['title',Q(('LEFT' if ch=='L' else 'RIGHT')+' BTL power output')],['rev',Q('Stereo Rev 1')]]
 get(a,'paper')[1]=Q('A3')
 # Remove unused control ICs off the original A3 page, plus power entry moved to main.
 def keep(z):
  if not isinstance(z,list):return True
  if z[0]=='symbol':return prop(z,'Reference')[2] not in ['U1','U3','U4','U5','IC1','J14','C17','TP9','TP10','TP11','#PWR01']
  pts=[]
  if get(z,'at'):pts=[tuple(map(float,get(z,'at')[1:3]))]
  elif z[0]=='wire':pts=[tuple(map(float,p[1:])) for p in get(z,'pts')[1:]]
  if pts and (all(x>450 for x,y in pts) or all(x>=180 and y>=200 for x,y in pts)):return False
  if z[0]=='wire' and set(pts)=={(340.36,165.1),(340.36,167.64)}:return False
  if z[0]=='label' and pts==[(340.36,165.1)]:return False
  return True
 a[:]=[z for z in a if keep(z)]
 # Preserve the physical stage; expose three controls and global power rails.
 cmap={'HI_A':'DRIVE_P','LI_A':'DRIVE_N','HI_B':'DRIVE_N','LI_B':'DRIVE_P','EN_A':'ENABLE','EN_B':'ENABLE'}
 for z in allof(a,'label'):
  if z[1] in cmap:z[1]=Q(cmap[z[1]])
  if z[1] in ['+24V','+12V_GD','PGND']:
   z[0]='global_label';z.insert(2,['shape','bidirectional']);get(z,'effects')[-1]=['justify','left'];at=get(z,'at');z.append(pr('Intersheetrefs','${INTERSHEET_REFS}',at[1],at[2],True))
 for z in allof(a,'text'):
  if 'HS / VSS' in z[1]:z[1]=Q('HS / VSS: Kelvin returns to respective MOSFET sources.\nComplementary DRIVE_P / DRIVE_N include external dead time.\nDNP diode cathode faces driver: optional faster turn-off path.')
 # All right-channel instances and object UUIDs are independent.
 refs={}
 for z in allof(a,'symbol'):
  ref=prop(z,'Reference')[2];new=re.sub(r'(\d+)$',lambda m:str(int(m[1])+100),ref) if ch=='R' else ref;refs[ref]=new
  prop(z,'Reference')[2]=Q(new)
  get(z,'instances')[1:]=[['project',Q('DiscreteClassD'),['path',Q('/'+rid+'/'+sid),['reference',Q(new)],['unit',get(z,'unit')[1]]]]]
  if ref=='J15':prop(z,'Value')[2]=Q(('LEFT' if ch=='L' else 'RIGHT')+' SPEAKER')
  if ref.startswith('Q') and mosfet=='DMN6070SY':
   prop(z,'Datasheet')[2]=Q('https://www.diodes.com/datasheet/download/DMN6070SY.pdf')
   z.append(pr('Pin verification','Diodes DS39440 Rev 3-2 page 1 top view matches SOT-89-3: 1=G, 2=D including tab, 3=S',hide=True))
  if ref.startswith('Q') and mosfet=='DMTH6016LPS':
   get(z,'lib_id')[1]=Q('DiscreteClassD:DMTH6016LPS');prop(z,'Value')[2]=Q('DMTH6016LPS');prop(z,'Footprint')[2]=Q('DiscreteClassD:DMTH6016LPS_PowerDI5060-8');prop(z,'Datasheet')[2]=Q('https://www.diodes.com/datasheet/download/DMTH6016LPS.pdf')
   z[:]=[x for x in z if not(isinstance(x,list) and x[0]=='pin')]
  if ch=='R':
   def uu(v):
    for e in v:
     if isinstance(e,list):
      if e[0]=='uuid':e[1]=uid()
      else:uu(e)
   uu(z)
 if ch=='R':
  for z in a:
   if isinstance(z,list) and z[0]!='symbol' and get(z,'uuid'):get(z,'uuid')[1]=uid()
 s=Sheet('temp',path='/'+rid+'/'+sid);s.a=a;s.used={get(z,'lib_id')[1] for z in allof(a,'symbol')};s.comps={(prop(z,'Reference')[2],int(get(z,'unit')[1])):z for z in allof(a,'symbol')};s.intent={r:{} for r,u in s.comps}
 for oldref in ['U2','U6']:
  p=s.pp(refs[oldref]);a9=(p['9'][0],p['9'][1]+5.08);a11=(p['11'][0],p['11'][1]+5.08)
  s.a[:]=[z for z in s.a if not(isinstance(z,list) and z[0]=='global_label' and tuple(map(float,get(z,'at')[1:3]))==a11)]
  s.wire(a9,a11);s.dot(a9)
 for i,n in enumerate(['DRIVE_P','DRIVE_N','ENABLE']):
  p=(208.28,220.98+i*15.24);q=(233.68,p[1]);s.label(n,p,'hierarchical_label');s.wire(p,q);s.label(n,q)
 s.text('CHANNEL CONTROL / SHARED SUPPLIES',182.88,207.01,1.6)
 s.text('Bridge A: HI = DRIVE_P, LI = DRIVE_N.\nBridge B: HI = DRIVE_N, LI = DRIVE_P.\nENABLE drives both EN pins. Defaults LOW on main.\n+24V / +12V_GD / PGND are global.\nSpeaker and switch nets remain local to this channel.\nPGND is the single board-wide 0 V reference.',274.32,214.63,1.0)
 # The internal bootstrap diode energizes HB from VDD; flags describe this real source.
 for n,x,ref in [('HB_A',200.66,'#FLG11' if ch=='L' else '#FLG111'),('HB_B',246.38,'#FLG12' if ch=='L' else '#FLG112')]:flag(s,n,x,269.24,ref)
 s.text('HB flags represent charging through each UCC27301A internal bootstrap diode.',182.88,281.94,.9)
 s.save(dest/('PowerOutput_'+ch+'.kicad_sch'));return s,refs

def build(dest,opa_rail,mosfet):
 dest.mkdir(exist_ok=True,parents=True)
 s=Sheet('24 V stereo BTL Class-D - shared analogue / control',paper='A1',rootid=rid)
 regulators(s);shared(s,opa_rail)
 ids={c:channel(s,c,0 if c=='L' else 294.64,304.8) for c in ['L','R']}
 s.section('STEREO LINE INPUT',619.76,17.78)
 s.text('OPA1656 U1 / U3: +12V_GD supply; VREF remains 2.5 V.\nDMN6070SY MOSFETs retained in both channels; G=1, D=2/tab, S=3.\nDEAD TIME TUNE: gate timing and regulator thermals require bench validation.',17.78,548.64,1.27)
 if opa_rail=='OPA_SUPPLY_PENDING':
  s.text('INCOMPLETE DRAFT - ENGINEERING DECISIONS PENDING\nOPA1656 supply unassigned: +5 V common-mode range is insufficient.\nSaved DMN6070SY retained provisionally; AGENTS.md specifies DMTH6016LPS.',17.78,548.64,1.5)
 s.add('Connector:Conn_01x03_Socket','J1','STEREO LINE INPUT',660.4,43.18,foot='Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical')
 for p,n in [('1','LEFT_IN'),('2','PGND'),('3','RIGHT_IN')]:s.net('J1',p,n)
 s.text('Pin 1 LEFT_IN / pin 2 PGND / pin 3 RIGHT_IN\nNominal 2 Vrms source; 47k / 10k input attenuators.\nBoth channels use the same VREF and triangle carrier.',619.76,60.96,1.27)
 s.section('IC ALLOCATION / REV 1',619.76,104.14)
 s.text('U1A: LEFT input follower\nU1B: RIGHT input follower\nU3A: VREF_2V5 buffer\nU3B: shared triangle integrator\n\nU7A: oscillator Schmitt comparator\nU7B: LEFT PWM comparator\nU8A: RIGHT PWM comparator\nU8B: spare; inputs tied, output open\n\nU4 / U5: LEFT inverter / dual Schmitt buffer\nU9 / U10: RIGHT inverter / dual Schmitt buffer\nU11: +24V to +12V_GD TPS7A4901\nU12: +24V to +5V_A TPS7A4901\n\nU2 / U6: LEFT UCC27301A gate drivers\nU102 / U106: RIGHT UCC27301A gate drivers\n\nTotal: 14 IC packages, 8 power MOSFETs.',619.76,116.84,1.27)
 s.section('DESIGN / COMMISSIONING NOTES',619.76,248.92)
 s.text('Open-loop Rev 1; no audio feedback or protection.\nTarget 30 W/channel into 8 ohms at +24 V.\nPower target and timing require bench validation.\n\nInput attenuation = 10k / (47k + 10k) = 0.17544.\nAC corner = 1 / (2 pi x 57k x 220n) = 12.69 Hz.\nRF pole approx. 193 kHz from (47k || 10k) / 100p.\n2 Vrms input gives 0.351 Vrms / 0.496 Vpk modulation.\n\nNon-inverting Schmitt + inverting integrator:\nVtri = Vref + (10k / 49k9) x (Vref - Vsquare).\nf = 49k9 / (4 x 10k x 3k09 x 1n) = 403.722 kHz.\nComparator delay, hysteresis and op-amp dynamics\nchange actual amplitude / period. Measure and tune.\n\nDead time is provisional: RC tau = 33 ns.\nIdeal rise to 2.5 V takes 22.9 ns at a 5 V source.\nThreshold spread, propagation skew, diode current,\nparasitics, driver and MOSFET switching all matter.\nMeasure all eight gates before selecting final timing.\n\nBoth channels default DISABLED (10k pulldowns).\nDNP 1k pullups permit later standalone enabling.\n\nPGND is the single global board-wide 0 V reference.\nSpeaker outputs float; do not ground either terminal.\nBulk capacitors are shared; local stage bypass stays.\n\nMetric SMD R/C land patterns assigned, no placement.\nFilm/filter capacitor MPNs and thermals need checking\nbefore PCB layout / manufacture.',619.76,261.62,1.15)
 s.a.append(['sheet_instances',['path',Q('/'),['page',Q('1')]]])
 s.save(dest/'DiscreteClassD.kicad_sch')
 children={}
 for c in ['L','R']:children[c]=power_copy(c,ids[c],mosfet,dest)[0]
 # A local copy of the verified symbols makes the schematic portable.
 loc=cp(local)
 for id in ['DiscreteClassD:TPS7A4901DGNR','DiscreteClassD:TLV3602DGKR']:
  z=cp(libs[id]);z[1]=Q(id.split(':')[1]);loc.append(z)
 (dest/'DiscreteClassD.kicad_sym').write_text(dump(loc)+'\n')
 (dest/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "DiscreteClassD") (type "KiCad") (uri "${KIPRJMOD}/DiscreteClassD.kicad_sym") (options "") (descr "Project-local verified amplifier symbols")))\n')
 (ROOT/'output/verification/stereo-final/intended-main.json').write_text(json.dumps(s.intent,indent=2))
 print('Wrote',dest,'main',len(s.comps),'symbol units; power',[(c,len(ch.comps)) for c,ch in children.items()])

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--prepare',action='store_true');ap.add_argument('--draft',action='store_true');ap.add_argument('--opa-rail',choices=['+5V_A','+12V_GD','OPA_SUPPLY_PENDING'],default='OPA_SUPPLY_PENDING');ap.add_argument('--mosfet',choices=['DMN6070SY','DMTH6016LPS'],default='DMN6070SY');args=ap.parse_args()
 if args.prepare:
  s=Sheet('Stereo control - regulator preparation',rootid=rid);regulators(s);s.save(BASE/'regulator-preparation.kicad_sch')
  print('Prepared verified regulator circuitry without changing working schematic.')
 else:build(ROOT/'output/verification/stereo-draft' if args.draft else ROOT,args.opa_rail,args.mosfet)

"""Rebuild ONLY output stage from preserved baseline; do not rerun after manual edits."""
from pathlib import Path
from copy import deepcopy as cp
import uuid, math, json
from sexp import *
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'output/verification/DiscreteClassD.before-output-stage.kicad_sch'
a=parse(BASE.read_text()); rootid=get(a,'uuid')[1]
uid=lambda:Q(str(uuid.uuid4()))
sheetid=Q('99d915ba-7acf-4db8-8201-984b0c5ab123'); childid=Q('ee0d932c-82bb-42e1-bc04-2b5d78c21d66')
path=Q('/'+rootid+'/'+sheetid)
libs={x[1]:cp(x) for x in allof(get(a,'lib_symbols'),'symbol')}
original={prop(x,'Reference')[2]:x for x in allof(a,'symbol')}
libroot=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols')
def loadlib(id):
 if id not in libs:
  lib,name=id.split(':'); src=parse((libroot/(lib+'.kicad_sym')).read_text()); z=cp(next(x for x in allof(src,'symbol') if x[1]==name)); z[1]=Q(id); libs[id]=z
 return libs[id]
def effects(size=1.27,justify=None):
 e=['effects',['font',['size',str(size),str(size)]]]
 if justify:e.append(['justify',*justify.split()])
 return e
def property_(name,value,x=0,y=0,hide=False):
 p=['property',Q(name),Q(value),['at',str(x),str(y),'0'],effects()]
 if hide:p.insert(4,['hide','yes'])
 return p
def pin(name,n,x,y,ang,typ='passive',hide=False):
 p=['pin',typ,'line',['at',str(x),str(y),str(ang)],['length','2.54'],['name',Q(name),effects(1.0)],['number',Q(n),effects(1.0)]]
 if hide:p.insert(3,['hide','yes'])
 return p
# Correct existing driver drawing for functional readability; physical pin numbers unchanged.
id='DiscreteClassD:UCC27301ADRCR'; name=id.split(':')[1]
z=cp(libs['Custom:UCC27301ADRCR']); z[1]=Q(id)
for s in allof(z,'symbol'):z.remove(s)
z.append(['symbol',Q(name+'_0_1'),['rectangle',['start','-10.16','12.7'],['end','10.16','-12.7'],['stroke',['width','0'],['type','default']],['fill',['type','background']]]])
z.append(['symbol',Q(name+'_1_1'),pin('VDD','1',0,15.24,270,'power_in'),pin('NC','2',-12.7,-10.16,0,'no_connect'),pin('HB','3',12.7,10.16,180,'power_in'),pin('HO','4',12.7,5.08,180,'output'),pin('HS','5',12.7,0,180,'passive'),pin('EN','6',-12.7,-5.08,0,'input'),pin('HI','7',-12.7,5.08,0,'input'),pin('LI','8',-12.7,0,0,'input'),pin('VSS','9',0,-15.24,90,'power_in'),pin('LO','10',12.7,-5.08,180,'output'),pin('EP','11',5.08,-15.24,90,'power_in')])
prop(z,'Value')[2]=Q(name); prop(z,'Datasheet')[2]=Q('https://www.ti.com/lit/ds/symlink/ucc27301a.pdf'); libs[id]=z
# Reuse original MOSFET graphics, expose package numbering and all package contacts.
id='DiscreteClassD:DMTH6016LPS'; z=cp(libs['Transistor_FET:Q_NMOS_GDS']); z[1]=Q(id)
for s in allof(z,'symbol'):
 s[1]=Q(s[1].replace('Q_NMOS_GDS','DMTH6016LPS'))
 for p in allof(s,'pin'):
  old=get(p,'number')[1]; get(p,'number')[1]=Q({'1':'4','2':'5','3':'1'}[old]); get(p,'name')[1]=Q({'1':'G','2':'D','3':'S'}[old])
  if old in ['2','3']:
   get(p,'name')[1]=Q('D (5-8)' if old=='2' else 'S (1-3)')
   for n in (['6','7','8'] if old=='2' else ['2','3']):
    pp=cp(p); get(pp,'number')[1]=Q(n); pp.insert(3,['hide','yes']); s.append(pp)
prop(z,'Value')[2]=Q('DMTH6016LPS'); prop(z,'Datasheet')[2]=Q('https://www.diodes.com/datasheet/download/DMTH6016LPS.pdf'); libs[id]=z
child=['kicad_sch',['version','20260306'],['generator',Q('eeschema')],['generator_version',Q('10.0')],['uuid',childid],['paper',Q('A3')],['title_block',['title',Q('24 V / 30 W mono BTL - power and output stage')],['rev',Q('PS1')]],['lib_symbols']]
used=set(); comps={}; intended={}
def add(id,ref,val,x,y,angle=0,foot='',old=None,dnp=False,extra=None):
 lib=loadlib(id); used.add(id)
 s=['symbol',['lib_id',Q(id)],['at',str(x),str(y),str(angle)],['unit','1'],['in_bom','no' if dnp else 'yes'],['on_board','yes'],['dnp','yes' if dnp else 'no'],['uuid',get(original[old],'uuid')[1] if old else uid()]]
 # Compact fields beside vertical passives, above horizontal parts.
 if id.startswith('Device:') and angle==0:fx,fy=x+3.0,y-1.5; justify='left'
 else:fx,fy=x,y-5.5; justify=None
 for nm,v,px,py,h in [('Reference',ref,fx,fy,False),('Value',val,fx,fy+2.4,False),('Footprint',foot,x,y,True),('Datasheet',str(prop(lib,'Datasheet')[2]) if prop(lib,'Datasheet') else '',x,y,True)]:
  p=property_(nm,v,px,py,h)
  if not h:
   if angle in [90,270]:get(p,'at')[3]=str(angle)
   get(p,'effects')[1][1][1:]=['1','1']
   if justify:get(p,'effects').append(['justify','left'])
  s.append(p)
 if id=='Device:D':
  for pn,yy in [('Reference',y-5.08),('Value',y-2.54)]:get(prop(s,pn),'at')[1:]=[str(x),str(yy),'0']
 if id=='Connector:TestPoint':
  for pn,yy in [('Reference',y-5.08),('Value',y-2.54)]:
   get(prop(s,pn),'at')[1:]=[str(x+3.81),str(yy),'0'];get(prop(s,pn),'effects').append(['justify','left'])
 for k,v in (extra or {}).items():
  if prop(s,k):prop(s,k)[2]=Q(v)
  else:s.append(property_(k,v,x,y,True))
 if dnp:s.append(property_('Population','DNP - omit from default assembly',x,y,True))
 s.append(['instances',['project',Q('DiscreteClassD'),['path',path,['reference',Q(ref)],['unit','1']]]])
 child.append(s);comps[ref]=s;intended[ref]={};return ref
def pins(ref):
 s=comps[ref]; lib=libs[get(s,'lib_id')[1]]; x,y,angle=map(float,get(s,'at')[1:]);r=math.radians(angle);out={}
 for sub in allof(lib,'symbol'):
  for p in allof(sub,'pin'):
   px,py=map(float,get(p,'at')[1:3]); out[get(p,'number')[1]]=(round(x+px*math.cos(r)-py*math.sin(r),4),round(y-px*math.sin(r)-py*math.cos(r),4))
 return out
def wire(p,q):
 if p==q:return
 assert p[0]==q[0] or p[1]==q[1],(p,q)
 child.append(['wire',['pts',['xy',*map(str,p)],['xy',*map(str,q)]],['stroke',['width','0'],['type','default']],['uuid',uid()]])
def label(net,p,angle=0):child.append(['label',Q(net),['at',*map(str,p),str(angle)],effects(1.0,'left bottom'),['uuid',uid()]])
def dot(p):child.append(['junction',['at',*map(str,p)],['diameter','0'],['color','0','0','0','0'],['uuid',uid()]])
def text_(s,x,y,size=1.27):child.append(['text',Q(s),['at',str(x),str(y),'0'],effects(size,'left top'),['uuid',uid()]])
def netpin(ref,n,net,dx=0,dy=0):
 p=pins(ref)[str(n)];q=(round(p[0]+dx,4),round(p[1]+dy,4));wire(p,q);label(net,q);intended[ref][str(n)]=net;return q
def nc(ref,n):child.append(['no_connect',['at',*map(str,pins(ref)[str(n)])],['uuid',uid()]])
def two(ref,n1,n2):
 ps=pins(ref); keys=list(ps); netpin(ref,keys[0],n1,dy=-2.54); netpin(ref,keys[1],n2,dy=2.54)
rfoot='Resistor_SMD:R_0805_2012Metric';cfoot='Capacitor_SMD:C_0805_2012Metric';dfoot='Diode_SMD:D_SOD-123'
ufoot='Package_SON:VSON-10-1EP_3x3mm_P0.5mm_EP1.65x2.4mm';qfoot='DiscreteClassD:DMTH6016LPS_PowerDI5060-8'
tpfoot='TestPoint:TestPoint_Pad_D1.5mm'; tpnum=0

def tp(net,x,y):
 global tpnum
 tpnum+=1;ref=add('Connector:TestPoint',f'TP{tpnum}',net,x,y,foot=tpfoot);netpin(ref,'1',net,dy=2.54)

for b,ox,U,QH,QL,ci,ri,di in [('A',0,'U2','Q1','Q2',1,1,1),('B',200.66,'U6','Q3','Q4',7,7,3)]:
 X=lambda x:round(x+ox,4)
 text_('HALF BRIDGE '+b,X(20.32),15.24,2)
 add('DiscreteClassD:UCC27301ADRCR',U,'UCC27301ADRCR',X(50.8),71.12,foot=ufoot,old='U2' if b=='A' else None)
 for pn,yy in [('Reference',43.18),('Value',45.72)]:get(prop(comps[U],pn),'at')[1:]=[str(X(50.8)),str(yy),'0']
 # Driver supply, logic and output stubs; HB and HS directly wired to bootstrap.
 netpin(U,'1','+12V_GD',dy=-5.08)
 for n,name in [('7','HI_'),('8','LI_'),('6','EN_')]:netpin(U,n,name+b,dx=-10.16)
 nc(U,'2'); netpin(U,'4','HO_'+b,dx=5.08);netpin(U,'10','LO_'+b,dx=5.08)
 for n in ['9','11']:netpin(U,n,'PGND',dy=5.08)
 # Bootstrap at x81.28, center HB / HS.
 cref=f'C{ci}'; add('Device:C',cref,'100n / 25V',X(81.28),66.04,foot=cfoot,old='C1' if b=='A' else None,extra={'Dielectric':'X7R','Function':'Bootstrap HB-HS'})
 hb=pins(U)['3'];hs=pins(U)['5'];cpins=pins(cref)
 wire(hb,(X(81.28),hb[1]));wire((X(81.28),hb[1]),cpins['1']);wire(cpins['2'],(X(81.28),hs[1]));wire(hs,(X(81.28),hs[1]));label('HB_'+b,(X(81.28),hb[1]));label('SW_'+b,(X(81.28),hs[1]));intended[U].update({'3':'HB_'+b,'5':'SW_'+b});intended[cref]={'1':'HB_'+b,'2':'SW_'+b}
 # Pair displayed vertically. Generic graphics gate x-5.08 and drain/source x+2.54.
 for ref,qy,is_hi,k in [(QH,48.26,True,0),(QL,99.06,False,1)]:
  gate=('GH_' if is_hi else 'GL_')+b; drive=('HO_' if is_hi else 'LO_')+b; source='SW_'+b if is_hi else 'PGND'; drain='+24V' if is_hi else 'SW_'+b
  add('DiscreteClassD:DMTH6016LPS',ref,'DMTH6016LPS',X(139.7),qy,foot=qfoot,old=ref if b=='A' else None)
  # fields beside FET, clear of gate and drain/source wires
  for pn,yy in [('Reference',qy-1.27),('Value',qy+1.27)]:
   p=prop(comps[ref],pn);get(p,'at')[1:]=[str(X(146.05)),str(yy),'0'];get(p,'effects').append(['justify','left'])
  p=pins(ref);gy=p['4'][1];main=f'R{ri+k*3}';pull=f'R{ri+k*3+1}';alt=f'R{ri+k*3+2}';dio=f'D{di+k}'
  add('Device:R',main,'10R',X(114.3),gy,angle=90,foot=rfoot)
  rp=pins(main);wire(rp['2'],p['4']);netpin(main,'1',drive,dx=-7.62);label(gate,p['4']);intended[main]['2']=gate;intended[ref]['4']=gate
  # source resistor branch down from gate, separate source reference label.
  add('Device:R',pull,'47k',X(129.54),round(gy+15.24,4),foot=rfoot)
  wire((X(129.54),gy),pins(pull)['1']);dot((X(129.54),gy));netpin(pull,'2',source,dy=2.54);intended[pull]['1']=gate
  # DNP turn-off branch: gate -> Ralt -> diode anode, cathode -> driver.
  ay=round(gy-12.7,4);add('Device:D',dio,'DNP diode',X(104.14),ay,foot=dfoot,dnp=True,extra={'Requirement':'Fast diode >=30V; pulse-current rating to be selected; cathode faces driver'})
  add('Device:R',alt,'10R DNP',X(119.38),ay,angle=90,foot=rfoot,dnp=True)
  netpin(dio,'1',drive,dx=-5.08);wire(pins(dio)['2'],pins(alt)['1']);netpin(alt,'2',gate,dx=5.08);intended[dio]['2']='ALT_'+ref;intended[alt].update({'1':'ALT_'+ref,'2':gate})
  for n in ['1','2','3']:intended[ref][n]=source
  for n in ['5','6','7','8']:intended[ref][n]=drain
 # Continuous +24V -> QH -> SW -> QL -> PGND column.
 h=pins(QH);l=pins(QL);netpin(QH,'5','+24V',dy=-7.62);wire(h['1'],l['5']);label('SW_'+b,(h['1'][0],76.2));netpin(QL,'1','PGND',dy=7.62)
 # local driver and bridge decoupling across named rails
 for j,(val,vol,die,foot,net) in enumerate([('100n','25V','X7R',cfoot,'+12V_GD'),('4u7','25V','X7R',cfoot,'+12V_GD'),('100n','50V','X7R',cfoot,'+24V'),('1u','50V','X7R','Capacitor_SMD:C_1206_3216Metric','+24V'),('10u','50V','X7R','Capacitor_SMD:C_1210_3225Metric','+24V')],1):
  ref=f'C{ci+j}';xx=X(25.4+(j-1)*27.94);add('Device:C',ref,val+' / '+vol,xx,144.78,foot=foot,extra={'Dielectric':die,'Layout':'Adjacent to '+U if j<3 else 'Small local +24V / MOSFET / PGND loop','Requirement':'Verify effective capacitance under DC bias'});two(ref,net,'PGND')
 text_('Driver bypass: at VDD/VSS',X(20.32),127,1.27);text_('Local 24 V power loop ceramics',X(81.28),127,1.27)
 # snubber
 ref=f'R{13 if b=="A" else 14}';cap=f'C{13 if b=="A" else 14}'
 add('Device:R',ref,'10R DNP',X(175.26),83.82,foot='Resistor_SMD:R_1206_3216Metric',dnp=True);netpin(ref,'1','SW_'+b,dy=-5.08)
 add('Device:C',cap,'330p DNP',X(175.26),101.6,foot=cfoot,dnp=True,extra={'Voltage':'100V','Dielectric':'C0G','Requirement':'Tune after ringing measurement'})
 wire(pins(ref)['2'],pins(cap)['1']);netpin(cap,'2','PGND',dy=5.08);intended[ref]['2']='SNUB_'+b;intended[cap]['1']='SNUB_'+b
 for n,xx in [('SW_',20.32),('HO_',48.26),('LO_',76.2)]:tp(n+b,X(xx),172.72)
 text_('HS / VSS: Kelvin returns to respective MOSFET sources.\nGate loops short. EN defaults disabled; HI/LI await dead-time logic.\nDNP diode cathode faces driver: optional faster turn-off path.',X(20.32),186.69,1.05)
# Filter and connectors, preserved output part for now verified below.
text_('DIFFERENTIAL OUTPUT / 8 OHM SPEAKER',20.32,207.01,1.8)
add('Device:L_Coupled_1243','L6','CSAD0660-100M',55.88,231.14,foot='DiscreteClassD:CSAD0660-100M',old='L6',extra={'Datasheet':'https://www.codaca.com/Private/pdf/CSAD0660.pdf','Inductance':'2 x 10uH','Verification':'Verified: Codaca CSAD0660.pdf page 1, revised 2020-07-14; windings 1-2 and 4-3'})
for pn,yy in [('Reference',219.71),('Value',222.25)]:get(prop(comps['L6'],pn),'at')[1:]=['55.88',str(yy),'0']
for n,net in [('1','SW_A'),('2','OUT_A'),('4','SW_B'),('3','OUT_B')]:netpin('L6',n,net,dx=-10.16 if n in ['1','4'] else 10.16)
add('Device:C','C15','330n',93.98,231.14,foot='Capacitor_SMD:C_2220_5750Metric',extra={'Voltage':'100V','Dielectric':'Low-loss C0G / SMD film only','Requirement':'Provisional 5750 metric land pattern; exact stock/parallel realization and ripple rating to be selected'})
two('C15','OUT_A','OUT_B')
add('Device:R','R15','10R / 1W',129.54,220.98,foot='Resistor_SMD:R_2512_6332Metric',extra={'Requirement':'Non-inductive; verify heating at switching residual and full output'})
add('Device:C','C16','100n / 100V',129.54,238.76,foot='Capacitor_SMD:C_1210_3225Metric',extra={'Dielectric':'C0G or SMD film','Requirement':'Exact low-loss part to be selected'})
netpin('R15','1','OUT_A',dy=-2.54);wire(pins('R15')['2'],pins('C16')['1']);netpin('C16','2','OUT_B',dy=2.54);intended['R15']['2']='ZOBEL';intended['C16']['1']='ZOBEL'
add('Connector:Conn_01x02_Socket','J15','SPEAKER OUT',160.02,228.6,foot='DiscreteClassD:Power_Input_2_SMD',old='J15')
netpin('J15','1','OUT_A',dx=-5.08);netpin('J15','2','OUT_B',dx=-5.08)
text_('Speaker floats: neither terminal connects to PGND.\nL6: 10uH per winding; verified pins 1-2 and 4-3.',20.32,250.19,1.05)
for net,xx in [('OUT_A',50.8),('OUT_B',88.9)]:tp(net,xx,266.7)
# Input supplies and bulk
text_('POWER ENTRY',182.88,207.01,1.8)
add('Connector:Conn_01x02_Socket','J14','24V INPUT',198.12,223.52,foot='DiscreteClassD:Power_Input_2_SMD',old='J14')
netpin('J14','1','+24V',dx=-5.08);netpin('J14','2','PGND',dx=-5.08)
add('Device:C_Polarized','C17','1000u / 35V FR',228.6,226.06,foot='Capacitor_THT:CP_Radial_D12.5mm_P5.00mm',extra={'MPN':'EEUFR1V102','Manufacturer':'Panasonic','Datasheet':'https://na.industrial.panasonic.com/products/capacitors/aluminum-electrolytic-capacitors/series/83367/model/83808'})
two('C17','+24V','PGND')
# supply entry as SMD pads, retains no additional THT exception
add('Connector:Conn_01x02_Socket','J16','12V GD INPUT',198.12,246.38,foot='DiscreteClassD:Power_Input_2_SMD')
netpin('J16','1','+12V_GD',dx=-5.08);netpin('J16','2','PGND',dx=-5.08)
for net,xx in [('+24V',185.42),('+12V_GD',220.98),('PGND',251.46)]:tp(net,xx,266.7)
# Explicit board layout requirements.
text_('PCB CONSTRAINTS / LATER WORK',279.4,207.01,1.6)
text_('Place each driver against its MOSFET pair.\nMinimize gate loops and local 24 V ceramic loops.\nHS Kelvin to high-side source; VSS Kelvin to low-side source.\nKeep SW_A / SW_B copper compact.\nNo ground plane under large switch-node copper.\nPlace L6 close to bridges. Keep HI / LI away from SW copper.\nKeep PGND distinct from analogue ground.\nGate drive requires bootstrap refresh / suitable duty limits.\nNo PWM, dead-time, feedback or protection designed here.\n+5V_A is reserved for future controls; not used on this sheet.',279.4,214.63,1.05)
# Library output
for id in sorted(used):get(child,'lib_symbols').append(cp(libs[id]))
(ROOT/'PowerOutput.kicad_sch').write_text(dump(child)+'\n')
# Remove only prior output-stage objects; leave every unrelated symbol and its original attributes intact.
outputrefs={'U2','Q1','Q2','C1','L6','J14','J15','#PWR01','#PWR02','#PWR03'}
# All baseline wires/labels have been audited visually as output-stage-only.
a[:]=[x for x in a if not (isinstance(x,list) and (x[0] in ['wire','label'] or (x[0]=='symbol' and prop(x,'Reference')[2] in outputrefs)))]
a.append(['sheet',['at','50.8','35.56'],['size','152.4','45.72'],['stroke',['width','0'],['type','default']],['fill',['color','0','0','0','0']],['uuid',sheetid],property_('Sheetname','Power output stage',50.8,34.29),property_('Sheetfile','PowerOutput.kicad_sch',50.8,82.55),['instances',['project',Q('DiscreteClassD'),['path',Q('/'+rootid),['page',Q('2')]]]]])
a.append(['text',Q('Output stage is on hierarchical sheet 2.\nExisting control and analogue symbols remain unchanged.'),['at','50.8','88.9','0'],effects(1.27,'left top'),['uuid',uid()]])
# Preserve original text for every unchanged top-level object, including unrelated symbols.
raw=BASE.read_text(); depth=0; quoted=False; escaped=False; start=0; chunks=[]
for i,c in enumerate(raw):
 if quoted:
  if escaped:escaped=False
  elif c=='\\':escaped=True
  elif c=='\"':quoted=False
  continue
 if c=='\"':quoted=True
 elif c=='(':
  if depth==1:start=i
  depth+=1
 elif c==')':
  depth-=1
  if depth==1:chunks.append(raw[start:i+1])
rawmap={dump(parse(t)):t for t in chunks}
(ROOT/'DiscreteClassD.kicad_sch').write_text('(kicad_sch\n'+'\n'.join('\t'+rawmap.get(dump(x),dump(x,1)) for x in a[1:])+'\n)\n')
local=['kicad_symbol_lib',['version','20241209'],['generator',Q('kicad_symbol_editor')]]
for id in sorted(used):
 if id.startswith('DiscreteClassD:'):
  z=cp(libs[id]);z[1]=Q(id.split(':')[1]);local.append(z)
(ROOT/'DiscreteClassD.kicad_sym').write_text(dump(local)+'\n')
(ROOT/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "DiscreteClassD") (type "KiCad") (uri "${KIPRJMOD}/DiscreteClassD.kicad_sym") (options "") (descr "Verified output-stage symbols")))\n')
(ROOT/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "DiscreteClassD") (type "KiCad") (uri "${KIPRJMOD}/DiscreteClassD.pretty") (options "") (descr "Project-local output-stage footprints")))\n')
pretty=ROOT/'DiscreteClassD.pretty';pretty.mkdir(exist_ok=True)
# Copy existing local footprint geometry; restore physical MOSFET pad numbering.
f=parse(Path('/Users/tomwatson/Downloads/Custom.pretty/DMTH6016LPSQ.kicad_mod').read_text());f[1]=Q('DMTH6016LPS_PowerDI5060-8')
for p in allof(f,'pad'):
 x,y=map(float,get(p,'at')[1:3]);old=p[1]
 if old=='1':p[1]=Q('4')
 elif old=='3':p[1]=Q({-1.905:'1',-.635:'2',.635:'3'}[x])
 else:p[1]=Q({-1.905:'8',-.635:'7',.635:'6',1.905:'5'}[x] if x else '5')
prop(f,'Value')[2]=Q('DMTH6016LPS_PowerDI5060-8');(pretty/'DMTH6016LPS_PowerDI5060-8.kicad_mod').write_text(dump(f)+'\n')
f=parse(Path('/Users/tomwatson/Downloads/Custom.pretty/CSAD0660-100M.kicad_mod').read_text())
for p in allof(f,'pad'):
 n=p[1]; x,y={'1':(-1.625,-2.6),'2':(-1.625,2.6),'3':(1.625,2.6),'4':(1.625,-2.6)}[n];get(p,'at')[1:]=[str(x),str(y)];get(p,'size')[1:]=['2.65','2.6']
(pretty/'CSAD0660-100M.kicad_mod').write_text(dump(f)+'\n')
f=['footprint',Q('Power_Input_2_SMD'),['version','20241229'],['generator',Q('pcbnew')],['layer',Q('F.Cu')],['attr','smd'],['property',Q('Reference'),Q('REF**'),['at','0','-3','0'],['layer',Q('F.SilkS')],effects(1)],['property',Q('Value'),Q('Power_Input_2_SMD'),['at','0','3','0'],['layer',Q('F.Fab')],effects(1)]]
for n,y in [('1',-2),('2',2)]:f.append(['pad',Q(n),'smd','rect',['at','0',str(y)],['size','3','2.5'],['layers',Q('F.Cu'),Q('F.Paste'),Q('F.Mask')]])
(pretty/'Power_Input_2_SMD.kicad_mod').write_text(dump(f)+'\n')
(ROOT/'output/verification/intended-connections.json').write_text(json.dumps(intended,indent=2))
print('Generated output stage:',len(comps),'components;',len(used),'symbol types')

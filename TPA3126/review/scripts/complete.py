from schlib import *
import shutil
BASE=Path('.')
ROOT=load('review/original/TPA3126.kicad_sch'); ROOTID=get(ROOT,'uuid')[1]
ORIG={f:load('review/original/'+f+'.kicad_sch') for f in ['TPA3126','ESP32','DAC','Amp','Power']}
SHEETS={val(s,'Sheetfile').split('.')[0]:get(s,'uuid')[1] for s in many(ROOT,'sheet')}
STD=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols')
FPSTD=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints')
RFP='Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder'
CFP='Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder'
C2FP='Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder'
FILM='Capacitor_THT:C_Rect_L7.2mm_W5.0mm_P5.00mm'
MKP='Capacitor_THT:C_Rect_L7.2mm_W8.5mm_P5.00mm_FKP2_FKP2_MKS2_MKP2'
MOL='Connector_Molex:Molex_KK-396_A-41791-0002_1x02_P3.96mm_Vertical'
TPFP='TestPoint:TestPoint_Pad_D1.5mm'
num=lambda v:S(str(round(v,6)))
def uid():return str(uuid.uuid4())
def a(k,*v):return [S(k),*v]
def xy(k,x,y,*v):return a(k,num(x),num(y),*v)
def effect(size=1.27,justify=None,hide=False):
 z=a('effects',a('font',a('size',num(size),num(size))))
 if justify:z.append(a('justify',*[S(j) for j in justify.split()]))
 if hide:z.append(a('hide',S('yes')))
 return z
def wire(n,*pts):
 for p,q in zip(pts,pts[1:]):
  if p!=q:n.append(a('wire',a('pts',xy('xy',*p),xy('xy',*q)),a('stroke',a('width',S('0')),a('type',S('default'))),a('uuid',uid())))
def junction(n,p):n.append(a('junction',xy('at',*p),a('diameter',S('0')),a('color',S('0'),S('0'),S('0'),S('0')),a('uuid',uid())))
def label(n,name,x,y,angle=0,kind='label',direction='input'):
 z=a(kind,name)
 if kind=='hierarchical_label':z.append(a('shape',S(direction)))
 z.extend([xy('at',x,y,S(str(angle))),effect(1.27,('left' if angle==0 else 'right')+(' bottom' if kind=='label' else '')),a('uuid',uid())]);n.append(z);return z
def note(n,t,x,y,size=1.27):n.append(a('text',t,a('exclude_from_sim',S('no')),xy('at',x,y,S('0')),effect(size,'left top'),a('uuid',uid())))
def lib(n,id):
 ls=get(n,'lib_symbols');old=next((x for x in many(ls,'symbol') if x[1]==id),None)
 if old:return old
 for orig in ORIG.values():
  found=next((x for x in many(get(orig,'lib_symbols'),'symbol') if x[1]==id),None)
  if found:r=copy.deepcopy(found);ls.append(r);return r
 category,name=id.split(':');st=load(STD/(category+'.kicad_sym'))
 r=copy.deepcopy(next(x for x in many(st,'symbol') if x[1]==name))
 ext=get(r,'extends')
 if ext:
  base=copy.deepcopy(next(x for x in many(st,'symbol') if x[1]==ext[1]));base[1]=name
  for p in many(r,'property'):
   oldp=prop(base,p[1]);
   if oldp:base.remove(oldp)
   base.append(p)
  r=base
 r[1]=id;ls.append(r);return r
def instance(n,id,ref,value,x,y,angle=0,fp='',mpn='',sheet='',dnp=False,on_board=True):
 l=lib(n,id)
 z=a('symbol',a('lib_id',id),xy('at',x,y,S(str(angle))),a('unit',S('1')),a('exclude_from_sim',S('no')),a('in_bom',S('no') if ref.startswith('#') else S('yes')),a('on_board',S('yes') if on_board else S('no')),a('dnp',S('yes') if dnp else S('no')),a('uuid',uid()))
 for key,value1 in [('Reference',ref),('Value',value),('Footprint',fp),('Datasheet',val(l,'Datasheet') or ''),('MPN',mpn)]:
  z.append(a('property',key,value1,xy('at',x+(3.5 if angle==0 else 0),y+({'Reference':-1.4,'Value':1.4}.get(key,0)),S('0')),effect(1.0,'left' if angle==0 else None,hide=key not in ['Reference','Value'])))
 path='/'+ROOTID+('/'+SHEETS[sheet] if sheet else '')
 z.append(a('instances',a('project','TPA3126',a('path',path,a('reference',ref),a('unit',S('1'))))))
 n.append(z);return z
def existing(n,ref):return next(x for x in many(n,'symbol') if val(x,'Reference')==ref)
def setp(s,k,v):
 p=prop(s,k)
 if p:p[2]=v
 else:s.append(a('property',k,v,xy('at',0,0,S('0')),effect(hide=True)))
def pxy(n,s,p):return next((x,y) for pin,name,x,y,typ in pins(n,s) if pin==str(p))
def sref(n,r,p):return pxy(n,existing(n,r),p)
def gnd(n,x,y,rot=0):
 ref='#PWR'+str(300+sum(len(many(v,'symbol')) for v in ORIG.values())+len(many(n,'symbol')))
 z=instance(n,'power:GND',ref,'GND',x,y,rot,sheet=CURRENT)
 # Use standard library positions for a properly oriented GND graphic/value.
 for p in many(z,'property'):
  if p[1] in ['Reference','Value']:
   get(p,'at')[1:]=[num(x),num(y+(3.81 if rot==0 else -3.81)),S('0')]
   ef=get(p,'effects')
   ef[:]=effect(1.0,hide=p[1]=='Reference')
 return z
def resistor(n,ref,value,x,y,angle=0,mpn=''):
 return instance(n,'Device:R',ref,value,x,y,angle,RFP,mpn,CURRENT)
def cap(n,ref,value,x,y,angle=0,fp=CFP,mpn='',dnp=False):
 return instance(n,'Device:C',ref,value,x,y,angle,fp,mpn,CURRENT,dnp)
def flag(n,x,y,ref):return instance(n,'power:PWR_FLAG',ref,'PWR_FLAG',x,y,0,sheet=CURRENT)
def tp(n,ref,name,x,y):return instance(n,'Connector:TestPoint',ref,name,x,y,0,TPFP,'',CURRENT)
def remove(n,*k):n[:]=[x for x in n if not(isinstance(x,list) and x[0] in k)]
def reset_canvas(n):remove(n,'wire','junction','label','hierarchical_label','text','no_connect')
def nc(n,p):n.append(a('no_connect',xy('at',*p),a('uuid',uid())))
def snap(n):
 # Schematic connection geometry uses 50 mil grid. Property and library graphics are exempt.
 for x in n:
  if not isinstance(x,list) or x[0] in ['lib_symbols','property','text','title_block']:continue
  if x[0] in ['symbol','junction','label','hierarchical_label','no_connect','sheet']:
   at=get(x,'at')
   if at:
    dx=round(float(at[1])/1.27)*1.27-float(at[1]);dy=round(float(at[2])/1.27)*1.27-float(at[2])
    at[1:3]=[num(float(at[1])+dx),num(float(at[2])+dy)]
    for p in many(x,'property'):
     atp=get(p,'at');atp[1:3]=[num(float(atp[1])+dx),num(float(atp[2])+dy)]
  if x[0]=='wire':
   for p in get(x,'pts')[1:]:p[1:3]=[num(round(float(v)/1.27)*1.27) for v in p[1:3]]

def title(n,t):
 old=get(n,'title_block')
 if old:n.remove(old)
 n.append(a('title_block',a('title',t),a('date','2026-10-19'),a('rev','Schematic review A'),a('comment',S('1'),'Schematic completion only - PCB unchanged')))

# Retain circuits and identifiers on power sheet; improve heat and transient margins.
CURRENT='Power';n=copy.deepcopy(ORIG[CURRENT]);snap(n)
for k in ['text']:remove(n,k)
for h in many(n,'hierarchical_label'):
 if h[1]=='5V':h[1]='4V_PRE'
setp(existing(n,'R24'),'Value','17k4 / 1%');setp(existing(n,'R24'),'MPN','RC0603FR-0717K4L')
setp(existing(n,'TP2'),'Value','4V_PRE')
# The regulator has an actively driven output; the old output PWR_FLAG was redundant.
n.remove(existing(n,'#FLG017'))
# Replace the inherited 18 V TVS with a clamp that has usable margin below the 30 V amplifier maximum.
s=existing(n,'D2');get(s,'lib_id')[1]='Device:D_TVS';lib(n,'Device:D_TVS')
setp(s,'Value','SMBJ16A');setp(s,'Footprint','Diode_SMD:D_SMB');setp(s,'MPN','SMBJ16A');setp(s,'Datasheet','https://www.littelfuse.com/assetdocs/littelfuse-tvs-diode-smbj-datasheet?assetguid=5c5b35fb-7b17-4d3f-8c02-98a612bca794')
# Existing D2 orientation puts pin 1 (cathode) on PVDD.
setp(existing(n,'D1'),'MPN','1N4740ATR');setp(existing(n,'D1'),'Value','10V / 1W')
setp(existing(n,'Q1'),'MPN','DMP4015SK3-13');setp(existing(n,'U3'),'MPN','LMR51430XFDDCR');setp(existing(n,'U4'),'MPN','TLV1117LV33DCYR')
setp(existing(n,'L1'),'MPN','SRP6030WA-6R8M');setp(existing(n,'J1'),'MPN','09-65-2028')
setp(existing(n,'F2'),'MPN','0034.6621');setp(existing(n,'F2'),'Value','T3.15A / 250V')
# Input bulk local to the protection circuit, in addition to amplifier local reservoirs.
s=instance(n,'Device:C_Polarized','C47','220u / 35V',101.6,62.23,0,'Capacitor_THT:CP_Radial_D8.0mm_P3.50mm','35ZLH220MEFC8X11.5',CURRENT)
wire(n,(101.6,50.8),sref(n,'C47',1));wire(n,sref(n,'C47',2),(101.6,71.12));gnd(n,101.6,71.12);junction(n,(101.6,50.8))
note(n,'INPUT: 12-16 V DC ONLY',22.86,30.48,2)
note(n,'J1 pin 1 = +DC; pin 2 = GND. F2: T3.15A. Q1 reverse polarity; D1 clamps |VGS|.\nD2 SMBJ16A: 16 V standoff, 26 V rated pulse clamp. Not a sustained overvoltage regulator.\nC47 input bulk; C35/C36 are local amplifier bulk. Use a regulated, current-limited SELV supply.\nR27/R28: PVDD/11 -> GPIO36; 100n filtering. ADC1 works while Wi-Fi is active.',22.86,78.74)
note(n,'4.05 V PRE-REGULATOR',104.14,99.06,2)
note(n,'U3 retained: 3 A, 500 kHz forced PWM. 0.6 x (1 + 100k/17k4) = 4.048 V.\nL1 6u8: ripple ~0.89 A p-p at 16 V, nominal 500 kHz. Local ceramics at VIN/SW.\nFeeds both 3.3 V LDOs. Do not substitute the PFM LMR51430X version.\nVIN_SENSE is advisory: mute/shut down early during a falling input; verify hold-up on bench.',104.14,133.35)
note(n,'3.3 V ESP32 LDO',104.14,149.86,2)
note(n,'TLV1117LV33: 1 A; tab = output. Retained topology, reduced input voltage.\nAt 0.25 A: ~0.19 W; at 0.5 A: ~0.37 W; at 1 A: ~0.75 W.\nUse copper heat spreading. C52 10u ceramic plus C55 22u at ESP32.\nTPS7A2033 on DAC sheet supplies only the DAC.',104.14,154.94)
title(n,'Power - 12-16 V input, 4.05 V intermediate, 3.3 V rails');save('Power.kicad_sch',n);POWER=n

# DAC: preserve verified layout and wiring; remove stale notes and fix real interfaces/types.
CURRENT='DAC';n=copy.deepcopy(ORIG[CURRENT]);
# Translate the original 25 mil-offset block onto the 50 mil connection grid.
for item in n:
 if not isinstance(item,list) or item[0]=='lib_symbols':continue
 def trans(q):
  if not isinstance(q,list):return
  if q and q[0] in ['at','xy'] and len(q)>=3:
   q[1]=num(float(q[1])-.635);q[2]=num(float(q[2])-.635)
  for z in q:
   if isinstance(z,list):trans(z)
 trans(item)
remove(n,'text');snap(n)
for h in many(n,'hierarchical_label'):
 h[1]={'5V':'4V_PRE','OUT-L-DAC':'WOOFER_AUDIO','OUT-R-DAC':'TWEETER_AUDIO'}.get(h[1],h[1])
l=lib(n,'Custom:TPS7A2033PDBVR')
for u in many(l,'symbol'):
 for p in many(u,'pin'):p[1]=S({'1':'power_in','2':'power_in','3':'input','4':'no_connect','5':'power_out'}[get(p,'number')[1]])
n.remove(existing(n,'#FLG009'))
setp(existing(n,'IC4'),'MPN','TPS7A2033PDBVR');setp(existing(n,'U2'),'MPN','PCM5122PWR')
setp(existing(n,'C7'),'Value','10u / 50V');setp(existing(n,'C7'),'Footprint','Capacitor_THT:CP_Radial_D5.0mm_P2.00mm');setp(existing(n,'C7'),'MPN','UFW1H100MDD')
setp(existing(n,'C10'),'Value','22u / 25V');setp(existing(n,'C10'),'Footprint','Capacitor_THT:CP_Radial_D5.0mm_P2.00mm');setp(existing(n,'C10'),'MPN','UFW1E220MDD')
# Retain the owned C0G 2.7n rather than gratuitously change to 2.2n.
for r in ['C16','C19']:setp(existing(n,r),'Value','2n7 C0G / 50V');setp(existing(n,r),'MPN','0805N272J500CT')
for r in ['C12','C14']:setp(existing(n,r),'Value','2u2 X7R / 10V');setp(existing(n,r),'MPN','CL21B225KPFNNNE')
t=tp(n,'TP5','DAC_3V3',203.2,46.99);wire(n,(203.2,48.26),(203.2,46.99));junction(n,(203.2,48.26))
note(n,'PCM5122 - I2C VOLUME / MCLK-LESS I2S',38.1,25.4,2)
note(n,'MODE1=0, MODE2=1; ADR2=ADR1=0 -> I2C 0x4C (7 bit). SCK grounded.\nBCK -> PLL reference; use 64fs BCK and I2S 32-bit slots. Enable normal clock-error handling.\nP0 R13 SRCREF=BCK (0x10). P0 R61/R62 = channel digital volume; ramp together for master volume.\nOUTL -> woofer (TPA right bridge); OUTR -> tweeter (TPA left bridge).\nR2/R3 + C16/C19 retain 470R/2n7 C0G output filtering; amp input pads limit full-scale level.\nXSMT pulled low by R32 until GPIO18 releases mute. Keep volume muted throughout setup.\nVCOM grounded in default VREF mode. LDOO decoupled; unused GPIO3-6 are no-connects.\nClock loss automatically powers down DAC/line drivers. Valid but incorrect DSP data still needs limiting.\nAll grounds share GND; route analogue return to source, away from amplifier switching currents.',30.48,142.24)
title(n,'PCM5122 - left woofer, right tweeter, register controlled');save('DAC.kicad_sch',n);DAC=n

# ESP32: retain module, buttons, firmware GPIOs, source resistors and the existing wiring.
CURRENT='ESP32';n=copy.deepcopy(ORIG[CURRENT]);snap(n)
# Remove dangling inherited controls and duplicate/incorrect hierarchical labels; recreate only necessary ports.
remove(n,'hierarchical_label','text')
# Replace local SCL/SDA label endpoints with hierarchy ports on existing wires.
for x in list(many(n,'label')):
 if x[1] in ['BTN']:n.remove(x)
 if x[1] in ['SCL','SDA']:
  at=get(x,'at');n.remove(x);label(n,x[1],float(at[1]),float(at[2]),0,'hierarchical_label','output' if x[1]=='SCL' else 'bidirectional')
for name,p,d in [('3V3-ESP',(90.17,41.91),'input'),('LRCK',(107.95,62.23),'output'),('BCK',(107.95,64.77),'output'),('DATA',(107.95,77.47),'output')]:label(n,name,*p,180,'hierarchical_label',d)
# Pullups retain their wires, with a local rail name instead of duplicate child ports.
for p in [(52.07,34.29),(63.5,34.29)]:label(n,'3V3-ESP',*p,90)
label(n,'3V3-ESP',99.06,41.91); # joins existing supply wire via extension
wire(n,(99.06,41.91),(128.27,41.91))
# Fully remove the obsolete BTN stub from GPIO34 (unused input).
for w in list(many(n,'wire')):
 pts=get(w,'pts')[1:];coords=[tuple(map(float,p[1:3])) for p in pts]
 if (128.27,52.07) in coords:n.remove(w)
# Correct imported passive pin electrical types without changing any pin numbers or names.
l=lib(n,'Custom:ESP32-Wrover-IE-N16R8')
for u in many(l,'symbol'):
 for p in many(u,'pin'):
  name=get(p,'name')[1];pn=get(p,'number')[1]
  p[1]=S('power_in' if name.startswith('GND') or pn=='2' else 'no_connect' if name.startswith('NC') else 'input' if pn in ['3','4','5','6','7'] else 'bidirectional')
module=existing(n,'IC5');setp(module,'MPN','ESP32-WROVER-IE-N16R8')
# New controls on unreserved, non-strapping pins, including input-only fault input.
for pn,name,d,side in [('4','VIN_SENSE','input','L'),('7','AMP_FAULT_N','input','L'),('12','AMP_ENABLE','output','L'),('30','DAC_XSMT','output','R'),('37','AMP_MUTE_CMD','output','R')]:
 p=sref(n,'IC5',pn);x=101.6 if side=='L' else 198.12;wire(n,p,(x,p[1]));label(n,name,x,p[1],180 if side=='L' else 0,'hierarchical_label',d)
# UART labels already wired to module. Add a real, labelled external programming connector.
j=instance(n,'Connector_Generic:Conn_01x06','J2','UART / 3V3 LOGIC',53.34,111.76,0,'Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical','MC34635',CURRENT)
for pn,name in [(1,'GND'),(2,'RX'),(3,'TX'),(4,'EN'),(5,'GPIO0'),(6,'3V3-ESP')]:
 p=pxy(n,j,pn);wire(n,p,(35.56,p[1]));
 if name=='GND':gnd(n,35.56,p[1])
 else:label(n,name,35.56,p[1],180)
# I2C pullups at ESP32 3.3 V. Kept separate from DAC analogue supply.
for ref,name,x in [('R31','SCL',93.98),('R33','SDA',114.3)]:
 r=resistor(n,ref,'4k7',x,116.84,mpn='RMCF0805FT4K70');wire(n,pxy(n,r,1),(x,109.22));label(n,'3V3-ESP',x,109.22,90)
 wire(n,pxy(n,r,2),(x,125.73));label(n,name,x,125.73,270)
# Actual LEDs use existing 1k series resistors, preserving active-high GPIO behavior.
for ref,name,x,y,mpn in [('D3','WIFI_LED',152.4,116.84,'KP-2012LSGC'),('D4','BT_LED',180.34,116.84,'KP-2012EC')]:
 d=instance(n,'Device:LED',ref,mpn,x,y,90,'LED_SMD:LED_0805_2012Metric',mpn,CURRENT)
 pp=pxy(n,d,2);wire(n,pp,(x,106.68));label(n,name,x,106.68,90)
 pp=pxy(n,d,1);wire(n,pp,(x,127));gnd(n,x,127)
# Local 22u reservoir at module supply, in addition to existing 100n.
c=cap(n,'C55','22u / 25V',83.82,45.72,mpn='CL31A226KAHNNNE');wire(n,pxy(n,c,1),(83.82,38.1));label(n,'3V3-ESP',83.82,38.1,90);wire(n,pxy(n,c,2),(83.82,53.34));gnd(n,83.82,53.34)
# Intentionally unused GPIOs and module NC pads get true no-connect markers.
used={'1','2','3','4','7','8','9','10','11','12','15','16','25','30','31','33','34','35','37',*map(str,range(38,48))}
for pn,name,x,y,typ in pins(n,module):
 if pn not in used:nc(n,(x,y))
note(n,'ESP32-WROVER-IE-N16R8: EXTERNAL ANTENNA',25.4,20.32,2)
note(n,'Preserved: LED Wi-Fi=32, BT=33; LRCK=25, BCK=26, DIN=13; SCL=19, SDA=21.\nAdded: SDZ enable=27; MUTE command=23 (HIGH=mute); FAULTZ=35 (input only); DAC_XSMT=18.\nGPIO36 ADC1 monitors PVDD/11. GPIO0 BOOT pull-up; EN reset has 10k/1u RC.\nGPIO6-11 / GPIO16-17 reserved for internal flash/PSRAM: no external use.\nJ2: pins 2/3 go to ESP RX/TX (cross adapter TX/RX). Pin 6 is voltage reference only.\nDo not power the board through J2; adapter must use 3.3 V logic.\nModule custom pads 39-47 are segments of the common exposed GND area.\nFit a compatible external antenna to the IE module; keep RF connector/feed away from switch nodes.',25.4,144.78)
title(n,'ESP32-WROVER-IE - existing firmware GPIOs retained');save('ESP32.kicad_sch',n);ESP=n

# Amplifier: retain the installed IC and four input capacitors; complete all missing circuitry.
CURRENT='Amp';n=copy.deepcopy(ORIG[CURRENT]);reset_canvas(n);get(n,'paper')[1]='A3'
# Retain U1 identity/pin mapping; use the verified standard top-PowerPAD footprint.
for z in list(many(n,'symbol')):
 if val(z,'Reference')!='U1':n.remove(z)
u=existing(n,'U1');old=get(u,'at');dx=137.16-float(old[1]);dy=91.44-float(old[2]);old[1:3]=[num(137.16),num(91.44)]
for p in many(u,'property'):
 at=get(p,'at');at[1:3]=[num(float(at[1])+dx),num(float(at[2])+dy)]
setp(u,'MPN','TPA3126D2DADR');setp(u,'Footprint','Package_SO:Texas_DAD0032A_HTSSOP-32_6.1x11mm_P0.65mm_TopEP3.71x3.81mm')
l=lib(n,'Custom:TPA3126D2DADR')
for un in many(l,'symbol'):
 for p in many(un,'pin'):
  pn=get(p,'number')[1]
  if pn=='3':p[1]=S('open_collector')
  elif pn=='7':p[1]=S('power_out')
  elif pn in ['20','24','26','30']:p[1]=S('passive')
  elif pn=='16':p[1]=S('output') # This schematic fixes master mode.
  elif pn in ['21','23','27','29']:p[1]=S('output')
# Imported U1 body kept; all grounds connected explicitly.
for pn in ['9','22','25','28']:wire(n,pxy(n,u,pn),(172.72,pxy(n,u,pn)[1]))
wire(n,(172.72,114.3),(172.72,129.54));gnd(n,172.72,129.54)
for y in [114.3,116.84,119.38,121.92]:junction(n,(172.72,y))
# Direct PVCC/AVCC common supply bus.
label(n,'PVDD',25.4,33.02,180,'hierarchical_label','input');wire(n,(25.4,33.02),(101.6,33.02),(101.6,73.66))
for pn in ['18','19','31','32','17']:
 p=pxy(n,u,pn);wire(n,(101.6,p[1]),p);junction(n,(101.6,p[1]))
for ref,x,typ in [('C35',35.56,'bulk'),('C33',50.8,'100n'),('C36',66.04,'bulk'),('C34',81.28,'100n'),('C32',96.52,'1u')]:
 if typ=='bulk':c=instance(n,'Device:C_Polarized',ref,'220u / 35V',x,43.18,0,'Capacitor_THT:CP_Radial_D8.0mm_P3.50mm','35ZLH220MEFC8X11.5',CURRENT)
 else:c=cap(n,ref,typ+' / 50V',x,43.18,mpn='C1206C104K5RACTU' if typ=='100n' else 'CL31B105KBHNFNE')
 wire(n,(x,33.02),pxy(n,c,1));wire(n,pxy(n,c,2),(x,50.8));gnd(n,x,50.8);junction(n,(x,33.02))
c=cap(n,'C28','1u / 50V',76.2,83.82,mpn='CL31B105KBHNFNE');wire(n,pxy(n,u,7),(76.2,78.74),pxy(n,c,1));wire(n,pxy(n,c,2),(76.2,91.44));gnd(n,76.2,91.44);label(n,'GVDD',88.9,78.74)
# Remote input and control blocks have short local wiring and clearly named amplifier nodes.
for pn,name in [('4','AMP_RINP'),('5','AMP_RINN'),('10','AMP_LINP'),('11','AMP_LINN'),('2','AMP_SDZ'),('6','PLIMIT'),('8','GAIN_SLV'),('12','AMP_MUTE')]:
 p=pxy(n,u,pn);wire(n,p,(104.14,p[1]));label(n,name,104.14,p[1],180)
# Hybrid mode and 400 kHz: all four mode pins explicitly grounded.
for pn in ['1','13','14','15']:
 p=pxy(n,u,pn);wire(n,p,(99.06,p[1]));gnd(n,99.06,p[1])
nc(n,pxy(n,u,16))
p=pxy(n,u,3);wire(n,p,(166.37,p[1]));label(n,'AMP_FAULT_N',166.37,p[1])
# Two independent windings per package, physical numbering per CODACA diagram.
id='TPA3126:CSAD0660-100M';ls=get(n,'lib_symbols')
ll=parse('(symbol "TPA3126:CSAD0660-100M" (pin_names (offset 0) (hide yes)) (in_bom yes) (on_board yes) (property "Reference" "L" (at 0 9 0) (effects (font (size 1.27 1.27)))) (property "Value" "CSAD0660-100M" (at 0 7 0) (effects (font (size 1.27 1.27)))) (symbol "CSAD0660-100M_0_1"))')
body=get(ll,'symbol')
for y,pa,pb in [(5.08,'1','2'),(-5.08,'4','3')]:
 points=[(-5.08,y),(-4.2,y)]+[( -4.2+j*.21,y+1.25*math.sin(j*math.pi/10)) for j in range(41)]+[(5.08,y)]
 body.append(a('polyline',a('pts',*[xy('xy',*p) for p in points]),a('stroke',a('width',S('0.254')),a('type',S('default'))),a('fill',a('type',S('none')))))
 for pn,x,ang in [(pa,-7.62,0),(pb,7.62,180)]:
  body.append(a('pin',S('passive'),S('line'),xy('at',x,y,S(str(ang))),a('length',S('2.54')),a('name',pn,effect()),a('number',pn,effect())))
ls.append(ll)
for ref,cy in [('L2',66.04),('L3',111.76)]:instance(n,id,ref,'2 x 10u / 3A5',220.98,cy,0,'Custom:CSAD0660-100M','CSAD0660-100M',CURRENT)
# Output wiring, no paralleling of bridges.
for pn,ref,lp,kink in [('29','L2',1,None),('27','L2',4,205.74),('23','L3',1,200.66),('21','L3',4,195.58)]:
 p=pxy(n,u,pn);q=sref(n,ref,lp)
 if kink:wire(n,p,(kink,p[1]),(kink,q[1]),q)
 else:wire(n,p,q)
 label(n,{'29':'SW_WP','27':'SW_WN','23':'SW_TP','21':'SW_TN'}[pn],181.61,p[1])
# Bootstrap always matches the corresponding output name. TI pin table has left-side text swapped.
for ref,pn,out,y,retx in [('C24','30','29',81.28,198.12),('C25','26','27',73.66,190.5),('C26','24','23',88.9,203.2),('C27','20','21',109.22,187.96)]:
 c=cap(n,ref,'220n / 25V',180.34,y,90,C2FP,'CL21B224KAFNNNE');p=pxy(n,u,pn)
 xx=167.64 if ref in ['C24','C27'] else 170.18
 wire(n,p,(xx,p[1]),(xx,y),pxy(n,c,1));o=pxy(n,u,out)
 wire(n,pxy(n,c,2),(retx,y),(retx,o[1]));junction(n,(retx,o[1]))
# Filters: two shunt film capacitors per BTL channel, following TI Fig.31.
for ref,x,y,lr,pn,up in [('C37',251.46,50.8,'L2',2,True),('C38',251.46,83.82,'L2',3,False),('C39',251.46,96.52,'L3',2,True),('C40',251.46,129.54,'L3',3,False)]:
 c=cap(n,ref,'680n / 100V MKP',x,y,fp=MKP,mpn='MKP2D036801M00JSSD');out=sref(n,lr,pn)
 target=pxy(n,c,2 if up else 1);wire(n,(x,out[1]),target)
 gg=pxy(n,c,1 if up else 2);end=(x,gg[1]+(-2.54 if up else 2.54));wire(n,gg,end);gnd(n,*end,180 if up else 0)
# Speaker connectors retain the selected Molex 3.96 family.
for ref,y,value in [('J16',60.96,'WOOFER / CH1'),('J17',106.68,'TWEETER / CH2')]:instance(n,'Connector_Generic:Conn_01x02',ref,value,292.1,y,0,MOL,'09-65-2028',CURRENT)
wire(n,sref(n,'L2',2),sref(n,'J16',1));wire(n,sref(n,'L2',3),(279.4,71.12),(279.4,63.5),sref(n,'J16',2))
wire(n,sref(n,'L3',2),(261.62,106.68));label(n,'TW_FILTER_P',261.62,106.68)
wire(n,sref(n,'J17',1),(274.32,106.68));label(n,'TW_PROTECTED_P',274.32,106.68,180)
wire(n,sref(n,'L3',3),(279.4,116.84),(279.4,109.22),sref(n,'J17',2))
for ref,lr,pn in [('TP9','L2',2),('TP10','L2',3),('TP11','L3',2),('TP12','L3',3)]:
 p=sref(n,lr,pn);x=241.3;wire(n,p,(x,p[1]));tp(n,ref,ref.replace('TP','OUT_'),x,p[1]);junction(n,(x,p[1]))
for p in [(251.46,60.96),(251.46,71.12),(251.46,106.68),(251.46,116.84)]:junction(n,p)
# External UES capacitor plus bypassable header, both sides are BTL output potential.
j=instance(n,'Connector_Generic:Conn_01x02','J18','CAP LOOP / BYPASS',330.2,142.24,0,'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical','MC34629',CURRENT)
for pn,name in [(1,'TW_FILTER_P'),(2,'TW_PROTECTED_P')]:
 p=pxy(n,j,pn);wire(n,p,(307.34,p[1]));label(n,name,307.34,p[1],180)
c=instance(n,'Device:C','C54','47u / 50V BIPOLAR - EXTERNAL',355.6,143.51,0,'','UES1H470MPM',CURRENT,on_board=False)
wire(n,pxy(n,c,1),(355.6,135.89));label(n,'TW_FILTER_P',355.6,135.89,90)
wire(n,pxy(n,c,2),(355.6,151.13));label(n,'TW_PROTECTED_P',355.6,151.13,270)
# Startup and fault block, separate logic supply from the DAC analogue rail.
label(n,'3V3-ESP',25.4,133.35,180,'hierarchical_label','input');wire(n,(25.4,133.35),(96.52,133.35));label(n,'3V3-ESP',40.64,133.35)
for ref,name,x,y,val1 in [('R21','AMP_ENABLE',45.72,139.7,'10k'),('R26','AMP_MUTE_CMD',45.72,175.26,'10k')]:
 r=resistor(n,ref,val1,x,y,90,mpn='RC0805FR-0710KL');p=pxy(n,r,1);wire(n,(25.4,y),p);label(n,name,25.4,y,180,'hierarchical_label','input');wire(n,pxy(n,r,2),(76.2,y))
label(n,'AMP_SDZ',76.2,139.7);label(n,'AMP_MUTE',76.2,175.26)
r=resistor(n,'R25','100k',63.5,148.59,mpn='RC0805FR-07100KL');wire(n,(63.5,139.7),pxy(n,r,1));wire(n,pxy(n,r,2),(63.5,156.21));gnd(n,63.5,156.21);junction(n,(63.5,139.7))
for ref,y,name in [('C30',148.59,'AMP_SDZ'),('C31',184.15,'AMP_MUTE')]:
 c=cap(n,ref,'100n / 50V',76.2,y,mpn='C1206C104K5RACTU');wire(n,(76.2,y-8.89),pxy(n,c,1));wire(n,pxy(n,c,2),(76.2,y+7.62));gnd(n,76.2,y+7.62)
r=resistor(n,'R29','100k',63.5,166.37,mpn='RC0805FR-07100KL');wire(n,pxy(n,r,1),(63.5,158.75));label(n,'3V3-ESP',63.5,158.75,90);wire(n,pxy(n,r,2),(63.5,175.26));junction(n,(63.5,175.26))
r=resistor(n,'R30','100k',96.52,142.24,mpn='RC0805FR-07100KL');wire(n,(96.52,133.35),pxy(n,r,1));wire(n,pxy(n,r,2),(96.52,151.13),(116.84,151.13));label(n,'AMP_FAULT_N',116.84,151.13,0,'hierarchical_label','output');label(n,'AMP_FAULT_N',96.52,151.13)
for ref,x,y,name in [('TP6',109.22,151.13,'FAULTZ'),('TP7',71.12,139.7,'SDZ'),('TP8',71.12,175.26,'MUTE')]:tp(n,ref,name,x,y);junction(n,(x,y))
# Gain and provisional common limiter. Divider total >100k.
r=resistor(n,'R18','5k6',96.52,220.98,mpn='RMCF0805FT5K60');wire(n,pxy(n,r,1),(96.52,213.36));label(n,'GAIN_SLV',96.52,213.36,90);wire(n,pxy(n,r,2),(96.52,228.6));gnd(n,96.52,228.6)
r=resistor(n,'R19','100k / 1%',45.72,208.28,mpn='RC0805FR-07100KL');wire(n,pxy(n,r,1),(45.72,200.66));label(n,'GVDD',45.72,200.66,90);wire(n,pxy(n,r,2),(45.72,217.17),(68.58,217.17));label(n,'PLIMIT',68.58,217.17)
r=resistor(n,'R20','33k / 1%',45.72,226.06,mpn='RC0805FR-0733KL');wire(n,(45.72,217.17),pxy(n,r,1));wire(n,pxy(n,r,2),(45.72,233.68));gnd(n,45.72,233.68)
c=cap(n,'C29','1u / 50V',63.5,226.06,mpn='CL31B105KBHNFNE');wire(n,(63.5,217.17),pxy(n,c,1));wire(n,pxy(n,c,2),(63.5,233.68));gnd(n,63.5,233.68);junction(n,(63.5,217.17))
# Matched AC coupling; source-ground reference stays on source side of the negative capacitor.
for pos,cr1,cr2,rs,rb,rn,stem,name in [(0,'C1','C2','R12','R13','R16','R','WOOFER_AUDIO'),(142.24,'C6','C5','R14','R15','R17','L','TWEETER_AUDIO')]:
 x0=25.4+pos;y=251.46
 label(n,name,x0,y,180,'hierarchical_label','input')
 r=resistor(n,rs,'3k3',45.72+pos,y,90,mpn='RMCF0805FT3K30');wire(n,(x0,y),pxy(n,r,1));wire(n,pxy(n,r,2),(85.09+pos,y))
 r=resistor(n,rb,'1k',63.5+pos,242.57,mpn='RC0805FR-071KL');wire(n,pxy(n,r,2),(63.5+pos,y));wire(n,pxy(n,r,1),(63.5+pos,234.95));gnd(n,63.5+pos,234.95,180);junction(n,(63.5+pos,y))
 c=copy.deepcopy(existing(ORIG['Amp'],cr1));get(c,'at')[1:]=[num(91.44+pos),num(y),S('90')]
 for p in many(c,'property'):
  get(p,'at')[1:]=[num(91.44+pos),num(y+(-3.81 if p[1]=='Reference' else 3.81)),S('0')]
 setp(c,'MPN','MKS2C041001F00JSSD');setp(c,'Value','1u / 63V FILM');n.append(c);wire(n,(85.09+pos,y),pxy(n,c,1));wire(n,pxy(n,c,2),(120.65+pos,y));label(n,'AMP_'+stem+'INP',120.65+pos,y)
 r=resistor(n,rn,'820R',76.2+pos,261.62,90,mpn='RC0805FR-07820RL');wire(n,(53.34+pos,261.62),pxy(n,r,1));gnd(n,53.34+pos,261.62)
 c=copy.deepcopy(existing(ORIG['Amp'],cr2));get(c,'at')[1:]=[num(91.44+pos),num(261.62),S('90')]
 for p in many(c,'property'):get(p,'at')[1:]=[num(91.44+pos),num(261.62+(-3.81 if p[1]=='Reference' else 3.81)),S('0')]
 setp(c,'MPN','MKS2C041001F00JSSD');setp(c,'Value','1u / 63V FILM');n.append(c);wire(n,pxy(n,r,2),pxy(n,c,1));wire(n,pxy(n,c,2),(120.65+pos,261.62));label(n,'AMP_'+stem+'INN',120.65+pos,261.62)
# DNP snubbers: separate, visible tuning bank; no inherited TPA3220 values.
for i,(name,x) in enumerate([('SW_WP',195.58),('SW_WN',218.44),('SW_TP',241.3),('SW_TN',264.16)]):
 c=cap(n,'C'+str(41+i),'330p C0G / 50V DNP',x,166.37,fp=C2FP,mpn='GMC21CG331J50NT',dnp=True);wire(n,pxy(n,c,1),(x,158.75));label(n,name,x,158.75,90)
 r=resistor(n,'R'+str(35+i),'18R / 0.25W DNP',x,179.07,mpn='RC0805FR-0718RL');get(r,'dnp')[1]=S('yes');wire(n,pxy(n,c,2),pxy(n,r,1));wire(n,pxy(n,r,2),(x,186.69));gnd(n,x,186.69)
note(n,'TPA3126D2 - STEREO BTL / 4 OHM LOADS',25.4,20.32,2)
note(n,'20 dB MASTER; AM[2:0]=000 -> 400 kHz nominal. MODSEL=0 -> hybrid mode.\nEach CSAD package: winding 1-2, winding 4-3. No assumed flux cancellation.\nTI Fig.31 filter: 10u per leg + 680n to GND per leg (four film capacitors total).\nKeep 20 x 18 x 10 mm heatsink clearance over U1; top PowerPAD, no PCB EP copper.\nTop pad may be grounded (preferred) or floating per TI; never connect it to PVDD.',292.1,22.86)
note(n,'SAFE STARTUP / FAULT',25.4,123.19,1.8)
note(n,'SDZ default LOW; MUTE default HIGH. 10k/100n command filtering\nlimits slew below TI 10 V/ms. SDZ asserted low is the primary safe state.\nMUTE command HIGH=mute, LOW=play. Wait >=50 ms after SDZ high\nbefore unmuting. FAULTZ open-drain -> GPIO35, 100k pull-up.\nNo automatic retry link: log fault, mute, cycle SDZ only after diagnosis.',25.4,195.58)
note(n,'PLIMIT IS PROVISIONAL',119.38,200.66,1.8)
note(n,'100k/33k: VPLIMIT = 0.2481 x GVDD = 1.39 V nominal.\nTI virtual-rail model: Vpk ~5.56 V; ~3.4 W sine / 4 ohm\nafter series loss. TI table 3 RMS labels conflict with this model.\nMeasure actual clipping/limit into dummy loads at 12 and 16 V.\nShared limiter cannot protect each driver or define safe excursion.\nInput pad: 3k3/1k plus DAC 470R -> ~0.206 gain, ~4.3 Vrms\nrequested at DAC FS and 20 dB (before PLIMIT). Keep DSP limits.',119.38,207.01)
note(n,'EXTERNAL TWEETER CAPACITOR / STEREO BYPASS',292.1,165.1,1.8)
note(n,'C54 = Nichicon UES1H470MPM, 47u / 50V bipolar, 10 x 20 mm.\nWire across J18 pins 1-2. It is in series with CH2 positive.\nFor stereo: remove capacitor harness and fit a rated shorting link.\nWith neither cap nor link, CH2 positive is OPEN (safe no-output).\nPin 1 = filtered bridge positive; pin 2 = speaker connector positive.\nNeither pin is ground. Change link only with power off.\nNominal 4 ohm pole ~847 Hz; actual response follows tweeter impedance.\nAccount for capacitor phase/response in the DSP crossover.',292.1,172.72)
note(n,'SNUBBERS C41-C44 / R35-R38: DNP, tune on bench.\nTI starting point 330p / 18R; no copied TPA3220 snubber.\nAll filtered speaker terminals float relative to GND.\nRoute source-side input reference returns to the DAC GND.\nPower loops must not share those return traces.',292.1,218.44)
note(n,'WOOFER: DAC LEFT -> AMPLIFIER RIGHT BRIDGE',25.4,274.32)
note(n,'TWEETER: DAC RIGHT -> AMPLIFIER LEFT BRIDGE',167.64,274.32)
title(n,'TPA3126D2 - protected two-way outputs; bypassable CH2 cap');save('Amp.kicad_sch',n);AMP=n

# Preserve sheet hierarchy and UUIDs, replace obsolete top-level interface wiring.
CURRENT='';n=copy.deepcopy(ROOT);reset_canvas(n)
for s in list(many(n,'symbol')):
 if not(val(s,'Reference') or '').startswith('H'):n.remove(s)
# Rebuild sheet boxes with ample spacing and directly wired audio and I2S.
config={
'Power':((20.32,22.86),(43.18,38.1),[],[('PVDD','output',27.94),('4V_PRE','output',35.56),('3V3-ESP','output',43.18),('VIN_SENSE','output',50.8)]),
'ESP32':((20.32,78.74),(63.5,78.74),[('3V3-ESP','input',86.36),('VIN_SENSE','input',93.98)],[('BCK','output',86.36),('LRCK','output',93.98),('DATA','output',101.6),('SCL','output',109.22),('SDA','bidirectional',116.84),('DAC_XSMT','output',124.46),('AMP_ENABLE','output',134.62),('AMP_MUTE_CMD','output',142.24),('AMP_FAULT_N','input',149.86)]),
'DAC':((111.76,78.74),(58.42,55.88),[('BCK','input',86.36),('LRCK','input',93.98),('DATA','input',101.6),('SCL','input',109.22),('SDA','bidirectional',116.84),('DAC_XSMT','input',124.46)],[('WOOFER_AUDIO','output',93.98),('TWEETER_AUDIO','output',101.6)]),
'Amp':((210.82,78.74),(60.96,78.74),[('WOOFER_AUDIO','input',93.98),('TWEETER_AUDIO','input',101.6),('AMP_ENABLE','input',134.62),('AMP_MUTE_CMD','input',142.24),('AMP_FAULT_N','output',149.86)],[])}
sheetpins={}
for s in many(n,'sheet'):
 name=val(s,'Sheetfile').split('.')[0];(x,y),(w,h),left,right=config[name]
 get(s,'at')[1:]=[num(x),num(y)];get(s,'size')[1:]=[num(w),num(h)]
 for p in many(s,'property'):
  get(p,'at')[1:]=[num(x),num(y-1.27 if p[1]=='Sheetname' else y+h+1.27),S('0')]
 remove(s,'pin')
 for side,items in [('L',left),('R',right)]:
  for nam,d,yy in items:
   xx=x if side=='L' else x+w
   s.append(a('pin',nam,S(d),xy('at',xx,yy,S('180' if side=='L' else '0')),a('uuid',uid()),effect(1.0,'left' if side=='L' else 'right')));sheetpins[(name,nam)]=(xx,yy)
 # Power supply input pins across top of DAC/amplifier.
 top=[('4V_PRE',x+25.4)] if name=='DAC' else [('PVDD',x+20.32),('3V3-ESP',x+43.18)] if name=='Amp' else []
 for nam,xx in top:
  s.append(a('pin',nam,S('input'),xy('at',xx,y,S('90')),a('uuid',uid()),effect(1.0,'right')));sheetpins[(name,nam)]=(xx,y)
for sig in ['BCK','LRCK','DATA','SCL','SDA','DAC_XSMT']:wire(n,sheetpins['ESP32',sig],sheetpins['DAC',sig])
for sig in ['WOOFER_AUDIO','TWEETER_AUDIO']:wire(n,sheetpins['DAC',sig],sheetpins['Amp',sig])
for sig,y in [('AMP_ENABLE',166.37),('AMP_MUTE_CMD',172.72),('AMP_FAULT_N',179.07)]:
 p=sheetpins['ESP32',sig];q=sheetpins['Amp',sig];wire(n,p,(91.44,p[1]),(91.44,y),(200.66,y),(200.66,q[1]),q)
 # Each line needs its own vertical lane to avoid shorting controls.
# Correct common vertical lanes into separated tracks.
for w in list(many(n,'wire')):
 pts=get(w,'pts');pp=[tuple(map(float,p[1:3])) for p in pts[1:]]
 if any((p[0] in [91.44,200.66] and p[1]>=134.62) for p in pp):n.remove(w)
for i,(sig,y) in enumerate([('AMP_ENABLE',166.37),('AMP_MUTE_CMD',172.72),('AMP_FAULT_N',179.07)]):
 p=sheetpins['ESP32',sig];q=sheetpins['Amp',sig];xl=96.52-i*3.81;xr=190.5+i*3.81;wire(n,p,(xl,p[1]),(xl,y),(xr,y),(xr,q[1]),q)
for key,p in sheetpins.items():
 name,sig=key
 if sig in ['PVDD','4V_PRE','3V3-ESP','VIN_SENSE']:
  q=(p[0],p[1]-7.62) if (name in ['DAC','Amp']) else (p[0]+7.62,p[1]) if name=='Power' else (p[0]-7.62,p[1])
  wire(n,p,q);label(n,sig,*q,90 if name in ['DAC','Amp'] else 0 if name=='Power' else 180)
# Move mounting holes to unused top left area.
for i,r in enumerate(['H1','H2','H3','H4']):
 s=existing(n,r);at=get(s,'at');dx=83.82-float(at[1]);dy=25.4+i*7.62-float(at[2]);at[1:3]=[num(83.82),num(25.4+i*7.62)]
 for p in many(s,'property'):
  q=get(p,'at');q[1:3]=[num(float(q[1])+dx),num(float(q[2])+dy)]
note(n,'ACTIVE SPEAKER - ESP32-WROVER / PCM5122 / TPA3126D2',111.76,22.86,2)
note(n,'12-16 V DC -> protected PVDD -> stereo BTL amplifier.\nPVDD -> 4.05 V FPWM buck -> ESP32 3.3 V LDO + DAC 3.3 V low-noise LDO.\nPCM5122 LEFT = woofer / CH1; RIGHT = tweeter / CH2. Both speaker returns are active.\nExternal Nichicon UES capacitor on J18; replace with shorting link for stereo use.\nNo passive crossover. DSP crossover/EQ/limiting remains a firmware and acoustic task.',111.76,30.48)
note(n,'STARTUP: rails settle -> ESP32 boots (SDZ low, MUTE high, XSMT low).\nConfigure PCM5122 at 0x4C with both channels muted; configure DSP and valid 64fs I2S.\nEnable SDZ, wait >=50 ms, release DAC mute, then amplifier mute; ramp DAC volume.\nSHUTDOWN: ramp down, assert DAC XSMT low >=150/fs +0.2 ms; assert MUTE then SDZ low.\nFAULT: mute and shut down, log fault; deliberate retry only after fault cause is removed.\nReview report and bench validation are required before connecting the real drivers.',20.32,187.96)
title(n,'Bluetooth / Snapcast active speaker - schematic review');save('TPA3126.kicad_sch',n)

# Make all nonstandard library dependencies portable without touching the PCB.
fpdir=Path('TPA3126.pretty')
for name in ['ESP32-WROVER-IE-N16R8','SOT95P280X145-5N','TS026650BK100SCRD','CSAD0660-100M','SRP6030WA-6R8M']:
 shutil.copy2(Path('/Users/tomwatson/Downloads/Custom.pretty')/(name+'.kicad_mod'),fpdir/(name+'.kicad_mod'))
Path('fp-lib-table').write_text('(fp_lib_table (version 7)\n (lib (name "TPA3220") (type "KiCad") (uri "${KIPRJMOD}/TPA3126.pretty") (options "") (descr "Inherited footprints"))\n (lib (name "Custom") (type "KiCad") (uri "${KIPRJMOD}/TPA3126.pretty") (options "") (descr "Project local verified dependencies"))\n)\n')
# Store exact embedded custom symbols so editor update does not depend on the user's global library.
symbols={}
for f in ['ESP32','DAC','Amp','Power','TPA3126']:
 ns=load(f+'.kicad_sch')
 for sym in many(get(ns,'lib_symbols'),'symbol'):
  if ':' in sym[1] and sym[1].split(':')[0] in ['Custom','TPA3126']:
   q=copy.deepcopy(sym);q[1]=q[1].split(':')[1];symbols[q[1]]=q
save('TPA3126.kicad_sym',a('kicad_symbol_lib',a('version',S('20241209')),a('generator','kicad_symbol_editor'),*symbols.values()))
Path('sym-lib-table').write_text('(sym_lib_table (version 7)\n (lib (name "Custom") (type "KiCad") (uri "${KIPRJMOD}/TPA3126.kicad_sym") (options "") (descr "Retained custom pin maps; corrected electrical types"))\n (lib (name "TPA3126") (type "KiCad") (uri "${KIPRJMOD}/TPA3126.kicad_sym") (options "") (descr "Codaca independent dual inductor"))\n)\n')

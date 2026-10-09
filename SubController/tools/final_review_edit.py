"""Scoped final-review edits from the preserved baseline. Never touches PCB/project."""
from pathlib import Path
from copy import deepcopy
import sys,uuid,re,json,zipfile
from sexpr import parse,dump,Q,child,children
P=Path(__file__).resolve().parents[1]
ns={'__file__':str(P/'tools/build_schematic.py')}
exec((P/'tools/build_schematic.py').read_text().split('# 2: Input isolation')[0],ns)
Sheet=ns['Sheet'];ns['counter'].update({'#PWR':1000,'TP':6,'J':24,'R':111,'C':61,'D':6})
z=zipfile.ZipFile(P/'design/final-review/before-final-review.zip')
def load(name):return parse(z.read(name).decode())
def prop(s,k):return next(p for p in children(s,'property') if p[1]==k)
def symbols(a,ref):return [s for s in children(a,'symbol') if prop(s,'Reference')[2]==ref]
def change(a,ref,key,value):
 for s in symbols(a,ref):prop(s,key)[2]=Q(value)
def note(a,find,repl):
 for t in children(a,'text'):
  if find in str(t[1]):t[1]=Q(repl)
def addon(name):
 s=Sheet(name,'',0);s.count=10000;return s
def add(a,s):
 libs=child(a,'lib_symbols');known={x[1] for x in children(libs,'symbol')}
 for k,v in s.libs.items():
  if k not in known:libs.append(v)
 a.extend(parse(x) for x in s.items)
def save(name,a):
 # Reuse unchanged baseline top-level text verbatim; only edited records reserialize.
 old=z.read(name).decode();starts=[];dep=0;quoted=False;esc=False;start=None
 for i,c in enumerate(old):
  if quoted:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c=='"':quoted=False
   continue
  if c=='"':quoted=True
  elif c=='(':
   dep+=1
   if dep==2:start=i
  elif c==')':
   if dep==2:starts.append(old[start:i+1])
   dep-=1
 bydump={dump(parse(t)):t for t in starts}
 out='(kicad_sch\n'+'\n'.join('\t'+bydump.get(dump(x),dump(x)) for x in a[1:])+'\n)\n'
 (P/name).write_text(out)
# All coils now match the owned 5V Omron. Preserve relay contact geometry/pin numbering.
for name in ['01_inputs.kicad_sch','07_drivers.kicad_sch']:
 a=load(name)
 for r in ['K1','K2','K3','K4']:
  change(a,r,'Value','AGN2004H');change(a,r,'Footprint','Custom:Relay_DPDT_Panasonic_AGN2004H')
 note(a,'MONO =','MONO = (10/22)(L+R); AV = (20/22)LFE, after input division.\nL/R are separately buffered. Main speakers remain full range.')
 if name.startswith('07'):
  # Pull the mute-inverter base from the rail it must protect, not disappearing +5R.
  # Locate R97's +5R global label by its known local wire region.
  for t in children(a,'global_label'):
   at=child(t,'at')
   if t[1]=='+5R' and abs(float(at[1])-289.56)<0.01 and abs(float(at[2])-110.49)<0.01:t[1]=Q('+5A')
  note(a,'RUN=0:', 'RUN=0: Q6 OFF, Q7 ON => CS mute asserted.\nR97 uses +5A: loss of +5R still asserts mute while +5A lives.\nRUN=1: Q6 ON, Q7 OFF => CS_RUN high; no rail backfeed.')
 save(name,a)
# Explicit dielectric/rating on live values; preserve C56 reference and existing footprints.
a=load('02_crossover.kicad_sch')
for r in ['C11','C12','C13','C14','C16','C56']:change(a,r,'Value','100n FILM / 63V')
# LP bypass jumper between slope output and relay input, fits clear lower-right area.
for t in children(a,'global_label'):
 if t[1]=='REF_LP':t[1]=Q('LP_SLOPE')
s=addon('02_crossover.kicad_sch');p=s.sym('Connector_Generic:Conn_01x03',365.76,238.76,ref='J25',value='LP: FILTER / BYPASS',foot='Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical')[0]
for pin,net in {'1':'LP_SLOPE','2':'REF_LP','3':'MONO'}.items():s.net(net,p[pin],-5.08)
s.text('J25: 1-2 normal; 2-3 bench bypass. Change muted.',297.18,256.54,1.016);add(a,s);save('02_crossover.kicad_sch',a)
a=load('01_inputs.kicad_sch')
# save above modified version rather than reloading old twice
# retain the earlier input corrections
for r in ['K1','K2','K3','K4']:change(a,r,'Value','AGN2004H');change(a,r,'Footprint','Custom:Relay_DPDT_Panasonic_AGN2004H')
for r in ['C1','C2']:change(a,r,'Value','100p C0G / 50V')
note(a,'MONO =','MONO = (10/22)(L+R); AV = (20/22)LFE, after input division.\nNo direct L/R connection. Main speakers remain full range.')
s=addon('01_inputs.kicad_sch')
for ref,net,x in [('TP7','GND',30.48),('TP8','BUF_L',190.5),('TP9','BUF_R',238.76),('TP10','MONO',287.02)]:
 p=s.sym('Connector:TestPoint',x,203.2,ref=ref,value=net,foot='TestPoint:TestPoint_Pad_D1.5mm')[0];s.net(net,p['1'])
s.text('TP8/9: selected REF L/R buffers; both carry LFE in AV.\nProbe inactive RCA returns only with an isolated/differential instrument.',20.32,180.34,1.016)
add(a,s);save('01_inputs.kicad_sch',a)
# Replace only control page with direct MCU GPIO; keep references of remaining parts.
s=addon('05_control.kicad_sch');s.title='Control and isolated trigger';s.page=6
s.text('ATtiny1614 DIRECT CONTROL / RESET-SAFE MUTE / ISOLATED TRIGGER',20.32,15.24)
s.text('All audio stays analogue. MCU reset makes RUN and AV GPIO high impedance; external pull-downs drop relays.\nInternal clock; BOD and watchdog required. PA0 remains UPDI. No I/O expander or retained relay latch.',20.32,25.4,1.016)
p=s.sym('MCU_Microchip_ATtiny:ATtiny1614-SS',76.2,88.9,ref='U8')[0]
mp={'1':'+5R','14':'GND','10':'UPDI','11':'SER_DATA_INV','12':'SER_CLK_INV','13':'SER_CS_INV','2':'REF_ENC_A','3':'REF_ENC_B','4':'AV_ENC_A','5':'AV_ENC_B','6':'TRIGGER_N','7':'RAIL_GOOD','8':'AV_ENABLE','9':'RUN_REQUEST'}
for pin,net in mp.items():s.net(net,p[pin],-12.7 if pin in ['1','14','6','7','8','9'] else 10.16)

for item_index,item in enumerate(s.items):
 if '(property "Reference" "U8"' in item:
  obj=parse(item)
  child(prop(obj,'Reference'),'at')[1:3]=['66.04','60.96']
  child(prop(obj,'Value'),'at')[1:3]=['66.04','63.5']
  s.items[item_index]=dump(obj)
s.powercap(25.4,114.3,'+5R') # explicit ref patched below
# assign old C41 ref to preserve local decoupling identity
for i,item in enumerate(s.items):
 if '(property "Reference" "C62"' in item:s.items[i]=item.replace('"C62"','"C41"')
p=s.sym('Connector_Generic:Conn_01x03',40.64,154.94,ref='J17',value='UPDI / +5R / GND',foot='Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical')[0]
for pin,net in {'1':'UPDI','2':'+5R','3':'GND'}.items():s.net(net,p[pin],-5.08)
for x,ref,val,a,b,ra,rb in [(177.8,'J18','REF LEVEL','REF_ENC_A','REF_ENC_B','R59','R60'),(266.7,'J19','LFE LEVEL','AV_ENC_A','AV_ENC_B','R61','R62')]:
 p=s.sym('Connector_Generic:Conn_01x03',x,60.96,ref=ref,value=val,foot='Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical')[0]
 for pin,net in {'1':a,'2':'GND','3':b}.items():s.net(net,p[pin],-5.08)
 for xx,ref,net in [(x-17.78,ra,a),(x+17.78,rb,b)]:
  p=s.sym('Device:R',xx,104.14,ref=ref,value='10k',foot='Resistor_SMD:R_0805_2012Metric')[0];s.net('+5R',p['1'],-5.08);s.net(net,p['2'],-5.08)
s.text('Dry-contact encoders; software quadrature debounce.\nSeparate stored REF/LFE levels; never positive CS gain.',160.02,127,1.016)
p=s.sym('Connector_Generic:Conn_01x02',370.84,58.42,ref='J20',value='ISOLATED TRIGGER 12V',foot='Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical')[0]
s.net('TRIG_PLUS',p['1'],-5.08);s.net('TRIG_MINUS',p['2'],-5.08)
ns['custom']['VO617A-3']=deepcopy(next(x for x in children(parse((P/'libraries/SubController.kicad_sym').read_text()),'symbol') if x[1]=='VO617A-3'))
op=s.sym('SubController:VO617A-3',330.2,162.56,ref='U10')[0]
r=s.sym('Device:R',294.64,160.02,ref='R63',value='2k2 / 0.125W',angle=270,foot='Resistor_SMD:R_0805_2012Metric')[0];s.net('TRIG_PLUS',r['2'],-5.08);s.wire(r['1'],op['1']);s.label('TRIG_LED_A',op['1'],180,True);s.net('TRIG_MINUS',op['2'],-5.08)
d=s.sym('Device:D',292.1,187.96,ref='D1',value='1N4148W',angle=90,foot='Diode_SMD:D_SOD-123')[0];s.net('TRIG_LED_A',d['1'],-5.08);s.net('TRIG_MINUS',d['2'],-5.08)
s.net('TRIGGER_RAW',op['4'],5.08);s.gnd(op['3'])
r=s.sym('Device:R',373.38,157.48,ref='R64',value='10k',foot='Resistor_SMD:R_0805_2012Metric')[0];s.net('+5R',r['1']);s.net('TRIGGER_N',r['2'])
p=s.sym('Connector_Generic:Conn_01x03',363.22,104.14,ref='J24',value='AUTO / REF(open) / AV',foot='Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical')[0]
for pin,net in {'1':'TRIGGER_RAW','2':'TRIGGER_N','3':'GND'}.items():s.net(net,p[pin],-5.08)
s.text('Open/inactive=REF, active=AV. J24: 1-2 AUTO, open REF, 2-3 AV.\n12V trigger ~5mA; for 5V fit 750R. Trigger return stays isolated.',252.73,203.2,1.016)
for i,(base,out,pull) in enumerate([('SER_DATA_INV','CS_DATA','+5R'),('SER_CLK_INV','CS_CLK','+5R'),('SER_CS_INV','CS_N','GND')]):
 x=40.64+i*78.74;y=231.14
 tr=s.sym('SubController:BC337_stock',x+22.86,y,ref=f'Q{i+1}',value='BC337 (stock)',foot='Package_TO_SOT_THT:TO-92_Inline')[0]
 rb=s.sym('Device:R',x-2.54,y,ref=f'R{65+3*i}',value='10k',angle=270,foot='Resistor_SMD:R_0805_2012Metric')[0];s.net(base,rb['2'],-2.54);s.wire(rb['1'],tr['2']);s.gnd(tr['3']);s.net(out,tr['1'])
 rr=s.sym('Device:R',x+45.72,y-20.32,ref=f'R{66+3*i}',value='10k',foot='Resistor_SMD:R_0805_2012Metric')[0];s.net('+5A',rr['1']);s.net(out,rr['2'])
 rr=s.sym('Device:R',x-15.24,y+20.32,ref=f'R{67+3*i}',value='47k',foot='Resistor_SMD:R_0805_2012Metric')[0];s.net(base,rr['1'],-2.54);s.net(pull,rr['2'],-2.54)
s.text('Serial collectors use +5A. 10kHz software clock, inverted GPIO. Default clock/data LOW, CS HIGH.',20.32,279.4,1.016)
a=load('05_control.kicad_sch');a=[x for x in a if not(isinstance(x,list) and x[0] in ['symbol','wire','junction','global_label','label','text','no_connect','lib_symbols'])];a.append(['lib_symbols']);add(a,s);save('05_control.kicad_sch',a)
# Bench points and hard mute bypass, on otherwise untouched interlock sheet.
a=load('08_rail_interlock.kicad_sch');s=addon('08_rail_interlock.kicad_sch')
for i,(net,x,y) in enumerate([('LP_SLOPE',40.64,208.28),('PHASE_OUT',116.84,208.28),('HP_OUT',193.04,208.28),('AMP_OUT',269.24,208.28),('TRIGGER_N',40.64,248.92),('AV_ENABLE',116.84,248.92),('RUN_REQUEST',193.04,248.92),('RAIL_GOOD',269.24,248.92)],11):
 p=s.sym('Connector:TestPoint',x,y,ref=f'TP{i}',value=net,foot='TestPoint:TestPoint_Pad_D1.5mm')[0];s.net(net,p['1'])
p=s.sym('Connector_Generic:Conn_01x02',355.6,208.28,ref='J26',value='FORCE MUTE (FIT SHUNT)',foot='Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical')[0];s.net('RAIL_GOOD',p['1'],-5.08);s.gnd(p['2'])
s.text('J26 shorts open-collector RAIL_GOOD to GND: hardware mute, independent of firmware.\nTP11 post-LPF; TP12 post-phase; TP13 post-subsonic; TP14 final output.\nUse GND TP7 as scope reference; never clip scope ground to an inactive RCA return.',40.64,180.34,1.016)
add(a,s);save('08_rail_interlock.kicad_sch',a)

# User explicitly selects AGN2004H for all relays, using their existing footprint/model.
for name in ['03_level_phase.kicad_sch','04_protection_output.kicad_sch']:
 a=load(name)
 for r in ['K3','K4']:
  change(a,r,'Value','AGN2004H');change(a,r,'Footprint','Custom:Relay_DPDT_Panasonic_AGN2004H')
 save(name,a)
print('Scoped schematic changes saved. PCB and project untouched.')
# Protect CS3310 AIN against excessive injection while its rails start/stop.
# 2k2 sits INSIDE U4A's DC/audio feedback; 100p provides local HF feedback.
name='03_level_phase.kicad_sch';a=parse((P/name).read_text());s=addon(name)
start=(180.34,60.96);end=(190.5,60.96)
removed=[]
for w in children(a,'wire'):
 ps=[tuple(map(float,p[1:])) for p in children(child(w,'pts'),'xy')]
 if ps==[start,end] or ps==[end,start]:removed.append(w)
assert len(removed)==1,removed
for w in removed:a.remove(w)
r=s.sym('Device:R',185.42,60.96,ref='R112',value='2k2',angle=270,foot='Resistor_SMD:R_0805_2012Metric')[0]
s.wire(start,r['2']);s.wire(r['1'],end);s.label('ATT_DRIVE',start,180,True)
# Route compensation above the stage without adding a direct CS capacitive load.
c=s.sym('Device:C',172.72,38.1,ref='C62',value='100p C0G / 50V',angle=270,foot='Capacitor_SMD:C_0805_2012Metric')[0]
s.wire(start,(185.42,60.96)) if False else None
s.wire(start,(180.34,38.1),c['1']);s.dot(start)
s.wire(c['2'],(158.75,38.1),(158.75,63.5));s.dot((158.75,63.5))
note(a,'Fixed -0.5','DC/audio gain -0.5; R112 limits CS input fault current <7.2mA.\nR39 senses ATT_IN after R112; C62 provides local HF feedback.\nHF corner ~130kHz (10k CS load); output -2 restores level.')
add(a,s);save(name,a)
# Physical relay model: preserve the user's exact existing model and path.
import shutil
model=P/'InputSwitch.3dshapes/Relay_DPDT_Panasonic_AGN2004H.step'
model.parent.mkdir(exist_ok=True)
shutil.copy2(P.parent/'InputSwitch/InputSwitch.3dshapes/Relay_DPDT_Panasonic_AGN2004H.step',model)
# Correct all relay library identities without changing their contact geometry.
libpath=P/'libraries/SubController.kicad_sym';lib=parse(z.read('libraries/SubController.kicad_sym').decode())
relay=deepcopy(next(x for x in children(lib,'symbol') if x[1]=='G6K_2P_Y'))
relay[1]=Q('AGN2004H')
for u in children(relay,'symbol'):u[1]=Q(str(u[1]).replace('G6K_2P_Y','AGN2004H'))
prop(relay,'Value')[2]=Q('AGN2004H');prop(relay,'Footprint')[2]=Q('Custom:Relay_DPDT_Panasonic_AGN2004H')
# Original relay symbol has no datasheet property; add the manufacturer source.
relay.append(parse('(property "Datasheet" "https://mediap.industry.panasonic.eu/assets/download-files/import/ds_61007_en_gn.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))'))
lib.append(relay);libpath.write_text(dump(lib)+'\n')
for name in ['01_inputs.kicad_sch','03_level_phase.kicad_sch','04_protection_output.kicad_sch','07_drivers.kicad_sch']:
 a=parse((P/name).read_text());ls=child(a,'lib_symbols')
 ls[:]=[x for x in ls if not(isinstance(x,list) and x[0]=='symbol' and x[1]=='SubController:G6K_2P_Y')]
 r=deepcopy(relay);r[1]=Q('SubController:AGN2004H');ls.append(r)
 for sym in children(a,'symbol'):
  if prop(sym,'Reference')[2] in ['K1','K2','K3','K4']:
   child(sym,'lib_id')[1]=Q('SubController:AGN2004H')
   prop(sym,'Datasheet')[2]=Q('https://mediap.industry.panasonic.eu/assets/download-files/import/ds_61007_en_gn.pdf')
   for p in children(sym,'property'):
    if p[1]=='Design_note':p[2]=Q('AGN2004H: coil 1+/8-, NC2/7, COM3/6, NO4/5. User specifies 5V drive for nominal 4.5V coils.')
 if name.startswith('07'):
  note(a,'Q4 switches','Q4 switches three AGN2004H coils: ~101mA nominal, allow 120mA.\nQ5 switches one coil: ~34mA. User specifies +5R drive (4.5V rated coils).\nAllow >=50ms muted relay settling; verify release time with flyback diodes.\nU13 AV heat: allow 2.1W; effective junction-to-ambient <=25 C/W.')
 save(name,a)
# Negative comparator inputs must not be driven below GND when +5R/reference vanish first.
# Scale only the negative sense dividers to bound Schottky clamp current below 0.1mA.
name='06_power_mute.kicad_sch';a=load(name);s=addon(name)
for r,v in [('R85','15k / 0.1%'),('R86','180k / 0.1%'),('R89','20k / 0.1%'),('R90','86k / 0.1%')]:change(a,r,'Value',v)
p=s.sym('Diode:BAT54A',152.4,208.28,ref='D7',value='BAT54A-7-F',foot='Package_TO_SOT_SMD:SOT-23')[0]
s.net('SENSE_NEG15',p['1'],-5.08);s.net('SENSE_NEG5',p['2'],5.08);s.gnd(p['3'])
note(a,'Trip nominal','Nominal trip magnitudes: 13.75V / 13.75V / 4.25V / 4.125V.\nNegative sense ratios unchanged; D7 dual diode clamp asymmetric shutdown.\n+/-5V monitors detect collapse, not full CS supply compliance. Require 500ms stable rearm.')
note(a,'U13 up to','U13 control supply: allow 2.1W AV; effective junction-to-ambient <=25 C/W.\nAll four AGN2004H coils intentionally use +5R. Nominal ~34mA each.\nTPS7A3901: allow 0.35W incl. load margin; solder exposed pad to GND copper.')
add(a,s);save(name,a)
# Shared PSU: Kelvin-sense the P68 input return instead of bonding it to local GND.
name='04_protection_output.kicad_sch';a=parse((P/name).read_text());s=addon(name)
# Change only GND symbols directly attached to U6A+, J16.2 and R55.2,
# plus K4 NC's GND symbol. Resolve from observed baseline coordinates.
# Find their exact GND coordinates from electrical geometry in the baseline.

remove_pts={(294.64,203.2),(363.22,240.03),(386.08,142.24),(381.0,210.82)}
for sym in list(children(a,'symbol')):
 if str(child(sym,'lib_id')[1])=='power:GND':
  at=tuple(map(float,child(sym,'at')[1:3]))
  if at in remove_pts:
   a.remove(sym)
   if at!=(294.64,203.2):s.label('AMP_RETURN',at,0,True)
r1=s.sym('Device:R',251.46,180.34,ref='R113',value='20k / 0.1%',foot='Resistor_SMD:R_0805_2012Metric')[0]
r2=s.sym('Device:R',251.46,198.12,ref='R114',value='10k / 0.1%',foot='Resistor_SMD:R_0805_2012Metric')[0]
s.net('AMP_RETURN',r1['1'],-7.62);s.wire(r1['2'],r2['1']);s.gnd(r2['2']);s.dot((251.46,189.23))
s.wire((251.46,189.23),(289.56,189.23),(289.56,203.2),(294.64,203.2))
change(a,'R52','Value','10k / 0.1%');change(a,'R53','Value','20k / 0.1%');change(a,'J16','Value','P68: SIGNAL / SGND SENSE')
note(a,'K4 OFF:', 'K4 OFF: P68 input shorted to its own SGND (AMP_RETURN).\nU6A output = AMP_RETURN - 2*POLARITY_OUT; use 0.1% matched ratios.\nJ16.1 -> P68 J6.2 SIGNAL; J16.2 -> P68 J6.1 SGND (sense only).\nShared PSU 0V connects to P68 power star; no direct AMP_RETURN-to-GND bond.')
add(a,s);save(name,a)
# Fault resistor dissipation: 15.75^2/2200=113mW; specify comfortable pulse/DC margin.
name='03_level_phase.kicad_sch';a=parse((P/name).read_text());change(a,'R112','Value','2k2 / 0.25W');save(name,a)
# Block final-stage DC; precharge on the isolated relay side while K4 is muted.
name='04_protection_output.kicad_sch';a=parse((P/name).read_text());s=addon(name);s.count=11000
for t in children(a,'global_label'):
 at=child(t,'at')
 if t[1]=='AMP_SERIES' and float(at[2])==152.4:t[1]=Q('AMP_AC')
 if t[1]=='AMP_OUT' and abs(float(at[2])-232.41)<.01:t[1]=Q('AMP_AC')
c=s.sym('Device:C',330.2,236.22,ref='C63',value='10u / 50V BIPOLAR',angle=270,foot='SubController:C_NP_Radial_D8.0mm_P3.50mm')[0]
s.net('AMP_SERIES',c['2'],-5.08);s.wire(c['1'],(350.52,236.22),(350.52,232.41),(363.22,232.41));s.dot((363.22,232.41))
change(a,'R55','Value','22k')
s.text('C63: Nichicon UES1H100MPM, non-polar. R55 charges it while muted.\nKeep mute >=2s after rail stabilisation/mode change; verify transient at J16.',20.32,265.43,1.016)
add(a,s);save(name,a)
# Copy the exact user relay footprint into this project, retaining its existing model.
fp=P/'libraries/Custom.pretty';fp.mkdir(exist_ok=True)
shutil.copy2('/Users/tomwatson/Downloads/Custom.pretty/Relay_DPDT_Panasonic_AGN2004H.kicad_mod',fp/'Relay_DPDT_Panasonic_AGN2004H.kicad_mod')
(P/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "SubController") (type "KiCad") (uri "${KIPRJMOD}/libraries/SubController.pretty") (options "") (descr "Verified project footprints")) (lib (name "Custom") (type "KiCad") (uri "${KIPRJMOD}/libraries/Custom.pretty") (options "") (descr "Exact user AGN2004H footprint")))\n')
# Nonpolar version of the standard 8mm/3.5mm radial footprint: remove polarity graphics.
fp=parse(Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Capacitor_THT.pretty/CP_Radial_D8.0mm_P3.50mm.kicad_mod').read_text())
fp[1]=Q('C_NP_Radial_D8.0mm_P3.50mm')
fp[:]=[t for t in fp if not(isinstance(t,list) and (t[0] in ['fp_line','model'] or (t[0]=='fp_text' and t[2]=='+')))]
for t in children(fp,'property'):
 if t[1]=='Value':t[2]=Q('C_NP_Radial_D8.0mm_P3.50mm')
child(fp,'descr')[1]=Q('Nonpolar Nichicon UES1H100MPM; diameter8mm height11.5mm pitch3.5mm; standard KiCad radial pads/courtyard without polarity graphics')
(P/'libraries/SubController.pretty/C_NP_Radial_D8.0mm_P3.50mm.kicad_mod').write_text(dump(fp)+'\n')
for name in ['03_level_phase.kicad_sch','06_power_mute.kicad_sch','SubController.kicad_sch']:
 a=parse((P/name).read_text())
 for t in children(a,'text'):
  t[1]=Q(str(t[1]).replace('~130kHz','~110.5kHz').replace('250mA','300mA').replace('250 mA','300 mA').replace('ATtiny412','ATtiny1614'))
 save(name,a)
# Impedance rescale retains unity Sallen-Key topology and nominal 40..120Hz.
name='02_crossover.kicad_sch';a=parse((P/name).read_text());s=addon(name);s.count=12000
for r in ['R10','R17','R24','R31']:change(a,r,'Value','4k27')
for c in ['C11','C12','C13','C14','C16','C56']:change(a,c,'Value','220n FILM / 63V')
for i in range(4):
 x=73.66+i*88.9;y=195.58
 r=s.sym('Device:R',x,177.8,ref=f'R{115+i}',value='15k',angle=270,foot='Resistor_SMD:R_0805_2012Metric')[0]
 s.wire(r['2'],(x-7.62,177.8),(x-7.62,y));s.dot((x-7.62,y))
 s.wire(r['1'],(x+12.7,177.8),(x+12.7,y));s.dot((x+12.7,y))
 s.text(f'R{115+i}: reduces impedance / gang error',x-33.02,164.0,.85)
note(a,'Nominal R=','R = 4k27 + (pot || 15k); Cf=440n, Cg=220n. Nominal 39.8..119.8Hz.\nAt 70Hz each physical rheostat is ~3k81. Max DC source resistance <28k.\nMeasure all four gangs and film caps; calibrate actual knob scale. Wiper tied to terminal1.\nKeep RV1 <=50 C ambient. CW increases crossover frequency.')
for t in children(a,'text'):
 t[1]=Q(str(t[1]).replace('Cf=200n','Cf=440n').replace('Cg=100n','Cg=220n').replace('2x100n','2x220n'))
add(a,s);save(name,a)
# Clean obsolete expander language, retaining all other sheet content.
name='08_rail_interlock.kicad_sch';a=parse((P/name).read_text())
for t in children(a,'text'):t[1]=Q(str(t[1]).replace('GP7','ATtiny PB2').replace('K4 grounds amplifier input','K4 shorts input to AMP_RETURN'))
save(name,a)
# One ground-transfer pole avoids inter-pole timing bridging two source grounds.
name='01_inputs.kicad_sch';a=parse((P/name).read_text());s=addon(name);s.count=13000
# Remove second K2 pole connections by observed pin coordinates from baseline.
k2=next(x for x in symbols(a,'K2') if child(x,'unit')[1]=='2')
x,y=map(float,child(k2,'at')[1:3]);ends=[(round(x-10.16,2),y),(round(x+10.16,2),round(y-5.08,2)),(round(x+10.16,2),round(y+5.08,2))]
remove_wire=[];wire_ends=set()
for w in children(a,'wire'):
 ps=[tuple(map(float,p[1:])) for p in children(child(w,'pts'),'xy')]
 if any(p in ends for p in ps):remove_wire.append(w);wire_ends.update(ps)
for w in remove_wire:a.remove(w)
for t in list(a):
 if isinstance(t,list) and t[0] in ['global_label','symbol']:
  at=child(t,'at')
  if at and tuple(map(float,at[1:3])) in wire_ends:
   if t[0]=='global_label' or child(t,'lib_id')[1]=='power:GND':a.remove(t)
for p in ends:s.nc(p)
for t in children(a,'global_label'):
 if t[1] in ['REF_L_RETURN','REF_R_RETURN']:t[1]=Q('REF_RETURN')
s.text('K2A alone transfers the source return; K2B unused.\nReference L/R returns share REF_RETURN before the relay.\nNo inter-pole timing bridge between Reference and AVR returns.',40.64,162.56,1.016)
add(a,s)
for t in children(a,'text'):
 if 'MONO =' in str(t[1]):child(t,'at')[1:3]=['245','180']
# Keep input-cap values readable beside the 47k bias resistors.
for r in ['C1','C2']:
 sym=symbols(a,r)[0];at=child(prop(sym,'Value'),'at');at[1]=str(float(at[1])-12.7);at[2]=str(float(at[2])+5.08)
save(name,a)
# Readability corrections from the rendered complete schematic review.
for name in ['02_crossover.kicad_sch','03_level_phase.kicad_sch','04_protection_output.kicad_sch','06_power_mute.kicad_sch']:
 a=parse((P/name).read_text())
 if name.startswith('02'):
  for t in children(a,'text'):
   if 'J25: 1-2' in str(t[1]):child(t,'at')[1:3]=['20.32','248.92']
 if name.startswith('03'):
  for t in children(a,'global_label'):
   if t[1]=='ATT_DRIVE':child(t,'at')[3]='90'
 if name.startswith('04'):
  for t in children(a,'text'):
   if 'K4 OFF:' in str(t[1]):child(t,'at')[1:3]=['20.32','195.58']
  # Duplicate adjacent global labels name the same short output wire; hide only one text by removing it.
  labs=[t for t in children(a,'global_label') if t[1]=='AMP_DRIVE']
  if len(labs)==2:
   pts=[tuple(map(float,child(t,'at')[1:3])) for t in labs]
   a.remove(min(labs,key=lambda t:float(child(t,'at')[1])))
   extra=addon(name);extra.count=14000;extra.wire(*pts);add(a,extra)
  change(a,'J16','Value','P68 SIGNAL / SENSE')
  sym=symbols(a,'J16')[0]
  for p in children(sym,'property'):
   if p[1] in ['Value','Reference']:child(p,'at')[1]='355.6'
  for t in children(a,'global_label'):
   if t[1]=='AMP_RETURN' and float(child(t,'at')[2])==210.82:child(t,'at')[3]='270'
 if name.startswith('06'):
  note(a,'U11 ~0.27W','U11: budget 0.35W; solder EP to GND copper / thermal vias at layout.\nU13: AV budget 2.2W; effective junction-to-ambient <=25 C/W, heatsink required.\nC46+C57 / C48+C58 directly at IN pins; C47/C49 at OUT pins.\nNR/SS100n; CFF10n each; keep CS VD+ tied to VA+. Local GND shares P68 power 0V.')
 save(name,a)
# K5 isolates powered sources from unpowered opamps; shares the fail-safe RUN coil driver.
name='01_inputs.kicad_sch';a=parse((P/name).read_text());s=addon(name);s.count=15000
ns['custom']['AGN2004H']=deepcopy(relay)
# Rename only the buffer-side labels, leaving K1 switched outputs named SEL_L/R.
for t in children(a,'global_label'):
 if t[1] in ['SEL_L','SEL_R'] and float(child(t,'at')[1])>120:t[1]=Q(str(t[1]).replace('SEL_','LIVE_'))
for unit,y,source,dst in [(1,81.28,'SEL_L','LIVE_L'),(2,132.08,'SEL_R','LIVE_R')]:
 p=s.sym('SubController:AGN2004H',139.7,y,ref='K5',unit=unit,value='AGN2004H',foot='Custom:Relay_DPDT_Panasonic_AGN2004H')[0]
 common,nc,no=('3','2','4') if unit==1 else ('6','7','5')
 s.net(dst,p[common],-5.08);s.gnd(p[nc]);s.net(source,p[no],5.08)
s.text('K5 OFF grounds buffer inputs; powered sources are disconnected.\nK5 and K4 share RUN. Connect at CS code0, wait 2s, then fade up.',92.71,150.0,1.016)
add(a,s);save(name,a)
name='07_drivers.kicad_sch';a=parse((P/name).read_text());s=addon(name);s.count=15000
p=s.sym('SubController:AGN2004H',345.44,114.3,ref='K5',unit=3,value='AGN2004H',foot='Custom:Relay_DPDT_Panasonic_AGN2004H')[0]
s.net('+5R',p['1'],-2.54);s.net('MUTE_COIL',p['8'],-2.54)
change(a,'R93','Value','100R');change(a,'R96','Value','4k7')
note(a,'Q4 switches','Q4 drives K1..K3: ~101mA nominal; allow 120mA. Q5 drives K4/K5: ~68mA; allow 80mA.\nAll AGN2004H coils intentionally use +5R (4.5V nominal).\nR95 retains 1k fault-current limit; R93=100R increases Q5 base drive.\nU13: allow 2.7W; effective junction-to-ambient <=20 C/W. +15V source >=350mA.')
add(a,s);save(name,a)
for name in ['06_power_mute.kicad_sch','SubController.kicad_sch']:
 a=parse((P/name).read_text())
 for t in children(a,'text'):t[1]=Q(str(t[1]).replace('300mA','350mA').replace('2.2W','2.7W').replace('<=25 C/W','<=20 C/W'))
 save(name,a)
# Shared power 0V also requires high-impedance input return sensing, not an RCA-to-PGND bond.
name='01_inputs.kicad_sch';a=parse((P/name).read_text());s=addon(name);s.count=16000
for r in ['R1','R2','R3','R4']:change(a,r,'Value','47k / 0.1%')
for sym in list(children(a,'symbol')):
 if child(sym,'lib_id')[1]=='power:GND' and tuple(map(float,child(sym,'at')[1:3]))==(86.36,167.64):
  a.remove(sym);s.label('SOURCE_RETURN',(86.36,167.64),180,True)
for i,y in enumerate([50.8,101.6]):
 lo=(200.66,round(y+22.86,2));hi=(226.06,round(y+22.86,2))
 for w in list(children(a,'wire')):
  ps=[tuple(map(float,p[1:])) for p in children(child(w,'pts'),'xy')]
  if set(ps)=={lo,hi}:a.remove(w)
 rf=s.sym('Device:R',213.36,y+22.86,ref=f'R{119+2*i}',value='47k / 0.1%',angle=270,foot='Resistor_SMD:R_0805_2012Metric')[0]
 s.wire(lo,rf['2']);s.wire(rf['1'],hi)
 rr=s.sym('Device:R',180.34,y+22.86,ref=f'R{120+2*i}',value='47k / 0.1%',angle=270,foot='Resistor_SMD:R_0805_2012Metric')[0]
 s.net('SOURCE_RETURN',rr['2'],-5.08);s.wire(rr['1'],lo);s.dot(lo)
 c=s.sym('Device:C',213.36,y+33.02,ref=f'C{64+i}',value='100p C0G / 50V',angle=270,foot='Capacitor_SMD:C_0805_2012Metric')[0]
 s.wire(lo,(lo[0],round(y+33.02,2)),c['2']);s.wire(c['1'],(hi[0],round(y+33.02,2)),hi);s.dot(hi)
note(a,'Input loading:','U1 differential receivers: Vout = SIGNAL - SOURCE_RETURN (DC gain1).\n47k matched ratios; REF input ~94k/channel, LFE ~47k. Return is sensed, not bonded.\nC1/C64 and C2/C65: matched 100p C0G; differential RF pole ~33.9kHz.\n0.1% resistors; select capacitor pairs within 2% for common-mode rejection.')
for t in children(a,'text'):
 if 'U1 differential' in str(t[1]):child(t,'at')[1:3]=['246.38','114.3']
 if 'No upstream bias' in str(t[1]):t[1]=Q(str(t[1]).replace('No upstream bias or ESD path to board GND.','Inactive source has no bias / ESD path to board GND.'))
 if 'K2A alone' in str(t[1]):t[1]=Q('K2A selects SOURCE_RETURN for differential input sensing. K2B unused.\nReference L/R returns share REF_RETURN before the relay.\nNever bond SOURCE_RETURN to GND or chassis.')
add(a,s);save(name,a)
# Mark a resistor-only commissioning gain option, keeping default gain unchanged.
name='03_level_phase.kicad_sch';a=parse((P/name).read_text());s=addon(name);s.count=16000
s.text('GAIN TUNE: R38=20k normal (input design ceiling 4Vrms).\nR38=10k gives +6dB; use only with <=2Vrms sources and recalibrate both modes.',128.27,120.65,1.016)
add(a,s);save(name,a)
# Use an available precision E192 value; collapse threshold changes by only 37.5mV.
name='06_power_mute.kicad_sch';a=parse((P/name).read_text());change(a,'R90','Value','86k6 / 0.1%')
for t in children(a,'text'):t[1]=Q(str(t[1]).replace('4.125V','4.1625V'))
save(name,a)
# Record the completed schematic revision date (no PCB revision change).
for path in P.glob('*.kicad_sch'):
 a=parse(path.read_text());tb=child(a,'title_block')
 if tb:
  if child(tb,'date'):child(tb,'date')[1]=Q('2026-10-08')
  if child(tb,'rev'):child(tb,'rev')[1]=Q('B')
 save(path.name,a)

for name in ['01_inputs.kicad_sch','07_drivers.kicad_sch']:
 a=parse((P/name).read_text())
 for sym in symbols(a,'K5'):
  x,y=map(float,child(sym,'at')[1:3])
  for key,dy in [('Reference',-12.7),('Value',-10.16)]:child(prop(sym,key),'at')[1:3]=[str(x-5.08),str(round(y+dy,2))]
 for t in children(a,'text'):t[1]=Q(str(t[1]).replace('after input division','after differential receivers'))
 save(name,a)

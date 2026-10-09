"""Independent assertions and ideal AC nodal solution of KiCad's exported netlist."""
from pathlib import Path
import sys,json,math,re,cmath
import numpy as np
from sexpr import parse,child,children
P=Path(__file__).resolve().parents[1]
data=parse((P/'design/final-review/final.net').read_text())
comps={str(child(c,'ref')[1]):dict(value=str(child(c,'value')[1]),foot=str(child(c,'footprint')[1])) for c in children(child(data,'components'),'comp')}
pins={};nets={}
for n in children(child(data,'nets'),'net'):
 name=str(child(n,'name')[1]);nets[name]=[]
 for node in children(n,'node'):
  ref,pin=str(child(node,'ref')[1]),str(child(node,'pin')[1]);pins.setdefault(ref,{})[pin]=name;nets[name].append((ref,pin))
checks=[]
def check(ok,description):
 checks.append(description);assert ok,description
def equal(ref,expect):
 for pin,net in expect.items():check(pins[ref][pin]==net,f'{ref}.{pin} = {net}')
for i in range(1,7):equal('U'+str(i),{'8':'+15V','4':'-15V'})
equal('U7',{'12':'+5A','4':'+5A','13':'-5A','15':'GND','10':'GND','5':'GND','9':'GND','16':'ATT_IN','14':'ATT_OUT','8':'CS_RUN'})
equal('K1',{'2':'REF_L','7':'REF_R','4':'LFE','5':'LFE','3':'SEL_L','6':'SEL_R','1':'+5R','8':'AV_COIL'})
equal('K2',{'2':'REF_RETURN','4':'LFE_RETURN','3':'SOURCE_RETURN','1':'+5R','8':'AV_COIL'})
equal('K3',{'2':'REF_LP','4':'MONO','3':'LEVEL_IN','7':'HP_OUT','5':'AV_HP_SELECT','6':'HP_SELECTED','8':'AV_COIL'})
for p in ['5','6','7']:check(pins['K2'][p].startswith('unconnected-'),'K2 unused pole pin '+p+' isolated')
equal('K4',{'2':'AMP_RETURN','4':'AMP_AC','3':'AMP_OUT','8':'MUTE_COIL'})
equal('K5',{'1':'+5R','8':'MUTE_COIL','2':'GND','7':'GND','3':'LIVE_L','6':'LIVE_R','4':'SEL_L','5':'SEL_R'})
for net in ['REF_L','REF_R','REF_RETURN','LFE','LFE_RETURN']:
 check(all(r.startswith(('J','K')) for r,p in nets[net]),net+' has no permanent board-ground bias/protection path')
for net in ['TRIG_PLUS','TRIG_MINUS','TRIG_LED_A']:
 check(all(r in ['J20','U10','R63','D1'] for r,p in nets[net]),net+' only opto-side components')
equal('D1',{'1':'TRIG_LED_A','2':'TRIG_MINUS'})
equal('U10',{'1':'TRIG_LED_A','2':'TRIG_MINUS','4':'TRIGGER_RAW','3':'GND'})
check(comps['U10']['value']=='VO617A-3','Requested VO617A-3 optocoupler fitted')
check(comps['U10']['foot']=='Package_DIP:DIP-4_W7.62mm','VO617A-3 base part DIP4 7.62mm footprint')
equal('D2',{'1':'+15V','2':'+5A'});equal('D3',{'1':'-5A','2':'-15V'});equal('D4',{'1':'+15V','2':'+5R'})
for ref,drain in [('D5','AV_COIL'),('D6','MUTE_COIL')]:equal(ref,{'1':'+5R','2':drain})
equal('U8',{'10':'UPDI','1':'+5R','14':'GND','11':'SER_DATA_INV','12':'SER_CLK_INV','13':'SER_CS_INV','2':'REF_ENC_A','3':'REF_ENC_B','4':'AV_ENC_A','5':'AV_ENC_B','6':'TRIGGER_N','7':'RAIL_GOOD','8':'AV_ENABLE','9':'RUN_REQUEST'})
check('U9' not in comps,'No expander retaining RUN across MCU reset')
equal('R97',{'1':'+5A','2':'CS_MUTE_INV'})
equal('D7',{'1':'SENSE_NEG15','2':'SENSE_NEG5','3':'GND'})
equal('J25',{'1':'LP_SLOPE','2':'REF_LP','3':'MONO'})
equal('J26',{'1':'RAIL_GOOD','2':'GND'})
equal('C63',{'1':'AMP_AC','2':'AMP_SERIES'})
equal('R55',{'1':'AMP_AC','2':'AMP_RETURN'})
equal('R113',{'1':'AMP_RETURN'})
check(set(nets['AMP_RETURN'])=={('J16','2'),('K4','2'),('R55','2'),('R113','1')},'P68 signal return never directly bonds to processor power ground')
for k in ['K1','K2','K3','K4','K5']:
 check(comps[k]['value']=='AGN2004H' and comps[k]['foot']=='Custom:Relay_DPDT_Panasonic_AGN2004H',k+' user selected Panasonic with existing footprint')
equal('U11',{'1':'+15V','2':'+15V','4':'GND','11':'GND','5':'-15V','10':'+5A','6':'-5A'})
equal('U13',{'1':'+15V','2':'GND','3':'+5R'})
check('U12' not in comps,'Separate 7905 regulator removed')
check(comps['U11']['value']=='TPS7A3901','Owned dual TPS7A3901 fitted')
check(comps['U11']['foot']=='SubController:TPS7A3901_DSC0010J_WSON10','TI DSC0010J exact local footprint')
check(pins['U11']['8']!='GND' and pins['R111']['2']==pins['U11']['8'],'Negative lower feedback arm connected to BUF, not GND')
for first,last,fb,out in [('R105','R106','9','10'),('R108','R110','7','6')]:
 check(pins[first]['2']==pins['U11'][out] and pins[last]['1']==pins['U11'][fb],first+' upper feedback arm endpoint wiring')
for a,b in [('R105','R106'),('R108','R109'),('R109','R110')]:check(pins[a]['1']==pins[b]['2'],a+' series link to '+b)
check(pins['R107']['1']==pins['U11']['9'] and pins['R107']['2']=='GND','Positive feedback lower arm returns to GND')
check(pins['R111']['1']==pins['U11']['7'],'Negative feedback lower arm returns to FBN')
equal('C59',{'1':pins['U11']['3'],'2':'GND'})
check(set(nets[pins['U11']['3']])=={('U11','3'),('C59','1')},'NR/SS connects only to C59, isolated from every supply rail')
for nr,expected in [('8',{('U11','8'),('R111','2')}),('9',{('U11','9'),('R106','1'),('R107','1'),('C60','1')}),('7',{('U11','7'),('R110','1'),('R111','1'),('C61','1')})]:
 check(set(nets[pins['U11'][nr]])==expected,'TPS internal node '+nr+' exact connections')
for a,b in [('R105','R106'),('R108','R109'),('R109','R110')]:
 check(set(nets[pins[a]['1']])=={(a,'1'),(b,'2')},a+' intermediate divider node isolated')
equal('C60',{'1':pins['U11']['9'],'2':'+5A'});equal('C61',{'1':pins['U11']['7'],'2':'-5A'})
for ref,net in [('C46','+15V'),('C57','+15V'),('C48','-15V'),('C58','-15V'),('C47','+5A'),('C49','-5A')]:
 equal(ref,{'1':net,'2':'GND'});check(comps[ref]['value']=='10u / 50V X5R',ref+' regulator ceramic 10u 50V')
equal('U14',{'1':'VREF_2V5','2':'GND'})
for ref in ['Q1','Q2','Q3','Q4','Q5','Q6','Q7','Q8','Q9']:equal(ref,{'3':'GND'})
for ref in ['C44','C45','C51']:
 pp=pins[ref];check((pp['1']=='GND' and pp['2'].startswith('-')) or (pp['2']=='GND' and pp['1'].startswith('+')),ref+' electrolytic polarity')
check(all(f'J{i}' not in comps for i in range(5,9)),'Four frequency-bank headers removed')
for gang,ref,src,dst in [(1,'R10','MONO','LP1_A'),(2,'R17','LP1_A','LP1_B'),(3,'R24','LP12','LP2_A'),(4,'R31','LP2_A','LP2_B')]:
 check(comps[ref]['value']=='4k27',ref+' minimum filter resistance = 4k27')
 equal(ref,{'2':src});equal('RV1',{f'R{gang}.1':dst,f'R{gang}.2':dst,f'R{gang}.3':pins[ref]['1']})
 check(set(nets[pins[ref]['1']])=={(ref,'1'),('RV1',f'R{gang}.3'),(f'R{114+gang}','2')},f'Gang {gang} CW end only connected through series resistor')
check(comps['RV1']['value']=='PTD904-2015K-B203','Exact Bourns four-gang part fitted')
# Footprint pad sets versus all manufacturer-numbered symbol pins (NC pads included).
base=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints')
fp_paths={'SubController':P/'libraries/SubController.pretty'}
for table in [Path.home()/'Library/Preferences/kicad/10.0/fp-lib-table',P/'fp-lib-table']:
 if table.exists():
  for lib in children(parse(table.read_text()),'lib'):
   uri=str(child(lib,'uri')[1]).replace('${KIPRJMOD}',str(P));fp_paths[str(child(lib,'name')[1])]=Path(uri)
for ref,c in comps.items():
 lib,fp=c['foot'].split(':');file=fp_paths.get(lib,base/(lib+'.pretty'))/(fp+'.kicad_mod')
 f=parse(file.read_text());pads={str(p[1]) for p in children(f,'pad') if str(p[1])};check(set(pins[ref])==pads,ref+' footprint pad set matches symbol pins')
# Coordinate/drill check of the exact PTD904 manufacturer pattern, not just pads.
pf=parse((P/'libraries/SubController.pretty/PTD904_2015K_B203_Horizontal.kicad_mod').read_text())
potpads={str(p[1]):p for p in children(pf,'pad')}
for gang,x in [(1,-5),(2,-7.5),(3,-12.5),(4,-15)]:
 for term,y in [(1,2.5),(2,0),(3,-2.5)]:
  pad=potpads[f'R{gang}.{term}'];at=child(pad,'at')
  check((float(at[1]),float(at[2]))==(x,y),f'RV1 R{gang}.{term} manufacturer coordinate {x},{y}mm')
  check(float(child(pad,'drill')[1])==1.0,f'RV1 R{gang}.{term} manufacturer 1.0mm hole')
# Function from values, never copied resistance/capacitance into AC topology.
def value(v):
 v=v.split()[0].upper().replace('FILM','').removesuffix('F');m=re.fullmatch(r'(\d+(?:\.\d+)?)([RKNMUP]?)(\d*)',v);assert m,v
 a,scale,b=m.groups();return float(a+('.'+b if b else ''))*{'':1,'R':1,'K':1e3,'N':1e-9,'M':1e6,'U':1e-6,'P':1e-12}[scale]
ops=[(pins[f'U{i}'][a],pins[f'U{i}'][b],pins[f'U{i}'][o]) for i in range(1,7) for a,b,o in [('3','2','1'),('5','6','7')]]
# Each scenario connects actual relay / jumper pins and solves ideal opamps + CS analog VCVS.
def solve(freq,mode='REF',bank=3,slope=24,hp=1,ap=None,pol=0,mute=False,level=1,source='both',noise=False,rv=None,lp_bypass=False,hp_bypass=False,av_hp=False,all_nodes=False,remote_ground=0,vos=None,ib=None,source_return=0,cs_input_R=10000):
 parent={n:n for n in nets}
 def root(n):
  while parent[n]!=n:n=parent[n]
  return n
 def join(a,b):parent[root(a)]=root(b)
 def short(ref,a,b):join(pins[ref][str(a)],pins[ref][str(b)])
 for k in ['K1','K2','K3']:
  short(k,3,2 if mode=='REF' else 4);short(k,6,7 if mode=='REF' else 5)
 short('K4',3,2 if mute else 4)
 short('K5',3,2 if mute else 4);short('K5',6,7 if mute else 5)
 # Each selected pot resistance is an analogue rheostat between CW terminal3
 # and wiper2. Terminal1 is physically tied to wiper2 for open-wiper fallback.
 rv=[pot_positions[bank]]*4 if rv is None else ([rv]*4 if isinstance(rv,(int,float)) else rv)
 for gang,r in enumerate(rv,1):
  if r==0:short('RV1',f'R{gang}.3',f'R{gang}.2')
 for j in [11,12]:short(f'J{j}',2*hp+1,2*hp+2)
 short('J25',2,3 if lp_bypass else 1);short('J4',2,1 if slope==12 else 3);short('J10',2,1 if ap is None else 3)
 short('J13',2,3 if av_hp else 1);short('J14',2,1 if hp_bypass else 3);short('J15',2,1 if pol==0 else 3)
 gnd=root('GND');branches=[];noisy_R=[]
 for ref,c in comps.items():
  if ref=='RV1':continue
  if ref[0] not in ['R','C']:continue
  a,b=(root(pins[ref][p]) for p in ['1','2'])
  # Only analog section R1..R55 C1..C40, all local supply decouplers skip.
  if ref[0]=='R' and int(ref[1:])>55 and ref not in ['R112','R113','R114','R115','R116','R117','R118','R119','R120','R121','R122']:continue
  if ref[0]=='C' and int(ref[1:])>40 and ref not in ['C56','C62','C63','C64','C65']:continue
  if any(n.startswith(('+','-')) for n in [a,b]):continue
  v=value(c['value']);y=1/v if ref[0]=='R' else 2j*math.pi*freq*v;branches.append((a,b,y))
  if ref[0]=='R':noisy_R.append((a,b,v))
 for gang,r in enumerate(rv,1):
  if r>0:
   a,b=(root(pins['RV1'][f'R{gang}.{t}']) for t in [3,2]);branches.append((a,b,1/r));noisy_R.append((a,b,r))
 if ap is not None:branches.append((root('PHASE_TOP'),root('PHASE_WIPER'),1/max(ap,1e-6)))
 branches.append((root('ATT_IN'),gnd,1/cs_input_R));branches.append((root('AMP_OUT'),root('AMP_RETURN'),1/(23000+1/(2j*math.pi*freq*10e-6))))
 activeops=[tuple(root(x) for x in o) for o in ops];vcs=[(root('ATT_OUT'),root('ATT_IN'),level)]
 selected=['REF_L','REF_R'] if mode=='REF' else ['LFE'];voltages=[(root(x),source_return+(0 if source=='none' else 1 if source=='both' or x.endswith('_L') else 0)) for x in selected]+[(root('AMP_RETURN'),remote_ground),(root('SOURCE_RETURN'),source_return)]
 # Keep only actual branch/opamp/source connected nodes; dangling frequency resistor tails valid.
 names=set(n for a,b,y in branches for n in [a,b])|set(n for o in activeops for n in o)|set(n for o in vcs for n in o[:2])|set(n for n,v in voltages);names.discard(gnd)
 ix={n:i for i,n in enumerate(sorted(names))};nv=len(ix);extra=len(activeops)+len(vcs)+len(voltages);A=np.zeros((nv+extra,nv+extra),complex);z=np.zeros(nv+extra,complex)
 def add(a,b,v):
  if a!=gnd and b!=gnd:A[ix[a],ix[b]]+=v
 for a,b,y in branches:add(a,a,y);add(b,b,y);add(a,b,-y);add(b,a,-y)
 k=nv
 for oi,(plus,minus,out) in enumerate(activeops):
  if out!=gnd:A[ix[out],k]+=1
  if plus!=gnd:A[k,ix[plus]]+=1
  if minus!=gnd:A[k,ix[minus]]-=1
  if vos is not None:z[k]=-vos[oi]
  if ib is not None:
   for n,current in zip([plus,minus],ib[oi]):
    if n!=gnd:z[ix[n]]+=current
  k+=1
 for out,inp,gain in vcs:
  A[ix[out],k]+=1;A[k,ix[out]]+=1;A[k,ix[inp]]-=gain;k+=1
 for n,v in voltages:
  A[ix[n],k]+=1;A[k,ix[n]]+=1;z[k]=v;k+=1
 result=np.linalg.solve(A,z)
 if noise:
  e=np.zeros(nv+extra,complex);e[ix[root('AMP_OUT')]]=1;adj=np.linalg.solve(A.T,e)
  sensitivity=lambda n:0 if n==gnd else adj[ix[n]]
  psd_R=sum(abs(sensitivity(a)-sensitivity(b))**2*4*1.380649e-23*300/r for a,b,r in noisy_R)
  psd_ops=sum(abs(adj[nv+i])**2*(4.5e-9)**2+(abs(sensitivity(a))**2+abs(sensitivity(b))**2)*(0.7e-12)**2 for i,(a,b,o) in enumerate(activeops))
  psd_CS=abs(adj[nv+len(activeops)])**2*(4.2e-6)**2/(20000-20)
  return [psd_R,psd_ops,psd_CS]
 if all_nodes:return {n:(0 if root(n)==gnd else complex(result[ix[root(n)]])) for n in nets if root(n)==gnd or root(n) in ix}
 return 0 if root('AMP_OUT')==gnd else result[ix[root('AMP_OUT')]]
from analyse import L,H,AP,pot_positions,LP_K,LP_SERIES,effective_pot
def output_network(freq):
 zamp=23000+1/(2j*math.pi*freq*10e-6)
 zload=1/(1/value(comps['R55']['value'])+1/zamp)
 return zload/(100+1/(2j*math.pi*freq*value(comps['C63']['value']))+zload)
input_gain=value(comps['R119']['value'])/value(comps['R120']['value'])
sum_gain=2*value(comps['R7']['value'])/value(comps['R5']['value'])
check(value(comps['R5']['value'])==value(comps['R6']['value']),'Both mono summing input resistors match')
maxerr=0;cases=0
for mode in ['REF','AV']:
 for bank in range(7):
  for slope in [12,24]:
   for hp in range(3):
    for ap in [None,25000]:
     for pol in [0,180]:
      for freq in [5,20,50,100,500]:
       r=LP_SERIES+effective_pot(pot_positions[bank]);aa,bb=[(16900,34000),(12700,25500),(10200,20500)][hp]
       expected=input_gain*sum_gain/(1+2j*math.pi*freq*47000*100e-12)*output_network(freq)/(1+2j*math.pi*freq*1.44e-6)*(1 if mode=='AV' else L(freq,r,r)**(slope//12)*H(freq,aa,bb))*(1 if ap is None else AP(freq,2200+ap*value(comps['R43']['value'])/(ap+value(comps['R43']['value']))))*(-1 if pol else 1)
       actual=solve(freq,mode,bank,slope,hp,ap,pol);err=abs(actual-expected);maxerr=max(maxerr,err);cases+=1
       assert err<1e-7,(mode,bank,slope,hp,ap,pol,freq,actual,expected,err)
# Both end stops and unequal gangs: model the actual four resistances rather
# than silently assuming matching or interpreting the +/-3dB divider spec.
for rv in [[0]*4,[20000]*4,[16000]*4,[24000]*4,[5000,7000,6500,9000],[16000,24000,19000,21000]]:
 for slope in [12,24]:
  for freq in [5,20,50,100,500]:
   rr=[LP_SERIES+effective_pot(x) for x in rv]
   expected=input_gain*sum_gain/(1+2j*math.pi*freq*47000*100e-12)*output_network(freq)/(1+2j*math.pi*freq*1.44e-6)*L(freq,*rr[:2])*(L(freq,*rr[2:]) if slope==24 else 1)*H(freq,12700,25500)
   actual=solve(freq,slope=slope,rv=rv);err=abs(actual-expected);maxerr=max(maxerr,err);cases+=1
   assert err<1e-7,(rv,slope,freq,err)
for f in [5,20,70,120,1000,20000]:
 for g in [-1,-.1,.1,1]:
  check(abs(solve(f,mode='AV',source='none',source_return=g))<1e-8,'Differential receivers reject selected-source ground shift '+str((f,g)))
check(abs(solve(70,source='left')/solve(70)-.5)<1e-8,'One REF channel produces half correlated-stereo output')
check(solve(70,mute=True)==0,'Output relay OFF shorts amplifier input to AMP_RETURN')
for f in [5,20,70,120,1000,20000]:
 for v in [-1,-.1,.1,1]:
  check(abs(solve(f,mode='AV',source='none',remote_ground=v)-v)<1e-8,'Output ground sensing follows remote return '+str((f,v)))
  check(abs(solve(f,mute=True,remote_ground=v)-v)<1e-8,'Muted output follows remote SGND '+str((f,v)))
check(abs(solve(70,level=.1)/solve(70)-.1)<1e-8,'Analog attenuation setting scales output')
for mode in ['REF','AV']:
 for f in [5,20,70,120,1000,20000]:
  expected=solve(f,mode=mode)*(1+2j*math.pi*f*1.44e-6)/(1+2j*math.pi*f*1.495e-6)
  check(abs(solve(f,mode=mode,cs_input_R=8000)-expected)<1e-7,'CS minimum8k input loading '+str((mode,f)))
report={'assertions_passed':len(checks),'assertions':checks,'ideal_AC_scenarios_passed':cases,'maximum_complex_response_error':maxerr,'limitations':'Ideal opamps and CS gain model; excludes finite GBW, device nonlinearities/noise/offsets and real relay transients. No SPICE or bench qualification.'}
(P/'design/final-review/connectivity-and-AC.json').write_text(json.dumps(report,indent=2)+'\n')
print(f'{len(checks)} connectivity/package assertions, {cases} AC scenarios passed; max complex error {maxerr:.3g}')

noise_results={}
for mode,ap in [('REF',None),('REF',50000),('AV',None),('AV',50000)]:
 fs=np.geomspace(20,20000,151);psds=np.array([solve(f,mode=mode,ap=ap,noise=True) for f in fs]);powers=np.trapezoid(psds,fs,axis=0)
 noise_results[f'{mode}_phase_'+('bypass' if ap is None else 'full')]={'resistor_uVrms':float(np.sqrt(powers[0])*1e6),'opamp_uVrms':float(np.sqrt(powers[1])*1e6),'CS_typ_uVrms':float(np.sqrt(powers[2])*1e6),'total_typ_uVrms':float(np.sqrt(sum(powers))*1e6),'total_with_CS_max_other_typ_uVrms':float(np.sqrt(powers[0]+powers[1]+4*powers[2])*1e6)}
(P/'design/final-review/noise-estimates.json').write_text(json.dumps({'conditions':'20Hz-20kHz, 300K, ideal zero-impedance source, opamp white en=4.5nV and in=0.7pA, CS specified integrated noise treated as equivalent white PSD; excludes 1/f, carbon-pot excess/contact noise, source excess noise, hum, clock feedthrough and nonlinearities. Estimates, not guaranteed limits.', 'results':noise_results},indent=2)+'\n')
print('Noise estimates saved.')

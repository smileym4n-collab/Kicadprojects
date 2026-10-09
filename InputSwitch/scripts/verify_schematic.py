"""Check exported KiCad netlist against independent system requirements."""
from pathlib import Path
import xml.etree.ElementTree as E
import json, hashlib, math
from collections import defaultdict
root=Path(__file__).resolve().parent.parent
r=E.parse(root/'review/final-netlist.xml').getroot()
pn={}; nets={}; comps={c.attrib['ref']:c for c in r.findall('components/comp')}
for n in r.findall('nets/net'):
 name=n.attrib['name'];nets[name]=set()
 for x in n.findall('node'):
  key=x.attrib['ref']+'.'+x.attrib['pin'];pn[key]=name;nets[name].add(key)
checks=[]
def ck(ok,desc):
 checks.append({'pass':bool(ok),'check':desc})
 if not ok:raise AssertionError(desc)
def same(*ps):return len({pn[p] for p in ps})==1
def nn(p,net):ck(pn[p]==net,p+' belongs to '+net)
for p,net in {'U2.1':'+5V','U2.8':'GND','U2.6':'UPDI','J8.1':'UPDI','J8.2':'+5V','J8.3':'GND','U2.4':'SOURCE_AV','U2.5':'MUTE','U2.7':'AUDIO_PRESENT_N','U2.2':'P3A_ON','U2.3':'TOGGLE_AV','U3.9':'+5V','U4.9':'+12V','U3.8':'GND','U4.8':'GND','U1.1':'+12V','U1.2':'GND','U1.3':'+5V','J10.1':'+12V','J10.2':'G7L_LOW','J9.1':'GND','J9.3':'+5V','R2.2':'GND','R3.2':'GND','R4.2':'GND','R5.2':'GND'}.items():nn(p,net)
ck(nets['UPDI']=={'U2.6','J8.1'},'UPDI is reserved and has no load/RC')
for k,n in [('K1',16),('K2',15),('K3',14)]:
 nn(k+'.1','+5V');ck(same(k+'.8',f'U3.{n}'),k+' coil has its own ULN channel')
 ck(comps[k].findtext('value')=='G6K-2P-Y DC5',k+' is labelled DC5')
ck(same('U3.1','U3.2','U2.4'),'K1/K2 command shared at inputs only')
ck(same('U3.3','U2.5'),'K3 command is MUTE')
ck(same('U4.1','U2.2'),'G7L command is P3A_ON')
for u,ns in [('U3',[4,5,6,7]),('U4',[2,3,4,5,6,7])]:
 for n in ns:nn(f'{u}.{n}','GND')
for ch,k,jr,ja,jo,base,amp,op,dc,qref in [('L','K1','J1','J2','J5',20,'U5','U6','U10','Q2'),('R','K2','J3','J4','J6',40,'U7','U8','U11','Q3')]:
 for p,net in {k+'.3':'SEL_'+ch+'_SIGNAL',k+'.6':'SEL_'+ch+'_RETURN',jo+'.2':'SEL_'+ch+'_RETURN',dc+'.1':'+5V',dc+'.2':'GND',dc+'.5':'SEL_'+ch+'_RETURN',dc+'.7':'ISO_'+ch+'_5V',amp+'.4':'SEL_'+ch+'_RETURN',amp+'.8':'ISO_'+ch+'_QUIET',op+'.3':'GND',qref+'.3':'SEL_'+ch+'_RETURN'}.items():nn(p,net)
 ck(same(jr+'.1',k+'.2') and same(jr+'.2',k+'.7'),ch+' REFERENCE on both NC contacts')
 ck(same(ja+'.1',k+'.4') and same(ja+'.2',k+'.5'),ch+' AV on both NO contacts')
 ck(same(f'C{base+4}.1',k+'.3'),'Detector '+ch+' taps before mute')
 ck(same(f'R{base+13}.2','U2.7'),'Detector '+ch+' optocoupler reaches MCU envelope')
 ck(same(amp+'.1',amp+'.6',f'R{base+5}.2'),'Detector '+ch+' amplifier output to comparator inverting input')
 ck(same(amp+'.5',f'R{base+7}.2',f'R{base+8}.1',f'R{base+9}.1'),'Detector '+ch+' threshold and positive hysteresis')
 ck(same(amp+'.7',f'R{base+9}.2',f'R{base+10}.1'),'Detector '+ch+' comparator drives BJT, not MCU directly')
 ck(same(op+'.2',qref+'.1'),'Detector '+ch+' opto cathode driven by collector')
 ck(same(f'R{base+14}.1',f'C{base+3}.1',f'R{base+2}.2'),'Detector '+ch+' divider midpoint at bias')
 ck(same(f'R{base+14}.2',amp+'.4'),'Detector '+ch+' bias divider bottom at own return')
 ck(comps[dc].findtext('value')=='SPU03L-05','Detector '+ch+' uses stocked 5V module')
 ck(same(f'R{base}.1',dc+'.7') and same(f'R{base}.2',dc+'.5'),'Detector '+ch+' preload is across raw isolated output')
 ck(same(f'R{base+1}.1',dc+'.7') and same(f'R{base+1}.2',amp+'.8'),'Detector '+ch+' filter feeds LM358 supply')
ck(len({pn[x] for x in ['J1.2','J2.2','J3.2','J4.2','J5.2','J6.2','U2.8']})==7,'All four input returns, two selected returns and GND are distinct copper nets')
class DSU:
 def __init__(self):self.p={n:n for n in nets}
 def find(self,n):
  while self.p[n]!=n:n=self.p[n]
  return n
 def join(self,a,b):self.p[self.find(a)]=self.find(b)
 def pins(self,*ps):
  for a,b in zip(ps,ps[1:]):self.join(pn[a],pn[b])
 def eq(self,a,b):return self.find(pn[a])==self.find(pn[b])
# Static contact states. These assumptions come from Omron's contact drawing,
# not the schematic's graphics or pin labels.
for av in [False,True]:
 for mute in [False,True]:
  d=DSU()
  for k in ['K1','K2']:d.pins(k+'.3',k+('.4' if av else '.2'));d.pins(k+'.6',k+('.5' if av else '.7'))
  d.pins('K3.3','K3.4' if mute else 'K3.2');d.pins('K3.6','K3.5' if mute else 'K3.7')
  state=f'AV={av}, MUTE={mute}'
  for active,inactive,out in [(('J2' if av else 'J1'),('J1' if av else 'J2'),'J5'),(('J4' if av else 'J3'),('J3' if av else 'J4'),'J6')]:
   ck(d.eq(out+'.2',active+'.2'),state+': selected return reaches '+out)
   ck(not d.eq(out+'.2',inactive+'.2'),state+': inactive return isolated at '+out)
   ck(d.eq(out+'.1',out+'.2')==mute,state+': output short follows mute at '+out)
   ck(d.eq(out+'.1',active+'.1')!=mute,state+': selected signal passes iff unmuted at '+out)
   ck(not d.eq(active+'.1',active+'.2'),state+': source output never shorted')
   ck(not d.eq(out+'.2','U2.8'),state+': output return isolated from control')
  ck(not d.eq('J5.2','J6.2'),state+': L/R returns not joined on board')
# Conservatively join each detector's internal active/passive paths, including
# capacitors: this proves there is no hidden resistive/AC wired bypass of barriers.
d=DSU()
for ref,c in comps.items():
 ps=[p for p in pn if p.startswith(ref+'.')]
 if ref in ['U10','U11']:d.pins(ref+'.1',ref+'.2');d.pins(ref+'.5',ref+'.7')
 elif ref in ['U6','U8']:d.pins(ref+'.1',ref+'.2');d.pins(ref+'.3',ref+'.4')
 elif ref.startswith('K'):d.pins(ref+'.1',ref+'.8')
 elif ref.startswith('J') or ref.startswith('TP'):continue
 else:d.pins(*ps)
for ch in ['L','R']:
 ck(d.find('SEL_'+ch+'_RETURN')!=d.find('GND'),'No conductive/AC component path from '+ch+' detector to control')
ck(d.find('SEL_L_RETURN')!=d.find('SEL_R_RETURN'),'Independent detector channels have no internal return bridge')
# A real external shared P3A return creates the known transitional limitation.
d=DSU();d.pins('J5.2','J6.2');d.pins('K1.6','K1.5');d.pins('K2.6','K2.7')
ck(d.eq('J2.2','J3.2'),'Known limitation reproduced: staggered K1/K2 + external P3A common returns bridges sources transiently')
for f in ['InputSwitch.kicad_pcb','InputSwitch.kicad_pro']:
 ck((root/f).read_bytes()==(root/'review/pre-spu03-2026-10-01'/f).read_bytes(),f+' unchanged byte for byte')
ck('Errors 0  Warnings 0' in (root/'review/final-erc.txt').read_text(),'Final ERC: zero errors and warnings')
calc={'midband_gain':101*100/570,'input_ohms':570000,'input_highpass_hz':1/(2*math.pi*570000*100e-9),'gain_highpass_hz':1/(2*math.pi*1000*33e-6),'quiet_rail_filter_hz':1/(2*math.pi*100*47e-6),'envelope_tau_ms':47000*2.2e-6*1000,'nominal_threshold_rms_mV':(1.11-(1.11/10000+.02/2.2e6)/(1/10000+1/100000+1/2.2e6))/(101*100/570)/math.sqrt(2)*1000}
report={'passed':len(checks),'checks':checks,'nominal_calculations_not_simulation':calc,'limitations':['ULN2003A/G6K pickup voltage not guaranteed','Independent relay timing can bridge source returns externally','No firmware, transient simulation, layout, EMI, thermal or bench validation']}
(root/'review/connectivity-checks.json').write_text(json.dumps(report,indent=2)+'\n')
(root/'review/connectivity-checks.txt').write_text('\n'.join('PASS: '+c['check'] for c in checks)+'\n\n'+json.dumps(calc,indent=2)+'\n')
print(str(len(checks))+' checks passed.');print(json.dumps(calc,indent=2))
